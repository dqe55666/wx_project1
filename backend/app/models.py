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


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    service_area: Mapped[str | None] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accepted_orders: Mapped[list["CareOrder"]] = relationship(back_populates="employee")


class CareOrder(Base):
    __tablename__ = "care_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    review_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hospital_id: Mapped[int] = mapped_column(ForeignKey("hospital_units.id"))
    service_item_id: Mapped[int] = mapped_column(ForeignKey("service_items.id"))
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    hospital: Mapped[HospitalUnit] = relationship(back_populates="orders")
    service_item: Mapped[ServiceItem] = relationship(back_populates="orders")
    employee: Mapped[Employee | None] = relationship(back_populates="accepted_orders")
    review: Mapped["OrderReview | None"] = relationship(back_populates="order", uselist=False)


class OrderReview(Base):
    __tablename__ = "order_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("care_orders.id"), unique=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order: Mapped[CareOrder] = relationship(back_populates="review")
