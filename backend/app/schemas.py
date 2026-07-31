from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HospitalBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=2, max_length=255)
    latitude: float
    longitude: float
    phone: str | None = None
    service_radius_km: int = Field(default=15, ge=1, le=200)
    is_active: bool = True


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(HospitalBase):
    pass


class HospitalOut(HospitalBase):
    id: int
    distance_km: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ServiceItemOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    price_cents: int
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=1000)
    price_cents: int = Field(ge=1, le=100000000)
    stock: int = Field(ge=0, le=1000000)
    cover: str = Field(default="📦", min_length=1, max_length=20)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    sales_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MallOrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class EmployeeBase(BaseModel):
    employee_code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=50)
    phone: str = Field(min_length=6, max_length=30)
    service_area: str | None = Field(default=None, max_length=120)
    role: Literal["caregiver", "customer_service"] = "caregiver"
    commission_rate: float = Field(default=85, ge=0, le=100)
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass


class EmployeeOut(EmployeeBase):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderAssign(BaseModel):
    employee_id: int


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=1000)


class ReviewUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class StaffLogin(BaseModel):
    employee_id: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class EarlyFinishResponse(BaseModel):
    approved: bool


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class ForceStopCreate(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class SupportTicketCreate(BaseModel):
    category: Literal["support", "feedback"] = "support"
    subject: str | None = Field(default=None, max_length=120)
    content: str = Field(min_length=1, max_length=1000)
    customer_name: str = Field(default="小陪用户", min_length=1, max_length=50)
    customer_avatar: str | None = Field(default=None, max_length=500)


class BottleCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    author_name: str = Field(default="小陪用户", min_length=1, max_length=50)
    author_avatar: str | None = Field(default=None, max_length=500)
    is_anonymous: bool = False


class BottleOut(BaseModel):
    id: int
    content: str
    author_name: str
    author_avatar: str | None = None
    is_anonymous: bool
    status: str
    created_at: datetime


class BottleSettingsUpdate(BaseModel):
    review_enabled: bool


class BottleSettingsOut(BaseModel):
    review_enabled: bool


class OrderCreate(BaseModel):
    hospital_id: int
    service_item_id: int
    patient_name: str = Field(min_length=2, max_length=50)
    patient_phone: str = Field(min_length=6, max_length=30)
    appointment_time: datetime
    address_detail: str = Field(min_length=3, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    note: str | None = None


class OrderOut(BaseModel):
    id: int
    order_no: str
    review_token: str
    hospital_id: int
    service_item_id: int
    patient_name: str
    patient_phone: str
    appointment_time: datetime
    address_detail: str
    distance_km: float | None = None
    note: str | None = None
    status: str
    employee_id: int | None = None
    accepted_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    stopped_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
