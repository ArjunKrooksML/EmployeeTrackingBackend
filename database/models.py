from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Boolean, BigInteger, Time, Float, ForeignKey, UniqueConstraint
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
    salary = Column(Integer, nullable=False)
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


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("employees.employee_id"), nullable=True)
    status = Column(String(50), nullable=False, default="To Do")
    priority = Column(String(50), nullable=False, default="Medium")
    target_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    date = Column(Date, nullable=False)
    attendance = Column(ENUM('pending', 'present', 'absent', 'late', name='attendance_status', create_type=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checkin = Column(Time, nullable=True)
    # GPS coordinates captured at check-in
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('employee_id', 'date', name='attendance_employee_date_unique'),)
