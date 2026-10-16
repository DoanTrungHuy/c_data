import requests
import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')
headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://www.careerlink.vn/viec-lam/cntt-phan-mem/19'
r = requests.get(url, headers=headers, timeout=10)
print('status:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a'):
    href = a.get('href', '')
    if '/tim-viec-lam/' in href and href.endswith('.html'):
        print(href, '|', a.get_text(strip=True))
