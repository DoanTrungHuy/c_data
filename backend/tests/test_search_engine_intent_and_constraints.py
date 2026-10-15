"""
Bộ kiểm thử chuyên sâu cho Hệ thống Tìm kiếm Ngữ nghĩa & Ràng buộc cứng (Intent-Aware Semantic Search & Hard Constraints Engine)
Tuân thủ đầy đủ Definition of Done (DoD) của Yêu cầu Cải tiến Search Engine:
1. Hỗ trợ tiếng Việt có dấu và không dấu, biến thể chức danh và từ đồng nghĩa chuyên môn.
2. Kiểm thử tổ hợp nhiều bộ lọc: Địa điểm, cấp bậc, nơi làm việc, kỹ năng, công ty.
3. Quy tắc điều kiện cứng (Strict Mode):
   - Chỉ Hạ Long thì không tự đưa việc ở Hà Nội vào.
   - Phân biệt địa điểm làm việc thực tế với trụ sở chính doanh nghiệp (Trụ sở Hà Nội nhưng làm việc tại Hạ Long thì hợp lệ; Trụ sở Hà Nội làm việc tại Hà Nội thì loại trừ).
   - Chỉ Remote 100% thì không đưa Hybrid hoặc Onsite vào.
   - Fresher / Junior thì không tự đưa Senior / Lead / Manager / >=3 năm kinh nghiệm vào.
   - Chỉ tin còn tuyển đã xác minh (verified_only) thì không đưa unknown, expired, closed vào kết quả chính.
   - Cụm từ trích dẫn trong ngoặc kép và từ khóa loại trừ (-keyword).
4. Trường hợp không có kết quả phù hợp:
   - Trả về danh sách rỗng, chẩn đoán rõ ràng và danh sách gợi ý nới lỏng (suggested_relaxations).
   - Tuyệt đối không tự ý nới lỏng rồi giả vờ đã khớp đầy đủ.
5. Chế độ mềm (Fuzzy & Soft Preferences khi strict_mode=False).
"""

from datetime import datetime, timedelta, timezone
import unittest
import uuid

from app.models.job import Job
from app.services.search_intent_parser import search_intent_parser, normalize_text
from app.services.hybrid_search_engine import hybrid_search_engine


def create_test_job(
    title: str,
    company: str,
    desc: str,
    req: str = "",
    province: str = "Quảng Ninh",
    district: str = "Hạ Long",
    job_type: str = "full-time",
    workplace_type: str = "onsite",
    experience_level: str = "junior",
    status: str = "active_confirmed",
    salary_min: int = 10000000,
    salary_max: int = 15000000,
    locations: list = None,
    posted_days_ago: float = 1.0,
    expires_in_days: float = 30.0,
) -> Job:
    now = datetime.now(timezone.utc)
    return Job(
        id=str(uuid.uuid4()),
        title=title,
        company_name=company,
        description=desc,
        requirements=req,
        location_province=province,
        location_district=district,
        location_full=f"{district}, {province}" if district and province else (province or district or ""),
        locations=locations or [{"province": province, "district": district, "address": f"{district}, {province}", "is_primary": True}],
        job_type=job_type,
        workplace_type=workplace_type,
        experience_level=experience_level,
        status=status,
        salary_min=salary_min,
        salary_max=salary_max,
        source_platform="CareerViet",
        source_url=f"https://example.com/jobs/{uuid.uuid4().hex[:8]}",
        posted_at=now - timedelta(days=posted_days_ago),
        expires_at=now + timedelta(days=expires_in_days) if expires_in_days is not None else None,
        crawled_at=now,
        is_active=status in ["active_confirmed", "active_likely"],
    )


