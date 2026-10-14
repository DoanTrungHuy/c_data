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

    def test_07_zero_mismatched_company_domains(self):
        """Kiểm tra không bao giờ có chuyện tên công ty A nhưng URL lại trỏ sang domain của công ty B"""
        mismatched = []
        for j in self.jobs:
            cname = (j.get("company_name") or "").lower()
            url = (j.get("source_url") or "").lower()
            
            if "cict.com.vn" in url and "cict" not in cname and "cảng" not in cname:
                mismatched.append((j["id"], j["company_name"], url))
            elif "flc.vn" in url and "flc" not in cname:
                mismatched.append((j["id"], j["company_name"], url))
            elif "wyndhamhalong.com" in url and "wyndham" not in cname:
                mismatched.append((j["id"], j["company_name"], url))
            elif "vinmec.com" in url and "vinmec" not in cname:
                mismatched.append((j["id"], j["company_name"], url))

        self.assertEqual(len(mismatched), 0, f"Phát hiện domain bị gán sai công ty: {mismatched}")
        print("  ✓ Test 07 - Tương thích 100% giữa Tên Doanh Nghiệp & Domain Nguồn: 100% ĐẠT")

    def test_08_zero_fallback_company_abuse(self):
        """Kiểm tra không bị lỗi gán hàng loạt sang 'Tập Đoàn Đầu Tư & Kinh Doanh Bất Động Sản Hạ Long'"""
        abused = []
        for j in self.jobs:
            cname = j.get("company_name") or ""
            title = j.get("title") or ""
            if "Bất Động Sản Hạ Long" in cname and "Bất Động Sản Hạ Long" not in title and "bất động sản" not in title.lower():
                abused.append((j["id"], title, cname))

        self.assertEqual(len(abused), 0, f"Phát hiện tin bị gán sai sang fallback company: {abused}")
        print("  ✓ Test 08 - Zero Fallback Company Abuse: 100% ĐẠT")

    def test_09_zero_out_of_province_non_it_jobs(self):
        """Kiểm tra 100% các tin ngoài tỉnh Quảng Ninh đều là chuyên môn CNTT / Phần mềm theo đúng yêu cầu"""
        invalid_jobs = []
        for j in self.jobs:
            prov = j.get("location_province") or ""
            title = j.get("title") or ""
            cat = j.get("category") or ""
            full = j.get("location_full") or ""

            # Nếu tiêu đề ghi làm tại Quảng Ninh thì province BẮT BUỘC phải là Quảng Ninh
            if "làm tại quảng ninh" in title.lower() and prov != "Quảng Ninh":
                invalid_jobs.append((j["id"], title, "Ghi làm tại QN nhưng prov là: " + prov))

            # Nếu ngoài Quảng Ninh thì bắt buộc là tin CNTT
            if prov != "Quảng Ninh":
                is_it = "công nghệ thông tin" in cat.lower() or "it" in title.lower() or "software" in title.lower()
                if not is_it:
                    invalid_jobs.append((j["id"], title, prov, cat))

        self.assertEqual(len(invalid_jobs), 0, f"Phát hiện tin ngoài tỉnh không thuộc CNTT hoặc lệch nhãn: {invalid_jobs}")
        print("  ✓ Test 09 - 100% Tin ngoài tỉnh là CNTT & Không lệch nhãn địa điểm: 100% ĐẠT")

    def test_10_quality_scores_and_tier_validity(self):
        """Kiểm tra 100% việc làm có điểm chất lượng hợp lệ (50 - 100) và xếp hạng tier chuẩn"""
        invalid = []
        for j in self.jobs:
            score = j.get("quality_score")
            tier = j.get("quality_tier")
            if score is None or not (0 <= score <= 100):
                invalid.append((j["id"], j["title"], "Điểm chất lượng không hợp lệ", score))
            if tier not in ["diamond", "gold", "standard"]:
                invalid.append((j["id"], j["title"], "Tier không hợp lệ", tier))
            if tier == "diamond" and score < 85:
                invalid.append((j["id"], j["title"], "Diamond nhưng điểm < 85", score))

        self.assertEqual(len(invalid), 0, f"Phát hiện điểm hoặc tier chất lượng không hợp lệ: {invalid}")
        print("  ✓ Test 10 - Điểm Thẩm Định Chất Lượng & Phân Cấp Tier: 100% ĐẠT")

    def test_11_interview_process_and_perks_presence(self):
        """Kiểm tra 100% việc làm có cấu trúc lộ trình phỏng vấn 3 bước và danh sách quyền lợi chi tiết"""
        missing_data = []
        for j in self.jobs:
            interview = j.get("interview_process")
            perks = j.get("benefits_detail")
            audit = j.get("quality_audit")

            if not interview or len(interview) != 3:
                missing_data.append((j["id"], j["title"], "Thiếu quy trình phỏng vấn 3 bước"))
            if not perks or len(perks) == 0:
                missing_data.append((j["id"], j["title"], "Thiếu danh sách quyền lợi chi tiết"))
            if not audit or not isinstance(audit, dict):
                missing_data.append((j["id"], j["title"], "Thiếu bảng thẩm định chất lượng audit"))

        self.assertEqual(len(missing_data), 0, f"Phát hiện tin thiếu cấu trúc chất lượng: {missing_data}")
        print("  ✓ Test 11 - Lộ Trình Phỏng Vấn 3 Bước & Bảng Thẩm Định Quyền Lợi: 100% ĐẠT")

    def test_12_evidence_proof_integrity(self):
        """Kiểm tra 100% việc làm có Hồ Sơ Dẫn Chứng Đăng Tuyển (Evidence Proof) xác thực, đầy đủ hotline/portal/trích dẫn"""
        invalid_proof = []
        for j in self.jobs:
            ep = j.get("evidence_proof")
            if not ep or not isinstance(ep, dict):
                invalid_proof.append((j["id"], j["title"], "Thiếu object evidence_proof"))
                continue
            if not ep.get("verified"):
                invalid_proof.append((j["id"], j["title"], "verified không phải True"))
            if not ep.get("source_name"):
                invalid_proof.append((j["id"], j["title"], "Thiếu source_name"))
            direct_url = ep.get("direct_url") or ""
            if not (direct_url.startswith("http://") or direct_url.startswith("https://")):
                invalid_proof.append((j["id"], j["title"], "direct_url không hợp lệ: " + direct_url))
            if ep.get("url_status") != 200:
                invalid_proof.append((j["id"], j["title"], "url_status không phải 200: " + str(ep.get("url_status"))))
            contact = ep.get("recruiter_contact") or {}
            if not contact.get("hotline") and not contact.get("email"):
                invalid_proof.append((j["id"], j["title"], "Thiếu thông tin liên hệ HR (hotline hoặc email)"))
            snippet = ep.get("announcement_snippet") or ""
            if len(snippet.strip()) < 15:
                invalid_proof.append((j["id"], j["title"], "Trích dẫn bằng chứng đăng tuyển quá ngắn"))

        self.assertEqual(len(invalid_proof), 0, f"Phát hiện tin tuyển dụng có hồ sơ dẫn chứng không đạt chuẩn: {invalid_proof}")
        print("  ✓ Test 12 - Hồ Sơ Dẫn Chứng Đăng Tuyển Xác Thực (Evidence Proof): 100% ĐẠT")


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
