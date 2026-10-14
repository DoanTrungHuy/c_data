"""
Utility functions for C_Data web crawlers.
Includes text cleaning, salary parsing, location normalization, category detection, and experience level detection.
"""

import html
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

# ==============================================================================
# 1. 63 Standard Provinces and Centrally-Governed Cities of Vietnam
# ==============================================================================
ALL_63_PROVINCES: List[str] = [
    "An Giang",
    "Bà Rịa - Vũng Tàu",
    "Bắc Giang",
    "Bắc Kạn",
    "Bạc Liêu",
    "Bắc Ninh",
    "Bến Tre",
    "Bình Định",
    "Bình Dương",
    "Bình Phước",
    "Bình Thuận",
    "Cà Mau",
    "Cần Thơ",
    "Cao Bằng",
    "Đà Nẵng",
    "Đắk Lắk",
    "Đắk Nông",
    "Điện Biên",
    "Đồng Nai",
    "Đồng Tháp",
    "Gia Lai",
    "Hà Giang",
    "Hà Nam",
    "Hà Nội",
    "Hà Tĩnh",
    "Hải Dương",
    "Hải Phòng",
    "Hậu Giang",
    "Hòa Bình",
    "Hưng Yên",
    "Khánh Hòa",
    "Kiên Giang",
    "Kon Tum",
    "Lai Châu",
    "Lâm Đồng",
    "Lạng Sơn",
    "Lào Cai",
    "Long An",
    "Nam Định",
    "Nghệ An",
    "Ninh Bình",
    "Ninh Thuận",
    "Phú Thọ",
    "Phú Yên",
    "Quảng Bình",
    "Quảng Nam",
    "Quảng Ngãi",
    "Quảng Ninh",
    "Quảng Trị",
    "Sóc Trăng",
    "Sơn La",
    "Tây Ninh",
    "Thái Bình",
    "Thái Nguyên",
    "Thanh Hóa",
    "Thừa Thiên Huế",
    "Tiền Giang",
    "TP. Hồ Chí Minh",
    "Trà Vinh",
    "Tuyên Quang",
    "Vĩnh Long",
    "Vĩnh Phúc",
    "Yên Bái",
]

