"""
TopCV crawler for C_Data job aggregation platform.
Crawls job postings from https://www.topcv.vn.
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

logger = logging.getLogger("crawler.topcv")


class TopCVCrawler(BaseCrawler):
    """
    Crawler for TopCV (https://www.topcv.vn)
    """

    platform_name = "topcv"
    base_url = "https://www.topcv.vn"
    delay_seconds = 2.5

    # TopCV Province ID mapping
    PROVINCE_IDS: Dict[str, int] = {
        "Hà Nội": 1,
        "TP. Hồ Chí Minh": 2,
        "Đà Nẵng": 3,
        "Bình Dương": 4,
        "Đồng Nai": 5,
        "Hải Phòng": 6,
        "Bắc Ninh": 7,
        "Hưng Yên": 8,
        "Quảng Ninh": 9,
        "Hải Dương": 10,
        "Vĩnh Phúc": 11,
        "Thái Nguyên": 12,
        "Cần Thơ": 13,
        "Long An": 14,
        "Bà Rịa - Vũng Tàu": 15,
        "Bắc Giang": 16,
        "Tiền Giang": 17,
        "Thái Bình": 18,
        "Nam Định": 19,
        "Thanh Hóa": 20,
        "Nghệ An": 21,
        "Hà Nam": 22,
        "Phú Thọ": 23,
        "Thừa Thiên Huế": 24,
        "Quảng Nam": 25,
        "Bình Định": 26,
        "Khánh Hòa": 27,
        "Lâm Đồng": 28,
        "Bình Phước": 29,
        "Tây Ninh": 30,
        "Bến Tre": 31,
        "Đồng Tháp": 32,
        "Vĩnh Long": 33,
        "An Giang": 34,
        "Kiên Giang": 35,
        "Cà Mau": 36,
        "Sóc Trăng": 37,
        "Bạc Liêu": 38,
        "Trà Vinh": 39,
        "Hậu Giang": 40,
        "Ninh Bình": 41,
        "Hòa Bình": 42,
        "Sơn La": 43,
        "Điện Biên": 44,
        "Lai Châu": 45,
        "Lào Cai": 46,
        "Yên Bái": 47,
        "Hà Giang": 48,
        "Tuyên Quang": 49,
        "Cao Bằng": 50,
        "Bắc Kạn": 51,
        "Lạng Sơn": 52,
        "Hà Tĩnh": 53,
        "Quảng Bình": 54,
        "Quảng Trị": 55,
        "Quảng Ngãi": 56,
        "Phú Yên": 57,
        "Ninh Thuận": 58,
        "Bình Thuận": 59,
        "Kon Tum": 60,
        "Gia Lai": 61,
        "Đắk Lắk": 62,
        "Đắk Nông": 63,
    }

    def _build_search_url(self, page: int = 1, province_id: Optional[int] = None) -> str:
        """
        Build search listing URL for TopCV.
        """
        if province_id:
            return f"{self.base_url}/tim-viec-lam-moi-nhat?province_id={province_id}&page={page}"
        return f"{self.base_url}/tim-viec-lam-moi-nhat?page={page}"

    def crawl_job_detail(self, job_url: str) -> Dict[str, Any]:
        """
        Scrape detailed job information from a TopCV job detail page.
        """
        detail = {
            "description": "",
            "requirements": "",
            "benefits": "",
            "expires_at": None,
            "raw_html": "",
        }

        resp = self._make_request(job_url)
        if not resp or resp.status_code != 200:
            self.logger.warning(f"Could not load detail page: {job_url}")
            return detail

        soup = BeautifulSoup(resp.content, "html.parser")

        # 1. Look for structured job-description items
        # Usually TopCV has .job-description__item or sections with h3 titles
        desc_parts = []
        req_parts = []
        benefit_parts = []

        # Find items under job detail container
        sections = soup.select(".job-description__item, .job-data, .box-job-description")
        if not sections:
            # Fallback to general container
            sections = soup.select(".job-detail__box--left, .job-detail-content, .job-description")

        for sec in sections:
            sec_text = sec.get_text(separator="\n", strip=True)
            sec_title = ""
            title_tag = sec.find(["h2", "h3", "h4", "strong", "div", "h5"])
            if title_tag:
                sec_title = title_tag.get_text(strip=True).lower()

            if any(k in sec_title for k in ["mô tả", "nội dung công việc", "job description"]):
                desc_parts.append(sec_text)
            elif any(k in sec_title for k in ["yêu cầu", "tiêu chuẩn", "requirement", "kinh nghiệm"]):
                req_parts.append(sec_text)
            elif any(k in sec_title for k in ["quyền lợi", "chế độ", "benefit", "đãi ngộ"]):
                benefit_parts.append(sec_text)

        # Fallback if no specific sections split detected
        if not desc_parts and not req_parts:
            # Extract main text
            main_content = soup.select_one(".job-detail__information-detail, .job-description, #job-description")
            if main_content:
                text = clean_html(str(main_content))
                # Try regex splitting on headers
                split_desc = re.split(r"(?:Yêu cầu ứng viên|Yêu cầu công việc|QUYỀN LỢI ĐƯỢC HƯỞNG|Quyền lợi):?", text, flags=re.IGNORECASE)
                if len(split_desc) >= 2:
                    desc_parts.append(split_desc[0].strip())
                    req_parts.append(split_desc[1].strip())
                    if len(split_desc) >= 3:
                        benefit_parts.append(split_desc[2].strip())
                else:
                    desc_parts.append(text)

        detail["description"] = clean_html("\n\n".join(desc_parts))
        detail["requirements"] = clean_html("\n\n".join(req_parts))
        detail["benefits"] = clean_html("\n\n".join(benefit_parts))

        # Check for deadline / expires_at
        # e.g., "Hạn nộp hồ sơ: 30/11/2026"
        deadline_tag = soup.find(text=re.compile(r"Hạn nộp hồ sơ|Hạn nộp", re.IGNORECASE))
        if deadline_tag:
            date_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", str(deadline_tag.parent))
            if date_match:
                try:
                    d, m, y = map(int, date_match.groups())
                    detail["expires_at"] = datetime(y, m, d, tzinfo=timezone.utc)
                except ValueError:
                    pass

        return detail

    def crawl_search_page(self, page: int = 1, province_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Crawl a single search page of TopCV.
        """
        search_url = self._build_search_url(page=page, province_id=province_id)
        self.logger.info(f"Crawling TopCV page {page}: {search_url}")

        resp = self._make_request(search_url)
        if not resp or resp.status_code != 200:
            self.logger.warning(f"Failed to fetch TopCV search page: {search_url}")
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        jobs: List[Dict[str, Any]] = []

        # TopCV job item cards
        job_cards = soup.select(
            ".job-item-search-result, .job-item-2, .job-item, div[data-job-id], .job-ta"
        )
        if not job_cards:
            # Fallback search for anchor tags linking to viec-lam
            job_cards = [
                a.find_parent("div")
                for a in soup.select("a[href*='/viec-lam/']")
                if a.find_parent("div")
            ]
            # Deduplicate parents
            seen_ids = set()
            unique_cards = []
            for card in job_cards:
                cid = id(card)
                if cid not in seen_ids:
                    seen_ids.add(cid)
                    unique_cards.append(card)
            job_cards = unique_cards

        self.logger.info(f"Found {len(job_cards)} job cards on page {page}")

        for card in job_cards:
            try:
                # 1. Job Title & Detail URL
                title_elem = card.select_one(
                    ".job-title a, .title a, a.job-item-title, h3 a, a[target='_blank'][href*='/viec-lam/']"
                )
                if not title_elem:
                    continue

                title = clean_html(title_elem.get_text(strip=True))
                href = title_elem.get("href", "")
                if not href:
                    continue

                source_url = urljoin(self.base_url, href.split("?")[0])  # Clean tracking params

                # 2. Company Name
                company_elem = card.select_one(
                    ".company a, .company-name a, .company-title a, a[class*='company'], .name a"
                )
                company_name = clean_html(company_elem.get_text(strip=True)) if company_elem else None

                # 3. Salary
                salary_elem = card.select_one(
                    ".salary, .title-salary, .job-item-salary, span[class*='salary'], label[class*='salary']"
                )
                salary_text = clean_html(salary_elem.get_text(strip=True)) if salary_elem else None
                salary_min, salary_max = self.parse_salary(salary_text)

                # 4. Location
                loc_elem = card.select_one(
                    ".address, .location, .job-item-address, span[class*='address'], span[class*='location']"
                )
                loc_raw = clean_html(loc_elem.get_text(strip=True)) if loc_elem else ""
                loc_data = normalize_location(loc_raw)

                province = loc_data.get("province")
                if not province and province_id:
                    # Map reverse from province_id if available
                    for name, pid in self.PROVINCE_IDS.items():
                        if pid == province_id:
                            province = name
                            break

                # 5. Extract full description from detail page
                detail = self.crawl_job_detail(source_url)

                # 6. Categorization & metadata
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
                self.logger.error(f"Error parsing TopCV job card: {e}", exc_info=False)
                continue

        return jobs

    def crawl(
        self,
        max_pages: int = 50,
        province_id: Optional[int] = None,
        province_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Crawl TopCV up to max_pages. Supports filtering by province.
        """
        all_jobs: List[Dict[str, Any]] = []

        target_province_id = province_id
        if not target_province_id and province_name:
            target_province_id = self.PROVINCE_IDS.get(province_name) or self.PROVINCE_IDS.get(
                normalize_province(province_name) or ""
            )

        self.logger.info(
            f"Starting TopCV crawl (max_pages={max_pages}, province_id={target_province_id})..."
        )

        for page in range(1, max_pages + 1):
            try:
                page_jobs = self.crawl_search_page(page=page, province_id=target_province_id)
                if not page_jobs:
                    self.logger.info(f"No jobs found on page {page}. Ending crawl.")
                    break

                all_jobs.extend(page_jobs)
                self.logger.info(f"TopCV page {page} collected {len(page_jobs)} jobs. Total so far: {len(all_jobs)}")

            except Exception as e:
                self.logger.error(f"Error on TopCV page {page}: {e}", exc_info=True)
                continue

        self.logger.info(f"TopCV crawl finished. Collected {len(all_jobs)} jobs.")
        return all_jobs
