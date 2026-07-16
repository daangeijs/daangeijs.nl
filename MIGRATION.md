# Astro migration — session coordination

Two Claude sessions work this branch concurrently. Division of labor:

- **Other session ("Phase" plan)**: content porting — `content/**`, `src/content.config.ts`,
  MDX shortcode conversion + its components, `netlify.toml`, `package.json` build wiring.
- **This session (task-list plan)**: design + pages — `src/styles/`, `src/layouts/`,
  `src/components/` (Header/Footer/ThemeToggle/SocialIcons/cards), `src/pages/**`,
  `public/favicon.svg`, `src/data/repos.json`.

Contract between the two:
- Collection schema = `src/content.config.ts` as committed (posts/media/publications/projects).
- URLs preserved from Hugo: `/posts/<dir>/`, `/media/<dir>/`, `/publications/<dir>/`,
  `/tags/<tag>/`, `/archives/`, `/search/`.
- Search: pagefind (already in build script). Search page = this session.
- Homepage placeholder (`src/pages/index.astro`) is replaced by this session — skip your Phase 3.

Delete this file when the migration merges.
