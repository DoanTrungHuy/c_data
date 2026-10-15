"""
Hệ thống Tìm kiếm Lai & Xếp hạng Theo Ý Định Người Dùng (Hybrid Search & Explainable Ranking Engine)
Kết hợp:
1. Thu hồi ứng viên ngữ nghĩa & từ khóa (Keyword + Semantic Retrieval)
2. Phân tách rõ ràng Ràng buộc cứng (Hard Constraints) và Sở thích mềm (Soft Preferences)
3. Chấm điểm độ phù hợp minh bạch và giải thích lý do xếp hạng (Explainable Ranking Breakdown)
4. Khử trùng lặp đa nguồn (Cross-source Deduplication) và bảo toàn liên kết gốc
5. Chẩn đoán chi tiết hành trình tìm kiếm (Search Diagnostics)
"""

from datetime import datetime, timedelta, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import unidecode

from app.models.job import Job
from app.services.search_intent_parser import SearchIntent, normalize_text

logger = logging.getLogger("c_data.hybrid_search")


class HybridSearchEngine:
    """
    Hệ thống tìm kiếm kết hợp và xếp hạng có thể giải thích được
    """

    def rank_and_filter_jobs(
        self,
        candidate_jobs: List[Job],
        intent: SearchIntent,
        strict_mode: bool = False,
        verified_only: bool = False,
        sort_by: Optional[str] = "newest",
        workplace_type: Optional[str] = None,
        experience_level: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Lọc theo ràng buộc cứng, chấm điểm theo sở thích mềm và tạo báo cáo chẩn đoán tìm kiếm.
        Nếu không có kết quả đáp ứng điều kiện cứng: trả về danh sách rỗng và gợi ý nới lỏng (suggested_relaxations),
        tuyệt đối không tự ý nới lỏng rồi giả vờ đã khớp đầy đủ.
        """
        now = datetime.now(timezone.utc)

        # Đồng bộ các tham số rõ ràng vào intent nếu có
        if verified_only:
            intent.verified_only = True
            intent.hard_constraints["verified_only"] = True
        if workplace_type:
            intent.workplace_type = workplace_type
            intent.hard_constraints["workplace_type"] = workplace_type
            if workplace_type == "remote":
                intent.is_remote_required = True
        if experience_level:
            intent.seniority = experience_level
            intent.hard_constraints["seniority"] = experience_level
        if company_name:
            intent.target_company = company_name
            intent.hard_constraints["company_name"] = company_name

        parsed_intent_dict = {
            "primary_role": intent.primary_role,
            "role_family": intent.role_family,
            "target_province": intent.target_province,
            "target_district": intent.target_district,
            "province": intent.target_province,
            "city": intent.target_district,
            "location_aliases": intent.location_aliases,
            "seniority": intent.seniority,
            "work_environment": intent.work_environment,
            "workplace_type": intent.workplace_type,
            "is_remote_required": intent.is_remote_required,
            "is_office_preferred": intent.is_office_preferred,
            "travel_preference": intent.travel_preference,
            "field_work_preference": intent.field_work_preference,
            "max_posting_age_days": intent.max_posting_age_days,
            "negative_constraints": intent.negative_constraints,
            "required_skills": intent.required_skills,
            "target_company": intent.target_company,
            "verified_only": intent.verified_only,
            "exact_phrases": intent.exact_phrases,
            "hard_constraints": intent.hard_constraints,
        }

        diagnostics = {
            "original_query": intent.raw_query,
            "parsed_intent": parsed_intent_dict,
            "intent": parsed_intent_dict,
            "strict_mode": strict_mode,
            "expanded_queries": intent.expanded_queries,
            "total_candidates_examined": len(candidate_jobs),
            "removed_by_filters": {
                "hard_location": 0,
                "hard_remote": 0,
                "hard_workplace_type": 0,
                "hard_seniority": 0,
                "hard_verified": 0,
                "hard_posting_age": 0,
                "hard_exclusion": 0,
                "hard_exact_phrase": 0,
                "hard_company": 0,
                "expired": 0,
            },
            "duplicates_consolidated": 0,
            "ranking_details": [],
            "suggested_relaxations": [],
        }

        # 0. Loại bỏ trước các tin đã hết hạn hoặc đã đóng
        active_candidates = []
        for job in candidate_jobs:
            if getattr(job, "status", None) in ["expired", "closed"]:
                diagnostics["removed_by_filters"]["expired"] += 1
                continue
            effective_deadline = getattr(job, "deadline_at", None) or getattr(job, "expires_at", None)
            if effective_deadline:
                exp = effective_deadline if effective_deadline.tzinfo else effective_deadline.replace(tzinfo=timezone.utc)
                if exp < now:
                    diagnostics["removed_by_filters"]["expired"] += 1
                    continue
            active_candidates.append(job)

        # 1. Khử trùng lặp đa nguồn (Cross-source Deduplication)
        deduped_candidates, duplicates_count = self._deduplicate_jobs(active_candidates)
        diagnostics["duplicates_consolidated"] = duplicates_count

        eligible_jobs = []

        # 2. Đánh giá từng tin tuyển dụng theo ràng buộc cứng
        for job in deduped_candidates:
            passed_hard, fail_reason = self._evaluate_hard_constraints(job, intent, now, strict_mode)
            if not passed_hard:
                if "location" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_location"] += 1
                elif "remote" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_remote"] += 1
                elif "workplace_type" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_workplace_type"] += 1
                elif "seniority" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_seniority"] += 1
                elif "verified" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_verified"] += 1
                elif "posting_age" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_posting_age"] += 1
                elif "exclusion" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_exclusion"] += 1
                elif "exact_phrase" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_exact_phrase"] += 1
                elif "company" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_company"] += 1
                continue

            # Chấm điểm độ phù hợp & lập giải thích xếp hạng đa tín hiệu
            score_data = self._score_job_intent_fit(job, intent, now)
            if score_data["total_score"] > 0:
                eligible_jobs.append({
                    "job": job,
                    "score": score_data["total_score"],
                    "reasons": score_data["reasons"],
                    "ranking_breakdown": score_data.get("ranking_breakdown"),
                    "criteria_scores": score_data["criteria_scores"],
                    "all_sources": getattr(job, "_consolidated_sources", [
                        {"platform": job.source_platform, "url": job.source_url}
                    ]),
                })

        # 3. Xử lý trường hợp không có kết quả đáp ứng điều kiện cứng:
        # Tuyệt đối không tự ý nới lỏng rồi giả vờ đã khớp đầy đủ, mà đề xuất suggested_relaxations
        if len(eligible_jobs) == 0:
            rm = diagnostics["removed_by_filters"]
            relaxations = []
            if rm.get("hard_location", 0) > 0:
                target = intent.target_district or intent.target_province or "khu vực đã chọn"
                relaxations.append(f"Mở rộng phạm vi địa điểm: Thử tìm kiếm trên toàn tỉnh hoặc các khu vực lân cận thay vì chỉ giới hạn tại {target}.")
            if rm.get("hard_remote", 0) > 0 or rm.get("hard_workplace_type", 0) > 0:
                relaxations.append("Nới lỏng hình thức làm việc: Bật thêm lựa chọn Hybrid hoặc Onsite tại văn phòng thay vì chỉ giới hạn Remote 100%.")
            if rm.get("hard_seniority", 0) > 0:
                relaxations.append("Nới lỏng cấp độ kinh nghiệm: Mở rộng tiêu chí sang Middle hoặc Không giới hạn kinh nghiệm để tiếp cận nhiều cơ hội hơn.")
            if rm.get("hard_verified", 0) > 0:
                relaxations.append("Mở rộng trạng thái xác minh: Tắt tùy chọn 'Chỉ tin đã xác minh' để xem các cơ hội mới thu thập đang chờ xác thực.")
            if rm.get("hard_posting_age", 0) > 0:
                relaxations.append("Mở rộng thời gian đăng bài: Thử tìm các tin đăng trong vòng 14 đến 30 ngày thay vì chỉ các tin mới nhất.")
            if rm.get("hard_exclusion", 0) > 0:
                relaxations.append("Nới lỏng điều kiện loại trừ: Thử bỏ bớt một số từ khóa phủ định hoặc điều kiện cấm trong ô tìm kiếm.")
            if rm.get("hard_exact_phrase", 0) > 0:
                relaxations.append("Bỏ dấu ngoặc kép: Thử tìm kiếm từ khóa linh hoạt không đặt trong dấu ngoặc kép để tăng độ phủ kết quả.")
            if rm.get("hard_company", 0) > 0:
                relaxations.append("Bỏ lọc theo công ty: Thử tìm kiếm theo vị trí nghề nghiệp chung thay vì giới hạn tại một doanh nghiệp cụ thể.")

            if not relaxations and len(candidate_jobs) == 0:
                relaxations.append("Thử thay đổi từ khóa tìm kiếm hoặc sử dụng các từ đồng nghĩa phổ biến trong ngành.")

            diagnostics["suggested_relaxations"] = relaxations

        # 4. Sắp xếp kết quả theo yêu cầu (Relevance, Newest, Salary)
        if sort_by == "salary_desc":
            eligible_jobs.sort(
                key=lambda x: (
                    x["job"].salary_max or x["job"].salary_min or 0,
                    x["score"]
                ),
                reverse=True,
            )
        elif sort_by == "salary_asc":
            eligible_jobs.sort(
                key=lambda x: (
                    x["job"].salary_min or x["job"].salary_max or 999999999,
                    -x["score"]
                ),
            )
        elif sort_by == "pure_newest":
            eligible_jobs.sort(
                key=lambda x: (
                    x["job"].posted_at or x["job"].crawled_at or datetime.min.replace(tzinfo=timezone.utc),
                    x["score"]
                ),
                reverse=True,
            )
        else:  # Mặc định theo Độ liên quan (Relevance Ranking: Score -> Posted_at)
            eligible_jobs.sort(
                key=lambda x: (
                    x["score"],
                    x["job"].posted_at or x["job"].crawled_at or datetime.min.replace(tzinfo=timezone.utc)
                ),
                reverse=True,
            )

        diagnostics["final_eligible_count"] = len(eligible_jobs)
        diagnostics["ranking_details"] = [
            {
                "job_id": str(item["job"].id),
                "title": item["job"].title,
                "company": item["job"].company_name,
                "score": round(item["score"], 1),
                "ranking_breakdown": item.get("ranking_breakdown"),
                "criteria": item["criteria_scores"],
                "reasons": item["reasons"],
            }
            for item in eligible_jobs[:10]
        ]

        return eligible_jobs, diagnostics


    def _deduplicate_jobs(self, jobs: List[Job]) -> Tuple[List[Job], int]:
        """
        Khử trùng lặp đa nguồn sử dụng JobDeduplicationEngine.
        Áp dụng chuẩn hóa Canonical URL, Anti-merge guard, bảo toàn độ tin cậy và lịch sử xung đột.
        """
        from app.services.job_deduplication_engine import job_deduplication_engine
        return job_deduplication_engine.consolidate_jobs(jobs)

    def _evaluate_hard_constraints(
        self,
        job: Job,
        intent: SearchIntent,
        now: datetime,
        strict_mode: bool,
    ) -> Tuple[bool, str]:
        """
        Đánh giá các ràng buộc cứng:
        - Ràng buộc tin đã xác minh (Verified only): Loại trừ unknown, expired, closed.
        - Ràng buộc Remote 100%: Tuyệt đối không đưa Hybrid hoặc Onsite vào.
        - Ràng buộc Hybrid / Onsite khi chọn cụ thể.
        - Ràng buộc cấp bậc kinh nghiệm: Fresher/Junior không đưa Senior/Lead/Manager/3+ năm vào.
        - Ràng buộc địa lý: Phân biệt địa điểm làm việc thực tế với trụ sở chính công ty. Chỉ Hạ Long khi có bằng chứng phù hợp.
        - Ràng buộc doanh nghiệp, trích dẫn nguyên văn và điều kiện phủ định.
        """
        title_norm = normalize_text(job.title)
        desc_norm = normalize_text(job.description or "")
        req_norm = normalize_text(job.requirements or "")
        comp_norm = normalize_text(job.company_name or "")
        loc_norm = normalize_text(f"{job.location_province or ''} {job.location_district or ''} {job.location_full or ''}")
        full_content_norm = f"{title_norm} {desc_norm} {req_norm} {comp_norm} {loc_norm}"

        # 0. Ràng buộc tin đã xác minh (Verified Only)
        is_verified_required = (
            intent.verified_only or
            intent.hard_constraints.get("verified_only", False)
        )
        if is_verified_required:
            job_status = getattr(job, "status", None)
            if job_status not in ["active_confirmed", "active_likely"]:
                return False, f"hard_verified: Trạng thái '{job_status}' chưa được xác thực (chỉ nhận active_confirmed/active_likely)"

        # 1. Ràng buộc Remote cứng (Remote 100% vs Hybrid vs Onsite)
        req_remote = (
            intent.is_remote_required or
            intent.workplace_type == "remote" or
            intent.hard_constraints.get("workplace_type") == "remote" or
            intent.hard_constraints.get("work_type") == "remote"
        )
        if req_remote:
            job_wp = getattr(job, "workplace_type", "")
            # Tuyệt đối không cho phép Hybrid hoặc Onsite lẫn vào khi yêu cầu Remote 100%
            if job_wp == "hybrid":
                return False, "hard_remote: Yêu cầu remote 100%, không chấp nhận Hybrid"
            if job_wp == "onsite":
                return False, "hard_remote: Yêu cầu remote 100%, không chấp nhận Onsite"

            # Kiểm tra text mô tả nếu có yếu tố Hybrid bắt buộc lên văn phòng
            if any(w in desc_norm for w in ["hybrid", "len cong ty", "len van phong", "ngay tai van phong"]):
                if not any(w in desc_norm for w in ["remote 100%", "100% remote", "toan thoi gian tu xa"]):
                    return False, "hard_remote: Vị trí yêu cầu Hybrid/lên văn phòng, không phải Remote 100%"

            is_remote_confirmed = (
                job_wp == "remote" or
                job.job_type in ["remote", "Làm việc từ xa"] or
                "remote" in title_norm or
                "lam viec tu xa" in title_norm or
                "lam tai nha" in desc_norm or
                "remote 100%" in desc_norm or
                "100% remote" in desc_norm
            )
            if not is_remote_confirmed:
                return False, "hard_remote: Vị trí không xác thực làm việc từ xa"

        # 1b. Ràng buộc Hybrid cứng
        req_hybrid = (
            intent.workplace_type == "hybrid" or
            intent.hard_constraints.get("workplace_type") == "hybrid"
        )
        if req_hybrid and strict_mode:
            job_wp = getattr(job, "workplace_type", "")
            is_hybrid = (
                job_wp == "hybrid" or
                "hybrid" in title_norm or
                "hybrid" in desc_norm or
                "ban thoi gian van phong" in desc_norm
            )
            if not is_hybrid:
                return False, "hard_workplace_type: Chỉ chấp nhận hình thức Hybrid"

        # 1c. Ràng buộc Onsite cứng
        req_onsite = (
            intent.workplace_type == "onsite" or
            intent.hard_constraints.get("workplace_type") == "onsite"
        )
        if req_onsite and strict_mode:
            job_wp = getattr(job, "workplace_type", "")
            if job_wp == "remote" or job.job_type in ["remote", "Làm việc từ xa"]:
                return False, "hard_workplace_type: Chỉ chấp nhận hình thức Onsite tại văn phòng"

        # 2. Ràng buộc thời gian đăng bài (Tuổi bài viết dựa trên original posted_at)
        if intent.max_posting_age_days:
            posted = job.posted_at
            if not posted:
                posted = job.crawled_at

            if posted:
                p_dt = posted if posted.tzinfo else posted.replace(tzinfo=timezone.utc)
                age_days = (now - p_dt).total_seconds() / 86400.0
                if age_days > intent.max_posting_age_days:
                    return False, f"hard_posting_age: Đăng cách đây {round(age_days, 1)} ngày (vượt quá {intent.max_posting_age_days} ngày)"

        # 3. Ràng buộc địa lý (Phân biệt Địa điểm làm việc thực tế với Trụ sở doanh nghiệp)
        # Chỉ xem là việc tại Hạ Long / Quảng Ninh khi có bằng chứng phù hợp; không tự đưa việc Hà Nội vào.
        if intent.target_province and not req_remote and strict_mode:
            target_prov_norm = normalize_text(intent.target_province)
            target_dist_norm = normalize_text(intent.target_district) if intent.target_district else None

            # Bằng chứng địa điểm làm việc thực tế
            actual_location_evidence = False

            prov_field_norm = normalize_text(job.location_province or "")
            dist_field_norm = normalize_text(job.location_district or "")
            full_loc_field_norm = normalize_text(job.location_full or "")

            structured_locations = getattr(job, "locations", None) or []
            if isinstance(structured_locations, list):
                for loc_item in structured_locations:
                    if isinstance(loc_item, dict):
                        lp = normalize_text(loc_item.get("province", ""))
                        ld = normalize_text(loc_item.get("district", ""))
                        la = normalize_text(loc_item.get("address", ""))
                        if target_prov_norm in lp or any(normalize_text(a) in f"{lp} {ld} {la}" for a in intent.location_aliases):
                            actual_location_evidence = True
                            break

            if not actual_location_evidence:
                for alias in intent.location_aliases:
                    norm_alias = normalize_text(alias)
                    if norm_alias and (
                        norm_alias in prov_field_norm or
                        norm_alias in dist_field_norm or
                        norm_alias in full_loc_field_norm or
                        norm_alias in title_norm
                    ):
                        actual_location_evidence = True
                        break

            if not actual_location_evidence:
                work_loc_matches = re.findall(
                    r"(?:dia diem lam viec|noi lam viec|lam viec tai|chi nhanh|co so)\s*:\s*([^.\n;]+)",
                    desc_norm
                )
                for wlm in work_loc_matches:
                    for alias in intent.location_aliases:
                        if normalize_text(alias) in wlm:
                            actual_location_evidence = True
                            break

            # Kiểm tra phân định: Trụ sở Hà Nội nhưng làm việc thực tế ở Hà Nội -> REJECT
            if target_prov_norm == "quang ninh":
                is_explicitly_outside = False
                if any(omp in prov_field_norm for omp in ["ha noi", "ho chi minh", "da nang"]):
                    if not any(a in full_loc_field_norm or a in title_norm for a in ["ha long", "bai chay", "hon gai", "quang ninh"]):
                        is_explicitly_outside = True
                if is_explicitly_outside or not actual_location_evidence:
                    return False, f"hard_location: Không có bằng chứng địa điểm làm việc thực tế tại {intent.target_province}"
            else:
                if not actual_location_evidence:
                    return False, f"hard_location: Không thuộc khu vực {intent.target_province}"

            # Nếu yêu cầu cụ thể thành phố Hạ Long
            if target_dist_norm:
                dist_matched = False
                halong_aliases = ["ha long", "bai chay", "hon gai", "tuan chau"] if "ha long" in target_dist_norm else [target_dist_norm]
                for ha in halong_aliases:
                    if (
                        ha in dist_field_norm or
                        ha in full_loc_field_norm or
                        ha in title_norm or
                        ha in desc_norm
                    ):
                        dist_matched = True
                        break
                if not dist_matched:
                    return False, f"hard_location: Địa điểm không thuộc {intent.target_district}"

        # 4. Ràng buộc cấp bậc / kinh nghiệm (Seniority: Fresher/Junior vs Senior/Lead)
        is_entry_search = (
            intent.seniority in ["fresher", "junior", "intern"] or
            intent.hard_constraints.get("seniority") in ["fresher", "junior", "intern"]
        )
        if is_entry_search and strict_mode:
            exp_lvl = getattr(job, "experience_level", "") or ""
            if exp_lvl in ["senior", "lead", "middle_senior", "manager", "director"]:
                return False, "hard_seniority: Tìm kiếm Fresher/Junior nhưng tin tuyển dụng yêu cầu cấp bậc Senior/Lead"

            if any(re.search(rf"\b{re.escape(w)}\b", title_norm) for w in [
                "senior", "lead", "truong nhom", "truong phong", "giam doc", "quan ly", "architect", "chuyen gia"
            ]):
                return False, "hard_seniority: Tiêu đề yêu cầu cấp bậc Senior/Lead/Quản lý"

            exp_patterns = [
                r"(?:tu|it nhat|toi thieu|tren|yeu cau)\s*([3-9]|1[0-9])\s*nam\s*(?:kinh nghiem|kn)",
                r"([3-9]|1[0-9])\+\s*nam\s*(?:kinh nghiem|kn)",
            ]
            for pat in exp_patterns:
                m = re.search(pat, req_norm) or re.search(pat, desc_norm)
                if m:
                    years = int(m.group(1))
                    if years >= 3:
                        return False, f"hard_seniority: Yêu cầu từ {years} năm kinh nghiệm (Senior), không phù hợp với Fresher/Junior"

        is_senior_search = (
            intent.seniority in ["senior", "lead"] or
            intent.hard_constraints.get("seniority") in ["senior", "lead"]
        )
        if is_senior_search and strict_mode:
            exp_lvl = getattr(job, "experience_level", "") or ""
            if exp_lvl in ["intern", "fresher"] or any(w in title_norm for w in ["thuc tap", "intern", "hoc viec"]):
                return False, "hard_seniority: Tìm kiếm Senior nhưng tin là vị trí Thực tập sinh/Fresher"

        # 5. Ràng buộc doanh nghiệp (Target Company)
        target_comp = intent.target_company or intent.hard_constraints.get("company_name")
        if target_comp and strict_mode:
            tc_norm = normalize_text(target_comp)
            if tc_norm and tc_norm not in comp_norm and comp_norm not in tc_norm:
                return False, f"hard_company: Doanh nghiệp '{job.company_name}' không khớp '{target_comp}'"

        # 6. Ràng buộc cụm từ trích dẫn trong ngoặc kép (Exact Quoted Phrases)
        if intent.exact_phrases and strict_mode:
            for phrase in intent.exact_phrases:
                p_norm = normalize_text(phrase)
                if p_norm and p_norm not in full_content_norm:
                    return False, f"hard_exact_phrase: Không chứa cụm từ bắt buộc '{phrase}'"

        # 7. Ràng buộc điều kiện loại trừ / cấm kỵ (Negative Constraints)
        if intent.negative_constraints and strict_mode:
            for neg in intent.negative_constraints:
                neg_norm = normalize_text(neg)
                if not neg_norm:
                    continue
                if neg_norm in ["lap dat tren cao / leo cot", "lap dat tren cao", "leo cot", "tren cao"]:
                    if any(w in full_content_norm for w in ["tren cao", "leo cot", "keo cap ngoai troi"]):
                        return False, "hard_exclusion: Yêu cầu leo cột / trên cao bị loại trừ"
                elif neg_norm in ["di cong tac thuong xuyen", "di cong tac", "cong tac xa"]:
                    if any(w in full_content_norm for w in ["di cong tac", "cong tac xa", "di tinh"]):
                        return False, "hard_exclusion: Yêu cầu đi công tác bị loại trừ"
                else:
                    if re.search(rf"\b{re.escape(neg_norm)}\b", full_content_norm):
                        return False, f"hard_exclusion: Chứa từ khóa bị loại trừ '{neg}'"

        return True, "passed"


    def _score_job_intent_fit(
        self,
        job: Job,
        intent: SearchIntent,
        now: datetime,
    ) -> Dict[str, Any]:
        """
        Chấm điểm độ phù hợp và giải thích rõ ràng lý do dựa trên MultiSignalRankingEngine:
        7 tín hiệu chuẩn hóa: Gate cứng, Chức danh/kỹ năng (40đ), Nguồn (15đ), Xác thực (15đ),
        Độ tươi mới posted_at (10đ), Đầy đủ dữ liệu & URL ứng tuyển (10đ), Địa điểm & hình thức (10đ).
        """
        from app.services.ranking_engine import multi_signal_ranking_engine
        breakdown = multi_signal_ranking_engine.score_job(job, intent, now)
        criteria_scores = {
            k: v.get("score", 0.0)
            for k, v in breakdown.signals.items()
        }
        return {
            "total_score": breakdown.total_score,
            "reasons": breakdown.reasons,
            "criteria_scores": criteria_scores,
            "ranking_breakdown": breakdown.to_dict(),
        }

    def _legacy_score_job_intent_fit(
        self,
        job: Job,
        intent: SearchIntent,
        now: datetime,
    ) -> Dict[str, Any]:
        """
        Chấm điểm độ phù hợp và giải thích rõ ràng lý do:

        - Job-role relevance (+35 max)
        - Responsibility & Content match (+20 max)
        - Technical skill match (+15 max)
        - Location match (+20 max)
        - Seniority match (+15 max, hoặc phạt -25 cho senior khi cần junior)
        - Work environment & Exclusion check (+15 bonus / -35 penalty)
        - Freshness boost (+10 max)
        """
        title_raw = job.title or ""
        title_norm = normalize_text(title_raw)
        desc_raw = job.description or ""
        desc_norm = normalize_text(desc_raw)
        req_raw = job.requirements or ""
        req_norm = normalize_text(req_raw)
        comp_norm = normalize_text(job.company_name or "")
        loc_norm = normalize_text(f"{job.location_province or ''} {job.location_district or ''} {job.location_full or ''}")
        full_content_norm = f"{title_norm} {desc_norm} {req_norm}"

        reasons: List[str] = []
        criteria_scores = {
            "role_score": 0.0,
            "responsibility_score": 0.0,
            "skill_score": 0.0,
            "location_score": 0.0,
            "seniority_score": 0.0,
            "work_env_score": 0.0,
            "freshness_score": 0.0,
        }

        # =====================================================================
        # 1. KHỚP VAI TRÒ NGHỀ NGHIỆP (Job-Role Relevance - Max 35 điểm)
        # =====================================================================
        role_matched = False
        for syn in intent.role_synonyms:
            syn_norm = normalize_text(syn)
            if not syn_norm:
                continue
            # Khớp trong tiêu đề
            if re.search(rf"\b{re.escape(syn_norm)}\b", title_norm):
                criteria_scores["role_score"] = 35.0
                reasons.append(f"Tiêu đề khớp chính xác vị trí: '{syn}' (+35)")
                role_matched = True
                break
            elif syn_norm in title_norm:
                criteria_scores["role_score"] = max(criteria_scores["role_score"], 28.0)
                reasons.append(f"Tiêu đề chứa từ khóa vai trò: '{syn}' (+28)")
                role_matched = True

        # Khớp token vai trò độc lập (Ví dụ: IT, CNTT, Bác sĩ, Lái xe) trong tiêu đề
        if not role_matched and intent.primary_role:
            if "IT" in intent.primary_role:
                if re.search(r"\b(it|cntt)\b", title_norm):
                    criteria_scores["role_score"] = 30.0
                    reasons.append("Tiêu đề chứa định danh chuyên môn IT/CNTT (+30)")
                    role_matched = True

        # Khớp ngành nghề danh mục
        if not role_matched and intent.primary_role:
            cat_norm = normalize_text(job.category or "")
            if normalize_text(intent.primary_role) in cat_norm or cat_norm in normalize_text(intent.primary_role):
                criteria_scores["role_score"] = 25.0
                reasons.append(f"Ngành nghề phù hợp với nhóm: {intent.primary_role} (+25)")
                role_matched = True
            elif ("it" in normalize_text(intent.primary_role) or "phan mem" in normalize_text(intent.primary_role)) and (
                "cong nghe thong tin" in cat_norm or "phan mem" in cat_norm or "it" in cat_norm
            ):
                criteria_scores["role_score"] = 25.0
                reasons.append("Ngành nghề thuộc nhóm Công nghệ thông tin / IT (+25)")
                role_matched = True

        # Khớp tổ hợp từ khóa trong tiêu đề (chỉ xét từ khóa nghề nghiệp, LOẠI TRỪ địa danh và hư từ)
        loc_words = {
            "quang", "ninh", "ha", "long", "cam", "pha", "uong", "bi", "bai", "chay",
            "hon", "gai", "tuan", "chau", "noi", "sai", "gon", "chi", "minh", "da", "nang",
            "viet", "nam", "tinh", "tp", "thanh", "pho", "quan", "huyen", "phuong", "xa"
        }
        for alias in intent.location_aliases:
            loc_words.update(normalize_text(alias).split())
        if intent.target_province:
            loc_words.update(normalize_text(intent.target_province).split())
        if intent.target_district:
            loc_words.update(normalize_text(intent.target_district).split())

        if not role_matched:
            norm_q = normalize_text(intent.raw_query)
            stop_words = {"tuyen", "can", "gap", "viec", "lam", "tim", "o", "tai", "cho", "nguoi", "moi", "dang", "trong", "ngay", "job", "jobs"}
            q_words = [w for w in norm_q.split() if len(w) >= 2 and w not in loc_words and w not in stop_words]
            if len(q_words) >= 1:
                matched_words = [w for w in q_words if re.search(rf"\b{re.escape(w)}\b", title_norm)]
                if len(matched_words) >= 1:
                    criteria_scores["role_score"] = 25.0
                    reasons.append(f"Tiêu đề chứa từ khóa vai trò: {' + '.join(matched_words)} (+25)")
                    role_matched = True

        # Nếu không khớp vai trò, kiểm tra từ khóa chuyên môn trong tiêu đề hoặc toàn bài (tránh gán điểm khi query chỉ gồm địa danh)
        if criteria_scores["role_score"] == 0:
            norm_q = normalize_text(intent.raw_query)
            q_tokens_non_loc = [w for w in norm_q.split() if w not in loc_words]
            if q_tokens_non_loc and len(norm_q) <= 25 and (norm_q in title_norm or norm_q in full_content_norm):
                criteria_scores["role_score"] = 20.0
                reasons.append(f"Khớp từ khóa tìm kiếm: '{intent.raw_query}' (+20)")

        # =====================================================================
        # 2. KHỚP TRÁCH NHIỆM THỰC TẾ & MÔ TẢ (Responsibility Match - Max 20 điểm)
        # =====================================================================
        resp_hits = 0
        it_responsibilities = [
            ("ho tro", "hỗ trợ kỹ thuật người dùng"),
            ("sua chua", "xử lý sự cố phần cứng / máy tính"),
            ("cai dat", "cài đặt phần mềm / hệ điều hành"),
            ("he thong", "quản trị hệ thống máy chủ / PMS"),
            ("mang lan", "quản lý mạng nội bộ WiFi/LAN"),
            ("khach san", "vận hành hệ thống CNTT resort / khách sạn"),
            ("phan mem", "phát triển / bảo trì ứng dụng"),
        ]
        for key, label in it_responsibilities:
            if key in desc_norm:
                resp_hits += 1

        if resp_hits >= 3:
            criteria_scores["responsibility_score"] = 20.0
            reasons.append(f"Nhiệm vụ thực tế khớp cao ({resp_hits} đầu việc chuyên môn) (+20)")
        elif resp_hits >= 1:
            criteria_scores["responsibility_score"] = 10.0 + resp_hits * 3
            reasons.append(f"Mô tả công việc có các trách nhiệm kỹ thuật phù hợp (+{int(criteria_scores['responsibility_score'])})")

        # =====================================================================
        # 3. KHỚP KỸ NĂNG CHUYÊN MÔN (Skill Match - Max 15 điểm)
        # =====================================================================
        if intent.required_skills:
            matched_skills = []
            for skill in intent.required_skills:
                skill_norm = normalize_text(skill)
                if re.search(rf"\b{re.escape(skill_norm)}\b", full_content_norm):
                    matched_skills.append(skill)
            if matched_skills:
                criteria_scores["skill_score"] = min(15.0, len(matched_skills) * 8.0)
                reasons.append(f"Khớp các kỹ năng yêu cầu: {', '.join(matched_skills)} (+{int(criteria_scores['skill_score'])})")

        # =====================================================================
        # 4. KHỚP ĐỊA ĐIỂM (Location Match - Max 20 điểm)
        # =====================================================================
        if intent.target_province:
            loc_matched = False
            # Khớp huyện / thành phố cụ thể (Hạ Long, Bãi Cháy...)
            if intent.target_district and (
                normalize_text(intent.target_district) in loc_norm or
                any(normalize_text(a) in loc_norm for a in ["bai chay", "hon gai", "tuan chau", "ha long"])
            ):
                criteria_scores["location_score"] = 20.0
                reasons.append(f"Nơi làm việc đúng khu vực trọng điểm: {intent.target_district} (+20)")
                loc_matched = True
            elif normalize_text(intent.target_province) in loc_norm:
                criteria_scores["location_score"] = 15.0
                reasons.append(f"Nơi làm việc tại tỉnh {intent.target_province} (+15)")
                loc_matched = True
            elif any(normalize_text(a) in loc_norm for a in intent.location_aliases):
                criteria_scores["location_score"] = 12.0
                reasons.append(f"Nằm trong khu vực phụ cận {intent.target_province} (+12)")
                loc_matched = True

            if not loc_matched and not intent.is_remote_required:
                # Phạt điểm nếu vị trí ở tỉnh khác
                criteria_scores["location_score"] = -15.0
                reasons.append("Địa điểm làm việc ngoài khu vực ưu tiên (-15)")
        else:
            criteria_scores["location_score"] = 10.0

        # =====================================================================
        # 5. ĐÁNH GIÁ CẤP BẬC / KINH NGHIỆM (Seniority Match - Max 15 điểm)
        # =====================================================================
        is_job_senior = any(w in title_norm or w in req_norm for w in ["senior", "truong nhom", "lead", "manager", "5 nam", "4 nam", "3 nam"])
        is_job_entry = any(w in full_content_norm for w in [
            "khong yeu cau kinh nghiem", "khong can kinh nghiem", "chua co kinh nghiem",
            "fresher", "junior", "moi ra truong", "dao tao tu dau", "1 nam", "tap su"
        ])

        if intent.seniority in ["fresher", "junior"]:
            if is_job_senior:
                criteria_scores["seniority_score"] = -25.0
                reasons.append("Yêu cầu cấp bậc Senior / Trưởng nhóm (không phù hợp người mới) (-25)")
            elif is_job_entry:
                criteria_scores["seniority_score"] = 15.0
                reasons.append("Phù hợp người mới ra trường / Chưa nhiều kinh nghiệm (+15)")
            else:
                criteria_scores["seniority_score"] = 5.0
        elif intent.seniority == "senior":
            if is_job_senior:
                criteria_scores["seniority_score"] = 15.0
                reasons.append("Phù hợp cấp bậc Senior / Chuyên viên chuyên sâu (+15)")
        else:
            criteria_scores["seniority_score"] = 5.0

        # =====================================================================
        # 6. MÔI TRƯỜNG LÀM VIỆC & PHỦ ĐỊNH / LOẠI TRỪ (Work Env & Exclusions)
        # =====================================================================
        # Kiểm tra mong muốn làm việc văn phòng (office-based)
        if intent.is_office_preferred:
            has_office_terms = any(w in full_content_norm for w in ["van phong", "resort", "khach san", "toa nha", "ngoi truc", "pms", "truc van phong"])
            if has_office_terms:
                criteria_scores["work_env_score"] += 15.0
                reasons.append("Môi trường văn phòng / Khách sạn nghỉ dưỡng cố định (+15)")
            else:
                reasons.append("Môi trường làm việc: Chưa nêu rõ (Unknown)")

        # Kiểm tra các điều cấm kỵ (Negative Constraints)
        if intent.field_work_preference == "avoid_heights" or "lắp đặt trên cao / leo cột" in intent.negative_constraints:
            has_heights = any(w in full_content_norm for w in ["tren cao", "leo cot", "keo cap ngoai troi", "ngoai troi", "cong trinh"])
            if has_heights:
                criteria_scores["work_env_score"] -= 35.0
                reasons.append("Có yêu cầu kéo cáp / làm việc ngoài trời hoặc trên cao (Trái sở thích) (-35)")

        if intent.travel_preference == "avoid_travel" or "đi công tác thường xuyên" in intent.negative_constraints:
            has_travel = any(w in full_content_norm for w in ["di cong tac", "cong tac xa", "di tinh", "luu dong"])
            if has_travel:
                criteria_scores["work_env_score"] -= 30.0
                reasons.append("Có yêu cầu đi công tác xa / lưu động (Trái sở thích) (-30)")

        # =====================================================================
        # 7. ĐỘ TƯƠI MỚI BÀI ĐĂNG (Freshness Boost - Max 10 điểm)
        # =====================================================================
        posted = job.posted_at or job.crawled_at
        if posted:
            p_dt = posted if posted.tzinfo else posted.replace(tzinfo=timezone.utc)
            diff_hours = (now - p_dt).total_seconds() / 3600.0
            if diff_hours <= 12:
                criteria_scores["freshness_score"] = 10.0
                reasons.append(f"Tin rất mới (đăng cách đây {int(diff_hours)} giờ) (+10)")
            elif diff_hours <= 72:
                criteria_scores["freshness_score"] = 7.0
                reasons.append(f"Đăng trong 3 ngày qua (+7)")
            elif diff_hours <= 168:
                criteria_scores["freshness_score"] = 4.0
                reasons.append("Đăng trong tuần (+4)")

        # =====================================================================
        # 8. KHỚP TÊN DOANH NGHIỆP & CỤM TỪ TRÍCH DẪN (Company & Exact Phrases)
        # =====================================================================
        if intent.target_company:
            tc_norm = normalize_text(intent.target_company)
            if tc_norm and (tc_norm in comp_norm or comp_norm in tc_norm):
                criteria_scores["company_score"] = 25.0
                reasons.append(f"Khớp chính xác tên doanh nghiệp: '{intent.target_company}' (+25)")

        if intent.exact_phrases:
            matched_p = [p for p in intent.exact_phrases if normalize_text(p) in full_content_norm]
            if matched_p:
                criteria_scores["exact_phrase_score"] = min(20.0, len(matched_p) * 10.0)
                reasons.append(f"Khớp cụm từ trong ngoặc kép: {', '.join(matched_p)} (+{int(criteria_scores['exact_phrase_score'])})")

        # Tính tổng điểm
        total = sum(criteria_scores.values())

        # Bảo vệ độ chuẩn xác (Strict relevance gate):
        has_signal = (
            criteria_scores["role_score"] > 0 or
            criteria_scores["skill_score"] > 0 or
            criteria_scores["responsibility_score"] >= 15.0 or
            criteria_scores.get("company_score", 0.0) > 0 or
            criteria_scores.get("exact_phrase_score", 0.0) > 0
        )
        if not has_signal and intent.primary_role:
            total = 0.0

        return {
            "total_score": max(0.0, total),
            "reasons": reasons,
            "criteria_scores": criteria_scores,
        }


hybrid_search_engine = HybridSearchEngine()

