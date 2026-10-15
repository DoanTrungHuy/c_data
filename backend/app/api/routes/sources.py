"""
Source Management & Registry REST API Routes.
Provides endpoints for monitoring, toggling, health-checking, and configuring job sources.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.source import (
    SourceCategory,
    SourceDefinition,
    SourceHealthCheckResult,
    SourceHealthStatus,
    SourceRegistrySummary,
    SourceToggleRequest,
)
from app.services.source_registry import source_registry

router = APIRouter(prefix="/sources", tags=["Sources & Source Registry"])


@router.get("", response_model=List[SourceDefinition])
async def list_registered_sources(
    category: Optional[SourceCategory] = Query(None, description="Lọc theo nhóm nguồn trong 5 nhóm chuẩn"),
    enabled_only: bool = Query(False, description="Chỉ lấy các nguồn đang bật"),
    health_status: Optional[SourceHealthStatus] = Query(None, description="Lọc theo tình trạng sức khỏe"),
) -> List[SourceDefinition]:
    """
    Liệt kê toàn bộ các nguồn tuyển dụng đã đăng ký trong Source Registry
    """
    return source_registry.list_sources(
        category=category,
        enabled_only=enabled_only,
        health_status=health_status,
    )


@router.get("/summary/overview", response_model=SourceRegistrySummary)
async def get_source_registry_summary() -> SourceRegistrySummary:
    """
    Lấy báo cáo tổng quan về số lượng và tình trạng các nguồn trong hệ thống C_Data
    """
    return source_registry.get_summary()


@router.get("/pipeline/metrics")
async def get_pipeline_observability_metrics():
    """
    Quan sát toàn diện trạng thái Pipeline từ nguồn thu thập đến kết quả tìm kiếm:
    - Số nguồn cấu hình, hoạt động thực tế, nguồn lỗi/chặn
    - Số tác vụ trong Queue (pending, processing, dead_letter) & Queue Lag
    - Số tin phát hiện, tỷ lệ chuẩn hóa và tỷ lệ URL ứng tuyển hợp lệ
    - Cảnh báo tự động khi nguồn ngừng đồng bộ hoặc tỷ lệ lỗi cao
    """
    from app.services.pipeline_observability_service import pipeline_observability_service
    return pipeline_observability_service.get_pipeline_telemetry()


@router.get("/{source_id}", response_model=SourceDefinition)
async def get_source_details(source_id: str) -> SourceDefinition:
    """
    Lấy thông tin chi tiết, cấu hình rate limit, mốc thời gian crawl và ghi chú tuân thủ của một nguồn
    """
    src = source_registry.get_source(source_id)
    if not src:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy nguồn tuyển dụng có mã '{source_id}' trong registry.",
        )
    return src


@router.post("/{source_id}/toggle", response_model=SourceDefinition)
async def toggle_source_status(
    source_id: str,
    payload: SourceToggleRequest,
) -> SourceDefinition:
    """
    Bật hoặc tắt một nguồn tuyển dụng độc lập mà không ảnh hưởng tới các nguồn khác
    """
    try:
        updated = source_registry.toggle_source(source_id, is_enabled=payload.is_enabled)
        return updated
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nguồn '{source_id}' không tồn tại.",
        )


@router.post("/{source_id}/health-check", response_model=SourceHealthCheckResult)
async def run_single_source_health_check(source_id: str) -> SourceHealthCheckResult:
    """
    Kích hoạt kiểm tra sức khỏe thời gian thực cho một nguồn (kết nối HTTP, DNS, trạng thái API key)
    """
    try:
        return source_registry.run_health_check(source_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nguồn '{source_id}' không tồn tại.",
        )


@router.post("/health-check-all", response_model=List[SourceHealthCheckResult])
async def run_all_sources_health_check() -> List[SourceHealthCheckResult]:
    """
    Kích hoạt kiểm tra sức khỏe thời gian thực cho toàn bộ các nguồn trong Registry
    """
    return source_registry.run_health_check_all()
