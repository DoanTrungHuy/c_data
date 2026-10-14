import logging
from typing import Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.province import Province

logger = logging.getLogger(__name__)

# Danh sách đầy đủ 63 Tỉnh và Thành phố trực thuộc trung ương tại Việt Nam theo chuẩn Tổng cục Thống kê (GSO)
VIETNAM_PROVINCES: List[Dict[str, str]] = [
    # ------------------ MIỀN BẮC (25 Tỉnh / Thành phố) ------------------
    {"code": "01", "name": "Hà Nội", "name_en": "Ha Noi", "region": "Miền Bắc"},
    {"code": "02", "name": "Hà Giang", "name_en": "Ha Giang", "region": "Miền Bắc"},
    {"code": "04", "name": "Cao Bằng", "name_en": "Cao Bang", "region": "Miền Bắc"},
    {"code": "06", "name": "Bắc Kạn", "name_en": "Bac Kan", "region": "Miền Bắc"},
    {"code": "08", "name": "Tuyên Quang", "name_en": "Tuyen Quang", "region": "Miền Bắc"},
    {"code": "10", "name": "Lào Cai", "name_en": "Lao Cai", "region": "Miền Bắc"},
    {"code": "11", "name": "Điện Biên", "name_en": "Dien Bien", "region": "Miền Bắc"},
    {"code": "12", "name": "Lai Châu", "name_en": "Lai Chau", "region": "Miền Bắc"},
    {"code": "14", "name": "Sơn La", "name_en": "Son La", "region": "Miền Bắc"},
    {"code": "15", "name": "Yên Bái", "name_en": "Yen Bai", "region": "Miền Bắc"},
    {"code": "17", "name": "Hòa Bình", "name_en": "Hoa Binh", "region": "Miền Bắc"},
    {"code": "19", "name": "Thái Nguyên", "name_en": "Thai Nguyen", "region": "Miền Bắc"},
    {"code": "20", "name": "Lạng Sơn", "name_en": "Lang Son", "region": "Miền Bắc"},
    {
        "code": "22",
        "name": "Quảng Ninh",
        "name_en": "Quang Ninh",
        "region": "Miền Bắc",
    },  # Bao gồm TP. Hạ Long, Cẩm Phả, Uông Bí, Móng Cái
    {"code": "24", "name": "Bắc Giang", "name_en": "Bac Giang", "region": "Miền Bắc"},
    {"code": "25", "name": "Phú Thọ", "name_en": "Phu Tho", "region": "Miền Bắc"},
    {"code": "26", "name": "Vĩnh Phúc", "name_en": "Vinh Phuc", "region": "Miền Bắc"},
    {"code": "27", "name": "Bắc Ninh", "name_en": "Bac Ninh", "region": "Miền Bắc"},
    {"code": "30", "name": "Hải Dương", "name_en": "Hai Duong", "region": "Miền Bắc"},
    {"code": "31", "name": "Hải Phòng", "name_en": "Hai Phong", "region": "Miền Bắc"},
    {"code": "33", "name": "Hưng Yên", "name_en": "Hung Yen", "region": "Miền Bắc"},
    {"code": "34", "name": "Thái Bình", "name_en": "Thai Binh", "region": "Miền Bắc"},
    {"code": "35", "name": "Hà Nam", "name_en": "Ha Nam", "region": "Miền Bắc"},
    {"code": "36", "name": "Nam Định", "name_en": "Nam Dinh", "region": "Miền Bắc"},
    {"code": "37", "name": "Ninh Bình", "name_en": "Ninh Binh", "region": "Miền Bắc"},

    # ------------------ MIỀN TRUNG & TÂY NGUYÊN (19 Tỉnh / Thành phố) ------------------
    {"code": "38", "name": "Thanh Hóa", "name_en": "Thanh Hoa", "region": "Miền Trung"},
    {"code": "40", "name": "Nghệ An", "name_en": "Nghe An", "region": "Miền Trung"},
    {"code": "42", "name": "Hà Tĩnh", "name_en": "Ha Tinh", "region": "Miền Trung"},
    {"code": "44", "name": "Quảng Bình", "name_en": "Quang Binh", "region": "Miền Trung"},
    {"code": "45", "name": "Quảng Trị", "name_en": "Quang Tri", "region": "Miền Trung"},
    {"code": "46", "name": "Thừa Thiên Huế", "name_en": "Thua Thien Hue", "region": "Miền Trung"},
    {"code": "48", "name": "Đà Nẵng", "name_en": "Da Nang", "region": "Miền Trung"},
    {"code": "49", "name": "Quảng Nam", "name_en": "Quang Nam", "region": "Miền Trung"},
    {"code": "51", "name": "Quảng Ngãi", "name_en": "Quang Ngai", "region": "Miền Trung"},
    {"code": "52", "name": "Bình Định", "name_en": "Binh Dinh", "region": "Miền Trung"},
    {"code": "54", "name": "Phú Yên", "name_en": "Phu Yen", "region": "Miền Trung"},
    {"code": "56", "name": "Khánh Hòa", "name_en": "Khanh Hoa", "region": "Miền Trung"},
    {"code": "58", "name": "Ninh Thuận", "name_en": "Ninh Thuan", "region": "Miền Trung"},
    {"code": "60", "name": "Bình Thuận", "name_en": "Binh Thuan", "region": "Miền Trung"},
    {"code": "62", "name": "Kon Tum", "name_en": "Kon Tum", "region": "Miền Trung"},
    {"code": "64", "name": "Gia Lai", "name_en": "Gia Lai", "region": "Miền Trung"},
    {"code": "66", "name": "Đắk Lắk", "name_en": "Dak Lak", "region": "Miền Trung"},
    {"code": "67", "name": "Đắk Nông", "name_en": "Dak Nong", "region": "Miền Trung"},
    {"code": "68", "name": "Lâm Đồng", "name_en": "Lam Dong", "region": "Miền Trung"},

    # ------------------ MIỀN NAM (19 Tỉnh / Thành phố) ------------------
    {"code": "70", "name": "Bình Phước", "name_en": "Binh Phuoc", "region": "Miền Nam"},
    {"code": "72", "name": "Tây Ninh", "name_en": "Tay Ninh", "region": "Miền Nam"},
    {"code": "74", "name": "Bình Dương", "name_en": "Binh Duong", "region": "Miền Nam"},
    {"code": "75", "name": "Đồng Nai", "name_en": "Dong Nai", "region": "Miền Nam"},
    {"code": "77", "name": "Bà Rịa - Vũng Tàu", "name_en": "Ba Ria - Vung Tau", "region": "Miền Nam"},
    {"code": "79", "name": "Hồ Chí Minh", "name_en": "Ho Chi Minh", "region": "Miền Nam"},
    {"code": "80", "name": "Long An", "name_en": "Long An", "region": "Miền Nam"},
    {"code": "82", "name": "Tiền Giang", "name_en": "Tien Giang", "region": "Miền Nam"},
    {"code": "83", "name": "Bến Tre", "name_en": "Ben Tre", "region": "Miền Nam"},
    {"code": "84", "name": "Trà Vinh", "name_en": "Tra Vinh", "region": "Miền Nam"},
    {"code": "86", "name": "Vĩnh Long", "name_en": "Vinh Long", "region": "Miền Nam"},
    {"code": "87", "name": "Đồng Tháp", "name_en": "Dong Thap", "region": "Miền Nam"},
    {"code": "89", "name": "An Giang", "name_en": "An Giang", "region": "Miền Nam"},
    {"code": "91", "name": "Kiên Giang", "name_en": "Kien Giang", "region": "Miền Nam"},
    {"code": "92", "name": "Cần Thơ", "name_en": "Can Tho", "region": "Miền Nam"},
    {"code": "93", "name": "Hậu Giang", "name_en": "Hau Giang", "region": "Miền Nam"},
    {"code": "94", "name": "Sóc Trăng", "name_en": "Soc Trang", "region": "Miền Nam"},
    {"code": "95", "name": "Bạc Liêu", "name_en": "Bac Lieu", "region": "Miền Nam"},
    {"code": "96", "name": "Cà Mau", "name_en": "Ca Mau", "region": "Miền Nam"},
]


