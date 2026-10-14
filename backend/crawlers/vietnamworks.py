"""
VietnamWorks crawler for C_Data job aggregation platform.
Crawls job postings from https://www.vietnamworks.com via JSON API and HTML fallback.
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

logger = logging.getLogger("crawler.vietnamworks")


class VietnamWorksCrawler(BaseCrawler):
    """
    Crawler for VietnamWorks (https://www.vietnamworks.com)
    Supports both JSON API and HTML page scraping fallback.
    """

    platform_name = "vietnamworks"
    base_url = "https://www.vietnamworks.com"
    api_search_url = "https://ms.vietnamworks.com/job-search/v1.0/search"
    api_v2_url = "https://www.vietnamworks.com/api/v2/jobs"
    delay_seconds = 2.5

    def _get_api_headers(self) -> Dict[str, str]:
        """Headers required for VietnamWorks API requests."""
        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.vietnamworks.com",
            "Referer": "https://www.vietnamworks.com/",
            "X-Source": "JobSearch",
        }

    def _crawl_via_api(self, page: int = 1, hits_per_page: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Attempt to fetch jobs via VietnamWorks JSON API endpoints.
        """
        # Try MS Search API first
        payload = {
            "query": "",
            "filter": [],
            "ranges": [],
            "order": [],
            "hitsPerPage": hits_per_page,
            "page": page - 1,  # 0-indexed in API
        }

        resp = self._make_request(
            self.api_search_url,
            method="POST",
            json=payload,
            headers=self._get_api_headers(),
        )

        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                items = data.get("data", []) or data.get("hits", [])
                if items:
                    self.logger.info(f"Successfully retrieved {len(items)} jobs via MS search API (page {page})")
                    return self._parse_api_jobs(items)
            except Exception as e:
                self.logger.warning(f"Error parsing VietnamWorks MS API response: {e}")

        # Fallback to API v2 GET endpoint
        params = {
            "page": page,
            "fields": "id,title,company,salary,location,jobDescription,jobRequirement,alias,workingLocations",
            "limit": hits_per_page,
        }
        resp_v2 = self._make_request(
            self.api_v2_url,
            method="GET",
            params=params,
            headers=self._get_api_headers(),
        )

        if resp_v2 and resp_v2.status_code == 200:
            try:
                data = resp_v2.json()
                items = data.get("data", []) or data.get("jobs", [])
                if items:
                    self.logger.info(f"Successfully retrieved {len(items)} jobs via v2 API (page {page})")
                    return self._parse_api_jobs(items)
            except Exception as e:
                self.logger.warning(f"Error parsing VietnamWorks v2 API response: {e}")

        return None

    def _parse_api_jobs(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert VietnamWorks JSON API records into normalized job dicts.
        """
        parsed_jobs: List[Dict[str, Any]] = []

        for item in items:
            try:
                title = item.get("jobTitle") or item.get("title") or ""
                if not title:
                    continue

                # Company
                company_name = ""
                company_info = item.get("company") or {}
                if isinstance(company_info, dict):
                    company_name = company_info.get("name") or company_info.get("companyName") or ""
                elif isinstance(company_info, str):
                    company_name = company_info
                if not company_name:
                    company_name = item.get("companyName", "")

                # URL / Alias
                alias = item.get("alias") or item.get("jobUrl") or item.get("url") or ""
                job_id = item.get("jobId") or item.get("id") or ""
                if alias.startswith("http"):
                    source_url = alias
                elif alias:
                    source_url = urljoin(self.base_url, f"/{alias}-jv" if not alias.endswith("-jv") else f"/{alias}")
                elif job_id:
                    source_url = f"{self.base_url}/job/{job_id}"
                else:
                    continue

                # Salary
                salary_min = item.get("salaryMin")
                salary_max = item.get("salaryMax")
                pretty_salary = item.get("prettySalary") or item.get("salary") or ""
                if not salary_min and not salary_max and pretty_salary:
                    salary_min, salary_max = self.parse_salary(pretty_salary)
                elif salary_min or salary_max:
                    pretty_salary = f"{salary_min or 0} - {salary_max or ''} VNĐ"

                # Location
                locations_list = item.get("workingLocations") or item.get("locations") or []
                loc_strings = []
                if isinstance(locations_list, list):
                    for loc in locations_list:
                        if isinstance(loc, dict):
                            loc_strings.append(loc.get("cityName") or loc.get("address") or "")
                        elif isinstance(loc, str):
                            loc_strings.append(loc)
                loc_full = ", ".join(filter(None, loc_strings)) or item.get("location", "")
                loc_data = normalize_location(loc_full)

                # Description and requirements
                desc = clean_html(item.get("jobDescription") or "")
                req = clean_html(item.get("jobRequirement") or item.get("requirements") or "")

                category = item.get("category") or self.detect_category(title, desc)
                job_type = self.normalize_job_type(f"{title} {item.get('jobType', '')}")
                exp_level = self.detect_experience(f"{title} {req} {item.get('jobLevel', '')}")

                # Date parsing
                posted_at = datetime.now(timezone.utc)
                published = item.get("publishedDate") or item.get("approvedOn")
                if published:
                    try:
                        if isinstance(published, (int, float)):
                            posted_at = datetime.fromtimestamp(published / 1000.0, tz=timezone.utc)
                        elif isinstance(published, str):
                            posted_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    except Exception:
                        pass

                expires_at = None
                expired = item.get("expiredDate")
                if expired:
                    try:
                        if isinstance(expired, (int, float)):
                            expires_at = datetime.fromtimestamp(expired / 1000.0, tz=timezone.utc)
                        elif isinstance(expired, str):
                            expires_at = datetime.fromisoformat(expired.replace("Z", "+00:00"))
                    except Exception:
                        pass

                job_dict = {
                    "title": title.strip(),
                    "company_name": company_name.strip() if company_name else None,
                    "description": desc or f"Vị trí: {title}. Công ty: {company_name}.",
                    "requirements": req,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_text": str(pretty_salary) if pretty_salary else None,
                    "location_province": loc_data.get("province"),
                    "location_district": loc_data.get("district"),
                    "location_full": loc_data.get("full") or loc_data.get("province"),
                    "job_type": job_type,
                    "category": category,
                    "experience_level": exp_level,
                    "source_platform": self.platform_name,
                    "source_url": source_url,
                    "posted_at": posted_at,
                    "expires_at": expires_at,
                    "crawled_at": datetime.now(timezone.utc),
                    "is_active": True,
                    "raw_data": item,
                }
                parsed_jobs.append(job_dict)

            except Exception as e:
                self.logger.error(f"Error parsing VietnamWorks API item: {e}", exc_info=False)
                continue

        return parsed_jobs

    def crawl_job_detail(self, job_url: str) -> Dict[str, Any]:
        """
        Fetch HTML detail page if API didn't provide full description.
        """
        detail = {
            "description": "",
            "requirements": "",
            "benefits": "",
            "expires_at": None,
        }
        resp = self._make_request(job_url)
        if not resp or resp.status_code != 200:
            return detail

        soup = BeautifulSoup(resp.content, "html.parser")
        desc_elem = soup.select_one(".job-description, .description, div[class*='JobDescription']")
        req_elem = soup.select_one(".job-requirements, .requirements, div[class*='JobRequirement']")

        if desc_elem:
            detail["description"] = clean_html(str(desc_elem))
        if req_elem:
            detail["requirements"] = clean_html(str(req_elem))

        return detail

    def crawl_search_page_html(self, page: int = 1) -> List[Dict[str, Any]]:
        """
        Fallback scraper for VietnamWorks HTML search results.
        """
        url = f"{self.base_url}/tim-viec-lam/tat-ca-viec-lam?page={page}"
        self.logger.info(f"Crawling VietnamWorks HTML page {page}: {url}")

        resp = self._make_request(url)
        if not resp or resp.status_code != 200:
            self.logger.warning(f"Failed to fetch VietnamWorks HTML page: {url}")
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        jobs: List[Dict[str, Any]] = []

        # Find job card containers
        job_cards = soup.select(
            "div[class*='job-card'], div[class*='JobCard_card'], .block-job-item, .job-item"
        )
        if not job_cards:
            job_cards = [
                a.find_parent("div")
                for a in soup.select("a[href*='-jv']")
                if a.find_parent("div")
            ]

        self.logger.info(f"Found {len(job_cards)} job cards on HTML page {page}")

        for card in job_cards:
            try:
                title_elem = card.select_one(
                    "a[class*='title'], h2 a, h3 a, a[href*='-jv'], .job-title a"
                )
                if not title_elem:
                    continue

                title = clean_html(title_elem.get_text(strip=True))
                href = title_elem.get("href", "")
                if not href:
                    continue

                source_url = urljoin(self.base_url, href.split("?")[0])

                company_elem = card.select_one(
                    "a[class*='company'], div[class*='company'], span[class*='company'], .company-name"
                )
                company_name = clean_html(company_elem.get_text(strip=True)) if company_elem else None

                salary_elem = card.select_one(
                    "span[class*='salary'], div[class*='salary'], .salary"
                )
                salary_text = clean_html(salary_elem.get_text(strip=True)) if salary_elem else None
                salary_min, salary_max = self.parse_salary(salary_text)

                loc_elem = card.select_one(
                    "span[class*='location'], div[class*='location'], .location"
                )
                loc_raw = clean_html(loc_elem.get_text(strip=True)) if loc_elem else ""
                loc_data = normalize_location(loc_raw)

                # Fetch details
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
                    "location_province": loc_data.get("province"),
                    "location_district": loc_data.get("district"),
                    "location_full": loc_data.get("full") or loc_data.get("province"),
                    "job_type": job_type,
                    "category": category,
                    "experience_level": exp_level,
                    "source_platform": self.platform_name,
                    "source_url": source_url,
                    "posted_at": datetime.now(timezone.utc),
                    "expires_at": detail.get("expires_at"),
                    "crawled_at": datetime.now(timezone.utc),
                    "is_active": True,
                    "raw_data": {"raw_salary": salary_text, "raw_location": loc_raw},
                }
                jobs.append(job_dict)

            except Exception as e:
                self.logger.error(f"Error parsing VietnamWorks HTML card: {e}", exc_info=False)
                continue

        return jobs

    def crawl(self, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Crawl VietnamWorks up to max_pages using API, falling back to HTML parsing if necessary.
        """
        all_jobs: List[Dict[str, Any]] = []
        self.logger.info(f"Starting VietnamWorks crawl (max_pages={max_pages})...")

        for page in range(1, max_pages + 1):
            try:
                # 1. Attempt API crawl first
                page_jobs = self._crawl_via_api(page=page)

                # 2. If API fails or yields no jobs, fallback to HTML crawl
                if page_jobs is None or len(page_jobs) == 0:
                    self.logger.info(f"API returned no results for page {page}. Falling back to HTML crawl.")
                    page_jobs = self.crawl_search_page_html(page=page)

                if not page_jobs:
                    self.logger.info(f"No jobs found on VietnamWorks page {page}. Ending crawl.")
                    break

                all_jobs.extend(page_jobs)
                self.logger.info(
                    f"VietnamWorks page {page} collected {len(page_jobs)} jobs. Total so far: {len(all_jobs)}"
                )

            except Exception as e:
                self.logger.error(f"Error crawling VietnamWorks page {page}: {e}", exc_info=True)
                continue

        self.logger.info(f"VietnamWorks crawl completed. Collected {len(all_jobs)} jobs.")
        return all_jobs
