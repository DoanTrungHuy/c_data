import sqlite3
import re
import sys
import json
import httpx
from bs4 import BeautifulSoup
import time

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

# Get all CareerViet jobs in DB that are IT
c.execute("SELECT id, title, company_name, source_platform, source_url, location_province, location_district, category FROM jobs WHERE source_url LIKE '%careerviet.vn%'")
rows = c.fetchall()

it_kw = [
    'it', 'cntt', 'lập trình', 'developer', 'software', 'phần mềm',
    'hệ thống', 'mạng', 'helpdesk', 'devops', 'tester', 'qa', 'qc',
    'dữ liệu', 'data', 'công nghệ thông tin', 'kỹ sư phần mềm',
    'security', 'an toàn thông tin', 'ai', 'cloud', 'system', 'database',
    'vi tính', 'frontend', 'backend', 'fullstack', 'react', 'python',
    'kỹ thuật viên', 'network', 'chuyển đổi số'
]

non_it_filters = [
    'nội thất', 'bất động sản', 'an toàn lao động', 'thủ kho',
    'quản lý cửa hàng', 'giao dịch viên', 'kinh doanh b2b', 'sales b2b',
    'logistics supervisor', 'admin executive', 'customer advisor',
    'clerk, operations', 'phòng giao dịch', 'định giá tài sản',
    'tư vấn giám sát', 'sales thị trường', 'lễ tân', 'phục vụ', 'lái xe',
    'chuyên viên khách hàng', 'tập sự chuyên viên', 'nhập liệu chứng từ',
    'nhân sự', 'sales representative', 'phó phòng cơ điện', 'asm -',
    'chuyên viên quan hệ khách hàng', 'cán bộ tư vấn giám sát',
    'dệt may', 'textile', 'quy nhon office manager', 'bảo trì máy bia',
    'sales executive -', 'store manager', 'legal specialist', 'marketing',
    'water treatment', 'printing', 'hvac', 'đào tạo và phát triển hệ thống'
]

cv_it_rows = []
for r in rows:
    t_low = r[1].lower()
    cat_low = (r[7] or "").lower()
    if any(n in t_low for n in non_it_filters) and not any(k in t_low for k in ['công nghệ thông tin', 'lập trình', 'developer', 'software', 'it helpdesk', 'it officer', 'it support']):
        continue
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
    if is_it:
        cv_it_rows.append(r)

print(f"Total CareerViet IT rows to verify: {len(cv_it_rows)}")

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=8.0,
    follow_redirects=True,
    verify=False
)

results = []
for i, (jid, title, comp, platform, url, prov, dist, cat) in enumerate(cv_it_rows):
    try:
        r = client.get(url)
        if r.status_code != 200:
            results.append({"id": jid, "title": title, "status": r.status_code, "valid": False, "reason": "http_error"})
            continue
        
        soup = BeautifulSoup(r.text, "html.parser")
        h1 = soup.find("h1")
        h1_text = h1.get_text(strip=True) if h1 else ""
        
        # Check title similarity
        title_clean = re.sub(r'[\(\)\[\]\-\:\,\.\/]', '', title.lower()).strip()
        h1_clean = re.sub(r'[\(\)\[\]\-\:\,\.\/]', '', h1_text.lower()).strip()
        
        # Check if expired or not found
        expired_msg = soup.select_one(".job-expired, .expired-alert, .alert-danger")
        is_expired = False
        if expired_msg and ("hết hạn" in expired_msg.get_text().lower() or "đã đóng" in expired_msg.get_text().lower()):
            is_expired = True
            
        loc_el = soup.select_one(".map p, .location, .job-location")
        loc_text = loc_el.get_text(strip=True) if loc_el else ""
        
        # Company
        comp_el = soup.select_one(".employer-name, .company-name, .employer, a.employer")
        comp_text = comp_el.get_text(strip=True) if comp_el else comp
        
        # JD description
        desc_el = soup.select_one(".detail-row, .job-description, .content-tab")
        has_jd = bool(desc_el and len(desc_el.get_text().strip()) > 50)
        
        results.append({
            "id": jid,
            "title": title,
            "h1": h1_text,
            "company": comp_text,
            "location_raw": loc_text,
            "url": url,
            "has_jd": has_jd,
            "is_expired": is_expired,
            "valid": bool(h1_text and has_jd and not is_expired),
        })
        print(f"[{i+1}/{len(cv_it_rows)}] {'VALID' if (h1_text and has_jd and not is_expired) else 'INVALID'}: {title[:35]} | Loc: {loc_text[:20]}")
    except Exception as e:
        results.append({"id": jid, "title": title, "valid": False, "error": str(e)})
        print(f"[{i+1}/{len(cv_it_rows)}] ERROR: {title[:35]} -> {e}")

valid_count = sum(1 for r in results if r.get("valid"))
print(f"\nAudit complete! Valid IT CareerViet jobs: {valid_count} / {len(cv_it_rows)}")

with open("scripts/cv_verified_it_jobs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
