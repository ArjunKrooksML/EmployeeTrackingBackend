from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Boolean, BigInteger, Time, Float, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from .connection import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    address = Column(Text, nullable=False)
    phone_no = Column(String(15), nullable=False)
    id_type = Column(String(50), nullable=False)
    id_number = Column(String(50), nullable=False, unique=True)
    year_joined = Column(String(10), nullable=True)
    basic = Column(Integer, nullable=False, default=0)
    da = Column(Integer, nullable=False, default=0)
    hra = Column(Integer, nullable=False, default=0)
    others = Column(Integer, nullable=False, default=0)
    # role: employee | senior | hr | gm
    role = Column(String(20), nullable=False, server_default='employee')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    client_name = Column(String(150), nullable=False)
    address = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    completion_date = Column(Date, nullable=True)
    po_prefix = Column(String(50), nullable=True)
    has_forging = Column(Boolean, nullable=False, default=False)


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    iscompleted = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(100), nullable=False, default="To Do")
    priority = Column(String(100), nullable=False, default="Medium")
    task_type = Column(String(100), nullable=True)
    tools_type = Column(String(100), nullable=True)


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    leave_type = Column(String(50), nullable=False)  # 'casual', 'sick', 'emergency'
    leave_date = Column(Date, nullable=False)
    day_type = Column(String(50), nullable=False)    # 'full', 'first_half', 'second_half'
    status = Column(String(50), nullable=False, default="pending") # 'pending', 'approved', 'rejected'
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Admin(Base):
    __tablename__ = "admin"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    attendance = Column(ENUM('pending', 'present', 'absent', 'late', name='attendance_status', create_type=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checkin = Column(Time, nullable=True)
    # GPS coordinates captured at check-in
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('employee_id', 'date', name='attendance_employee_date_unique'),)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_number = Column(String(100), nullable=False, unique=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class POItem(Base):
    __tablename__ = "po_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    size = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)


class SupplyOrder(Base):
    __tablename__ = "supply_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False)
    invoice_number = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SOItem(Base):
    __tablename__ = "so_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    so_id = Column(Integer, ForeignKey("supply_orders.id", ondelete="CASCADE"), nullable=False)
    size = Column(String(20), nullable=False)
    supplied_qty = Column(Integer, nullable=False)
    balance_qty = Column(Integer, nullable=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Text, nullable=False, unique=True, index=True)
    user_type = Column(String(20), nullable=False)  # "admin" or "employee"
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.task_id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    storage_path = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class OtpToken(Base):
    __tablename__ = "otp_tokens"

    email = Column(String(255), primary_key=True)
    otp = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class DPR(Base):
    __tablename__ = "dpr"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    mm16 = Column(Integer, nullable=True, default=0)
    mm20 = Column(Integer, nullable=True, default=0)
    mm25 = Column(Integer, nullable=True, default=0)
    mm32 = Column(Integer, nullable=True, default=0)
    forging_qty = Column(Integer, nullable=True, default=0)
    uploaded_by = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    items = Column(JSON, nullable=False)
    attachment_path = Column(Text, nullable=True)
    attachment_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default='pending')
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SalaryDeduction(Base):
    __tablename__ = "salary_deductions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id", ondelete="CASCADE"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic = Column(Integer, default=0)
    da = Column(Integer, default=0)
    hra = Column(Integer, default=0)
    others = Column(Integer, default=0)
    lates_count = Column(Integer, default=0)
    absents_from_lates = Column(Integer, default=0)
    half_day_absents = Column(Integer, default=0)
    full_absents = Column(Integer, default=0)
    paid_leave_used = Column(Boolean, default=False)
    leave_deduction = Column(Float, default=0.0)
    advance_deduction = Column(Float, default=0.0)
    total_deduction = Column(Float, default=0.0)
    gross_salary = Column(Integer, default=0)
    net_salary = Column(Float, default=0.0)
    working_days = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('employee_id', 'month', 'year', name='salary_emp_month_year_unique'),)
