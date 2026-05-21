# Blog Comments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub-Discussions-backed comment thread (Giscus) to every blog article, with a build script that keeps future articles covered automatically.

**Architecture:** Giscus is a third-party script that renders a comment widget in an iframe and stores comments in the repo's GitHub Discussions — no backend. A new build script (`scripts/inject-comments.py`) injects a marker-delimited `<section>` into every article HTML file, mirroring the existing `inject-meta.py` pattern, and is wired into `build.py`. A custom CSS theme file makes the Giscus widget match the site's "Atelier" card design.

**Tech Stack:** Static HTML/CSS/JS site, Python 3 build scripts, Giscus (`giscus.app`), GitHub Discussions.

**Testing note:** This repo has no test framework — the existing `scripts/*.py` are untested utilities. Per "follow established patterns," this plan verifies behavior with explicit commands (run the script, grep exact counts, double-run for idempotency, full build, post-deploy live check) instead of a unit-test harness. Each code task has a verification step with exact commands and expected output.

**Commits:** The repo owner opted out of commits during this work. No `git commit` steps are included — commit manually when ready.

**Working directory:** All paths are relative to the blog repo root: `d:\hop\code\duthaho.dev\blog`. Run all commands from there.

---

## Task 1: One-time GitHub setup (manual — repo owner)

This task is done by a human in the GitHub web UI. It produces two values
(`REPO_ID`, `CATEGORY_ID`) that Task 3 needs. It writes no code.

**Files:** none.

- [ ] **Step 1: Make the repo public**

Go to `https://github.com/duthaho/duthaho.dev` → **Settings** → scroll to
**Danger Zone** → **Change repository visibility** → **Make public** →
confirm.

- [ ] **Step 2: Enable Discussions**

Settings → **General** → **Features** section → check **Discussions**.

- [ ] **Step 3: Install the Giscus GitHub App**

Visit `https://github.com/apps/giscus` → **Install** → choose **Only
select repositories** → select `duthaho/duthaho.dev` → **Install**.

- [ ] **Step 4: Create the "Comments" Discussion category**

Go to the repo's **Discussions** tab → click the pencil/edit icon next to
**Categories** → **New category**. Set:
- Title: `Comments`
- Discussion Format: **Announcement** (only maintainers can open
  top-level threads; Giscus still creates one thread per article)

Save.

- [ ] **Step 5: Generate REPO_ID and CATEGORY_ID**

Go to `https://giscus.app`. In the configuration form:
- **Repository:** `duthaho/duthaho.dev` — wait for the green
  "✓ giscus is installed" confirmation.
- **Page ↔ Discussions Mapping:** select **"Discussion title contains
  page pathname"**.
- **Discussion Category:** select **Comments**.

Scroll to the generated `<script>` snippet. Copy these two values from it:
- `data-repo-id="..."` → this is **REPO_ID** (starts with `R_`)
- `data-category-id="..."` → this is **CATEGORY_ID** (starts with `DIC_`)

- [ ] **Step 6: Verify**

On `giscus.app` the repo field shows "✓ giscus is installed" with no red
error text. You have recorded two strings: `REPO_ID` (starts `R_`) and
`CATEGORY_ID` (starts `DIC_`). Keep them for Task 3.

---

## Task 2: Create the custom Giscus theme

A custom theme so the Giscus widget matches the article cards (white
card interior `#ffffff`, text `#1f2328`, links `#0969da`, vermillion
`#C13B14` primary button). This is the GitHub light theme with the
palette overridden — Giscus loads this one file as the entire theme.

**Files:**
- Create: `giscus-theme.css`

- [ ] **Step 1: Create `giscus-theme.css`**

Create `giscus-theme.css` in the repo root with exactly this content:

