"""
Test Suite for C_Data Cross-Source Deduplication & Consolidation Engine (Prompt Acceptance).
Verifies:
1. Canonical URL tracking parameter removal while preserving essential routing parameters.
2. Cross-source repost deduplication (same job posted across portal, job board, social).
3. Anti-Merge Guard: Same company and title but different jobs/branches are NOT merged.
4. Salary disparity and dissimilar content anti-merge guards.
5. Extended deadline & updated job handling (preserves first_seen_at, updates deadline).
6. High-trust evidence preservation against newer low-trust duplicate copies.
7. Status conflict history tracking when sources disagree.
"""

from datetime import datetime, timedelta, timezone
import unittest

from app.services.job_deduplication_engine import (
    JobDeduplicationEngine,
    canonicalize_url,
    compute_text_similarity,
    job_deduplication_engine,
    normalize_company_name,
    normalize_job_title,
)


class MockJobRecord:
    """Mock job model object for testing deduplication algorithms"""
    def __init__(
        self,
        title: str,
        company_name: str,
        source_url: str,
        apply_url: str = None,
        source_job_id: str = None,
        source_platform: str = "CareerViet",
        salary_min: int = None,
        salary_max: int = None,
        location_province: str = "Quảng Ninh",
        location_district: str = "Hạ Long",
        description: str = "",
        posted_at: datetime = None,
        deadline_at: datetime = None,
        status: str = "active_likely",
        status_evidence: str = None,
        extraction_confidence: float = 0.85,
    ):
        self.title = title
        self.company_name = company_name
        self.source_url = source_url
        self.apply_url = apply_url or source_url
        self.source_job_id = source_job_id
        self.source_platform = source_platform
        self.source_name = source_platform
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.location_province = location_province
        self.location_district = location_district
        self.description = description
        self.posted_at = posted_at or datetime.now(timezone.utc)
        self.first_seen_at = self.posted_at
        self.last_seen_at = self.posted_at
        self.crawled_at = self.posted_at
        self.deadline_at = deadline_at
        self.expires_at = deadline_at
        self.status = status
        self.status_evidence = status_evidence or "Tin công khai"
        self.status_reason = "Thu thập từ nguồn"
        self.extraction_confidence = extraction_confidence


