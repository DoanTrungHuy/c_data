import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import companies, jobs, provinces, stats
from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine
from app.data.provinces import seed_provinces

# Thiết lập hệ thống ghi log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger("c_data")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Quản lý vòng đời khởi chạy và kết thúc của ứng dụng FastAPI C_Data
    """
    logger.info("==================================================")
    logger.info("Đang khởi động C_Data Backend Service...")
    logger.info(f"Dự án: {settings.PROJECT_NAME}")
    logger.info(f"Môi trường: {settings.ENVIRONMENT}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info("==================================================")

    # Import tất cả models để Base.metadata biết các bảng
    import app.models  # noqa: F401

    # Tự động tạo tất cả bảng nếu chưa tồn tại (phù hợp cho development)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Đã tạo / kiểm tra toàn bộ bảng trong database.")

    # Tự động nạp dữ liệu 63 tỉnh thành khi khởi chạy
    try:
        async with AsyncSessionLocal() as session:
            await seed_provinces(session)
            logger.info("Khởi tạo và đồng bộ 63 tỉnh/thành phố thành công.")
    except Exception as e:
        logger.warning(f"Chưa thể tự động seed tỉnh thành: {e}")

    yield

    logger.info("Đang dừng dịch vụ C_Data Backend...")
    await engine.dispose()
    logger.info("Đã đóng toàn bộ kết nối Database.")


# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="C_Data API - Nền tảng tổng hợp, chuẩn hóa và phân tích tin tuyển dụng việc làm tại Việt Nam.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Cấu hình CORS Middleware (cho phép truy cập linh hoạt từ frontend local và cloud deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router API V1
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(companies.router, prefix=settings.API_V1_PREFIX)
app.include_router(provinces.router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["General"])
async def root():
    """
    Endpoint mặc định chào mừng người dùng và cung cấp thông tin điều hướng API
    """
    return {
        "message": f"Chào mừng bạn đến với {settings.PROJECT_NAME} API!",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_PREFIX,
        "endpoints": {
            "jobs": f"{settings.API_V1_PREFIX}/jobs",
            "search": f"{settings.API_V1_PREFIX}/jobs/search",
            "companies": f"{settings.API_V1_PREFIX}/companies",
            "provinces": f"{settings.API_V1_PREFIX}/provinces",
            "stats": f"{settings.API_V1_PREFIX}/stats/dashboard",
        },
    }


@app.get("/health", tags=["General"])
async def health_check():
    """
    Endpoint kiểm tra trạng thái hoạt động (Healthcheck) của Backend
    """
    return {
        "status": "healthy",
        "service": "c_data_backend",
        "environment": settings.ENVIRONMENT,
    }
