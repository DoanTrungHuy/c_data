import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.company import CompanyResponse

# Quy ước kiểu môi trường làm việc
WorkplaceType = Literal["onsite", "hybrid", "remote", "unknown"]

# Quy ước trạng thái tuyển dụng chuẩn
JobStatus = Literal[
    "active_confirmed",  # Còn tuyển & có bằng chứng xác minh (URL chi tiết live, contact verified)
    "active_likely",     # Mới phát hiện/mới cào, chưa có dấu hiệu đóng đơn, chưa xác minh sâu
    "expired",           # Đã quá hạn chót nộp hồ sơ
    "closed",            # Doanh nghiệp đã đóng đơn (tuyển đủ, ngừng nhận hồ sơ)
    "unknown",           # Không đủ bằng chứng để xác định
]

# Kỳ hạn chi trả lương
SalaryPeriod = Literal["month", "year", "hour", "day", "project", "unknown"]


class JobLocation(BaseModel):
    """
    Schema chi tiết cho từng địa điểm làm việc
    """
    province: Optional[str] = Field(None, max_length=100, description="Tỉnh / Thành phố")
    district: Optional[str] = Field(None, max_length=100, description="Quận / Huyện")
    address: Optional[str] = Field(None, description="Địa chỉ cụ thể nơi làm việc")
    is_primary: bool = Field(True, description="Địa điểm làm việc chính")
    country: str = Field("Vietnam", description="Quốc gia")

    model_config = ConfigDict(from_attributes=True)


