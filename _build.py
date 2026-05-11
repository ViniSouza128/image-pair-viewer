"""
Build a self-contained `comparador.html` from a folder of before/after pairs.

This is a CLI alternative to the in-browser "Galeria offline" export. Useful
when you want to process a folder once and produce a shareable HTML file
without opening the browser UI.

Strategy: instead of duplicating the HTML/CSS/JS as a Python template, we
read the live `index.html` and inject a `window.EMBEDDED_DATA = [...]` block
right before the main `<script>` — the same hook the in-browser export uses.
That means: any new feature you add to `index.html` is automatically picked
up by the next build, no Python changes needed.

Pairing logic (mirrors `parseId` in index.html):
  - Pega TODOS os runs de 4+ dígitos consecutivos no nome (sem extensão)
    e junta com '-' como ID composto. Cobre Canon, Sony, Nikon, Fuji,
    Panasonic Lumix, Android (data+hora), Google Pixel, DJI, GoPro.
  - Within a group (same ID), the shortest filename = "before",
    longest = "after". `_v2`/`_v10` markers são descartados (<4 dígitos).

EXIF: data, autor, câmera, lente, ISO, abertura, obturador, focal.
GPS coords (se presentes) NÃO são resolvidos aqui — o reverse-geocoding
acontece em runtime no browser via Nominatim (mesma estratégia do remoto).

Usage:
  python _build.py                        # source = script dir
  python _build.py --src C:\\photos       # explicit source folder
  python _build.py --out gallery.html     # explicit output path
  python _build.py --max-full 2400        # bigger embedded images
"""
import argparse
import base64
import io
import json
import os
import re
import sys

from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS

try:
    from PIL.TiffImagePlugin import IFDRational
except ImportError:
    IFDRational = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTS = (".jpg", ".jpeg", ".png", ".webp")


# --------- File pairing (mirrors parseId/pairFiles in index.html) ---------

ID_DIGITS_RE = re.compile(r"\d{4,}")


def parse_id(filename: str):
    """Extract compound ID from filename: all 4+ digit runs joined by '-'.

    Examples:
        IMG_0093.jpg            -> '0093'
        DSC04321.JPG            -> '04321'
        IMG_20240115_143025.jpg -> '20240115-143025'
        IMG_0093_v2.jpg         -> '0093'   ('2' is <4 digits, ignored)
    """
    stem = os.path.splitext(filename)[0]
    runs = ID_DIGITS_RE.findall(stem)
    if not runs:
        return None
    return "-".join(runs)


def pair_files(filenames):
    """Group files by ID, then shortest name = before, longest = after."""
    groups = {}
    for f in filenames:
        pid = parse_id(f)
        if pid is not None:
            groups.setdefault(pid, []).append(f)

    pairs = []
    for pid in sorted(groups):
        group = groups[pid]
        if len(group) < 2:
            print(f"  [skip] {pid}: only {len(group)} file(s)", file=sys.stderr)
            continue
        sortedg = sorted(group, key=lambda f: (len(f), f.lower()))
        pairs.append((pid, sortedg[0], sortedg[-1]))
    return pairs


# --------- Image processing ---------

