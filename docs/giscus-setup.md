# Giscus Setup

This site supports comments through [Giscus](https://giscus.app/). If the required values are missing from `_config.yml`, the post page shows a warning box instead of the embedded comment section.

## What Giscus Needs

Add these values under `giscus:` in [`_config.yml`](../_config.yml):

- `repo`
- `repo_id`
- `category`
- `category_id`

Example:

```yml
giscus:
  repo: riffpointer/riffpointer.github.io
  repo_id: YOUR_REPO_ID
  category: General
  category_id: YOUR_CATEGORY_ID
  mapping: pathname
  strict: 0
  reactions_enabled: 1
  emit_metadata: 0
  input_position: bottom
  theme: preferred_color_scheme
  lang: en
  loading: lazy
```

## How To Get The Values

1. Go to [giscus.app](https://giscus.app/).
2. Select the repository you want to use. 
3. Make sure the Giscus GitHub App is installed on that repository.
4. Choose the discussion category that will store comments.
5. Copy the generated repository and category IDs into `_config.yml`.

## Required Repository Settings

Giscus only works if the repository is configured correctly:

- The repository must be public.
- The Giscus GitHub App must be installed.
- Discussions must be enabled in the repository.
- The selected discussion category must allow Giscus to create or map discussions.

## Site Behavior

The comments section is included on post pages unless a post explicitly sets `comments: false`.

If Giscus is not configured correctly, the site shows a warning that lists the missing fields. For example:

- `repo`
- `category_id`

That warning means the comment section is intentionally disabled until the missing values are filled in.

## Troubleshooting

- If no comments appear, check `_config.yml` first.
- If the warning names a field, that field is empty or missing.
- If the embed loads but no discussion appears, verify the repository and category you selected in Giscus.
- If the page is not showing comments at all, confirm the post does not have `comments: false` in front matter.

## Related Files

- [`_includes/comments.html`](../_includes/comments.html)
- [`_layouts/post.html`](../_layouts/post.html)
- [`_config.yml`](../_config.yml)
