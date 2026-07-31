#!/usr/bin/env python3
"""
Render Open Graph PNGs (1200×630) from scripts/og/template.html using
headless Chrome — no Playwright dependency.

Generates:
  - og-default.png                  (the brand card; no URL params)
  - og/<slug>.png  for each article (per-post card; title/num/date in URL)

Notes on the rendering trick: Chrome's headless --window-size reserves ~98px
vertical for an internal chrome shell, so we render at 1200×728 and crop the
top 1200×630. With --force-device-scale-factor=2 the output is 2400×1260.

Usage:
    python scripts/og/render.py            # default + all articles
    python scripts/og/render.py --default  # default only
    python scripts/og/render.py --post agentic-patterns
"""
from __future__ import annotations
import argparse, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import urlencode

ROOT     = Path(__file__).resolve().parent.parent.parent  # blog/
TEMPLATE = ROOT / "scripts" / "og" / "template.html"
OUT_DIR  = ROOT / "og"
EXT      = "jpg"            # JPEG quality 85 → ~150 KB per card
QUALITY  = 85
DEFAULT_OUT = ROOT / f"og-default.{EXT}"

VIEWPORT = (1200, 630)
SCALE    = 2                # 2× device scale → 2400×1260 source image
WINDOW_OFFSET_Y = 98        # Chrome headless eats ~98px for shell


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME_BIN"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("chrome"),
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("msedge"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    print("ERROR: no Chrome/Edge binary found. Set CHROME_BIN env var.",
          file=sys.stderr)
    sys.exit(1)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_article(path: Path) -> dict | None:
    if path.name == "index.html":
        return None
    html = path.read_text(encoding="utf-8")
    m = re.search(
        r'<h1 class="page-title">(.*?)</h1>', html, re.DOTALL
    )
    if not m: return None
    raw = m.group(1)
    em_m = re.search(r"<em>(.*?)</em>", raw, re.DOTALL)
    if em_m:
        head   = strip_tags(raw[:em_m.start()])
        clause = strip_tags(em_m.group(1))
        head   = re.sub(r"[—–\-]\s*$", "", head).strip()
        clause = re.sub(r"^\s*[—–\-]\s*", "", clause).strip()
        title_param = f"{head}|{clause}"
    else:
        title_param = strip_tags(raw)

    date_m = re.search(
        r"<strong>date:</strong>\s*(\d{2}/\d{2}/\d{4})", html
    )
    date = date_m.group(1) if date_m else ""

    return {"slug": path.stem, "title": title_param, "date": date}


def gather_posts() -> list[dict]:
    posts = []
    for p in sorted(ROOT.glob("*.html")):
        info = parse_article(p)
        if info: posts.append(info)
    def sort_key(d):
        m = re.match(r"(\d{2})/(\d{2})/(\d{4})", d["date"])
        return (m.group(3), m.group(2), m.group(1)) if m else ("0","0","0")
    posts.sort(key=sort_key)
    for i, p in enumerate(posts, start=1):
        p["num"] = i
    return posts


def template_url(params: dict | None = None) -> str:
    base = TEMPLATE.resolve().as_uri()
    if not params: return base
    return f"{base}?{urlencode(params)}"


def crop_top(src: Path, dst: Path, w: int, h: int) -> None:
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: Pillow is required. Install with: pip install Pillow",
              file=sys.stderr)
        sys.exit(1)
    img = Image.open(src)
    out = img.crop((0, 0, w, h))
    if dst.suffix.lower() in {".jpg", ".jpeg"}:
        out = out.convert("RGB")  # drop alpha for JPEG
        out.save(dst, "JPEG", quality=QUALITY,
                 optimize=True, progressive=True)
    elif dst.suffix.lower() == ".webp":
        out.save(dst, "WEBP", quality=QUALITY, method=6)
    else:
        out.save(dst, optimize=True)


def render(chrome: str, url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    win_w = VIEWPORT[0]
    win_h = VIEWPORT[1] + WINDOW_OFFSET_Y

    with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
    ) as tmp:
        tmp_path = Path(tmp.name)

    try:
        subprocess.run([
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            f"--force-device-scale-factor={SCALE}",
            f"--window-size={win_w},{win_h}",
            "--virtual-time-budget=10000",
            f"--screenshot={tmp_path}",
            url,
        ], check=True, capture_output=True)
        # crop top 1200×630 (in source pixels → 2400×1260 in output px)
        crop_top(
            tmp_path, out,
            VIEWPORT[0] * SCALE, VIEWPORT[1] * SCALE,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
    size_kb = out.stat().st_size // 1024
    print(f"  wrote {out.relative_to(ROOT)} ({size_kb} KB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--default", action="store_true",
                    help="Render only the brand default card.")
    ap.add_argument("--post", default=None,
                    help="Render only this slug.")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"Template not found: {TEMPLATE}", file=sys.stderr)
        sys.exit(1)

    chrome = find_chrome()
    posts  = gather_posts()
    if args.post:
        posts = [p for p in posts if p["slug"] == args.post]
        if not posts:
            print(f"No post with slug '{args.post}'", file=sys.stderr)
            sys.exit(1)

    print(f"Rendering at {VIEWPORT[0]}×{VIEWPORT[1]} (×{SCALE}) "
          f"using {chrome}")

    if not args.post:
        render(chrome, template_url(), DEFAULT_OUT)

    if not args.default:
        for post in posts:
            params = {
                "title":  post["title"],
                "num":    str(post["num"]),
                "date":   post["date"],
                "kicker": "Bài viết",
            }
            out = OUT_DIR / f"{post['slug']}.{EXT}"
            render(chrome, template_url(params), out)

    print("Done.")


if __name__ == "__main__":
    main()
