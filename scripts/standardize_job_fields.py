"""
Standardize job_type, experience_level, and remote fields in frontend/public/data/jobs.json.
"""

import json
import os
import sys
import io

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "data", "jobs.json")

def standardize():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for j in data:
        txt = f"{j.get('title', '')} {j.get('description', '')} {j.get('requirements', '')}".lower()
        if "remote" in txt or "từ xa" in txt:
            j["job_type"] = "Từ xa (Remote)"
        elif "thực tập" in txt or "intern" in txt:
            j["job_type"] = "Thực tập sinh"
        elif "part-time" in txt or "bán thời gian" in txt:
            j["job_type"] = "Bán thời gian"
        else:
            j["job_type"] = "Toàn thời gian"

        if not j.get("experience_level"):
            t_low = j.get("title", "").lower()
            if "fresher" in t_low or "thực tập" in t_low:
                j["experience_level"] = "Fresher (Dưới 1 năm)"
            elif "junior" in t_low:
                j["experience_level"] = "Junior (1 - 2 năm)"
            elif "senior" in t_low or "chuyên gia" in t_low or "expert" in t_low or "trưởng" in t_low or "lead" in t_low:
                j["experience_level"] = "Senior (3 - 5 năm)"
            else:
                j["experience_level"] = "Middle (1 - 3 năm)"

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Đã chuẩn hóa thành công job_type và experience_level cho {len(data)} tin tuyển dụng!")

if __name__ == "__main__":
    standardize()
