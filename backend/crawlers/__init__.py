"""
Crawlers package for C_Data job aggregation platform.
Provides crawler implementations for Vietnamese job portals:
- TopCV (topcv.vn)
- CareerBuilder / CareerViet (careerbuilder.vn)
- VietnamWorks (vietnamworks.com)
- TimViecNhanh (timviecnhanh.com)
"""

from typing import Dict, List, Optional, Type

from crawlers.base import BaseCrawler
from crawlers.careerbuilder import CareerBuilderCrawler
from crawlers.scheduler import (
    get_crawler_status,
    run_all_crawlers,
    run_crawler,
)
from crawlers.timviecnhanh import TimViecNhanhCrawler
from crawlers.topcv import TopCVCrawler
from crawlers.vietnamworks import VietnamWorksCrawler

CRAWLERS_REGISTRY: Dict[str, Type[BaseCrawler]] = {
    "topcv": TopCVCrawler,
    "careerbuilder": CareerBuilderCrawler,
    "vietnamworks": VietnamWorksCrawler,
    "timviecnhanh": TimViecNhanhCrawler,
}


def get_all_crawlers(db_session=None) -> List[BaseCrawler]:
    """
    Instantiate and return a list of all registered crawler instances.
    """
    return [cls(db_session=db_session) for cls in CRAWLERS_REGISTRY.values()]


def get_crawler_by_name(name: str, db_session=None) -> Optional[BaseCrawler]:
    """
    Retrieve and instantiate a specific crawler instance by its platform name.
    """
    cls = CRAWLERS_REGISTRY.get(name.lower().strip())
    if cls:
        return cls(db_session=db_session)
    return None


__all__ = [
    "BaseCrawler",
    "TopCVCrawler",
    "CareerBuilderCrawler",
    "VietnamWorksCrawler",
    "TimViecNhanhCrawler",
    "CRAWLERS_REGISTRY",
    "get_all_crawlers",
    "get_crawler_by_name",
    "run_all_crawlers",
    "run_crawler",
    "get_crawler_status",
]
