from typing import List
from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.schemas.stats import (
    CategoryJobCount,
    DashboardStats,
    PlatformJobCount,
    ProvinceJobCount,
)
from app.services.stats_service import stats_service

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    db: SessionDep,
) -> DashboardStats:
    """
    Lấy toàn bộ thông tin thống kê tổng quan cho màn hình Dashboard C_Data
    """
    return await stats_service.get_dashboard_stats(db)


@router.get("/provinces", response_model=List[ProvinceJobCount])
async def get_jobs_by_province_stat(
    db: SessionDep,
    limit: int = Query(20, ge=1, le=63, description="Số lượng tỉnh thành cần lấy"),
) -> List[ProvinceJobCount]:
    """
    Lấy bảng xếp hạng các tỉnh thành có nhiều việc làm nhất
    """
    return await stats_service.get_jobs_by_province(db, limit=limit)


@router.get("/categories", response_model=List[CategoryJobCount])
async def get_jobs_by_category_stat(
    db: SessionDep,
    limit: int = Query(20, ge=1, le=50, description="Số lượng ngành nghề cần lấy"),
) -> List[CategoryJobCount]:
    """
    Lấy bảng xếp hạng các ngành nghề có nhu cầu tuyển dụng cao nhất
    """
    return await stats_service.get_jobs_by_category(db, limit=limit)


@router.get("/platforms", response_model=List[PlatformJobCount])
async def get_jobs_by_platform_stat(
    db: SessionDep,
) -> List[PlatformJobCount]:
    """
    Lấy tỷ lệ việc làm thu thập từ các nền tảng nguồn
    """
    return await stats_service.get_jobs_by_platform(db)
