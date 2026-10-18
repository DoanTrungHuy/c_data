"""
Discovery Queue & Search Engine Discovery Coordinator for C_Data Platform (Master Prompt Section 4, 5, 8).
Coordinates automated discovery targets:
- Targeted Search Syntaxes: site:facebook.com, site:linkedin.com/posts, local IT queries
- Persistent Discovery Queue with priority, frequency, and cross-link ingestion
- Anti-Hallucination & Validated direct URL tracking
"""

from datetime import datetime, timedelta, timezone
import hashlib
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import urllib.parse
from pydantic import BaseModel, Field

from app.schemas.universal_job import (
    LocationNormalized,
    UniversalJob,
    VerificationAuditEvidence,
    VerificationStatus,
)
from app.services.job_deduplication_engine import canonicalize_url

logger = logging.getLogger("c_data.discovery_engine")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
QUEUE_FILE_PATH = DATA_DIR / "discovery_queue_state.json"


class DiscoveryTarget(BaseModel):
    """Mục tiêu khám phá trong hàng đợi Discovery Queue"""
    target_id: str = Field(..., description="Mã băm duy nhất của mục tiêu")
    url_or_query: str = Field(..., description="Cú pháp tìm kiếm hoặc URL cần quét")
    target_type: str = Field(..., description="search_syntax, domain_career, social_fanpage, public_group")
    priority: int = Field(default=2, ge=1, le=5, description="1 (ưu tiên cao nhất) đến 5 (thấp)")
    frequency_hours: int = Field(default=12, ge=1, description="Chu kỳ quét định kỳ tính theo giờ")
    last_scanned_at: Optional[str] = Field(None, description="Thời điểm quét gần nhất")
    next_scan_at: Optional[str] = Field(None, description="Thời điểm quét dự kiến tiếp theo")
    discovery_source: str = Field(default="seed", description="seed, cross_link, search_expansion")
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    is_active: bool = Field(default=True)
    notes: Optional[str] = None


