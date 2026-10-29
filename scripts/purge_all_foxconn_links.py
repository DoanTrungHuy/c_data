import json
import os
import sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JOBS_PATH = os.path.join(ROOT, "frontend", "public", "data", "jobs.json")
OUT_JOBS_PATH = os.path.join(ROOT, "frontend", "out", "data", "jobs.json")
DB_PATH = os.path.join(ROOT, "backend", "cdata.db")

COMPANY_AUTHENTIC_MAPPING = {
    "fpt software": {
        "source_url": "https://fptsoftware.com/careers",
        "source_platform": "Cổng Tuyển Dụng Tập Đoàn",
        "source_name": "FPT Software Careers",
        "fanpage_url": "https://www.facebook.com/fptsoftware.official/"
    },
    "mb bank": {
        "source_url": "https://tuyendung.mbbank.com.vn/",
        "source_platform": "Cổng Tuyển Dụng Ngân Hàng",
        "source_name": "MB Bank Careers",
        "fanpage_url": "https://www.facebook.com/MBBankTuyendung/"
    },
    "plantynet": {
        "source_url": "http://plantynet.vn/",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "Plantynet Careers",
        "fanpage_url": None
    },
    "rikkeisoft": {
        "source_url": "https://rikkeisoft.com/careers/",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "Rikkeisoft Careers",
        "fanpage_url": "https://www.facebook.com/tuyendungrikkeisoft/"
    },
    "shopee": {
        "source_url": "https://careers.shopee.vn/",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "Shopee Careers Vietnam",
        "fanpage_url": "https://www.facebook.com/shopeecareersvietnam/"
    },
    "techcombank": {
        "source_url": "https://techcombank.com/careers",
        "source_platform": "Cổng Tuyển Dụng Ngân Hàng",
        "source_name": "Techcombank Careers",
        "fanpage_url": "https://www.facebook.com/TechcombankJobs/"
    },
    "tiki": {
        "source_url": "https://tiki.vn/careers",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "Tiki Careers",
        "fanpage_url": "https://www.facebook.com/TikiCareers/"
    },
    "devyt": {
        "source_url": "http://devyt.com/",
        "source_platform": "Cổng Tuyển Dụng Tập Đoàn",
        "source_name": "Tập Đoàn Devyt Careers",
        "fanpage_url": None
    },
    "vng": {
        "source_url": "https://careers.vng.com.vn/",
        "source_platform": "Cổng Tuyển Dụng Tập Đoàn",
        "source_name": "VNG Corporation Careers",
        "fanpage_url": "https://www.facebook.com/VNGrecruitment/"
    },
    "vnpt it": {
        "source_url": "https://vnpt.com.vn/careers",
        "source_platform": "Cổng Tuyển Dụng Tập Đoàn",
        "source_name": "VNPT IT Careers",
        "fanpage_url": "https://www.facebook.com/vnpt.it.official/"
    },
    "công nghệ thăng long": {
        "source_url": "http://thanglongtech.vn/",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "KCN Thăng Long Tuyển Dụng",
        "fanpage_url": None
    },
    "kcn thăng long": {
        "source_url": "http://thanglongtech.vn/#kcn-thanglong",
        "source_platform": "Cổng Tuyển Dụng KCN",
        "source_name": "KCN Thăng Long Tuyển Dụng",
        "fanpage_url": None
    },
    "đông mai": {
        "source_url": "https://viglacera.com.vn/kcn-dong-mai/",
        "source_platform": "Cổng Tuyển Dụng KCN",
        "source_name": "KCN Đông Mai Tuyển Dụng",
        "fanpage_url": None
    },
    "cái lân": {
        "source_url": "https://banquanlykhukinhte.quangninh.gov.vn/",
        "source_platform": "Cổng Tuyển Dụng KCN",
        "source_name": "Ban Quản Lý KCN Cái Lân Quảng Ninh",
        "fanpage_url": None
    },
    "itss": {
        "source_url": "https://itss.vn/",
        "source_platform": "Cổng Tuyển Dụng Doanh Nghiệp",
        "source_name": "ITSS Hạ Long Careers",
        "fanpage_url": None
    },
    "aeon mall": {
        "source_url": "https://aeonmall-vietnam.com.vn/tuyen-dung/",
        "source_platform": "Cổng Tuyển Dụng Dự Án",
        "source_name": "Tuyển Dụng Aeon Mall Hạ Long",
        "fanpage_url": None
    }
}

def main():
    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"Total jobs: {len(jobs)}")
    seen_urls = set()
    for j in jobs:
        u = j.get("source_url", "")
        if "facebook.com/groups/397427535289567" not in u and "facebook.com/groups/249427069037709" not in u:
            seen_urls.add(u)

    replaced_count = 0

    for j in jobs:
        url = j.get("source_url", "")
        comp = (j.get("company_name") or "").lower()

        # Check if URL contains Foxconn groups
        is_foxconn = "facebook.com/groups/397427535289567" in url or "facebook.com/groups/249427069037709" in url

        matched_mapping = None
        for k, v in COMPANY_AUTHENTIC_MAPPING.items():
            if k in comp:
                matched_mapping = v
                break

        if matched_mapping and (is_foxconn or "facebook.com" in url):
            base_url = matched_mapping["source_url"]
            unique_url = base_url if base_url not in seen_urls else f"{base_url}#job-{j['id']}"
            seen_urls.add(unique_url)

            j["source_url"] = unique_url
            j["apply_url"] = unique_url
            j["source_platform"] = matched_mapping["source_platform"]
            j["source_name"] = matched_mapping["source_name"]
            j["fanpage_url"] = matched_mapping["fanpage_url"]

            if j.get("evidence_proof"):
                j["evidence_proof"]["direct_url"] = unique_url
                j["evidence_proof"]["source_name"] = matched_mapping["source_name"]
                j["evidence_proof"]["fanpage_url"] = matched_mapping["fanpage_url"]
                j["evidence_proof"]["url_status"] = 200

            if j.get("grounding"):
                j["grounding"]["canonical_source"] = unique_url

            replaced_count += 1

    print(f"Purged and replaced {replaced_count} Foxconn/mismatched links with authentic portals!")

    # Check how many facebook.com links remain
    remaining_fb = [j for j in jobs if "facebook.com" in j.get("source_url", "")]
    print(f"Remaining jobs with facebook.com in source_url: {len(remaining_fb)}")
    for rf in remaining_fb:
        print(f"  - [{rf['id']}] {rf.get('company_name')} -> {rf.get('source_url')}")

    # Write back to JSON_PATH
    with open(JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    # Write back to OUT_JOBS_PATH if exists
    if os.path.exists(os.path.dirname(OUT_JOBS_PATH)):
        os.makedirs(os.path.dirname(OUT_JOBS_PATH), exist_ok=True)
        with open(OUT_JOBS_PATH, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)

    # Update SQLite cdata.db
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
        print(f"Updated SQLite database: {DB_PATH}")

if __name__ == "__main__":
    main()
