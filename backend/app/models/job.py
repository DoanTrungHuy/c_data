import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.company import Company


class Job(Base):
    """
    Bảng lưu trữ dữ liệu tin tuyển dụng việc làm tổng hợp từ các nền tảng
    """
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        doc="Tiêu đề việc làm",
    )
    company_name: Mapped[Optional[str]] = mapped_column(
        String(300),
        nullable=True,
        index=True,
        doc="Tên công ty tuyển dụng",
    )
    company_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Khóa ngoại liên kết tới bảng companies",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Mô tả công việc chi tiết",
    )
    requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Yêu cầu ứng viên",
    )
    salary_min: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        doc="Mức lương tối thiểu (VNĐ)",
    )
    salary_max: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        doc="Mức lương tối đa (VNĐ)",
    )
    salary_text: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        doc="Mô tả mức lương nguyên bản (Ví dụ: Thỏa thuận, 15 - 20 triệu)",
    )
    location_province: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Tỉnh / Thành phố làm việc",
    )
    location_district: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Quận / Huyện làm việc",
    )
    location_full: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Địa chỉ chi tiết nơi làm việc",
    )
    job_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        doc="Hình thức làm việc: full-time, part-time, remote, intern",
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Ngành nghề / Danh mục công việc (CNTT, Marketing, Kế toán,...)",
    )
    experience_level: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Cấp bậc kinh nghiệm (Intern, Fresher, Junior, Senior, Manager,...)",
    )
    source_platform: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Nền tảng nguồn cào dữ liệu (TopCV, VietnamWorks, ITviec, CareerBuilder...)",
    )
    source_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="Đường dẫn URL gốc của bài tuyển dụng (dùng để khử trùng lặp)",
    )
    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        doc="Thời điểm bài viết được đăng tải trên nguồn gốc",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        doc="Hạn nộp hồ sơ ứng tuyển",
    )
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        doc="Thời điểm hệ thống cào dữ liệu",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
        index=True,
        doc="Trạng thái bài đăng còn hiệu lực hay đã hết hạn",
    )
    raw_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Dữ liệu JSON thô thu thập từ crawler",
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

    # Quan hệ nhiều - một với Company
    company: Mapped[Optional["Company"]] = relationship(
        "Company",
        back_populates="jobs",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', platform='{self.source_platform}')>"
