import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT DISTINCT source_platform, count(*) FROM jobs GROUP BY source_platform")
for plat, cnt in c.fetchall():
    print(f"Platform: {plat} | Count: {cnt}")

c.execute("""
    SELECT j.id, j.title, j.company_id, comp.name, j.location_province, j.location_district, 
           j.location_full, j.source_url, j.source_platform, j.is_active, j.raw_data
    FROM jobs j
    LEFT JOIN companies comp ON j.company_id = comp.id
    WHERE j.source_url LIKE '%careerviet%'
""")

rows = c.fetchall()
print(f"Total CareerViet jobs in DB: {len(rows)}")

for idx, r in enumerate(rows[:30]):
    jid, title, cid, cname, prov, dist, loc_full, url, plat, is_active, raw = r
    print(f"[{idx+1}] ID: {jid} | Title: {title} | Company: {cname} | Prov: {prov} | Dist: {dist} | Active: {is_active} | URL: {url}")

conn.close()
