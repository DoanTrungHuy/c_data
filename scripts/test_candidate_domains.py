import httpx
import sys

sys.stdout.reconfigure(encoding="utf-8")

candidates = {
    "BV Da Khoa QN": [
        "https://bvdktquangninh.vn/",
        "https://benhviendakhoa.quangninh.gov.vn/",
        "https://quangninh.gov.vn/",
        "https://soytequangninh.gov.vn/"
    ],
    "CALOFIC": [
        "http://calofic.com.vn/",
        "https://www.wilmar-international.com/",
        "https://career.wilmar-clv.com/"
    ],
    "Dong Tau Ha Long": [
        "https://sbic.com.vn/",
        "http://www.halongshipyard.vn/",
        "https://dongtauhalong.com.vn/"
    ],
    "Nhiet Dien QTP": [
        "https://qtp.vn/",
        "http://qtp.com.vn/",
        "https://www.evngenco1.com.vn/"
    ],
    "Central Retail": [
        "https://go-vietnam.vn/",
        "https://www.centralretail.com/vn/",
        "https://centralretail.com/"
    ]
}

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=8.0,
    follow_redirects=True,
    verify=False
)

for group, clist in candidates.items():
    print(f"\n--- {group} ---")
    for url in clist:
        try:
            r = client.get(url, timeout=6.0)
            print(f"[{r.status_code}] {url} -> {r.url}")
        except Exception as e:
            print(f"[ERR] {url} -> {str(e)[:35]}")
