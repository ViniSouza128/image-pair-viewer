"""
Build the Open Graph share image (1200x630) used in WhatsApp / Twitter /
LinkedIn / Facebook / Slack previews when the GitHub Pages URL is pasted.

Output: og-image.jpg (also referenced by index.html via <meta property="og:image">).

DESIGN:
  - 1200x630 (standard OG ratio 1.91:1, supported by all platforms).
  - Left: 510x510 rounded card showing a real before/after split with the
    orange slider line + knob over the center — visually communicates
    "comparison tool" instantly.
  - Right: brand mark (2 dots + name), big 2-line title (second line
    in accent color), subtitle, URL pill at the bottom.

WHY JPEG:
  - WhatsApp aggressively shrinks the thumbnail and prefers small
    payloads. 1200x630 JPEG quality 88 is ~150-180 KB, vs ~500 KB+ as PNG.
  - No transparency needed (the card has a solid dark BG).

FONTS:
  - Title:    Segoe UI Black (heaviest available system font, big visual weight)
  - Brand:    Inter SemiBold
  - Subtitle: Inter Medium
  - URL:      Inter Medium
  - Fallback: default PIL bitmap if the system fonts aren't found
    (only triggers on non-Windows hosts; project is built on Win).

Run:
  python _og_build.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(SCRIPT_DIR, "og-image.jpg")

# Canvas + brand
W, H = 1200, 630
BG = (8, 9, 12)                  # --bg #08090c
BG_CARD = (14, 16, 21)           # --bg-1
FG = (238, 240, 245)             # --fg #eef0f5
FG_2 = (191, 196, 210)           # --fg-2
FG_3 = (125, 131, 149)           # --fg-3
LINE = (38, 42, 54)              # --line
BEFORE = (108, 199, 255)         # --before
ACCENT = (255, 174, 60)          # --after / --accent
ACCENT_BG = (255, 174, 60, 22)   # accent at low alpha for the URL pill

FONT_CANDIDATES = {
    "title": [
        "C:/Windows/Fonts/seguibl.ttf",   # Segoe UI Black
        "C:/Windows/Fonts/segoeuib.ttf",  # Segoe UI Bold (fallback)
        "C:/Windows/Fonts/arialbd.ttf",
    ],
    "semibold": [
        "C:/Windows/Fonts/Inter-SemiBold.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ],
    "medium": [
        "C:/Windows/Fonts/Inter-Medium.ttf",
        "C:/Windows/Fonts/Inter-Regular.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
}


def load_font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    """First existing TTF in the candidate list, at the requested size."""
    for path in FONT_CANDIDATES[kind]:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    # Last resort — PIL's built-in bitmap. Looks awful at big sizes,
    # but at least the script doesn't crash on a fresh dev box.
    print(f"WARN: no TTF found for '{kind}', using default bitmap", file=sys.stderr)
    return ImageFont.load_default()


def square_crop(im: Image.Image, size: int) -> Image.Image:
    """Center-crop to square and resize to `size`x`size`."""
    w, h = im.size
    s = min(w, h)
    cx, cy = w // 2, h // 2
    im = im.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2))
    return im.resize((size, size), Image.LANCZOS)


def rounded_mask(size_w: int, size_h: int, radius: int) -> Image.Image:
    m = Image.new("L", (size_w, size_h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size_w, size_h),
                                        radius=radius, fill=255)
    return m


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # ------- LEFT: rounded card with split before/after -------
    card_size = 510
    card_x = 60
    card_y = (H - card_size) // 2

    # Slight outer glow / shadow under the card — gives the card "lift".
    shadow = Image.new("RGBA", (card_size + 80, card_size + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((40, 40, card_size + 40, card_size + 40),
                         radius=32, fill=(0, 0, 0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=24))
    img.paste(shadow, (card_x - 40, card_y - 30), shadow)

    # Card background (slightly lighter than main BG for visual separation).
    bg_panel = Image.new("RGBA", (card_size, card_size), BG_CARD + (255,))
    img.paste(bg_panel, (card_x, card_y), rounded_mask(card_size, card_size, 28))

    # Real before/after halves. We pick foggy-morning because it has the
    # most dramatic visible difference (warm dehaze) and the silhouettes
    # read well at thumb scale.
    samples_dir = os.path.join(SCRIPT_DIR, "samples")
    before_path = os.path.join(samples_dir, "sample_0001_foggy-morning.jpg")
    after_path = os.path.join(samples_dir, "sample_0001_foggy-morning_edited.jpg")
    if not (os.path.isfile(before_path) and os.path.isfile(after_path)):
        raise RuntimeError(
            "Samples not found. Run `python _samples_build.py` first."
        )

    inner_pad = 14  # breathing room between card edge and photo
    inner_size = card_size - inner_pad * 2

    with Image.open(before_path) as bi, Image.open(after_path) as ai:
        before_sq = square_crop(bi, inner_size)
        after_sq = square_crop(ai, inner_size)

    split = Image.new("RGB", (inner_size, inner_size))
    half = inner_size // 2
    split.paste(before_sq.crop((0, 0, half, inner_size)), (0, 0))
    split.paste(after_sq.crop((half, 0, inner_size, inner_size)), (half, 0))

    # Round the inner photo corners slightly less than the card (visual nesting).
    inner_mask = rounded_mask(inner_size, inner_size, 16)
    img.paste(split, (card_x + inner_pad, card_y + inner_pad), inner_mask)

    # Slider: thin vertical line + center knob (mirrors the live UI).
    slider_x = card_x + inner_pad + half
    line_top = card_y + inner_pad
    line_bot = card_y + inner_pad + inner_size
    draw.rectangle((slider_x - 2, line_top, slider_x + 2, line_bot),
                   fill=ACCENT + (255,))
    knob_r = 30
    knob_y = card_y + card_size // 2
    # White ring → orange ring → dark center (matches live app handle).
    draw.ellipse((slider_x - knob_r, knob_y - knob_r,
                  slider_x + knob_r, knob_y + knob_r),
                 fill=BG_CARD + (255,), outline=ACCENT + (255,), width=5)
    inner_knob = 9
    draw.ellipse((slider_x - inner_knob, knob_y - inner_knob,
                  slider_x + inner_knob, knob_y + inner_knob),
                 fill=ACCENT + (255,))

    # Tiny "Antes" / "Depois" badges on each half — bottom corners.
    badge_font = load_font("semibold", 16)
    pad = 10
    for side, label, color, anchor in [
        ("left", "ANTES", BEFORE, (card_x + inner_pad + 14, card_y + card_size - inner_pad - 32)),
        ("right", "DEPOIS", ACCENT, (card_x + card_size - inner_pad - 14, card_y + card_size - inner_pad - 32)),
    ]:
        tw = draw.textlength(label, font=badge_font)
        bw = int(tw + 22)
        bx = anchor[0] if side == "left" else anchor[0] - bw
        by = anchor[1]
        draw.rounded_rectangle((bx, by, bx + bw, by + 26),
                               radius=13, fill=(0, 0, 0, 130))
        draw.text((bx + 11, by + 4), label, font=badge_font,
                  fill=color + (255,))

    # ------- RIGHT: brand + title + subtitle + URL pill -------
    rx = 620           # left edge of the text column
    rmax = W - 50      # right edge of canvas with breathing room
    text_w = rmax - rx

    # Brand row (logo + name) at the top.
    brand_y = card_y + 8
    dot_r = 11
    draw.ellipse((rx, brand_y, rx + dot_r * 2, brand_y + dot_r * 2),
                 fill=BEFORE + (255,))
    draw.ellipse((rx + dot_r * 2 - 6, brand_y, rx + dot_r * 4 - 6, brand_y + dot_r * 2),
                 fill=ACCENT + (255,))
    brand_font = load_font("semibold", 20)
    draw.text((rx + dot_r * 4 + 8, brand_y + 1),
              "IMAGE-PAIR-VIEWER", font=brand_font,
              fill=FG_2 + (255,))

    # Big title — two lines, 2nd line in accent color.
    title_font = load_font("title", 78)
    line1 = "Compare any"
    line2 = "before & after."
    title_y = brand_y + 70
    draw.text((rx, title_y), line1, font=title_font, fill=FG + (255,))
    # Measure line height via bbox for tight vertical packing.
    bbox1 = draw.textbbox((rx, title_y), line1, font=title_font)
    line_h = bbox1[3] - bbox1[1]
    draw.text((rx, title_y + int(line_h * 1.05)),
              line2, font=title_font, fill=ACCENT + (255,))

    # Subtitle — two lines of body copy.
    sub_font = load_font("medium", 24)
    sub_y = title_y + int(line_h * 2.2) + 24
    subtitle_lines = [
        "Slider, side-by-side & solo modes — EXIF, GPS, 8",
        "languages. Zero upload, runs in your browser.",
    ]
    for i, ln in enumerate(subtitle_lines):
        draw.text((rx, sub_y + i * 34), ln, font=sub_font,
                  fill=FG_2 + (255,))

    # URL pill at the bottom — accent-tinted background.
    url = "vinisouza128.github.io/image-pair-viewer"
    url_font = load_font("medium", 22)
    url_w = draw.textlength(url, font=url_font)
    pill_pad_x = 20
    pill_pad_y = 10
    pill_w = int(url_w + pill_pad_x * 2)
    pill_h = 44
    pill_x = rx
    pill_y = card_y + card_size - pill_h + 8
    draw.rounded_rectangle((pill_x, pill_y, pill_x + pill_w, pill_y + pill_h),
                           radius=pill_h // 2, fill=ACCENT_BG,
                           outline=ACCENT + (90,), width=1)
    draw.text((pill_x + pill_pad_x, pill_y + pill_pad_y - 2),
              url, font=url_font, fill=ACCENT + (255,))

    return img


def main() -> int:
    img = build()
    # JPEG quality 88 — visually lossless at this size, ~150-180 KB.
    img.save(OUT_PATH, format="JPEG", quality=88, optimize=True, progressive=True)
    sz = os.path.getsize(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({sz/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
