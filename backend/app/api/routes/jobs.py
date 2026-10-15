import logging
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import SessionDep
from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobSearchParams,
)
from app.services.job_service import job_service
from app.services.ranking_engine import multi_signal_ranking_engine
from app.services.search_intent_parser import search_intent_parser
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    db: SessionDep,
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (q alias)"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm trong tiêu đề hoặc mô tả"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố làm việc"),
    category: Optional[str] = Query(None, description="Danh mục / Ngành nghề"),
    workplace_type: Optional[str] = Query(None, description="Nơi làm việc: onsite, hybrid, remote"),
    experience_level: Optional[str] = Query(None, description="Cấp độ kinh nghiệm: intern, fresher, junior, middle, senior, lead"),
    company_name: Optional[str] = Query(None, description="Tên công ty tuyển dụng"),
    job_type: Optional[str] = Query(None, description="Hình thức: full-time, part-time, remote, intern"),
    salary_min: Optional[int] = Query(None, ge=0, description="Mức lương tối thiểu (VNĐ)"),
    salary_max: Optional[int] = Query(None, ge=0, description="Mức lương tối đa (VNĐ)"),
    source_platform: Optional[str] = Query(None, description="Nền tảng cào dữ liệu: TopCV, VietnamWorks, ITviec..."),
    sort_by: Optional[str] = Query("newest", description="Sắp xếp: newest, relevance, salary_desc, salary_asc"),
    live: bool = Query(False, description="Tự động cào thêm tin mới từ các trang tuyển dụng và mạng xã hội trước khi trả về kết quả"),
    strict_mode: bool = Query(False, description="Chế độ khớp khắt khe các ràng buộc cứng"),
    verified_only: bool = Query(False, description="Chỉ lấy tin tuyển dụng đã xác minh (active_confirmed, active_likely)"),
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
        workplace_type=workplace_type,
        experience_level=experience_level,
        company_name=company_name,
        job_type=job_type,
        salary_min=salary_min,
        salary_max=salary_max,
        source_platform=source_platform,
        sort_by=sort_by,
        live=live,
        strict_mode=strict_mode,
        verified_only=verified_only,
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
        suggested_relaxations=diagnostics.get("suggested_relaxations", []) if diagnostics else [],
        diagnostics=diagnostics,
    )


@router.get("/search", response_model=JobListResponse)
async def search_jobs(
    db: SessionDep,
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm (q alias)"),
    query: Optional[str] = Query(None, description="Từ khóa tìm kiếm chính"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố"),
    category: Optional[str] = Query(None, description="Ngành nghề"),
    workplace_type: Optional[str] = Query(None, description="Nơi làm việc: onsite, hybrid, remote"),
    experience_level: Optional[str] = Query(None, description="Cấp độ kinh nghiệm: intern, fresher, junior, middle, senior, lead"),
    company_name: Optional[str] = Query(None, description="Tên công ty tuyển dụng"),
    job_type: Optional[str] = Query(None, description="Hình thức làm việc"),
    salary_min: Optional[int] = Query(None, ge=0, description="Mức lương tối thiểu"),
    salary_max: Optional[int] = Query(None, ge=0, description="Mức lương tối đa"),
    source_platform: Optional[str] = Query(None, description="Nguồn tuyển dụng"),
    sort_by: Optional[str] = Query("newest", description="Thứ tự: newest, relevance, salary_desc, salary_asc"),
    live: bool = Query(False, description="Tự động cào thêm tin mới từ các trang tuyển dụng và mạng xã hội"),
    strict_mode: bool = Query(False, description="Chế độ khớp khắt khe các ràng buộc cứng"),
    verified_only: bool = Query(False, description="Chỉ lấy tin tuyển dụng đã xác minh"),
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
        workplace_type=workplace_type,
        experience_level=experience_level,
        company_name=company_name,
        job_type=job_type,
        salary_min=salary_min,
        salary_max=salary_max,
        source_platform=source_platform,
        sort_by=sort_by,
        live=live,
        strict_mode=strict_mode,
        verified_only=verified_only,
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
        suggested_relaxations=diagnostics.get("suggested_relaxations", []) if diagnostics else [],
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


@router.get("/ranking-debug/compare")
async def compare_ranking_debug(
    db: SessionDep,
    job_a_id: str = Query(..., description="Mã ID tin tuyển dụng A"),
    job_b_id: str = Query(..., description="Mã ID tin tuyển dụng B"),
    q: Optional[str] = Query(None, description="Từ khóa hoặc truy vấn tìm kiếm"),
    province: Optional[str] = Query(None, description="Tỉnh/Thành phố mục tiêu"),
    strict_mode: bool = Query(False, description="Chế độ khớp ràng buộc cứng"),
):
    """
    So sánh chi tiết Pairwise Ranking Debug giữa 2 việc làm.
    Giải thích minh bạch tại sao một việc làm có thứ hạng cao hơn việc làm kia dựa trên 7 tín hiệu.
    """
    stmt_a = select(Job).where(Job.id == str(job_a_id))
    res_a = await db.execute(stmt_a)
    job_a = res_a.scalar_one_or_none()
    if not job_a:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy việc làm A với ID: {job_a_id}",
        )

    stmt_b = select(Job).where(Job.id == str(job_b_id))
    res_b = await db.execute(stmt_b)
    job_b = res_b.scalar_one_or_none()
    if not job_b:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy việc làm B với ID: {job_b_id}",
        )

    intent = search_intent_parser.parse_query(
        query=q,
        province=province,
        strict_mode=strict_mode,
    )
    result = multi_signal_ranking_engine.compare_ranking(job_a, job_b, intent)
    return result


@router.get("/ranking-debug/explain/{job_id}")
async def explain_job_ranking(
    job_id: str,
    db: SessionDep,
    q: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    province: Optional[str] = Query(None, description="Tỉnh / Thành phố"),
    strict_mode: bool = Query(False, description="Chế độ khớp ràng buộc cứng"),
):
    """
    Giải thích chi tiết bảng điểm 7 tín hiệu xếp hạng cho một tin tuyển dụng cụ thể.
    """
    stmt = select(Job).where(Job.id == str(job_id))
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy việc làm với ID: {job_id}",
        )

    intent = search_intent_parser.parse_query(
        query=q,
        province=province,
        strict_mode=strict_mode,
    )
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    breakdown = multi_signal_ranking_engine.score_job(job, intent, now)
    return {
        "job_id": str(job.id),
        "title": job.title,
        "company": job.company_name,
        "source_platform": job.source_platform,
        "status": job.status,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
        "crawled_at": job.crawled_at.isoformat() if job.crawled_at else None,
        "ranking_breakdown": breakdown.to_dict(),
    }


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