class JobBase(BaseModel):
    """
    Schema chuẩn phổ quát (Universal Job Schema) dùng chung cho tất cả các nguồn
    """
    title: str = Field(..., max_length=500, description="Tiêu đề tin tuyển dụng")
    company_name: Optional[str] = Field(None, max_length=300, description="Tên công ty")
    company_id: Optional[str] = Field(None, description="Khóa ngoại công ty")

    # Địa điểm đa điểm
    locations: List[JobLocation] = Field(default_factory=list, description="Danh sách địa điểm làm việc")
    location_province: Optional[str] = Field(None, max_length=100, description="Tỉnh / Thành phố chính")
    location_district: Optional[str] = Field(None, max_length=100, description="Quận / Huyện chính")
    location_full: Optional[str] = Field(None, description="Địa chỉ đầy đủ")

    # Môi trường & Hình thức làm việc
    workplace_type: WorkplaceType = Field("unknown", description="Môi trường làm việc: onsite, hybrid, remote, unknown")
    employment_type: str = Field("unknown", max_length=50, description="Hình thức: full-time, part-time, contract, intern, temporary, unknown")
    job_type: Optional[str] = Field(None, max_length=50, description="Hình thức làm việc cũ (tương thích ngược)")
    category: Optional[str] = Field(None, max_length=100, description="Danh mục / Ngành nghề")
    experience_level: Optional[str] = Field(None, max_length=100, description="Cấp bậc kinh nghiệm")
    required_skills: List[str] = Field(default_factory=list, description="Danh sách kỹ năng yêu cầu")

    # Lương
    salary_min: Optional[int] = Field(None, ge=0, description="Lương tối thiểu (VNĐ)")
    salary_max: Optional[int] = Field(None, ge=0, description="Lương tối đa (VNĐ)")
    salary_currency: str = Field("VND", max_length=10, description="Đơn vị tiền tệ")
    salary_period: SalaryPeriod = Field("month", description="Kỳ chi trả: month, year, hour, day, project, unknown")
    salary_text: Optional[str] = Field(None, max_length=200, description="Mô tả lương nguyên bản")

    # Nội dung
    description: Optional[str] = Field(None, description="Mô tả công việc")
    requirements: Optional[str] = Field(None, description="Yêu cầu công việc")

    # Mốc thời gian chuẩn xác
    posted_at: Optional[datetime] = Field(None, description="Thời điểm đăng tin gốc")
    updated_at: Optional[datetime] = Field(None, description="Thời điểm cập nhật bản ghi")
    deadline_at: Optional[datetime] = Field(None, description="Hạn chót nộp hồ sơ")
    expires_at: Optional[datetime] = Field(None, description="Hạn chót (tương thích ngược)")
    first_seen_at: Optional[datetime] = Field(None, description="Thời điểm phát hiện lần đầu")
    last_seen_at: Optional[datetime] = Field(None, description="Thời điểm quan sát thấy lần cuối")
    last_verified_at: Optional[datetime] = Field(None, description="Thời điểm xác minh lần cuối")

    # Nguồn & Định danh
    source_name: str = Field("unknown", max_length=100, description="Tên nguồn chuẩn hóa")
    source_platform: Optional[str] = Field(None, max_length=100, description="Nguồn cào dữ liệu (tương thích)")
    source_url: str = Field(..., description="Đường dẫn bài viết gốc")
    apply_url: Optional[str] = Field(None, description="Đường dẫn ứng tuyển trực tiếp")
    source_job_id: Optional[str] = Field(None, max_length=255, description="Mã tin trên hệ thống nguồn")

    # Trạng thái & Bằng chứng xác minh
    status: JobStatus = Field("unknown", description="Trạng thái tuyển dụng")
    status_reason: Optional[str] = Field(None, description="Lý do cho trạng thái")
    status_evidence: Optional[Dict[str, Any]] = Field(None, description="Bằng chứng xác thực")
    is_active: bool = Field(True, description="Trạng thái còn hiệu lực hiển thị")

    # Độ tin cậy & Chống trùng lặp
    extraction_confidence: float = Field(1.0, ge=0.0, le=1.0, description="Độ tin cậy trích xuất (0.0 - 1.0)")
    location_confidence: float = Field(1.0, ge=0.0, le=1.0, description="Độ tin cậy địa điểm (0.0 - 1.0)")
    raw_data_reference: Optional[str] = Field(None, description="Tham chiếu bản ghi thô")
    content_hash: Optional[str] = Field(None, max_length=64, description="Mã băm SHA256 chống trùng")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Dữ liệu nguyên bản JSON")

    @field_validator("required_skills", mode="before")
    @classmethod
    def normalize_required_skills(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(item) for item in v if item]
        if isinstance(v, str):
            clean = v.strip()
            if not clean:
                return []
            try:
                import json
                parsed = json.loads(clean)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item]
            except Exception:
                pass
            return [clean]
        return []

    @field_validator("locations", mode="before")
    @classmethod
    def normalize_locations(cls, v: Any) -> List[Any]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            clean = v.strip()
            if not clean:
                return []
            try:
                import json
                parsed = json.loads(clean)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return []

    @field_validator("status_evidence", mode="before")

    @classmethod
    def normalize_status_evidence(cls, v: Any) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            clean = v.strip()
            if not clean:
                return None
            try:
                import json
                parsed = json.loads(clean)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            return {"evidence_text": clean}
        return None

    @field_validator("raw_data", mode="before")
    @classmethod
    def normalize_raw_data(cls, v: Any) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            clean = v.strip()
            if not clean:
                return None
            try:
                import json
                parsed = json.loads(clean)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            return {"raw_text": clean}
        return None

    @field_validator(

        "posted_at",
        "updated_at",
        "deadline_at",
        "expires_at",
        "first_seen_at",
        "last_seen_at",
        "last_verified_at",
        mode="before",
    )
    @classmethod
    def ensure_timezone_aware(cls, v: Any) -> Optional[datetime]:
        """Đảm bảo mọi datetime đều chuẩn hóa sang timezone UTC"""
        if v is None:
            return None
        if isinstance(v, str):
            clean_str = v.strip()
            if not clean_str:
                return None
            try:
                # Hỗ trợ ISO string kết thúc bằng Z hoặc +00:00
                if clean_str.endswith("Z"):
                    clean_str = clean_str[:-1] + "+00:00"
                dt = datetime.fromisoformat(clean_str)
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            except Exception:
                return None
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return None

    @model_validator(mode="after")
    def validate_and_sync_job_data(self) -> "JobBase":
        """
        Quy tắc nghiệp vụ:
        1. Đồng bộ source_name <-> source_platform
        2. Đồng bộ deadline_at <-> expires_at
        3. Đồng bộ locations <-> location_province
        4. Xác thực trạng thái tuyển dụng:
           - Nếu deadline_at < now -> status BẮT BUỘC là 'expired'
           - Không tự sinh mặc định rằng thiếu hạn tuyển nghĩa là tin còn tuyển (không tự đặt active_confirmed)
           - Đồng bộ is_active theo status
        5. Tự động sinh content_hash nếu chưa có
        """
        now = datetime.now(timezone.utc)

        # 1. Nguồn
        if (not self.source_name or self.source_name == "unknown") and self.source_platform:
            self.source_name = self.source_platform
        elif not self.source_platform and self.source_name:
            self.source_platform = self.source_name

        # 2. Hạn chót
        if self.deadline_at is not None and self.expires_at is None:
            self.expires_at = self.deadline_at
        elif self.expires_at is not None and self.deadline_at is None:
            self.deadline_at = self.expires_at

        # 3. Địa điểm
        if not self.locations and (self.location_province or self.location_district or self.location_full):
            self.locations = [
                JobLocation(
                    province=self.location_province,
                    district=self.location_district,
                    address=self.location_full,
                    is_primary=True,
                )
            ]
        elif self.locations:
            primary = next((loc for loc in self.locations if loc.is_primary), self.locations[0])
            if not self.location_province and primary.province:
                self.location_province = primary.province
            if not self.location_district and primary.district:
                self.location_district = primary.district
            if not self.location_full and primary.address:
                self.location_full = primary.address

        # 4. Kiểm tra trạng thái tuyển dụng
        effective_deadline = self.deadline_at or self.expires_at
        if effective_deadline:
            dl_utc = (
                effective_deadline
                if effective_deadline.tzinfo
                else effective_deadline.replace(tzinfo=timezone.utc)
            )
            if dl_utc < now:
                self.status = "expired"
                if not self.status_reason:
                    self.status_reason = f"Đã qua hạn chót nộp hồ sơ ({dl_utc.date()})"
                self.is_active = False

        # Quy tắc: Thiếu hạn tuyển không được tự động coi là active_confirmed nếu không có bằng chứng
        if effective_deadline is None and self.status == "active_confirmed":
            has_verified_proof = bool(
                self.status_evidence
                and (self.status_evidence.get("verified") or self.status_evidence.get("url_status") == 200)
            )
            if not has_verified_proof:
                self.status = "active_likely"
                self.status_reason = "Tin phát hiện gần đây nhưng chưa có hạn nộp hoặc bằng chứng xác thực trực tiếp"

        # Đồng bộ cờ is_active
        if self.status in ["active_confirmed", "active_likely"]:
            self.is_active = True
        elif self.status in ["expired", "closed"]:
            self.is_active = False

        # 5. Sinh content_hash
        if not self.content_hash:
            c = (self.company_name or "").strip().lower()
            t = (self.title or "").strip().lower()
            p = (self.location_province or "").strip().lower()
            token = f"{c}::{t}::{p}"
            self.content_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        return self


