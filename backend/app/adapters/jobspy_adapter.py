"""
Multi-Source JobSpy Adapter for C_Data Platform (Inspired by DrJonoG/job_search).
Thu thập tin tuyển dụng đa nguồn từ Indeed, LinkedIn, Glassdoor, Google Jobs
thông qua thư viện python-jobspy, tích hợp Firecrawl HTML Purifier & MD5 Fingerprinting.
"""

from datetime import datetime, timezone
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional
import urllib.parse

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from app.services.html_purifier import (
    compute_job_fingerprint,
    extract_contacts_and_salary_from_text,
    purify_html_to_markdown,
)

logger = logging.getLogger("c_data.adapters.jobspy")

# Nhận diện địa danh chuẩn xác
LOCATION_RULES = [
    (r"hạ long|ha long|bãi cháy|hòn gai|quảng ninh|quang ninh", "Quảng Ninh", "Hạ Long"),
    (r"cẩm phả|cam pha", "Quảng Ninh", "Cẩm Phả"),
    (r"uông bí|uong bi", "Quảng Ninh", "Uông Bí"),
    (r"móng cái|mong cai", "Quảng Ninh", "Móng Cái"),
    (r"hà nội|ha noi|cau giay|ba dinh|hoan kiem|dong da|hai ba trung", "Hà Nội", None),
    (r"hồ chí minh|ho chi minh|tphcm|saigon|sài gòn|quận 1|quận 7|thủ đức", "Hồ Chí Minh", None),
    (r"đà nẵng|da nang", "Đà Nẵng", None),
    (r"hải phòng|hai phong", "Hải Phòng", None),
]


