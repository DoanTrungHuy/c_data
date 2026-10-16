import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

it_jobs = []
for j in jobs:
    title = j.get("title", "")
    cat = j.get("category", "")
    desc = j.get("description", "")
    if any(k in title.lower() for k in ["it", "phần mềm", "lập trình", "kỹ sư cntt", "hệ thống", "mạng", "developer", "tester", "viễn thông"]):
        it_jobs.append(j)

print(f"Tổng số việc làm: {len(jobs)}")
print(f"Số việc làm thuộc lĩnh vực IT / CNTT / Phần mềm / Viễn thông: {len(it_jobs)}")
print("=" * 60)
for idx, j in enumerate(it_jobs):
    print(f"[{idx+1}] {j.get('title')} | {j.get('company_name')} | {j.get('source_url')}")
