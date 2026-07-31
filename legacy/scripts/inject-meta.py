#!/usr/bin/env python3
"""
Inject SEO meta + Open Graph + Twitter Card tags into every HTML page.

Reads existing fields from each page:
  - <title>...</title>                      → og:title / twitter:title
  - <p class="page-desc">...</p>            → description / og:description (articles)
  - <meta name="description" ...>           → description / og:description (index)
  - "<strong>date:</strong> DD/MM/YYYY"     → article:published_time

Writes a marked block right after <title>, so re-running this script
replaces the previous block instead of duplicating it.

Usage:
    python scripts/inject-meta.py             # all pages (index + every article)
    python scripts/inject-meta.py --index     # index.html only
    python scripts/inject-meta.py --post foo  # one article (slug = foo)
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SITE_URL     = "https://duthaho.dev"
SITE_NAME    = "Nhật ký dev"
SITE_LOCALE  = "vi_VN"
SITE_LANG    = "vi"
SITE_TAGLINE = "Suy nghĩ sau giờ làm"
AUTHOR       = "duthaho"
AUTHOR_URL   = "https://about.duthaho.dev"
OG_DEFAULT   = "og-default.jpg"           # site root
OG_PER_POST  = "og/{slug}.jpg"            # falls back to default if missing

META_START   = "<!-- SEO:auto-meta -->"
META_END     = "<!-- /SEO:auto-meta -->"
JSONLD_START = "<!-- SEO:auto-jsonld -->"
JSONLD_END   = "<!-- /SEO:auto-jsonld -->"

# Kept for backwards compatibility with helper functions below.
START = META_START
END   = META_END

BLOG_DIR = Path(__file__).resolve().parent.parent


def strip_tags(s: str) -> str:
    """Strip HTML tags, collapse whitespace, trim."""
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def html_attr_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace('"', "&quot;")
             .replace("<", "&lt;")
             .replace(">", "&gt;"))


def vn_date_to_iso(d: str) -> str | None:
    """Convert DD/MM/YYYY → YYYY-MM-DD."""
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", d.strip())
    if not m: return None
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def extract_title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    return strip_tags(m.group(1)) if m else ""


def extract_description(html: str, is_index: bool) -> str:
    if is_index:
        m = re.search(
            r'<meta\s+name="description"\s+content="([^"]+)"',
            html
        )
        return m.group(1).strip() if m else ""
    m = re.search(
        r'<p class="page-desc">(.*?)</p>', html, re.DOTALL
    )
    return strip_tags(m.group(1)) if m else ""


def extract_date(html: str) -> str | None:
    m = re.search(
        r"<strong>date:</strong>\s*(\d{2}/\d{2}/\d{4})", html
    )
    return vn_date_to_iso(m.group(1)) if m else None


def og_image_for(slug: str, is_index: bool) -> str:
    """Use per-post image if it's been rendered, else fall back to default."""
    if not is_index:
        per_post = BLOG_DIR / OG_PER_POST.format(slug=slug)
        if per_post.exists():
            return f"{SITE_URL}/{OG_PER_POST.format(slug=slug)}"
    return f"{SITE_URL}/{OG_DEFAULT}"


def build_meta_block(*, page_url: str, title: str, desc: str,
                     is_index: bool, published: str | None,
                     og_image: str) -> str:
    title_e  = html_attr_escape(title)
    desc_e   = html_attr_escape(desc)
    site_e   = html_attr_escape(SITE_NAME)
    og_type  = "website" if is_index else "article"

    lines = [
        META_START,
        f'<meta name="description" content="{desc_e}">',
        f'<link rel="canonical" href="{page_url}">',
        f'<link rel="alternate" type="application/rss+xml" '
        f'title="{site_e}" href="{SITE_URL}/feed.xml">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{site_e}">',
        f'<meta property="og:locale" content="{SITE_LOCALE}">',
        f'<meta property="og:url" content="{page_url}">',
        f'<meta property="og:title" content="{title_e}">',
        f'<meta property="og:description" content="{desc_e}">',
        f'<meta property="og:image" content="{og_image}">',
        f'<meta property="og:image:width" content="1200">',
        f'<meta property="og:image:height" content="630">',
    ]
    if not is_index and published:
        lines += [
            f'<meta property="article:published_time" content="{published}">',
            f'<meta property="article:author" content="{AUTHOR}">',
        ]
    lines += [
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title_e}">',
        f'<meta name="twitter:description" content="{desc_e}">',
        f'<meta name="twitter:image" content="{og_image}">',
        META_END,
    ]
    return "\n".join(lines)


