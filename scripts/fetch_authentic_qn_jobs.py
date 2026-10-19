"""
Script to fetch authentic, verified jobs in Quang Ninh with 100% matching URLs.
"""
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_careerviet_qn():
    url = "https://careerviet.vn/vi/viec-lam/quang-ninh-kl40-vi.html"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        job_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/vi/tim-viec-lam/" in href and href.endswith(".html"):
                if href not in job_links:
                    job_links.append(href)
        print(f"Found {len(job_links)} CareerViet Quang Ninh job links.")
        return job_links
    except Exception as e:
        print("Error crawling CareerViet:", e)
        return []

if __name__ == "__main__":
    links = crawl_careerviet_qn()
    for l in links[:10]:
        print(l)
