import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "data", "jobs.json"))
with open(json_path, "r", encoding="utf-8") as f:
    jobs = json.load(f)

print(f"Total jobs: {len(jobs)}")

jid_jobs = []
other_jobs = []

for idx, j in enumerate(jobs):
    url = j.get("source_url", "")
    proof_url = j.get("evidence_proof", {}).get("direct_url", "")
    title = j.get("title", "")
    company = j.get("company_name", "")
    
    if "?jid=" in url or "?jid=" in proof_url:
        jid_jobs.append((idx, j["id"], title, company, url))
    else:
        other_jobs.append((idx, j["id"], title, company, url))

print(f"\n--- Jobs with ?jid= ({len(jid_jobs)}) ---")
for idx, jid, title, comp, url in jid_jobs:
    print(f"#{idx+1} [{jid}] {title} | {comp}\n   -> {url}")

print(f"\n--- Total other jobs: {len(other_jobs)} ---")
# Count domains
domains = {}
for idx, jid, title, comp, url in other_jobs:
    domain = url.split("/")[2] if "://" in url else "unknown"
    domains[domain] = domains.get(domain, 0) + 1

for d, count in domains.items():
    print(f"Domain: {d} -> {count} jobs")
