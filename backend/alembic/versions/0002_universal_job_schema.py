"""universal_job_schema

Revision ID: 0002_universal
Revises: 0001_initial
Create Date: 2026-10-15 02:40:00.000000

"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002_universal"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sử dụng batch_alter_table để tương thích hoàn toàn cả SQLite và PostgreSQL
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        # 1. Địa điểm đa điểm
        batch_op.add_column(sa.Column("locations", sa.JSON(), nullable=True))

        # 2. Môi trường & Hình thức làm việc
        batch_op.add_column(sa.Column("workplace_type", sa.String(length=20), server_default="unknown", nullable=False))
        batch_op.add_column(sa.Column("employment_type", sa.String(length=50), server_default="unknown", nullable=False))
        batch_op.add_column(sa.Column("required_skills", sa.JSON(), nullable=True))

        # 3. Lương & Kỳ chi trả
        batch_op.add_column(sa.Column("salary_currency", sa.String(length=10), server_default="VND", nullable=False))
        batch_op.add_column(sa.Column("salary_period", sa.String(length=20), server_default="month", nullable=False))

        # 4. Mốc thời gian chuẩn xác
        batch_op.add_column(sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
        batch_op.add_column(sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
        batch_op.add_column(sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True))

        # 5. Nguồn & Định danh
        batch_op.add_column(sa.Column("source_name", sa.String(length=100), server_default="unknown", nullable=False))
        batch_op.add_column(sa.Column("apply_url", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("source_job_id", sa.String(length=255), nullable=True))

        # 6. Trạng thái & Bằng chứng xác minh
        batch_op.add_column(sa.Column("status", sa.String(length=50), server_default="unknown", nullable=False))
        batch_op.add_column(sa.Column("status_reason", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("status_evidence", sa.JSON(), nullable=True))

        # 7. Độ tin cậy & Chống trùng lặp
        batch_op.add_column(sa.Column("extraction_confidence", sa.Float(), server_default="1.0", nullable=False))
        batch_op.add_column(sa.Column("location_confidence", sa.Float(), server_default="1.0", nullable=False))
        batch_op.add_column(sa.Column("raw_data_reference", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("content_hash", sa.String(length=64), nullable=True))

        # Tạo index cho các trường tìm kiếm và lọc dữ liệu chính
        batch_op.create_index(op.f("ix_jobs_workplace_type"), ["workplace_type"], unique=False)
        batch_op.create_index(op.f("ix_jobs_employment_type"), ["employment_type"], unique=False)
        batch_op.create_index(op.f("ix_jobs_source_name"), ["source_name"], unique=False)
        batch_op.create_index(op.f("ix_jobs_deadline_at"), ["deadline_at"], unique=False)
        batch_op.create_index(op.f("ix_jobs_first_seen_at"), ["first_seen_at"], unique=False)
        batch_op.create_index(op.f("ix_jobs_last_seen_at"), ["last_seen_at"], unique=False)
        batch_op.create_index(op.f("ix_jobs_last_verified_at"), ["last_verified_at"], unique=False)
        batch_op.create_index(op.f("ix_jobs_status"), ["status"], unique=False)
        batch_op.create_index(op.f("ix_jobs_content_hash"), ["content_hash"], unique=False)
        batch_op.create_index(op.f("ix_jobs_source_job_id"), ["source_job_id"], unique=False)

    # 8. Thực hiện data backfill cho toàn bộ các bản ghi hiện có
    connection = op.get_bind()
    jobs_table = sa.table(
        "jobs",
        sa.column("id", sa.String),
        sa.column("title", sa.String),
        sa.column("company_name", sa.String),
        sa.column("location_province", sa.String),
        sa.column("location_district", sa.String),
        sa.column("location_full", sa.Text),
        sa.column("job_type", sa.String),
        sa.column("source_platform", sa.String),
        sa.column("source_name", sa.String),
        sa.column("source_url", sa.Text),
        sa.column("expires_at", sa.DateTime),
        sa.column("deadline_at", sa.DateTime),
        sa.column("crawled_at", sa.DateTime),
        sa.column("first_seen_at", sa.DateTime),
        sa.column("last_seen_at", sa.DateTime),
        sa.column("last_verified_at", sa.DateTime),
        sa.column("is_active", sa.Boolean),
        sa.column("status", sa.String),
        sa.column("status_reason", sa.Text),
        sa.column("status_evidence", sa.JSON),
        sa.column("workplace_type", sa.String),
        sa.column("employment_type", sa.String),
        sa.column("locations", sa.JSON),
        sa.column("content_hash", sa.String),
        sa.column("extraction_confidence", sa.Float),
        sa.column("location_confidence", sa.Float),
        sa.column("raw_data_reference", sa.Text),
        sa.column("apply_url", sa.Text),
        sa.column("source_job_id", sa.String),
        sa.column("salary_currency", sa.String),
        sa.column("salary_period", sa.String),
        sa.column("required_skills", sa.JSON),
        sa.column("raw_data", sa.JSON),
    )

    now = datetime.now(timezone.utc)
    select_stmt = sa.select(
        jobs_table.c.id,
        jobs_table.c.title,
        jobs_table.c.company_name,
        jobs_table.c.location_province,
        jobs_table.c.location_district,
        jobs_table.c.location_full,
        jobs_table.c.job_type,
        jobs_table.c.source_platform,
        jobs_table.c.source_url,
        jobs_table.c.expires_at,
        jobs_table.c.crawled_at,
        jobs_table.c.is_active,
        jobs_table.c.raw_data,
    )
    rows = connection.execute(select_stmt).fetchall()

    for row in rows:
        jid, title, comp, prov, dist, loc_full, jtype, splat, surl, exp, crw, act, raw = row

        # Đồng bộ nguồn
        s_name = splat or "unknown"

        # Đồng bộ hạn chót
        d_line = exp

        # Đồng bộ first_seen / last_seen
        f_seen = crw or now
        l_seen = crw or now

        # Đồng bộ địa điểm
        locs = []
        if prov or dist or loc_full:
            locs = [{"province": prov, "district": dist, "address": loc_full, "is_primary": True}]

        # Đồng bộ workplace_type
        wp_type = "unknown"
        jt_str = (jtype or "").lower()
        if "remote" in jt_str or "từ xa" in jt_str:
            wp_type = "remote"
        elif "hybrid" in jt_str:
            wp_type = "hybrid"
        elif prov or "full-time" in jt_str or "part-time" in jt_str:
            wp_type = "onsite"

        # Đồng bộ employment_type
        emp_type = "unknown"
        if "part-time" in jt_str or "bán thời gian" in jt_str:
            emp_type = "part-time"
        elif "intern" in jt_str or "thực tập" in jt_str:
            emp_type = "intern"
        elif "contract" in jt_str or "hợp đồng" in jt_str:
            emp_type = "contract"
        elif "full-time" in jt_str or "toàn thời gian" in jt_str:
            emp_type = "full-time"

        # Tính toán content_hash
        c_clean = (comp or "").strip().lower()
        t_clean = (title or "").strip().lower()
        p_clean = (prov or "").strip().lower()
        chash = hashlib.sha256(f"{c_clean}::{t_clean}::{p_clean}".encode("utf-8")).hexdigest()

        # Xác định trạng thái chuẩn xác
        has_evidence = False
        evidence_data = None
        if raw and isinstance(raw, dict):
            if "evidence_proof" in raw:
                has_evidence = True
                evidence_data = raw.get("evidence_proof")

        status_val = "unknown"
        status_rsn = "Khởi tạo từ dữ liệu cào"

        if exp:
            exp_utc = exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
            if exp_utc < now:
                status_val = "expired"
                status_rsn = f"Hạn nộp hồ sơ đã qua ({exp_utc.date()})"
            elif has_evidence and evidence_data.get("verified"):
                status_val = "active_confirmed"
                status_rsn = "Có bằng chứng dẫn chứng đăng tuyển xác thực"
            elif act:
                status_val = "active_likely"
                status_rsn = "Tin tuyển dụng còn hạn nộp hồ sơ"
            else:
                status_val = "closed"
                status_rsn = "Tin đã đóng hoặc đánh dấu dừng tuyển"
        else:
            # Quy tắc: Thiếu hạn tuyển KHÔNG tự sinh mặc định là còn tuyển
            if has_evidence and evidence_data.get("verified"):
                status_val = "active_confirmed"
                status_rsn = "Xác thực trực tiếp từ cổng tuyển dụng chính thức"
            elif act:
                status_val = "active_likely"
                status_rsn = "Mới phát hiện trong chu kỳ cào gần nhất"
            else:
                status_val = "unknown"
                status_rsn = "Không có thông tin hạn tuyển và chưa xác thực"

        update_stmt = (
            jobs_table.update()
            .where(jobs_table.c.id == jid)
            .values(
                source_name=s_name,
                deadline_at=d_line,
                first_seen_at=f_seen,
                last_seen_at=l_seen,
                locations=locs,
                workplace_type=wp_type,
                employment_type=emp_type,
                content_hash=chash,
                status=status_val,
                status_reason=status_rsn,
                status_evidence=evidence_data,
                extraction_confidence=1.0,
                location_confidence=1.0,
            )
        )
        connection.execute(update_stmt)


def downgrade() -> None:
    with op.batch_alter_table("jobs", schema=None) as batch_op:
        batch_op.drop_index(op.f("ix_jobs_source_job_id"))
        batch_op.drop_index(op.f("ix_jobs_content_hash"))
        batch_op.drop_index(op.f("ix_jobs_status"))
        batch_op.drop_index(op.f("ix_jobs_last_verified_at"))
        batch_op.drop_index(op.f("ix_jobs_last_seen_at"))
        batch_op.drop_index(op.f("ix_jobs_first_seen_at"))
        batch_op.drop_index(op.f("ix_jobs_deadline_at"))
        batch_op.drop_index(op.f("ix_jobs_source_name"))
        batch_op.drop_index(op.f("ix_jobs_employment_type"))
        batch_op.drop_index(op.f("ix_jobs_workplace_type"))

        batch_op.drop_column("content_hash")
        batch_op.drop_column("raw_data_reference")
        batch_op.drop_column("location_confidence")
        batch_op.drop_column("extraction_confidence")
        batch_op.drop_column("status_evidence")
        batch_op.drop_column("status_reason")
        batch_op.drop_column("status")
        batch_op.drop_column("source_job_id")
        batch_op.drop_column("apply_url")
        batch_op.drop_column("source_name")
        batch_op.drop_column("last_verified_at")
        batch_op.drop_column("last_seen_at")
        batch_op.drop_column("first_seen_at")
        batch_op.drop_column("deadline_at")
        batch_op.drop_column("salary_period")
        batch_op.drop_column("salary_currency")
        batch_op.drop_column("required_skills")
        batch_op.drop_column("employment_type")
        batch_op.drop_column("workplace_type")
        batch_op.drop_column("locations")
