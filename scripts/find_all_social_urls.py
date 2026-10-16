import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("backend/app/services/social_deep_harvester.py", "r", encoding="utf-8") as f:
    content = f.read()

urls = re.findall(r'"source_url":\s*"([^"]+)"', content)
print(f"Total source_urls in social_deep_harvester.py: {len(urls)}")
for idx, u in enumerate(urls):
    print(f"[{idx+1}] {u}")
