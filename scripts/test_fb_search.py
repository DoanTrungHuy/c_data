import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

queries = [
    'site:facebook.com "tuyển dụng" "IT" "Hạ Long"',
    'site:facebook.com "tuyển dụng" "IT" "Quảng Ninh"',
    'site:facebook.com "tuyển dụng" "kỹ thuật máy tính" "Hạ Long"',
    'site:facebook.com "tuyển dụng IT" "Hà Nội"',
    'site:facebook.com/groups "Tuyển dụng IT"',
    'site:facebook.com "tuyển dụng" "lập trình viên" "Quảng Ninh"',
]

for q in queries:
    print(f"\n--- Query: {q} ---")
    try:
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": q}, headers=headers, timeout=10)
        print("Status:", r.status_code)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            results = soup.select(".result__body")
            print("Results count:", len(results))
            for res in results[:3]:
                title_el = res.select_one(".result__title a")
                snippet_el = res.select_one(".result__snippet")
                title = title_el.get_text(strip=True) if title_el else ""
                href = title_el.get("href", "") if title_el else ""
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                
                # Unwrap duckduckgo uddg param
                if "uddg=" in href:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    real_url = parsed.get("uddg", [href])[0]
                else:
                    real_url = href
                print(f"Title: {title}")
                print(f"URL: {real_url}")
                print(f"Snippet: {snippet[:120]}...")
    except Exception as e:
        print("Error:", e)
