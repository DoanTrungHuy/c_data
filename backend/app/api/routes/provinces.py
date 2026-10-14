from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select

from app.api.deps import SessionDep
from app.models.job import Job
from app.models.province import Province
from app.schemas.job import JobListResponse
from app.schemas.job import JobSearchParams
from app.schemas.province import ProvinceListResponse, ProvinceResponse
from app.services.job_service import job_service

router = APIRouter(prefix="/provinces", tags=["Provinces"])


@router.get("", response_model=ProvinceListResponse)
async def list_provinces(
    db: SessionDep,
    region: Optional[str] = Query(None, description="Lọc theo miền: Miền Bắc, Miền Trung, Miền Nam"),
) -> ProvinceListResponse:
    """
    Lấy danh sách 63 tỉnh/thành phố của Việt Nam
    """
    stmt = select(Province)
    if region:
        stmt = stmt.where(Province.region.ilike(f"%{region.strip()}%"))
    stmt = stmt.order_by(Province.code.asc())

    result = await db.execute(stmt)
    provinces = list(result.scalars().all())

    return ProvinceListResponse(
        items=provinces,
        total=len(provinces),
    )


@router.get("/{code}/jobs", response_model=JobListResponse)
async def get_jobs_in_province(
    code: str,
    db: SessionDep,
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(20, ge=1, le=100, description="Số tin mỗi trang"),
    category: Optional[str] = Query(None, description="Lọc thêm theo ngành nghề"),
    job_type: Optional[str] = Query(None, description="Lọc thêm theo hình thức làm việc"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
) -> JobListResponse:
    """
    Lấy danh sách việc làm tại một tỉnh/thành phố cụ thể dựa trên mã code (GSO)
    """
    # 1. Tìm thông tin tỉnh thành theo code
    stmt = select(Province).where(Province.code == code)
    res = await db.execute(stmt)
    province = res.scalar_one_or_none()

    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy tỉnh thành với mã: {code}",
        )

    # 2. Tìm các công việc có location_province khớp với tên tỉnh
    search_params = JobSearchParams(
        query=query,
        province=province.name,
        category=category,
        job_type=job_type,
        page=page,
        page_size=page_size,
    )
    items, total, total_pages = await job_service.get_jobs(db, search_params)

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
