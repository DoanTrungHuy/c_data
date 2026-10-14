import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = 'backend/cdata.db'
json_path = 'frontend/public/data/jobs.json'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

fixes = [
    {
        "id": "73b4faca-22da-41e8-b168-427ad7b3f99b",
        "company_name": "Công Ty CP Thi Công & Giám Sát Nội Thất",
        "location_province": "Hà Nội",
        "location_district": "Cầu Giấy",
        "location_full": "Hà Nội, Khánh Hòa, TP. Hồ Chí Minh",
        "desc_find": "Doanh nghiệp tại Quảng Ninh. Nơi làm việc: Hà NộiKhánh HòaHồ Chí Minh",
        "desc_replace": "Công Ty CP Thi Công & Giám Sát Nội Thất. Nơi làm việc: Hà Nội, Khánh Hòa, TP. Hồ Chí Minh"
    },
    {
        "id": "eb0745f4-ae35-4939-8021-6fe1b2a26b66",
        "company_name": "Công Ty CP Cơ Điện & Quản Lý Kho Xây Dựng",
        "location_province": "Hà Nội",
        "location_district": "Nam Từ Liêm",
        "location_full": "Hà Nội, TP. Hồ Chí Minh, Đà Nẵng",
        "desc_find": "Doanh nghiệp tại Quảng Ninh. Nơi làm việc: Hà NộiHồ Chí MinhĐà Nẵng",
        "desc_replace": "Công Ty CP Cơ Điện & Quản Lý Kho Xây Dựng. Nơi làm việc: Hà Nội, TP. Hồ Chí Minh, Đà Nẵng"
    },
    {
        "id": "f26b9a3f-7814-4fa2-bb3d-88cf44c83a53",
        "company_name": "Công Ty Kiểm Định & QAQC Nội Thất",
        "location_province": "Hà Nội",
        "location_district": "Thanh Xuân",
        "location_full": "Hà Nội, Khánh Hòa, TP. Hồ Chí Minh",
        "desc_find": "Doanh nghiệp tại Quảng Ninh. Nơi làm việc: Hà NộiKhánh HòaHồ Chí Minh",
        "desc_replace": "Công Ty Kiểm Định & QAQC Nội Thất. Nơi làm việc: Hà Nội, Khánh Hòa, TP. Hồ Chí Minh"
    },
    {
        "id": "67e2b954-66d2-4304-be94-45a3032417d2",
        "company_name": "Tập Đoàn Đầu Tư & Kinh Doanh Bất Động Sản Hạ Long",
        "location_province": "Quảng Ninh",
        "location_district": "Hạ Long",
        "location_full": "Khu đô thị Bãi Cháy, TP. Hạ Long (Quảng Ninh) & Hà Nội, Hưng Yên",
        "desc_find": "Doanh nghiệp tại Quảng Ninh. Nơi làm việc: Hà NộiQuảng NinhHưng Yên",
        "desc_replace": "Tập Đoàn Đầu Tư & Kinh Doanh Bất Động Sản Hạ Long. Nơi làm việc: Khu đô thị Bãi Cháy, TP. Hạ Long (Quảng Ninh) & Hà Nội, Hưng Yên"
    }
]

print("1. Updating SQLite database backend/cdata.db...")
for fix in fixes:
    # Update Job
    cur.execute("""
        UPDATE jobs
        SET company_name = ?,
            location_province = ?,
            location_district = ?,
            location_full = ?,
            description = REPLACE(description, ?, ?)
        WHERE id = ?
    """, (
        fix["company_name"],
        fix["location_province"],
        fix["location_district"],
        fix["location_full"],
        fix["desc_find"],
        fix["desc_replace"],
        fix["id"]
    ))

    # Also check if company record exists or needs update
    cur.execute("SELECT company_id FROM jobs WHERE id = ?", (fix["id"],))
    row = cur.fetchone()
    if row and row[0]:
        comp_id = row[0]
        cur.execute("""
            UPDATE companies
            SET name = ?,
                province = ?
            WHERE id = ?
        """, (fix["company_name"], fix["location_province"], comp_id))

conn.commit()
print("SQLite database updated successfully.")

print("2. Updating frontend/public/data/jobs.json...")
with open(json_path, 'r', encoding='utf-8') as f:
    jobs_json = json.load(f)

updated_json_count = 0
for j in jobs_json:
    for fix in fixes:
        if j["id"] == fix["id"]:
            j["company_name"] = fix["company_name"]
            j["location_province"] = fix["location_province"]
            j["location_district"] = fix["location_district"]
            j["location_full"] = fix["location_full"]
            if fix["desc_find"] in j.get("description", ""):
                j["description"] = j["description"].replace(fix["desc_find"], fix["desc_replace"])
            if j.get("company"):
                j["company"]["name"] = fix["company_name"]
                j["company"]["province"] = fix["location_province"]
            updated_json_count += 1
            print(f"Updated in JSON: [{j['id']}] {j['title']} -> Prov: {j['location_province']}, Full: {j['location_full']}, Comp: {j['company_name']}")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(jobs_json, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_json_count} jobs in {json_path}")
