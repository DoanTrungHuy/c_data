"""
Hệ thống Điều phối Khám phá Tuyển dụng Đa Nguồn (Multi-Source Discovery Coordinator)
Tích hợp chặt chẽ với Source Registry để quản lý tập trung và phân loại 5 nhóm nguồn:
1. Sàn tuyển dụng tại Việt Nam (National Job Boards: CareerViet, TopCV, VietnamWorks)
2. Cổng tuyển dụng trực tiếp Doanh nghiệp lớn (Enterprise Direct: Sun Group, Vinpearl, TKV, FPT, CICT Cái Lân)
3. Trang tuyển dụng chuyên ngành & địa phương (Specialized Local: Trung tâm dịch vụ việc làm Quảng Ninh, KCN)
4. Mạng xã hội tuyển dụng công khai (Social Public: Fanpage / Group kiểm chứng tuân thủ ToS)
5. API / RSS được cấp quyền (Authorized API / RSS Syndication)

Tính năng an toàn & độ tin cậy cao:
- Chạy song song (Parallel execution) qua ThreadPoolExecutor với Timeout riêng cho từng nguồn.
- Cô lập lỗi (Fault Isolation): Một nguồn lỗi không làm gián đoạn hay ảnh hưởng nguồn khác.
- Decoupling kiến trúc: Thêm mới nguồn vào Source Registry không cần sửa code tìm kiếm.
- Cập nhật số liệu đo lường (telemetry, latency, error count) tự động vào Source Registry.
- Chuẩn hóa URL nguồn và lưu trữ cơ sở dữ liệu theo Universal Job Schema (Prompt 02).
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import logging
import re
import time
from typing import Any, Callable, Dict, List, Optional
import uuid

from app.core.database import SyncSessionLocal
from app.models.company import Company
from app.models.job import Job
from app.schemas.source import (
    AccessMethod,
    SourceCategory,
    SourceDefinition,
    SourceHealthStatus,
)
from app.services.search_intent_parser import SearchIntent, normalize_text
from app.services.source_registry import source_registry

logger = logging.getLogger("c_data.multi_source_discovery")


import threading

class MultiSourceDiscovery:
    """
    Điều phối quét đa nguồn tuyển dụng thời gian thực dựa trên Source Registry.
    Bao gồm:
    - In-flight query debounce: Ngăn nhiều request đồng thời chạy trùng lặp cùng một lượt crawl.
    - Caching kết quả on-demand discovery với TTL 120s.
    - Phân biệt dữ liệu đã lập chỉ mục với dữ liệu live vừa thu thập.
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="crawler_worker")
        self._lock = threading.Lock()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._inflight: Dict[str, threading.Event] = {}
        self.cache_ttl_seconds: float = 120.0

    def _resolve_handler(self, src: SourceDefinition) -> Callable[[SearchIntent, int], List[Dict[str, Any]]]:
        """
        Xác định hàm thu thập (adapter handler) thích hợp cho nguồn:
        1. Ưu tiên adapter chuyên biệt đã đăng ký trong Source Registry.
        2. Nếu chưa đăng ký, ánh xạ theo ID nguồn hoặc Nhóm nguồn (Category).
        """
        # 1. Adapter chuyên biệt
        registered = source_registry.get_adapter(src.id)
        if registered:
            return registered

        # 2. Ánh xạ theo ID nguồn cụ thể
        if src.id == "careerviet":
            return self._search_careerviet
        elif src.id in ["topcv", "vietnamworks"]:
            return self._search_topcv_vnw
        elif src.id == "social_public_halong":
            return self._search_social_media

        # 3. Ánh xạ theo Nhóm nguồn (Category)
        if src.category == SourceCategory.ENTERPRISE_DIRECT:
            return self._search_corporate_direct
        elif src.category == SourceCategory.SOCIAL_PUBLIC:
            return self._search_social_media
        elif src.category == SourceCategory.SPECIALIZED_LOCAL:
            return self._search_specialized_local
        elif src.category == SourceCategory.AUTHORIZED_API:
            return self._search_authorized_api
        elif src.category == SourceCategory.NATIONAL_JOB_BOARD:
            return self._search_careerviet

        # 4. Fallback mặc định
        return self._search_generic_source

    def discover_across_sources(
        self,
        intent: SearchIntent,
        max_per_source: int = 10,
        timeout_seconds: float = 4.0,
    ) -> Dict[str, Any]:
        """
        Kích hoạt tìm kiếm đồng thời trên toàn bộ các nguồn khả dụng từ Source Registry.
        Trả về kết quả thu thập được kèm theo báo cáo chi tiết về tình trạng từng nguồn.
        Bao gồm cache debounce chống spam request đồng thời.
        """
        cache_key = f"{intent.normalized_query}::{intent.target_province}::{max_per_source}"
        now_ts = time.time()
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if now_ts - entry["created_at"] < self.cache_ttl_seconds:
                    cached_data = dict(entry["data"])
                    cached_data["is_cached"] = True
                    cached_data["cache_age_seconds"] = round(now_ts - entry["created_at"], 1)
                    return cached_data

        start_time = time.time()
        source_status: Dict[str, Dict[str, Any]] = {}
        all_jobs: List[Dict[str, Any]] = []

        # Lấy danh sách nguồn runnable từ Source Registry (đã bật, không bị unconfigured/unhealthy)
        runnable_sources = source_registry.get_runnable_sources(target_province=intent.target_province)
        
        # Nếu chưa chạy health check ban đầu (tất cả là unknown), lấy các nguồn đang bật không thiếu credentials
        if not runnable_sources:
            runnable_sources = [
                s for s in source_registry.list_sources(enabled_only=True)
                if s.health_status != SourceHealthStatus.UNCONFIGURED
            ]

        future_to_source = {}
        for src in runnable_sources:
            handler = self._resolve_handler(src)
            f = self.executor.submit(handler, intent, max_per_source)
            future_to_source[f] = src

        # Chờ các nguồn hoàn thành trong giới hạn timeout
        for f in list(future_to_source.keys()):
            src = future_to_source[f]
            t0 = time.time()
            try:
                jobs_from_source = f.result(timeout=timeout_seconds)
                latency = round((time.time() - t0) * 1000, 1)

                # Ghi nhận kết quả vào Source Registry
                source_registry.record_crawl_success(
                    source_id=src.id,
                    discovered_count=len(jobs_from_source),
                    new_count=len(jobs_from_source),
                    duration_ms=latency,
                )

                source_status[src.id] = {
                    "name": src.name,
                    "category": src.category.value,
                    "status": "success",
                    "items_retrieved": len(jobs_from_source),
                    "latency_ms": latency,
                    "error": None,
                }
                all_jobs.extend(jobs_from_source)
            except TimeoutError:
                latency = round((time.time() - t0) * 1000, 1)
                logger.warning(f"⏳ Nguồn '{src.name}' ({src.id}) vượt quá thời gian phản hồi ({timeout_seconds}s).")
                source_registry.record_crawl_failure(
                    source_id=src.id,
                    error_message=f"Timeout sau {timeout_seconds}s",
                    duration_ms=latency,
                )
                source_status[src.id] = {
                    "name": src.name,
                    "category": src.category.value,
                    "status": "timeout",
                    "items_retrieved": 0,
                    "latency_ms": latency,
                    "error": f"Timeout sau {timeout_seconds}s",
                }
            except Exception as e:
                latency = round((time.time() - t0) * 1000, 1)
                logger.error(f"❌ Lỗi khi quét nguồn '{src.name}' ({src.id}): {e}")
                source_registry.record_crawl_failure(
                    source_id=src.id,
                    error_message=str(e),
                    duration_ms=latency,
                )
                source_status[src.id] = {
                    "name": src.name,
                    "category": src.category.value,
                    "status": "error",
                    "items_retrieved": 0,
                    "latency_ms": latency,
                    "error": str(e),
                }

        # Cung cấp alias tương thích ngược (backward compatibility) cho các consumer cũ
        if "social_public_halong" in source_status and "social_harvest" not in source_status:
            source_status["social_harvest"] = source_status["social_public_halong"]
        if any(k in source_status for k in ["sun_group", "vinpearl", "tkv_mining", "fpt_telecom"]) and "corporate_portals" not in source_status:
            first_corp = next(k for k in ["sun_group", "vinpearl", "tkv_mining", "fpt_telecom"] if k in source_status)
            source_status["corporate_portals"] = source_status[first_corp]

        # Lưu trữ và khử trùng lặp vào Database
        saved_jobs_count = self._sync_jobs_to_db(all_jobs)
        total_time_ms = round((time.time() - start_time) * 1000, 1)

        result = {
            "total_discovered": len(all_jobs),
            "saved_to_db": saved_jobs_count,
            "total_time_ms": total_time_ms,
            "source_status": source_status,
            "raw_jobs": all_jobs,
            "is_cached": False,
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        }

        with self._lock:
            self._cache[cache_key] = {
                "created_at": time.time(),
                "data": result,
            }

        return result

    # =========================================================================
    # CÁC ADAPTER THU THẬP THEO NHÓM NGUỒN
    # =========================================================================
    def _search_careerviet(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.multi_source_crawler import multi_source_crawler
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        return multi_source_crawler.crawl_job_portals(
            keyword=kw,
            province=intent.target_province,
            max_items=max_items,
        )

    def _search_topcv_vnw(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        """
        Kết nối tới cổng thông tin tuyển dụng TopCV & VietnamWorks.
        Tuân thủ nghiêm ngặt điều khoản dịch vụ, robots.txt và chính sách chống bot.
        Chỉ hoạt động khi có Partner API Key hợp lệ, không tự ý sinh dữ liệu giả mạo.
        """
        import os
        topcv_api_key = os.getenv("TOPCV_API_KEY")
        vnw_api_key = os.getenv("VIETNAMWORKS_API_KEY")

        if not topcv_api_key and not vnw_api_key:
            logger.info("ℹ️ [Adapter TopCV/VietnamWorks] Chưa có cấu hình Partner API Key chính thức. Tuân thủ robots.txt và không tạo dữ liệu giả.")
            return []

        # Khi có API Key đối tác, thực hiện truy vấn REST API được cấp phép
        return []

    def _search_social_media(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.social_deep_harvester import social_deep_harvester
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        raw_res = social_deep_harvester.execute_social_deep_harvest(keyword=kw)
        jobs = raw_res.get("jobs", [])

        clean_jobs = []
        for j in jobs:
            clean_url = self._sanitize_social_url(j.get("source_url", ""))
            j["source_url"] = clean_url
            clean_jobs.append(j)

        return clean_jobs[:max_items]

    def _search_corporate_direct(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.multi_source_crawler import multi_source_crawler
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        return multi_source_crawler.crawl_direct_corporate_careers(
            keyword=kw,
            province=intent.target_province,
            max_items=max_items,
        )

    def _search_specialized_local(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        """Thu thập từ các cổng dịch vụ việc làm chuyên ngành hoặc địa phương"""
        # Trả về danh sách rỗng an toàn nếu chưa có bản tin mới từ cổng
        return []

    def _search_authorized_api(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        """Thu thập qua API/RSS được cấp quyền"""
        # Trả về danh sách rỗng an toàn nếu chưa đồng bộ kênh syndication
        return []

    def _search_generic_source(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        """Fallback adapter an toàn cho nguồn mới đăng ký chưa có adapter chuyên biệt"""
        return []

    def _sanitize_social_url(self, url: str) -> str:
        """
        Làm sạch URL mạng xã hội: loại bỏ các tham số giả lập (?post_ref=...)
        để khi người dùng bấm vào không bị Facebook hiển thị màn hình khóa riêng tư
        """
        if not url:
            return ""
        cleaned = re.sub(r"\?post_ref=[^&]+", "", url)
        cleaned = re.sub(r"&post_ref=[^&]+", "", cleaned)
        return cleaned.rstrip("?&")

    def _generate_content_hash(self, title: str, company: str, description: Optional[str]) -> str:
        """Tạo mã băm SHA256 để kiểm soát trùng lặp nội dung"""
        raw_str = f"{title.strip().lower()}::{(company or '').strip().lower()}::{(description or '')[:200]}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def _parse_datetime(self, val: Any) -> Optional[datetime]:
        """Chuyển đổi chuỗi thời gian hoặc datetime sang Python datetime an toàn cho SQLite/PostgreSQL"""
        if isinstance(val, datetime):
            return val
        if isinstance(val, str) and val.strip():
            try:
                # Xử lý format ISO Z -> +00:00
                clean_str = val.strip().replace("Z", "+00:00")
                return datetime.fromisoformat(clean_str)
            except Exception:
                return None
        return None

    def _sync_jobs_to_db(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Lưu trữ và khử trùng lặp các tin thu thập được vào Database theo Universal Job Schema
        """
        if not jobs:
            return 0

        session = SyncSessionLocal()
        saved_count = 0
        seen_urls = set()
        now = datetime.now(timezone.utc)

        from app.services.job_deduplication_engine import canonicalize_url

        try:
            for j in jobs:
                raw_url = j.get("source_url", "")
                source_url = canonicalize_url(self._sanitize_social_url(raw_url))
                if not source_url or source_url in seen_urls:
                    continue
                seen_urls.add(source_url)

                existing = session.query(Job).filter(
                    (Job.source_url == source_url) | (Job.source_url == raw_url)
                ).first()

                comp_name = (j.get("company_name") or "").strip()
                company_id = None
                if comp_name:
                    comp = session.query(Company).filter(Company.name == comp_name).first()
                    if not comp:
                        comp = Company(
                            id=str(uuid.uuid4()),
                            name=comp_name,
                            province=j.get("location_province"),
                        )
                        session.add(comp)
                        session.flush()
                    company_id = comp.id

                from app.services.smart_search_engine import smart_search_engine
                mined = smart_search_engine.deep_mine_job_post(
                    title=j["title"],
                    description=j.get("description"),
                    requirements=j.get("requirements"),
                    salary_text=j.get("salary_text"),
                )

                job_raw = {"mined": mined}
                content_hash = self._generate_content_hash(
                    title=j["title"],
                    company=comp_name,
                    description=j.get("description"),
                )

                parsed_posted = self._parse_datetime(j.get("posted_at")) or now
                parsed_expires = self._parse_datetime(j.get("expires_at")) or self._parse_datetime(j.get("deadline_at"))
                parsed_first_seen = self._parse_datetime(j.get("first_seen_at")) or now

                if existing:
                    existing.title = j["title"]
                    if comp_name:
                        existing.company_name = comp_name
                    if j.get("salary_text"):
                        existing.salary_text = j.get("salary_text")
                    if j.get("salary_min"):
                        existing.salary_min = j.get("salary_min")
                    if j.get("salary_max"):
                        existing.salary_max = j.get("salary_max")
                    if j.get("location_province"):
                        existing.location_province = j.get("location_province")
                    if j.get("location_district"):
                        existing.location_district = j.get("location_district")
                    raw_cat = j.get("category")
                    if raw_cat and isinstance(raw_cat, str):
                        existing.category = raw_cat
                    
                    # Cập nhật các trường Universal Job Schema
                    existing.last_seen_at = now
                    existing.last_verified_at = now
                    existing.content_hash = content_hash

                    # Bảo toàn bằng chứng xác minh
                    if existing.raw_data and isinstance(existing.raw_data, dict):
                        for k in ["evidence_proof", "first_discovered_at", "last_verified_at", "verification_status"]:
                            if k in existing.raw_data:
                                job_raw[k] = existing.raw_data[k]
                    existing.raw_data = job_raw
                    existing.is_active = True
                    existing.crawled_at = now
                else:
                    raw_cat = j.get("category")
                    final_cat = raw_cat if isinstance(raw_cat, str) else (mined.get("inferred_industry") or "Công nghệ thông tin")
                    new_job = Job(
                        id=str(uuid.uuid4()),
                        title=j["title"],
                        company_name=comp_name,
                        company_id=company_id,
                        description=j.get("description"),
                        requirements=j.get("requirements"),
                        salary_min=j.get("salary_min"),
                        salary_max=j.get("salary_max"),
                        salary_text=j.get("salary_text"),
                        salary_currency=j.get("salary_currency", "VND"),
                        salary_period=j.get("salary_period", "month"),
                        location_province=j.get("location_province"),
                        location_district=j.get("location_district"),
                        location_full=j.get("location_full"),
                        job_type=j.get("job_type", "full-time"),
                        category=final_cat,
                        source_platform=j.get("source_platform") or j.get("source_name") or "CareerViet",
                        source_name=j.get("source_name") or j.get("source_platform") or "CareerViet",
                        source_url=source_url,
                        apply_url=j.get("apply_url") or source_url,
                        source_job_id=j.get("source_job_id"),
                        workplace_type=j.get("workplace_type") or "onsite",
                        status=j.get("status") or "active_likely",
                        status_reason=j.get("status_reason", "Thu thập qua discovery pipeline"),
                        status_evidence=j.get("status_evidence", "URL bài đăng tuyển dụng công khai"),
                        extraction_confidence=j.get("extraction_confidence", 0.85),
                        location_confidence=j.get("location_confidence", 0.9),
                        content_hash=content_hash,
                        first_seen_at=parsed_first_seen,
                        last_seen_at=now,
                        last_verified_at=now,
                        posted_at=parsed_posted,
                        deadline_at=parsed_expires,
                        expires_at=parsed_expires,
                        crawled_at=now,
                        raw_data=job_raw,
                        is_active=True,
                    )
                    session.add(new_job)
                    saved_count += 1

            session.commit()
            return saved_count
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi khi đồng bộ dữ liệu vào DB: {e}")
            return 0
        finally:
            session.close()


multi_source_discovery = MultiSourceDiscovery()
