"""
CareerViet / CareerBuilder Vietnam Job Crawler Adapter.
Implements the BaseJobAdapter contract for parsing public listings, detail pages,
pagination, incremental crawling, and error classification for CareerViet.vn.
"""

from datetime import datetime, timezone
import logging
import re
import time
from typing import Any, Dict, List, Optional
import urllib.parse

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import unidecode

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from crawlers.utils import extract_salary_range, normalize_location

logger = logging.getLogger("c_data.adapters.careerviet")

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"


def slugify_vietnamese(text: str) -> str:
    clean = unidecode.unidecode(text).lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return clean


class CareerVietAdapter(BaseJobAdapter):
    """
    Adapter thu thập dữ liệu chuyên biệt cho CareerViet (careerbuilder.vn / careerviet.vn)
    Không dùng chung HTML parser với các nguồn khác.
    """

    adapter_id = "careerviet"
    source_name = "Sàn tuyển dụng CareerViet"
    source_domain = "careerviet.vn"
    base_url = "https://careerviet.vn"
    default_delay_seconds = 1.0

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or self._init_session()

    def _init_session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        s.mount("https://", HTTPAdapter(max_retries=retries))
        s.headers.update({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        return s

    def build_search_url(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        page: int = 1,
    ) -> str:
        """Tạo URL tìm kiếm chuẩn cho CareerViet"""
        search_kw = (keyword or "").strip()
        search_prov = (province or "").strip()
        query_part = f"{search_kw} {search_prov}".strip()

        if query_part:
            slug = slugify_vietnamese(query_part)
            if page > 1:
                return f"{self.base_url}/viec-lam/{slug}-k-trang-{page}-vi.html"
            return f"{self.base_url}/viec-lam/{slug}-k-vi.html"
        else:
            if page > 1:
                return f"{self.base_url}/viec-lam/tat-ca-viec-lam-trang-{page}-vi.html"
            return f"{self.base_url}/viec-lam/tat-ca-viec-lam-vi.html"

    def parse_html_search_page(
        self,
        html_content: str,
        target_url: str = "https://careerviet.vn",
        since_timestamp: Optional[datetime] = None,
        limit: int = 20,
    ) -> AdapterCrawlResult:
        """
        Bóc tách HTML danh sách kết quả tìm kiếm của CareerViet.
        Phương thức này hoàn toàn độc lập và có thể chạy offline trên fixture test.
        """
        result = AdapterCrawlResult(
            source_id=self.adapter_id,
            source_name=self.source_name,
            raw_metadata={"target_url": target_url},
        )

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            job_containers = soup.find_all("div", class_=re.compile(r"job-item|jobs-item"))

            # Nếu không tìm thấy class job-item, fallback sang thẻ a chứa /tim-viec-lam/
            if not job_containers:
                links = soup.find_all("a", href=lambda h: h and "/tim-viec-lam/" in h)
                seen_parents = set()
                job_containers = []
                for l in links:
                    p = l.find_parent("div", class_=re.compile(r"caption|figure|item")) or l.parent
                    if p and p not in seen_parents:
                        seen_parents.add(p)
                        job_containers.append(p)

            now = datetime.now(timezone.utc)
            result.total_detected = len(job_containers)

            for container in job_containers:
                if len(result.items) >= limit:
                    break

                # 1. Tìm liên kết và tiêu đề
                a_tag = container.find("a", href=lambda h: h and ("/tim-viec-lam/" in h or "/viec-lam/" in h))
                if not a_tag:
                    continue

                raw_title = a_tag.get_text(strip=True)
                if not raw_title or any(w in raw_title.lower() for w in ["hạn nộp", "lương:", "cạnh tranh"]):
                    continue

                href = a_tag["href"]
                full_url = urllib.parse.urljoin(self.base_url, href)

                # Bóc tách source_job_id
                job_id_match = re.search(r"\.([0-9A-Za-z]+)\.html", full_url)
                source_job_id = job_id_match.group(1) if job_id_match else full_url.split("/")[-1].replace(".html", "")

                # 2. Tên công ty
                comp_tag = container.find("a", href=lambda h: h and "/nha-tuyen-dung/" in h)
                if not comp_tag:
                    comp_tag = container.find("a", class_=re.compile(r"company"))
                company_name = comp_tag.get_text(strip=True) if comp_tag else "Doanh nghiệp tuyển dụng"

                # 3. Lương
                sal_tag = container.find(class_=re.compile(r"salary|luong"))
                salary_text = sal_tag.get_text(strip=True) if sal_tag else "Thỏa thuận"
                sal_min, sal_max = extract_salary_range(salary_text)

                # 4. Địa điểm
                loc_tag = container.find(class_=re.compile(r"location|dia-diem"))
                location_raw = loc_tag.get_text(separator=", ", strip=True) if loc_tag else "Toàn quốc"
                loc_norm = normalize_location(location_raw)

                # 5. Mốc thời gian đăng / cập nhật
                posted_date = None
                container_text = container.get_text(separator=" ", strip=True)
                date_match = re.search(r"Cập nhật[:\s]*(\d{1,2})[-/](\d{1,2})[-/](\d{4})", container_text)
                if date_match:
                    try:
                        d, m, y = map(int, date_match.groups())
                        posted_date = datetime(y, m, d, tzinfo=timezone.utc)
                    except Exception:
                        posted_date = None

                # Incremental crawling: bỏ qua nếu bài viết cũ hơn mốc since_timestamp
                if since_timestamp and posted_date and posted_date < since_timestamp:
                    continue

                is_fixture = "[FIXTURE_TEST_ONLY]" in raw_title or "[FIXTURE_TEST_ONLY]" in html_content

                item = RawJobRecord(
                    source_job_id=source_job_id,
                    title=raw_title,
                    company_name=company_name,
                    source_url=full_url,
                    apply_url=full_url,
                    salary_text=salary_text,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    location_raw=location_raw,
                    location_province=loc_norm.get("province"),
                    location_district=loc_norm.get("district"),
                    workplace_type="onsite",
                    employment_type="full-time",
                    posted_at=posted_date,
                    status="active_likely",
                    status_evidence=f"Tin đăng công khai trên CareerViet (cập nhật {posted_date.strftime('%d/%m/%Y') if posted_date else 'mới'})",
                    extraction_confidence=0.9,
                    location_confidence=0.85 if loc_norm.get("province") else 0.5,
                    raw_data_reference={"extracted_from": target_url, "html_tag": container.name},
                    is_test_fixture=is_fixture,
                )
                result.items.append(item)

            # 6. Nhận diện phân trang (Pagination)
            pagination_container = soup.find(class_=re.compile(r"pagination|paging"))
            if pagination_container:
                next_elem = pagination_container.find(class_=re.compile(r"next"))
                next_link = next_elem.find("a") if next_elem and next_elem.name != "a" else next_elem
                if next_link and next_link.get("href"):
                    result.has_more = True
                    match_pg = re.search(r"trang-(\d+)", next_link["href"])
                    if match_pg:
                        result.next_page = int(match_pg.group(1))

        except Exception as e:
            logger.error(f"Lỗi khi bóc tách HTML CareerViet: {e}")
            result.errors.append(
                AdapterError(
                    error_type=AdapterErrorType.PARSE_ERROR,
                    message=f"Lỗi phân tích cú pháp HTML CareerViet: {str(e)}",
                    url=target_url,
                )
            )

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
        Thực hiện phát hiện tin tuyển dụng thực tế qua kết nối mạng tới CareerViet
        """
        t0 = time.time()
        target_url = self.build_search_url(keyword=keyword, province=province, page=page)

        try:
            resp = self.session.get(target_url, timeout=10.0)
            latency = round((time.time() - t0) * 1000, 1)

            if resp.status_code == 200:
                result = self.parse_html_search_page(
                    html_content=resp.text,
                    target_url=target_url,
                    since_timestamp=since_timestamp,
                    limit=limit,
                )
                result.crawl_duration_ms = latency
                result.page = page
                return result

            elif resp.status_code == 429:
                err = AdapterError(
                    error_type=AdapterErrorType.RATE_LIMITED,
                    message="Máy chủ CareerViet phản hồi mã 429 (Too Many Requests)",
                    url=target_url,
                    status_code=429,
                )
                return AdapterCrawlResult(
                    source_id=self.adapter_id,
                    source_name=self.source_name,
                    crawl_duration_ms=latency,
                    errors=[err],
                )

            elif resp.status_code in [401, 403]:
                err = AdapterError(
                    error_type=AdapterErrorType.ROBOTS_DENIED,
                    message=f"Bị chặn truy cập HTTP {resp.status_code}",
                    url=target_url,
                    status_code=resp.status_code,
                )
                return AdapterCrawlResult(
                    source_id=self.adapter_id,
                    source_name=self.source_name,
                    crawl_duration_ms=latency,
                    errors=[err],
                )
            else:
                err = AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"Máy chủ phản hồi mã lỗi HTTP {resp.status_code}",
                    url=target_url,
                    status_code=resp.status_code,
                )
                return AdapterCrawlResult(
                    source_id=self.adapter_id,
                    source_name=self.source_name,
                    crawl_duration_ms=latency,
                    errors=[err],
                )

        except requests.exceptions.Timeout:
            latency = round((time.time() - t0) * 1000, 1)
            err = AdapterError(
                error_type=AdapterErrorType.NETWORK_TIMEOUT,
                message="Quá thời gian chờ phản hồi (Timeout sau 10s)",
                url=target_url,
            )
            return AdapterCrawlResult(
                source_id=self.adapter_id,
                source_name=self.source_name,
                crawl_duration_ms=latency,
                errors=[err],
            )
        except requests.exceptions.RequestException as e:
            latency = round((time.time() - t0) * 1000, 1)
            err = AdapterError(
                error_type=AdapterErrorType.CONNECTION_FAILED,
                message=f"Lỗi kết nối mạng: {str(e)}",
                url=target_url,
            )
            return AdapterCrawlResult(
                source_id=self.adapter_id,
                source_name=self.source_name,
                crawl_duration_ms=latency,
                errors=[err],
            )

    def parse_html_detail_page(self, html_content: str, job_url: str) -> Dict[str, Any]:
        """Bóc tách nội dung trang chi tiết CareerViet"""
        soup = BeautifulSoup(html_content, "html.parser")
        desc_parts, req_parts, benefit_parts = [], [], []

        detail_boxes = soup.select(".detail-box, .detail-row, .job-detail-content")
        for box in detail_boxes:
            title_tag = box.find(["h2", "h3", "h4", "strong"])
            title_text = title_tag.get_text(strip=True).lower() if title_tag else ""
            content = box.get_text(separator="\n", strip=True)

            if any(k in title_text for k in ["mô tả công việc", "mô tả"]):
                desc_parts.append(content)
            elif any(k in title_text for k in ["yêu cầu công việc", "yêu cầu"]):
                req_parts.append(content)
            elif any(k in title_text for k in ["phúc lợi", "quyền lợi"]):
                benefit_parts.append(content)

        deadline = None
        exp_box = soup.find(class_=re.compile(r"expiry|han-nop"))
        if exp_box:
            m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", exp_box.get_text())
            if m:
                try:
                    d, mo, y = map(int, m.groups())
                    deadline = datetime(y, mo, d, tzinfo=timezone.utc)
                except Exception:
                    pass

        return {
            "description": "\n\n".join(desc_parts),
            "requirements": "\n\n".join(req_parts),
            "benefits": "\n\n".join(benefit_parts),
            "deadline_at": deadline,
        }

    def fetch_job_detail(
        self,
        source_job_id: str,
        detail_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Lấy nội dung chi tiết bài đăng qua HTTP"""
        try:
            resp = self.session.get(detail_url, timeout=8.0)
            if resp.status_code == 200:
                return self.parse_html_detail_page(resp.text, detail_url)
            return None
        except Exception as e:
            logger.warning(f"Lỗi khi lấy chi tiết CareerViet '{detail_url}': {e}")
            return None


# Thể hiện Singleton của Adapter
careerviet_adapter = CareerVietAdapter()