```css
/*! Giscus theme — "Atelier" for duthaho.dev
 * Based on the GitHub light theme (MIT, (c) 2018 GitHub Inc.,
 * https://github.com/primer/primitives/blob/main/LICENSE),
 * with the palette overridden to match the site's article cards.
 */
main {
  --color-prettylights-syntax-comment: #6e7781;
  --color-prettylights-syntax-constant: #0550ae;
  --color-prettylights-syntax-entity: #8250df;
  --color-prettylights-syntax-storage-modifier-import: #24292f;
  --color-prettylights-syntax-entity-tag: #116329;
  --color-prettylights-syntax-keyword: #cf222e;
  --color-prettylights-syntax-string: #0a3069;
  --color-prettylights-syntax-variable: #953800;
  --color-prettylights-syntax-brackethighlighter-unmatched: #82071e;
  --color-prettylights-syntax-invalid-illegal-text: #f6f8fa;
  --color-prettylights-syntax-invalid-illegal-bg: #82071e;
  --color-prettylights-syntax-carriage-return-text: #f6f8fa;
  --color-prettylights-syntax-carriage-return-bg: #cf222e;
  --color-prettylights-syntax-string-regexp: #116329;
  --color-prettylights-syntax-markup-list: #3b2300;
  --color-prettylights-syntax-markup-heading: #0550ae;
  --color-prettylights-syntax-markup-italic: #24292f;
  --color-prettylights-syntax-markup-bold: #24292f;
  --color-prettylights-syntax-markup-deleted-text: #82071e;
  --color-prettylights-syntax-markup-deleted-bg: #ffebe9;
  --color-prettylights-syntax-markup-inserted-text: #116329;
  --color-prettylights-syntax-markup-inserted-bg: #dafbe1;
  --color-prettylights-syntax-markup-changed-text: #953800;
  --color-prettylights-syntax-markup-changed-bg: #ffd8b5;
  --color-prettylights-syntax-markup-ignored-text: #eaeef2;
  --color-prettylights-syntax-markup-ignored-bg: #0550ae;
  --color-prettylights-syntax-meta-diff-range: #8250df;
  --color-prettylights-syntax-brackethighlighter-angle: #57606a;
  --color-prettylights-syntax-sublimelinter-gutter-mark: #8c959f;
  --color-prettylights-syntax-constant-other-reference-link: #0a3069;
  --color-btn-text: #1f2328;
  --color-btn-bg: #f4f1ea;
  --color-btn-border: #1f232826;
  --color-btn-shadow: 0 1px 0 #1f23280a;
  --color-btn-inset-shadow: inset 0 1px 0 #ffffff40;
  --color-btn-hover-bg: #ece7da;
  --color-btn-hover-border: #1f232826;
  --color-btn-active-bg: #e4ddcc;
  --color-btn-active-border: #1f232826;
  --color-btn-selected-bg: #e4ddcc;
  --color-btn-primary-text: #fff;
  --color-btn-primary-bg: #c13b14;
  --color-btn-primary-border: #1f232826;
  --color-btn-primary-shadow: 0 1px 0 #1f23281a;
  --color-btn-primary-inset-shadow: inset 0 1px 0 #ffffff08;
  --color-btn-primary-hover-bg: #a83110;
  --color-btn-primary-hover-border: #1f232826;
  --color-btn-primary-selected-bg: #8e2a0c;
  --color-btn-primary-selected-shadow: inset 0 1px 0 #002d1133;
  --color-btn-primary-disabled-text: #fffc;
  --color-btn-primary-disabled-bg: #dcb3a6;
  --color-btn-primary-disabled-border: #1f232826;
  --color-action-list-item-default-hover-bg: #d0d7de52;
  --color-segmented-control-bg: #eaeef2;
  --color-segmented-control-button-bg: #fff;
  --color-segmented-control-button-selected-border: #8c959f;
  --color-fg-default: #1f2328;
  --color-fg-muted: #5d5b54;
  --color-fg-subtle: #8a8775;
  --color-canvas-default: #ffffff;
  --color-canvas-overlay: #ffffff;
  --color-canvas-inset: #f7f5ee;
  --color-canvas-subtle: #f7f5ee;
  --color-border-default: #d6d2c4;
  --color-border-muted: #e8e3d4;
  --color-neutral-muted: #afb8c133;
  --color-accent-fg: #0969da;
  --color-accent-emphasis: #0969da;
  --color-accent-muted: #54aeff66;
  --color-accent-subtle: #ddf4ff;
  --color-success-fg: #1a7f37;
  --color-attention-fg: #9a6700;
  --color-attention-muted: #d4a72c66;
  --color-attention-subtle: #fff8c5;
  --color-danger-fg: #d1242f;
  --color-danger-muted: #ff818266;
  --color-danger-subtle: #ffebe9;
  --color-primer-shadow-inset: inset 0 1px 0 #d0d7de33;
  --color-scale-gray-1: #eaeef2;
  --color-scale-blue-1: #b6e3ff;
  --color-social-reaction-bg-hover: var(--color-scale-gray-1);
  --color-social-reaction-bg-reacted-hover: var(--color-scale-blue-1);
}

main .pagination-loader-container {
  background-image: url(https://github.com/images/modules/pulls/progressive-disclosure-line.svg);
}

main .gsc-loading-image {
  background-image: url(https://github.githubassets.com/images/mona-loading-default.gif);
}
```

