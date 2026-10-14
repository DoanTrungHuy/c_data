"""
Script Tạo Bộ Nhận Diện Thương Hiệu & Favicon Đơn Giản, Đẳng Cấp Cho C_Data
- Thiết kế: Cyber Wave C + Emerald Astroid Beacon Sparkle
- Tạo favicon.ico (đa kích thước 16x16, 32x32, 48x48, 64x64)
- Tạo apple-touch-icon.png (180x180) & apple-icon.png
- Tạo icon-192.png & icon-512.png cho PWA & mobile
- Tạo favicon.svg & icon.svg đồng bộ cho trình duyệt hiện đại
- Đồng bộ vào cả frontend/public và frontend/src/app để Next.js 14 nhận diện tự động
"""

import math
import os
from PIL import Image, ImageDraw


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def render_logo(size=512):
    scale = 8
    dim = 64 * scale
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base Squircle (Obsidian Midnight Slate)
    rx = int(16 * scale)
    draw.rounded_rectangle([0, 0, dim - 1, dim - 1], radius=rx, fill=(10, 15, 26, 255))

    # Viền sáng tinh tế (Cyber Cyan Glow Border)
    bw = max(2, int(1.2 * scale))
    draw.rounded_rectangle(
        [bw // 2, bw // 2, dim - 1 - bw // 2, dim - 1 - bw // 2],
        radius=rx - bw,
        outline=(56, 189, 248, 70),
        width=bw,
    )

    # 2. Chữ "C" khí động học (Cyber Wave C Monogram)
    cx, cy = int(30.5 * scale), int(32 * scale)
    r = int(17.2 * scale)
    cap_r = int(3.6 * scale)

    c_cyan = (56, 189, 248)    # #38BDF8 (Sky 400 - Top terminal)
    c_blue = (37, 99, 235)     # #2563EB (Blue 600 - Body)
    c_violet = (139, 92, 246)  # #8B5CF6 (Purple 500 - Bottom terminal)

    # 43 deg to 317 deg
    for deg_10 in range(430, 3171, 2):
        deg = deg_10 / 10.0
        rad = math.radians(deg)
        x = cx + int(r * math.cos(rad))
        y = cy + int(r * math.sin(rad))
        if deg >= 180:
            t = (317 - deg) / 137.0
            col = lerp(c_cyan, c_blue, t)
        else:
            t = (180 - deg) / 137.0
            col = lerp(c_blue, c_violet, t)
        draw.ellipse([x - cap_r, y - cap_r, x + cap_r, y + cap_r], fill=col + (255,))

    # 3. Ngọn Hải Đăng Di Sản / Astroid Star Sparkle tại (39.5, 32)
    scx, scy = int(39.5 * scale), int(32 * scale)
    sw = int(6.2 * scale)
    sh = int(8.2 * scale)

    # Generate points for astroid sparkle curve
    star_pts = []
    n_steps = 32
    # Top to Right
    for i in range(n_steps):
        t = i / float(n_steps)
        x = scx + sw * (t**2.2)
        y = scy - sh * ((1 - t)**2.2)
        star_pts.append((int(x), int(y)))
    # Right to Bottom
    for i in range(n_steps):
        t = i / float(n_steps)
        x = scx + sw * ((1 - t)**2.2)
        y = scy + sh * (t**2.2)
        star_pts.append((int(x), int(y)))
    # Bottom to Left
    for i in range(n_steps):
        t = i / float(n_steps)
        x = scx - sw * (t**2.2)
        y = scy + sh * ((1 - t)**2.2)
        star_pts.append((int(x), int(y)))
    # Left to Top
    for i in range(n_steps):
        t = i / float(n_steps)
        x = scx - sw * ((1 - t)**2.2)
        y = scy - sh * (t**2.2)
        star_pts.append((int(x), int(y)))

    # Fill emerald spark (#10B981)
    draw.polygon(star_pts, fill=(16, 185, 129, 255))

    # White high-contrast core
    spark_core = int(1.8 * scale)
    draw.ellipse(
        [scx - spark_core, scy - spark_core, scx + spark_core, scy + spark_core],
        fill=(255, 255, 255, 255),
    )

    return img.resize((size, size), Image.Resampling.LANCZOS)


def get_svg_content():
    return """<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cdata-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0A0F1A" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
    <linearGradient id="cdata-arc" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#8B5CF6" />
    </linearGradient>
    <linearGradient id="cdata-spark" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399" />
      <stop offset="50%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
    <linearGradient id="cdata-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.4" />
      <stop offset="100%" stop-color="#8B5CF6" stop-opacity="0.15" />
    </linearGradient>
  </defs>

  <!-- Obsidian Squircle Base -->
  <rect width="64" height="64" rx="16" fill="url(#cdata-bg)" />
  <rect x="0.75" y="0.75" width="62.5" height="62.5" rx="15.25" stroke="url(#cdata-border)" stroke-width="1.5" />

  <!-- The Cyber Wave C Monogram -->
  <path
    d="M43 20 A 17 17 0 1 0 43 44"
    stroke="url(#cdata-arc)"
    stroke-width="7.2"
    stroke-linecap="round"
  />

  <!-- The Emerald Astroid Beacon Sparkle -->
  <path
    d="M39.5 24 Q39.5 32 45.7 32 Q39.5 32 39.5 40 Q39.5 32 33.3 32 Q39.5 32 39.5 24 Z"
    fill="url(#cdata-spark)"
  />

  <!-- High-Precision Core Node -->
  <circle cx="39.5" cy="32" r="1.8" fill="#FFFFFF" />
</svg>"""


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    public_dir = os.path.join(root_dir, "frontend", "public")
    app_dir = os.path.join(root_dir, "frontend", "src", "app")

    os.makedirs(public_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)

    print("🎨 Đang sinh bộ nhận diện biểu tượng C_Data (Cyber Wave C + Emerald Beacon)...")

    # Tạo các kích thước ảnh tiêu chuẩn
    img_512 = render_logo(512)
    img_192 = render_logo(192)
    img_180 = render_logo(180)
    img_64 = render_logo(64)
    img_48 = render_logo(48)
    img_32 = render_logo(32)
    img_16 = render_logo(16)

    # 1. Lưu các file PNG trong frontend/public
    img_512.save(os.path.join(public_dir, "icon-512.png"), format="PNG")
    img_192.save(os.path.join(public_dir, "icon-192.png"), format="PNG")
    img_180.save(os.path.join(public_dir, "apple-touch-icon.png"), format="PNG")
    print("  ✓ Đã xuất: icon-512.png, icon-192.png, apple-touch-icon.png")

    # 2. Lưu favicon.ico (multi-size: 16, 32, 48, 64)
    ico_path_public = os.path.join(public_dir, "favicon.ico")
    img_64.save(
        ico_path_public,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
        append_images=[img_48, img_32, img_16],
    )
    print("  ✓ Đã xuất: frontend/public/favicon.ico (16x16, 32x32, 48x48, 64x64)")

    # 3. Đồng bộ vào frontend/src/app cho Next.js 14 App Router tự động gán thẻ <link>
    ico_path_app = os.path.join(app_dir, "favicon.ico")
    img_64.save(
        ico_path_app,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
        append_images=[img_48, img_32, img_16],
    )
    img_32.save(os.path.join(app_dir, "icon.png"), format="PNG")
    img_180.save(os.path.join(app_dir, "apple-icon.png"), format="PNG")
    print("  ✓ Đã xuất vào Next.js App Router: app/favicon.ico, app/icon.png, app/apple-icon.png")

    # 4. Xuất file SVG vector
    svg = get_svg_content()
    with open(os.path.join(public_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    with open(os.path.join(public_dir, "icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    with open(os.path.join(app_dir, "icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("  ✓ Đã xuất: public/favicon.svg, public/icon.svg, app/icon.svg")
    print("✨ Hoàn tất xuất toàn bộ bộ icon và favicon chuẩn quốc tế!")


if __name__ == "__main__":
    main()
