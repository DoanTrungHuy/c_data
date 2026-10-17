"""
Job Verification Engine for C_Data Platform (Prompt 07 & Task P0).
Xác minh trạng thái tuyển dụng thực tế dựa trên bằng chứng minh bạch, TUYỆT ĐỐI KHÔNG SUY ĐOÁN:

Tuân thủ nghiêm ngặt 8 nguyên tắc:
1. Hạn ứng tuyển đã qua: đánh dấu `expired`.
2. Nhà tuyển dụng hoặc trang web thông báo đã đóng: đánh dấu `closed`.
3. Chỉ đánh dấu `active_confirmed` khi có bằng chứng đáng tin cậy (nút nộp đơn hoạt động, hotline phản hồi, portal mở).
4. Trang còn tồn tại hoặc trả HTTP 200 KHÔNG ĐỦ để khẳng định còn tuyển.
5. Timeout, lỗi mạng hoặc bị chặn KHÔNG ĐỒNG NGHĨA với tin đã đóng.
6. Không có ngày hết hạn KHÔNG ĐỒNG NGHĨA với tin còn tuyển.
7. Nếu bằng chứng chưa đủ hoặc mâu thuẫn: giữ `unknown` hoặc `active_likely`.
8. Tuyệt đối KHÔNG dùng LLM để tự suy đoán trạng thái rồi coi kết quả suy đoán là bằng chứng xác minh.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
import urllib.parse

import requests

from app.models.job import Job
from app.services.open_source_reference_verifier import open_source_reference_verifier

logger = logging.getLogger("c_data.verification_engine")

CLOSED_SIGNALS = [
    "đã tuyển đủ", "đã đủ người", "ngưng nhận hồ sơ", "đóng tuyển dụng",
    "hết hạn nộp", "tin tuyển dụng đã hết hạn", "công việc này đã dừng tuyển",
    "vị trí này đã đóng", "job is closed", "expired job", "no longer accepting",
]

ACTIVE_SIGNALS = [
    "nộp hồ sơ ngay", "ứng tuyển ngay", "gửi cv", "apply now",
    "thông tin liên hệ hr", "hạn nộp hồ sơ:", "đang nhận hồ sơ",
]


@dataclass
class VerificationResult:
    status: str                                      # active_confirmed, active_likely, expired, closed, unknown
    status_reason: str
    status_evidence: Dict[str, Any]
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.85
    url_checked: Optional[str] = None
    http_status: Optional[int] = None


class JobVerificationEngine:
    """
    Hệ thống thẩm định & xác minh trạng thái tuyển dụng theo bằng chứng
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 C_DataVerifier/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def verify_job(
        self,
        job: Job,
        live_check: bool = False,
        timeout_seconds: float = 3.0,
    ) -> VerificationResult:
        """
        Xác minh một tin tuyển dụng theo các quy tắc khắt khe
        """
        now = datetime.now(timezone.utc)
        effective_deadline = job.deadline_at or job.expires_at

        # ---------------------------------------------------------------------
        # QUY TẮC 1: Hạn ứng tuyển đã qua -> EXPIRED
        # ---------------------------------------------------------------------
        if effective_deadline:
            dl_utc = effective_deadline if effective_deadline.tzinfo else effective_deadline.replace(tzinfo=timezone.utc)
            if dl_utc < now:
                return VerificationResult(
                    status="expired",
                    status_reason=f"Đã quá hạn nộp hồ sơ ({dl_utc.strftime('%Y-%m-%d')})",
                    status_evidence={
                        "rule": "RULE_1_DEADLINE_EXPIRED",
                        "deadline_at": dl_utc.isoformat(),
                        "current_time": now.isoformat(),
                    },
                    confidence=1.0,
                    verified_at=now,
                )

        # ---------------------------------------------------------------------
        # QUY TẮC 2: Kiểm tra nội dung văn bản có dấu hiệu đóng tuyển dụng -> CLOSED
        # ---------------------------------------------------------------------
        combined_text = f"{job.title} {job.description or ''} {job.requirements or ''}".lower()
        for signal in CLOSED_SIGNALS:
            if signal in combined_text:
                return VerificationResult(
                    status="closed",
                    status_reason=f"Nội dung chứa tín hiệu đóng tuyển: '{signal}'",
                    status_evidence={
                        "rule": "RULE_2_CLOSED_SIGNAL_IN_CONTENT",
                        "detected_signal": signal,
                    },
                    confidence=0.95,
                    verified_at=now,
                )

        # ---------------------------------------------------------------------
        # QUY TẮC 3, 4, 5: Thẩm định bằng chứng liên kết nguồn & Schema.org JSON-LD
        # ---------------------------------------------------------------------
        target_url = job.apply_url or job.source_url
        if target_url and target_url.startswith("http"):
            audit = open_source_reference_verifier.audit_reference(
                url=target_url,
                expected_title=job.title,
                expected_company=job.company,
                fetch_live=live_check,
            )
            if not audit.is_valid_job_reference:
                return VerificationResult(
                    status="closed",
                    status_reason=f"Liên kết nguồn bị từ chối thẩm định: {audit.reason}",
                    status_evidence={
                        "rule": "RULE_REFERENCE_VERIFICATION_REJECTED",
                        "verdict_code": audit.verdict_code,
                        "url": target_url,
                        "resolved_url": audit.resolved_url,
                        "reason": audit.reason,
                    },
                    confidence=audit.confidence,
                    verified_at=now,
                    url_checked=target_url,
                    http_status=audit.http_status,
                )
            elif audit.has_schema_job_posting:
                return VerificationResult(
                    status="active_confirmed",
                    status_reason=f"Đã đối soát thành công cấu trúc Schema.org JobPosting: {audit.reason}",
                    status_evidence={
                        "rule": "RULE_SCHEMA_JOBPOSTING_VERIFIED",
                        "url": target_url,
                        "resolved_url": audit.resolved_url,
                        "schema_data": audit.extracted_schema,
                        "http_status": audit.http_status or 200,
                    },
                    confidence=0.99,
                    verified_at=now,
                    url_checked=target_url,
                    http_status=audit.http_status or 200,
                )

        if live_check and target_url and target_url.startswith("http"):
            try:
                resp = self.session.get(target_url, timeout=timeout_seconds, allow_redirects=True)
                page_text = resp.text.lower()

                # Kiểm tra tín hiệu đóng tuyển trên trang đích
                for signal in CLOSED_SIGNALS:
                    if signal in page_text:
                        return VerificationResult(
                            status="closed",
                            status_reason=f"Trang tuyển dụng phản hồi thông báo đã đóng: '{signal}'",
                            status_evidence={
                                "rule": "RULE_2_LIVE_PAGE_CLOSED",
                                "url": target_url,
                                "http_status": resp.status_code,
                                "detected_signal": signal,
                            },
                            confidence=0.95,
                            verified_at=now,
                            url_checked=target_url,
                            http_status=resp.status_code,
                        )

                # QUY TẮC 4: HTTP 200 KHÔNG ĐỦ để khẳng định còn tuyển
                # Chỉ đánh dấu active_confirmed khi CÓ NÚT ỨNG TUYỂN / FORM NỘP ĐƠN
                has_active_signal = any(sig in page_text for sig in ACTIVE_SIGNALS)
                if resp.status_code == 200 and has_active_signal:
                    return VerificationResult(
                        status="active_confirmed",
                        status_reason="Trang tuyển dụng phản hồi HTTP 200 và có form/nút ứng tuyển đang hoạt động",
                        status_evidence={
                            "rule": "RULE_3_ACTIVE_CONFIRMED_EVIDENCE",
                            "url": target_url,
                            "http_status": 200,
                            "active_indicators_found": True,
                        },
                        confidence=0.95,
                        verified_at=now,
                        url_checked=target_url,
                        http_status=200,
                    )
                elif resp.status_code == 200:
                    # Có HTTP 200 nhưng không tìm thấy nút ứng tuyển rõ ràng -> active_likely
                    return VerificationResult(
                        status="active_likely",
                        status_reason="Trang tồn tại (HTTP 200) nhưng chưa xác thực được nút nộp đơn còn mở",
                        status_evidence={
                            "rule": "RULE_4_HTTP_200_NOT_ENOUGH",
                            "url": target_url,
                            "http_status": 200,
                            "active_indicators_found": False,
                        },
                        confidence=0.70,
                        verified_at=now,
                        url_checked=target_url,
                        http_status=200,
                    )
            except (requests.Timeout, requests.ConnectionError) as e:
                # QUY TẮC 5: Timeout hoặc lỗi mạng KHÔNG đồng nghĩa với tin đã đóng -> Giữ trạng thái thận trọng
                return VerificationResult(
                    status="unknown",
                    status_reason=f"Không thể kết nối máy chủ ({type(e).__name__}). Không coi đây là bằng chứng đã đóng.",
                    status_evidence={
                        "rule": "RULE_5_NETWORK_ERROR_IS_NOT_CLOSED",
                        "url": target_url,
                        "error_type": type(e).__name__,
                    },
                    confidence=0.50,
                    verified_at=now,
                    url_checked=target_url,
                )

        # ---------------------------------------------------------------------
        # QUY TẮC 6, 7: Không có hạn tuyển hoặc chưa đủ bằng chứng -> UNKNOWN hoặc ACTIVE_LIKELY
        # ---------------------------------------------------------------------
        if not effective_deadline:
            # QUY TẮC 6: Không thấy hạn tuyển không đồng nghĩa với còn tuyển
            return VerificationResult(
                status="unknown",
                status_reason="Tin chưa có hạn nộp hồ sơ xác định từ nguồn gốc",
                status_evidence={
                    "rule": "RULE_6_NO_DEADLINE_MEANS_UNKNOWN",
                    "deadline_at": None,
                },
                confidence=0.60,
                verified_at=now,
            )

        # Có hạn nộp còn xa nhưng chưa xác thực trực tiếp
        return VerificationResult(
            status="active_likely",
            status_reason=f"Có hạn nộp hồ sơ hợp lệ ({effective_deadline.strftime('%Y-%m-%d')}) từ nguồn kiểm duyệt",
            status_evidence={
                "rule": "RULE_7_ACTIVE_LIKELY_WITH_FUTURE_DEADLINE",
                "deadline_at": effective_deadline.isoformat(),
            },
            confidence=0.85,
            verified_at=now,
        )


job_verification_engine = JobVerificationEngine()
