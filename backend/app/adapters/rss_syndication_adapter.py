"""
RSS / Atom Syndication Job Adapter for C_Data Platform.
Dedicated XML feed parser for government and open syndication labor portals (vieclamvietnam.gov.vn).
Completely isolated XML parser with incremental crawl and error handling.
"""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import logging
import re
import time
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

import requests

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from crawlers.utils import extract_salary_range, normalize_location

logger = logging.getLogger("c_data.adapters.rss")

DEFAULT_FEED_URL = "https://vieclamvietnam.gov.vn/rss/viec-lam"


class RssSyndicationAdapter(BaseJobAdapter):
    """
    Adapter thu thập dữ liệu qua chuẩn RSS 2.0 / Atom XML.
    Tách biệt hoàn toàn với HTML parser của các trang việc làm khác.
    """

    adapter_id = "government_rss"
    source_name = "Cổng Thông Tin Việc Làm Quốc Gia (RSS)"
    source_domain = "vieclamvietnam.gov.vn"
    feed_url = DEFAULT_FEED_URL

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "C_DataRSSBot/1.0 (+https://cdata.vn/bot)",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9",
        })

    def parse_xml_feed(
        self,
        xml_content: str,
        target_url: str = DEFAULT_FEED_URL,
        since_timestamp: Optional[datetime] = None,
        limit: int = 20,
    ) -> AdapterCrawlResult:
        """
        Bóc tách XML RSS 2.0 độc lập.
        Có thể chạy offline trên fixture XML để kiểm thử hồi quy.
        """
        result = AdapterCrawlResult(
            source_id=self.adapter_id,
            source_name=self.source_name,
            raw_metadata={"feed_url": target_url},
        )

        try:
            root = ET.fromstring(xml_content)
            # Hỗ trợ cả chuẩn channel/item (RSS 2.0) và feed/entry (Atom)
            items = root.findall(".//item")
            if not items:
                # Thử tìm entry theo Atom namespace
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

            result.total_detected = len(items)

            def _find_elem(el, tags):
                for t in tags:
                    f = el.find(t)
                    if f is not None:
                        return f
                return None

            for it in items:
                if len(result.items) >= limit:
                    break

                # Trích xuất title
                title_elem = _find_elem(it, ["title", "{http://www.w3.org/2005/Atom}title"])
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                if not title:
                    continue

                # Trích xuất link & guid
                link_elem = _find_elem(it, ["link", "{http://www.w3.org/2005/Atom}link"])
                link = ""
                if link_elem is not None:
                    link = link_elem.text.strip() if link_elem.text else link_elem.get("href", "")

                guid_elem = _find_elem(it, ["guid", "id", "{http://www.w3.org/2005/Atom}id"])
                guid = guid_elem.text.strip() if guid_elem is not None and guid_elem.text else link
                source_job_id = re.sub(r"[^0-9a-zA-Z_-]", "_", guid[-40:])

                # Trích xuất pubDate
                pub_elem = _find_elem(it, ["pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}updated"])
                posted_date = None
                if pub_elem is not None and pub_elem.text:
                    try:
                        posted_date = parsedate_to_datetime(pub_elem.text)
                        if not posted_date.tzinfo:
                            posted_date = posted_date.replace(tzinfo=timezone.utc)
                    except Exception:
                        pass

                # Incremental crawl: bỏ qua nếu bài đăng cũ hơn since_timestamp
                if since_timestamp and posted_date and posted_date < since_timestamp:
                    continue

                # Trích xuất tác giả / công ty
                author_elem = _find_elem(it, ["author", "{http://purl.org/dc/elements/1.1/}creator", "{http://www.w3.org/2005/Atom}author"])
                company_name = author_elem.text.strip() if author_elem is not None and author_elem.text else "Cơ quan tuyển dụng nhà nước"

                # Trích xuất description
                desc_elem = _find_elem(it, ["description", "summary", "{http://purl.org/rss/1.0/modules/content/}encoded", "{http://www.w3.org/2005/Atom}summary"])
                description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                # Trích xuất mức lương và địa điểm từ nội dung RSS
                sal_min, sal_max = extract_salary_range(description)
                loc_norm = normalize_location(description)

                is_fixture = "[FIXTURE_TEST_ONLY]" in title or "[FIXTURE_TEST_ONLY]" in xml_content

                item = RawJobRecord(
                    source_job_id=source_job_id,
                    title=title,
                    company_name=company_name,
                    source_url=link,
                    apply_url=link,
                    salary_text="Theo quy định",
                    salary_min=sal_min,
                    salary_max=sal_max,
                    location_raw=loc_norm.get("province") or "Toàn quốc",
                    location_province=loc_norm.get("province"),
                    location_district=loc_norm.get("district"),
                    workplace_type="onsite",
                    employment_type="full-time",
                    description=description,
                    posted_at=posted_date,
                    status="active_likely",
                    status_evidence="Nguồn mở từ Cổng Thông tin Việc làm Quốc gia (RSS)",
                    extraction_confidence=0.95,
                    location_confidence=0.85 if loc_norm.get("province") else 0.5,
                    raw_data_reference={"rss_guid": guid, "feed_url": target_url},
                    is_test_fixture=is_fixture,
                )
                result.items.append(item)

        except ET.ParseError as e:
            logger.error(f"Lỗi cú pháp XML RSS: {e}")
            result.errors.append(
                AdapterError(
                    error_type=AdapterErrorType.PARSE_ERROR,
                    message=f"Lỗi cú pháp XML RSS: {str(e)}",
                    url=target_url,
                )
            )
        except Exception as e:
            logger.error(f"Lỗi bóc tách RSS feed: {e}")
            result.errors.append(
                AdapterError(
                    error_type=AdapterErrorType.UNKNOWN,
                    message=f"Lỗi không xác định khi đọc RSS: {str(e)}",
                    url=target_url,
                )
            )

        return result

    def discover_jobs(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        page: int = 1,
        cursor: Optional[str] = None,
        limit: int = 20,
        since_timestamp: Optional[datetime] = None,
    ) -> AdapterCrawlResult:
        """Thu thập danh sách việc làm từ kênh RSS qua HTTP"""
        t0 = time.time()
        try:
            resp = self.session.get(self.feed_url, timeout=8.0)
            latency = round((time.time() - t0) * 1000, 1)

            if resp.status_code == 200:
                result = self.parse_xml_feed(
                    xml_content=resp.text,
                    target_url=self.feed_url,
                    since_timestamp=since_timestamp,
                    limit=limit,
                )
                result.crawl_duration_ms = latency
                return result
            else:
                err = AdapterError(
                    error_type=AdapterErrorType.HTTP_ERROR,
                    message=f"Máy chủ RSS phản hồi lỗi HTTP {resp.status_code}",
                    url=self.feed_url,
                    status_code=resp.status_code,
                )
                return AdapterCrawlResult(
                    source_id=self.adapter_id,
                    source_name=self.source_name,
                    crawl_duration_ms=latency,
                    errors=[err],
                )
        except requests.exceptions.Timeout:
            latency = round((time.time() - t0) * 1000, 1)
            err = AdapterError(
                error_type=AdapterErrorType.NETWORK_TIMEOUT,
                message="Quá thời gian chờ phản hồi RSS Feed (Timeout sau 8s)",
                url=self.feed_url,
            )
            return AdapterCrawlResult(
                source_id=self.adapter_id,
                source_name=self.source_name,
                crawl_duration_ms=latency,
                errors=[err],
            )
        except requests.exceptions.RequestException as e:
            latency = round((time.time() - t0) * 1000, 1)
            err = AdapterError(
                error_type=AdapterErrorType.CONNECTION_FAILED,
                message=f"Lỗi kết nối RSS: {str(e)}",
                url=self.feed_url,
            )
            return AdapterCrawlResult(
                source_id=self.adapter_id,
                source_name=self.source_name,
                crawl_duration_ms=latency,
                errors=[err],
            )

    def fetch_job_detail(
        self,
        source_job_id: str,
        detail_url: str,
    ) -> Optional[Dict[str, Any]]:
        """Kênh RSS đã cung cấp tóm tắt trực tiếp, không bắt buộc truy cập trang con"""
        return None


rss_syndication_adapter = RssSyndicationAdapter()
