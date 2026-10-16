import json
import requests
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total jobs: {len(jobs)}")
print("=" * 60)

for i in range(min(25, len(jobs))):
    j = jobs[i]
    title = j.get("title", "")
    comp = j.get("company_name", "")
    url = j.get("source_url", "")
    plat = j.get("source_platform", "")
    print(f"[{i+1}] {title[:35]} | {comp[:25]} | {plat} | {url}")
