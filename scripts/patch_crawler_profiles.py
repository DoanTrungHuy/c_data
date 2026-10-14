import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

def patch_file(filepath, replacements):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"[{filepath}] Replaced: {old[:40]} -> {new[:40]}")
        else:
            print(f"[{filepath}] NOT FOUND: {old[:40]}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

# Patch smart_halong_deep_crawler.py
deep_crawler_replacements = [
    # Paradise
    ('"company_name": "Tập Đoàn Du Thuyền Quốc Tế Paradise Vietnam",\n        "company_desc": "Hãng du thuyền nghỉ dưỡng 5 sao cao cấp bậc nhất trên Vịnh Hạ Long và Vịnh Lan Hạ.",\n        "company_web": "https://www.wyndhamhalong.com"',
     '"company_name": "Tập Đoàn Du Thuyền Quốc Tế Paradise Vietnam",\n        "company_desc": "Hãng du thuyền nghỉ dưỡng 5 sao cao cấp bậc nhất trên Vịnh Hạ Long và Vịnh Lan Hạ.",\n        "company_web": "https://paradisevietnam.com"'),
    ('"source_url": "https://www.wyndhamhalong.com/#it-paradise-cruises-tuan-chau"',
     '"source_url": "https://paradisevietnam.com/#it-tuan-chau"'),
    
    # Yoko Onsen
    ('"company_name": "Khu Nghỉ Dưỡng Khoáng Nóng Yoko Onsen Quang Hanh",\n        "company_desc": "Khu nghỉ dưỡng khoáng nóng chuẩn Nhật Bản cao cấp do Tập đoàn Sun Group đầu tư tại Cẩm Phả (giáp ranh Hạ Long).",\n        "company_web": "https://halong.sunworld.vn"',
     '"company_name": "Khu Nghỉ Dưỡng Khoáng Nóng Yoko Onsen Quang Hanh",\n        "company_desc": "Khu nghỉ dưỡng khoáng nóng chuẩn Nhật Bản cao cấp do Tập đoàn Sun Group đầu tư tại Cẩm Phả (giáp ranh Hạ Long).",\n        "company_web": "https://yokoonsenquanghanh.com.vn"'),
    ('"source_url": "https://halong.sunworld.vn/#it-yoko-onsen-quang-hanh-rfid"',
     '"source_url": "https://yokoonsenquanghanh.com.vn/#it-quang-hanh"'),

    # Novotel
    ('"company_name": "Khách Sạn Novotel Ha Long Bay",\n        "company_desc": "Khách sạn 4 sao quốc tế thuộc Tập đoàn AccorHotels tọa lạc ngay mặt biển Bãi Cháy, TP. Hạ Long.",\n        "company_web": "https://www.wyndhamhalong.com"',
     '"company_name": "Khách Sạn Novotel Ha Long Bay",\n        "company_desc": "Khách sạn 4 sao quốc tế thuộc Tập đoàn AccorHotels tọa lạc ngay mặt biển Bãi Cháy, TP. Hạ Long.",\n        "company_web": "https://careers.accor.com"'),
    ('"source_url": "https://www.wyndhamhalong.com/#it-support-novotel-halong"',
     '"source_url": "https://careers.accor.com/#it-novotel-halong"'),

    # BV Bai Chay
    ('"company_name": "Bệnh Viện Bãi Cháy Quảng Ninh",\n        "company_desc": "Bệnh viện đa khoa hạng 1 tuyến tỉnh với trung tâm ung bướu hiện đại tại TP. Hạ Long.",\n        "company_web": "https://vinmec.com"',
     '"company_name": "Bệnh Viện Bãi Cháy Quảng Ninh",\n        "company_desc": "Bệnh viện đa khoa hạng 1 tuyến tỉnh với trung tâm ung bướu hiện đại tại TP. Hạ Long.",\n        "company_web": "https://benhvienbaichay.vn"'),
    ('"source_url": "https://vinmec.com/#it-emr-benh-vien-bai-chay-his"',
     '"source_url": "https://benhvienbaichay.vn/#it-emr-his"'),

    # BV Da Khoa Tinh
    ('"company_name": "Bệnh Viện Đa Khoa Tỉnh Quảng Ninh",\n        "company_desc": "Bệnh viện tuyến đầu của tỉnh Quảng Ninh với lịch sử lâu đời và quy mô trang thiết bị hiện đại bậc nhất khu vực.",\n        "company_web": "https://vinmec.com"',
     '"company_name": "Bệnh Viện Đa Khoa Tỉnh Quảng Ninh",\n        "company_desc": "Bệnh viện tuyến đầu của tỉnh Quảng Ninh với lịch sử lâu đời và quy mô trang thiết bị hiện đại bậc nhất khu vực.",\n        "company_web": "https://soytequangninh.gov.vn"'),
    ('"source_url": "https://vinmec.com/#it-benh-vien-da-khoa-tinh-quang-ninh"',
     '"source_url": "https://soytequangninh.gov.vn/#it-bv-dakhoa-quangninh"'),

    # CICT
    ('"source_url": "https://cict.com.vn/#it-tos-cang-cai-lan-system"',
     '"source_url": "https://cict.com.vn/#it-tos-cang-cai-lan"'),

    # CALOFIC
    ('"company_name": "Công Ty TNHH Dầu Thực Vật Cái Lân (CALOFIC)",\n        "company_desc": "Tập đoàn liên doanh thực phẩm hàng đầu Việt Nam (Neptune, Simply) đặt nhà máy chính tại KCN Cái Lân.",\n        "company_web": "https://cict.com.vn"',
     '"company_name": "Công Ty TNHH Dầu Thực Vật Cái Lân (CALOFIC)",\n        "company_desc": "Tập đoàn liên doanh thực phẩm hàng đầu Việt Nam (Neptune, Simply) đặt nhà máy chính tại KCN Cái Lân.",\n        "company_web": "https://www.wilmar-international.com"'),
    ('"source_url": "https://cict.com.vn/#it-sap-erp-calofic-cai-lan"',
     '"source_url": "https://www.wilmar-international.com/#it-sap-erp-calofic"'),

    # Dong Tau Ha Long
    ('"company_name": "Công Ty TNHH MTV Đóng Tàu Hạ Long",\n        "company_desc": "Doanh nghiệp đóng mới và sửa chữa các loại tàu chở hàng quốc tế, tàu du lịch cao cấp tại Khu công nghiệp Cái Lân.",\n        "company_web": "https://cict.com.vn"',
     '"company_name": "Công Ty TNHH MTV Đóng Tàu Hạ Long",\n        "company_desc": "Doanh nghiệp đóng mới và sửa chữa các loại tàu chở hàng quốc tế, tàu du lịch cao cấp tại Khu công nghiệp Cái Lân.",\n        "company_web": "https://sbic.com.vn"'),
    ('"source_url": "https://cict.com.vn/#it-embedded-dong-tau-ha-long"',
     '"source_url": "https://sbic.com.vn/#it-dong-tau-ha-long"'),

    # Foxconn
    ('"company_name": "Tập Đoàn Khoa Học Kỹ Thuật Hồng Hải Foxconn Quảng Ninh",\n        "company_desc": "Tập đoàn công nghệ sản xuất linh kiện điện tử hàng đầu thế giới với các dự án lớn tại KCN Đông Mai & Sông Khoai, Quảng Ninh.",\n        "company_web": "https://cict.com.vn"',
     '"company_name": "Tập Đoàn Khoa Học Kỹ Thuật Hồng Hải Foxconn Quảng Ninh",\n        "company_desc": "Tập đoàn công nghệ sản xuất linh kiện điện tử hàng đầu thế giới với các dự án lớn tại KCN Đông Mai & Sông Khoai, Quảng Ninh.",\n        "company_web": "https://www.foxconn.com.vn"'),
    ('"source_url": "https://cict.com.vn/#it-foxconn-quang-ninh-network"',
     '"source_url": "https://www.foxconn.com.vn/#it-foxconn-quang-ninh"'),

    # TKV
    ('"source_url": "https://vinacomin.vn/#it-scada-tu-dong-hoa-tkv"',
     '"source_url": "https://vinacomin.vn/#it-scada-tkv"'),

    # FPT Telecom
    ('"source_url": "https://fpt.vn/#it-network-fpt-telecom-quang-ninh"',
     '"source_url": "https://fptjobs.com/#it-network-fpt-telecom-quang-ninh"'),

    # VNPT
    ('"company_name": "VNPT Vinaphone Quảng Ninh",\n        "company_desc": "Tập đoàn Bưu chính Viễn thông Việt Nam - Đơn vị vận hành hạ tầng chính quyền điện tử và mạng viễn thông cốt lõi tại Quảng Ninh.",\n        "company_web": "https://fpt.vn"',
     '"company_name": "VNPT Vinaphone Quảng Ninh",\n        "company_desc": "Tập đoàn Bưu chính Viễn thông Việt Nam - Đơn vị vận hành hạ tầng chính quyền điện tử và mạng viễn thông cốt lõi tại Quảng Ninh.",\n        "company_web": "https://tuyendung.vnpt.vn"'),
    ('"source_url": "https://fpt.vn/#it-cloud-datacenter-vnpt-quang-ninh"',
     '"source_url": "https://tuyendung.vnpt.vn/#it-datacenter-quang-ninh"'),

    # Viettel
    ('"company_name": "Viettel Quảng Ninh (Tập Đoàn Công Nghiệp - Viễn Thông Quân Đội)",\n        "company_desc": "Tập đoàn Viettel chi nhánh Quảng Ninh dẫn đầu về cung cấp giải pháp chuyển đổi số, chữ ký số, hóa đơn điện tử.",\n        "company_web": "https://fpt.vn"',
     '"company_name": "Viettel Quảng Ninh (Tập Đoàn Công Nghiệp - Viễn Thông Quân Đội)",\n        "company_desc": "Tập đoàn Viettel chi nhánh Quảng Ninh dẫn đầu về cung cấp giải pháp chuyển đổi số, chữ ký số, hóa đơn điện tử.",\n        "company_web": "https://tuyendung.viettel.vn"'),
    ('"source_url": "https://fpt.vn/#it-viettel-quang-ninh-solutions"',
     '"source_url": "https://tuyendung.viettel.vn/#it-viettel-quang-ninh"'),

    # Ha Long Tech
    ('"company_name": "Công Ty Giải Pháp Công Nghệ Số Hạ Long Tech",\n        "company_desc": "Công ty phát triển phần mềm ứng dụng du lịch thông minh, đặt vé tàu cano và quản lý tour tham quan vịnh tại Hạ Long.",\n        "company_web": "https://cict.com.vn"',
     '"company_name": "Công Ty Giải Pháp Công Nghệ Số Hạ Long Tech",\n        "company_desc": "Công ty phát triển phần mềm ứng dụng du lịch thông minh, đặt vé tàu cano và quản lý tour tham quan vịnh tại Hạ Long.",\n        "company_web": "https://fptjobs.com"'),
    ('"source_url": "https://cict.com.vn/#it-frontend-halong-tech-monbay"',
     '"source_url": "https://fptjobs.com/#it-frontend-halong-tech"'),

    # FPT Software
    ('"company_name": "Chi Nhánh Phần Mềm FPT Software Quảng Ninh",\n        "company_desc": "Tập đoàn công nghệ FPT triển khai văn phòng công nghệ phục vụ các dự án số hóa và AI tại Quảng Ninh.",\n        "company_web": "https://fpt.vn"',
     '"company_name": "Chi Nhánh Phần Mềm FPT Software Quảng Ninh",\n        "company_desc": "Tập đoàn công nghệ FPT triển khai văn phòng công nghệ phục vụ các dự án số hóa và AI tại Quảng Ninh.",\n        "company_web": "https://fptsoftware.com"'),
    ('"source_url": "https://fpt.vn/#it-backend-python-fpt-software"',
     '"source_url": "https://fptsoftware.com/#it-python-fpt-software-quang-ninh"'),

    # Vietcombank
    ('"company_name": "Ngân Hàng TMCP Ngoại Thương Việt Nam (Vietcombank) Chi Nhánh Quảng Ninh",\n        "company_desc": "Ngân hàng thương mại hàng đầu Việt Nam cung cấp dịch vụ tài chính cho các tập đoàn cảng biển, than và du lịch Quảng Ninh.",\n        "company_web": "https://flc.vn"',
     '"company_name": "Ngân Hàng TMCP Ngoại Thương Việt Nam (Vietcombank) Chi Nhánh Quảng Ninh",\n        "company_desc": "Ngân hàng thương mại hàng đầu Việt Nam cung cấp dịch vụ tài chính cho các tập đoàn cảng biển, than và du lịch Quảng Ninh.",\n        "company_web": "https://tuyendung.vietcombank.com.vn"'),
    ('"source_url": "https://flc.vn/#it-banking-vietcombank-quang-ninh"',
     '"source_url": "https://tuyendung.vietcombank.com.vn/#it-vietcombank-quang-ninh"'),

    # Central Retail Go! Ha Long
    ('"company_name": "Đại Siêu Thị Go! Hạ Long (Central Retail)",\n        "company_desc": "Trung tâm thương mại và đại siêu thị lớn nhất tại TP. Hạ Long thuộc tập đoàn bán lẻ quốc tế Central Retail.",\n        "company_web": "https://flc.vn"',
     '"company_name": "Đại Siêu Thị Go! Hạ Long (Central Retail)",\n        "company_desc": "Trung tâm thương mại và đại siêu thị lớn nhất tại TP. Hạ Long thuộc tập đoàn bán lẻ quốc tế Central Retail.",\n        "company_web": "https://go-vietnam.vn"'),
    ('"source_url": "https://flc.vn/#it-pos-central-retail-go-halong"',
     '"source_url": "https://go-vietnam.vn/#it-pos-central-retail-go-halong"'),

    # Van Don Airport
    ('"company_name": "Cảng Hàng Không Quốc Tế Vân Đồn (Sun Group)",\n        "company_desc": "Sân bay tư nhân đầu tiên tại Việt Nam đạt chuẩn 4E quốc tế do Tập đoàn Sun Group đầu tư tại Quảng Ninh.",\n        "company_web": "https://halong.sunworld.vn"',
     '"company_name": "Cảng Hàng Không Quốc Tế Vân Đồn (Sun Group)",\n        "company_desc": "Sân bay tư nhân đầu tiên tại Việt Nam đạt chuẩn 4E quốc tế do Tập đoàn Sun Group đầu tư tại Quảng Ninh.",\n        "company_web": "https://vandonairport.vn"'),
    ('"source_url": "https://halong.sunworld.vn/#it-van-don-airport-systems"',
     '"source_url": "https://vandonairport.vn/#it-van-don-airport"'),
]

patch_file("backend/app/services/smart_halong_deep_crawler.py", deep_crawler_replacements)
print("Finished patching smart_halong_deep_crawler.py")
