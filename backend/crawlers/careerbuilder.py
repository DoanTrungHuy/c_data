"""
CareerBuilder Vietnam crawler for C_Data job aggregation platform.
Crawls job postings from https://careerbuilder.vn (careerviet.vn).
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

logger = logging.getLogger("crawler.careerbuilder")


class CareerBuilderCrawler(BaseCrawler):
    """
    Crawler for CareerBuilder Vietnam (careerviet.vn)
    """

    platform_name = "careerbuilder"
    base_url = "https://careerbuilder.vn"
    fallback_base_url = "https://careerviet.vn"
    delay_seconds = 2.5

    def _build_search_url(self, page: int = 1) -> str:
        """
        Build URL for CareerBuilder search pages.
        Format: https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-trang-{page}-vi.html
        """
        return f"{self.base_url}/viec-lam/tat-ca-viec-lam-trang-{page}-vi.html"

    def crawl_job_detail(self, job_url: str) -> Dict[str, Any]:
        """
        Fetch and parse full job details from job detail page.
        """
        detail = {
            "description": "",
            "requirements": "",
            "benefits": "",
            "expires_at": None,
            "job_type": None,
            "experience_level": None,
        }

        resp = self._make_request(job_url)
        if not resp or resp.status_code != 200:
            self.logger.warning(f"Could not load CareerBuilder detail page: {job_url}")
            return detail

        soup = BeautifulSoup(resp.content, "html.parser")

        # Detail content boxes in CareerBuilder
        # Elements often: .detail-row, .job-detail-content, .job-description, .detail-box
        desc_parts = []
        req_parts = []
        benefit_parts = []

        detail_boxes = soup.select(".detail-row, .detail-box, .job-detail-content, .box-item")
        for box in detail_boxes:
            title_tag = box.find(["h2", "h3", "h4", "strong", "div", "p"])
            title_text = title_tag.get_text(strip=True).lower() if title_tag else ""
            content_text = box.get_text(separator="\n", strip=True)

            if any(k in title_text for k in ["mô tả công việc", "mô tả", "job description"]):
                desc_parts.append(content_text)
            elif any(k in title_text for k in ["yêu cầu công việc", "yêu cầu", "job requirement", "kỹ năng"]):
                req_parts.append(content_text)
            elif any(k in title_text for k in ["phúc lợi", "quyền lợi", "chế độ", "benefit"]):
                benefit_parts.append(content_text)

        # Fallback if boxes were not separated by class
        if not desc_parts and not req_parts:
            main_container = soup.select_one(".full-content, .job-detail-content, .job-description")
            if main_container:
                raw_text = clean_html(str(main_container))
                sections = re.split(r"(?:Yêu cầu công việc|Yêu cầu ứng viên|Phúc lợi|Quyền lợi):?", raw_text, flags=re.IGNORECASE)
                if len(sections) >= 2:
                    desc_parts.append(sections[0].strip())
                    req_parts.append(sections[1].strip())
                    if len(sections) >= 3:
                        benefit_parts.append(sections[2].strip())
                else:
                    desc_parts.append(raw_text)

        detail["description"] = clean_html("\n\n".join(desc_parts))
        detail["requirements"] = clean_html("\n\n".join(req_parts))
        detail["benefits"] = clean_html("\n\n".join(benefit_parts))

        # Check for expiry / deadline
        # e.g., "Hạn nộp hồ sơ: 15-11-2026"
        deadline_match = re.search(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", soup.get_text())
        if deadline_match:
            try:
                d, m, y = map(int, deadline_match.groups())
                detail["expires_at"] = datetime(y, m, d, tzinfo=timezone.utc)
            except ValueError:
                pass

        return detail

    def crawl_search_page(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        Crawl a single search page of CareerBuilder Vietnam.
        """
        search_url = self._build_search_url(page=page)
        self.logger.info(f"Crawling CareerBuilder page {page}: {search_url}")

        resp = self._make_request(search_url)
        if not resp or resp.status_code != 200:
            # Try fallback URL if careerbuilder.vn redirected or failed
            fallback_url = f"{self.fallback_base_url}/viec-lam/tat-ca-viec-lam-trang-{page}-vi.html"
            self.logger.info(f"Retrying with fallback domain: {fallback_url}")
            resp = self._make_request(fallback_url)

        if not resp or resp.status_code != 200:
            self.logger.warning(f"Failed to fetch CareerBuilder search page: {search_url}")
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        jobs: List[Dict[str, Any]] = []

        # Find job card containers
        job_cards = soup.select(
            ".job-item, .jobs-side-list .job-item, div[class*='job-item'], .item-job, .bx-job-item"
        )
        if not job_cards:
            job_cards = [
                a.find_parent("div")
                for a in soup.select("a[href*='/viec-lam/']")
                if a.find_parent("div")
            ]

        self.logger.info(f"Found {len(job_cards)} job cards on CareerBuilder page {page}")

        for card in job_cards:
            try:
                # 1. Job Title & URL
                title_elem = card.select_one(
                    ".job_title a, a.job_title, .title a, a[class*='job-title'], h2 a, h3 a, a.title"
                )
                if not title_elem:
                    continue

                title = clean_html(title_elem.get_text(strip=True))
                href = title_elem.get("href", "")
                if not href:
                    continue

                source_url = urljoin(self.base_url, href.split("?")[0])

                # 2. Company Name
                company_elem = card.select_one(
                    ".company-name a, a.company-name, .company a, a[class*='company'], .caption .company-name"
                )
                company_name = clean_html(company_elem.get_text(strip=True)) if company_elem else None

                # 3. Salary
                salary_elem = card.select_one(
                    ".salary, div.salary, p.salary, li.salary, span.salary, div[class*='salary']"
                )
                salary_text = clean_html(salary_elem.get_text(strip=True)) if salary_elem else None
                salary_min, salary_max = self.parse_salary(salary_text)

                # 4. Location
                loc_elem = card.select_one(
                    ".location, div.location, li.location, div[class*='location'], .location p"
                )
                loc_raw = clean_html(loc_elem.get_text(strip=True)) if loc_elem else ""
                loc_data = normalize_location(loc_raw)
                province = loc_data.get("province")

                # 5. Posted date
                time_elem = card.select_one(".time, div.time, time, span.time, .post-date")
                time_raw = clean_html(time_elem.get_text(strip=True)) if time_elem else ""
                posted_at = datetime.now(timezone.utc)
                if time_raw:
                    date_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", time_raw)
                    if date_match:
                        try:
                            d, m, y = map(int, date_match.groups())
                            posted_at = datetime(y, m, d, tzinfo=timezone.utc)
                        except ValueError:
                            pass

                # 6. Detail scraping
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
                    "location_province": province,
                    "location_district": loc_data.get("district"),
                    "location_full": loc_data.get("full") or province,
                    "job_type": job_type,
                    "category": category,
                    "experience_level": exp_level,
                    "source_platform": self.platform_name,
                    "source_url": source_url,
                    "posted_at": posted_at,
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
                self.logger.error(f"Error parsing CareerBuilder job card: {e}", exc_info=False)
                continue

        return jobs

    def crawl(self, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Crawl CareerBuilder Vietnam up to max_pages.
        """
        all_jobs: List[Dict[str, Any]] = []
        self.logger.info(f"Starting CareerBuilder crawl (max_pages={max_pages})...")

        for page in range(1, max_pages + 1):
            try:
                page_jobs = self.crawl_search_page(page=page)
                if not page_jobs:
                    self.logger.info(f"No jobs found on CareerBuilder page {page}. Ending crawl.")
                    break

                all_jobs.extend(page_jobs)
                self.logger.info(
                    f"CareerBuilder page {page} collected {len(page_jobs)} jobs. Total so far: {len(all_jobs)}"
                )

            except Exception as e:
                self.logger.error(f"Error crawling CareerBuilder page {page}: {e}", exc_info=True)
                continue

        self.logger.info(f"CareerBuilder crawl completed. Collected {len(all_jobs)} jobs.")
        return all_jobs
