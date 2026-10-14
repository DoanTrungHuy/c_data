import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Cấu hình ứng dụng C_Data đọc từ biến môi trường hoặc file .env
    """
    # Thông tin dự án
    PROJECT_NAME: str = "C_Data - Việc Làm Việt Nam"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Kết nối cơ sở dữ liệu
    # URL bất đồng bộ (Async) dành cho FastAPI — mặc định dùng SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./cdata.db"
    # URL đồng bộ (Sync) dành cho Alembic migrations và Celery workers
    DATABASE_URL_SYNC: str = "sqlite:///./cdata.db"

    # Redis Cache & Broker (tùy chọn, không bắt buộc cho dev)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Thiết lập Crawler / Scraper
    CRAWL_INTERVAL_HOURS: int = 12
    CRAWL_MAX_PAGES: int = 50
    CRAWL_DELAY_SECONDS: int = 2

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "*",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Khởi tạo singleton settings
settings = Settings()
