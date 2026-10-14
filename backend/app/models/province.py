from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Province(Base):
    """
    Bảng danh mục các tỉnh và thành phố trực thuộc trung ương của Việt Nam
    """
    __tablename__ = "provinces"

    code: Mapped[str] = mapped_column(
        String(10),
        primary_key=True,
        doc="Mã định danh tỉnh thành theo Tổng cục Thống kê (01, 79, ...)",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Tên tiếng Việt có dấu (Hà Nội, TP. Hồ Chí Minh,...)",
    )
    name_en: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Tên tiếng Anh hoặc không dấu (Ha Noi, Ho Chi Minh,...)",
    )
    region: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        doc="Vùng miền địa lý: Miền Bắc, Miền Trung, Miền Nam",
    )

    def __repr__(self) -> str:
        return f"<Province(code='{self.code}', name='{self.name}', region='{self.region}')>"
