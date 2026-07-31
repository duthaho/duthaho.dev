# Post migration guide (VN HTML → English MDX)

You convert one legacy Vietnamese HTML post in `legacy/<slug>.html` into an
English MDX post at `src/content/posts/<slug>.mdx`.

**Reference exemplar (copy its style exactly):** `src/content/posts/redis-streams-over-kafka.mdx`
**Components live in:** `src/components/` — read them to see their props.
**Styles are already ported**; do not touch CSS. Only produce the `.mdx` file.

## 1. Translation rules
- Translate ALL Vietnamese prose to natural, idiomatic English (NOT literal/word-for-word).
- Preserve the author's voice: first person, personal, wry, honest, a little self-deprecating.
- Keep technical terms, code, commands, product names, URLs, and numbers exactly.
- Keep the meaning and structure of every paragraph, list, heading, and block. Do not summarize, drop, or add content.
- Section headings (`<h2>`) → `## English heading`.
- `<em>` emphasis → `*italics*`; `<strong>` → `**bold**`; `<code>x</code>` → `` `x` ``.
- Inline links `<a href>` → `[text](href)`. Internal links like `href="caching-is-never-free.html"` become `[text](/caching-is-never-free/)`.

## 2. Frontmatter (YAML)
Use the exact `num`, `date`, `pinned`, `filename` values given in your task prompt.
Translate `title`, `titleEm`, `description`, and `readMore` items.
- `title` + `titleEm`: the headline is two-tone in the original — main title, then an
  emphasised tail (the `<em>` part of the `<h1 class="page-title">`). Split accordingly.
  If there is no `<em>` tail, omit `titleEm`.
- `description`: translate the `<p class="page-desc">` (same text as the meta description). One paragraph.
- `filename`: the `<span class="terminal-filename">` inside `content-card` (e.g. `agentic-rag.md`).
- `readMore`: translate the `<section class="read-more">` list. Each `<li>` has a
  `<span class="read-more-kind">` (kind), the link text (title), href, and a
  `<span class="rm-by">` (by). Translate kind ("nguồn"→"source", "trên blog"→"on the blog")
  and the `by` text. For internal blog links use the bare slug (e.g. `caching-is-never-free`),
  for external use the full URL.

## 3. Component mapping (legacy HTML class → MDX component)
Import only the components you use, at the top of the body (after frontmatter):
```mdx
import Callout from '../../components/Callout.astro';
import Finding from '../../components/Finding.astro';
import PullQuote from '../../components/PullQuote.astro';
import Diagram from '../../components/Diagram.astro';
import InlineFlag from '../../components/InlineFlag.astro';
import Aside from '../../components/Aside.astro';
```
| Legacy HTML | MDX |
| --- | --- |
| `<div class="pq"><p>…</p></div>` | `<PullQuote>…</PullQuote>` |
| `<div class="pq closing-quote">` | `<PullQuote closing>…</PullQuote>` |
| `<div class="callout"><div class="callout-label">L</div><p>…</p></div>` | `<Callout label="L">…</Callout>` |
| `<div class="finding-block"><div class="finding-num">01</div><div class="finding-title">T</div><p>…</p></div>` | `<Finding n="01" title="T">…</Finding>` |
| `<span class="inline-flag">…</span>` | `<InlineFlag>…</InlineFlag>` |
| `<div class="aside"><p>…</p></div>` | `<Aside>…</Aside>` |
| `<div class="diagram"><span class="diagram-label">L</span>ASCII…</div>` | `<Diagram label="L" code={\`…ASCII…\`} />` |
| `<hr class="divider">` | `<hr class="divider" />` |

### Critical rules
- **Diagram**: put the ASCII art verbatim inside a template-literal `code={\`...\`}` prop so
  whitespace/alignment is preserved. Decode HTML entities: `&amp;`→`&`, `&lt;`→`<`,
  `&gt;`→`>`, `&nbsp;`→space. Translate any Vietnamese labels/words inside the art but
  KEEP the column alignment reasonable. The label goes in the `label` prop, not the code.
- Inside component slots you may use Markdown (`**bold**`, `` `code` ``, `*italic*`).
- Ordinary `<p>`, `<ul>/<ol>/<li>`, `<h2>` become plain Markdown (blank line between blocks).
- Do NOT include: the `<head>`, topbar, meta-card, terminal-card wrappers, breadcrumb,
  page-title/page-desc (those come from the layout/frontmatter), post-nav, comments, footer.
  Only the article's inner content (what was inside `<article class="article">`), MINUS the
  trailing `<section class="read-more">` (that goes in frontmatter) and any post-nav.

## 4. Output
Write only `src/content/posts/<slug>.mdx`. Build is validated later centrally — do not run the build.
Make sure MDX is valid: components closed, no stray raw `<`/`>` in prose (escape as needed),
template literals for diagrams. Match the exemplar's formatting closely.
