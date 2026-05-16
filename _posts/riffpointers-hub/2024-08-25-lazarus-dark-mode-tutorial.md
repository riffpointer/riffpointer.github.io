---
title: "Lazarus Dark Mode Tutorial (Windows)"
date: 2024-08-25 12:00:00 +05:30
categories: ["Lazarus", "Windows", "Tutorial", "FreePascal"]
tags: ["lazarus", "dark-mode", "tutorial", "pascal", "fpc", "windows", "ide"]
---

Hey there, fellow developer! If you're like me and spend hours coding away in Lazarus, you know that a bright white screen can be a bit much for the eyes. Today is a great day because I'm going to help you bring some stylish dark mode goodness to your Lazarus IDE and your own LCL applications on Windows!

> **Quick Note:** This specific guide is just for my friends on **Windows**. If you're on Linux or macOS, you're in luck; your system theme usually handles this automatically!
{: .prompt-info }

# Lazarus IDE Configuration

Before we dive in, let's make sure we're all set for success! It's always a good idea to have the latest version of Lazarus installed. Make sure you're using the right version for your computer (like the 64-bit version for 64-bit Windows) and that you've already flipped the "Dark Mode" switch in your Windows settings. A fresh install of Lazarus works best to keep things simple and smooth!

## Installation Steps

1. Fire up your Lazarus IDE.
2. Head over to the [metadarkstyle GitHub page](https://github.com/zamtmn/metadarkstyle/) and grab the `metadarkstyle` package. Just follow the friendly instructions there!
3. Once you've installed it, go ahead and rebuild the IDE. It only takes a moment!

## Final Setup

Now for the fun part! Go to **Tools > Options** and look for **Dark Style** under **Environment**. Set the `PreferredAppMode` to `Allow Dark`, give the IDE a quick restart, and—voila!—you've got a beautiful dark workspace.

# Application Implementation

You don't have to keep all that style to yourself! You can easily add dark mode to the apps you build for others too.

1. Open your project and make sure you've installed the packages mentioned above.
2. Pop open **Project > Project Inspector...**.
3. Click **Add > New Requirement**.
4. Search for and add both `metadarkstyle` and `metadarkstyledsgn`.
5. Now, open your main project file (the one ending in `.lpr`).
6. In the `uses` section, add these three friendly helpers:
```pascal
uses
  // ...
  uDarkStyleParams,
  uMetaDarkStyle,
  uDarkStyleSchemes;
```
7. Right after the `begin` statement, add these two lines to tell your app to embrace the dark side:
```pascal
PreferredAppMode := pamAllowDark;
uMetaDarkStyle.ApplyMetaDarkStyle(DefaultDark);
```
8. Hit run and enjoy your sleek new creation!

I hope this guide helps you feel more comfortable while you're building amazing things. Happy coding, and have a wonderful day!
