import httpx
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

url = "https://careerviet.vn/vi/tim-viec-lam/katinat-vung-tau-quan-ly-cua-hang.35C87067.html"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"}

try:
    r = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
    print("Status:", r.status_code)
    print("Final URL:", r.url)
    titles = re.findall(r'<title>(.*?)</title>', r.text, re.IGNORECASE)
    print("Title:", titles[0] if titles else "None")
    
    # Check employer / company in CareerViet HTML
    employers = re.findall(r'class="employer-name"[^>]*>([^<]+)<', r.text)
    if not employers:
        employers = re.findall(r'class="company-name"[^>]*>([^<]+)<', r.text)
    if not employers:
        employers = re.findall(r'"hiringOrganization":\s*\{\s*"@type":\s*"Organization",\s*"name":\s*"([^"]+)"', r.text)
    print("Employer matches:", employers)
except Exception as e:
    print("Error:", e)
