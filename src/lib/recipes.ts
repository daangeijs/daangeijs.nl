// Latest recipes from dekeukenvandael.nl, fetched at build time.
// The Hugo RSS feed has no images, so each recipe page is fetched for its og:image.
export interface Recipe {
  title: string;
  link: string;
  image: string;
  date: Date;
}

const FEED = 'https://www.dekeukenvandael.nl/index.xml';

const decode = (s: string) =>
  s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#34;|&quot;/g, '"')
    .replace(/&#39;/g, "'");

export async function latestRecipes(count = 5): Promise<Recipe[]> {
  try {
    const res = await fetch(FEED);
    if (!res.ok) return [];
    const xml = await res.text();
    const items = [...xml.matchAll(/<item>([\s\S]*?)<\/item>/g)].slice(0, count);

    const recipes = await Promise.all(
      items.map(async ([, item]) => {
        const title = decode(item.match(/<title>([\s\S]*?)<\/title>/)?.[1] ?? '');
        const link = item.match(/<link>([\s\S]*?)<\/link>/)?.[1] ?? '';
        const date = new Date(item.match(/<pubDate>([\s\S]*?)<\/pubDate>/)?.[1] ?? 0);
        let image = '';
        try {
          const page = await (await fetch(link)).text();
          image = page.match(/property="og:image" content="([^"]+)"/)?.[1] ?? '';
        } catch {
          // leave image empty; recipe gets filtered out below
        }
        return { title, link, image, date };
      })
    );

    return recipes.filter((r) => r.title && r.link && r.image);
  } catch {
    // Feed unreachable at build time: the section simply doesn't render.
    return [];
  }
}
