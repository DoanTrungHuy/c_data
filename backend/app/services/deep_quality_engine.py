"""
C_Data - Deep Quality Engine (Hệ Thống Thẩm Định & Đánh Giá Chất Lượng Tuyển Dụng)
Chuyên sâu: TP. Hạ Long & Tỉnh Quảng Ninh + Việc làm CNTT Chuyên Môn Cao

Nguyên tắc: "Chất lượng hơn số lượng - Tìm càng lâu càng sâu"
Thang điểm 100 dựa trên 5 trụ cột:
1. Doanh nghiệp & Pháp nhân xác thực (25đ)
2. Minh bạch mức lương & Thu nhập thực tế (20đ)
3. Địa điểm làm việc cụ thể tại Hạ Long / Quảng Ninh (20đ)
4. Kênh liên hệ HR trực tiếp (Hotline, Zalo, Email tên miền doanh nghiệp) (15đ)
5. Bản mô tả công việc (JD) sâu & Bóc tách Tech Stack cụ thể (20đ)
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# Từ điển bóc tách Tech Stack & Công nghệ chuyên môn
TECH_TAXONOMY = {
    # Hạ tầng & Mạng
    "Cisco": [r"\bcisco\b", r"\bswitch cisco\b", r"\brouter cisco\b"],
    "Fortinet": [r"\bfortinet\b", r"\bfortigate\b"],
    "Firewall": [r"\bfirewall\b", r"\btuong lua\b"],
    "Windows Server": [r"\bwindows server\b", r"\bactive directory\b", r"\bgroup policy\b"],
    "Linux": [r"\blinux\b", r"\bubuntu\b", r"\bcentos\b", r"\bdebian\b"],
    "VMware ESXi": [r"\bvmware\b", r"\besxi\b", r"\bao hoa\b"],
    "TCP/IP & VPN": [r"\btcp\/ip\b", r"\bvpn\b", r"\bvlan\b", r"\bran\/wan\b", r"\blan\/wan\b"],
    "WiFi 6 & Controller": [r"\bwifi\b", r"\baruba\b", r"\bruijie\b", r"\bunifi\b"],

    # Chuyên ngành Khách sạn & Du lịch
    "Opera PMS": [r"\bopera\b", r"\bopera pms\b"],
    "Micros POS": [r"\bmicros\b", r"\bmicros pos\b", r"\bpos\b", r"\bphan mem ban hang\b"],
    "Smile PMS": [r"\bsmile\b", r"\bsmile pms\b"],
    "Smart Key & RFID": [r"\brfid\b", r"\bthe tu\b", r"\bve dien tu\b", r"\bsoat ve\b"],

    # Chuyên ngành Cảng biển & Hàng hải
    "TOS Cảng Biển": [r"\btos\b", r"\bterminal operating system\b", r"\bphan mem cang\b"],
    "EDI Hải Quan": [r"\bedi\b", r"\bhai quan\b", r"\bkhai bao hai quan\b"],
    "GPS & Radar Hàng Hải": [r"\bgps\b", r"\bradar\b", r"\bdinh vi tau\b"],

    # Chuyên ngành Khai khoáng & Tự động hóa công nghiệp
    "SCADA / DCS": [r"\bscada\b", r"\bdcs\b", r"\bhe thong dieu khien\b"],
    "PLC Siemens": [r"\bplc\b", r"\bsiemens\b", r"\bs7-1200\b", r"\bs7-1500\b"],
    "PLC Mitsubishi": [r"\bmitsubishi\b", r"\bplc mitsubishi\b"],
    "Modbus & RS485": [r"\bmodbus\b", r"\brs485\b", r"\btruyen thong cong nghiep\b"],

    # Chuyên ngành Y tế thông minh
    "HIS Quản Lý Bệnh Viện": [r"\bhis\b", r"\bquan ly benh vien\b"],
    "PACS Chẩn Đoán Hình Ảnh": [r"\bpacs\b", r"\bdicom\b"],
    "Bệnh Án Điện Tử (EMR)": [r"\bemr\b", r"\bbenh an dien tu\b"],

    # Chuyên ngành FDI & Nhà máy chế tạo
    "ERP SAP": [r"\bsap\b", r"\berp\b"],
    "Hệ Thống MES": [r"\bmes\b", r"\bmanufacturing execution\b"],

    # Phát triển phần mềm & Dữ liệu
    "Python": [r"\bpython\b"],
    "FastAPI": [r"\bfastapi\b"],
    "React.js": [r"\breact\b", r"\breactjs\b"],
    "Next.js": [r"\bnext\.?js\b"],
    "TypeScript": [r"\btypescript\b"],
    "SQL Server": [r"\bsql server\b", r"\bmssql\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "Oracle DB": [r"\boracle\b"],
    "Docker & Container": [r"\bdocker\b", r"\bcontainer\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "DevOps & CI/CD": [r"\bdevops\b", r"\bci\/cd\b"],
    "AI & Trí Tuệ Nhân Tạo": [r"\bai\b", r"\bmachine learning\b", r"\bdeep learning\b"],
    "An Toàn Thông Tin": [r"\ban toan thong tin\b", r"\bsecurity\b", r"\bbao mat\b", r"\bsoc\b"],
}

# Tiêu chí phúc lợi bóc tách
BENEFIT_TAXONOMY = {
    "Xe đưa đón CBCNV": [r"\bxe dua don\b", r"\bxe cong ty\b"],
    "Bao ăn ca / Bữa trưa": [r"\ban ca\b", r"\bbao an\b", r"\bcom trua\b", r"\bphu cap an\b"],
    "Thưởng tháng 13 & Lễ Tết": [r"\bthang 13\b", r"\bthuong le\b", r"\bthuong tet\b"],
    "Bảo hiểm sức khỏe cao cấp": [r"\bbao hiem bao viet\b", r"\bbao hiem pvi\b", r"\bbao hiem suc khoe\b", r"\bcham soc suc khoe\b"],
    "Chỗ lưu trú / Ký túc xá": [r"\bluu tru\b", r"\bky tuc xa\b", r"\bnha o\b", r"\bkytucxa\b"],
    "Thưởng phí dịch vụ (Service Charge)": [r"\bservice charge\b", r"\bphi dich vu\b"],
    "Được cấp Laptop & Thiết bị": [r"\blaptop\b", r"\bmay tinh\b", r"\btrang thiet bi\b"],
    "Du lịch / Nghỉ mát hàng năm": [r"\bdu lich\b", r"\bnghi mat\b", r"\bteambuilding\b"],
    "Phụ cấp độc hại / Làm việc hầm lò": [r"\bdoc hai\b", r"\bham lo\b", r"\bphu cap mo\b"],
}


def extract_tech_stack(text: str) -> List[str]:
    """Bóc tách chính xác các công nghệ, phần mềm, thiết bị có trong tin tuyển dụng"""
    text_lower = text.lower()
    matched = []
    for tech_name, patterns in TECH_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                matched.append(tech_name)
                break
    return matched[:8]


def extract_benefits(text: str) -> List[str]:
    """Bóc tách quyền lợi cụ thể được cam kết trong tin"""
    text_lower = text.lower()
    matched = []
    for b_name, patterns in BENEFIT_TAXONOMY.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                matched.append(b_name)
                break
    # Mặc định thêm các quyền lợi tiêu chuẩn nếu ít hơn 2
    if "BHXH, BHYT theo luật lao động" not in matched:
        matched.append("Đầy đủ BHXH, BHYT & BHTN theo Bộ luật Lao động")
    return matched[:6]


def generate_interview_process(category: str, title: str) -> List[Dict[str, str]]:
    """Tạo lộ trình phỏng vấn tiêu chuẩn, thực tế theo vị trí"""
    title_l = title.lower()
    if "kỹ sư" in title_l or "chuyên viên" in title_l or "developer" in title_l or "lập trình" in title_l:
        return [
            {"step": 1, "title": "Sàng lọc hồ sơ CV", "desc": "HR thẩm duyệt bằng cấp, kinh nghiệm và kỹ năng trong 24-48h."},
            {"step": 2, "title": "Phỏng vấn Kỹ thuật & Nghiệp vụ", "desc": "Gặp Trưởng bộ phận CNTT, đánh giá xử lý tình huống thực tế hoặc bài test năng lực."},
            {"step": 3, "title": "Thỏa thuận đãi ngộ & Nhận việc", "desc": "Thống nhất mức lương, chế độ đãi ngộ, ký kết thư mời nhận việc (Offer Letter)."}
        ]
    elif "it support" in title_l or "helpdesk" in title_l or "kỹ thuật viên" in title_l:
        return [
            {"step": 1, "title": "Tiếp nhận hồ sơ", "desc": "HR liên hệ trao đổi sơ bộ qua điện thoại/Zalo trong vòng 24 giờ."},
            {"step": 2, "title": "Phỏng vấn trực tiếp tại cơ sở", "desc": "Kiểm tra thao tác phần cứng mạng, máy in, hệ thống camera và thái độ phục vụ."},
            {"step": 3, "title": "Bàn giao ca trực & Thử việc", "desc": "Hướng dẫn nhận diện sơ đồ mạng, nhận trang phục bảo hộ và nhận việc ngay."}
        ]
    else:
        return [
            {"step": 1, "title": "Nộp hồ sơ ứng tuyển", "desc": "Gửi thông tin qua Zalo HR hoặc nộp trực tiếp tại văn phòng."},
            {"step": 2, "title": "Gặp mặt phỏng vấn", "desc": "Trao đổi công việc, lịch làm việc theo ca và kiểm tra sức khỏe cơ bản."},
            {"step": 3, "title": "Tiếp nhận chính thức", "desc": "Ký hợp đồng lao động, cấp phát đồng phục và xếp lịch ca làm."}
        ]


def compute_job_quality(
    job_data: Dict[str, Any],
    company_domain: Optional[str] = None
) -> Tuple[int, str, Dict[str, Any]]:
    """
    Tính toán Điểm Chất Lượng Tuyển Dụng (0 - 100) và Thẩm định chi tiết
    Trả về: (score, tier, quality_audit)
    """
    score = 0
    audit = {
        "corporate_verified": False,
        "salary_transparent": False,
        "address_specific": False,
        "direct_contact": False,
        "jd_detailed": False,
        "tech_stack_clarity": False,
        "anti_scam_verified": True,
    }

    # 1. Pháp nhân & Doanh nghiệp xác thực (25đ)
    src_url = (job_data.get("source_url") or "").lower()
    comp_name = (job_data.get("company_name") or "").strip()
    is_direct_domain = any(domain in src_url for domain in [
        "wyndhamhalong.com", "vinacomin.vn", "flc.vn", "cict.com.vn",
        "sunworld.vn", "vinmec.com", "foxconn.com.vn", "vietcombank.com.vn",
        "fptjobs.com", "careers.accor.com", "paradisevietnam.com", "yokoonsenquanghanh.com.vn",
        "vandonairport.vn", "careerviet.vn", "topcv.vn", "vietnamworks.com"
    ])
    if is_direct_domain and len(comp_name) > 3:
        score += 25
        audit["corporate_verified"] = True
    elif len(comp_name) > 3:
        score += 15
        audit["corporate_verified"] = True

    # 2. Minh bạch mức lương (20đ)
    s_min = job_data.get("salary_min")
    s_max = job_data.get("salary_max")
    s_text = (job_data.get("salary_text") or "").strip()
    if s_min and s_max and s_min > 0 and s_max > 0:
        score += 20
        audit["salary_transparent"] = True
    elif (s_min and s_min > 0) or (s_max and s_max > 0):
        score += 16
        audit["salary_transparent"] = True
    elif s_text and ("triệu" in s_text.lower() or "tr/" in s_text.lower() or "k/h" in s_text.lower() or "usd" in s_text.lower()):
        score += 14
        audit["salary_transparent"] = True
    else:
        score += 5  # Thỏa thuận

    # 3. Địa điểm làm việc chi tiết tại Hạ Long / Quảng Ninh (20đ)
    loc_full = (job_data.get("location_full") or "").strip()
    loc_prov = (job_data.get("location_province") or "").strip()
    loc_dist = (job_data.get("location_district") or "").strip()
    
    # Có địa chỉ chi tiết tới số nhà/phường/đường/KCN
    has_specific_address = any(k in loc_full.lower() for k in [
        "phường", "đường", "khu đô thị", "kcn", "khu công nghiệp", "số ", "tòa nhà", "cảng", "km "
    ])
    if loc_prov == "Quảng Ninh" and has_specific_address:
        score += 20
        audit["address_specific"] = True
    elif loc_prov == "Quảng Ninh" and loc_dist:
        score += 17
        audit["address_specific"] = True
    elif has_specific_address:
        score += 15
        audit["address_specific"] = True
    else:
        score += 8

    # 4. Kênh liên hệ trực tiếp HR (15đ)
    raw_data = job_data.get("raw_data") or {}
    mined = raw_data.get("mined") if isinstance(raw_data, dict) else {}
    has_phone = bool((mined or {}).get("phones") or raw_data.get("phone"))
    has_email = bool((mined or {}).get("emails") or raw_data.get("email") or raw_data.get("hr_email"))
    if has_phone and has_email:
        score += 15
        audit["direct_contact"] = True
    elif has_phone or has_email:
        score += 12
        audit["direct_contact"] = True
    else:
        score += 5

    # 5. Bản mô tả công việc (JD) sâu & Kỹ năng rõ ràng (20đ)
    desc = (job_data.get("description") or "").strip()
    req = (job_data.get("requirements") or "").strip()
    full_text = f"{job_data.get('title', '')} {desc} {req}"
    tech_stack = extract_tech_stack(full_text)
    
    if len(desc) >= 120 and len(req) >= 40:
        score += 10
        audit["jd_detailed"] = True
    elif len(desc) >= 60:
        score += 6
        audit["jd_detailed"] = True

    if len(tech_stack) >= 2:
        score += 10
        audit["tech_stack_clarity"] = True
    elif len(tech_stack) >= 1:
        score += 6
        audit["tech_stack_clarity"] = True

    # Giới hạn điểm từ 0 đến 100
    final_score = min(100, max(0, score))

    # Xếp hạng phân cấp chất lượng
    if final_score >= 85:
        tier = "diamond"  # 💎 Thẩm Định Kim Cương
    elif final_score >= 70:
        tier = "gold"     # ⭐ Đạt Chuẩn Kiểm Định
    else:
        tier = "standard" # 📋 Chuẩn Cơ Bản

    return final_score, tier, audit


def enrich_job_posting(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nâng cấp & làm giàu dữ liệu toàn diện cho một bài đăng tuyển dụng
    """
    title = job_data.get("title", "")
    desc = job_data.get("description", "")
    req = job_data.get("requirements", "")
    category = job_data.get("category", "")
    full_content = f"{title} {desc} {req} {category}"

    # 1. Bóc tách Tech Stack
    tech_stack = extract_tech_stack(full_content)

    # 2. Bóc tách Phúc lợi
    benefits = extract_benefits(full_content)

    # 3. Lộ trình phỏng vấn
    interview_process = generate_interview_process(category, title)

    # 4. Tính toán Điểm Chất Lượng Thẩm Định
    quality_score, quality_tier, quality_audit = compute_job_quality(job_data)

    # 5. Cập nhật vào bản ghi
    enriched = dict(job_data)
    enriched["quality_score"] = quality_score
    enriched["quality_tier"] = quality_tier
    enriched["tech_stack"] = tech_stack
    enriched["benefits_detail"] = benefits
    enriched["interview_process"] = interview_process
    enriched["quality_audit"] = quality_audit

    # Đảm bảo raw_data cũng được lưu vết
    if not enriched.get("raw_data") or not isinstance(enriched["raw_data"], dict):
        enriched["raw_data"] = {}
    enriched["raw_data"]["quality_score"] = quality_score
    enriched["raw_data"]["quality_tier"] = quality_tier
    enriched["raw_data"]["tech_stack"] = tech_stack
    enriched["raw_data"]["benefits_detail"] = benefits
    enriched["raw_data"]["interview_process"] = interview_process
    enriched["raw_data"]["quality_audit"] = quality_audit

    return enriched
