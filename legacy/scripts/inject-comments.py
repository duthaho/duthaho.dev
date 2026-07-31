#!/usr/bin/env python3
"""
Inject the Giscus comment widget into every article page.

Giscus stores comments in the repo's GitHub Discussions — there is no
backend to run. This script adds a <section class="comments-card"> that
loads the Giscus client, placed inside .article-main right after the
article content card.

The block is wrapped in marker comments, so re-running this script
replaces the previous block instead of duplicating it.

index.html (the listing page) is skipped — only article pages, which
carry the TOC <aside class="article-sidebar">, get comments.

Usage:
    python scripts/inject-comments.py             # every article
    python scripts/inject-comments.py --post foo  # one article (slug = foo)
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# ── Giscus configuration ─────────────────────────────────────
# These are PUBLIC values (they appear in the embed on the live site),
# so they are safe to commit. REPO_ID and CATEGORY_ID are generated at
# https://giscus.app after the one-time GitHub setup (Task 1 of the
# implementation plan). Paste the recorded values below.
REPO        = "duthaho/duthaho.dev"
REPO_ID     = "R_kgDOR2nYrQ"
CATEGORY    = "Blog"
CATEGORY_ID = "DIC_kwDOR2nYrc4C9gvp"
THEME_URL   = "https://cdn.jsdelivr.net/gh/duthaho/duthaho.dev@main/giscus-theme.css"
LANG        = "vi"

COMMENTS_START = "<!-- comments:start -->"
COMMENTS_END   = "<!-- comments:end -->"

BLOG_DIR = Path(__file__).resolve().parent.parent


def build_comments_block() -> str:
    """The full <section> + Giscus <script>, between marker comments."""
    return "\n".join([
        COMMENTS_START,
        '<section class="terminal-card comments-card" id="comments">',
        '  <div class="terminal-header">',
        '    <div class="terminal-dots">',
        '      <span class="dot red"></span>',
        '      <span class="dot yellow"></span>',
        '      <span class="dot green"></span>',
        '    </div>',
        '    <span class="terminal-filename">comments.md</span>',
        '  </div>',
        '  <div class="terminal-body comments-body">',
        '    <script src="https://giscus.app/client.js"',
        f'            data-repo="{REPO}"',
        f'            data-repo-id="{REPO_ID}"',
        f'            data-category="{CATEGORY}"',
        f'            data-category-id="{CATEGORY_ID}"',
        '            data-mapping="pathname"',
        '            data-strict="1"',
        '            data-reactions-enabled="1"',
        '            data-emit-metadata="0"',
        '            data-input-position="bottom"',
        f'            data-theme="{THEME_URL}"',
        f'            data-lang="{LANG}"',
        '            data-loading="lazy"',
        '            crossorigin="anonymous"',
        '            async>',
        '    </script>',
        '    <noscript>Bình luận cần JavaScript được bật.</noscript>',
        '  </div>',
        '</section>',
        COMMENTS_END,
    ])


def inject_comments(html: str) -> str:
    """Replace an existing comment block, or insert a new one inside
    .article-main right after the content card. Returns html unchanged
    if the page has no TOC <aside> (i.e. it is not an article page)."""
    block = build_comments_block()

    existing = re.compile(
        re.escape(COMMENTS_START) + r".*?" + re.escape(COMMENTS_END),
        re.DOTALL,
    )
    if existing.search(html):
        return existing.sub(lambda _m: block, html)

    # First-time insert. The </div> that closes .article-main is the
    # one immediately followed (whitespace only) by the TOC <aside>.
    anchor = re.compile(
        r"(\n[ \t]*</div>)(\s*<aside class=\"article-sidebar\""
        r" id=\"toc-sidebar\"></aside>)"
    )
    if not anchor.search(html):
        return html
    return anchor.sub(
        lambda m: "\n" + block + m.group(1) + m.group(2),
        html, count=1,
    )


def process(path: Path) -> bool:
    if path.name == "index.html":
        return False
    html = path.read_text(encoding="utf-8")
    new_html = inject_comments(html)
    if new_html == html:
        print(f"  unchanged {path.name}")
        return False
    path.write_text(new_html, encoding="utf-8")
    print(f"  updated   {path.name}")
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--post", default=None,
                    help="Update one article by slug (e.g. agentic-patterns).")
    args = ap.parse_args()

    if "PASTE_" in REPO_ID or "PASTE_" in CATEGORY_ID:
        print("ERROR: set REPO_ID and CATEGORY_ID at the top of "
              "scripts/inject-comments.py (see Task 1).", file=sys.stderr)
        sys.exit(1)

    if args.post:
        candidate = BLOG_DIR / f"{args.post}.html"
        if not candidate.exists():
            print(f"No file at {candidate}", file=sys.stderr)
            sys.exit(1)
        files = [candidate]
    else:
        files = sorted(f for f in BLOG_DIR.glob("*.html")
                       if f.name != "index.html")

    print(f"Injecting Giscus comments into {len(files)} file(s) in {BLOG_DIR}")
    changed = sum(process(f) for f in files)
    print(f"Done. {changed} file(s) changed.")


if __name__ == "__main__":
    main()
