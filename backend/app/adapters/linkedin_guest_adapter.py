"""
LinkedIn Guest Public Job Search Adapter for C_Data Platform.
Utilizes the official public guest endpoint (no login / no credential needed)
to harvest authentic tech and IT job postings in Vietnam, Hanoi, and Quang Ninh.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
import urllib.parse
from bs4 import BeautifulSoup
import requests
import unidecode

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseCrawlerAdapter,
    RawJobRecord,
)
from app.services.job_deduplication_engine import canonicalize_url

logger = logging.getLogger("c_data.adapters.linkedin_guest")


class LinkedInGuestAdapter(BaseCrawlerAdapter):
    """
    Adapter cào việc làm công khai qua LinkedIn Guest Search API
    """

    source_id = "linkedin_guest_api"
    source_name = "LinkedIn Public Guest Search"
    base_endpoint = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    def __init__(self, timeout_seconds: float = 10.0):
        super().__init__()
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def fetch_jobs(
        self,
        keyword: str = "IT",
        location: str = "Vietnam",
        start: int = 0,
    ) -> AdapterCrawlResult:
        """
        Truy vấn danh sách việc làm khách công khai từ LinkedIn
        """
        start_time = datetime.now(timezone.utc)
        if not isinstance(keyword, str):
            kw_str = getattr(keyword, "raw_query", "IT") if keyword else "IT"
        else:
            kw_str = keyword or "IT"
        loc_str = location if isinstance(location, str) and location else "Vietnam"

        params = {
            "keywords": kw_str,
            "location": loc_str,
            "start": start if isinstance(start, int) else 0,
        }
        url = f"{self.base_endpoint}?{urllib.parse.urlencode(params)}"
        logger.info(f"🔍 [LinkedIn Guest] Đang truy vấn: {url}")

        try:
            resp = self.session.get(url, timeout=self.timeout)
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if resp.status_code == 429:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.RATE_LIMITED,
                    message="LinkedIn Guest API rate limit (429)",
                    url=url,
                    status_code=429,
                ))
                return AdapterCrawlResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    items=[],
                    crawl_duration_ms=duration_ms,
                    total_detected=0,
                )

            if resp.status_code != 200:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"HTTP error {resp.status_code}",
                    url=url,
                    status_code=resp.status_code,
                ))
                return AdapterCrawlResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    items=[],
                    crawl_duration_ms=duration_ms,
                    total_detected=0,
                )

            records = self.parse_html_snippet(resp.text, keyword=keyword, default_location=location)
            return AdapterCrawlResult(
                source_id=self.source_id,
                source_name=self.source_name,
                items=records,
                crawl_duration_ms=duration_ms,
                total_detected=len(records),
                has_more=(len(records) >= 10),
            )

        except requests.Timeout:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.NETWORK_TIMEOUT,
                message=f"Timeout kết nối sau {self.timeout}s",
                url=url,
            ))
            return AdapterCrawlResult(source_id=self.source_id, source_name=self.source_name, items=[], crawl_duration_ms=duration_ms)
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(
                error_type=AdapterErrorType.UNKNOWN,
                message=f"Lỗi không xác định: {e}",
                url=url,
            ))
            return AdapterCrawlResult(source_id=self.source_id, source_name=self.source_name, items=[], crawl_duration_ms=duration_ms)

    def parse_html_snippet(self, html: str, keyword: str = "IT", default_location: str = "Vietnam") -> List[RawJobRecord]:
        """
        Bóc tách các thẻ danh sách `<li>` trong đoạn mã HTML trả về từ LinkedIn Guest API
        """
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("li")
        records: List[RawJobRecord] = []
        now = datetime.now(timezone.utc)

        for li in items:
            title_tag = li.select_one(".base-search-card__title")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            comp_tag = li.select_one(".base-search-card__subtitle a, .base-search-card__subtitle")
            company_name = comp_tag.get_text(strip=True) if comp_tag else "Doanh nghiệp (LinkedIn)"

            loc_tag = li.select_one(".job-search-card__location")
            location_str = loc_tag.get_text(strip=True) if loc_tag else default_location

            link_tag = li.select_one("a.base-card__full-link, a")
            raw_url = link_tag["href"] if (link_tag and link_tag.has_attr("href")) else ""
            clean_url = canonicalize_url(raw_url)

            # Trích xuất mã ID bài đăng LinkedIn
            entity_urn = li.select_one("[data-entity-urn]")
            source_job_id = ""
            if entity_urn and entity_urn.has_attr("data-entity-urn"):
                urn_str = entity_urn["data-entity-urn"]
                m = re.search(r"jobPosting:(\d+)", urn_str)
                if m:
                    source_job_id = m.group(1)

            if not source_job_id and clean_url:
                m_url = re.search(r"-(\d{8,})", clean_url)
                if m_url:
                    source_job_id = m_url.group(1)

            if not source_job_id:
                source_job_id = str(abs(hash(f"{title}_{company_name}_{clean_url}")) % 1000000000)

            # Ngày đăng (từ thẻ time)
            time_tag = li.select_one("time[datetime]")
            posted_date = None
            if time_tag and time_tag.has_attr("datetime"):
                dt_str = time_tag["datetime"]
                try:
                    posted_date = datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                except Exception:
                    posted_date = now

            # Xác định địa bàn tỉnh thành (hỗ trợ cả có dấu và không dấu)
            prov = "Toàn quốc"
            clean_loc = unidecode.unidecode(location_str).lower()
            if "ha long" in clean_loc or "quang ninh" in clean_loc or "bai chay" in clean_loc or "hon gai" in clean_loc:
                prov = "Quảng Ninh"
            elif "ha noi" in clean_loc or "hanoi" in clean_loc:
                prov = "Hà Nội"
            elif "ho chi minh" in clean_loc or "hcm" in clean_loc or "saigon" in clean_loc:
                prov = "TP. Hồ Chí Minh"
            elif "da nang" in clean_loc:
                prov = "Đà Nẵng"

            # Phân loại cấp bậc
            level = "Junior"
            title_lower = title.lower()
            if "intern" in title_lower or "thực tập" in title_lower:
                level = "Intern"
            elif "fresher" in title_lower or "entry" in title_lower or "graduate" in title_lower:
                level = "Fresher"
            elif "senior" in title_lower or "lead" in title_lower or "principal" in title_lower:
                level = "Senior"
            elif "manager" in title_lower or "head" in title_lower or "director" in title_lower:
                level = "Manager"

            record = RawJobRecord(
                source_job_id=source_job_id,
                title=title,
                company_name=company_name,
                source_url=clean_url,
                apply_url=clean_url,
                location_raw=location_str,
                location_province=prov,
                location_district="Hạ Long" if prov == "Quảng Ninh" else None,
                workplace_type="remote" if "remote" in title_lower or "remote" in clean_loc else "onsite",
                employment_type="full-time",
                experience_level=level,
                category=keyword if (isinstance(keyword, str) and keyword != "IT") else "Công nghệ thông tin",
                posted_at=posted_date,
                status="active_likely",
                status_reason="Tìm thấy bài đăng công khai trên LinkedIn Guest Portal",
                extraction_confidence=0.90,
                location_confidence=0.88,
                first_seen_at=now,
            )
            records.append(record)

        return records

    def as_discovery_callable(self):
        """Trả về hàm callable tương thích với Discovery Queue và SourceRegistry"""
        def _execute(intent: Any = None, max_items: int = 10, **kwargs) -> List[Dict[str, Any]]:
            if isinstance(intent, str):
                kw = intent
                prov = kwargs.get("province")
            elif intent is not None:
                kw = getattr(intent, "expanded_queries", [None])[0] if getattr(intent, "expanded_queries", None) else getattr(intent, "raw_query", None)
                prov = getattr(intent, "target_province", None)
            else:
                kw = kwargs.get("keyword", "IT")
                prov = kwargs.get("province")
            loc = prov if isinstance(prov, str) and prov else "Vietnam"
            res = self.fetch_jobs(keyword=kw or "IT", location=loc)
            return [r.to_dict() for r in res.items[:max_items]]
        return _execute


# Singleton instance
linkedin_guest_adapter = LinkedInGuestAdapter()
