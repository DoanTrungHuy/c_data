"""
Pydantic schemas for C_Data Source Registry & Source Management System.
Defines metadata, access methods, rate limits, health checks, and metrics for job sources.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceCategory(str, Enum):
    """5 nhóm nguồn tuyển dụng chuẩn của C_Data"""
    ENTERPRISE_DIRECT = "enterprise_direct"         # Trang tuyển dụng chính thức của doanh nghiệp
    NATIONAL_JOB_BOARD = "national_job_board"       # Website tuyển dụng tại Việt Nam (CareerViet, TopCV, VietnamWorks, ...)
    SPECIALIZED_LOCAL = "specialized_local"         # Trang tuyển dụng chuyên ngành hoặc địa phương (Quảng Ninh Job Center, ...)
    SOCIAL_PUBLIC = "social_public"                 # Nguồn công khai từ mạng xã hội (Fanpage/Group công khai tuân thủ ToS)
    AUTHORIZED_API = "authorized_api"               # API/RSS hoặc nguồn dữ liệu được cấp quyền chính thức


class AccessMethod(str, Enum):
    """Phương thức truy cập dữ liệu"""
    API = "api"                                     # REST API / GraphQL chính thức
    RSS = "rss"                                     # RSS Feed / Atom syndication
    SITEMAP = "sitemap"                             # XML Sitemap discovery
    PUBLIC_WEB = "public_web"                       # Cào trang công khai tuân thủ robots.txt
    AUTHORIZED_ADAPTER = "authorized_adapter"       # Adapter chuyên biệt có kiểm soát bản quyền/token


class CredentialStatus(str, Enum):
    """Trạng thái xác thực credential của nguồn"""
    UNNEEDED = "unneeded"                           # Nguồn công khai, không cần xác thực
    VALID = "valid"                                 # Credential hợp lệ và đã được kiểm tra
    MISSING = "missing"                             # Cần credential nhưng chưa cấu hình trong biến môi trường
    INVALID = "invalid"                             # Credential có cấu hình nhưng bị từ chối / hết hạn


class SourceHealthStatus(str, Enum):
    """Tình trạng sức khỏe thực tế của nguồn (không tự động coi là healthy nếu chỉ khai báo)"""
    HEALTHY = "healthy"                             # Kết nối tốt, phản hồi chuẩn xác
    DEGRADED = "degraded"                           # Phản hồi chậm hoặc có lỗi cục bộ không nghiêm trọng
    UNHEALTHY = "unhealthy"                         # Lỗi kết nối, 4xx/5xx hoặc bị chặn truy cập
    UNCONFIGURED = "unconfigured"                   # Thiếu cấu hình/credential cần thiết, chưa thể chạy
    UNKNOWN = "unknown"                             # Chưa từng chạy health check


class RateLimitConfig(BaseModel):
    """Cấu hình giới hạn tần suất truy vấn để tôn trọng tài nguyên máy chủ nguồn"""
    requests_per_minute: int = Field(default=30, ge=1, le=600, description="Số yêu cầu tối đa mỗi phút")
    min_delay_seconds: float = Field(default=1.0, ge=0.0, description="Độ trễ tối thiểu giữa 2 request liên tiếp")
    concurrent_limit: int = Field(default=2, ge=1, le=10, description="Số luồng truy vấn song song tối đa")


class SourceMetrics(BaseModel):
    """Số liệu đo lường hiệu năng và độ tin cậy của nguồn"""
    discovered_count: int = Field(default=0, description="Tổng số bản ghi phát hiện")
    new_count: int = Field(default=0, description="Số bản ghi mới thêm vào hệ thống")
    error_count: int = Field(default=0, description="Số lượt gặp lỗi khi crawl")
    last_crawl_duration_ms: float = Field(default=0.0, description="Thời gian thực thi lần crawl gần nhất (ms)")
    total_runs: int = Field(default=0, description="Tổng số lần chạy crawl")


class SourceDefinition(BaseModel):
    """Mô hình dữ liệu đầy đủ của một nguồn tuyển dụng trong Source Registry"""
    id: str = Field(..., description="Định danh duy nhất (slug), ví dụ: careerviet, sun_group")
    name: str = Field(..., description="Tên hiển thị của nguồn")
    category: SourceCategory = Field(..., description="Nhóm nguồn trong 5 nhóm chuẩn")
    domain: str = Field(..., description="Tên miền chính (FQDN), ví dụ: careerviet.vn")
    access_method: AccessMethod = Field(..., description="Phương thức truy cập dữ liệu")
    is_enabled: bool = Field(default=True, description="Trạng thái bật/tắt độc lập của nguồn")
    priority: int = Field(default=5, ge=1, le=10, description="Mức độ ưu tiên (1: cao nhất, 10: thấp nhất)")
    sync_interval_seconds: int = Field(default=3600, ge=60, description="Tần suất đồng bộ mặc định (giây)")
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    # Trạng thái sức khỏe và bằng chứng thực tế
    health_status: SourceHealthStatus = Field(default=SourceHealthStatus.UNKNOWN)
    health_evidence: Optional[str] = Field(default=None, description="Bằng chứng từ kết quả kiểm tra sức khỏe gần nhất")
    last_health_check_at: Optional[datetime] = Field(default=None)
    
    # Lịch sử crawl
    last_successful_crawl: Optional[datetime] = Field(default=None)
    last_failed_crawl: Optional[datetime] = Field(default=None)
    last_error_message: Optional[str] = Field(default=None)
    
    # Số liệu phát hiện & đo lường
    metrics: SourceMetrics = Field(default_factory=SourceMetrics)
    
    # Xác thực & Tuân thủ
    credential_status: CredentialStatus = Field(default=CredentialStatus.UNNEEDED)
    required_credentials: List[str] = Field(default_factory=list, description="Danh sách tên biến môi trường cần thiết")
    access_conditions: Optional[str] = Field(default=None, description="Điều kiện truy cập")
    compliance_notes: Optional[str] = Field(default=None, description="Ghi chú tuân thủ robots.txt, ToS và bản quyền")
    target_provinces: List[str] = Field(default_factory=lambda: ["Toàn quốc"], description="Phạm vi địa lý trọng tâm")


class SourceToggleRequest(BaseModel):
    """Yêu cầu bật/tắt nguồn"""
    is_enabled: bool


class SourceHealthCheckResult(BaseModel):
    """Kết quả kiểm tra sức khỏe của một nguồn"""
    source_id: str
    source_name: str
    status: SourceHealthStatus
    is_healthy: bool
    latency_ms: float
    evidence: str
    checked_at: datetime
    error: Optional[str] = None


class SourceRegistrySummary(BaseModel):
    """Báo cáo tổng quan về trạng thái danh mục nguồn"""
    total_sources: int
    enabled_sources: int
    disabled_sources: int
    healthy_sources: int
    degraded_sources: int
    unhealthy_sources: int
    unconfigured_sources: int
    by_category: Dict[str, int]
