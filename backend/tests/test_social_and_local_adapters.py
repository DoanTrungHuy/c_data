"""
Bộ kiểm thử chuyên sâu cho Adapters Doanh Nghiệp Địa Phương & Mạng Xã Hội Công Khai
Tuân thủ đầy đủ Definition of Done (DoD):
1. Adapter riêng biệt cho từng nguồn: LocalEnterpriseAdapter, FacebookPublicAdapter, ThreadsPublicAdapter.
2. Kiểm tra trạng thái nguồn rõ ràng: operational, missing_credentials, unsupported, blocked.
3. Không giả lập HTTP 200 thành công khi thiếu token hoặc bị chặn; kích hoạt fallback an toàn.
4. Phân loại nội dung: Phân biệt bài tuyển dụng gốc, bài chia sẻ, bài hỏi đáp/thảo luận, bài đã đóng và tin rác/lừa đảo.
5. Vệ sinh URL: Loại bỏ tham số tracking (fbclid, utm_*, ref, hrc...).
6. API và Nút 'Quét sâu MXH' báo cáo đầy đủ: queried_sources, failed_or_blocked_sources, scanned_at timestamp.
"""

from datetime import datetime, timedelta, timezone
import unittest

from app.adapters.base import AdapterErrorType
from app.adapters.local_enterprise_adapter import local_enterprise_adapter, LocalEnterpriseAdapter
from app.adapters.facebook_public_adapter import (
    facebook_public_adapter,
    FacebookPublicAdapter,
    FacebookPostType,
    sanitize_canonical_url,
)
from app.adapters.threads_public_adapter import threads_public_adapter, ThreadsPublicAdapter, clean_threads_url
from app.services.social_deep_harvester import social_deep_harvester


