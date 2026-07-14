import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';
import { byDateDesc } from '../lib/site';

// Feed lives at /index.xml — the Hugo-era URL existing subscribers use.
export async function GET(context: APIContext) {
  const posts = (await getCollection('posts', ({ data }) => !data.draft)).map((p) => ({
    title: p.data.title,
    pubDate: p.data.date,
    description: p.data.description ?? p.data.summary,
    link: `/posts/${p.id}/`,
  }));
  const media = (await getCollection('media', ({ data }) => !data.draft)).map((m) => ({
    title: m.data.title,
    pubDate: m.data.date,
    description: m.data.summary,
    link: `/media/${m.id}/`,
  }));

  const items = [...posts, ...media].sort(
    (a, b) => b.pubDate.valueOf() - a.pubDate.valueOf()
  );

  return rss({
    title: 'Daan Geijs',
    description:
      'Writing and media appearances by Daan Geijs — product discovery, machine learning, and AI in the clinic.',
    site: context.site!,
    items,
    customData: '<language>en</language>',
  });
}
