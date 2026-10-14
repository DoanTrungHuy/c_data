import re
import sys
import httpx
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

url = "https://careerviet.vn/vi/tim-viec-lam/IT-tai-quang-ninh-k4-l28-vi.html"
client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"},
    timeout=10.0,
    follow_redirects=True,
    verify=False,
)

r = client.get(url)
print("Status:", r.status_code, "Final URL:", r.url)

links = re.findall(r'href="([^"]*tim-viec-lam/[^"]*\.html)"', r.text)
unique_links = list(set(links))
print(f"Found {len(unique_links)} job links with regex:")
for l in unique_links[:10]:
    print(" ", l)
