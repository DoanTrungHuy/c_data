"""
Ybox Fresher & Junior Job Crawler Adapter for C_Data Platform.
Thu thập tin thực tập, Fresher, Junior CNTT từ cổng việc làm giới trẻ Ybox.vn
sử dụng GraphQL API chính thức (https://api.ybox.vn/graphql) và cơ chế xử lý lỗi kiên cố.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
import urllib.parse
import requests

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from app.services.job_deduplication_engine import canonicalize_url

logger = logging.getLogger("c_data.adapters.ybox")


class YboxAdapter(BaseJobAdapter):
    """
    Adapter chuyên biệt cho nguồn Ybox.vn dành cho Fresher, Intern và Junior.
    Giao tiếp qua GraphQL endpoint https://api.ybox.vn/graphql.
    """

    adapter_id = "ybox_fresher"
    source_id = "ybox_fresher"
    source_name = "Kênh việc làm sinh viên & Fresher Ybox"
    source_domain = "ybox.vn"
    graphql_url = "https://api.ybox.vn/graphql"
    base_web_url = "https://ybox.vn"
    default_delay_seconds = 2.0

    def __init__(self, timeout_seconds: float = 8.0):
        super().__init__()
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataBot/2.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://ybox.vn",
            "Referer": "https://ybox.vn/tuyen-dung",
        })

    def discover_jobs(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        page: int = 1,
        cursor: Optional[str] = None,
        limit: int = 20,
        since_timestamp: Optional[datetime] = None,
    ) -> AdapterCrawlResult:
        """
        Truy vấn tin tuyển dụng từ Ybox GraphQL API
        """
        start_time = datetime.now(timezone.utc)
        search_kw = keyword or "IT"
        query_str = """
        query GetYboxPosts($limit: Int, $q: String, $page: Int) {
          ForYou(limit: $limit, q: $q, page: $page) {
            count
            edges {
              _id
              title
              slug
              nameCompany
              emailCompany
              publishedAt
              deadline
              active
              summary
            }
          }
        }
        """
        variables = {
            "limit": limit,
            "q": search_kw,
            "page": page,
        }

        try:
            resp = self.session.post(
                self.graphql_url,
                json={"query": query_str, "variables": variables},
                timeout=self.timeout,
            )
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if resp.status_code != 200:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"HTTP {resp.status_code} từ Ybox GraphQL",
                    url=self.graphql_url,
                    status_code=resp.status_code,
                ))
                return AdapterCrawlResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    items=[],
                    crawl_duration_ms=duration_ms,
                )

            data = resp.json()
            errors = data.get("errors", [])
            if errors:
                err_msg = errors[0].get("message", "Lỗi GraphQL Ybox")
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.PARSE_ERROR,
                    message=f"Ybox GraphQL Error: {err_msg}",
                    url=self.graphql_url,
                ))

            edges = data.get("data", {}).get("ForYou", {}).get("edges", [])
            records: List[RawJobRecord] = []
            now = datetime.now(timezone.utc)

            for edge in edges:
                job_id = edge.get("_id") or str(abs(hash(edge.get("title", ""))) % 1000000000)
                title = edge.get("title") or "Cơ hội việc làm Fresher"
                company = edge.get("nameCompany") or "Doanh nghiệp tuyển dụng Ybox"
                slug = edge.get("slug") or "tuyen-dung"
                job_url = f"{self.base_web_url}/tuyen-dung/{slug}-{job_id}"
                clean_url = canonicalize_url(job_url)

                # Deadline
                deadline_dt = None
                if edge.get("deadline"):
                    try:
                        deadline_dt = datetime.fromisoformat(str(edge["deadline"]).replace("Z", "+00:00"))
                    except Exception:
                        deadline_dt = None

                # Posted date
                posted_dt = now
                if edge.get("publishedAt"):
                    try:
                        posted_dt = datetime.fromisoformat(str(edge["publishedAt"]).replace("Z", "+00:00"))
                    except Exception:
                        posted_dt = now

                # Location inference
                loc_raw = province or "Toàn quốc"
                prov = "Toàn quốc"
                if province and ("ha noi" in province.lower() or "hà nội" in province.lower()):
                    prov = "Hà Nội"
                elif province and ("quang ninh" in province.lower() or "hạ long" in province.lower()):
                    prov = "Quảng Ninh"

                records.append(RawJobRecord(
                    source_job_id=str(job_id),
                    title=title,
                    company_name=company,
                    source_url=clean_url,
                    apply_url=clean_url,
                    location_raw=loc_raw,
                    location_province=prov,
                    location_district="Hạ Long" if prov == "Quảng Ninh" else None,
                    workplace_type="onsite",
                    employment_type="full-time",
                    experience_level="Fresher",
                    category="Công nghệ thông tin / Fresher",
                    description=edge.get("summary") or "",
                    posted_at=posted_dt,
                    deadline=deadline_dt,
                    status="active_likely",
                    status_reason="Tin tuyển dụng sinh viên & khởi nghiệp trên cổng Ybox",
                    extraction_confidence=0.88,
                    location_confidence=0.80,
                    first_seen_at=now,
                ))

            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=records,
                crawl_duration_ms=duration_ms,
                total_detected=len(records),
                has_more=False,
            )

        except requests.Timeout:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.NETWORK_TIMEOUT,
                message=f"Timeout kết nối Ybox sau {self.timeout}s",
                url=self.graphql_url,
            ))
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=[],
                crawl_duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.UNKNOWN,
                message=f"Lỗi: {e}",
                url=self.graphql_url,
            ))
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=[],
                crawl_duration_ms=duration_ms,
            )

    def fetch_job_detail(self, source_job_id: str, detail_url: str) -> Optional[Dict[str, Any]]:
        """Lấy chi tiết tin từ GraphQL Post query"""
        query_str = """
        query GetPostDetail($id: String!) {
          Post(id: $id) {
            _id
            title
            content
            nameCompany
            emailCompany
            website
            deadline
          }
        }
        """
        try:
            resp = self.session.post(
                self.graphql_url,
                json={"query": query_str, "variables": {"id": source_job_id}},
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                p = resp.json().get("data", {}).get("Post")
                if p:
                    return {
                        "id": p.get("_id"),
                        "title": p.get("title"),
                        "description": p.get("content"),
                        "company_name": p.get("nameCompany"),
                        "email": p.get("emailCompany"),
                        "website": p.get("website"),
                        "deadline": p.get("deadline"),
                    }
        except Exception as e:
            logger.warning(f"Lỗi fetch_job_detail Ybox ({source_job_id}): {e}")
        return None


# Singleton instance
ybox_adapter = YboxAdapter()
