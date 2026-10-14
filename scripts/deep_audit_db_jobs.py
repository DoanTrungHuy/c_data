import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("""
    SELECT j.id, j.title, j.company_id, comp.name, j.location_province, j.location_district, 
           j.location_full, j.source_url, j.source_platform, j.is_active, j.raw_data
    FROM jobs j
    LEFT JOIN companies comp ON j.company_id = comp.id
""")

rows = c.fetchall()
print(f"Total jobs in DB: {len(rows)}")

careerviet_jobs = []
other_jobs = []

for r in rows:
    jid, title, cid, cname, prov, dist, loc_full, url, plat, is_active, raw = r
    raw_dict = {}
    if raw:
        try:
            raw_dict = json.loads(raw)
        except Exception:
            pass
            
    item = {
        "id": jid,
        "title": title,
        "cid": cid,
        "company_name": cname,
        "province": prov,
        "district": dist,
        "location_full": loc_full,
        "source_url": url,
        "source_platform": plat,
        "is_active": is_active,
        "raw_dict": raw_dict
    }
    if plat and "careerviet" in plat.lower():
        careerviet_jobs.append(item)
    else:
        other_jobs.append(item)

print(f"\nCareerViet jobs count: {len(careerviet_jobs)}")
for idx, j in enumerate(careerviet_jobs):
    raw_comp = j["raw_dict"].get("company") or j["raw_dict"].get("company_name")
    print(f"[{idx+1}] ID: {j['id']} | Title: {j['title']} | DB Comp: {j['company_name']} | Raw Comp: {raw_comp} | Prov: {j['province']} | Dist: {j['district']} | Active: {j['is_active']} | URL: {j['source_url']}")

print(f"\nOther jobs count: {len(other_jobs)}")
for idx, j in enumerate(other_jobs):
    print(f"[{idx+1}] ID: {j['id']} | Title: {j['title']} | DB Comp: {j['company_name']} | Prov: {j['province']} | Dist: {j['district']} | Active: {j['is_active']} | URL: {j['source_url']}")

conn.close()
