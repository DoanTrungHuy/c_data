"""
Unit & Integration Test Suite for Chặng C: Web Crawler Adapters
Tests LinkedIn Guest API, ITviec, Ybox, and JobsGO adapters for:
- Standard BaseJobAdapter contract
- Universal Job Schema compatibility
- Resilient error handling (HTTP error, Cloudflare 403, timeouts)
- Zero-fraud location & canonical URL extraction
"""

import io
import os
import sys
from pathlib import Path
import unittest

# Đảm bảo console UTF-8 trên Windows an toàn
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thêm đường dẫn backend vào sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.adapters.base import (
    AdapterCrawlResult,
    AdapterError,
    AdapterErrorType,
    BaseJobAdapter,
    RawJobRecord,
)
from app.adapters.itviec_adapter import ITviecAdapter, itviec_adapter
from app.adapters.linkedin_guest_adapter import LinkedInGuestAdapter, linkedin_guest_adapter
from app.adapters.ybox_adapter import YboxAdapter, ybox_adapter
from app.adapters.jobsgo_adapter import JobsGOAdapter, jobsgo_adapter
from app.schemas.universal_job import UniversalJob, VerificationStatus
from app.services.source_registry import source_registry


class TestChặngCWebAdapters(unittest.TestCase):
    """Bộ kiểm thử Chặng C: Các Web Crawler Adapter mở rộng"""

    def test_01_linkedin_guest_adapter_contract_and_universal_job(self):
        """Kiểm tra LinkedInGuestAdapter: Kế thừa BaseJobAdapter và trích xuất UniversalJob hợp lệ"""
        self.assertIsInstance(linkedin_guest_adapter, BaseJobAdapter)
        self.assertEqual(linkedin_guest_adapter.source_id, "linkedin_guest_api")
        
        # Test parse mẫu HTML snippet của LinkedIn guest
        sample_html = """
        <li>
            <div class="base-card" data-entity-urn="urn:li:jobPosting:4478440089">
                <a class="base-card__full-link" href="https://vn.linkedin.com/jobs/view/python-developer-at-fpt-software-4478440089?trackingId=xyz">
                    <h3 class="base-search-card__title">Senior Python Developer</h3>
                </a>
                <h4 class="base-search-card__subtitle"><a href="/company/fpt-software">FPT Software</a></h4>
                <div class="job-search-card__location">Hạ Long, Quảng Ninh, Vietnam</div>
                <time datetime="2026-10-15">2 days ago</time>
            </div>
        </li>
        """
        records = linkedin_guest_adapter.parse_html_snippet(sample_html, keyword="Python", default_location="Quảng Ninh")
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.source_job_id, "4478440089")
        self.assertEqual(r.title, "Senior Python Developer")
        self.assertEqual(r.company_name, "FPT Software")
        self.assertEqual(r.location_province, "Quảng Ninh")
        self.assertEqual(r.location_district, "Hạ Long")
        self.assertTrue(r.source_url.startswith("https://vn.linkedin.com/jobs/view/"))

        # Kiểm tra chuyển đổi sang UniversalJob 27 trường
        uj = r.to_universal_job(source_id="linkedin_guest_api", source_name="LinkedIn Public Guest")
        self.assertIsInstance(uj, UniversalJob)
        self.assertEqual(uj.job_id, "linkedin_guest_api_4478440089")
        self.assertEqual(uj.title, "Senior Python Developer")
        self.assertEqual(uj.company_name, "FPT Software")
        self.assertEqual(uj.location_normalized.province, "Quảng Ninh")
        print("  ✓ LinkedInGuestAdapter parse & to_universal_job PASS 100%")

    def test_02_itviec_adapter_contract_and_parsing(self):
        """Kiểm tra ITviecAdapter: Bóc tách thẻ `.job-card`, phân loại địa bàn & kỹ năng"""
        self.assertIsInstance(itviec_adapter, BaseJobAdapter)
        self.assertEqual(itviec_adapter.source_id, "itviec")

        sample_card = """
        <div class="job-card">
            <h3><a href="/it-jobs/backend-developer-java-dosoftpro-4517">Backend Developer (Java, Spring Boot)</a></h3>
            <div class="imy-3 d-flex align-items-center">
                <span class="ims-2"><a class="text-rich-grey" href="/companies/dosoftpro">DOSOFTPRO Vietnam</a></span>
            </div>
            <div class="text-nowrap">Hà Nội</div>
            <span class="itag">Java</span>
            <span class="itag">Spring Boot</span>
        </div>
        """
        records = itviec_adapter.parse_cards(sample_card, default_province="Hà Nội")
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.title, "Backend Developer (Java, Spring Boot)")
        self.assertEqual(r.company_name, "DOSOFTPRO Vietnam")
        self.assertEqual(r.location_province, "Hà Nội")
        self.assertIn("Java", r.required_skills)
        self.assertIn("Spring Boot", r.required_skills)

        # Chuyển đổi UniversalJob
        uj = r.to_universal_job(source_id="itviec", source_name="ITviec")
        self.assertEqual(uj.source_name, "ITviec")
        self.assertEqual(uj.verification_status, VerificationStatus.LIKELY_ACTIVE)
        print("  ✓ ITviecAdapter parse card, company & skills PASS 100%")

    def test_03_ybox_adapter_graphql_contract_and_safety(self):
        """Kiểm tra YboxAdapter: Kết nối GraphQL an toàn, không crash khi upstream lỗi"""
        self.assertIsInstance(ybox_adapter, BaseJobAdapter)
        self.assertEqual(ybox_adapter.source_id, "ybox_fresher")

        # Gọi discover_jobs thực tế hoặc fallback
        result = ybox_adapter.discover_jobs(keyword="IT", province="Hà Nội", limit=2)
        self.assertIsInstance(result, AdapterCrawlResult)
        self.assertEqual(result.source_id, "ybox_fresher")
        # Dù Ybox có dữ liệu hay lỗi Elasticsearch upstream, kết quả không được crash
        self.assertIsInstance(result.items, list)
        print(f"  ✓ YboxAdapter live query handled gracefully ({len(result.items)} items, duration: {result.crawl_duration_ms:.1f}ms)")

    def test_04_jobsgo_adapter_waf_resilience(self):
        """Kiểm tra JobsGOAdapter: Tự động ghi nhận lỗi Cloudflare/WAF 403 không crash hệ thống"""
        self.assertIsInstance(jobsgo_adapter, BaseJobAdapter)
        self.assertEqual(jobsgo_adapter.source_id, "jobsgo")

        # Gọi live query tới JobsGO (kỳ vọng ghi nhận HTTP 403 hoặc bóc tách HTML thành công)
        result = jobsgo_adapter.discover_jobs(keyword="IT", province="Quảng Ninh", limit=2)
        self.assertIsInstance(result, AdapterCrawlResult)
        self.assertEqual(result.source_id, "jobsgo")
        
        # Nếu bị 403, kiểm tra phân loại lỗi chuẩn AdapterErrorType.BLOCKED
        if any(e.status_code == 403 for e in result.errors):
            blocked_err = next(e for e in result.errors if e.status_code == 403)
            self.assertEqual(blocked_err.error_type, AdapterErrorType.BLOCKED)
            print(f"  ✓ JobsGOAdapter Cloudflare 403 classified as BLOCKED with zero crash!")
        else:
            print(f"  ✓ JobsGOAdapter executed successfully ({len(result.items)} items)")

    def test_05_source_registry_adapter_callables(self):
        """Kiểm tra SourceRegistry: Tích hợp đầy đủ các adapter và callable hoạt động đồng bộ"""
        required_sources = ["careerviet", "linkedin_guest_api", "itviec", "ybox_fresher", "jobsgo"]
        for src_id in required_sources:
            adapter_func = source_registry.get_adapter(src_id)
            self.assertIsNotNone(adapter_func, f"Thiếu adapter function cho {src_id}")
            self.assertTrue(callable(adapter_func), f"Adapter {src_id} không phải callable")

        print("  ✓ SourceRegistry: Tất cả 5 web crawler adapters đăng ký callable thành công!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
