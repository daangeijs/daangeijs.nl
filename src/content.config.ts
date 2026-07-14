import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const cover = (image: () => z.ZodType) =>
  z
    .object({
      image: image().optional(),
      alt: z.string().optional(),
      hidden: z.boolean().default(false),
    })
    .optional();

const posts = defineCollection({
  loader: glob({ pattern: '*/index.{md,mdx}', base: './content/posts' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.coerce.date(),
      draft: z.boolean().default(false),
      tags: z.array(z.string()).default([]),
      summary: z.string().optional(),
      description: z.string().optional(),
      cover: cover(image),
    }),
});

const media = defineCollection({
  loader: glob({ pattern: '*/index.{md,mdx}', base: './content/media' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.coerce.date(),
      draft: z.boolean().default(false),
      tags: z.array(z.string()).default([]),
      summary: z.string().optional(),
      cover: cover(image),
    }),
});

const publications = defineCollection({
  loader: glob({ pattern: '*/index.{md,mdx}', base: './content/publications' }),
  schema: z.object({
    title: z.string(),
    authors: z.array(z.string()),
    date: z.coerce.date(),
    journal: z.string().optional(),
    volume: z.string().optional(),
    number: z.string().optional(),
    pages: z.string().optional(),
    publisher: z.string().optional(),
    school: z.string().optional(),
    url: z.string().optional(),
    hidden: z.boolean().default(true),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: '*/index.{md,mdx}', base: './content/projects' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      summary: z.string(),
      description: z.string().optional(),
      thumbnail: image().optional(),
      role: z.string().optional(),
      timeframe: z.string().optional(),
      external_url: z.string().url().optional(),
      tags: z.array(z.string()).default([]),
      weight: z.number().default(100),
      draft: z.boolean().default(false),
    }),
});

export const collections = { posts, media, publications, projects };
