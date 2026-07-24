import hashlib
import hmac
import secrets
import time
from datetime import datetime
from pathlib import Path
from random import randint

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .amap import reverse_geocode, search_hospitals
from .config import settings
from .database import Base, SessionLocal, engine, get_db, upgrade_schema
from .geo import haversine_km
from .models import CareOrder, Employee, HospitalUnit, ServiceItem
from .schemas import (
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    HospitalCreate,
    HospitalOut,
    HospitalUpdate,
    OrderCreate,
    OrderAccept,
    OrderAssign,
    OrderOut,
    ServiceItemOut,
    StaffLogin,
)

app = FastAPI(title=settings.app_name)
staff_auth = HTTPBearer(auto_error=False)

origins = ["*"] if settings.cors_origins == "*" else settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/admin", StaticFiles(directory=static_dir / "admin", html=True), name="admin")
app.mount("/staff", StaticFiles(directory=static_dir / "staff", html=True), name="staff")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    upgrade_schema()
    with SessionLocal() as db:
        seed_data(db)


def seed_data(db: Session):
    if db.query(ServiceItem).count() == 0:
        db.add_all(
            [
                ServiceItem(
                    name="基础陪护",
                    description="院内陪诊、取号、检查陪同",
                    price_cents=9800,
                    duration_minutes=180,
                ),
                ServiceItem(
                    name="术后护理",
                    description="术后观察、基础生活照护",
                    price_cents=19800,
                    duration_minutes=240,
                ),
            ]
        )
    if db.query(HospitalUnit).count() == 0:
        db.add_all(
            [
                HospitalUnit(
                    name="示例医院护理站",
                    address="上海市黄浦区人民大道 100 号",
                    latitude=31.2304,
                    longitude=121.4737,
                    phone="021-12345678",
                    service_radius_km=20,
                )
            ]
        )
    if db.query(Employee).count() == 0:
        db.add_all(
            [
                Employee(
                    name="张护理",
                    username="张护理",
                    password_hash=hash_password("123456"),
                    phone="13800000001",
                    service_area="黄浦区",
                ),
                Employee(
                    name="李陪诊",
                    username="李陪诊",
                    password_hash=hash_password("123456"),
                    phone="13800000002",
                    service_area="徐汇区",
                ),
            ]
        )
    for employee in db.query(Employee).all():
        if not employee.username:
            employee.username = employee.name
        if not employee.password_hash:
            employee.password_hash = hash_password("123456")
    db.commit()


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored_hash)


def create_staff_token(employee_id: int) -> str:
    expires_at = int(time.time()) + settings.staff_token_expire_seconds
    payload = f"{employee_id}.{expires_at}"
    signature = hmac.new(
        settings.staff_token_secret.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    return f"{payload}.{signature}"


def require_staff(
    credentials: HTTPAuthorizationCredentials | None = Depends(staff_auth),
    db: Session = Depends(get_db),
) -> Employee:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    try:
        employee_id_text, expires_at_text, signature = credentials.credentials.split(".")
        payload = f"{employee_id_text}.{expires_at_text}"
        expected_signature = hmac.new(
            settings.staff_token_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature) or int(expires_at_text) < time.time():
            raise ValueError
        employee = db.get(Employee, int(employee_id_text))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态已失效")
    if not employee or not employee.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="员工账号不可用")
    return employee


def hospital_to_out(hospital: HospitalUnit, lat: float | None, lng: float | None):
    distance = None
    if lat is not None and lng is not None:
        distance = haversine_km(lat, lng, float(hospital.latitude), float(hospital.longitude))
    return HospitalOut.model_validate(hospital).model_copy(update={"distance_km": distance})


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/")
def root():
    return {"name": settings.app_name, "admin": "/admin/", "health": "/api/health"}


