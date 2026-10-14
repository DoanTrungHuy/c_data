"""
Script nạp dữ liệu mẫu ban đầu cho C_Data, đặc biệt tập trung vào
Hạ Long - Quảng Ninh và các tỉnh thành lớn tại Việt Nam.
"""
import uuid
from datetime import datetime, timedelta, timezone
from app.core.database import SyncSessionLocal
from app.models.job import Job
from app.models.company import Company

SAMPLE_COMPANIES = [
    {
        "name": "Tập đoàn Sun Group - Vùng Đông Bắc",
        "logo_url": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=128&h=128&fit=crop",
        "website": "https://sungroup.com.vn",
        "province": "Quảng Ninh",
        "description": "Tập đoàn phát triển du lịch nghỉ dưỡng, vui chơi giải trí hàng đầu tại Hạ Long và Việt Nam.",
        "industry": "Du lịch & Nghỉ dưỡng",
    },
    {
        "name": "Vinpearl Resort & Spa Hạ Long",
        "logo_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=128&h=128&fit=crop",
        "website": "https://vinpearl.com",
        "province": "Quảng Ninh",
        "description": "Khu nghỉ dưỡng 5 sao nằm trọn trên đảo Rều, Bãi Cháy, TP. Hạ Long.",
        "industry": "Khách sạn & Nhà hàng",
    },
    {
        "name": "Công ty Cổ phần Công nghệ Thông tin Hạ Long (HaLong Tech)",
        "logo_url": "https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=128&h=128&fit=crop",
        "website": "https://halongtech.vn",
        "province": "Quảng Ninh",
        "description": "Cung cấp giải pháp chuyển đổi số cho doanh nghiệp du lịch, cảng biển và cơ quan nhà nước tại Quảng Ninh.",
        "industry": "Công nghệ thông tin",
    },
    {
        "name": "Cảng Quốc tế Quảng Ninh (Quang Ninh Port)",
        "logo_url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=128&h=128&fit=crop",
        "website": "https://quangninhport.com.vn",
        "province": "Quảng Ninh",
        "description": "Hệ thống cảng biển nước sâu cửa ngõ kinh tế phía Bắc.",
        "industry": "Logistics & Vận tải biển",
    },
    {
        "name": "Tập đoàn Công nghiệp Than - Khoáng sản Việt Nam (TKV - Vùng Cẩm Phả)",
        "logo_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=128&h=128&fit=crop",
        "website": "https://vinacomin.vn",
        "province": "Quảng Ninh",
        "description": "Doanh nghiệp khai thác, chế biến khoáng sản và năng lượng hàng đầu.",
        "industry": "Khai khoáng & Năng lượng",
    },
    {
        "name": "FPT Software Hà Nội",
        "logo_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=128&h=128&fit=crop",
        "website": "https://fptsoftware.com",
        "province": "Hà Nội",
        "description": "Công ty phần mềm hàng đầu Đông Nam Á.",
        "industry": "Công nghệ thông tin",
    },
    {
        "name": "VNG Corporation",
        "logo_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=128&h=128&fit=crop",
        "website": "https://vng.com.vn",
        "province": "TP. Hồ Chí Minh",
        "description": "Kỳ lân công nghệ đầu tiên tại Việt Nam.",
        "industry": "Internet & Trò chơi trực tuyến",
    },
    {
        "name": "Bệnh viện Đa khoa Quốc tế Vinmec Hạ Long",
        "logo_url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=128&h=128&fit=crop",
        "website": "https://vinmec.com",
        "province": "Quảng Ninh",
        "description": "Bệnh viện tiêu chuẩn quốc tế tại phường Hồng Gai, TP. Hạ Long.",
        "industry": "Y tế & Chăm sóc sức khỏe",
    },
    {
        "name": "Trung tâm Ngoại ngữ Quốc tế Quảng Ninh",
        "logo_url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=128&h=128&fit=crop",
        "website": "https://halongedu.vn",
        "province": "Quảng Ninh",
        "description": "Đào tạo tiếng Anh, tiếng Trung giao tiếp & luyện thi tại Hạ Long.",
        "industry": "Giáo dục & Đào tạo",
    },
]

now = datetime.now(timezone.utc)

