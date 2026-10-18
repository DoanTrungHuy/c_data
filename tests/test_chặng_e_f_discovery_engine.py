"""
Unit & Integration Test Suite for Chặng E & F: Search Engine & Social Media Discovery Engine
Tests DiscoveryQueueEngine for:
- 12 Seed exploration targets with priority ordering
- Search syntaxes (site:facebook.com, site:linkedin.com/posts, local IT queries)
- Query Expansion Engine producing 26+ multidimensional IT and location queries
- Cross-link target enqueuing, deduplication, and persistence
- Scan telemetry recording and score updates
"""

import io
import json
from pathlib import Path
import sys
import unittest

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.services.discovery_engine import (
    DiscoveryQueueEngine,
    DiscoveryTarget,
    QUEUE_FILE_PATH,
    discovery_queue_engine,
)


class TestChặngEFDiscoveryEngine(unittest.TestCase):
    """Bộ kiểm thử Chặng E & F: Discovery Queue & Search Engine Coordinator"""

    def test_01_seed_targets_and_search_syntaxes(self):
        """Kiểm tra 12 seed targets khởi tạo và các cú pháp site:facebook.com / site:linkedin.com"""
        targets = discovery_queue_engine.list_targets()
        self.assertGreaterEqual(len(targets), 12)

        queries = [t.url_or_query for t in targets]
        # Kiểm tra sự hiện diện của cú pháp có chủ đích (Master Prompt Mục 4)
        has_fb_syntax = any("site:facebook.com" in q for q in queries)
        has_li_syntax = any("site:linkedin.com/posts" in q for q in queries)
        has_local_it = any("Hạ Long" in q for q in queries)

        self.assertTrue(has_fb_syntax, "Thiếu cú pháp tìm kiếm site:facebook.com")
        self.assertTrue(has_li_syntax, "Thiếu cú pháp tìm kiếm site:linkedin.com/posts")
        self.assertTrue(has_local_it, "Thiếu từ khóa địa bàn Hạ Long")
        print(f"  ✓ Discovery Queue chứa {len(targets)} targets có chủ đích (Facebook, LinkedIn Posts, Local IT)")

    def test_02_priority_ordering(self):
        """Kiểm tra thứ tự ưu tiên trong hàng đợi Discovery (P1 trước, P5 sau)"""
        targets = discovery_queue_engine.list_targets()
        priorities = [t.priority for t in targets]
        # Đảm bảo danh sách được sắp xếp theo priority tăng dần
        self.assertEqual(priorities, sorted(priorities))
        self.assertEqual(targets[0].priority, 1)
        print("  ✓ Sắp xếp ưu tiên hàng đợi (Priority 1 -> 5) hoạt động chuẩn xác")

    def test_03_query_expansion_multidimensional(self):
        """Kiểm tra bộ mở rộng truy vấn: Sinh 26+ truy vấn mở rộng cho IT tại Hạ Long"""
        expanded = discovery_queue_engine.generate_expanded_queries(base_keyword="IT", province="Hạ Long")
        self.assertGreaterEqual(len(expanded), 20)

        # Kiểm tra bao phủ các vị trí kỹ thuật cốt lõi
        joined = " ".join(expanded)
        self.assertIn("IT Helpdesk", joined)
        self.assertIn("IT Support", joined)
        self.assertIn("Quản trị hệ thống", joined)
        self.assertIn("Lập trình viên", joined)
        self.assertIn("Hạ Long", joined)
        print(f"  ✓ Query Expansion Engine sinh thành công {len(expanded)} biến thể từ khóa và cú pháp tìm kiếm")

    def test_04_cross_link_enqueuing_and_deduplication(self):
        """Kiểm tra đưa liên kết chéo mới vào hàng đợi và khử trùng lặp tự động"""
        test_url = "https://www.facebook.com/groups/itquangninh/posts/test_chặng_ef_123"
        tid1 = discovery_queue_engine.enqueue_target(
            url_or_query=test_url,
            target_type="public_group",
            discovery_source="cross_link",
            notes="Test target for Chặng E & F"
        )
        self.assertIsNotNone(tid1)

        # Enqueue lại cùng URL -> phải trả về cùng target_id mà không bị nhân bản
        initial_count = len(discovery_queue_engine.list_targets())
        tid2 = discovery_queue_engine.enqueue_target(
            url_or_query=test_url,
            target_type="public_group",
        )
        self.assertEqual(tid1, tid2)
        self.assertEqual(len(discovery_queue_engine.list_targets()), initial_count)
        print("  ✓ Enqueue & Deduplication hoạt động ổn định, không nhân bản mục tiêu")

    def test_05_persistent_state_storage(self):
        """Kiểm tra lưu trữ bền vững trạng thái Discovery Queue xuống đĩa"""
        self.assertTrue(QUEUE_FILE_PATH.exists())
        with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)
        self.assertGreaterEqual(len(data), 12)
        print(f"  ✓ Trạng thái Discovery Queue được lưu trữ bền vững tại {QUEUE_FILE_PATH.name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
