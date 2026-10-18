"""
Universal Job Schema for C_Data Platform (Master Prompt Section 7 & 9).
Provides the unified data representation for all crawlers, connectors,
deduplication engines, verification auditors, and frontend API endpoints.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VerificationStatus(str, Enum):
    """
    Quy ước 7 trạng thái tuyển dụng chuẩn theo Section 9 của Master Prompt:
    Tuyệt đối không dùng boolean is_active mơ hồ.
    """
    ACTIVE_CONFIRMED = "active_confirmed"  # Có bằng chứng xác nhận đang tuyển (nút apply hoạt động, schema verified)
    LIKELY_ACTIVE = "likely_active"        # Có tín hiệu tích cực (tin mới, hạn xa) nhưng chưa đủ bằng chứng khẳng định
    UNVERIFIED = "unverified"              # Chưa đủ thông tin để kết luận
    EXPIRED = "expired"                    # Hạn tuyển đã qua theo nguồn đáng tin cậy
    CLOSED = "closed"                      # Nguồn xác nhận đã đóng hoặc đã tuyển đủ
    REMOVED = "removed"                    # Bài gốc không còn truy cập được (chưa tự động suy ra đã tuyển đủ)
    CONFLICTING = "conflicting"            # Các nguồn cung cấp thông tin mâu thuẫn


class LocationNormalized(BaseModel):
    """Cấu trúc địa bàn làm việc đã chuẩn hóa hành chính"""
    city: str = Field(..., description="Thành phố / Thị xã / Huyện (ví dụ: Hạ Long, Cẩm Phả)")
    province: str = Field(..., description="Tỉnh / Thành phố trực thuộc trung ương (ví dụ: Quảng Ninh, Hà Nội)")
    district: Optional[str] = Field(None, description="Quận / Huyện / Phường (ví dụ: Bãi Cháy, Cầu Giấy)")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Độ tin cậy chuẩn hóa địa danh")


class VerificationAuditEvidence(BaseModel):
    """Bằng chứng thẩm định chi tiết mỗi lần kiểm tra"""
    checked_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    url_checked: str
    http_status: Optional[int] = None
    deadline_at: Optional[str] = None
    evidence_found: Dict[str, Any] = Field(default_factory=dict)
    method: str = Field(default="live_http_and_schema_audit")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    status_reason: str = Field(..., description="Lý do chi tiết cập nhật trạng thái")


class UniversalJob(BaseModel):
    """
    Schema chuẩn hóa phổ quát (Master Prompt Section 7).
    Mọi nguồn (sàn việc làm, web doanh nghiệp, mạng xã hội, ATS) đều phải ánh xạ về schema này.
    """
    job_id: str = Field(..., description="Mã định danh nội bộ ổn định (UUID hoặc canonical hash)")
    title: str = Field(..., description="Chức danh công việc chuẩn hóa")
    company_name: str = Field(..., description="Tên công ty tuyển dụng")
    
    # Địa điểm
    location_raw: str = Field(..., description="Chuỗi địa điểm nguyên bản từ nguồn")
    location_normalized: LocationNormalized = Field(..., description="Địa điểm đã được chuẩn hóa")
    
    # Chuyên môn & Cấp bậc
    job_categories: List[str] = Field(default_factory=list, description="Danh mục phân loại chuyên môn CNTT")
    seniority: str = Field(default="Junior", description="Cấp bậc: Intern, Fresher, Junior, Middle, Senior, Lead, Manager, Không yêu cầu")
    experience_requirement: str = Field(default="Không yêu cầu kinh nghiệm", description="Mô tả yêu cầu kinh nghiệm nguyên bản")
    
    # Hình thức làm việc
    work_type: str = Field(default="On-site", description="On-site, Hybrid, Remote")
    work_schedule: Optional[str] = Field(None, description="Toàn thời gian, Bán thời gian, Thực tập, Ca kíp")
    
    # Lương
    salary_min: Optional[int] = Field(None, description="Lương tối thiểu (VND)")
    salary_max: Optional[int] = Field(None, description="Lương tối đa (VND)")
    salary_currency: str = Field(default="VND", description="Đơn vị tiền tệ")
    salary_text: Optional[str] = Field(None, description="Chuỗi mô tả lương gốc (ví dụ: 12 - 18 triệu)")
    
    # Nội dung & Kỹ năng
    description: str = Field(default="", description="Mô tả công việc chi tiết")
    required_skills: List[str] = Field(default_factory=list, description="Kỹ năng yêu cầu")
    
    # Dấu vết thời gian (Phân biệt ngày đăng thật với ngày crawl)
    posted_at: Optional[str] = Field(None, description="Thời điểm đăng tin gốc được chứng minh")
    deadline: Optional[str] = Field(None, description="Hạn chót ứng tuyển được chứng minh")
    first_seen_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Nguồn & Đường dẫn
    source_name: str = Field(..., description="Tên nguồn (ví dụ: CareerViet, Sun Group Portal, LinkedIn Guest)")
    source_type: str = Field(default="job_board", description="job_board, enterprise_direct, social_public, specialized_local, authorized_api")
    original_url: str = Field(..., description="URL bài đăng chi tiết gốc")
    application_url: Optional[str] = Field(None, description="URL form ứng tuyển trực tiếp (nếu có)")
    employer_url: Optional[str] = Field(None, description="Website chính thức của nhà tuyển dụng")
    application_method: Optional[str] = Field(None, description="online_form, email, hotline, in_person")
    
    # Trạng thái & Đối soát
    verification_status: VerificationStatus = Field(default=VerificationStatus.UNVERIFIED)
    verification_evidence: List[VerificationAuditEvidence] = Field(default_factory=list)
    
    # Chống trùng lặp & Vận hành
    duplicate_group_id: Optional[str] = Field(None, description="ID nhóm trùng lặp đa nguồn")
    crawl_status: str = Field(default="success", description="success, partial, pending_verification")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
