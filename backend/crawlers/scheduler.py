"""
Scheduler and execution manager for C_Data web crawlers.
Coordinates running all crawlers or single platform crawler,
persists execution metrics and statuses to local JSON file and Redis.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("crawlers.scheduler")

# Local status file path
STATUS_FILE_PATH = Path(
    os.getenv("CRAWLER_STATUS_FILE", Path(__file__).parent / "crawler_status.json")
)


def _get_redis_client():
    """
    Attempt to connect to Redis using REDIS_URL environment variable.
    Returns None if Redis is not installed or unreachable.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis
        client = redis.Redis.from_url(redis_url, decode_responses=True, socket_timeout=3)
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"Redis not available for status caching: {e}")
        return None


def get_crawler_status() -> Dict[str, Any]:
    """
    Retrieve current or last execution status and metrics for all crawlers.
    Checks Redis first, then falls back to local JSON status file.
    """
    # 1. Try Redis
    redis_client = _get_redis_client()
    if redis_client:
        try:
            cached = redis_client.get("cdata:crawlers:status")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Failed to read crawler status from Redis: {e}")

    # 2. Try Local File
    if STATUS_FILE_PATH.exists():
        try:
            with open(STATUS_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read crawler status file: {e}")

    # 3. Default empty status
    return {
        "last_run": None,
        "crawlers": {
            "topcv": {"status": "idle", "last_run": None, "jobs_crawled": 0, "jobs_saved": 0, "error": None},
            "careerbuilder": {"status": "idle", "last_run": None, "jobs_crawled": 0, "jobs_saved": 0, "error": None},
            "vietnamworks": {"status": "idle", "last_run": None, "jobs_crawled": 0, "jobs_saved": 0, "error": None},
            "timviecnhanh": {"status": "idle", "last_run": None, "jobs_crawled": 0, "jobs_saved": 0, "error": None},
        },
    }


def update_crawler_status(platform_name: str, data: Dict[str, Any]) -> None:
    """
    Save execution status for a given platform to both local JSON and Redis.
    """
    current_status = get_crawler_status()
    current_status["last_run"] = datetime.now(timezone.utc).isoformat()
    if "crawlers" not in current_status:
        current_status["crawlers"] = {}

    current_status["crawlers"][platform_name] = data

    # 1. Save to local JSON file
    try:
        STATUS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATUS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(current_status, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write crawler status file: {e}")

    # 2. Save to Redis
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.set("cdata:crawlers:status", json.dumps(current_status, ensure_ascii=False))
            # Also set platform-specific key for convenience
            redis_client.set(f"cdata:crawlers:status:{platform_name}", json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.warning(f"Failed to write crawler status to Redis: {e}")


def run_crawler(
    platform_name: str,
    max_pages: int = 10,
    save_to_db: bool = True,
    db_session=None,
    **crawler_kwargs,
) -> Dict[str, Any]:
    """
    Run a single crawler by platform name.
    Args:
        platform_name: Name of the platform ('topcv', 'careerbuilder', 'vietnamworks', 'timviecnhanh')
        max_pages: Maximum pagination depth to crawl
        save_to_db: Whether to upsert crawled jobs into the database
        db_session: Optional SQLAlchemy session
    Returns:
        Dictionary with execution result, job count, duration, and errors.
    """
    from crawlers.careerbuilder import CareerBuilderCrawler
    from crawlers.timviecnhanh import TimViecNhanhCrawler
    from crawlers.topcv import TopCVCrawler
    from crawlers.vietnamworks import VietnamWorksCrawler

    crawlers_map = {
        "topcv": TopCVCrawler,
        "careerbuilder": CareerBuilderCrawler,
        "vietnamworks": VietnamWorksCrawler,
        "timviecnhanh": TimViecNhanhCrawler,
    }

    norm_name = platform_name.lower().strip()
    crawler_class = crawlers_map.get(norm_name)

    if not crawler_class:
        msg = f"Unknown crawler platform '{platform_name}'. Available: {list(crawlers_map.keys())}"
        logger.error(msg)
        return {
            "platform": platform_name,
            "status": "failed",
            "error": msg,
            "jobs_crawled": 0,
            "jobs_saved": 0,
            "duration_seconds": 0,
        }

    logger.info(f"===> Starting crawler [{norm_name}] (max_pages={max_pages}, save_to_db={save_to_db})")
    start_time = time.time()
    start_iso = datetime.now(timezone.utc).isoformat()

    status_data = {
        "platform": norm_name,
        "status": "running",
        "started_at": start_iso,
        "finished_at": None,
        "jobs_crawled": 0,
        "jobs_saved": 0,
        "duration_seconds": 0,
        "error": None,
    }
    update_crawler_status(norm_name, status_data)

    try:
        crawler = crawler_class(db_session=db_session)
        jobs = crawler.crawl(max_pages=max_pages, **crawler_kwargs)
        jobs_crawled = len(jobs)
        jobs_saved = 0

        if save_to_db and jobs:
            jobs_saved = crawler.save_jobs(jobs)

        duration = round(time.time() - start_time, 2)
        end_iso = datetime.now(timezone.utc).isoformat()

        status_data.update({
            "status": "success",
            "finished_at": end_iso,
            "jobs_crawled": jobs_crawled,
            "jobs_saved": jobs_saved,
            "duration_seconds": duration,
            "error": None,
        })
        update_crawler_status(norm_name, status_data)

        logger.info(
            f"===> Completed crawler [{norm_name}]: {jobs_crawled} crawled, "
            f"{jobs_saved} saved in {duration}s"
        )
        return status_data

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        err_msg = str(e)
        logger.error(f"Error during crawl for [{norm_name}]: {err_msg}", exc_info=True)

        status_data.update({
            "status": "failed",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "error": err_msg,
        })
        update_crawler_status(norm_name, status_data)
        return status_data


def run_all_crawlers(
    max_pages: int = 10,
    save_to_db: bool = True,
    db_session=None,
) -> Dict[str, Any]:
    """
    Run all registered crawlers sequentially, collecting logs and results.
    Args:
        max_pages: Max pages to crawl per platform
        save_to_db: Whether to upsert into database
        db_session: Optional SQLAlchemy session
    Returns:
        Summary dict of execution across all platforms.
    """
    logger.info(f"========== STARTING ALL CRAWLERS (max_pages={max_pages}) ==========")
    platforms = ["topcv", "careerbuilder", "vietnamworks", "timviecnhanh"]
    start_time = time.time()
    results = {}
    total_crawled = 0
    total_saved = 0

    for platform in platforms:
        try:
            res = run_crawler(
                platform_name=platform,
                max_pages=max_pages,
                save_to_db=save_to_db,
                db_session=db_session,
            )
            results[platform] = res
            total_crawled += res.get("jobs_crawled", 0)
            total_saved += res.get("jobs_saved", 0)
        except Exception as e:
            logger.error(f"Failed to execute crawler for {platform}: {e}", exc_info=True)
            results[platform] = {
                "platform": platform,
                "status": "failed",
                "error": str(e),
                "jobs_crawled": 0,
                "jobs_saved": 0,
            }

    total_duration = round(time.time() - start_time, 2)
    logger.info(
        f"========== FINISHED ALL CRAWLERS: {total_crawled} crawled, "
        f"{total_saved} saved in {total_duration}s =========="
    )

    summary = {
        "status": "completed",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "total_duration_seconds": total_duration,
        "total_jobs_crawled": total_crawled,
        "total_jobs_saved": total_saved,
        "platforms": results,
    }

    return summary
