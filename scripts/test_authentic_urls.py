import httpx
import sys

sys.stdout.reconfigure(encoding="utf-8")

urls = {
    "Wyndham Legend": "https://www.wyndhamhalong.com/",
    "FLC": "https://flc.vn/",
    "Vinpearl": "https://vinpearl.com/",
    "Sun World": "https://halong.sunworld.vn/",
    "Muong Thanh": "https://muongthanh.com/",
    "Paradise Vietnam": "https://paradisevietnam.com/",
    "Novotel Accor": "https://all.accor.com/hotel/5807/index.vi.shtml",
    "Vinmec": "https://www.vinmec.com/",
    "BV Bai Chay": "https://benhvienbaichay.vn/",
    "BV Da Khoa Quang Ninh": "https://benhviendakhoaquangninh.vn/",
    "Cang Cai Lan CICT": "https://cict.com.vn/",
    "CALOFIC": "https://calofic.com.vn/",
    "Dong Tau Ha Long": "https://halongshipyard.vn/",
    "Foxconn VN": "https://www.foxconn.com.vn/",
    "TKV Vinacomin": "https://vinacomin.vn/",
    "Nhiet Dien QTP": "https://qtp.com.vn/",
    "FPT Telecom / Jobs": "https://fptjobs.com/",
    "VNPT Tuyendung": "https://tuyendung.vnpt.vn/",
    "Viettel Tuyendung": "https://tuyendung.viettel.vn/",
    "FPT Software": "https://fptsoftware.com/",
    "Vietcombank": "https://tuyendung.vietcombank.com.vn/",
    "Central Retail": "https://centralretailvietnam.com/tuyen-dung/",
    "Van Don Airport": "https://vandonairport.vn/",
    "Yoko Onsen": "https://yokoonsenquanghanh.com.vn/"
}

client = httpx.Client(
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0.0.0"},
    timeout=10.0,
    follow_redirects=True,
    verify=False
)

for name, url in urls.items():
    try:
        r = client.head(url)
        if r.status_code in [403, 405]:
            r = client.get(url, headers={"Range": "bytes=0-1024"})
        print(f"[{r.status_code}] {name}: {url} -> {r.url}")
    except Exception as e:
        print(f"[ERR] {name}: {url} -> {e}")
