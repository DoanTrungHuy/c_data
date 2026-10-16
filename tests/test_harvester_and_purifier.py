import os
import sys
import unittest

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.html_purifier import (
    purify_html_to_markdown,
    compute_job_fingerprint,
    extract_contacts_and_salary_from_text,
)
from app.adapters.jobspy_adapter import JobSpyMultiSourceAdapter
from app.adapters.ats_api_adapter import DirectATSApiAdapter


class TestHarvesterAndPurifier(unittest.TestCase):

    def test_01_purify_html_removes_noise_and_produces_clean_markdown(self):
        """Kiểm tra Firecrawl HTML Purifier loại bỏ script, style, nav và tạo Markdown chuẩn"""
        messy_html = """
        <html>
            <head>
                <style>.ads { color: red; }</style>
                <script>alert("tracking pixel");</script>
            </head>
            <body>
                <nav><a href="/home">Trang chủ</a></nav>
                <h1>Kỹ sư Phần mềm Python</h1>
                <p>Doanh nghiệp công nghệ hàng đầu tại Hạ Long.</p>
                <ul>
                    <li>Thành thạo FastAPI và Django</li>
                    <li>Có kinh nghiệm Docker, PostgreSQL</li>
                </ul>
                <div class="ads">Quảng cáo tài trợ không liên quan</div>
                <footer>Bản quyền 2026</footer>
            </body>
        </html>
        """
        markdown = purify_html_to_markdown(messy_html)

        self.assertNotIn("alert(", markdown)
        self.assertNotIn(".ads {", markdown)
        self.assertIn("# Kỹ sư Phần mềm Python", markdown)
        self.assertIn("- Thành thạo FastAPI và Django", markdown)
        self.assertIn("- Có kinh nghiệm Docker, PostgreSQL", markdown)

    def test_02_fingerprint_deduplication(self):
        """Kiểm tra Crawlee/Scrapy MD5 fingerprinting loại bỏ query tracking (fbclid, utm)"""
        url1 = "https://vn.indeed.com/viewjob?jk=12345&fbclid=IwAR123"
        url2 = "https://vn.indeed.com/viewjob?jk=12345&utm_source=facebook"
        title = "Backend Developer"
        company = "Tech Corp"

        fp1 = compute_job_fingerprint(url1, title, company)
        fp2 = compute_job_fingerprint(url2, title, company)

        # Hai URL có query tracking khác nhau phải cho ra cùng 1 fingerprint MD5
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 32)

    def test_03_extract_contacts_and_salary(self):
        """Kiểm tra trích xuất tự động số điện thoại, email và mức lương"""
        text = "Liên hệ ứng tuyển qua hotline: 0987.654.321 hoặc 0203.3616.838. Email: hr@company.vn. Lương 15 - 25 triệu VNĐ."
        res = extract_contacts_and_salary_from_text(text)

        self.assertIn("hr@company.vn", res["emails"])
        self.assertTrue(any("0987654321" in p.replace(".", "") for p in res["phones"]))
        self.assertIsNotNone(res["salary_hint"])
        self.assertIn("15 - 25", res["salary_hint"])

    def test_04_jobspy_zero_fraud_location(self):
        """Kiểm tra JobSpy Adapter tôn trọng tuyệt đối địa bàn thật, không gán bừa sang Quảng Ninh"""
        adapter = JobSpyMultiSourceAdapter()

        # Job Hà Nội
        loc_hn = adapter._resolve_location("Cầu Giấy, Hà Nội")
        self.assertEqual(loc_hn["province"], "Hà Nội")

        # Job Hồ Chí Minh
        loc_hcm = adapter._resolve_location("Quận 1, TP. Hồ Chí Minh")
        self.assertEqual(loc_hcm["province"], "Hồ Chí Minh")

        # Job Quảng Ninh
        loc_qn = adapter._resolve_location("Bãi Cháy, TP. Hạ Long, Quảng Ninh")
        self.assertEqual(loc_qn["province"], "Quảng Ninh")
        self.assertEqual(loc_qn["district"], "Hạ Long")

        # Job Remote
        loc_remote = adapter._resolve_location("Vietnam", is_remote=True)
        self.assertEqual(loc_remote["workplace_type"], "remote")
        self.assertEqual(loc_remote["province"], "Toàn quốc")

    def test_05_ats_api_adapter_location_and_provider(self):
        """Kiểm tra DirectATSApiAdapter phân giải địa bàn và hỗ trợ Greenhouse/Lever"""
        adapter = DirectATSApiAdapter()
        self.assertEqual(adapter.adapter_id, "ats_api_direct")

        # Phân giải Onsite Hạ Long
        qn = adapter._resolve_location("Ha Long Bay, Quang Ninh")
        self.assertEqual(qn["province"], "Quảng Ninh")
        self.assertEqual(qn["district"], "Hạ Long")
        self.assertEqual(qn["workplace_type"], "onsite")

        # Phân giải Remote
        rem = adapter._resolve_location("Remote - Anywhere in Vietnam")
        self.assertEqual(rem["province"], "Toàn quốc")
        self.assertEqual(rem["workplace_type"], "remote")


if __name__ == "__main__":
    unittest.main()

