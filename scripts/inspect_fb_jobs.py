import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
jobs = json.load(open("frontend/public/data/jobs.json", encoding="utf-8"))
fb_jobs = [j for j in jobs if j.get("source_platform") == "Facebook"]
print(f"Total Facebook jobs: {len(fb_jobs)}")
for i, j in enumerate(fb_jobs):
    print(f"{i+1}. {j.get('id')} | {j.get('title')[:35]} | {j.get('company_name')} | {j.get('source_url')}")