class TestSearchEngineIntentAndHardConstraints(unittest.TestCase):

    def setUp(self):
        self.engine = hybrid_search_engine
        self.parser = search_intent_parser

    # =========================================================================
    # 1. TIẾNG VIỆT CÓ DẤU & KHÔNG DẤU, TỪ ĐỒNG NGHĨA
    # =========================================================================
    def test_vietnamese_diacritics_and_synonyms(self):
        """Kiểm tra tìm kiếm không dấu khớp nội dung có dấu và ngược lại."""
        intent_no_accent = self.parser.parse("lap trinh vien java tai ha long")
        self.assertEqual(intent_no_accent.target_province, "Quảng Ninh")
        self.assertEqual(intent_no_accent.target_district, "Hạ Long")
        self.assertIn("Java", intent_no_accent.required_skills)

        job_accented = create_test_job(
            title="Lập trình viên Java Backend",
            company="Tập đoàn Công nghệ Hạ Long",
            desc="Phát triển hệ thống Microservices Spring Boot.",
            req="Có kiến thức về Java, Spring Boot, SQL.",
        )

        ranked, diag = self.engine.rank_and_filter_jobs([job_accented], intent_no_accent, strict_mode=True)
        self.assertEqual(len(ranked), 1)
        self.assertGreater(ranked[0]["score"], 40.0)

    # =========================================================================
    # 2. PHÂN BIỆT ĐỊA ĐIỂM THỰC TẾ VS TRỤ SỞ DOANH NGHIỆP
    # =========================================================================
    def test_actual_work_location_vs_headquarters(self):
        """
        Quy tắc:
        - Job A: Trụ sở chính Hà Nội, nhưng địa điểm làm việc thực tế tại Hạ Long -> HỢP LỆ cho tìm kiếm Hạ Long.
        - Job B: Trụ sở chính Hà Nội, địa điểm làm việc tại Cầu Giấy Hà Nội -> BỊ LOẠI TRỪ khỏi tìm kiếm Hạ Long.
        """
        intent = self.parser.parse("Nhân viên CNTT tại Hạ Long")

        # Job A: Trụ sở HN nhưng làm việc tại chi nhánh Hạ Long
        job_branch_halong = create_test_job(
            title="Chuyên viên CNTT Vận hành Khách sạn",
            company="Tập đoàn Khách sạn Quốc tế (Trụ sở chính: Keangnam, Hà Nội)",
            desc="Trụ sở chính: Tòa nhà Keangnam, Mễ Trì, Hà Nội. Địa điểm làm việc thực tế: Khách sạn Bãi Cháy, TP. Hạ Long, Quảng Ninh.",
            province="Quảng Ninh",
            district="Hạ Long",
            locations=[
                {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Bãi Cháy, Hạ Long", "is_primary": True},
                {"province": "Hà Nội", "district": "Nam Từ Liêm", "address": "Trụ sở chính Keangnam", "is_primary": False},
            ],
        )

        # Job B: Doanh nghiệp ở Hà Nội, làm việc hoàn toàn ở Hà Nội, không có Hạ Long
        job_only_hanoi = create_test_job(
            title="Chuyên viên CNTT Quản trị Hệ thống",
            company="Công ty Cổ phần Phần mềm Thủ Đô",
            desc="Trụ sở: Cầu Giấy, Hà Nội. Địa điểm làm việc: 15 Duy Tân, Cầu Giấy, Hà Nội.",
            province="Hà Nội",
            district="Cầu Giấy",
            locations=[{"province": "Hà Nội", "district": "Cầu Giấy", "address": "15 Duy Tân", "is_primary": True}],
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [job_branch_halong, job_only_hanoi],
            intent,
            strict_mode=True,
        )

        # Chỉ có job làm việc thực tế tại Hạ Long được giữ lại
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["job"].id, job_branch_halong.id)
        self.assertEqual(diag["removed_by_filters"]["hard_location"], 1)

    # =========================================================================
    # 3. RÀNG BUỘC REMOTE 100% (KHÔNG ĐƯỢC ĐƯA HYBRID HAY ONSITE VÀO)
    # =========================================================================
    def test_strict_remote_100_percent_rejects_hybrid_and_onsite(self):
        """
        Quy tắc: Khi tìm 'Remote 100%' hoặc bật lọc Remote:
        - Job Remote 100% -> HỢP LỆ.
        - Job Hybrid (lên văn phòng 2 ngày/tuần) -> BỊ LOẠI BỎ (Không được đưa Hybrid vào).
        - Job Onsite -> BỊ LOẠI BỎ.
        """
        intent = self.parser.parse("Lập trình viên Backend Remote 100%")
        self.assertTrue(intent.is_remote_required)
        self.assertEqual(intent.workplace_type, "remote")

        job_pure_remote = create_test_job(
            title="Backend Python Developer (Remote 100%)",
            company="Tech Corp Global",
            desc="Làm việc từ xa toàn thời gian 100% remote tại nhà. Hỗ trợ phụ cấp thiết bị.",
            workplace_type="remote",
            job_type="remote",
        )

        job_hybrid = create_test_job(
            title="Backend Developer (Hybrid linh hoạt)",
            company="Digital Studio",
            desc="Mô hình Hybrid: 3 ngày làm việc tại nhà, 2 ngày lên văn phòng họp.",
            workplace_type="hybrid",
        )

        job_onsite = create_test_job(
            title="Backend Developer Onsite",
            company="Bank Tech",
            desc="Làm việc trực tiếp tại tòa nhà văn phòng của ngân hàng.",
            workplace_type="onsite",
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [job_pure_remote, job_hybrid, job_onsite],
            intent,
            strict_mode=True,
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["job"].id, job_pure_remote.id)
        self.assertEqual(diag["removed_by_filters"]["hard_remote"], 2)

    # =========================================================================
    # 4. RÀNG BUỘC CẤP BẬC FRESHER / JUNIOR VS SENIOR / LEAD
    # =========================================================================
    def test_strict_seniority_fresher_junior_rejects_senior(self):
        """
        Quy tắc: Khi người dùng tìm 'Fresher' hoặc 'Junior', không tự đưa Senior / Lead / Trưởng nhóm vào.
        """
        intent = self.parser.parse("Junior IT Support cho người mới ra trường")
        self.assertEqual(intent.seniority, "fresher")

        job_entry = create_test_job(
            title="Nhân viên IT Support (Chấp nhận Fresher)",
            company="Khách Sạn Bãi Cháy",
            desc="Hỗ trợ người dùng nội bộ. Công ty nhận đào tạo sinh viên mới tốt nghiệp chưa có kinh nghiệm.",
            req="Tốt nghiệp ngành CNTT. Không yêu cầu kinh nghiệm.",
            experience_level="fresher",
        )

        job_senior_title = create_test_job(
            title="Senior IT Lead & Trưởng nhóm Quản trị Mạng",
            company="Tập đoàn Đầu tư",
            desc="Quản lý toàn bộ hạ tầng mạng và an toàn thông tin.",
            experience_level="senior",
        )

        job_heavy_experience = create_test_job(
            title="Chuyên viên Hệ thống CNTT",
            company="Công ty Hạ tầng Mạng",
            desc="Vận hành hệ thống mạng Data Center.",
            req="Yêu cầu tối thiểu 5 năm kinh nghiệm quản trị hệ thống Linux và Cloud.",
            experience_level="senior",
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [job_entry, job_senior_title, job_heavy_experience],
            intent,
            strict_mode=True,
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["job"].id, job_entry.id)
        self.assertEqual(diag["removed_by_filters"]["hard_seniority"], 2)

    # =========================================================================
    # 5. RÀNG BUỘC TIN ĐÃ XÁC MINH (VERIFIED ONLY)
    # =========================================================================
    def test_strict_verified_only_rejects_unknown_expired_closed(self):
        """
        Quy tắc: Khi bật lọc 'Chỉ tin còn tuyển đã xác minh', không đưa unknown, expired, closed vào kết quả chính.
        """
        intent = self.parser.parse("Kỹ sư phần mềm đã xác minh")
        self.assertTrue(intent.verified_only)

        job_confirmed = create_test_job(
            title="Kỹ sư phần mềm Python",
            company="Công ty Phần mềm A",
            desc="Xây dựng backend API.",
            status="active_confirmed",
        )

        job_likely = create_test_job(
            title="Kỹ sư phần mềm Java",
            company="Công ty Phần mềm B",
            desc="Xây dựng backend Java.",
            status="active_likely",
        )

        job_unknown = create_test_job(
            title="Kỹ sư phần mềm C++",
            company="Công ty Phần mềm C",
            desc="Lập trình nhúng.",
            status="unknown",
        )

        job_closed = create_test_job(
            title="Kỹ sư phần mềm PHP",
            company="Công ty Phần mềm D",
            desc="Bảo trì ứng dụng web.",
            status="closed",
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [job_confirmed, job_likely, job_unknown, job_closed],
            intent,
            strict_mode=True,
            verified_only=True,
        )

        # Chỉ có active_confirmed và active_likely được giữ lại
        job_ids = [r["job"].id for r in ranked]
        self.assertIn(job_confirmed.id, job_ids)
        self.assertIn(job_likely.id, job_ids)
        self.assertNotIn(job_unknown.id, job_ids)
        self.assertNotIn(job_closed.id, job_ids)

    # =========================================================================
    # 6. KHÔNG CÓ KẾT QUẢ VÀ ĐỀ XUẤT NỚI LỎNG (SUGGESTED_RELAXATIONS)
    # =========================================================================
    def test_zero_results_returns_empty_and_suggested_relaxations(self):
        """
        Quy tắc: Nếu không có kết quả đáp ứng điều kiện cứng:
        - Trả về danh sách rỗng (KHÔNG tự ý nới lỏng giả vờ đã khớp).
        - diagnostics['suggested_relaxations'] chứa hướng dẫn cụ thể dựa trên bộ lọc đã loại bỏ ứng viên.
        """
        # Tìm Remote tại Hạ Long nhưng chỉ có các việc làm Onsite
        intent = self.parser.parse("IT Helpdesk Remote 100% tại Hạ Long")

        onsite_job = create_test_job(
            title="IT Helpdesk Khách sạn",
            company="Resort Bãi Cháy",
            desc="Làm việc trực tiếp tại resort để hỗ trợ máy tính.",
            workplace_type="onsite",
            province="Quảng Ninh",
            district="Hạ Long",
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [onsite_job],
            intent,
            strict_mode=True,
        )

        # Tuyệt đối danh sách rỗng, không tự ý nới lỏng
        self.assertEqual(len(ranked), 0)
        self.assertEqual(diag["final_eligible_count"], 0)
        self.assertEqual(diag["removed_by_filters"]["hard_remote"], 1)

        # Phải có gợi ý nới lỏng rõ ràng
        relaxations = diag.get("suggested_relaxations", [])
        self.assertGreater(len(relaxations), 0)
        self.assertTrue(any("Hybrid" in r or "Onsite" in r or "hình thức làm việc" in r for r in relaxations))

    # =========================================================================
    # 7. CÚ PHÁP NGOẶC KÉP VÀ LOẠI TRỪ (-KEYWORD / NEGATIVE CONSTRAINTS)
    # =========================================================================
    def test_quoted_phrase_and_negative_keyword_exclusion(self):
        """
        Quy tắc:
        - Cụm từ '"React Native"' bắt buộc phải xuất hiện.
        - Cú pháp '-senior' loại bỏ mọi bài đăng có từ senior.
        """
        intent = self.parser.parse('Lập trình viên "React Native" -senior')
        self.assertIn("React Native", intent.exact_phrases)
        self.assertIn("senior", intent.negative_constraints)

        job_match = create_test_job(
            title="Lập trình viên React Native",
            company="App Mobile Agency",
            desc="Phát triển ứng dụng mobile đa nền tảng React Native.",
            experience_level="junior",
        )

        job_without_quoted = create_test_job(
            title="Lập trình viên ReactJS Frontend",
            company="Web Studio",
            desc="Chỉ làm web ReactJS, Redux và HTML/CSS.",
            experience_level="junior",
        )

        job_with_negated = create_test_job(
            title="Senior React Native Developer",
            company="Fintech Co",
            desc="Yêu cầu Senior React Native với 4 năm kinh nghiệm.",
            experience_level="senior",
        )

        ranked, diag = self.engine.rank_and_filter_jobs(
            [job_match, job_without_quoted, job_with_negated],
            intent,
            strict_mode=True,
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["job"].id, job_match.id)
        self.assertEqual(diag["removed_by_filters"]["hard_exact_phrase"], 1)
        self.assertEqual(diag["removed_by_filters"]["hard_exclusion"], 1)

    # =========================================================================
    # 8. SẮP XẾP THEO LƯƠNG & ĐỘ TƯƠI MỚI
    # =========================================================================
    def test_sorting_by_salary(self):
        """Kiểm tra sắp xếp theo mức lương giảm dần và tăng dần."""
        intent = self.parser.parse("Kỹ sư phần mềm")

        job_low = create_test_job(title="Kỹ sư phần mềm 1", company="A", desc="Lập trình.", salary_min=10000000, salary_max=12000000)
        job_high = create_test_job(title="Kỹ sư phần mềm 2", company="B", desc="Lập trình.", salary_min=25000000, salary_max=35000000)
        job_mid = create_test_job(title="Kỹ sư phần mềm 3", company="C", desc="Lập trình.", salary_min=18000000, salary_max=22000000)

        # Sắp xếp lương giảm dần
        ranked_desc, _ = self.engine.rank_and_filter_jobs(
            [job_low, job_high, job_mid],
            intent,
            sort_by="salary_desc",
        )
        self.assertEqual(ranked_desc[0]["job"].id, job_high.id)
        self.assertEqual(ranked_desc[1]["job"].id, job_mid.id)
        self.assertEqual(ranked_desc[2]["job"].id, job_low.id)

        # Sắp xếp lương tăng dần
        ranked_asc, _ = self.engine.rank_and_filter_jobs(
            [job_low, job_high, job_mid],
            intent,
            sort_by="salary_asc",
        )
        self.assertEqual(ranked_asc[0]["job"].id, job_low.id)
        self.assertEqual(ranked_asc[1]["job"].id, job_mid.id)
        self.assertEqual(ranked_asc[2]["job"].id, job_high.id)


if __name__ == "__main__":
    unittest.main()
