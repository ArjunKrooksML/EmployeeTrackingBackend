import json
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from openai import OpenAI
import config
from database.models import Employee as EmployeeDB, Admin as AdminDB, Project as ProjectDB, Task as TaskDB
from services import attendance as att_svc, leaves as leave_svc, employee_tasks as task_svc
from services import admin_tasks, admin_employees as emp_svc, employee_projects as proj_svc
from models.leaves import LeaveCreate
from models.tasks import TaskCreate

client = OpenAI(api_key=config.OPENAI_API_KEY)
MODEL = "gpt-4o-mini"

EMPLOYEE_SYSTEM = """You are SVAAS Assistant, an internal AI helper for SVAAS Inframax Solutions OPC Pvt Ltd. You help employees manage their day-to-day work through natural conversation.

## Who you're talking to
The current user is {employee_name}, role: {role}, employee ID: {employee_id}.
Today's date is {today}.

## What you can do
You have tools to:
- View the user's attendance, tasks, leaves, projects, and profile
- Mark attendance (check-in)
- Apply, view, and cancel leave requests
- Update task status and progress
- If the user is HR or GM: view all employees, all attendance, all leaves, approve or reject leave requests, create and assign tasks

## Behaviour rules
1. **Always confirm before any write action.** Before applying a leave, marking attendance, updating a task, or any action that changes data — summarise what you're about to do and ask the user to confirm. Only proceed after explicit confirmation ("yes", "confirm", "go ahead").
2. **Only act on what's asked.** Don't volunteer to do multiple things at once unless the user asked for it.
3. **Stay scoped.** You only have access to SVAAS data through your tools. Don't answer general HR policy questions, legal queries, or anything outside the application's data.
4. **Be concise.** This is a work tool. Short, clear responses. No unnecessary filler.
5. **Handle ambiguity by asking.** If a request is unclear (e.g. "apply leave" with no date), ask for the missing detail before calling any tool.
6. **Dates.** Always confirm the exact date before writing. If the user says "tomorrow" or "next Monday", resolve it to an actual date and confirm with the user.
7. **Role awareness.** Regular employees can only see and act on their own data. HR and GM can view and act on all employee data. Never show one employee's private data to another employee.

## Tone
Professional but approachable. You're a helpful colleague, not a formal system. Keep it brief."""

ADMIN_SYSTEM = """You are SVAAS Assistant, an internal AI helper for SVAAS Inframax Solutions OPC Pvt Ltd. You assist the system administrator with managing the entire system.

## Who you're talking to
The current user is {admin_name}, Administrator.
Today's date is {today}.

## What you can do
You have tools to manage the entire system:
- View and manage all employees
- View and manage all projects and tasks
- View all attendance records
- View and approve/reject all leave requests

## Behaviour rules
1. **Always confirm before any write action.** Before creating, updating, or deleting anything — summarise what you're about to do and ask for confirmation. Only proceed after explicit confirmation.
2. **Only act on what's asked.** Don't volunteer to do multiple things unless asked.
3. **Stay scoped.** You only have access to SVAAS data through your tools.
4. **Be concise.** Short, clear responses. No unnecessary filler.
5. **Handle ambiguity by asking.** If a request is unclear, ask for the missing detail.
6. **Dates.** Always confirm exact dates before any write operation.

## Tone
Professional but approachable. Keep it brief."""


def _ser(obj):
    if obj is None:
        return None
    if isinstance(obj, list):
        return [_ser(i) for i in obj]
    if hasattr(obj, '__table__'):
        d = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            d[col.name] = str(val) if isinstance(val, (date, datetime, time)) else val
        return d
    if isinstance(obj, dict):
        return {k: (str(v) if isinstance(v, (date, datetime, time)) else v) for k, v in obj.items()}
    return obj


def _fn(name, description, properties, required=None):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


