import json
import requests
import sys
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Bắt đầu kiểm tra toàn diện {len(jobs)} URL việc làm...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_url(item):
    idx, j = item
    url = j.get("source_url", "")
    comp = j.get("company_name", "")
    title = j.get("title", "")
    plat = j.get("source_platform", "")
    
    # Check if URL has dummy hashes or query params
    issues = []
    if "#it-" in url or "#" in url:
        issues.append("HAS_DUMMY_HASH")
    if "?post_ref=" in url or "?ref=" in url:
        issues.append("HAS_DUMMY_QUERY")
        
    try:
        # Check URL without fragment
        clean_url = url.split("#")[0]
        resp = requests.head(clean_url, headers=headers, timeout=5, allow_redirects=True)
        status = resp.status_code
        if status in [404, 403, 500, 502, 503]:
            # Retry with GET in case HEAD is blocked
            try:
                resp = requests.get(clean_url, headers=headers, timeout=5, stream=True)
                status = resp.status_code
            except Exception:
                pass
    except Exception as e:
        status = f"ERROR: {str(e)[:40]}"

    return {
        "index": idx,
        "title": title,
        "company": comp,
        "platform": plat,
        "url": url,
        "status": status,
        "issues": issues,
    }

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(check_url, enumerate(jobs)))

bad_urls = [r for r in results if r["status"] == 404 or str(r["status"]).startswith("ERROR") or len(r["issues"]) > 0]

print(f"\nKẾT QUẢ KIỂM TRA:")
print(f"Tổng số URL đã kiểm tra: {len(results)}")
print(f"Tổng số URL có vấn đề (404 / lỗi / hash / param giả): {len(bad_urls)}")
print("=" * 70)
for b in bad_urls[:35]:
    print(f"[{b['index']+1}] {b['title'][:30]} | {b['company'][:25]}")
    print(f"     URL: {b['url']}")
    print(f"     Status: {b['status']} | Issues: {b['issues']}")
