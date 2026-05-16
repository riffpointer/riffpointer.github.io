# Blog Issues And Missing Essential Features

Audit date: 2026-05-16

Build status checked with `bundle exec jekyll build`: passes.

## Critical Issues

2. Open Graph image points to `assets/img/ogp.png`, but that file is not present. Shared links can show a missing or broken preview image.
4. Post Open Graph type is wrong. Blog posts are emitted as `og:type="website"` because the template checks `page.location` instead of the post layout/type.
5. The default social metadata still contains theme placeholders such as `Jekyll Klise` for app names and tile metadata.
6. Several source strings show mojibake for the Klise theme name, which makes the footer, README, and posts look unpolished.
7. `fb:app_id`, `twitter:site`, and `twitter:creator` are rendered even when their config values are empty. This produces low-quality metadata like `@`.
8. The web app manifest icon paths are wrong. The manifest references `/android-chrome-192x192.png` and `/android-chrome-384x384.png`, but the actual files are under `/assets/favicons/`.
9. The site lacks a public `robots.txt` source file even though `_site/robots.txt` exists from generated output. This should be controlled explicitly in source.
10. There is no visible privacy policy or analytics/comment disclosure, despite loading third-party scripts when MathJax, Giscus, or analytics are enabled.

## SEO And Sharing Gaps

1. Most posts do not have explicit `description` front matter, so archive/search/social descriptions fall back to excerpts.
2. Posts do not have per-post social preview images.
3. There is no dedicated default Open Graph image asset in the source tree.
4. `twitter:card` is always `summary`; richer post sharing would usually use `summary_large_image` when a valid image is available.
5. Posts do not expose complete structured data. Existing hidden schema fields use plain spans and incomplete values instead of proper JSON-LD.
6. `dateModified` is emitted with an empty datetime when `page.modified` is not set.
7. `publisher`, `image`, and `mainEntityOfPage` structured-data fields are incomplete or invalid.
8. Tags exist at `/tags/`, but the Tags page is not in the main navigation.
9. The command palette links to `/tags.html`, while the actual permalink is `/tags/`.
10. There is no `series`, `category`, or related-post discovery flow for readers who finish an article.

## Accessibility Issues

1. There is no skip-to-content link.
2. The theme toggle is an `<a id="mode">` without `href`, `role="button"`, `aria-label`, or pressed state.
3. The mobile menu checkbox and label do not expose an accessible name or expanded state.
4. Several decorative SVGs are not consistently marked with `aria-hidden="true"` or given accessible labels.
5. The command palette uses a dialog. Requirement: when it opens, Tab and Shift+Tab must stay within the dialog, and focus must return to the trigger after close.
6. Command palette result items use `aria-selected`, but the containing list is not clearly modeled as a listbox/menu pattern.
7. Game modules inside the command palette are canvas-heavy and lack keyboard instructions or text alternatives.
8. The projects view toggle only has a static `aria-label="Toggle View"` and does not expose current state.
9. Search result empty states are hidden visually with inline styles in some places instead of a consistent accessible state.
10. The homepage starts the content area with an `h3`, skipping earlier heading levels.

## Content And Navigation Gaps

1. The homepage only lists recent posts and does not explain the blog's purpose beyond the author card.
2. There is no featured projects section on the homepage.
3. There is no latest/featured article callout.
4. There is no clear call-to-action for YouTube, GitHub projects, or contact on the homepage.
5. Project cards link directly to GitHub, but there are no project detail pages with screenshots, status, demos, changelogs, or writeups.
6. Project entries do not include status values such as active, paused, archived, or complete.
7. Project entries do not include last-updated dates.
8. Project entries do not include repository health signals such as license, stars, language, or release status.
9. The About page is very short and does not include a clear author bio, skills, interests, or what readers should expect.
10. The 404 page is minimal and should provide navigation back to home, archive, projects, and search.
11. There is no Now page for current work.
12. There is no Uses page for tools/software/hardware.
13. There is no Resources or Bookmarks page.
14. There is no public roadmap or changelog page for site updates.
15. There is no post publishing checklist for front matter, metadata, images, tags, and links.

## Search And Discovery Gaps

1. Archive search exists, but there is no global search entry in the main navigation.
2. The command palette searches navigation and posts, but not project data in the embedded JSON.
3. `assets/search.json` includes projects, but the archive page labels the search as article search and visually lists posts below it.
4. Tag filtering is only available on a separate tags page, not on the archive page.
5. Tags are based on post front matter only; older posts use `categories` but no `tags`, so they are not discoverable by tag. port them to tags
6. There is no related posts section.
7. There is no related projects section.
8. There is no popular posts or recommended reading section.
9. There is no archive pagination or grouping beyond year headings.
10. There is no search fallback message that clearly separates "no posts" from "no projects".

## Performance And Maintainability Issues

1. The command palette HTML is large and is injected into every page through the footer, even when the visitor does not use it.
2. Hidden game modules and canvas markup are shipped on every page.
3. `assets/js/main.js` contains many unrelated responsibilities in one file: theme, command palette, games, table of contents, copy buttons, and modules.
4. Some command palette actions use `javascript:` URLs, which is harder to secure, test, and reason about than event-driven buttons/actions.
5. Projects page behavior is implemented inline in `projects.html` instead of being centralized with the rest of the JavaScript.
6. Search and project filtering manipulate `style.display` directly instead of using state classes.
7. External scripts are loaded for comments and MathJax when enabled, but there is no documented performance budget or loading policy.
8. There is no automated link checker in CI.
9. There is no HTML validation step in CI.
10. There is no Lighthouse or accessibility audit workflow in CI.
11. There is no Markdown linting for posts and docs.
12. The README lacks complete local setup, build, serve, and deployment instructions. (Create a document for it in docs/ and link to it in readme)

## Missing Essential Features

1. Add a source-controlled `robots.txt`.
2. Add a real default Open Graph image and per-post image support.
3. Add a skip-to-content link.
4. Add accessible theme-toggle and mobile-menu controls.
5. Add explicit exclusions for internal-only folders such as `docs/`, `tools/`, `.bundle/`, `.jekyll-cache/`, and generated `_site/`.
6. Add a privacy page explaining comments, analytics, embeds, and external links.
7. Add project detail pages.
8. Add project metadata fields: status, repository URL, demo URL, screenshot, updated date, tech stack, and featured flag.
9. Add global search or make the command palette clearly discoverable as global search.
10. Add related posts and related projects.
11. Add a stronger homepage with intro, featured projects, recent posts, and contact/social actions.
12. Add a post template checklist for title, description, tags, image, modified date, and accessibility checks.
13. Add CI checks for build, links, HTML validity, and accessibility smoke tests.
14. Add documentation for deployment and local development.
15. Add a custom 404 page with useful links and search/discovery options.

## Suggested Fix Order

1. Fix publishing/exclusions so internal docs and tools are not deployed.
2. Fix broken metadata: `url`, Open Graph image, manifest icon paths, placeholder app names, and empty social tags.
3. Fix post metadata and structured data for blog posts.
4. Add accessibility basics: skip link, proper buttons, mobile menu state, and homepage heading order.
5. Add a stronger homepage and expose Tags/global search in navigation.
6. Add project detail pages and richer project metadata.
7. Split large JavaScript features and reduce always-loaded footer payload.
8. Add CI checks for links, HTML, accessibility, and Lighthouse.
