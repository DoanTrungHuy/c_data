"""
ITviec Specialized Tech Job Crawler Adapter for C_Data Platform.
Harvests tech, developer, and IT support vacancies from https://itviec.com.
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
    BaseCrawlerAdapter,
    RawJobRecord,
)
from app.services.job_deduplication_engine import canonicalize_url

logger = logging.getLogger("c_data.adapters.itviec")


class ITviecAdapter(BaseCrawlerAdapter):
    """
    Adapter cào việc làm chuyên sâu CNTT từ ITviec
    """

    source_id = "itviec"
    source_name = "Cổng việc làm CNTT chuyên sâu ITviec"
    base_url = "https://itviec.com"

    def __init__(self, timeout_seconds: float = 10.0):
        super().__init__()
        self.timeout = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataBot/2.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    def fetch_jobs(
        self,
        query: str = "IT",
        province: Optional[str] = None,
        page: int = 1,
    ) -> AdapterCrawlResult:
        """
        Truy vấn danh sách việc làm IT từ ITviec theo từ khóa và địa điểm
        """
        start_time = datetime.now(timezone.utc)
        search_term = query if isinstance(query, str) else "IT"
        prov_str = province if isinstance(province, str) else ""
        if prov_str and "ha long" in prov_str.lower():
            search_term = f"{search_term} ha long"
        elif prov_str and "quang ninh" in prov_str.lower():
            search_term = f"{search_term} quang ninh"
        elif prov_str and "ha noi" in prov_str.lower():
            search_term = f"{search_term} ha noi"

        params = {"query": search_term, "page": page}
        target_url = f"{self.base_url}/it-jobs?{urllib.parse.urlencode(params)}"
        logger.info(f"🔍 [ITviec] Đang truy vấn: {target_url}")

        try:
            resp = self.session.get(target_url, timeout=self.timeout)
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            if resp.status_code != 200:
                self.record_error(AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"HTTP {resp.status_code} từ ITviec",
                    url=target_url,
                    status_code=resp.status_code,
                ))
                return AdapterCrawlResult(source_id=self.source_id, source_name=self.source_name, items=[], crawl_duration_ms=duration_ms)

            records = self.parse_cards(resp.text, default_province=prov_str or "Toàn quốc")
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
            self.record_error(AdapterError(error_type=AdapterErrorType.NETWORK_TIMEOUT, message=f"Timeout kết nối sau {self.timeout}s", url=target_url))
            return AdapterCrawlResult(source_id=self.source_id, source_name=self.source_name, items=[], crawl_duration_ms=duration_ms)
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            self.record_error(AdapterError(error_type=AdapterErrorType.UNKNOWN, message=f"Lỗi: {e}", url=target_url))
            return AdapterCrawlResult(source_id=self.source_id, source_name=self.source_name, items=[], crawl_duration_ms=duration_ms)

    def parse_cards(self, html: str, default_province: str = "Toàn quốc") -> List[RawJobRecord]:
        """Bóc tách các thẻ `.job-card` trên trang ITviec"""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(".job-card")
        records: List[RawJobRecord] = []
        now = datetime.now(timezone.utc)

        for card in cards:
            title_tag = card.select_one("h3 a, h3, .text-it-black")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # Link
            link_tag = card.select_one("h3 a, a[href*='/it-jobs/']")
            raw_url = link_tag["href"] if (link_tag and link_tag.has_attr("href")) else ""
            if raw_url and not raw_url.startswith("http"):
                raw_url = urllib.parse.urljoin(self.base_url, raw_url)
            clean_url = canonicalize_url(raw_url)

            # ID tin
            m_id = re.search(r"-(\d{3,})", clean_url)
            source_job_id = m_id.group(1) if m_id else str(abs(hash(f"{title}_{clean_url}")) % 1000000000)

            # Công ty
            comp_tag = card.select_one(".ims-2 a, a[href*='/companies/'].text-rich-grey, a.text-rich-grey")
            if comp_tag and comp_tag.get_text(strip=True):
                company_name = comp_tag.get_text(strip=True)
            else:
                img_tag = card.select_one("a.logo-employer-card img[alt]")
                if img_tag and img_tag.get("alt"):
                    company_name = img_tag["alt"].replace("Vietnam Small Logo", "").replace("Small Logo", "").strip()
                else:
                    company_name = "Doanh nghiệp CNTT (ITviec)"

            # Địa điểm
            loc_tags = card.select(".text-nowrap, .text-truncate")
            location_str = default_province
            for lt in loc_tags:
                txt = lt.get_text(strip=True)
                if any(city in txt.lower() for city in ["ha noi", "hanoi", "ha long", "quang ninh", "da nang", "ho chi minh", "hcm", "remote"]):
                    location_str = txt
                    break

            # Kỹ năng
            skill_tags = card.select(".itag, .itag-sm")
            skills = [s.get_text(strip=True) for s in skill_tags if s.get_text(strip=True)]

            # Phân loại cấp bậc & môi trường
            card_text = card.get_text().lower()
            seniority = "Junior"
            if "fresher" in card_text or "intern" in card_text or "không yc kinh nghiệm" in card_text:
                seniority = "Fresher"
            elif "senior" in card_text:
                seniority = "Senior"

            workplace = "onsite"
            if "remote" in card_text:
                workplace = "remote"
            elif "hybrid" in card_text:
                workplace = "hybrid"

            prov = default_province
            loc_low = location_str.lower()
            if "ha long" in loc_low or "quang ninh" in loc_low:
                prov = "Quảng Ninh"
            elif "ha noi" in loc_low or "hanoi" in loc_low:
                prov = "Hà Nội"

            records.append(RawJobRecord(
                source_job_id=source_job_id,
                title=title,
                company_name=company_name,
                source_url=clean_url,
                apply_url=clean_url,
                location_raw=location_str,
                location_province=prov,
                location_district="Hạ Long" if prov == "Quảng Ninh" else None,
                workplace_type=workplace,
                employment_type="full-time",
                experience_level=seniority,
                category="Công nghệ thông tin / Phần mềm",
                required_skills=skills,
                posted_at=now,
                status="active_likely",
                status_reason="Tin tuyển dụng công nghệ xác thực trên sàn ITviec",
                extraction_confidence=0.92,
                location_confidence=0.88,
                first_seen_at=now,
            ))

        return records

    def as_discovery_callable(self):
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
            res = self.fetch_jobs(query=kw or "IT", province=prov if isinstance(prov, str) else None)
            return [r.to_dict() for r in res.items[:max_items]]
        return _execute


# Singleton instance
itviec_adapter = ITviecAdapter()
