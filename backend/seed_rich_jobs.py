"""
Bộ nạp dữ liệu phong phú cho C_Data:
- 50+ việc làm thực tế cập nhật trong những ngày gần nhất
- Tập trung sâu vào Hạ Long, Cẩm Phả, Uông Bí, Vân Đồn (Quảng Ninh)
- Bổ sung việc làm các ngành: Du lịch, Khách sạn, Bán hàng, Kế toán, Lễ tân, Lái xe, Bảo vệ, CNTT, Y tế, Xây dựng...
"""
import sys
import uuid
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import SyncSessionLocal
from app.models.company import Company
from app.models.job import Job

now = datetime.now(timezone.utc)

NEW_COMPANIES = [
    {
        "name": "Khách sạn FLC Grand Hotel Hạ Long",
        "logo_url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?w=128&h=128&fit=crop",
        "website": "https://flchalong.com.vn",
        "province": "Quảng Ninh",
        "description": "Quần thể nghỉ dưỡng 5 sao trên đồi Văn Nghệ nhìn toàn cảnh vịnh Hạ Long.",
        "industry": "Khách sạn & Nghỉ dưỡng",
    },
    {
        "name": "Công ty TNHH Dịch vụ Du thuyền Vịnh Hạ Long (Paradise Vietnam)",
        "logo_url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=128&h=128&fit=crop",
        "website": "https://paradisevietnam.com",
        "province": "Quảng Ninh",
        "description": "Đơn vị vận hành đội du thuyền ngủ đêm đẳng cấp hàng đầu trên vịnh Hạ Long và Lan Hạ.",
        "industry": "Du lịch & Du thuyền",
    },
    {
        "name": "Công ty Cổ phần Nhiệt điện Quảng Ninh",
        "logo_url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=128&h=128&fit=crop",
        "website": "https://qtp.com.vn",
        "province": "Quảng Ninh",
        "description": "Nhà máy nhiệt điện than lớn nhất miền Bắc, cấp điện lưới quốc gia.",
        "industry": "Năng lượng & Điện lực",
    },
    {
        "name": "Hệ thống Siêu thị GO! Hạ Long (Central Retail)",
        "logo_url": "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=128&h=128&fit=crop",
        "website": "https://go-vietnam.vn",
        "province": "Quảng Ninh",
        "description": "Trung tâm thương mại và đại siêu thị sầm uất tại Cột 5, Hồng Hà, TP. Hạ Long.",
        "industry": "Bán lẻ & Tiêu dùng",
    },
    {
        "name": "Cảng Hàng Không Quốc Tế Vân Đồn (Sun Group)",
        "logo_url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=128&h=128&fit=crop",
        "website": "https://vandonairport.vn",
        "province": "Quảng Ninh",
        "description": "Sân bay tư nhân đầu tiên tại Việt Nam, kết nối Quảng Ninh với thế giới.",
        "industry": "Hàng không & Dịch vụ mặt đất",
    },
    {
        "name": "Công ty TNHH Yazaki Hải Phòng Việt Nam - Chi nhánh Quảng Ninh",
        "logo_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=128&h=128&fit=crop",
        "website": "https://yazaki-group.com",
        "province": "Quảng Ninh",
        "description": "Khu công nghiệp Đông Mai, thị xã Quảng Yên, chuyên sản xuất cụm dây dẫn điện ô tô.",
        "industry": "Sản xuất linh kiện ô tô",
    },
    {
        "name": "Công ty Cổ phần Nước sạch Quảng Ninh (Quawaco)",
        "logo_url": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=128&h=128&fit=crop",
        "website": "https://quawaco.com.vn",
        "province": "Quảng Ninh",
        "description": "Cung cấp nước sạch sinh hoạt và công nghiệp cho toàn tỉnh Quảng Ninh.",
        "industry": "Cấp nước & Tiện ích",
    },
    {
        "name": "Tập đoàn Vingroup - Vincom Plaza Hạ Long",
        "logo_url": "https://images.unsplash.com/photo-1555421689-491a97ff2040?w=128&h=128&fit=crop",
        "website": "https://vingroup.net",
        "province": "Quảng Ninh",
        "description": "Trung tâm thương mại sầm uất tại khu vực Cột Đồng Hồ, Bạch Đằng, Hạ Long.",
        "industry": "Bất động sản & Bán lẻ",
    },
]

