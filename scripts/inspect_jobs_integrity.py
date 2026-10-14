import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

def check():
    print("=== CHECKING FRONTEND jobs.json ===")
    with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
        frontend_jobs = json.load(f)
    print(f"Total jobs in frontend: {len(frontend_jobs)}")
    
    for i, j in enumerate(frontend_jobs):
        title = j.get("title", "")
        company = j.get("company_name", "")
        prov = j.get("location_province", "")
        dist = j.get("location_district", "")
        url = j.get("source_url", "")
        phones = j.get("raw_data", {}).get("mined", {}).get("phones", []) if isinstance(j.get("raw_data"), dict) else []
        phone = phones[0] if (isinstance(phones, list) and len(phones) > 0) else None
        platform = j.get("source_platform", "")
        
        # Check potential anomalies
        anomalies = []
        if "Tập Đoàn Đầu Tư & Kinh Doanh Bất Động Sản" in company:
            anomalies.append("FALLBACK_COMPANY_NAME")
        if "Hà Nội" in title or "Hà Nội" in str(j.get("description", ""))[:100] and prov == "Quảng Ninh":
            anomalies.append("HN_IN_QN")
        if prov != "Quảng Ninh" and "Hạ Long" in title:
            anomalies.append("PROV_NOT_QN_BUT_HALONG_TITLE")
        if prov not in ["Quảng Ninh", "Hà Nội", "Hồ Chí Minh", "Toàn quốc"]:
            anomalies.append(f"UNUSUAL_PROV_{prov}")
        if not url:
            anomalies.append("NO_URL")
        elif "cict.com.vn" in url and "cict" not in company.lower() and "cảng" not in company.lower():
            anomalies.append(f"MISMATCHED_DOMAIN_CICT_FOR_{company}")
        elif "flc.vn" in url and "flc" not in company.lower():
            anomalies.append(f"MISMATCHED_DOMAIN_FLC_FOR_{company}")
            
        print(f"[{i+1}] {title[:40]} | Comp: {company[:30]} | Loc: {prov} - {dist} | Plat: {platform} | URL: {url[:50]} | Anomalies: {anomalies}")

    print("\n=== CHECKING DATABASE cdata.db ===")
    conn = sqlite3.connect("backend/cdata.db")
    c = conn.cursor()
    c.execute("SELECT count(*) FROM jobs")
    print("Total jobs in DB:", c.fetchone()[0])
    
    c.execute("SELECT id, title, company_id, location_province, location_district, source_url, source_platform FROM jobs WHERE is_active = 1")
    rows = c.fetchall()
    print("Active jobs in DB:", len(rows))
    
    c.execute("SELECT id, name, website FROM companies")
    companies_db = {r[0]: (r[1], r[2]) for r in c.fetchall()}
    print(f"Total companies in DB: {len(companies_db)}")
    
    print("\nSample DB active jobs:")
    for r in rows[:15]:
        comp_info = companies_db.get(r[2], ("NO_COMPANY", "NO_WEB"))
        print(f"Job: {r[1][:35]} | Comp: {comp_info[0][:30]} | Prov: {r[3]} - {r[4]} | URL: {r[5][:40] if r[5] else 'None'}")
        
    conn.close()

if __name__ == "__main__":
    check()
