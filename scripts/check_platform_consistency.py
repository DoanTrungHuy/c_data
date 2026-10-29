import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total jobs: {len(jobs)}")

fb_platform_jobs = [j for j in jobs if j.get("source_platform") == "Facebook"]
print(f"Jobs with source_platform == 'Facebook': {len(fb_platform_jobs)}")

for j in fb_platform_jobs:
    print(f"- [{j['id']}] {j.get('title')} | Company: {j.get('company_name')}")
    print(f"  Platform: {j.get('source_platform')} | Source URL: {j.get('source_url')}")
    print(f"  Fanpage: {j.get('fanpage_url')}")
