export interface ProvinceOption {
  name: string;
  code: string;
  popular?: boolean;
}

export const VIETNAM_PROVINCES: ProvinceOption[] = [
  // Popular first
  { name: "Hà Nội", code: "HN", popular: true },
  { name: "Hồ Chí Minh", code: "HCM", popular: true },
  { name: "Đà Nẵng", code: "DN", popular: true },
  { name: "Quảng Ninh", code: "QN", popular: true },
  { name: "Hải Phòng", code: "HP", popular: true },
  { name: "Bình Dương", code: "BD", popular: true },
  { name: "Đồng Nai", code: "DNI", popular: true },
  { name: "Cần Thơ", code: "CT", popular: true },
  { name: "Bắc Ninh", code: "BN", popular: true },

  // Remaining provinces alphabetical
  { name: "An Giang", code: "AG" },
  { name: "Bà Rịa - Vũng Tàu", code: "BRVT" },
  { name: "Bắc Giang", code: "BG" },
  { name: "Bắc Kạn", code: "BK" },
  { name: "Bạc Liêu", code: "BL" },
  { name: "Bến Tre", code: "BT" },
  { name: "Bình Định", code: "BDI" },
  { name: "Bình Phước", code: "BP" },
  { name: "Bình Thuận", code: "BTH" },
  { name: "Cà Mau", code: "CM" },
  { name: "Cao Bằng", code: "CB" },
  { name: "Đắk Lắk", code: "DL" },
  { name: "Đắk Nông", code: "DKN" },
  { name: "Điện Biên", code: "DB" },
  { name: "Đồng Tháp", code: "DT" },
  { name: "Gia Lai", code: "GL" },
  { name: "Hà Giang", code: "HG" },
  { name: "Hà Nam", code: "HNA" },
  { name: "Hà Tĩnh", code: "HT" },
  { name: "Hải Dương", code: "HD" },
  { name: "Hậu Giang", code: "HGI" },
  { name: "Hòa Bình", code: "HB" },
  { name: "Hưng Yên", code: "HY" },
  { name: "Khánh Hòa", code: "KH" },
  { name: "Kiên Giang", code: "KG" },
  { name: "Kon Tum", code: "KT" },
  { name: "Lai Châu", code: "LC" },
  { name: "Lâm Đồng", code: "LD" },
  { name: "Lạng Sơn", code: "LS" },
  { name: "Lào Cai", code: "LCA" },
  { name: "Long An", code: "LA" },
  { name: "Nam Định", code: "ND" },
  { name: "Nghệ An", code: "NA" },
  { name: "Ninh Bình", code: "NB" },
  { name: "Ninh Thuận", code: "NT" },
  { name: "Phú Thọ", code: "PT" },
  { name: "Phú Yên", code: "PY" },
  { name: "Quảng Bình", code: "QB" },
  { name: "Quảng Nam", code: "QNA" },
  { name: "Quảng Ngãi", code: "QNG" },
  { name: "Quảng Trị", code: "QT" },
  { name: "Sóc Trăng", code: "ST" },
  { name: "Sơn La", code: "SL" },
  { name: "Tây Ninh", code: "TN" },
  { name: "Thái Bình", code: "TB" },
  { name: "Thái Nguyên", code: "TNG" },
  { name: "Thanh Hóa", code: "TH" },
  { name: "Thừa Thiên Huế", code: "TTH" },
  { name: "Tiền Giang", code: "TG" },
  { name: "Trà Vinh", code: "TV" },
  { name: "Tuyên Quang", code: "TQ" },
  { name: "Vĩnh Long", code: "VL" },
  { name: "Vĩnh Phúc", code: "VP" },
  { name: "Yên Bái", code: "YB" },
];

export interface CategoryOption {
  name: string;
  iconName: string;
  countLabel?: string;
  slug: string;
}

export const POPULAR_CATEGORIES: CategoryOption[] = [
  { name: "Công nghệ thông tin / Phần mềm", iconName: "CodeBracketIcon", slug: "it-phan-mem", countLabel: "1,200+ việc" },
  { name: "Kinh doanh / Bán hàng", iconName: "BriefcaseIcon", slug: "kinh-doanh-ban-hang", countLabel: "2,500+ việc" },
  { name: "Marketing / Truyền thông / PR", iconName: "MegaphoneIcon", slug: "marketing-truyen-thong", countLabel: "980+ việc" },
  { name: "Kế toán / Kiểm toán / Thuế", iconName: "CalculatorIcon", slug: "ke-toan-kiem-toan", countLabel: "850+ việc" },
  { name: "Hành chính / Nhân sự", iconName: "UserGroupIcon", slug: "hanh-chinh-nhan-su", countLabel: "640+ việc" },
  { name: "Sản xuất / Kỹ thuật công nghiệp", iconName: "WrenchScrewdriverIcon", slug: "ky-thuat-san-xuat", countLabel: "1,100+ việc" },
  { name: "Chăm sóc khách hàng / Telesales", iconName: "PhoneIcon", slug: "cham-soc-khach-hang", countLabel: "720+ việc" },
  { name: "Du lịch / Khách sạn / Nhà hàng", iconName: "GlobeAltIcon", slug: "du-lich-khach-san", countLabel: "530+ việc" },
];

export const JOB_TYPES = [
  { value: "Toàn thời gian", label: "Toàn thời gian" },
  { value: "Bán thời gian", label: "Bán thời gian" },
  { value: "Làm việc từ xa", label: "Từ xa / Remote" },
  { value: "Thực tập", label: "Thực tập sinh" },
  { value: "Hợp đồng / Dự án", label: "Hợp đồng / Dự án" },
];

export const SALARY_RANGES = [
  { label: "Tất cả mức lương", min: undefined, max: undefined },
  { label: "Dưới 10 triệu", min: undefined, max: 10000000 },
  { label: "10 - 15 triệu", min: 10000000, max: 15000000 },
  { label: "15 - 25 triệu", min: 15000000, max: 25000000 },
  { label: "25 - 50 triệu", min: 25000000, max: 50000000 },
  { label: "Trên 50 triệu", min: 50000000, max: undefined },
];

export const SOURCE_PLATFORMS = [
  { id: "Facebook", name: "Facebook (Group & Fanpage)" },
  { id: "Threads", name: "Threads (Meta)" },
  { id: "TikTok", name: "TikTok Jobs" },
  { id: "CareerViet", name: "CareerViet" },
  { id: "TopCV", name: "TopCV" },
  { id: "VietnamWorks", name: "VietnamWorks" },
  { id: "ITviec", name: "ITviec" },
  { id: "Doanh Nghiệp", name: "Website Doanh Nghiệp" },
];
