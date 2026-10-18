"""
JobsGO Tech & Local Job Crawler Adapter for C_Data Platform.
Thu thập tin tuyển dụng việc làm CNTT tại Quảng Ninh & Hà Nội từ https://jobsgo.vn.
Tích hợp khả năng tự phát hiện và báo cáo chặn Cloudflare WAF (HTTP 403) chuẩn xác.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
import urllib.parse
from bs4 import BeautifulSoup
import requests

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from app.services.job_deduplication_engine import canonicalize_url

logger = logging.getLogger("c_data.adapters.jobsgo")


class JobsGOAdapter(BaseJobAdapter):
    """
    Adapter thu thập tin tuyển dụng từ JobsGO
    """

    adapter_id = "jobsgo"
    source_id = "jobsgo"
    source_name = "Cổng việc làm JobsGO"
    source_domain = "jobsgo.vn"
    base_url = "https://jobsgo.vn"
    default_delay_seconds = 2.0

    def __init__(self, timeout_seconds: float = 8.0):
        super().__init__()
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataBot/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://jobsgo.vn/",
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
        Truy vấn việc làm trên JobsGO theo từ khóa và địa bàn
        """
        start_time = datetime.now(timezone.utc)
        search_kw = keyword or "IT"
        
        # Chọn URL phù hợp theo địa bàn
        if province and ("quang ninh" in province.lower() or "hạ long" in province.lower()):
            target_url = f"{self.base_url}/viec-lam-cong-nghe-thong-tin-tai-quang-ninh.html"
        elif province and ("ha noi" in province.lower() or "hà nội" in province.lower()):
            target_url = f"{self.base_url}/viec-lam-cong-nghe-thong-tin-tai-ha-noi.html"
        else:
            params = {"keyword": search_kw, "page": page}
            target_url = f"{self.base_url}/viec-lam.html?{urllib.parse.urlencode(params)}"

        logger.info(f"🔍 [JobsGO] Đang truy vấn: {target_url}")

        try:
            resp = self.session.get(target_url, timeout=self.timeout)
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if resp.status_code == 403:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.BLOCKED,
                    message="Bị chặn bởi tường lửa Cloudflare/WAF của JobsGO (HTTP 403)",
                    url=target_url,
                    status_code=403,
                ))
                return AdapterCrawlResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    items=[],
                    crawl_duration_ms=duration_ms,
                    errors=self.errors,
                )

            if resp.status_code != 200:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"HTTP {resp.status_code} từ JobsGO",
                    url=target_url,
                    status_code=resp.status_code,
                ))
                return AdapterCrawlResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    items=[],
                    crawl_duration_ms=duration_ms,
                    errors=self.errors,
                )

            records = self.parse_html(resp.text, default_province=province or "Toàn quốc")
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=records,
                crawl_duration_ms=duration_ms,
                total_detected=len(records),
                has_more=(len(records) >= 15),
            )

        except requests.Timeout:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.NETWORK_TIMEOUT,
                message=f"Timeout kết nối JobsGO sau {self.timeout}s",
                url=target_url,
            ))
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=[],
                crawl_duration_ms=duration_ms,
                errors=self.errors,
            )
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.UNKNOWN,
                message=f"Lỗi: {e}",
                url=target_url,
            ))
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=[],
                crawl_duration_ms=duration_ms,
                errors=self.errors,
            )

    def parse_html(self, html: str, default_province: str = "Toàn quốc") -> List[RawJobRecord]:
        """Bóc tách danh sách việc làm khi nhận được HTML hợp lệ"""
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".job-item, .brows-job-list, .item-click")
        records: List[RawJobRecord] = []
        now = datetime.now(timezone.utc)

        for el in items:
            title_tag = el.select_one("h3 a, .job-title a, a[href*='/viec-lam/']")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            raw_url = title_tag.get("href", "")
            if raw_url and not raw_url.startswith("http"):
                raw_url = urllib.parse.urljoin(self.base_url, raw_url)
            clean_url = canonicalize_url(raw_url)

            # Công ty
            comp_tag = el.select_one(".company-name, .text-silver a, a[href*='/nha-tuyen-dung/']")
            company_name = comp_tag.get_text(strip=True) if comp_tag else "Doanh nghiệp (JobsGO)"

            # ID tin
            m_id = re.search(r"-(\d{6,})", clean_url)
            source_job_id = m_id.group(1) if m_id else str(abs(hash(f"{title}_{clean_url}")) % 1000000000)

            # Địa điểm
            loc_tag = el.select_one(".job-location, .location")
            loc_str = loc_tag.get_text(strip=True) if loc_tag else default_province

            prov = default_province
            if any(k in loc_str.lower() for k in ["hạ long", "ha long", "quảng ninh", "quang ninh"]):
                prov = "Quảng Ninh"
            elif any(k in loc_str.lower() for k in ["hà nội", "ha noi"]):
                prov = "Hà Nội"

            records.append(RawJobRecord(
                source_job_id=source_job_id,
                title=title,
                company_name=company_name,
                source_url=clean_url,
                apply_url=clean_url,
                location_raw=loc_str,
                location_province=prov,
                location_district="Hạ Long" if prov == "Quảng Ninh" else None,
                workplace_type="onsite",
                employment_type="full-time",
                experience_level="Junior",
                category="Công nghệ thông tin",
                posted_at=now,
                status="active_likely",
                status_reason="Tin tuyển dụng phát hiện trên JobsGO",
                extraction_confidence=0.85,
                location_confidence=0.82,
                first_seen_at=now,
            ))

        return records

    def fetch_job_detail(self, source_job_id: str, detail_url: str) -> Optional[Dict[str, Any]]:
        return None


# Singleton instance
jobsgo_adapter = JobsGOAdapter()
