# Design: Comments for blog articles

**Date:** 2026-05-21
**Status:** Approved
**Repo:** `duthaho/duthaho.dev` (the `blog/` directory is the git repo)

## Goal

Let readers leave comments on the 10 blog articles (and every future
article) without the blog owner running or maintaining a server.

## Approach: Giscus

Comments are stored in the blog repo's **GitHub Discussions** via
[Giscus](https://giscus.app). No backend, no database, free, no
maintenance. Moderation happens in GitHub's native Discussions UI.

**Constraint accepted:** readers must sign in with a GitHub account to
post. The audience is developers, so this is acceptable. Non-developer
readers cannot comment.

### Alternatives rejected

- **Utterances** — stores comments as GitHub *Issues*; clutters the
  issue tracker and has fewer features than Discussions.
- **Self-hosted Cloudflare Worker + D1** — full data ownership but adds
  a real spam/moderation/maintenance burden. Overkill for a personal
  blog.
- **Disqus / hosted services** — ads, third-party tracking, slow
  iframe, and the vendor owns the comment data.

## Components

### 1. GitHub setup (one-time, manual — done by the owner)

Performed in the GitHub UI before the embed works:

1. Make `duthaho/duthaho.dev` **public**.
2. Enable **Discussions** on the repo (Settings → Features).
3. Install the **giscus GitHub App** (`github.com/apps/giscus`) on the
   repo.
4. Create a Discussions category named `Comments`, of type
   **Announcement** (only maintainers can open top-level threads;
   Giscus creates one thread per article automatically).
5. From `giscus.app`, generate and copy the `repo-id` and the
   `category-id` for the `Comments` category.

These IDs are **public values** (they appear in the embed on the live
site), so they are safe to commit to the repo.

### 2. Giscus embed block

A `comments.md` terminal-card rendered directly below the article
content — inside `.article-main`, immediately after the
`.content-card` div, so the thread is constrained to the article text
column.

The block is wrapped in marker comments so the build script can
replace it idempotently:

```html
<!-- comments:start -->
<section class="terminal-card comments-card" id="comments">
  <div class="terminal-header">
    <div class="terminal-dots">
      <span class="dot red"></span>
      <span class="dot yellow"></span>
      <span class="dot green"></span>
    </div>
    <span class="terminal-filename">comments.md</span>
  </div>
  <div class="terminal-body comments-body">
    <script src="https://giscus.app/client.js"
            data-repo="duthaho/duthaho.dev"
            data-repo-id="<REPO_ID>"
            data-category="Comments"
            data-category-id="<CATEGORY_ID>"
            data-mapping="pathname"
            data-strict="1"
            data-reactions-enabled="1"
            data-emit-metadata="0"
            data-input-position="bottom"
            data-theme="https://duthaho.dev/giscus-theme.css"
            data-lang="vi"
            data-loading="lazy"
            crossorigin="anonymous"
            async>
    </script>
    <noscript>Bình luận cần JavaScript được bật.</noscript>
  </div>
</section>
<!-- comments:end -->
```

Configuration rationale:

- `data-mapping="pathname"` + `data-strict="1"` — each article maps to
  its own discussion, keyed by the URL path. Stable because article
  filenames do not change.
- `data-lang="vi"` — Vietnamese UI, matching the site.
- `data-loading="lazy"` — the iframe loads only when scrolled near, so
  page-speed and Core Web Vitals are unaffected.
- `data-reactions-enabled="1"` — readers can react to the post.
- `data-input-position="bottom"` — comment box below the thread.
- `data-theme` — points at the custom theme (component 4) via an
  absolute HTTPS URL (required by Giscus).
- `<noscript>` — graceful message for readers with JavaScript off.

### 3. `scripts/inject-comments.py`

A new build script that mirrors the existing `scripts/inject-meta.py`:

- Holds the Giscus config as hardcoded constants at the top of the file
  (`REPO`, `REPO_ID`, `CATEGORY`, `CATEGORY_ID`) — same style as
  `inject-meta.py`'s `SITE_URL` etc.
- Iterates every article HTML page — all `*.html` in the blog root
  **except `index.html`**.
- Injects the embed block between `<!-- comments:start -->` and
  `<!-- comments:end -->`. If the markers already exist, it replaces
  the block; otherwise it inserts the block at the correct anchor
  (inside `.article-main`, after `.content-card`). This makes the
  script **idempotent** — re-running it never duplicates the block.
- Supports a `--post <slug>` flag to process a single article, like the
  other build scripts.
- Is added to `scripts/build.py` as a new step (step 4/4), so future
  articles get comments automatically on the next build.

### 4. `giscus-theme.css`

A custom Giscus theme file at the **site root** (`blog/giscus-theme.css`),
deployed as a static asset and referenced by the embed via
`https://duthaho.dev/giscus-theme.css`.

Every built-in Giscus theme is a generic light or dark theme — none
matches the site's "Atelier" aesthetic (*vermillion ink on warm bone*).
The custom theme maps Giscus's CSS variables to the site palette:

- Background → `--paper` (`#ECE3D0`)
- Text → `--ink` (`#1B1814`) / `--ink-soft`
- Accent / links / buttons → `--vermillion` (`#C13B14`)
- Borders → `--rule-soft`
- Fonts → IBM Plex Mono (UI/code) and Newsreader (body), matching the
  site.

### 5. `style.css` additions

`.comments-card` / `.comments-body` rules so the new terminal-card's
width, margin, and spacing match the article content card above it.

## Data flow

1. Reader opens an article and scrolls toward the bottom.
2. The Giscus iframe lazy-loads.
3. Giscus looks up the GitHub Discussion whose mapping matches the page
   pathname.
4. Existing comments render inside the `comments.md` card.
5. The reader signs in with GitHub and posts a comment.
6. The comment is saved as a comment on that repo Discussion.
7. The owner receives a GitHub notification and moderates (hide /
   delete / block) from the GitHub Discussions UI.

## Scope

**In scope**

- All 10 existing articles.
- Every future article — automatic via the build script.
- A custom theme matching the site design.

**Out of scope**

- `index.html` (the listing page) gets no comments.
- Anonymous commenting.
- A custom moderation UI — moderation uses GitHub's native tools.
- Email notifications beyond GitHub's own notification system.

## Edge cases

- **JavaScript disabled** → empty card showing the `<noscript>`
  message.
- **`giscus.app` unreachable** → empty card; the rest of the page is
  unaffected.
- **Local development** → the page pathname differs from production, so
  locally posted comments will not match production discussions; the
  theme URL points at the deployed file. Comments are only meaningful
  on the deployed site — this is expected.
- **Renaming a published article file** → breaks that article's
  discussion mapping (a new path is a new, empty thread). Published
  article filenames must not be renamed.

## Testing

- Run `inject-comments.py` → the block appears exactly once in all 10
  article files and not in `index.html`.
- Re-run `inject-comments.py` → still exactly once per file
  (idempotency).
- `python scripts/build.py` runs clean end-to-end with the new step.
- Post-deploy: load an article, post a test comment, confirm it appears
  in the repo's Discussions, and confirm the theme matches the site.
- Page-speed: confirm lazy-loading keeps the Giscus iframe off the
  critical rendering path.
