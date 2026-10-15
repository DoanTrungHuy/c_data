"""
Unit test suite for C_Data Universal Job Schema.
Tests:
1. Full data record (Dữ liệu đầy đủ)
2. Sparse / Minimum data record (Dữ liệu thiếu & defaults)
3. Date & Timezone normalization (UTC, ISO-8601, timezone-aware)
4. Status conventions & transitions (active_confirmed, active_likely, expired, closed, unknown)
5. Non-assumption of active status when deadline is missing
6. Location synchronization (locations JSON <-> location_province / district / full)
7. Deterministic content_hash generation
8. SQLite database persistence & indexing round-trip
"""

from datetime import datetime, timedelta, timezone
import json
import unittest
import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models.job import Job
from app.schemas.job import JobBase, JobCreate, JobLocation, JobResponse, JobUpdate


class TestUniversalJobSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database for testing schema and ORM operations
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db: Session = self.SessionLocal()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    # =========================================================================
    # 1. TEST DỮ LIỆU ĐẦY ĐỦ (FULL DATA RECORD)
    # =========================================================================
    def test_01_full_data_record_validation(self):
        """Kiểm tra bản ghi với 100% các trường schema mới và cũ đầy đủ."""
        now = datetime.now(timezone.utc)
        future_dl = now + timedelta(days=30)
        past_post = now - timedelta(days=2)

        payload = {
            "title": "Senior Cloud Infrastructure Engineer (AWS/DevOps)",
            "company_name": "FPT Software Quảng Ninh",
            "locations": [
                {
                    "province": "Quảng Ninh",
                    "district": "Hạ Long",
                    "address": "Tòa nhà FPT, Phường Bạch Đằng, TP. Hạ Long",
                    "is_primary": True,
                    "country": "Vietnam",
                },
                {
                    "province": "Hà Nội",
                    "district": "Cầu Giấy",
                    "address": "Tòa nhà FPT Cầu Giấy, Duy Tân",
                    "is_primary": False,
                    "country": "Vietnam",
                },
            ],
            "workplace_type": "hybrid",
            "employment_type": "full-time",
            "experience_level": "Senior (3 - 5 năm)",
            "required_skills": ["AWS", "Terraform", "Kubernetes", "Docker", "Python"],
            "salary_min": 35000000,
            "salary_max": 60000000,
            "salary_currency": "VND",
            "salary_period": "month",
            "salary_text": "35 - 60 triệu VNĐ",
            "description": "Quản trị hạ tầng điện toán đám mây và triển khai CI/CD cho các dự án quy mô lớn.",
            "requirements": "Tối thiểu 3 năm kinh nghiệm với AWS, Kubernetes và tự động hóa hạ tầng.",
            "posted_at": past_post.isoformat(),
            "updated_at": now.isoformat(),
            "deadline_at": future_dl.isoformat(),
            "first_seen_at": (now - timedelta(days=1)).isoformat(),
            "last_seen_at": now.isoformat(),
            "last_verified_at": now.isoformat(),
            "source_name": "Cổng Nghề Nghiệp FPT Software",
            "source_url": "https://fptsoftware.com/careers/cloud-infra-2026",
            "apply_url": "https://fptsoftware.com/careers/apply?id=cloud-infra-2026",
            "source_job_id": "fpt_cloud_2026_qn",
            "status": "active_confirmed",
            "status_reason": "Đã xác minh trực tiếp từ cổng việc làm FPT Software",
            "status_evidence": {
                "verified": True,
                "url_status": 200,
                "recruiter_email": "recruitment@fpt.com",
            },
            "extraction_confidence": 0.98,
            "location_confidence": 1.0,
            "raw_data_reference": "raw_snap_fpt_001",
        }

        # 1. Pydantic validation
        job_schema = JobCreate(**payload)
        self.assertEqual(job_schema.title, payload["title"])
        self.assertEqual(job_schema.workplace_type, "hybrid")
        self.assertEqual(job_schema.employment_type, "full-time")
        self.assertEqual(len(job_schema.locations), 2)
        self.assertEqual(job_schema.location_province, "Quảng Ninh")  # Primary location synced
        self.assertEqual(job_schema.salary_currency, "VND")
        self.assertEqual(job_schema.salary_period, "month")
        self.assertEqual(job_schema.status, "active_confirmed")
        self.assertTrue(job_schema.is_active)
        self.assertIsNotNone(job_schema.content_hash)
        self.assertEqual(len(job_schema.content_hash), 64)

        # 2. ORM roundtrip
        orm_job = Job(**job_schema.model_dump())
        orm_job.sync_universal_fields()
        self.db.add(orm_job)
        self.db.commit()

        # Query back
        saved = self.db.execute(select(Job).where(Job.source_url == payload["source_url"])).scalar_one()
        self.assertEqual(saved.workplace_type, "hybrid")
        self.assertEqual(saved.employment_type, "full-time")
        self.assertEqual(saved.salary_min, 35000000)
        self.assertEqual(saved.status, "active_confirmed")
        self.assertEqual(saved.source_name, "Cổng Nghề Nghiệp FPT Software")
        self.assertEqual(saved.source_platform, "Cổng Nghề Nghiệp FPT Software")  # Sync compatibility
        self.assertEqual(len(saved.required_skills), 5)
        self.assertEqual(saved.extraction_confidence, 0.98)

    # =========================================================================
    # 2. TEST DỮ LIỆU THIẾU (SPARSE / PARTIAL DATA RECORD)
    # =========================================================================
    def test_02_sparse_data_defaults(self):
        """Kiểm tra bản ghi dữ liệu tối thiểu chỉ có tiêu đề và URL nguồn."""
        minimal_payload = {
            "title": "Nhân viên Bán Hàng",
            "source_url": "https://example.com/job/minimal-123",
        }

        job_schema = JobCreate(**minimal_payload)

        # Kiểm tra các giá trị mặc định chuẩn xác
        self.assertEqual(job_schema.workplace_type, "unknown")
        self.assertEqual(job_schema.employment_type, "unknown")
        self.assertEqual(job_schema.status, "unknown")
        self.assertEqual(job_schema.salary_currency, "VND")
        self.assertEqual(job_schema.salary_period, "month")
        self.assertEqual(job_schema.locations, [])
        self.assertEqual(job_schema.required_skills, [])
        self.assertEqual(job_schema.extraction_confidence, 1.0)
        self.assertEqual(job_schema.location_confidence, 1.0)
        self.assertIsNotNone(job_schema.content_hash)

        # Lưu vào Database không bị lỗi NOT NULL
        orm_job = Job(**job_schema.model_dump())
        orm_job.sync_universal_fields()
        self.db.add(orm_job)
        self.db.commit()
        self.assertIsNotNone(orm_job.id)

    # =========================================================================
    # 3. TEST XỬ LÝ NGÀY THÁNG & TIMEZONE (DATE & TIMEZONE INTEGRITY)
    # =========================================================================
    def test_03_timezone_handling_and_normalization(self):
        """Đảm bảo các trường thời gian luôn lưu trữ và chuẩn hóa timezone UTC chính xác."""
        payload = {
            "title": "Frontend Developer",
            "source_url": "https://example.com/job/timezone-test",
            # ISO format with trailing Z
            "posted_at": "2026-10-15T08:00:00Z",
            # ISO format with timezone offset +07:00
            "deadline_at": "2026-11-20T23:59:59+07:00",
            # Naive datetime string without timezone
            "first_seen_at": "2026-10-15T10:30:00",
        }

        job = JobCreate(**payload)

        # 1. posted_at phải có tzinfo
        self.assertIsNotNone(job.posted_at.tzinfo)
        self.assertEqual(job.posted_at.utcoffset().total_seconds(), 0)

        # 2. deadline_at phải có tzinfo và chuyển đổi đúng mốc thời gian
        self.assertIsNotNone(job.deadline_at.tzinfo)

        # 3. first_seen_at naive phải được tự động gán timezone UTC
        self.assertIsNotNone(job.first_seen_at.tzinfo)
        self.assertEqual(job.first_seen_at.tzinfo, timezone.utc)

        # 4. expires_at và deadline_at đồng bộ 1-1
        self.assertEqual(job.expires_at, job.deadline_at)

        # 5. Invalid date string không làm ứng dụng crash mà trả về None
        invalid_payload = {
            "title": "Tester",
            "source_url": "https://example.com/job/invalid-date",
            "posted_at": "ngày hôm qua",
        }
        invalid_job = JobCreate(**invalid_payload)
        self.assertIsNone(invalid_job.posted_at)

    # =========================================================================
    # 4. TEST QUY ƯỚC TRẠNG THÁI & CHUYỂN TRẠNG THÁI (STATUS CONVENTIONS)
    # =========================================================================
    def test_04_status_expired_when_deadline_passed(self):
        """Tin tuyển dụng có hạn chót trong quá khứ BẮT BUỘC phải chuyển sang 'expired'."""
        now = datetime.now(timezone.utc)
        past_deadline = now - timedelta(days=5)

        payload = {
            "title": "Kỹ Sư Hệ Thống Cũ",
            "source_url": "https://example.com/job/expired-status-test",
            "deadline_at": past_deadline,
            "status": "active_confirmed",  # Cố tình truyền active nhưng đã quá hạn
        }

        job = JobCreate(**payload)

        # Trạng thái bắt buộc phải bị override thành 'expired'
        self.assertEqual(job.status, "expired")
        self.assertFalse(job.is_active)
        self.assertIn("Đã qua hạn chót", job.status_reason)

    def test_05_no_auto_assumption_when_deadline_missing(self):
        """Không tự sinh mặc định rằng thiếu hạn tuyển nghĩa là active_confirmed."""
        payload = {
            "title": "Chuyên Viên Pháp Chế",
            "source_url": "https://example.com/job/no-deadline-test",
            "deadline_at": None,
            "expires_at": None,
            "status": "active_confirmed",  # Truyền active_confirmed nhưng KHÔNG có bằng chứng
            "status_evidence": None,
        }

        job = JobCreate(**payload)

        # Không được phép giữ active_confirmed khi thiếu hạn tuyển và không có bằng chứng
        self.assertNotEqual(job.status, "active_confirmed")
        self.assertEqual(job.status, "active_likely")
        self.assertIn("chưa có hạn nộp hoặc bằng chứng", job.status_reason)

    def test_06_active_confirmed_allowed_with_evidence(self):
        """Được phép gắn 'active_confirmed' nếu có bằng chứng xác minh (evidence_proof)."""
        payload = {
            "title": "IT Helpdesk Resort",
            "source_url": "https://example.com/job/evidence-confirmed-test",
            "deadline_at": None,
            "status": "active_confirmed",
            "status_evidence": {
                "verified": True,
                "url_status": 200,
                "source_type": "official_portal",
            },
        }

        job = JobCreate(**payload)
        self.assertEqual(job.status, "active_confirmed")
        self.assertTrue(job.is_active)

    def test_07_closed_status_disables_active_flag(self):
        """Trạng thái 'closed' tự động tắt cờ is_active."""
        payload = {
            "title": "Nhân viên Kho Vận",
            "source_url": "https://example.com/job/closed-test",
            "status": "closed",
            "status_reason": "Nhà tuyển dụng thông báo đã tuyển đủ số lượng",
        }

        job = JobCreate(**payload)
        self.assertEqual(job.status, "closed")
        self.assertFalse(job.is_active)

    # =========================================================================
    # 5. TEST ĐỒNG BỘ ĐỊA ĐIỂM (LOCATION SYNCHRONIZATION)
    # =========================================================================
    def test_08_location_synchronization(self):
        """Đồng bộ hai chiều giữa mảng locations và location_province/district/full."""
        # A. Cung cấp location_province -> locations tự sinh
        payload_a = {
            "title": "Kỹ Sư Mỏ TKV",
            "source_url": "https://example.com/job/loc-sync-a",
            "location_province": "Quảng Ninh",
            "location_district": "Cẩm Phả",
            "location_full": "Mỏ than Đèo Nai, Cẩm Phả, Quảng Ninh",
        }
        job_a = JobCreate(**payload_a)
        self.assertEqual(len(job_a.locations), 1)
        self.assertEqual(job_a.locations[0].province, "Quảng Ninh")
        self.assertEqual(job_a.locations[0].district, "Cẩm Phả")

        # B. Cung cấp mảng locations -> location_province tự trích xuất từ primary
        payload_b = {
            "title": "Lập Trình Viên React",
            "source_url": "https://example.com/job/loc-sync-b",
            "locations": [
                {
                    "province": "Đà Nẵng",
                    "district": "Hải Châu",
                    "address": "Bạch Đằng, Hải Châu, Đà Nẵng",
                    "is_primary": True,
                }
            ],
        }
        job_b = JobCreate(**payload_b)
        self.assertEqual(job_b.location_province, "Đà Nẵng")
        self.assertEqual(job_b.location_district, "Hải Châu")
        self.assertEqual(job_b.location_full, "Bạch Đằng, Hải Châu, Đà Nẵng")

    # =========================================================================
    # 6. TEST MÃ BĂM NỘI DUNG (CONTENT HASH STABILITY & DEDUPLICATION)
    # =========================================================================
    def test_09_content_hash_stability(self):
        """Kiểm tra mã băm SHA-256 ổn định, không phân biệt hoa thường và khoảng trắng."""
        job1 = JobCreate(
            title="Kỹ Sư CNTT",
            company_name="Bệnh Viện Vinmec",
            location_province="Quảng Ninh",
            source_url="https://example.com/job/hash-1",
        )

        job2 = JobCreate(
            title="  kỹ sư cntt  ",
            company_name="  bệnh viện vinmec  ",
            location_province="quảng ninh",
            source_url="https://example.com/job/hash-2",
        )

        # Hai tin có cùng nội dung chuẩn hóa phải có cùng content_hash
        self.assertEqual(job1.content_hash, job2.content_hash)

        # Tin khác công ty phải có content_hash khác
        job3 = JobCreate(
            title="Kỹ Sư CNTT",
            company_name="Bệnh Viện Bãi Cháy",
            location_province="Quảng Ninh",
            source_url="https://example.com/job/hash-3",
        )
        self.assertNotEqual(job1.content_hash, job3.content_hash)


if __name__ == "__main__":
    unittest.main()
