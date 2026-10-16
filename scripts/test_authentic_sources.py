import urllib.request
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}

def test_url(url):
    print(f"\n--- Testing: {url} ---")
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
            title_m = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE | re.DOTALL)
            title = title_m.group(1).strip() if title_m else 'No title'
            print(f"Status: {resp.status}, Title: {title}")
            return body
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test TopCV IT in Ha Long
body = test_url('https://www.topcv.vn/viec-lam-it/tp-ha-long-quang-ninh')
if body:
    job_links = set(re.findall(r'href="(https://www\.topcv\.vn/viec-lam/[a-zA-Z0-9\-]+/\d+\.html)"', body))
    print(f"Found {len(job_links)} TopCV job links:")
    for l in list(job_links)[:10]:
        print("  -", l)
