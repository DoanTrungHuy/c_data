"""
Verification test suite for C_Data crawlers module.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from crawlers.utils import (
    ALL_63_PROVINCES,
    PROVINCE_ALIASES,
    clean_html,
    detect_experience_level,
    detect_job_category,
    extract_salary_range,
    normalize_job_type,
    normalize_location,
    normalize_province,
)
from crawlers import (
    BaseCrawler,
    CareerBuilderCrawler,
    TimViecNhanhCrawler,
    TopCVCrawler,
    VietnamWorksCrawler,
    get_all_crawlers,
    get_crawler_by_name,
    get_crawler_status,
)
from app.models.job import Job
from app.core.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def run_tests():
    print("=== 1. Checking 63 Provinces ===")
    assert len(ALL_63_PROVINCES) == 63, f"Expected 63 provinces, got {len(ALL_63_PROVINCES)}"
    print(f"Verified {len(ALL_63_PROVINCES)} provinces.")

    print("\n=== 2. Checking Salary Parsing ===")
    salary_cases = [
        ("8 - 12 triệu", (8000000, 12000000)),
        ("Trên 15 triệu", (15000000, None)),
        ("Thỏa thuận", (None, None)),
        ("8-12 tr", (8000000, 12000000)),
        ("15.000.000 - 20.000.000 VNĐ", (15000000, 20000000)),
        ("Dưới 10 triệu", (None, 10000000)),
        ("$1,000 - $2,000", (25400000, 50800000)),
        ("1000 - 2000 USD", (25400000, 50800000)),
        ("2.5 - 3.5 triệu", (2500000, 3500000)),
    ]
    for text, expected in salary_cases:
        res = extract_salary_range(text)
        print(f"  '{text}' -> {res}")
        assert res == expected, f"Failed for '{text}': got {res}, expected {expected}"
    print("Salary parsing verified successfully.")

    print("\n=== 3. Checking Province Aliases & Normalization ===")
    province_cases = [
        ("HN", "Hà Nội"),
        ("ha noi", "Hà Nội"),
        ("Hanoi", "Hà Nội"),
        ("HCM", "TP. Hồ Chí Minh"),
        ("Tp.HCM", "TP. Hồ Chí Minh"),
        ("TP. Hồ Chí Minh", "TP. Hồ Chí Minh"),
        ("Sài Gòn", "TP. Hồ Chí Minh"),
        ("QN", "Quảng Ninh"),
        ("Quảng Ninh", "Quảng Ninh"),
        ("Hạ Long, Quảng Ninh", "Quảng Ninh"),
        ("Đà Nẵng", "Đà Nẵng"),
        ("Bình Dương", "Bình Dương"),
        ("Đồng Nai", "Đồng Nai"),
        ("Bắc Ninh", "Bắc Ninh"),
        ("Cần Thơ", "Cần Thơ"),
        ("Bà Rịa - Vũng Tàu", "Bà Rịa - Vũng Tàu"),
        ("Vũng Tàu", "Bà Rịa - Vũng Tàu"),
    ]
    for text, expected in province_cases:
        res = normalize_province(text)
        print(f"  '{text}' -> {res}")
        assert res == expected, f"Failed for '{text}': got {res}, expected {expected}"
    print("Province normalization verified successfully.")

    print("\n=== 4. Checking Job Types & Experience Detection ===")
    assert normalize_job_type("Toàn thời gian") == "full-time"
    assert normalize_job_type("Part-time theo ca") == "part-time"
    assert normalize_job_type("Làm việc từ xa (Remote)") == "remote"
    assert normalize_job_type("Thực tập sinh Intern") == "intern"
    assert normalize_job_type("Cộng tác viên freelance") == "freelance"

    assert detect_experience_level("Chấp nhận sinh viên mới ra trường không cần kinh nghiệm") == "Không yêu cầu kinh nghiệm"
    assert detect_experience_level("Yêu cầu 1 - 2 năm kinh nghiệm") == "1 - 2 năm"
    assert detect_experience_level("Có ít nhất 3 năm kinh nghiệm trong ngành") == "3 - 5 năm"
    assert detect_experience_level("Vị trí Trưởng phòng kinh doanh") == "Quản lý / Trưởng phòng"
    print("Job types and experience detection verified successfully.")

    print("\n=== 5. Checking Category Detection ===")
    assert detect_job_category("Senior Python Backend Developer") == "IT / Phần mềm"
    assert detect_job_category("Chuyên viên Digital Marketing SEO & Ads") == "Marketing / Truyền thông"
    assert detect_job_category("Nhân viên Kế toán tổng hợp") == "Kế toán / Kiểm toán / Tài chính"
    assert detect_job_category("Nhân viên Bán hàng Showroom") == "Bán hàng / Kinh doanh"
    print("Job category detection verified successfully.")

    print("\n=== 6. Checking Crawlers Instantiation ===")
    crawlers = get_all_crawlers()
    assert len(crawlers) == 4
    names = [c.platform_name for c in crawlers]
    assert set(names) == {"topcv", "careerbuilder", "vietnamworks", "timviecnhanh"}
    print(f"All crawlers instantiated: {names}")

    for name in ["topcv", "careerbuilder", "vietnamworks", "timviecnhanh"]:
        c = get_crawler_by_name(name)
        assert c is not None
        assert c.platform_name == name
    print("get_crawler_by_name verified successfully.")

    print("\n=== 7. Testing save_jobs Upsert with SQLite in-memory DB ===")
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    crawler = get_crawler_by_name("topcv", db_session=session)
    job_payload = [
        {
            "title": "Senior Python Developer",
            "company_name": "Antigravity Tech Corp",
            "description": "Lập trình backend bằng Python, FastAPI, Celery, PostgreSQL.",
            "requirements": "3-5 năm kinh nghiệm làm việc với Python và Microservices.",
            "salary_min": 25000000,
            "salary_max": 40000000,
            "salary_text": "25 - 40 triệu",
            "location_province": "Hà Nội",
            "location_district": "Cầu Giấy",
            "location_full": "Tầng 5, Tòa nhà Keangnam, Cầu Giấy, Hà Nội",
            "job_type": "full-time",
            "category": "IT / Phần mềm",
            "experience_level": "3 - 5 năm",
            "source_platform": "topcv",
            "source_url": "https://www.topcv.vn/viec-lam/senior-python-dev-test-1",
        }
    ]

    # Insert 1st time
    saved_count = crawler.save_jobs(job_payload)
    assert saved_count == 1, f"Expected 1 saved job, got {saved_count}"
    assert session.query(Job).count() == 1

    # Insert same source_url 2nd time (should update, not insert duplicate)
    job_payload[0]["salary_min"] = 30000000
    job_payload[0]["salary_max"] = 45000000
    job_payload[0]["salary_text"] = "30 - 45 triệu"
    saved_count_2 = crawler.save_jobs(job_payload)
    assert saved_count_2 == 0, f"Expected 0 new jobs, got {saved_count_2}"
    assert session.query(Job).count() == 1

    # Verify updated values in DB
    saved_job = session.query(Job).filter_by(source_url="https://www.topcv.vn/viec-lam/senior-python-dev-test-1").first()
    assert saved_job is not None
    assert saved_job.salary_min == 30000000
    assert saved_job.salary_max == 45000000
    assert saved_job.salary_text == "30 - 45 triệu"
    print("Database upsert deduplication verified successfully.")

    session.close()

    print("\n=== 8. Checking Scheduler Status ===")
    status = get_crawler_status()
    assert "crawlers" in status
    for p in ["topcv", "careerbuilder", "vietnamworks", "timviecnhanh"]:
        assert p in status["crawlers"]
    print("Crawler status reporting verified successfully.")

    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
