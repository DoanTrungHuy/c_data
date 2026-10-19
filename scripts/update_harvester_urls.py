import os
import re
import sys
sys.path.insert(0, os.path.abspath("."))
from scripts.repair_facebook_links import FB_MAPPINGS, build_facebook_search_url

with open('backend/app/services/social_deep_harvester.py', 'r', encoding='utf-8') as f:
    content = f.read()

count = 0
for comp, data in FB_MAPPINGS.items():
    search_url = build_facebook_search_url(data['query'])
    escaped_comp = re.escape(comp)
    pattern = rf'("company_name":\s*"{escaped_comp}",[\s\S]*?"source_url":\s*")(https://www\.facebook\.com/[^"]+)(")'
    new_content, n = re.subn(pattern, rf'\g<1>{search_url}\3', content)
    if n > 0:
        content = new_content
        count += n

with open('backend/app/services/social_deep_harvester.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Updated {count} Facebook URLs in social_deep_harvester.py to resilient search URLs!")
