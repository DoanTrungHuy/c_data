import math
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.job import Job
from app.schemas.job import JobCreate, JobSearchParams, JobUpdate


class JobService:
    """
    Service xử lý các nghiệp vụ liên quan đến việc làm:
    - Tìm kiếm, phân trang và lọc đa tiêu chí
    - Cào và cập nhật dữ liệu (Upsert / Deduplication)
    - Tự động liên kết công ty và làm sạch dữ liệu
    - Vô hiệu hóa các tin tuyển dụng đã hết hạn
    """

    async def get_jobs(
        self,
        db: AsyncSession,
        params: JobSearchParams,
    ) -> Tuple[List[Job], int, int, List[str], List[str], Dict[str, Any]]:
        """
        Lấy danh sách việc làm theo các điều kiện lọc, phân tích ngữ nghĩa sâu và gợi ý từ khóa.
        Sử dụng SearchIntentParser, MultiSourceDiscovery và HybridSearchEngine.
        Trả về tuple: (danh_sách_job, tổng_số_bản_ghi, tổng_số_trang, từ_khóa_gợi_ý, ngành_suy_luận, chẩn_đoán)
        """
        from app.services.search_intent_parser import search_intent_parser
        from app.services.hybrid_search_engine import hybrid_search_engine
        from app.services.multi_source_discovery import multi_source_discovery

        now_dt = datetime.now(timezone.utc)
        search_query = (params.q or params.query or "").strip()

        # 1. Phân tích ý định tìm kiếm có cấu trúc (SearchIntent)
        intent = search_intent_parser.parse(search_query)

        # Ghi đè hoặc bổ sung thông tin từ UI bộ lọc nếu người dùng chọn trực tiếp
        if params.province:
            intent.target_province = params.province.strip()
            if intent.target_province not in intent.location_aliases:
                intent.location_aliases.insert(0, intent.target_province)

        # 2. Quét đa nguồn thời gian thực nếu được yêu cầu (live=True)
        discovery_telemetry = None
        if params.live:
            try:
                discovery_telemetry = multi_source_discovery.discover_across_sources(
                    intent=intent,
                    max_per_source=8,
                    timeout_seconds=3.5,
                )
            except Exception as e:
                logger.warning(f"Lỗi khi điều phối khám phá đa nguồn: {e}")

        # 3. Thu hồi ứng viên từ Cơ sở dữ liệu (Candidate Retrieval)
        base_filters = [
            Job.is_active.is_(True),
            Job.status.notin_(["expired", "closed"]),
            or_(Job.deadline_at.is_(None), Job.deadline_at >= now_dt),
            or_(Job.expires_at.is_(None), Job.expires_at >= now_dt),
        ]

        if params.category:
            base_filters.append(Job.category.ilike(f"%{params.category.strip()}%"))

        if params.province:
            base_filters.append(
                or_(
                    Job.location_province.ilike(f"%{params.province.strip()}%"),
                    Job.location_district.ilike(f"%{params.province.strip()}%"),
                    Job.location_full.ilike(f"%{params.province.strip()}%"),
                )
            )

        if getattr(params, "workplace_type", None):
            base_filters.append(Job.workplace_type.ilike(f"%{params.workplace_type.strip()}%"))

        if params.job_type:
            base_filters.append(
                or_(
                    Job.job_type.ilike(f"%{params.job_type.strip()}%"),
                    Job.workplace_type.ilike(f"%{params.job_type.strip()}%"),
                    Job.employment_type.ilike(f"%{params.job_type.strip()}%"),
                )
            )

        if getattr(params, "source_name", None):
            base_filters.append(
                or_(
                    Job.source_name.ilike(f"%{params.source_name.strip()}%"),
                    Job.source_platform.ilike(f"%{params.source_name.strip()}%"),
                )
            )
        elif params.source_platform:
            base_filters.append(
                or_(
                    Job.source_platform.ilike(f"%{params.source_platform.strip()}%"),
                    Job.source_name.ilike(f"%{params.source_platform.strip()}%"),
                )
            )

        if getattr(params, "experience_level", None):
            base_filters.append(Job.experience_level.ilike(f"%{params.experience_level.strip()}%"))

        if getattr(params, "company_name", None):
            base_filters.append(Job.company_name.ilike(f"%{params.company_name.strip()}%"))

        if getattr(params, "verified_only", False):
            base_filters.append(Job.status.in_(["active_confirmed", "active_likely"]))

        if getattr(params, "status", None):
            base_filters.append(Job.status == params.status.strip())

        if params.salary_min is not None:
            base_filters.append(
                or_(
                    Job.salary_max >= params.salary_min,
                    Job.salary_min >= params.salary_min,
                )
            )
        if params.salary_max is not None:
            base_filters.append(
                or_(
                    Job.salary_min <= params.salary_max,
                    Job.salary_max <= params.salary_max,
                )
            )

        # Thu hồi ứng viên theo ngữ nghĩa và từ khóa mở rộng (Không dùng AND gây mất tin)
        candidate_filters = list(base_filters)
        if search_query:
            query_match_clauses = []

            # A. Khớp các từ đồng nghĩa và biến thể vai trò nghề nghiệp
            for syn in intent.role_synonyms[:6]:
                syn_clean = syn.strip()
                if len(syn_clean) >= 2:
                    query_match_clauses.append(Job.title.ilike(f"%{syn_clean}%"))
                    query_match_clauses.append(Job.category.ilike(f"%{syn_clean}%"))

            # B. Khớp các kỹ năng công nghệ yêu cầu
            for skill in intent.required_skills:
                query_match_clauses.append(Job.title.ilike(f"%{skill}%"))
                query_match_clauses.append(Job.description.ilike(f"%{skill}%"))

            # C. Khớp từ khóa ngắn hoặc từ viết tắt (IT, AI, B2, TKV...)
            clean_tokens = [t for t in intent.normalized_query.split() if len(t) >= 2]
            for tok in clean_tokens[:4]:
                if tok in ["it", "cntt", "ai", "b2", "tkv"]:
                    query_match_clauses.append(Job.title.ilike(f"%{tok}%"))
                elif len(tok) >= 4:
                    query_match_clauses.append(Job.title.ilike(f"%{tok}%"))
                    query_match_clauses.append(Job.description.ilike(f"%{tok}%"))

            if query_match_clauses:
                candidate_filters.append(or_(*query_match_clauses))

        # Lấy tập ứng viên (Fetch candidate pool)
        fetch_limit = 150 if search_query else params.page_size * 2
        candidate_stmt = (
            select(Job)
            .options(selectinload(Job.company))
            .where(and_(*candidate_filters))
            .order_by(Job.posted_at.desc().nullslast(), Job.crawled_at.desc())
            .limit(fetch_limit)
        )

        res = await db.execute(candidate_stmt)
        candidate_jobs = list(res.scalars().all())

        # Nếu tìm kiếm cụ thể mà tập ứng viên lọc quá hẹp, nới lỏng khi KHÔNG bật strict_mode
        if search_query and len(candidate_jobs) < 10 and not params.strict_mode:
            relaxed_stmt = (
                select(Job)
                .options(selectinload(Job.company))
                .where(and_(*base_filters))
                .order_by(Job.posted_at.desc().nullslast(), Job.crawled_at.desc())
                .limit(100)
            )
            relaxed_res = await db.execute(relaxed_stmt)
            existing_ids = {j.id for j in candidate_jobs}
            for rj in relaxed_res.scalars().all():
                if rj.id not in existing_ids:
                    candidate_jobs.append(rj)

        # 4. Chấm điểm độ phù hợp và xếp hạng có thể giải thích (Hybrid Ranking & Explainability)
        ranked_items, diagnostics = hybrid_search_engine.rank_and_filter_jobs(
            candidate_jobs=candidate_jobs,
            intent=intent,
            strict_mode=params.strict_mode,
            verified_only=getattr(params, "verified_only", False),
            sort_by=getattr(params, "sort_by", "newest"),
            workplace_type=getattr(params, "workplace_type", None),
            experience_level=getattr(params, "experience_level", None),
            company_name=getattr(params, "company_name", None),
        )


        if discovery_telemetry:
            diagnostics["multi_source_discovery"] = discovery_telemetry

        # 5. Phân trang kết quả
        total = len(ranked_items)
        offset = (params.page - 1) * params.page_size
        paged_items = ranked_items[offset : offset + params.page_size]

        jobs = []
        for item in paged_items:
            j = item["job"]
            j.all_sources = item.get("all_sources")
            j.match_reasons = item.get("reasons")
            j.match_score = round(item.get("score", 0.0), 1)
            j.ranking_breakdown = item.get("ranking_breakdown")
            jobs.append(j)

        total_pages = math.ceil(total / params.page_size) if total > 0 else 0

        related_suggestions = intent.role_synonyms[:6] if intent.role_synonyms else [
            "IT Helpdesk Hạ Long", "Lập trình viên React", "IT Officer Khách Sạn",
            "Kế toán tổng hợp", "Lái xe B2 Du lịch", "Thợ mỏ than TKV",
        ]
        matched_industries = [intent.primary_role] if intent.primary_role else []

        return jobs, total, total_pages, related_suggestions, matched_industries, diagnostics

    async def get_job_by_id(
        self,
        db: AsyncSession,
        job_id: str,
    ) -> Optional[Job]:
        """
        Lấy thông tin chi tiết một tin tuyển dụng theo ID.
        Nếu tin đã hết hạn hoặc không còn hiệu lực, tự động vô hiệu hóa (is_active=False).
        """
        stmt = (
            select(Job)
            .options(selectinload(Job.company))
            .where(Job.id == str(job_id))
        )
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            return None

        # Tự động vô hiệu hóa nếu tin đã quá hạn nộp
        now_dt = datetime.now(timezone.utc)
        effective_deadline = job.deadline_at or job.expires_at
        if effective_deadline:
            dl_utc = effective_deadline if effective_deadline.tzinfo else effective_deadline.replace(tzinfo=timezone.utc)
            if dl_utc < now_dt:
                job.is_active = False
                job.status = "expired"
                job.status_reason = f"Đã quá hạn nộp hồ sơ ({dl_utc.date()})"
                await db.commit()
                return None

        if not job.is_active or job.status in ["expired", "closed"]:
            return None

        return job

    async def search_jobs(
        self,
        db: AsyncSession,
        params: JobSearchParams,
    ) -> Tuple[List[Job], int, int, List[str], List[str], Dict[str, Any]]:
        """
        Tìm kiếm nâng cao việc làm (tận dụng logic get_jobs)
        """
        return await self.get_jobs(db, params)

    async def get_or_create_company(
        self,
        db: AsyncSession,
        company_name: str,
        province: Optional[str] = None,
        logo_url: Optional[str] = None,
        website: Optional[str] = None,
    ) -> Optional[Company]:
        """
        Tìm hoặc tạo mới một công ty theo tên để liên kết với tin tuyển dụng
        """
        name_clean = company_name.strip()
        if not name_clean:
            return None

        stmt = select(Company).where(func.lower(Company.name) == func.lower(name_clean))
        res = await db.execute(stmt)
        company = res.scalar_one_or_none()

        if not company:
            company = Company(
                name=name_clean,
                province=province,
                logo_url=logo_url,
                website=website,
            )
            db.add(company)
            await db.flush()
        else:
            # Cập nhật thông tin bổ sung nếu trước đó chưa có
            updated = False
            if not company.logo_url and logo_url:
                company.logo_url = logo_url
                updated = True
            if not company.website and website:
                company.website = website
                updated = True
            if not company.province and province:
                company.province = province
                updated = True
            if updated:
                await db.flush()

        return company

    async def create_job(
        self,
        db: AsyncSession,
        data: Union[JobCreate, Dict[str, Any]],
    ) -> Job:
        """
        Tạo mới một tin tuyển dụng từ dữ liệu crawler
        """
        job_dict = data.model_dump() if isinstance(data, JobCreate) else dict(data)

        # Xử lý liên kết công ty nếu có tên công ty
        company_name = job_dict.get("company_name")
        company_id = job_dict.get("company_id")
        if company_name and not company_id:
            company = await self.get_or_create_company(
                db=db,
                company_name=company_name,
                province=job_dict.get("location_province"),
            )
            if company:
                job_dict["company_id"] = company.id

        new_job = Job(**job_dict)
        new_job.sync_universal_fields()
        db.add(new_job)
        await db.commit()
        await db.refresh(new_job)
        return new_job

    async def upsert_job(
        self,
        db: AsyncSession,
        source_url: str,
        data: Union[JobCreate, Dict[str, Any]],
    ) -> Job:
        """
        Cập nhật hoặc thêm mới tin tuyển dụng dựa trên source_url (Deduplication).
        Nếu URL đã tồn tại trong DB, cập nhật lại dữ liệu mới nhất và kích hoạt lại (is_active=True).
        """
        job_dict = data.model_dump() if isinstance(data, JobCreate) else dict(data)
        job_dict["source_url"] = source_url

        stmt = select(Job).options(selectinload(Job.company)).where(Job.source_url == source_url)
        res = await db.execute(stmt)
        existing_job = res.scalar_one_or_none()

        # Tìm hoặc tạo công ty
        company_name = job_dict.get("company_name")
        if company_name:
            company = await self.get_or_create_company(
                db=db,
                company_name=company_name,
                province=job_dict.get("location_province"),
            )
            if company:
                job_dict["company_id"] = company.id

        if existing_job:
            for key, value in job_dict.items():
                if key not in ("id", "created_at", "crawled_at", "first_seen_at") and hasattr(existing_job, key):
                    if value is not None or key == "is_active":
                        setattr(existing_job, key, value)
            existing_job.crawled_at = datetime.now(timezone.utc)
            existing_job.last_seen_at = datetime.now(timezone.utc)
            existing_job.sync_universal_fields()
            await db.commit()
            await db.refresh(existing_job)
            return existing_job
        else:
            return await self.create_job(db, job_dict)

    async def deactivate_expired_jobs(self, db: AsyncSession) -> int:
        """
        Vô hiệu hóa (is_active = False, status = 'expired') cho toàn bộ các tin tuyển dụng đã qua ngày hết hạn
        """
        now_dt = datetime.now(timezone.utc)
        stmt = (
            update(Job)
            .where(
                and_(
                    Job.status.in_(["active_confirmed", "active_likely", "unknown"]),
                    or_(
                        and_(Job.deadline_at.is_not(None), Job.deadline_at < now_dt),
                        and_(Job.expires_at.is_not(None), Job.expires_at < now_dt),
                    ),
                )
            )
            .values(
                is_active=False,
                status="expired",
                status_reason=f"Đã qua hạn chót nộp hồ sơ theo chu kỳ kiểm tra tự động ({now_dt.date()})",
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount or 0


# Singleton instance
job_service = JobService()