BASE_TOOLS = [
    _fn("get_my_profile", "Get the current employee's profile and salary details.", {}, []),
    _fn("get_my_attendance", "Get the current employee's attendance records.", {
        "limit": {"type": "integer", "description": "Number of records to return (default 30)"},
    }),
    _fn("get_my_tasks", "Get all tasks assigned to the current employee.", {}, []),
    _fn("get_my_leaves", "Get the current employee's leave requests.", {}, []),
    _fn("get_projects", "Get all projects.", {}, []),
    _fn("mark_attendance", "Check in the current employee for today. Only call after user confirms.", {}, []),
    _fn("apply_leave", "Submit a leave request. Only call after user confirms.", {
        "leave_type": {"type": "string", "enum": ["casual", "sick", "emergency"]},
        "leave_date": {"type": "string", "description": "YYYY-MM-DD"},
        "day_type": {"type": "string", "enum": ["full", "first_half", "second_half"]},
        "reason": {"type": "string"},
    }, ["leave_type", "leave_date", "day_type"]),
    _fn("cancel_leave", "Cancel a pending leave request. Only call after user confirms.", {
        "leave_id": {"type": "integer"},
    }, ["leave_id"]),
    _fn("update_task_status", "Mark a task as completed. Only call after user confirms.", {
        "task_id": {"type": "integer"},
        "is_completed": {"type": "boolean"},
    }, ["task_id", "is_completed"]),
]

MANAGER_TOOLS = [
    _fn("get_all_employees", "Get a list of all employees.", {}, []),
    _fn("get_all_leaves", "Get all leave requests, optionally filtered by status.", {
        "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
    }),
    _fn("approve_reject_leave", "Approve or reject a leave request. Only call after user confirms.", {
        "leave_id": {"type": "integer"},
        "status": {"type": "string", "enum": ["approved", "rejected"]},
    }, ["leave_id", "status"]),
    _fn("get_all_attendance", "Get all employee attendance records.", {
        "limit": {"type": "integer"},
    }),
    _fn("create_task", "Create and assign a task to an employee. Only call after user confirms.", {
        "task_name": {"type": "string"},
        "project_id": {"type": "integer"},
        "assigned_to": {"type": "integer"},
        "description": {"type": "string"},
        "deadline": {"type": "string", "description": "YYYY-MM-DD"},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"]},
    }, ["task_name", "project_id", "assigned_to"]),
]

ADMIN_TOOLS = [
    _fn("get_projects", "Get all projects.", {}, []),
    _fn("get_all_employees", "Get a list of all employees.", {}, []),
    _fn("get_all_tasks", "Get all tasks.", {
        "status": {"type": "string"},
    }),
    _fn("get_all_leaves", "Get all leave requests.", {
        "status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
    }),
    _fn("approve_reject_leave", "Approve or reject a leave request. Only call after user confirms.", {
        "leave_id": {"type": "integer"},
        "status": {"type": "string", "enum": ["approved", "rejected"]},
    }, ["leave_id", "status"]),
    _fn("get_all_attendance", "Get all attendance records.", {
        "limit": {"type": "integer"},
    }),
    _fn("create_task", "Create and assign a task. Only call after user confirms.", {
        "task_name": {"type": "string"},
        "project_id": {"type": "integer"},
        "assigned_to": {"type": "integer"},
        "description": {"type": "string"},
        "deadline": {"type": "string"},
        "priority": {"type": "string", "enum": ["Low", "Medium", "High", "Urgent"]},
    }, ["task_name", "project_id", "assigned_to"]),
]


def _tools_for_role(role: str) -> list:
    if role in ("hr", "gm"):
        return BASE_TOOLS + MANAGER_TOOLS
    if role == "senior":
        return BASE_TOOLS + [MANAGER_TOOLS[4]]  # create_task only
    return BASE_TOOLS


