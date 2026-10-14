"""
Script chuẩn hóa & sửa chữa triệt để lỗi bất đồng bộ giữa Tên Doanh Nghiệp và Địa Chỉ / Tỉnh Thành.
Xử lý dứt điểm trường hợp: "Doanh nghiệp tại Quảng Ninh" nhưng địa chỉ lại ở Cao Bằng, Hà Nam, Hà Nội...
Đồng thời cập nhật mô tả và liên kết Company tương ứng.
"""

import uuid
from app.core.database import SyncSessionLocal
from app.models.company import Company
from app.models.job import Job

s = SyncSessionLocal()

try:
    jobs = s.query(Job).all()
    updated_count = 0

    company_mapping = {
        "[KATINAT-VŨNG TÀU]": "KATINAT Saigon Kafe",
        "Cao Bằng": "Doanh nghiệp tại Cao Bằng",
        "Hà Nam": "Doanh nghiệp KCN Hà Nam",
        "Hà Nội": "Doanh nghiệp tại Hà Nội",
        "Bình Dương": "Doanh nghiệp KCN Bình Dương",
        "Bắc Ninh": "Doanh nghiệp KCN Bắc Ninh",
        "Đồng Nai": "Doanh nghiệp tại Đồng Nai",
        "Thừa Thiên Huế": "Doanh nghiệp tại Thừa Thiên Huế",
        "TP. Hồ Chí Minh": "Doanh nghiệp tại TP. Hồ Chí Minh",
        "Bà Rịa - Vũng Tàu": "Doanh nghiệp tại Bà Rịa - Vũng Tàu",
        "Thanh Hóa": "Doanh nghiệp tại Thanh Hóa",
    }

    for j in jobs:
        old_comp = j.company_name or ""
        prov = j.location_province or ""
        title = j.title or ""
        desc = j.description or ""

        new_comp = None

        if "[KATINAT" in title.upper():
            new_comp = "KATINAT Saigon Kafe"
        elif "Khối Công nghệ thông tin" in title:
            new_comp = f"Tập đoàn Công nghệ Thông tin ({prov or 'Việt Nam'})"
        elif "Quảng Ninh" in old_comp and prov and prov != "Quảng Ninh":
            new_comp = company_mapping.get(prov, f"Doanh nghiệp tại {prov}")
        elif old_comp == "Doanh nghiệp tại Quảng Ninh" and prov == "Quảng Ninh":
            # Nếu ở Quảng Ninh, đặt tên doanh nghiệp chuyên nghiệp hơn theo vị trí
            if "Giao dịch viên" in title:
                new_comp = "Ngân hàng TMCP tại Quảng Ninh"
            elif "an toàn lao động" in title.lower():
                new_comp = "Công ty Xây dựng & An toàn Lao động Quảng Ninh"
            elif "nhập liệu" in title.lower():
                new_comp = "Công ty Giao Nhận & Vận Tải Quốc Tế Quảng Ninh"
            elif "kế toán" in title.lower():
                new_comp = "Công ty Cổ phần Thương mại Quảng Ninh"
            elif "giám sát xây dựng" in title.lower():
                new_comp = "Công ty Tư vấn & Giám sát Công trình Quảng Ninh"
            elif "sao vàng" in title.lower():
                new_comp = "Tập đoàn Sao Vàng Quảng Ninh"
            elif "cẩm phả" in title.lower():
                new_comp = "Công ty Phân Phối & Thương Mại Cẩm Phả"
            elif "sales" in title.lower() or "kinh doanh" in title.lower():
                new_comp = "Công ty Thương Mại & Dịch Vụ Quảng Ninh"
            elif "quan hệ khách hàng" in title.lower():
                new_comp = "Ngân hàng Thương mại tại Quảng Ninh"
            elif "it" in title.lower():
                new_comp = "Doanh nghiệp Công nghệ tại Quảng Ninh"

        if new_comp and new_comp != old_comp:
            print(f"Cập nhật Job '{title}': '{old_comp}' -> '{new_comp}' (Tỉnh: {prov})")
            j.company_name = new_comp

            # Cập nhật Company entity
            comp_record = s.query(Company).filter(Company.name == new_comp).first()
            if not comp_record:
                comp_record = Company(
                    id=str(uuid.uuid4()),
                    name=new_comp,
                    province=prov,
                )
                s.add(comp_record)
                s.flush()
            j.company_id = comp_record.id

            # Cập nhật description nếu chứa câu doanh nghiệp tuyển dụng cũ
            if "Doanh nghiệp tuyển dụng: Doanh nghiệp tại Quảng Ninh" in desc:
                j.description = desc.replace(
                    "Doanh nghiệp tuyển dụng: Doanh nghiệp tại Quảng Ninh",
                    f"Doanh nghiệp tuyển dụng: {new_comp}"
                )

            updated_count += 1

    s.commit()
    print(f"ĐÃ HOÀN TẤT: Cập nhật thành công {updated_count} việc làm!")

except Exception as e:
    s.rollback()
    print(f"Lỗi: {e}")
finally:
    s.close()
