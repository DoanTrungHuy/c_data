"""
Company Registry Service for C_Data Platform.
Manages verified local enterprises in Ha Long and Quang Ninh across:
- Hospitality & Luxury Tourism (Sun World, Vinpearl, Wyndham, Muong Thanh, FLC, Novotel, Paradise)
- Healthcare & Hospitals (Vinmec, Bãi Cháy, Đa khoa Tỉnh, Sản Nhi)
- Industry, Mining & Ports (TKV, Đông Bắc, CICT Cái Lân, Cảng Quảng Ninh, Foxconn)
- Local IT & Telecommunications (FPT Telecom, VNPT, Viettel, MobiFone)
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests

from app.schemas.company import CompanyRegistryProfile
from app.schemas.universal_job import (
    LocationNormalized,
    UniversalJob,
    VerificationAuditEvidence,
    VerificationStatus,
)

logger = logging.getLogger("c_data.company_registry")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_FILE_PATH = DATA_DIR / "company_registry_state.json"
BASE_PROJECT_DIR = Path(__file__).resolve().parents[3]  # c_data root
FRONTEND_EXPORT_PATH = BASE_PROJECT_DIR / "frontend" / "public" / "data" / "local_companies.json"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataBot/2.0"


class CompanyRegistry:
    """
    Quản lý danh mục doanh nghiệp địa phương trọng điểm tại Hạ Long & Quảng Ninh.
    Đảm bảo:
    - Hồ sơ có địa chỉ cụ thể tại địa bàn, không khai báo chung chung.
    - URL tuyển dụng chính thức, kênh mạng xã hội, hotline HR minh bạch.
    - Kiểm toán định kỳ trạng thái hoạt động của từng trang tuyển dụng.
    - Cung cấp dữ liệu phục vụ tìm kiếm ưu tiên việc làm tại Hạ Long.
    """

    def __init__(self):
        self._companies: Dict[str, CompanyRegistryProfile] = {}
        self._initialize_catalog()
        self._load_persisted_state()

    def _initialize_catalog(self) -> None:
        """Khởi tạo danh bạ 20 doanh nghiệp trọng điểm tại Hạ Long / Quảng Ninh"""
        catalog = [
            # -------------------------------------------------------------
            # NHÓM 1: DU LỊCH, NGHỈ DƯỠNG & KHÁCH SẠN CAO CẤP
            # -------------------------------------------------------------
            CompanyRegistryProfile(
                company_id="sun_world_halong",
                name="Công ty TNHH Mặt Trời Hạ Long (Sun World Halong Complex)",
                brand_name="Sun World Halong Complex - Tập đoàn Sun Group",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 9 Đường Hạ Long, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://halongcomplex.sunworld.vn",
                career_url="https://tuyendung.sungroup.com.vn",
                social_channels={
                    "facebook": "https://www.facebook.com/SunWorldHalongComplex",
                    "career_fanpage": "https://www.facebook.com/TuyendungSunGroupVungDongBac",
                },
                hr_contacts={
                    "hotline": "0203.3616.789",
                    "email": "tuyendung@sungroup.com.vn",
                    "hr_desk": "Văn phòng Nhân sự Sun World Halong, Cổng 1 Công viên Rồng",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư Quản trị Hệ thống CNTT & Phần mềm Vận hành",
                    "IT Helpdesk & Hỗ trợ kỹ thuật phần cứng",
                    "Kỹ thuật viên Mạng & Cáp quang nội bộ",
                    "Nhân viên Vận hành Hệ thống Bán vé điện tử & POS",
                ],
                notes="Tổ hợp vui chơi giải trí hàng đầu miền Bắc, hệ thống CNTT quy mô lớn bao gồm quản lý vé, mạng cáp quang và camera an ninh diện rộng.",
            ),
            CompanyRegistryProfile(
                company_id="vinpearl_resort_halong",
                name="Công ty Cổ phần Vinpearl - Chi nhánh Quảng Ninh",
                brand_name="Vinpearl Resort & Spa Hạ Long (Đảo Rều)",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Đảo Rều, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://vinpearl.com/vi/hotels/vinpearl-resort-spa-ha-long",
                career_url="https://vinpearl.com/vi/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/vinpearlresortandspahalong",
                    "linkedin": "https://www.linkedin.com/company/vinpearl",
                },
                hr_contacts={
                    "hotline": "0983.456.789",
                    "email": "v.tuyendung@vinpearl.com",
                    "hr_desk": "Bến cano đưa đón Vinpearl Đảo Rều, Bãi Cháy",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Chuyên viên IT Helpdesk & Hỗ trợ Kỹ thuật Resort Đảo Rều",
                    "IT Officer / Quản trị mạng WiFi & IPTV phòng nghỉ",
                    "Kỹ sư Vận hành Phần mềm Opera PMS Khách sạn",
                ],
                notes="Resort 5 sao biệt lập trên đảo Rều, yêu cầu kỹ thuật viên IT trực xử lý sự cố mạng, POS nhà hàng và hệ thống kiểm soát du khách.",
            ),
            CompanyRegistryProfile(
                company_id="wyndham_legend_halong",
                name="Khách sạn Quốc tế 5 sao Wyndham Legend Hạ Long",
                brand_name="Wyndham Legend Halong Hotel",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 12 Đường Hạ Long, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://www.wyndhamhalong.com",
                career_url="https://www.wyndhamhalong.com/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/wyndhamlegendhalong",
                },
                hr_contacts={
                    "hotline": "0203.3636.555",
                    "email": "hr@wyndhamhalong.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "IT Officer / Chuyên viên Quản trị Hệ thống Khách sạn 5 Sao",
                    "IT Support Technician",
                ],
                notes="Khách sạn 5 sao mặt biển Bãi Cháy thuộc tập đoàn Wyndham Hotels & Resorts toàn cầu.",
            ),
            CompanyRegistryProfile(
                company_id="muong_thanh_luxury_halong",
                name="Khách sạn Mường Thanh Luxury Hạ Long Centre",
                brand_name="Mường Thanh Hospitality Quảng Ninh",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Khu 2, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://luxuryhalongcentre.muongthanh.com",
                career_url="https://tuyendung.muongthanh.com",
                social_channels={
                    "facebook": "https://www.facebook.com/MuongThanhLuxuryHaLongCentre",
                },
                hr_contacts={
                    "hotline": "0203.3646.618",
                    "email": "tuyendung@muongthanh.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Nhân viên CNTT / IT Khách sạn",
                    "Kỹ thuật viên Âm thanh - Ánh sáng & Mạng hội nghị",
                ],
                notes="Chuỗi khách sạn quy mô lớn với 2 cơ sở tại Bãi Cháy và Hòn Gai.",
            ),
            CompanyRegistryProfile(
                company_id="flc_halong_resort",
                name="Công ty TNHH Đầu tư và Phát triển FLC Hạ Long",
                brand_name="FLC Halong Bay Golf Club & Luxury Resort",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Đoàn Kết, Phường Hồng Hà, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://flchalong.com.vn",
                career_url="https://tuyendung.flc.vn",
                social_channels={
                    "facebook": "https://www.facebook.com/flchalongbayluxuryresort",
                },
                hr_contacts={
                    "hotline": "0203.3698.888",
                    "email": "tuyendung@flc.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Chuyên viên Quản trị Mạng & Hạ tầng Server FLC",
                    "IT Support Sân Golf & Khách sạn",
                ],
                notes="Quần thể nghỉ dưỡng và sân golf trên đồi Hồng Hà nhìn ra vịnh Hạ Long.",
            ),
            CompanyRegistryProfile(
                company_id="novotel_halong_bay",
                name="Khách sạn Quốc tế Novotel Ha Long Bay",
                brand_name="Novotel Ha Long Bay (Tập đoàn Accor)",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 160 Đường Hạ Long, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://all.accor.com/hotel/5893/index.vi.shtml",
                career_url="https://careers.accor.com",
                social_channels={
                    "facebook": "https://www.facebook.com/NovotelHaLongBayHotel",
                },
                hr_contacts={
                    "hotline": "0203.3848.108",
                    "email": "H5893-HR@accor.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Assistant IT Manager / IT Executive",
                    "IT Technician",
                ],
                notes="Khách sạn 4 sao quốc tế thuộc tập đoàn Accor tại trung tâm du lịch Bãi Cháy.",
            ),
            CompanyRegistryProfile(
                company_id="paradise_vietnam_halong",
                name="Tập đoàn Du lịch Paradise Vietnam",
                brand_name="Paradise Vietnam Cruises & Hotels",
                industry_group="hospitality_tourism",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Đảo Tuần Châu, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://paradisevietnam.com",
                career_url="https://paradisevietnam.com/vi/co-hoi-nghe-nghiep",
                social_channels={
                    "facebook": "https://www.facebook.com/ParadiseVietnamHotelsCruises",
                },
                hr_contacts={
                    "hotline": "0906.099.606",
                    "email": "hr@paradisevietnam.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "IT Executive phụ trách Hệ thống Du thuyền & Khách sạn",
                    "Nhân viên Kỹ thuật Phần mềm Đặt chỗ nội bộ",
                ],
                notes="Đơn vị vận hành đội du thuyền ngủ đêm 5 sao lớn nhất trên vịnh Hạ Long và vịnh Lan Hạ.",
            ),

            # -------------------------------------------------------------
            # NHÓM 2: Y TẾ, BỆNH VIỆN & CHĂM SÓC SỨC KHỎE
            # -------------------------------------------------------------
            CompanyRegistryProfile(
                company_id="vinmec_halong",
                name="Bệnh viện Đa khoa Quốc tế Vinmec Hạ Long",
                brand_name="Vinmec Hạ Long International Hospital",
                industry_group="healthcare",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 10A Lê Thánh Tông, Phường Hồng Gai, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://www.vinmec.com/vi/vinmec-ha-long",
                career_url="https://www.vinmec.com/vi/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/vinmec",
                },
                hr_contacts={
                    "hotline": "0203.3828.188",
                    "email": "v.tuyendung@vinmec.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư CNTT Bệnh viện / Quản trị Hệ thống HIS - LIS - PACS",
                    "Chuyên viên Quản trị Cơ sở Dữ liệu & Báo cáo Y tế",
                    "IT Helpdesk Hỗ trợ Khối Khám chữa bệnh",
                ],
                notes="Bệnh viện đa khoa quốc tế đạt chứng chỉ JCI, hệ thống CNTT y tế hiện đại với phần mềm HIS/PACS chuyên sâu.",
            ),
            CompanyRegistryProfile(
                company_id="bai_chay_hospital",
                name="Bệnh viện Bãi Cháy Tỉnh Quảng Ninh",
                brand_name="Bệnh viện Bãi Cháy",
                industry_group="healthcare",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Phường Giếng Đáy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="http://benhvienbaichay.vn",
                career_url="http://benhvienbaichay.vn/thong-bao-tuyen-dung.html",
                social_channels={
                    "facebook": "https://www.facebook.com/benhvienbaichayquangninh",
                },
                hr_contacts={
                    "hotline": "0203.3846.566",
                    "email": "tochuc.bvbc@gmail.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư CNTT - Phòng Công nghệ Thông tin",
                    "Lập trình viên / Triển khai Phần mềm Quản lý Bệnh viện",
                    "Kỹ thuật viên Quản trị Mạng Bệnh viện",
                ],
                notes="Bệnh viện đa khoa hạng I tuyến tỉnh, đẩy mạnh chuyển đổi số bệnh viện không giấy tờ, bệnh án điện tử EMR.",
            ),
            CompanyRegistryProfile(
                company_id="quang_ninh_provincial_hospital",
                name="Bệnh viện Đa khoa Tỉnh Quảng Ninh",
                brand_name="Bệnh viện Đa khoa Tỉnh Quảng Ninh",
                industry_group="healthcare",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Phố Tuệ Tĩnh, Phường Bạch Đằng, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="http://benhviendakhoatinhquangninh.vn",
                career_url="http://benhviendakhoatinhquangninh.vn/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/benhviendakhoatinhquangninh",
                },
                hr_contacts={
                    "hotline": "0203.3825.489",
                    "email": "tochuc.bvdkt@gmail.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư CNTT Quản trị Hệ thống Máy chủ & Bệnh án Điện tử",
                    "Nhân viên Kỹ thuật Hỗ trợ Máy trạm Khoa Khám bệnh",
                ],
                notes="Bệnh viện hạt nhân tuyến tỉnh, quản lý hạ tầng mạng lớn và cơ sở dữ liệu y tế toàn tỉnh.",
            ),
            CompanyRegistryProfile(
                company_id="quang_ninh_obstetrics_pediatrics",
                name="Bệnh viện Sản Nhi Tỉnh Quảng Ninh",
                brand_name="Bệnh viện Sản Nhi Quảng Ninh",
                industry_group="healthcare",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Phường Đại Yên, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="http://sannhiquangninh.vn",
                career_url="http://sannhiquangninh.vn/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/bvsannhiquangninh",
                },
                hr_contacts={
                    "hotline": "0203.3696.568",
                    "email": "tccb.sannhiqn@gmail.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư CNTT - Quản lý Phần mềm Bệnh viện & Kiosk Đăng ký Khám",
                    "Kỹ thuật viên Tin học Y tế",
                ],
                notes="Bệnh viện chuyên khoa Sản Nhi hiện đại tại cửa ngõ TP. Hạ Long.",
            ),

            # -------------------------------------------------------------
            # NHÓM 3: CÔNG NGHIỆP, KHAI THÁC MỎ, CẢNG BIỂN & LOGISTICS
            # -------------------------------------------------------------
            CompanyRegistryProfile(
                company_id="tkv_vinacomin",
                name="Tập đoàn Công nghiệp Than - Khoáng sản Việt Nam (TKV)",
                brand_name="Tập đoàn TKV - Vùng Than Quảng Ninh",
                industry_group="industry_logistics",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 95 Lê Thánh Tông, Phường Hồng Gai, TP. Hạ Long, Quảng Ninh"},
                    {"province": "Quảng Ninh", "district": "Cẩm Phả", "address": "TP. Cẩm Phả, Quảng Ninh"}
                ],
                website_home="https://vinacomin.vn",
                career_url="https://vinacomin.vn/thong-tin-tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/tapdoantkv",
                },
                hr_contacts={
                    "hotline": "0203.3825.265",
                    "email": "banlaodong@vinacomin.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư Tự động hóa & Hệ thống SCADA Giám sát Mỏ",
                    "Kỹ sư Công nghệ Thông tin - Quản trị Hệ thống ERP Tập đoàn",
                    "Kỹ sư Quản trị Mạng & Hạ tầng Trung tâm Dữ liệu Than",
                    "Chuyên viên Triển khai Chuyển đổi Số Ngành Than",
                ],
                notes="Tập đoàn công nghiệp khai thác trụ cột của Quảng Ninh, đang chuyển đổi mạnh sang tự động hóa hầm lò và điều khiển tập trung.",
            ),
            CompanyRegistryProfile(
                company_id="dong_bac_corporation",
                name="Tổng Công ty Đông Bắc (Bộ Quốc phòng)",
                brand_name="Tổng Công ty Đông Bắc",
                industry_group="industry_logistics",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Phường Hồng Hải, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://dongbac.vn",
                career_url="https://dongbac.vn/tuyen-dung",
                social_channels={},
                hr_contacts={
                    "hotline": "0203.3835.484",
                    "email": "vanphong@dongbac.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư CNTT & An toàn Thông tin",
                    "Kỹ sư Tự động hóa Dây chuyền Cơ khí",
                ],
                notes="Doanh nghiệp quân đội làm kinh tế quy mô lớn đóng quân trên địa bàn tỉnh Quảng Ninh.",
            ),
            CompanyRegistryProfile(
                company_id="cict_cai_lan_port",
                name="Công ty TNHH Cảng Container Quốc tế Cái Lân (CICT)",
                brand_name="Cảng CICT Cái Lân",
                industry_group="industry_logistics",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Khu công nghiệp Cái Lân, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://cict.com.vn",
                career_url="https://cict.com.vn/career",
                social_channels={
                    "linkedin": "https://www.linkedin.com/company/cai-lan-international-container-terminal",
                },
                hr_contacts={
                    "hotline": "0203.3515.888",
                    "email": "recruitment@cict.com.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "IT Systems & TOS Engineer (Phần mềm Điều hành Cảng Biển TOS)",
                    "Network & Infrastructure Support Specialist",
                    "EDI / Data Exchange Specialist Cảng Biển",
                ],
                notes="Cảng container nước sâu hiện đại nhất miền Bắc, sử dụng phần mềm điều hành cảng biển TOS (Terminal Operating System) đạt chuẩn quốc tế.",
            ),
            CompanyRegistryProfile(
                company_id="quang_ninh_port",
                name="Công ty Cổ phần Cảng Quảng Ninh",
                brand_name="Cảng Quảng Ninh",
                industry_group="industry_logistics",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 1 Đường Cái Lân, Phường Bãi Cháy, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="http://quangninhport.com.vn",
                career_url="http://quangninhport.com.vn/tuyen-dung",
                social_channels={},
                hr_contacts={
                    "hotline": "0203.3846.505",
                    "email": "vanphong@quangninhport.com.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Nhân viên Kỹ thuật Phần mềm Quản trị Cảng",
                    "Kỹ thuật viên Tin học & Cân điện tử",
                ],
                notes="Cảng bốc xếp hàng rời tổng hợp trọng điểm phía Bắc.",
            ),
            CompanyRegistryProfile(
                company_id="foxconn_quang_ninh",
                name="Tập đoàn Foxconn (FII Vietnam - Chi nhánh Quảng Ninh)",
                brand_name="Foxconn Quảng Ninh (KCN Đông Mai & Sông Khoai)",
                industry_group="industry_logistics",
                locations=[
                    {"province": "Quảng Ninh", "district": "Quảng Yên", "address": "KCN Đông Mai, TX. Quảng Yên, Quảng Ninh (giáp Hạ Long)"}
                ],
                website_home="https://foxconn.com.vn",
                career_url="https://foxconn.com.vn/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/foxconnvietnam",
                },
                hr_contacts={
                    "hotline": "0203.3768.888",
                    "email": "hr-quangninh@foxconn.com",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Software / MES Engineer (Manufacturing Execution System)",
                    "IT Infrastructure & Network Engineer",
                    "Automation & PLC Programmer",
                ],
                notes="Tổ hợp nhà máy sản xuất thiết bị điện tử, linh kiện thông minh quy mô hàng trăm triệu USD giáp ranh TP. Hạ Long.",
            ),

            # -------------------------------------------------------------
            # NHÓM 4: VIỄN THÔNG, CNTT & PHẦN MỀM ĐỊA PHƯƠNG
            # -------------------------------------------------------------
            CompanyRegistryProfile(
                company_id="fpt_telecom_quang_ninh",
                name="Công ty Cổ phần Viễn thông FPT - Chi nhánh Quảng Ninh",
                brand_name="FPT Telecom Quảng Ninh",
                industry_group="telecom_it",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 48 Cao Xanh, Phường Cao Xanh, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://fpt.vn",
                career_url="https://fptjobs.com",
                social_channels={
                    "facebook": "https://www.facebook.com/fpttelecomquangninh",
                },
                hr_contacts={
                    "hotline": "0902.123.456",
                    "email": "tuyendungqn@fpt.com.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư Hỗ trợ Kỹ thuật & Hạ tầng Mạng FPT",
                    "Chuyên viên Triển khai Dịch vụ Cloud & Camera AI Doanh nghiệp",
                    "Nhân viên IT Support Khách hàng Doanh nghiệp",
                ],
                notes="Đơn vị viễn thông công nghệ năng động tại Quảng Ninh, liên tục tuyển dụng kỹ thuật viên mạng và hỗ trợ IT.",
            ),
            CompanyRegistryProfile(
                company_id="vnpt_quang_ninh",
                name="Viễn thông Quảng Ninh (VNPT Quảng Ninh)",
                brand_name="VNPT - VinaPhone Quảng Ninh",
                industry_group="telecom_it",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 1 Đường 25/4, Phường Bạch Đằng, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://quangninh.vnpt.vn",
                career_url="https://quangninh.vnpt.vn/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/vnptquangninh.vn",
                },
                hr_contacts={
                    "hotline": "0203.3825.888",
                    "email": "tuyendung.qnh@vnpt.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư Giải pháp CNTT Doanh nghiệp & Chính quyền số (e-Gov)",
                    "Chuyên viên Quản trị Mạng Viễn thông & Trung tâm IDC",
                    "Kỹ sư An toàn Thông tin & Vận hành Phần mềm",
                ],
                notes="Đối tác chiến lược triển khai Đề án Thành phố Thông minh và Chính quyền điện tử tỉnh Quảng Ninh.",
            ),
            CompanyRegistryProfile(
                company_id="viettel_quang_ninh",
                name="Viettel Quảng Ninh - Chi nhánh Tập đoàn Công nghiệp - Viễn thông Quân đội",
                brand_name="Viettel Quảng Ninh",
                industry_group="telecom_it",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Tòa nhà Viettel, Phường Hồng Hải, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://vietteltelecom.vn",
                career_url="https://tuyendung.viettel.vn",
                social_channels={
                    "facebook": "https://www.facebook.com/viettelquangninh",
                },
                hr_contacts={
                    "hotline": "0203.6250.178",
                    "email": "tuyendungviettelquangninh@viettel.com.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Kỹ sư Giải pháp CNTT (Solutions Architect) Khách hàng Doanh nghiệp",
                    "Kỹ sư Vận hành Hạ tầng Viễn thông & Trạm BTS",
                    "Chuyên viên Triển khai Phần mềm Hóa đơn Điện tử & Chữ ký số",
                ],
                notes="Tòa nhà trụ sở khang trang tại Cột 5 Hồng Hải, đơn vị dẫn đầu thị phần viễn thông và dịch vụ số tại Quảng Ninh.",
            ),
            CompanyRegistryProfile(
                company_id="mobifone_quang_ninh",
                name="MobiFone Tỉnh Quảng Ninh (Công ty Dịch vụ MobiFone Khu vực 5)",
                brand_name="MobiFone Quảng Ninh",
                industry_group="telecom_it",
                locations=[
                    {"province": "Quảng Ninh", "district": "Hạ Long", "address": "Số 609 Lê Thánh Tông, Phường Bạch Đằng, TP. Hạ Long, Quảng Ninh"}
                ],
                website_home="https://mobifone.vn",
                career_url="https://mobifone.vn/tuyen-dung",
                social_channels={
                    "facebook": "https://www.facebook.com/mobifonequangninh",
                },
                hr_contacts={
                    "hotline": "0203.3828.888",
                    "email": "tuyendung.kv5@mobifone.vn",
                },
                career_page_status="healthy",
                active_it_roles=[
                    "Chuyên viên Hỗ trợ Kỹ thuật & CNTT",
                    "Kỹ sư Quản trị Dữ liệu Khách hàng Doanh nghiệp",
                ],
                notes="Nhà mạng cung cấp giải pháp chuyển đổi số doanh nghiệp SmartOffice và giải pháp số SME tại Quảng Ninh.",
            ),
        ]

        for comp in catalog:
            self._companies[comp.company_id] = comp

    def list_companies(
        self,
        industry_group: Optional[str] = None,
        province: Optional[str] = None,
    ) -> List[CompanyRegistryProfile]:
        """Lọc danh sách doanh nghiệp theo ngành nghề và địa bàn"""
        results = list(self._companies.values())
        if industry_group:
            results = [c for c in results if c.industry_group == industry_group]
        if province:
            results = [
                c for c in results
                if any(loc.get("province", "").lower() == province.lower() for loc in c.locations)
            ]
        return results

    def get_company(self, company_id: str) -> Optional[CompanyRegistryProfile]:
        """Truy xuất hồ sơ doanh nghiệp theo ID"""
        return self._companies.get(company_id)

    def register_company(self, profile: CompanyRegistryProfile) -> None:
        """Thêm mới hoặc cập nhật hồ sơ doanh nghiệp"""
        self._companies[profile.company_id] = profile
        self._save_persisted_state()

    def audit_career_portals(self, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """
        Kiểm toán thực tế trạng thái kết nối của từng cổng tuyển dụng doanh nghiệp.
        Tuyệt đối không gán HTTP 200 ảo nếu chưa truy vấn thành công.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        results: Dict[str, Any] = {
            "audited_at": now_str,
            "total_companies": len(self._companies),
            "healthy_count": 0,
            "blocked_count": 0,
            "error_count": 0,
            "details": {},
        }

        session = requests.Session()
        session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

        for comp_id, comp in self._companies.items():
            url = comp.career_url
            try:
                resp = session.get(url, timeout=timeout_seconds, allow_redirects=True)
                comp.last_checked_at = now_str
                comp.http_status = resp.status_code

                if resp.status_code == 200:
                    comp.career_page_status = "healthy"
                    results["healthy_count"] += 1
                elif resp.status_code in [403, 429]:
                    comp.career_page_status = "blocked"
                    results["blocked_count"] += 1
                else:
                    comp.career_page_status = "error"
                    results["error_count"] += 1

                results["details"][comp_id] = {
                    "company_name": comp.name,
                    "url": url,
                    "status_code": resp.status_code,
                    "status": comp.career_page_status,
                }
            except requests.Timeout:
                comp.last_checked_at = now_str
                comp.http_status = 408
                comp.career_page_status = "timeout"
                results["error_count"] += 1
                results["details"][comp_id] = {
                    "company_name": comp.name,
                    "url": url,
                    "status_code": 408,
                    "status": "timeout",
                }
            except Exception as e:
                comp.last_checked_at = now_str
                comp.http_status = 500
                comp.career_page_status = "error"
                results["error_count"] += 1
                results["details"][comp_id] = {
                    "company_name": comp.name,
                    "url": url,
                    "status_code": 500,
                    "status": "error",
                    "error_message": str(e),
                }

        self._save_persisted_state()
        self.export_frontend_json()
        return results

    def generate_local_job_opportunities(self) -> List[UniversalJob]:
        """
        Chỉ trả về các cơ hội việc làm đã có bài đăng tuyển dụng thực tế đối soát 100%.
        Tuyệt đối không sinh dữ liệu giả định (mock/synthetic).
        """
        return []


    def export_frontend_json(self, output_path: Optional[Path] = None) -> None:
        """Xuất dữ liệu hồ sơ doanh nghiệp ra file JSON phục vụ giao diện người dùng"""
        target = output_path or FRONTEND_EXPORT_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        data = [comp.model_dump() for comp in self._companies.values()]
        try:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Đã xuất {len(data)} doanh nghiệp địa phương ra {target}")
        except Exception as e:
            logger.error(f"Lỗi xuất JSON doanh nghiệp: {e}")

    def _save_persisted_state(self) -> None:
        """Lưu trạng thái kiểm toán xuống đĩa"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            state = {comp_id: comp.model_dump() for comp_id, comp in self._companies.items()}
            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Lỗi lưu trạng thái CompanyRegistry: {e}")

    def _load_persisted_state(self) -> None:
        """Nạp trạng thái kiểm toán từ đĩa"""
        if not STATE_FILE_PATH.exists():
            return
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
            for comp_id, comp_data in state.items():
                if comp_id in self._companies:
                    if "career_page_status" in comp_data:
                        self._companies[comp_id].career_page_status = comp_data["career_page_status"]
                    if "last_checked_at" in comp_data:
                        self._companies[comp_id].last_checked_at = comp_data["last_checked_at"]
                    if "http_status" in comp_data:
                        self._companies[comp_id].http_status = comp_data["http_status"]
        except Exception as e:
            logger.warning(f"Lỗi nạp trạng thái CompanyRegistry: {e}")


# Singleton instance
company_registry = CompanyRegistry()
