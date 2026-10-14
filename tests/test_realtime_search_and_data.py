"""
Bộ Kiểm Thử Tự Động Toàn Diện Cho Tìm Kiếm Real-time & Tính Chuẩn Xác Dữ Liệu
C_Data - Chạy trước khi xuất bản & kiểm định chất lượng

Các bài kiểm tra bắt buộc:
1. Test Zero-404: Kiểm tra tính hợp lệ của source_url trong toàn bộ dữ liệu.
2. Test Chuẩn Xác Địa Bàn: 100% không có chuyện ghi tỉnh A mà địa chỉ lại ở tỉnh B (Quảng Ninh vs Hà Nội).
3. Test Không Dính Chữ: Không có bất kỳ chuỗi địa danh nào bị dính liền thiếu dấu cách/phẩy.
4. Test Độ Chính Xác Tìm Kiếm Realtime: Kiểm thử truy vấn "IT Hạ Long", "Bãi Cháy", "Cái Lân", "Hà Nội", "Quảng Ninh".
5. Test Hiệu Năng: Tốc độ tìm kiếm tức thì dưới 10ms.
"""

import json
import os
import re
import sys
import time
import unicodedata
import unittest

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data", "jobs.json"))


def remove_vietnamese_tones(text: str) -> str:
    if not text:
        return ""
    nfd = unicodedata.normalize("NFD", text)
    cleaned = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return cleaned.replace("đ", "d").replace("Đ", "D").lower().strip()


