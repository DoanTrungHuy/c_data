import json
import re
import sys
import httpx

sys.stdout.reconfigure(encoding="utf-8")

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=10.0,
    verify=False
)

url = "https://careerviet.vn/vi/tim-viec-lam/tat-ca-viec-lam-tai-quang-ninh-l28-vi.html"
r = client.get(url)
print("Status:", r.status_code)

match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text)
if match:
    data = json.loads(match.group(1))
    print("Found __NEXT_DATA__!")
    props = data.get("props", {}).get("pageProps", {})
    print("pageProps keys:", list(props.keys()))
    
    # Check for job list in props
    for k, v in props.items():
        if isinstance(v, list) and len(v) > 0:
            print(f"Key '{k}' is list with {len(v)} items")
            if isinstance(v[0], dict):
                print("  Sample item keys:", list(v[0].keys())[:8])
                title = v[0].get("JOB_TITLE") or v[0].get("job_title") or v[0].get("title")
                print("  Sample title:", title)
        elif isinstance(v, dict):
            print(f"Key '{k}' is dict with keys:", list(v.keys())[:8])
else:
    print("No __NEXT_DATA__ script found.")
