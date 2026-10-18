"""
Cross-Source Job Deduplication & Consolidation Engine for C_Data Platform.
Provides multi-signal deduplication, canonical URL sanitization, anti-merge guards,
trust-weighted evidence preservation, and conflict history tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import urllib.parse
import unidecode

logger = logging.getLogger("c_data.deduplication")

# Danh sách tham số tracking tiếp thị cần loại bỏ khỏi canonical URL
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "zanpid", "mc_eid", "_ga", "_gl",
    "ref", "source_ref", "post_ref", "tracking_id", "trk", "campaign_id",
}

# Danh sách tham số điều hướng cốt lõi CẦN GIỮ LẠI để mở đúng tin tuyển dụng
ESSENTIAL_QUERY_PARAMS = {
    "jobid", "job_id", "id", "job_code", "post_id", "v", "c", "city",
    "code", "jid", "nha_tuyen_dung_id",
}

# Bảng xếp hạng độ tin cậy nguồn (Trust Level Hierarchy: 1 = cao nhất, 4 = thấp nhất)
SOURCE_TRUST_HIERARCHY = {
    "enterprise_direct": 1,
    "authorized_api": 1,
    "national_job_board": 2,
    "specialized_local": 3,
    "social_public": 4,
}


def canonicalize_url(url: Optional[str]) -> str:
    """
    Chuẩn hóa URL canonical:
    - Loại bỏ an toàn các tham số tracking tiếp thị (utm_*, fbclid, ref, post_ref...).
    - BẢO TOÀN các query parameters cần thiết để mở đúng tin (jobId, id, v, code...).
    - Chuẩn hóa scheme (lowercase), hostname (lowercase), và bỏ fragment (#...).
    """
    if not url:
        return ""

    url_str = url.strip()
    # Loại bỏ anchor fragment (#...)
    url_str = re.sub(r"#.*$", "", url_str)

    try:
        parsed = urllib.parse.urlsplit(url_str)
        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()

        # Chuẩn hóa path: bỏ trailing slash trừ khi là root
        path = parsed.path
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")

        # Lọc query parameters
        query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        clean_pairs = []
        for k, v in query_pairs:
            k_lower = k.lower()
            # Nếu là tracking param rõ ràng, bỏ qua
            if k_lower in TRACKING_PARAMS:
                continue
            # Nếu param có tiền tố utm_, bỏ qua
            if k_lower.startswith("utm_"):
                continue
            clean_pairs.append((k, v))

        # Tái cấu trúc query string
        clean_query = urllib.parse.urlencode(clean_pairs)
        canonical = urllib.parse.urlunsplit((scheme, netloc, path, clean_query, ""))
        return canonical
    except Exception as e:
        logger.debug(f"Không thể chuẩn hóa URL '{url}': {e}")
        return url_str.strip()


def normalize_company_name(name: Optional[str]) -> str:
    """
    Chuẩn hóa tên công ty để so khớp đa nguồn:
    - Loại bỏ các tiền tố/hậu tố pháp nhân (Công ty Cổ phần, TNHH, Tập đoàn...).
    - Ánh xạ các thương hiệu lớn tại Việt Nam và Quảng Ninh.
    """
    if not name:
        return ""

    raw = unidecode.unidecode(name).lower()

    # Bỏ các tiền tố pháp nhân phổ biến
    noise_prefixes = [
        r"\bcong ty co phan\b", r"\bctcp\b", r"\bcong ty tnhh mtv\b",
        r"\bcong ty tnhh\b", r"\btnhh\b", r"\btap doan\b", r"\bchi nhanh\b",
        r"\bdoanh nghiep\b", r"\btong cong ty\b", r"\bhotel & resort\b",
        r"\bhotels and resorts\b", r"\bcomplex\b",
    ]
    for p in noise_prefixes:
        raw = re.sub(p, "", raw)

    clean = re.sub(r"[^a-z0-9\s]", " ", raw)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Nhận diện thương hiệu trọng điểm
    if "sun world" in clean or "sun group" in clean or "yoko onsen" in clean:
        return "sungroup"
    if "vinpearl" in clean or "vingroup" in clean or "vinmec" in clean:
        return "vingroup"
    if "than deo nai" in clean or "than coc sau" in clean or "than ha long" in clean or "vinacomin" in clean or "tkv" in clean:
        return "tkv_vinacomin"
    if "fpt" in clean:
        return "fpt"
    if "wyndham legend" in clean:
        return "wyndham_halong"
    if "cang container quoc te cai lan" in clean or "cict" in clean:
        return "cict_cailan"
    if "paradise" in clean:
        return "paradise_cruises"
    if "muong thanh" in clean:
        return "muongthanh"
    if "viettel" in clean:
        return "viettel"

    return clean


def normalize_job_title(title: Optional[str]) -> str:
    """
    Chuẩn hóa chức danh công việc:
    - Loại bỏ từ khóa giật tít tuyển dụng: [Tuyển gấp], [Cần tuyển], [Hot], [Lương cao]...
    - Giữ lại danh xưng chuyên môn và cấp bậc.
    """
    if not title:
        return ""

    raw = unidecode.unidecode(title).lower()
    # Loại bỏ ngoặc vuông/ngoặc tròn và từ quảng bá
    raw = re.sub(r"\[.*?\]|\(.*?\)", " ", raw)
    noise_words = [
        r"\btuyen gap\b", r"\bcan tuyen\b", r"\btuyen dung\b", r"\burgent\b",
        r"\bhot\b", r"\bluong cao\b", r"\bdi lam ngay\b", r"\bthu nhap khung\b",
        r"\bbao an o\b", r"\bpart time\b", r"\bfull time\b", r"\bca ngay\b",
        r"\bca dem\b", r"\bnam\s*[/,]\s*nu\b", r"\bnam\s+hoac\s+nu\b",
    ]
    for w in noise_words:
        raw = re.sub(w, "", raw)

    clean = re.sub(r"[^a-z0-9\s]", " ", raw)
    # Standardize equivalent roles (Vietnamese / English)
    clean = re.sub(r"\blap trinh vien\b", "developer", clean)
    clean = re.sub(r"\bky su phan mem\b", "software engineer", clean)
    clean = re.sub(r"\bnhan vien kinh doanh\b", "sales", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def compute_text_similarity(text1: Optional[str], text2: Optional[str]) -> float:
    """
    Tính toán độ tương đồng giữa hai đoạn văn bản dựa trên tập từ vựng (Word Jaccard)
    và N-gram Dice coefficient.
    """
    if not text1 or not text2:
        return 0.0

    t1 = unidecode.unidecode(text1).lower()
    t2 = unidecode.unidecode(text2).lower()

    words1 = set(re.findall(r"\b[a-z0-9]{2,}\b", t1))
    words2 = set(re.findall(r"\b[a-z0-9]{2,}\b", t2))

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)
    jaccard = len(intersection) / len(union) if union else 0.0

    # Trigram similarity để hỗ trợ sai khác nhỏ về cách viết
    def get_trigrams(s: str) -> Set[str]:
        return {s[i:i+3] for i in range(len(s) - 2)}

    tri1 = get_trigrams(t1[:500])
    tri2 = get_trigrams(t2[:500])
    dice = (2.0 * len(tri1.intersection(tri2))) / (len(tri1) + len(tri2)) if (tri1 and tri2) else 0.0

    return round(0.6 * jaccard + 0.4 * dice, 3)


class JobDeduplicationEngine:
    """
    Hệ thống phát hiện trùng lặp và hợp nhất tin tuyển dụng đa nguồn.
    """

    def are_jobs_duplicate(self, job_a: Any, job_b: Any) -> Tuple[bool, str, float]:
        """
        Đánh giá xem 2 tin tuyển dụng có phải là bản trùng lặp hay không.
        Trả về: (is_duplicate: bool, match_reason: str, confidence_score: float)
        """
        # 1. TÍN HIỆU CẤP 1: TRÙNG KHỚP TUYỆT ĐỐI THEO ID HOẶC CANONICAL URL (100% TIN CẬY)
        url_a = canonicalize_url(getattr(job_a, "source_url", None) or getattr(job_a, "apply_url", None))
        url_b = canonicalize_url(getattr(job_b, "source_url", None) or getattr(job_b, "apply_url", None))

        if url_a and url_b and url_a == url_b:
            return True, "exact_canonical_url", 1.0

        src_name_a = getattr(job_a, "source_name", None) or getattr(job_a, "source_platform", None)
        src_name_b = getattr(job_b, "source_name", None) or getattr(job_b, "source_platform", None)
        src_id_a = getattr(job_a, "source_job_id", None)
        src_id_b = getattr(job_b, "source_job_id", None)

        if src_name_a and src_name_b and src_name_a == src_name_b and src_id_a and src_id_b:
            if str(src_id_a).strip() == str(src_id_b).strip():
                return True, "exact_source_job_id", 1.0

        # 2. TÍN HIỆU CẤP 2: CÙNG CÔNG TY + CÙNG TIÊU ĐỀ + CÙNG ĐỊA BÀN
        comp_a = normalize_company_name(getattr(job_a, "company_name", ""))
        comp_b = normalize_company_name(getattr(job_b, "company_name", ""))

        # Nếu không cùng công ty (và không rỗng), không gộp
        if comp_a and comp_b and comp_a != comp_b:
            return False, "different_company", 0.0

        title_a = normalize_job_title(getattr(job_a, "title", ""))
        title_b = normalize_job_title(getattr(job_b, "title", ""))

        prov_a = (getattr(job_a, "location_province", "") or "").lower().strip()
        prov_b = (getattr(job_b, "location_province", "") or "").lower().strip()
        dist_a = (getattr(job_a, "location_district", "") or "").lower().strip()
        dist_b = (getattr(job_b, "location_district", "") or "").lower().strip()

        # BỘ LỌC CHỐNG GỘP SAI (ANTI-MERGE GUARDS):
        # "Không chỉ dựa vào cùng tiêu đề để gộp vì một công ty có thể đăng nhiều vị trí giống nhau"
        
        # Guard 1: Khác biệt tỉnh thành rõ rệt
        if prov_a and prov_b and prov_a != prov_b and "toàn quốc" not in [prov_a, prov_b]:
            return False, "anti_merge_different_province", 0.0

        # Guard 2: Cùng công ty và cùng tiêu đề nhưng khác biệt chi nhánh / quận huyện rõ ràng
        # Ví dụ: Mường Thanh tuyển Lễ tân Bãi Cháy vs Lễ tân Hòn Gai hoặc FPT tuyển Hạ Long vs Cẩm Phả
        def _clean_dist(d: str) -> str:
            d_norm = unidecode.unidecode(d).lower()
            d_clean = re.sub(r"\b(quan|huyen|thi xa|tx|tp|thanh pho|phuong|xa)\b", " ", d_norm)
            d_clean = re.sub(r"[^a-z0-9\s]", " ", d_clean)
            return re.sub(r"\s+", " ", d_clean).strip()

        cdist_a = _clean_dist(dist_a)
        cdist_b = _clean_dist(dist_b)
        if cdist_a and cdist_b and cdist_a != cdist_b and cdist_a not in cdist_b and cdist_b not in cdist_a:
            # Kiểm tra xem mô tả có nói về 2 chi nhánh khác nhau không
            desc_sim = compute_text_similarity(
                getattr(job_a, "description", ""),
                getattr(job_b, "description", "")
            )
            # Nếu khác quận huyện và mô tả không trùng khớp cao, giữ độc lập
            if desc_sim < 0.80:
                return False, f"anti_merge_different_district_{cdist_a}_vs_{cdist_b}", 0.0

        # Guard 3: Khác biệt quá lớn về mức lương (ví dụ: Fresher 7tr vs Lead 30tr dù cùng chức danh kỹ thuật)
        min_a = getattr(job_a, "salary_min", None)
        min_b = getattr(job_b, "salary_min", None)
        if min_a and min_b and min_a > 0 and min_b > 0:
            ratio = max(min_a, min_b) / min(min_a, min_b)
            if ratio >= 2.5:
                return False, "anti_merge_salary_disparity", 0.0

        # Guard 4: Cùng tiêu đề nhưng nội dung mô tả hoàn toàn khác biệt (< 0.30)
        desc_a = getattr(job_a, "description", "") or ""
        desc_b = getattr(job_b, "description", "") or ""
        if len(desc_a) > 50 and len(desc_b) > 50:
            sim = compute_text_similarity(desc_a, desc_b)
            if sim < 0.25 and title_a != title_b:
                return False, f"anti_merge_dissimilar_content_{sim}", 0.0

        # XÁC NHẬN TRÙNG LẶP NẾU TIÊU ĐỀ VÀ CÔNG TY KHỚP NHAU
        if comp_a and comp_b and comp_a == comp_b:
            title_sim = compute_text_similarity(title_a, title_b)
            if title_a and title_b and (title_a == title_b or title_a in title_b or title_b in title_a or title_sim >= 0.50):
                return True, f"same_company_and_title_{title_sim}", max(0.85, title_sim)

        # 3. TÍN HIỆU CẤP 3: BÀI ĐĂNG LẠI (CROSS-SOURCE REPOST) CÓ TƯƠNG ĐỒNG NỘI DUNG CAO
        if len(desc_a) > 80 and len(desc_b) > 80:
            sim = compute_text_similarity(desc_a, desc_b)
            if sim >= 0.70:
                return True, f"high_content_similarity_{sim}", sim

        return False, "no_match", 0.0

    def consolidate_jobs(self, jobs: List[Any]) -> Tuple[List[Any], int]:
        """
        Hợp nhất danh sách việc làm đa nguồn:
        - Giữ lại đầy đủ nguồn gốc của từng bản ghi (`consolidated_sources`).
        - Bảo toàn URL ứng tuyển tốt nhất có bằng chứng xác thực (`best_apply_url`).
        - Bảo toàn ngày đăng của từng nguồn và cập nhật `last_seen_at`.
        - Bảo toàn bằng chứng tin cậy cao nhất, không để bản sao kém tin cậy ghi đè.
        - Ghi nhận lịch sử khi có xung đột trạng thái (`status_conflict_history`).
        """
        if not jobs:
            return [], 0

        consolidated: List[Any] = []
        duplicates_count = 0

        for current_job in jobs:
            matched_target = None
            match_reason = ""
            match_score = 0.0

            # So khớp với danh sách đã hợp nhất
            for existing in consolidated:
                is_dup, reason, score = self.are_jobs_duplicate(existing, current_job)
                if is_dup:
                    matched_target = existing
                    match_reason = reason
                    match_score = score
                    break

            if matched_target:
                duplicates_count += 1
                self._merge_job_records(matched_target, current_job, match_reason, match_score)
            else:
                self._initialize_consolidated_metadata(current_job)
                consolidated.append(current_job)

        return consolidated, duplicates_count

    def _initialize_consolidated_metadata(self, job: Any) -> None:
        """Khởi tạo cấu trúc metadata hợp nhất cho bản ghi mới"""
        src_platform = getattr(job, "source_platform", None) or getattr(job, "source_name", "Khác")
        src_url = getattr(job, "source_url", "")
        clean_url = canonicalize_url(src_url)
        posted_at = getattr(job, "posted_at", None)
        crawled_at = getattr(job, "crawled_at", None) or datetime.now(timezone.utc)
        status_val = getattr(job, "status", "active_likely")

        source_entry = {
            "platform": src_platform,
            "url": src_url,
            "source_name": src_platform,
            "source_url": src_url,
            "canonical_url": clean_url,
            "posted_at": posted_at.isoformat() if posted_at else None,
            "first_seen_at": (getattr(job, "first_seen_at", None) or crawled_at).isoformat(),
            "last_seen_at": (getattr(job, "last_seen_at", None) or crawled_at).isoformat(),
            "status": status_val,
            "status_evidence": getattr(job, "status_evidence", None),
            "confidence": getattr(job, "extraction_confidence", 0.8),
        }

        # Lưu danh sách nguồn đã hợp nhất
        setattr(job, "_consolidated_sources", [source_entry])
        setattr(job, "_posted_at_by_source", {src_platform: posted_at.isoformat() if posted_at else None})
        setattr(job, "_all_valid_source_urls", [clean_url] if clean_url else [])
        setattr(job, "_best_apply_url", getattr(job, "apply_url", None) or src_url)
        setattr(job, "_status_conflict_history", [])

    def _merge_job_records(self, primary: Any, secondary: Any, reason: str, score: float) -> None:
        """
        Hợp nhất bản ghi `secondary` vào bản ghi `primary`.
        Quy tắc:
        - Không để bản sao mới hơn nhưng kém tin cậy ghi đè mất bằng chứng tốt hơn.
        - Cập nhật last_seen_at = max(primary, secondary).
        - Gia hạn deadline_at = max(primary, secondary) nếu bài đăng mới có hạn xa hơn.
        - Bảo toàn URL ứng tuyển tốt nhất có bằng chứng.
        - Ghi vết xung đột trạng thái nếu một bên báo expired/closed mà bên kia active.
        """
        now = datetime.now(timezone.utc)

        # 1. Trích xuất metadata nguồn của secondary
        sec_platform = getattr(secondary, "source_platform", None) or getattr(secondary, "source_name", "Khác")
        sec_url = getattr(secondary, "source_url", "")
        sec_clean_url = canonicalize_url(sec_url)
        sec_posted_at = getattr(secondary, "posted_at", None)
        sec_seen_at = getattr(secondary, "last_seen_at", None) or getattr(secondary, "crawled_at", None) or now
        sec_status = getattr(secondary, "status", "active_likely")
        sec_evidence = getattr(secondary, "status_evidence", None)
        sec_confidence = getattr(secondary, "extraction_confidence", 0.75)

        sec_entry = {
            "platform": sec_platform,
            "url": sec_url,
            "source_name": sec_platform,
            "source_url": sec_url,
            "canonical_url": sec_clean_url,
            "posted_at": sec_posted_at.isoformat() if sec_posted_at else None,
            "first_seen_at": (getattr(secondary, "first_seen_at", None) or now).isoformat(),
            "last_seen_at": sec_seen_at.isoformat() if hasattr(sec_seen_at, "isoformat") else str(sec_seen_at),
            "status": sec_status,
            "status_evidence": sec_evidence,
            "confidence": sec_confidence,
            "merged_reason": reason,
        }

        # 2. Hợp nhất danh sách nguồn
        if not hasattr(primary, "_consolidated_sources"):
            self._initialize_consolidated_metadata(primary)

        # Tránh trùng lặp trong consolidated_sources
        existing_urls = {s.get("canonical_url") for s in primary._consolidated_sources if s.get("canonical_url")}
        if sec_clean_url and sec_clean_url not in existing_urls:
            primary._consolidated_sources.append(sec_entry)
            primary._all_valid_source_urls.append(sec_clean_url)

        # Lưu ngày đăng theo nguồn
        if hasattr(primary, "_posted_at_by_source"):
            primary._posted_at_by_source[sec_platform] = sec_posted_at.isoformat() if sec_posted_at else None

        # 3. Cập nhật mốc thời gian nhìn thấy gần nhất (last_seen_at)
        pri_seen_at = getattr(primary, "last_seen_at", None) or now
        if hasattr(sec_seen_at, "tzinfo") and hasattr(pri_seen_at, "tzinfo"):
            primary.last_seen_at = max(pri_seen_at, sec_seen_at)

        # 4. Cập nhật hạn nộp hồ sơ (Deadline / Expires At) khi có tin gia hạn
        pri_exp = getattr(primary, "deadline_at", None) or getattr(primary, "expires_at", None)
        sec_exp = getattr(secondary, "deadline_at", None) or getattr(secondary, "expires_at", None)
        if sec_exp:
            if not pri_exp or sec_exp > pri_exp:
                primary.deadline_at = sec_exp
                primary.expires_at = sec_exp
                # Cập nhật bằng chứng gia hạn
                primary.status_reason = f"Được gia hạn hạn nộp hồ sơ tới {sec_exp.strftime('%d/%m/%Y')}"

        # 5. Đánh giá cấp độ tin cậy để bảo toàn URL ứng tuyển và bằng chứng tốt nhất
        pri_trust = self._get_trust_level(primary)
        sec_trust = self._get_trust_level(secondary)

        # Nếu secondary có độ tin cậy cao hơn (số nhỏ hơn), nâng cấp thông tin cốt lõi
        if sec_trust < pri_trust:
            if getattr(secondary, "apply_url", None):
                primary._best_apply_url = secondary.apply_url
                primary.apply_url = secondary.apply_url
            if getattr(secondary, "status_evidence", None):
                primary.status_evidence = secondary.status_evidence
            if getattr(secondary, "extraction_confidence", 0) > getattr(primary, "extraction_confidence", 0):
                primary.extraction_confidence = secondary.extraction_confidence

        # 6. Ghi nhận mâu thuẫn trạng thái (Status Conflict)
        pri_status = getattr(primary, "status", "active_likely")
        if pri_status != sec_status:
            conflict_entry = {
                "detected_at": now.isoformat(),
                "primary_source": getattr(primary, "source_platform", "Primary"),
                "primary_status": pri_status,
                "secondary_source": sec_platform,
                "secondary_status": sec_status,
                "reason": f"Mâu thuẫn trạng thái khi hợp nhất từ {reason}",
            }
            if not hasattr(primary, "_status_conflict_history"):
                primary._status_conflict_history = []
            primary._status_conflict_history.append(conflict_entry)

            # Quy tắc giải quyết xung đột:
            # Nếu nguồn chính thức đóng bài, chuyển sang closed
            if "closed" in [pri_status, sec_status]:
                primary.status = "closed"
                primary.status_reason = "Đã được ghi nhận đóng tuyển dụng từ nguồn chính thức"
            elif "expired" in [pri_status, sec_status]:
                # Nếu có một bên vừa được gia hạn với deadline tương lai thì vẫn giữ active_likely
                if primary.deadline_at and primary.deadline_at > now:
                    primary.status = "active_likely"
                    primary.status_reason = "Được cập nhật gia hạn hạn tuyển dụng mới"
                else:
                    primary.status = "expired"

    def _get_trust_level(self, job: Any) -> int:
        """Xác định cấp độ tin cậy của tin tuyển dụng dựa trên nguồn"""
        src = (getattr(job, "source_platform", None) or getattr(job, "source_name", "")).lower()
        if any(k in src for k in ["sun group", "vinpearl", "tkv", "fpt", "doanh nghiệp", "corporate"]):
            return SOURCE_TRUST_HIERARCHY["enterprise_direct"]
        if any(k in src for k in ["rss", "chính phủ", "bộ lđ", "quốc gia"]):
            return SOURCE_TRUST_HIERARCHY["authorized_api"]
        if any(k in src for k in ["careerviet", "topcv", "vietnamworks", "careerbuilder"]):
            return SOURCE_TRUST_HIERARCHY["national_job_board"]
        if any(k in src for k in ["quảng ninh", "trung tâm", "kcn"]):
            return SOURCE_TRUST_HIERARCHY["specialized_local"]
        return SOURCE_TRUST_HIERARCHY["social_public"]


# Singleton instance dùng chung
job_deduplication_engine = JobDeduplicationEngine()
