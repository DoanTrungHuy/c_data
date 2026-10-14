"""
C_Data - Deep Quality & Long-Running Harvester Runner
Thực thi thu thập sâu & đối soát chất lượng định kỳ:
- Ưu tiên trọng điểm TP. Hạ Long & Tỉnh Quảng Ninh
- Lọc 100% Zero-404 và kiểm tra hạn tuyển dụng thực tế
- Thẩm định 5 trụ cột chất lượng (Điểm 0 - 100, Diamond & Gold Tiers)
- Tự động bóc tách Tech Stack, Lộ trình phỏng vấn 3 bước, Quyền lợi chi tiết
- Đồng bộ cơ sở dữ liệu SQLite và xuất bản trực tiếp vào frontend/public/data/jobs.json
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import SyncSessionLocal
from app.services.smart_background_harvester import SmartBackgroundHarvester
from app.services.deep_quality_engine import enrich_job_posting


def run_cycle():
    print("\n" + "=" * 65)
    print("🚀 BẮT ĐẦU CHU KỲ QUÉT SÂU & THẨM ĐỊNH CHẤT LƯỢNG (DEEP HARVEST)")
    print("=" * 65)
    
    with SyncSessionLocal() as session:
        harvester = SmartBackgroundHarvester(session)
        summary = harvester.run_full_cycle()
        
        print("\n📊 BÁO CÁO THỐNG KÊ CHU TRÌNH:")
        print(f"  • Việc làm tại Quảng Ninh ưu tiên: {summary.get('halong_count')}")
        print(f"  • Đã rà soát hoạt động:           {summary.get('retained_count')} tin")
        print(f"  • Đã đóng/loại bỏ tin lỗi/hết hạn:{summary.get('purged_count')} tin")
        print(f"  • Tổng xuất bản sau thẩm định:    {summary.get('exported_count')} tin")

    print("\n🎉 CHU KỲ QUÉT SÂU HOÀN TẤT THÀNH CÔNG!")


def main():
    parser = argparse.ArgumentParser(description="C_Data Deep Quality Harvester Daemon")
    parser.add_argument("--interval", type=int, default=1800, help="Thời gian lặp lại (giây), mặc định 1800s (30 phút)")
    parser.add_argument("--once", action="store_true", help="Chỉ chạy 1 lần duy nhất rồi thoát")
    args = parser.parse_args()

    if args.once:
        run_cycle()
        return

    print(f"Bắt đầu chạy daemon quét sâu định kỳ mỗi {args.interval} giây ({args.interval / 60:.0f} phút)...")
    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"Lỗi trong chu kỳ quét: {e}", file=sys.stderr)
        
        print(f"\n[NGHỈ] Đang đợi {args.interval} giây cho chu kỳ tiếp theo...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