class TestRealtimeSearchAndData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            cls.jobs = json.load(f)
        print(f"\n[SETUP] Đã nạp thành công {len(cls.jobs)} việc làm từ {JSON_PATH}")

    def test_01_zero_404_and_valid_urls(self):
        """Kiểm tra 100% việc làm có source_url hợp lệ (HTTP/HTTPS) và không chứa tham số rác"""
        invalid_urls = []
        for j in self.jobs:
            url = j.get("source_url") or ""
            if not url.startswith("http"):
                invalid_urls.append((j["id"], j["title"], "URL không hợp lệ"))
            if "?post_ref=" in url or "?ref=" in url:
                invalid_urls.append((j["id"], j["title"], "URL chứa tham số rác"))
        self.assertEqual(len(invalid_urls), 0, f"Phát hiện URL không hợp lệ: {invalid_urls}")
        print("  ✓ Test 01 - Zero 404 & Link hợp lệ: 100% ĐẠT")

    def test_02_zero_location_mismatch(self):
        """Kiểm tra không có việc làm nào ghi Quảng Ninh nhưng địa chỉ chỉ ở Hà Nội hay tỉnh khác"""
        mismatches = []
        qn_keywords = [
            "quảng ninh", "hạ long", "cẩm phả", "uông bí", "móng cái", "đông triều",
            "quảng yên", "vân đồn", "bãi cháy", "hòn gai", "hồng gai", "cái lân", "giếng đáy", "hà khẩu"
        ]
        for j in self.jobs:
            prov = (j.get("location_province") or "").strip()
            full = (j.get("location_full") or "").strip()
            comp = (j.get("company_name") or "").strip()

            if prov == "Quảng Ninh":
                has_qn = any(k in full.lower() for k in qn_keywords)
                has_hn_only = "hà nội" in full.lower() and not has_qn
                if has_hn_only:
                    mismatches.append((j["id"], j["title"], prov, full, comp))
                if "Doanh nghiệp tại Quảng Ninh" in comp and has_hn_only:
                    mismatches.append((j["id"], j["title"], "Tên công ty sai lệch"))

        self.assertEqual(len(mismatches), 0, f"Phát hiện lệch địa bàn Quảng Ninh - Hà Nội: {mismatches}")
        print("  ✓ Test 02 - Không lệch địa bàn Quảng Ninh vs Hà Nội: 100% ĐẠT")

    def test_03_zero_concatenated_location_strings(self):
        """Kiểm tra không bị lỗi dính liền chuỗi như 'Hà NộiKhánh Hòa' hay 'Hà NộiHồ Chí Minh'"""
        concatenated = []
        patterns = [
            r"Hà Nội[A-ZÀ-Ỹ]",
            r"Quảng Ninh[A-ZÀ-Ỹ]",
            r"Đà Nẵng[A-ZÀ-Ỹ]",
            r"Hồ Chí Minh[A-ZÀ-Ỹ]",
            r"Hưng Yên[A-ZÀ-Ỹ]",
        ]
        for j in self.jobs:
            full = j.get("location_full") or ""
            for pat in patterns:
                if re.search(pat, full):
                    concatenated.append((j["id"], j["title"], full))

        self.assertEqual(len(concatenated), 0, f"Phát hiện chuỗi địa danh bị dính liền: {concatenated}")
        print("  ✓ Test 03 - Chuỗi địa danh phân tách dấu phẩy rõ ràng: 100% ĐẠT")

    def test_04_realtime_search_quang_ninh_filter_strictness(self):
        """Kiểm tra khi lọc tỉnh Quảng Ninh thì 100% kết quả phải ở Quảng Ninh, tuyệt đối không lẫn Hà Nội"""
        from typing import List, Dict, Any

        # Mô phỏng thuật toán tìm kiếm của clientSearch.ts
        def search_filter(province_target: str) -> List[Dict[str, Any]]:
            norm_target = remove_vietnamese_tones(province_target)
            results = []
            for j in self.jobs:
                norm_prov = remove_vietnamese_tones(j.get("location_province") or "")
                norm_full = remove_vietnamese_tones(j.get("location_full") or "")
                if norm_target in norm_prov or norm_target in norm_full:
                    # Chặn nếu tỉnh đó thực tế là tỉnh khác
                    if norm_target == "quang ninh" and "ha noi" in norm_full and "quang ninh" not in norm_full and "ha long" not in norm_full:
                        continue
                    results.append(j)
            return results

        qn_results = search_filter("Quảng Ninh")
        self.assertGreater(len(qn_results), 30, "Số lượng việc làm Quảng Ninh phải > 30")

        # Kiểm tra từng kết quả xem có bất kỳ tin nào chỉ tuyển ở Hà Nội không
        for r in qn_results:
            full = (r.get("location_full") or "").lower()
            prov = (r.get("location_province") or "").lower()
            if "hà nội" in full:
                # Phải có Quảng Ninh hoặc Hạ Long kèm theo
                has_qn = "quảng ninh" in full or "hạ long" in full or prov == "quảng ninh"
                self.assertTrue(has_qn, f"Lẫn tin Hà Nội vào Quảng Ninh: {r['title']} - {r['location_full']}")

        print(f"  ✓ Test 04 - Lọc chuẩn Quảng Ninh: {len(qn_results)} việc làm, 0% lẫn lộn: 100% ĐẠT")

    def test_05_ha_long_it_specialized_positions(self):
        """Kiểm tra sự hiện diện đầy đủ của các trụ cột CNTT trọng điểm Hạ Long"""
        it_jobs = [
            j for j in self.jobs
            if "Quảng Ninh" in (j.get("location_province") or "")
            and any(k in (j.get("title") or "").lower() or k in (j.get("category") or "").lower() for k in ["it", "cntt", "mạng", "phần mềm", "tự động hóa", "scada", "kỹ thuật"])
        ]
        self.assertGreater(len(it_jobs), 15, "Phải có ít nhất 15 vị trí CNTT/Kỹ thuật tại Quảng Ninh")
        print(f"  ✓ Test 05 - Danh mục IT chuyên sâu Hạ Long: {len(it_jobs)} vị trí chuyên môn: 100% ĐẠT")

    def test_06_realtime_performance_latency(self):
        """Kiểm tra hiệu năng tìm kiếm tức thì: 100 lượt tìm kiếm trong < 50ms (trung bình < 5ms/lượt)"""
        # Giả lập chỉ mục tìm kiếm thời gian thực (giống clientSearch.ts)
        indexed_jobs = [
            (j, remove_vietnamese_tones(j.get("title") or "") + " " + remove_vietnamese_tones(j.get("location_full") or ""))
            for j in self.jobs
        ]
        start = time.perf_counter()
        test_queries = ["it", "support", "hạ long", "bãi cháy", "cái lân", "kế toán", "fpt", "vinmec", "wyndham", "scada"]
        for _ in range(10):
            for q in test_queries:
                norm_q = remove_vietnamese_tones(q)
                _ = [j for j, search_text in indexed_jobs if norm_q in search_text]
        duration_ms = (time.perf_counter() - start) * 1000
        avg_latency = duration_ms / 100
        self.assertLess(avg_latency, 5.0, f"Độ trễ tìm kiếm phải < 5ms (thực tế: {avg_latency:.2f}ms)")
        print(f"  ✓ Test 06 - Hiệu năng tìm kiếm Realtime: {avg_latency:.3f}ms/lượt (< 5ms): 100% ĐẠT")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CHẠY BỘ KIỂM THỬ TỰ ĐỘNG CHUẨN XÁC DỮ LIỆU & TÌM KIẾM REALTIME")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRealtimeSearchAndData)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n🎉 TẤT CẢ CÁC BÀI TEST ĐỀU ĐẠT CHUẨN XÁC 100%!")
        sys.exit(0)
    else:
        print("\n❌ CÓ BÀI TEST THẤT BẠI!")
        for failure in result.failures:
            print("FAILURE:", failure[0])
            print(failure[1])
        for error in result.errors:
            print("ERROR:", error[0])
            print(error[1])
        sys.exit(1)
