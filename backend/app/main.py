import hashlib
import hmac
import secrets
import time
from datetime import datetime
from pathlib import Path
from random import randint

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .amap import reverse_geocode, search_hospitals, static_map
from .config import settings
from .database import Base, SessionLocal, engine, get_db, upgrade_schema
from .geo import haversine_km
from .models import (
    BottleSettings,
    CareOrder,
    DriftBottle,
    Employee,
    EmployeeIncomeRecord,
    HospitalUnit,
    MallOrder,
    OrderMessage,
    OrderReview,
    Product,
    ServiceItem,
    SupportMessage,
    SupportTicket,
)
from .schemas import (
    BottleCreate,
    BottleOut,
    BottleSettingsOut,
    BottleSettingsUpdate,
    EmployeeCreate,
    EmployeeOut,
    EmployeeUpdate,
    EarlyFinishResponse,
    ForceStopCreate,
    HospitalCreate,
    HospitalOut,
    HospitalUpdate,
    LocationUpdate,
    MallOrderCreate,
    MessageCreate,
    OrderCreate,
    OrderAssign,
    OrderOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    ReviewCreate,
    ReviewUpdate,
    ServiceItemOut,
    StaffLogin,
    SupportTicketCreate,
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
app.mount("/support", StaticFiles(directory=static_dir / "support", html=True), name="support")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    upgrade_schema()
    with SessionLocal() as db:
        seed_data(db)


def seed_data(db: Session):
    if not db.get(BottleSettings, 1):
        db.add(BottleSettings(id=1, review_enabled=False))
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
    if db.query(Product).count() == 0:
        db.add_all(
            [
                Product(
                    name="医用护理床",
                    category="康复器械",
                    description="家用多功能护理床，可摇起、摇落、翻身，方便照顾卧床老人。",
                    price_cents=188000,
                    stock=18,
                    sales_count=326,
                    cover="🛏️",
                ),
                Product(
                    name="血压计（家用手腕式）",
                    category="护理用品",
                    description="一键测量，清晰大屏显示，适合居家日常监测。",
                    price_cents=26800,
                    stock=56,
                    sales_count=1280,
                    cover="🩺",
                ),
                Product(
                    name="成人纸尿裤 L 码",
                    category="日常防护",
                    description="柔软透气，高吸收量，适合日常护理使用。",
                    price_cents=8900,
                    stock=120,
                    sales_count=956,
                    cover="🧻",
                ),
                Product(
                    name="可折叠助行器",
                    category="康复器械",
                    description="轻便可折叠，稳固防滑，辅助日常行走训练。",
                    price_cents=19800,
                    stock=32,
                    sales_count=412,
                    cover="🦯",
                ),
            ]
        )
    if db.query(Employee).count() == 0:
        db.add_all(
            [
                Employee(
                    employee_code="YG1001",
                    name="张护理",
                    username="张护理",
                    password_hash=hash_password("123456"),
                    phone="13800000001",
                    service_area="黄浦区",
                    role="caregiver",
                ),
                Employee(
                    employee_code="YG1002",
                    name="李陪诊",
                    username="李陪诊",
                    password_hash=hash_password("123456"),
                    phone="13800000002",
                    service_area="徐汇区",
                    role="caregiver",
                ),
            ]
        )
    if not db.query(Employee).filter(Employee.employee_code == "KF1001").first():
        db.add(
            Employee(
                employee_code="KF1001",
                name="客服小周",
                username="KF1001",
                password_hash=hash_password("123456"),
                phone="13800000003",
                service_area="在线客服",
                role="customer_service",
                commission_rate=0,
            )
        )
    for employee in db.query(Employee).all():
        if not employee.employee_code:
            employee.employee_code = f"YG{employee.id:04d}"
        if not employee.username:
            employee.username = employee.employee_code
        if not employee.password_hash:
            employee.password_hash = hash_password("123456")
        if employee.commission_rate is None:
            employee.commission_rate = 85
        if not employee.role:
            employee.role = "caregiver"
    for order in db.query(CareOrder).all():
        if not order.review_token:
            order.review_token = secrets.token_urlsafe(24)
    backfill_income_records(db)
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


def get_bottle_settings(db: Session) -> BottleSettings:
    settings_record = db.get(BottleSettings, 1)
    if settings_record:
        return settings_record
    settings_record = BottleSettings(id=1, review_enabled=False)
    db.add(settings_record)
    db.commit()
    db.refresh(settings_record)
    return settings_record


def bottle_to_dict(bottle: DriftBottle):
    is_anonymous = bool(bottle.is_anonymous)
    return {
        "id": bottle.id,
        "content": bottle.content,
        "author_name": "匿名漂流者" if is_anonymous else bottle.author_name,
        "author_avatar": None if is_anonymous else bottle.author_avatar,
        "is_anonymous": is_anonymous,
        "status": bottle.status,
        "created_at": bottle.created_at,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/api/bottles", response_model=list[BottleOut])
def list_bottles(
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
):
    bottles = (
        db.query(DriftBottle)
        .filter(DriftBottle.status == "published")
        .order_by(DriftBottle.created_at.desc(), DriftBottle.id.desc())
        .limit(limit)
        .all()
    )
    return [bottle_to_dict(bottle) for bottle in bottles]


@app.post("/api/bottles", response_model=BottleOut)
def create_bottle(payload: BottleCreate, db: Session = Depends(get_db)):
    settings_record = get_bottle_settings(db)
    bottle = DriftBottle(
        content=payload.content.strip(),
        author_name=payload.author_name.strip() or "小陪用户",
        author_avatar=payload.author_avatar,
        is_anonymous=payload.is_anonymous,
        status="pending" if settings_record.review_enabled else "published",
    )
    db.add(bottle)
    db.commit()
    db.refresh(bottle)
    return bottle_to_dict(bottle)


@app.get("/api/admin/bottles/settings", response_model=BottleSettingsOut)
def get_admin_bottle_settings(db: Session = Depends(get_db)):
    settings_record = get_bottle_settings(db)
    return {"review_enabled": settings_record.review_enabled}


@app.put("/api/admin/bottles/settings", response_model=BottleSettingsOut)
def update_admin_bottle_settings(
    payload: BottleSettingsUpdate, db: Session = Depends(get_db)
):
    settings_record = get_bottle_settings(db)
    settings_record.review_enabled = payload.review_enabled
    db.commit()
    return {"review_enabled": settings_record.review_enabled}


@app.get("/api/admin/bottles", response_model=list[BottleOut])
def list_admin_bottles(
    review_status: str | None = Query(default=None, pattern="^(pending|published)$"),
    limit: int = Query(default=500, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(DriftBottle)
    if review_status:
        query = query.filter(DriftBottle.status == review_status)
    bottles = query.order_by(DriftBottle.created_at.desc(), DriftBottle.id.desc()).limit(limit).all()
    return [bottle_to_dict(bottle) for bottle in bottles]


@app.post("/api/admin/bottles/{bottle_id}/publish", response_model=BottleOut)
def publish_bottle(bottle_id: int, db: Session = Depends(get_db)):
    bottle = db.get(DriftBottle, bottle_id)
    if not bottle:
        raise HTTPException(status_code=404, detail="漂流瓶不存在")
    bottle.status = "published"
    db.commit()
    db.refresh(bottle)
    return bottle_to_dict(bottle)


@app.delete("/api/admin/bottles/{bottle_id}")
def delete_bottle(bottle_id: int, db: Session = Depends(get_db)):
    bottle = db.get(DriftBottle, bottle_id)
    if not bottle:
        raise HTTPException(status_code=404, detail="漂流瓶不存在")
    db.delete(bottle)
    db.commit()
    return {"ok": True}


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


@app.get("/api/products", response_model=list[ProductOut])
def list_products(
    keyword: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=50),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active.is_(True))
    if keyword and keyword.strip():
        query = query.filter(Product.name.contains(keyword.strip()))
    if category and category.strip():
        query = query.filter(Product.category == category.strip())
    return query.order_by(Product.sales_count.desc(), Product.created_at.desc()).all()


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active.is_(True)).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")
    return product


def mall_order_to_dict(order: MallOrder, include_token: bool = False):
    data = {
        "id": order.id,
        "order_no": order.order_no,
        "product_id": order.product_id,
        "product_name": order.product_name,
        "product_cover": order.product_cover,
        "unit_price_cents": order.unit_price_cents,
        "quantity": order.quantity,
        "amount_cents": order.amount_cents,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }
    if include_token:
        data["access_token"] = order.access_token
    return data


def get_mall_order(order_id: int, access_token: str, db: Session) -> MallOrder:
    order = (
        db.query(MallOrder)
        .filter(MallOrder.id == order_id, MallOrder.access_token == access_token)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="商城订单不存在或访问凭据无效")
    return order


@app.post("/api/mall/orders")
def create_mall_order(payload: MallOrderCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == payload.product_id, Product.is_active.is_(True)).first()
    if not product or product.stock < payload.quantity:
        raise HTTPException(status_code=409, detail="商品已下架或库存不足")
    order = MallOrder(
        order_no=f"MO{datetime.utcnow():%Y%m%d%H%M%S}{randint(1000, 9999)}",
        access_token=secrets.token_urlsafe(24),
        product_id=product.id,
        product_name=product.name,
        product_cover=product.cover,
        unit_price_cents=product.price_cents,
        quantity=payload.quantity,
        amount_cents=product.price_cents * payload.quantity,
        status="pending_payment",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return mall_order_to_dict(order, include_token=True)


@app.get("/api/mall/orders/{order_id}")
def get_mall_order_status(
    order_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    return mall_order_to_dict(get_mall_order(order_id, token, db))


@app.post("/api/mall/orders/{order_id}/pay")
def pay_mall_order(
    order_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = (
        db.query(MallOrder)
        .filter(MallOrder.id == order_id, MallOrder.access_token == token)
        .with_for_update()
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="商城订单不存在或访问凭据无效")
    if order.status == "paid":
        return mall_order_to_dict(order)
    updated = (
        db.query(Product)
        .filter(
            Product.id == order.product_id,
            Product.is_active.is_(True),
            Product.stock >= order.quantity,
        )
        .update(
            {
                Product.stock: Product.stock - order.quantity,
                Product.sales_count: Product.sales_count + order.quantity,
            },
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(status_code=409, detail="商品已下架或库存不足")
    order.status = "paid"
    order.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return mall_order_to_dict(order)


@app.get("/api/admin/products", response_model=list[ProductOut])
def list_admin_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.created_at.desc()).all()


@app.post("/api/admin/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/admin/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/admin/products/{product_id}")
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    product.is_active = False
    db.commit()
    return {"ok": True}


@app.get("/api/admin/employees", response_model=list[EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(Employee).order_by(Employee.created_at.desc()).all()


@app.post("/api/admin/employees", response_model=EmployeeOut)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.phone == payload.phone).first():
        raise HTTPException(status_code=400, detail="该联系电话已存在")
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="员工 ID 已存在")
    employee = Employee(
        **payload.model_dump(),
        username=payload.employee_code,
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
    employee_code_conflict = (
        db.query(Employee)
        .filter(Employee.employee_code == payload.employee_code, Employee.id != employee_id)
        .first()
    )
    if employee_code_conflict:
        raise HTTPException(status_code=400, detail="员工 ID 已存在")
    for key, value in payload.model_dump().items():
        setattr(employee, key, value)
    employee.username = payload.employee_code
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


def order_status_text(order: CareOrder) -> str:
    if order.completion_type == "negotiated_early":
        return "经协商提前结束"
    if order.completion_type == "system_confirmed":
        return "由系统确认，订单结束"
    return {
        "pending": "待接单",
        "accepted": "已接单",
        "in_progress": "工作中",
        "completed": "服务已完成",
        "stopped": "订单已停止",
    }.get(order.status, order.status)


def order_to_dict(order: CareOrder):
    return {
        "id": order.id,
        "order_no": order.order_no,
        "patient_name": order.patient_name,
        "patient_phone": order.patient_phone,
        "hospital_name": order.hospital.name,
        "service_name": order.service_item.name,
        "service_price_cents": order.service_item.price_cents,
        "service_duration_minutes": order.service_item.duration_minutes,
        "appointment_time": order.appointment_time.isoformat(),
        "address_detail": order.address_detail,
        "latitude": float(order.latitude) if order.latitude is not None else None,
        "longitude": float(order.longitude) if order.longitude is not None else None,
        "customer_location_updated_at": (
            order.customer_location_updated_at.isoformat()
            if order.customer_location_updated_at
            else None
        ),
        "distance_km": float(order.distance_km) if order.distance_km is not None else None,
        "note": order.note,
        "status": order.status,
        "status_text": order_status_text(order),
        "completion_type": order.completion_type,
        "employee_id": order.employee_id,
        "employee_code": order.employee.employee_code if order.employee else None,
        "employee_name": order.employee.name if order.employee else None,
        "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
        "started_at": order.started_at.isoformat() if order.started_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "stopped_at": order.stopped_at.isoformat() if order.stopped_at else None,
        "staff_location_updated_at": (
            order.staff_location_updated_at.isoformat() if order.staff_location_updated_at else None
        ),
        "early_finish_pending": bool(
            order.early_finish_requested_at and order.early_finish_response is None
        ),
        "commission_rate": float(order.commission_rate) if order.commission_rate is not None else None,
        "staff_earning_cents": order.staff_earning_cents,
        "review": (
            {
                "rating": order.review.rating,
                "content": order.review.content,
                "created_at": order.review.created_at.isoformat(),
            }
            if order.review
            else None
        ),
        "created_at": order.created_at.isoformat(),
    }


def message_to_dict(message: OrderMessage):
    return {
        "id": message.id,
        "order_id": message.order_id,
        "sender_type": message.sender_type,
        "sender_id": message.sender_id,
        "sender_name": message.sender_name,
        "content": message.content,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def list_order_messages(order_id: int, after_id: int, limit: int, db: Session):
    query = db.query(OrderMessage).filter(OrderMessage.order_id == order_id)
    if after_id:
        query = query.filter(OrderMessage.id > after_id)
    return [
        message_to_dict(message)
        for message in query.order_by(OrderMessage.id.asc()).limit(limit).all()
    ]


def create_order_message(
    order: CareOrder,
    payload: MessageCreate,
    sender_type: str,
    sender_id: int | None,
    sender_name: str,
    db: Session,
):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    message = OrderMessage(
        order_id=order.id,
        sender_type=sender_type,
        sender_id=sender_id,
        sender_name=sender_name,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message_to_dict(message)


def ticket_to_dict(ticket: SupportTicket, include_token: bool = False):
    data = {
        "id": ticket.id,
        "category": ticket.category,
        "subject": ticket.subject,
        "customer_name": ticket.customer_name,
        "customer_avatar": ticket.customer_avatar,
        "status": ticket.status,
        "service_employee_id": ticket.service_employee_id,
        "service_employee_name": ticket.service_employee.name if ticket.service_employee else None,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
        "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
    }
    if include_token:
        data["access_token"] = ticket.access_token
    return data


def support_message_to_dict(message: SupportMessage):
    return {
        "id": message.id,
        "ticket_id": message.ticket_id,
        "sender_type": message.sender_type,
        "sender_id": message.sender_id,
        "sender_name": message.sender_name,
        "content": message.content,
        "created_at": message.created_at.isoformat() if message.created_at else None,
    }


def create_support_message(
    ticket: SupportTicket,
    payload: MessageCreate,
    sender_type: str,
    sender_id: int | None,
    sender_name: str,
    db: Session,
):
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    message = SupportMessage(
        ticket_id=ticket.id,
        sender_type=sender_type,
        sender_id=sender_id,
        sender_name=sender_name,
        content=content,
    )
    ticket.updated_at = datetime.utcnow()
    db.add(message)
    db.commit()
    db.refresh(message)
    return support_message_to_dict(message)


def get_customer_support_ticket(ticket_id: int, token: str, db: Session) -> SupportTicket:
    ticket = (
        db.query(SupportTicket)
        .filter(SupportTicket.id == ticket_id, SupportTicket.access_token == token)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="客服工单不存在或访问凭据无效")
    return ticket


def require_customer_service(employee: Employee):
    if employee.role != "customer_service":
        raise HTTPException(status_code=403, detail="该功能仅限客服员工")
    return employee


def require_caregiver(employee: Employee):
    if employee.role != "caregiver":
        raise HTTPException(status_code=403, detail="客服账号不能操作陪诊订单")
    return employee


@app.post("/api/support/tickets")
def create_support_ticket(payload: SupportTicketCreate, db: Session = Depends(get_db)):
    ticket = SupportTicket(
        access_token=secrets.token_urlsafe(24),
        category=payload.category,
        subject=payload.subject.strip() if payload.subject else None,
        customer_name=payload.customer_name.strip() or "小陪用户",
        customer_avatar=payload.customer_avatar,
        status="open",
    )
    db.add(ticket)
    db.flush()
    db.add(
        SupportMessage(
            ticket_id=ticket.id,
            sender_type="customer",
            sender_name=ticket.customer_name,
            content=payload.content.strip(),
        )
    )
    db.commit()
    db.refresh(ticket)
    return ticket_to_dict(ticket, include_token=True)


@app.get("/api/support/tickets/{ticket_id}")
def get_support_ticket(
    ticket_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    return ticket_to_dict(get_customer_support_ticket(ticket_id, token, db), include_token=True)


@app.get("/api/support/tickets/{ticket_id}/messages")
def get_support_messages(
    ticket_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    ticket = get_customer_support_ticket(ticket_id, token, db)
    query = db.query(SupportMessage).filter(SupportMessage.ticket_id == ticket.id)
    if after_id:
        query = query.filter(SupportMessage.id > after_id)
    return [support_message_to_dict(item) for item in query.order_by(SupportMessage.id.asc()).limit(limit).all()]


@app.post("/api/support/tickets/{ticket_id}/messages")
def send_support_message(
    ticket_id: int,
    payload: MessageCreate,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    ticket = get_customer_support_ticket(ticket_id, token, db)
    if ticket.status == "resolved":
        ticket.status = "open"
        ticket.resolved_at = None
    return create_support_message(ticket, payload, "customer", None, ticket.customer_name, db)


@app.get("/api/staff/support/tickets")
def list_support_tickets(
    ticket_status: str = Query(default="all", alias="status", pattern="^(all|open|in_progress|resolved)$"),
    limit: int = Query(default=100, ge=1, le=200),
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    require_customer_service(employee)
    query = db.query(SupportTicket).filter(
        or_(SupportTicket.service_employee_id.is_(None), SupportTicket.service_employee_id == employee.id)
    )
    if ticket_status != "all":
        query = query.filter(SupportTicket.status == ticket_status)
    return [ticket_to_dict(item) for item in query.order_by(SupportTicket.updated_at.desc()).limit(limit).all()]


def get_service_ticket(ticket_id: int, employee: Employee, db: Session, lock: bool = False) -> SupportTicket:
    require_customer_service(employee)
    query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
    if lock:
        query = query.with_for_update()
    ticket = query.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="客服工单不存在")
    if ticket.service_employee_id not in (None, employee.id):
        raise HTTPException(status_code=403, detail="该工单已由其他客服处理")
    return ticket


@app.post("/api/staff/support/tickets/{ticket_id}/accept")
def accept_support_ticket(
    ticket_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    ticket = get_service_ticket(ticket_id, employee, db, lock=True)
    if ticket.status == "resolved":
        raise HTTPException(status_code=409, detail="已办结的工单不能领取")
    ticket.service_employee_id = employee.id
    ticket.status = "in_progress"
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket_to_dict(ticket)


@app.get("/api/staff/support/tickets/{ticket_id}/messages")
def staff_support_messages(
    ticket_id: int,
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    ticket = get_service_ticket(ticket_id, employee, db)
    query = db.query(SupportMessage).filter(SupportMessage.ticket_id == ticket.id)
    if after_id:
        query = query.filter(SupportMessage.id > after_id)
    return [support_message_to_dict(item) for item in query.order_by(SupportMessage.id.asc()).limit(limit).all()]


@app.post("/api/staff/support/tickets/{ticket_id}/messages")
def send_staff_support_message(
    ticket_id: int,
    payload: MessageCreate,
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    ticket = get_service_ticket(ticket_id, employee, db, lock=True)
    if ticket.status == "resolved":
        ticket.status = "in_progress"
        ticket.resolved_at = None
    if ticket.service_employee_id is None:
        ticket.service_employee_id = employee.id
    return create_support_message(ticket, payload, "customer_service", employee.id, employee.name, db)


@app.post("/api/staff/support/tickets/{ticket_id}/resolve")
def resolve_support_ticket(
    ticket_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    ticket = get_service_ticket(ticket_id, employee, db, lock=True)
    if ticket.service_employee_id is None:
        raise HTTPException(status_code=409, detail="请先领取工单")
    ticket.status = "resolved"
    ticket.resolved_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket_to_dict(ticket)


@app.post("/api/staff/orders/{order_id}/force-stop")
def customer_service_force_stop_order(
    order_id: int,
    payload: ForceStopCreate,
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    require_customer_service(employee)
    order = admin_close_order(order_id, "stopped", db)
    reason = payload.reason.strip() if payload.reason else "客服介入处理"
    create_order_message(
        db.get(CareOrder, order_id),
        MessageCreate(content=f"客服已强制停止该订单。原因：{reason}"),
        "customer_service",
        employee.id,
        employee.name,
        db,
    )
    return order


def record_order_income(order: CareOrder, db: Session):
    if not order.employee_id or not order.staff_earning_cents or order.staff_earning_cents <= 0:
        return
    if db.query(EmployeeIncomeRecord.id).filter(EmployeeIncomeRecord.order_id == order.id).first():
        return
    db.add(
        EmployeeIncomeRecord(
            employee_id=order.employee_id,
            order_id=order.id,
            amount_cents=order.staff_earning_cents,
            status="available",
        )
    )


def backfill_income_records(db: Session):
    completed_orders = (
        db.query(CareOrder)
        .filter(
            CareOrder.status == "completed",
            CareOrder.employee_id.is_not(None),
            CareOrder.staff_earning_cents.is_not(None),
            CareOrder.staff_earning_cents > 0,
        )
        .all()
    )
    for order in completed_orders:
        record_order_income(order, db)


def complete_order(order: CareOrder, db: Session, completion_type: str = "staff_completed"):
    order.status = "completed"
    order.completed_at = datetime.utcnow()
    order.completion_type = completion_type
    if not order.employee:
        order.commission_rate = None
        order.staff_earning_cents = None
        return
    rate = float(order.employee.commission_rate) if order.employee.commission_rate is not None else 85
    order.commission_rate = rate
    order.staff_earning_cents = int(round(order.service_item.price_cents * rate / 100))
    record_order_income(order, db)


@app.get("/api/admin/orders")
def list_orders(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    orders = db.query(CareOrder).order_by(CareOrder.created_at.desc()).limit(limit).all()
    return [order_to_dict(order) for order in orders]


@app.get("/api/admin/customers")
def list_customers(db: Session = Depends(get_db)):
    """Return customer profiles aggregated from care-order contact details."""
    customers = {}
    orders = db.query(CareOrder).order_by(CareOrder.created_at.desc()).all()
    for order in orders:
        key = (order.patient_name, order.patient_phone)
        profile = customers.get(key)
        if profile is None:
            profile = {
                "name": order.patient_name,
                "phone": order.patient_phone,
                "order_count": 0,
                "latest_order_at": order.created_at,
                "latest_order_no": order.order_no,
            }
            customers[key] = profile
        profile["order_count"] += 1
    return sorted(
        customers.values(),
        key=lambda customer: customer["latest_order_at"],
        reverse=True,
    )


def get_orders_for_employee(employee: Employee, order_status: str, db: Session, limit: int):
    require_caregiver(employee)
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
    require_caregiver(employee)
    db.query(Employee).filter(Employee.id == employee.id).with_for_update().one()
    active_order = (
        db.query(CareOrder.id)
        .filter(
            CareOrder.employee_id == employee.id,
            CareOrder.status.in_(["accepted", "in_progress"]),
        )
        .first()
    )
    if active_order:
        db.rollback()
        raise HTTPException(status_code=409, detail="您有进行中的订单，请完成后再接新单")
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
    employee = db.query(Employee).filter(Employee.employee_code == payload.employee_id).first()
    if not employee or not employee.is_active or not verify_password(payload.password, employee.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    return {
        "access_token": create_staff_token(employee.id),
        "token_type": "bearer",
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "name": employee.name,
            "phone": employee.phone,
            "service_area": employee.service_area,
            "role": employee.role,
            "commission_rate": float(employee.commission_rate),
        },
    }


@app.get("/api/staff/me")
def staff_me(employee: Employee = Depends(require_staff)):
    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "name": employee.name,
        "phone": employee.phone,
        "service_area": employee.service_area,
        "role": employee.role,
        "commission_rate": float(employee.commission_rate),
    }


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


def get_staff_order(order_id: int, employee: Employee, db: Session) -> CareOrder:
    require_caregiver(employee)
    order = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.employee_id == employee.id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在或未分配给当前员工")
    return order


@app.post("/api/staff/orders/{order_id}/accept")
def staff_accept_order(
    order_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    return order_to_dict(claim_order(order_id, employee, db))


@app.post("/api/staff/orders/{order_id}/start")
def staff_start_order(
    order_id: int, employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    require_caregiver(employee)
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
    require_caregiver(employee)
    order = (
        db.query(CareOrder)
        .filter(
            CareOrder.id == order_id,
            CareOrder.employee_id == employee.id,
            CareOrder.status == "in_progress",
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=409, detail="该订单当前不能结束工作")
    started_at = order.started_at or datetime.utcnow()
    elapsed_minutes = max(0, int((datetime.utcnow() - started_at).total_seconds() // 60))
    scheduled_minutes = order.service_item.duration_minutes
    if elapsed_minutes < scheduled_minutes:
        order.early_finish_requested_at = datetime.utcnow()
        order.early_finish_response = None
        order.early_finish_responded_at = None
        db.commit()
        db.refresh(order)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "requires_customer_confirmation": True,
                "served_minutes": elapsed_minutes,
                "scheduled_minutes": scheduled_minutes,
                "order": order_to_dict(order),
            },
        )
    complete_order(order, db, "staff_completed")
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@app.post("/api/staff/orders/{order_id}/location")
def update_staff_location(
    order_id: int,
    payload: LocationUpdate,
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    require_caregiver(employee)
    order = (
        db.query(CareOrder)
        .filter(
            CareOrder.id == order_id,
            CareOrder.employee_id == employee.id,
            CareOrder.status.in_(["accepted", "in_progress"]),
        )
        .first()
    )
    if not order:
        raise HTTPException(status_code=409, detail="该订单当前不能更新位置")
    order.staff_latitude = payload.latitude
    order.staff_longitude = payload.longitude
    order.staff_location_updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "updated_at": order.staff_location_updated_at.isoformat()}


@app.get("/api/staff/orders/{order_id}/messages")
def staff_order_messages(
    order_id: int,
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    order = get_staff_order(order_id, employee, db)
    return list_order_messages(order.id, after_id, limit, db)


@app.post("/api/staff/orders/{order_id}/messages")
def send_staff_order_message(
    order_id: int,
    payload: MessageCreate,
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    order = get_staff_order(order_id, employee, db)
    return create_order_message(order, payload, "staff", employee.id, employee.name, db)


def income_record_to_dict(record: EmployeeIncomeRecord):
    order = record.order
    return {
        "id": record.id,
        "order_id": record.order_id,
        "order_no": order.order_no,
        "service_name": order.service_item.name,
        "amount_cents": record.amount_cents,
        "status": record.status,
        "commission_rate": float(order.commission_rate) if order.commission_rate is not None else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@app.get("/api/staff/wallet")
def staff_wallet(
    limit: int = Query(default=100, ge=1, le=200),
    employee: Employee = Depends(require_staff),
    db: Session = Depends(get_db),
):
    require_caregiver(employee)
    records = (
        db.query(EmployeeIncomeRecord)
        .filter(EmployeeIncomeRecord.employee_id == employee.id)
        .order_by(EmployeeIncomeRecord.created_at.desc(), EmployeeIncomeRecord.id.desc())
        .limit(limit)
        .all()
    )
    total_income_cents = (
        db.query(func.coalesce(func.sum(EmployeeIncomeRecord.amount_cents), 0))
        .filter(
            EmployeeIncomeRecord.employee_id == employee.id,
            EmployeeIncomeRecord.status == "available",
        )
        .scalar()
    )
    return {
        "summary": {
            "pending_withdrawal_cents": int(total_income_cents or 0),
            "total_income_cents": int(total_income_cents or 0),
            "settled_order_count": len(records),
        },
        "records": [income_record_to_dict(record) for record in records],
    }


@app.get("/api/staff/location-map")
def staff_location_map(
    employee: Employee = Depends(require_staff), db: Session = Depends(get_db)
):
    require_caregiver(employee)
    orders = (
        db.query(CareOrder)
        .filter(
            CareOrder.employee_id == employee.id,
            CareOrder.status.in_(["accepted", "in_progress"]),
        )
        .all()
    )
    points = []
    markers = []
    staff_order = next(
        (
            order
            for order in orders
            if order.staff_latitude is not None and order.staff_longitude is not None
        ),
        None,
    )
    if staff_order:
        staff_point = (float(staff_order.staff_longitude), float(staff_order.staff_latitude))
        points.append(staff_point)
        markers.append(f"mid,0x00897B,S:{staff_point[0]:.6f},{staff_point[1]:.6f}")
    for order in orders:
        if order.latitude is None or order.longitude is None:
            continue
        customer_point = (float(order.longitude), float(order.latitude))
        points.append(customer_point)
        markers.append(f"mid,0xE91E63,C:{customer_point[0]:.6f},{customer_point[1]:.6f}")
    if not points:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    center_lng = sum(point[0] for point in points) / len(points)
    center_lat = sum(point[1] for point in points) / len(points)
    image, content_type = static_map(
        {
            "location": f"{center_lng:.6f},{center_lat:.6f}",
            "zoom": "13" if len(points) > 1 else "15",
            "size": "1000*460",
            "markers": "|".join(markers),
        }
    )
    return Response(content=image, media_type=content_type)


@app.post("/api/admin/orders/{order_id}/assign")
def admin_assign_order(
    order_id: int, payload: OrderAssign, db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee).filter(Employee.id == payload.employee_id).with_for_update().first()
    )
    if not employee or not employee.is_active:
        raise HTTPException(status_code=400, detail="请选择有效员工")
    if employee.role != "caregiver":
        raise HTTPException(status_code=400, detail="客服不能被分配陪诊订单")
    order = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.status.in_(["pending", "accepted"]))
        .with_for_update()
        .first()
    )
    if not order:
        db.rollback()
        raise HTTPException(status_code=409, detail="仅待接单或已接单的订单可以指定员工")
    if order.employee_id == employee.id:
        return order_to_dict(order)
    active_order = (
        db.query(CareOrder.id)
        .filter(
            CareOrder.employee_id == employee.id,
            CareOrder.status.in_(["accepted", "in_progress"]),
        )
        .first()
    )
    if active_order:
        db.rollback()
        raise HTTPException(status_code=409, detail="该员工有进行中的订单，不能再分配新订单")
    order.employee_id = employee.id
    order.status = "accepted"
    order.accepted_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


def admin_close_order(order_id: int, target_status: str, db: Session):
    order = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.status.notin_(["completed", "stopped"]))
        .first()
    )
    if not order:
        raise HTTPException(status_code=409, detail="该订单已结束或不存在")
    if target_status == "completed":
        complete_order(order, db, "system_confirmed")
    else:
        order.status = "stopped"
        order.stopped_at = datetime.utcnow()
        order.completion_type = "system_confirmed"
        order.commission_rate = None
        order.staff_earning_cents = None
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@app.post("/api/admin/orders/{order_id}/finish")
def admin_finish_order(order_id: int, db: Session = Depends(get_db)):
    return admin_close_order(order_id, "completed", db)


@app.post("/api/admin/orders/{order_id}/stop")
def admin_stop_order(order_id: int, db: Session = Depends(get_db)):
    return admin_close_order(order_id, "stopped", db)


@app.post("/api/admin/orders/{order_id}/force-stop")
def admin_force_stop_order(order_id: int, db: Session = Depends(get_db)):
    return admin_close_order(order_id, "stopped", db)


@app.put("/api/admin/orders/{order_id}/review")
def admin_update_order_review(
    order_id: int, payload: ReviewUpdate, db: Session = Depends(get_db)
):
    review = db.query(OrderReview).filter(OrderReview.order_id == order_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="该订单暂无评价")
    review.content = payload.content
    db.commit()
    order = db.get(CareOrder, order_id)
    return order_to_dict(order)


def get_customer_order(order_id: int, review_token: str, db: Session) -> CareOrder:
    order = (
        db.query(CareOrder)
        .filter(CareOrder.id == order_id, CareOrder.review_token == review_token)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="预约不存在或访问凭据无效")
    return order


def customer_order_to_dict(order: CareOrder):
    return {
        "id": order.id,
        "order_no": order.order_no,
        "hospital_id": order.hospital_id,
        "hospital_name": order.hospital.name,
        "service_item_id": order.service_item_id,
        "service_name": order.service_item.name,
        "service_price_cents": order.service_item.price_cents,
        "service_duration_minutes": order.service_item.duration_minutes,
        "patient_name": order.patient_name,
        "patient_phone": order.patient_phone,
        "appointment_time": order.appointment_time.isoformat(),
        "address_detail": order.address_detail,
        "distance_km": float(order.distance_km) if order.distance_km is not None else None,
        "note": order.note,
        "status": order.status,
        "status_text": order_status_text(order),
        "completion_type": order.completion_type,
        "employee_name": order.employee.name if order.employee else None,
        "employee_phone": order.employee.phone if order.employee else None,
        "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
        "started_at": order.started_at.isoformat() if order.started_at else None,
        "completed_at": order.completed_at.isoformat() if order.completed_at else None,
        "stopped_at": order.stopped_at.isoformat() if order.stopped_at else None,
        "early_finish": (
            {
                "requested_at": order.early_finish_requested_at.isoformat(),
                "served_minutes": max(
                    0,
                    int((datetime.utcnow() - order.started_at).total_seconds() // 60),
                ),
                "scheduled_minutes": order.service_item.duration_minutes,
            }
            if order.early_finish_requested_at and order.early_finish_response is None and order.started_at
            else None
        ),
        "created_at": order.created_at.isoformat(),
        "review": (
            {
                "rating": order.review.rating,
                "content": order.review.content,
                "created_at": order.review.created_at.isoformat(),
            }
            if order.review
            else None
        ),
    }


def customer_location_to_dict(order: CareOrder):
    return {
        "order_no": order.order_no,
        "status": order.status,
        "employee_name": order.employee.name if order.employee else None,
        "customer_location": (
            {
                "latitude": float(order.latitude),
                "longitude": float(order.longitude),
                "updated_at": (
                    order.customer_location_updated_at.isoformat()
                    if order.customer_location_updated_at
                    else None
                ),
            }
            if order.latitude is not None and order.longitude is not None
            else None
        ),
        "staff_location": (
            {
                "latitude": float(order.staff_latitude),
                "longitude": float(order.staff_longitude),
                "updated_at": order.staff_location_updated_at.isoformat(),
            }
            if order.staff_latitude is not None
            and order.staff_longitude is not None
            and order.staff_location_updated_at is not None
            else None
        ),
    }


@app.get("/api/customer/orders/{order_id}")
def get_customer_order_status(
    order_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    return customer_order_to_dict(get_customer_order(order_id, token, db))


@app.get("/api/customer/orders/{order_id}/messages")
def customer_order_messages(
    order_id: int,
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = get_customer_order(order_id, token, db)
    return list_order_messages(order.id, after_id, limit, db)


@app.post("/api/customer/orders/{order_id}/messages")
def send_customer_order_message(
    order_id: int,
    payload: MessageCreate,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = get_customer_order(order_id, token, db)
    return create_order_message(order, payload, "customer", None, order.patient_name, db)


@app.get("/api/customer/orders/{order_id}/location")
def get_customer_order_location(
    order_id: int,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    return customer_location_to_dict(get_customer_order(order_id, token, db))


@app.post("/api/customer/orders/{order_id}/location")
def update_customer_order_location(
    order_id: int,
    payload: LocationUpdate,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = get_customer_order(order_id, token, db)
    if order.status not in {"accepted", "in_progress"}:
        raise HTTPException(status_code=409, detail="当前订单不能更新位置")
    order.latitude = payload.latitude
    order.longitude = payload.longitude
    order.customer_location_updated_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "updated_at": order.customer_location_updated_at.isoformat()}


@app.post("/api/customer/orders/{order_id}/early-finish-response")
def respond_to_early_finish(
    order_id: int,
    payload: EarlyFinishResponse,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = get_customer_order(order_id, token, db)
    if (
        order.status != "in_progress"
        or not order.early_finish_requested_at
        or order.early_finish_response is not None
    ):
        raise HTTPException(status_code=409, detail="当前没有待确认的提前结束申请")
    order.early_finish_response = payload.approved
    order.early_finish_responded_at = datetime.utcnow()
    if payload.approved:
        complete_order(order, db, "negotiated_early")
    db.commit()
    db.refresh(order)
    return customer_order_to_dict(order)


@app.post("/api/customer/orders/{order_id}/review")
def create_order_review(
    order_id: int,
    payload: ReviewCreate,
    token: str = Query(..., min_length=16, max_length=64),
    db: Session = Depends(get_db),
):
    order = get_customer_order(order_id, token, db)
    if order.status != "completed":
        raise HTTPException(status_code=409, detail="服务结束后才能评价")
    if order.review:
        raise HTTPException(status_code=409, detail="该订单已评价")
    review = OrderReview(order_id=order.id, **payload.model_dump())
    db.add(review)
    db.commit()
    db.refresh(order)
    return customer_order_to_dict(order)


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
        review_token=secrets.token_urlsafe(24),
        distance_km=distance,
        customer_location_updated_at=(
            datetime.utcnow() if payload.latitude is not None and payload.longitude is not None else None
        ),
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
