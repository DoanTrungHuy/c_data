import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

print(f"Total jobs: {len(jobs)}")

for j in jobs:
    prov = str(j.get('location_province') or '')
    dist = str(j.get('location_district') or '')
    full = str(j.get('location_full') or '')
    title = str(j.get('title') or '')
    comp = str(j.get('company_name') or '')
    desc = str(j.get('description') or '')
    req = str(j.get('requirements') or '')

    # Check for any mention of Hanoi or other provinces in Quang Ninh jobs
    if 'Quảng Ninh' in prov or 'Hạ Long' in dist or 'Hạ Long' in full:
        if 'Hà Nội' in full or 'Hà Nội' in dist or 'Hà Nội' in comp or 'Hà Nội' in desc[:200]:
            print("---")
            print(f"ID: {j['id']}")
            print(f"Title: {title}")
            print(f"Company: {comp}")
            print(f"Province: {prov}")
            print(f"District: {dist}")
            print(f"Full: {full}")
            print(f"Desc snippet: {desc[:150]}")
