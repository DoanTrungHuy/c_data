import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

provinces_of_vietnam = [
    "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Quảng Ninh", "Bắc Ninh",
    "Bình Dương", "Đồng Nai", "Khánh Hòa", "Huế", "Thanh Hóa", "Nghệ An", "Bà Rịa - Vũng Tàu",
    "Hưng Yên", "Hải Dương", "Hà Nam", "Nam Định", "Thái Bình", "Vĩnh Phúc", "Bắc Giang",
    "Phú Thọ", "Thái Nguyên", "Lào Cai", "Yên Bái", "Tuyên Quang", "Lạng Sơn", "Cao Bằng",
    "Bắc Kạn", "Hà Giang", "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình", "Ninh Bình",
    "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên",
    "Ninh Thuận", "Bình Thuận", "Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng",
    "Bình Phước", "Tây Ninh", "Long An", "Tiền Giang", "Bến Tre", "Trà Vinh", "Vĩnh Long",
    "Đồng Tháp", "An Giang", "Kiên Giang", "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau"
]

print(f"Auditing {len(jobs)} jobs...")

issues = []

for j in jobs:
    prov = (j.get('location_province') or '').strip()
    full = (j.get('location_full') or '').strip()
    dist = (j.get('location_district') or '').strip()
    comp = (j.get('company_name') or '').strip()
    title = (j.get('title') or '').strip()
    desc = (j.get('description') or '').strip()

    # If prov is Quang Ninh, but full does NOT contain Quang Ninh or any QN town
    qn_tokens = ['quảng ninh', 'hạ long', 'cẩm phả', 'uông bí', 'móng cái', 'đông triều', 'quảng yên', 'vân đồn', 'cô tô', 'tiên yên', 'ba chẽ', 'bình liêu', 'đầm hà', 'hải hà', 'bãi cháy', 'hòn gai', 'cái lân', 'giếng đáy', 'hà khẩu']
    
    is_prov_qn = 'quảng ninh' in prov.lower()
    has_qn_in_full = any(t in full.lower() for t in qn_tokens)
    has_qn_in_dist = any(t in dist.lower() for t in qn_tokens)
    has_qn_in_title = any(t in title.lower() for t in qn_tokens)

    if is_prov_qn and not (has_qn_in_full or has_qn_in_dist or has_qn_in_title):
        issues.append({
            "id": j['id'],
            "type": "MARKED_AS_QN_BUT_NOT_QN",
            "title": title,
            "comp": comp,
            "prov": prov,
            "dist": dist,
            "full": full
        })
    elif is_prov_qn and ('hà nội' in full.lower() or 'hà nội' in comp.lower()):
        issues.append({
            "id": j['id'],
            "type": "QN_MIXED_WITH_HANOI",
            "title": title,
            "comp": comp,
            "prov": prov,
            "dist": dist,
            "full": full
        })

print(f"Total issues found: {len(issues)}")
for issue in issues:
    print(issue)
