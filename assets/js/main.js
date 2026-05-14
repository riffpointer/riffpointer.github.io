(() => {
  const normalizePath = (value) => {
    if (!value) {
      return "/";
    }

    try {
      return new URL(value, window.location.origin).pathname.replace(/\/index\.html$/, "/");
    } catch (error) {
      return value;
    }
  };

  const buildCommandPaletteItems = () => {
    const menuLinks = Array.from(document.querySelectorAll(".menu-link")).filter(
      (link) => link.getAttribute("href")
    );
    const items = menuLinks.map((link) => {
      const isRss = link.classList.contains("rss") || link.getAttribute("href").includes("feed.xml");
      const title = isRss ? "RSS Feed" : link.textContent.trim();
      const href = link.getAttribute("href");

      return {
        title,
        href,
        description: isRss ? "Open the RSS feed" : `Go to ${title}`,
        keywords: [title, href, "navigation", isRss ? "rss" : ""].filter(Boolean),
      };
    });

    const searchLink = document.querySelector('a[href="/archive/"]');

    if (searchLink) {
      items.push({
        title: "Search archive",
        href: "/archive/",
        description: "Open the archive search page",
        keywords: ["search", "archive", "posts"],
      });
    }

    const currentPath = normalizePath(window.location.pathname);
    return items.filter((item) => normalizePath(item.href) !== currentPath || item.href === "/");
  };

  const initCommandPalette = () => {
    const palette = document.getElementById("command-palette");
    const input = document.getElementById("command-palette-input");
    const list = document.getElementById("command-palette-list");
    const empty = palette && palette.querySelector(".command-palette__empty");
    const openTriggers = Array.from(document.querySelectorAll("[data-command-palette-open]"));
    const closeTriggers = Array.from(document.querySelectorAll("[data-command-palette-close]"));

    if (!palette || !input || !list || !empty) {
      return;
    }

    const items = buildCommandPaletteItems();
    let activeIndex = 0;
    let isOpen = false;

    const render = (query = "") => {
      const normalized = query.trim().toLowerCase();
      const filtered = normalized
        ? items.filter((item) =>
            [item.title, item.href, item.description, ...(item.keywords || [])]
              .join(" ")
              .toLowerCase()
              .includes(normalized)
          )
        : items;

      list.innerHTML = "";
      empty.hidden = filtered.length > 0;

      filtered.forEach((item, index) => {
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.className = "command-palette__item";
        link.href = item.href;
        link.dataset.index = String(index);
        link.innerHTML = `<strong>${item.title}</strong><span>${item.description}</span>`;
        li.appendChild(link);
        list.appendChild(li);
      });

      activeIndex = 0;
      updateActive(filtered);
    };

    const updateActive = (filteredItems) => {
      const links = Array.from(list.querySelectorAll(".command-palette__item"));

      links.forEach((link, index) => {
        const active = index === activeIndex && filteredItems.length > 0;
        link.classList.toggle("is-active", active);
        link.setAttribute("aria-selected", active ? "true" : "false");
      });
    };

    const getFilteredItems = () =>
      Array.from(list.querySelectorAll(".command-palette__item"));

    const openPalette = () => {
      if (isOpen) {
        return;
      }

      isOpen = true;
      palette.hidden = false;
      palette.setAttribute("aria-hidden", "false");
      document.body.classList.add("command-palette-open");
      render(input.value);
      window.requestAnimationFrame(() => input.focus());
    };

    const closePalette = () => {
      if (!isOpen) {
        return;
      }

      isOpen = false;
      palette.hidden = true;
      palette.setAttribute("aria-hidden", "true");
      document.body.classList.remove("command-palette-open");
      input.value = "";
    };

    const activateCurrent = () => {
      const links = getFilteredItems();
      const current = links[activeIndex];

      if (current) {
        window.location.href = current.href;
      }
    };

    render();

    openTriggers.forEach((trigger) => trigger.addEventListener("click", openPalette));
    closeTriggers.forEach((trigger) => trigger.addEventListener("click", closePalette));

    palette.addEventListener("click", (event) => {
      if (event.target === palette || event.target.classList.contains("command-palette__backdrop")) {
        closePalette();
      }
    });

    input.addEventListener("input", () => render(input.value));
    input.addEventListener("keydown", (event) => {
      const links = getFilteredItems();

      if (event.key === "ArrowDown") {
        event.preventDefault();
        activeIndex = links.length ? (activeIndex + 1) % links.length : 0;
        updateActive(links);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        activeIndex = links.length ? (activeIndex - 1 + links.length) % links.length : 0;
        updateActive(links);
      } else if (event.key === "Enter") {
        event.preventDefault();
        activateCurrent();
      } else if (event.key === "Escape") {
        event.preventDefault();
        closePalette();
      }
    });

    document.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();

      if ((event.metaKey || event.ctrlKey) && key === "k") {
        event.preventDefault();
        if (isOpen) {
          closePalette();
        } else {
          openPalette();
        }
      }

      if (key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey) {
        const target = event.target;
        if (
          target instanceof HTMLElement &&
          (target.tagName === "INPUT" ||
            target.tagName === "TEXTAREA" ||
            target.isContentEditable)
        ) {
          return;
        }

        event.preventDefault();
        openPalette();
      }

      if (key === "escape") {
        closePalette();
      }
    });
  };

  initCommandPalette();

  // Theme switch
  const body = document.body;
  const lamp = document.getElementById("mode");

  const toggleTheme = (state) => {
    lamp.classList.remove("theme-toggle-rotating");
    void lamp.offsetWidth;
    lamp.classList.add("theme-toggle-rotating");

    if (state === "dark") {
      localStorage.setItem("theme", "light");
      body.removeAttribute("data-theme");
    } else if (state === "light") {
      localStorage.setItem("theme", "dark");
      body.setAttribute("data-theme", "dark");
    } else {
      initTheme(state);
    }
  };

  if (lamp) {
    lamp.addEventListener("click", () =>
      toggleTheme(localStorage.getItem("theme"))
    );

    lamp.addEventListener("animationend", () => {
      lamp.classList.remove("theme-toggle-rotating");
    });
  }

  // Post table of contents
  const tocRoot = document.querySelector("[data-toc]");

  if (tocRoot) {
    const tocButton = tocRoot.querySelector(".toc-button");
    const tocPanel = tocRoot.querySelector(".toc-panel");
    const tocList = tocRoot.querySelector(".toc-list");
    const tocClose = tocRoot.querySelector(".toc-close");
    const headings = Array.from(
      document.querySelectorAll(".page-content h2, .page-content h3, .page-content h4")
    ).filter((heading) => heading.id);

    if (!tocButton || !tocPanel || !tocList || headings.length < 2) {
      tocRoot.hidden = true;
    } else {
      const mobileTocQuery = window.matchMedia("(max-width: 767px)");
      const openClass = "is-open";

      const closeToc = () => {
        document.documentElement.classList.remove("toc-open");
        document.body.classList.remove("toc-open");
        tocRoot.classList.remove(openClass);
        tocButton.setAttribute("aria-expanded", "false");
        tocPanel.hidden = true;
        document.documentElement.classList.remove("toc-open");
        document.body.classList.remove("toc-open");
      };

      const openToc = () => {
        tocRoot.classList.add(openClass);
        tocButton.setAttribute("aria-expanded", "true");
        tocPanel.hidden = false;
        document.documentElement.classList.toggle("toc-open", mobileTocQuery.matches);
        document.body.classList.toggle("toc-open", mobileTocQuery.matches);
      };

      headings.forEach((heading) => {
        const item = document.createElement("a");
        item.className = `toc-link toc-link-${heading.tagName.toLowerCase()}`;
        item.href = `#${heading.id}`;
        item.textContent = heading.textContent.trim();
        item.addEventListener("click", closeToc);
        tocList.appendChild(item);
      });

      tocButton.addEventListener("click", () => {
        if (tocRoot.classList.contains(openClass)) {
          closeToc();
        } else {
          openToc();
        }
      });

      tocClose.addEventListener("click", closeToc);

      document.addEventListener("click", (event) => {
        if (!tocRoot.classList.contains(openClass)) {
          return;
        }

        if (!tocRoot.contains(event.target)) {
          closeToc();
        }
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          closeToc();
        }
      });

      mobileTocQuery.addEventListener("change", () => {
        if (!tocRoot.classList.contains(openClass)) {
          return;
        }

        document.documentElement.classList.toggle("toc-open", mobileTocQuery.matches);
        document.body.classList.toggle("toc-open", mobileTocQuery.matches);
      });
    }
  }

  // Code block copy buttons
  const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  };

  document.querySelectorAll(".highlight").forEach((highlight) => {
    const pre = highlight.querySelector("pre");
    const wrapper = highlight.closest(".highlighter-rouge") || highlight;

    if (!pre || wrapper.querySelector(".copy-code-button")) {
      return;
    }

    const button = document.createElement("button");
    button.className = "copy-code-button";
    button.type = "button";
    button.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>';
    button.setAttribute("aria-label", "Copy code to clipboard");

    button.addEventListener("click", async () => {
      try {
        await copyText(pre.innerText.trimEnd());
        button.innerHTML =
          '<i class="bi bi-check2" aria-hidden="true"></i><span>Copied</span>';
        button.classList.add("is-copied");
      } catch (error) {
        button.innerHTML =
          '<i class="bi bi-exclamation-circle" aria-hidden="true"></i><span>Failed</span>';
      }

      window.setTimeout(() => {
        button.innerHTML =
          '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>';
        button.classList.remove("is-copied");
      }, 1600);
    });

    wrapper.appendChild(button);
  });

  // Blur the content when the menu is open
  const cbox = document.getElementById("menu-trigger");

  if (cbox) {
    cbox.addEventListener("change", function () {
      const area = document.querySelector(".wrapper");
      this.checked
        ? area.classList.add("blurry")
        : area.classList.remove("blurry");
    });

    const menuOverlay = document.querySelector(".trigger");

    if (menuOverlay) {
      menuOverlay.addEventListener("click", (event) => {
        if (event.target !== menuOverlay) {
          return;
        }

        cbox.checked = false;
        cbox.dispatchEvent(new Event("change"));
      });
    }
  }

  // Dock-like proximity scaling for navbar links
  const dockRoot = document.querySelector(".trigger-container");
  const canHover = window.matchMedia("(hover: hover) and (pointer: fine)");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const dockEffect = {
    maxDistance: 92,
    maxScaleBoost: 0.24,
    maxLift: 4,
    focusExponent: 3.4,
    resetScale: 1,
    resetLift: 0,
  };

  if (
    dockRoot &&
    canHover.matches &&
    !reduceMotion.matches
  ) {
    const dockLinks = Array.from(dockRoot.querySelectorAll(".menu-link"));
    let frameId = null;
    let lastPoint = null;

    const resetDock = () => {
      dockLinks.forEach((link) => {
        link.style.setProperty("--dock-scale", String(dockEffect.resetScale));
        link.style.setProperty(
          "--dock-translate-y",
          `${dockEffect.resetLift}px`
        );
      });
    };

    const updateDock = () => {
      frameId = null;

      if (!lastPoint) {
        resetDock();
        return;
      }

      const { clientX, clientY } = lastPoint;
      dockLinks.forEach((link) => {
        const rect = link.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const distance = Math.hypot(clientX - centerX, clientY - centerY);
        const influence = Math.max(
          0,
          1 - distance / dockEffect.maxDistance
        );
        const focus = Math.pow(influence, dockEffect.focusExponent);
        const scale =
          dockEffect.resetScale + focus * dockEffect.maxScaleBoost;
        const lift = -focus * dockEffect.maxLift;

        link.style.setProperty("--dock-scale", scale.toFixed(3));
        link.style.setProperty("--dock-translate-y", `${lift.toFixed(1)}px`);
      });
    };

    const queueDockUpdate = (event) => {
      lastPoint = event;

      if (frameId) {
        return;
      }

      frameId = window.requestAnimationFrame(updateDock);
    };

    dockRoot.addEventListener("pointermove", queueDockUpdate);
    dockRoot.addEventListener("pointerleave", () => {
      lastPoint = null;
      resetDock();
    });

    resetDock();
  }
})();
