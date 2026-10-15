"""
Crawler Adapters Package for C_Data Platform.
"""

from app.adapters.base import (
    AdapterError,
    AdapterErrorType,
    AdapterCrawlResult,
    BaseJobAdapter,
    RawJobRecord,
)
from app.adapters.local_enterprise_adapter import local_enterprise_adapter, LocalEnterpriseAdapter
from app.adapters.facebook_public_adapter import facebook_public_adapter, FacebookPublicAdapter
from app.adapters.threads_public_adapter import threads_public_adapter, ThreadsPublicAdapter

__all__ = [
    "AdapterError",
    "AdapterErrorType",
    "AdapterCrawlResult",
    "BaseJobAdapter",
    "RawJobRecord",
    "local_enterprise_adapter",
    "LocalEnterpriseAdapter",
    "facebook_public_adapter",
    "FacebookPublicAdapter",
    "threads_public_adapter",
    "ThreadsPublicAdapter",
]
