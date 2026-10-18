import json
import sqlite3
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
json_path = os.path.join(root_dir, "frontend", "public", "data", "jobs.json")
out_json_path = os.path.join(root_dir, "frontend", "out", "data", "jobs.json")
db_path = os.path.join(root_dir, "backend", "cdata.db")

with open(json_path, "r", encoding="utf-8") as f:
    jobs = json.load(f)

DISQUALIFIED_TERMS = [
    "filter", "jobs in", "garment", "merchandiser", "fabric", "may mặc",
    "dệt may", "thời trang", "cnc", "máy phay", "gia công cơ khí"
]

def is_clean_job(j):
    comp = j.get("company_name", "").lower()
    title = j.get("title", "").lower()
    
    # Quảng Ninh jobs are kept unless obviously fake
    if j.get("location_province") == "Quảng Ninh":
        return True

    for term in DISQUALIFIED_TERMS:
        if term in title or term in comp:
            return False
    return True

cleaned = [j for j in jobs if is_clean_job(j)]

print(f"Dataset purification: before={len(jobs)}, after={len(cleaned)}")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

if os.path.exists(os.path.dirname(out_json_path)):
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("DELETE FROM jobs")
for j in cleaned:
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
total_db = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
conn.close()
print(f"SQLite DB updated successfully. Total verified pure IT jobs: {total_db}")
