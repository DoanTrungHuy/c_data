import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Starting with {len(jobs)} jobs.")
cleaned = []
for j in jobs:
    t = j["title"].lower()
    if any(k in t for k in ["import", "export", "procurement", "kinh doanh ta", "kinh doanh (junior", "production trainer", "sales engineer"]):
        print("Excluding non-pure IT:", j["title"])
        continue
    cleaned.append(j)

print(f"Cleaned strictly pure IT jobs: {len(cleaned)}")

with open("frontend/public/data/jobs.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

conn = sqlite3.connect("backend/cdata.db")
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
        j["source_url"], j["location_province"], j["location_district"], j.get("location_full"),
        j.get("salary_text", "Thỏa thuận"), j.get("salary_min"), j.get("salary_max"),
        "Công nghệ thông tin / Phần mềm / IT", j.get("description", ""), j.get("requirements", "")
    ))
conn.commit()
conn.close()
print("Database synchronized.")
