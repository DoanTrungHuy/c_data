import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT id, title, location_province, location_district, source_url, raw_data FROM jobs WHERE source_url LIKE '%careerviet%'")
rows = c.fetchall()

print(f"Total CareerViet jobs: {len(rows)}")
for i, r in enumerate(rows):
    jid, title, prov, dist, url, raw = r
    raw_obj = json.loads(raw) if raw else {}
    print(f"[{i+1}] {title}")
    print(f"    Prov: {prov} | Dist: {dist} | URL: {url}")
    print(f"    Raw keys: {list(raw_obj.keys()) if isinstance(raw_obj, dict) else type(raw_obj)}")
    if isinstance(raw_obj, dict):
        for k in ['company', 'company_name', 'employer', 'hiringOrganization', 'source', 'platform']:
            if k in raw_obj:
                print(f"    {k}: {raw_obj[k]}")
    print("-" * 50)

conn.close()
