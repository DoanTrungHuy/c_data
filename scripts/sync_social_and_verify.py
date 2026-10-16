import sys
import io
import os
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.append(os.path.abspath("backend"))

from app.core.database import SyncSessionLocal
from app.models.job import Job
from app.services.social_deep_harvester import social_deep_harvester
from app.services.smart_background_harvester import SmartBackgroundHarvester

print("=== 1. KÍCH HOẠT QUÉT SÂU FACEBOOK IT HẠ LONG & QUẢNG NINH ===")
harvest_res = social_deep_harvester.execute_social_deep_harvest(keyword="IT Hạ Long")
print(f"Tổng số việc làm IT quét được từ Facebook/mạng xã hội: {harvest_res.get('total_harvested')}")
print(f"Số việc làm lưu/cập nhật thành công: {harvest_res.get('saved_count')}")

session = SyncSessionLocal()
# Vô hiệu hóa các URL fanpage gốc nếu đã có bài viết trực tiếp /posts/
session.query(Job).filter(Job.source_url == "https://www.facebook.com/NovotelHaLongBay/").update({"is_active": False})
session.commit()
session.close()

print("\n=== 2. CHẠY BỘ ĐỐI SOÁT & PURGE ĐỊNH KỲ (LOẠI BỎ TIN THIẾU JD / HẾT HẠN) ===")
harvester = SmartBackgroundHarvester()
retained, purged = harvester.audit_and_purge_expired_jobs()
print(f"Số tin giữ lại: {retained} | Số tin bị đóng do thiếu JD/hết hạn: {purged}")

print("\n=== 3. XUẤT BẢN DATA SANG FRONTEND / PUBLIC / DATA / JOBS.JSON ===")
exported_count = harvester.export_verified_dataset_to_frontend()
print(f"Đã xuất bản thành công {exported_count} việc làm ra frontend/public/data/jobs.json")

# Kiểm tra lại các tin Facebook trong jobs.json
with open("frontend/public/data/jobs.json", "r", encoding="utf-8") as f:
    jobs = json.load(f)

fb_jobs = [j for j in jobs if "facebook.com" in (j.get("source_url") or "")]
print(f"\n=== TỔNG SỐ VIỆC LÀM FACEBOOK TRONG JOBS.JSON: {len(fb_jobs)} ===")
for i, j in enumerate(fb_jobs):
    print(f"[{i+1}] {j.get('title')} | {j.get('company_name')}")
    print(f"     URL: {j.get('source_url')}")
    print(f"     Mô tả: {len(j.get('description', ''))} ký tự | Yêu cầu (JD): {len(j.get('requirements', ''))} ký tự")
    evidence = j.get("raw_data", {}).get("evidence_proof", {})
    print(f"     Zalo/Hotline: {evidence.get('company_official_hotline')} | Địa chỉ: {evidence.get('verified_workplace')}")
