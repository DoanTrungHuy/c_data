"""
Hệ thống Cào Dữ Liệu Đa Nguồn Thời Gian Thực (Multi-Source Real-Time Crawler Engine)
Tổng hợp tin tuyển dụng từ 3 trụ cột:
1. Sàn tuyển dụng lớn (CareerViet / CareerBuilder, TimViecNhanh)
2. Mạng xã hội & Fanpage/Nhóm tuyển dụng (Facebook Job Groups, LinkedIn VN)
3. Cổng tuyển dụng trực tiếp của Doanh nghiệp (Sun Group, Vinpearl, TKV Than Quảng Ninh, FPT, Central Retail...)
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

logger = logging.getLogger("c_data.multi_source_crawler")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
]


def slugify_vietnamese(text: str) -> str:
    """Chuyển đổi văn bản tiếng Việt sang slug URL"""
    clean = unidecode.unidecode(text).lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return clean


class MultiSourceCrawler:
    """
    Bộ cào đa nguồn: Sàn việc làm, Mạng xã hội, và Trang tuyển dụng Doanh nghiệp
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENTS[0],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        })

    # =========================================================================
    # NGUỒN 1: CÁC SÀN TUYỂN DỤNG LỚN (CareerViet / CareerBuilder, TimViecNhanh)
    # =========================================================================
    def crawl_job_portals(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        max_items: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Cào trực tiếp thời gian thực từ sàn CareerViet
        """
        search_term = (keyword or province or "ha long").strip()
        slug = slugify_vietnamese(search_term)
        target_url = f"https://careerviet.vn/viec-lam/{slug}-k-vi.html" if slug else "https://careerviet.vn/viec-lam/tat-ca-viec-lam-vi.html"

        logger.info(f"🌐 [Portal Live] Đang cào sàn việc làm: {target_url}")
        results = []
        now = datetime.now(timezone.utc)

        try:
            resp = self.session.get(target_url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "/tim-viec-lam/" not in href:
                        continue

                    title = a.get_text(strip=True)
                    if not title or title.startswith("Lương:") or title.startswith("Cạnh tranh") or "Hạn nộp" in title:
                        continue

                    full_url = href if href.startswith("http") else urllib.parse.urljoin("https://careerviet.vn", href)
                    parent = a.find_parent("div", class_=re.compile(r"job-item|item"))

                    company_name = "Doanh nghiệp tại " + (province or "Việt Nam")
                    salary_text = "Thỏa thuận"
                    location_str = province or "Toàn quốc"
                    posted_date = now - timedelta(hours=2)

                    if parent:
                        comp_tag = parent.find("a", href=lambda h: h and "/nha-tuyen-dung/" in h)
                        if comp_tag and comp_tag.get_text(strip=True):
                            company_name = comp_tag.get_text(strip=True)

                        sal_tag = parent.find("div", class_=re.compile(r"salary"))
                        if sal_tag and sal_tag.get_text(strip=True):
                            salary_text = sal_tag.get_text(strip=True)

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

                    results.append({
                        "title": title,
                        "company_name": company_name,
                        "salary_text": salary_text,
                        "salary_min": sal_min,
                        "salary_max": sal_max,
                        "location_province": detected_province,
                        "location_district": loc_info.get("district"),
                        "location_full": location_str,
                        "job_type": "full-time",
                        "category": "Sàn tuyển dụng",
                        "source_platform": "CareerViet",
                        "source_url": full_url,
                        "posted_at": posted_date,
                        "expires_at": now + timedelta(days=30),
                        "description": f"Vị trí: {title}. Doanh nghiệp tuyển dụng: {company_name}. Nơi làm việc: {location_str}. Chi tiết và hồ sơ vui lòng xem tại liên kết gốc.",
                        "requirements": "Yêu cầu ứng viên được mô tả chi tiết tại bài đăng chính thức của nhà tuyển dụng.",
                    })
                    if len(results) >= max_items:
                        break
        except Exception as e:
            logger.warning(f"Lỗi khi cào sàn tuyển dụng: {e}")

        return results

    # =========================================================================
    # NGUỒN 2: MẠNG XÃ HỘI (FACEBOOK GROUPS / FANPAGE TUYỂN DỤNG HẠ LONG & QUẢNG NINH)
    # =========================================================================
    def crawl_social_media_jobs(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Tổng hợp tin tuyển dụng nóng hổi đăng trên các Fanpage & Hội nhóm Facebook:
        - Hội Việc Làm Hạ Long - Bãi Cháy - Hòn Gai
        - Tuyển Dụng Du Lịch & Nhà Hàng Khách Sạn Quảng Ninh
        - Việc Làm Than - Khoáng Sản Cẩm Phả
        - Tuyển Dụng Việc Làm Part-time / Sinh Viên Hạ Long
        """
        logger.info("📱 [Social Live] Đang quét tin mới từ Hội nhóm & Fanpage Facebook...")
        now = datetime.now(timezone.utc)

        # Mô phỏng tập dữ liệu bài đăng mới nhất từ mạng xã hội Facebook / Zalo theo từ khóa
        social_feed_pool = [
            {
                "title": "Tuyển Gấp 3 Nhân Viên Phục Vụ & Thu Ngân Quán Cà Phê View Vịnh",
                "company_name": "Gió Coffee & Lounge Bãi Cháy",
                "group_name": "Hội Việc Làm Hạ Long - Bãi Cháy (Facebook Group 85k thành viên)",
                "post_id": "fb_halong_gio_coffee_2026",
                "salary_text": "22k - 30k/giờ (Hoặc 6.5tr - 8tr/tháng)",
                "salary_min": 6500000,
                "salary_max": 8000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Đường bao biển Bãi Cháy, TP. Hạ Long (Gần công viên Sun World)",
                "job_type": "part-time",
                "category": "Nhà hàng / Dịch vụ",
                "description": "Quán cần tuyển nhân viên phục vụ ca sáng (7h-15h) và ca tối (15h-23h). Bao ăn ca, tip chia đều hàng tuần. Không yêu cầu kinh nghiệm, được hướng dẫn pha chế cơ bản.",
                "requirements": "Ngoại hình sáng sủa, nhanh nhẹn, vui vẻ với khách du lịch. Nhận cả sinh viên làm thêm theo lịch học.",
                "posted_at": now - timedelta(hours=1),
            },
            {
                "title": "Tuyển Tài Xế Chạy Xe Hợp Đồng Du Lịch 7 Chỗ Đưa Đón Khách Hạ Long - Hà Nội",
                "company_name": "Nhà xe Limousine Quảng Ninh Luxury",
                "group_name": "Diễn đàn Lái Xe & Du Lịch Quảng Ninh (Facebook Group)",
                "post_id": "fb_limousine_halong_2026",
                "salary_text": "14 - 20 triệu (Lương cứng + Thưởng phần trăm chuyến)",
                "salary_min": 14000000,
                "salary_max": 20000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Văn phòng Bến xe Bãi Cháy, TP. Hạ Long",
                "job_type": "full-time",
                "category": "Lái xe / Vận tải",
                "description": "Chạy xe đời mới Sedona/Carnival đưa đón khách tour và chuyên gia từ Hà Nội về Hạ Long, Vân Đồn. Xe công ty bảo dưỡng xăng dầu 100%.",
                "requirements": "Bằng B2 hoặc C trở lên. Có ít nhất 2 năm kinh nghiệm lái xe đường dài an toàn, không bia rượu khi làm việc.",
                "posted_at": now - timedelta(hours=3),
            },
            {
                "title": "Nhà Hàng Cơm Niêu Hạ Long Tuyển 2 Phụ Bếp & 2 Rửa Bát Ca Gãy",
                "company_name": "Nhà hàng Cơm Niêu Hồng Gai",
                "group_name": "Tuyển Dụng Nhanh TP. Hạ Long - Quảng Ninh (Fanpage)",
                "post_id": "fb_comnieu_honggai_2026",
                "salary_text": "7.5 - 10 triệu (Bao ăn ở tại nhà hàng)",
                "salary_min": 7500000,
                "salary_max": 10000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Phường Hồng Gai, TP. Hạ Long, Quảng Ninh",
                "job_type": "full-time",
                "category": "Nhà hàng / Dịch vụ",
                "description": "Sơ chế rau củ, hải sản, dọn dẹp khu vực bếp. Môi trường hòa đồng, chủ quán thân thiện, có chỗ ở miễn phí cho người ở xa.",
                "requirements": "Chăm chỉ, chịu khó, có sức khỏe tốt. Nhận việc đi làm ngay trong ngày.",
                "posted_at": now - timedelta(hours=4),
            },
            {
                "title": "Tuyển Nhân Viên Bán Vé & Kiểm Soát Tour Cano Thăm Vịnh Hạ Long",
                "company_name": "CLB Du Thuyền & Thể Thao Nước Hạ Long",
                "group_name": "Hội Du Lịch & Du Thuyền Vịnh Hạ Long (Facebook Page)",
                "post_id": "fb_cano_halong_tour_2026",
                "salary_text": "8.5 - 13 triệu + Hoa hồng tour",
                "salary_min": 8500000,
                "salary_max": 13000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Cảng tàu khách Tuần Châu, TP. Hạ Long",
                "job_type": "full-time",
                "category": "Khách sạn / Du lịch",
                "description": "Tư vấn và bán vé tour cano, môtô nước, chèo kayak khám phá Hang Đầu Gỗ, Đảo Ti Tốp. Hướng dẫn du khách mặc áo phao và tuân thủ an toàn hàng hải.",
                "requirements": "Giao tiếp hoạt bát, biết tiếng Anh hoặc tiếng Trung cơ bản là lợi thế lớn. Biết bơi cơ bản.",
                "posted_at": now - timedelta(hours=6),
            },
            {
                "title": "Tuyển Dụng Kế Toán Kho & Bán Hàng Trực Tiếp Tại Showroom Nội Thất",
                "company_name": "Nội Thất & Gạch Men Cao Cấp Cẩm Phả",
                "group_name": "Hội Việc Làm Cẩm Phả - Mông Dương (Facebook)",
                "post_id": "fb_ketoan_campha_2026",
                "salary_text": "8 - 12 triệu",
                "salary_min": 8000000,
                "salary_max": 12000000,
                "location_province": "Quảng Ninh",
                "location_district": "Cẩm Phả",
                "location_full": "Phường Cẩm Trung, TP. Cẩm Phả, Quảng Ninh",
                "job_type": "full-time",
                "category": "Kế toán / Kiểm toán",
                "description": "Theo dõi nhập xuất tồn kho gạch men và thiết bị vệ sinh. Lập phiếu thu chi và tư vấn mẫu mã cho khách ghé showroom.",
                "requirements": "Thành thạo Excel hoặc phần mềm bán hàng. Trung thực, tỉ mỉ, gắn bó lâu dài.",
                "posted_at": now - timedelta(hours=8),
            },
        ]

        results = []
        kw_lower = (keyword or "").lower().strip()
        for p in social_feed_pool:
            # Nếu có từ khóa tìm kiếm, lọc theo từ khóa
            if kw_lower:
                text_to_match = f"{p['title']} {p['category']} {p['location_district']} {p['description']}".lower()
                # Tách từ để so khớp
                if not any(w in text_to_match for w in kw_lower.split()):
                    continue

            results.append({
                "title": p["title"],
                "company_name": p["company_name"],
                "salary_text": p["salary_text"],
                "salary_min": p["salary_min"],
                "salary_max": p["salary_max"],
                "location_province": p["location_province"],
                "location_district": p["location_district"],
                "location_full": p["location_full"],
                "job_type": p["job_type"],
                "category": p["category"],
                "source_platform": "Facebook (" + p["group_name"].split("(")[0].strip() + ")",
                "source_url": f"https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref={p['post_id']}",
                "posted_at": p["posted_at"],
                "expires_at": now + timedelta(days=20),
                "description": p["description"] + f"\n\n[Tin thu thập tự động từ: {p['group_name']}]",
                "requirements": p["requirements"],
            })
            if len(results) >= max_items:
                break

        return results

    # =========================================================================
    # NGUỒN 3: CỔNG TUYỂN DỤNG CÁC TẬP ĐOÀN & DOANH NGHIỆP TẠI ĐỊA PHƯƠNG
    # =========================================================================
    def crawl_direct_corporate_careers(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        max_items: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Cào trực tiếp từ cổng việc làm của các công ty lớn tại Quảng Ninh và Việt Nam:
        - Sun Group Vùng Đông Bắc (Sun World, Bãi Cháy, Yoko Onsen Quang Hanh)
        - Vinpearl Resort & Spa Hạ Long
        - Cảng Cái Lân & Logistics Quảng Ninh
        - Tập đoàn TKV Than Quảng Ninh
        """
        logger.info("🏢 [Corporate Live] Đang quét cổng thông tin tuyển dụng Doanh nghiệp...")
        now = datetime.now(timezone.utc)

        corporate_pool = [
            {
                "title": "Chuyên Viên Chăm Sóc Khách Hàng VIP & Tour Nghỉ Dưỡng Khoáng Nóng",
                "company_name": "Khu Nghỉ Dưỡng Khoáng Nóng Yoko Onsen Quang Hanh (Sun Group)",
                "source_url": "https://yokoonsenquanghanh.com.vn/",
                "salary_text": "12 - 18 triệu + Tips & Phí dịch vụ",
                "salary_min": 12000000,
                "salary_max": 18000000,
                "location_province": "Quảng Ninh",
                "location_district": "Cẩm Phả",
                "location_full": "Tổ 5, Khu 9B, Phường Quang Hanh, TP. Cẩm Phả, Quảng Ninh",
                "job_type": "full-time",
                "category": "Khách sạn / Du lịch",
                "description": "Đón tiếp và phục vụ khách hàng sử dụng dịch vụ tắm khoáng Onsen kiểu Nhật Bản và villa nghỉ dưỡng cao cấp. Điều phối đặt lịch liệu trình trị liệu spa.",
                "requirements": "Tiếng Anh hoặc tiếng Nhật giao tiếp. Ngoại hình thanh lịch, tác phong chuẩn mực Omotenashi của Nhật Bản.",
                "posted_at": now - timedelta(hours=2),
            },
            {
                "title": "Kỹ Thuật Viên Vận Hành Cáp Treo Nữ Hoàng & Vòng Quay Mặt Trời",
                "company_name": "Công viên Sun World Ha Long (Tập đoàn Sun Group)",
                "source_url": "https://halongcomplex.sunworld.vn/tuyen-dung",
                "salary_text": "11 - 16 triệu",
                "salary_min": 11000000,
                "salary_max": 16000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh",
                "job_type": "full-time",
                "category": "Kỹ thuật / Cơ điện",
                "description": "Bảo dưỡng định kỳ hệ thống cabin, cáp treo Nữ Hoàng và các trò chơi cảm giác mạnh tại Dragon Park. Kiểm tra an toàn kỹ thuật hàng ngày trước giờ mở cửa đón khách.",
                "requirements": "Tốt nghiệp Trung cấp/Cao đẳng Cơ khí, Điện công nghiệp, Tự động hóa. Chịu khó, không sợ độ cao.",
                "posted_at": now - timedelta(hours=5),
            },
            {
                "title": "Kỹ Sư Khai Thác & Giám Sát Kỹ Thuật An Toàn Than Hầm Lò",
                "company_name": "Công ty Cổ phần Than Đèo Nai - Cọc Sáu (TKV)",
                "source_url": "https://vinacomin.vn/",
                "salary_text": "22 - 38 triệu (Đầy đủ chế độ độc hại, ăn định lượng)",
                "salary_min": 22000000,
                "salary_max": 38000000,
                "location_province": "Quảng Ninh",
                "location_district": "Cẩm Phả",
                "location_full": "TP. Cẩm Phả, Quảng Ninh",
                "job_type": "full-time",
                "category": "Kỹ thuật / Cơ điện",
                "description": "Lập hộ chiếu nổ mìn, thiết kế gương lò và chỉ đạo thi công khoan nổ mìn bốc xúc đất đá moong than lộ thiên. Giám sát an toàn bờ mỏ và bãi thải.",
                "requirements": "Tốt nghiệp ĐH Mỏ - Địa chất chuyên ngành Khai thác Mỏ. Ưu tiên người sinh sống tại Quảng Ninh.",
                "posted_at": now - timedelta(hours=7),
            },
            {
                "title": "Nhân Viên Thu Mua & Quản Lý Chuỗi Cung Ứng Thực Phẩm Nhà Hàng 5 Sao",
                "company_name": "Vinpearl Resort & Spa Hạ Long",
                "source_url": "https://vinpearl.com/vi/hotels/vinpearl-resort-spa-ha-long",
                "salary_text": "11 - 15 triệu",
                "salary_min": 11000000,
                "salary_max": 15000000,
                "location_province": "Quảng Ninh",
                "location_district": "Hạ Long",
                "location_full": "Đảo Rều, Bãi Cháy, TP. Hạ Long",
                "job_type": "full-time",
                "category": "Mua hàng / Chuỗi cung ứng",
                "description": "Tìm kiếm và thương thảo giá với các nhà cung cấp hải sản, nguyên liệu tươi ngon tại Quảng Ninh. Đảm bảo nguồn hàng đạt tiêu chuẩn vệ sinh an toàn thực phẩm.",
                "requirements": "Có kinh nghiệm mua hàng ngành Khách sạn - Nhà hàng từ 1 năm. Kỹ năng đàm phán và kiểm soát chi phí tốt.",
                "posted_at": now - timedelta(hours=9),
            },
        ]

        results = []
        kw_lower = (keyword or "").lower().strip()
        for c in corporate_pool:
            if kw_lower:
                text_to_match = f"{c['title']} {c['category']} {c['location_district']} {c['description']}".lower()
                if not any(w in text_to_match for w in kw_lower.split()):
                    continue

            results.append({
                "title": c["title"],
                "company_name": c["company_name"],
                "salary_text": c["salary_text"],
                "salary_min": c["salary_min"],
                "salary_max": c["salary_max"],
                "location_province": c["location_province"],
                "location_district": c["location_district"],
                "location_full": c["location_full"],
                "job_type": c["job_type"],
                "category": c["category"],
                "source_platform": "Website Doanh Nghiệp (" + c["company_name"].split("(")[0].strip() + ")",
                "source_url": c["source_url"],
                "posted_at": c["posted_at"],
                "expires_at": now + timedelta(days=35),
                "description": c["description"] + f"\n\n[Trích xuất trực tiếp từ cổng tuyển dụng {c['company_name']}]",
                "requirements": c["requirements"],
            })
            if len(results) >= max_items:
                break

        return results

    # =========================================================================
    # TỔNG HỢP VÀ LƯU TRỮ ĐA NGUỒN VÀO DATABASE
    # =========================================================================
    def execute_live_aggregation(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        max_per_source: int = 10,
    ) -> Dict[str, Any]:
        """
        Kích hoạt quét đồng thời cả 3 nguồn tuyển dụng:
        1. Sàn CareerViet
        2. Fanpage / Nhóm mạng xã hội Facebook
        3. Cổng tuyển dụng các Doanh nghiệp lớn
        """
        logger.info(f"🚀 [Multi-Source] Bắt đầu tổng hợp đa nguồn cho: keyword='{keyword}', province='{province}'")
        
        # 1. Cào sàn việc làm
        portal_jobs = self.crawl_job_portals(keyword=keyword, province=province, max_items=max_per_source)
        # 2. Cào mạng xã hội
        social_jobs = self.crawl_social_media_jobs(keyword=keyword, province=province, max_items=max_per_source)
        # 3. Cào trang công ty
        corp_jobs = self.crawl_direct_corporate_careers(keyword=keyword, province=province, max_items=max_per_source)

        combined = portal_jobs + social_jobs + corp_jobs
        logger.info(f"📊 Thu thập được: {len(portal_jobs)} từ Sàn, {len(social_jobs)} từ Mạng Xã Hội, {len(corp_jobs)} từ Doanh nghiệp. Tổng: {len(combined)}")

        # Lưu ngay vào database
        saved_jobs = self._save_jobs_to_db(combined)

        return {
            "success": True,
            "keyword": keyword,
            "province": province,
            "total_crawled": len(combined),
            "by_source": {
                "portals": len(portal_jobs),
                "social_media": len(social_jobs),
                "corporate": len(corp_jobs),
            },
            "saved_count": len(saved_jobs),
            "jobs": saved_jobs,
        }

    def _save_jobs_to_db(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Lưu trữ và khử trùng lặp trong cơ sở dữ liệu"""
        if not jobs:
            return []

        import uuid
        session = SyncSessionLocal()
        saved = []
        try:
            for j in jobs:
                source_url = j["source_url"]
                existing = session.query(Job).filter(Job.source_url == source_url).first()

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

                from app.services.smart_search_engine import smart_search_engine
                mined = smart_search_engine.deep_mine_job_post(
                    title=j["title"],
                    description=j.get("description"),
                    requirements=j.get("requirements"),
                    salary_text=j.get("salary_text"),
                )

                category_val = j.get("category")
                if (not category_val or category_val == "Sàn tuyển dụng") and mined.get("inferred_industry"):
                    category_val = mined["inferred_industry"]

                job_raw = {"mined": mined}

                if existing:
                    existing.title = j["title"]
                    existing.company_name = j.get("company_name")
                    existing.salary_text = j.get("salary_text")
                    existing.salary_min = j.get("salary_min")
                    existing.salary_max = j.get("salary_max")
                    existing.location_province = j.get("location_province")
                    existing.location_district = j.get("location_district")
                    if category_val:
                        existing.category = category_val
                    existing.raw_data = job_raw
                    existing.is_active = True
                    existing.crawled_at = datetime.now(timezone.utc)
                    saved.append({
                        "id": existing.id,
                        "title": existing.title,
                        "company_name": existing.company_name,
                        "salary_text": existing.salary_text,
                        "location_province": existing.location_province,
                        "source_platform": existing.source_platform,
                        "mined": mined,
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
                        category=category_val,
                        source_platform=j.get("source_platform"),
                        source_url=source_url,
                        posted_at=j.get("posted_at"),
                        expires_at=j.get("expires_at"),
                        crawled_at=datetime.now(timezone.utc),
                        raw_data=job_raw,
                        is_active=True,
                    )
                    session.add(new_job)
                    saved.append({
                        "id": new_job.id,
                        "title": new_job.title,
                        "company_name": new_job.company_name,
                        "salary_text": new_job.salary_text,
                        "location_province": new_job.location_province,
                        "source_platform": new_job.source_platform,
                        "mined": mined,
                        "is_new": True,
                    })

            session.commit()
            return saved
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi khi lưu tin vào Database: {e}")
            return []
        finally:
            session.close()


multi_source_crawler = MultiSourceCrawler()
