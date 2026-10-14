"""
Script Khởi Chạy Con Chạy Nền Thu Thập & Đối Soát Tuyển Dụng (Background Harvester Daemon)
Chạy liên tục trong nền để:
1. Quét toàn diện các tỉnh thành, ưu tiên tuyệt đối TP. Hạ Long & Quảng Ninh.
2. Kiểm tra thực tế mọi link nguồn (Zero 404).
3. Rà soát hạn nộp hồ sơ và dấu hiệu đóng đơn để không bao giờ đăng tin hết hạn.
4. Tự động đồng bộ và xuất bản dữ liệu mới cho Frontend / GitHub Pages.

Cách dùng:
- Chạy 1 lần: python scripts/run_background_harvester_daemon.py --once
- Chạy liên tục (mặc định mỗi 30 phút): python scripts/run_background_harvester_daemon.py
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import sys
import time

# Đảm bảo đường dẫn import từ backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Daemon-Harvester] %(message)s",
)
logger = logging.getLogger("c_data.daemon_harvester")

from app.services.smart_background_harvester import SmartBackgroundHarvester


def main():
    parser = argparse.ArgumentParser(description="C_Data Background Harvester Daemon")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Chạy 1 chu kỳ duy nhất rồi thoát",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="Thời gian nghỉ giữa các chu kỳ quét (tính bằng giây, mặc định: 1800s = 30 phút)",
    )
    args = parser.parse_args()

    harvester = SmartBackgroundHarvester()
    logger.info("🚀 Khởi động Con Chạy Nền Thu Thập & Đối Soát C_Data...")
    logger.info(f"Ưu tiên: Hạ Long & Quảng Ninh | Chế độ: {'Chạy 1 lần' if args.once else f'Lặp lại mỗi {args.interval}s'}")

    iteration = 1
    while True:
        start_time = time.time()
        logger.info(f"\n--- BẮT ĐẦU CHU KỲ #{iteration} ({datetime.now().strftime('%H:%M:%S %d/%m/%Y')}) ---")

        try:
            result = harvester.run_full_cycle()
            elapsed = time.time() - start_time
            logger.info(
                f"✅ Hoàn tất chu kỳ #{iteration} trong {elapsed:.1f}s: "
                f"Xác thực Hạ Long={result.get('halong_verified')}, "
                f"Đang tuyển={result.get('retained_active')}, "
                f"Đã đóng={result.get('purged_expired')}, "
                f"Đã xuất bản={result.get('exported_frontend')} tin."
            )
        except Exception as e:
            logger.error(f"❌ Lỗi trong chu kỳ #{iteration}: {e}", exc_info=True)

        if args.once:
            logger.info("Chế độ --once đã hoàn thành. Thoát chương trình.")
            break

        logger.info(f"⏳ Nghỉ {args.interval}s trước khi bắt đầu chu kỳ tiếp theo...")
        time.sleep(args.interval)
        iteration += 1


if __name__ == "__main__":
    main()
