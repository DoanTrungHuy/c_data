"""
Authorized Partner API Job Adapter for C_Data Platform.
Handles protected job boards (TopCV, VietnamWorks) that require official partner API keys.
Strict compliance:
- Validates credential tokens.
- Reports AUTH_REQUIRED when missing credentials.
- NEVER fabricates mock data or bypasses anti-bot mechanisms.
"""

from datetime import datetime, timezone
import logging
import os
import time
from typing import Any, Dict, List, Optional
import requests

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)

logger = logging.getLogger("c_data.adapters.partner_api")


class PartnerApiAdapter(BaseJobAdapter):
    """
    Adapter cho các nguồn yêu cầu khóa xác thực API đối tác (TopCV / VietnamWorks).
    """

    adapter_id = "topcv"
    source_name = "Cổng Việc Làm TopCV (Partner API)"
    source_domain = "topcv.vn"
    env_key_name = "TOPCV_API_KEY"
    api_endpoint = "https://api.topcv.vn/v1/partner/jobs"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def get_api_key(self) -> Optional[str]:
        return os.getenv(self.env_key_name)

    def parse_api_response(
        self,
        payload: Dict[str, Any],
        target_url: str = "https://api.topcv.vn/v1/partner/jobs",
        since_timestamp: Optional[datetime] = None,
        limit: int = 20,
    ) -> AdapterCrawlResult:
        """
        Bóc tách JSON response từ API đối tác.
        Có thể chạy offline với fixture JSON.
        """
        result = AdapterCrawlResult(
            source_id=self.adapter_id,
            source_name=self.source_name,
            raw_metadata={"api_endpoint": target_url},
        )

        items = payload.get("data", []) or payload.get("items", [])
        result.total_detected = len(items)

        for raw in items:
            if len(result.items) >= limit:
                break

            title = raw.get("title", "").strip()
            if not title:
                continue

            posted_at = None
            if raw.get("posted_at"):
                try:
                    posted_at = datetime.fromisoformat(raw["posted_at"])
                except Exception:
                    pass

            if since_timestamp and posted_at and posted_at < since_timestamp:
                continue

            item = RawJobRecord(
                source_job_id=str(raw.get("id", raw.get("job_id", ""))),
                title=title,
                company_name=raw.get("company_name", "Doanh nghiệp đối tác"),
                source_url=raw.get("url", f"https://topcv.vn/viec-lam/{raw.get('id')}"),
                apply_url=raw.get("apply_url") or raw.get("url"),
                salary_text=raw.get("salary_text", "Thỏa thuận"),
                salary_min=raw.get("salary_min"),
                salary_max=raw.get("salary_max"),
                location_raw=raw.get("location", "Toàn quốc"),
                location_province=raw.get("province"),
                location_district=raw.get("district"),
                workplace_type=raw.get("workplace_type", "onsite"),
                employment_type=raw.get("employment_type", "full-time"),
                description=raw.get("description"),
                requirements=raw.get("requirements"),
                benefits=raw.get("benefits"),
                posted_at=posted_at,
                status="active_confirmed",
                status_evidence="Xác thực từ Partner API chính thức",
                extraction_confidence=1.0,
                location_confidence=0.95,
                raw_data_reference={"api_id": raw.get("id")},
                is_test_fixture="[FIXTURE_TEST_ONLY]" in title,
            )
            result.items.append(item)

        # Hỗ trợ cursor hoặc next_page
        if "next_cursor" in payload:
            result.next_cursor = payload["next_cursor"]
            result.has_more = bool(payload["next_cursor"])
        elif "next_page" in payload:
            result.next_page = payload["next_page"]
            result.has_more = bool(payload["next_page"])

        return result

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
        Kiểm tra API Key trước khi thực hiện request:
        Nếu chưa có cấu hình API Key, báo lỗi AUTH_REQUIRED minh bạch và không cào lậu.
        """
        t0 = time.time()
        api_key = self.get_api_key()

        if not api_key:
            err = AdapterError(
                error_type=AdapterErrorType.AUTH_REQUIRED,
                message=f"Chưa cấu hình biến môi trường '{self.env_key_name}'. Yêu cầu thỏa thuận đối tác để truy cập API chính thức.",
                url=self.api_endpoint,
            )
            return AdapterCrawlResult(
                source_id=self.adapter_id,
                source_name=self.source_name,
                crawl_duration_ms=round((time.time() - t0) * 1000, 1),
                errors=[err],
            )

        # Khi đã có API Key, thực hiện request hợp lệ
        try:
            headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
            params = {"q": keyword or "", "province": province or "", "page": page, "limit": limit}
            resp = self.session.get(self.api_endpoint, headers=headers, params=params, timeout=8.0)
            latency = round((time.time() - t0) * 1000, 1)

            if resp.status_code == 200:
                result = self.parse_api_response(resp.json(), target_url=self.api_endpoint, since_timestamp=since_timestamp, limit=limit)
                result.crawl_duration_ms = latency
                return result
            elif resp.status_code in [401, 403]:
                err = AdapterError(error_type=AdapterErrorType.AUTH_REQUIRED, message="API Key không hợp lệ hoặc đã hết hạn", url=self.api_endpoint, status_code=resp.status_code)
                return AdapterCrawlResult(source_id=self.adapter_id, source_name=self.source_name, crawl_duration_ms=latency, errors=[err])
            else:
                err = AdapterError(error_type=AdapterErrorType.HTTP_ERROR, message=f"API trả về mã lỗi HTTP {resp.status_code}", url=self.api_endpoint, status_code=resp.status_code)
                return AdapterCrawlResult(source_id=self.adapter_id, source_name=self.source_name, crawl_duration_ms=latency, errors=[err])

        except requests.exceptions.RequestException as e:
            latency = round((time.time() - t0) * 1000, 1)
            err = AdapterError(error_type=AdapterErrorType.CONNECTION_FAILED, message=f"Lỗi kết nối tới Partner API: {e}", url=self.api_endpoint)
            return AdapterCrawlResult(source_id=self.adapter_id, source_name=self.source_name, crawl_duration_ms=latency, errors=[err])

    def fetch_job_detail(self, source_job_id: str, detail_url: str) -> Optional[Dict[str, Any]]:
        return None


partner_api_adapter = PartnerApiAdapter()
