#!/usr/bin/env python3
"""Generate docs/assets/social-preview.png at 1280x640.

GitHub renders the social preview at 2:1 and crops the edges in some link
cards, so the type stays inside a generous margin. The image carries no star
count and no version number, letting it stay accurate as the project moves.

    pip install Pillow && python3 scripts/make_preview.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "social-preview.png"

W, H = 1280, 640
MARGIN = 96

INK = (233, 237, 243)
DIM = (146, 158, 176)
ACCENT = (126, 231, 168)
STRIKE = (233, 122, 122)
BG_TOP = (14, 17, 22)
BG_BOTTOM = (22, 27, 35)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/freefont",
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for directory in FONT_DIRS:
        candidate = Path(directory) / name
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def gradient(width: int, height: int) -> Image.Image:
    base = Image.new("RGB", (1, height))
    pixels = base.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        pixels[0, y] = tuple(
            round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)
        )
    return base.resize((width, height))


def main() -> int:
    img = gradient(W, H)
    draw = ImageDraw.Draw(img)

    title = font("DejaVuSans-Bold.ttf", 92)
    subtitle = font("DejaVuSans.ttf", 33)
    mono = font("DejaVuSansMono.ttf", 27)
    label = font("DejaVuSans-Bold.ttf", 21)

    draw.text((MARGIN, 92), "yesand", font=title, fill=INK)
    draw.text(
        (MARGIN, 206),
        "Rewrite agent instructions into positive form,",
        font=subtitle,
        fill=DIM,
    )
    draw.text(
        (MARGIN, 250),
        "so every line names the action to take.",
        font=subtitle,
        fill=DIM,
    )

    # before / after strip
    card_y, card_h = 340, 132
    card_w = (W - 2 * MARGIN - 40) // 2

    draw.rounded_rectangle(
        [MARGIN, card_y, MARGIN + card_w, card_y + card_h],
        radius=14, fill=(30, 22, 24), outline=(74, 48, 52), width=2,
    )
    draw.text((MARGIN + 26, card_y + 22), "BEFORE", font=label, fill=STRIKE)
    draw.text((MARGIN + 26, card_y + 60), '"Do not use markdown', font=mono, fill=INK)
    draw.text((MARGIN + 26, card_y + 92), ' in your response."', font=mono, fill=INK)

    right = MARGIN + card_w + 40
    draw.rounded_rectangle(
        [right, card_y, right + card_w, card_y + card_h],
        radius=14, fill=(20, 32, 26), outline=(46, 78, 58), width=2,
    )
    draw.text((right + 26, card_y + 22), "AFTER", font=label, fill=ACCENT)
    draw.text((right + 26, card_y + 60), '"Write your response', font=mono, fill=INK)
    draw.text((right + 26, card_y + 92), ' as prose paragraphs."', font=mono, fill=INK)

    footer = font("DejaVuSans.ttf", 25)
    draw.text(
        (MARGIN, 528),
        "An Agent Skill  ·  MIT  ·  ships with a reproducible compliance benchmark",
        font=footer,
        fill=DIM,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT.relative_to(ROOT)} ({img.width}x{img.height}, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
