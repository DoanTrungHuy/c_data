"""
Multi-Signal Ranking Engine for C_Data Platform.
Hệ thống Xếp Hạng Đa Tín Hiệu & Giải Thích Độ Phù Hợp Tuyển Dụng

Thứ tự ưu tiên tín hiệu:
1. Thỏa mãn các điều kiện cứng (Gate 0)
2. Mức độ liên quan về chức danh, kỹ năng và mô tả (0 - 40 điểm)
3. Độ tin cậy của nguồn tuyển dụng (0 - 15 điểm)
4. Tình trạng tuyển dụng được xác minh (0 - 15 điểm)
5. Độ mới của bài đăng gốc dựa trên posted_at (0 - 10 điểm)
6. Độ đầy đủ của dữ liệu và URL ứng tuyển trực tiếp (0 - 10 điểm)
7. Mức độ khớp địa điểm và hình thức làm việc (0 - 10 điểm)

Nguyên tắc bắt buộc:
- Không xếp tin lên cao chỉ vì nguồn crawl được nhiều dữ liệu (Source Volume Neutrality).
- Không xếp tin lên cao chỉ vì trang được crawl gần đây (crawled_at != posted_at).
- Không để việc thiếu dữ liệu lương tự động làm điểm thấp quá mức nếu người dùng không yêu cầu lương (Salary Neutrality).
- Cung cấp cấu trúc ranking_breakdown và cơ chế so sánh ranking debug có thể giải thích.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from app.models.job import Job
from app.services.search_intent_parser import SearchIntent, normalize_text

logger = logging.getLogger("c_data.ranking_engine")


# Bản đồ thẩm quyền và độ tin cậy của nguồn (Source Authority Mapping)
# Điểm chỉ dựa trên thẩm quyền của loại nguồn, TUYỆT ĐỐI không phụ thuộc vào số lượng tin cào được
SOURCE_TRUST_MAP = {
    # Tier 1: Cổng thông tin chính thức của Doanh nghiệp (Enterprise Direct Portal)
    "enterprise_direct": 15.0,
    "sun_group": 15.0,
    "vinpearl": 15.0,
    "tkv_mining": 15.0,
    "fpt_telecom": 15.0,
    "viettel": 15.0,
    "vnpt": 15.0,
    
    # Tier 2: Sàn việc làm uy tín đã được kiểm duyệt (Major Accredited Job Boards)
    "major_job_board": 12.0,
    "careerviet": 12.0,
    "topcv": 12.0,
    "vietnamworks": 12.0,
    "itviec": 12.0,
    
    # Tier 2.5: Kênh API đối tác & RSS Syndication chính thống
    "partner_api": 10.0,
    "rss_feed": 10.0,
    "quangninh_work_rss": 10.0,
    "partner_portal_api": 10.0,
    
    # Tier 3: Cổng thông tin chuyên ngành / địa phương
    "specialized_local": 8.0,
    "local_portal": 8.0,
    
    # Tier 4: Kênh mạng xã hội / hội nhóm tuyển dụng công khai
    "community_social": 4.0,
    "facebook_community": 4.0,
    "threads_community": 4.0,
    "tiktok_community": 4.0,
}


@dataclass
class JobScoreBreakdown:
    total_score: float
    semantic_relevance: float
    source_trust: float
    verification_status: float
    posting_freshness: float
    data_completeness: float
    location_workplace: float
    penalties: float
    signals: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score": round(self.total_score, 1),
            "signals": self.signals,
            "penalties": round(self.penalties, 1),
            "reasons": self.reasons,
        }


class MultiSignalRankingEngine:
    """
    Hệ thống chấm điểm và xếp hạng đa tín hiệu có thể giải thích (Explainable Multi-Signal Scorer)
    """

    def score_job(
        self,
        job: Job,
        intent: SearchIntent,
        now: Optional[datetime] = None,
    ) -> JobScoreBreakdown:
        if now is None:
            now = datetime.now(timezone.utc)

        reasons: List[str] = []
        signals: Dict[str, Any] = {}

        # ---------------------------------------------------------------------
        # TÍN HIỆU 1: MỨC ĐỘ LIÊN QUAN CHỨC DANH, KỸ NĂNG & MÔ TẢ (Max 40 điểm)
        # ---------------------------------------------------------------------
        rel_score, rel_detail, rel_reasons = self._calculate_semantic_relevance(job, intent)
        signals["semantic_relevance"] = {
            "score": round(rel_score, 1),
            "max": 40.0,
            "weight_pct": 40,
            "details": rel_detail,
        }
        reasons.extend(rel_reasons)

        # ---------------------------------------------------------------------
        # TÍN HIỆU 2: ĐỘ TIN CẬY CỦA NGUỒN (Max 15 điểm)
        # Không cộng điểm theo số lượng tin cào được (Volume Neutrality)
        # ---------------------------------------------------------------------
        src_score, src_detail, src_reasons = self._calculate_source_trust(job)
        signals["source_trust"] = {
            "score": round(src_score, 1),
            "max": 15.0,
            "weight_pct": 15,
            "details": src_detail,
        }
        reasons.extend(src_reasons)

        # ---------------------------------------------------------------------
        # TÍN HIỆU 3: TÌNH TRẠNG TUYỂN DỤNG ĐƯỢC XÁC MINH (Max 15 điểm)
        # ---------------------------------------------------------------------
        ver_score, ver_detail, ver_reasons = self._calculate_verification_status(job)
        signals["verification_status"] = {
            "score": round(ver_score, 1),
            "max": 15.0,
            "weight_pct": 15,
            "details": ver_detail,
        }
        reasons.extend(ver_reasons)

        # ---------------------------------------------------------------------
        # TÍN HIỆU 4: ĐỘ MỚI CỦA BÀI ĐĂNG GỐC (POSTED_AT) (Max 10 điểm)
        # Tuyệt đối không dùng crawled_at để gian lận độ tươi mới
        # ---------------------------------------------------------------------
        fresh_score, fresh_detail, fresh_reasons = self._calculate_posting_freshness(job, now)
        signals["posting_freshness"] = {
            "score": round(fresh_score, 1),
            "max": 10.0,
            "weight_pct": 10,
            "details": fresh_detail,
        }
        reasons.extend(fresh_reasons)

        # ---------------------------------------------------------------------
        # TÍN HIỆU 5: ĐỘ ĐẦY ĐỦ DỮ LIỆU & URL ỨNG TUYỂN (Max 10 điểm)
        # Quy tắc: Thiếu lương KHÔNG bị trừ điểm nếu người dùng không yêu cầu lương
        # ---------------------------------------------------------------------
        comp_score, comp_detail, comp_reasons = self._calculate_data_completeness(job, intent)
        signals["data_completeness"] = {
            "score": round(comp_score, 1),
            "max": 10.0,
            "weight_pct": 10,
            "details": comp_detail,
        }
        reasons.extend(comp_reasons)

        # ---------------------------------------------------------------------
        # TÍN HIỆU 6: MỨC ĐỘ KHỚP ĐỊA ĐIỂM & HÌNH THỨC LÀM VIỆC (Max 10 điểm)
        # ---------------------------------------------------------------------
        loc_score, loc_detail, loc_reasons = self._calculate_location_workplace(job, intent)
        signals["location_workplace"] = {
            "score": round(loc_score, 1),
            "max": 10.0,
            "weight_pct": 10,
            "details": loc_detail,
        }
        reasons.extend(loc_reasons)

        # ---------------------------------------------------------------------
        # TÍNH ĐIỂM PHẠT (Penalties trong chế độ mềm)
        # ---------------------------------------------------------------------
        penalty_score, penalty_reasons = self._calculate_penalties(job, intent)
        if penalty_score < 0:
            signals["penalties"] = {
                "score": round(penalty_score, 1),
                "reasons": penalty_reasons,
            }
            reasons.extend(penalty_reasons)

        # ---------------------------------------------------------------------
        # TỔNG HỢP ĐIỂM VÀ BẢO VỆ ĐỘ LIÊN QUAN (Relevance Gate)
        # ---------------------------------------------------------------------
        raw_total = (
            rel_score +
            src_score +
            ver_score +
            fresh_score +
            comp_score +
            loc_score +
            penalty_score
        )

        # Bảo vệ độ liên quan: nếu người dùng có nhập từ khóa tìm kiếm nhưng không có bất kỳ tín hiệu nghề nghiệp/kỹ năng/công ty nào
        # thì điểm tổng bị triệt tiêu về 0 (không để tin spam nguồn uy tín chiếm trang kết quả)
        if (intent.raw_query or intent.primary_role) and rel_score <= 0 and not intent.target_company:
            raw_total = 0.0

        total_score = max(0.0, min(100.0, raw_total))

        return JobScoreBreakdown(
            total_score=total_score,
            semantic_relevance=rel_score,
            source_trust=src_score,
            verification_status=ver_score,
            posting_freshness=fresh_score,
            data_completeness=comp_score,
            location_workplace=loc_score,
            penalties=penalty_score,
            signals=signals,
            reasons=reasons,
        )

    # =========================================================================
    # 1. SEMANTIC RELEVANCE (Max 40 pts)
    # =========================================================================
    def _calculate_semantic_relevance(
        self,
        job: Job,
        intent: SearchIntent,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        title_raw = job.title or ""
        title_norm = normalize_text(title_raw)
        desc_norm = normalize_text(job.description or "")
        req_norm = normalize_text(job.requirements or "")
        full_norm = f"{title_norm} {desc_norm} {req_norm}"

        reasons = []
        details: Dict[str, Any] = {}
        score = 0.0

        # A. Khớp vai trò / chức danh trong tiêu đề (Max 25 điểm)
        title_score = 0.0
        role_matched = False

        norm_q = normalize_text(intent.raw_query)
        q_words = [w for w in norm_q.split() if len(w) >= 2] if norm_q else []
        loc_tokens = set(intent.location_aliases or []) | {"ha", "long", "quang", "ninh", "bai", "chay", "hon", "gai", "hn", "hcm", "noi", "sai", "gon"}
        role_words = [w for w in q_words if w not in loc_tokens]

        # 1. Khớp cụm từ trong ngoặc kép nếu có
        if intent.exact_phrases:
            for phrase in intent.exact_phrases:
                p_norm = normalize_text(phrase)
                if p_norm and p_norm in title_norm:
                    title_score = 25.0
                    reasons.append(f"Tiêu đề chứa cụm từ chính xác: '{phrase}' (+25.0)")
                    role_matched = True
                    break

        # 2. Khớp tuyệt đối hoặc cụm từ tìm kiếm trong tiêu đề (Ưu tiên cao nhất)
        if not role_matched and norm_q:
            if title_norm == norm_q:
                title_score = 25.0
                reasons.append(f"Tiêu đề khớp chính xác tuyệt đối: '{intent.raw_query}' (+25.0)")
                role_matched = True
            elif norm_q in title_norm:
                title_score = 24.0
                reasons.append(f"Tiêu đề chứa nguyên cụm tìm kiếm: '{intent.raw_query}' (+24.0)")
                role_matched = True
            elif len(q_words) > 1 and all(re.search(rf"\b{re.escape(w)}\b", title_norm) for w in q_words):
                title_score = 23.0
                reasons.append(f"Tiêu đề chứa đầy đủ các từ trong: '{intent.raw_query}' (+23.0)")
                role_matched = True
            elif len(role_words) > 1 and all(re.search(rf"\b{re.escape(w)}\b", title_norm) for w in role_words):
                title_score = 23.0
                reasons.append(f"Tiêu đề chứa đầy đủ các từ khóa chuyên môn: '{' '.join(role_words)}' (+23.0)")
                role_matched = True

        # 3. Khớp từ đồng nghĩa vai trò chính xác
        if not role_matched:
            for syn in intent.role_synonyms:
                syn_norm = normalize_text(syn)
                if not syn_norm:
                    continue
                if re.search(rf"\b{re.escape(syn_norm)}\b", title_norm):
                    title_score = 22.0
                    reasons.append(f"Tiêu đề khớp vai trò tương đương: '{syn}' (+22.0)")
                    role_matched = True
                    break
                elif syn_norm in title_norm:
                    title_score = max(title_score, 18.0)
                    reasons.append(f"Tiêu đề chứa từ khóa vai trò: '{syn}' (+18.0)")
                    role_matched = True

        # 4. Token độc lập IT / CNTT
        if not role_matched and intent.primary_role:
            if "IT" in intent.primary_role and re.search(r"\b(it|cntt)\b", title_norm):
                title_score = 20.0
                reasons.append("Tiêu đề chứa định danh chuyên môn IT/CNTT (+20.0)")
                role_matched = True

        # 5. Ngành nghề danh mục
        if not role_matched and intent.primary_role:
            cat_norm = normalize_text(job.category or "")
            if normalize_text(intent.primary_role) in cat_norm or cat_norm in normalize_text(intent.primary_role):
                title_score = 15.0
                reasons.append(f"Danh mục nghề nghiệp phù hợp nhóm: {intent.primary_role} (+15.0)")
                role_matched = True

        # 6. Từ khóa đơn (chỉ khi truy vấn chỉ có 1 từ duy nhất)
        if not role_matched and len(q_words) == 1:
            w = q_words[0]
            if re.search(rf"\b{re.escape(w)}\b", title_norm):
                title_score = 15.0
                reasons.append(f"Tiêu đề khớp từ khóa đơn: '{w}' (+15.0)")
                role_matched = True

        score += title_score
        details["title_match_score"] = round(title_score, 1)

        # B. Khớp kỹ năng chuyên môn (Skill Match - Max 10 điểm)
        skill_score = 0.0
        if intent.required_skills:
            matched_skills = []
            for sk in intent.required_skills:
                sk_norm = normalize_text(sk)
                if re.search(rf"\b{re.escape(sk_norm)}\b", full_norm):
                    matched_skills.append(sk)
            if matched_skills:
                skill_score = min(10.0, len(matched_skills) * 5.0)
                reasons.append(f"Khớp kỹ năng yêu cầu: {', '.join(matched_skills)} (+{round(skill_score, 1)})")
        else:
            # Nếu người dùng không chỉ định kỹ năng, tin có thông tin kỹ năng bài bản được cộng điểm nhẹ
            req_skills = getattr(job, "required_skills", None)
            if req_skills and len(req_skills) >= 1:
                skill_score = 4.0
                reasons.append(f"Tin có mô tả chi tiết {len(req_skills)} kỹ năng chuyên môn (+4.0)")

        score += skill_score
        details["skill_match_score"] = round(skill_score, 1)

        # C. Khớp trách nhiệm thực tế trong mô tả (Max 5 điểm)
        resp_score = 0.0
        if any(w in desc_norm for w in ["ho tro", "sua chua", "cai dat", "he thong", "mang lan", "lap trinh", "phat trien"]):
            resp_score = 5.0
            reasons.append("Nhiệm vụ công việc khớp mô tả thực tế (+5.0)")
        elif len(desc_norm) > 100:
            resp_score = 2.5

        score += resp_score
        details["responsibility_score"] = round(resp_score, 1)

        return min(40.0, score), details, reasons

    # =========================================================================
    # 2. SOURCE AUTHORITY & TRUST (Max 15 pts) - Không phụ thuộc số lượng cào
    # =========================================================================
    def _calculate_source_trust(
        self,
        job: Job,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        reasons = []
        platform_key = normalize_text(job.source_platform or job.source_name or "unknown")
        
        # Nhận diện cấp thẩm quyền của nguồn
        base_score = 6.0
        source_tier = "Tier 3 (Cổng thông tin tuyển dụng)"

        for key, val in SOURCE_TRUST_MAP.items():
            if key in platform_key or platform_key in key:
                base_score = val
                if val >= 14.0:
                    source_tier = "Tier 1 (Cổng thông tin chính thức Doanh nghiệp)"
                elif val >= 11.0:
                    source_tier = "Tier 2 (Sàn việc làm uy tín đã kiểm duyệt)"
                elif val >= 9.0:
                    source_tier = "Tier 2.5 (Nguồn cấp dữ liệu đối tác / RSS chính thức)"
                elif val <= 5.0:
                    source_tier = "Tier 4 (Cộng đồng / Mạng xã hội)"
                break

        # Nhân hệ số độ tin cậy trích xuất (extraction_confidence)
        conf = getattr(job, "extraction_confidence", 1.0) or 1.0
        final_source_score = min(15.0, base_score * conf)

        src_name = job.source_platform or job.source_name or "Hệ thống"
        reasons.append(f"Độ tin cậy nguồn: {source_tier} từ '{src_name}' (+{round(final_source_score, 1)})")

        details = {
            "source_platform": src_name,
            "source_tier": source_tier,
            "base_score": base_score,
            "confidence_multiplier": conf,
            "volume_boost": 0.0,  # Khẳng định 0 điểm dựa trên số lượng cào
        }
        return final_source_score, details, reasons

    # =========================================================================
    # 3. VERIFICATION STATUS (Max 15 pts)
    # =========================================================================
    def _calculate_verification_status(
        self,
        job: Job,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        reasons = []
        status = getattr(job, "status", "unknown") or "unknown"
        evidence = getattr(job, "status_evidence", {}) or {}

        if status == "active_confirmed":
            score = 15.0
            reasons.append("Tình trạng tuyển dụng: Đã xác thực còn tuyển (active_confirmed) (+15.0)")
        elif status == "active_likely":
            score = 10.0
            reasons.append("Tình trạng tuyển dụng: Có hạn nộp hồ sơ hợp lệ từ nguồn uy tín (active_likely) (+10.0)")
        elif status == "unknown":
            score = 3.0
            reasons.append("Tình trạng tuyển dụng: Chưa có hạn nộp hoặc đang chờ xác thực cộng đồng (+3.0)")
        else:  # expired, closed
            score = 0.0
            reasons.append(f"Tình trạng tuyển dụng: Tin {status} (+0.0)")

        details = {
            "status": status,
            "has_evidence": bool(evidence),
            "evidence_reference": getattr(job, "raw_data_reference", None),
        }
        return score, details, reasons

    # =========================================================================
    # 4. POSTING FRESHNESS (Max 10 pts) - Dựa trên posted_at, không dùng crawled_at
    # =========================================================================
    def _calculate_posting_freshness(
        self,
        job: Job,
        now: datetime,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        reasons = []
        posted = job.posted_at

        # BẢO VỆ CHỐNG GIAN LẬN: Tuyệt đối không dùng crawled_at để tính độ mới bài đăng
        if not posted:
            details = {
                "posted_at": None,
                "crawled_at": str(job.crawled_at) if job.crawled_at else None,
                "freshness_reason": "Thiếu ngày đăng gốc (posted_at), không tính điểm độ tươi mới",
            }
            reasons.append("Thiếu ngày đăng gốc (posted_at): 0 điểm độ tươi mới (không dùng thời gian crawl để gian lận độ mới)")
            return 0.0, details, reasons

        p_utc = posted if posted.tzinfo else posted.replace(tzinfo=timezone.utc)
        diff_hours = (now - p_utc).total_seconds() / 3600.0
        age_days = diff_hours / 24.0

        if diff_hours <= 24:
            score = 10.0
            reasons.append(f"Tin đăng rất mới (trong 24h qua: {int(diff_hours)}h trước) (+10.0)")
        elif age_days <= 3.0:
            score = 8.0
            reasons.append(f"Tin đăng cách đây {round(age_days, 1)} ngày (+8.0)")
        elif age_days <= 7.0:
            score = 6.0
            reasons.append(f"Tin đăng trong tuần ({int(age_days)} ngày trước) (+6.0)")
        elif age_days <= 14.0:
            score = 4.0
            reasons.append(f"Tin đăng trong 2 tuần qua ({int(age_days)} ngày trước) (+4.0)")
        elif age_days <= 30.0:
            score = 2.0
            reasons.append(f"Tin đăng trong tháng ({int(age_days)} ngày trước) (+2.0)")
        else:
            score = 0.0
            reasons.append(f"Tin đăng trên 30 ngày ({int(age_days)} ngày trước) (+0.0)")

        details = {
            "posted_at": str(p_utc),
            "age_days": round(age_days, 1),
            "age_hours": round(diff_hours, 1),
        }
        return score, details, reasons

    # =========================================================================
    # 5. DATA COMPLETENESS & APPLY URL (Max 10 pts) - Salary Neutrality
    # =========================================================================
    def _calculate_data_completeness(
        self,
        job: Job,
        intent: SearchIntent,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        reasons = []
        score = 0.0
        details: Dict[str, Any] = {}

        # A. Có URL ứng tuyển trực tiếp hoặc liên kết bài đăng gốc hợp lệ (Max 5 điểm)
        apply_url = job.apply_url or job.source_url
        if apply_url and apply_url.startswith("http"):
            score += 5.0
            reasons.append("Có liên kết ứng tuyển / nguồn tin trực tiếp (+5.0)")
            details["has_apply_url"] = True
        else:
            details["has_apply_url"] = False

        # B. Độ đầy đủ của mô tả & yêu cầu tuyển dụng (Max 3 điểm)
        desc_len = len(job.description or "")
        req_len = len(job.requirements or "")
        if desc_len >= 150 and req_len >= 50:
            score += 3.0
            reasons.append("Mô tả công việc và yêu cầu tuyển dụng chi tiết, rõ ràng (+3.0)")
            details["content_quality"] = "high"
        elif desc_len >= 50:
            score += 1.5
            details["content_quality"] = "medium"
        else:
            details["content_quality"] = "low"

        # C. Có cấu trúc địa chỉ chi tiết (Max 2 điểm)
        if job.location_province and (job.location_district or job.location_full):
            score += 2.0
            details["structured_location"] = True
        else:
            details["structured_location"] = False

        # D. NGUYÊN TẮC TRUNG TÍNH VỚI MỨC LƯƠNG (Salary Neutrality)
        # Nếu người dùng KHÔNG yêu cầu lương: tin không có lương không bị trừ điểm
        if intent.min_salary is None:
            details["salary_evaluation"] = "neutral (user did not specify salary)"
        else:
            # Người dùng có yêu cầu mức lương cụ thể
            has_salary_info = bool(job.salary_min or job.salary_max)
            if has_salary_info:
                effective_sal = job.salary_max or job.salary_min or 0
                if effective_sal >= intent.min_salary:
                    score += 2.0
                    reasons.append(f"Mức lương đáp ứng kỳ vọng ({effective_sal:,} VNĐ >= {intent.min_salary:,} VNĐ) (+2.0)")
                    details["salary_evaluation"] = "matched"
                else:
                    score -= 4.0
                    reasons.append(f"Mức lương thấp hơn kỳ vọng ({effective_sal:,} VNĐ < {intent.min_salary:,} VNĐ) (-4.0)")
                    details["salary_evaluation"] = "below_expectation"
            else:
                # Không có dữ liệu lương khi người dùng yêu cầu: đối xử trung tính nhẹ (0 điểm), không phạt nặng
                details["salary_evaluation"] = "undisclosed (neutral)"

        return min(10.0, max(0.0, score)), details, reasons

    # =========================================================================
    # 6. LOCATION & WORKPLACE FIT (Max 10 pts)
    # =========================================================================
    def _calculate_location_workplace(
        self,
        job: Job,
        intent: SearchIntent,
    ) -> Tuple[float, Dict[str, Any], List[str]]:
        reasons = []
        score = 0.0
        details: Dict[str, Any] = {}

        loc_norm = normalize_text(f"{job.location_province or ''} {job.location_district or ''} {job.location_full or ''}")

        # A. Khớp địa điểm (Max 6 điểm)
        if intent.target_province:
            # Khớp quận/huyện cụ thể (Hạ Long, Bãi Cháy...)
            if intent.target_district and (
                normalize_text(intent.target_district) in loc_norm or
                any(normalize_text(a) in loc_norm for a in ["bai chay", "hon gai", "tuan chau", "ha long"])
            ):
                score += 6.0
                reasons.append(f"Địa điểm đúng trọng điểm {intent.target_district} (+6.0)")
                details["district_match"] = True
            elif normalize_text(intent.target_province) in loc_norm:
                score += 4.5
                reasons.append(f"Địa điểm tại tỉnh {intent.target_province} (+4.5)")
                details["province_match"] = True
            elif any(normalize_text(a) in loc_norm for a in intent.location_aliases):
                score += 3.5
                reasons.append(f"Địa điểm trong khu vực lân cận {intent.target_province} (+3.5)")
                details["alias_match"] = True
        else:
            score += 3.0
            details["location"] = "generic"

        # B. Khớp hình thức làm việc (Max 4 điểm)
        wp_type = getattr(job, "workplace_type", "unknown") or "unknown"
        if intent.is_remote_required or intent.workplace_type == "remote":
            if wp_type == "remote" or job.job_type in ["remote", "Làm việc từ xa"]:
                score += 4.0
                reasons.append("Đúng hình thức làm việc từ xa Remote (+4.0)")
        elif intent.workplace_type == "hybrid":
            if wp_type == "hybrid" or "hybrid" in loc_norm:
                score += 4.0
                reasons.append("Đúng hình thức làm việc kết hợp Hybrid (+4.0)")
        elif intent.is_office_preferred or intent.workplace_type == "onsite":
            if wp_type == "onsite" or "van phong" in normalize_text(job.description or ""):
                score += 4.0
                reasons.append("Môi trường làm việc văn phòng / cố định (+4.0)")
            else:
                score += 2.0
        else:
            score += 2.0

        details["workplace_type"] = wp_type
        return min(10.0, score), details, reasons

    # =========================================================================
    # 7. PENALTIES (Negative scores in soft mode)
    # =========================================================================
    def _calculate_penalties(
        self,
        job: Job,
        intent: SearchIntent,
    ) -> Tuple[float, List[str]]:
        penalty = 0.0
        reasons = []
        full_norm = normalize_text(f"{job.title} {job.description} {job.requirements}")

        # Phạt tin đã hết hạn hoặc đóng tuyển dụng
        if getattr(job, "status", "") in ["expired", "closed"]:
            penalty -= 30.0
            reasons.append(f"Phạt nặng: Tin tuyển dụng đã {job.status} (-30.0)")

        # Phạt mức lương thấp hơn yêu cầu khi người dùng có chỉ định lương tối thiểu
        if intent.min_salary:
            eff_sal = job.salary_max or job.salary_min or 0
            if eff_sal > 0 and eff_sal < intent.min_salary:
                penalty -= 10.0
                reasons.append(f"Phạt: Mức lương ({eff_sal:,} VNĐ) thấp hơn yêu cầu tối thiểu ({intent.min_salary:,} VNĐ) (-10.0)")

        # Phạt vi phạm điều kiện loại trừ mềm (Negative Constraints)
        if intent.field_work_preference == "avoid_heights":
            if any(w in full_norm for w in ["tren cao", "leo cot", "keo cap ngoai troi"]):
                penalty -= 25.0
                reasons.append("Phạt: Công việc có yêu cầu làm việc ngoài trời / leo cột (Trái sở thích) (-25.0)")

        if intent.travel_preference == "avoid_travel":
            if any(w in full_norm for w in ["di cong tac", "cong tac xa", "di tinh"]):
                penalty -= 20.0
                reasons.append("Phạt: Công việc có yêu cầu đi công tác thường xuyên (-20.0)")

        # Phạt cấp bậc kinh nghiệm lệch lớn (Senior khi tìm Fresher)
        if intent.seniority in ["fresher", "junior"]:
            is_senior = any(w in normalize_text(job.title) for w in ["senior", "lead", "truong nhom", "truong phong", "giam doc"])
            if is_senior or getattr(job, "experience_level", "") in ["senior", "lead"]:
                penalty -= 20.0
                reasons.append("Phạt: Chức danh Senior/Lead không phù hợp người mới (-20.0)")

        return penalty, reasons

    # =========================================================================
    # RANKING UTILITY & PAIRWISE COMPARISON (DEBUG RANKING INSPECTOR)
    # =========================================================================
    def rank_jobs(
        self,
        jobs: List[Job],
        intent: SearchIntent,
        sort_by: str = "relevance",
    ) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        scored_jobs = []

        for j in jobs:
            breakdown = self.score_job(j, intent, now)
            scored_jobs.append({
                "job": j,
                "score": breakdown.total_score,
                "breakdown": breakdown.to_dict(),
                "reasons": breakdown.reasons,
                "all_sources": getattr(j, "_consolidated_sources", [
                    {"platform": j.source_platform, "url": j.source_url}
                ]),
            })

        # Sắp xếp theo thứ tự yêu cầu
        if sort_by == "salary_desc":
            scored_jobs.sort(key=lambda x: (x["job"].salary_max or x["job"].salary_min or 0, x["score"]), reverse=True)
        elif sort_by == "salary_asc":
            scored_jobs.sort(key=lambda x: (x["job"].salary_min or x["job"].salary_max or 999999999, -x["score"]))
        elif sort_by == "pure_newest":
            scored_jobs.sort(key=lambda x: (x["job"].posted_at or x["job"].crawled_at or datetime.min.replace(tzinfo=timezone.utc), x["score"]), reverse=True)
        else:  # "relevance"
            scored_jobs.sort(
                key=lambda x: (
                    x["score"],
                    x["job"].posted_at or x["job"].crawled_at or datetime.min.replace(tzinfo=timezone.utc)
                ),
                reverse=True,
            )

        return scored_jobs

    def compare_ranking(
        self,
        job_a: Job,
        job_b: Job,
        intent: SearchIntent,
    ) -> Dict[str, Any]:
        """
        So sánh chi tiết pairwise giữa 2 việc làm để giải thích tại sao Job A xếp trên Job B
        """
        now = datetime.now(timezone.utc)
        score_a = self.score_job(job_a, intent, now)
        score_b = self.score_job(job_b, intent, now)

        winner = "job_a" if score_a.total_score >= score_b.total_score else "job_b"
        diff = abs(score_a.total_score - score_b.total_score)

        comparison_details = []
        signal_keys = [
            ("semantic_relevance", "Mức độ liên quan chức danh & kỹ năng (Max 40đ)"),
            ("source_trust", "Độ tin cậy nguồn tuyển dụng (Max 15đ)"),
            ("verification_status", "Trạng thái xác minh còn tuyển (Max 15đ)"),
            ("posting_freshness", "Độ mới của bài đăng gốc (Max 10đ)"),
            ("data_completeness", "Độ đầy đủ dữ liệu & URL ứng tuyển (Max 10đ)"),
            ("location_workplace", "Khớp địa điểm & hình thức (Max 10đ)"),
        ]

        for k, label in signal_keys:
            val_a = score_a.signals.get(k, {}).get("score", 0.0)
            val_b = score_b.signals.get(k, {}).get("score", 0.0)
            delta = val_a - val_b
            comparison_details.append({
                "signal": k,
                "label": label,
                "job_a_score": val_a,
                "job_b_score": val_b,
                "delta_a_minus_b": round(delta, 1),
                "favor": "job_a" if delta > 0 else ("job_b" if delta < 0 else "tie"),
            })

        summary_reason = (
            f"'{job_a.title}' ({round(score_a.total_score, 1)}đ) xếp trên '{job_b.title}' ({round(score_b.total_score, 1)}đ) "
            f"với cách biệt {round(diff, 1)} điểm do vượt trội về các tín hiệu chính."
            if winner == "job_a" else
            f"'{job_b.title}' ({round(score_b.total_score, 1)}đ) xếp trên '{job_a.title}' ({round(score_a.total_score, 1)}đ) "
            f"với cách biệt {round(diff, 1)} điểm."
        )

        return {
            "winner": winner,
            "point_difference": round(diff, 1),
            "summary_explanation": summary_reason,
            "job_a": {
                "id": str(job_a.id),
                "title": job_a.title,
                "company": job_a.company_name,
                "total_score": round(score_a.total_score, 1),
                "breakdown": score_a.to_dict(),
            },
            "job_b": {
                "id": str(job_b.id),
                "title": job_b.title,
                "company": job_b.company_name,
                "total_score": round(score_b.total_score, 1),
                "breakdown": score_b.to_dict(),
            },
            "signal_comparison": comparison_details,
        }


multi_signal_ranking_engine = MultiSignalRankingEngine()