@app.get("/api/hospitals", response_model=list[HospitalOut])
def list_hospitals(
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(HospitalUnit)
    if not include_inactive:
        query = query.filter(HospitalUnit.is_active.is_(True))
    hospitals = [hospital_to_out(item, lat, lng) for item in query.all()]
    if lat is not None and lng is not None:
        hospitals.sort(key=lambda item: item.distance_km if item.distance_km is not None else 999999)
    return hospitals


@app.get("/api/location/regeo")
def regeo_location(lat: float = Query(...), lng: float = Query(...)):
    return reverse_geocode(lat, lng)


@app.get("/api/amap/hospitals")
def search_amap_hospitals(
    keyword: str | None = Query(default=None),
    lat: float | None = Query(default=None),
    lng: float | None = Query(default=None),
    radius_km: int = Query(default=30, ge=1, le=50),
):
    return search_hospitals(
        keyword=keyword,
        lat=lat,
        lng=lng,
        radius_m=radius_km * 1000,
    )


@app.post("/api/admin/hospitals", response_model=HospitalOut)
def create_hospital(payload: HospitalCreate, db: Session = Depends(get_db)):
    hospital = HospitalUnit(**payload.model_dump())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital_to_out(hospital, None, None)


@app.put("/api/admin/hospitals/{hospital_id}", response_model=HospitalOut)
def update_hospital(
    hospital_id: int,
    payload: HospitalUpdate,
    db: Session = Depends(get_db),
):
    hospital = db.get(HospitalUnit, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="医院单位不存在")
    for key, value in payload.model_dump().items():
        setattr(hospital, key, value)
    db.commit()
    db.refresh(hospital)
    return hospital_to_out(hospital, None, None)


@app.delete("/api/admin/hospitals/{hospital_id}")
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = db.get(HospitalUnit, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="医院单位不存在")
    hospital.is_active = False
    db.commit()
    return {"ok": True}


@app.get("/api/services", response_model=list[ServiceItemOut])
def list_services(db: Session = Depends(get_db)):
    return db.query(ServiceItem).filter(ServiceItem.is_active.is_(True)).all()


@app.get("/api/employees", response_model=list[EmployeeOut])
def list_active_employees(db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.is_active.is_(True)).order_by(Employee.id).all()


@app.get("/api/admin/employees", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).order_by(Employee.created_at.desc()).all()


@app.post("/api/admin/employees", response_model=EmployeeOut)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="该联系电话已存在")
    if db.query(Employee).filter(Employee.username == payload.name).first():
        raise HTTPException(status_code=400, detail="员工姓名已被用作登录账号")
    employee = Employee(
        **payload.model_dump(),
        username=payload.name,
        password_hash=hash_password("123456"),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@app.put("/api/admin/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    duplicate = db.query(Employee).filter(Employee.phone == payload.phone, Employee.id != employee_id).first()
    if duplicate:
        raise HTTPException(status_code=400, detail="该联系电话已存在")
    username_conflict = (
        db.query(Employee)
        .filter(Employee.username == payload.name, Employee.id != employee_id)
        .first()
    )
    if username_conflict:
        raise HTTPException(status_code=400, detail="员工姓名已被用作登录账号")
    for key, value in payload.model_dump().items():
        setattr(employee, key, value)
    employee.username = payload.name
    db.commit()
    db.refresh(employee)
    return employee


@app.delete("/api/admin/employees/{employee_id}")
def deactivate_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    employee.is_active = False
    db.commit()
    return {"ok": True}


def order_to_dict(order: CareOrder):
    return {
        "id": order.id,
        "order_no": order.order_no,
        "patient_name": order.patient_name,
        "patient_phone": order.patient_phone,
        "hospital_name": order.hospital.name,
        "service_name": order.service_item.name,
        "appointment_time": order.appointment_time.isoformat(),
        "address_detail": order.address_detail,
        "distance_km": float(order.distance_km) if order.distance_km is not None else None,
        "note": order.note,
        "status": order.status,
        "employee_id": order.employee_id,
        "employee_name": order.employee.name if order.employee else None,
        "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
        "started_at": order.started_at.isoformat() if order.started_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "stopped_at": order.stopped_at.isoformat() if order.stopped_at else None,
        "created_at": order.created_at.isoformat(),
    }


@app.get("/api/admin/orders")
def list_orders(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    orders = db.query(CareOrder).order_by(CareOrder.created_at.desc()).limit(limit).all()
    return [order_to_dict(order) for order in orders]


def get_orders_for_employee(employee: Employee, order_status: str, db: Session, limit: int):
    query = db.query(CareOrder)
    if order_status == "pending":
        query = query.filter(CareOrder.status == "pending")
    elif order_status in {"accepted", "in_progress", "completed", "stopped"}:
        query = query.filter(CareOrder.status == order_status, CareOrder.employee_id == employee.id)
    else:
        query = query.filter(
            or_(CareOrder.status == "pending", CareOrder.employee_id == employee.id)
        )
    return [
        order_to_dict(order)
        for order in query.order_by(CareOrder.appointment_time.asc()).limit(limit).all()
    ]


def claim_order(order_id: int, employee: Employee, db: Session):
    updated = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.status == "pending", CareOrder.employee_id.is_(None))
        .update(
            {
                CareOrder.employee_id: employee.id,
                CareOrder.status: "accepted",
                CareOrder.accepted_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="该订单已被其他员工接走或不存在")
    db.commit()
    return db.get(CareOrder, order_id)


@app.post("/api/staff/login")
def staff_login(payload: StaffLogin, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.username == payload.username).first()
    if not employee or not employee.is_active or not verify_password(payload.password, employee.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    return {
        "access_token": create_staff_token(employee.id),
        "token_type": "bearer",
        "employee": {"id": employee.id, "name": employee.name, "service_area": employee.service_area},
    }


@app.get("/api/staff/me")
def staff_me(employee: Employee = Depends(require_staff)):
    return {"id": employee.id, "name": employee.name, "service_area": employee.service_area}


@app.get("/api/staff/orders")
def staff_orders(
    order_status: str = Query(
        default="pending",
        alias="status",
        pattern="^(all|pending|accepted|in_progress|completed|stopped)$",
    ),
    limit: int = Query(default=50, ge=1, le=200),
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    return get_orders_for_employee(employee, order_status, db, limit)


@app.post("/api/staff/orders/{order_id}/accept")
def staff_accept_order(
    order_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    return order_to_dict(claim_order(order_id, employee, db))


@app.post("/api/staff/orders/{order_id}/start")
def staff_start_order(
    order_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    updated = (
        db.query(CareOrder)
        .filter(
            CareOrder.id == order_id,
            CareOrder.employee_id == employee.id,
            CareOrder.status == "accepted",
        )
        .update(
            {CareOrder.status: "in_progress", CareOrder.started_at: datetime.utcnow()},
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="该订单尚未由你接单，或已开始工作")
    db.commit()
    return order_to_dict(db.get(CareOrder, order_id))


@app.post("/api/staff/orders/{order_id}/finish")
def staff_finish_order(
    order_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    updated = (
        db.query(CareOrder)
        .filter(
            CareOrder.id == order_id,
            CareOrder.employee_id == employee.id,
            CareOrder.status == "in_progress",
        )
        .update(
            {CareOrder.status: "completed", CareOrder.completed_at: datetime.utcnow()},
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="该订单当前不能结束工作")
    db.commit()
    return order_to_dict(db.get(CareOrder, order_id))


@app.post("/api/admin/orders/{order_id}/assign")
def admin_assign_order(
    order_id: int, payload: OrderAssign, db: Session = Depends(get_db)
):
    employee = db.get(Employee, payload.employee_id)
    if not employee or not employee.is_active:
        raise HTTPException(status_code=400, detail="请选择有效员工")
    updated = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.status.in_(["pending", "accepted"]))
        .update(
            {
                CareOrder.employee_id: employee.id,
                CareOrder.status: "accepted",
                CareOrder.accepted_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="仅待接单或已接单的订单可以指定员工")
    db.commit()
    return order_to_dict(db.get(CareOrder, order_id))


def admin_close_order(order_id: int, target_status: str, db: Session):
    timestamp_column = CareOrder.completed_at if target_status == "completed" else CareOrder.stopped_at
    updated = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.status.notin_(["completed", "stopped"]))
        .update(
            {CareOrder.status: target_status, timestamp_column: datetime.utcnow()},
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="该订单已结束或不存在")
    db.commit()
    return order_to_dict(db.get(CareOrder, order_id))


@app.post("/api/admin/orders/{order_id}/finish")
def admin_finish_order(order_id: int, db: Session = Depends(get_db)):
    return admin_close_order(order_id, "completed", db)


@app.post("/api/admin/orders/{order_id}/stop")
def admin_stop_order(order_id: int, db: Session = Depends(get_db)):
    return admin_close_order(order_id, "stopped", db)


@app.get("/api/employee/orders")
def list_employee_orders(
    employee_id: int = Query(...),
    status: str = Query(default="all", pattern="^(all|pending|accepted)$"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)
    if not employee or not employee.is_active:
        raise HTTPException(status_code=400, detail="请选择有效员工")
    return get_orders_for_employee(employee, status, db, limit)


@app.post("/api/employee/orders/{order_id}/accept")
def accept_order(order_id: int, payload: OrderAccept, db: Session = Depends(get_db)):
    employee = db.get(Employee, payload.employee_id)
    if not employee or not employee.is_active:
        raise HTTPException(status_code=400, detail="请选择有效员工")
    return order_to_dict(claim_order(order_id, employee, db))


@app.post("/api/orders", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    hospital = db.get(HospitalUnit, payload.hospital_id)
    if not hospital or not hospital.is_active:
        raise HTTPException(status_code=400, detail="请选择有效医院单位")

    service_item = db.get(ServiceItem, payload.service_item_id)
    if not service_item or not service_item.is_active:
        raise HTTPException(status_code=400, detail="请选择有效服务项目")

    distance = None
    if payload.latitude is not None and payload.longitude is not None:
        distance = haversine_km(
            payload.latitude,
            payload.longitude,
            float(hospital.latitude),
            float(hospital.longitude),
        )

    order = CareOrder(
        **payload.model_dump(),
        order_no=f"CO{datetime.utcnow():%Y%m%d%H%M%S}{randint(1000, 9999)}",
        distance_km=distance,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
