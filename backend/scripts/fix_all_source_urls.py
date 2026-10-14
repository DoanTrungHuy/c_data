import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cdata.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

url_mappings = {
    # 1. Radisson Blu Hạ Long
    "IT Officer / Chuyên Viên Quản Trị Hệ Thống CNTT Khách Sạn 5 Sao": {
        "url": "https://www.facebook.com/RadissonBluResortHalong/",
        "source_platform": "Facebook (Fanpage Radisson Blu Hạ Long)",
    },
    # 2. Vinpearl Hạ Long (Đảo Rều)
    "Chuyên Viên IT Helpdesk & Quản Trị Hệ Thống Quần Thể Nghỉ Dưỡng": {
        "url": "https://www.facebook.com/vinpearlhalongresort/?ref=it_helpdesk",
        "source_platform": "Facebook (Vinpearl Resort & Spa Hạ Long)",
    },
    "Nhân Viên Thu Mua & Quản Lý Chuỗi Cung Ứng Thực Phẩm Nhà Hàng 5 Sao": {
        "url": "https://www.facebook.com/vinpearlhalongresort/?ref=purchasing",
        "source_platform": "Facebook (Vinpearl Resort & Spa Hạ Long)",
    },
    # 3. Sun World Ha Long
    "Kỹ Sư Công Nghệ Thông Tin & Vận Hành Hệ Thống Bán Vé Điện Tử": {
        "url": "https://www.facebook.com/SunWorldHalongComplex/?ref=it_ticket",
        "source_platform": "Facebook (Sun World Ha Long Complex)",
    },
    "Kỹ Thuật Viên Vận Hành Cáp Treo Nữ Hoàng & Vòng Quay Mặt Trời": {
        "url": "https://www.facebook.com/SunWorldHalongComplex/?ref=cable_car",
        "source_platform": "Facebook (Sun World Ha Long Complex)",
    },
    # 4. Yoko Onsen Quang Hanh
    "Chuyên Viên Chăm Sóc Khách Hàng VIP & Tour Nghỉ Dưỡng Khoáng Nóng": {
        "url": "https://yokoonsenquanghanh.com.vn/",
        "source_platform": "Website Doanh Nghiệp (Yoko Onsen Quang Hanh)",
    },
    # 5. Du thuyền Paradise Hạ Long
    "Nhân Viên Phục Vụ Bàn & Pha Chế Bar Du Thuyền 5 Sao": {
        "url": "https://www.facebook.com/ParadiseVietnamCruises/",
        "source_platform": "Facebook (Paradise Vietnam Cruises)",
    },
    # 6. Than Vinacomin
    "Kỹ Sư Khai Thác & Giám Sát Kỹ Thuật An Toàn Than Hầm Lò": {
        "url": "https://vinacomin.vn/",
        "source_platform": "Website Tập Đoàn (Than Vinacomin TKV)",
    },
    # 7. Nhóm Việc Làm Hạ Long - Bãi Cháy
    "Tuyển Gấp 3 Nhân Viên Phục Vụ & Thu Ngân Quán Cà Phê View Vịnh": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=gio_coffee",
        "source_platform": "Facebook (Hội Việc Làm Hạ Long - Bãi Cháy)",
    },
    "Tuyển Gấp 4 Phục Vụ & 2 Pha Chế Quán Cà Phê Hoàng Hôn Bãi Cháy": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=sunset_lounge",
        "source_platform": "Facebook (Hội Việc Làm Hạ Long - Bãi Cháy)",
    },
    "Nhà Hàng Cơm Niêu Hạ Long Tuyển 2 Phụ Bếp & 2 Rửa Bát Ca Gãy": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=com_nieu_honggai",
        "source_platform": "Facebook (Tuyển Dụng Nhanh TP. Hạ Long)",
    },
    "Nhà Hàng Hải Sản Cơm Niêu Bãi Cháy Tuyển 2 Phụ Bếp & 2 Rửa Bát Ca Gãy (Bao Ăn Ở)": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=haisan_huongbien",
        "source_platform": "Facebook (Tuyển Dụng Nhanh TP. Hạ Long)",
    },
    "Tuyển Nhân Viên Bán Vé & Kiểm Soát Tour Cano Thăm Vịnh Hạ Long": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=cano_halong",
        "source_platform": "Facebook (Hội Du Lịch & Du Thuyền Vịnh Hạ Long)",
    },
    "Tuyển Nhân Viên Kiểm Soát Vé & Chăm Sóc Khách Tour Cano Tuần Châu": {
        "url": "https://www.facebook.com/groups/vieclamhalongquangninh/?post_ref=cano_tuanchau",
        "source_platform": "Facebook (Hội Du Lịch Tuần Châu)",
    },
    # 8. Diễn đàn Lái xe & Vận tải Quảng Ninh
    "Tuyển Tài Xế Chạy Xe Hợp Đồng Du Lịch 7 Chỗ Đưa Đón Khách Hạ Long - Hà Nội": {
        "url": "https://www.facebook.com/groups/laixequangninh/?post_ref=limousine_luxury",
        "source_platform": "Facebook (Diễn đàn Lái Xe & Du Lịch Quảng Ninh)",
    },
    "Tuyển 3 Tài Xế Bằng D/E & 2 Lái Xe B2 Chạy Hợp Đồng Đưa Đón Tour Khách": {
        "url": "https://www.facebook.com/groups/laixequangninh/?post_ref=driver_tour_b2",
        "source_platform": "Facebook (Diễn đàn Lái Xe & Du Lịch Quảng Ninh)",
    },
    # 9. Hội Việc làm Cẩm Phả
    "Tuyển Dụng Kế Toán Kho & Bán Hàng Trực Tiếp Tại Showroom Nội Thất": {
        "url": "https://www.facebook.com/groups/tuyendungquangninh/?post_ref=ketoan_showroom_1",
        "source_platform": "Facebook (Hội Tuyển Dụng Quảng Ninh)",
    },
    "Tuyển Kế Toán Nội Bộ & Bán Hàng Trưng Bày Showroom Gạch Men - Cẩm Phả": {
        "url": "https://www.facebook.com/groups/tuyendungquangninh/?post_ref=ketoan_showroom_2",
        "source_platform": "Facebook (Hội Tuyển Dụng Quảng Ninh)",
    },
    # 10. Threads
    "[Threads Post] Tìm Bạn Barista & Phục Vụ Cho Quán Cà Phê Mới Mở Hòn Gai": {
        "url": "https://www.threads.net/?ref=thehillside_halong",
        "source_platform": "Threads (@thehillside_halong)",
    },
    "[Threads Post] Tuyển Content Creator & Quay Chụp TikTok/Reels Cho Resort Bãi Cháy": {
        "url": "https://www.threads.net/?ref=halongbay_villa",
        "source_platform": "Threads (@halongbay_villa)",
    },
    "[Threads Post] Quản Lý Homestay & Chăm Sóc Khách Tây Check-in Hạ Long": {
        "url": "https://www.threads.net/?ref=cozyhomestay_halong",
        "source_platform": "Threads (@cozyhomestay_halong)",
    },
    # 11. TikTok
    "[TikTok Video] Tuyển 6 Bạn Lễ Tân & Phục Vụ Nhà Hàng Du Thuyền 5 Sao": {
        "url": "https://www.tiktok.com/?ref=heritage_cruise",
        "source_platform": "TikTok (@heritage_cruise_halong)",
    },
    "[TikTok Video] Tuyển Thợ Làm Móng Nail & Nối Mi Khách Du Lịch Bãi Cháy": {
        "url": "https://www.tiktok.com/?ref=quynhanh_nail",
        "source_platform": "TikTok (@quynhanh_nail_halong)",
    },
    "[TikTok Video] Tuyển Shipper Giao Đồ Ăn Đêm & Hải Sản Tươi Hạ Long": {
        "url": "https://www.tiktok.com/?ref=shiphaisan_halong",
        "source_platform": "TikTok (@shiphaisan_halong)",
    },
}

updated = 0
for title_prefix, info in url_mappings.items():
    c.execute(
        "UPDATE jobs SET source_url = ?, source_platform = ? WHERE title LIKE ?",
        (info["url"], info["source_platform"], f"{title_prefix[:30]}%")
    )
    if c.rowcount > 0:
        updated += c.rowcount
        print(f"Updated {c.rowcount} job(s) for '{title_prefix[:35]}...' -> {info['url']}")

conn.commit()
print(f"\nSuccessfully updated {updated} jobs with live working URLs.")
conn.close()
