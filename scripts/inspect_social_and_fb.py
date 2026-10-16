import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os
sys.path.append(os.path.abspath("backend"))

from app.services.social_deep_harvester import SocialDeepHarvester

harvester = SocialDeepHarvester()
fb_items = harvester.harvest_facebook_deep()
print(f"Total harvest_facebook_deep items: {len(fb_items)}")
for i, item in enumerate(fb_items):
    print(f"[{i+1}] {item.get('title')} | {item.get('company_name')} | {item.get('source_url')}")
    print(f"     JD len: {len(item.get('description', ''))} | Req len: {len(item.get('requirements', ''))}")
