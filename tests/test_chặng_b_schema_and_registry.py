"""
Unit & Integration Test Suite for Chặng B:
- Universal Job Schema Validation (27 fields)
- Verification Status Enum (7 statuses)
- Product Search Configuration (Hạ Long, IT, Fresher/Junior)
- Source Registry 19 Sources Mapping
"""

from datetime import datetime, timezone
import io
from pathlib import Path
import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.product_config import product_config
from app.schemas.universal_job import (
    LocationNormalized,
    UniversalJob,
    VerificationAuditEvidence,
    VerificationStatus,
)
from app.services.source_registry import source_registry
from app.schemas.source import SourceCategory, SourceHealthStatus


class TestChặngBSchemaAndRegistry(unittest.TestCase):
    """Kiểm thử Chặng B: Universal Job Schema, Product Config và Source Registry"""

    def test_universal_job_schema_instantiation_and_serialization(self):
        """Xác thực UniversalJob schema đầy đủ 27 trường chuẩn hóa"""
        audit_ev = VerificationAuditEvidence(
            checked_at="2026-10-17T19:30:00Z",
            url_checked="https://sungroup.com.vn/careers/ky-su-dien",
            http_status=200,
            deadline_at="2026-11-30",
            evidence_found={"schema_job_posting": True, "apply_button_active": True},
            method="live_http_and_schema_audit",
            confidence=0.98,
            status_reason="Đã đối soát thành công cấu trúc Schema.org JobPosting và nút apply đang mở",
        )

        loc_norm = LocationNormalized(
            city="Hạ Long",
            province="Quảng Ninh",
            district="Bãi Cháy",
            confidence=0.98,
        )

        job = UniversalJob(
            job_id="job_halong_001",
            title="Kỹ Sư Quản Trị Hệ Thống IT Support",
            company_name="Tập đoàn Sun Group Vùng Đông Bắc",
            location_raw="Bãi Cháy, TP. Hạ Long, Quảng Ninh",
            location_normalized=loc_norm,
            job_categories=["IT Support", "System Administration", "Network Engineering"],
            seniority="Junior",
            experience_requirement="1 năm kinh nghiệm hoặc Fresher tốt nghiệp xuất sắc",
            work_type="On-site",
            work_schedule="Toàn thời gian",
            salary_min=12000000,
            salary_max=18000000,
            salary_currency="VND",
            salary_text="12 - 18 triệu/tháng",
            description="Vận hành hệ thống mạng LAN/WAN và máy chủ tại Ga Cáp treo Nữ Hoàng.",
            required_skills=["Network", "Windows Server", "CCNA", "Troubleshooting"],
            posted_at="2026-10-15T08:00:00Z",
            deadline="2026-11-30",
            source_name="Sun Group Portal",
            source_type="enterprise_direct",
            original_url="https://sungroup.com.vn/careers/ky-su-dien",
            application_url="https://sungroup.com.vn/careers/ky-su-dien/apply",
            employer_url="https://sungroup.com.vn",
            application_method="online_form",
            verification_status=VerificationStatus.ACTIVE_CONFIRMED,
            verification_evidence=[audit_ev],
            duplicate_group_id=None,
            crawl_status="success",
        )

        # Chuyển đổi sang JSON dict
        d = job.model_dump()
        self.assertEqual(d["job_id"], "job_halong_001")
        self.assertEqual(d["location_normalized"]["city"], "Hạ Long")
        self.assertEqual(d["verification_status"], "active_confirmed")
        self.assertEqual(len(d["verification_evidence"]), 1)
        self.assertEqual(d["verification_evidence"][0]["http_status"], 200)

    def test_all_verification_statuses_supported(self):
        """Xác thực 7 trạng thái tuyển dụng chuẩn theo Master Prompt Section 9"""
        statuses = [s.value for s in VerificationStatus]
        expected = [
            "active_confirmed",
            "likely_active",
            "unverified",
            "expired",
            "closed",
            "removed",
            "conflicting",
        ]
        for exp in expected:
            self.assertIn(exp, statuses, f"Trạng thái {exp} phải có trong VerificationStatus enum")

    def test_product_config_defaults(self):
        """Xác thực cấu hình mặc định (Hạ Long, Quảng Ninh, IT, Fresher/Junior)"""
        self.assertEqual(product_config.primary_city, "Hạ Long")
        self.assertEqual(product_config.primary_province, "Quảng Ninh")
        self.assertIn("Hà Nội", product_config.secondary_allowed_provinces)
        self.assertIn("Fresher", product_config.priority_seniorities)
        self.assertIn("Junior", product_config.priority_seniorities)
        self.assertIn("Intern", product_config.priority_seniorities)
        self.assertTrue(len(product_config.field_work_penalty_keywords) >= 5)
        self.assertTrue(len(product_config.it_task_indicators) >= 10)

    def test_source_registry_catalog_expansion(self):
        """Xác thực SourceRegistry nạp đầy đủ 19 nguồn thuộc 5 nhóm chuẩn"""
        all_sources = source_registry.list_sources(enabled_only=False)
        self.assertGreaterEqual(len(all_sources), 19, "SourceRegistry phải có ít nhất 19 nguồn")

        source_ids = [s.id for s in all_sources]
        required_ids = [
            "careerviet",
            "sun_group",
            "vinpearl",
            "tkv_mining",
            "cict_cailan",
            "fpt_telecom",
            "viettel_group",
            "itviec",
            "jobsgo",
            "glints_vn",
            "ybox_fresher",
            "linkedin_guest_api",
        ]
        for req_id in required_ids:
            self.assertIn(req_id, source_ids, f"Nguồn {req_id} phải được đăng ký trong SourceRegistry")

        # Kiểm tra đủ 5 nhóm
        categories = {s.category for s in all_sources}
        self.assertEqual(len(categories), 5, "Phải bao phủ đầy đủ 5 nhóm SourceCategory")


if __name__ == "__main__":
    unittest.main()
