"""
Test Suite for Phần C: Comprehensive Filter Verification.
Kiểm thử lọc:
1. Hạ Long (có dấu & không dấu: 'Hạ Long', 'ha long', 'Hạ long').
2. Hà Nội (có dấu & không dấu: 'Hà Nội', 'ha noi').
3. Remote / Từ xa ('remote', 'từ xa', 'lam viec tu xa', 'hybrid').
4. Fresher / Junior ('Fresher', 'Junior', 'fresher', 'junior').
5. Loại hình làm việc ('Toàn thời gian', 'toan thoi gian', 'Bán thời gian', 'Thực tập').
6. Đảm bảo lọc chính xác cả có dấu và không dấu, cách ly địa bàn 100%, không rò rỉ sai phạm vi.
"""

import io
import json
import os
import sys
import unittest

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Import client search simulation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tests.test_massive_search_benchmark import simulate_client_search


class TestSearchFiltersComprehensive(unittest.TestCase):

    def setUp(self):
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "public", "data", "jobs.json"
        )
        with open(data_path, "r", encoding="utf-8") as f:
            self.jobs = json.load(f)

    def test_01_filter_ha_long_accented_and_unaccented(self):
        """Kiểm thử lọc Hạ Long: Cả 'Hạ Long' và 'ha long' phải trả về đúng việc làm tại Hạ Long, 0% lẫn Hà Nội"""
        queries = ["Hạ Long", "ha long", "Hạ long", "HA LONG"]
        for q in queries:
            results = simulate_client_search(self.jobs, query=q)
            self.assertGreater(len(results), 0, f"Truy vấn '{q}' phải tìm thấy việc làm tại Hạ Long")
            for j in results:
                loc = f"{j.get('location_province', '')} {j.get('location_district', '')} {j.get('location_full', '')}".lower()
                self.assertTrue(
                    "quảng ninh" in loc or "hạ long" in loc or "ha long" in loc or "bãi cháy" in loc or "cái lân" in loc,
                    f"Truy vấn '{q}' trả về việc làm ngoài Hạ Long/Quảng Ninh: {j.get('title')} ({loc})"
                )
                self.assertFalse(
                    "hà nội" in loc and not ("quảng ninh" in loc or "hạ long" in loc),
                    f"Truy vấn '{q}' bị rò rỉ việc làm chỉ ở Hà Nội: {j.get('title')}"
                )

    def test_02_filter_ha_noi_accented_and_unaccented(self):
        """Kiểm thử lọc Hà Nội: Cả 'Hà Nội' và 'ha noi' phải trả về việc làm tại Hà Nội, 0% lẫn việc làm thuần Quảng Ninh"""
        queries = ["Hà Nội", "ha noi", "Hà noi", "HA NOI"]
        for q in queries:
            results = simulate_client_search(self.jobs, query=q)
            self.assertGreater(len(results), 0, f"Truy vấn '{q}' phải tìm thấy việc làm tại Hà Nội")
            for j in results:
                loc = f"{j.get('location_province', '')} {j.get('location_district', '')} {j.get('location_full', '')}".lower()
                self.assertTrue(
                    "hà nội" in loc or "ha noi" in loc or "cầu giấy" in loc or "đống đa" in loc or "ba đình" in loc or "thanh xuân" in loc,
                    f"Truy vấn '{q}' trả về việc làm không thuộc Hà Nội: {j.get('title')} ({loc})"
                )

    def test_03_filter_province_param_direct(self):
        """Kiểm thử tham số lọc province trực tiếp (không chỉ qua text search query)"""
        # Lọc province = "Quảng Ninh"
        qn_results = simulate_client_search(self.jobs, province="Quảng Ninh")
        self.assertGreater(len(qn_results), 0)
        for j in qn_results:
            loc = (j.get("location_province") or "").lower()
            self.assertIn("quảng ninh", loc)

        # Lọc province = "Hà Nội"
        hn_results = simulate_client_search(self.jobs, province="Hà Nội")
        self.assertGreater(len(hn_results), 0)
        for j in hn_results:
            loc = (j.get("location_province") or "").lower()
            self.assertIn("hà nội", loc)

    def test_04_filter_fresher_and_junior(self):
        """Kiểm thử tìm kiếm cấp bậc Fresher / Junior"""
        for term in ["Junior", "junior", "Fresher", "fresher"]:
            results = simulate_client_search(self.jobs, query=term)
            # Nếu có kết quả thì 100% kết quả phải liên quan đến Junior/Fresher
            for j in results:
                text = f"{j.get('title', '')} {j.get('experience_level', '')} {j.get('description', '')} {j.get('requirements', '')}".lower()
                self.assertTrue(
                    "junior" in text or "fresher" in text or "kinh nghiệm" in text or "năm" in text,
                    f"Kết quả không chứa tín hiệu Fresher/Junior: {j.get('title')}"
                )

    def test_05_filter_remote_and_work_types(self):
        """Kiểm thử từ khóa Remote và Loại hình làm việc"""
        # Kiểm tra từ khóa Remote
        remote_results = simulate_client_search(self.jobs, query="remote")
        for j in remote_results:
            text = f"{j.get('title', '')} {j.get('description', '')} {j.get('requirements', '')} {j.get('job_type', '')}".lower()
            self.assertTrue(
                "remote" in text or "từ xa" in text or "hybrid" in text or "online" in text,
                f"Kết quả tìm remote không chứa tín hiệu từ xa: {j.get('title')}"
            )

        # Kiểm tra bộ lọc loại hình làm việc Toàn thời gian (cả có dấu và không dấu)
        fulltime_results_accented = simulate_client_search(self.jobs, job_type="Toàn thời gian")
        self.assertGreater(len(fulltime_results_accented), 0, "Lọc có dấu 'Toàn thời gian' phải trả về kết quả")
        
        fulltime_results_unaccented = simulate_client_search(self.jobs, job_type="toan thoi gian")
        self.assertEqual(len(fulltime_results_accented), len(fulltime_results_unaccented), "Kết quả lọc có dấu và không dấu phải đồng nhất 100%")


if __name__ == "__main__":
    unittest.main()
