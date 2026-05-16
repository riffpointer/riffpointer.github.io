# Local Setup, Build, Serve, and Deploy

This repository is a Jekyll site deployed through GitHub Pages.

## Prerequisites

Install the following before working on the site:

- Git
- Ruby
- Bundler
- A terminal such as PowerShell, Windows Terminal, or a Unix shell

Optional:

- Node.js, if you want to run the CI checks locally
- Visual Studio Build Tools on Windows, if native gems need compilation

## Clone The Repository

```powershell
git clone https://github.com/riffpointer/riffpointer.github.io.git
cd riffpointer.github.io
```

## Install Dependencies

```powershell
bundle install
```

If Bundler reports missing native extensions, install the platform build tools your Ruby setup requires and run `bundle install` again.

## Build The Site

```powershell
bundle exec jekyll build
```

This writes the generated site to `_site/`.

## Serve The Site Locally

```powershell
bundle exec jekyll serve
```

Then open:

```text
http://localhost:4000
```

To include drafts during local preview:

```powershell
bundle exec jekyll serve --drafts
```

If port 4000 is already in use, choose another port:

```powershell
bundle exec jekyll serve --port 4001
```

## Run The Same Checks Used In CI

The CI workflow runs the site build plus link, HTML, markdown, and accessibility checks. To mirror the most important local checks:

```powershell
bundle exec jekyll build
npx --yes markdownlint-cli2
```

The link, HTML, and Lighthouse checks depend on a built `_site/` directory and browser tooling, so they are best run in the same environment as CI when you need full parity.

## Deploy

Deployment is automatic.

Push changes to `main`, and GitHub Actions runs the site build and validation workflow before publishing the site to GitHub Pages.

If the workflow fails, fix the reported issue locally, rebuild, and push again.

## Windows Notes

If you are setting up on Windows, the repository also has a dedicated guide in [Windows Development Setup](windows-development-setup.md) with OS-specific installation steps and troubleshooting.
