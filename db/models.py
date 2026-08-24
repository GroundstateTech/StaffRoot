from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(24), nullable=False, default="EMPLOYEE")
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    admin_center_user_id = Column(String(128), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="user_account")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    admin_center_employee_id = Column(String(128), nullable=True, index=True)
    source_system = Column(String(64), default="local")
    last_synced_at = Column(DateTime, nullable=True)

    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(160), nullable=True, index=True)
    phone = Column(String(40), nullable=True)

    address_line1 = Column(String(180), nullable=True)
    address_line2 = Column(String(180), nullable=True)
    city = Column(String(80), nullable=True)
    state = Column(String(40), nullable=True)
    postal_code = Column(String(24), nullable=True)
    country = Column(String(80), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    hire_date = Column(Date, nullable=True)
    status = Column(String(40), default="Active")
    ssn_last4 = Column(String(4), nullable=True)

    emergency_contact_name = Column(String(160), nullable=True)
    emergency_contact_phone = Column(String(40), nullable=True)

    user_account = relationship("User", back_populates="employee", uselist=False)
    job_detail = relationship("JobDetail", back_populates="employee", uselist=False, cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="employee", cascade="all, delete-orphan")
    payroll_items = relationship("PayrollItem", back_populates="employee")

class JobDetail(Base):
    __tablename__ = "job_details"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    department = Column(String(100), nullable=True)
    position_title = Column(String(160), nullable=True)
    employment_type = Column(String(60), default="Full-time")
    pay_type = Column(String(24), default="HOURLY")
    base_rate = Column(Numeric(10, 2), default=0)
    pay_schedule = Column(String(60), default="Bi-weekly")

    employee = relationship("Employee", back_populates="job_detail")

class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    work_date = Column(Date, nullable=False)
    hours_regular = Column(Numeric(6, 2), default=0)
    hours_overtime = Column(Numeric(6, 2), default=0)
    notes = Column(String(255), nullable=True)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="time_entries")

class PayPeriod(Base):
    __tablename__ = "pay_periods"

    id = Column(Integer, primary_key=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    pay_date = Column(Date, nullable=False)
    description = Column(String(160), nullable=True)

    runs = relationship("PayrollRun", back_populates="pay_period", cascade="all, delete-orphan")

class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True)
    pay_period_id = Column(Integer, ForeignKey("pay_periods.id"), nullable=False)
    run_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(40), default="DRAFT")
    notes = Column(Text, nullable=True)

    pay_period = relationship("PayPeriod", back_populates="runs")
    items = relationship("PayrollItem", back_populates="run", cascade="all, delete-orphan")

class PayrollItem(Base):
    __tablename__ = "payroll_items"

    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    hours_regular = Column(Numeric(6, 2), default=0)
    hours_overtime = Column(Numeric(6, 2), default=0)
    gross_pay = Column(Numeric(12, 2), default=0)
    net_pay = Column(Numeric(12, 2), default=0)
    taxes = Column(Numeric(12, 2), default=0)
    deductions = Column(Numeric(12, 2), default=0)

    employee = relationship("Employee", back_populates="payroll_items")
    run = relationship("PayrollRun", back_populates="items")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(128), nullable=False)
    details = Column(Text, nullable=True)

class AppMeta(Base):
    __tablename__ = "app_meta"

    key = Column(String(80), primary_key=True)
    value = Column(String(255), nullable=True)
