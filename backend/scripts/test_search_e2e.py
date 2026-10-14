import asyncio
from app.core.database import AsyncSessionLocal
from app.services.job_service import job_service
from app.schemas.job import JobSearchParams

async def main():
    queries = [
        "IT Support ở Hạ Long",
        "kế toán",
        "lái xe",
        "spa",
        "than",
        "bác sĩ",
        "Junior backend Java ở Quảng Ninh, mới đăng trong 7 ngày"
    ]
    async with AsyncSessionLocal() as session:
        for q in queries:
            params = JobSearchParams(q=q, page=1, page_size=5)
            jobs, total, pages, kw, ind, diag = await job_service.get_jobs(session, params)
            print("=========================================")
            print(f"QUERY: [{q}] => Total Found: {total}")
            intent = diag.get("parsed_intent", {})
            print(f"Role: {intent.get('primary_role')} | Prov: {intent.get('target_province')} | Dist: {intent.get('target_district')}")
            for j in jobs[:2]:
                score = getattr(j, "match_score", None)
                print(f"  * {j.title} | {j.company_name} | Score: {score}")
                reasons = getattr(j, "match_reasons", [])
                if reasons:
                    print(f"    Reasons: {reasons[:2]}")

if __name__ == "__main__":
    asyncio.run(main())
