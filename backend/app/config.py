from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    app_name: str = "医护陪护上门预约系统"
    database_url: str = (
        "mysql+pymysql://root:password@127.0.0.1:3306/care_booking?charset=utf8mb4"
    )
    cors_origins: str = "*"
    amap_key: str = ""
    amap_private_key: str = ""
    staff_token_secret: str = "change-this-in-production"
    staff_token_expire_seconds: int = 28800

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
