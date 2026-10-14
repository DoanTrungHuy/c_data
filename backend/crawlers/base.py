"""
Base crawler class for C_Data job aggregation platform.
Provides shared utilities for HTTP requests, rate limiting, user-agent rotation,
data normalization, and database upsert operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from crawlers.utils import (
    clean_html,
    detect_experience_level,
    detect_job_category,
    extract_salary_range,
    normalize_job_type,
    normalize_province,
)

# Realistic desktop User-Agent strings for rotation
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    # Firefox on Windows & macOS
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
]


class BaseCrawler(ABC):
    """
    Abstract Base Class for all job crawlers in C_Data.
    """

    platform_name: str = "base"
    base_url: str = ""
    delay_seconds: float = 2.0

    def __init__(self, db_session=None):
        self.logger = logging.getLogger(f"crawler.{self.platform_name}")
        self.db_session = db_session
        self.session = self._init_http_session()

    def _init_http_session(self) -> requests.Session:
        """
        Configure requests session with connection pooling and automated retry policy.
        """
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_random_user_agent(self) -> str:
        """Return a randomized realistic browser User-Agent."""
        return random.choice(USER_AGENTS)

    def _get_default_headers(self) -> Dict[str, str]:
        """Generate baseline browser HTTP headers."""
        return {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        }

    def _make_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        timeout: int = 25,
        **kwargs,
    ) -> Optional[requests.Response]:
        """
        Execute an HTTP request with retry logic, rate limit pause, and rotating headers.
        """
        # Respect rate limits
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds + random.uniform(0.1, 0.5))

        req_headers = self._get_default_headers()
        if headers:
            req_headers.update(headers)

        try:
            self.logger.debug(f"Requesting [{method}] {url}")
            response = self.session.request(
                method=method,
                url=url,
                headers=req_headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
                **kwargs,
            )

            if response.status_code >= 400:
                self.logger.warning(
                    f"HTTP {response.status_code} for URL: {url}"
                )
                return response

            return response
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout connecting to {url}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error requesting {url}: {e}")
            return None

    def parse_salary(self, salary_text: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse raw Vietnamese salary text into (salary_min, salary_max) in VND.
        """
        return extract_salary_range(salary_text)

    def normalize_province(self, location_text: Optional[str]) -> Optional[str]:
        """
        Normalize raw location text into one of the 63 standard Vietnamese provinces.
        """
        return normalize_province(location_text)

    def normalize_job_type(self, text: Optional[str]) -> str:
        """
        Normalize job type string into full-time, part-time, remote, intern, contract, freelance.
        """
        return normalize_job_type(text)

    def detect_category(self, title: str, description: str = "") -> str:
        """
        Categorize job based on title and description.
        """
        return detect_job_category(title, description)

    def detect_experience(self, text: Optional[str]) -> str:
        """
        Detect standardized experience level.
        """
        return detect_experience_level(text)

    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean HTML and excessive whitespace.
        """
        return clean_html(text)

    @abstractmethod
    def crawl(self, max_pages: int = 50) -> List[Dict[str, Any]]:
        """
        Crawl job postings from the platform.
        Returns a list of raw job dictionaries.
        """
        pass

    def _get_or_create_session(self):
        """
        Retrieve existing DB session or create a new synchronous session using SyncSessionLocal.
        """
        if self.db_session:
            return self.db_session, False

        try:
            from app.core.database import SyncSessionLocal
            return SyncSessionLocal(), True
        except ImportError:
            # Fallback direct creation from DATABASE_URL_SYNC
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            db_url = os.getenv(
                "DATABASE_URL_SYNC",
                "sqlite:///./cdata.db",
            )
            engine = create_engine(db_url)
            SessionLocal = sessionmaker(bind=engine)
            return SessionLocal(), True

    def save_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Upsert a list of job dicts into the database.
        Uses source_url for deduplication.
        Returns count of newly inserted jobs.
        """
        if not jobs:
            self.logger.info("No jobs to save.")
            return 0

        try:
            from app.models.job import Job
        except ImportError:
            self.logger.error("Could not import Job model from app.models.job.")
            return 0

        session, should_close = self._get_or_create_session()
        new_jobs_count = 0
        updated_jobs_count = 0

        try:
            for job_data in jobs:
                source_url = job_data.get("source_url")
                if not source_url:
                    continue

                # Query existing job by source_url
                existing_job = session.query(Job).filter(Job.source_url == source_url).first()

                title = job_data.get("title", "").strip()
                if not title:
                    continue

                company_name = job_data.get("company_name")
                description = job_data.get("description")
                requirements = job_data.get("requirements")
                salary_min = job_data.get("salary_min")
                salary_max = job_data.get("salary_max")
                salary_text = job_data.get("salary_text")
                location_province = job_data.get("location_province")
                location_district = job_data.get("location_district")
                location_full = job_data.get("location_full")
                job_type = job_data.get("job_type", "full-time")
                category = job_data.get("category", "Khác")
                experience_level = job_data.get("experience_level")
                source_platform = job_data.get("source_platform", self.platform_name)
                posted_at = job_data.get("posted_at")
                expires_at = job_data.get("expires_at")
                raw_data = job_data.get("raw_data") or {}

                now_utc = datetime.now(timezone.utc)

                if existing_job:
                    # Update fields
                    existing_job.title = title
                    if company_name:
                        existing_job.company_name = company_name
                    if description:
                        existing_job.description = description
                    if requirements:
                        existing_job.requirements = requirements
                    if salary_min is not None:
                        existing_job.salary_min = salary_min
                    if salary_max is not None:
                        existing_job.salary_max = salary_max
                    if salary_text:
                        existing_job.salary_text = salary_text
                    if location_province:
                        existing_job.location_province = location_province
                    if location_district:
                        existing_job.location_district = location_district
                    if location_full:
                        existing_job.location_full = location_full
                    if job_type:
                        existing_job.job_type = job_type
                    if category:
                        existing_job.category = category
                    if experience_level:
                        existing_job.experience_level = experience_level
                    if expires_at:
                        existing_job.expires_at = expires_at
                    existing_job.crawled_at = now_utc
                    existing_job.is_active = True
                    if raw_data:
                        existing_job.raw_data = raw_data

                    updated_jobs_count += 1
                else:
                    # Insert new job
                    new_job = Job(
                        id=str(uuid.uuid4()),
                        title=title,
                        company_name=company_name,
                        description=description,
                        requirements=requirements,
                        salary_min=salary_min,
                        salary_max=salary_max,
                        salary_text=salary_text,
                        location_province=location_province,
                        location_district=location_district,
                        location_full=location_full,
                        job_type=job_type,
                        category=category,
                        experience_level=experience_level,
                        source_platform=source_platform,
                        source_url=source_url,
                        posted_at=posted_at,
                        expires_at=expires_at,
                        crawled_at=now_utc,
                        is_active=True,
                        raw_data=raw_data,
                    )
                    session.add(new_job)
                    new_jobs_count += 1

            session.commit()
            self.logger.info(
                f"[{self.platform_name}] Successfully saved jobs: "
                f"{new_jobs_count} new, {updated_jobs_count} updated."
            )
            return new_jobs_count

        except Exception as e:
            session.rollback()
            self.logger.error(f"[{self.platform_name}] Database save failed: {e}", exc_info=True)
            return 0
        finally:
            if should_close:
                session.close()
