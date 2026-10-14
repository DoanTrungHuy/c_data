import urllib.request
import urllib.parse
import json

queries = ['kế toán', 'lái xe', 'phục vụ', 'bác sĩ', 'xây dựng', 'bán hàng', 'du lịch', 'giao dịch viên', 'than', 'spa', 'it']

for q in queries:
    url = 'http://127.0.0.1:8000/api/v1/jobs?q=' + urllib.parse.quote(q)
    try:
        req = urllib.request.urlopen(url)
        data = json.loads(req.read().decode('utf-8'))
        t = data.get('total', 0)
        print(f"=== Query: [{q}] -> Total: {t} ===")
        for item in data.get('items', [])[:3]:
            title = item.get('title')
            comp = item.get('company_name')
            cat = item.get('category')
            print(f"   - {title} ({comp}) | Cat: {cat}")
    except Exception as e:
        print(f"Query [{q}] failed: {e}")