def build_jsonld_block(*, page_url: str, title: str, desc: str,
                       is_index: bool, published: str | None,
                       og_image: str) -> str:
    person = {
        "@type": "Person",
        "name":  AUTHOR,
        "url":   AUTHOR_URL,
    }
    publisher = {
        "@type": "Organization",
        "name":  SITE_NAME,
        "url":   f"{SITE_URL}/",
    }

    if is_index:
        obj = {
            "@context":      "https://schema.org",
            "@type":         "WebSite",
            "name":          SITE_NAME,
            "alternateName": SITE_TAGLINE,
            "url":           f"{SITE_URL}/",
            "description":   desc,
            "inLanguage":    SITE_LANG,
            "author":        person,
            "publisher":     person,
            "image":         og_image,
        }
    else:
        obj = {
            "@context":         "https://schema.org",
            "@type":            "Article",
            "headline":         title,
            "description":      desc,
            "image":            og_image,
            "datePublished":    published,
            "dateModified":     published,
            "author":           person,
            "publisher":        publisher,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id":   page_url,
            },
            "url":              page_url,
            "inLanguage":       SITE_LANG,
        }
        # Drop any nulls so the schema validator stays happy.
        obj = {k: v for k, v in obj.items() if v is not None}

    payload = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    # Escape "</" so the JSON can't break out of the <script> tag.
    payload = payload.replace("</", "<\\/")

    return "\n".join([
        JSONLD_START,
        f'<script type="application/ld+json">{payload}</script>',
        JSONLD_END,
    ])


def inject_block(html: str, block: str,
                 start: str, end: str, anchor: str) -> str:
    """Replace existing block between markers, or insert after anchor regex."""
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    if pattern.search(html):
        return pattern.sub(lambda _m: block, html)
    return re.sub(
        f"({anchor})",
        lambda m: m.group(1) + "\n" + block,
        html, count=1,
    )


def strip_duplicate_tags(html: str) -> str:
    """Remove any standalone meta/link/script tags that duplicate what's
    inside the SEO blocks. The blocks themselves are left intact."""
    meta_pat   = re.compile(re.escape(META_START)   + r".*?" + re.escape(META_END),   re.DOTALL)
    jsonld_pat = re.compile(re.escape(JSONLD_START) + r".*?" + re.escape(JSONLD_END), re.DOTALL)

    def safe_ranges() -> list[tuple[int, int]]:
        ranges = []
        for pat in (meta_pat, jsonld_pat):
            m = pat.search(html)
            if m: ranges.append((m.start(), m.end()))
        return ranges

    duplicates = [
        re.compile(r'[ \t]*<meta\s+name="description"[^>]*>'),
        re.compile(r'[ \t]*<link\s+rel="canonical"[^>]*>'),
        re.compile(r'[ \t]*<link\s+rel="alternate"\s+type="application/rss\+xml"[^>]*>'),
        re.compile(r'[ \t]*<meta\s+(?:name|property)="og:[^"]+"[^>]*>'),
        re.compile(r'[ \t]*<meta\s+(?:name|property)="twitter:[^"]+"[^>]*>'),
        re.compile(r'[ \t]*<meta\s+property="article:[^"]+"[^>]*>'),
        re.compile(r'[ \t]*<script\s+type="application/ld\+json"[^>]*>.*?</script>',
                   re.DOTALL),
    ]

    for pat in duplicates:
        ranges = safe_ranges()
        result, last = [], 0
        for m in pat.finditer(html):
            if any(s <= m.start() < e for s, e in ranges):
                continue
            result.append(html[last:m.start()])
            end = m.end()
            if end < len(html) and html[end] == "\n":
                end += 1
            last = end
        result.append(html[last:])
        html = "".join(result)
    return html


def inject(html: str, meta_block: str, jsonld_block: str) -> str:
    html = inject_block(html, meta_block,
                        META_START, META_END, r"</title>")
    html = inject_block(html, jsonld_block,
                        JSONLD_START, JSONLD_END, re.escape(META_END))
    return strip_duplicate_tags(html)


def process(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    is_index = path.name == "index.html"
    slug = path.stem

    title = extract_title(html)
    desc  = extract_description(html, is_index)
    if not title or not desc:
        print(f"  skip {path.name}: missing title or description")
        return False

    page_url = (
        f"{SITE_URL}/" if is_index
        else f"{SITE_URL}/{slug}.html"
    )
    published = None if is_index else extract_date(html)
    og_image  = og_image_for(slug, is_index)

    args = dict(page_url=page_url, title=title, desc=desc,
                is_index=is_index, published=published,
                og_image=og_image)
    meta_block   = build_meta_block(**args)
    jsonld_block = build_jsonld_block(**args)
    new_html = inject(html, meta_block, jsonld_block)
    if new_html == html:
        print(f"  unchanged {path.name}")
        return False

    path.write_text(new_html, encoding="utf-8")
    print(f"  updated  {path.name}  ({len(desc)} char desc)")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--index", action="store_true",
                   help="Update index.html only.")
    g.add_argument("--post", default=None,
                   help="Update one article by slug (e.g. agentic-patterns).")
    args = ap.parse_args()

    if args.index:
        files = [BLOG_DIR / "index.html"]
    elif args.post:
        candidate = BLOG_DIR / f"{args.post}.html"
        if not candidate.exists():
            print(f"No file at {candidate}", file=sys.stderr)
            sys.exit(1)
        files = [candidate]
    else:
        files = sorted(BLOG_DIR.glob("*.html"))

    print(f"Injecting SEO meta into {len(files)} file(s) in {BLOG_DIR}")
    changed = sum(process(f) for f in files)
    print(f"Done. {changed} file(s) changed.")


if __name__ == "__main__":
    main()
