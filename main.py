from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import admin_employees, admin_projects, admin_tasks, admin_auth, employees, projects, tasks, attendance, leaves, salary, orders, chat, dpr, expenses, admin_expenses, procurement, chasers
app = FastAPI(
    title="Employee Tracking System API",
    description="API for managing employees, projects, tasks, and attendance",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)
app.include_router(admin_auth.router)
app.include_router(admin_employees.router)
app.include_router(admin_projects.router)
app.include_router(admin_tasks.router)
app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(attendance.router)
app.include_router(leaves.router)
app.include_router(salary.router)
app.include_router(orders.router)
app.include_router(chat.router)
app.include_router(dpr.router)
app.include_router(expenses.router)
app.include_router(admin_expenses.router)
app.include_router(procurement.router)
app.include_router(chasers.router)


@app.get("/")
async def root():
    return {"message": "Employee Tracking System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

