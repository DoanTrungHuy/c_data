import urllib.request
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def check_url(url):
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        return resp.status, len(resp.read())
    except Exception as e:
        return f"ERR: {e}", 0

print("1. Kiểm tra Trang chủ /")
html = urllib.request.urlopen("http://localhost:3000/").read().decode("utf-8")
css_matches = re.findall(r'href="(/_next/static/css/[^"]+)"', html)
script_matches = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)

print(f"CSS ({len(css_matches)} files):")
for c in css_matches:
    status, size = check_url("http://localhost:3000" + c)
    print(f"  • {c} -> {status} (size: {size} bytes)")

print(f"JS Scripts ({len(script_matches)} files):")
for s in script_matches[:5]:
    status, size = check_url("http://localhost:3000" + s)
    print(f"  • {s} -> {status} (size: {size} bytes)")

print("\n2. Kiểm tra Trang /jobs")
status, size = check_url("http://localhost:3000/jobs")
print(f"  • /jobs -> {status} (size: {size} bytes)")

print("\n3. Kiểm tra Trang /sources")
status, size = check_url("http://localhost:3000/sources")
print(f"  • /sources -> {status} (size: {size} bytes)")
