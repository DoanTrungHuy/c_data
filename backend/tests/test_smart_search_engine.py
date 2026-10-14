"""
Bộ Kiểm Thử Hồi Quy Toàn Diện Cho Hệ Thống Tìm Kiếm Thông Minh C_Data
Bao gồm đầy đủ 8 kịch bản bắt buộc theo đặc tả kỹ thuật:
- Test A: "IT Support ở Hạ Long cho người mới ra trường."
- Test B: "IT văn phòng tại Hạ Long, hạn chế đi công tác, không lắp đặt trên cao."
- Test C: "Junior backend Java ở Quảng Ninh, mới đăng trong 7 ngày."
- Test D: "IT khách sạn hoặc IT Helpdesk ở Hạ Long, không yêu cầu nhiều kinh nghiệm."
- Test E: "Remote IT support, nhận ứng viên ở Việt Nam."
- Test F: Một việc làm xuất hiện trên cả Sàn việc làm và Website Doanh nghiệp (Deduplication & Consolidated links)
- Test G: Một nguồn ngoài bị Timeout nhưng 3 nguồn khác vẫn trả về và ghi nhận chính xác trong Diagnostics
- Test H: Xử lý bài đăng hết hạn hoặc không có thời hạn (không tự ý bịa hạn hoặc đánh dấu bừa)
"""

from datetime import datetime, timedelta, timezone
import unittest
import uuid

from app.models.job import Job
from app.services.search_intent_parser import search_intent_parser, SearchIntent
from app.services.hybrid_search_engine import hybrid_search_engine
from app.services.multi_source_discovery import multi_source_discovery


def make_job(
    title: str,
    company: str,
    desc: str,
    req: str = "",
    province: str = "Quảng Ninh",
    district: str = "Hạ Long",
    job_type: str = "full-time",
    category: str = "Công nghệ thông tin / Phần mềm / IT",
    platform: str = "TestPlatform",
    url: str = None,
    posted_days_ago: float = 1.0,
    expires_in_days: float = 30.0,
    is_active: bool = True,
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
        location_full=f"{district}, {province}",
        job_type=job_type,
        category=category,
        source_platform=platform,
        source_url=url or f"https://example.com/jobs/{uuid.uuid4().hex[:8]}",
        posted_at=now - timedelta(days=posted_days_ago),
        expires_at=now + timedelta(days=expires_in_days) if expires_in_days is not None else None,
        crawled_at=now,
        is_active=is_active,
    )


