from datetime import datetime, time, timezone
from typing import List
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.job import Job
from app.schemas.stats import (
    CategoryJobCount,
    DashboardStats,
    PlatformJobCount,
    ProvinceJobCount,
)


class StatsService:
    """
    Service thống kê dữ liệu thị trường việc làm Việt Nam
    """

    async def get_jobs_by_province(
        self,
        db: AsyncSession,
        limit: int = 20,
    ) -> List[ProvinceJobCount]:
        """
        Thống kê top tỉnh/thành phố có nhiều việc làm nhất
        """
        stmt = (
            select(Job.location_province, func.count(Job.id).label("job_count"))
            .where(Job.is_active.is_(True), Job.location_province.is_not(None))
            .group_by(Job.location_province)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [
            ProvinceJobCount(province=row[0], count=row[1])
            for row in res.all()
            if row[0]
        ]

    async def get_jobs_by_category(
        self,
        db: AsyncSession,
        limit: int = 20,
    ) -> List[CategoryJobCount]:
        """
        Thống kê top ngành nghề có nhu cầu tuyển dụng cao nhất
        """
        stmt = (
            select(Job.category, func.count(Job.id).label("job_count"))
            .where(Job.is_active.is_(True), Job.category.is_not(None))
            .group_by(Job.category)
            .order_by(func.count(Job.id).desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return [
            CategoryJobCount(category=row[0], count=row[1])
            for row in res.all()
            if row[0]
        ]

    async def get_jobs_by_platform(
        self,
        db: AsyncSession,
    ) -> List[PlatformJobCount]:
        """
        Thống kê số lượng việc làm phân bổ theo nền tảng nguồn cào
        """
        stmt = (
            select(Job.source_platform, func.count(Job.id).label("job_count"))
            .where(Job.is_active.is_(True), Job.source_platform.is_not(None))
            .group_by(Job.source_platform)
            .order_by(func.count(Job.id).desc())
        )
        res = await db.execute(stmt)
        return [
            PlatformJobCount(platform=row[0], count=row[1])
            for row in res.all()
            if row[0]
        ]

    async def get_dashboard_stats(
        self,
        db: AsyncSession,
    ) -> DashboardStats:
        """
        Tổng hợp toàn bộ chỉ số dashboard thống kê
        """
        # 1. Tổng số việc làm đang active
        total_jobs_res = await db.execute(
            select(func.count(Job.id)).where(Job.is_active.is_(True))
        )
        total_jobs = total_jobs_res.scalar_one_or_none() or 0

        # 2. Tổng số công ty
        total_companies_res = await db.execute(select(func.count(Company.id)))
        total_companies = total_companies_res.scalar_one_or_none() or 0

        # 3. Tổng số tỉnh thành có việc làm
        provinces_res = await db.execute(
            select(func.count(distinct(Job.location_province))).where(
                Job.is_active.is_(True),
                Job.location_province.is_not(None),
            )
        )
        total_provinces = provinces_res.scalar_one_or_none() or 0

        # 4. Việc làm mới thu thập hôm nay
        now = datetime.now(timezone.utc)
        today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        today_jobs_res = await db.execute(
            select(func.count(Job.id)).where(
                Job.is_active.is_(True),
                Job.crawled_at >= today_start,
            )
        )
        new_jobs_today = today_jobs_res.scalar_one_or_none() or 0

        # 5. Các thống kê chi tiết theo tỉnh, ngành và nền tảng
        jobs_by_prov = await self.get_jobs_by_province(db, limit=15)
        jobs_by_cat = await self.get_jobs_by_category(db, limit=15)
        jobs_by_plat = await self.get_jobs_by_platform(db)

        return DashboardStats(
            total_jobs=total_jobs,
            total_companies=total_companies,
            total_provinces_with_jobs=total_provinces,
            new_jobs_today=new_jobs_today,
            jobs_by_province=jobs_by_prov,
            jobs_by_category=jobs_by_cat,
            jobs_by_platform=jobs_by_plat,
        )


# Singleton instance
stats_service = StatsService()
