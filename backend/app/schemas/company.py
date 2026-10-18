import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """
    Schema cơ sở cho thông tin công ty
    """
    name: str = Field(..., max_length=300, description="Tên công ty")
    logo_url: Optional[str] = Field(None, description="Đường dẫn ảnh logo")
    website: Optional[str] = Field(None, description="Trang web doanh nghiệp")
    province: Optional[str] = Field(None, max_length=100, description="Tỉnh / Thành phố đặt trụ sở")
    description: Optional[str] = Field(None, description="Mô tả công ty")
    industry: Optional[str] = Field(None, max_length=200, description="Ngành nghề kinh doanh")


class CompanyCreate(CompanyBase):
    """
    Schema khi thêm mới công ty
    """
    pass


class CompanyUpdate(BaseModel):
    """
    Schema cập nhật thông tin công ty
    """
    name: Optional[str] = Field(None, max_length=300)
    logo_url: Optional[str] = None
    website: Optional[str] = None
    province: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=200)


class CompanyResponse(CompanyBase):
    """
    Schema phản hồi thông tin công ty
    """
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyJobBrief(BaseModel):
    """
    Schema tóm tắt việc làm trực thuộc công ty
    """
    id: str
    title: str
    salary_text: Optional[str] = None
    location_province: Optional[str] = None
    job_type: Optional[str] = None
    category: Optional[str] = None
    source_platform: Optional[str] = None
    source_url: str
    posted_at: Optional[datetime] = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class CompanyDetailResponse(CompanyResponse):
    """
    Schema phản hồi chi tiết công ty kèm danh sách việc làm đang mở
    """
    jobs: List[CompanyJobBrief] = []
    total_active_jobs: int = 0


class CompanyListResponse(BaseModel):
    """
    Schema phản hồi danh sách công ty phân trang
    """
    items: List[CompanyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CompanyRegistryProfile(BaseModel):
    """
    Hồ sơ doanh nghiệp địa phương chuyên sâu (Master Prompt Nhóm B & E).
    Lưu trữ cấu trúc thông tin doanh nghiệp tại Hạ Long / Quảng Ninh,
    kênh tuyển dụng chính thức, hotline HR và trạng thái theo dõi trực tiếp.
    """
    company_id: str = Field(..., description="Mã định danh duy nhất của doanh nghiệp")
    name: str = Field(..., description="Tên đầy đủ theo pháp nhân")
    brand_name: Optional[str] = Field(None, description="Tên thương hiệu phổ biến")
    industry_group: str = Field(..., description="hospitality_tourism, healthcare, industry_logistics, telecom_it, education_finance")
    locations: List[Dict[str, str]] = Field(default_factory=list, description="Danh sách địa chỉ tại Quảng Ninh")
    website_home: str = Field(..., description="Website chính thức của doanh nghiệp")
    career_url: str = Field(..., description="Trang nghề nghiệp / tuyển dụng chính thức")
    social_channels: Dict[str, str] = Field(default_factory=dict, description="Kênh Facebook, LinkedIn, Zalo tuyển dụng")
    hr_contacts: Dict[str, Any] = Field(default_factory=dict, description="Hotline HR, email tuyển dụng")
    career_page_status: str = Field(default="unknown", description="healthy, redirected, blocked, unmaintained, unknown")
    last_checked_at: Optional[str] = Field(None, description="Thời điểm kiểm tra HTTP gần nhất")
    http_status: Optional[int] = Field(None, description="Mã HTTP status trang tuyển dụng")
    active_it_roles: List[str] = Field(default_factory=list, description="Vị trí CNTT/kỹ thuật trọng điểm thường tuyển")
    notes: Optional[str] = Field(None, description="Ghi chú nghiệp vụ và đặc thù địa bàn")

