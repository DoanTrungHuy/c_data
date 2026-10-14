import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from app.schemas.job import JobSearchParams
from app.services.job_service import JobService

async def test_search():
    job_service = JobService()
    async with AsyncSessionLocal() as session:
        for query in ["IT", "Lập trình viên Frontend React", "Giao dịch viên", "Lái xe"]:
            print(f"\n=======================================================")
            print(f"TESTING QUERY: '{query}'")
            print(f"=======================================================")
            params = JobSearchParams(q=query, page=1, page_size=20)
            jobs, total, pages, suggestions, matched_ind = await job_service.get_jobs(session, params)
            print(f"Total found: {total} (Page 1 has {len(jobs)} jobs)")
            print(f"Matched Industries: {matched_ind}")
            print(f"Suggestions: {suggestions[:3]}")
            print("Jobs returned:")
            for idx, j in enumerate(jobs, 1):
                print(f"  {idx}. [{j.category}] {j.title} ({j.company_name})")
                assert "giao dịch viên" not in j.title.lower() if query == "IT" else True

if __name__ == "__main__":
    asyncio.run(test_search())