class TestSocialAndLocalAdapters(unittest.TestCase):
    def setUp(self):
        self.local_adapter = local_enterprise_adapter
        self.fb_adapter = facebook_public_adapter
        self.th_adapter = threads_public_adapter
        self.harvester = social_deep_harvester

    def test_01_local_enterprise_adapter_discovery(self):
        """
        Kiểm tra LocalEnterpriseAdapter phát hiện các việc làm chính thức từ Sun Group, Vinpearl, TKV, Wyndham Legend.
        Đảm bảo trích xuất địa chỉ chuẩn, hotline HR và URL ứng tuyển trực tiếp.
        """
        res = self.local_adapter.discover_jobs(province="Quảng Ninh", limit=10)

        self.assertTrue(res.is_successful)
        self.assertGreaterEqual(len(res.items), 4)

        # Kiểm tra tính toàn vẹn của từng bản ghi
        for item in res.items:
            self.assertEqual(item.location_province, "Quảng Ninh")
            self.assertIn(item.location_district, ["Hạ Long", "Cẩm Phả"])
            self.assertTrue(item.apply_url.startswith("http"))
            self.assertEqual(item.status, "active_confirmed")
            self.assertEqual(item.post_classification, "original_hiring_post")
            self.assertIsNotNone(item.author_name)
            self.assertIsNotNone(item.posted_at)
            self.assertIsNotNone(item.first_seen_at)

    def test_02_facebook_adapter_honest_credential_status_and_fallback(self):
        """
        Kiểm tra FacebookPublicAdapter:
        - Khi không có META_GRAPH_API_TOKEN: Báo lỗi MISSING_CREDENTIALS trung thực, không giả vờ thành công.
        - Tự động kích hoạt chế độ Fallback qua cổng thông tin Fanpage công khai.
        """
        # Giả lập môi trường không có token
        adapter_no_token = FacebookPublicAdapter()
        adapter_no_token.api_token = None

        res = adapter_no_token.discover_jobs(keyword="sun world", province="Quảng Ninh")

        # Phải có lỗi MISSING_CREDENTIALS trong danh sách errors
        error_types = [err.error_type for err in res.errors]
        self.assertIn(AdapterErrorType.MISSING_CREDENTIALS, error_types)
        self.assertEqual(res.raw_metadata["access_mode"], "public_page_fallback")
        self.assertFalse(res.raw_metadata["api_credential_present"])

        # Vẫn lấy được tin qua kênh fallback công khai
        self.assertGreater(len(res.items), 0)
        for item in res.items:
            self.assertEqual(item.raw_data_reference["access_mode"], "public_page_fallback")

    def test_03_facebook_post_classification(self):
        """
        Kiểm tra phân loại bài đăng Facebook:
        - Bài tuyển dụng gốc: Giữ lại.
        - Bài thảo luận / hỏi đáp ("Cho em hỏi...", "Review môi trường..."): Bị loại bỏ.
        - Bài đã đóng ("Đã tuyển đủ"): Phân loại EXPIRED_CLOSED.
        - Bài spam / lừa đảo ("Nạp tiền làm nhiệm vụ Telegram..."): Bị loại bỏ 100%.
        """
        self.assertEqual(
            self.fb_adapter.classify_post("Tuyển dụng 02 kỹ sư lập trình Python Bãi Cháy lương 20tr"),
            FacebookPostType.ORIGINAL_HIRING,
        )
        self.assertEqual(
            self.fb_adapter.classify_post("Mọi người ơi cho em hỏi làm ở khách sạn này có ổn không ạ?"),
            FacebookPostType.DISCUSSION_QUESTION,
        )
        self.assertEqual(
            self.fb_adapter.classify_post("Nhà hàng thông báo đã tuyển đủ người, cảm ơn các bạn!"),
            FacebookPostType.EXPIRED_CLOSED,
        )
        self.assertEqual(
            self.fb_adapter.classify_post("Xem video like tiktok kiếm 500k làm nhiệm vụ nạp tiền rút lời qua telegram"),
            FacebookPostType.SPAM_COMMERCIAL,
        )

    def test_04_canonical_url_sanitization(self):
        """
        Kiểm tra loại bỏ toàn bộ tham số theo dõi (fbclid, utm_*, ref, igshid...) khỏi canonical URL.
        """
        raw_fb = "https://www.facebook.com/sunworld/posts/12345?fbclid=IwAR3xyz_tracking&utm_source=feed&ref=page_internal"
        cleaned_fb = sanitize_canonical_url(raw_fb)
        self.assertNotIn("fbclid", cleaned_fb)
        self.assertNotIn("utm_source", cleaned_fb)
        self.assertNotIn("ref", cleaned_fb)
        self.assertEqual(cleaned_fb, "https://www.facebook.com/sunworld/posts/12345")

        raw_th = "https://www.threads.net/@studio/post/123?xmt=AQG_test&igshid=sample_token"
        cleaned_th = clean_threads_url(raw_th)
        self.assertNotIn("xmt", cleaned_th)
        self.assertNotIn("igshid", cleaned_th)
        self.assertEqual(cleaned_th, "https://www.threads.net/@studio/post/123")

    def test_05_threads_adapter_discussion_filtering(self):
        """
        Kiểm tra ThreadsPublicAdapter loại bỏ các bài chat tâm sự Gen Z,
        chỉ giữ lại các bài đăng tuyển dụng thực tế của thương hiệu (@halongtech_studio, @thehillside_halong).
        """
        res = self.th_adapter.discover_jobs(province="Quảng Ninh")
        self.assertTrue(res.is_successful)
        for item in res.items:
            self.assertIn("@", item.author_id)
            self.assertIn("Hạ Long", item.location_raw)
            self.assertEqual(item.post_classification, "original_hiring_post")

    def test_06_social_deep_harvester_telemetry_reporting(self):
        """
        Kiểm tra Nút 'Quét sâu MXH' trả về đầy đủ:
        - scanned_at: Timestamp thời điểm quét.
        - queried_sources: Danh sách các nguồn thực sự được truy vấn kèm latency và items_count.
        - failed_or_blocked_sources: Báo rõ các nguồn thiếu credential hoặc bị chặn kèm hành động fallback.
        - post_types_summary: Thống kê số bài gốc, bài chia sẻ, bài thảo luận đã lọc, bài spam đã chặn.
        """
        harvest_result = self.harvester.execute_social_deep_harvest(keyword="IT Hạ Long")

        self.assertTrue(harvest_result["success"])
        self.assertIn("scanned_at", harvest_result)
        self.assertTrue(harvest_result["scanned_at"].startswith("202"))

        # Kiểm tra queried_sources
        queried = harvest_result.get("queried_sources", [])
        self.assertGreaterEqual(len(queried), 2)
        source_ids = [s["source_id"] for s in queried]
        self.assertIn("facebook_public", source_ids)
        self.assertIn("threads_public", source_ids)

        # Kiểm tra failed_or_blocked_sources
        failed = harvest_result.get("failed_or_blocked_sources", [])
        self.assertGreaterEqual(len(failed), 1)
        for f in failed:
            self.assertIn(f["status"], ["missing_credentials", "blocked", "unsupported", "error"])
            self.assertTrue(f["fallback_applied"])

        # Kiểm tra post_types_summary
        summary = harvest_result.get("post_types_summary", {})
        self.assertIn("original_hiring", summary)
        self.assertIn("discussions_filtered", summary)
        self.assertIn("spam_rejected", summary)
        self.assertGreater(summary["spam_rejected"], 0)


if __name__ == "__main__":
    unittest.main()
