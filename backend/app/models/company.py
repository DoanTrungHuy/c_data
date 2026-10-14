import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.job import Job


class Company(Base):
    """
    Bảng lưu trữ thông tin công ty tuyển dụng
    """
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
        doc="Tên công ty / doanh nghiệp tuyển dụng",
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Đường dẫn ảnh đại diện / logo công ty",
    )
    website: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Địa chỉ trang web công ty",
    )
    province: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Tỉnh / Thành phố đặt trụ sở chính",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Mô tả tóm tắt về doanh nghiệp",
    )
    industry: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        doc="Ngành nghề hoạt động chính của công ty",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Quan hệ 1-N với danh sách việc làm
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name='{self.name}', province='{self.province}')>"