SAMPLE_JOBS = [
    # --- Hạ Long / Quảng Ninh ---
    {
        "title": "Chuyên Viên Quản Trị Hệ Thống IT & Hạ Tầng Mạng",
        "company_name": "Tập đoàn Sun Group - Vùng Đông Bắc",
        "description": "Quản lý và vận hành toàn bộ hạ tầng mạng, máy chủ tại Sun World Ha Long và Sun Premier Village. Hỗ trợ xử lý sự cố kỹ thuật nội bộ, giám sát an ninh mạng.",
        "requirements": "Tốt nghiệp ĐH/CĐ chuyên ngành CNTT. Kinh nghiệm từ 1 năm với mạng Cisco, Windows Server, hệ thống camera. Sống tại Hạ Long hoặc sẵn sàng chuyển về Quảng Ninh.",
        "salary_min": 14000000,
        "salary_max": 20000000,
        "salary_text": "14 - 20 triệu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Đường Hạ Long, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Công nghệ thông tin",
        "experience_level": "Junior / 1-3 năm",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/it-sun-group-halong-2024",
        "posted_at": now - timedelta(days=1),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Trưởng Ca Lễ Tân Tiếng Anh / Tiếng Trung (Front Desk Shift Leader)",
        "company_name": "Vinpearl Resort & Spa Hạ Long",
        "description": "Phụ trách điều phối ca làm việc tại tiền sảnh, đón tiếp khách VIP, giải quyết các yêu cầu phát sinh trong ca. Hướng dẫn nhân viên mới tuân thủ quy chuẩn 5 sao.",
        "requirements": "Tối thiểu 2 năm kinh nghiệm lễ tân khách sạn 4-5 sao. Giao tiếp trôi chảy Tiếng Anh (ưu tiên biết thêm Tiếng Trung). Ngoại hình ưa nhìn, tác phong chuyên nghiệp.",
        "salary_min": 12000000,
        "salary_max": 18000000,
        "salary_text": "12 - 18 triệu + Phí phục vụ (Service Charge)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Đảo Rều, Bãi Cháy, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Khách sạn / Du lịch",
        "experience_level": "Chuyên viên / 2 năm",
        "source_platform": "TimViecNhanh",
        "source_url": "https://timviecnhanh.com/viec-lam/truong-ca-le-tan-vinpearl-ha-long",
        "posted_at": now - timedelta(days=2),
        "expires_at": now + timedelta(days=25),
    },
    {
        "title": "Kế Toán Tổng Hợp Doanh Nghiệp Du Lịch & Dịch Vụ",
        "company_name": "Công ty Cổ phần Công nghệ Thông tin Hạ Long (HaLong Tech)",
        "description": "Lập báo cáo thuế, báo cáo tài chính nội bộ định kỳ. Theo dõi công nợ khách hàng và đối tác du lịch. Kiểm soát chi phí hoạt động dự án công nghệ.",
        "requirements": "Tốt nghiệp chuyên ngành Tài chính - Kế toán. Thành thạo phần mềm MISA, Excel. Cẩn thận, trung thực, có ít nhất 2 năm kinh nghiệm kế toán tổng hợp.",
        "salary_min": 10000000,
        "salary_max": 15000000,
        "salary_text": "10 - 15 triệu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Khu đô thị Cột 5 - Cột 8, Phường Hồng Hà, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Kế toán / Kiểm toán",
        "experience_level": "Có kinh nghiệm",
        "source_platform": "CareerBuilder",
        "source_url": "https://careerbuilder.vn/viec-lam/ke-toan-tong-hop-ha-long-quang-ninh",
        "posted_at": now - timedelta(hours=12),
        "expires_at": now + timedelta(days=20),
    },
    {
        "title": "Nhân Viên Điều Độ Cảng Biển & Giám Sát Logistics Container",
        "company_name": "Cảng Quốc tế Quảng Ninh (Quang Ninh Port)",
        "description": "Theo dõi kế hoạch cập cảng của tàu hàng, xếp dỡ hàng hóa container và hàng rời. Điều phối phương tiện cơ giới tại bãi cảng, lập biên bản giao nhận.",
        "requirements": "Sức khỏe tốt, chịu được áp lực làm việc theo ca. Ưu tiên tốt nghiệp ngành Hàng hải, Logistics, Kinh tế vận tải. Tiếng Anh giao tiếp cơ bản đọc hiểu chứng từ.",
        "salary_min": 11000000,
        "salary_max": 16000000,
        "salary_text": "11 - 16 triệu",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Cảng Cái Lân, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Vận tải / Kho vận",
        "experience_level": "Mới tốt nghiệp / 1 năm",
        "source_platform": "Facebook (Tuyển dụng Quảng Ninh)",
        "source_url": "https://facebook.com/groups/tuyendungquangninh/posts/dieu-do-cang-cailan-2024",
        "posted_at": now - timedelta(days=3),
        "expires_at": now + timedelta(days=15),
    },
    {
        "title": "Kỹ Sư Cơ Điện Hầm Lò & Tự Động Hóa Mỏ",
        "company_name": "Tập đoàn Công nghiệp Than - Khoáng sản Việt Nam (TKV - Vùng Cẩm Phả)",
        "description": "Giám sát, bảo trì hệ thống tời trục, băng tải điện và trạm biến áp mỏ hầm lò. Đảm bảo an toàn kỹ thuật điện và thiết bị máy mỏ.",
        "requirements": "Tốt nghiệp ĐH chuyên ngành Điện khí hóa xí nghiệp mỏ, Cơ điện mỏ, Tự động hóa. Ưu tiên có hộ khẩu tại Quảng Ninh (Cẩm Phả, Hạ Long).",
        "salary_min": 18000000,
        "salary_max": 30000000,
        "salary_text": "18 - 30 triệu (Đầy đủ chế độ hầm lò)",
        "location_province": "Quảng Ninh",
        "location_district": "Cẩm Phả",
        "location_full": "Phường Cẩm Tây, TP. Cẩm Phả, Quảng Ninh",
        "job_type": "full-time",
        "category": "Kỹ thuật / Cơ điện",
        "experience_level": "Trung cấp / Kỹ sư",
        "source_platform": "VietnamWorks",
        "source_url": "https://vietnamworks.com/viec-lam/ky-su-co-dien-ham-lo-cam-pha-quang-ninh",
        "posted_at": now - timedelta(days=4),
        "expires_at": now + timedelta(days=35),
    },
    {
        "title": "Bác Sĩ Đa Khoa / Hồi Sức Cấp Cứu",
        "company_name": "Bệnh viện Đa khoa Quốc tế Vinmec Hạ Long",
        "description": "Thăm khám, chẩn đoán và điều trị bệnh nhân tại khoa Cấp cứu & Nội tổng quát. Phối hợp hội chẩn cùng các chuyên gia quốc tế.",
        "requirements": "Tốt nghiệp Bác sĩ Đa khoa, có chứng chỉ hành nghề. Ít nhất 3 năm kinh nghiệm lâm sàng. Có chế độ phụ cấp thu hút nhân tài về Hạ Long.",
        "salary_min": 30000000,
        "salary_max": 60000000,
        "salary_text": "30 - 60 triệu (Thỏa thuận theo năng lực)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "10A Lê Thánh Tông, Hồng Gai, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Y tế / Chăm sóc sức khỏe",
        "experience_level": "Chuyên gia / Bác sĩ",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/bac-si-vinmec-ha-long-2024",
        "posted_at": now - timedelta(days=2),
        "expires_at": now + timedelta(days=40),
    },
    {
        "title": "Giáo Viên Tiếng Anh Giao Tiếp & IELTS (Full-time / Part-time)",
        "company_name": "Trung tâm Ngoại ngữ Quốc tế Quảng Ninh",
        "description": "Giảng dạy các lớp thiếu nhi, thiếu niên và luyện thi IELTS từ 5.5 - 7.0. Tham gia xây dựng giáo án sáng tạo, tổ chức CLB tiếng Anh cuối tuần tại Hạ Long.",
        "requirements": "IELTS 7.0+ hoặc chứng chỉ TESOL/CELTA. Nhiệt huyết, phát âm chuẩn, yêu thích giảng dạy. Chấp nhận sinh viên năm cuối xuất sắc.",
        "salary_min": 8000000,
        "salary_max": 18000000,
        "salary_text": "8 - 18 triệu (hoặc 250k - 400k/giờ)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Trần Hưng Đạo, TP. Hạ Long, Quảng Ninh",
        "job_type": "part-time",
        "category": "Giáo dục / Đào tạo",
        "experience_level": "Fresher / Đã có kinh nghiệm",
        "source_platform": "Facebook (Hội Việc Làm Hạ Long)",
        "source_url": "https://facebook.com/groups/vieclamhalong/posts/giao-vien-tieng-anh-2024",
        "posted_at": now - timedelta(days=1),
        "expires_at": now + timedelta(days=15),
    },
    {
        "title": "Nhân Viên Marketing & Sáng Tạo Nội Dung Du Lịch Hạ Long (TikTok / Fanpage)",
        "company_name": "Tập đoàn Sun Group - Vùng Đông Bắc",
        "description": "Lên kịch bản, quay dựng video ngắn quảng bá danh lam Hạ Long, các show diễn tại Sun World. Vận hành kênh mạng xã hội, bắt trend du lịch.",
        "requirements": "Có khiếu thẩm mỹ, quay dựng cơ bản (CapCut, Premiere). Năng động, thích khám phá các điểm check-in tại Quảng Ninh.",
        "salary_min": 10000000,
        "salary_max": 16000000,
        "salary_text": "10 - 16 triệu + Thưởng KPI view",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Bãi Cháy, TP. Hạ Long, Quảng Ninh",
        "job_type": "full-time",
        "category": "Marketing / Truyền thông",
        "experience_level": "Fresher / 1 năm",
        "source_platform": "TimViecNhanh",
        "source_url": "https://timviecnhanh.com/viec-lam/marketing-sang-tao-sun-world-halong",
        "posted_at": now - timedelta(hours=6),
        "expires_at": now + timedelta(days=30),
    },

    # --- Hà Nội & TP. HCM & Đà Nẵng ---
    {
        "title": "Senior Python / FastAPI Backend Engineer (Remote)",
        "company_name": "FPT Software Hà Nội",
        "description": "Thiết kế kiến trúc vi dịch vụ (Microservices), tối ưu hóa cơ sở dữ liệu lớn và crawler dữ liệu tự động. Xây dựng API tốc độ cao phục vụ hàng triệu người dùng.",
        "requirements": "Trên 4 năm kinh nghiệm Python, FastAPI/Django, PostgreSQL, Redis, Docker. Thành thạo thiết kế RESTful API và bất đồng bộ asyncio.",
        "salary_min": 35000000,
        "salary_max": 55000000,
        "salary_text": "35 - 55 triệu (Có thưởng dự án)",
        "location_province": "Hà Nội",
        "location_district": "Cầu Giấy",
        "location_full": "Tòa nhà FPT, Phố Duy Tân, Cầu Giấy, Hà Nội (Hỗ trợ Remote toàn quốc)",
        "job_type": "remote",
        "category": "Công nghệ thông tin",
        "experience_level": "Senior / 4+ năm",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/senior-python-fastapi-fpt-remote",
        "posted_at": now - timedelta(days=1),
        "expires_at": now + timedelta(days=30),
    },
    {
        "title": "Frontend React / Next.js Developer",
        "company_name": "VNG Corporation",
        "description": "Phát triển giao diện ứng dụng web Next.js 14 hiện đại, tối ưu SEO và trải nghiệm di động mượt mà. Phối hợp chặt chẽ cùng UI/UX Designer.",
        "requirements": "Tối thiểu 2 năm kinh nghiệm React, TypeScript, Tailwind CSS, Next.js. Nắm vững SSR, Responsive Design, REST API.",
        "salary_min": 22000000,
        "salary_max": 35000000,
        "salary_text": "22 - 35 triệu",
        "location_province": "TP. Hồ Chí Minh",
        "location_district": "Quận 7",
        "location_full": "VNG Campus, Khu chế xuất Tân Thuận, Quận 7, TP. HCM",
        "job_type": "full-time",
        "category": "Công nghệ thông tin",
        "experience_level": "Middle / 2-4 năm",
        "source_platform": "VietnamWorks",
        "source_url": "https://vietnamworks.com/viec-lam/frontend-nextjs-vng-hcm",
        "posted_at": now - timedelta(days=2),
        "expires_at": now + timedelta(days=28),
    },
    {
        "title": "Chuyên Viên Tuyển Dụng & Phát Triển Nhân Tài (HR Talent Acquisition)",
        "company_name": "FPT Software Hà Nội",
        "description": "Tìm kiếm, sàng lọc và phỏng vấn ứng viên ngành công nghệ. Mở rộng mạng lưới tuyển dụng đến các trường đại học tại các tỉnh miền Bắc.",
        "requirements": "Ít nhất 1.5 năm kinh nghiệm tuyển dụng IT/Tech. Kỹ năng giao tiếp, thương lượng xuất sắc, chủ động và linh hoạt.",
        "salary_min": 13000000,
        "salary_max": 20000000,
        "salary_text": "13 - 20 triệu",
        "location_province": "Hà Nội",
        "location_district": "Nam Từ Liêm",
        "location_full": "Khu công nghệ cao Hòa Lạc / Cầu Giấy, Hà Nội",
        "job_type": "full-time",
        "category": "Nhân sự / Hành chính",
        "experience_level": "Chuyên viên",
        "source_platform": "CareerBuilder",
        "source_url": "https://careerbuilder.vn/viec-lam/hr-talent-acquisition-fpt-hanoi",
        "posted_at": now - timedelta(days=3),
        "expires_at": now + timedelta(days=20),
    },
    {
        "title": "Thực Tập Sinh Lập Trình Web (Intern Web Developer - Hỗ trợ phụ cấp)",
        "company_name": "Công ty Cổ phần Công nghệ Thông tin Hạ Long (HaLong Tech)",
        "description": "Được đào tạo bài bản về Python FastAPI và Next.js. Tham gia trực tiếp dự án thật về số hóa du lịch và hệ thống cổng thông tin.",
        "requirements": "Sinh viên năm 3, 4 ngành CNTT hoặc tự học lập trình nghiêm túc. Có kiến thức cơ bản về HTML/CSS/JS/Python. Ham học hỏi.",
        "salary_min": 3000000,
        "salary_max": 5000000,
        "salary_text": "3 - 5 triệu (Hỗ trợ thực tập + cơ hội lên chính thức)",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Phường Hồng Gai, TP. Hạ Long, Quảng Ninh",
        "job_type": "intern",
        "category": "Công nghệ thông tin",
        "experience_level": "Thực tập sinh",
        "source_platform": "TopCV",
        "source_url": "https://topcv.vn/viec-lam/intern-developer-halongtech-quangninh",
        "posted_at": now - timedelta(hours=8),
        "expires_at": now + timedelta(days=45),
    },
]


