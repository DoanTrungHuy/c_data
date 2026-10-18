import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
r = requests.get('https://www.topcv.vn/viec-lam/nhan-vien-it-helpdesk-on-site/2325899.html', headers=headers, timeout=10)
print('Status:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
h1 = soup.select_one('h1')
print('H1:', ascii(h1.text.strip() if h1 else 'None'))
comp = soup.select_one('.company-name, .company-title, a[href*="/cong-ty/"]')
print('Company:', ascii(comp.text.strip() if comp else 'None'))

# Find location and salary
for item in soup.select('.job-detail__info--section-item, .box-item, .general-item'):
    print('Item:', ascii(item.get_text(separator=' ', strip=True)))