class TestDeduplicationEngine(unittest.TestCase):
    """Bộ kiểm thử cho Hệ thống Khử trùng lặp & Hợp nhất Đa nguồn"""

    def setUp(self):
        self.engine = job_deduplication_engine

    def test_01_canonical_url_tracking_param_sanitization(self):
        """
        Kiểm tra chuẩn hóa URL:
        - Loại bỏ an toàn các tham số tracking (utm_*, fbclid, post_ref, ref...).
        - BẢO TOÀN các query parameters cần thiết để mở đúng bài viết (jobId, id, v...).
        """
        # URL chứa cả UTM tracking và routing parameter jobId
        dirty_url = (
            "https://careerviet.vn/vi/tim-viec-lam/lap-trinh-vien-react.html"
            "?utm_source=facebook&utm_medium=cpc&utm_campaign=spring_2026&fbclid=IwAR123&jobId=998811&ref=fanpage"
        )
        clean = canonicalize_url(dirty_url)

        self.assertNotIn("utm_source", clean)
        self.assertNotIn("fbclid", clean)
        self.assertNotIn("ref=fanpage", clean)
        # Tham số cốt lõi jobId phải được giữ lại
        self.assertIn("jobId=998811", clean)

        # Hai URL có tham số tracking khác nhau nhưng cùng bản tin cốt lõi
        url_copy_1 = "https://careerviet.vn/job/12345?utm_source=email&jobId=12345"
        url_copy_2 = "https://careerviet.vn/job/12345?fbclid=xyz987&jobId=12345"
        self.assertEqual(canonicalize_url(url_copy_1), canonicalize_url(url_copy_2))

    def test_02_cross_source_repost_consolidation(self):
        """
        Kiểm tra bài đăng lại (repost) qua nhiều kênh:
        - Cổng tuyển dụng chính thức của Sun Group.
        - CareerViet.
        - Nhóm Facebook việc làm.
        Gộp thành 1 việc làm, giữ toàn bộ nguồn gốc và ưu tiên apply_url của Sun Group.
        """
        now = datetime.now(timezone.utc)
        job_portal = MockJobRecord(
            title="Kỹ Sư CNTT & Vận Hành Hệ Thống Vé Cáp Treo",
            company_name="Tập đoàn Sun Group (Sun World Ha Long)",
            source_url="https://halongcomplex.sunworld.vn/tuyen-dung/it-ticketing",
            apply_url="https://sungroup.com.vn/careers/apply/it-ticketing",
            source_platform="Sun Group Official Portal",
            salary_min=13000000,
            salary_max=19000000,
            location_province="Quảng Ninh",
            location_district="Hạ Long",
            description="Quản lý hệ thống bán vé điện tử QR Code, RFID và hệ thống mạng cabin cáp treo Nữ Hoàng.",
            posted_at=now - timedelta(days=3),
            status="active_confirmed",
            status_evidence="Xác thực từ Cổng Tuyển Dụng Tập Đoàn Sun Group",
            extraction_confidence=1.0,
        )

        job_social = MockJobRecord(
            title="Tuyển Gấp Kỹ Sư CNTT Vận Hành Cáp Treo Nữ Hoàng",
            company_name="Công viên Sun World Ha Long",
            source_url="https://www.facebook.com/groups/vieclamhalongquangninh/permalink/987654321/",
            apply_url="https://www.facebook.com/groups/vieclamhalongquangninh/",
            source_platform="Facebook Group Việc Làm Hạ Long",
            salary_min=13000000,
            salary_max=19000000,
            location_province="Quảng Ninh",
            location_district="Hạ Long",
            description="Sun World Bãi Cháy cần tuyển kỹ sư CNTT vận hành cổng soát vé thông minh RFID và mạng cáp quang.",
            posted_at=now - timedelta(days=1),
            status="active_likely",
            status_evidence="Bài đăng chia sẻ trên mạng xã hội",
            extraction_confidence=0.75,
        )

        consolidated, dup_count = self.engine.consolidate_jobs([job_portal, job_social])

        self.assertEqual(len(consolidated), 1)
        self.assertEqual(dup_count, 1)

        result_job = consolidated[0]
        # Giữ đầy đủ cả 2 nguồn
        self.assertEqual(len(result_job._consolidated_sources), 2)
        source_names = [s["source_name"] for s in result_job._consolidated_sources]
        self.assertIn("Sun Group Official Portal", source_names)
        self.assertIn("Facebook Group Việc Làm Hạ Long", source_names)

        # URL ứng tuyển tốt nhất phải là cổng chính thức của Sun Group, KHÔNG bị link Facebook đè lên
        self.assertEqual(result_job._best_apply_url, "https://sungroup.com.vn/careers/apply/it-ticketing")
        self.assertEqual(result_job.status_evidence, "Xác thực từ Cổng Tuyển Dụng Tập Đoàn Sun Group")
        self.assertEqual(result_job.extraction_confidence, 1.0)

    def test_03_same_title_different_jobs_not_merged_anti_merge_guard(self):
        """
        Quy tắc bắt buộc (Anti-Merge Guard):
        'Không chỉ dựa vào cùng tiêu đề để gộp vì một công ty có thể đăng nhiều vị trí giống nhau'.
        Cùng một công ty, cùng tiêu đề 'Nhân Viên Lễ Tân' nhưng ở 2 chi nhánh khác nhau
        (Bãi Cháy vs Hòn Gai) với mô tả khác biệt -> KHÔNG ĐƯỢC GỘP!
        """
        now = datetime.now(timezone.utc)
        job_branch_a = MockJobRecord(
            title="Nhân Viên Lễ Tân Khách Sạn (Front Desk)",
            company_name="Khách Sạn Mường Thanh Luxury",
            source_url="https://muongthanh.com/careers/receptionist-baichay",
            location_province="Quảng Ninh",
            location_district="Bãi Cháy",
            description="Đón tiếp du khách lưu trú tại Khách sạn Mường Thanh Luxury Bãi Cháy ven biển.",
            salary_min=8000000,
            salary_max=12000000,
            posted_at=now,
        )

        job_branch_b = MockJobRecord(
            title="Nhân Viên Lễ Tân Khách Sạn (Front Desk)",
            company_name="Khách Sạn Mường Thanh Luxury",
            source_url="https://muongthanh.com/careers/receptionist-hongai",
            location_province="Quảng Ninh",
            location_district="Hòn Gai",
            description="Phục vụ khách đoàn hội nghị và công tác tại Khách sạn Mường Thanh Hòn Gai trung tâm TP.",
            salary_min=8000000,
            salary_max=12000000,
            posted_at=now,
        )

        is_dup, reason, _ = self.engine.are_jobs_duplicate(job_branch_a, job_branch_b)
        self.assertFalse(is_dup, f"Bị gộp sai dù khác chi nhánh/quận huyện! Lý do: {reason}")

        consolidated, dup_count = self.engine.consolidate_jobs([job_branch_a, job_branch_b])
        # Phải giữ nguyên 2 bản ghi độc lập
        self.assertEqual(len(consolidated), 2)
        self.assertEqual(dup_count, 0)

    def test_04_same_title_different_specialties_and_salaries_not_merged(self):
        """
        Anti-Merge Guard: Cùng công ty 'Than Hạ Long - TKV', cùng chức danh 'Kỹ Sư Cơ Điện',
        nhưng một bên là kỹ sư mỏ hầm lò (35tr) và một bên là kỹ sư điện văn phòng (12tr)
        -> Chênh lệch lương lớn và mô tả khác nhau, KHÔNG ĐƯỢC GỘP!
        """
        job_underground = MockJobRecord(
            title="Kỹ Sư Cơ Điện",
            company_name="Công ty Than Hạ Long - TKV",
            source_url="https://vinacomin.vn/jobs/co-dien-ham-lo",
            location_province="Quảng Ninh",
            location_district="Cẩm Phả",
            salary_min=32000000,
            salary_max=45000000,
            description="Chỉ đạo thi công hệ thống điện hầm lò mức -350m, quản lý trạm biến áp phòng nổ dưới lòng đất.",
        )

        job_office = MockJobRecord(
            title="Kỹ Sư Cơ Điện",
            company_name="Công ty Than Hạ Long - TKV",
            source_url="https://vinacomin.vn/jobs/co-dien-van-phong",
            location_province="Quảng Ninh",
            location_district="Cẩm Phả",
            salary_min=11000000,
            salary_max=15000000,
            description="Bảo trì hệ thống máy lạnh, chiếu sáng và máy phát điện dự phòng tại tòa nhà điều hành.",
        )

        is_dup, reason, _ = self.engine.are_jobs_duplicate(job_underground, job_office)
        self.assertFalse(is_dup, f"Bị gộp sai dù chênh lệch lương lớn và công việc khác nhau! Lý do: {reason}")

        consolidated, dup_count = self.engine.consolidate_jobs([job_underground, job_office])
        self.assertEqual(len(consolidated), 2)
        self.assertEqual(dup_count, 0)

    def test_05_updated_or_extended_deadline(self):
        """
        Kiểm tra tin được cập nhật hoặc gia hạn hạn nộp (extended deadline):
        - Bản ghi A có hạn cũ: 20/10/2026.
        - Bản ghi B (đăng cập nhật sau đó) gia hạn hạn nộp: 25/11/2026.
        - Kết quả: Gia hạn deadline_at lên 25/11/2026, cập nhật last_seen_at nhưng bảo toàn first_seen_at.
        """
        time_a = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
        deadline_old = datetime(2026, 10, 20, 17, 0, tzinfo=timezone.utc)

        time_b = datetime(2026, 10, 15, 10, 0, tzinfo=timezone.utc)
        deadline_extended = datetime(2026, 11, 25, 17, 0, tzinfo=timezone.utc)

        job_original = MockJobRecord(
            title="Kỹ Sư An Toàn Môi Trường Mỏ Than",
            company_name="Công Ty CP Than Đèo Nai - Cọc Sáu",
            source_url="https://vinacomin.vn/jobs/ky-su-an-toan-2026",
            posted_at=time_a,
            deadline_at=deadline_old,
            status="active_likely",
        )

        job_extended = MockJobRecord(
            title="Kỹ Sư An Toàn Môi Trường Mỏ Than",
            company_name="Công Ty CP Than Đèo Nai - Cọc Sáu",
            source_url="https://vinacomin.vn/jobs/ky-su-an-toan-2026?update=extended",
            posted_at=time_b,
            deadline_at=deadline_extended,
            status="active_likely",
        )

        consolidated, dup_count = self.engine.consolidate_jobs([job_original, job_extended])

        self.assertEqual(len(consolidated), 1)
        self.assertEqual(dup_count, 1)

        result_job = consolidated[0]
        # Hạn nộp mới được cập nhật gia hạn
        self.assertEqual(result_job.deadline_at, deadline_extended)
        # first_seen_at được giữ nguyên từ bản tin ban đầu
        self.assertEqual(result_job.first_seen_at, time_a)
        # last_seen_at cập nhật theo bản cập nhật mới
        self.assertEqual(result_job.last_seen_at, time_b)

    def test_06_higher_trust_evidence_preserved_against_newer_low_trust_duplicate(self):
        """
        Kiểm tra quy tắc: 'Không để bản sao mới hơn nhưng kém tin cậy ghi đè mất bằng chứng tốt hơn'.
        Một bản sao mới xuất hiện trên Facebook không được hạ cấp bằng chứng xác thực từ cổng Vinpearl.
        """
        now = datetime.now(timezone.utc)
        vinpearl_job = MockJobRecord(
            title="Bác Sĩ Đa Khoa & Phục Hồi Chức Năng Bệnh Viện Vinmec Hạ Long",
            company_name="Bệnh viện Đa khoa Quốc tế Vinmec Hạ Long",
            source_url="https://vinpearl.com/vi/vinmec-halong/tuyen-dung-bac-si",
            apply_url="https://vinpearl.com/vi/careers/apply-doctor",
            source_platform="Vinpearl Official Portal",
            status_evidence="Chứng nhận kiểm định từ Cổng Tuyển Dụng Vingroup",
            extraction_confidence=1.0,
            posted_at=now - timedelta(days=5),
        )

        fb_job_copy = MockJobRecord(
            title="Tuyển Bác Sĩ Đa Khoa Bệnh Viện Vinmec Hạ Long",
            company_name="Vinmec Hạ Long",
            source_url="https://facebook.com/groups/bacsi/post/112233",
            apply_url="https://facebook.com/groups/bacsi",
            source_platform="Facebook Group Y Tế",
            status_evidence="Bài chia sẻ cộng đồng chưa xác minh",
            extraction_confidence=0.6,
            posted_at=now,  # Mới hơn
        )

        consolidated, _ = self.engine.consolidate_jobs([vinpearl_job, fb_job_copy])
        res = consolidated[0]

        # Bằng chứng của cổng chính thức được bảo toàn
        self.assertEqual(res.status_evidence, "Chứng nhận kiểm định từ Cổng Tuyển Dụng Vingroup")
        self.assertEqual(res.extraction_confidence, 1.0)
        self.assertEqual(res._best_apply_url, "https://vinpearl.com/vi/careers/apply-doctor")

    def test_07_status_conflict_history_recorded(self):
        """
        Kiểm tra ghi vết xung đột trạng thái (Status Conflict):
        Một nguồn báo active, một nguồn báo closed -> ghi nhận lịch sử và chuyển trạng thái closed.
        """
        now = datetime.now(timezone.utc)
        job_active = MockJobRecord(
            title="Nhân Viên Chăm Sóc Khách Hàng VIP Yoko Onsen Quang Hanh",
            company_name="Khu Nghỉ Dưỡng Khoáng Nóng Yoko Onsen",
            source_url="https://yokoonsenquanghanh.com.vn/careers/cs-vip",
            source_platform="Aggregator",
            status="active_likely",
            posted_at=now - timedelta(days=2),
        )

        job_closed = MockJobRecord(
            title="Nhân Viên Chăm Sóc Khách Hàng VIP Yoko Onsen Quang Hanh",
            company_name="Khu Nghỉ Dưỡng Khoáng Nóng Yoko Onsen",
            source_url="https://yokoonsenquanghanh.com.vn/careers/cs-vip",
            source_platform="Sun Group Official Portal",
            status="closed",
            status_evidence="Thông báo chính thức: Đã tuyển đủ chỉ tiêu",
            posted_at=now,
        )

        consolidated, _ = self.engine.consolidate_jobs([job_active, job_closed])
        res = consolidated[0]

        # Trạng thái giải quyết theo nguồn chính thức đã đóng
        self.assertEqual(res.status, "closed")
        # Lịch sử xung đột được ghi vết
        self.assertTrue(hasattr(res, "_status_conflict_history"))
        self.assertEqual(len(res._status_conflict_history), 1)
        conflict = res._status_conflict_history[0]
        self.assertEqual(conflict["primary_status"], "active_likely")
        self.assertEqual(conflict["secondary_status"], "closed")


if __name__ == "__main__":
    unittest.main()
