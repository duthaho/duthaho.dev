import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const posts = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/posts' }),
  schema: z.object({
    // Sequential post number shown as #NN in the feed and article header.
    num: z.number(),
    title: z.string(),
    // Optional emphasised tail of the title (rendered in <em>), matching the
    // original two-tone headline style.
    titleEm: z.string().optional(),
    description: z.string(),
    date: z.coerce.date(),
    author: z.string().default('duthaho'),
    // Short slug shown in the terminal card header, e.g. "redis-streams.md".
    filename: z.string().optional(),
    pinned: z.boolean().default(false),
    draft: z.boolean().default(false),
    // Curated "Read more" links shown at the foot of the article.
    readMore: z
      .array(
        z.object({
          kind: z.string(), // e.g. "source", "on the blog"
          title: z.string(),
          href: z.string(),
          by: z.string().optional(),
        }),
      )
      .optional(),
  }),
});

export const collection = { posts };
export const collections = { posts };
