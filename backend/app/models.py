from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class HospitalUnit(Base):
    __tablename__ = "hospital_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    service_radius_km: Mapped[int] = mapped_column(Integer, default=15)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders: Mapped[list["CareOrder"]] = relationship(back_populates="hospital")


class ServiceItem(Base):
    __tablename__ = "service_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=120)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    orders: Mapped[list["CareOrder"]] = relationship(back_populates="service_item")


class Customer(Base):
    """Persisted customer account/profile keyed by verified contact phone."""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    orders: Mapped[list["CareOrder"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(50), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sales_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cover: Mapped[str] = mapped_column(String(20), nullable=False, default="📦")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class MallOrder(Base):
    __tablename__ = "mall_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    access_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    product_cover: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending_payment", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    service_area: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="caregiver", index=True)
    commission_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=85.00)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accepted_orders: Mapped[list["CareOrder"]] = relationship(back_populates="employee")
    income_records: Mapped[list["EmployeeIncomeRecord"]] = relationship(back_populates="employee")


class CareOrder(Base):
    __tablename__ = "care_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    review_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospital_units.id"))
    service_item_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"))
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), index=True)
    patient_name: Mapped[str] = mapped_column(String(50), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    appointment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    address_detail: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    customer_location_updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    distance_km: Mapped[float | None] = mapped_column(Numeric(8, 2))
    note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), index=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime)
    staff_latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    staff_longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    staff_location_updated_at: Mapped[datetime | None] = mapped_column(DateTime)
    early_finish_requested_at: Mapped[datetime | None] = mapped_column(DateTime)
    early_finish_response: Mapped[bool | None] = mapped_column(Boolean)
    early_finish_responded_at: Mapped[datetime | None] = mapped_column(DateTime)
    commission_rate: Mapped[float | None] = mapped_column(Numeric(5, 2))
    staff_earning_cents: Mapped[int | None] = mapped_column(Integer)
    completion_type: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    hospital: Mapped[HospitalUnit] = relationship(back_populates="orders")
    service_item: Mapped[ServiceItem] = relationship(back_populates="orders")
    customer: Mapped[Customer | None] = relationship(back_populates="orders")
    employee: Mapped[Employee | None] = relationship(back_populates="accepted_orders")
    review: Mapped["OrderReview | None"] = relationship(back_populates="order", uselist=False)
    messages: Mapped[list["OrderMessage"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    income_record: Mapped["EmployeeIncomeRecord | None"] = relationship(
        back_populates="order", uselist=False
    )


class OrderReview(Base):
    __tablename__ = "order_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("care_orders.id"), unique=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped[CareOrder] = relationship(back_populates="review")


class OrderMessage(Base):
    __tablename__ = "order_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("care_orders.id"), index=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sender_id: Mapped[int | None] = mapped_column(Integer)
    sender_name: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    order: Mapped[CareOrder] = relationship(back_populates="messages")


class EmployeeIncomeRecord(Base):
    __tablename__ = "employee_income_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("care_orders.id"), nullable=False, unique=True, index=True
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="available", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    employee: Mapped[Employee] = relationship(back_populates="income_records")
    order: Mapped[CareOrder] = relationship(back_populates="income_record")


class BottleSettings(Base):
    __tablename__ = "bottle_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class DriftBottle(Base):
    __tablename__ = "drift_bottles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False, default="小陪用户")
    author_avatar: Mapped[str | None] = mapped_column(String(500))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="published", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    access_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="support", index=True)
    subject: Mapped[str | None] = mapped_column(String(120))
    customer_name: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_avatar: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    service_employee_id: Mapped[int | None] = mapped_column(ForeignKey("employees.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    service_employee: Mapped[Employee | None] = relationship(foreign_keys=[service_employee_id])
    messages: Mapped[list["SupportMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    sender_id: Mapped[int | None] = mapped_column(Integer)
    sender_name: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    ticket: Mapped[SupportTicket] = relationship(back_populates="messages")
