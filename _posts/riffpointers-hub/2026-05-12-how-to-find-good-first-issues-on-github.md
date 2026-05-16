---
layout: post
title:  "Finding Good First Issues on GitHub"
date:   2026-05-12 10:00:00 +05:30
categories: [github, issues, open-source]
tags: [github, issues, open-source]
---

Finding a **"good first issue"** is a great way to start contributing to open source, or if you're just doing it as a fun hobby, it's great as well, either way, this guide will help you find issues on GitHub tagged **"good first issue"**.

## Using GitHub's site-wide search option {: #github-search}

1. Go to [GitHub's homepage](https://github.com) and make sure you're logged in.
2. In the top navigation bar, you'll find a search bar, click on it.
3. Type `label:"good first issue" is:open` in the search bar and press <kbd>Enter</kbd> to search.
4. GitHub will show a list of issues tagged with **"good first issue"** from all public repos.
5. Append `language:<your language>` (e.g `language:python`) to the search term to filter out repositories using that language only.
6. You can add a date filter condition like `updated:>2024-01-01` to filter out old and possibly dead projects (btw that's not always the case)
7. You can also use `no:assignee` to filter out issues being worked on by other contributors.

## Using curated aggregator sites {: #aggregator-sites}

There are many sites built specifically for finding contribution opportunities on GitHub, here are some of the popular ones:
1. [Good First Issue](https://goodfirstissue.dev/): Curates easy pickings from popular open-source projects
2. [Up For Grabs](https://up-for-grabs.net/): A massive list of projects that have tasks specifically for new contributors.
3. [First Timers Only](https://www.firsttimersonly.com/): Aggregates projects that actively want help and guide you through the process.
4. [Good First Issues](https://goodfirstissues.com/): Features a live feed of the latest beginner-friendly issues.

## Practicing open-source contributions

If you've never made a Pull Request before, use a "sandbox" repository to learn the workflow without the pressure of a real project. You can lend your first contributions to repositories that are built specifically for welcoming new contributors and educating them about how open-source contribution works, such as [First Contributions](https://github.com/firstcontributions/first-contributions). This repository provides a hands-on tutorial that walks you through forking, cloning, and submitting your first PR.

Also, always read the `CONTRIBUTING.md` file in the repo for specific setup and coding standards, make sure to not miss this step or you'll be in a room full of angry project maintainers!

It's also a good practice to comment first, i.e commenting on an issue with "I'd like to work on this, can I be assigned?", or a similar request, as it will avoid duplicated effort, which can waste your precious time.

If you learned something new from this article, make sure to *share this with your friends* as well! 

***Thanks for reading!***
