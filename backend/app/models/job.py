import hashlib
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
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
    Bảng lưu trữ dữ liệu tin tuyển dụng việc làm tổng hợp đa nguồn theo chuẩn Universal Job Schema.
    Hỗ trợ đầy đủ:
    - Nhận diện công ty & vị trí (id, title, company_name, company_id)
    - Địa điểm đa điểm (locations JSON, location_province, location_district, location_full)
    - Môi trường & Hình thức làm việc (workplace_type, employment_type, job_type, category, experience_level)
    - Kỹ năng & Lương (required_skills, salary_min, salary_max, salary_currency, salary_period, salary_text)
    - Mô tả & Yêu cầu (description, requirements)
    - Dấu vết thời gian chuẩn (posted_at, updated_at, deadline_at, first_seen_at, last_seen_at, last_verified_at)
    - Nguồn & Định danh (source_name, source_platform, source_url, apply_url, source_job_id)
    - Trạng thái & Bằng chứng xác minh (status, status_reason, status_evidence, is_active)
    - Chỉ số độ tin cậy & Chống trùng lặp (extraction_confidence, location_confidence, content_hash, raw_data_reference)
    """
    __tablename__ = "jobs"

    # 1. Định danh chính
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

    # 2. Địa điểm làm việc (Hỗ trợ đa địa điểm & tương thích ngược)
    locations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        doc="Danh sách các địa điểm làm việc có cấu trúc: [{'province': '...', 'district': '...', 'address': '...', 'is_primary': True}]",
    )
    location_province: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Tỉnh / Thành phố làm việc chính",
    )
    location_district: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Quận / Huyện làm việc chính",
    )
    location_full: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Địa chỉ chi tiết nơi làm việc",
    )

    # 3. Môi trường & Hình thức làm việc
    workplace_type: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        server_default="unknown",
        nullable=False,
        index=True,
        doc="Môi trường làm việc: onsite, hybrid, remote, hoặc unknown",
    )
    employment_type: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        server_default="unknown",
        nullable=False,
        index=True,
        doc="Hình thức lao động: full-time, part-time, contract, intern, temporary, unknown",
    )
    job_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        doc="Hình thức làm việc cũ (tương thích ngược: full-time, part-time, remote, intern)",
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
        doc="Cấp bậc kinh nghiệm: intern, fresher, junior, middle, senior, lead, manager, unknown",
    )
    required_skills: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        default=list,
        doc="Danh sách các kỹ năng công nghệ/nghiệp vụ yêu cầu",
    )

    # 4. Mức lương & Đãi ngộ
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
    salary_currency: Mapped[str] = mapped_column(
        String(10),
        default="VND",
        server_default="VND",
        nullable=False,
        doc="Đơn vị tiền tệ (mặc định VND, hoặc USD,...)",
    )
    salary_period: Mapped[str] = mapped_column(
        String(20),
        default="month",
        server_default="month",
        nullable=False,
        doc="Kỳ trả lương: month, year, hour, day, project, unknown",
    )
    salary_text: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        doc="Mô tả mức lương nguyên bản (Ví dụ: Thỏa thuận, 15 - 20 triệu)",
    )

    # 5. Nội dung tuyển dụng
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

    # 6. Các mốc thời gian độc lập & Timezone chuẩn xác
    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Thời điểm bài viết được đăng tải trên nguồn gốc (nếu có bằng chứng xác minh)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Thời điểm bản ghi được cập nhật lần cuối trong database C_Data",
    )
    deadline_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Hạn chót nộp hồ sơ ứng tuyển chính thức",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Hạn nộp hồ sơ (trường tương thích ngược, đồng bộ 1-1 với deadline_at)",
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Thời điểm hệ thống C_Data phát hiện tin tuyển dụng lần đầu tiên",
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Thời điểm hệ thống quan sát thấy tin tuyển dụng xuất hiện lần gần nhất",
    )
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Thời điểm xác minh tình trạng tuyển dụng thực tế gần nhất",
    )
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Thời điểm cào dữ liệu (tương thích ngược)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Thời điểm tạo bản ghi",
    )

    # 7. Nguồn tuyển dụng & Đường dẫn liên kết
    source_name: Mapped[str] = mapped_column(
        String(100),
        default="unknown",
        server_default="unknown",
        nullable=False,
        index=True,
        doc="Tên chuẩn hóa của nguồn tin (CareerViet, TopCV, FPT Telecom, Wyndham Legend...)",
    )
    source_platform: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        doc="Nền tảng cào dữ liệu (tương thích ngược với source_name)",
    )
    source_url: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
        doc="Đường dẫn URL gốc của bài tuyển dụng (dùng để khử trùng lặp)",
    )
    apply_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Đường dẫn ứng tuyển trực tiếp (portal submit form, ATS URL hoặc mailto)",
    )
    source_job_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        doc="Mã định danh của bài đăng trên hệ thống nguồn (nếu có)",
    )

    # 8. Quy ước trạng thái & Bằng chứng xác minh
    status: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        server_default="unknown",
        nullable=False,
        index=True,
        doc="Trạng thái tuyển dụng: active_confirmed, active_likely, expired, closed, unknown",
    )
    status_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Lý do giải thích cụ thể cho trạng thái tuyển dụng",
    )
    status_evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Hồ sơ dẫn chứng xác thực: HTTP status code, URL test, contact recruiter, text snippet",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="1",
        nullable=False,
        index=True,
        doc="Cờ nhị phân còn hiển thị hay không (tương thích ngược: True nếu status in [active_confirmed, active_likely])",
    )

    # 9. Độ tin cậy & Chống trùng lặp nội dung
    extraction_confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        server_default="1.0",
        nullable=False,
        doc="Điểm tin cậy trích xuất dữ liệu (0.0 đến 1.0)",
    )
    location_confidence: Mapped[float] = mapped_column(
        Float,
        default=1.0,
        server_default="1.0",
        nullable=False,
        doc="Điểm tin cậy bóc tách địa điểm (0.0 đến 1.0)",
    )
    raw_data_reference: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Mã định danh hoặc đường dẫn tham chiếu đến dữ liệu snapshot thô",
    )
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        doc="Mã băm SHA-256 nội dung chính để phát hiện trùng lặp giữa các nguồn",
    )
    raw_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Dữ liệu JSON thô thu thập từ crawler",
    )

    # Quan hệ nhiều - một với Company
    company: Mapped[Optional["Company"]] = relationship(
        "Company",
        back_populates="jobs",
        lazy="selectin",
    )

    def compute_content_hash(self) -> str:
        """Tạo mã SHA-256 duy nhất dựa trên company, title và địa bàn chuẩn hóa."""
        c = (self.company_name or "").strip().lower()
        t = (self.title or "").strip().lower()
        p = (self.location_province or "").strip().lower()
        token = f"{c}::{t}::{p}"
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def sync_universal_fields(self) -> None:
        """
        Đồng bộ tự động giữa các trường mới và trường tương thích ngược:
        - source_name <-> source_platform
        - deadline_at <-> expires_at
        - status <-> is_active
        - locations <-> location_province / location_district / location_full
        - content_hash
        """
        # Đồng bộ nguồn
        if not self.source_name or self.source_name == "unknown":
            if self.source_platform:
                self.source_name = self.source_platform
        elif not self.source_platform:
            self.source_platform = self.source_name

        # Đồng bộ hạn nộp
        if self.deadline_at is not None and self.expires_at is None:
            self.expires_at = self.deadline_at
        elif self.expires_at is not None and self.deadline_at is None:
            self.deadline_at = self.expires_at

        # Đồng bộ địa điểm
        if not self.locations and (self.location_province or self.location_district or self.location_full):
            self.locations = [
                {
                    "province": self.location_province,
                    "district": self.location_district,
                    "address": self.location_full,
                    "is_primary": True,
                }
            ]
        elif self.locations and isinstance(self.locations, list) and len(self.locations) > 0:
            primary = next((loc for loc in self.locations if loc.get("is_primary")), self.locations[0])
            if not self.location_province and primary.get("province"):
                self.location_province = primary.get("province")
            if not self.location_district and primary.get("district"):
                self.location_district = primary.get("district")
            if not self.location_full and primary.get("address"):
                self.location_full = primary.get("address")

        # Đồng bộ workplace_type từ job_type nếu unknown
        if self.workplace_type == "unknown" and self.job_type:
            jt_lower = self.job_type.lower()
            if "remote" in jt_lower or "từ xa" in jt_lower:
                self.workplace_type = "remote"
            elif "hybrid" in jt_lower:
                self.workplace_type = "hybrid"
            elif "full-time" in jt_lower or "part-time" in jt_lower or "toàn thời gian" in jt_lower:
                self.workplace_type = "onsite"

        # Đồng bộ employment_type từ job_type nếu unknown
        if self.employment_type == "unknown" and self.job_type:
            jt_lower = self.job_type.lower()
            if "part-time" in jt_lower or "bán thời gian" in jt_lower:
                self.employment_type = "part-time"
            elif "intern" in jt_lower or "thực tập" in jt_lower:
                self.employment_type = "intern"
            elif "full-time" in jt_lower or "toàn thời gian" in jt_lower:
                self.employment_type = "full-time"
            elif "contract" in jt_lower or "hợp đồng" in jt_lower:
                self.employment_type = "contract"

        # Đồng bộ content_hash nếu chưa có
        if not self.content_hash:
            self.content_hash = self.compute_content_hash()

        # Kiểm tra hạn chót so với thời gian hiện tại để cập nhật status nếu đã quá hạn
        now_dt = datetime.now(timezone.utc)
        dl = self.deadline_at or self.expires_at
        if dl:
            dl_utc = dl if dl.tzinfo else dl.replace(tzinfo=timezone.utc)
            if dl_utc < now_dt:
                self.status = "expired"
                self.status_reason = f"Hết hạn nộp hồ sơ vào {dl_utc.isoformat()}"
                self.is_active = False

        # Đồng bộ cờ is_active tương thích ngược
        if self.status in ["active_confirmed", "active_likely"]:
            self.is_active = True
        elif self.status in ["expired", "closed"]:
            self.is_active = False

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, title='{self.title}', status='{self.status}', source='{self.source_name}')>"
