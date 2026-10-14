import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.company import CompanyResponse


class JobBase(BaseModel):
    """
    Schema cơ sở chứa toàn bộ các thuộc tính định danh việc làm
    """
    title: str = Field(..., max_length=500, description="Tiêu đề tin tuyển dụng")
    company_name: Optional[str] = Field(None, max_length=300, description="Tên công ty")
    company_id: Optional[str] = Field(None, description="Khóa ngoại công ty")
    description: Optional[str] = Field(None, description="Mô tả công việc")
    requirements: Optional[str] = Field(None, description="Yêu cầu công việc")
    salary_min: Optional[int] = Field(None, ge=0, description="Lương tối thiểu (VNĐ)")
    salary_max: Optional[int] = Field(None, ge=0, description="Lương tối đa (VNĐ)")
    salary_text: Optional[str] = Field(None, max_length=200, description="Mô tả lương nguyên bản")
    location_province: Optional[str] = Field(None, max_length=100, description="Tỉnh / Thành phố")
    location_district: Optional[str] = Field(None, max_length=100, description="Quận / Huyện")
    location_full: Optional[str] = Field(None, description="Địa chỉ đầy đủ")
    job_type: Optional[str] = Field(None, max_length=50, description="Hình thức: full-time, part-time, remote, intern")
    category: Optional[str] = Field(None, max_length=100, description="Danh mục / Ngành nghề")
    experience_level: Optional[str] = Field(None, max_length=100, description="Cấp bậc kinh nghiệm")
    source_platform: Optional[str] = Field(None, max_length=100, description="Nguồn cào dữ liệu")
    source_url: str = Field(..., description="Đường dẫn bài viết gốc")
    posted_at: Optional[datetime] = Field(None, description="Thời điểm đăng tin")
    expires_at: Optional[datetime] = Field(None, description="Hạn chót nộp hồ sơ")
    is_active: bool = Field(True, description="Trạng thái còn hiệu lực")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu nguyên bản JSON")


class JobCreate(JobBase):
    """
    Schema tạo mới tin tuyển dụng (dùng bởi scraper/crawler)
    """
    pass


class JobUpdate(BaseModel):
    """
    Schema cập nhật thông tin tin tuyển dụng
    """
    title: Optional[str] = Field(None, max_length=500)
    company_name: Optional[str] = Field(None, max_length=300)
    company_id: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_text: Optional[str] = None
    location_province: Optional[str] = None
    location_district: Optional[str] = None
    location_full: Optional[str] = None
    job_type: Optional[str] = None
    category: Optional[str] = None
    experience_level: Optional[str] = None
    source_platform: Optional[str] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    raw_data: Optional[Dict[str, Any]] = None


class JobResponse(JobBase):
    """
    Schema phản hồi thông tin chi tiết một tin tuyển dụng
    """
    id: str
    crawled_at: datetime
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyResponse] = None
    all_sources: Optional[List[Dict[str, Any]]] = Field(None, description="Danh sách các nguồn gốc nơi tin này xuất hiện")
    match_reasons: Optional[List[str]] = Field(None, description="Lý do xếp hạng và độ phù hợp với ý định tìm kiếm")
    match_score: Optional[float] = Field(None, description="Điểm độ phù hợp")

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """
    Schema danh sách việc làm có phân trang và thông tin gợi ý ngành nghề thông minh
    """
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    related_keywords: List[str] = Field(default_factory=list, description="Từ khóa gợi ý liên quan theo ngành")
    matched_industries: List[str] = Field(default_factory=list, description="Các ngành nghề liên quan được hệ thống tự động suy luận")
    diagnostics: Optional[Dict[str, Any]] = Field(None, description="Báo cáo chẩn đoán toàn trình tìm kiếm thông minh")


class JobSearchParams(BaseModel):
    """
    Tham số tìm kiếm và lọc dữ liệu việc làm
    """
    query: Optional[str] = Field(None, description="Từ khóa tìm kiếm trong tiêu đề hoặc mô tả")
    q: Optional[str] = Field(None, description="Từ khóa tìm kiếm (alias)")
    province: Optional[str] = Field(None, description="Lọc theo tỉnh thành")
    category: Optional[str] = Field(None, description="Lọc theo ngành nghề")
    job_type: Optional[str] = Field(None, description="Lọc theo loại hình: full-time, part-time, remote, intern")
    salary_min: Optional[int] = Field(None, ge=0, description="Mức lương tối thiểu (VNĐ)")
    salary_max: Optional[int] = Field(None, ge=0, description="Mức lương tối đa (VNĐ)")
    source_platform: Optional[str] = Field(None, description="Nguồn cào: TopCV, VietnamWorks, ITviec...")
    page: int = Field(1, ge=1, description="Trang hiện tại")
    page_size: int = Field(20, ge=1, le=100, description="Số lượng mục trên một trang")
    sort_by: Optional[str] = Field("newest", description="Thứ tự sắp xếp: newest, salary_desc, salary_asc")
    live: bool = Field(False, description="Kích hoạt quét đa nguồn thời gian thực")
    strict_mode: bool = Field(False, description="Chế độ khớp khắt khe các ràng buộc cứng")
