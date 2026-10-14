"""
TimViecNhanh crawler for C_Data job aggregation platform.
Crawls job postings from https://www.timviecnhanh.com (vieclam24h).
Specializes in blue-collar, manufacturing, trade, and provincial jobs (e.g. Quảng Ninh, Bình Dương, Hải Phòng).
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from crawlers.utils import (
    clean_html,
    detect_experience_level,
    detect_job_category,
    extract_salary_range,
    normalize_job_type,
    normalize_location,
    normalize_province,
)

logger = logging.getLogger("crawler.timviecnhanh")


class TimViecNhanhCrawler(BaseCrawler):
    """
    Crawler for TimViecNhanh (https://www.timviecnhanh.com)
    """

    platform_name = "timviecnhanh"
    base_url = "https://www.timviecnhanh.com"
    fallback_base_url = "https://vieclam24h.vn"
    delay_seconds = 2.5

    def _build_search_url(self, page: int = 1, province: Optional[str] = None) -> str:
        """
        Build URL for TimViecNhanh job search.
        Format: https://www.timviecnhanh.com/viec-lam?page={page}
        """
        if province:
            norm_prov = normalize_province(province) or province
            return f"{self.base_url}/viec-lam?tinh-thanh={norm_prov}&page={page}"
        return f"{self.base_url}/viec-lam?page={page}"

    def crawl_job_detail(self, job_url: str) -> Dict[str, Any]:
        """
        Scrape detailed job description, requirements, benefits from detail page.
        """
        detail = {
            "description": "",
            "requirements": "",
            "benefits": "",
            "expires_at": None,
        }

        resp = self._make_request(job_url)
        if not resp or resp.status_code != 200:
            self.logger.warning(f"Could not load TimViecNhanh detail page: {job_url}")
            return detail

        soup = BeautifulSoup(resp.content, "html.parser")

        # Sections in TimViecNhanh
        desc_parts = []
        req_parts = []
        benefit_parts = []

        # Find section containers
        sections = soup.select(
            ".job-description, .job-requirements, .detail-box, .box-item, div[class*='job-content'], div[class*='JobDetail']"
        )

        for sec in sections:
            title_elem = sec.find(["h2", "h3", "h4", "h5", "strong", "div", "p"])
            title_text = title_elem.get_text(strip=True).lower() if title_elem else ""
            content_text = sec.get_text(separator="\n", strip=True)

            if any(k in title_text for k in ["mô tả công việc", "mô tả", "công việc"]):
                desc_parts.append(content_text)
            elif any(k in title_text for k in ["yêu cầu ứng viên", "yêu cầu công việc", "yêu cầu"]):
                req_parts.append(content_text)
            elif any(k in title_text for k in ["quyền lợi", "chế độ", "phúc lợi"]):
                benefit_parts.append(content_text)

        # Fallback if no explicit boxes found
        if not desc_parts and not req_parts:
            main_body = soup.select_one(".content-body, .job-detail, main, #main-content")
            if main_body:
                text = clean_html(str(main_body))
                splits = re.split(
                    r"(?:Yêu cầu công việc|Yêu cầu ứng viên|Quyền lợi được hưởng|Chế độ đãi ngộ):?",
                    text,
                    flags=re.IGNORECASE,
                )
                if len(splits) >= 2:
                    desc_parts.append(splits[0].strip())
                    req_parts.append(splits[1].strip())
                    if len(splits) >= 3:
                        benefit_parts.append(splits[2].strip())
                else:
                    desc_parts.append(text)

        detail["description"] = clean_html("\n\n".join(desc_parts))
        detail["requirements"] = clean_html("\n\n".join(req_parts))
        detail["benefits"] = clean_html("\n\n".join(benefit_parts))

        # Check for expiry / deadline
        deadline_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", soup.get_text())
        if deadline_match:
            try:
                d, m, y = map(int, deadline_match.groups())
                detail["expires_at"] = datetime(y, m, d, tzinfo=timezone.utc)
            except ValueError:
                pass

        return detail

    def crawl_search_page(self, page: int = 1, province: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Crawl a single search page of TimViecNhanh.
        """
        search_url = self._build_search_url(page=page, province=province)
        self.logger.info(f"Crawling TimViecNhanh page {page}: {search_url}")

        resp = self._make_request(search_url)
        if not resp or resp.status_code != 200:
            # Fallback domain if needed
            fallback_url = f"{self.fallback_base_url}/tim-kiem-viec-lam-nhanh?page={page}"
            self.logger.info(f"Retrying with fallback URL: {fallback_url}")
            resp = self._make_request(fallback_url)

        if not resp or resp.status_code != 200:
            self.logger.warning(f"Failed to fetch TimViecNhanh search page: {search_url}")
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        jobs: List[Dict[str, Any]] = []

        # Find job card containers
        job_cards = soup.select(
            ".job-item, .item-job, div[class*='job-item'], div[class*='JobCard'], article, .list-job-item"
        )
        if not job_cards:
            job_cards = [
                a.find_parent("div")
                for a in soup.select("a[href*='/viec-lam/'], a[href*='-jv']")
                if a.find_parent("div")
            ]

        self.logger.info(f"Found {len(job_cards)} job cards on TimViecNhanh page {page}")

        for card in job_cards:
            try:
                # 1. Job Title & URL
                title_elem = card.select_one(
                    "a[class*='title'], h2 a, h3 a, a.job-title, .title a, a[href*='/viec-lam/']"
                )
                if not title_elem:
                    continue

                title = clean_html(title_elem.get_text(strip=True))
                href = title_elem.get("href", "")
                if not href or len(title) < 3:
                    continue

                source_url = urljoin(self.base_url, href.split("?")[0])

                # 2. Company Name
                company_elem = card.select_one(
                    "a[class*='company'], div[class*='company'], span[class*='company'], p[class*='company'], .employer"
                )
                company_name = clean_html(company_elem.get_text(strip=True)) if company_elem else None

                # 3. Salary
                salary_elem = card.select_one(
                    "span[class*='salary'], div[class*='salary'], p[class*='salary'], .text_pink, .salary"
                )
                salary_text = clean_html(salary_elem.get_text(strip=True)) if salary_elem else None
                salary_min, salary_max = self.parse_salary(salary_text)

                # 4. Location
                loc_elem = card.select_one(
                    "span[class*='address'], span[class*='location'], div[class*='address'], div[class*='location'], .address"
                )
                loc_raw = clean_html(loc_elem.get_text(strip=True)) if loc_elem else ""
                loc_data = normalize_location(loc_raw)
                province_name = loc_data.get("province") or (normalize_province(province) if province else None)

                # 5. Detail scraping
                detail = self.crawl_job_detail(source_url)
                description = detail.get("description") or f"Vị trí: {title}. Công ty: {company_name}."
                requirements = detail.get("requirements") or ""

                category = self.detect_category(title, description)
                job_type = self.normalize_job_type(f"{title} {loc_raw} {description}")
                exp_level = self.detect_experience(f"{title} {requirements}")

                job_dict = {
                    "title": title,
                    "company_name": company_name,
                    "description": description,
                    "requirements": requirements,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_text": salary_text,
                    "location_province": province_name,
                    "location_district": loc_data.get("district"),
                    "location_full": loc_data.get("full") or province_name,
                    "job_type": job_type,
                    "category": category,
                    "experience_level": exp_level,
                    "source_platform": self.platform_name,
                    "source_url": source_url,
                    "posted_at": datetime.now(timezone.utc),
                    "expires_at": detail.get("expires_at"),
                    "crawled_at": datetime.now(timezone.utc),
                    "is_active": True,
                    "raw_data": {
                        "benefits": detail.get("benefits"),
                        "raw_salary": salary_text,
                        "raw_location": loc_raw,
                    },
                }

                jobs.append(job_dict)

            except Exception as e:
                self.logger.error(f"Error parsing TimViecNhanh job card: {e}", exc_info=False)
                continue

        return jobs

    def crawl(self, max_pages: int = 50, province: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Crawl TimViecNhanh job postings up to max_pages.
        """
        all_jobs: List[Dict[str, Any]] = []
        self.logger.info(
            f"Starting TimViecNhanh crawl (max_pages={max_pages}, province={province})..."
        )

        for page in range(1, max_pages + 1):
            try:
                page_jobs = self.crawl_search_page(page=page, province=province)
                if not page_jobs:
                    self.logger.info(f"No jobs found on TimViecNhanh page {page}. Ending crawl.")
                    break

                all_jobs.extend(page_jobs)
                self.logger.info(
                    f"TimViecNhanh page {page} collected {len(page_jobs)} jobs. Total so far: {len(all_jobs)}"
                )

            except Exception as e:
                self.logger.error(f"Error crawling TimViecNhanh page {page}: {e}", exc_info=True)
                continue

        self.logger.info(f"TimViecNhanh crawl completed. Collected {len(all_jobs)} jobs.")
        return all_jobs