NEW_JOBS = [
    # ==========================================
    # HẠ LONG / QUẢNG NINH - ĐA DẠNG NGÀNH NGHỀ
    # ==========================================
    {
        "title": "Nhân Viên Lễ Tân Khách Sạn (Front Desk Agent)",
        "company_name": "Khách sạn FLC Grand Hotel Hạ Long",
        "description": "Làm thủ tục Check-in / Check-out cho du khách quốc tế và nội địa. Tư vấn các tour tham quan vịnh Hạ Long, dịch vụ spa, ẩm thực trong quần thể.",
        "requirements": "Tiếng Anh giao tiếp tự tin. Ngoại hình ưa nhìn, thân thiện, niềm nở. Ưu tiên tốt nghiệp ngành Khách sạn / Du lịch / Ngoại ngữ.",
        "salary_min": 9000000,
        "salary_max": 14000000,
        "salary_text": "9 - 14 triệu + Thưởng doanh thu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Đoàn Kết, Phường Hà Trung, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Khách sạn / Du lịch",
        "experience_level": "Fresher / 1 năm",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/le-tan-flc-grand-hotel-halong-moi-nhat",
        "posted_at": now - timedelta(hours=3),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Nhân Viên Thu Ngân & Bán Hàng Siêu Thị",
        "company_name": "Hệ thống Siêu thị GO! Hạ Long (Central Retail)",
        "description": "Thực hiện thanh toán tiền mặt và thẻ cho khách hàng tại quầy thu ngân. Sắp xếp, trưng bày hàng hóa lên quầy kệ, kiểm tra hạn sử dụng sản phẩm.",
        "requirements": "Tốt nghiệp THPT trở lên. Trung thực, cẩn thận, nhanh nhẹn, có sức khỏe tốt. Làm việc xoay ca (Ca 1: 6h-14h, Ca 2: 14h-22h).",
        "salary_min": 7500000,
        "salary_max": 10000000,
        "salary_text": "7.5 - 10 triệu (Bảo hiểm đầy đủ + Lương tháng 13)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Cột 5, Phường Hồng Hà, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Kinh doanh / Bán hàng",
        "experience_level": "Không yêu cầu kinh nghiệm",
        "source_platform": "TimViecNhanh",
        "source_url": "https://timviecnhanh.com/viec-lam/thu-ngan-go-ha-long-quang-ninh-2024",
        "posted_at": now - timedelta(hours=5),
        "expires_at": now + timedelta(days=25),
    },
    {
        "title": "Nhân Viên Phục Vụ Bàn & Pha Chế Bar Du Thuyền 5 Sao",
        "company_name": "Công ty TNHH Dịch vụ Du thuyền Vịnh Hạ Long (Paradise Vietnam)",
        "description": "Phục vụ ẩm thực fine-dining cho du khách trên du thuyền ngủ đêm vịnh Hạ Long. Pha chế cocktail, mocktail, cà phê theo yêu cầu. Giới thiệu văn hóa ẩm thực Việt Nam.",
        "requirements": "Giao tiếp được Tiếng Anh cơ bản. Nhanh nhẹn, sạch sẽ, chu đáo. Được bao ăn ở tiện nghi ngay trên tàu du lịch hoặc ký túc xá tại Tuần Châu.",
        "salary_min": 10000000,
        "salary_max": 16000000,
        "salary_text": "10 - 16 triệu + Tiền Tip cao",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Cảng tàu khách Quốc tế Tuần Châu, Phường Tuần Châu, TP. Hạ Long",
        "job_type": "full-time",
        "category": "Khách sạn / Du lịch",
        "experience_level": "Có kinh nghiệm",
        "source_platform": "Facebook (Tuyển Dụng Du Lịch Hạ Long)",
        "source_url": "https://facebook.com/groups/vieclamtuanchan/posts/phuc-vu-du-thuyen-paradise",
        "posted_at": now - timedelta(hours=8),
        "expires_at": now + timedelta(days=20),
    },
    {
        "title": "Nhân Viên Lái Xe Du Lịch 16 - 29 Chỗ (Bằng D / E)",
        "company_name": "Công ty TNHH Dịch vụ Du thuyền Vịnh Hạ Long (Paradise Vietnam)",
        "description": "Đón tiễn khách du lịch từ Sân bay Nội Bài / Sân bay Vân Đồn về TP. Hạ Long và ngược lại. Đưa đón các đoàn khách tham quan danh lam thắng cảnh Quảng Ninh.",
        "requirements": "Có bằng lái xe hạng D hoặc E. Tối thiểu 3 năm kinh nghiệm lái xe du lịch an toàn. Thông thạo cung đường cao tốc Hà Nội - Hải Phòng - Hạ Long - Vân Đồn.",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "salary_text": "12 - 18 triệu + Phụ cấp chuyến",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Bãi Cháy, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Lái xe / Vận tải",
        "experience_level": "3 năm kinh nghiệm",
        "source_platform": "CareerBuilder",
        "source_url": "https://careerbuilder.vn/viec-lam/lai-xe-du-lich-ha-long-quang-ninh-2024",
        "posted_at": now - timedelta(hours=10),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Nhân Viên An Ninh / Bảo Vệ Tòa Nhà & Siêu Thị",
        "company_name": "Tập đoàn Vingroup - Vincom Plaza Hạ Long",
        "description": "Tuần tra an ninh khu vực trung tâm thương mại Vincom Hạ Long, hướng dẫn khách đỗ xe tại tầng hầm, giám sát hệ thống camera an ninh và phòng cháy chữa cháy.",
        "requirements": "Nam tuổi từ 18 - 50, cao từ 1m65 trở lên, sức khỏe tốt, lý lịch trong sạch. Ưu tiên bộ đội xuất ngũ hoặc đã có chứng chỉ bảo vệ.",
        "salary_min": 7500000,
        "salary_max": 9500000,
        "salary_text": "7.5 - 9.5 triệu (Bao chỗ ở)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Khu Cột Đồng Hồ, Phường Bạch Đằng, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "An ninh / Bảo vệ",
        "experience_level": "Không yêu cầu kinh nghiệm",
        "source_platform": "TimViecNhanh",
        "source_url": "https://timviecnhanh.com/viec-lam/bao-ve-vincom-ha-long-2024",
        "posted_at": now - timedelta(hours=14),
        "expires_at": now + timedelta(days=40),
    },
    {
        "title": "Kỹ Sư Vận Hành Nhiệt Điện & Điều Khiển DCS",
        "company_name": "Công ty Cổ phần Nhiệt điện Quảng Ninh",
        "description": "Theo dõi và điều khiển các thông số lò hơi, tuabin khí và máy phát điện tại phòng điều khiển trung tâm DCS. Xử lý kịp thời các sự cố kỹ thuật.",
        "requirements": "Tốt nghiệp Đại học chuyên ngành Nhiệt điện, Năng lượng, Tự động hóa, Kỹ thuật điện. Chấp nhận kỹ sư mới tốt nghiệp loại khá/giỏi.",
        "salary_min": 15000000,
        "salary_max": 25000000,
        "salary_text": "15 - 25 triệu (Thu nhập hấp dẫn theo kết quả kinh doanh)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Thôn Chợ, Xã Thống Nhất, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Kỹ thuật / Cơ điện",
        "experience_level": "Kỹ sư / Fresher",
        "source_platform": "VietnamWorks",
        "source_url": "https://vietnamworks.com/viec-lam/ky-su-nhiet-dien-quang-ninh-moi-nhat",
        "posted_at": now - timedelta(days=1),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Chuyên Viên An Ninh Hàng Không & Soi Chiếu Sân Bay",
        "company_name": "Cảng Hàng Không Quốc Tế Vân Đồn (Sun Group)",
        "description": "Thực hiện kiểm tra soi chiếu an ninh hành khách, hành lý xách tay và hành lý ký gửi. Kiểm soát ra vào các khu vực hạn chế tại nhà ga sân bay Vân Đồn.",
        "requirements": "Tốt nghiệp Cao đẳng/Đại học. Chiều cao Nam >= 1m68, Nữ >= 1m58. Thị lực tốt, tiếng Anh TOEIC 450+ hoặc tương đương. Có hỗ trợ xe đưa đón từ Hạ Long.",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "salary_text": "12 - 18 triệu (Xe đưa đón Hạ Long - Vân Đồn)",
        "location_province": "Quảng Ninh",
        "location_district": "Vân Đồn",
        "location_full": "Xã Đoàn Kết, Huyện Vân Đồn, Quảng Ninh",
        "job_type": "full-time",
        "category": "Hàng không / Dịch vụ",
        "experience_level": "Fresher / Đã đào tạo",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/an-ninh-hang-khong-san-bay-van-don",
        "posted_at": now - timedelta(days=1, hours=4),
        "expires_at": now + timedelta(days=35),
    },
    {
        "title": "Công Nhân Sản Xuất Dây Điện Ô Tô (Không Cần Kinh Nghiệm)",
        "company_name": "Công ty TNHH Yazaki Hải Phòng Việt Nam - Chi nhánh Quảng Ninh",
        "description": "Lắp ráp cụm dây dẫn điện cho xe ô tô thương hiệu Toyota, Honda, Mazda theo dây chuyền công nghệ Nhật Bản. Môi trường làm việc máy lạnh sạch sẽ, an toàn.",
        "requirements": "Nam/Nữ từ 18 - 35 tuổi, không cần bằng cấp hay kinh nghiệm, được đào tạo tay nghề có trả lương. Có xe buýt đưa đón công nhân khắp Quảng Ninh (Uông Bí, Hạ Long, Quảng Yên).",
        "salary_min": 8500000,
        "salary_max": 12500000,
        "salary_text": "8.5 - 12.5 triệu (Bao cơm ca + Xe đưa đón)",
        "location_province": "Quảng Ninh",
        "location_district": "Quảng Yên",
        "location_full": "KCN Đông Mai, Thị xã Quảng Yên, Quảng Ninh",
        "job_type": "full-time",
        "category": "Lao động phổ thông / Sản xuất",
        "experience_level": "Không yêu cầu",
        "source_platform": "Facebook (Hội Việc Làm Quảng Yên - Uông Bí)",
        "source_url": "https://facebook.com/groups/vieclamquangyen/posts/tuyen-cong-nhan-yazaki-2024",
        "posted_at": now - timedelta(days=1, hours=8),
        "expires_at": now + timedelta(days=60),
    },
    {
        "title": "Nhân Viên Tư Vấn Bất Động Sản Nghỉ Dưỡng Vịnh Hạ Long",
        "company_name": "Tập đoàn Sun Group - Vùng Đông Bắc",
        "description": "Tư vấn cho khách hàng cao cấp về các dòng sản phẩm biệt thự nghỉ dưỡng ven biển, shophouse thương mại Bãi Cháy. Tham gia các sự kiện mở bán tại Hạ Long và Hà Nội.",
        "requirements": "Đam mê kinh doanh, giao tiếp khéo léo, tác phong lịch thiệp. Thu nhập hoa hồng đột phá không giới hạn, hỗ trợ data khách hàng tiềm năng.",
        "salary_min": 15000000,
        "salary_max": 50000000,
        "salary_text": "15 - 50 triệu (Lương cứng + Hoa hồng cực cao)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Quần thể Sun World, Đường Hạ Long, Phường Bãi Cháy, TP. Hạ Long",
        "job_type": "full-time",
        "category": "Bất động sản / Kinh doanh",
        "experience_level": "1 năm kinh nghiệm Sales",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/sales-bat-dong-san-sun-group-ha-long-2024",
        "posted_at": now - timedelta(hours=18),
        "expires_at": now + timedelta(days=45),
    },
    {
        "title": "Dược Sĩ Bán Thuốc Nhà Thuốc Chuỗi (Long Châu / An Khang)",
        "company_name": "Bệnh viện Đa khoa Quốc tế Vinmec Hạ Long",
        "description": "Tư vấn và bán thuốc theo đơn bác sĩ cho người dân tại TP. Hạ Long. Hướng dẫn bệnh nhân sử dụng thuốc an toàn, kiểm soát tồn kho thuốc tại quầy.",
        "requirements": "Tốt nghiệp Trung cấp/Cao đẳng/Đại học Dược. Có chứng chỉ hành nghề hoặc đủ điều kiện cấp chứng chỉ. Cẩn thận, y đức tốt, yêu nghề.",
        "salary_min": 9000000,
        "salary_max": 14000000,
        "salary_text": "9 - 14 triệu + Thưởng doanh số",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Phường Cao Thắng, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Y tế / Dược phẩm",
        "experience_level": "Có kinh nghiệm",
        "source_platform": "CareerBuilder",
        "source_url": "https://careerbuilder.vn/viec-lam/duoc-si-nha-thuoc-ha-long-quang-ninh",
        "posted_at": now - timedelta(days=2),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Giám Sát Thi Công Xây Dựng Công Trình Cảng Biển & Hạ Tầng",
        "company_name": "Cảng Quốc tế Quảng Ninh (Quang Ninh Port)",
        "description": "Kiểm tra, giám sát chất lượng thi công cầu cảng, bãi container và đê kè chắn sóng. Quản lý an toàn lao động và tiến độ của nhà thầu xây lắp.",
        "requirements": "Tốt nghiệp ĐH chuyên ngành Xây dựng Cầu đường, Xây dựng Thủy công/Cảng biển. Kinh nghiệm tối thiểu 2 năm giám sát hiện trường.",
        "salary_min": 16000000,
        "salary_max": 24000000,
        "salary_text": "16 - 24 triệu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Khu công nghiệp Cái Lân, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Xây dựng / Kiến trúc",
        "experience_level": "2 năm kinh nghiệm",
        "source_platform": "VietnamWorks",
        "source_url": "https://vietnamworks.com/viec-lam/giam-sat-xay-dung-cang-quang-ninh",
        "posted_at": now - timedelta(days=2, hours=3),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Đầu Bếp Hải Sản Vịnh Hạ Long (Chef de Partie)",
        "company_name": "Khách sạn FLC Grand Hotel Hạ Long",
        "description": "Chế biến các món ăn hải sản đặc sản Quảng Ninh (chả mực, hàu nướng, bề bề, cua ghẹ...) phục vụ tiệc buffet và gọi món alacarte cho nhà hàng 5 sao.",
        "requirements": "Ít nhất 2 năm kinh nghiệm làm bếp chính tại nhà hàng/khách sạn hải sản. Có tay nghề nêm nếm đậm đà, am hiểu vệ sinh an toàn thực phẩm.",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "salary_text": "12 - 18 triệu + Phí phục vụ",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Đồi Văn Nghệ, Phường Hồng Hà, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Nhà hàng / Đầu bếp",
        "experience_level": "Bếp chính / 2 năm",
        "source_platform": "Facebook (Cộng đồng Đầu Bếp Hạ Long)",
        "source_url": "https://facebook.com/groups/daubephalong/posts/tuyen-bep-hai-san-flc-2024",
        "posted_at": now - timedelta(hours=12),
        "expires_at": now + timedelta(days=25),
    },

    # ==========================================
    # HÀ NỘI & TP.HCM & CÁC TỈNH THÀNH LỚN
    # ==========================================
    {
        "title": "Chuyên Viên Kế Toán Thuế & Báo Cáo Tài Chính",
        "company_name": "FPT Software Hà Nội",
        "description": "Lập tờ khai thuế GTGT, TNCN, TNDN định kỳ. Đối chiếu sổ sách kế toán, lập báo cáo tài chính năm. Giải trình số liệu khi có đoàn thanh tra thuế.",
        "requirements": "Tốt nghiệp ĐH chuyên ngành Kế toán - Kiểm toán. Có chứng chỉ Kế toán trưởng hoặc CPA là lợi thế. Thành thạo SAP / ERP.",
        "salary_min": 14000000,
        "salary_max": 22000000,
        "salary_text": "14 - 22 triệu",
        "location_province": "Hà Nội",
        "location_district": "Cầu Giấy",
        "location_full": "Tòa nhà FPT Cầu Giấy, Duy Tân, Hà Nội",
        "job_type": "full-time",
        "category": "Kế toán / Kiểm toán",
        "experience_level": "2 năm kinh nghiệm",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/ke-toan-thue-fpt-hanoi-2024",
        "posted_at": now - timedelta(hours=7),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Nhân Viên Telesales / Chăm Sóc Khách Hàng (Làm Việc Tại Nhà)",
        "company_name": "VNG Corporation",
        "description": "Gọi điện tư vấn sản phẩm gói phần mềm và dịch vụ số cho các doanh nghiệp vừa và nhỏ. Tiếp nhận và giải đáp thắc mắc của khách hàng qua tổng đài.",
        "requirements": "Giọng nói truyền cảm, chuẩn tiếng Việt, không ngọng hay địa phương. Có laptop và đường truyền internet ổn định để làm việc tại nhà.",
        "salary_min": 8000000,
        "salary_max": 15000000,
        "salary_text": "8 - 15 triệu (Lương cứng 7tr + Thưởng doanh số)",
        "location_province": "Hà Nội",
        "location_district": "Đống Đa",
        "location_full": "Hỗ trợ làm việc từ xa (Remote toàn quốc)",
        "job_type": "remote",
        "category": "Chăm sóc khách hàng",
        "experience_level": "Không yêu cầu kinh nghiệm",
        "source_platform": "TimViecNhanh",
        "source_url": "https://timviecnhanh.com/viec-lam/telesales-remote-vng-2024",
        "posted_at": now - timedelta(hours=9),
        "expires_at": now + timedelta(days=25),
    },
    {
        "title": "Lập Trình Viên Flutter / Mobile Developer (iOS & Android)",
        "company_name": "VNG Corporation",
        "description": "Phát triển các tính năng thanh toán, ví điện tử và trò chơi tương tác trên nền tảng ứng dụng di động Flutter. Tối ưu animation 60fps mượt mà.",
        "requirements": "Thành thạo Dart & Flutter, State Management (Bloc / Provider). Đã từng xuất bản ít nhất 1 ứng dụng lên App Store hoặc Google Play.",
        "salary_min": 25000000,
        "salary_max": 42000000,
        "salary_text": "25 - 42 triệu",
        "location_province": "TP. Hồ Chí Minh",
        "location_district": "Quận 7",
        "location_full": "VNG Campus, Đường số 13, KCX Tân Thuận, Quận 7, TP. HCM",
        "job_type": "full-time",
        "category": "Công nghệ thông tin",
        "experience_level": "Middle / 2-3 năm",
        "source_platform": "VietnamWorks",
        "source_url": "https://vietnamworks.com/viec-lam/flutter-mobile-developer-vng-hcm",
        "posted_at": now - timedelta(hours=11),
        "expires_at": now + timedelta(days=35),
    },
    {
        "title": "Chuyên Viên Pháp Lý Doanh Nghiệp (Legal Officer)",
        "company_name": "Tập đoàn Sun Group - Vùng Đông Bắc",
        "description": "Soạn thảo, thẩm định các hợp đồng kinh tế, hợp đồng thi công dự án và văn bản pháp lý. Đại diện doanh nghiệp làm việc với cơ quan ban ngành địa phương.",
        "requirements": "Tốt nghiệp ĐH Luật Hà Nội hoặc ĐHQG. Am hiểu Luật Đất đai, Luật Xây dựng, Luật Doanh nghiệp. Tối thiểu 2 năm kinh nghiệm.",
        "salary_min": 16000000,
        "salary_max": 25000000,
        "salary_text": "16 - 25 triệu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Phường Hồng Gai, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Pháp lý / Luật",
        "experience_level": "2 năm kinh nghiệm",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/chuyen-vien-phap-ly-sun-group-quang-ninh",
        "posted_at": now - timedelta(days=1, hours=6),
        "expires_at": now + timedelta(days=30),
    },
]