class JobCreate(JobBase):
    """
    Schema tạo mới tin tuyển dụng (dùng bởi scraper/crawler và data pipeline)
    """
    pass


class JobUpdate(BaseModel):
    """
    Schema cập nhật thông tin tin tuyển dụng
    """
    title: Optional[str] = Field(None, max_length=500)
    company_name: Optional[str] = Field(None, max_length=300)
    company_id: Optional[str] = None
    locations: Optional[List[JobLocation]] = None
    location_province: Optional[str] = None
    location_district: Optional[str] = None
    location_full: Optional[str] = None
    workplace_type: Optional[WorkplaceType] = None
    employment_type: Optional[str] = None
    job_type: Optional[str] = None
    category: Optional[str] = None
    experience_level: Optional[str] = None
    required_skills: Optional[List[str]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[SalaryPeriod] = None
    salary_text: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    posted_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    source_name: Optional[str] = None
    source_platform: Optional[str] = None
    apply_url: Optional[str] = None
    source_job_id: Optional[str] = None
    status: Optional[JobStatus] = None
    status_reason: Optional[str] = None
    status_evidence: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    extraction_confidence: Optional[float] = None
    location_confidence: Optional[float] = None
    raw_data_reference: Optional[str] = None
    content_hash: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class JobResponse(JobBase):
    """
    Schema phản hồi thông tin chi tiết một tin tuyển dụng
    """
    id: str
    created_at: datetime
    updated_at: datetime
    crawled_at: datetime
    company: Optional[CompanyResponse] = None
    all_sources: Optional[List[Dict[str, Any]]] = Field(None, description="Danh sách các nguồn gốc nơi tin này xuất hiện")
    match_reasons: Optional[List[str]] = Field(None, description="Lý do xếp hạng và độ phù hợp với ý định tìm kiếm")
    match_score: Optional[float] = Field(None, description="Điểm độ phù hợp")
    ranking_breakdown: Optional[Dict[str, Any]] = Field(None, description="Chi tiết giải thích điểm số từng tín hiệu ranking đa chiều")

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
    suggested_relaxations: List[str] = Field(default_factory=list, description="Gợi ý nới lỏng bộ lọc khi không có kết quả khớp điều kiện cứng")
    diagnostics: Optional[Dict[str, Any]] = Field(None, description="Báo cáo chẩn đoán toàn trình tìm kiếm thông minh")


class JobSearchParams(BaseModel):
    """
    Tham số tìm kiếm và lọc dữ liệu việc làm
    """
    query: Optional[str] = Field(None, description="Từ khóa tìm kiếm trong tiêu đề hoặc mô tả")
    q: Optional[str] = Field(None, description="Từ khóa tìm kiếm (alias)")
    province: Optional[str] = Field(None, description="Lọc theo tỉnh thành")
    category: Optional[str] = Field(None, description="Lọc theo ngành nghề")
    workplace_type: Optional[str] = Field(None, description="Lọc theo nơi làm việc: onsite, hybrid, remote")
    experience_level: Optional[str] = Field(None, description="Cấp độ kinh nghiệm: intern, fresher, junior, middle, senior, lead")
    job_type: Optional[str] = Field(None, description="Lọc theo loại hình: full-time, part-time, remote, intern")
    salary_min: Optional[int] = Field(None, ge=0, description="Mức lương tối thiểu (VNĐ)")
    salary_max: Optional[int] = Field(None, ge=0, description="Mức lương tối đa (VNĐ)")
    company_name: Optional[str] = Field(None, description="Lọc theo tên doanh nghiệp tuyển dụng")
    source_platform: Optional[str] = Field(None, description="Nguồn cào: TopCV, VietnamWorks, ITviec...")
    source_name: Optional[str] = Field(None, description="Tên nguồn chuẩn hóa")
    status: Optional[str] = Field(None, description="Lọc theo trạng thái: active_confirmed, active_likely, expired, closed")
    verified_only: bool = Field(False, description="Chỉ lấy tin tuyển dụng đã xác minh (active_confirmed, active_likely)")
    page: int = Field(1, ge=1, description="Trang hiện tại")
    page_size: int = Field(20, ge=1, le=100, description="Số lượng mục trên một trang")
    sort_by: Optional[str] = Field("newest", description="Thứ tự sắp xếp: newest, relevance, salary_desc, salary_asc")
    live: bool = Field(False, description="Kích hoạt quét đa nguồn thời gian thực")
    strict_mode: bool = Field(False, description="Chế độ khớp khắt khe các ràng buộc cứng")
    saved: bool = Field(False, description="Chỉ lấy danh sách đã lưu")