- [ ] **Step 2: Verify the file is valid CSS**

Run: `python -c "import pathlib; t=pathlib.Path('giscus-theme.css').read_text(encoding='utf-8'); assert t.count('{')==t.count('}'), 'unbalanced braces'; assert '--color-btn-primary-bg: #c13b14' in t; print('OK', len(t), 'bytes')"`

Expected: `OK <n> bytes` with no AssertionError.

---

## Task 3: Create the comment-injection build script

A new build script that injects a marker-delimited `<section>` carrying
the Giscus widget into every article page. Mirrors `scripts/inject-meta.py`.

**Files:**
- Create: `scripts/inject-comments.py`

- [ ] **Step 1: Create `scripts/inject-comments.py`**

Create `scripts/inject-comments.py` with exactly this content:

```python
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
REPO_ID     = "PASTE_REPO_ID_FROM_GISCUS"
CATEGORY    = "Comments"
CATEGORY_ID = "PASTE_CATEGORY_ID_FROM_GISCUS"
THEME_URL   = "https://duthaho.dev/giscus-theme.css"
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
```

- [ ] **Step 2: Paste the real Giscus IDs**

In `scripts/inject-comments.py`, replace the two placeholder constants
with the values recorded in Task 1, Step 5:
- `REPO_ID = "PASTE_REPO_ID_FROM_GISCUS"` → `REPO_ID = "R_..."` (the recorded REPO_ID)
- `CATEGORY_ID = "PASTE_CATEGORY_ID_FROM_GISCUS"` → `CATEGORY_ID = "DIC_..."` (the recorded CATEGORY_ID)

- [ ] **Step 3: Verify the script parses and IDs are set**

Run: `python -c "import ast; ast.parse(open('scripts/inject-comments.py',encoding='utf-8').read()); print('parse OK')"`
Expected: `parse OK`

Run: `python -c "src=open('scripts/inject-comments.py',encoding='utf-8').read(); assert 'PASTE_' not in src, 'IDs not set'; print('IDs set OK')"`
Expected: `IDs set OK` (if it fails, complete Task 3 Step 2 first).

---

## Task 4: Run the script and verify injection + idempotency

This is the behavioral test for Task 3: the block must land exactly once
per article, never in `index.html`, and a second run must change nothing.

**Files:** modifies all 10 article HTML files (adds the comment block).

- [ ] **Step 1: Confirm no article has the block yet (red state)**

Run: `python -c "import glob; n=sum(open(f,encoding='utf-8').read().count('<!-- comments:start -->') for f in glob.glob('*.html')); print('blocks before:', n)"`
Expected: `blocks before: 0`

- [ ] **Step 2: Run the injection script**

Run: `python scripts/inject-comments.py`
Expected output: `Injecting Giscus comments into 10 file(s) ...` followed by
10 `updated` lines and `Done. 10 file(s) changed.`

- [ ] **Step 3: Verify exactly one block per article, none in index.html (green state)**

