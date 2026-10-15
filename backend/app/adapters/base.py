"""
Unified Crawler Adapter Architecture for C_Data Platform.
Defines standard interfaces, data transfer models, error classifications,
and incremental crawl contracts for all job data sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger("c_data.adapters.base")


class AdapterErrorType(str, Enum):
    """Phân loại lỗi chuẩn hóa của bộ thu thập dữ liệu"""
    NETWORK_TIMEOUT = "network_timeout"           # Quá thời gian chờ phản hồi từ máy chủ nguồn
    CONNECTION_FAILED = "connection_failed"       # Lỗi kết nối vật lý, DNS hoặc SSL/TLS
    HTTP_ERROR = "http_error"                     # Mã lỗi HTTP (4xx, 5xx)
    RATE_LIMITED = "rate_limited"                 # Máy chủ phản hồi 429 Too Many Requests
    ROBOTS_DENIED = "robots_denied"               # Bị từ chối theo chính sách robots.txt
    AUTH_REQUIRED = "auth_required"               # Thiếu API Key hoặc token xác thực đối tác
    PARSE_ERROR = "parse_error"                   # Lỗi thay đổi cấu trúc HTML/XML/JSON không bóc tách được
    NOT_FOUND = "not_found"                       # Bài đăng 404 hoặc đã bị gỡ
    UNSUPPORTED = "unsupported"                   # Nền tảng không hỗ trợ truy cập bằng phương thức này
    BLOCKED = "blocked"                           # Bị chặn bởi nền tảng hoặc yêu cầu đăng nhập tài khoản cá nhân
    MISSING_CREDENTIALS = "missing_credentials"   # Thiếu token xác thực hoặc khóa API được cấp quyền
    UNKNOWN = "unknown"                           # Lỗi không xác định khác


@dataclass
class AdapterError:
    """Thông tin chi tiết về lỗi xảy ra trong quá trình thu thập"""
    error_type: AdapterErrorType
    message: str
    url: Optional[str] = None
    status_code: Optional[int] = None
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "url": self.url,
            "status_code": self.status_code,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass
class RawJobRecord:
    """
    Bản ghi dữ liệu thô chuẩn hóa do Adapter trích xuất từ nguồn.
    Tương thích 100% với Universal Job Schema (Prompt 02).
    """
    source_job_id: str
    title: str
    company_name: str
    source_url: str
    apply_url: Optional[str] = None
    
    # Lương & Chế độ
    salary_text: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "VND"
    salary_period: str = "month"
    
    # Địa điểm
    location_raw: str = ""
    location_province: Optional[str] = None
    location_district: Optional[str] = None
    
    # Tính chất công việc & Cấp bậc
    workplace_type: str = "onsite"               # onsite, hybrid, remote, unknown
    employment_type: str = "full-time"           # full-time, part-time, contract, internship
    experience_level: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    
    # Nội dung
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    category: Optional[str] = None
    
    # Mốc thời gian
    posted_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    
    # Trạng thái & Bằng chứng
    status: str = "active_likely"
    status_reason: Optional[str] = "Thu thập trực tiếp từ adapter nguồn"
    status_evidence: Optional[str] = None
    extraction_confidence: float = 0.85
    location_confidence: float = 0.85
    
    # Tác giả, tổ chức & phân loại bài đăng công khai
    author_name: Optional[str] = None
    author_id: Optional[str] = None
    post_classification: str = "original_hiring_post"  # original_hiring_post, shared_post, discussion_question, expired_closed, spam_commercial_ad
    first_seen_at: Optional[datetime] = None
    discovered_at: Optional[datetime] = None
    
    # Metadata nguồn & Băm nội dung
    content_hash: str = ""
    raw_data_reference: Dict[str, Any] = field(default_factory=dict)
    is_test_fixture: bool = False

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Tạo mã băm SHA256 dựa trên nội dung cốt lõi để phát hiện thay đổi (Incremental Crawl)"""
        norm_title = self.title.strip().lower()
        norm_company = self.company_name.strip().lower()
        norm_desc = (self.description or "")[:300].strip().lower()
        raw_key = f"{norm_title}::{norm_company}::{norm_desc}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_job_id": self.source_job_id,
            "title": self.title,
            "company_name": self.company_name,
            "source_url": self.source_url,
            "apply_url": self.apply_url or self.source_url,
            "salary_text": self.salary_text,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "salary_period": self.salary_period,
            "location_full": self.location_raw,
            "location_province": self.location_province,
            "location_district": self.location_district,
            "workplace_type": self.workplace_type,
            "job_type": self.employment_type,
            "experience_level": self.experience_level,
            "required_skills": self.required_skills,
            "description": self.description,
            "requirements": self.requirements,
            "benefits": self.benefits,
            "category": self.category,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "expires_at": self.deadline_at.isoformat() if self.deadline_at else None,
            "status": self.status,
            "status_reason": self.status_reason,
            "status_evidence": self.status_evidence,
            "extraction_confidence": self.extraction_confidence,
            "location_confidence": self.location_confidence,
            "author_name": self.author_name,
            "author_id": self.author_id,
            "post_classification": self.post_classification,
            "first_seen_at": self.first_seen_at.isoformat() if self.first_seen_at else None,
            "discovered_at": (self.discovered_at or self.first_seen_at).isoformat() if (self.discovered_at or self.first_seen_at) else None,
            "content_hash": self.content_hash,
            "raw_data_reference": self.raw_data_reference,
            "is_test_fixture": self.is_test_fixture,
        }


