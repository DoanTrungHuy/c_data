"""
Default Product Configuration for C_Data Platform (Master Prompt Section 2).
Defines centralized product defaults, location preferences, seniority rankings,
IT domain keywords, and field penalty rules.
Can be modified dynamically without rewriting any crawler adapters.
"""

from typing import List, Set
from pydantic import BaseModel, Field


class ProductSearchConfig(BaseModel):
    """Cấu hình tìm kiếm & sàng lọc mặc định của hệ thống C_Data"""
    
    # 1. Địa bàn ưu tiên
    primary_city: str = Field(default="Hạ Long", description="Thành phố ưu tiên số 1")
    primary_province: str = Field(default="Quảng Ninh", description="Tỉnh thành ưu tiên số 1")
    secondary_allowed_provinces: List[str] = Field(
        default=["Hà Nội"],
        description="Các tỉnh thành có thể mở rộng bằng bộ lọc địa điểm"
    )

    # 2. Ngành nghề ưu tiên (CNTT và mọi công việc có nhiệm vụ CNTT thực chất)
    it_core_categories: List[str] = Field(
        default=[
            "Software Development",
            "Backend",
            "Frontend",
            "Fullstack",
            "Mobile App",
            "Data Engineering",
            "Data Analysis",
            "Database Administration (DBA)",
            "IT Support",
            "IT Helpdesk",
            "IT Officer",
            "IT Executive",
            "System Administration",
            "Network Engineering",
            "NOC / SOC / Security",
            "ERP / Business Application",
            "Hospitality IT (IT Khách sạn / Resort)",
            "Healthcare IT (HIS / LIS / PACS / EMR)",
            "Application Support & Implementation",
            "QA / QC / Software Tester",
            "DevOps / Cloud Infrastructure",
        ]
    )

    # 3. Cấp bậc ưu tiên: Ưu tiên tuyển dụng sinh viên, mới ra trường, người mới vào nghề
    priority_seniorities: List[str] = Field(
        default=["Intern", "Fresher", "Junior", "Không yêu cầu kinh nghiệm"]
    )

    # 4. Hình thức làm việc hỗ trợ
    allowed_work_types: List[str] = Field(
        default=["Full-time", "Part-time", "Internship", "Contract", "Hybrid", "Remote", "On-site"]
    )

    # 5. Tiêu chí văn phòng vs Hiện trường (Field travel penalty)
    # Ưu tiên công việc văn phòng / tại chỗ. Hạ thấp thứ hạng các việc leo trèo / đi xa
    field_work_penalty_keywords: List[str] = Field(
        default=[
            "leo cao",
            "kéo cáp ngoài trời",
            "thực địa vùng sâu",
            "thường xuyên đi công tác tỉnh xa",
            "lắp đặt cột viễn thông",
            "trèo trụ điện",
            "hiện trường lưu động",
        ]
    )

    # 6. Từ khóa nhận diện nhiệm vụ CNTT cho các chức danh không có chữ "IT"
    it_task_indicators: List[str] = Field(
        default=[
            "cài đặt phần mềm",
            "quản trị hệ thống máy tính",
            "khắc phục sự cố mạng lan",
            "bảo trì máy chủ",
            "quản lý cơ sở dữ liệu",
            "vận hành phần mềm his",
            "vận hành phần mềm pms",
            "vận hành hệ thống erp",
            "hỗ trợ người dùng đầu cuối",
            "troubleshoot network",
            "backup dữ liệu",
            "quản lý camera an ninh",
            "hỗ trợ kỹ thuật phần cứng",
            "triển khai phần mềm",
            "kiểm thử phần mềm",
        ]
    )


# Singleton instance cấu hình toàn cục
product_config = ProductSearchConfig()
