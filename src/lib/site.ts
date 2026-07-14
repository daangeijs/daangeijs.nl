import type { CollectionEntry } from 'astro:content';

export const formatDate = (date: Date) =>
  date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

export const readingTime = (body: string) => {
  const words = body.trim().split(/\s+/).length;
  return Math.max(1, Math.round(words / 220));
};

/** Shorten an author list the way the old site did: "A and B et al." */
export const shortAuthors = (authors: string[], max = 2) => {
  const names = authors.map((a) => {
    const [last, first] = a.split(',').map((s) => s.trim());
    return first ? `${first.split(' ')[0]} ${last}` : last;
  });
  if (names.length <= max) return names.join(' and ');
  return `${names.slice(0, max).join(', ')} et al.`;
};

export const byDateDesc = <T extends { data: { date: Date } }>(a: T, b: T) =>
  b.data.date.valueOf() - a.data.date.valueOf();

export const visiblePosts = (posts: CollectionEntry<'posts'>[]) =>
  posts.filter((p) => !p.data.draft).sort(byDateDesc);

/** Hugo-compatible tag slug: lowercase, spaces to hyphens. */
export const tagSlug = (tag: string) => tag.toLowerCase().replaceAll(' ', '-');
