import { OGImageRoute } from 'astro-og-canvas';
import { getCollection } from 'astro:content';

const posts = await getCollection('posts', ({ data }) => !data.draft);

const pages = Object.fromEntries(
  posts.map((post) => [
    post.id,
    {
      title: post.data.titleEm
        ? `${post.data.title}: ${post.data.titleEm}`
        : post.data.title,
      description: post.data.description,
      num: post.data.num,
    },
  ]),
);

export const { getStaticPaths, GET } = OGImageRoute({
  param: 'route',
  pages,
  getImageOptions: (_path, page) => ({
    title: page.title,
    description: page.description,
    logo: undefined,
    bgGradient: [
      [236, 227, 208], // --paper #ECE3D0
      [216, 205, 179], // --paper-deep #D8CDB3
    ],
    border: { color: [193, 59, 20], width: 20, side: 'inline-start' }, // vermillion
    padding: 70,
    font: {
      title: {
        color: [27, 24, 20], // --ink #1B1814
        size: 62,
        weight: 'Bold',
        lineHeight: 1.15,
      },
      description: {
        color: [110, 101, 87], // --ink-mute
        size: 30,
        lineHeight: 1.4,
      },
    },
  }),
});
