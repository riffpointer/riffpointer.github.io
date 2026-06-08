# Ubuntu / Debian Development Setup

This project is a Jekyll site. On Ubuntu, Debian, and their derivatives (like Linux Mint, Pop!_OS, and Elementary OS), setting up the environment involves installing Ruby, build tools for compiling native gem extensions (like `sassc`), Bundler, and configuring your environment to install packages without root permissions.

## Prerequisites

To run this project locally, you need:

- **Git**
- **Ruby** (and its development headers)
- **GCC / Make** (build tools)
- **Bundler**
- **Node.js & npm** (optional, for local linting/CI checks)

---

## Step-by-Step Installation

Follow these steps to set up the development environment on your Ubuntu or Debian system.

### 1. Update Package Lists

Make sure your package manager's cache is up to date:

```bash
sudo apt update
```

### 2. Install System Dependencies

Install Ruby, compilation tools, and other libraries required to build native gem extensions:

```bash
sudo apt install -y git ruby-full build-essential zlib1g-dev libffi-dev libssl-dev nodejs npm
```

*Note: `ruby-full` includes the Ruby interpreter, development headers (`ruby-dev`), and standard libraries required to compile C-extension gems.*

### 3. Configure Gem Installation Path (Recommended)

By default, running `gem install` requires `sudo` privileges because it tries to write to system directories. To avoid using `sudo` (which can lead to file ownership issues and security risks), configure RubyGems to install gems to your home directory:

1. Create a directory for your local gems:
   ```bash
   mkdir -p ~/gems
   ```

2. Add environment variables to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`):
   ```bash
   echo '# Custom Ruby Gem path' >> ~/.bashrc
   echo 'export GEM_HOME="$HOME/gems"' >> ~/.bashrc
   echo 'export PATH="$HOME/gems/bin:$PATH"' >> ~/.bashrc
   ```

3. Reload your terminal settings:
   ```bash
   source ~/.bashrc
   ```

### 4. Install Bundler

Install Bundler to manage the project's dependencies:

```bash
gem install bundler
```

Verify that Bundler is installed and accessible:

```bash
bundle --version
```

### 5. Clone the Repository

Clone the project and enter the repository directory:

```bash
git clone https://github.com/riffpointer/riffpointer.github.io.git
cd riffpointer.github.io
```

*Note: If you have already cloned the repository, navigate to the folder in your terminal.*

### 6. Install Jekyll and Gem Dependencies

Install the Ruby gems specified in the [Gemfile](../Gemfile):

```bash
bundle install
```

This will compile and install all required gems locally.

### 7. Run the Site Locally

Start the local Jekyll server:

```bash
bundle exec jekyll serve
```

Once the server starts, you can view the site by navigating to:

```text
http://localhost:4000
```

To include draft posts in your local build, run:

```bash
bundle exec jekyll serve --drafts
```

If port 4000 is already in use by another application, specify an alternative port:

```bash
bundle exec jekyll serve --port 4001
```

---

## Running CI Validation Checks Locally

Before pushing changes to GitHub, you can run the primary markdown linting checks locally to match what runs in the GitHub Actions CI pipeline:

```bash
bundle exec jekyll build
npx --yes markdownlint-cli2
```

---

## Troubleshooting Common Issues

### Issue: Permission Denied during `gem install` or `bundle install`
- **Cause**: Ruby is trying to install gems globally in `/var/lib/gems/` which requires root access.
- **Solution**: Follow **Step 3** to set up a local `GEM_HOME` in your home directory, or run the command with `bundle install --path vendor/bundle` (though setting `GEM_HOME` is generally preferred for a cleaner global-user workflow).

### Issue: Missing `mkmf` or native extension building fails
- **Cause**: The compiler headers for Ruby or development libraries are missing.
- **Solution**: Ensure you have installed `ruby-full` (or `ruby-dev` explicitly) and `build-essential`. Run:
  ```bash
  sudo apt install -y ruby-dev build-essential
  ```

### Issue: `jekyll` command not found
- **Cause**: The executable is not in your system `PATH`, or you tried to run `jekyll` directly instead of via Bundler.
- **Solution**: Always run commands prefixed with `bundle exec` (e.g., `bundle exec jekyll serve`), and ensure your `PATH` includes `~/gems/bin` as described in **Step 3**.

---

## Project Structure & Workflow

- **Configuration**: System configuration is defined in [`_config.yml`](../_config.yml).
- **Posts**: Markdown files for blog posts live in [`_posts/`](../_posts/).
- **Layouts**: Page structures live in [`_layouts/`](../_layouts/).
- **Includes**: Reusable HTML/Liquid components live in [`_includes/`](../_includes/).

### Standard Development Flow

1. Update your local branch: `git pull`
2. Update dependencies (if changed): `bundle install`
3. Launch local server: `bundle exec jekyll serve`
4. Preview and test your changes in the browser.
5. Check markdown formatting: `npx --yes markdownlint-cli2`
6. Commit and push your changes.
