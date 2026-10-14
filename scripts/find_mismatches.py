import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

for j in jobs:
    prov = j.get('location_province')
    full = j.get('location_full')
    dist = j.get('location_district')
    title = j.get('title')
    comp = j.get('company_name')

    # check if prov is Quang Ninh but full does not contain Quang Ninh or Ha Long
    if prov == 'Quảng Ninh':
        if full and ('Quảng Ninh' not in full and 'Hạ Long' not in full and 'Cẩm Phả' not in full and 'Uông Bí' not in full and 'Vân Đồn' not in full and 'Móng Cái' not in full):
            print(f"Mismatch: [{j['id']}] {title} | Prov: {prov} | Full: {full}")
