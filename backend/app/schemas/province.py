from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProvinceBase(BaseModel):
    """
    Schema cơ sở cho tỉnh thành
    """
    code: str = Field(..., max_length=10, description="Mã tỉnh thành theo GSO")
    name: str = Field(..., max_length=100, description="Tên tiếng Việt có dấu")
    name_en: Optional[str] = Field(None, max_length=100, description="Tên tiếng Anh hoặc không dấu")
    region: Optional[str] = Field(None, max_length=50, description="Vùng miền: Miền Bắc, Miền Trung, Miền Nam")


class ProvinceCreate(ProvinceBase):
    """
    Schema tạo mới tỉnh thành
    """
    pass


class ProvinceResponse(ProvinceBase):
    """
    Schema phản hồi tỉnh thành
    """
    model_config = ConfigDict(from_attributes=True)


class ProvinceWithStatsResponse(ProvinceResponse):
    """
    Schema tỉnh thành kèm số lượng việc làm hiện có
    """
    job_count: int = 0


class ProvinceListResponse(BaseModel):
    """
    Schema danh sách các tỉnh thành
    """
    items: List[ProvinceResponse]
    total: int
