import sqlite3
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

db_path = "backend/cdata.db"
json_path = "frontend/public/data/jobs.json"

provinces = [
    "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ", "Quảng Ninh", "Bắc Ninh",
    "Bình Dương", "Đồng Nai", "Khánh Hòa", "Thừa Thiên Huế", "Huế", "Thanh Hóa", "Nghệ An",
    "Bà Rịa - Vũng Tàu", "Hưng Yên", "Hải Dương", "Hà Nam", "Nam Định", "Thái Bình", "Vĩnh Phúc",
    "Bắc Giang", "Phú Thọ", "Thái Nguyên", "Lào Cai", "Yên Bái", "Tuyên Quang", "Lạng Sơn",
    "Cao Bằng", "Bắc Kạn", "Hà Giang", "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình",
    "Ninh Bình", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Quảng Nam", "Quảng Ngãi", "Bình Định",
    "Phú Yên", "Ninh Thuận", "Bình Thuận", "Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông",
    "Lâm Đồng", "Bình Phước", "Tây Ninh", "Long An", "Tiền Giang", "Bến Tre", "Trà Vinh",
    "Vĩnh Long", "Đồng Tháp", "An Giang", "Kiên Giang", "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau"
]

def clean_location_string(loc_str: str) -> str:
    if not loc_str:
        return loc_str
    
    # Specific known fixes
    if "Hồ Chí MinhKhánh HòaBà Rịa - Vũng Tàu" in loc_str:
        return "TP. Hồ Chí Minh, Khánh Hòa, Bà Rịa - Vũng Tàu"
    if "Quảng NinhHải PhòngHải Dương" in loc_str:
        return "Quảng Ninh (KCN Đông Mai), Hải Phòng, Hải Dương"
    if "Hải PhòngHà NộiThái Bình" in loc_str:
        return "Hải Phòng, Hà Nội, Thái Bình"
    
    # Generic regex split: insert comma and space between adjacent province names
    result = loc_str
    for p in provinces:
        # If followed immediately by another capital letter without comma/space
        pattern = re.compile(rf"({re.escape(p)})([A-ZÀ-Ỹ])")
        result = pattern.sub(r"\1, \2", result)
        
    return result

print("1. Updating SQLite database...")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, location_full, description FROM jobs")
rows = cur.fetchall()
updated_db_count = 0

for row in rows:
    job_id, loc_full, desc = row
    cleaned_loc = clean_location_string(loc_full or "")
    if cleaned_loc != loc_full:
        cleaned_desc = (desc or "").replace(loc_full, cleaned_loc) if loc_full else desc
        cur.execute(
            "UPDATE jobs SET location_full = ?, description = ? WHERE id = ?",
            (cleaned_loc, cleaned_desc, job_id)
        )
        updated_db_count += 1
        print(f"DB Updated [{job_id}]: '{loc_full}' -> '{cleaned_loc}'")

conn.commit()
conn.close()
print(f"Updated {updated_db_count} jobs in DB.")

print("2. Updating frontend/public/data/jobs.json...")
with open(json_path, "r", encoding="utf-8") as f:
    jobs = json.load(f)

updated_json_count = 0
for j in jobs:
    old_full = j.get("location_full") or ""
    new_full = clean_location_string(old_full)
    if new_full != old_full:
        j["location_full"] = new_full
        if old_full in j.get("description", ""):
            j["description"] = j["description"].replace(old_full, new_full)
        updated_json_count += 1
        print(f"JSON Updated [{j['id']}]: '{old_full}' -> '{new_full}'")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_json_count} jobs in JSON.")