class JobSpyMultiSourceAdapter(BaseJobAdapter):
    """
    Adapter thu thập việc làm IT tự động từ Indeed và LinkedIn.
    Áp dụng kỹ thuật:
    - TLS Fingerprinting qua curl_cffi (vượt Cloudflare chống bot).
    - Firecrawl-style HTML markdown purification.
    - Scrapy / Crawlee MD5 deduplication cache.
    - Zero-fraud location principle (địa chỉ chuẩn 100% theo dữ liệu nguồn).
    """

    adapter_id = "jobspy_multi_source"
    source_name = "JobSpy Multi-Source Aggregator (Indeed & LinkedIn)"
    source_domain = "indeed.com / linkedin.com"
    default_delay_seconds = 1.5

    def __init__(self, sites: Optional[List[str]] = None, country_indeed: str = "vietnam"):
        self.sites = sites or ["indeed", "linkedin"]
        self.country_indeed = country_indeed

    def _resolve_location(self, raw_loc: str, is_remote: bool = False) -> Dict[str, Optional[str]]:
        """Phân tích trung thực địa bàn làm việc, tuyệt đối không gán nhầm sang Quảng Ninh."""
        text = (raw_loc or "").strip().lower()

        if is_remote or "remote" in text or "từ xa" in text:
            return {
                "province": "Toàn quốc",
                "district": "Làm việc từ xa (Remote)",
                "workplace_type": "remote",
            }

        for pattern, prov, dist in LOCATION_RULES:
            if re.search(pattern, text):
                return {
                    "province": prov,
                    "district": dist or "",
                    "workplace_type": "onsite",
                }

        return {
            "province": "Toàn quốc",
            "district": raw_loc.strip() if raw_loc else "",
            "workplace_type": "onsite",
        }

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
        Thực thi cào dữ liệu qua python-jobspy với các tham số tối ưu.
        """
        start_time = time.time()
        now = datetime.now(timezone.utc)
        search_term = keyword or "IT Software Engineer Developer"
        loc_search = province or "Vietnam"
        items: List[RawJobRecord] = []
        errors: List[AdapterError] = []

        try:
            from jobspy import scrape_jobs

            logger.info(
                f"[JobSpy] Bắt đầu cào {self.sites} với từ khóa '{search_term}', địa điểm: '{loc_search}', limit: {limit}"
            )

            df = scrape_jobs(
                site_name=self.sites,
                search_term=search_term,
                location=loc_search,
                results_wanted=limit,
                country_indeed=self.country_indeed,
            )

            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    try:
                        title = str(row.get("title") or "").strip()
                        company = str(row.get("company") or "").strip()
                        job_url = str(row.get("job_url_direct") or row.get("job_url") or "").strip()

                        if not title or not company or not job_url:
                            continue

                        raw_desc = str(row.get("description") or "")
                        clean_desc = purify_html_to_markdown(raw_desc)
                        if not clean_desc or len(clean_desc) < 30:
                            clean_desc = f"Vị trí {title} tại {company}. Xem chi tiết JD và ứng tuyển tại liên kết nguồn gốc."

                        raw_location_str = str(row.get("location") or "")
                        is_remote_flag = bool(row.get("is_remote", False))
                        loc_resolved = self._resolve_location(raw_location_str, is_remote_flag)

                        min_amt = row.get("min_amount")
                        max_amt = row.get("max_amount")
                        currency = str(row.get("currency") or "VND").upper()
                        salary_text = "Thỏa thuận"

                        salary_min = None
                        salary_max = None
                        if min_amt is not None and not (isinstance(min_amt, float) and min_amt != min_amt):
                            salary_min = int(min_amt)
                        if max_amt is not None and not (isinstance(max_amt, float) and max_amt != max_amt):
                            salary_max = int(max_amt)

                        if salary_min and salary_max:
                            salary_text = f"{salary_min:,} - {salary_max:,} {currency}"
                        elif salary_min:
                            salary_text = f"Từ {salary_min:,} {currency}"
                        elif salary_max:
                            salary_text = f"Lên đến {salary_max:,} {currency}"

                        skills_raw = row.get("skills")
                        required_skills: List[str] = []
                        if isinstance(skills_raw, list):
                            required_skills = [str(s).strip() for s in skills_raw if s]
                        elif isinstance(skills_raw, str) and skills_raw.strip():
                            required_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

                        content_hash = compute_job_fingerprint(job_url, title, company)
                        source_site = str(row.get("site") or "indeed").lower()

                        posted_val = row.get("date_posted")
                        posted_at = now
                        if isinstance(posted_val, datetime):
                            posted_at = posted_val if posted_val.tzinfo else posted_val.replace(tzinfo=timezone.utc)

                        record = RawJobRecord(
                            source_job_id=f"jobspy_{source_site}_{content_hash[:12]}",
                            title=title,
                            company_name=company,
                            source_url=job_url,
                            apply_url=job_url,
                            salary_text=salary_text,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            salary_currency=currency,
                            location_raw=raw_location_str,
                            location_province=loc_resolved["province"],
                            location_district=loc_resolved["district"],
                            workplace_type=loc_resolved["workplace_type"],
                            employment_type=str(row.get("job_type") or "full-time").lower(),
                            experience_level=str(row.get("job_level") or "Middle"),
                            required_skills=required_skills,
                            description=clean_desc,
                            requirements=f"Chi tiết kỹ năng chuyên môn: {', '.join(required_skills)}" if required_skills else clean_desc[:250],
                            benefits="Chế độ đãi ngộ theo tiêu chuẩn doanh nghiệp, trao đổi trực tiếp khi phỏng vấn.",
                            category="Công nghệ thông tin / Phần mềm",
                            posted_at=posted_at,
                            content_hash=content_hash,
                            raw_data={
                                "aggregator": "python-jobspy",
                                "source_site": source_site,
                                "emails": row.get("emails"),
                                "company_industry": row.get("company_industry"),
                            },
                            status="active_likely",
                            status_reason="Thu thập trực tiếp từ Indeed / LinkedIn qua JobSpy Engine",
                        )
                        items.append(record)
                    except Exception as row_err:
                        logger.debug(f"[JobSpy] Bỏ qua bản ghi lỗi: {row_err}")

        except Exception as e:
            logger.error(f"[JobSpy] Lỗi thực thi JobSpy scraper: {e}", exc_info=True)
            errors.append(
                AdapterError(
                    error_type=AdapterErrorType.UNKNOWN,
                    message=f"Lỗi JobSpy: {str(e)}",
                )
            )

        duration_ms = (time.time() - start_time) * 1000.0
        return AdapterCrawlResult(
            source_id="jobspy_multi_source",
            source_name=self.source_name,
            items=items,
            crawl_duration_ms=round(duration_ms, 2),
            crawl_timestamp=now,
            page=page,
            total_detected=len(items),
            errors=errors,
            raw_metadata={
                "sites": self.sites,
                "country_indeed": self.country_indeed,
            },
        )

    def fetch_job_detail(
        self,
        source_job_id: str,
        detail_url: str,
    ) -> Optional[Dict[str, Any]]:
        return {
            "source_job_id": source_job_id,
            "detail_url": detail_url,
            "adapter": self.adapter_id,
        }


jobspy_multi_source_adapter = JobSpyMultiSourceAdapter()
