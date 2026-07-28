import hashlib
import json
import ssl
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import certifi
from fastapi import HTTPException

from .config import settings


AMAP_REGEOCODE_URL = "https://restapi.amap.com/v3/geocode/regeo"
AMAP_PLACE_AROUND_URL = "https://restapi.amap.com/v5/place/around"
AMAP_PLACE_TEXT_URL = "https://restapi.amap.com/v5/place/text"
AMAP_STATIC_MAP_URL = "https://restapi.amap.com/v3/staticmap"
HOSPITAL_POI_TYPE = "090000"


def reverse_geocode(lat: float, lng: float):
    if not settings.amap_key:
        raise HTTPException(status_code=500, detail="未配置高德 Web 服务 Key")

    params = {
        "extensions": "base",
        "key": settings.amap_key,
        "location": f"{lng:.6f},{lat:.6f}",
        "output": "json",
        "radius": "1000",
    }
    data = amap_get(AMAP_REGEOCODE_URL, params)

    if data.get("status") != "1":
        raise HTTPException(
            status_code=502,
            detail=data.get("info") or "高德地图逆地理编码失败",
        )

    regeocode = data.get("regeocode") or {}
    address = regeocode.get("addressComponent") or {}
    return {
        "formatted_address": regeocode.get("formatted_address") or "",
        "country": normalize_amap_value(address.get("country")),
        "province": normalize_amap_value(address.get("province")),
        "city": normalize_amap_value(address.get("city")),
        "district": normalize_amap_value(address.get("district")),
        "township": normalize_amap_value(address.get("township")),
        "adcode": normalize_amap_value(address.get("adcode")),
        "citycode": normalize_amap_value(address.get("citycode")),
        "latitude": lat,
        "longitude": lng,
    }


def search_hospitals(
    keyword: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_m: int = 30000,
    page_size: int = 20,
):
    if keyword:
        keyword = keyword.strip()

    if lat is not None and lng is not None:
        params = {
            "key": settings.amap_key,
            "keywords": keyword or "医院",
            "location": f"{lng:.6f},{lat:.6f}",
            "output": "json",
            "page_size": str(page_size),
            "radius": str(radius_m),
            "show_fields": "business",
            "types": HOSPITAL_POI_TYPE,
        }
        data = amap_get(AMAP_PLACE_AROUND_URL, params)
    else:
        params = {
            "key": settings.amap_key,
            "keywords": keyword or "医院",
            "output": "json",
            "page_size": str(page_size),
            "show_fields": "business",
            "types": HOSPITAL_POI_TYPE,
        }
        data = amap_get(AMAP_PLACE_TEXT_URL, params)

    if data.get("status") != "1":
        raise HTTPException(
            status_code=502,
            detail=data.get("info") or "高德地图医院检索失败",
        )

    pois = data.get("pois") or []
    return [normalize_poi(item) for item in pois if normalize_poi(item)]


def amap_get(url: str, params: dict[str, str]):
    if not settings.amap_key:
        raise HTTPException(status_code=500, detail="未配置高德 Web 服务 Key")

    if settings.amap_private_key:
        params["sig"] = build_signature(params, settings.amap_private_key)

    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(f"{url}?{urlencode(params)}", timeout=8, context=context) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="高德地图服务请求失败") from exc


def static_map(params: dict[str, str]):
    if not settings.amap_key:
        raise HTTPException(status_code=500, detail="未配置高德 Web 服务 Key")

    params["key"] = settings.amap_key
    if settings.amap_private_key:
        params["sig"] = build_signature(params, settings.amap_private_key)

    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(
            f"{AMAP_STATIC_MAP_URL}?{urlencode(params)}", timeout=8, context=context
        ) as response:
            content = response.read()
            content_type = response.headers.get_content_type()
        if content_type == "application/json":
            detail = json.loads(content.decode("utf-8")).get("info") or "高德静态地图服务失败"
            raise HTTPException(status_code=502, detail=detail)
        return content, content_type
    except HTTPException:
        raise
    except (OSError, URLError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="高德静态地图服务请求失败") from exc


def normalize_poi(item):
    location = item.get("location") or ""
    if "," not in location:
        return None
    lng, lat = location.split(",", 1)
    address = normalize_amap_value(item.get("address"))
    pname = normalize_amap_value(item.get("pname"))
    cityname = normalize_amap_value(item.get("cityname"))
    adname = normalize_amap_value(item.get("adname"))
    return {
        "id": item.get("id") or "",
        "name": item.get("name") or "",
        "address": address or "".join([pname, cityname, adname]),
        "latitude": float(lat),
        "longitude": float(lng),
        "phone": normalize_amap_value(item.get("tel")),
        "distance_m": parse_int(item.get("distance")),
        "province": pname,
        "city": cityname,
        "district": adname,
    }


def build_signature(params: dict[str, str], private_key: str):
    payload = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hashlib.md5(f"{payload}{private_key}".encode("utf-8")).hexdigest()


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_amap_value(value):
    if isinstance(value, list):
        return ""
    return value or ""