@dataclass
class AdapterCrawlResult:
    """Kết quả thu thập hoàn chỉnh của một lượt thực thi Adapter"""
    source_id: str
    source_name: str
    items: List[RawJobRecord] = field(default_factory=list)
    crawl_duration_ms: float = 0.0
    crawl_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    page: int = 1
    next_page: Optional[int] = None
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    has_more: bool = False
    total_detected: int = 0
    errors: List[AdapterError] = field(default_factory=list)
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_successful(self) -> bool:
        return len(self.errors) == 0 or len(self.items) > 0


class BaseJobAdapter(ABC):
    """
    Giao diện (Interface/Contract) chuẩn hóa cho toàn bộ các Adapter thu thập tin tuyển dụng.
    Bảo đảm:
    - Mỗi adapter có parser riêng biệt, không để lỗi HTML của nguồn này ảnh hưởng nguồn khác.
    - Hỗ trợ phân trang (page hoặc cursor).
    - Hỗ trợ incremental crawling (so khớp `since_timestamp` và `content_hash`).
    - Báo cáo chi tiết thời gian thực thi, telemetry và phân loại lỗi.
    """

    adapter_id: str = "base_adapter"
    source_name: str = "Base Source"
    source_domain: str = ""
    default_delay_seconds: float = 1.0

    @abstractmethod
    def discover_jobs(
        self,
        keyword: Optional[str] = None,
        province: Optional[str] = None,
        page: int = 1,
        cursor: Optional[str] = None,
        limit: int = 20,
        since_timestamp: Optional[datetime] = None,
    ) -> AdapterCrawlResult:
        """
        Phát hiện danh sách tin tuyển dụng từ nguồn:
        - Hỗ trợ phân trang qua `page` hoặc `cursor`.
        - Khi có `since_timestamp`, chỉ lấy hoặc ưu tiên các bài đăng mới hơn mốc này.
        - Trả về AdapterCrawlResult chuẩn hóa chứa RawJobRecord và phân loại lỗi.
        """
        pass

    @abstractmethod
    def fetch_job_detail(
        self,
        source_job_id: str,
        detail_url: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Lấy nội dung chi tiết bài đăng (mô tả, yêu cầu, phúc lợi, hạn nộp) khi được phép truy cập.
        Trả về None nếu không lấy được hoặc bị hạn chế.
        """
        pass

    def as_discovery_callable(self):
        """
        Chuyển đổi Adapter thành callable tương thích với MultiSourceDiscovery và SourceRegistry
        Signature: (intent, max_items) -> List[Dict[str, Any]]
        """
        def _callable(intent: Any, max_items: int = 10) -> List[Dict[str, Any]]:
            kw = intent.expanded_queries[0] if getattr(intent, "expanded_queries", None) else getattr(intent, "raw_query", None)
            prov = getattr(intent, "target_province", None)
            res = self.discover_jobs(keyword=kw, province=prov, limit=max_items)
            return [item.to_dict() for item in res.items[:max_items]]
        return _callable
