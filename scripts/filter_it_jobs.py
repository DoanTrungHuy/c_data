import sqlite3
import re
import sys
import json
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

c.execute("SELECT id, title, company_name, source_platform, source_url, location_province, location_district, category FROM jobs")
jobs = c.fetchall()

print(f"Total jobs in DB: {len(jobs)}")

it_kw = [
    'it', 'cntt', 'lập trình', 'developer', 'software', 'phần mềm',
    'hệ thống', 'mạng', 'helpdesk', 'devops', 'tester', 'qa', 'qc',
    'dữ liệu', 'data', 'công nghệ thông tin', 'kỹ sư phần mềm',
    'security', 'an toàn thông tin', 'ai', 'cloud', 'system', 'database',
    'vi tính', 'frontend', 'backend', 'fullstack', 'react', 'python'
]

# Non-IT keywords that might falsely trigger 'it' or 'qa'
non_it_filters = [
    'nội thất', 'bất động sản', 'an toàn lao động', 'thủ kho',
    'quản lý cửa hàng', 'giao dịch viên', 'kinh doanh b2b', 'sales b2b',
    'logistics supervisor', 'admin executive', 'customer advisor',
    'clerk, operations', 'phòng giao dịch', 'định giá tài sản',
    'tư vấn giám sát', 'sales thị trường', 'lễ tân', 'phục vụ', 'lái xe',
    'chuyên viên khách hàng', 'tập sự chuyên viên'
]

valid_it_jobs = []
dropped_jobs = []

for j in jobs:
    jid, title, comp, platform, url, prov, dist, cat = j
    t_low = title.lower()
    cat_low = (cat or "").lower()
    
    # Check if clearly non-IT
    if any(n in t_low for n in non_it_filters) and not any(k in t_low for k in ['công nghệ thông tin', 'lập trình', 'developer', 'software']):
        dropped_jobs.append((jid, title, comp, url, "non_it_filter"))
        continue
        
    # Check if IT
    is_it = False
    for kw in it_kw:
        if kw in ['it', 'qa', 'qc', 'ai']:
            if re.search(r'\b' + kw + r'\b', t_low) or re.search(r'\b' + kw + r'\b', cat_low):
                is_it = True
                break
        else:
            if kw in t_low or kw in cat_low:
                is_it = True
                break
                
    if not is_it:
        dropped_jobs.append((jid, title, comp, url, "not_it_role"))
        continue
        
    valid_it_jobs.append(j)

print(f"Valid IT candidates: {len(valid_it_jobs)}")
print(f"Dropped non-IT: {len(dropped_jobs)}")

# Print sample of IT jobs
print("\n--- Valid IT sample (first 15): ---")
for j in valid_it_jobs[:15]:
    print(f"- {j[1]} | {j[2]} | {j[4]}")
