"""
Unit Test Suite for Open-Source Reference Verifier Engine.
Tests:
1. Syntactic filtering (anchors, tracking parameters, bare root domains).
2. Anti-booking & hospitality negative scoring.
3. Title similarity matching (fuzzy token sort & sequence matching).
4. Direct ATS portal validation.
5. 100% Audit of production jobs in frontend/public/data/jobs.json.
"""

import json
import os
import sys
import io
import unittest

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.open_source_reference_verifier import (
    open_source_reference_verifier,
    compute_title_similarity,
)


class TestOpenSourceReferenceVerifier(unittest.TestCase):

    def setUp(self):
        self.verifier = open_source_reference_verifier
        self.jobs_path = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "public", "data", "jobs.json"
        )
        with open(self.jobs_path, "r", encoding="utf-8") as f:
            self.jobs = json.load(f)

    def test_01_reject_root_domains(self):
        """Kiểm tra chặn các domain trang chủ không có path tuyển dụng"""
        root_urls = [
            "https://wyndhamhalong.com/",
            "https://wyndhamhalong.com",
            "https://muongthanh.com/",
            "https://flc.vn/",
            "https://example.com/",
        ]
        for url in root_urls:
            is_valid, reason = self.verifier.is_syntactically_valid(url)
            self.assertFalse(is_valid, f"URL root {url} không được phép coi là tin tuyển dụng!")

    def test_02_reject_fake_anchors_and_tracking(self):
        """Kiểm tra chặn các anchor ảo (#it-) và tham số rác (?post_ref=)"""
        bad_urls = [
            "https://wyndhamhalong.com/#it-officer",
            "https://cict.com.vn/tuyen-dung#it-network",
            "https://company.vn/jobs?post_ref=facebook",
            "https://company.vn/jobs?ref=internal",
        ]
        for url in bad_urls:
            is_valid, reason = self.verifier.is_syntactically_valid(url)
            self.assertFalse(is_valid, f"URL {url} phải bị từ chối do chứa anchor hoặc tham số giả lập!")

    def test_03_title_similarity_matching(self):
        """Kiểm tra thuật toán đối soát tiêu đề (Fuzzy Title Matcher)"""
        # Trùng khớp cao
        sim1 = compute_title_similarity(
            "Chuyên Viên Công Nghệ Thông Tin",
            "Tuyển Dụng Chuyên Viên Công Nghệ Thông Tin (IT Executive) - CareerViet"
        )
        self.assertGreater(sim1, 0.4, f"Độ tương đồng phải cao ({sim1})")

        # Hoàn toàn lệch lạc (IT vs Hotel Booking)
        sim2 = compute_title_similarity(
            "Tuyển Gấp IT Officer / Chuyên Viên Quản Trị Hệ Thống CNTT",
            "Wyndham Legend Halong - Luxury 5-Star Hotel Booking & Reservation"
        )
        self.assertLess(sim2, 0.2, f"Độ tương đồng phải rất thấp ({sim2})")

    def test_04_accept_verified_ats_portals(self):
        """Kiểm tra chấp thuận các cổng tuyển dụng chính thức (CareerViet, TopCV, VietnamWorks, ITviec)"""
        valid_sample = "https://careerviet.vn/vi/tim-viec-lam/nhan-vien-it-tieng-trung-lam-tai-quang-ninh.35C833DD.html"
        verdict = self.verifier.audit_reference(valid_sample, fetch_live=False)
        self.assertTrue(verdict.is_valid_job_reference)
        self.assertEqual(verdict.verdict_code, "DIRECT_ATS_PORTAL")
        self.assertGreaterEqual(verdict.confidence, 0.90)

    def test_05_production_jobs_100_percent_pass(self):
        """Kiểm tra 100% dữ liệu thực tế hiện tại (66 jobs) đều vượt qua kiểm định mã nguồn mở"""
        self.assertGreater(len(self.jobs), 0, "Dữ liệu việc làm không được rỗng!")
        rejected_jobs = []

        for job in self.jobs:
            url = job.get("source_url")
            if not url:
                continue
            verdict = self.verifier.audit_reference(
                url=url,
                expected_title=job.get("title"),
                expected_company=job.get("company"),
                fetch_live=False,
            )
            if not verdict.is_valid_job_reference:
                rejected_jobs.append({
                    "id": job.get("id"),
                    "title": job.get("title"),
                    "url": url,
                    "reason": verdict.reason,
                })

        self.assertEqual(
            len(rejected_jobs), 0,
            f"Phát hiện {len(rejected_jobs)} tin vi phạm kiểm định tham chiếu nguồn: {rejected_jobs}"
        )
        print(f"\n  ✓ Đã kiểm định thành công 100% ({len(self.jobs)}/{len(self.jobs)}) tin tuyển dụng chuẩn xác!")


if __name__ == "__main__":
    unittest.main()
