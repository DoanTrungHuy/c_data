import os
import re
import json
import sqlite3

HARVESTER_PATH = "backend/app/services/social_deep_harvester.py"
JOBS_PATH = "frontend/public/data/jobs.json"
OUT_JOBS_PATH = "frontend/out/data/jobs.json"
DB_PATH = "backend/cdata.db"

with open(HARVESTER_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Replace any "Facebook (...)" with true platform types
replacements = {
    '"source_platform": "Facebook (Novotel Ha Long Bay Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (Tuyển Dụng Sun Group Vùng Đông Bắc)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Cộng Đồng IT Quảng Ninh & Tuyển Dụng CNTT)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Hội Việc Làm Hạ Long - Bãi Cháy)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (FPT Telecom Quảng Ninh Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Việc Làm CNTT & Chuyển Đổi Số Quảng Ninh)",': '"source_platform": "Cổng Đơn Vị Y Tế",',
    '"source_platform": "Facebook (Viettel Quảng Ninh Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Cộng Đồng Tuyển Dụng ERP)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (Mường Thanh Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (Wyndham Legend Halong Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (Bệnh Viện Bãi Cháy Tuyển Dụng)",': '"source_platform": "Cổng Đơn Vị Y Tế",',
    '"source_platform": "Facebook (Than Hòn Gai - TKV Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (FPT Software Careers)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Viettel Digital Talent)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (VNG Recruitment)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (Rikkeisoft Tuyển Dụng)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (VNPT IT Official)",': '"source_platform": "Cổng Tuyển Dụng Tập Đoàn",',
    '"source_platform": "Facebook (MB Bank Careers)",': '"source_platform": "Cổng Tuyển Dụng Ngân Hàng",',
    '"source_platform": "Facebook (Techcombank Careers)",': '"source_platform": "Cổng Tuyển Dụng Ngân Hàng",',
    '"source_platform": "Facebook (Shopee Careers Vietnam)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
    '"source_platform": "Facebook (Tiki Careers)",': '"source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",',
}

for old, new in replacements.items():
    code = code.replace(old, new)

with open(HARVESTER_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated social_deep_harvester.py successfully!")

# Now update jobs.json
with open(JOBS_PATH, "r", encoding="utf-8") as f:
    jobs = json.load(f)

PLATFORM_MAP = {
    "cict": "Cổng Tuyển Dụng Doanh Nghiệp",
    "fpt software": "Cổng Tuyển Dụng Tập Đoàn",
    "viettel": "Cổng Tuyển Dụng Tập Đoàn",
    "vng": "Cổng Tuyển Dụng Tập Đoàn",
    "rikkeisoft": "Cổng Tuyển Dụng Doanh Nghiệp",
    "vnpt": "Cổng Tuyển Dụng Tập Đoàn",
    "mb bank": "Cổng Tuyển Dụng Ngân Hàng",
    "techcombank": "Cổng Tuyển Dụng Ngân Hàng",
    "shopee": "Cổng Tuyển Dụng Doanh Nghiệp",
    "tiki": "Cổng Tuyển Dụng Doanh Nghiệp",
    "novotel": "Cổng Tuyển Dụng Doanh Nghiệp",
    "sun group": "Cổng Tuyển Dụng Tập Đoàn",
    "sun world": "Cổng Tuyển Dụng Tập Đoàn",
    "vinpearl": "Cổng Tuyển Dụng Tập Đoàn",
    "fpt telecom": "Cổng Tuyển Dụng Tập Đoàn",
    "vinmec": "Cổng Tuyển Dụng Doanh Nghiệp",
    "mường thanh": "Cổng Tuyển Dụng Doanh Nghiệp",
    "wyndham": "Cổng Tuyển Dụng Doanh Nghiệp",
    "bệnh viện bãi cháy": "Cổng Đơn Vị Y Tế",
    "bệnh viện đa khoa": "Cổng Đơn Vị Y Tế",
    "than hòn gai": "Cổng Tuyển Dụng Tập Đoàn",
    "bia hà nội": "Cổng Tuyển Dụng Doanh Nghiệp",
    "itss": "Cổng Tuyển Dụng Doanh Nghiệp",
    "plantynet": "Cổng Tuyển Dụng Doanh Nghiệp",
    "devyt": "Cổng Tuyển Dụng Tập Đoàn",
    "kcn thăng long": "Cổng Tuyển Dụng KCN",
    "đông mai": "Cổng Tuyển Dụng KCN",
    "cái lân": "Cổng Tuyển Dụng KCN",
    "aeon mall": "Cổng Tuyển Dụng Dự Án",
}

FANPAGE_MAP = {
    "fpt software": "https://www.facebook.com/fptsoftware.official/",
    "viettel": "https://www.facebook.com/ViettelQuangNinhOfficial/",
    "vng": "https://www.facebook.com/VNGrecruitment/",
    "rikkeisoft": "https://www.facebook.com/tuyendungrikkeisoft/",
    "vnpt": "https://www.facebook.com/vnpt.it.official/",
    "mb bank": "https://www.facebook.com/MBBankTuyendung/",
    "techcombank": "https://www.facebook.com/TechcombankJobs/",
    "shopee": "https://www.facebook.com/shopeecareersvietnam/",
    "tiki": "https://www.facebook.com/TikiCareers/",
    "novotel": "https://www.facebook.com/NovotelHaLongBay/",
    "sun world": "https://www.facebook.com/SunWorldHalongComplex/",
    "vinpearl": "https://www.facebook.com/Vinpearl/",
    "fpt telecom": "https://www.facebook.com/fpttelecomquangninh/",
    "vinmec": "https://www.facebook.com/VinmecHealthcareSystem/",
    "mường thanh": "https://www.facebook.com/MuongThanhLuxuryHaLongCentre/",
    "wyndham": "https://www.facebook.com/wyndhamlegendhalong/",
    "bệnh viện bãi cháy": "https://www.facebook.com/benhvienbaichayqn/",
    "bệnh viện đa khoa": "https://www.facebook.com/benhviendakhoatinhquangninh/",
    "than hòn gai": "https://www.facebook.com/thanhongaitkv/",
    "cict": "https://www.facebook.com/CICTCaiLan/",
}

updated = 0
for j in jobs:
    comp = (j.get("company_name") or "").lower()
    p = j.get("source_platform") or ""
    
    # If platform is Facebook or needs standardization
    if p == "Facebook" or "facebook (" in p.lower():
        for k, v in PLATFORM_MAP.items():
            if k in comp:
                j["source_platform"] = v
                j["source_name"] = v
                if j.get("evidence_proof"):
                    j["evidence_proof"]["source_name"] = v
                updated += 1
                break

    # Attach fanpage if available
    for k, fp in FANPAGE_MAP.items():
        if k in comp and not j.get("fanpage_url"):
            j["fanpage_url"] = fp
            if j.get("evidence_proof"):
                j["evidence_proof"]["fanpage_url"] = fp

print(f"Standardized {updated} job platforms in jobs.json!")

with open(JOBS_PATH, "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

if os.path.exists(os.path.dirname(OUT_JOBS_PATH)):
    with open(OUT_JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

# Update SQLite
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM jobs")
    for j in jobs:
        c.execute("""
            INSERT OR REPLACE INTO jobs (
                id, title, company_name, source_platform, source_url,
                location_province, location_district, location_full,
                salary_text, salary_min, salary_max,
                category, description, requirements,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            j["id"], j["title"], j["company_name"], j.get("source_platform", "CareerViet"),
            j["source_url"], j["location_province"], j.get("location_district"), j["location_full"],
            j.get("salary_text", "Thỏa thuận"), j.get("salary_min"), j.get("salary_max"),
            j.get("category", "Công nghệ thông tin / Phần mềm / IT"), j.get("description", ""), j.get("requirements", "")
        ))
    conn.commit()
    conn.close()
    print("Synchronized SQLite cdata.db!")
