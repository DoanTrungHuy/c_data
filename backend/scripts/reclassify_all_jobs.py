import os
import sqlite3
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.smart_search_engine import smart_search_engine

db_path = os.path.join(backend_dir, "cdata.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, title, description, requirements, salary_text, category FROM jobs")
jobs = c.fetchall()

print(f"Total jobs to re-examine: {len(jobs)}")

updated_count = 0
for j in jobs:
    jid, title, desc, req, sal, old_cat = j
    mined = smart_search_engine.deep_mine_job_post(
        title=title,
        description=desc,
        requirements=req,
        salary_text=sal,
    )
    new_cat = mined.get("inferred_industry") or old_cat
    if new_cat and new_cat != old_cat:
        print(f"Updating job '{title[:40]}':")
        print(f"  Old: {old_cat}")
        print(f"  New: {new_cat}")
        c.execute("UPDATE jobs SET category = ? WHERE id = ?", (new_cat, jid))
        updated_count += 1

conn.commit()
print(f"\nSuccessfully re-classified {updated_count} jobs.")

# Print all IT jobs now
c.execute("SELECT id, title, category, company_name FROM jobs WHERE category LIKE '%Công nghệ thông tin%'")
it_jobs = c.fetchall()
print(f"\nJobs currently categorized as IT ({len(it_jobs)} total):")
for it in it_jobs:
    print(f"  - [{it[1]}] | {it[3]}")

# Print Banking jobs
c.execute("SELECT id, title, category, company_name FROM jobs WHERE category LIKE '%Ngân hàng%'")
bank_jobs = c.fetchall()
print(f"\nJobs categorized as Banking/Finance ({len(bank_jobs)} total):")
for bk in bank_jobs:
    print(f"  - [{bk[1]}] | {bk[3]}")

conn.close()
