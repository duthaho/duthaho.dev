import rss from '@astrojs/rss';
import { getSortedPosts } from '../lib/posts';

export async function GET(context) {
  const posts = await getSortedPosts();
  return rss({
    title: 'Nhật ký dev',
    description: 'After-hours notes on AI, engineering, and the developer craft.',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.titleEm ? `${post.data.title}: ${post.data.titleEm}` : post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `/${post.id}/`,
    })),
    customData: `<language>en-us</language>`,
  });
}