# ==============================================================================
# 2. Comprehensive Province Aliases and Variations
# ==============================================================================
PROVINCE_ALIASES: Dict[str, str] = {
    # Hà Nội
    "hn": "Hà Nội",
    "ha noi": "Hà Nội",
    "hanoi": "Hà Nội",
    "tp ha noi": "Hà Nội",
    "tp. ha noi": "Hà Nội",
    "thanh pho ha noi": "Hà Nội",
    "hà nội": "Hà Nội",
    "tp hà nội": "Hà Nội",
    "tp. hà nội": "Hà Nội",
    "thành phố hà nội": "Hà Nội",
    "ha noi city": "Hà Nội",

    # TP. Hồ Chí Minh
    "hcm": "TP. Hồ Chí Minh",
    "tphcm": "TP. Hồ Chí Minh",
    "tp hcm": "TP. Hồ Chí Minh",
    "tp.hcm": "TP. Hồ Chí Minh",
    "tp. hcm": "TP. Hồ Chí Minh",
    "sai gon": "TP. Hồ Chí Minh",
    "saigon": "TP. Hồ Chí Minh",
    "sài gòn": "TP. Hồ Chí Minh",
    "ho chi minh": "TP. Hồ Chí Minh",
    "tp ho chi minh": "TP. Hồ Chí Minh",
    "tp. ho chi minh": "TP. Hồ Chí Minh",
    "thanh pho ho chi minh": "TP. Hồ Chí Minh",
    "hồ chí minh": "TP. Hồ Chí Minh",
    "tp hồ chí minh": "TP. Hồ Chí Minh",
    "tp. hồ chí minh": "TP. Hồ Chí Minh",
    "thành phố hồ chí minh": "TP. Hồ Chí Minh",
    "hcmc": "TP. Hồ Chí Minh",
    "ho chi minh city": "TP. Hồ Chí Minh",

    # Đà Nẵng
    "dn": "Đà Nẵng",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
    "tp da nang": "Đà Nẵng",
    "tp. da nang": "Đà Nẵng",
    "đà nẵng": "Đà Nẵng",
    "tp đà nẵng": "Đà Nẵng",
    "tp. đà nẵng": "Đà Nẵng",
    "thành phố đà nẵng": "Đà Nẵng",

    # Hải Phòng
    "hp": "Hải Phòng",
    "hai phong": "Hải Phòng",
    "haiphong": "Hải Phòng",
    "tp hai phong": "Hải Phòng",
    "tp. hai phong": "Hải Phòng",
    "hải phòng": "Hải Phòng",
    "tp hải phòng": "Hải Phòng",
    "tp. hải phòng": "Hải Phòng",
    "thành phố hải phòng": "Hải Phòng",

    # Cần Thơ
    "ct": "Cần Thơ",
    "can tho": "Cần Thơ",
    "cantho": "Cần Thơ",
    "tp can tho": "Cần Thơ",
    "tp. can tho": "Cần Thơ",
    "cần thơ": "Cần Thơ",
    "tp cần thơ": "Cần Thơ",
    "tp. cần thơ": "Cần Thơ",
    "thành phố cần thơ": "Cần Thơ",

    # Quảng Ninh
    "qn": "Quảng Ninh",
    "quang ninh": "Quảng Ninh",
    "quangninh": "Quảng Ninh",
    "quảng ninh": "Quảng Ninh",
    "ha long": "Quảng Ninh",
    "hạ long": "Quảng Ninh",
    "cam pha": "Quảng Ninh",
    "cẩm phả": "Quảng Ninh",
    "uong bi": "Quảng Ninh",
    "uông bí": "Quảng Ninh",
    "mong cai": "Quảng Ninh",
    "móng cái": "Quảng Ninh",

    # Bình Dương
    "bd": "Bình Dương",
    "binh duong": "Bình Dương",
    "binhduong": "Bình Dương",
    "bình dương": "Bình Dương",
    "thu dau mot": "Bình Dương",
    "thủ dầu một": "Bình Dương",
    "di an": "Bình Dương",
    "dĩ an": "Bình Dương",
    "thuan an": "Bình Dương",
    "thuận an": "Bình Dương",
    "ben cat": "Bình Dương",
    "bến cát": "Bình Dương",
    "tan uyen": "Bình Dương",
    "tân uyên": "Bình Dương",

    # Đồng Nai
    "dong nai": "Đồng Nai",
    "dongnai": "Đồng Nai",
    "đồng nai": "Đồng Nai",
    "bien hoa": "Đồng Nai",
    "biên hòa": "Đồng Nai",
    "long thanh": "Đồng Nai",
    "long thành": "Đồng Nai",
    "nhon trach": "Đồng Nai",
    "nhơn trạch": "Đồng Nai",

    # Bắc Ninh
    "bn": "Bắc Ninh",
    "bac ninh": "Bắc Ninh",
    "bacninh": "Bắc Ninh",
    "bắc ninh": "Bắc Ninh",
    "tu son": "Bắc Ninh",
    "từ sơn": "Bắc Ninh",

    # Bà Rịa - Vũng Tàu
    "brvt": "Bà Rịa - Vũng Tàu",
    "br-vt": "Bà Rịa - Vũng Tàu",
    "ba ria vung tau": "Bà Rịa - Vũng Tàu",
    "ba ria - vung tau": "Bà Rịa - Vũng Tàu",
    "bà rịa vũng tàu": "Bà Rịa - Vũng Tàu",
    "bà rịa - vũng tàu": "Bà Rịa - Vũng Tàu",
    "vung tau": "Bà Rịa - Vũng Tàu",
    "vũng tàu": "Bà Rịa - Vũng Tàu",
    "vt": "Bà Rịa - Vũng Tàu",
    "ba ria": "Bà Rịa - Vũng Tàu",
    "bà rịa": "Bà Rịa - Vũng Tàu",

    # Các tỉnh miền Bắc
    "bac giang": "Bắc Giang",
    "bắc giang": "Bắc Giang",
    "bac kan": "Bắc Kạn",
    "bac can": "Bắc Kạn",
    "bắc kạn": "Bắc Kạn",
    "bắc cạn": "Bắc Kạn",
    "cao bang": "Cao Bằng",
    "cao bằng": "Cao Bằng",
    "dien bien": "Điện Biên",
    "điện biên": "Điện Biên",
    "ha giang": "Hà Giang",
    "hà giang": "Hà Giang",
    "ha nam": "Hà Nam",
    "hà nam": "Hà Nam",
    "hai duong": "Hải Dương",
    "hải dương": "Hải Dương",
    "hoa binh": "Hòa Bình",
    "hòa bình": "Hòa Bình",
    "hung yen": "Hưng Yên",
    "hưng yên": "Hưng Yên",
    "lai chau": "Lai Châu",
    "lai châu": "Lai Châu",
    "lang son": "Lạng Sơn",
    "lạng sơn": "Lạng Sơn",
    "lao cai": "Lào Cai",
    "lào cai": "Lào Cai",
    "sapa": "Lào Cai",
    "nam dinh": "Nam Định",
    "nam định": "Nam Định",
    "ninh binh": "Ninh Bình",
    "ninh bình": "Ninh Bình",
    "phu tho": "Phú Thọ",
    "phú thọ": "Phú Thọ",
    "viet tri": "Phú Thọ",
    "việt trì": "Phú Thọ",
    "son la": "Sơn La",
    "sơn la": "Sơn La",
    "thai binh": "Thái Bình",
    "thái bình": "Thái Bình",
    "thai nguyen": "Thái Nguyên",
    "thái nguyên": "Thái Nguyên",
    "tuyen quang": "Tuyên Quang",
    "tuyên quang": "Tuyên Quang",
    "vinh phuc": "Vĩnh Phúc",
    "vĩnh phúc": "Vĩnh Phúc",
    "yen bai": "Yên Bái",
    "yên bái": "Yên Bái",

    # Các tỉnh miền Trung & Tây Nguyên
    "thanh hoa": "Thanh Hóa",
    "thanh hóa": "Thanh Hóa",
    "nghe an": "Nghệ An",
    "nghệ an": "Nghệ An",
    "tp vinh": "Nghệ An",
    "vinh": "Nghệ An",
    "ha tinh": "Hà Tĩnh",
    "hà tĩnh": "Hà Tĩnh",
    "quang binh": "Quảng Bình",
    "quảng bình": "Quảng Bình",
    "dong hoi": "Quảng Bình",
    "đồng hới": "Quảng Bình",
    "quang tri": "Quảng Trị",
    "quảng trị": "Quảng Trị",
    "dong ha": "Quảng Trị",
    "đông hà": "Quảng Trị",
    "thua thien hue": "Thừa Thiên Huế",
    "thừa thiên huế": "Thừa Thiên Huế",
    "hue": "Thừa Thiên Huế",
    "huế": "Thừa Thiên Huế",
    "tth": "Thừa Thiên Huế",
    "quang nam": "Quảng Nam",
    "quảng nam": "Quảng Nam",
    "tam ky": "Quảng Nam",
    "tam kỳ": "Quảng Nam",
    "hoi an": "Quảng Nam",
    "hội an": "Quảng Nam",
    "quang ngai": "Quảng Ngãi",
    "quảng ngãi": "Quảng Ngãi",
    "binh dinh": "Bình Định",
    "bình định": "Bình Định",
    "quy nhon": "Bình Định",
    "quy nhơn": "Bình Định",
    "phu yen": "Phú Yên",
    "phú yên": "Phú Yên",
    "tuy hoa": "Phú Yên",
    "tuy hòa": "Phú Yên",
    "khanh hoa": "Khánh Hòa",
    "khánh hòa": "Khánh Hòa",
    "nha trang": "Khánh Hòa",
    "cam ranh": "Khánh Hòa",
    "ninh thuan": "Ninh Thuận",
    "ninh thuận": "Ninh Thuận",
    "phan rang": "Ninh Thuận",
    "binh thuan": "Bình Thuận",
    "bình thuận": "Bình Thuận",
    "phan thiet": "Bình Thuận",
    "phan thiết": "Bình Thuận",
    "kon tum": "Kon Tum",
    "kontum": "Kon Tum",
    "gia lai": "Gia Lai",
    "gialai": "Gia Lai",
    "pleiku": "Gia Lai",
    "dak lak": "Đắk Lắk",
    "daklak": "Đắk Lắk",
    "đắk lắk": "Đắk Lắk",
    "đắc lắc": "Đắk Lắk",
    "dac lac": "Đắk Lắk",
    "buon ma thuot": "Đắk Lắk",
    "buôn ma thuột": "Đắk Lắk",
    "bmt": "Đắk Lắk",
    "dak nong": "Đắk Nông",
    "daknong": "Đắk Nông",
    "đắk nông": "Đắk Nông",
    "đắc nông": "Đắk Nông",
    "dac nong": "Đắk Nông",
    "gia nghia": "Đắk Nông",
    "lam dong": "Lâm Đồng",
    "lamdong": "Lâm Đồng",
    "lâm đồng": "Lâm Đồng",
    "da lat": "Lâm Đồng",
    "đà lạt": "Lâm Đồng",
    "bao loc": "Lâm Đồng",
    "bảo lộc": "Lâm Đồng",

    # Các tỉnh miền Nam & Tây Nam Bộ
    "binh phuoc": "Bình Phước",
    "bình phước": "Bình Phước",
    "dong xoai": "Bình Phước",
    "đồng xoài": "Bình Phước",
    "tay ninh": "Tây Ninh",
    "tây ninh": "Tây Ninh",
    "long an": "Long An",
    "tan an": "Long An",
    "tân an": "Long An",
    "tien giang": "Tiền Giang",
    "tiền giang": "Tiền Giang",
    "my tho": "Tiền Giang",
    "mỹ tho": "Tiền Giang",
    "ben tre": "Bến Tre",
    "bến tre": "Bến Tre",
    "tra vinh": "Trà Vinh",
    "trà vinh": "Trà Vinh",
    "vinh long": "Vĩnh Long",
    "vĩnh long": "Vĩnh Long",
    "dong thap": "Đồng Tháp",
    "đồng tháp": "Đồng Tháp",
    "cao lanh": "Đồng Tháp",
    "cao lãnh": "Đồng Tháp",
    "sa dec": "Đồng Tháp",
    "sa đéc": "Đồng Tháp",
    "an giang": "An Giang",
    "long xuyen": "An Giang",
    "long xuyên": "An Giang",
    "chau doc": "An Giang",
    "châu đốc": "An Giang",
    "kien giang": "Kiên Giang",
    "kiên giang": "Kiên Giang",
    "rach gia": "Kiên Giang",
    "rạch giá": "Kiên Giang",
    "phu quoc": "Kiên Giang",
    "phú quốc": "Kiên Giang",
    "hau giang": "Hậu Giang",
    "hậu giang": "Hậu Giang",
    "vi thanh": "Hậu Giang",
    "vị thanh": "Hậu Giang",
    "soc trang": "Sóc Trăng",
    "sóc trăng": "Sóc Trăng",
    "bac lieu": "Bạc Liêu",
    "bạc liêu": "Bạc Liêu",
    "ca mau": "Cà Mau",
}

