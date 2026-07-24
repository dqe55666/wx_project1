from datetime import datetime

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


class EmployeeBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    phone: str = Field(min_length=6, max_length=30)
    service_area: str | None = Field(default=None, max_length=120)
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


class OrderAccept(BaseModel):
    employee_id: int


class OrderAssign(BaseModel):
    employee_id: int


class StaffLogin(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=128)


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
