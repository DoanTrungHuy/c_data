import sqlite3
import re
import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT id, title, company_name, source_platform, source_url, location_province, location_district, category, description FROM jobs")
jobs = c.fetchall()

print(f"Total jobs in DB: {len(jobs)}")

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=10.0,
    follow_redirects=True,
    verify=False
)

# Test 10 CareerViet jobs from DB to inspect actual page title and H1
for i, j in enumerate(jobs[:10]):
    jid, title, comp, platform, url, prov, dist, cat, desc = j
    try:
        r = client.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        h1 = soup.find("h1")
        h1_text = h1.get_text(strip=True) if h1 else "NO_H1"
        title_tag = soup.find("title")
        page_title = title_tag.get_text(strip=True) if title_tag else "NO_TITLE"
        # Check location on page
        loc_el = soup.select_one(".map p, .location, .job-location")
        page_loc = loc_el.get_text(strip=True) if loc_el else "NO_LOC"
        
        print(f"\n--- Job {i+1}: {title[:40]} ---")
        print(f"  URL: {url}")
        print(f"  Status: {r.status_code}")
        print(f"  Page H1: {h1_text[:60]}")
        print(f"  Page Loc: {page_loc}")
        print(f"  DB Prov: {prov}, Dist: {dist}")
    except Exception as e:
        print(f"\n--- Job {i+1} Error: {e}")
