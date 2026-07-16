[![Netlify Status](https://api.netlify.com/api/v1/badges/47ad4c41-9dcf-4a49-b2f7-dde625aa801c/deploy-status)](https://app.netlify.com/sites/daangeijs/deploys)

# daangeijs.nl

Source code of https://daangeijs.nl — my personal website. Built with [Astro](https://astro.build/) and deployed on Netlify.

## Develop

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # static output in dist/ (runs Pagefind indexing)
npm run preview
```

## Structure

- `content/` — markdown/MDX content: `posts`, `media`, `publications`, `projects` (Astro content collections, see `src/content.config.ts`)
- `src/pages/` — routes; `src/components/`, `src/layouts/`, `src/styles/` — UI
- `src/pages/index.xml.ts` — RSS feed at `/index.xml`
- Search is [Pagefind](https://pagefind.app/), built from `dist/` after `astro build`
