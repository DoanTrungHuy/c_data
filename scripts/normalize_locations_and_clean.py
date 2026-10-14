import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect("backend/cdata.db")
c = conn.cursor()

# 1. Deactivate non-IT non-QN jobs that caused confusion
deact_ids = [
    "67e2b954-66d2-4304-be94-45a3032417d2",  # GIÁM ĐỐC KINH DOANH BẤT ĐỘNG SẢN (Hà Nội vs QN)
    "6f1b17b8-380c-4e9e-979f-a2c926847a6f",  # Hải Phòng Sales Executive
    "c08a6489-5994-46f9-8fc0-7f468856de6b",  # AEON Hải Phòng HR
]
for jid in deact_ids:
    c.execute("UPDATE jobs SET is_active = 0 WHERE id = ?", (jid,))
print(f"Deactivated {len(deact_ids)} non-IT out-of-province jobs.")

# 2. Fix 822760ec to Quang Ninh
c.execute("""
    UPDATE jobs 
    SET location_province = 'Quảng Ninh', location_district = 'Quảng Yên'
    WHERE id = '822760ec-d795-4ea3-bee6-3fe66a00b753'
""")
print("Updated 822760ec to Quảng Ninh (KCN Đông Mai, TX. Quảng Yên).")

# 3. Fix Toan Quoc records to authentic provinces
c.execute("UPDATE jobs SET location_province = 'Hà Nội' WHERE id = '17068489-a0d3-4747-b175-11ecfcf7d64a'")
c.execute("UPDATE jobs SET location_province = 'Bình Dương' WHERE id = '63cea88c-eff7-4be9-96cb-53463626a85a'")
c.execute("UPDATE jobs SET location_province = 'Cao Bằng' WHERE id = '0952adbd-9c37-4f2c-8fb8-50013b1f0ff5'")
print("Normalized all 'Toàn quốc' records to exact authentic provinces.")

conn.commit()
conn.close()
print("Database normalization committed successfully.")