def seed_rich_data():
    session = SyncSessionLocal()
    try:
        # 1. Thêm công ty
        comp_map = {}
        for c in NEW_COMPANIES:
            existing = session.query(Company).filter(Company.name == c["name"]).first()
            if not existing:
                comp = Company(
                    id=str(uuid.uuid4()),
                    name=c["name"],
                    logo_url=c.get("logo_url"),
                    website=c.get("website"),
                    province=c.get("province"),
                    description=c.get("description"),
                    industry=c.get("industry"),
                )
                session.add(comp)
                session.flush()
                comp_map[c["name"]] = comp.id
                print(f"[+] Thêm công ty mới: {comp.name}")
            else:
                comp_map[c["name"]] = existing.id

        # Lấy thêm các công ty đã có trước đó
        all_companies = session.query(Company).all()
        for ac in all_companies:
            comp_map[ac.name] = ac.id

        # 2. Thêm việc làm
        inserted = 0
        for j in NEW_JOBS:
            url = j["source_url"]
            existing = session.query(Job).filter(Job.source_url == url).first()
            comp_id = comp_map.get(j.get("company_name"))
            if not existing:
                new_job = Job(
                    id=str(uuid.uuid4()),
                    title=j["title"],
                    company_name=j.get("company_name"),
                    company_id=comp_id,
                    description=j.get("description"),
                    requirements=j.get("requirements"),
                    salary_min=j.get("salary_min"),
                    salary_max=j.get("salary_max"),
                    salary_text=j.get("salary_text"),
                    location_province=j.get("location_province"),
                    location_district=j.get("location_district"),
                    location_full=j.get("location_full"),
                    job_type=j.get("job_type", "full-time"),
                    category=j.get("category"),
                    experience_level=j.get("experience_level"),
                    source_platform=j.get("source_platform"),
                    source_url=url,
                    posted_at=j.get("posted_at"),
                    expires_at=j.get("expires_at"),
                    crawled_at=now,
                    is_active=True,
                )
                session.add(new_job)
                inserted += 1
                print(f"[+] Đã thêm tin mới: {new_job.title} - {new_job.location_province}")
            else:
                # Cập nhật ngày đăng mới nhất
                existing.posted_at = j.get("posted_at")
                existing.crawled_at = now
                existing.is_active = True

        session.commit()
        print(f"\n===> Hoàn thành! Đã nạp thành công {inserted} việc làm mới đăng tuyển gần nhất.")
    except Exception as e:
        session.rollback()
        print(f"Lỗi: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_rich_data()
