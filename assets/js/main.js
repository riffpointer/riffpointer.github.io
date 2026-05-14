(() => {
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
