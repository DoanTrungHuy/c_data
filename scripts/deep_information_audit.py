import sys
import io
import json
import re
from urllib.parse import urlparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"==================================================")
print(f"BẮT ĐẦU KIỂM TRA TOÀN DIỆN {len(jobs)} VIỆC LÀM TRONG HỆ THỐNG")
print(f"==================================================")

issues = []
qn_jobs = []

PROVINCES_KNOWN = [
    "Quảng Ninh", "Hà Nội", "Hồ Chí Minh", "TP. Hồ Chí Minh", "Đà Nẵng",
    "Hải Phòng", "Hải Dương", "Bắc Ninh", "Bình Dương", "Cần Thơ",
    "Đồng Nai", "Khánh Hòa", "Hưng Yên", "Vĩnh Phúc", "Bà Rịa - Vũng Tàu"
]

NON_IT_TERMS = [
    "bán hàng", "thu ngân", "kế toán", "lái xe", "phục vụ", "bảo vệ",
    "thủ kho", "cơ khí", "may mặc", "dệt may", "thực phẩm", "nông nghiệp",
    "xây dựng", "buồng phòng", "đầu bếp"
]

for idx, j in enumerate(jobs, 1):
    jid = j.get("id")
    title = (j.get("title") or "").strip()
    comp = (j.get("company_name") or "").strip()
    url = (j.get("source_url") or "").strip()
    prov = (j.get("location_province") or "").strip()
    full_loc = (j.get("location_full") or "").strip()
    desc = (j.get("description") or "").strip()
    req = (j.get("requirements") or "").strip()
    sal_min = j.get("salary_min")
    sal_max = j.get("salary_max")
    ep = j.get("evidence_proof") or {}

    # 1. Kiểm tra Tiêu đề
    if not title or len(title) < 5:
        issues.append((jid, "Tiêu đề quá ngắn hoặc rỗng", title))
    if any(bad in title.lower() for bad in ["test job", "sample", "undefined", "null"]):
        issues.append((jid, "Tiêu đề chứa từ khóa rác", title))

    # 2. Kiểm tra Doanh nghiệp
    if not comp or comp.lower() in ["doanh nghiệp cntt", "doanh nghiệp đối tác", "filter", "chế độ phúc lợi", "công ty"]:
        issues.append((jid, "Tên công ty chung chung hoặc rác", comp))

    # 3. Kiểm tra Link nguồn (source_url)
    if not url.startswith("http://") and not url.startswith("https://"):
        issues.append((jid, "URL không hợp lệ", url))
    if "facebook.com/groups/397427535289567" in url or "facebook.com/groups/249427069037709" in url:
        issues.append((jid, "URL chứa link nhóm Facebook Foxconn cũ", url))
    if "facebook.com/search" in url:
        issues.append((jid, "URL chứa link tìm kiếm giả lập", url))

    # 4. Kiểm tra Địa bàn Quảng Ninh
    if prov == "Quảng Ninh":
        qn_jobs.append(j)
        qn_keywords = ["quảng ninh", "hạ long", "cẩm phả", "uông bí", "bãi cháy", "cái lân", "đông mai", "móng cái", "quảng yên"]
        has_qn = any(k in full_loc.lower() for k in qn_keywords)
        if not has_qn:
            issues.append((jid, "Ghi tỉnh Quảng Ninh nhưng địa chỉ không có từ khóa Quảng Ninh", full_loc))
        if "hà nội" in full_loc.lower() and not any(k in full_loc.lower() for k in ["hạ long", "quảng ninh", "bãi cháy"]):
            issues.append((jid, "Ghi Quảng Ninh nhưng địa chỉ thực tế là Hà Nội", full_loc))

    # 5. Kiểm tra chuỗi địa danh dính chữ
    for p in ["Hà Nội", "Quảng Ninh", "Hồ Chí Minh", "Đà Nẵng"]:
        if re.search(p + r"[A-ZÀ-Ỹ]", full_loc):
            issues.append((jid, f"Địa chỉ bị dính chữ ({p})", full_loc))

    # 6. Kiểm tra Chuyên môn CNTT đối với tin ngoài tỉnh
    if prov != "Quảng Ninh":
        cat = (j.get("category") or "").lower()
        t_low = title.lower()
        is_it = any(k in t_low or k in cat for k in ["it", "cntt", "công nghệ thông tin", "lập trình", "phần mềm", "developer", "software", "mạng", "hệ thống", "cloud", "data", "qa", "qc", "tester", "security", "engineer", "devops", "architect", "analyst"])
        if not is_it:
            issues.append((jid, "Tin ngoài tỉnh không thuộc chuyên ngành CNTT", f"{title} | {cat}"))

    # 7. Kiểm tra JD & Requirements
    if len(desc) < 30:
        issues.append((jid, "Mô tả JD quá ngắn (<30 ký tự)", desc))
    if len(req) < 20:
        issues.append((jid, "Yêu cầu công việc quá ngắn (<20 ký tự)", req))

    # 8. Kiểm tra Mức lương
    if sal_min is not None and sal_max is not None:
        if sal_min > sal_max:
            issues.append((jid, f"Mức lương min ({sal_min}) lớn hơn max ({sal_max})", ""))
        if sal_min < 0 or sal_max > 500000000:
            issues.append((jid, f"Mức lương bất thường (min={sal_min}, max={sal_max})", ""))

    # 9. Kiểm tra Evidence Proof
    if not ep:
        issues.append((jid, "Thiếu đối tượng evidence_proof", ""))
    elif not ep.get("verified"):
        issues.append((jid, "Evidence proof chưa được verified", ""))

print(f"\n[KẾT QUẢ KIỂM TRA]")
print(f"- Tổng số việc làm đã kiểm tra: {len(jobs)}")
print(f"- Số việc làm tại Quảng Ninh: {len(qn_jobs)}")
print(f"- Số vấn đề phát hiện: {len(issues)}")

if issues:
    print(f"\nDANH SÁCH CHI TIẾT CÁC VẤN ĐỀ ({len(issues)}):")
    for iss in issues[:30]:
        print(f"  ❌ [{iss[0]}] {iss[1]}: {iss[2]}")
    if len(issues) > 30:
        print(f"  ... và còn {len(issues) - 30} vấn đề khác.")
else:
    print("\n✅ HOÀN TOÀN KHÔNG CÓ BẤT KỲ VẤN ĐỀ NÀO! DỮ LIỆU ĐẠT CHUẨN 100%!")

print("\n--------------------------------------------------")
print("DANH SÁCH CÁC VIỆC LÀM TẠI TỈNH QUẢNG NINH:")
print("--------------------------------------------------")
for idx, q in enumerate(qn_jobs, 1):
    print(f"{idx}. [{q['id']}] {q.get('title')}")
    print(f"   🏢 Công ty: {q.get('company_name')}")
    print(f"   📍 Địa điểm: {q.get('location_full')}")
    print(f"   🌐 Nguồn: {q.get('source_platform')} -> {q.get('source_url')}")
    if q.get('fanpage_url'):
        print(f"   📱 Fanpage: {q.get('fanpage_url')}")
    print()
