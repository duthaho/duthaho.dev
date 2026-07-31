# Nhật ký dev

A tech blog sharing personal reflections on AI, engineering, and the developer craft.

**https://duthaho.dev**

## Stack

[Astro](https://astro.build) + MDX. Posts are Markdown/MDX files in
`src/content/posts/`; bespoke editorial blocks are Astro components.

- `src/content/posts/*.mdx` — one file per post (frontmatter schema in `src/content.config.ts`)
- `src/components/` — `Callout`, `Finding`, `PullQuote`, `Diagram`, `InlineFlag`, `Aside`
- `src/layouts/` — `BaseLayout` (chrome, SEO, JSON-LD), `PostLayout` (article shell)
- `src/pages/` — `index.astro` (feed), `[slug].astro` (posts), `rss.xml.js`, `og/[...route].ts`
- `src/styles/global.css` — the site design system
- `public/` — static assets, `robots.txt`, `_redirects` (old `.html` → clean URLs)

## Develop

```sh
npm install
npm run dev      # local dev server
npm run build    # production build to dist/
npm run preview  # preview the build
```

## Writing a post

Add `src/content/posts/<slug>.mdx` with frontmatter (`num`, `title`, `titleEm`,
`description`, `date`, optional `filename`, `pinned`, `readMore`). Import components
as needed. OG card, RSS, sitemap, reading time, and prev/next are generated automatically.

## Deploy

Cloudflare Pages:
- Build command: `npm run build`
- Output directory: `dist`
- Node version: pinned via `.nvmrc` (22)

OG social cards are generated at build time (`astro-og-canvas`). Comments via giscus.

## License

All content is written by the author. All rights reserved.
