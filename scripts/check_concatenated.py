import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

print(f"Total jobs: {len(jobs)}")

for j in jobs:
    full = j.get('location_full') or ''
    prov = j.get('location_province') or ''
    title = j.get('title') or ''
    comp = j.get('company_name') or ''
    
    # Check concatenated locations
    patterns = ['Hà NộiHồ Chí Minh', 'Hà NộiKhánh Hòa', 'Hà NộiQuảng Ninh', 'Quảng NinhHà Nội', 'Đà NẵngHà Nội', 'Hà NộiHưng Yên']
    if any(p in full for p in patterns):
        print(f"Concatenated full location: [{j['id']}] {title} | Prov: {prov} | Full: '{full}'")
