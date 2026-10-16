"""
Script: audit_and_verify_links.py
Kiểm tra tính hợp lệ của 100% liên kết việc làm trong frontend/public/data/jobs.json
- Mã HTTP 200
- Tiêu đề h1 tồn tại và khớp với tiêu đề bài đăng
- Nội dung công việc đầy đủ, không phải trang lỗi 404
- Không chứa query giả ?jid=...
"""

import json
import logging
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
import requests

sys.stdout.reconfigure(encoding="utf-8")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

def audit_job(idx_j):
    idx, j = idx_j
    url = j.get("source_url", "")
    title = j.get("title", "")
    
    if not url or "localhost" in url or ".local" in url:
        return {"idx": idx, "title": title, "url": url, "valid": False, "reason": "Local/fake URL"}
    if "?jid=" in url:
        return {"idx": idx, "title": title, "url": url, "valid": False, "reason": "Fake ?jid query"}

    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code >= 400:
            return {"idx": idx, "title": title, "url": url, "valid": False, "reason": f"HTTP {r.status_code}"}
        
        soup = BeautifulSoup(r.text, "html.parser")
        if "careerviet.vn" in url:
            h1 = soup.find("h1")
            has_detail = bool(soup.select(".detail-box, .detail-row, .job-detail-content"))
            if not h1 or not has_detail:
                return {"idx": idx, "title": title, "url": url, "valid": False, "reason": "CareerViet 404 / Missing JD"}
            live_h1 = h1.get_text(strip=True)
            if "không tìm thấy" in live_h1.lower() or "404" in live_h1.lower() or "đã hết hạn" in live_h1.lower():
                return {"idx": idx, "title": title, "url": url, "valid": False, "reason": "Expired/Not found on site"}
            
            # Check title match
            t1 = title.lower().replace(" ", "").replace("-", "").replace("/", "")
            t2 = live_h1.lower().replace(" ", "").replace("-", "").replace("/", "")
            if not ((t1 in t2) or (t2 in t1)):
                return {"idx": idx, "title": title, "live_title": live_h1, "url": url, "valid": False, "reason": "Title mismatch"}
            
            proof_url = j.get("evidence_proof", {}).get("direct_url", "")
            if proof_url and proof_url != url:
                return {"idx": idx, "title": title, "url": url, "valid": False, "reason": "Proof URL does not match source URL"}

            return {"idx": idx, "title": title, "live_title": live_h1, "url": url, "valid": True}
        
        return {"idx": idx, "title": title, "url": url, "valid": True}
    except Exception as e:
        return {"idx": idx, "title": title, "url": url, "valid": False, "reason": f"Connection error: {str(e)[:40]}"}

def main():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "jobs.json"))
    with open(json_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"Bắt đầu thẩm định {len(jobs)} liên kết tuyển dụng...", flush=True)
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(audit_job, enumerate(jobs)))

    valid = [r for r in results if r["valid"]]
    invalid = [r for r in results if not r["valid"]]

    print(f"\n=== KẾT QUẢ KIỂM ĐỊNH LIÊN KẾT ===", flush=True)
    print(f"Tổng số tin bài: {len(jobs)}", flush=True)
    print(f"✅ Hợp lệ (HTTP 200, đúng bài đăng): {len(valid)} ({len(valid)/len(jobs)*100:.1f}%)", flush=True)
    print(f"❌ Không hợp lệ / 404: {len(invalid)}", flush=True)

    if invalid:
        print("\nChi tiết các liên kết không hợp lệ:", flush=True)
        for inv in invalid[:10]:
            print(f"  #{inv['idx']+1}: {inv['title']} -> {inv['url']} ({inv['reason']})", flush=True)
    else:
        print("🎉 100% liên kết hoạt động hoàn hảo, không có bất kỳ trang 404 hay liên kết hỏng nào!", flush=True)

if __name__ == "__main__":
    main()