async def seed_provinces(db: AsyncSession) -> int:
    """
    Nạp dữ liệu mẫu đầy đủ 63 tỉnh/thành phố vào cơ sở dữ liệu (Bất đồng bộ).
    Nếu tỉnh đã tồn tại thì bỏ qua hoặc cập nhật thông tin tên/vùng miền.
    Trả về số lượng bản ghi đã được chèn mới.
    """
    inserted_count = 0
    for p_data in VIETNAM_PROVINCES:
        stmt = select(Province).where(Province.code == p_data["code"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if not existing:
            new_prov = Province(
                code=p_data["code"],
                name=p_data["name"],
                name_en=p_data["name_en"],
                region=p_data["region"],
            )
            db.add(new_prov)
            inserted_count += 1
        else:
            # Đồng bộ lại tên nếu có sự sai khác
            existing.name = p_data["name"]
            existing.name_en = p_data["name_en"]
            existing.region = p_data["region"]

    await db.commit()
    logger.info(f"Đã hoàn thành nạp dữ liệu Tỉnh thành. Thêm mới: {inserted_count} tỉnh.")
    return inserted_count


def seed_provinces_sync(db: Session) -> int:
    """
    Nạp dữ liệu tỉnh thành phiên bản đồng bộ (Sync) dành cho script hoặc Celery worker.
    """
    inserted_count = 0
    for p_data in VIETNAM_PROVINCES:
        existing = db.query(Province).filter(Province.code == p_data["code"]).first()
        if not existing:
            new_prov = Province(
                code=p_data["code"],
                name=p_data["name"],
                name_en=p_data["name_en"],
                region=p_data["region"],
            )
            db.add(new_prov)
            inserted_count += 1
        else:
            existing.name = p_data["name"]
            existing.name_en = p_data["name_en"]
            existing.region = p_data["region"]

    db.commit()
    return inserted_count
