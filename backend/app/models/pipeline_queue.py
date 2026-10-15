"""
SQLAlchemy Model for C_Data Pipeline Message Queue System.
Provides persistent storage, ACID guarantees, transactional state transitions,
distributed tracing, retry with exponential backoff, and Dead-Letter Queue (DLQ).
"""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from app.core.database import Base


class PipelineMessage(Base):
    """
    Bảng lưu trữ thông điệp hàng đợi của Pipeline xử lý tuyển dụng đa giai đoạn.
    Hỗ trợ 7 giai đoạn xử lý:
    1. discover_jobs
    2. fetch_job_detail
    3. normalize_job
    4. verify_job_status
    5. deduplicate_job
    6. index_job
    7. refresh_job_status
    """
    __tablename__ = "pipeline_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(64), nullable=False, index=True, doc="Định danh tác vụ logic")
    trace_id = Column(String(64), nullable=False, index=True, doc="Distributed trace ID xuyên suốt 7 giai đoạn")
    parent_message_id = Column(String(36), nullable=True, index=True, doc="ID của message giai đoạn trước")

    # Giai đoạn và Nguồn
    stage = Column(String(32), nullable=False, index=True, doc="Tên giai đoạn hiện tại trong pipeline")
    source_id = Column(String(64), nullable=False, index=True, doc="ID nguồn từ Source Registry (careerviet, sun_group, v.v.)")
    
    # Khóa chống lặp (Idempotency Key)
    idempotency_key = Column(String(128), nullable=False, unique=True, index=True, doc="Khóa duy nhất ngăn chặn xử lý trùng")

    # Dữ liệu & Tham chiếu
    payload = Column(Text, nullable=True, doc="Dữ liệu JSON gọn nhẹ của message (không chứa HTML thô lớn)")
    payload_ref = Column(String(256), nullable=True, doc="URI hoặc ID tham chiếu tới tệp HTML/dữ liệu lớn lưu ngoài")

    # Trạng thái vòng đời: pending, processing, completed, failed_retryable, dead_letter
    status = Column(String(32), nullable=False, default="pending", index=True)
    
    # Cơ chế Retry & Exponential Backoff
    attempt_count = Column(Integer, nullable=False, default=0, doc="Số lần đã thử thực thi")
    max_retries = Column(Integer, nullable=False, default=3, doc="Số lần thử tối đa trước khi đưa vào DLQ")
    next_run_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True, doc="Mốc thời gian chạy tiếp theo")
    
    # Khóa Worker và phục hồi sau sự cố (Worker Crash Recovery)
    locked_at = Column(DateTime, nullable=True, doc="Thời điểm worker nhận xử lý message")
    locked_by = Column(String(64), nullable=True, doc="Định danh worker đang giữ khóa tác vụ")

    # Lỗi & Phân loại lỗi
    last_error = Column(Text, nullable=True, doc="Chi tiết lỗi gặp phải lần gần nhất")
    error_type = Column(String(32), nullable=True, default="none", doc="Phân loại: transient, permanent, none")

    # Mốc thời gian
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_pipeline_messages_stage_status_next_run", "stage", "status", "next_run_at"),
        Index("ix_pipeline_messages_source_status", "source_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<PipelineMessage id={self.id} stage={self.stage} source={self.source_id} status={self.status} attempts={self.attempt_count}>"
