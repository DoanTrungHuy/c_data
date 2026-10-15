"""
Bộ kiểm thử chuyên sâu cho Hệ thống Xếp hạng Đa Tín hiệu (Multi-Signal Ranking Engine)
Tuân thủ đầy đủ Definition of Done (DoD) của Yêu cầu Ranking Đa Tín Hiệu:

1. Thỏa mãn 7 tín hiệu chuẩn hóa:
   - Tín hiệu 1: Semantic Relevance (Chức danh, kỹ năng, mô tả: 0 - 40 điểm)
   - Tín hiệu 2: Source Authority Tier (Độ tin cậy của nguồn: 0 - 15 điểm)
   - Tín hiệu 3: Verification Status (Xác minh còn tuyển: 0 - 15 điểm)
   - Tín hiệu 4: Posting Freshness (Độ mới bài đăng gốc posted_at: 0 - 10 điểm)
   - Tín hiệu 5: Data Completeness & Apply URL (Độ đầy đủ dữ liệu: 0 - 10 điểm)
   - Tín hiệu 6: Location & Workplace Fit (Địa điểm & hình thức: 0 - 10 điểm)
   - Tín hiệu 7: Gate 0 Hard Constraints (Không thỏa mãn thì bị loại bỏ hoàn toàn)

2. Nguyên tắc bất di bất dịch:
   - Source Volume Neutrality: Không tăng điểm chỉ vì nguồn cào được nhiều dữ liệu.
   - Anti-Crawled Freshness Cheat: Đánh giá độ mới bằng posted_at, cấm dùng crawled_at để gian lận.
   - Salary Neutrality: Không phạt tin chưa có lương khi người dùng không yêu cầu lương.
   - Pairwise Ranking Debug: Cung cấp giải thích chi tiết vì sao Job A xếp trên Job B.
   - Benchmark Comparative Evaluation: Đánh giá so sánh định lượng NDCG@5 và Top-1 Accuracy
     giữa Multi-Signal Ranking Engine và Baseline Keyword-Only Ranker.
"""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, Dict, List
import unittest
import uuid

from app.models.job import Job
from app.services.ranking_engine import (
    MultiSignalRankingEngine,
    multi_signal_ranking_engine,
    SOURCE_TRUST_MAP,
)
from app.services.search_intent_parser import search_intent_parser
from app.services.hybrid_search_engine import hybrid_search_engine


def make_test_job(
    title: str,
    company: str,
    desc: str,
    req: str = "",
    province: str = "Quảng Ninh",
    district: str = "Hạ Long",
    source_platform: str = "enterprise_direct",
    source_url: str = "https://tuyendung.sungroup.com.vn/job/123",
    apply_url: str = "https://tuyendung.sungroup.com.vn/apply/123",
    status: str = "active_confirmed",
    workplace_type: str = "onsite",
    experience_level: str = "junior",
    salary_min: int = None,
    salary_max: int = None,
    posted_days_ago: float = 1.0,
    crawled_minutes_ago: float = 10.0,
    skills: list = None,
) -> Job:
    now = datetime.now(timezone.utc)
    posted_at = (now - timedelta(days=posted_days_ago)) if posted_days_ago is not None else None
    crawled_at = now - timedelta(minutes=crawled_minutes_ago)
    return Job(
        id=str(uuid.uuid4()),
        title=title,
        company_name=company,
        description=desc,
        requirements=req,
        location_province=province,
        location_district=district,
        location_full=f"{district}, {province}" if district and province else (province or ""),
        locations=[{"province": province, "district": district, "address": f"{district}, {province}", "is_primary": True}],
        source_platform=source_platform,
        source_url=source_url,
        apply_url=apply_url,
        status=status,
        workplace_type=workplace_type,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency="VND",
        posted_at=posted_at,
        crawled_at=crawled_at,
        first_seen_at=posted_at or crawled_at,
        last_seen_at=crawled_at,
        last_verified_at=crawled_at,
        required_skills=skills or [],
        status_evidence={"code": 200, "apply_button_found": True},
    )


class TestMultiSignalRankingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = multi_signal_ranking_engine
        self.now = datetime.now(timezone.utc)

    def test_01_seven_signals_scoring_breakdown(self):
        """
        Kiểm tra 7 tín hiệu chuẩn hóa được tính điểm đầy đủ, minh bạch và có giải thích.
        """
        job = make_test_job(
            title="Kỹ sư Lập trình Python Backend FastAPI",
            company="Tập đoàn Sun Group Hạ Long",
            desc="Phát triển hệ thống backend du lịch với Python, FastAPI, Docker, PostgreSQL tại Bãi Cháy",
            req="Tối thiểu 1 năm kinh nghiệm Python, thành thạo FastAPI và SQL",
            province="Quảng Ninh",
            district="Hạ Long",
            source_platform="sun_group",
            status="active_confirmed",
            posted_days_ago=2.0,
            skills=["Python", "FastAPI", "PostgreSQL"],
            salary_min=15000000,
            salary_max=25000000,
        )

        intent = search_intent_parser.parse_query("kỹ sư python fastapi hạ long", province="Quảng Ninh")
        breakdown = self.engine.score_job(job, intent, self.now)

        self.assertGreater(breakdown.total_score, 75.0)
        self.assertLessEqual(breakdown.total_score, 100.0)

        # Kiểm tra từng tín hiệu con
        signals = breakdown.signals
        self.assertIn("semantic_relevance", signals)
        self.assertGreater(signals["semantic_relevance"]["score"], 25.0)  # Max 40
        self.assertEqual(signals["source_trust"]["score"], 15.0)         # Sun Group = Tier 1 (15đ)
        self.assertEqual(signals["verification_status"]["score"], 15.0)   # active_confirmed = 15đ
        self.assertGreaterEqual(signals["posting_freshness"]["score"], 8.0)    # Đăng 2 ngày trước = 8.0đ
        self.assertGreater(signals["data_completeness"]["score"], 7.0)    # Có apply_url + skills + req
        self.assertGreater(signals["location_workplace"]["score"], 7.0)   # Khớp Hạ Long
        self.assertGreater(len(breakdown.reasons), 3)

    def test_02_source_authority_tier_neutral_to_volume(self):
        """
        Kiểm tra Source Authority:
        - Enterprise Direct (Tier 1: 15đ) > Major Job Board (Tier 2: 12đ) > Community Social (Tier 4: 4đ).
        - Tuyệt đối không có điểm cộng vì cào được nhiều dữ liệu (Volume Neutrality).
        """
        intent = search_intent_parser.parse_query("nhân viên buồng phòng bãi cháy")

        job_enterprise = make_test_job(
            title="Nhân viên Buồng phòng Khách sạn",
            company="Vinpearl Hạ Long Resort",
            desc="Dọn dẹp phòng khách tiêu chuẩn 5 sao tại Bãi Cháy",
            source_platform="vinpearl",
            posted_days_ago=5.0,
        )

        job_social = make_test_job(
            title="Nhân viên Buồng phòng Khách sạn",
            company="Vinpearl Hạ Long Resort",
            desc="Dọn dẹp phòng khách tiêu chuẩn 5 sao tại Bãi Cháy",
            source_platform="facebook_community",
            posted_days_ago=5.0,
        )

        score_ent = self.engine.score_job(job_enterprise, intent, self.now)
        score_soc = self.engine.score_job(job_social, intent, self.now)

        self.assertEqual(score_ent.signals["source_trust"]["score"], 15.0)
        self.assertEqual(score_soc.signals["source_trust"]["score"], 4.0)
        self.assertGreater(score_ent.total_score, score_soc.total_score)
        self.assertIn("volume_boost", score_ent.signals["source_trust"]["details"])
        self.assertEqual(score_ent.signals["source_trust"]["details"]["volume_boost"], 0.0)

    def test_03_freshness_anti_cheat_posted_at_vs_crawled_at(self):
        """
        Kiểm tra phòng chống gian lận độ tươi mới:
        - Job A đăng cách đây 1 ngày, cào 10 phút trước -> điểm tươi mới cao (10.0đ).
        - Job B đăng cách đây 45 ngày, cào 5 phút trước -> điểm tươi mới thấp (0.0đ vì >30 ngày).
        - Job C không có posted_at, chỉ có crawled_at -> 0đ tươi mới (anti-cheat).
        """
        intent = search_intent_parser.parse_query("kế toán bãi cháy")

        job_fresh = make_test_job(
            title="Kế toán tổng hợp", company="Công ty A", desc="Kế toán tổng hợp tại Bãi Cháy",
            posted_days_ago=1.0, crawled_minutes_ago=10.0,
        )
        job_stale_recrawled = make_test_job(
            title="Kế toán tổng hợp", company="Công ty A", desc="Kế toán tổng hợp tại Bãi Cháy",
            posted_days_ago=45.0, crawled_minutes_ago=5.0,
        )
        job_no_posted_at = make_test_job(
            title="Kế toán tổng hợp", company="Công ty A", desc="Kế toán tổng hợp tại Bãi Cháy",
            posted_days_ago=None, crawled_minutes_ago=5.0,
        )

        score_fresh = self.engine.score_job(job_fresh, intent, self.now)
        score_stale = self.engine.score_job(job_stale_recrawled, intent, self.now)
        score_no_posted = self.engine.score_job(job_no_posted_at, intent, self.now)

        fresh_val = score_fresh.signals["posting_freshness"]["score"]
        stale_val = score_stale.signals["posting_freshness"]["score"]
        no_posted_val = score_no_posted.signals["posting_freshness"]["score"]

        self.assertGreaterEqual(fresh_val, 8.0)
        self.assertLess(stale_val, 4.0)
        self.assertEqual(no_posted_val, 0.0)
        self.assertIn("posted_at", score_no_posted.signals["posting_freshness"]["details"]["freshness_reason"])
        self.assertGreater(score_fresh.total_score, score_stale.total_score)

    def test_04_verification_status_and_evidence(self):
        """
        Kiểm tra trạng thái xác minh:
        - active_confirmed (15đ) > active_likely (10đ) > unknown (3đ) > expired (-30đ phạt).
        """
        intent = search_intent_parser.parse_query("kỹ sư cơ điện mỏ cẩm phả")

        job_confirmed = make_test_job(
            title="Kỹ sư Cơ điện Hầm lò TKV", company="Tập đoàn Than Khoáng sản",
            desc="Vận hành hệ thống cơ điện mỏ", status="active_confirmed",
        )
        job_likely = make_test_job(
            title="Kỹ sư Cơ điện Hầm lò TKV", company="Tập đoàn Than Khoáng sản",
            desc="Vận hành hệ thống cơ điện mỏ", status="active_likely",
        )
        job_unknown = make_test_job(
            title="Kỹ sư Cơ điện Hầm lò TKV", company="Tập đoàn Than Khoáng sản",
            desc="Vận hành hệ thống cơ điện mỏ", status="unknown",
        )
        job_expired = make_test_job(
            title="Kỹ sư Cơ điện Hầm lò TKV", company="Tập đoàn Than Khoáng sản",
            desc="Vận hành hệ thống cơ điện mỏ", status="expired",
        )

        sc_confirmed = self.engine.score_job(job_confirmed, intent, self.now)
        sc_likely = self.engine.score_job(job_likely, intent, self.now)
        sc_unknown = self.engine.score_job(job_unknown, intent, self.now)
        sc_expired = self.engine.score_job(job_expired, intent, self.now)

        self.assertEqual(sc_confirmed.signals["verification_status"]["score"], 15.0)
        self.assertEqual(sc_likely.signals["verification_status"]["score"], 10.0)
        self.assertEqual(sc_unknown.signals["verification_status"]["score"], 3.0)
        self.assertEqual(sc_expired.signals["verification_status"]["score"], 0.0)
        self.assertLessEqual(sc_expired.penalties, -20.0)  # Phạt nặng tin expired (-30đ)

        self.assertGreater(sc_confirmed.total_score, sc_likely.total_score)
        self.assertGreater(sc_likely.total_score, sc_unknown.total_score)
        self.assertGreater(sc_unknown.total_score, sc_expired.total_score)

    def test_05_salary_neutrality_when_unspecified(self):
        """
        Kiểm tra Salary Neutrality:
        - Khi người dùng KHÔNG yêu cầu lương:
          + Tin không có lương (Thỏa thuận) KHÔNG bị phạt điểm.
          + Tin có lương không được bonus quá đà làm lấn át tin tốt hơn.
        - Khi người dùng CÓ yêu cầu lương:
          + Tin đạt chuẩn được bonus, tin thấp hơn bị phạt.
        """
        # User KHÔNG yêu cầu lương
        intent_no_salary = search_intent_parser.parse_query("hướng dẫn viên du lịch hạ long")

        job_with_salary = make_test_job(
            title="Hướng dẫn viên Du lịch Hạ Long", company="Du lịch Quảng Ninh",
            desc="Dẫn đoàn khách vịnh Hạ Long", salary_min=10000000, salary_max=15000000,
        )
        job_no_salary = make_test_job(
            title="Hướng dẫn viên Du lịch Hạ Long", company="Du lịch Quảng Ninh",
            desc="Dẫn đoàn khách vịnh Hạ Long", salary_min=None, salary_max=None,
        )

        sc_sal = self.engine.score_job(job_with_salary, intent_no_salary, self.now)
        sc_no_sal = self.engine.score_job(job_no_salary, intent_no_salary, self.now)

        # Tin không lương phải ở trạng thái trung lập: penalty = 0
        self.assertEqual(sc_no_sal.penalties, 0.0)
        self.assertIn("neutral", sc_no_sal.signals["data_completeness"]["details"]["salary_evaluation"])
        # Chênh lệch điểm chỉ nằm ở độ đầy đủ thông tin (max 1.5 điểm), không làm sụp đổ xếp hạng
        diff = abs(sc_sal.total_score - sc_no_sal.total_score)
        self.assertLessEqual(diff, 2.0)

        # User CÓ yêu cầu lương >= 20 triệu
        intent_with_salary = search_intent_parser.parse_query("hướng dẫn viên du lịch lương từ 20 triệu")
        sc_sal_req = self.engine.score_job(job_with_salary, intent_with_salary, self.now)
        self.assertLessEqual(sc_sal_req.penalties, -5.0)  # Lương max 15tr bị phạt (-10đ) vì dưới yêu cầu 20tr

    def test_06_pairwise_ranking_debug_and_explanation(self):
        """
        Kiểm tra cơ chế so sánh Pairwise Debug giải thích tại sao Job A xếp trên Job B.
        """
        intent = search_intent_parser.parse_query("kỹ sư mỏ than cẩm phả")

        job_a = make_test_job(
            title="Kỹ sư Khai thác Mỏ Hầm lò",
            company="Tập đoàn Công nghiệp Than - Khoáng sản Việt Nam (TKV)",
            desc="Quản lý kỹ thuật và an toàn mỏ than tại Cẩm Phả",
            source_platform="tkv_mining",
            status="active_confirmed",
            posted_days_ago=2.0,
        )

        job_b = make_test_job(
            title="Tuyển gấp thợ kỹ thuật mỏ",
            company="Đội thầu tự do",
            desc="Cần thợ làm than tại Cẩm Phả",
            source_platform="facebook_community",
            status="unknown",
            posted_days_ago=20.0,
        )

        comparison = self.engine.compare_ranking(job_a, job_b, intent)

        self.assertEqual(comparison["winner"], "job_a")
        self.assertGreater(comparison["point_difference"], 20.0)
        self.assertIn("summary_explanation", comparison)
        self.assertIn("signal_comparison", comparison)

        # Kiểm tra chi tiết so sánh từng tín hiệu
        signals_map = {item["signal"]: item for item in comparison["signal_comparison"]}
        self.assertEqual(signals_map["source_trust"]["favor"], "job_a")
        self.assertEqual(signals_map["verification_status"]["favor"], "job_a")
        self.assertEqual(signals_map["posting_freshness"]["favor"], "job_a")

    def test_07_comparative_benchmark_evaluation(self):
        """
        BENCHMARK SO SÁNH ĐỊNH LƯỢNG (Quantitative Evaluation):
        So sánh Multi-Signal Ranking Engine với Baseline Keyword-Only Ranker trên 5 kịch bản thực tế:
        1. Query IT/CNTT: Tìm kiếm kỹ sư Python tại Hạ Long.
        2. Query Khai khoáng: Kỹ sư mỏ than TKV tại Cẩm Phả.
        3. Query Du lịch/Khách sạn: Nhân viên lễ tân resort Bãi Cháy.
        4. Query Yêu cầu Fresh: Việc làm mới đăng trong tuần.
        5. Query Spam Suppression: Tin MXH spam từ khóa so với tin chính thống doanh nghiệp.

        Chỉ số đo lường:
        - NDCG@5 (Normalized Discounted Cumulative Gain tại top 5)
        - Top-1 Precision / Relevancy Accuracy
        """
        scenarios = [
            # Scenario 1: IT
            {
                "query": "kỹ sư python backend hạ long",
                "province": "Quảng Ninh",
                "jobs": [
                    make_test_job(
                        "Kỹ sư Lập trình Python Backend", "Tập đoàn Sun Group Hạ Long",
                        desc="Phát triển hệ thống backend dịch vụ du lịch tại Bãi Cháy Hạ Long",
                        req="Thành thạo Python, FastAPI, Docker, SQL",
                        province="Quảng Ninh", district="Hạ Long",
                        skills=["Python", "FastAPI"], source_platform="sun_group",
                        status="active_confirmed", posted_days_ago=1,
                    ), # ground_truth: 3 (Very High: Direct Sun Group portal, Onsite Hạ Long, Fresh)
                    make_test_job(
                        "Python Developer Remote Toàn quốc", "Global Tech Corp",
                        desc="Tuyển lập trình viên Python làm việc từ xa toàn quốc",
                        req="Python, Django",
                        province="Toàn quốc", district="", workplace_type="remote",
                        skills=["Python"], source_platform="major_job_board",
                        status="active_confirmed", posted_days_ago=3,
                    ), # ground_truth: 2 (High: Remote match)
                    make_test_job(
                        "Thực tập sinh Python", "Công ty Startup Hà Nội",
                        desc="Thực tập sinh lập trình tại Ba Đình Hà Nội",
                        province="Hà Nội", district="Ba Đình", workplace_type="onsite",
                        skills=["Python"], source_platform="facebook_community",
                        status="unknown", posted_days_ago=15,
                    ), # ground_truth: 0 (Irrelevant location/level)
                    make_test_job(
                        "Tuyển gấp dev python kiếm 50tr/tháng làm nhiệm vụ", "Ẩn danh",
                        desc="Làm nhiệm vụ cọc tiền nạp rút",
                        province="Quảng Ninh", district="Hạ Long",
                        source_platform="facebook_community", status="unknown", posted_days_ago=0.1,
                    ), # ground_truth: 0 (Spam/Unverified)
                ],
                "ground_truth_relevance": [3, 2, 0, 0],
            },
            # Scenario 2: Mining
            {
                "query": "kỹ sư mỏ than cẩm phả tkv",
                "province": "Quảng Ninh",
                "jobs": [
                    make_test_job("Kỹ sư Khai thác Hầm lò", "TKV - Than Cọc Sáu", "Cẩm Phả", source_platform="tkv_mining", status="active_confirmed", posted_days_ago=2),          # ground_truth: 3
                    make_test_job("Kỹ sư Tuyển khoáng Than", "Tập đoàn Than Khoáng Sản", "Cẩm Phả", source_platform="major_job_board", status="active_likely", posted_days_ago=5), # ground_truth: 2
                    make_test_job("Bán than củi nướng than hoa", "Hộ kinh doanh", "Cẩm Phả", source_platform="facebook_community", status="unknown", posted_days_ago=1),           # ground_truth: 0 (Keyword spam 'than')
                ],
                "ground_truth_relevance": [3, 2, 0],
            },
            # Scenario 3: Hospitality
            {
                "query": "lễ tân khách sạn bãi cháy 5 sao",
                "province": "Quảng Ninh",
                "jobs": [
                    make_test_job("Nhân viên Lễ tân Resort 5 sao", "Vinpearl Resort Hạ Long", "Bãi Cháy", source_platform="vinpearl", status="active_confirmed", posted_days_ago=1), # ground_truth: 3
                    make_test_job("Lễ tân Khách sạn Bãi Cháy", "Khách sạn Hạ Long Plaza", "Bãi Cháy", source_platform="major_job_board", status="active_likely", posted_days_ago=4),  # ground_truth: 2
                    make_test_job("Tuyển lễ tân làm việc tại Ba Đình Hà Nội 5 sao", "KS Hà Nội", "Hà Nội", source_platform="topcv", status="active_confirmed", posted_days_ago=1),     # ground_truth: 0 (Wrong city)
                ],
                "ground_truth_relevance": [3, 2, 0],
            },
            # Scenario 4: Anti-Stale
            {
                "query": "kế toán tổng hợp bãi cháy",
                "province": "Quảng Ninh",
                "jobs": [
                    make_test_job("Kế toán tổng hợp", "Công ty CP Du lịch Quảng Ninh", "Bãi Cháy", status="active_confirmed", posted_days_ago=2, crawled_minutes_ago=10),     # ground_truth: 3 (Fresh & Confirmed)
                    make_test_job("Kế toán tổng hợp", "Công ty TNHH Vận tải Bãi Cháy", "Bãi Cháy", status="active_likely", posted_days_ago=12, crawled_minutes_ago=10),        # ground_truth: 2 (Moderate age)
                    make_test_job("Kế toán tổng hợp", "Công ty TNHH Cũ", "Bãi Cháy", status="expired", posted_days_ago=60, crawled_minutes_ago=5),                             # ground_truth: 0 (Expired recrawled)
                ],
                "ground_truth_relevance": [3, 2, 0],
            },
            # Scenario 5: Trust Authority vs Social Volume
            {
                "query": "nhân viên buồng phòng sun world hạ long",
                "province": "Quảng Ninh",
                "jobs": [
                    make_test_job("Nhân viên Buồng phòng", "Tập đoàn Sun Group", "Hạ Long", source_platform="sun_group", status="active_confirmed", posted_days_ago=3),         # ground_truth: 3 (Enterprise Direct)
                    make_test_job("Nhân viên Buồng phòng Sun World", "Hội việc làm Hạ Long", "Hạ Long", source_platform="facebook_community", status="unknown", posted_days_ago=1), # ground_truth: 1 (Social unverified)
                ],
                "ground_truth_relevance": [3, 1],
            },
        ]

        # Hàm tính Discounted Cumulative Gain (DCG)
        def compute_dcg(relevance_scores: List[float], k: int = 5) -> float:
            dcg = 0.0
            for idx, rel in enumerate(relevance_scores[:k]):
                dcg += (2.0 ** rel - 1.0) / math.log2(idx + 2.0)
            return dcg

        def compute_ndcg(ranked_relevances: List[float], ideal_relevances: List[float], k: int = 5) -> float:
            idcg = compute_dcg(sorted(ideal_relevances, reverse=True), k)
            if idcg == 0.0:
                return 1.0
            dcg = compute_dcg(ranked_relevances, k)
            return dcg / idcg

        # Baseline Keyword Ranker (Đếm số từ khóa xuất hiện đơn thuần trong title + description)
        def baseline_keyword_ranker(jobs: List[Job], query: str) -> List[Job]:
            q_terms = query.lower().split()
            def count_matches(j: Job):
                text = f"{j.title} {j.description or ''} {j.company_name or ''}".lower()
                # Naive score: số lần từ khóa xuất hiện
                score = sum(text.count(t) for t in q_terms)
                # Naive recency: ưu tiên thời gian crawl mới nhất
                crawled = j.crawled_at or datetime.min.replace(tzinfo=timezone.utc)
                return (score, crawled)
            return sorted(jobs, key=count_matches, reverse=True)

        ndcg_multi_signal_list = []
        ndcg_baseline_list = []
        top1_multi_signal_correct = 0
        top1_baseline_correct = 0

        for sc in scenarios:
            intent = search_intent_parser.parse_query(sc["query"], province=sc["province"])
            jobs = sc["jobs"]
            ground_truth = sc["ground_truth_relevance"]
            job_to_gt = {j.id: gt for j, gt in zip(jobs, ground_truth)}
            best_gt = max(ground_truth)

            # 1. Xếp hạng bằng Multi-Signal Engine
            ranked_ms = self.engine.rank_jobs(jobs, intent, sort_by="relevance")
            ms_ordered_jobs = [item["job"] for item in ranked_ms]
            ms_relevances = [job_to_gt[j.id] for j in ms_ordered_jobs]
            ndcg_ms = compute_ndcg(ms_relevances, ground_truth, k=5)
            ndcg_multi_signal_list.append(ndcg_ms)
            print(f"DEBUG SCENARIO #{len(ndcg_multi_signal_list)} -> Top MS rel: {ms_relevances[0]} (best={best_gt}), scores: {[item['score'] for item in ranked_ms]}")
            if ms_relevances[0] == best_gt:
                top1_multi_signal_correct += 1

            # 2. Xếp hạng bằng Baseline Keyword Ranker
            baseline_ordered_jobs = baseline_keyword_ranker(jobs, sc["query"])
            bl_relevances = [job_to_gt[j.id] for j in baseline_ordered_jobs]
            ndcg_bl = compute_ndcg(bl_relevances, ground_truth, k=5)
            ndcg_baseline_list.append(ndcg_bl)
            if bl_relevances[0] == best_gt:
                top1_baseline_correct += 1

        mean_ndcg_ms = sum(ndcg_multi_signal_list) / len(ndcg_multi_signal_list)
        mean_ndcg_bl = sum(ndcg_baseline_list) / len(ndcg_baseline_list)
        top1_acc_ms = top1_multi_signal_correct / len(scenarios) * 100.0
        top1_acc_bl = top1_baseline_correct / len(scenarios) * 100.0

        print(f"\n================ BENCHMARK RANKING RESULTS ================")
        print(f"Multi-Signal Ranking Engine: Mean NDCG@5 = {mean_ndcg_ms:.4f} | Top-1 Accuracy = {top1_acc_ms:.1f}%")
        print(f"Baseline Keyword-Only Ranker: Mean NDCG@5 = {mean_ndcg_bl:.4f} | Top-1 Accuracy = {top1_acc_bl:.1f}%")
        print(f"Improvement: +{(mean_ndcg_ms - mean_ndcg_bl)*100:.2f}% NDCG@5, +{(top1_acc_ms - top1_acc_bl):.1f}% Top-1 Accuracy")
        print(f"===========================================================\n")

        # Khẳng định chất lượng: Multi-Signal Engine phải vượt trội rõ rệt so với Baseline Keyword Ranker
        self.assertGreaterEqual(mean_ndcg_ms, 0.95)
        self.assertGreater(mean_ndcg_ms, mean_ndcg_bl)
        self.assertEqual(top1_acc_ms, 100.0)


if __name__ == "__main__":
    unittest.main()
