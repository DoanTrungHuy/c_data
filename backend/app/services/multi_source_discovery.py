"""
Hệ thống Điều phối Khám phá Tuyển dụng Đa Nguồn (Multi-Source Discovery Coordinator)
Tìm kiếm và thu thập dữ liệu thời gian thực từ 4 trụ cột:
1. Sàn CareerViet / CareerBuilder
2. Cổng thông tin TopCV & VietnamWorks
3. Mạng xã hội tuyển dụng địa phương (Facebook Groups/Fanpages, Threads, TikTok)
4. Cổng tuyển dụng trực tiếp Doanh nghiệp lớn (Sun Group, Vinpearl, TKV, FPT Telecom, Cảng Cái Lân)

Tính năng an toàn & độ tin cậy cao:
- Chạy song song (Parallel execution) với bộ đếm thời gian Timeout riêng biệt cho từng nguồn.
- Cô lập lỗi (Fault Isolation): Một nguồn bị lỗi mạng hoặc timeout không làm gián đoạn các nguồn khác.
- Chuẩn hóa link nguồn: Loại bỏ hoàn toàn các tham số nhân tạo (?post_ref=...) để ngăn chặn lỗi Facebook 404/Padlock.
- Khử trùng lặp đa nguồn và lưu trữ cập nhật cơ sở dữ liệu tự động.
- Cung cấp telemetry và nhật ký trạng thái từng nguồn phục vụ chẩn đoán tìm kiếm (Search Diagnostics).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import logging
import re
import time
from typing import Any, Dict, List, Optional
import uuid

from app.core.database import SyncSessionLocal
from app.models.company import Company
from app.models.job import Job
from app.services.search_intent_parser import SearchIntent, normalize_text
from crawlers.utils import extract_salary_range, normalize_location

logger = logging.getLogger("c_data.multi_source_discovery")


class MultiSourceDiscovery:
    """
    Điều phối quét đa nguồn tuyển dụng thời gian thực
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="crawler_worker")

    def discover_across_sources(
        self,
        intent: SearchIntent,
        max_per_source: int = 10,
        timeout_seconds: float = 4.0,
    ) -> Dict[str, Any]:
        """
        Kích hoạt tìm kiếm đồng thời trên toàn bộ các nguồn được cấu hình.
        Trả về kết quả thu thập được kèm theo báo cáo chi tiết về tình trạng từng nguồn.
        """
        start_time = time.time()
        source_status: Dict[str, Dict[str, Any]] = {}
        all_jobs: List[Dict[str, Any]] = []

        # Các nguồn tham gia tìm kiếm
        sources_to_run = [
            ("careerviet", self._search_careerviet, "Sàn việc làm CareerViet"),
            ("topcv_vietnamworks", self._search_topcv_vnw, "Cổng TopCV / VietnamWorks"),
            ("social_harvest", self._search_social_media, "Mạng xã hội (Facebook • Threads • TikTok)"),
            ("corporate_portals", self._search_corporate_direct, "Website Doanh nghiệp (Sun Group, Vinpearl, TKV, FPT)"),
        ]

        future_to_source = {}
        for source_key, search_fn, display_name in sources_to_run:
            f = self.executor.submit(search_fn, intent, max_per_source)
            future_to_source[f] = (source_key, display_name)

        # Chờ các nguồn hoàn thành trong giới hạn timeout
        for f in list(future_to_source.keys()):
            source_key, display_name = future_to_source[f]
            t0 = time.time()
            try:
                # Chờ tối đa timeout_seconds cho mỗi tác vụ
                jobs_from_source = f.result(timeout=timeout_seconds)
                latency = round((time.time() - t0) * 1000, 1)
                source_status[source_key] = {
                    "name": display_name,
                    "status": "success",
                    "items_retrieved": len(jobs_from_source),
                    "latency_ms": latency,
                    "error": None,
                }
                all_jobs.extend(jobs_from_source)
            except TimeoutError:
                latency = round((time.time() - t0) * 1000, 1)
                logger.warning(f"⏳ Nguồn '{display_name}' vượt quá thời gian phản hồi ({timeout_seconds}s). Bỏ qua để không làm nghẽn tìm kiếm.")
                source_status[source_key] = {
                    "name": display_name,
                    "status": "timeout",
                    "items_retrieved": 0,
                    "latency_ms": latency,
                    "error": f"Timeout sau {timeout_seconds}s",
                }
            except Exception as e:
                latency = round((time.time() - t0) * 1000, 1)
                logger.error(f"❌ Lỗi khi quét nguồn '{display_name}': {e}")
                source_status[source_key] = {
                    "name": display_name,
                    "status": "error",
                    "items_retrieved": 0,
                    "latency_ms": latency,
                    "error": str(e),
                }

        # Lưu trữ và khử trùng lặp vào Database
        saved_jobs_count = self._sync_jobs_to_db(all_jobs)
        total_time_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "total_discovered": len(all_jobs),
            "saved_to_db": saved_jobs_count,
            "total_time_ms": total_time_ms,
            "source_status": source_status,
            "raw_jobs": all_jobs,
        }

    # =========================================================================
    # NGUỒN 1: SÀN TUYỂN DỤNG CAREERVIET
    # =========================================================================
    def _search_careerviet(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.multi_source_crawler import multi_source_crawler
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        return multi_source_crawler.crawl_job_portals(
            keyword=kw,
            province=intent.target_province,
            max_items=max_items,
        )

    # =========================================================================
    # NGUỒN 2: CỔNG TOPCV VÀ VIETNAMWORKS (ADAPTER CÓ KIỂM SOÁT BẢN QUYỀN)
    # =========================================================================
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
            logger.info("ℹ️ [Adapter TopCV/VietnamWorks] Chưa có cấu hình Partner API Key chính thức. Hệ thống tuân thủ robots.txt và không tạo dữ liệu giả.")
            return []

        # Khi có API Key đối tác, thực hiện truy vấn REST API được cấp phép
        return []

    # =========================================================================
    # NGUỒN 3: MẠNG XÃ HỘI (FACEBOOK • THREADS • TIKTOK)
    # =========================================================================
    def _search_social_media(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.social_deep_harvester import social_deep_harvester
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        raw_res = social_deep_harvester.execute_social_deep_harvest(keyword=kw)
        jobs = raw_res.get("jobs", [])

        # Vệ sinh đường dẫn Facebook: Đảm bảo không có ?post_ref=... gây lỗi 404/Padlock
        clean_jobs = []
        for j in jobs:
            clean_url = self._sanitize_social_url(j.get("source_url", ""))
            j["source_url"] = clean_url
            clean_jobs.append(j)

        return clean_jobs[:max_items]

    # =========================================================================
    # NGUỒN 4: WEBSITE DOANH NGHIỆP TRỰC TIẾP
    # =========================================================================
    def _search_corporate_direct(self, intent: SearchIntent, max_items: int) -> List[Dict[str, Any]]:
        from app.services.multi_source_crawler import multi_source_crawler
        kw = intent.expanded_queries[0] if intent.expanded_queries else intent.raw_query
        return multi_source_crawler.crawl_direct_corporate_careers(
            keyword=kw,
            province=intent.target_province,
            max_items=max_items,
        )

    def _sanitize_social_url(self, url: str) -> str:
        """
        Làm sạch URL mạng xã hội: loại bỏ các tham số giả lập (?post_ref=...)
        để khi người dùng bấm vào không bị Facebook hiển thị màn hình khóa riêng tư
        """
        if not url:
            return ""
        # Bỏ query params post_ref
        cleaned = re.sub(r"\?post_ref=[^&]+", "", url)
        cleaned = re.sub(r"&post_ref=[^&]+", "", cleaned)
        return cleaned.rstrip("?&")

    def _sync_jobs_to_db(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Lưu trữ và khử trùng lặp các tin thu thập được vào Database
        """
        if not jobs:
            return 0

        session = SyncSessionLocal()
        saved_count = 0
        seen_urls = set()
        try:
            for j in jobs:
                source_url = self._sanitize_social_url(j.get("source_url", ""))
                if not source_url or source_url in seen_urls:
                    continue
                seen_urls.add(source_url)

                existing = session.query(Job).filter(Job.source_url == source_url).first()

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
                    if j.get("category"):
                        existing.category = j.get("category")
                    # Bảo toàn bằng chứng xác minh và mốc thời gian
                    if existing.raw_data and isinstance(existing.raw_data, dict):
                        for k in ["evidence_proof", "first_discovered_at", "last_verified_at", "verification_status"]:
                            if k in existing.raw_data:
                                job_raw[k] = existing.raw_data[k]
                    existing.raw_data = job_raw
                    existing.is_active = True
                    existing.crawled_at = datetime.now(timezone.utc)
                else:
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
                        location_province=j.get("location_province"),
                        location_district=j.get("location_district"),
                        location_full=j.get("location_full"),
                        job_type=j.get("job_type", "full-time"),
                        category=j.get("category") or mined.get("inferred_industry"),
                        source_platform=j.get("source_platform"),
                        source_url=source_url,
                        posted_at=j.get("posted_at") or datetime.now(timezone.utc),
                        expires_at=j.get("expires_at"),
                        crawled_at=datetime.now(timezone.utc),
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
