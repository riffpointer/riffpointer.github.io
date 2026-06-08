---
layout: post
title: Installing GitHub Desktop on Linux
date: "2026-06-08 10:00:00 +05:30"
categories: [Linux, Github, Guide]
tags: [linux, github, desktop, shiftkey, git]
---

GitHub does not provide official packages for Github Desktop for Linux. However, you can install the unofficial, community-maintained fork by **shiftkey** on various Linux distributions.

> BTW This guide uses shiftkey's package mirrors. For source or release binaries, visit the [shiftkey/desktop](https://github.com/shiftkey/desktop) repository.
{: .prompt-info }

## 1. Debian / Ubuntu & derivatives

Run the following commands to import the GPG key and add the APT repository:

```bash
# Import GPG key
wget -qO - https://apt.packages.shiftkey.dev/gpg.key | gpg --dearmor | sudo tee /usr/share/keyrings/shiftkey-packages.gpg > /dev/null

# Add APT repository
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/shiftkey-packages.gpg] https://apt.packages.shiftkey.dev/rt/debian any main" > /etc/apt/sources.list.d/shiftkey-packages.list'

# Install GitHub Desktop
sudo apt update && sudo apt install github-desktop
```

## 2. Fedora / Red Hat & derivatives

Import the GPG key and register the YUM/DNF repository config:

```bash
# Import GPG key
sudo rpm --import https://rpm.packages.shiftkey.dev/gpg.key

# Add YUM repository
sudo sh -c 'echo -e "[shiftkey-packages]\nname=GitHub Desktop for Linux\nbaseurl=https://rpm.packages.shiftkey.dev/rt/yum/any/x86_64\nenabled=1\ngpgcheck=1\ngpgkey=https://rpm.packages.shiftkey.dev/gpg.key" > /etc/yum.repos.d/shiftkey-packages.repo'

# Install GitHub Desktop
sudo dnf install github-desktop
```

## 3. Arch Linux & derivatives

GitHub Desktop is available in the Arch User Repository (AUR). You can install it using an AUR helper like `yay` or `paru`:

```bash
# Install binary version from AUR
yay -S github-desktop-bin
```

## 4. Flatpak

Alternatively, you can install the Flatpak package from Flathub:

```bash
flatpak install flathub io.github.shiftey.Desktop
```
