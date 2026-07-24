from datetime import datetime
from pathlib import Path
from random import randint

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .amap import reverse_geocode, search_hospitals
from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .geo import haversine_km
from .models import CareOrder, HospitalUnit, ServiceItem
from .schemas import (
    HospitalCreate,
    HospitalOut,
    HospitalUpdate,
    OrderCreate,
    OrderOut,
    ServiceItemOut,
)

app = FastAPI(title=settings.app_name)

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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
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
    db.commit()


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


@app.get("/api/admin/orders")
def list_orders(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    orders = db.query(CareOrder).order_by(CareOrder.created_at.desc()).limit(limit).all()
    return [
        {
            "id": order.id,
            "order_no": order.order_no,
            "patient_name": order.patient_name,
            "patient_phone": order.patient_phone,
            "hospital_name": order.hospital.name,
            "service_name": order.service_item.name,
            "appointment_time": order.appointment_time.isoformat(),
            "address_detail": order.address_detail,
            "distance_km": float(order.distance_km) if order.distance_km is not None else None,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]


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
