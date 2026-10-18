import json, requests, urllib3, time
from bs4 import BeautifulSoup
urllib3.disable_warnings()

with open('frontend/public/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = json.load(f)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}

results = {'matched': [], 'mismatched': [], 'broken': [], 'synthetic': []}

for j in jobs:
    jid = j.get('id', '')
    title = j.get('title', '')
    url = j.get('apply_url') or j.get('source_url', '')
    comp = j.get('company_name', '')
    src = j.get('source_platform') or j.get('source_name', '')
    
    if jid.startswith('local_ent_') or 'Doanh Nghiệp Trọng Điểm' in src:
        results['synthetic'].append({'id': jid, 'title': title, 'url': url, 'company': comp, 'reason': 'Synthetic local enterprise profile'})
        continue
    
    if 'facebook.com' in url or 'fptjobs.com' in url:
        try:
            r = requests.get(url, headers=headers, timeout=5, verify=False)
            if r.status_code != 200:
                results['broken'].append({'id': jid, 'title': title, 'url': url, 'status': r.status_code})
            else:
                if title.lower() in r.text.lower():
                    results['matched'].append({'id': jid, 'title': title, 'url': url, 'company': comp})
                else:
                    results['mismatched'].append({'id': jid, 'title': title, 'url': url, 'reason': 'Page does not contain job title'})
        except Exception as e:
            results['broken'].append({'id': jid, 'title': title, 'url': url, 'error': str(e)})
        time.sleep(0.5)
        continue

    try:
        r = requests.get(url, headers=headers, timeout=5, verify=False)
        if r.status_code != 200:
            results['broken'].append({'id': jid, 'title': title, 'url': url, 'status': r.status_code})
            time.sleep(0.5)
            continue
        soup = BeautifulSoup(r.text, 'html.parser')
        h1 = soup.select_one('h1')
        h1_text = h1.get_text(strip=True) if h1 else ''
        p_title = (soup.title.string or '') if soup.title else ''
        
        words = [w for w in title.lower().split() if len(w) > 3]
        matched_words = [w for w in words if w in (h1_text + ' ' + p_title + ' ' + r.text[:3000]).lower()]
        ratio = len(matched_words) / max(len(words), 1)
        if ratio >= 0.5:
            results['matched'].append({'id': jid, 'title': title, 'url': url, 'company': comp, 'h1': h1_text, 'ratio': ratio})
        else:
            results['mismatched'].append({'id': jid, 'title': title, 'url': url, 'h1': h1_text, 'ratio': ratio})
    except Exception as e:
        results['broken'].append({'id': jid, 'title': title, 'url': url, 'error': str(e)})
    time.sleep(0.5)

print(f"TOTAL AUDIT: {len(jobs)} jobs")
print(f"  100% REAL MATCHED : {len(results['matched'])}")
print(f"  SYNTHETIC/MOCK    : {len(results['synthetic'])}")
print(f"  BROKEN URL (404)  : {len(results['broken'])}")
print(f"  MISMATCHED TITLE  : {len(results['mismatched'])}")

with open('audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