Run: `python -c "import glob; per={f:open(f,encoding='utf-8').read().count('<!-- comments:start -->') for f in sorted(glob.glob('*.html'))}; print(per); assert per['index.html']==0; assert all(v==1 for k,v in per.items() if k!='index.html'); print('PASS: 1 block per article, 0 in index')"`
Expected: a dict showing `1` for every article and `0` for `index.html`, then `PASS: ...`.

- [ ] **Step 4: Verify idempotency — run again, expect no changes**

Run: `python scripts/inject-comments.py`
Expected output: 10 `unchanged` lines and `Done. 0 file(s) changed.`

- [ ] **Step 5: Verify the block is inside .article-main, after the content card**

Run: `python -c "h=open('agentic-patterns.html',encoding='utf-8').read(); i=h.index('comments:start'); pre=h[:i]; assert pre.count('<div class=\"article-main\">')==1; assert h.index('content-card')<i<h.index('article-sidebar'); print('placement OK')"`
Expected: `placement OK` (block sits after the content card and before the TOC aside).

---

## Task 5: Style the comments card

The comment `<section>` reuses `class="terminal-card"` inside
`.article-main`, so it already inherits the article card chrome (white
card, panel header, hidden dots) from existing `body.article-page
.article-main .terminal-card` rules. Only three small additions are
needed: vertical spacing from the content card, full-width Giscus iframe,
and styling for the `<noscript>` fallback.

**Files:**
- Modify: `style.css` (append at end of file)

- [ ] **Step 1: Append the comments-card styles to `style.css`**

Append exactly this block to the very end of `style.css`:

```css

/* ═════════════════════════════════════════════════════════════
   COMMENTS CARD
   The Giscus widget, in its own terminal-card below the article.
   ═════════════════════════════════════════════════════════════ */
.comments-card { margin-top: 2rem; }

.comments-body .giscus,
.comments-body .giscus-frame {
  width: 100%;
}

.comments-body noscript {
  display: block;
  font-family: var(--idx-font-mono);
  font-size: 0.85rem;
  color: var(--idx-text-muted);
}
```

- [ ] **Step 2: Verify the rules were appended and braces balance**

Run: `python -c "t=open('style.css',encoding='utf-8').read(); assert '.comments-card { margin-top: 2rem; }' in t; assert t.count('{')==t.count('}'), 'unbalanced braces'; print('CSS OK')"`
Expected: `CSS OK`

---

## Task 6: Wire the script into the build

Add `inject-comments.py` as a fourth step in `scripts/build.py` so future
articles get comments automatically on every build.

**Files:**
- Modify: `scripts/build.py`

- [ ] **Step 1: Renumber the existing step labels to /4**

In `scripts/build.py`, change the three step labels:
- `step("1/3  render OG cards", cmd)` → `step("1/4  render OG cards", cmd)`
- `step("2/3  build sitemap + RSS",` → `step("2/4  build sitemap + RSS",`
- `step("3/3  inject meta + JSON-LD", cmd)` → `step("3/4  inject meta + JSON-LD", cmd)`

- [ ] **Step 2: Add the fourth build step**

In `scripts/build.py`, find this block in `main()`:

```python
    cmd = [PYTHON, str(SCRIPTS / "inject-meta.py")]
    if args.post: cmd += ["--post", args.post]
    step("3/4  inject meta + JSON-LD", cmd)

    print("\nBuild complete. Ready to deploy.")
```

Replace it with:

```python
    cmd = [PYTHON, str(SCRIPTS / "inject-meta.py")]
    if args.post: cmd += ["--post", args.post]
    step("3/4  inject meta + JSON-LD", cmd)

    cmd = [PYTHON, str(SCRIPTS / "inject-comments.py")]
    if args.post: cmd += ["--post", args.post]
    step("4/4  inject comments", cmd)

    print("\nBuild complete. Ready to deploy.")
```

- [ ] **Step 3: Verify build.py still parses**

Run: `python -c "import ast; ast.parse(open('scripts/build.py',encoding='utf-8').read()); print('build.py parse OK')"`
Expected: `build.py parse OK`

---

## Task 7: Full build verification

Confirm the whole build pipeline runs clean with the new step, and that
re-running it is idempotent (no duplicate comment blocks).