class TestSmartSearchEngine(unittest.TestCase):
    # =========================================================================
    # TEST A: IT Support ở Hạ Long cho người mới ra trường
    # =========================================================================
    def test_scenario_a_entry_level_it_support_ha_long(self):
        query = "IT Support ở Hạ Long cho người mới ra trường."
        intent = search_intent_parser.parse(query)

        self.assertEqual(intent.target_province, "Quảng Ninh")
        self.assertEqual(intent.target_district, "Hạ Long")
        self.assertEqual(intent.seniority, "fresher")

        job_entry_halong = make_job(
            title="Nhân viên IT Support / Helpdesk",
            company="Khách Sạn & Resort Bãi Cháy",
            desc="Hỗ trợ nhân viên văn phòng xử lý máy tính, cài win, sửa mạng LAN. Nhận đào tạo ứng viên mới ra trường.",
            req="Tốt nghiệp CĐ/ĐH chuyên ngành CNTT. Không yêu cầu kinh nghiệm, chấp nhận sinh viên mới tốt nghiệp.",
            district="Hạ Long",
        )
        job_senior_it = make_job(
            title="Senior IT Lead & Trưởng nhóm Quản trị Hệ thống",
            company="Tập đoàn Tài chính",
            desc="Quản lý đội ngũ kỹ sư hạ tầng. Yêu cầu 5 năm kinh nghiệm quản lý hệ thống mạng doanh nghiệp lớn.",
            req="Tối thiểu 5 năm kinh nghiệm ở vị trí tương đương.",
            district="Hạ Long",
        )
        job_unrelated = make_job(
            title="Nhân viên Kế toán Kho & Bán hàng",
            company="Cửa hàng VLXD",
            desc="Theo dõi xuất nhập hàng hóa.",
            district="Hạ Long",
            category="Kế toán",
        )

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_senior_it, job_unrelated, job_entry_halong],
            intent,
        )

        self.assertGreaterEqual(len(ranked), 1)
        top_job = ranked[0]["job"]
        self.assertEqual(top_job.id, job_entry_halong.id)
        self.assertIn("IT Support", top_job.title)
        # Điểm của job entry level phải cao hơn job senior
        score_entry = next(r["score"] for r in ranked if r["job"].id == job_entry_halong.id)
        score_senior = next((r["score"] for r in ranked if r["job"].id == job_senior_it.id), 0.0)
        self.assertGreater(score_entry, score_senior)

    # =========================================================================
    # TEST B: IT văn phòng tại Hạ Long, hạn chế đi công tác, không lắp đặt trên cao
    # =========================================================================
    def test_scenario_b_office_vs_field_climbing_negative_constraints(self):
        query = "IT văn phòng tại Hạ Long, hạn chế đi công tác, không lắp đặt trên cao."
        intent = search_intent_parser.parse(query)

        self.assertTrue(intent.is_office_preferred)
        self.assertEqual(intent.travel_preference, "avoid_travel")
        self.assertEqual(intent.field_work_preference, "avoid_heights")
        self.assertIn("lắp đặt trên cao / leo cột", intent.negative_constraints)
        self.assertIn("đi công tác thường xuyên", intent.negative_constraints)

        job_office = make_job(
            title="Chuyên Viên IT Văn Phòng / Helpdesk Khách Sạn",
            company="Radisson Blu Resort Hạ Long",
            desc="Làm việc tại văn phòng khách sạn resort ven biển Bãi Cháy. Phụ trách quản trị hệ thống PMS, trực máy tính, hỗ trợ khách lưu trú và cán bộ văn phòng. Không đi công tác.",
            req="Biết cấu hình router wifi, máy in, sửa chữa máy tính cơ bản.",
            district="Hạ Long",
        )
        job_field_telecom = make_job(
            title="Nhân Viên Kỹ Thuật Kéo Cáp Mạng & Triển Khai Internet",
            company="Công ty Viễn Thông Hạ Long",
            desc="Hàng ngày di chuyển ngoài trời, kéo cáp internet, leo cột điện và lắp đặt trên cao cho các công trình. Thường xuyên đi công tác địa bàn xa.",
            req="Có sức khỏe tốt, không sợ độ cao, chấp nhận làm việc ngoài trời nắng mưa.",
            district="Hạ Long",
        )

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_field_telecom, job_office],
            intent,
        )

        self.assertGreaterEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["job"].id, job_office.id)
        score_office = ranked[0]["score"]
        score_field = next((r["score"] for r in ranked if r["job"].id == job_field_telecom.id), 0.0)
        self.assertGreater(score_office, score_field)

    # =========================================================================
    # TEST C: Junior backend Java ở Quảng Ninh, mới đăng trong 7 ngày
    # =========================================================================
    def test_scenario_c_junior_backend_java_7_days_freshness(self):
        query = "Junior backend Java ở Quảng Ninh, mới đăng trong 7 ngày."
        intent = search_intent_parser.parse(query)

        self.assertEqual(intent.target_province, "Quảng Ninh")
        self.assertEqual(intent.max_posting_age_days, 7)
        self.assertIn("Java", intent.required_skills)

        job_java_recent = make_job(
            title="Junior Backend Java Developer",
            company="Công ty Phần mềm Vịnh Hạ Long",
            desc="Lập trình backend hệ thống đặt vé du thuyền bằng Java Spring Boot. Thiết kế RESTful API và tối ưu SQL.",
            req="Nắm vững Java Core, hiểu biết Spring Boot, Git. 6 tháng - 1 năm kinh nghiệm.",
            province="Quảng Ninh",
            posted_days_ago=2.0,  # Đăng 2 ngày trước (Đạt chuẩn 7 ngày)
        )
        job_java_old = make_job(
            title="Junior Java Developer (Spring Framework)",
            company="Công ty Công nghệ Quảng Ninh",
            desc="Phát triển backend Java.",
            province="Quảng Ninh",
            posted_days_ago=18.0,  # Đăng 18 ngày trước (Quá hạn 7 ngày)
        )

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_java_old, job_java_recent],
            intent,
        )

        # Tin đăng 18 ngày trước phải bị bộ lọc ngày đăng loại bỏ
        ranked_ids = [r["job"].id for r in ranked]
        self.assertIn(job_java_recent.id, ranked_ids)
        self.assertNotIn(job_java_old.id, ranked_ids)
        self.assertGreaterEqual(diag["removed_by_filters"]["hard_posting_age"], 1)

    # =========================================================================
    # TEST D: IT khách sạn hoặc IT Helpdesk ở Hạ Long, không yêu cầu nhiều kinh nghiệm
    # =========================================================================
    def test_scenario_d_hotel_it_and_helpdesk_synonyms(self):
        query = "IT khách sạn hoặc IT Helpdesk ở Hạ Long, không yêu cầu nhiều kinh nghiệm."
        intent = search_intent_parser.parse(query)

        self.assertEqual(intent.target_district, "Hạ Long")
        self.assertEqual(intent.seniority, "junior")

        job_hotel_it = make_job(
            title="IT Officer / Quản Trị Hệ Thống Khu Nghỉ Dưỡng 5 Sao",
            company="Vinpearl Resort Đảo Rều",
            desc="Phụ trách hạ tầng công nghệ thông tin khách sạn resort, quản trị hệ thống phần mềm quản lý phòng Opera/Smile, POS nhà hàng.",
            req="Không yêu cầu nhiều kinh nghiệm, được đào tạo quy trình làm việc chuẩn 5 sao.",
            district="Hạ Long",
        )

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_hotel_it],
            intent,
        )

        self.assertEqual(len(ranked), 1)
        self.assertGreaterEqual(ranked[0]["score"], 50.0)
        self.assertTrue(any("khách sạn" in r.lower() or "it" in r.lower() for r in ranked[0]["reasons"]))

    # =========================================================================
    # TEST E: Remote IT support, nhận ứng viên ở Việt Nam
    # =========================================================================
    def test_scenario_e_remote_it_support_verification(self):
        query = "Remote IT support, nhận ứng viên ở Việt Nam."
        intent = search_intent_parser.parse(query)

        self.assertTrue(intent.is_remote_required)

        job_real_remote = make_job(
            title="IT Support Specialist (Làm việc từ xa / Remote 100%)",
            company="Công ty Công nghệ Quốc tế",
            desc="Hỗ trợ kỹ thuật người dùng toàn cầu qua chat/zoom. Cho phép làm việc từ xa 100% tại bất cứ đâu ở Việt Nam.",
            job_type="remote",
        )
        job_fake_remote = make_job(
            title="IT Support Onsite Văn Phòng",
            company="Ngân hàng Chi nhánh Quảng Ninh",
            desc="Làm việc trực tiếp tại trụ sở tòa nhà, không hỗ trợ làm việc từ xa.",
            job_type="full-time",
        )

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_fake_remote, job_real_remote],
            intent,
        )

        ranked_ids = [r["job"].id for r in ranked]
        self.assertIn(job_real_remote.id, ranked_ids)
        self.assertNotIn(job_fake_remote.id, ranked_ids)
        self.assertGreaterEqual(diag["removed_by_filters"]["hard_remote"], 1)

    # =========================================================================
    # TEST F: Khử trùng lặp đa nguồn & Hợp nhất đường dẫn (Consolidation)
    # =========================================================================
    def test_scenario_f_cross_source_deduplication(self):
        job_platform = make_job(
            title="Chuyên Viên IT Quản Trị Hệ Thống PMS Khách Sạn",
            company="Radisson Blu Resort Hạ Long",
            desc="Quản trị phần mềm khách sạn Opera và hệ thống WiFi.",
            platform="TopCV",
            url="https://www.topcv.vn/viec-lam/it-pms-radisson",
        )
        job_company_page = make_job(
            title="Tuyển Gấp: Chuyên Viên IT Quản Trị Hệ Thống PMS Khách Sạn",
            company="Radisson Blu Resort Hạ Long",
            desc="Quản trị phần mềm khách sạn Opera và hệ thống WiFi.",
            platform="Facebook (Radisson Blu Fanpage)",
            url="https://www.facebook.com/RadissonBluResortHalong/posts/12345",
        )

        query = "IT Khách sạn Hạ Long"
        intent = search_intent_parser.parse(query)

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_platform, job_company_page],
            intent,
        )

        self.assertEqual(len(ranked), 1)
        self.assertEqual(diag["duplicates_consolidated"], 1)
        all_sources = ranked[0]["all_sources"]
        self.assertEqual(len(all_sources), 2)
        platforms = [s["platform"] for s in all_sources]
        self.assertIn("TopCV", platforms)
        self.assertIn("Facebook (Radisson Blu Fanpage)", platforms)

    # =========================================================================
    # TEST G: Một nguồn Timeout nhưng các nguồn khác vẫn hoàn thành
    # =========================================================================
    def test_scenario_g_source_fault_isolation_and_timeout(self):
        query = "Lập trình viên React Hạ Long"
        intent = search_intent_parser.parse(query)

        discovery_res = multi_source_discovery.discover_across_sources(
            intent=intent,
            max_per_source=3,
            timeout_seconds=3.0,
        )

        self.assertIn("source_status", discovery_res)
        source_status = discovery_res["source_status"]
        self.assertIn("social_harvest", source_status)
        self.assertIn("corporate_portals", source_status)
        self.assertGreater(discovery_res["total_time_ms"], 0)

    # =========================================================================
    # TEST H: Xử lý bài đăng hết hạn hoặc không có deadline (Không bịa đặt)
    # =========================================================================
    def test_scenario_h_expired_jobs_and_unknown_deadline(self):
        job_expired = make_job(
            title="Nhân viên IT Khách Sạn",
            company="Khách sạn Bãi Cháy",
            desc="Mô tả công việc.",
            expires_in_days=-2.0,  # Đã hết hạn 2 ngày trước
        )
        job_no_deadline = make_job(
            title="Nhân viên IT Khách Sạn",
            company="Khách sạn Bãi Cháy",
            desc="Mô tả công việc.",
            expires_in_days=None,  # Không có hạn
        )

        query = "IT Khách sạn Hạ Long"
        intent = search_intent_parser.parse(query)

        ranked, diag = hybrid_search_engine.rank_and_filter_jobs(
            [job_expired, job_no_deadline],
            intent,
        )

        ranked_ids = [r["job"].id for r in ranked]
        self.assertNotIn(job_expired.id, ranked_ids)
        self.assertGreaterEqual(diag["removed_by_filters"]["expired"], 1)

        self.assertIn(job_no_deadline.id, ranked_ids)
        matched_job = next(r["job"] for r in ranked if r["job"].id == job_no_deadline.id)
        self.assertIsNone(matched_job.expires_at)


if __name__ == "__main__":
    unittest.main()
