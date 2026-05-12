"""
Build sample before/after pairs from Wikimedia Commons CC-licensed photos.

Downloads 4 high-quality photos, then generates realistic "after" versions
by applying photographic edits (color grade, contrast, dehaze, vignette).

This script is meant to be run once to populate samples/ for the GitHub
Pages demo. The samples/ folder is checked in (via .gitignore exception)
so users can try the app without uploading their own photos.

Output naming follows the pairing rule in index.html (parseId):
  sample_0001_xxx.jpg          -> ID "0001", shorter name = BEFORE
  sample_0001_xxx_edited.jpg   -> ID "0001", longer name = AFTER

Each pair has a unique 4-digit ID so the pairing is unambiguous.

Run:
  python _samples_build.py
"""
import io
import os
import sys
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "samples")

# ---- Source images (all from Wikimedia Commons, CC BY-SA 4.0 or Public Domain)
# Picked for diverse subjects (landscape, geology, action, atmosphere) and
# high resolution. Each will become a before/after pair after editing.
SOURCES = [
    {
        "id": "0001",
        "slug": "foggy-morning",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/51/A_foggy_winter_morning.jpg",
        "credit": "A foggy winter morning by Soumyajit Nandy, CC BY-SA 4.0",
        "wiki": "https://commons.wikimedia.org/wiki/File:A_foggy_winter_morning.jpg",
        "edit": "dehaze",
    },
    {
        "id": "0002",
        "slug": "prismatic-spring",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Aerial_image_of_Grand_Prismatic_Spring_%28view_from_the_south%29.jpg",
        "credit": "Aerial image of Grand Prismatic Spring by Jim Peaco / NPS, Public Domain (work of US federal government)",
        "wiki": "https://commons.wikimedia.org/wiki/File:Aerial_image_of_Grand_Prismatic_Spring_(view_from_the_south).jpg",
        "edit": "vibrant",
    },
    {
        "id": "0003",
        "slug": "surfer-wave",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Henry_Espinoza_Panta_smashing_a_wave_at_Lobitos.jpg",
        "credit": "Henry Espinoza Panta smashing a wave at Lobitos by Marco Garro, CC BY-SA 4.0",
        "wiki": "https://commons.wikimedia.org/wiki/File:Henry_Espinoza_Panta_smashing_a_wave_at_Lobitos.jpg",
        "edit": "cinematic",
    },
    {
        "id": "0004",
        "slug": "f35-airshow",
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/6d/F-35_Heritage_Flight_Team_performs_in_Bell_Fort_Worth_Alliance_AirShow.jpg",
        "credit": "F-35 Heritage Flight Team by Senior Airman Tristen W. Webb / U.S. Air Force, Public Domain",
        "wiki": "https://commons.wikimedia.org/wiki/File:F-35_Heritage_Flight_Team_performs_in_Bell_Fort_Worth_Alliance_AirShow.jpg",
        "edit": "punchy",
    },
]

MAX_DIM = 2000
QUALITY = 85
USER_AGENT = "image-pair-viewer-samples-builder/1.0 (https://github.com/ViniSouza128/image-pair-viewer)"


def download(url: str) -> Image.Image:
    print(f"  downloading: {url[:90]}...", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    print(f"    -> {len(data)/1024/1024:.1f} MB", flush=True)
    img = Image.open(io.BytesIO(data))
    img.load()
    return img


def resize_to(img: Image.Image, max_dim: int) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dim / max(w, h))
    if scale < 1.0:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    return img


def save_jpeg(img: Image.Image, path: str) -> None:
    img.save(path, format="JPEG", quality=QUALITY, optimize=True, progressive=True)
    size = os.path.getsize(path)
    print(f"    saved: {os.path.basename(path)} ({size/1024:.0f} KB)", flush=True)


# ---- Edits — each one mimics a real photographer's grading style.
# These are intentionally strong so the before/after difference is clear
# in the slider view. The point isn't subtle retouching, it's demoing
# the comparison tool.

def edit_dehaze(img: Image.Image) -> Image.Image:
    """Foggy morning: lift contrast & saturation, warm shadows, add clarity.

    Mimics the 'dehaze' slider in Lightroom — kills the milky veil and
    reveals the underlying scene. Foggy winter shots are the classic
    test case for this slider.
    """
    out = img
    out = ImageEnhance.Contrast(out).enhance(1.55)
    out = ImageEnhance.Color(out).enhance(1.45)
    out = ImageEnhance.Brightness(out).enhance(0.92)
    # Sharpen to recover detail lost in the haze.
    out = out.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=2))
    # Warm tint (slight orange in shadows).
    r, g, b = out.split()
    r = r.point(lambda p: min(255, int(p * 1.05)))
    b = b.point(lambda p: int(p * 0.96))
    return Image.merge("RGB", (r, g, b))


def edit_vibrant(img: Image.Image) -> Image.Image:
    """Grand Prismatic: punch the colors of the thermal pools.

    The pools are naturally colorful but aerial shots often look flat
    because of atmospheric haze. We crank saturation, lift contrast,
    and sharpen.
    """
    out = img
    out = ImageEnhance.Contrast(out).enhance(1.35)
    out = ImageEnhance.Color(out).enhance(1.65)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))
    # Slight cool shift in midtones — makes the blues pop.
    r, g, b = out.split()
    b = b.point(lambda p: min(255, int(p * 1.04)))
    return Image.merge("RGB", (r, g, b))


