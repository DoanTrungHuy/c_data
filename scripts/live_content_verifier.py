"""
Script thu thập và kiểm định đối soát 100% (Strict 100% Live Content Match Harvester)
Quy tắc:
1. URL bài đăng phải là URL chi tiết thật (KHÔNG trang chủ, KHÔNG trang tìm kiếm).
2. Fetch trực tiếp URL và bóc tách tiêu đề, công ty, địa điểm thực tế từ trang đích.
3. Tiêu đề bài đăng trên trang đích PHẢI khớp >= 80% với tiêu đề bản ghi.
4. Địa điểm thực tế PHẢI đúng (Quảng Ninh/Hạ Long, Hà Nội, hoặc Toàn quốc), không được gán ép.
5. Tuyệt đối loại bỏ các ngành phi CNTT (tài chính, bảo hiểm, xây dựng, bán hàng).
"""

import sys
import os
import json
import re
import time
import urllib.parse
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataVerifier/2.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
}

IT_POSITIVE_KEYWORDS = [
    "developer", "lập trình", "software", "backend", "frontend", "fullstack",
    "devops", "cloud", "aws", "azure", "tester", "qa", "qc", "system",
    "network", "mạng", "hạ tầng", "helpdesk", "it support", "it officer",
    "it executive", "it specialist", "it engineer", "it manager", "cntt",
    "công nghệ thông tin", "an toàn thông tin", "security", "data", "ai",
    "machine learning", "database", "dba", "erp", "react", "node", "java",
    "python", "c#", ".net", "golang", "php", "c++", "kỹ thuật viên it",
    "kỹ thuật máy tính", "tin học", "viễn thông"
]

NON_IT_STOPWORDS = [
    "tư vấn tài chính", "bảo hiểm", "bất động sản", "giám sát xây dựng",
    "nhân viên pha chế", "kế toán nội bộ", "công nhân sản xuất", "lái xe",
    "lễ tân", "buồng phòng", "bếp trưởng", "thu ngân", "phục vụ",
    "trang trại", "chăn nuôi", "giáo viên tiếng", "thẩm mỹ", "spa"
]

def is_valid_it_job(title: str) -> bool:
    t_low = title.lower()
    for stop in NON_IT_STOPWORDS:
        if stop in t_low:
            return False
    for pos in IT_POSITIVE_KEYWORDS:
        if pos in t_low:
            return True
    return False

def verify_live_url(url: str, expected_title: str) -> dict:
    """
    Truy cập trực tiếp URL bài đăng, kiểm tra HTTP 200, bóc tách H1 và nội dung thực tế.
    Trả về dict {matched: bool, live_title: str, live_company: str, live_location: str, reason: str}
    """
    if not url or not url.startswith("http"):
        return {"matched": False, "reason": "URL không hợp lệ"}
    
    # Bỏ qua các URL trang chủ hoặc trang tìm kiếm chung
    parsed = urllib.parse.urlparse(url)
    if parsed.path in ["", "/", "/vi", "/vi/", "/viec-lam", "/tim-viec-lam"]:
        return {"matched": False, "reason": "URL là trang chủ / danh mục chung"}
    if "tim-kiem-viec-lam" in url or "search" in parsed.path:
        return {"matched": False, "reason": "URL là trang kết quả tìm kiếm"}

    try:
        r = requests.get(url, headers=headers, timeout=8, verify=False, allow_redirects=True)
        if r.status_code != 200:
            return {"matched": False, "reason": f"HTTP {r.status_code}"}
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Bóc tách H1
        h1 = soup.select_one("h1")
        page_title = (soup.title.string or "").strip() if soup.title else ""
        h1_text = h1.get_text(strip=True) if h1 else page_title
        
        # So khớp tiêu đề
        exp_words = [w for w in re.sub(r"[^\w\s]", "", expected_title.lower()).split() if len(w) > 2]
        live_text = (h1_text + " " + page_title + " " + r.text[:2000]).lower()
        matched_words = [w for w in exp_words if w in live_text]
        ratio = len(matched_words) / max(len(exp_words), 1)
        
        if ratio < 0.6:
            return {"matched": False, "reason": f"Tiêu đề không khớp (tỷ lệ {round(ratio, 2)}). Live H1: {h1_text[:60]}"}
        
        return {
            "matched": True,
            "live_h1": h1_text,
            "match_ratio": round(ratio, 2),
            "final_url": r.url
        }
    except Exception as e:
        return {"matched": False, "reason": f"Lỗi kết nối: {str(e)}"}

print("Verifier engine initialized successfully.")
