import uuid
from datetime import datetime
from typing import Any, List, Optional
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
