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
from app.adapters.jobspy_adapter import JobSpyMultiSourceAdapter
from app.adapters.ats_api_adapter import DirectATSApiAdapter, ats_api_direct_adapter
from app.adapters.linkedin_guest_adapter import LinkedInGuestAdapter, linkedin_guest_adapter
from app.adapters.itviec_adapter import ITviecAdapter, itviec_adapter
from app.adapters.ybox_adapter import YboxAdapter, ybox_adapter
from app.adapters.jobsgo_adapter import JobsGOAdapter, jobsgo_adapter

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
    "JobSpyMultiSourceAdapter",
    "DirectATSApiAdapter",
    "ats_api_direct_adapter",
    "LinkedInGuestAdapter",
    "linkedin_guest_adapter",
    "ITviecAdapter",
    "itviec_adapter",
    "YboxAdapter",
    "ybox_adapter",
    "JobsGOAdapter",
    "jobsgo_adapter",
]