def edit_cinematic(img: Image.Image) -> Image.Image:
    """Surfer: dramatic teal/orange cinematic grade + vignette.

    The 'teal & orange' look is the most recognizable Hollywood grade:
    shadows toward teal, highlights toward orange. Plus a vignette
    to draw the eye to the surfer.
    """
    out = img
    out = ImageEnhance.Contrast(out).enhance(1.30)
    out = ImageEnhance.Color(out).enhance(1.15)
    # Teal shadows + orange highlights (rough approximation).
    r, g, b = out.split()
    # Lift orange in highlights (R+, B-) and push teal in shadows (B+ in dark areas).
    r = r.point(lambda p: min(255, int(p * 1.06)) if p > 128 else int(p * 0.95))
    b = b.point(lambda p: int(p * 1.08) if p < 128 else int(p * 0.92))
    out = Image.merge("RGB", (r, g, b))
    out = ImageEnhance.Contrast(out).enhance(1.05)
    # Vignette via radial gradient mask.
    out = _vignette(out, strength=0.45)
    return out


def edit_punchy(img: Image.Image) -> Image.Image:
    """F-35: aviation-style punchy edit — sharpen + clarity + sky boost.

    Aviation photographers love punchy contrast, ultra-sharp aircraft
    detail, and a deep blue sky. We push all three.
    """
    out = img
    out = ImageEnhance.Contrast(out).enhance(1.40)
    out = ImageEnhance.Color(out).enhance(1.30)
    out = out.filter(ImageFilter.UnsharpMask(radius=2.0, percent=160, threshold=3))
    # Deepen the blue channel (sky).
    r, g, b = out.split()
    b = b.point(lambda p: min(255, int(p * 1.08)) if p > 100 else p)
    return Image.merge("RGB", (r, g, b))


def _vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Multiply the image by a radial gradient (darker at the corners)."""
    w, h = img.size
    # Build a radial mask: white center, black corners.
    cx, cy = w / 2, h / 2
    max_r = ((cx) ** 2 + (cy) ** 2) ** 0.5
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            d = (dx * dx + dy * dy) ** 0.5
            t = d / max_r  # 0 at center, 1 at corner
            v = max(0.0, 1.0 - strength * (t ** 2))
            px[x, y] = int(v * 255)
    # Pixel-by-pixel is slow on big images — use a smaller mask and resize.
    return _apply_mask_brightness(img, mask)


def _apply_mask_brightness(img: Image.Image, mask: Image.Image) -> Image.Image:
    """Multiply RGB channels by mask/255."""
    r, g, b = img.split()
    r = Image.composite(r, Image.new("L", r.size, 0), mask)
    g = Image.composite(g, Image.new("L", g.size, 0), mask)
    b = Image.composite(b, Image.new("L", b.size, 0), mask)
    return Image.merge("RGB", (r, g, b))


def fast_vignette(img: Image.Image, strength: float = 0.4) -> Image.Image:
    """Faster vignette: build a small radial mask, scale up."""
    w, h = img.size
    # Small mask, then upscale (cheap blur).
    mw, mh = 64, max(1, round(64 * h / w))
    cx, cy = mw / 2, mh / 2
    max_r = ((cx) ** 2 + (cy) ** 2) ** 0.5
    mask = Image.new("L", (mw, mh), 0)
    px = mask.load()
    for y in range(mh):
        for x in range(mw):
            dx = x - cx
            dy = y - cy
            d = (dx * dx + dy * dy) ** 0.5
            t = d / max_r
            v = max(0.0, 1.0 - strength * (t * t))
            px[x, y] = int(v * 255)
    mask = mask.resize((w, h), Image.LANCZOS)
    return _apply_mask_brightness(img, mask)


# Patch: use fast_vignette instead of pixel-by-pixel.
_vignette = fast_vignette


EDITS = {
    "dehaze": edit_dehaze,
    "vibrant": edit_vibrant,
    "cinematic": edit_cinematic,
    "punchy": edit_punchy,
}


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = []

    for src in SOURCES:
        print(f"\n[{src['id']}] {src['slug']}", flush=True)
        try:
            orig = download(src["url"])
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            return 1

        # Resize once, then derive before/after from the same downsized image
        # so they share the exact same pixel geometry.
        base = resize_to(orig, MAX_DIM)

        before_name = f"sample_{src['id']}_{src['slug']}.jpg"
        after_name = f"sample_{src['id']}_{src['slug']}_edited.jpg"
        before_path = os.path.join(OUT_DIR, before_name)
        after_path = os.path.join(OUT_DIR, after_name)

        # Save "before" = unedited downsized original.
        save_jpeg(base, before_path)

        # Save "after" = edited.
        edit_fn = EDITS[src["edit"]]
        edited = edit_fn(base)
        save_jpeg(edited, after_path)

        manifest.append({
            "id": src["id"],
            "slug": src["slug"],
            "before": before_name,
            "after": after_name,
            "edit": src["edit"],
            "credit": src["credit"],
            "wiki": src["wiki"],
        })

    # Write a small JS manifest the front-end can fetch.
    manifest_path = os.path.join(OUT_DIR, "manifest.json")
    import json
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nWrote manifest: {manifest_path}")

    # Total size.
    total = sum(os.path.getsize(os.path.join(OUT_DIR, f))
                for f in os.listdir(OUT_DIR)
                if f.lower().endswith(".jpg"))
    print(f"Total samples size: {total/1024/1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