def _exec_emp_tool(name: str, inp: dict, emp: EmployeeDB, db: Session) -> dict:
    role = emp.role or "employee"
    is_manager = role in ("hr", "gm")
    is_senior = role == "senior"

    if name == "get_my_profile":
        return _ser(emp)
    if name == "get_my_attendance":
        records = att_svc.get_att(emp.employee_id, db)
        return {"attendance": _ser(records[:inp.get("limit", 30)])}
    if name == "get_my_tasks":
        return {"tasks": _ser(task_svc.get_employee_tasks(emp.employee_id, db))}
    if name == "get_my_leaves":
        return {"leaves": _ser(leave_svc.get_employee_leaves(emp.employee_id, db))}
    if name == "get_projects":
        return {"projects": _ser(proj_svc.list_all_projects(db))}
    if name == "mark_attendance":
        rec = att_svc.do_checkin(emp.employee_id, db)
        return {"result": "Checked in successfully", "record": _ser(rec)}
    if name == "apply_leave":
        leave = leave_svc.request_leave(LeaveCreate(
            employee_id=emp.employee_id,
            leave_type=inp["leave_type"],
            leave_date=inp["leave_date"],
            day_type=inp["day_type"],
            reason=inp.get("reason"),
        ), db)
        return {"result": "Leave applied successfully", "leave": _ser(leave)}
    if name == "cancel_leave":
        leave_svc.cancel_leave(inp["leave_id"], emp.employee_id, db)
        return {"result": "Leave cancelled successfully"}
    if name == "update_task_status":
        task = task_svc.update_task_status(inp["task_id"], emp.employee_id, inp["is_completed"], db)
        return {"result": "Task updated", "task": _ser(task)}
    if name == "get_all_employees" and is_manager:
        return {"employees": _ser(db.query(EmployeeDB).all())}
    if name == "get_all_leaves" and is_manager:
        result = leave_svc.get_all_leaves(db, page=1, page_size=100, status=inp.get("status"))
        return {"leaves": result["items"]}
    if name == "approve_reject_leave" and is_manager:
        leave = leave_svc.update_leave_status(inp["leave_id"], inp["status"], db)
        return {"result": f"Leave {inp['status']}", "leave": _ser(leave)}
    if name == "get_all_attendance" and is_manager:
        result = att_svc.all_att(db, page=1, page_size=inp.get("limit", 50))
        return {"attendance": result["items"]}
    if name == "create_task" and (is_manager or is_senior):
        task = admin_tasks.create_task(TaskCreate(
            task_name=inp["task_name"], project_id=inp["project_id"],
            assigned_to=inp["assigned_to"], description=inp.get("description"),
            deadline=inp.get("deadline"), priority=inp.get("priority", "Medium"), status="To Do",
        ), db)
        return {"result": "Task created", "task": _ser(task)}
    return {"error": f"Tool '{name}' not available for your role"}


def _exec_admin_tool(name: str, inp: dict, db: Session) -> dict:
    if name == "get_projects":
        return {"projects": _ser(proj_svc.list_all_projects(db))}
    if name == "get_all_employees":
        return {"employees": _ser(db.query(EmployeeDB).all())}
    if name == "get_all_tasks":
        result = admin_tasks.list_tasks(db, page=1, page_size=100, status=inp.get("status"))
        return {"tasks": _ser(result["items"])}
    if name == "get_all_leaves":
        result = leave_svc.get_all_leaves(db, page=1, page_size=100, status=inp.get("status"))
        return {"leaves": result["items"]}
    if name == "approve_reject_leave":
        leave = leave_svc.update_leave_status(inp["leave_id"], inp["status"], db)
        return {"result": f"Leave {inp['status']}", "leave": _ser(leave)}
    if name == "get_all_attendance":
        result = att_svc.all_att(db, page=1, page_size=inp.get("limit", 50))
        return {"attendance": result["items"]}
    if name == "create_task":
        task = admin_tasks.create_task(TaskCreate(
            task_name=inp["task_name"], project_id=inp["project_id"],
            assigned_to=inp["assigned_to"], description=inp.get("description"),
            deadline=inp.get("deadline"), priority=inp.get("priority", "Medium"), status="To Do",
        ), db)
        return {"result": "Task created", "task": _ser(task)}
    return {"error": f"Unknown tool '{name}'"}


def chat_employee(messages: list, emp: EmployeeDB, db: Session) -> str:
    system = EMPLOYEE_SYSTEM.format(
        employee_name=emp.employee_name,
        role=emp.role or "employee",
        employee_id=emp.employee_id,
        today=str(date.today()),
    )
    tools = _tools_for_role(emp.role or "employee")
    return _run(messages, system, tools, lambda n, i: _exec_emp_tool(n, i, emp, db))


def chat_admin(messages: list, admin: AdminDB, db: Session) -> str:
    system = ADMIN_SYSTEM.format(
        admin_name=admin.name or admin.email,
        today=str(date.today()),
    )
    return _run(messages, system, ADMIN_TOOLS, lambda n, i: _exec_admin_tool(n, i, db))


def _run(messages: list, system: str, tools: list, executor) -> str:
    history = [{"role": "system", "content": system}]
    history += [{"role": m["role"], "content": m["content"]} for m in messages]

    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=history,
            tools=tools,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        history.append(msg)

        if resp.choices[0].finish_reason == "stop":
            return msg.content or ""

        if resp.choices[0].finish_reason == "tool_calls":
            for tc in msg.tool_calls:
                try:
                    inp = json.loads(tc.function.arguments)
                    result = executor(tc.function.name, inp)
                except Exception as e:
                    result = {"error": str(e)}
                history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