def encode_jpeg(img: Image.Image, max_dim: int, quality: int) -> str:
    """Encode `img` as a base64 JPEG data URL, capped at `max_dim` largest side."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dim / max(w, h))
    if scale < 1.0:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


# --------- EXIF ---------

def to_float(v):
    if v is None:
        return None
    if IFDRational is not None and isinstance(v, IFDRational):
        try:
            return float(v)
        except Exception:
            return None
    if isinstance(v, tuple) and len(v) == 2:
        n, d = v
        try:
            return n / d if d else None
        except Exception:
            return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def dms_to_decimal(dms, ref):
    """Convert EXIF DMS (degrees, minutes, seconds) tuple to decimal degrees."""
    try:
        deg = to_float(dms[0]) or 0
        m = to_float(dms[1]) or 0
        s = to_float(dms[2]) or 0
        dec = deg + m / 60 + s / 3600
        if ref in ("S", "W"):
            dec = -dec
        return dec
    except Exception:
        return None


def extract_exif(img: Image.Image) -> dict:
    """Pull a small map of human-readable EXIF fields (matches the runtime parser)."""
    raw = None
    try:
        raw = img._getexif()
    except Exception:
        pass
    if not raw:
        return {}
    exif = {TAGS.get(k, str(k)): v for k, v in raw.items()}

    def g(*keys):
        for k in keys:
            v = exif.get(k)
            if v not in (None, ""):
                return v
        return None

    out: dict[str, str] = {}

    # Camera (Make + Model, dedup if Model already contains Make)
    make = g("Make")
    model = g("Model")
    parts = []
    if make:
        parts.append(str(make).strip())
    if model:
        ms = str(model).strip()
        if make and ms.lower().startswith(str(make).strip().lower()):
            parts = [ms]
        else:
            parts.append(ms)
    if parts:
        out["camera"] = " ".join(parts)

    lens = g("LensModel", "LensMake")
    if lens:
        out["lens"] = str(lens).strip()

    author = g("Artist", "XPAuthor")
    if author:
        # XPAuthor is UTF-16 encoded as bytes
        if isinstance(author, bytes):
            try:
                author = author.decode("utf-16-le").rstrip("\x00")
            except Exception:
                author = author.decode("ascii", errors="ignore")
        out["author"] = str(author).strip()

    d = g("DateTimeOriginal", "DateTime")
    if d:
        s = str(d).strip()
        s = re.sub(r"^(\d{4}):(\d{2}):(\d{2})", r"\1-\2-\3", s)
        out["date"] = s

    iso = g("ISOSpeedRatings", "PhotographicSensitivity", "ISO")
    if isinstance(iso, tuple):
        iso = iso[0] if iso else None
    if iso:
        out["iso"] = f"ISO {iso}"

    aperture = to_float(g("FNumber", "ApertureValue"))
    if aperture and aperture > 0:
        out["aperture"] = f"f/{aperture:.1f}"

    shutter = to_float(g("ExposureTime"))
    if shutter and shutter > 0:
        if shutter >= 1:
            out["shutter"] = f"{shutter:.1f}s"
        else:
            out["shutter"] = f"1/{round(1/shutter)}s"

    focal = to_float(g("FocalLength"))
    if focal and focal > 0:
        out["focal"] = f"{focal:.0f}mm"

    # GPS — apenas coords brutas. O reverse geocoding fica pro runtime
    # (Nominatim) ou pra um fluxo offline separado.
    gps_info = exif.get("GPSInfo")
    if gps_info and isinstance(gps_info, dict):
        gps = {GPSTAGS.get(k, str(k)): v for k, v in gps_info.items()}
        lat = dms_to_decimal(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
        lon = dms_to_decimal(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
        if lat is not None and lon is not None:
            out["lat"] = round(lat, 6)
            out["lon"] = round(lon, 6)

    return out


def fmt_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == "GB":
            if u == "B":
                return f"{int(x)} {u}"
            return f"{x:.1f} {u}"
        x /= 1024
    return f"{x:.1f} TB"


# --------- HTML injection ---------

def inject_embedded_data(html: str, data: list) -> str:
    """Insert `window.EMBEDDED_DATA = ...;` immediately before the main <script>.

    The runtime detects EMBEDDED_DATA and skips the upload screen, going
    straight to `startApp(...)`. This mirrors what the in-browser export
    does (see `buildExportHTML` in index.html).

    We also remove `</script>` substrings inside JSON values just in case
    a filename ever contains it — the HTML parser would otherwise close
    the script early.
    """
    # The "real" main script is the LAST <script> in the file (others
    # may exist inside <!-- comments --> or in CSS). We anchor on the
    # IIFE opener which is unique and stable across versions.
    marker = "(function(){\n'use strict';"
    if marker not in html:
        # Fallback: any <script>\n(function(){
        marker = "<script>"
    json_data = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    json_data = json_data.replace("</script>", "<\\/script>")
    inject = (
        '<script id="embeddedDataInjection">'
        'window.EMBEDDED_DATA=' + json_data + ';'
        '</script>\n'
    )
    # Insert immediately before the <script>...marker line.
    idx = html.find(marker)
    if idx < 0:
        raise RuntimeError("Could not find script injection point in index.html")
    # Walk back to the <script> tag opener so injection lands BEFORE it.
    script_open = html.rfind("<script>", 0, idx)
    if script_open < 0:
        raise RuntimeError("Could not find <script> tag before IIFE marker")
    return html[:script_open] + inject + html[script_open:]


# --------- Build ---------

def main() -> int:
    p = argparse.ArgumentParser(description="Build standalone comparador.html from a photo folder.")
    p.add_argument("--src", default=SCRIPT_DIR, help="Folder with the photos (default: script dir).")
    p.add_argument("--out", default=None, help="Output HTML path (default: <src>/comparador.html).")
    p.add_argument("--template", default=None, help="Path to index.html to use as template (default: <script-dir>/index.html).")
    p.add_argument("--max-full", type=int, default=2200, help="Max dimension for embedded full image.")
    p.add_argument("--quality", type=int, default=85, help="JPEG quality for full images.")
    p.add_argument("--max-thumb", type=int, default=240, help="Max dimension for thumbnail.")
    p.add_argument("--thumb-quality", type=int, default=72, help="JPEG quality for thumbnails.")
    args = p.parse_args()

    src = os.path.abspath(args.src)
    out = args.out or os.path.join(src, "comparador.html")
    template = args.template or os.path.join(SCRIPT_DIR, "index.html")

    if not os.path.isfile(template):
        print(f"ERROR: template not found at {template}", file=sys.stderr)
        return 1

    # Find image files (skip leading underscore = build helpers / templates).
    files = sorted(
        f for f in os.listdir(src)
        if f.lower().endswith(EXTS) and not f.startswith("_")
    )
    pairs = pair_files(files)
    print(f"Found {len(pairs)} pairs in {src}")

    if not pairs:
        print("ERROR: no pairs detected. Check filename pattern.", file=sys.stderr)
        return 1

    data = []
    for i, (pid, before_name, after_name) in enumerate(pairs, 1):
        bpath = os.path.join(src, before_name)
        apath = os.path.join(src, after_name)
        bsize = os.path.getsize(bpath)
        asize = os.path.getsize(apath)
        print(f"  [{i}/{len(pairs)}] {pid}: {before_name} <-> {after_name}", flush=True)

        with Image.open(bpath) as imB, Image.open(apath) as imA:
            imB_t = ImageOps.exif_transpose(imB)
            imA_t = ImageOps.exif_transpose(imA)
            bw, bh = imB_t.size
            aw, ah = imA_t.size
            before_src = encode_jpeg(imB_t, args.max_full, args.quality)
            after_src = encode_jpeg(imA_t, args.max_full, args.quality)
            thumb_src = encode_jpeg(imA_t, args.max_thumb, args.thumb_quality)
            exif = extract_exif(imB)

        data.append({
            "id": pid,
            "b": {"name": before_name, "src": before_src,
                  "w": bw, "h": bh, "size": fmt_size(bsize)},
            "a": {"name": after_name, "src": after_src,
                  "w": aw, "h": ah, "size": fmt_size(asize)},
            "t": thumb_src,
            "exif": exif,
        })

    with open(template, "r", encoding="utf-8") as f:
        html = f.read()
    html = inject_embedded_data(html, data)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    size_mb = os.path.getsize(out) / (1024 * 1024)
    print(f"Wrote {out} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
