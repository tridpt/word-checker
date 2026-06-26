"""Tao icon (.ico) cho file .exe va logo (.png) cho README.

Chay: python gen_assets.py
Ket qua nam trong thu muc assets/.
"""

import os

from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
BLUE = (43, 108, 176)
DARK = (30, 60, 90)
GREEN = (47, 133, 90)
WHITE = (255, 255, 255)
GREY = (210, 218, 226)


def _font(size: int, bold: bool = False):
    candidates = (
        ["arialbd.ttf", "Arialbd.ttf"] if bold else ["arial.ttf", "Arial.ttf"]
    )
    for name in candidates:
        for base in (r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu"):
            path = os.path.join(base, name)
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except OSError:
                    pass
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def draw_document(size: int) -> Image.Image:
    """Ve bieu tuong: trang giay co dau check xanh."""
    S = size
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Trang giay
    m = int(S * 0.16)
    page = [m, int(S * 0.08), S - m, S - int(S * 0.08)]
    radius = int(S * 0.04)
    d.rounded_rectangle(page, radius=radius, fill=WHITE, outline=GREY, width=max(1, S // 128))

    # Thanh tieu de mau xanh
    d.rounded_rectangle(
        [page[0], page[1], page[2], page[1] + int(S * 0.10)],
        radius=radius, fill=BLUE,
    )
    d.rectangle(
        [page[0], page[1] + int(S * 0.05), page[2], page[1] + int(S * 0.10)],
        fill=BLUE,
    )

    # Cac dong "van ban"
    line_x0 = page[0] + int(S * 0.07)
    line_x1 = page[2] - int(S * 0.07)
    y = page[1] + int(S * 0.20)
    step = int(S * 0.09)
    for i in range(4):
        x1 = line_x1 if i % 2 == 0 else line_x1 - int(S * 0.12)
        d.rounded_rectangle([line_x0, y, x1, y + max(2, S // 64)],
                            radius=S // 128, fill=GREY)
        y += step

    # Dau check tron mau xanh la
    r = int(S * 0.20)
    cx, cy = S - m - int(S * 0.02), S - int(S * 0.08) - int(S * 0.02)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN, outline=WHITE, width=max(1, S // 64))
    # Dau tick
    w = max(2, S // 32)
    d.line([(cx - r * 0.45, cy), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.5, cy - r * 0.4)],
           fill=WHITE, width=w, joint="curve")
    return img


def make_icon():
    base = draw_document(256)
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save(os.path.join(ASSETS, "icon.ico"), sizes=sizes)
    base.save(os.path.join(ASSETS, "icon.png"))


def make_logo():
    W, H = 900, 240
    img = Image.new("RGBA", (W, H), (244, 246, 248, 255))
    d = ImageDraw.Draw(img)

    icon = draw_document(180).resize((180, 180), Image.LANCZOS)
    img.alpha_composite(icon, (40, 30))

    title_font = _font(64, bold=True)
    sub_font = _font(30)
    d.text((250, 60), "Word Checker", font=title_font, fill=DARK)
    d.text((252, 140), "Kiem tra chinh ta & dinh dang file Word", font=sub_font, fill=BLUE)

    img.convert("RGB").save(os.path.join(ASSETS, "logo.png"))


if __name__ == "__main__":
    os.makedirs(ASSETS, exist_ok=True)
    make_icon()
    make_logo()
    print("Da tao: assets/icon.ico, assets/icon.png, assets/logo.png")
