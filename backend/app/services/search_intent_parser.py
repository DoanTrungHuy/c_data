"""
Hệ thống Phân tích Ý định Tìm kiếm Thông minh (Search Intent Parser)
Chuyển đổi truy vấn ngôn ngữ tự nhiên (tiếng Việt & tiếng Anh) thành cấu trúc SearchIntent rõ ràng,
phân biệt các ràng buộc cứng (hard constraints), sở thích mềm (soft preferences), điều kiện loại trừ
và từ đồng nghĩa chuyên môn.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import unidecode


@dataclass
class SearchIntent:
    raw_query: str
    normalized_query: str
    
    # Nghề nghiệp & Nhóm vai trò
    primary_role: Optional[str] = None
    role_family: List[str] = field(default_factory=list)
    role_synonyms: List[str] = field(default_factory=list)
    
    # Kỹ năng
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    
    # Địa điểm & Khu vực tương đương
    target_province: Optional[str] = None
    target_district: Optional[str] = None
    location_aliases: List[str] = field(default_factory=list)
    
    # Cấp bậc / Kinh nghiệm
    seniority: str = "any"  # 'intern', 'fresher', 'junior', 'middle', 'senior', 'lead', 'any'
    max_experience_years: Optional[int] = None
    
    # Môi trường làm việc & Tính chất công việc
    work_environment: str = "any"  # 'office', 'remote', 'hybrid', 'field', 'any'
    workplace_type: Optional[str] = None  # 'remote', 'hybrid', 'onsite'
    is_remote_required: bool = False
    is_office_preferred: bool = False
    travel_preference: str = "any"  # 'avoid_travel', 'allow_travel', 'any'
    field_work_preference: str = "any"  # 'avoid_field_work', 'avoid_heights', 'any'
    
    # Lương & Độ tươi mới
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    max_posting_age_days: Optional[int] = None  # Ví dụ: 7 ngày nếu yêu cầu 'mới đăng trong 7 ngày'

    # Doanh nghiệp & Xác thực
    target_company: Optional[str] = None
    verified_only: bool = False
    exact_phrases: List[str] = field(default_factory=list)
    
    # Ngôn ngữ & Yêu cầu khác
    language_requirements: List[str] = field(default_factory=list)
    
    # Điều kiện loại trừ rõ ràng (Explicit Exclusions)
    negative_constraints: List[str] = field(default_factory=list)
    
    # Ràng buộc cứng và sở thích mềm
    hard_constraints: Dict[str, Any] = field(default_factory=dict)
    soft_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Các biến thể truy vấn mở rộng có trọng tâm (Focused Search Queries)
    expanded_queries: List[str] = field(default_factory=list)



def normalize_text(text: Optional[str]) -> str:
    """Chuẩn hóa văn bản sang chữ thường không dấu, bảo vệ từ khóa kỹ thuật."""
    if not text:
        return ""
    s = str(text).strip()
    s = re.sub(r"(?i)\bc#\b", "csharp", s)
    s = re.sub(r"(?i)\bc\+\+\b", "cpp", s)
    s = re.sub(r"(?i)\.net\b", "dotnet", s)
    clean = unidecode.unidecode(s).lower()
    clean = re.sub(r"[^\w\s]", " ", clean)
    return re.sub(r"\s+", " ", clean).strip()


# Bản đồ địa danh địa phương và các khu vực vệ tinh liên quan
LOCATION_DATABASE: Dict[str, Dict[str, Any]] = {
    "quang ninh": {
        "province": "Quảng Ninh",
        "districts": ["Hạ Long", "Cẩm Phả", "Uông Bí", "Móng Cái", "Vân Đồn", "Đông Triều", "Quảng Yên"],
        "aliases": [
            "quang ninh", "ha long", "bai chay", "hon gai", "tuan chau",
            "cam pha", "uong bi", "van don", "mong cai", "dong trieu",
            "quang yen", "cai dam", "gieng day", "ha lam", "cao thang",
        ],
    },
    "ha noi": {
        "province": "Hà Nội",
        "districts": ["Cầu Giấy", "Nam Từ Liêm", "Bắc Từ Liêm", "Đống Đa", "Thanh Xuân", "Ba Đình", "Hoàn Kiếm", "Hai Bà Trưng", "Hoàng Mai", "Long Biên", "Hà Đông"],
        "aliases": ["ha noi", "cau giay", "my dinh", "thanh xuan", "dong da", "nam tu liem", "bac tu liem"],
    },
    "ho chi minh": {
        "province": "Hồ Chí Minh",
        "districts": ["Quận 1", "Quận 3", "Quận 7", "Bình Thạnh", "Tân Bình", "Thủ Đức", "Phú Nhuận"],
        "aliases": ["ho chi minh", "hcm", "sai gon", "thu duc", "quan 1", "quan 7"],
    },
    "da nang": {
        "province": "Đà Nẵng",
        "districts": ["Hải Châu", "Thanh Khê", "Sơn Trà", "Ngũ Hành Sơn", "Liên Chiểu"],
        "aliases": ["da nang", "hai chau", "son tra", "ngu hanh son"],
    },
    "hai phong": {
        "province": "Hải Phòng",
        "districts": ["Hồng Bàng", "Ngô Quyền", "Lê Chân", "Hải An", "Thủy Nguyên"],
        "aliases": ["hai phong", "thuy nguyen", "dinh vu"],
    },
}

# Bản đồ các nhóm nghề nghiệp IT và nghề nghiệp chuyên môn
ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "it_support_helpdesk": {
        "canonical": "IT Support / Helpdesk / IT Officer",
        "triggers": [
            "it", "cntt", "cong nghe thong tin", "information technology",
            "it support", "it helpdesk", "it officer", "it executive", "it jobs", "junior it",
            "ho tro ky thuat", "nhan vien it", "chuyen vien it", "it van phong", "it degree",
            "it khach san", "sua may tinh", "ky thuat may tinh", "cai dat may",
            "desktop support", "technical support", "it operations", "it admin",
        ],
        "synonyms": [
            "IT Support", "IT Helpdesk", "IT Officer", "Chuyên viên CNTT",
            "Chuyên viên IT", "Nhân viên IT", "Kỹ sư IT", "Hỗ trợ kỹ thuật",
            "Quản trị mạng & IT Helpdesk", "IT Executive", "Desktop Support",
            "Technical Support", "IT Khách Sạn",
        ],
        "environment_default": "office",
    },
    "system_network_admin": {
        "canonical": "Quản trị hệ thống & Mạng",
        "triggers": [
            "quan tri he thong", "quan tri mang", "system admin", "network engineer",
            "network support", "ha tang mang", "cisco", "router switch",
        ],
        "synonyms": [
            "Quản trị hệ thống", "Quản trị mạng", "System Administrator", "Network Support",
            "Kỹ sư mạng", "IT Infrastructure",
        ],
        "environment_default": "office",
    },
    "software_backend": {
        "canonical": "Kỹ sư Backend / Lập trình viên phần mềm",
        "triggers": [
            "backend", "lap trinh vien backend", "python developer", "java developer",
            "nodejs", "golang", "csharp", "dotnet", "lap trinh vien java",
            "software engineer", "ky su phan mem", "software developer", "backend developer",
            "software development",
        ],
        "synonyms": [
            "Lập trình viên Backend", "Backend Developer", "Java Developer",
            "Python Developer", "Kỹ sư phần mềm", "Software Engineer",
        ],
        "environment_default": "office",
    },
    "software_frontend": {
        "canonical": "Kỹ sư Frontend / Web Developer",
        "triggers": [
            "frontend", "react", "nextjs", "vue", "angular", "web developer",
            "lap trinh frontend", "ui developer",
        ],
        "synonyms": [
            "Lập trình viên Frontend", "Frontend Developer", "React Developer", "Web Developer",
        ],
        "environment_default": "office",
    },
    "telecom_technician": {
        "canonical": "Kỹ thuật viên viễn thông & Triển khai mạng ngoài",
        "triggers": [
            "keo cap", "lap dat internet", "ky thuat vien vien thong", "lap dat mang ngoai",
            "lap dat camera", "leo cot", "ngoai troi", "cong trinh vien thong",
        ],
        "synonyms": [
            "Kỹ thuật viên viễn thông", "Kỹ thuật viên kéo cáp", "Lắp đặt camera & mạng",
        ],
        "environment_default": "field",
    },
    "hotel_hospitality": {
        "canonical": "Du lịch / Khách sạn / Lễ tân",
        "triggers": [
            "khach san", "resort", "le tan", "front desk", "buong phong",
            "tour guide", "huong dan vien", "du thuyen", "cruise",
        ],
        "synonyms": [
            "Lễ tân khách sạn", "Nhân viên khách sạn", "Front Desk Officer",
            "Hướng dẫn viên du lịch", "Nhân viên du thuyền",
        ],
        "environment_default": "office",
    },
    "accounting": {
        "canonical": "Kế toán / Kiểm toán / Thuế",
        "triggers": [
            "ke toan", "ke toan tong hop", "ke toan kho", "ke toan noi bo", "kiem toan", "thue",
        ],
        "synonyms": [
            "Kế toán tổng hợp", "Kế toán nội bộ", "Kế toán kho", "Chuyên viên kế toán",
        ],
        "environment_default": "office",
    },
    "driver_transport": {
        "canonical": "Lái xe / Vận tải / Logistics",
        "triggers": [
            "lai xe", "tai xe", "driver", "bang b2", "bang c", "bang d", "limousine", "xe hop dong",
        ],
        "synonyms": [
            "Lái xe du lịch", "Tài xế B2", "Lái xe hợp đồng", "Tài xế đưa đón",
        ],
        "environment_default": "field",
    },
    "doctor_medical": {
        "canonical": "Y tế / Bác sĩ / Dược sĩ",
        "triggers": [
            "bac si", "doctor", "y ta", "dieu duong", "duoc si", "phong kham", "nha thuoc",
        ],
        "synonyms": [
            "Bác sĩ đa khoa", "Bác sĩ nội khoa", "Điều dưỡng", "Dược sĩ tư vấn",
        ],
        "environment_default": "office",
    },
    "mining_coal": {
        "canonical": "Than khoáng sản / Khai thác mỏ",
        "triggers": [
            "than", "tkv", "vinacomin", "ham lo", "tho lo", "mo than", "khai thac mo", "dia chat mo",
        ],
        "synonyms": [
            "Kỹ sư khai thác mỏ", "Thợ lò khai thác than", "Kỹ thuật viên mỏ TKV",
        ],
        "environment_default": "field",
    },
    "sales_business": {
        "canonical": "Kinh doanh / Bán hàng / CSKH",
        "triggers": [
            "ban hang", "kinh doanh", "sales", "nhan vien kinh doanh", "cskh", "telesales", "showroom",
        ],
        "synonyms": [
            "Nhân viên kinh doanh", "Nhân viên bán hàng", "Chuyên viên phát triển thị trường",
        ],
        "environment_default": "office",
    },
}


class SearchIntentParser:
    """
    Bộ bóc tách ý định chuyên sâu và hiểu ngữ nghĩa câu lệnh tuyển dụng
    """

    def parse(self, raw_query: str) -> SearchIntent:
        query_str = (raw_query or "").strip()
        norm_q = normalize_text(query_str)

        intent = SearchIntent(
            raw_query=query_str,
            normalized_query=norm_q,
        )

        if not query_str:
            return intent

        # 1. Phát hiện các cụm từ trong ngoặc kép và cú pháp đặc biệt (Quoted phrases & negation -term)
        self._extract_syntax_and_quotes(query_str, norm_q, intent)

        # 2. Phát hiện các phủ định & loại trừ rõ ràng (Explicit Exclusions)
        self._extract_exclusions(query_str, norm_q, intent)

        # 3. Phát hiện doanh nghiệp / công ty mục tiêu
        self._extract_company(query_str, norm_q, intent)

        # 4. Phát hiện yêu cầu tin đã xác minh (Verified only)
        self._extract_verified_intent(query_str, norm_q, intent)

        # 5. Phát hiện địa điểm & các alias địa phương
        self._extract_location(query_str, norm_q, intent)

        # 6. Phát hiện cấp bậc & kinh nghiệm (Seniority)
        self._extract_seniority(query_str, norm_q, intent)

        # 7. Phát hiện môi trường làm việc & sở thích di chuyển (Office / Remote / Travel / Field / Hybrid)
        self._extract_work_environment(query_str, norm_q, intent)

        # 8. Phát hiện độ tươi mới bài đăng (Recency / Max age days)
        self._extract_recency(query_str, norm_q, intent)

        # 9. Phát hiện vai trò nghề nghiệp chính và gia đình ngành (Role Family & Taxonomy)
        self._extract_role_and_skills(query_str, norm_q, intent)

        # 10. Phát hiện yêu cầu ngôn ngữ
        self._extract_languages(query_str, norm_q, intent)

        # 11. Phát hiện khoảng lương nếu có
        self._extract_salary(query_str, norm_q, intent)

        # 12. Thiết lập Ràng buộc cứng (Hard Constraints) và Sở thích mềm (Soft Preferences)
        self._compile_constraints(intent)

        # 13. Tạo các truy vấn mở rộng có trọng tâm (Focused Search Queries)
        self._generate_focused_queries(intent)

        return intent

    def parse_query(
        self,
        query: Optional[str] = None,
        province: Optional[str] = None,
        strict_mode: bool = False,
    ) -> SearchIntent:
        """
        Tiện ích phân tích ý định kèm tham số ngữ cảnh từ bộ lọc UI.
        """
        intent = self.parse(query or "")
        if province:
            p_clean = province.strip()
            intent.target_province = p_clean
            if p_clean not in intent.location_aliases:
                intent.location_aliases.insert(0, p_clean)
        if strict_mode:
            intent.hard_constraints["strict_mode"] = True
        return intent

    def _extract_syntax_and_quotes(self, raw: str, norm: str, intent: SearchIntent):
        """Trích xuất các cụm từ đặt trong dấu ngoặc kép '"..."' và các từ khóa loại trừ '-keyword'"""
        # Cụm từ trong ngoặc kép
        quoted = re.findall(r'["\']([^"\']+)["\']', raw)
        for q in quoted:
            clean_q = q.strip()
            if clean_q:
                intent.exact_phrases.append(clean_q)

        # Cú pháp loại trừ bắt đầu bằng dấu trừ: -senior, -hybrid, -kinhdoanh
        neg_matches = re.findall(r'(?:^|\s)-([a-zA-Z0-9_\u00C0-\u1EF9]+)', raw)
        for neg in neg_matches:
            clean_neg = normalize_text(neg)
            if clean_neg and clean_neg not in intent.negative_constraints:
                intent.negative_constraints.append(clean_neg)

    def _extract_verified_intent(self, raw: str, norm: str, intent: SearchIntent):
        """Phát hiện yêu cầu chỉ tìm các tin tuyển dụng đã xác minh"""
        verified_terms = [
            "da xac minh", "xac minh", "tin xac thuc", "da kiem chung", "verified",
            "active confirmed", "con tuyen", "dang tuyen thuc te", "khong lay tin het han",
        ]
        if any(term in norm for term in verified_terms):
            intent.verified_only = True

    def _extract_company(self, raw: str, norm: str, intent: SearchIntent):
        """Phát hiện tên công ty / doanh nghiệp tuyển dụng từ câu truy vấn"""
        company_patterns = [
            r"(?:tai|o|cho|cong ty|tap doan|doanh nghiep)\s+([a-zA-Z0-9\s]+?)(?:tai|o|can|tuyen|moi|luong|$)",
        ]
        known_companies = [
            ("vinpearl", "Vinpearl"),
            ("sun group", "Sun Group"),
            ("sun world", "Sun World"),
            ("fpt", "FPT"),
            ("viettel", "Viettel"),
            ("vnpt", "VNPT"),
            ("vingroup", "Vingroup"),
            ("vinfast", "VinFast"),
            ("techcombank", "Techcombank"),
            ("vietcombank", "Vietcombank"),
            ("muong thanh", "Mường Thanh"),
            ("bim group", "BIM Group"),
        ]
        for key, canonical in known_companies:
            if re.search(rf"\b{re.escape(key)}\b", norm):
                intent.target_company = canonical
                return

    def _extract_exclusions(self, raw: str, norm: str, intent: SearchIntent):
        """
        Bóc tách các mệnh đề phủ định / cấm kỵ:
        'không lắp đặt trên cao', 'hạn chế đi công tác', 'tránh đi xa', 'without frequent travel'
        """
        negation_patterns = [
            r"(?:khong|chua|dung|tranh|han che|khong thich|khong yeu cau|without|no|avoid)\s+([a-z0-9\s]+?)(?:,|;|\.|\bvaf\b|\bnhung\b|\bprefer\b|\bshow\b|$)",
            r"hạn chế\s+([a-z0-9\s]+?)(?:,|;|\.|$)",
            r"không\s+([a-z0-9\s]+?)(?:,|;|\.|$)",
        ]

        exclusions = list(intent.negative_constraints)
        for pat in negation_patterns:
            matches = re.findall(pat, norm)
            for m in matches:
                clause = m.strip()
                if not clause:
                    continue
                # Kiểm tra các điều kiện cụ thể
                if any(k in clause for k in ["lap dat tren cao", "leo cot", "tren cao", "tower climbing", "installation"]):
                    exclusions.append("lắp đặt trên cao / leo cột")
                    intent.field_work_preference = "avoid_heights"
                if any(k in clause for k in ["di cong tac", "cong tac xa", "travel", "frequent travel"]):
                    exclusions.append("đi công tác thường xuyên")
                    intent.travel_preference = "avoid_travel"
                if any(k in clause for k in ["kinh nghiem", "nhieu kinh nghiem", "experience"]):
                    intent.seniority = "junior"

        intent.negative_constraints = list(dict.fromkeys(exclusions))

    def _extract_location(self, raw: str, norm: str, intent: SearchIntent):
        """
        Nhận diện địa điểm và bổ sung các alias địa lý lân cận:
        'Hạ Long' -> Bãi Cháy, Hòn Gai, Tuần Châu, Cẩm Phả, Quảng Ninh
        """
        # Kiểm tra Hạ Long / Quảng Ninh
        if any(w in norm for w in ["ha long", "bai chay", "hon gai", "tuan chau", "quang ninh"]):
            intent.target_province = "Quảng Ninh"
            intent.target_district = "Hạ Long" if ("ha long" in norm or "bai chay" in norm or "hon gai" in norm or "tuan chau" in norm) else None
            intent.location_aliases = [
                "Hạ Long", "Quảng Ninh", "Bãi Cháy", "Hòn Gai", "Tuần Châu", "Cẩm Phả",
            ]
            return

        # Kiểm tra các tỉnh thành khác trong taxonomy
        for loc_key, loc_info in LOCATION_DATABASE.items():
            if any(alias in norm for alias in loc_info["aliases"]):
                intent.target_province = loc_info["province"]
                intent.location_aliases = [loc_info["province"]] + loc_info["districts"][:4]
                return

    def _extract_seniority(self, raw: str, norm: str, intent: SearchIntent):
        """Nhận diện cấp bậc tuyển dụng: intern, fresher, junior, middle, senior, lead"""
        if any(w in norm for w in [
            "thuc tap", "thuc tap sinh", "intern", "internship", "hoc viec", "tap su"
        ]):
            intent.seniority = "intern"
            intent.max_experience_years = 0
        elif any(w in norm for w in [
            "moi ra truong", "nguoi moi ra truong", "fresher", "sinh vien", "chua co kinh nghiem",
            "khong yeu cau kinh nghiem", "khong can kinh nghiem", "entry level", "entry-level"
        ]):
            intent.seniority = "fresher"
            intent.max_experience_years = 1
        elif any(w in norm for w in ["junior", "1 nam kinh nghiem", "it kinh nghiem", "it software"]):
            if intent.seniority == "any":
                intent.seniority = "junior"
                intent.max_experience_years = 2
        elif any(w in norm for w in ["middle", "mid level", "mid-level", "2 nam kinh nghiem", "3 nam kinh nghiem"]):
            if intent.seniority == "any":
                intent.seniority = "middle"
                intent.max_experience_years = 3
        elif any(w in norm for w in [
            "senior", "lau nam", "chuyen gia", "lead", "truong nhom", "quan ly", "truong phong", "giam doc", "architect"
        ]):
            intent.seniority = "senior"

    def _extract_work_environment(self, raw: str, norm: str, intent: SearchIntent):
        """Nhận diện mong muốn môi trường làm việc: văn phòng, remote, hybrid, onsite"""
        if any(w in norm for w in ["remote 100%", "remote", "tu xa", "lam tai nha", "work from home", "wfh", "100% remote"]):
            intent.work_environment = "remote"
            intent.workplace_type = "remote"
            intent.is_remote_required = True
        elif any(w in norm for w in ["hybrid", "ban thoi gian van phong", "linh hoat", "ket hop"]):
            intent.work_environment = "hybrid"
            intent.workplace_type = "hybrid"
        elif any(w in norm for w in ["onsite", "tai cho", "truc tiep", "van phong", "office", "office-based", "toa nha", "ngoi phong"]):
            intent.work_environment = "office"
            if any(w in norm for w in ["onsite", "tai cho", "truc tiep"]):
                intent.workplace_type = "onsite"
            intent.is_office_preferred = True

        if any(w in norm for w in ["han che di cong tac", "khong di cong tac", "without frequent travel", "no travel"]):
            intent.travel_preference = "avoid_travel"

        if any(w in norm for w in ["khong lap dat tren cao", "khong tren cao", "tower climbing", "tren cao"]):
            intent.field_work_preference = "avoid_heights"
        elif any(w in norm for w in ["khong lap dat", "khong treo", "khong cong trinh"]):
            intent.field_work_preference = "avoid_field_work"


    def _extract_recency(self, raw: str, norm: str, intent: SearchIntent):
        """Bóc tách điều kiện thời gian đăng bài: 'mới đăng trong 7 ngày', '24h', 'recent'"""
        # Pattern: mới đăng trong X ngày / X tuần / 24 giờ
        day_match = re.search(r"(?:moi dang|dang trong|gan day|recent|within)\s+(\d+)\s*(?:ngay|day|days)", norm)
        if day_match:
            intent.max_posting_age_days = int(day_match.group(1))
        elif "24h" in norm or "trong ngay" in norm:
            intent.max_posting_age_days = 1
        elif "7 ngay" in norm or "1 tuan" in norm:
            intent.max_posting_age_days = 7
        elif "30 ngay" in norm or "1 thang" in norm:
            intent.max_posting_age_days = 30
        elif "moi dang" in norm or "recent" in norm:
            intent.max_posting_age_days = 14

    def _extract_role_and_skills(self, raw: str, norm: str, intent: SearchIntent):
        """Bóc tách nghề nghiệp chính và kỹ năng liên quan"""
        # Kiểm tra kỹ năng lập trình / công nghệ cụ thể
        tech_skills = {
            "java": "Java",
            "spring": "Spring Boot",
            "python": "Python",
            "fastapi": "FastAPI",
            "django": "Django",
            "react": "React",
            "nextjs": "Next.js",
            "flutter": "Flutter",
            "csharp": "C#",
            "dotnet": ".NET",
            "php": "PHP",
            "nodejs": "Node.js",
            "sql": "SQL",
            "pms": "Hệ thống PMS Khách sạn",
            "opera": "Opera PMS",
            "smile": "Smile PMS",
            "wifi": "Mạng WiFi / LAN",
            "cisco": "Cisco",
            "camera": "Hệ thống Camera",
        }

        for k, v in tech_skills.items():
            if re.search(rf"\b{re.escape(k)}\b", norm):
                intent.required_skills.append(v)

        # Đối sánh vai trò nghề nghiệp
        best_role_key = None
        best_score = 0

        for r_key, r_info in ROLE_TAXONOMY.items():
            score = 0
            for trg in r_info["triggers"]:
                norm_trg = normalize_text(trg)
                word_count = len(norm_trg.split())
                if re.search(rf"\b{re.escape(norm_trg)}\b", norm):
                    score += 5 * word_count
                elif len(norm_trg) > 2 and norm_trg in norm:
                    score += 2 * word_count

            if score > best_score:
                best_score = score
                best_role_key = r_key

        if best_role_key:
            r_info = ROLE_TAXONOMY[best_role_key]
            intent.primary_role = r_info["canonical"]
            intent.role_family = [r_info["canonical"]]
            intent.role_synonyms = r_info["synonyms"]
            if intent.work_environment == "any":
                intent.work_environment = r_info.get("environment_default", "any")
        else:
            # Fallback nếu không khớp danh mục có sẵn:
            # Loại bỏ các từ địa danh và hư từ để không nhầm địa bàn thành chức danh
            clean_role = norm
            for loc in intent.location_aliases:
                clean_role = re.sub(rf"\b{re.escape(normalize_text(loc))}\b", "", clean_role)
            for stop in ["tuyen", "can", "gap", "viec", "lam", "tim", "o", "tai"]:
                clean_role = re.sub(rf"\b{stop}\b", "", clean_role)
            clean_role = re.sub(r"\s+", " ", clean_role).strip()
            if clean_role:
                intent.role_family = [clean_role]
                intent.role_synonyms = [clean_role]
            else:
                intent.role_family = []
                intent.role_synonyms = []

    def _extract_languages(self, raw: str, norm: str, intent: SearchIntent):
        """Nhận diện yêu cầu ngoại ngữ: tiếng Anh, tiếng Trung, tiếng Nhật"""
        if any(w in norm for w in ["tieng anh", "english", "basic english", "tieng anh co ban"]):
            intent.language_requirements.append("Tiếng Anh cơ bản")
        if any(w in norm for w in ["tieng trung", "chinese"]):
            intent.language_requirements.append("Tiếng Trung")
        if any(w in norm for w in ["tieng nhat", "japanese"]):
            intent.language_requirements.append("Tiếng Nhật")

    def _extract_salary(self, raw: str, norm: str, intent: SearchIntent):
        """Bóc tách mức lương nếu có: 'lương trên 15 triệu', '10 - 20tr'"""
        sal_match = re.search(r"(\d+)\s*(?:-|den|to)\s*(\d+)\s*(?:trieu|tr|m)", norm)
        if sal_match:
            intent.min_salary = int(sal_match.group(1)) * 1000000
            intent.max_salary = int(sal_match.group(2)) * 1000000
            return

        min_match = re.search(r"(?:tren|tu|it nhat|min)\s*(\d+)\s*(?:trieu|tr|m)", norm)
        if min_match:
            intent.min_salary = int(min_match.group(1)) * 1000000

    def _compile_constraints(self, intent: SearchIntent):
        """Phân loại rõ ràng Ràng buộc cứng (Hard) và Sở thích mềm (Soft)"""
        # 1. Ràng buộc cứng:
        # - Vị trí Remote (nếu bắt buộc)
        # - Tỉnh thành yêu cầu (nếu người dùng chỉ định rõ)
        # - Tuổi đăng bài (nếu người dùng yêu cầu 'mới đăng trong X ngày')
        if intent.is_remote_required:
            intent.hard_constraints["work_type"] = "remote"

        if intent.workplace_type:
            intent.hard_constraints["workplace_type"] = intent.workplace_type

        if intent.target_province and not intent.is_remote_required:
            intent.hard_constraints["location_province"] = intent.target_province

        if intent.target_district and not intent.is_remote_required:
            intent.hard_constraints["location_district"] = intent.target_district

        if intent.seniority and intent.seniority != "any":
            intent.hard_constraints["seniority"] = intent.seniority

        if intent.verified_only:
            intent.hard_constraints["verified_only"] = True

        if intent.target_company:
            intent.hard_constraints["company_name"] = intent.target_company

        if intent.exact_phrases:
            intent.hard_constraints["exact_phrases"] = intent.exact_phrases

        if intent.max_posting_age_days:
            intent.hard_constraints["max_posting_age_days"] = intent.max_posting_age_days


        # 2. Sở thích mềm:
        # - Môi trường làm việc văn phòng (ưu tiên nhưng không loại bỏ nếu thiếu thông tin)
        # - Cấp bậc junior / fresher (thưởng điểm cao cho junior, phạt điểm senior)
        # - Tránh leo cột / đi công tác xa
        # - Tiếng Anh cơ bản
        if intent.is_office_preferred:
            intent.soft_preferences["office_preferred"] = True
        if intent.travel_preference == "avoid_travel":
            intent.soft_preferences["avoid_travel"] = True
        if intent.field_work_preference != "any":
            intent.soft_preferences["field_work"] = intent.field_work_preference
        if intent.seniority in ["fresher", "junior"]:
            intent.soft_preferences["prefer_entry_level"] = True

    def _generate_focused_queries(self, intent: SearchIntent):
        """Tạo các biến thể từ khóa tìm kiếm tập trung để quét đa nguồn song song"""
        queries = []
        loc = intent.target_district or intent.target_province or ""

        # 1. Nếu có role synonyms
        if intent.role_synonyms:
            for syn in intent.role_synonyms[:5]:
                if loc:
                    queries.append(f"{syn} {loc}".strip())
                else:
                    queries.append(syn)
        elif len(intent.raw_query) <= 40:
            queries.append(intent.raw_query)
        elif intent.primary_role:
            queries.append(f"{intent.primary_role} {loc}".strip())

        # 2. Thêm biến thể kết hợp kỹ năng (nếu có kỹ năng cụ thể như Java)
        if intent.required_skills:
            for skill in intent.required_skills:
                queries.append(f"{skill} {loc}".strip())

        # 3. Biến thể tiếng Anh/tiếng Việt nếu là IT
        if intent.primary_role and "IT" in intent.primary_role:
            queries.extend([f"IT {loc}".strip(), f"CNTT {loc}".strip(), f"IT Helpdesk {loc}".strip()])

        intent.expanded_queries = list(dict.fromkeys([q for q in queries if q]))[:8]


search_intent_parser = SearchIntentParser()
