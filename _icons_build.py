"""
Build PWA icons from the same 2-dot design used in the favicon.

Output: icons/icon-{192,512,180}.png plus icons/icon-maskable-512.png.

Why a builder script:
  - The favicon is a tiny inline SVG that doesn't scale to a crisp PNG
    without antialiasing artifacts. Rendering with PIL at high resolution
    + downscaling (LANCZOS) gives clean edges at all PWA sizes.
  - Maskable icons need a 80% safe zone — the OS may crop a 192x192 icon
    into a circle/squircle on Android. We generate a dedicated variant
    with the artwork shrunk to fit that safe zone.

Design (mirrors the inline SVG favicon and the .upload-logo dots):
  - Two overlapping circles, blue-cyan + amber-orange
  - Same x-positions as the 32x32 viewBox favicon: cx=9 and cx=23, r=8
  - Solid dark background matches the app's --bg (#08090c)

Run:
  python _icons_build.py
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "icons")

# Brand colors — match index.html :root vars.
BG = (8, 9, 12, 255)            # --bg #08090c
BEFORE = (108, 199, 255, 255)   # --before #6cc7ff (blue)
AFTER = (255, 174, 60, 255)     # --after  #ffae3c (orange)


def render_icon(size: int, *, maskable: bool = False, transparent_bg: bool = False) -> Image.Image:
    """Render the 2-dot logo at `size`×`size`.

    We render 4x larger then downsample for crisp antialiased edges.
    The original favicon viewBox is 32×32 with circles at (9,16,r=8) and
    (23,16,r=8). We preserve those proportions but scale the overall
    artwork:

      - maskable=False: artwork fills ~95% of the canvas (1px breathing room)
      - maskable=True:  artwork shrinks to ~70% so it survives mask cropping
                        on Android adaptive icons (80% safe zone spec).
    """
    SS = 4  # supersample factor
    W = size * SS
    canvas = Image.new("RGBA", (W, W), (0, 0, 0, 0) if transparent_bg else BG)
    d = ImageDraw.Draw(canvas)

    # Original favicon: 32-wide canvas, circles at cx=9, cx=23, r=8.
    # That means the artwork "bounding box" spans x=1..31 = 30 of 32 units.
    # We'll scale that bounding box to either ~95% (regular) or ~70% (maskable).
    fill_ratio = 0.70 if maskable else 0.95
    bbox_w = W * fill_ratio
    unit = bbox_w / 30.0  # how many pixels per "viewBox unit"
    center_y = W / 2
    # Cx in viewBox is 9 and 23 — distance from the LEFT edge of the bbox.
    # The bbox starts at (W - bbox_w) / 2 from the canvas left.
    bbox_x0 = (W - bbox_w) / 2
    # Inside the bbox, the circle's leftmost point is at x=1 of the 32-wide
    # viewBox (cx=9, r=8 -> leftmost=1). So shift by 1 unit to align.
    cx1 = bbox_x0 + (9 - 1) * unit
    cx2 = bbox_x0 + (23 - 1) * unit
    r = 8 * unit

    # Blue circle (before).
    d.ellipse((cx1 - r, center_y - r, cx1 + r, center_y + r), fill=BEFORE)
    # Orange circle (after) — drawn second so its color wins on overlap.
    # In the CSS this is `mix-blend-mode:screen`; here we use solid for
    # crisper edges (PNG doesn't carry blend modes anyway).
    d.ellipse((cx2 - r, center_y - r, cx2 + r, center_y + r), fill=AFTER)

    # Downsample for antialiasing.
    return canvas.resize((size, size), Image.LANCZOS)


def save(img: Image.Image, name: str) -> None:
    path = os.path.join(OUT_DIR, name)
    img.save(path, format="PNG", optimize=True)
    sz = os.path.getsize(path)
    print(f"  saved: {name} ({sz/1024:.1f} KB)", flush=True)


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)

    print("Rendering PWA icons:")
    # Required by the manifest spec — minimum recommended sizes for installable PWAs.
    save(render_icon(192), "icon-192.png")
    save(render_icon(512), "icon-512.png")
    # Apple touch icon — iOS uses this when adding to home screen.
    save(render_icon(180), "icon-180.png")
    # Maskable for Android adaptive icons — the OS may crop into a shape
    # (circle, squircle, rounded square). Artwork is centered with margin
    # so it survives the crop.
    save(render_icon(512, maskable=True), "icon-maskable-512.png")
    # Monochrome alternative for browser shortcuts (rarely used, optional).
    # Also useful as a square favicon fallback.
    save(render_icon(32), "icon-32.png")

    print(f"\nWrote {len(os.listdir(OUT_DIR))} files to {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
