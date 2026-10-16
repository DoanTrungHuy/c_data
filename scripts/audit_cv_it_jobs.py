import sqlite3
import re
import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

# Get all CareerViet jobs in DB
c.execute("SELECT id, title, company_name, source_url, location_province, location_district, category FROM jobs WHERE source_url LIKE '%careerviet.vn%'")
cv_rows = c.fetchall()

print(f"Total CareerViet jobs in DB: {len(cv_rows)}")

# Check IT keywords
it_keywords = [
    'it', 'cntt', 'lập trình', 'developer', 'software', 'phần mềm',
    'hệ thống', 'mạng', 'helpdesk', 'devops', 'tester', 'qa', 'qc',
    'dữ liệu', 'data', 'công nghệ thông tin', 'kỹ sư phần mềm',
    'security', 'an toàn thông tin', 'ai', 'cloud', 'system', 'database'
]

cv_it_jobs = []
for r in cv_rows:
    t = r[1].lower()
    cat = (r[6] or "").lower()
    # Check word boundary for short keywords like 'it', 'qa', 'qc', 'ai'
    is_it = False
    for kw in it_keywords:
        if kw in ['it', 'qa', 'qc', 'ai']:
            if re.search(r'\b' + kw + r'\b', t) or re.search(r'\b' + kw + r'\b', cat):
                is_it = True
                break
        else:
            if kw in t or kw in cat:
                is_it = True
                break
    if is_it:
        cv_it_jobs.append(r)

print(f"CareerViet IT jobs in DB: {len(cv_it_jobs)}")
for j in cv_it_jobs:
    print(f"- {j[1]} | {j[2]} | {j[4]}")