class DiscoveryQueueEngine:
    """
    Điều phối Hàng đợi Khám phá (Discovery Queue) và Mở rộng Truy vấn Tìm kiếm
    theo Mục 5 của Master Prompt.
    """

    def __init__(self):
        self._queue: Dict[str, DiscoveryTarget] = {}
        self._initialize_seed_targets()
        self._load_persisted_state()

    def _generate_target_id(self, text: str) -> str:
        return hashlib.md5(text.strip().lower().encode("utf-8")).hexdigest()[:12]

    def _initialize_seed_targets(self) -> None:
        """Khởi tạo danh sách các mục tiêu tìm kiếm có chủ đích theo Master Prompt Mục 4"""
        seeds = [
            # 1. Cú pháp Facebook công khai
            (
                'site:facebook.com "tuyển dụng" "IT" "Hạ Long"',
                "search_syntax",
                1,
                6,
                "Tìm bài đăng tuyển dụng IT tại Hạ Long trên Facebook",
            ),
            (
                'site:facebook.com "tuyển dụng" ("IT Helpdesk" OR "quản trị mạng" OR "kỹ thuật máy tính") "Bãi Cháy"',
                "search_syntax",
                1,
                6,
                "Tìm IT Helpdesk / mạng tại khu vực du lịch Bãi Cháy",
            ),
            # 2. Cú pháp LinkedIn Posts
            (
                'site:linkedin.com/posts "tuyển" "Hạ Long" ("IT" OR "phần mềm" OR "helpdesk")',
                "search_syntax",
                1,
                12,
                "Tìm bài đăng công khai của Recruiter trên LinkedIn Posts",
            ),
            # 3. Cú pháp kỹ thuật & ERP tại Quảng Ninh
            (
                '"tuyển dụng" ("IT Support" OR "kỹ thuật máy tính" OR "lập trình") "Hạ Long" "2026"',
                "search_syntax",
                1,
                12,
                "Tìm bài tuyển dụng IT mới nhất năm 2026 tại Hạ Long",
            ),
            (
                '"tuyển dụng" ("ERP" OR "quản trị hệ thống" OR "SCADA") "Quảng Ninh"',
                "search_syntax",
                2,
                24,
                "Tìm vị trí ERP & SCADA công nghiệp tại Quảng Ninh",
            ),
            (
                'site:*.vn "tuyển dụng" "Hạ Long" "IT"',
                "search_syntax",
                2,
                24,
                "Quét toàn bộ domain .vn có tin tuyển dụng IT tại Hạ Long",
            ),
            # 4. Fanpage & Cổng doanh nghiệp địa phương
            (
                "https://www.facebook.com/TuyendungSunGroupVungDongBac",
                "social_fanpage",
                1,
                6,
                "Fanpage chính thức Tuyển dụng Sun Group Vùng Đông Bắc",
            ),
            (
                "https://www.facebook.com/fpttelecomquangninh",
                "social_fanpage",
                1,
                6,
                "Fanpage FPT Telecom Chi nhánh Quảng Ninh",
            ),
            (
                "https://tuyendung.sungroup.com.vn",
                "domain_career",
                1,
                6,
                "Cổng nghề nghiệp Tập đoàn Sun Group",
            ),
            (
                "https://vinpearl.com/vi/tuyen-dung",
                "domain_career",
                1,
                6,
                "Cổng nghề nghiệp Vinpearl Resort & Spa Hạ Long",
            ),
            (
                "https://vinacomin.vn/thong-tin-tuyen-dung",
                "domain_career",
                2,
                12,
                "Cổng nghề nghiệp Tập đoàn Than - Khoáng sản Việt Nam TKV",
            ),
            (
                "https://cict.com.vn/career",
                "domain_career",
                2,
                12,
                "Cổng tuyển dụng Cảng Quốc tế Cái Lân CICT",
            ),
        ]

        for query_or_url, t_type, prio, freq, note in seeds:
            tid = self._generate_target_id(query_or_url)
            self._queue[tid] = DiscoveryTarget(
                target_id=tid,
                url_or_query=query_or_url,
                target_type=t_type,
                priority=prio,
                frequency_hours=freq,
                discovery_source="seed",
                notes=note,
            )

    def enqueue_target(
        self,
        url_or_query: str,
        target_type: str = "cross_link",
        priority: int = 3,
        frequency_hours: int = 24,
        discovery_source: str = "cross_link",
        notes: Optional[str] = None,
    ) -> str:
        """
        Đưa mục tiêu mới phát hiện (từ liên kết chéo, hashtag, bài đăng) vào hàng đợi.
        Tự động khử trùng lặp qua target_id.
        """
        clean_text = url_or_query.strip()
        tid = self._generate_target_id(clean_text)
        if tid in self._queue:
            logger.debug(f"Mục tiêu {clean_text[:40]} đã tồn tại trong Discovery Queue.")
            return tid

        target = DiscoveryTarget(
            target_id=tid,
            url_or_query=clean_text,
            target_type=target_type,
            priority=priority,
            frequency_hours=frequency_hours,
            discovery_source=discovery_source,
            notes=notes,
        )
        self._queue[tid] = target
        self._save_persisted_state()
        logger.info(f"➕ Đã thêm mục tiêu mới vào Discovery Queue: {clean_text[:60]}")
        return tid

    def list_targets(
        self,
        target_type: Optional[str] = None,
        active_only: bool = True,
    ) -> List[DiscoveryTarget]:
        """Lấy danh sách các mục tiêu trong hàng đợi theo phân loại"""
        results = list(self._queue.values())
        if active_only:
            results = [t for t in results if t.is_active]
        if target_type:
            results = [t for t in results if t.target_type == target_type]
        # Sắp xếp theo ưu tiên tăng dần (1 trước, 5 sau)
        results.sort(key=lambda t: t.priority)
        return results

    def get_pending_targets(self, limit: int = 10) -> List[DiscoveryTarget]:
        """Lấy các mục tiêu đến hạn quét tiếp theo"""
        now = datetime.now(timezone.utc)
        pending: List[DiscoveryTarget] = []
        for t in self._queue.values():
            if not t.is_active:
                continue
            if not t.last_scanned_at:
                pending.append(t)
            else:
                try:
                    last_dt = datetime.fromisoformat(t.last_scanned_at)
                    if (now - last_dt) > timedelta(hours=t.frequency_hours):
                        pending.append(t)
                except Exception:
                    pending.append(t)

        pending.sort(key=lambda x: x.priority)
        return pending[:limit]

    def record_scan_result(self, target_id: str, success: bool, items_found: int = 0) -> None:
        """Ghi nhận kết quả thực thi một mục tiêu khám phá"""
        if target_id not in self._queue:
            return
        now_str = datetime.now(timezone.utc).isoformat()
        t = self._queue[target_id]
        t.last_scanned_at = now_str
        next_dt = datetime.now(timezone.utc) + timedelta(hours=t.frequency_hours)
        t.next_scan_at = next_dt.isoformat()
        if success and items_found > 0:
            t.confidence_score = min(1.0, t.confidence_score + 0.05)
        elif not success:
            t.confidence_score = max(0.4, t.confidence_score - 0.1)
        self._save_persisted_state()

    def generate_expanded_queries(self, base_keyword: str, province: str = "Hạ Long") -> List[str]:
        """
        Mở rộng từ khóa đa chiều theo Master Prompt Mục 5:
        Không giới hạn ở 'IT', mà mở rộng chức danh thực chất, kỹ năng và công nghệ.
        """
        core_roles = [
            "IT Helpdesk", "IT Support", "Quản trị hệ thống", "Quản trị mạng",
            "Kỹ sư phần mềm", "Lập trình viên", "Backend Developer", "Frontend Developer",
            "Kỹ thuật máy tính", "Chuyên viên CNTT", "ERP Consultant", "Hạ tầng Cloud",
        ]
        
        expanded = []
        prov_clean = "Hạ Long" if "ha long" in province.lower() or "quảng ninh" in province.lower() else province
        for role in core_roles:
            expanded.append(f'"{role}" "{prov_clean}"')
            expanded.append(f'tuyển dụng {role} {prov_clean}')

        # Thêm cú pháp mạng xã hội
        expanded.append(f'site:facebook.com "tuyển dụng" "IT" "{prov_clean}"')
        expanded.append(f'site:linkedin.com/posts "tuyển" "{prov_clean}" "IT"')
        return expanded

    def _save_persisted_state(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            state = {tid: t.model_dump() for tid, t in self._queue.items()}
            with open(QUEUE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Lỗi lưu Discovery Queue: {e}")

    def _load_persisted_state(self) -> None:
        if not QUEUE_FILE_PATH.exists():
            return
        try:
            with open(QUEUE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
            for tid, t_data in state.items():
                if tid in self._queue:
                    target = self._queue[tid]
                    if "last_scanned_at" in t_data:
                        target.last_scanned_at = t_data["last_scanned_at"]
                    if "next_scan_at" in t_data:
                        target.next_scan_at = t_data["next_scan_at"]
                    if "confidence_score" in t_data:
                        target.confidence_score = t_data["confidence_score"]
                else:
                    self._queue[tid] = DiscoveryTarget(**t_data)
        except Exception as e:
            logger.warning(f"Lỗi nạp Discovery Queue: {e}")


# Singleton instance
discovery_queue_engine = DiscoveryQueueEngine()
