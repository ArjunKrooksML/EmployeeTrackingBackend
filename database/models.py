from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Boolean, BigInteger, Time, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM
from .connection import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    dob = Column(Date, nullable=False)
    address = Column(Text, nullable=False)
    phone_no = Column(String(15), nullable=False)
    id_type = Column(String(50), nullable=False)
    id_number = Column(String(50), nullable=False)
    designation_id = Column(Integer, nullable=True)
    year_joined = Column(String(10), nullable=True)
    salary = Column(Integer, nullable=False)
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

    task_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, nullable=False)
    task_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(String(150), nullable=True)
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    iscompleted = Column(Boolean, nullable=False, server_default="false")
    created = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(100), nullable=False)
    priority = Column(String(100), nullable=False)


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
    attendance = Column(ENUM('present', 'absent', 'late', name='attendance_status', create_type=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checkin = Column(Time, nullable=True)

    __table_args__ = (UniqueConstraint('employee_id', 'date', name='attendance_employee_date_unique'),)
