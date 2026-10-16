"""
Script: generate_brand_icons_and_og.py
Tạo bộ nhận diện thương hiệu VịnhViệc:
- Favicon (.ico đa kích thước 16, 32, 48, 64)
- Icon PNG (.png các kích thước 32, 180, 192, 512)
- Icon SVG (.svg vector siêu nét)
- Open Graph Banner (.png 1200x630) hiển thị khi gửi link qua Zalo, Messenger, Facebook, Telegram...
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

# Thư mục đích
PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public"))
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src", "app"))

def render_logo_base(size=2048):
    """Vẽ logo VịnhViệc chuẩn tại độ phân giải siêu cao 2048x2048"""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # 1. Nền squircle bo góc tròn mềm mại
    corner_radius = int(size * 0.25) # 25% bo góc
    draw.rounded_rectangle(
        [0, 0, size, size],
        radius=corner_radius,
        fill="#09090B"
    )

    # 2. Viền tinh tế
    border_width = int(size * 0.025)
    draw.rounded_rectangle(
        [border_width // 2, border_width // 2, size - border_width // 2, size - border_width // 2],
        radius=corner_radius - border_width,
        outline=(255, 255, 255, 50),
        width=border_width
    )

    # 3. Ký tự Double-V VịnhViệc
    # Trong viewBox 40x40: M8.5 15 L14.5 27 L20 17 L25.5 27 L31.5 15
    scale = size / 40.0
    stroke_w = int(3.3 * scale)

    points = [
        (8.5 * scale, 15.0 * scale),
        (14.5 * scale, 27.0 * scale),
        (20.0 * scale, 17.0 * scale),
        (25.5 * scale, 27.0 * scale),
        (31.5 * scale, 15.0 * scale),
    ]

    # Vẽ từng đoạn line với đầu tròn
    half_w = stroke_w // 2
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        draw.line([p1, p2], fill="#FFFFFF", width=stroke_w)
        # Cap tròn
        draw.ellipse([p1[0] - half_w, p1[1] - half_w, p1[0] + half_w, p1[1] + half_w], fill="#FFFFFF")
        draw.ellipse([p2[0] - half_w, p2[1] - half_w, p2[0] + half_w, p2[1] + half_w], fill="#FFFFFF")

    # 4. Điểm nhấn Node Point (cx=20, cy=11, r=1.8)
    cx = 20.0 * scale
    cy = 10.8 * scale
    r = 1.9 * scale
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FFFFFF")

    return im


def generate_og_banner(logo_im):
    """Tạo banner Open Graph 1200x630px hiển thị khi chia sẻ link"""
    w, h = 1200, 630
    banner = Image.new("RGBA", (w, h), "#09090B")
    draw = ImageDraw.Draw(banner)

    # Grid viền mờ công nghệ cao
    for x in range(0, w, 60):
        draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 8), width=1)
    for y in range(0, h, 60):
        draw.line([(0, y), (w, y)], fill=(255, 255, 255, 8), width=1)

    # Khung viền ngoài
    draw.rectangle([10, 10, w - 10, h - 10], outline=(255, 255, 255, 25), width=2)

    # Chèn Logo VịnhViệc
    logo_size = 180
    logo_resized = logo_im.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    banner.paste(logo_resized, (80, 100), logo_resized)

    # Fonts
    font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 76)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
    font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    font_footer = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)

    # Text: VịnhViệc
    draw.text((290, 110), "VịnhViệc", font=font_title, fill="#FFFFFF")

    # Badge: QUẢNG NINH • ZERO-404
    badge_text = "HẠ LONG & QUẢNG NINH • ZERO-404"
    draw.rounded_rectangle([290, 205, 680, 245], radius=20, fill="#27272A")
    draw.text((310, 213), badge_text, font=font_badge, fill="#A1A1AA")

    # Mô tả chính
    draw.text(
        (80, 310),
        "Cổng Thông Tin Tuyển Dụng & Việc Làm Thông Minh Vùng Vịnh",
        font=font_sub,
        fill="#FFFFFF"
    )

    # 3 Khối tính năng chính (Feature Cards)
    features = [
        ("100% TIN THẬT", "Thẩm định liên kết gốc"),
        ("ĐỐI SOÁT ZERO-404", "Không dẫn trang chết"),
        ("AI SO KHỚP CV", "Chấm điểm độ phù hợp"),
    ]

    card_x = 80
    card_y = 380
    card_w = 320
    card_h = 100

    for i, (title_f, desc_f) in enumerate(features):
        x = card_x + i * (card_w + 25)
        draw.rounded_rectangle([x, card_y, x + card_w, card_y + card_h], radius=16, fill="#18181B", outline=(255, 255, 255, 30), width=1)
        draw.text((x + 20, card_y + 20), title_f, font=font_badge, fill="#FFFFFF")
        draw.text((x + 20, card_y + 55), desc_f, font=font_footer, fill="#A1A1AA")

    # Footer banner
    draw.text((80, 550), "🌐 vinhviec.vn • https://doantrunghuy.github.io/c_data", font=font_footer, fill="#71717A")
    draw.text((850, 550), "Bản quyền © 2026 VịnhViệc", font=font_footer, fill="#71717A")

    return banner.convert("RGB")


def main():
    print("Bắt đầu sinh bộ nhận diện biểu tượng thương hiệu VịnhViệc...")
    logo_base = render_logo_base(2048)

    # Dọn dẹp các file icon trùng lặp trong src/app để tránh xung đột Next.js 500 error
    conflicting_app_files = [
        os.path.join(APP_DIR, "favicon.ico"),
        os.path.join(APP_DIR, "icon.png"),
        os.path.join(APP_DIR, "icon.svg"),
        os.path.join(APP_DIR, "apple-icon.png"),
    ]
    for af in conflicting_app_files:
        if os.path.exists(af):
            try:
                os.remove(af)
                print(f"🧹 Đã xóa file xung đột: {af}")
            except Exception as e:
                print(f"⚠️ Không thể xóa {af}: {e}")

    # 1. Favicon .ico đa kích thước (16, 24, 32, 48, 64) chuẩn Windows & Web
    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
    public_ico = os.path.join(PUBLIC_DIR, "favicon.ico")
    logo_base.save(public_ico, format="ICO", sizes=ico_sizes)
    print(f"✅ Đã tạo multi-res favicon: {public_ico}")

    # 2. Icon PNG cho Web, PWA, Apple Touch Icon
    png_configs = [
        (os.path.join(PUBLIC_DIR, "icon-32.png"), (32, 32)),
        (os.path.join(PUBLIC_DIR, "apple-touch-icon.png"), (180, 180)),
        (os.path.join(PUBLIC_DIR, "icon-192.png"), (192, 192)),
        (os.path.join(PUBLIC_DIR, "icon-512.png"), (512, 512)),
        (os.path.join(PUBLIC_DIR, "icon.png"), (512, 512)),
    ]

    for path, sz in png_configs:
        resized = logo_base.resize(sz, Image.Resampling.LANCZOS)
        resized.save(path, format="PNG")
        print(f"✅ Đã tạo {path} ({sz[0]}x{sz[1]})")

    # 3. SVG icons (chuẩn vector siêu nét cho Chrome, Firefox, Safari)
    svg_content = """<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Obsidian Solid Squircle Base -->
  <rect width="40" height="40" rx="10" fill="#09090B" />
  <rect x="0.5" y="0.5" width="39" height="39" rx="9.5" stroke="rgba(255, 255, 255, 0.25)" stroke-width="1" />

  <!-- The Modern Double-V Monogram (VịnhViệc) -->
  <path
    d="M8.5 15 L14.5 27 L20 17 L25.5 27 L31.5 15"
    stroke="#FFFFFF"
    stroke-width="3.2"
    stroke-linecap="round"
    stroke-linejoin="round"
  />

  <!-- High-Precision Core Node Point -->
  <circle cx="20" cy="10.8" r="1.8" fill="#FFFFFF" />
</svg>"""

    for svg_path in [
        os.path.join(PUBLIC_DIR, "favicon.svg"),
        os.path.join(PUBLIC_DIR, "icon.svg"),
    ]:
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"✅ Đã tạo {svg_path}")

    # 4. Open Graph Banner (1200x630)
    og_banner = generate_og_banner(logo_base)
    og_public = os.path.join(PUBLIC_DIR, "og-image.png")
    og_app = os.path.join(APP_DIR, "opengraph-image.png")

    og_banner.save(og_public, format="PNG", quality=95)
    og_banner.save(og_app, format="PNG", quality=95)
    print(f"✅ Đã tạo Open Graph banner: {og_public} & {og_app}")

    print("🎉 Hoàn tất sinh toàn bộ tài nguyên nhận diện thương hiệu!")

if __name__ == "__main__":
    main()
