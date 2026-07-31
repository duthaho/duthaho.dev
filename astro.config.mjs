// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

const SITE = 'https://duthaho.dev';

// Deployed on Cloudflare Pages. Old /<slug>.html -> new /<slug>/ redirects are
// handled as real 301s at the edge via public/_redirects (not Astro redirects).

// https://astro.build/config
export default defineConfig({
  site: SITE,
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  markdown: {
    shikiConfig: { theme: 'github-dark' },
  },
});
