# Windows Development Setup

This project is a Jekyll site. On Windows, the main setup work is getting Ruby, Bundler, and the required build tools installed correctly.

## Prerequisites

Install these tools first:

- Git for Windows
- Ruby for Windows
- Bundler
- A terminal such as Windows Terminal or PowerShell

Optional, but useful:

- Visual Studio Build Tools
- Node.js, if you want to inspect or extend any front-end tooling

## Recommended Ruby Version

Use a recent stable Ruby version that is compatible with your Jekyll and gem dependencies. This repository is currently pinned to Jekyll 4.3.4, and the bundle is set up to use the older `sassc`-based Sass converter path so `bundle exec jekyll serve` works cleanly on Windows.

## 1. Install Git

Install Git for Windows from: https://git-scm.com/download/win

After installation, confirm it works:

```powershell
git --version
```

## 2. Install Ruby

Install Ruby for Windows from: https://rubyinstaller.org/

Choose the version with the DevKit option if it is available during setup.

After installation, confirm Ruby is available:

```powershell
ruby --version
gem --version
```

If the installer offers to run MSYS2 and MINGW development toolchain setup, accept it. Some Ruby gems used by Jekyll may need native build tools.

## 3. Install Bundler

Install Bundler if it is not already present:

```powershell
gem install bundler
```

Verify it:

```powershell
bundle --version
```

## 4. Clone the Repository

Clone the project and enter the repository:

```powershell
git clone https://github.com/riffpointer/riffpointer.github.io.git
cd riffpointer.github.io
```

If you already have the repository locally, just open the project folder in PowerShell.

## 5. Install Dependencies

Install the Ruby gems required by the site:

```powershell
bundle install
```

If bundler reports missing native extensions or build tools, install Visual Studio Build Tools and retry.

## 6. Run the Site Locally

Start the local Jekyll server:

```powershell
bundle exec jekyll serve
```

Then open:

```text
http://localhost:4000
```

If you want drafts included in the local build, use:

```powershell
bundle exec jekyll serve --drafts
```

## Common Windows Issues

- `bundle install` fails with native extension errors: install Visual Studio Build Tools and make sure MSYS2 was completed during Ruby setup.
- `jekyll` is not recognized: use `bundle exec jekyll serve` instead of calling `jekyll` directly.
- Port 4000 is already in use: rerun with a different port.

```powershell
bundle exec jekyll serve --port 4001
```

- Git line endings produce noisy diffs: keep Git configured for your preferred line-ending behavior before committing.

## Project Notes

- Site configuration lives in [`_config.yml`](../_config.yml).
- Posts live in [`_posts/`](../_posts/).
- Shared layouts live in [`_layouts/`](../_layouts/).
- Reusable includes live in [`_includes/`](../_includes/).

## Suggested Workflow

1. Pull the latest changes.
2. Run `bundle install` if dependencies changed.
3. Start the local server with `bundle exec jekyll serve`.
4. Make your edits.
5. Verify the site in a browser.
6. Commit only the intended changes.

## Deployment Reminder

This repository is hosted on GitHub Pages-style infrastructure, so keep in mind that not every local plugin or build-time dependency may be available in production.
