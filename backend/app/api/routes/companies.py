import math
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import SessionDep
from app.models.company import Company
from app.models.job import Job
from app.schemas.company import (
    CompanyDetailResponse,
    CompanyJobBrief,
    CompanyListResponse,
    CompanyResponse,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    db: SessionDep,
    query: Optional[str] = Query(None, description="Tìm theo tên công ty"),
    province: Optional[str] = Query(None, description="Lọc theo tỉnh thành"),
    industry: Optional[str] = Query(None, description="Lọc theo ngành nghề"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(20, ge=1, le=100, description="Số công ty mỗi trang"),
) -> CompanyListResponse:
    """
    Lấy danh sách các công ty tuyển dụng với tìm kiếm và phân trang
    """
    filters = []
    if query:
        filters.append(Company.name.ilike(f"%{query.strip()}%"))
    if province:
        filters.append(Company.province.ilike(f"%{province.strip()}%"))
    if industry:
        filters.append(Company.industry.ilike(f"%{industry.strip()}%"))

    # Đếm tổng số công ty thỏa điều kiện
    count_stmt = select(func.count(Company.id))
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total_res = await db.execute(count_stmt)
    total = total_res.scalar_one_or_none() or 0

    # Lấy danh sách công ty
    stmt = select(Company)
    if filters:
        stmt = stmt.where(and_(*filters))
    offset = (page - 1) * page_size
    stmt = stmt.order_by(Company.name.asc()).offset(offset).limit(page_size)

    result = await db.execute(stmt)
    companies = list(result.scalars().all())
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return CompanyListResponse(
        items=companies,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company_detail(
    company_id: str,
    db: SessionDep,
) -> CompanyDetailResponse:
    """
    Lấy thông tin chi tiết một công ty cùng với danh sách việc làm đang mở của họ
    """
    # Lấy thông tin công ty
    stmt = (
        select(Company)
        .options(selectinload(Company.jobs))
        .where(Company.id == company_id)
    )
    result = await db.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy công ty với ID: {company_id}",
        )

    # Lấy các tin tuyển dụng đang active của công ty này
    active_jobs = [j for j in company.jobs if j.is_active]
    # Sắp xếp bài đăng mới nhất lên đầu
    active_jobs.sort(key=lambda x: (x.posted_at or x.crawled_at), reverse=True)

    job_briefs = [
        CompanyJobBrief(
            id=j.id,
            title=j.title,
            salary_text=j.salary_text,
            location_province=j.location_province,
            job_type=j.job_type,
            category=j.category,
            source_platform=j.source_platform,
            source_url=j.source_url,
            posted_at=j.posted_at,
            is_active=j.is_active,
        )
        for j in active_jobs
    ]

    return CompanyDetailResponse(
        id=company.id,
        name=company.name,
        logo_url=company.logo_url,
        website=company.website,
        province=company.province,
        description=company.description,
        industry=company.industry,
        created_at=company.created_at,
        updated_at=company.updated_at,
        jobs=job_briefs,
        total_active_jobs=len(job_briefs),
    )