**Files:** none (runs the build).

- [ ] **Step 1: Run the full build (skip OG for speed)**

Run: `python scripts/build.py --skip-og`
Expected: steps `2/4`, `3/4`, and `4/4` all run; step `4/4 inject
comments` prints `Done. 0 file(s) changed.` (blocks already present from
Task 4); final line `Build complete. Ready to deploy.` Exit code 0.

- [ ] **Step 2: Verify still exactly one comment block per article**

Run: `python -c "import glob; assert all(open(f,encoding='utf-8').read().count('<!-- comments:start -->')==1 for f in glob.glob('*.html') if f!='index.html'); print('still 1 block per article')"`
Expected: `still 1 block per article`

- [ ] **Step 3: Confirm the theme file will be deployed**

Confirm `giscus-theme.css` is in the repo root alongside `style.css` and
`main.js`. If the deploy process uses an explicit file list (rather than
uploading the whole directory), add `giscus-theme.css` to it so the file
is served at `https://duthaho.dev/giscus-theme.css`.

Run: `python -c "import os; assert os.path.exists('giscus-theme.css'); print('theme file present at root')"`
Expected: `theme file present at root`

---

## Task 8: Post-deploy live verification

The real test. Giscus's `pathname` mapping and the absolute theme URL
only resolve correctly on the deployed site, so this must run after deploy.

**Files:** none.

- [ ] **Step 1: Deploy the site**

Deploy using the normal process for this site (the build from Task 7 is
already done). Ensure `giscus-theme.css` and all 10 updated article files
are uploaded.

- [ ] **Step 2: Verify the widget loads and is themed**

Open a deployed article, e.g. `https://duthaho.dev/agentic-patterns.html`,
and scroll to the bottom. Confirm:
- A `comments.md` terminal-card appears below the article content.
- The Giscus comment box renders inside it (white card, vermillion
  "Comment" button — confirms the custom theme loaded).
- No console errors mentioning `giscus`.

- [ ] **Step 3: Post a test comment and confirm storage**

Sign in to Giscus with GitHub, post a test comment. Confirm it appears in
the widget, then confirm a matching discussion now exists under the
**Comments** category at
`https://github.com/duthaho/duthaho.dev/discussions`. Delete the test
comment afterward if desired (via the GitHub Discussions UI).

- [ ] **Step 4: Verify lazy-loading kept the iframe off the critical path**

In the browser dev tools Network tab, reload the article and confirm the
`giscus.app` iframe request fires only when you scroll near the comments
section — not during initial page load.

---

## Self-Review

**Spec coverage** (against `docs/superpowers/specs/2026-05-21-blog-comments-design.md`):
- GitHub setup (public repo, Discussions, app, category, IDs) → Task 1.
- Giscus embed block with all configured `data-*` attributes → Task 3 (`build_comments_block`).
- `scripts/inject-comments.py` mirroring `inject-meta.py`, idempotent, `--post` flag, skips `index.html` → Tasks 3 + 4.
- Added to `build.py` as step 4/4 → Task 6.
- `giscus-theme.css` custom theme → Task 2.
- `style.css` `.comments-card` additions → Task 5.
- All 10 articles + future articles automatic → Tasks 4 + 6.
- Edge cases: JS-disabled `<noscript>` → in Task 3 block; placement/idempotency → Task 4; local-dev caveat → covered by deferring real check to Task 8.
- Testing items from spec → Tasks 4, 7, 8.

**Placeholder scan:** The only literal placeholders are `REPO_ID` /
`CATEGORY_ID` in Task 3 — these are unavoidable user-supplied values
generated by the owner's GitHub account in Task 1. Task 3 Step 2 sets
them explicitly and Step 3 verifies they are set; the script itself
refuses to run while they hold `PASTE_` defaults. No vague verbs, no TODO.

**Type/name consistency:** `COMMENTS_START` / `COMMENTS_END` markers,
`build_comments_block()`, `inject_comments()`, `process()`, `comments-card`
/ `comments-body` class names, and the `comments:start` / `comments:end`
marker strings are used identically across Tasks 3, 4, 5, and 7.
