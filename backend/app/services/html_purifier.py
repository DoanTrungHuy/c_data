"""
HTML Purifier & Markdown Converter Service (Inspired by Firecrawl & Crawlee).
Làm sạch mã HTML từ các trang tuyển dụng, loại bỏ thẻ rác, quảng cáo, tracking,
và chuyển đổi nội dung mô tả công việc (JD) thành văn bản Markdown chuẩn mực cho AI/RAG.
"""

from bs4 import BeautifulSoup
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple


# Các thẻ HTML gây nhiễu cần loại bỏ hoàn toàn
NOISE_TAGS = [
    "script", "style", "noscript", "svg", "nav", "header", "footer",
    "aside", "form", "iframe", "button", "input", "select", "textarea",
    "meta", "link"
]

# Các thuộc tính theo dõi / quảng cáo cần dọn dẹp
NOISE_ATTRS = [
    "onclick", "onload", "data-tracking", "data-analytics", "data-ad",
    "data-gtm", "style", "class", "id"
]


def purify_html_to_markdown(raw_html: str) -> str:
    """
    Chuyển đổi raw HTML phức tạp thành Markdown tinh gọn (Firecrawl pattern).
    """
    if not raw_html or not raw_html.strip():
        return ""

    try:
        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Loại bỏ toàn bộ thẻ gây nhiễu
        for tag_name in NOISE_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 2. Chuyển đổi các thẻ tiêu đề thành Markdown
        for level in range(1, 7):
            for h in soup.find_all(f"h{level}"):
                text = h.get_text().strip()
                if text:
                    h.replace_with(f"\n\n{'#' * level} {text}\n")
                else:
                    h.decompose()

        # 3. Chuyển đổi thẻ danh sách (ul, ol, li)
        for li in soup.find_all("li"):
            text = li.get_text().strip()
            if text:
                li.replace_with(f"\n- {text}")
            else:
                li.decompose()

        # 4. Chuyển đổi in đậm / in nghiêng
        for strong in soup.find_all(["strong", "b"]):
            text = strong.get_text().strip()
            if text:
                strong.replace_with(f" **{text}** ")
            else:
                strong.decompose()

        for em in soup.find_all(["em", "i"]):
            text = em.get_text().strip()
            if text:
                em.replace_with(f" *{text}* ")
            else:
                em.decompose()

        # 5. Chuyển đổi ngắt dòng <br> và đoạn văn <p>
        for br in soup.find_all("br"):
            br.replace_with("\n")

        for p in soup.find_all("p"):
            text = p.get_text().strip()
            if text:
                p.replace_with(f"\n\n{text}\n")
            else:
                p.decompose()

        # 6. Lấy toàn văn
        text = soup.get_text()

        # 7. Dọn dẹp khoảng trắng dư thừa
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        lines = [line.strip() for line in text.split("\n")]
        cleaned = "\n".join(lines).strip()
        return cleaned

    except Exception:
        # Fallback cơ bản bằng Regex nếu lỗi parser
        clean = re.sub(r"<[^>]+>", " ", raw_html)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean


def compute_job_fingerprint(source_url: str, title: str, company: str) -> str:
    """
    Tạo dấu vân tay MD5 để khử trùng lặp (Scrapy / Crawlee deduplication filter).
    Chuẩn hóa URL bỏ query parameter tracking (fbclid, utm_*, ref...).
    """
    norm_url = re.sub(r"\?.*$", "", (source_url or "").strip().lower())
    norm_title = re.sub(r"\s+", " ", (title or "").strip().lower())
    norm_company = re.sub(r"\s+", " ", (company or "").strip().lower())

    key = f"{norm_url}::{norm_title}::{norm_company}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def extract_contacts_and_salary_from_text(text: str) -> Dict[str, Any]:
    """
    Trích xuất tự động số điện thoại, email và mức lương từ văn bản đã được làm sạch.
    """
    phones = re.findall(r"(?:(?:0|\+84)[35789](?:[.\s]?\d){8}\b)|(?:0203(?:[.\s]?\d){6,7}\b)", text)
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)

    # Loại bỏ email rác hệ thống và dọn dấu chấm cuối câu
    clean_emails = [
        e.rstrip(".,;:!?)") for e in emails
        if not any(x in e.lower() for x in ["example", "sentry", "wixpress", "support@facebook"])
    ]

    # Tìm mẫu lương
    salary_match = re.search(
        r"(\d{1,2}(?:\s*[-–đến]\s*\d{1,2})?)\s*(?:triệu|tr|vnđ|vnd|usd|\$)",
        text,
        re.IGNORECASE
    )

    return {
        "phones": list(dict.fromkeys(phones)),
        "emails": list(dict.fromkeys(clean_emails)),
        "salary_hint": salary_match.group(0).strip() if salary_match else None,
    }
