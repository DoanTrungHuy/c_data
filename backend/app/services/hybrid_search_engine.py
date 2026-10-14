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
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Lọc theo ràng buộc cứng, chấm điểm theo sở thích mềm và tạo báo cáo chẩn đoán tìm kiếm.
        Trả về: (danh_sách_kết_quả_kèm_giải_thích, chẩn_đoán_search_diagnostics)
        """
        now = datetime.now(timezone.utc)
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
            "is_remote_required": intent.is_remote_required,
            "is_office_preferred": intent.is_office_preferred,
            "travel_preference": intent.travel_preference,
            "field_work_preference": intent.field_work_preference,
            "max_posting_age_days": intent.max_posting_age_days,
            "negative_constraints": intent.negative_constraints,
            "required_skills": intent.required_skills,
        }

        diagnostics = {
            "original_query": intent.raw_query,
            "parsed_intent": parsed_intent_dict,
            "intent": parsed_intent_dict,
            "expanded_queries": intent.expanded_queries,
            "total_candidates_examined": len(candidate_jobs),
            "removed_by_filters": {
                "hard_location": 0,
                "hard_remote": 0,
                "hard_posting_age": 0,
                "hard_exclusion": 0,
                "expired": 0,
            },
            "duplicates_consolidated": 0,
            "ranking_details": [],
        }

        # 0. Loại bỏ trước các tin đã hết hạn để không làm ảnh hưởng tin còn hạn khi khử trùng lặp
        active_candidates = []
        for job in candidate_jobs:
            if job.expires_at:
                exp = job.expires_at if job.expires_at.tzinfo else job.expires_at.replace(tzinfo=timezone.utc)
                if exp < now:
                    diagnostics["removed_by_filters"]["expired"] += 1
                    continue
            active_candidates.append(job)

        # 1. Khử trùng lặp đa nguồn (Cross-source Deduplication)
        deduped_candidates, duplicates_count = self._deduplicate_jobs(active_candidates)
        diagnostics["duplicates_consolidated"] = duplicates_count

        eligible_jobs = []

        # 2. Đánh giá từng tin tuyển dụng
        for job in deduped_candidates:
            # Áp dụng ràng buộc cứng (Hard Constraints)
            passed_hard, fail_reason = self._evaluate_hard_constraints(job, intent, now, strict_mode)
            if not passed_hard:
                if "location" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_location"] += 1
                elif "remote" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_remote"] += 1
                elif "posting_age" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_posting_age"] += 1
                elif "exclusion" in fail_reason:
                    diagnostics["removed_by_filters"]["hard_exclusion"] += 1
                continue

            # Chấm điểm độ phù hợp & lập giải thích xếp hạng
            score_data = self._score_job_intent_fit(job, intent, now)
            if score_data["total_score"] > 0:
                eligible_jobs.append({
                    "job": job,
                    "score": score_data["total_score"],
                    "reasons": score_data["reasons"],
                    "criteria_scores": score_data["criteria_scores"],
                    "all_sources": getattr(job, "_consolidated_sources", [
                        {"platform": job.source_platform, "url": job.source_url}
                    ]),
                })

        # 3. Sắp xếp theo tổng điểm độ phù hợp (Relevance Ranking)
        eligible_jobs.sort(key=lambda x: (x["score"], x["job"].posted_at or x["job"].crawled_at), reverse=True)

        diagnostics["final_eligible_count"] = len(eligible_jobs)
        diagnostics["ranking_details"] = [
            {
                "job_id": str(item["job"].id),
                "title": item["job"].title,
                "company": item["job"].company_name,
                "score": round(item["score"], 1),
                "criteria": item["criteria_scores"],
                "reasons": item["reasons"],
            }
            for item in eligible_jobs[:10]
        ]

        return eligible_jobs, diagnostics

    def _deduplicate_jobs(self, jobs: List[Job]) -> Tuple[List[Job], int]:
        """
        Khử trùng lặp đa nguồn dựa trên chuẩn hóa tiêu đề, tên công ty và địa phương.
        Bảo toàn toàn bộ danh sách đường dẫn gốc vào `_consolidated_sources`.
        """
        seen: Dict[str, Job] = {}
        duplicates_count = 0

        for j in jobs:
            title_norm = normalize_text(j.title)
            comp_norm = normalize_text(j.company_name or "")
            prov_norm = normalize_text(j.location_province or "")

            # Rút gọn các từ thừa để tạo chữ ký nhận diện trùng lặp
            title_clean = re.sub(r"(tuyen gap|tuyen dung|can tuyen|urgent|hot)\s*", "", title_norm).strip()
            dedup_key = f"{comp_norm}::{title_clean[:40]}::{prov_norm}"

            source_item = {
                "platform": j.source_platform or "Khác",
                "url": j.source_url,
                "posted_at": j.posted_at.isoformat() if j.posted_at else None,
            }

            if dedup_key in seen:
                duplicates_count += 1
                existing = seen[dedup_key]
                # Bổ sung nguồn mới vào danh sách tổng hợp
                if not hasattr(existing, "_consolidated_sources"):
                    existing._consolidated_sources = [
                        {"platform": existing.source_platform or "Khác", "url": existing.source_url, "posted_at": existing.posted_at.isoformat() if existing.posted_at else None}
                    ]
                if source_item not in existing._consolidated_sources:
                    existing._consolidated_sources.append(source_item)
            else:
                j._consolidated_sources = [source_item]
                seen[dedup_key] = j

        return list(seen.values()), duplicates_count

    def _evaluate_hard_constraints(
        self,
        job: Job,
        intent: SearchIntent,
        now: datetime,
        strict_mode: bool,
    ) -> Tuple[bool, str]:
        """
        Đánh giá các ràng buộc cứng:
        - Yêu cầu Remote: Việc làm phải có xác thực làm việc từ xa
        - Yêu cầu Thời gian đăng: 'mới đăng trong 7 ngày' phải kiểm tra posted_at, không phải crawled_at
        - Ràng buộc địa lý khắt khe nếu người dùng chọn chế độ strict
        """
        title_norm = normalize_text(job.title)
        desc_norm = normalize_text(job.description or "")
        loc_norm = normalize_text(f"{job.location_province or ''} {job.location_district or ''} {job.location_full or ''}")

        # 1. Ràng buộc Remote cứng
        if intent.is_remote_required:
            is_remote_confirmed = (
                job.job_type in ["remote", "Làm việc từ xa"] or
                "remote" in title_norm or
                "lam viec tu xa" in title_norm or
                "lam tai nha" in desc_norm or
                "remote 100%" in desc_norm
            )
            if not is_remote_confirmed:
                return False, "hard_remote: Vị trí không xác thực làm việc từ xa"

        # 2. Ràng buộc thời gian đăng bài (Tuổi bài viết dựa trên original posted_at)
        if intent.max_posting_age_days:
            posted = job.posted_at
            if not posted:
                # Nếu không có posted_at, kiểm tra crawled_at nhưng phạt độ tin cậy
                posted = job.crawled_at

            if posted:
                p_dt = posted if posted.tzinfo else posted.replace(tzinfo=timezone.utc)
                age_days = (now - p_dt).total_seconds() / 86400.0
                if age_days > intent.max_posting_age_days:
                    return False, f"hard_posting_age: Đăng cách đây {round(age_days, 1)} ngày (vượt quá {intent.max_posting_age_days} ngày)"

        # 3. Ràng buộc địa lý (trong chế độ Strict hoặc khi người dùng chỉ định địa phương)
        if intent.target_province and not intent.is_remote_required and strict_mode:
            prov_matched = False
            for alias in intent.location_aliases:
                norm_alias = normalize_text(alias)
                if norm_alias and (norm_alias in loc_norm or norm_alias in title_norm):
                    prov_matched = True
                    break
            if not prov_matched:
                return False, f"hard_location: Không thuộc khu vực {intent.target_province}"

        return True, "passed"

    def _score_job_intent_fit(
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

        # Tính tổng điểm
        total = sum(criteria_scores.values())

        # Bảo vệ độ chuẩn xác (Strict relevance gate):
        if criteria_scores["role_score"] <= 0 and criteria_scores["skill_score"] <= 0 and criteria_scores["responsibility_score"] < 15.0:
            total = 0.0

        return {
            "total_score": max(0.0, total),
            "reasons": reasons,
            "criteria_scores": criteria_scores,
        }


hybrid_search_engine = HybridSearchEngine()
