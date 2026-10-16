import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import requests

sys.stdout.reconfigure(encoding="utf-8")

json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "jobs.json"))
with open(json_path, "r", encoding="utf-8") as f:
    jobs = json.load(f)

real_cv = [j for j in jobs if "careerviet.vn" in j.get("source_url", "") and "?jid=" not in j.get("source_url", "")]
print(f"Checking {len(real_cv)} CareerViet jobs...")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def check_cv(j):
    url = j["source_url"]
    title = j["title"]
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code != 200:
            return {"id": j["id"], "title": title, "url": url, "status": r.status_code, "match": False, "reason": f"Status {r.status_code}"}
        
        soup = BeautifulSoup(r.text, "html.parser")
        h1 = soup.find("h1")
        if not h1:
            return {"id": j["id"], "title": title, "url": url, "status": 200, "match": False, "reason": "No H1"}
        
        h1_text = h1.get_text(strip=True)
        if "không tìm thấy" in h1_text.lower() or "404" in h1_text.lower() or "đã hết hạn" in h1_text.lower():
            return {"id": j["id"], "title": title, "url": url, "status": 200, "match": False, "reason": "Expired/Not found in H1"}
            
        # Check if title matches h1
        # Normalize
        t1 = title.lower().replace(" ", "").replace("-", "").replace("/", "")
        t2 = h1_text.lower().replace(" ", "").replace("-", "").replace("/", "")
        
        # Levenshtein or substring
        match = (t1 in t2) or (t2 in t1)
        return {
            "id": j["id"],
            "title": title,
            "live_h1": h1_text,
            "url": url,
            "status": 200,
            "match": match,
            "reason": "OK" if match else "Title mismatch"
        }
    except Exception as e:
        return {"id": j["id"], "title": title, "url": url, "status": 0, "match": False, "reason": str(e)[:30]}

with ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(check_cv, real_cv))

matches = [r for r in results if r["match"]]
mismatches = [r for r in results if not r["match"]]

print(f"\nTotal: {len(real_cv)}")
print(f"Matches: {len(matches)}")
print(f"Mismatches / Errors: {len(mismatches)}")

if mismatches:
    print("\nSample mismatches:")
    for m in mismatches[:15]:
        print(f"[{m['id']}] DB Title: {m['title']}\n  Live: {m.get('live_h1', 'N/A')}\n  URL: {m['url']}\n  Reason: {m['reason']}")
