from typing import List
from pydantic import BaseModel, Field


class ProvinceJobCount(BaseModel):
    """
    Số lượng công việc theo từng tỉnh thành
    """
    province: str = Field(..., description="Tên tỉnh / thành phố")
    count: int = Field(..., ge=0, description="Số lượng việc làm đang mở")


class CategoryJobCount(BaseModel):
    """
    Số lượng công việc theo từng danh mục / ngành nghề
    """
    category: str = Field(..., description="Tên ngành nghề")
    count: int = Field(..., ge=0, description="Số lượng việc làm")


class PlatformJobCount(BaseModel):
    """
    Số lượng công việc theo nền tảng nguồn cào
    """
    platform: str = Field(..., description="Tên nền tảng: TopCV, VietnamWorks, ITviec...")
    count: int = Field(..., ge=0, description="Số lượng việc làm thu thập được")


class DashboardStats(BaseModel):
    """
    Thống kê tổng quan cho trang chủ và dashboard quản trị C_Data
    """
    total_jobs: int = Field(..., ge=0, description="Tổng số việc làm đang hoạt động")
    total_companies: int = Field(..., ge=0, description="Tổng số doanh nghiệp tuyển dụng")
    total_provinces_with_jobs: int = Field(..., ge=0, description="Số lượng tỉnh thành có tin tuyển dụng")
    new_jobs_today: int = Field(..., ge=0, description="Số lượng việc làm mới thu thập hôm nay")
    jobs_by_province: List[ProvinceJobCount] = Field(default_factory=list, description="Thống kê việc làm theo tỉnh")
    jobs_by_category: List[CategoryJobCount] = Field(default_factory=list, description="Thống kê việc làm theo ngành")
    jobs_by_platform: List[PlatformJobCount] = Field(default_factory=list, description="Thống kê việc làm theo nền tảng nguồn")
