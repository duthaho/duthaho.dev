#!/usr/bin/env python3
"""
Build sitemap.xml and feed.xml (RSS 2.0) from all *.html in blog/.

Reads:
  - <title>                         → entry title
  - <p class="page-desc">           → entry description
  - "<strong>date:</strong> DD/MM/YYYY" → published date

Writes (idempotent — re-runnable any time):
  - blog/sitemap.xml
  - blog/feed.xml

Usage: python scripts/build-feeds.py
"""
from __future__ import annotations
import re
from datetime import datetime, time, timezone, timedelta
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

SITE_URL    = "https://duthaho.dev"
SITE_NAME   = "Nhật ký dev"
SITE_DESC   = "Suy nghĩ sau giờ làm về AI, engineering, và nghề dev — viết từ góc nhìn cá nhân."
SITE_LANG   = "vi"
AUTHOR      = "duthaho"
AUTHOR_EMAIL = "noreply@duthaho.dev"          # RSS spec wants "email (Name)"
TZ          = timezone(timedelta(hours=7))    # Asia/Ho_Chi_Minh

BLOG_DIR     = Path(__file__).resolve().parent.parent
SITEMAP_OUT  = BLOG_DIR / "sitemap.xml"
FEED_OUT     = BLOG_DIR / "feed.xml"


# ── helpers ────────────────────────────────────────────────────────────
def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_date(d: str) -> datetime | None:
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", d.strip())
    if not m: return None
    return datetime.combine(
        datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))).date(),
        time(9, 0),    # 09:00 local — looks human, not 00:00
        TZ,
    )


def extract_article(path: Path) -> dict | None:
    html = path.read_text(encoding="utf-8")
    title_m = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    desc_m  = re.search(r'<p class="page-desc">(.*?)</p>', html, re.DOTALL)
    date_m  = re.search(
        r"<strong>date:</strong>\s*(\d{2}/\d{2}/\d{4})", html
    )
    if not (title_m and desc_m and date_m):
        return None
    return {
        "slug":     path.stem,
        "title":    strip_tags(title_m.group(1)),
        "desc":     strip_tags(desc_m.group(1)),
        "datetime": parse_date(date_m.group(1)),
    }


def gather_articles() -> list[dict]:
    out = []
    for p in sorted(BLOG_DIR.glob("*.html")):
        if p.name == "index.html": continue
        info = extract_article(p)
        if info: out.append(info)
    out.sort(key=lambda d: d["datetime"], reverse=True)  # newest first
    return out


# ── sitemap ────────────────────────────────────────────────────────────
def build_sitemap(articles: list[dict]) -> str:
    today_iso = max(
        (a["datetime"] for a in articles),
        default=datetime.now(TZ),
    ).strftime("%Y-%m-%d")

    urls = [
        ("",         today_iso, "weekly",  "1.0"),  # index
    ] + [
        (f"{a['slug']}.html",
         a["datetime"].strftime("%Y-%m-%d"),
         "monthly", "0.8")
        for a in articles
    ]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, lastmod, changefreq, priority in urls:
        lines += [
            "  <url>",
            f"    <loc>{SITE_URL}/{path}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            f"    <changefreq>{changefreq}</changefreq>",
            f"    <priority>{priority}</priority>",
            "  </url>",
        ]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ── RSS 2.0 ────────────────────────────────────────────────────────────
def rfc822(dt: datetime) -> str:
    # e.g. "Sat, 25 Apr 2026 09:00:00 +0700"
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def build_feed(articles: list[dict]) -> str:
    last_build = (
        max(a["datetime"] for a in articles)
        if articles else datetime.now(TZ)
    )

    head = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"  <title>{xml_escape(SITE_NAME)}</title>",
        f"  <link>{SITE_URL}/</link>",
        f"  <description>{xml_escape(SITE_DESC)}</description>",
        f"  <language>{SITE_LANG}</language>",
        f"  <lastBuildDate>{rfc822(last_build)}</lastBuildDate>",
        f"  <managingEditor>{AUTHOR_EMAIL} ({AUTHOR})</managingEditor>",
        f"  <webMaster>{AUTHOR_EMAIL} ({AUTHOR})</webMaster>",
        f'  <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>',
    ]

    items = []
    for a in articles:
        url = f"{SITE_URL}/{a['slug']}.html"
        items += [
            "  <item>",
            f"    <title>{xml_escape(a['title'])}</title>",
            f"    <link>{url}</link>",
            f'    <guid isPermaLink="true">{url}</guid>',
            f"    <pubDate>{rfc822(a['datetime'])}</pubDate>",
            f"    <description>{xml_escape(a['desc'])}</description>",
            f"    <author>{AUTHOR_EMAIL} ({AUTHOR})</author>",
            "  </item>",
        ]

    tail = ["</channel>", "</rss>"]
    return "\n".join(head + items + tail) + "\n"


# ── main ───────────────────────────────────────────────────────────────
def main() -> None:
    articles = gather_articles()
    print(f"Found {len(articles)} articles in {BLOG_DIR}")

    SITEMAP_OUT.write_text(build_sitemap(articles), encoding="utf-8")
    print(f"  wrote {SITEMAP_OUT.relative_to(BLOG_DIR)}  "
          f"({SITEMAP_OUT.stat().st_size} bytes)")

    FEED_OUT.write_text(build_feed(articles), encoding="utf-8")
    print(f"  wrote {FEED_OUT.relative_to(BLOG_DIR)}     "
          f"({FEED_OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
