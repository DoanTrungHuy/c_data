import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

fb_jobs = [j for j in jobs if "facebook.com" in j.get("source_url", "")]
print(f"Total jobs: {len(jobs)}")
print(f"Total Facebook jobs: {len(fb_jobs)}")

for j in fb_jobs:
    print(f"- ID: {j['id']}")
    print(f"  Title: {j.get('title')}")
    print(f"  Company: {j.get('company_name')}")
    print(f"  Source URL: {j.get('source_url')}")
    print(f"  External Link: {j.get('external_link')}")
    print("---")
