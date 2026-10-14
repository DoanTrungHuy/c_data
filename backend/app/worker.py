import logging
from datetime import datetime, timezone
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.database import SyncSessionLocal
from app.models.job import Job

logger = logging.getLogger("cdata_worker")

# Khởi tạo Celery ứng dụng với Redis broker & backend
celery_app = Celery(
    "cdata_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Cấu hình Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 giờ tối đa cho mỗi crawl task
    worker_prefetch_multiplier=1,
)

# Thiết lập lịch trình chạy định kỳ (Celery Beat Schedule)
celery_app.conf.beat_schedule = {
    "run-all-crawlers-periodic": {
        "task": "app.worker.run_all_crawlers",
        "schedule": float(settings.CRAWL_INTERVAL_HOURS * 3600),  # Lặp lại theo số giờ cấu hình
    },
    "deactivate-expired-jobs-daily": {
        "task": "app.worker.deactivate_expired_jobs",
        "schedule": crontab(hour=1, minute=0),  # Chạy quét dọn mỗi ngày vào lúc 01:00 AM
    },
}


@celery_app.task(name="app.worker.run_single_crawler")
def run_single_crawler(platform_name: str):
    """
    Tác vụ Celery chạy crawler cho một nền tảng cụ thể (TopCV, VietnamWorks, CareerBuilder, v.v.)
    """
    normalized_platform = platform_name.strip().lower()
    logger.info(f"==> Bắt đầu crawler cho nền tảng tuyển dụng: {platform_name}")

    crawler_map = {
        "topcv": ("crawlers.topcv", "TopCVCrawler"),
        "vietnamworks": ("crawlers.vietnamworks", "VietnamWorksCrawler"),
        "careerbuilder": ("crawlers.careerbuilder", "CareerBuilderCrawler"),
    }

    try:
        if normalized_platform in crawler_map:
            module_name, class_name = crawler_map[normalized_platform]
            import importlib
            mod = importlib.import_module(module_name)
            crawler_cls = getattr(mod, class_name)
            crawler = crawler_cls()
            logger.info(f"Đang thu thập dữ liệu từ {platform_name} (max_pages={settings.CRAWL_MAX_PAGES})...")
            jobs = crawler.crawl(max_pages=settings.CRAWL_MAX_PAGES)
            saved_count = crawler.save_jobs(jobs)
            logger.info(f"Đã hoàn thành cào {platform_name}: Thu thập {len(jobs)} tin, lưu thành công {saved_count} tin mới.")
            return {
                "status": "success",
                "platform": platform_name,
                "crawled_count": len(jobs),
                "saved_count": saved_count,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        else:
            logger.warning(f"Nền tảng {platform_name} chưa có module crawler chuyên biệt, bỏ qua.")
            return {
                "status": "skipped",
                "platform": platform_name,
                "reason": "unsupported_platform",
            }
    except Exception as e:
        logger.error(f"Lỗi khi thực thi crawler {platform_name}: {e}", exc_info=True)
        return {
            "status": "failed",
            "platform": platform_name,
            "error": str(e),
        }


@celery_app.task(name="app.worker.run_all_crawlers")
def run_all_crawlers():
    """
    Tác vụ Celery kích hoạt toàn bộ các crawler của hệ thống C_Data
    """
    logger.info("==> Bắt đầu kích hoạt chu trình cào dữ liệu toàn diện các nền tảng...")
    supported_platforms = ["TopCV", "VietnamWorks", "ITviec", "CareerBuilder"]
    dispatched_tasks = []

    for platform in supported_platforms:
        task = run_single_crawler.delay(platform)
        dispatched_tasks.append({"platform": platform, "task_id": task.id})

    logger.info(f"Đã kích hoạt {len(dispatched_tasks)} tác vụ crawler thành công.")
    return dispatched_tasks


@celery_app.task(name="app.worker.deactivate_expired_jobs")
def deactivate_expired_jobs():
    """
    Tác vụ định kỳ quét và đánh dấu is_active=False cho các tin tuyển dụng đã quá hạn nộp hồ sơ
    """
    logger.info("==> Bắt đầu tác vụ kiểm tra và vô hiệu hóa tin tuyển dụng hết hạn...")
    try:
        with SyncSessionLocal() as session:
            now_dt = datetime.now(timezone.utc)
            # Truy vấn và cập nhật trạng thái
            updated_count = (
                session.query(Job)
                .filter(
                    Job.is_active.is_(True),
                    Job.expires_at.is_not(None),
                    Job.expires_at < now_dt,
                )
                .update({Job.is_active: False}, synchronize_session=False)
            )
            session.commit()
            logger.info(f"Đã vô hiệu hóa thành công {updated_count} tin tuyển dụng hết hạn.")
            return {"status": "success", "deactivated_count": updated_count}
    except Exception as e:
        logger.error(f"Lỗi khi vô hiệu hóa tin hết hạn: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}
