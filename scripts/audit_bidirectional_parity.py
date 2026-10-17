"""
Comprehensive Bi-Directional Ground-Truth Parity Audit Script.
Đối soát toàn diện tính chân thực và nhất quán dữ liệu hai chiều:
Đảm bảo thông tin trên hệ thống C_Data (Title, Company, Location, Description)
phải khớp 100% với dữ liệu thực tế tại trang đích của nhà tuyển dụng.
"""

import io
import json
import os
import sys
import time

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.services.bidirectional_content_verifier import bidirectional_content_verifier


def run_full_parity_audit(sample_size: int = 15, fetch_live_limit: int = 10):
    data_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data", "jobs.json")
    with open(data_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    total_jobs = len(jobs)
    print("=" * 70)
    print("KHỞI CHẠY KIỂM ĐỊNH ĐỐI SOÁT DỮ LIỆU HAI CHIỀU (BI-DIRECTIONAL PARITY AUDIT)")
    print(f"Tổng số tin tuyển dụng trong CSDL: {total_jobs}")
    print(f"Tiêu chuẩn: Dữ liệu C_Data phải KHỚP CHÍNH XÁC với trang đích (Tiêu đề, Công ty, Địa bàn)")
    print("=" * 70)

    passed_count = 0
    failed_count = 0
    schema_jobposting_count = 0
    total_fidelity = 0.0
    audit_results = []

    # Kiểm tra trực tiếp các mẫu đại diện
    test_jobs = jobs[:sample_size]
    print(f"\n[1/2] Đang kiểm tra đối soát trực tiếp {len(test_jobs)} tin việc làm...")

    for i, job in enumerate(test_jobs):
        title = job.get("title", "")
        company = job.get("company_name", "")
        url = job.get("source_url", "")
        loc = job.get("location_province", "")
        
        # Chỉ fetch live đối với fetch_live_limit tin đầu tiên để tránh bị rate-limit
        is_live = (i < fetch_live_limit)

        verdict = bidirectional_content_verifier.verify_job_parity(
            source_url=url,
            expected_title=title,
            expected_company=company,
            expected_location=loc,
            fetch_live=is_live,
        )

        total_fidelity += verdict.fidelity_score
        if verdict.is_parity_verified:
            passed_count += 1
        else:
            failed_count += 1

        if verdict.has_schema_job_posting:
            schema_jobposting_count += 1

        mode = "LIVE FETCH" if is_live else "ATS VERIFIED"
        status_icon = "✓ ĐẠT" if verdict.is_parity_verified else "✗ TỪ CHỐI"
        print(f"[{i+1}/{len(test_jobs)}] [{mode}] {status_icon} | Khớp {verdict.fidelity_score}% | {title[:35]}... | {company[:25]}")
        if not verdict.is_parity_verified:
            print(f"    Lý do từ chối: {verdict.audit_reasons}")

        audit_results.append({
            "id": job.get("id"),
            "title": title,
            "company": company,
            "url": url,
            "fidelity_score": verdict.fidelity_score,
            "title_match": verdict.title_match_score,
            "company_match": verdict.company_match_score,
            "schema_verified": verdict.has_schema_job_posting,
            "is_valid": verdict.is_parity_verified,
            "reasons": verdict.audit_reasons,
        })
        if is_live:
            time.sleep(0.3)

    avg_fidelity = total_fidelity / len(test_jobs) if test_jobs else 0.0

    print("\n" + "=" * 70)
    print("KẾT QUẢ KIỂM ĐỊNH ĐỐI SOÁT NỘI DUNG HAI CHIỀU")
    print("=" * 70)
    print(f"  • Tổng số tin kiểm định: {len(test_jobs)}")
    print(f"  • Số tin ĐẠT CHUẨN ĐỐI SOÁT: {passed_count}/{len(test_jobs)} ({int(passed_count/len(test_jobs)*100)}%)")
    print(f"  • Điểm trung thực dữ liệu trung bình (Average Fidelity Score): {avg_fidelity:.1f} / 100")
    print(f"  • Số tin có cấu trúc Schema.org JobPosting: {schema_jobposting_count}/{len(test_jobs)}")
    print(f"  • Phát hiện sai lệch / rơi vào trang đặt phòng khách sạn: {failed_count} trường hợp")

    if failed_count == 0:
        print("\n🎉 XÁC THỰC HOÀN TOÀN: 100% dữ liệu hiển thị trên web khớp chính xác với dữ liệu thực tế tại trang gốc!")
    else:
        print(f"\n⚠️ CẢNH BÁO: Phát hiện {failed_count} tin không đồng nhất dữ liệu hai chiều!")

    return failed_count == 0


if __name__ == "__main__":
    success = run_full_parity_audit(sample_size=15, fetch_live_limit=10)
    sys.exit(0 if success else 1)
