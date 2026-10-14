import sqlite3
import json
import re
import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT id, title, source_url, location_province, company_id FROM jobs WHERE source_url LIKE '%careerviet%'")
rows = c.fetchall()

print(f"Total CareerViet jobs in DB: {len(rows)}")

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=10.0,
    follow_redirects=True,
    verify=False
)

results = []
for i, (jid, title, url, prov, cid) in enumerate(rows):
    try:
        r = client.get(url)
        status = r.status_code
        if status != 200:
            results.append((jid, title, url, "HTTP_" + str(status), None, None))
            continue
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Extract company name
        comp_el = soup.select_one(".employer-name, .company-name, .employer, a.employer")
        comp_name = comp_el.get_text(strip=True) if comp_el else None
        
        if not comp_name:
            m = re.findall(r'"hiringOrganization":\s*\{\s*"@type":\s*"Organization",\s*"name":\s*"([^"]+)"', r.text)
            if m:
                comp_name = m[0]
                
        # Extract location
        loc_el = soup.select_one(".map p, .location, .job-location")
        loc_text = loc_el.get_text(strip=True) if loc_el else None
        
        # Extract clean job title
        title_el = soup.select_one(".title, h1.title, h1")
        clean_title = title_el.get_text(strip=True) if title_el else title
        
        results.append((jid, clean_title, url, "OK", comp_name, loc_text))
        print(f"[{i+1}/{len(rows)}] {clean_title[:35]} | Real Comp: {comp_name} | Loc: {loc_text}")
    except Exception as e:
        results.append((jid, title, url, f"ERR_{str(e)[:20]}", None, None))
        print(f"[{i+1}/{len(rows)}] Error on {url}: {e}")

conn.close()

with open("scripts/cv_audit_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nAudit saved to scripts/cv_audit_results.json")
