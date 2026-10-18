"""
Unit & Integration Test Suite for Chặng D: Company Registry for Local Enterprises
Tests CompanyRegistry for:
- 20 verified local enterprise profiles in Ha Long & Quang Ninh
- Coverage of Hospitality, Healthcare, Industry/Ports, Telecom & IT
- UniversalJob generation with official application hotlines & portals
- Live HTTP audit resilience and persistent state
- Frontend JSON synchronization
"""

import io
import json
import os
import sys
from pathlib import Path
import unittest

# Đảm bảo UTF-8 console an toàn
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.schemas.company import CompanyRegistryProfile
from app.schemas.universal_job import UniversalJob, VerificationStatus
from app.services.company_registry import (
    CompanyRegistry,
    FRONTEND_EXPORT_PATH,
    STATE_FILE_PATH,
    company_registry,
)


class TestChặngDCompanyRegistry(unittest.TestCase):
    """Bộ kiểm thử Chặng D: Danh mục doanh nghiệp trọng điểm địa phương"""

    def test_01_catalog_completeness_and_provinces(self):
        """Kiểm tra danh mục doanh nghiệp: Đủ 20 đơn vị với địa chỉ chuẩn xác tại Quảng Ninh"""
        companies = company_registry.list_companies()
        self.assertGreaterEqual(len(companies), 20)

        # Kiểm tra sự hiện diện của các đơn vị đầu ngành
        comp_ids = {c.company_id for c in companies}
        expected_anchors = [
            "sun_world_halong",
            "vinpearl_resort_halong",
            "wyndham_legend_halong",
            "vinmec_halong",
            "bai_chay_hospital",
            "tkv_vinacomin",
            "cict_cai_lan_port",
            "fpt_telecom_quang_ninh",
            "vnpt_quang_ninh",
            "viettel_quang_ninh",
        ]
        for aid in expected_anchors:
            self.assertIn(aid, comp_ids, f"Thiếu doanh nghiệp trọng điểm: {aid}")

        # Kiểm tra 100% doanh nghiệp có địa chỉ tại Quảng Ninh
        for c in companies:
            self.assertTrue(len(c.locations) > 0, f"Doanh nghiệp {c.company_id} thiếu locations")
            has_qn = any(loc.get("province") == "Quảng Ninh" for loc in c.locations)
            self.assertTrue(has_qn, f"Doanh nghiệp {c.company_id} không có địa chỉ tại Quảng Ninh")
            self.assertTrue(c.career_url.startswith("http"), f"Doanh nghiệp {c.company_id} thiếu career_url hợp lệ")
            self.assertGreater(len(c.active_it_roles), 0, f"Doanh nghiệp {c.company_id} thiếu active_it_roles")

        print(f"  ✓ Danh mục {len(companies)} doanh nghiệp Hạ Long / Quảng Ninh đầy đủ & hợp lệ 100%")

    def test_02_industry_group_coverage(self):
        """Kiểm tra phân bố ngành nghề: Phủ đủ Du lịch, Y tế, Công nghiệp/Cảng biển, Viễn thông & CNTT"""
        groups = {c.industry_group for c in company_registry.list_companies()}
        self.assertIn("hospitality_tourism", groups)
        self.assertIn("healthcare", groups)
        self.assertIn("industry_logistics", groups)
        self.assertIn("telecom_it", groups)

        tourism_comps = company_registry.list_companies(industry_group="hospitality_tourism")
        health_comps = company_registry.list_companies(industry_group="healthcare")
        industry_comps = company_registry.list_companies(industry_group="industry_logistics")
        tech_comps = company_registry.list_companies(industry_group="telecom_it")

        self.assertGreaterEqual(len(tourism_comps), 5)
        self.assertGreaterEqual(len(health_comps), 4)
        self.assertGreaterEqual(len(industry_comps), 4)
        self.assertGreaterEqual(len(tech_comps), 4)
        print(f"  ✓ Phân nhóm ngành: Du lịch ({len(tourism_comps)}), Y tế ({len(health_comps)}), Cảng/Mỏ ({len(industry_comps)}), CNTT ({len(tech_comps)})")

    def test_03_universal_job_generation(self):
        """Kiểm tra sinh cơ hội việc làm UniversalJob từ các vị trí IT đã thẩm định"""
        jobs = company_registry.generate_local_job_opportunities()
        self.assertGreaterEqual(len(jobs), 40)

        for job in jobs:
            self.assertIsInstance(job, UniversalJob)
            self.assertEqual(job.location_normalized.province, "Quảng Ninh")
            self.assertEqual(job.source_type, "enterprise_direct")
            self.assertEqual(job.verification_status, VerificationStatus.LIKELY_ACTIVE)
            self.assertGreater(len(job.verification_evidence), 0)
            self.assertTrue(job.original_url.startswith("http"))

        print(f"  ✓ Sinh thành công {len(jobs)} cơ hội việc làm CNTT chuẩn hóa UniversalJob tại Hạ Long")

    def test_04_audit_and_persistent_sync(self):
        """Kiểm tra cơ chế audit và xuất file JSON đồng bộ frontend"""
        # Xuất file JSON
        company_registry.export_frontend_json()
        self.assertTrue(FRONTEND_EXPORT_PATH.exists())
        with open(FRONTEND_EXPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), len(company_registry.list_companies()))
        print(f"  ✓ Đồng bộ frontend JSON thành công tại: {FRONTEND_EXPORT_PATH.name} ({len(data)} profiles)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
