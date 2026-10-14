"""
Service cào dữ liệu thời gian thực (Real-time Live Crawler).
Cho phép người dùng kích hoạt cào trực tiếp từ các cổng tuyển dụng
(CareerViet / CareerBuilder, TimViecNhanh) ngay khi tìm kiếm.
"""

from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any, Dict, List, Optional
import urllib.parse
from bs4 import BeautifulSoup
import requests
import unidecode

from app.core.database import SyncSessionLocal
from app.models.company import Company
from app.models.job import Job
from crawlers.utils import extract_salary_range, normalize_location

logger = logging.getLogger("c_data.live_crawler")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
]


def slugify_vietnamese(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành slug URL không dấu"""
    clean = unidecode.unidecode(text).lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return clean


class LiveCrawlerService:
    """
    Dịch vụ cào trực tiếp tin tuyển dụng thời gian thực
    """

    def crawl_careerviet_live(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        max_items: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Quét trực tiếp từ CareerViet (CareerBuilder VN) theo từ khóa hoặc tỉnh thành
        """
        headers = {
            "User-Agent": USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        # Xác định URL tìm kiếm
        search_term = (keyword or province or "ha long").strip()
        slug = slugify_vietnamese(search_term)

        if slug:
            target_url = f"https://careerviet.vn/viec-lam/{slug}-k-vi.html"
        else:
            target_url = "https://careerviet.vn/viec-lam/tat-ca-viec-lam-vi.html"

        logger.info(f"⚡ [Live Crawler] Bắt đầu cào trực tiếp từ: {target_url}")

        try:
            resp = requests.get(target_url, headers=headers, timeout=12)
            if resp.status_code != 200:
                logger.warning(f"CareerViet trả về mã lỗi HTTP {resp.status_code}")
                return []
        except Exception as e:
            logger.error(f"Lỗi kết nối tới CareerViet: {e}")
            return []

        soup = BeautifulSoup(resp.content, "html.parser")
        raw_items: List[Dict[str, Any]] = []

        now = datetime.now(timezone.utc)

        # Trích xuất các liên kết tin tuyển dụng hợp lệ
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/tim-viec-lam/" not in href:
                continue

            title = a.get_text(strip=True)
            if not title or title.startswith("Lương:") or title.startswith("Cạnh tranh") or "Hạn nộp" in title:
                continue

            full_url = href if href.startswith("http") else urllib.parse.urljoin("https://careerviet.vn", href)

            # Tìm thẻ cha chứa toàn bộ thông tin tin tuyển dụng
            parent = a.find_parent("div", class_=re.compile(r"job-item|item"))
            company_name = "Doanh nghiệp tại " + (province or "Việt Nam")
            salary_text = "Thỏa thuận"
            location_str = province or "Toàn quốc"
            posted_date = now - timedelta(hours=2)

            if parent:
                # Tên công ty
                comp_tag = parent.find("a", href=lambda h: h and "/nha-tuyen-dung/" in h)
                if comp_tag and comp_tag.get_text(strip=True):
                    company_name = comp_tag.get_text(strip=True)

                # Lương
                sal_tag = parent.find("div", class_=re.compile(r"salary"))
                if sal_tag and sal_tag.get_text(strip=True):
                    salary_text = sal_tag.get_text(strip=True)

                # Địa điểm
                loc_tag = parent.find("div", class_=re.compile(r"location"))
                if loc_tag:
                    location_str = loc_tag.get_text(separator=", ", strip=True)

                # Ngày cập nhật
                parent_text = parent.get_text(separator=" ", strip=True)
                date_match = re.search(r"Cập nhật[:\s]*(\d{1,2})[-/](\d{1,2})[-/](\d{4})", parent_text)
                if date_match:
                    try:
                        d, m, y = map(int, date_match.groups())
                        posted_date = datetime(y, m, d, tzinfo=timezone.utc)
                    except Exception:
                        pass

            sal_min, sal_max = extract_salary_range(salary_text)
            loc_info = normalize_location(location_str)
            detected_province = loc_info.get("province")

            if not detected_province:
                loc_lower = location_str.lower()
                if "quảng ninh" in loc_lower or "hạ long" in loc_lower or "cẩm phả" in loc_lower or "uông bí" in loc_lower or "vân đồn" in loc_lower:
                    detected_province = "Quảng Ninh"
                elif "hà nội" in loc_lower:
                    detected_province = "Hà Nội"
                elif "hồ chí minh" in loc_lower:
                    detected_province = "TP. Hồ Chí Minh"
                elif "đà nẵng" in loc_lower:
                    detected_province = "Đà Nẵng"
                else:
                    detected_province = province or "Toàn quốc"

            if company_name.startswith("Doanh nghiệp tại"):
                company_name = f"Doanh nghiệp tại {detected_province}"

            raw_items.append({
                "title": title,
                "company_name": company_name,
                "salary_text": salary_text,
                "salary_min": sal_min,
                "salary_max": sal_max,
                "location_province": detected_province,
                "location_district": loc_info.get("district"),
                "location_full": location_str,
                "job_type": "full-time",
                "category": "Việc làm mới cào realtime",
                "source_platform": "CareerViet (Real-time)",
                "source_url": full_url,
                "posted_at": posted_date,
                "expires_at": now + timedelta(days=30),
                "description": f"Vị trí: {title}. Doanh nghiệp tuyển dụng: {company_name}. Địa điểm làm việc: {location_str}. Chi tiết nộp hồ sơ vui lòng xem trực tiếp tại liên kết nguồn.",
                "requirements": "Yêu cầu chi tiết và tiêu chuẩn ứng viên được mô tả đầy đủ trên bài đăng gốc.",
            })

            if len(raw_items) >= max_items * 2:
                break

        # Khử trùng lặp theo source_url
        seen_urls = set()
        unique_items = []
        for it in raw_items:
            if it["source_url"] not in seen_urls:
                seen_urls.add(it["source_url"])
                unique_items.append(it)
                if len(unique_items) >= max_items:
                    break

        logger.info(f"⚡ [Live Crawler] Đã trích xuất thành công {len(unique_items)} tin mới từ CareerViet")
        return unique_items

    def save_live_jobs_sync(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Lưu ngay các tin tuyển dụng vừa cào thời gian thực vào cơ sở dữ liệu
        """
        if not jobs:
            return []

        session = SyncSessionLocal()
        saved_jobs = []
        try:
            for j in jobs:
                source_url = j["source_url"]
                existing = session.query(Job).filter(Job.source_url == source_url).first()

                # Kiểm tra hoặc tạo công ty
                comp_name = j.get("company_name", "").strip()
                company_id = None
                if comp_name:
                    existing_comp = session.query(Company).filter(Company.name == comp_name).first()
                    if not existing_comp:
                        new_comp = Company(
                            id=str(uuid.uuid4()),
                            name=comp_name,
                            province=j.get("location_province"),
                        )
                        session.add(new_comp)
                        session.flush()
                        company_id = new_comp.id
                    else:
                        company_id = existing_comp.id

                if existing:
                    # Cập nhật thông tin mới nhất
                    existing.title = j["title"]
                    existing.company_name = j.get("company_name")
                    existing.salary_text = j.get("salary_text")
                    existing.salary_min = j.get("salary_min")
                    existing.salary_max = j.get("salary_max")
                    existing.location_province = j.get("location_province")
                    existing.location_district = j.get("location_district")
                    existing.is_active = True
                    existing.crawled_at = datetime.now(timezone.utc)
                    saved_jobs.append({
                        "id": existing.id,
                        "title": existing.title,
                        "company_name": existing.company_name,
                        "salary_text": existing.salary_text,
                        "location_province": existing.location_province,
                        "is_new": False,
                    })
                else:
                    new_job = Job(
                        id=str(uuid.uuid4()),
                        title=j["title"],
                        company_name=j.get("company_name"),
                        company_id=company_id,
                        description=j.get("description"),
                        requirements=j.get("requirements"),
                        salary_min=j.get("salary_min"),
                        salary_max=j.get("salary_max"),
                        salary_text=j.get("salary_text"),
                        location_province=j.get("location_province"),
                        location_district=j.get("location_district"),
                        location_full=j.get("location_full"),
                        job_type=j.get("job_type", "full-time"),
                        category=j.get("category"),
                        source_platform=j.get("source_platform", "CareerViet (Real-time)"),
                        source_url=source_url,
                        posted_at=j.get("posted_at"),
                        expires_at=j.get("expires_at"),
                        crawled_at=datetime.now(timezone.utc),
                        is_active=True,
                    )
                    session.add(new_job)
                    saved_jobs.append({
                        "id": new_job.id,
                        "title": new_job.title,
                        "company_name": new_job.company_name,
                        "salary_text": new_job.salary_text,
                        "location_province": new_job.location_province,
                        "is_new": True,
                    })

            session.commit()
            logger.info(f"⚡ [Live Crawler] Đã lưu {len(saved_jobs)} tin cào realtime vào Database.")
            return saved_jobs
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi khi lưu tin cào realtime: {e}")
            return []
        finally:
            session.close()


live_crawler_service = LiveCrawlerService()
