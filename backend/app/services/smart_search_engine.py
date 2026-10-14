"""
Hệ thống Phân tích Sâu & Suy luận Từ Khóa Ngành nghề Thông Minh (Smart Search & Deep Text Mining Engine)
Chuyên dụng cho thị trường việc làm Việt Nam và đặc thù địa phương (Hạ Long, Quảng Ninh, Hà Nội, TP.HCM...)

Tính năng cốt lõi:
1. Mò từ khóa chuyên sâu vào toàn bộ nội dung bài viết (tiêu đề, mô tả, yêu cầu, quyền lợi, liên hệ).
2. Tự động suy luận ngành nghề liên quan & từ đồng nghĩa ngữ nghĩa (Semantic Industry & Skill Expansion).
3. Phân biệt từ viết tắt ngắn (IT, AI, QA, QC, HSE...) tránh nhầm lẫn với từ tiếng Việt thông thường (ít nhất, ai đó...).
4. Trích xuất thông tin ẩn trong bài viết Facebook/Mạng xã hội: số điện thoại, zalo, ca làm việc, bao ăn ở.
5. Chấm điểm độ phù hợp (Relevance Scoring) kết hợp độ tươi mới của tin (Recency Boosting).
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import unidecode


# =============================================================================
# TỪ ĐIỂN TRI THỨC NGÀNH NGHỀ & TỪ KHÓA LIÊN QUAN CHUYÊN SÂU (VIETNAMESE JOB TAXONOMY)
# =============================================================================
INDUSTRY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "hotel_tourism": {
        "canonical_name": "Du lịch / Khách sạn / Nghỉ dưỡng",
        "display_name": "Du lịch & Khách sạn",
        "triggers": [
            "du lich", "khach san", "resort", "hotel", "homestay", "villa", "nha nghi",
            "le tan", "front desk", "buong phong", "housekeeping", "bellman", "doorman",
            "huong dan vien", "hdv", "tour", "lu hanh", "cano", "du thuyen", "cruise",
            "tau du lich", "tham vinh", "yoko onsen", "ve tham quan", "cap treo",
            "dat phong", "booking tour", "dieu hanh tour",
        ],
        "related_keywords": [
            "Lễ tân khách sạn", "Nhân viên buồng phòng", "Hướng dẫn viên du lịch",
            "Phục vụ nhà hàng resort", "Lái cano / Thuyền viên", "Bán vé tour vịnh Hạ Long",
            "Quản trị khách sạn", "Bellman đón khách", "Chăm sóc khách hàng VIP",
        ],
        "occupations": [
            "lễ tân", "buồng phòng", "hướng dẫn viên", "bellman", "thuyền trưởng",
            "thủy thủ", "cano", "tour guide", "đặt phòng", "reservation",
        ],
    },
    "restaurant_fb": {
        "canonical_name": "Nhà hàng / Dịch vụ ăn uống / F&B",
        "display_name": "Nhà hàng & F&B",
        "triggers": [
            "nha hang", "quan an", "quan ca phe", "cafe", "coffee", "tra sua", "lounge",
            "bar", "pub", "phuc vu", "chay ban", "boi ban", "order", "thu ngan", "cashier",
            "pha che", "barista", "bartender", "phu bep", "dau bep", "bep truong", "bep chinh",
            "rua bat", "tap vu", "hai san", "com nieu", "nuong", "lau", "am thuc", "buffet",
        ],
        "related_keywords": [
            "Nhân viên phục vụ bàn", "Nhân viên pha chế / Barista", "Phụ bếp / Sơ chế hải sản",
            "Thu ngân ca gãy", "Tạp vụ / Rửa bát", "Bếp chính món Việt / Hải sản",
            "Quản lý nhà hàng", "Chạy bàn ca tối",
        ],
        "occupations": [
            "phục vụ", "chạy bàn", "bồi bàn", "pha chế", "barista", "phụ bếp",
            "đầu bếp", "thu ngân", "tạp vụ", "rửa bát", "bếp trưởng",
        ],
    },
    "transport_driver": {
        "canonical_name": "Vận tải / Lái xe / Giao nhận / Logistics",
        "display_name": "Lái xe & Vận tải",
        "triggers": [
            "lai xe", "tai xe", "driver", "bang b2", "bang c", "bang d", "bang e", "bang fc",
            "limousine", "xe khach", "xe tai", "xe con", "xe hop dong", "xe 7 cho", "xe 16 cho",
            "xe 29 cho", "xe 45 cho", "dua don", "giao hang", "shipper", "giao van", "phu xe",
            "kho van", "logistics", "cang cai lan", "container", "ben xe", "van tai",
        ],
        "related_keywords": [
            "Tài xế lái xe B2", "Lái xe tải bằng C", "Tài xế Limousine đưa đón",
            "Nhân viên giao hàng / Shipper", "Phụ xe tuyến cố định", "Điều phối vận tải",
            "Lái xe du lịch Hạ Long", "Nhân viên kho vận",
        ],
        "occupations": [
            "lái xe", "tài xế", "shipper", "giao hàng", "phụ xe", "điều xe",
            "thủ kho", "bốc xếp",
        ],
    },
    "banking_finance": {
        "canonical_name": "Ngân hàng / Tài chính / Giao dịch viên",
        "display_name": "Ngân hàng & Tài chính",
        "triggers": [
            "giao dich vien", "ngan hang", "tin dung", "teller", "chuyen vien khach hang",
            "giao dich quay", "kiem soat vien", "tham dinh", "huy dong von", "quay giao dich",
            "vietcombank", "bidv", "techcombank", "mb bank", "vpbank", "agribank", "hdbank", "tpbank",
            "sacombank", "vib", "msb", "tin dung ca nhan", "tin dung doanh nghiep",
        ],
        "related_keywords": [
            "Giao dịch viên ngân hàng", "Chuyên viên quản lý khách hàng cá nhân",
            "Chuyên viên thẩm định tín dụng", "Kiểm soát viên giao dịch quầy",
            "Tư vấn tài chính - bảo hiểm",
        ],
        "occupations": [
            "giao dịch viên", "chuyên viên tín dụng", "giao dịch quầy", "teller",
            "kiểm soát viên", "chuyên viên khách hàng",
        ],
    },
    "accounting_finance": {
        "canonical_name": "Kế toán / Kiểm toán / Thuế / Tài chính",
        "display_name": "Kế toán & Thuế",
        "triggers": [
            "ke toan", "kiem toan", "thue", "bao cao tai chinh", "bctc", "ke toan kho",
            "thu kho", "ke toan noi bo", "ke toan tong hop", "thu ngan", "chung tu",
            "hoa don", "quyet toan", "misa", "bravo", "excel", "tien luong", "c_and_b",
        ],
        "related_keywords": [
            "Kế toán tổng hợp", "Kế toán nội bộ", "Kế toán thuế & Báo cáo tài chính",
            "Kế toán kho & Bán hàng", "Thủ quỹ / Thu ngân", "Kiểm toán viên",
        ],
        "occupations": [
            "kế toán", "kiểm toán", "thủ kho", "thủ quỹ", "chuyên viên thuế",
        ],
    },
    "sales_marketing": {
        "canonical_name": "Kinh doanh / Bán hàng / Marketing / CSKH",
        "display_name": "Bán hàng & Kinh doanh",
        "triggers": [
            "ban hang", "kinh doanh", "sale", "sales", "telesale", "telesales", "tu van",
            "cham soc khach hang", "cskh", "showroom", "cua hang", "shop", "bat dong san",
            "bds", "moi gioi", "chot don", "truc page", "truc hotline", "marketing",
            "truyen thong", "quang cao", "seo", "content", "tiktok ads", "facebook ads",
        ],
        "related_keywords": [
            "Nhân viên kinh doanh B2B", "Nhân viên bán hàng Showroom", "Tư vấn bất động sản Hạ Long",
            "Telesales / Trực hotline", "Chuyên viên Digital Marketing", "Nhân viên trực page chốt đơn",
        ],
        "occupations": [
            "nhân viên kinh doanh", "bán hàng", "tư vấn", "telesales", "cskh",
            "marketing", "content", "chuyên viên sale",
        ],
    },
    "mining_industrial": {
        "canonical_name": "Công nghiệp / Than - Khoáng sản / Cơ điện",
        "display_name": "Công nghiệp & Than Khoáng sản",
        "triggers": [
            "than", "khoang san", "tkv", "vinacomin", "ham lo", "mo than", "lo thien",
            "than coc sau", "than deo nai", "than ha tu", "than nui beo", "mo quang hanh",
            "tho lo", "khai thac mo", "dia chat mo", "khoan no min", "co khi mo", "tho han",
            "tho dien", "bao tri may moc", "van hanh may", "xuc lat", "may dao", "dien cong nghiep",
            "tu dong hoa", "cong nhan mo", "cong nhan lo",
        ],
        "related_keywords": [
            "Kỹ sư khai thác mỏ hầm lò", "Thợ lò / Công nhân than TKV", "Thợ cơ khí sửa chữa",
            "Thợ hàn kết cấu", "Thợ điện công nghiệp", "Vận hành máy xúc lật",
            "Giám sát an toàn mỏ", "Bảo trì thiết bị nhà xưởng",
        ],
        "occupations": [
            "thợ lò", "thợ cơ khí", "thợ hàn", "thợ điện", "kỹ sư mỏ",
            "vận hành máy", "công nhân mỏ",
        ],
    },
    "construction_engineering": {
        "canonical_name": "Xây dựng / Kỹ thuật / An toàn lao động",
        "display_name": "Xây dựng & Kỹ thuật",
        "triggers": [
            "xay dung", "giam sat xay dung", "an toan lao dong", "hse", "ky su xay dung",
            "chi huy truong", "cong trinh", "kien truc", "du toan", "khao sat dia chat",
            "thi cong", "ket cau", "qs", "qa qc xay dung",
        ],
        "related_keywords": [
            "Chuyên viên an toàn lao động (HSE)", "Kỹ sư giám sát xây dựng",
            "Chỉ huy trưởng công trình", "Kỹ sư QS dự toán xây dựng",
            "Giám sát thi công hoàn thiện",
        ],
        "occupations": [
            "chuyên viên an toàn lao động", "giám sát xây dựng", "kỹ sư xây dựng", "hse",
            "kỹ sư công trình", "chỉ huy trưởng",
        ],
    },
    "it_software": {
        "canonical_name": "Công nghệ thông tin / Phần mềm / IT",
        "display_name": "Công nghệ thông tin",
        "triggers": [
            "it", "cntt", "lap trinh", "developer", "coder", "software", "frontend",
            "backend", "fullstack", "react", "vue", "angular", "node", "nodejs",
            "python", "java", "php", "csharp", "cpp", "dotnet", "mobile", "flutter",
            "react native", "tester", "kiem thu", "qa", "qc", "devops", "system admin",
            "quan tri mang", "sua may tinh", "ky thuat mang", "it helpdesk", "it officer",
            "it support", "ky thuat may tinh", "an ninh mang", "tri tue nhan tao", "ai expert",
        ],
        "related_keywords": [
            "Lập trình viên Frontend React", "Lập trình viên Backend Python/Node",
            "Kỹ sư phần mềm Fullstack", "Tester / Kiểm thử phần mềm",
            "Quản trị mạng & IT Helpdesk", "IT Officer Khách sạn", "DevOps Engineer",
        ],
        "occupations": [
            "lập trình viên", "kỹ sư phần mềm", "tester", "it helpdesk", "it officer",
            "it support", "devops", "quản trị hệ thống", "chuyên viên cntt",
        ],
    },
    "spa_beauty_health": {
        "canonical_name": "Làm đẹp / Spa / Y tế / Sức khỏe",
        "display_name": "Spa & Chăm sóc sức khỏe",
        "triggers": [
            "spa", "massage", "khoang nong", "onsen", "tri lieu", "cham soc da",
            "tham my", "cat toc", "nail", "goi dau", "duong sinh", "duoc si",
            "nha thuoc", "dieu duong", "y ta", "bac si", "phong kham", "nha khoa",
        ],
        "related_keywords": [
            "Kỹ thuật viên Spa trị liệu", "Kỹ thuật viên Onsen khoáng nóng",
            "Dược sĩ đứng quầy nhà thuốc", "Điều dưỡng phòng khám",
            "Thợ làm móng Nail & Mi", "Nhân viên gội đầu dưỡng sinh",
        ],
        "occupations": [
            "kỹ thuật viên spa", "dược sĩ", "điều dưỡng", "y tá", "bác sĩ",
            "thợ nail", "chuyên viên trị liệu",
        ],
    },
    "parttime_student": {
        "canonical_name": "Lao động phổ thông / Part-time / Sinh viên",
        "display_name": "Part-time & Sinh viên",
        "triggers": [
            "lao dong pho thong", "ldpt", "part-time", "parttime", "ban thoi gian",
            "thoi vu", "ca gay", "ca sang", "ca toi", "lam them", "sinh vien",
            "khong yeu cau kinh nghiem", "khong can kinh nghiem", "dao tao tu dau",
            "nhan viec ngay", "bao an o", "dong goi", "boc vac", "phu kho",
        ],
        "related_keywords": [
            "Việc làm Part-time sinh viên", "Chạy bàn ca gãy bao ăn",
            "Lao động phổ thông nhận việc ngay", "Đóng gói bốc xếp tại kho",
            "Nhân viên phục vụ không cần kinh nghiệm", "Việc làm thời vụ theo ca",
        ],
        "occupations": [
            "phục vụ part-time", "lao động phổ thông", "nhân viên thời vụ",
            "phụ kho", "đóng gói",
        ],
    },
}


def normalize_str(text: Optional[str]) -> str:
    """
    Chuẩn hóa văn bản tiếng Việt sang dạng không dấu, viết thường.
    Bảo toàn các từ khóa kỹ thuật quan trọng như c#, c++, .net, c&b trước khi lọc dấu.
    """
    if not text:
        return ""
    s = str(text)
    # Chuyển đổi các từ khóa lập trình đặc thù trước khi unidecode làm mất ký tự
    s = re.sub(r"(?i)\bc#\b", "csharp", s)
    s = re.sub(r"(?i)\bc\+\+\b", "cpp", s)
    s = re.sub(r"(?i)\.net\b", "dotnet", s)
    s = re.sub(r"(?i)\bc&b\b", "c_and_b", s)

    clean = unidecode.unidecode(s).lower().strip()
    clean = re.sub(r"[^\w\s]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def is_keyword_matched(trigger: str, text: str, raw_text: Optional[str] = None) -> bool:
    """
    Kiểm tra đối sánh từ khóa/trigger chính xác, ngăn chặn hoàn toàn việc nhầm lẫn:
    - Tránh bắt nhầm chữ cái đơn hoặc chuỗi con ngẫu nhiên trong từ tiếng Việt.
    - Với từ ngắn (<= 3 ký tự như 'it', 'ai', 'qa', 'qc', 'hse'): bắt buộc dùng ranh giới từ \b.
    - Riêng 'it': kiểm tra raw_text để phân biệt chữ 'IT' viết hoa với chữ 'ít' ('ít nhất', 'ít kinh nghiệm').
    - Riêng 'ai': kiểm tra raw_text để phân biệt chữ 'AI' viết hoa với chữ 'ai' ('ai cũng có thể').
    """
    if not trigger or not text:
        return False
    norm_trg = normalize_str(trigger)
    norm_text = normalize_str(text)
    if not norm_trg or not norm_text:
        return False

    raw = raw_text or text

    if norm_trg == "it":
        # 1. Nếu raw_text có chữ IT viết hoa hoặc I.T
        if re.search(r"\b(IT|I\.T)\b", raw):
            return True
        # 2. Hoặc xuất hiện trong cụm từ IT rõ ràng
        if re.search(r"\b(nhan vien it|chuyen vien it|it officer|it helpdesk|it support|it admin|phong it|it manager|it engineer|it lead|cntt|cong nghe thong tin)\b", norm_text):
            return True
        return False

    if norm_trg == "ai":
        if re.search(r"\bAI\b", raw):
            return True
        if "tri tue nhan tao" in norm_text or "ai engineer" in norm_text or "ai expert" in norm_text:
            return True
        return False

    if norm_trg in ["qa", "qc", "hse", "qs", "b2", "tkv", "hdv"]:
        pattern = rf"\b{re.escape(norm_trg)}\b"
        return bool(re.search(pattern, norm_text))

    # Với các từ bình thường: kiểm tra ranh giới từ
    pattern = rf"\b{re.escape(norm_trg)}\b"
    if re.search(pattern, norm_text):
        return True

    # Nếu trigger là một cụm từ dài (>= 4 ký tự) và text chứa cụm từ đó
    if len(norm_trg) >= 4 and norm_trg in norm_text:
        return True

    return False


class SmartSearchEngine:
    """
    Hệ thống phân tích truy vấn và suy luận nội dung bài viết việc làm
    """

    def expand_query(self, query_str: Optional[str]) -> Dict[str, Any]:
        """
        Phân tích từ khóa tìm kiếm của người dùng và mở rộng ngữ nghĩa sang các ngành nghề,
        vị trí và từ khóa liên quan.
        """
        raw_query = (query_str or "").strip()
        if not raw_query:
            return {
                "raw_query": "",
                "clean_tokens": [],
                "matched_industries": [],
                "expanded_terms": [],
                "related_suggestions": [
                    "Việc làm Hạ Long", "Khách sạn / Resort", "Lái xe B2 / Vận tải",
                    "Phục vụ nhà hàng F&B", "Kế toán tổng hợp", "Than khoáng sản TKV",
                    "Kinh doanh / Bán hàng", "Part-time sinh viên",
                ],
            }

        norm_q = normalize_str(raw_query)
        q_tokens = [t for t in norm_q.split() if len(t) > 0]

        matched_industries: List[Dict[str, Any]] = []
        expanded_terms_set: Set[str] = set()
        suggestions: List[str] = []

        # Thêm các token gốc vào danh sách mở rộng
        for t in q_tokens:
            expanded_terms_set.add(t)
        expanded_terms_set.add(norm_q)

        # Duyệt qua bảng tri thức ngành nghề
        for key, ind in INDUSTRY_TAXONOMY.items():
            triggers = ind["triggers"]
            is_matched = False

            for trg in triggers:
                if is_keyword_matched(trg, raw_query, raw_query):
                    is_matched = True
                    break
                norm_trg = normalize_str(trg)
                if len(norm_trg) >= 4 and (norm_trg in norm_q or norm_q in norm_trg):
                    is_matched = True
                    break

            if is_matched:
                matched_industries.append({
                    "id": key,
                    "canonical_name": ind["canonical_name"],
                    "display_name": ind["display_name"],
                })
                suggestions.extend(ind["related_keywords"][:4])
                for occ in ind["occupations"]:
                    expanded_terms_set.add(normalize_str(occ))
                for trg in ind["triggers"][:6]:
                    expanded_terms_set.add(normalize_str(trg))

        if not suggestions:
            suggestions = [
                f"{raw_query} tại Hạ Long",
                f"{raw_query} Quảng Ninh",
                f"{raw_query} lương cao",
                f"{raw_query} không cần kinh nghiệm",
            ]

        unique_suggestions: List[str] = []
        for s in suggestions:
            if s not in unique_suggestions:
                unique_suggestions.append(s)

        return {
            "raw_query": raw_query,
            "clean_tokens": q_tokens,
            "matched_industries": [m["canonical_name"] for m in matched_industries],
            "expanded_terms": list(expanded_terms_set),
            "related_suggestions": unique_suggestions[:6],
        }

    def deep_mine_job_post(
        self,
        title: str,
        description: Optional[str] = None,
        requirements: Optional[str] = None,
        salary_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Mò sâu vào toàn bộ nội dung bài viết để trích xuất:
        - Số điện thoại / Zalo liên hệ
        - Thời gian / Ca làm việc (ca sáng, ca tối, ca gãy, part-time)
        - Quyền lợi ẩn (bao ăn ở, tip, hoa hồng)
        - Danh mục ngành nghề tự động suy luận
        - Các hashtag / nhãn kỹ năng nổi bật
        """
        full_text = f"{title}\n{description or ''}\n{requirements or ''}\n{salary_text or ''}"
        norm_full = normalize_str(full_text)

        # 1. Trích xuất số điện thoại / Hotline / Zalo
        phone_patterns = [
            r"(?:0|\+84)(?:3|5|7|8|9)\d{8}",
            r"(?:0|\+84)\d{2}[-.\s]\d{3}[-.\s]\d{4}",
            r"(?:zalo|sdt|hotline|lh|lien he|alo)[\s:]*([0-9.\s-]{10,13})",
        ]
        found_phones = set()
        for pat in phone_patterns:
            matches = re.findall(pat, full_text, flags=re.IGNORECASE)
            for m in matches:
                digits = re.sub(r"\D", "", m if isinstance(m, str) else m[0])
                if len(digits) >= 10:
                    found_phones.add(digits)

        # 2. Phát hiện ca làm việc & hình thức
        shifts = []
        if any(w in norm_full for w in ["ca gay", "ca split"]):
            shifts.append("Ca gãy")
        if any(w in norm_full for w in ["ca sang", "sang 7h", "sang 8h"]):
            shifts.append("Ca sáng")
        if any(w in norm_full for w in ["ca toi", "ca dem", "toi 18h", "toi 17h"]):
            shifts.append("Ca tối")
        if any(w in norm_full for w in ["part time", "parttime", "ban thoi gian", "theo gio"]):
            shifts.append("Bán thời gian (Part-time)")
        if any(w in norm_full for w in ["xoay ca", "doi ca"]):
            shifts.append("Xoay ca linh hoạt")

        # 3. Phát hiện quyền lợi & ưu đãi hấp dẫn
        benefits = []
        if any(w in norm_full for w in ["bao an o", "ho tro an o", "co cho o"]):
            benefits.append("Bao ăn ở miễn phí")
        elif any(w in norm_full for w in ["bao an ca", "ho tro an trua", "an toi"]):
            benefits.append("Bao ăn theo ca")

        if any(w in norm_full for w in ["tip", "tien boa", "thuong tip"]):
            benefits.append("Có tiền tip / Phí dịch vụ")
        if any(w in norm_full for w in ["hoa hong", "chiet khau", "phan tram"]):
            benefits.append("Hoa hồng cao theo doanh số")
        if any(w in norm_full for w in ["khong yeu cau kinh nghiem", "khong can kinh nghiem", "dao tao tu dau"]):
            benefits.append("Không yêu cầu kinh nghiệm")
        if any(w in norm_full for w in ["sinh vien", "nhan sinh vien"]):
            benefits.append("Nhận sinh viên làm thêm")

        # 4. Tự động suy luận ngành nghề phù hợp nhất (Auto Category Inference)
        best_industry = None
        highest_score = 0
        inferred_tags = []

        for key, ind in INDUSTRY_TAXONOMY.items():
            score = 0
            for trigger in ind["triggers"]:
                # Nếu trigger nằm trong tiêu đề: điểm cực cao (+10 điểm)
                if is_keyword_matched(trigger, title, title):
                    score += 10
                    inferred_tags.append(trigger)
                # Nếu trigger nằm trong mô tả (+2 điểm)
                elif is_keyword_matched(trigger, full_text, full_text):
                    score += 2

            if score > highest_score and score >= 2:
                highest_score = score
                best_industry = ind["canonical_name"]

        clean_tags = list(dict.fromkeys(inferred_tags))[:5]

        return {
            "phones": list(found_phones),
            "shifts": shifts,
            "benefits": benefits,
            "inferred_industry": best_industry,
            "mined_tags": clean_tags,
        }

    def score_job_relevance(
        self,
        job: Any,
        raw_query: str,
        expanded_terms: List[str],
        matched_industries: List[str],
    ) -> float:
        """
        Tính điểm liên quan của một công việc với truy vấn người dùng:
        - Đảm bảo tính khắt khe: Nếu một bài viết KHÔNG CÓ bất kỳ từ khóa nào của truy vấn
          trong Tiêu đề, Tên công ty hoặc Mô tả, điểm sẽ là 0.0 (loại bỏ hoàn toàn).
        - Khớp từ khóa trong tiêu đề: +60 điểm
        - Khớp từ khóa trong tên công ty: +30 điểm
        - Khớp từ khóa trong mô tả: +20 điểm
        - Khớp từ khóa mở rộng kỹ năng trong tiêu đề: +25 điểm
        - Khớp ngành nghề suy luận: +15 điểm
        - Thưởng độ tươi mới (recency boost): +5 đến +20 điểm
        """
        raw_title = getattr(job, "title", "") or ""
        norm_title = normalize_str(raw_title)
        raw_desc = getattr(job, "description", "") or ""
        norm_desc = normalize_str(raw_desc)
        raw_comp = getattr(job, "company_name", "") or ""
        norm_comp = normalize_str(raw_comp)
        norm_cat = normalize_str(getattr(job, "category", "") or "")
        norm_q = normalize_str(raw_query)

        has_query_match = False
        score = 0.0

        # 1. Khớp từ khóa tìm kiếm trực tiếp trong tiêu đề
        if is_keyword_matched(raw_query, raw_title, raw_title):
            score += 60.0
            has_query_match = True
        elif len(norm_q) >= 4 and norm_q in norm_title:
            score += 50.0
            has_query_match = True

        # Khớp cụm tìm kiếm trong tên công ty
        if is_keyword_matched(raw_query, raw_comp, raw_comp):
            score += 30.0
            has_query_match = True
        elif len(norm_q) >= 4 and norm_q in norm_comp:
            score += 25.0
            has_query_match = True

        # Khớp trong mô tả / yêu cầu
        if is_keyword_matched(raw_query, raw_desc, raw_desc):
            score += 20.0
            has_query_match = True
        elif len(norm_q) >= 4 and norm_q in norm_desc:
            score += 15.0
            has_query_match = True

        # 2. Khớp các từ khóa mở rộng kỹ năng / chuyên môn
        expanded_hits = 0
        for term in expanded_terms:
            if not term or len(term) < 2:
                continue
            if is_keyword_matched(term, raw_title, raw_title):
                score += 25.0
                expanded_hits += 1
                has_query_match = True
            elif is_keyword_matched(term, raw_desc, raw_desc):
                score += 8.0
                expanded_hits += 1
                if expanded_hits >= 2:
                    has_query_match = True

        # 3. Khớp ngành nghề được hệ thống suy luận
        matched_category = False
        for ind in matched_industries:
            norm_ind = normalize_str(ind)
            if norm_ind and (norm_ind in norm_cat or norm_cat in norm_ind):
                matched_category = True
                score += 15.0
                break

        # NGUYÊN TẮC BẢO ĐẢM ĐỘ CHÍNH XÁC (Strict Relevance Gate):
        # Nếu không có bất kỳ từ khóa chuyên môn hay truy vấn nào khớp trong tiêu đề/công ty/mô tả,
        # loại bỏ hoàn toàn (score = 0.0)
        if not has_query_match:
            return 0.0

        # 4. Thưởng độ mới của bài viết (Recency Boost)
        posted_at = getattr(job, "posted_at", None) or getattr(job, "crawled_at", None)
        if posted_at:
            try:
                now = datetime.now(timezone.utc)
                if posted_at.tzinfo is None:
                    p_at = posted_at.replace(tzinfo=timezone.utc)
                else:
                    p_at = posted_at
                diff_seconds = (now - p_at).total_seconds()
                diff_hours = diff_seconds / 3600.0

                if diff_hours <= 6:
                    score += 20.0
                elif diff_hours <= 24:
                    score += 15.0
                elif diff_hours <= 72:  # 3 ngày
                    score += 10.0
                elif diff_hours <= 168:  # 7 ngày
                    score += 5.0
            except Exception:
                pass

        return score


smart_search_engine = SmartSearchEngine()
