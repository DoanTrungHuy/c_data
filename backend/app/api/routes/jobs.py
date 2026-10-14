import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import SessionDep
from app.schemas.job import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobSearchParams,
)
from app.services.job_service import job_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: SessionDep,
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (q alias)"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm trong tiêu đề hoặc mô tả"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố làm việc"),
    category: Optional[str] = Query(None, description="Danh mục / Ngành nghề"),
    job_type: Optional[str] = Query(None, description="Hình thức: full-time, part-time, remote, intern"),
    salary_min: Optional[int] = Query(None, ge=0, description="Mức lương tối thiểu (VNĐ)"),
    salary_max: Optional[int] = Query(None, ge=0, description="Mức lương tối đa (VNĐ)"),
    source_platform: Optional[str] = Query(None, description="Nền tảng cào dữ liệu: TopCV, VietnamWorks, ITviec..."),
    sort_by: Optional[str] = Query("newest", description="Sắp xếp: newest, salary_desc, salary_asc"),
    live: bool = Query(False, description="Tự động cào thêm tin mới từ các trang tuyển dụng và mạng xã hội trước khi trả về kết quả"),
    strict_mode: bool = Query(False, description="Chế độ khớp khắt khe các ràng buộc cứng"),
    page: int = Query(1, ge=1, description="Trang cần lấy"),
    page_size: int = Query(20, ge=1, le=100, description="Số lượng kết quả trên mỗi trang"),
) -> JobListResponse:
    """
    Lấy danh sách việc làm với các bộ lọc linh hoạt, phân tích ý định và phân trang
    """
    effective_q = (q or query or "").strip() or None

    search_params = JobSearchParams(
        query=effective_q,
        q=effective_q,
        province=province,
        category=category,
        job_type=job_type,
        salary_min=salary_min,
        salary_max=salary_max,
        source_platform=source_platform,
        sort_by=sort_by,
        live=live,
        strict_mode=strict_mode,
        page=page,
        page_size=page_size,
    )
    items, total, total_pages, related_keywords, matched_industries, diagnostics = await job_service.get_jobs(db, search_params)
    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        related_keywords=related_keywords,
        matched_industries=matched_industries,
        diagnostics=diagnostics,
    )


@router.get("/search", response_model=JobListResponse)
async def search_jobs(
    db: SessionDep,
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (q alias)"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm chính"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố"),
    category: Optional[str] = Query(None, description="Ngành nghề"),
    job_type: Optional[str] = Query(None, description="Hình thức làm việc"),
    salary_min: Optional[int] = Query(None, ge=0, description="Mức lương tối thiểu"),
    salary_max: Optional[int] = Query(None, ge=0, description="Mức lương tối đa"),
    source_platform: Optional[str] = Query(None, description="Nguồn tuyển dụng"),
    sort_by: Optional[str] = Query("newest", description="Thứ tự: newest, salary_desc, salary_asc"),
    live: bool = Query(False, description="Tự động cào thêm tin mới từ các trang tuyển dụng và mạng xã hội"),
    strict_mode: bool = Query(False, description="Chế độ khớp khắt khe các ràng buộc cứng"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    page_size: int = Query(20, ge=1, le=100, description="Kích thước trang"),
) -> JobListResponse:
    """
    Endpoint tìm kiếm nâng cao cho việc làm với SearchIntent và Hybrid Ranking
    """
    effective_q = (q or query or "").strip() or None
    params = JobSearchParams(
        query=effective_q,
        q=effective_q,
        province=province,
        category=category,
        job_type=job_type,
        salary_min=salary_min,
        salary_max=salary_max,
        source_platform=source_platform,
        sort_by=sort_by,
        live=live,
        strict_mode=strict_mode,
        page=page,
        page_size=page_size,
    )
    items, total, total_pages, related_keywords, matched_industries, diagnostics = await job_service.search_jobs(db, params)
    return JobListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        related_keywords=related_keywords,
        matched_industries=matched_industries,
        diagnostics=diagnostics,
    )


@router.post("/crawl-live")
async def crawl_live_jobs(
    q: Optional[str] = Query(None, description="Từ khóa cần cào trực tiếp"),
    province: Optional[str] = Query(None, description="Tỉnh thành cần cào trực tiếp"),
    max_items: int = Query(10, ge=1, le=50, description="Số lượng tin tối đa mỗi nguồn"),
):
    """
    ⚡ Cào trực tiếp tin tuyển dụng thời gian thực từ 3 nguồn:
    1. Sàn tuyển dụng (CareerViet / CareerBuilder)
    2. Hội nhóm & Fanpage mạng xã hội (Facebook Jobs Hạ Long / Quảng Ninh)
    3. Cổng thông tin tuyển dụng Doanh nghiệp (Sun Group, Vinpearl, TKV...)
    """
    from app.services.multi_source_crawler import multi_source_crawler
    from app.services.social_deep_harvester import social_deep_harvester

    # Cào đa nguồn kết hợp quét sâu mạng xã hội Facebook, Threads, TikTok
    portal_result = multi_source_crawler.execute_live_aggregation(
        keyword=q,
        province=province,
        max_per_source=max_items,
    )
    social_result = social_deep_harvester.execute_social_deep_harvest(keyword=q)

    total_all = portal_result["total_crawled"] + social_result["total_harvested"]
    return {
        "success": True,
        "query": q,
        "province": province,
        "total_crawled": total_all,
        "by_source": {
            "portals": portal_result["by_source"]["portals"],
            "facebook": social_result["by_platform"]["facebook"] + portal_result["by_source"]["social_media"],
            "threads": social_result["by_platform"]["threads"],
            "tiktok": social_result["by_platform"]["tiktok"],
            "corporate": portal_result["by_source"]["corporate"],
        },
        "saved_count": portal_result["saved_count"] + social_result["saved_count"],
        "conclusions": social_result["conclusions"],
        "message": f"⚡ Đã quét sâu thành công {total_all} tin từ Facebook, Threads, TikTok, Sàn tuyển dụng & Website Doanh nghiệp!",
    }


@router.post("/social-deep-harvest")
async def social_deep_harvest(
    q: Optional[str] = Query(None, description="Từ khóa chuyên biệt để mò sâu trên MXH"),
):
    """
    📱 Mò quét dữ liệu chuyên sâu đa mạng xã hội:
    - Facebook: Nhóm việc làm Hạ Long, Bãi Cháy, Quảng Ninh
    - Threads (Meta): Tuyển dụng Gen Z, Barista, F&B, Content Creator
    - TikTok: Tuyển dụng du thuyền 5 sao, Tiệm làm đẹp, Shipper đêm
    - Lọc bỏ 100% tin lừa đảo nhiệm vụ Telegram, cọc tiền gia công
    """
    from app.services.social_deep_harvester import social_deep_harvester

    result = social_deep_harvester.execute_social_deep_harvest(keyword=q)
    return result


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: SessionDep,
) -> JobResponse:
    """
    Lấy thông tin chi tiết một tin tuyển dụng theo mã định danh
    """
    job = await job_service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy việc làm với mã ID: {job_id}",
        )
    return job


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_or_upsert_job(
    job_in: JobCreate,
    db: SessionDep,
) -> JobResponse:
    """
    Thêm mới hoặc cập nhật việc làm (Upsert dựa theo source_url, dùng cho crawlers)
    """
    job = await job_service.upsert_job(db, job_in.source_url, job_in)
    return job
