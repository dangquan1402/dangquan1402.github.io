# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- Static GitHub Pages site, no build step. Pushing to `main` publishes the repo root via `.github/workflows/gh-pages.yml`; anything that must not go live (tooling, docs, this file) belongs in its `exclude_assets` list.
- Root `index.html` is a redirect to the LLM notes; changing it is the owner's decision. `/llm-engineering-notes/` is served by a different repo.
- Run `python3 scripts/check_site.py` after any page change (CI runs it on PRs): JSON-LD parses, internal links resolve, every page is in `sitemap.xml`, robots.txt names the AI crawlers, and banned claims are absent.
- App pages may state only shipped features. Never add ratings/`aggregateRating`, download counts, awards, "best"/"#1", or iCloud sync, and never name competitor apps. How-to articles link Apple's support docs for built-in routes instead of writing iOS menu steps from memory.
- Do not edit the policy text of the `privacy.html` pages.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
