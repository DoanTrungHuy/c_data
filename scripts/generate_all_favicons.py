"""
Script Tạo Bộ Nhận Diện Thương Hiệu & Favicon Đơn Giản, Hiện Đại Cho C_Data
- Tạo favicon.ico (đa kích thước 16x16, 32x32, 48x48, 64x64)
- Tạo apple-touch-icon.png (180x180)
- Tạo icon-192.png & icon-512.png cho PWA & mobile
- Tạo favicon.svg đồng bộ cho trình duyệt hiện đại
- Đồng bộ vào cả frontend/public và frontend/src/app để Next.js 14 nhận diện tự động
"""

import math
import os
from PIL import Image, ImageDraw


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def get_gradient_color(deg):
    c_cyan = (56, 189, 248)    # #38BDF8 (Cyan 400 - Top terminal)
    c_blue = (59, 130, 246)    # #3B82F6 (Blue 500 - Body)
    c_indigo = (99, 102, 241)  # #6366F1 (Indigo 500 - Bottom terminal)

    if deg >= 180:
        t = (315 - deg) / 135.0
        return lerp(c_cyan, c_blue, t)
    else:
        t = (180 - deg) / 135.0
        return lerp(c_blue, c_indigo, t)


def render_logo(size=512):
    scale = 4
    dim = size * scale
    img = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Base Squircle (Góc bo tròn phong cách Apple / Modern tech)
    r = int(dim * 0.25)
    # Nền tối sang trọng: Obsidian Slate
    draw.rounded_rectangle([0, 0, dim - 1, dim - 1], radius=r, fill=(11, 15, 25, 255))

    # Viền sáng tinh tế (Subtle outer ring)
    border_w = max(2, int(scale * 1.5))
    draw.rounded_rectangle(
        [border_w // 2, border_w // 2, dim - 1 - border_w // 2, dim - 1 - border_w // 2],
        radius=r - border_w,
        outline=(56, 189, 248, 50),
        width=border_w,
    )

    # 2. Chữ "C" cách điệu (Đường nét tối giản, liền mạch, hiện đại)
    cx, cy = dim // 2, dim // 2
    arc_r = int(dim * 0.275)
    cap_r = int(dim * 0.062)

    for deg_10 in range(450, 3151, 2):
        deg = deg_10 / 10.0
        rad = math.radians(deg)
        x = cx + int(arc_r * math.cos(rad))
        y = cy + int(arc_r * math.sin(rad))
        color = get_gradient_color(deg)
        draw.ellipse([x - cap_r, y - cap_r, x + cap_r, y + cap_r], fill=color + (255,))

    # 3. Điểm hội tụ dữ liệu (Data Core Spark) ở tâm mở của chữ "C"
    dot_cx = cx + int(dim * 0.08)
    dot_cy = cy
    dot_r = int(dim * 0.075)
    draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=(6, 182, 212, 255))

    inner_r = int(dot_r * 0.38)
    draw.ellipse([dot_cx - inner_r, dot_cy - inner_r, dot_cx + inner_r, dot_cy + inner_r], fill=(255, 255, 255, 255))

    return img.resize((size, size), Image.Resampling.LANCZOS)


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    public_dir = os.path.join(root_dir, "frontend", "public")
    app_dir = os.path.join(root_dir, "frontend", "src", "app")

    os.makedirs(public_dir, exist_ok=True)
    os.makedirs(app_dir, exist_ok=True)

    print("🎨 Đang sinh bộ nhận diện biểu tượng C_Data...")

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

    # 4. Xuất file SVG vector tối giản và chuẩn sắc nét
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <defs>
    <linearGradient id="cdata-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F19" />
      <stop offset="100%" stop-color="#172033" />
    </linearGradient>
    <linearGradient id="cdata-arc" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="50%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#6366F1" />
    </linearGradient>
    <linearGradient id="cdata-dot" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#06B6D4" />
    </linearGradient>
  </defs>

  <!-- Squircle Base -->
  <rect width="64" height="64" rx="16" fill="url(#cdata-bg)" />
  <rect x="0.75" y="0.75" width="62.5" height="62.5" rx="15.25" stroke="#38BDF8" stroke-opacity="0.25" stroke-width="1.5" />

  <!-- Minimalist 'C' Shape -->
  <path
    d="M44 20 A 17.5 17.5 0 1 0 44 44"
    stroke="url(#cdata-arc)"
    stroke-width="7.5"
    stroke-linecap="round"
  />

  <!-- High-contrast Data Core Dot -->
  <circle cx="37" cy="32" r="4.5" fill="url(#cdata-dot)" />
  <circle cx="37" cy="32" r="1.6" fill="#FFFFFF" />
</svg>"""

    with open(os.path.join(public_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    with open(os.path.join(app_dir, "icon.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("  ✓ Đã xuất: favicon.svg & icon.svg")
    print("✨ Hoàn tất xuất toàn bộ bộ icon và favicon chuẩn quốc tế!")


if __name__ == "__main__":
    main()