def seed_data():
    session = SyncSessionLocal()
    try:
        # 1. Thêm công ty
        company_map = {}
        for c_data in SAMPLE_COMPANIES:
            existing = session.query(Company).filter(Company.name == c_data["name"]).first()
            if not existing:
                comp = Company(
                    id=str(uuid.uuid4()),
                    name=c_data["name"],
                    logo_url=c_data.get("logo_url"),
                    website=c_data.get("website"),
                    province=c_data.get("province"),
                    description=c_data.get("description"),
                    industry=c_data.get("industry"),
                )
                session.add(comp)
                session.flush()
                company_map[c_data["name"]] = comp.id
                print(f"[+] Thêm công ty: {comp.name}")
            else:
                company_map[c_data["name"]] = existing.id

        # 2. Thêm việc làm
        inserted_jobs = 0
        for j_data in SAMPLE_JOBS:
            url = j_data["source_url"]
            existing = session.query(Job).filter(Job.source_url == url).first()
            if not existing:
                comp_id = company_map.get(j_data.get("company_name"))
                job = Job(
                    id=str(uuid.uuid4()),
                    title=j_data["title"],
                    company_name=j_data.get("company_name"),
                    company_id=comp_id,
                    description=j_data.get("description"),
                    requirements=j_data.get("requirements"),
                    salary_min=j_data.get("salary_min"),
                    salary_max=j_data.get("salary_max"),
                    salary_text=j_data.get("salary_text"),
                    location_province=j_data.get("location_province"),
                    location_district=j_data.get("location_district"),
                    location_full=j_data.get("location_full"),
                    job_type=j_data.get("job_type", "full-time"),
                    category=j_data.get("category"),
                    experience_level=j_data.get("experience_level"),
                    source_platform=j_data.get("source_platform"),
                    source_url=url,
                    posted_at=j_data.get("posted_at"),
                    expires_at=j_data.get("expires_at"),
                    crawled_at=now,
                    is_active=True,
                )
                session.add(job)
                inserted_jobs += 1
                print(f"[+] Thêm việc làm: {job.title} ({job.location_province})")

        session.commit()
        print(f"\n===> Hoàn thành nạp dữ liệu! Đã thêm {inserted_jobs} việc làm mới.")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi nạp dữ liệu: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
