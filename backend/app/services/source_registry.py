"""
Source Registry Service for C_Data Platform.
Centralized management, health check, credential verification, rate limiting,
metrics persistence, and dynamic adapter registry for all 5 job source categories.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Callable, Dict, List, Optional
import urllib.parse
import requests

from app.schemas.source import (
    AccessMethod,
    CredentialStatus,
    RateLimitConfig,
    SourceCategory,
    SourceDefinition,
    SourceHealthCheckResult,
    SourceHealthStatus,
    SourceMetrics,
    SourceRegistrySummary,
)

logger = logging.getLogger("c_data.source_registry")

# Đường dẫn lưu trữ trạng thái bền vững của Registry
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_FILE_PATH = DATA_DIR / "source_registry_state.json"

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataBot/1.0"


class SourceRegistry:
    """
    Quản lý danh mục nguồn tuyển dụng tập trung cho C_Data
    Đảm bảo:
    - Phân chia đầy đủ 5 nhóm nguồn.
    - Không đánh dấu active nếu chỉ khai báo cấu hình.
    - Health check thực tế (HTTP ping, kiểm tra credential, phản hồi máy chủ).
    - Lưu trữ bền vững số liệu (discovered, error, latency) và trạng thái bật/tắt.
    - Độc lập với search engine: thêm nguồn mới không cần sửa code tìm kiếm.
    """

    def __init__(self):
        self._sources: Dict[str, SourceDefinition] = {}
        self._adapters: Dict[str, Callable[..., List[Dict[str, Any]]]] = {}
        self._initialize_catalog()
        self._load_persisted_state()
        self._register_default_adapters()

    def _initialize_catalog(self) -> None:
        """
        Khởi tạo danh mục 5 nhóm nguồn chuẩn của nền tảng C_Data
        Trạng thái ban đầu luôn là UNKNOWN hoặc UNCONFIGURED, tuyệt đối không mặc định là HEALTHY
        """
        initial_sources: List[SourceDefinition] = [
            # -----------------------------------------------------------------
            # NHÓM 1: TRANG TUYỂN DỤNG CHÍNH THỨC CỦA DOANH NGHIỆP (ENTERPRISE_DIRECT)
            # -----------------------------------------------------------------
            SourceDefinition(
                id="sun_group",
                name="Tập đoàn Sun Group (Vùng Đông Bắc & Sun World)",
                category=SourceCategory.ENTERPRISE_DIRECT,
                domain="sungroup.com.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=2,
                sync_interval_seconds=7200,
                rate_limit=RateLimitConfig(requests_per_minute=20, min_delay_seconds=2.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Cổng thông tin tuyển dụng công khai, kiểm tra robots.txt trước khi thu thập.",
                compliance_notes="Tuân thủ chính sách bảo mật của Sun Group, chỉ thu thập tin công khai.",
                target_provinces=["Quảng Ninh", "Đà Nẵng", "Toàn quốc"],
            ),
            SourceDefinition(
                id="vinpearl",
                name="Vinpearl Resort & Khách sạn (Tập đoàn Vingroup)",
                category=SourceCategory.ENTERPRISE_DIRECT,
                domain="vinpearl.com",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=2,
                sync_interval_seconds=7200,
                rate_limit=RateLimitConfig(requests_per_minute=20, min_delay_seconds=2.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Cổng thông tin tuyển dụng công khai Vinpearl Hạ Long & toàn hệ thống.",
                compliance_notes="Tôn trọng robots.txt của vinpearl.com, không truy cập trang quản trị nội bộ.",
                target_provinces=["Quảng Ninh", "Nha Trang", "Phú Quốc", "Toàn quốc"],
            ),
            SourceDefinition(
                id="tkv_mining",
                name="Tập đoàn Than - Khoáng sản Việt Nam (TKV Quảng Ninh)",
                category=SourceCategory.ENTERPRISE_DIRECT,
                domain="vinacomin.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=3,
                sync_interval_seconds=14400,
                rate_limit=RateLimitConfig(requests_per_minute=15, min_delay_seconds=3.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Bản tin tuyển dụng lao động ngành mỏ, kỹ thuật khai thác than trên cổng TKV.",
                compliance_notes="Chỉ thu thập thông cáo báo chí và bản tin tuyển sinh/tuyển dụng công khai.",
                target_provinces=["Quảng Ninh", "Hà Nội"],
            ),
            SourceDefinition(
                id="fpt_telecom",
                name="FPT Telecom & Khối Công nghệ FPT",
                category=SourceCategory.ENTERPRISE_DIRECT,
                domain="fpt.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=2,
                sync_interval_seconds=7200,
                rate_limit=RateLimitConfig(requests_per_minute=25, min_delay_seconds=1.5),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Cổng việc làm FPT Telecom chi nhánh Quảng Ninh và toàn quốc.",
                compliance_notes="Tôn trọng băng thông máy chủ FPT, không crawl dữ liệu ứng viên.",
                target_provinces=["Quảng Ninh", "Hà Nội", "Hồ Chí Minh", "Toàn quốc"],
            ),
            SourceDefinition(
                id="cict_cailan",
                name="Công ty TNHH Cảng Container Quốc tế Cái Lân (CICT)",
                category=SourceCategory.ENTERPRISE_DIRECT,
                domain="cict.com.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=4,
                sync_interval_seconds=21600,
                rate_limit=RateLimitConfig(requests_per_minute=10, min_delay_seconds=4.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Thông báo tuyển dụng logistics cảng biển và vận hành cẩu container.",
                compliance_notes="Trang tin tức tuyển dụng mở.",
                target_provinces=["Quảng Ninh", "Hải Phòng"],
            ),

            # -----------------------------------------------------------------
            # NHÓM 2: WEBSITE TUYỂN DỤNG TẠI VIỆT NAM (NATIONAL_JOB_BOARD)
            # -----------------------------------------------------------------
            SourceDefinition(
                id="careerviet",
                name="Sàn tuyển dụng CareerViet (CareerBuilder VN)",
                category=SourceCategory.NATIONAL_JOB_BOARD,
                domain="careerviet.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=1,
                sync_interval_seconds=3600,
                rate_limit=RateLimitConfig(requests_per_minute=30, min_delay_seconds=1.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Truy cập danh mục việc làm công khai qua URL search.",
                compliance_notes="Tuân thủ giới hạn truy vấn, trích xuất chính xác liên kết gốc.",
                target_provinces=["Toàn quốc", "Quảng Ninh", "Hà Nội", "Hồ Chí Minh"],
            ),
            SourceDefinition(
                id="topcv",
                name="Cổng thông tin tuyển dụng TopCV",
                category=SourceCategory.NATIONAL_JOB_BOARD,
                domain="topcv.vn",
                access_method=AccessMethod.AUTHORIZED_ADAPTER,
                is_enabled=True,
                priority=1,
                sync_interval_seconds=3600,
                rate_limit=RateLimitConfig(requests_per_minute=60, min_delay_seconds=0.5),
                health_status=SourceHealthStatus.UNCONFIGURED,
                credential_status=CredentialStatus.MISSING,
                required_credentials=["TOPCV_API_KEY"],
                access_conditions="Yêu cầu khóa API đối tác chính thức (Partner API Key) để truy vấn.",
                compliance_notes="Tuân thủ nghiêm ngặt điều khoản bản quyền TopCV. Không dùng scraper lách bảo vệ.",
                target_provinces=["Toàn quốc"],
            ),
            SourceDefinition(
                id="vietnamworks",
                name="Cổng việc làm chuyên môn cao VietnamWorks",
                category=SourceCategory.NATIONAL_JOB_BOARD,
                domain="vietnamworks.com",
                access_method=AccessMethod.AUTHORIZED_ADAPTER,
                is_enabled=True,
                priority=1,
                sync_interval_seconds=3600,
                rate_limit=RateLimitConfig(requests_per_minute=60, min_delay_seconds=0.5),
                health_status=SourceHealthStatus.UNCONFIGURED,
                credential_status=CredentialStatus.MISSING,
                required_credentials=["VIETNAMWORKS_API_KEY"],
                access_conditions="Yêu cầu khóa xác thực API đối tác từ tập đoàn Navigos Group.",
                compliance_notes="Chỉ kích hoạt khi có hợp đồng đối tác chia sẻ dữ liệu hoặc API cấp phép.",
                target_provinces=["Toàn quốc"],
            ),

            # -----------------------------------------------------------------
            # NHÓM 3: TRANG TUYỂN DỤNG CHUYÊN NGÀNH HOẶC ĐỊA PHƯƠNG (SPECIALIZED_LOCAL)
            # -----------------------------------------------------------------
            SourceDefinition(
                id="quang_ninh_job_center",
                name="Trung tâm Dịch vụ Việc làm tỉnh Quảng Ninh",
                category=SourceCategory.SPECIALIZED_LOCAL,
                domain="quangninh.gov.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=2,
                sync_interval_seconds=14400,
                rate_limit=RateLimitConfig(requests_per_minute=15, min_delay_seconds=3.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Cổng thông tin sàn giao dịch việc làm định kỳ tỉnh Quảng Ninh.",
                compliance_notes="Thu thập thông báo tuyển dụng chính thống của cơ quan quản lý lao động tỉnh.",
                target_provinces=["Quảng Ninh"],
            ),
            SourceDefinition(
                id="quang_ninh_industrial_zones",
                name="Ban Quản lý Khu kinh tế & Khu công nghiệp Quảng Ninh",
                category=SourceCategory.SPECIALIZED_LOCAL,
                domain="bqlkkt.quangninh.gov.vn",
                access_method=AccessMethod.PUBLIC_WEB,
                is_enabled=True,
                priority=3,
                sync_interval_seconds=21600,
                rate_limit=RateLimitConfig(requests_per_minute=10, min_delay_seconds=4.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Bản tin tuyển dụng lao động khu công nghiệp (Đông Mai, Sông Khoai, Bắc Tiền Phong).",
                compliance_notes="Dữ liệu cổng dịch vụ công địa phương.",
                target_provinces=["Quảng Ninh"],
            ),

            # -----------------------------------------------------------------
            # NHÓM 4: NGUỒN CÔNG KHAI TỪ MẠNG XÃ HỘI (SOCIAL_PUBLIC)
            # -----------------------------------------------------------------
            SourceDefinition(
                id="social_public_halong",
                name="Kênh Thông báo Tuyển dụng Công khai Quảng Ninh (Mạng xã hội)",
                category=SourceCategory.SOCIAL_PUBLIC,
                domain="facebook.com",
                access_method=AccessMethod.AUTHORIZED_ADAPTER,
                is_enabled=True,
                priority=4,
                sync_interval_seconds=7200,
                rate_limit=RateLimitConfig(requests_per_minute=15, min_delay_seconds=3.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Chỉ thu thập các bài đăng công khai (Public Posts), không yêu cầu đăng nhập.",
                compliance_notes="Vệ sinh toàn bộ URL (loại bỏ tham số theo dõi), không vi phạm quyền riêng tư tài khoản cá nhân.",
                target_provinces=["Quảng Ninh"],
            ),
            SourceDefinition(
                id="threads_public",
                name="Kênh Tuyển dụng Threads Meta (Tài khoản Sáng tạo & F&B)",
                category=SourceCategory.SOCIAL_PUBLIC,
                domain="threads.net",
                access_method=AccessMethod.AUTHORIZED_ADAPTER,
                is_enabled=True,
                priority=4,
                sync_interval_seconds=7200,
                rate_limit=RateLimitConfig(requests_per_minute=15, min_delay_seconds=3.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Chỉ thu thập các bài đăng công khai của tài khoản thương hiệu, không truy cập tài khoản riêng tư.",
                compliance_notes="Tuân thủ điều khoản Threads API, loại bỏ tham số theo dõi URL.",
                target_provinces=["Quảng Ninh", "Toàn quốc"],
            ),

            # -----------------------------------------------------------------
            # NHÓM 5: API/RSS HOẶC NGUỒN DỮ LIỆU ĐƯỢC CẤP QUYỀN (AUTHORIZED_API)
            # -----------------------------------------------------------------
            SourceDefinition(
                id="government_national_labor_rss",
                name="Cổng Thông tin Việc làm Quốc gia (Bộ LĐ-TB&XH Open RSS)",
                category=SourceCategory.AUTHORIZED_API,
                domain="vieclamvietnam.gov.vn",
                access_method=AccessMethod.RSS,
                is_enabled=True,
                priority=3,
                sync_interval_seconds=14400,
                rate_limit=RateLimitConfig(requests_per_minute=20, min_delay_seconds=2.0),
                health_status=SourceHealthStatus.UNKNOWN,
                credential_status=CredentialStatus.UNNEEDED,
                access_conditions="Kênh RSS và Open Data của cơ quan quản lý lao động nhà nước.",
                compliance_notes="Tuân thủ chuẩn RSS syndication mở, định kỳ nạp dữ liệu.",
                target_provinces=["Toàn quốc", "Quảng Ninh"],
            ),
        ]

        for s in initial_sources:
            self._sources[s.id] = s

    def _register_default_adapters(self) -> None:
        """Đăng ký các Crawler Adapter chính thức cho từng nguồn tương ứng"""
        try:
            from app.adapters.careerviet_adapter import careerviet_adapter
            self.register_adapter("careerviet", careerviet_adapter.as_discovery_callable())
        except Exception as e:
            logger.warning(f"Chưa thể nạp CareerVietAdapter: {e}")

        try:
            from app.adapters.rss_syndication_adapter import rss_syndication_adapter
            self.register_adapter("government_national_labor_rss", rss_syndication_adapter.as_discovery_callable())
        except Exception as e:
            logger.warning(f"Chưa thể nạp RssSyndicationAdapter: {e}")

        try:
            from app.adapters.partner_api_adapter import partner_api_adapter
            self.register_adapter("topcv", partner_api_adapter.as_discovery_callable())
        except Exception as e:
            logger.warning(f"Chưa thể nạp PartnerApiAdapter: {e}")

        try:
            from app.adapters.local_enterprise_adapter import local_enterprise_adapter
            local_call = local_enterprise_adapter.as_discovery_callable()
            self.register_adapter("sun_group", local_call)
            self.register_adapter("vinpearl", local_call)
            self.register_adapter("tkv_mining", local_call)
            self.register_adapter("wyndham_legend_halong", local_call)
        except Exception as e:
            logger.warning(f"Chưa thể nạp LocalEnterpriseAdapter: {e}")

        try:
            from app.adapters.facebook_public_adapter import facebook_public_adapter
            self.register_adapter("social_public_halong", facebook_public_adapter.as_discovery_callable())
        except Exception as e:
            logger.warning(f"Chưa thể nạp FacebookPublicAdapter: {e}")

        try:
            from app.adapters.threads_public_adapter import threads_public_adapter
            self.register_adapter("threads_public", threads_public_adapter.as_discovery_callable())
        except Exception as e:
            logger.warning(f"Chưa thể nạp ThreadsPublicAdapter: {e}")

    def _load_persisted_state(self) -> None:
        """Nạp trạng thái và chỉ số đo lường đã lưu trữ từ đĩa"""
        if not STATE_FILE_PATH.exists():
            return
        try:
            with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for src_id, saved_attrs in data.items():
                if src_id in self._sources:
                    src = self._sources[src_id]
                    # Phục hồi trạng thái toggle
                    if "is_enabled" in saved_attrs:
                        src.is_enabled = bool(saved_attrs["is_enabled"])
                    # Phục hồi metrics
                    if "metrics" in saved_attrs:
                        src.metrics = SourceMetrics(**saved_attrs["metrics"])
                    # Phục hồi sức khỏe
                    if "health_status" in saved_attrs:
                        src.health_status = SourceHealthStatus(saved_attrs["health_status"])
                    if "health_evidence" in saved_attrs:
                        src.health_evidence = saved_attrs["health_evidence"]
                    if "credential_status" in saved_attrs:
                        src.credential_status = CredentialStatus(saved_attrs["credential_status"])
                    if "last_health_check_at" in saved_attrs and saved_attrs["last_health_check_at"]:
                        src.last_health_check_at = datetime.fromisoformat(saved_attrs["last_health_check_at"])
                    if "last_successful_crawl" in saved_attrs and saved_attrs["last_successful_crawl"]:
                        src.last_successful_crawl = datetime.fromisoformat(saved_attrs["last_successful_crawl"])
                    if "last_failed_crawl" in saved_attrs and saved_attrs["last_failed_crawl"]:
                        src.last_failed_crawl = datetime.fromisoformat(saved_attrs["last_failed_crawl"])
                    if "last_error_message" in saved_attrs:
                        src.last_error_message = saved_attrs["last_error_message"]
            logger.info(f"Đã phục hồi trạng thái cho {len(data)} nguồn từ {STATE_FILE_PATH}")
        except Exception as e:
            logger.warning(f"Không thể phục hồi trạng thái nguồn từ {STATE_FILE_PATH}: {e}")

    def _persist_state(self) -> None:
        """Lưu trữ trạng thái hiện tại xuống đĩa"""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            export_data = {}
            for src_id, src in self._sources.items():
                export_data[src_id] = {
                    "is_enabled": src.is_enabled,
                    "health_status": src.health_status.value,
                    "health_evidence": src.health_evidence,
                    "credential_status": src.credential_status.value,
                    "last_health_check_at": src.last_health_check_at.isoformat() if src.last_health_check_at else None,
                    "last_successful_crawl": src.last_successful_crawl.isoformat() if src.last_successful_crawl else None,
                    "last_failed_crawl": src.last_failed_crawl.isoformat() if src.last_failed_crawl else None,
                    "last_error_message": src.last_error_message,
                    "metrics": src.metrics.model_dump(),
                }
            with open(STATE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Lỗi khi lưu trữ trạng thái nguồn: {e}")

    # =========================================================================
    # QUẢN LÝ ĐĂNG KÝ VÀ TRUY VẤN NGUỒN
    # =========================================================================
    def register_source(self, source: SourceDefinition) -> None:
        """Đăng ký nguồn mới hoặc cập nhật cấu hình nguồn đã có"""
        self._sources[source.id] = source
        self._persist_state()
        logger.info(f"Đã đăng ký nguồn: [{source.category.value}] {source.name} (ID: {source.id})")

    def register_adapter(self, source_id: str, adapter_fn: Callable[..., List[Dict[str, Any]]]) -> None:
        """Đăng ký hàm thu thập / adapter cho nguồn tương ứng"""
        self._adapters[source_id] = adapter_fn
        logger.info(f"Đã liên kết adapter crawler cho nguồn '{source_id}'")

    def get_source(self, source_id: str) -> Optional[SourceDefinition]:
        """Lấy thông tin chi tiết một nguồn"""
        return self._sources.get(source_id)

    def list_sources(
        self,
        category: Optional[SourceCategory] = None,
        enabled_only: bool = False,
        health_status: Optional[SourceHealthStatus] = None,
    ) -> List[SourceDefinition]:
        """Liệt kê danh sách nguồn kèm bộ lọc linh hoạt"""
        results = []
        for s in self._sources.values():
            if category and s.category != category:
                continue
            if enabled_only and not s.is_enabled:
                continue
            if health_status and s.health_status != health_status:
                continue
            results.append(s)
        # Sắp xếp theo ưu tiên (1 -> 10)
        results.sort(key=lambda x: x.priority)
        return results

    def toggle_source(self, source_id: str, is_enabled: bool) -> SourceDefinition:
        """Bật/tắt nguồn độc lập"""
        src = self._sources.get(source_id)
        if not src:
            raise KeyError(f"Nguồn '{source_id}' không tồn tại trong Registry.")
        src.is_enabled = is_enabled
        self._persist_state()
        logger.info(f"Đã {'bật' if is_enabled else 'tắt'} nguồn '{src.name}' ({source_id})")
        return src

    def get_runnable_sources(self, target_province: Optional[str] = None) -> List[SourceDefinition]:
        """
        Lấy danh sách các nguồn sẵn sàng chạy cho quá trình tìm kiếm/cào dữ liệu:
        - Phải được BẬT (is_enabled = True)
        - Trạng thái sức khỏe KHÔNG PHẢI là UNCONFIGURED hoặc UNHEALTHY
        - Phù hợp với địa bàn (nếu có chỉ định)
        """
        runnable = []
        for s in self._sources.values():
            if not s.is_enabled:
                continue
            # Nguồn thiếu credential hoặc unhealthy thì bỏ qua để không gây lỗi nghẽn pipeline
            if s.health_status in [SourceHealthStatus.UNCONFIGURED, SourceHealthStatus.UNHEALTHY]:
                continue

            # Kiểm tra độ phủ địa bàn
            if target_province:
                prov_norm = target_province.lower()
                matches_prov = any(
                    prov_norm in tp.lower() or "toàn quốc" in tp.lower()
                    for tp in s.target_provinces
                )
                if not matches_prov:
                    continue

            runnable.append(s)

        runnable.sort(key=lambda x: x.priority)
        return runnable

    def get_adapter(self, source_id: str) -> Optional[Callable[..., List[Dict[str, Any]]]]:
        """Lấy adapter thực thi đã đăng ký"""
        return self._adapters.get(source_id)

    # =========================================================================
    # KIỂM TRA SỨC KHỎE (HEALTH CHECK) THỜI GIAN THỰC
    # =========================================================================
    def run_health_check(self, source_id: str) -> SourceHealthCheckResult:
        """
        Thực hiện kiểm tra sức khỏe thực tế cho một nguồn:
        - Kiểm tra credential nếu nguồn yêu cầu (ví dụ TOPCV_API_KEY).
        - Thực hiện HTTP HEAD/GET tới domain/endpoint với timeout an toàn.
        - Ghi lại latency và cập nhật bằng chứng thực tế (health_evidence).
        - Tuyệt đối không giả mạo kết quả.
        """
        src = self._sources.get(source_id)
        if not src:
            raise KeyError(f"Nguồn '{source_id}' không tồn tại.")

        now = datetime.now(timezone.utc)
        src.last_health_check_at = now

        # 1. Kiểm tra Credential nếu nguồn yêu cầu
        if src.required_credentials:
            missing_creds = [c for c in src.required_credentials if not os.getenv(c)]
            if missing_creds:
                src.credential_status = CredentialStatus.MISSING
                src.health_status = SourceHealthStatus.UNCONFIGURED
                src.health_evidence = f"Thiếu biến môi trường bắt buộc: {', '.join(missing_creds)}"
                self._persist_state()
                return SourceHealthCheckResult(
                    source_id=src.id,
                    source_name=src.name,
                    status=src.health_status,
                    is_healthy=False,
                    latency_ms=0.0,
                    evidence=src.health_evidence,
                    checked_at=now,
                    error=f"Chưa cấu hình API credentials: {missing_creds}",
                )
            else:
                src.credential_status = CredentialStatus.VALID

        # 2. Kiểm tra kết nối mạng thực tế qua HTTP
        t0 = time.time()
        url = f"https://{src.domain}"
        evidence = ""
        is_healthy = False
        error_msg = None

        try:
            # Thử gửi request HEAD nhẹ nhàng với User-Agent chuẩn
            resp = requests.head(
                url,
                headers={"User-Agent": DEFAULT_USER_AGENT},
                timeout=4.0,
                allow_redirects=True,
            )
            # Nếu HEAD bị 405 Method Not Allowed, thử GET với stream=True
            if resp.status_code == 405:
                resp = requests.get(
                    url,
                    headers={"User-Agent": DEFAULT_USER_AGENT},
                    timeout=4.0,
                    stream=True,
                )

            latency = round((time.time() - t0) * 1000, 1)

            if resp.status_code < 400:
                src.health_status = SourceHealthStatus.HEALTHY
                evidence = f"Máy chủ {src.domain} phản hồi HTTP {resp.status_code} ({latency}ms)"
                is_healthy = True
            elif resp.status_code in [403, 429]:
                # Máy chủ có cơ chế chống bot hoặc rate limit
                src.health_status = SourceHealthStatus.DEGRADED
                evidence = f"Máy chủ phản hồi HTTP {resp.status_code} (Cơ chế bảo vệ/Rate-limit) sau {latency}ms"
                is_healthy = True  # Vẫn coi là hoạt động nhưng degraded
            else:
                src.health_status = SourceHealthStatus.UNHEALTHY
                evidence = f"Máy chủ phản hồi lỗi HTTP {resp.status_code} sau {latency}ms"
                error_msg = f"HTTP Error {resp.status_code}"

        except requests.exceptions.Timeout:
            latency = round((time.time() - t0) * 1000, 1)
            src.health_status = SourceHealthStatus.DEGRADED
            evidence = f"Yêu cầu vượt quá thời gian chờ (Timeout sau {latency}ms)"
            error_msg = "Connection timeout"
        except requests.exceptions.RequestException as e:
            latency = round((time.time() - t0) * 1000, 1)
            src.health_status = SourceHealthStatus.UNHEALTHY
            evidence = f"Không thể kết nối đến {src.domain}: {type(e).__name__}"
            error_msg = str(e)

        src.health_evidence = evidence
        self._persist_state()

        return SourceHealthCheckResult(
            source_id=src.id,
            source_name=src.name,
            status=src.health_status,
            is_healthy=is_healthy,
            latency_ms=latency,
            evidence=evidence,
            checked_at=now,
            error=error_msg,
        )

    def run_health_check_all(self) -> List[SourceHealthCheckResult]:
        """Chạy kiểm tra sức khỏe trên toàn bộ danh mục nguồn"""
        results = []
        for src_id in list(self._sources.keys()):
            res = self.run_health_check(src_id)
            results.append(res)
        return results

    # =========================================================================
    # GHI NHẬN SỐ LIỆU ĐO LƯỜNG (METRICS & TELEMETRY)
    # =========================================================================
    def record_crawl_success(
        self,
        source_id: str,
        discovered_count: int,
        new_count: int,
        duration_ms: float,
    ) -> None:
        """Ghi nhận phiên crawl thành công từ một nguồn"""
        src = self._sources.get(source_id)
        if not src:
            return

        now = datetime.now(timezone.utc)
        src.last_successful_crawl = now
        src.metrics.discovered_count += discovered_count
        src.metrics.new_count += new_count
        src.metrics.last_crawl_duration_ms = duration_ms
        src.metrics.total_runs += 1

        # Cập nhật sức khỏe thành healthy nếu đã crawl thành công bản ghi
        if discovered_count > 0:
            src.health_status = SourceHealthStatus.HEALTHY
            src.health_evidence = f"Đồng bộ thành công {discovered_count} bản ghi ({round(duration_ms, 1)}ms)"

        self._persist_state()

    def record_crawl_failure(
        self,
        source_id: str,
        error_message: str,
        duration_ms: float,
    ) -> None:
        """Ghi nhận lỗi khi cào dữ liệu từ một nguồn"""
        src = self._sources.get(source_id)
        if not src:
            return

        now = datetime.now(timezone.utc)
        src.last_failed_crawl = now
        src.last_error_message = error_message
        src.metrics.error_count += 1
        src.metrics.last_crawl_duration_ms = duration_ms
        src.metrics.total_runs += 1

        # Nếu lỗi liên tiếp nhiều lần, đánh dấu degraded
        if src.metrics.error_count >= 3:
            src.health_status = SourceHealthStatus.DEGRADED
            src.health_evidence = f"Lỗi crawl lặp lại: {error_message}"

        self._persist_state()

    def get_summary(self) -> SourceRegistrySummary:
        """Tạo báo cáo tổng quan tình trạng các nguồn trong hệ thống"""
        total = len(self._sources)
        enabled = sum(1 for s in self._sources.values() if s.is_enabled)
        disabled = total - enabled
        healthy = sum(1 for s in self._sources.values() if s.health_status == SourceHealthStatus.HEALTHY)
        degraded = sum(1 for s in self._sources.values() if s.health_status == SourceHealthStatus.DEGRADED)
        unhealthy = sum(1 for s in self._sources.values() if s.health_status == SourceHealthStatus.UNHEALTHY)
        unconfigured = sum(1 for s in self._sources.values() if s.health_status == SourceHealthStatus.UNCONFIGURED)

        by_cat: Dict[str, int] = {}
        for s in self._sources.values():
            cat = s.category.value
            by_cat[cat] = by_cat.get(cat, 0) + 1

        return SourceRegistrySummary(
            total_sources=total,
            enabled_sources=enabled,
            disabled_sources=disabled,
            healthy_sources=healthy,
            degraded_sources=degraded,
            unhealthy_sources=unhealthy,
            unconfigured_sources=unconfigured,
            by_category=by_cat,
        )


# Khởi tạo thể hiện Singleton dùng chung cho toàn bộ ứng dụng
source_registry = SourceRegistry()