# Add standard province names as self-referencing entries
for _p in ALL_63_PROVINCES:
    PROVINCE_ALIASES[_p.lower()] = _p


# ==============================================================================
# 3. Text and HTML Cleaning
# ==============================================================================
def remove_accents(input_str: str) -> str:
    """
    Remove Vietnamese diacritics for insensitive search matching.
    """
    if not input_str:
        return ""
    # Normalize unicode decomposed form
    nfkd = unicodedata.normalize("NFKD", input_str)
    # Filter out non-spacing marks and handle special Vietnamese 'đ' / 'Đ'
    result = "".join(c for c in nfkd if not unicodedata.combining(c))
    return result.replace("đ", "d").replace("Đ", "D")


def clean_html(html_text: Optional[str]) -> str:
    """
    Clean HTML markup: remove script/style tags, strip HTML tags,
    decode HTML entities, normalize whitespace and line breaks.
    """
    if not html_text:
        return ""

    if not isinstance(html_text, str):
        html_text = str(html_text)

    # Remove script and style elements
    cleaned = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html_text, flags=re.DOTALL | re.IGNORECASE)
    # Replace <br>, <p>, <div>, <li> with newlines to preserve structure
    cleaned = re.sub(r"<(br|p|div|li)[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
    # Remove remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Unescape HTML entities (e.g. &nbsp;, &amp;)
    cleaned = html.unescape(cleaned)
    # Replace non-breaking spaces
    cleaned = cleaned.replace("\xa0", " ").replace("\u200b", "")

    # Normalize lines: strip trailing spaces on each line and remove excessive empty lines
    lines = [line.strip() for line in cleaned.splitlines()]
    result = []
    prev_blank = False
    for line in lines:
        if line:
            # Collapse multiple spaces within line
            line = re.sub(r"[ \t]+", " ", line)
            result.append(line)
            prev_blank = False
        elif not prev_blank:
            result.append("")
            prev_blank = True

    return "\n".join(result).strip()


# ==============================================================================
# 4. Province and Location Normalization
# ==============================================================================
def normalize_province(location_text: Optional[str]) -> Optional[str]:
    """
    Extract and normalize standard Vietnamese province name from location strings.
    Matches against all 63 provinces and common abbreviations/aliases.
    """
    if not location_text or not isinstance(location_text, str):
        return None

    raw_lower = location_text.lower().strip()
    unaccented = remove_accents(raw_lower)

    # 1. Exact match against alias keys
    if raw_lower in PROVINCE_ALIASES:
        return PROVINCE_ALIASES[raw_lower]
    if unaccented in PROVINCE_ALIASES:
        return PROVINCE_ALIASES[unaccented]

    # 2. Substring matching ordered by alias length descending
    # (To match e.g. "Bà Rịa - Vũng Tàu" before "Bà Rịa", "TP. Hồ Chí Minh" before "Hồ Chí Minh")
    sorted_aliases = sorted(PROVINCE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)

    # Match with word boundaries or punctuation separators
    for alias, standard_name in sorted_aliases:
        # Check if alias appears in raw_lower or unaccented text
        pattern = r"(?:^|[^\w\d])" + re.escape(alias) + r"(?:$|[^\w\d])"
        if re.search(pattern, raw_lower) or re.search(pattern, unaccented):
            return standard_name

    return None


def normalize_location(location_text: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Parse a Vietnamese location string into province, district, and clean full address.
    Returns:
        {
            "province": str | None,
            "district": str | None,
            "full": str
        }
    """
    if not location_text:
        return {"province": None, "district": None, "full": ""}

    cleaned_full = clean_html(location_text).strip()
    province = normalize_province(cleaned_full)

    # Extract district if present (e.g., "Quận Cầu Giấy", "Huyện Đông Anh", "Thị xã Đông Triều", "TP. Hạ Long")
    district = None
    district_match = re.search(
        r"(?:Quận|Huyện|Thị xã|TP\.|Thành phố)\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\-]+?)(?:,|-|\||\.|$)",
        cleaned_full,
        re.IGNORECASE,
    )
    if district_match:
        district_raw = district_match.group(0).strip(" ,.-|")
        # Filter out if it matched the province itself (e.g., "TP. Hà Nội")
        if not province or remove_accents(district_raw.lower()) != remove_accents(province.lower()):
            district = district_raw

    return {
        "province": province,
        "district": district,
        "full": cleaned_full,
    }


# ==============================================================================
# 5. Salary Range Parsing
# ==============================================================================
USD_TO_VND_RATE = 25400  # Default conversion rate for USD salaries


def _parse_numeric_value(val_str: str) -> Optional[float]:
    """
    Parse a numeric string which may use either comma or dot as thousand/decimal separator.
    Examples:
      '1,000' -> 1000.0
      '2.5' -> 2.5
      '2,5' -> 2.5
      '15.000.000' -> 15000000.0
    """
    if not val_str:
        return None
    cleaned_val = val_str.strip()
    # Remove thousand comma separators: e.g. 1,000 or 1,000,000
    if re.search(r"\d+,\d{3}", cleaned_val) and not re.search(r",\d{1,2}$", cleaned_val):
        cleaned_val = cleaned_val.replace(",", "")
    # Remove thousand dot separators: e.g. 15.000.000 or 1.000.000
    if re.search(r"\d+\.\d{3}", cleaned_val) and not re.search(r"\.\d{1,2}$", cleaned_val):
        cleaned_val = cleaned_val.replace(".", "")
    # Now replace remaining comma with dot for decimal: 2,5 -> 2.5
    cleaned_val = cleaned_val.replace(",", ".")
    try:
        return float(cleaned_val)
    except ValueError:
        return None


def extract_salary_range(text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse Vietnamese salary expressions into (salary_min, salary_max) in VND.

    Supported patterns:
      - '8 - 12 triệu', '8 - 12 tr', '8-12tr', '8-12 triệu/tháng' -> (8_000_000, 12_000_000)
      - 'Trên 15 triệu', '> 15 triệu', 'Từ 15 triệu', '15 triệu trở lên' -> (15_000_000, None)
      - 'Dưới 10 triệu', '< 10 triệu', 'Đến 10 triệu', 'Lên đến 20 triệu' -> (None, 10_000_000 / 20_000_000)
      - 'Thỏa thuận', 'Cạnh tranh', 'Thương lượng', 'Negotiable' -> (None, None)
      - '15.000.000 - 20.000.000 VNĐ' -> (15_000_000, 20_000_000)
      - '15.000.000 VNĐ', '15 triệu' -> (15_000_000, 15_000_000)
      - '$1,000 - $2,000', '1000 - 2000 USD' -> (25_400_000, 50_800_000)
      - '2.5 - 3.5 triệu' -> (2_500_000, 3_500_000)
    """
    if not text or not isinstance(text, str):
        return None, None

    cleaned = text.strip().lower()

    # Negotiable / Undefined
    negotiable_keywords = [
        "thỏa thuận",
        "thoa thuan",
        "thương lượng",
        "thuong luong",
        "cạnh tranh",
        "canh tranh",
        "negotiable",
        "competitive",
        "trao đổi",
        "phỏng vấn",
    ]
    if any(kw in cleaned for kw in negotiable_keywords):
        return None, None

    # Handle USD currencies
    is_usd = bool(re.search(r"(\$|usd|dollar)", cleaned, re.IGNORECASE))
    multiplier = USD_TO_VND_RATE if is_usd else 1

    # Check for unit "triệu" / "tr" / "million" / "m"
    is_trieu = bool(re.search(r"(triệu|trieu|\btr\b|\bm\b|million)", cleaned))
    if is_trieu and not is_usd:
        multiplier = 1_000_000

    # Remove currency symbol characters ($ and đ) to avoid breaking range boundaries
    num_text = re.sub(r"[\$₫đ]", " ", cleaned)

    # 1. Format: "15.000.000 - 20.000.000" or "15,000,000 - 20,000,000" (Full digit range >= 6 digits)
    full_digit_range = re.search(
        r"([\d\.\,]{6,})\s*(?:-|đến|to|~)\s*([\d\.\,]{6,})",
        num_text,
    )
    if full_digit_range:
        min_val = _parse_numeric_value(full_digit_range.group(1))
        max_val = _parse_numeric_value(full_digit_range.group(2))
        if min_val is not None and max_val is not None:
            return int(min_val), int(max_val)

    # 2. Number Range: "8 - 12 triệu", "8.5 - 12.5 tr", "$1,000 - $2,000", "1000 - 2000 USD"
    range_match = re.search(
        r"([\d\.\,]+)\s*(?:tr|triệu|k|m|usd)?\s*(?:-|đến|to|~)\s*([\d\.\,]+)",
        num_text,
    )
    if range_match:
        min_val = _parse_numeric_value(range_match.group(1))
        max_val = _parse_numeric_value(range_match.group(2))
        if min_val is not None and max_val is not None:
            return int(min_val * multiplier), int(max_val * multiplier)

    # Single full digit: "15.000.000 VNĐ"
    single_full_digit = re.search(r"([\d\.\,]{6,})", num_text)
    if single_full_digit and not is_trieu and not is_usd:
        val = _parse_numeric_value(single_full_digit.group(1))
        if val is not None:
            int_val = int(val)
            if any(term in cleaned for term in ["trên", ">", "từ"]):
                return int_val, None
            if any(term in cleaned for term in ["dưới", "<", "đến", "tới", "lên đến", "tối đa"]):
                return None, int_val
            return int_val, int_val

    # 3. Minimum only: "Trên 15 triệu", "Từ 15 triệu", "> 15 tr", "15 triệu trở lên"
    min_match = re.search(
        r"(?:trên|>|từ|ít nhất|tối thiểu|from)\s*([\d\.\,]+)",
        num_text,
    )
    if min_match:
        min_val = _parse_numeric_value(min_match.group(1))
        if min_val is not None:
            return int(min_val * multiplier), None

    if re.search(r"([\d\.\,]+)\s*(?:tr|triệu)?\s*(?:trở lên|\+)", num_text):
        m = re.search(r"([\d\.\,]+)", num_text)
        if m:
            min_val = _parse_numeric_value(m.group(1))
            if min_val is not None:
                return int(min_val * multiplier), None

    # 4. Maximum only: "Dưới 10 triệu", "< 10 tr", "Đến 10 triệu", "Lên tới 20 triệu", "Up to $1500"
    max_match = re.search(
        r"(?:dưới|<|đến|tới|lên đến|lên tới|tối đa|up to)\s*([\d\.\,]+)",
        num_text,
    )
    if max_match:
        max_val = _parse_numeric_value(max_match.group(1))
        if max_val is not None:
            return None, int(max_val * multiplier)

    # 5. Single number fallback e.g. "15 triệu", "$1500"
    single_match = re.search(r"([\d\.\,]+)", num_text)
    if single_match and (is_trieu or is_usd):
        val = _parse_numeric_value(single_match.group(1))
        if val is not None:
            int_val = int(val * multiplier)
            return int_val, int_val


    return None, None



# ==============================================================================
# 6. Job Category Detection
# ==============================================================================
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "IT / Phần mềm": [
        "developer",
        "lập trình",
        "backend",
        "frontend",
        "fullstack",
        "full-stack",
        "tester",
        "qa",
        "qc",
        "devops",
        "software",
        "react",
        "node",
        "python",
        "java",
        "php",
        ".net",
        "golang",
        "flutter",
        "ios",
        "android",
        "mobile",
        "data engineer",
        "data analyst",
        "ai",
        "machine learning",
        "it helpdesk",
        "system admin",
        "an ninh mạng",
        "cyber security",
        "cloud",
        "aws",
        "sql",
        "công nghệ thông tin",
    ],
    "Marketing / Truyền thông": [
        "marketing",
        "seo",
        "content",
        "copywriter",
        "digital marketing",
        "truyền thông",
        "media",
        "quảng cáo",
        "facebook ads",
        "google ads",
        "pr",
        "event",
        "sự kiện",
        "branding",
        "tiktok",
        "social media",
    ],
    "Bán hàng / Kinh doanh": [
        "sales",
        "kinh doanh",
        "nhân viên kinh doanh",
        "nvkd",
        "telesales",
        "tư vấn bán hàng",
        "bán hàng",
        "account executive",
        "phát triển thị trường",
        "showroom",
        "thương mại",
    ],
    "Kế toán / Kiểm toán / Tài chính": [
        "kế toán",
        "kiểm toán",
        "thu ngân",
        "auditing",
        "kế toán trưởng",
        "kế toán tổng hợp",
        "kế toán kho",
        "kế toán thuế",
        "thanh toán",
        "tài chính",
        "finance",
        "chứng khoán",
        "đầu tư",
    ],
    "Nhân sự / Hành chính": [
        "nhân sự",
        "hr",
        "tuyển dụng",
        "c&b",
        "hành chính",
        "văn thư",
        "lễ tân",
        "trợ lý",
        "thư ký",
        "tiền lương",
        "admin officer",
    ],
    "Chăm sóc khách hàng": [
        "cskh",
        "chăm sóc khách hàng",
        "customer service",
        "tổng đài",
        "call center",
        "hỗ trợ khách hàng",
        "trực chat",
        "tiếp đón",
    ],
    "Cơ khí / Ô tô / Tự động hóa": [
        "cơ khí",
        "tiện",
        "phay",
        "hàn",
        "bảo trì",
        "thợ cơ khí",
        "ô tô",
        "xe máy",
        "kỹ sư cơ khí",
        "tự động hóa",
        "plc",
        "cnc",
        "điện tử",
        "điện công nghiệp",
    ],
    "Xây dựng / Kiến trúc": [
        "xây dựng",
        "kiến trúc",
        "kỹ sư xây dựng",
        "chỉ huy trưởng",
        "giám sát công trình",
        "autocad",
        "thiết kế nội thất",
        "kết cấu",
        "dự toán",
        "công trình",
        "trắc địa",
    ],
    "Xuất nhập khẩu / Logistics": [
        "xuất nhập khẩu",
        "logistics",
        "kho vận",
        "giao nhận",
        "hải quan",
        "mua hàng",
        "procurement",
        "purchasing",
        "supply chain",
        "tài xế",
        "giao hàng",
        "shipper",
        "forwarder",
    ],
    "Giáo dục / Đào tạo": [
        "giáo viên",
        "giảng viên",
        "gia sư",
        "trợ giảng",
        "đào tạo",
        "teacher",
        "tutor",
        "tiếng anh",
        "mầm non",
        "giáo dục",
    ],
    "Y tế / Dược phẩm": [
        "bác sĩ",
        "dược sĩ",
        "điều dưỡng",
        "y tá",
        "nha khoa",
        "y tế",
        "trình dược viên",
        "phòng khám",
        "bệnh viện",
    ],
    "Khách sạn / Du lịch / Nhà hàng": [
        "đầu bếp",
        "phụ bếp",
        "pha chế",
        "barista",
        "bartender",
        "phục vụ",
        "waiter",
        "waitress",
        "tour guide",
        "hướng dẫn viên",
        "du lịch",
        "khách sạn",
        "resort",
        "nhà hàng",
    ],
    "Thiết kế / Sáng tạo": [
        "graphic designer",
        "thiết kế đồ họa",
        "photoshop",
        "illustrator",
        "ui/ux",
        "video editor",
        "dựng phim",
        "3d",
        "motion graphic",
        "họa viên",
    ],
    "Sản xuất / Vận hành": [
        "công nhân",
        "thợ may",
        "đóng gói",
        "tổ trưởng sản xuất",
        "quản đốc",
        "vận hành máy",
        "sản xuất",
        "dây chuyền",
    ],
    "Lao động phổ thông": [
        "lao động phổ thông",
        "bảo vệ",
        "tạp vụ",
        "bốc xếp",
        "vệ sinh",
        "giúp việc",
        "phụ kho",
    ],
    "Ngân hàng / Bảo hiểm": [
        "ngân hàng",
        "tín dụng",
        "thẩm định",
        "giao dịch viên",
        "bảo hiểm",
        "bancassurance",
    ],
}


def detect_job_category(title: str, description: str = "") -> str:
    """
    Detect standard job category based on keywords in title and description.
    Title has higher weight.
    """
    combined = f"{title} {title} {description}".lower()

    best_category = "Khác"
    max_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", combined))
        if score > max_score:
            max_score = score
            best_category = category

    return best_category


# ==============================================================================
# 7. Experience Level Detection
# ==============================================================================
def detect_experience_level(text: Optional[str]) -> str:
    """
    Extract standardized experience level from requirements or description text.
    """
    if not text:
        return "Không yêu cầu kinh nghiệm"

    lower = text.lower()

    if any(k in lower for k in ["không yêu cầu", "khong yeu cau", "không cần", "no experience", "fresher", "mới tốt nghiệp", "chưa có kinh nghiệm"]):
        return "Không yêu cầu kinh nghiệm"

    if any(k in lower for k in ["trưởng phòng", "giám đốc", "quản lý", "director", "manager", "head of", "lead"]):
        return "Quản lý / Trưởng phòng"

    # 1. Multi-year ranges (must check before single-year keywords)
    if any(k in lower for k in ["3 - 5 năm", "3-5 năm", "3 đến 5 năm", "3-5 years"]):
        return "3 - 5 năm"

    if any(k in lower for k in ["2 - 3 năm", "2-3 năm", "2 đến 3 năm", "2-3 years"]):
        return "2 - 3 năm"

    if any(k in lower for k in ["1 - 2 năm", "1-2 năm", "1 đến 2 năm", "1-2 years"]):
        return "1 - 2 năm"

    # 2. Single-year thresholds and single numbers
    if any(k in lower for k in ["trên 5 năm", "> 5 năm", "5 năm trở lên", "5+ năm", "từ 5 năm", "ít nhất 5 năm", "5 năm"]):
        return "Trên 5 năm"

    if any(k in lower for k in ["từ 4 năm", "4 năm", "từ 3 năm", "ít nhất 3 năm", "3 năm"]):
        return "3 - 5 năm"

    if any(k in lower for k in ["từ 2 năm", "ít nhất 2 năm", "2 năm"]):
        return "2 - 3 năm"

    if any(k in lower for k in ["từ 1 năm", "ít nhất 1 năm", "1 năm"]):
        return "1 - 2 năm"

    if any(k in lower for k in ["dưới 1 năm", "< 1 năm", "6 tháng", "dưới một năm"]):
        return "Dưới 1 năm"

    return "Không yêu cầu kinh nghiệm"



# ==============================================================================
# 8. Job Type Normalization
# ==============================================================================
def normalize_job_type(text: Optional[str]) -> str:
    """
    Normalize Vietnamese job type string into:
    full-time, part-time, remote, intern, contract, freelance.
    """
    if not text:
        return "full-time"

    lower = text.lower()

    if any(k in lower for k in ["thực tập", "intern", "internship", "học việc"]):
        return "intern"
    if any(k in lower for k in ["từ xa", "remote", "làm việc tại nhà", "work from home", "wfh"]):
        return "remote"
    if any(k in lower for k in ["bán thời gian", "part-time", "part time", "theo ca"]):
        return "part-time"
    if any(k in lower for k in ["hợp đồng", "thời vụ", "ngắn hạn", "contract"]):
        return "contract"
    if any(k in lower for k in ["tự do", "freelance", "cộng tác viên", "ctv"]):
        return "freelance"

    return "full-time"
