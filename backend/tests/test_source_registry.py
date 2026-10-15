"""
Test Suite for C_Data Source Registry & Source Management System (Prompt 03 Acceptance).
Verifies:
1. All 5 required source categories are represented.
2. Unverified sources are not marked active by default.
3. Credential status verification (missing vs valid).
4. Independent enable/disable toggling.
5. Rate limit and sync interval constraints.
6. Metrics persistence and crawl telemetry tracking.
7. Search engine decoupling: registering a new source dynamically executes without code changes.
8. REST API endpoints for source management.
"""

from datetime import datetime, timezone
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.source import (
    AccessMethod,
    CredentialStatus,
    RateLimitConfig,
    SourceCategory,
    SourceDefinition,
    SourceHealthCheckResult,
    SourceHealthStatus,
    SourceMetrics,
)
from app.services.multi_source_discovery import multi_source_discovery
from app.services.search_intent_parser import SearchIntent
from app.services.source_registry import SourceRegistry, source_registry


class TestSourceRegistry(unittest.TestCase):
    """Bộ kiểm thử tính đúng đắn của Source Registry C_Data"""

    def setUp(self):
        self.registry = source_registry
        self.client = TestClient(app)

    def test_01_all_five_categories_represented(self):
        """Kiểm tra có đầy đủ 5 nhóm nguồn tuyển dụng theo yêu cầu P0"""
        sources = self.registry.list_sources()
        categories_found = {s.category for s in sources}

        self.assertIn(SourceCategory.ENTERPRISE_DIRECT, categories_found, "Thiếu nhóm Enterprise Direct")
        self.assertIn(SourceCategory.NATIONAL_JOB_BOARD, categories_found, "Thiếu nhóm National Job Board")
        self.assertIn(SourceCategory.SPECIALIZED_LOCAL, categories_found, "Thiếu nhóm Specialized Local")
        self.assertIn(SourceCategory.SOCIAL_PUBLIC, categories_found, "Thiếu nhóm Social Public")
        self.assertIn(SourceCategory.AUTHORIZED_API, categories_found, "Thiếu nhóm Authorized API")

        # Xác nhận tổng số nguồn đã khởi tạo
        self.assertGreaterEqual(len(sources), 10, "Registry phải có ít nhất 10 nguồn được định nghĩa sẵn")

    def test_02_unverified_sources_never_active_by_default(self):
        """
        Quy tắc nghiêm ngặt: Không được đánh dấu một nguồn là active chỉ vì đã khai báo trong cấu hình.
        Trạng thái mặc định ban đầu phải là UNKNOWN hoặc UNCONFIGURED.
        """
        sources = self.registry.list_sources()
        for src in sources:
            # Nếu nguồn chưa từng chạy health check hoặc chưa từng crawl thành công
            if src.last_health_check_at is None and src.last_successful_crawl is None:
                self.assertIn(
                    src.health_status,
                    [SourceHealthStatus.UNKNOWN, SourceHealthStatus.UNCONFIGURED],
                    f"Nguồn '{src.id}' chưa kiểm tra nhưng đã bị đánh dấu {src.health_status}!",
                )

    def test_03_credential_verification_detects_missing(self):
        """Kiểm tra nguồn yêu cầu API Key (TopCV, VietnamWorks) khi thiếu env var sẽ báo UNCONFIGURED / MISSING"""
        # Đảm bảo tạm thời không có env var
        with patch.dict(os.environ, {}, clear=True):
            res_topcv = self.registry.run_health_check("topcv")
            self.assertEqual(res_topcv.status, SourceHealthStatus.UNCONFIGURED)
            self.assertFalse(res_topcv.is_healthy)
            self.assertIn("TOPCV_API_KEY", res_topcv.evidence)

            src = self.registry.get_source("topcv")
            self.assertEqual(src.credential_status, CredentialStatus.MISSING)

    def test_04_credential_verification_with_valid_key(self):
        """Kiểm tra khi cấu hình API Key, trạng thái credential chuyển sang VALID"""
        with patch.dict(os.environ, {"TOPCV_API_KEY": "test_partner_token_123"}):
            with patch("requests.head") as mock_head:
                mock_head.return_value.status_code = 200
                res = self.registry.run_health_check("topcv")
                src = self.registry.get_source("topcv")
                self.assertEqual(src.credential_status, CredentialStatus.VALID)

    def test_05_independent_toggle_behavior(self):
        """Kiểm tra bật/tắt một nguồn độc lập không ảnh hưởng tới nguồn khác"""
        # Lấy trạng thái ban đầu của sun_group và vinpearl
        sun = self.registry.get_source("sun_group")
        vin = self.registry.get_source("vinpearl")
        initial_sun_state = sun.is_enabled
        initial_vin_state = vin.is_enabled

        # Tắt sun_group
        self.registry.toggle_source("sun_group", is_enabled=False)
        self.assertFalse(self.registry.get_source("sun_group").is_enabled)
        # vinpearl không được đổi
        self.assertEqual(self.registry.get_source("vinpearl").is_enabled, initial_vin_state)

        # Lấy runnable sources: sun_group không được có mặt
        runnable_ids = [s.id for s in self.registry.get_runnable_sources()]
        self.assertNotIn("sun_group", runnable_ids)

        # Bật lại sun_group
        self.registry.toggle_source("sun_group", is_enabled=True)
        self.assertTrue(self.registry.get_source("sun_group").is_enabled)

    def test_06_rate_limit_and_sync_intervals(self):
        """Kiểm tra các thuộc tính rate_limit và tần suất đồng bộ"""
        src = self.registry.get_source("careerviet")
        self.assertIsNotNone(src.rate_limit)
        self.assertGreater(src.rate_limit.requests_per_minute, 0)
        self.assertGreaterEqual(src.rate_limit.min_delay_seconds, 0.0)
        self.assertGreater(src.sync_interval_seconds, 0)

    def test_07_metrics_and_telemetry_recording(self):
        """Kiểm tra ghi nhận telemetry và chỉ số crawl (thành công / thất bại)"""
        src_id = "fpt_telecom"
        src_before = self.registry.get_source(src_id)
        runs_before = src_before.metrics.total_runs
        discovered_before = src_before.metrics.discovered_count
        new_before = src_before.metrics.new_count

        # Ghi nhận thành công
        self.registry.record_crawl_success(src_id, discovered_count=8, new_count=3, duration_ms=150.5)
        src_after = self.registry.get_source(src_id)

        self.assertEqual(src_after.metrics.total_runs, runs_before + 1)
        self.assertEqual(src_after.metrics.discovered_count, discovered_before + 8)
        self.assertEqual(src_after.metrics.new_count, new_before + 3)
        self.assertIsNotNone(src_after.last_successful_crawl)
        self.assertEqual(src_after.health_status, SourceHealthStatus.HEALTHY)

        # Ghi nhận lỗi
        errors_before = src_after.metrics.error_count
        self.registry.record_crawl_failure(src_id, error_message="HTTP 503 Service Unavailable", duration_ms=210.0)
        src_err = self.registry.get_source(src_id)

        self.assertEqual(src_err.metrics.error_count, errors_before + 1)
        self.assertEqual(src_err.last_error_message, "HTTP 503 Service Unavailable")
        self.assertIsNotNone(src_err.last_failed_crawl)

    def test_08_dynamic_discovery_decoupling_dod(self):
        """
        Definition of Done: Đăng ký một nguồn mới vào Registry và xác nhận
        MultiSourceDiscovery tự động phát hiện và thực thi mà không sửa search engine!
        """
        new_source_id = "test_custom_mining_portal"
        custom_source = SourceDefinition(
            id=new_source_id,
            name="Cổng Việc Làm Thử Nghiệm Ngành Than",
            category=SourceCategory.SPECIALIZED_LOCAL,
            domain="vieclamthan.quangninh.local",
            access_method=AccessMethod.AUTHORIZED_ADAPTER,
            is_enabled=True,
            priority=1,
            health_status=SourceHealthStatus.HEALTHY,
            target_provinces=["Quảng Ninh"],
        )
        self.registry.register_source(custom_source)

        # Đăng ký adapter động
        def mock_custom_adapter(intent: SearchIntent, max_items: int):
            return [{
                "title": "Kỹ Sư An Toàn Mỏ Than Test Decoupling",
                "company_name": "Công ty Than Thử Nghiệm C_Data",
                "source_url": "https://vieclamthan.quangninh.local/job/999",
                "location_province": "Quảng Ninh",
                "location_district": "Cẩm Phả",
                "salary_text": "25 triệu",
                "salary_min": 25000000,
                "salary_max": 25000000,
                "job_type": "full-time",
            }]

        self.registry.register_adapter(new_source_id, mock_custom_adapter)

        # Chạy multi_source_discovery
        intent = SearchIntent(
            raw_query="kỹ sư an toàn",
            normalized_query="ky su an toan",
            target_province="Quảng Ninh",
        )
        discovery_result = multi_source_discovery.discover_across_sources(intent, max_per_source=5, timeout_seconds=3.0)

        # Xác nhận nguồn mới được gọi tự động
        status_dict = discovery_result.get("source_status", {})
        self.assertIn(new_source_id, status_dict, "Nguồn mới đăng ký phải xuất hiện trong báo cáo điều phối!")
        self.assertEqual(status_dict[new_source_id]["status"], "success")
        self.assertEqual(status_dict[new_source_id]["items_retrieved"], 1)

        # Kiểm tra metric nguồn mới được cập nhật
        registered_test_src = self.registry.get_source(new_source_id)
        self.assertGreaterEqual(registered_test_src.metrics.discovered_count, 1)

    def test_09_rest_api_endpoints(self):
        """Kiểm thử các API REST /api/v1/sources"""
        # 1. GET /api/v1/sources
        resp = self.client.get("/api/v1/sources")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 5)

        # 2. GET /api/v1/sources/summary/overview
        resp_sum = self.client.get("/api/v1/sources/summary/overview")
        self.assertEqual(resp_sum.status_code, 200)
        summary = resp_sum.json()
        self.assertIn("total_sources", summary)
        self.assertIn("by_category", summary)
        self.assertEqual(len(summary["by_category"]), 5)

        # 3. GET /api/v1/sources/{source_id}
        resp_detail = self.client.get("/api/v1/sources/careerviet")
        self.assertEqual(resp_detail.status_code, 200)
        self.assertEqual(resp_detail.json()["id"], "careerviet")

        # 4. POST /api/v1/sources/{source_id}/toggle
        resp_toggle = self.client.post("/api/v1/sources/careerviet/toggle", json={"is_enabled": False})
        self.assertEqual(resp_toggle.status_code, 200)
        self.assertFalse(resp_toggle.json()["is_enabled"])

        # Bật lại
        resp_toggle_back = self.client.post("/api/v1/sources/careerviet/toggle", json={"is_enabled": True})
        self.assertEqual(resp_toggle_back.status_code, 200)
        self.assertTrue(resp_toggle_back.json()["is_enabled"])


if __name__ == "__main__":
    unittest.main()
