(() => {
  const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const t = document.createElement("textarea");
    t.value = text;
    t.setAttribute("readonly", "");
    t.style.position = "fixed";
    t.style.left = "-9999px";
    document.body.appendChild(t);
    t.select();
    document.execCommand("copy");
    t.remove();
  };

  const tocRoot = document.querySelector("[data-toc]");
  if (tocRoot) {
    const btn = tocRoot.querySelector(".toc-button");
    const pnl = tocRoot.querySelector(".toc-panel");
    const lst = tocRoot.querySelector(".toc-list");
    const cls = tocRoot.querySelector(".toc-close");
    const heads = Array.from(document.querySelectorAll(".page-content h2, .page-content h3, .page-content h4")).filter((h) => h.id);
    if (!btn || !pnl || !lst || heads.length < 2) {
      tocRoot.hidden = true;
    } else {
      const mQ = window.matchMedia("(max-width: 767px)");
      const oC = "is-open";
      const cT = () => {
        document.documentElement.classList.remove("toc-open");
        document.body.classList.remove("toc-open");
        tocRoot.classList.remove(oC);
        btn.setAttribute("aria-expanded", "false");
        pnl.hidden = true;
      };
      const oT = () => {
        tocRoot.classList.add(oC);
        btn.setAttribute("aria-expanded", "true");
        pnl.hidden = false;
        document.documentElement.classList.toggle("toc-open", mQ.matches);
        document.body.classList.toggle("toc-open", mQ.matches);
      };
      heads.forEach((h) => {
        const a = document.createElement("a");
        a.className = `toc-link toc-link-${h.tagName.toLowerCase()}`;
        a.href = `#${h.id}`;
        
        const clone = h.cloneNode(true);
        const anchor = clone.querySelector(".anchor-head");
        if (anchor) anchor.remove();
        a.textContent = clone.textContent.trim();

        a.addEventListener("click", cT);
        lst.appendChild(a);
      });
      btn.addEventListener("click", () => tocRoot.classList.contains(oC) ? cT() : oT());
      cls.addEventListener("click", cT);
      document.addEventListener("click", (e) => {
        if (!tocRoot.classList.contains(oC)) return;
        if (!tocRoot.contains(e.target)) cT();
      });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape") cT(); });
      mQ.addEventListener("change", () => {
        if (!tocRoot.classList.contains(oC)) return;
        document.documentElement.classList.toggle("toc-open", mQ.matches);
        document.body.classList.toggle("toc-open", mQ.matches);
      });
    }
  }

  document.querySelectorAll(".highlight").forEach((h) => {
    // Robustly find the pre element
    let pre = h.tagName === "PRE" ? h : h.querySelector("pre");
    if (!pre && h.classList.contains("rouge-code")) {
      pre = h.querySelector("pre");
    }
    
    // Find the best container for the button
    const wrap = h.closest("div.highlighter-rouge, figure.highlight") || (pre ? pre.parentElement : h);
    if (!pre || !wrap || wrap.querySelector(".copy-code-button")) return;
    
    // Ensure the container is ready for absolute positioning
    if (window.getComputedStyle(wrap).position === "static") {
      wrap.style.position = "relative";
    }

    const b = document.createElement("button");
    b.className = "copy-code-button";
    b.type = "button";
    b.title = "Copy";
    b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i>';
    let copyCount = 0;
    let lastCopyTime = 0;
    b.addEventListener("click", async () => {
      const now = Date.now();
      
      // Debounce only the clipboard instruction (1s)
      if (now - lastCopyTime > 1000) {
        try {
          await copyText(pre.innerText.trimEnd());
          lastCopyTime = now;
        } catch (e) {
          console.error("Copy failed", e);
          b.innerHTML = '<i class="bi bi-exclamation-circle" aria-hidden="true"></i>';
          b.title = "Failed";
          return;
        }
      }

      copyCount++;
      
      // Get absolute coordinates
      const rect = h.getBoundingClientRect();
      const wrapRect = wrap.getBoundingClientRect();
      
      // Get border widths to adjust relative positioning
      const wrapStyle = window.getComputedStyle(wrap);
      const borderLeft = parseFloat(wrapStyle.borderLeftWidth) || 0;
      const borderTop = parseFloat(wrapStyle.borderTopWidth) || 0;
      
      // Destination is exactly where the button is positioned
      const destTop = b.offsetTop;
      const destLeft = b.offsetLeft;
      
      // Initial state relative to wrapper's internal coordinate system
      // Align exactly with the code block's position
      const startTop = rect.top - wrapRect.top - borderTop;
      const startLeft = rect.left - wrapRect.left - borderLeft;
      
      // Screenshot animation
      const snapshot = h.cloneNode(true);
      const aniWrap = document.createElement("div");
      aniWrap.className = "copy-screenshot-snapshot";
      
      // Set initial state and destination variables
      aniWrap.style.width = `${rect.width}px`;
      aniWrap.style.height = `${rect.height}px`;
      aniWrap.style.top = `${startTop}px`;
      aniWrap.style.left = `${startLeft}px`;
      aniWrap.style.setProperty("--dest-top", `${destTop}px`);
      aniWrap.style.setProperty("--dest-left", `${destLeft}px`);

      // Lock snapshot content to original size to prevent reflow during shrink
      snapshot.style.width = `${rect.width}px`;
      snapshot.style.height = `${rect.height}px`;
      snapshot.style.margin = "0";
      
      // Calculate dynamic scale factors to fit inside the 1.5px border (28 - 3 = 25)
      const scaleX = 25 / rect.width;
      const scaleY = 25 / rect.height;
      aniWrap.style.setProperty("--scale-x", scaleX);
      aniWrap.style.setProperty("--scale-y", scaleY);

      aniWrap.appendChild(snapshot);
      
      // Independent flash element
      const flash = document.createElement("div");
      flash.className = "copy-flash-overlay";
      
      wrap.appendChild(flash);
      wrap.appendChild(aniWrap);
      
      // Force a style calculation
      void aniWrap.offsetWidth;
      
      // Cleanup flash
      setTimeout(() => flash.remove(), 240);
      
      // Trigger animation
      requestAnimationFrame(() => {
        aniWrap.classList.add("is-shrinking");
      });

      // Cleanup snapshot after animation ends (800ms transition)
      setTimeout(() => {
        aniWrap.remove();
        // Button state - show after animation ends
        b.innerHTML = '<i class="bi bi-check2" aria-hidden="true"></i>';
        b.title = "Copied";
        b.classList.add("is-copied");
      }, 800);

      window.setTimeout(() => {
        copyCount--;
        if (copyCount <= 0) {
          copyCount = 0;
          b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i>';
          b.title = "Copy";
          b.classList.remove("is-copied");
        }
      }, 2400); 
    });
    wrap.appendChild(b);
  });

  const mTrig = document.getElementById("menu-trigger");
  if (mTrig) {
    const syncMenuState = () => {
      const isOpen = mTrig.checked;
      mTrig.setAttribute("aria-expanded", isOpen ? "true" : "false");
      mTrig.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    };
    syncMenuState();
    mTrig.addEventListener("change", function () {
      syncMenuState();
    });
    const mOver = document.querySelector(".trigger");
    if (mOver) mOver.addEventListener("click", (e) => { if (e.target === mOver) { mTrig.checked = false; mTrig.dispatchEvent(new Event("change")); } });
  }

  const dRoot = document.querySelector(".trigger-container");
  const canH = window.matchMedia("(hover: hover) and (pointer: fine)");
  const rMot = window.matchMedia("(prefers-reduced-motion: reduce)");
  const dEff = { maxD: 92, boost: 0.24, lift: 4, exp: 3.4 };
  if (dRoot && canH.matches && !rMot.matches) {
    const dLinks = Array.from(dRoot.querySelectorAll(".menu-link"));
    let fId = null, lP = null;
    const updD = () => {
      fId = null;
      if (!lP) {
        dLinks.forEach((l) => {
          l.style.setProperty("--dock-scale", "1");
          l.style.setProperty("--dock-translate-y", "0px");
        });
        return;
      }
      dLinks.forEach((l) => {
        const r = l.getBoundingClientRect();
        const d = Math.hypot(lP.clientX - (r.left + r.width / 2), lP.clientY - (r.top + r.height / 2));
        const inf = Math.max(0, 1 - d / dEff.maxD);
        const foc = Math.pow(inf, dEff.exp);
        l.style.setProperty("--dock-scale", (1 + foc * dEff.boost).toFixed(3));
        l.style.setProperty("--dock-translate-y", `${(-foc * dEff.lift).toFixed(1)}px`);
      });
    };
    dRoot.addEventListener("pointermove", (e) => { lP = e; if (!fId) fId = requestAnimationFrame(updD); });
    dRoot.addEventListener("pointerleave", () => { lP = null; updD(); });
  }

  // Projects search and filtering
  const projectSearch = document.getElementById("project-search");
  const projectGrid = document.getElementById("project-grid-new");
  const projectCategories = document.getElementById("project-categories");
  const projectsEmptyState = document.getElementById("projects-empty-state");

  if (projectSearch && projectGrid && projectCategories) {
    const cards = Array.from(projectGrid.querySelectorAll(".project-card-new"));
    const categoryBtns = Array.from(projectCategories.querySelectorAll(".category-btn"));
    let currentCategory = "all";

    const filterProjects = () => {
      const searchTerm = projectSearch.value.toLowerCase().trim();
      let visibleCount = 0;

      cards.forEach((card) => {
        const cardCategory = card.getAttribute("data-category");
        const cardText = card.textContent.toLowerCase();

        const matchesCategory = currentCategory === "all" || cardCategory === currentCategory;
        const matchesSearch = cardText.includes(searchTerm);

        const isVisible = matchesCategory && matchesSearch;
        card.hidden = !isVisible;

        if (isVisible) {
          visibleCount++;
        }
      });

      if (projectsEmptyState) {
        projectsEmptyState.hidden = visibleCount !== 0;
      }
    };

    // Category button click handlers
    projectCategories.addEventListener("click", (event) => {
      const btn = event.target.closest(".category-btn");
      if (!btn) return;

      categoryBtns.forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");

      currentCategory = btn.getAttribute("data-category") || "all";
      
      // Update URL query parameter
      try {
        const url = new URL(window.location);
        if (currentCategory === "all") {
          url.searchParams.delete("category");
        } else {
          url.searchParams.set("category", currentCategory);
        }
        window.history.replaceState({}, "", url);
      } catch (e) {}

      filterProjects();
    });

    // Search input handler
    projectSearch.addEventListener("input", filterProjects);

    // Check query params on load
    try {
      const params = new URLSearchParams(window.location.search);
      const catParam = params.get("category");
      if (catParam) {
        const targetBtn = categoryBtns.find((b) => b.getAttribute("data-category") === catParam);
        if (targetBtn) {
          categoryBtns.forEach((b) => b.classList.remove("is-active"));
          targetBtn.classList.add("is-active");
          currentCategory = catParam;
          filterProjects();
        }
      }
    } catch (e) {}
  }

  // Resources search and filtering
  const resourcesSearch = document.getElementById("resources-search");
  const resourcesGrid = document.getElementById("resources-grid");
  const resourcesCategories = document.getElementById("resources-categories");
  const resourcesEmptyState = document.getElementById("resources-empty-state");

  if (resourcesSearch && resourcesGrid && resourcesCategories) {
    const cards = Array.from(resourcesGrid.querySelectorAll(".resource-card"));
    const categoryBtns = Array.from(resourcesCategories.querySelectorAll(".category-btn"));
    let currentCategory = "all";

    const filterResources = () => {
      const searchTerm = resourcesSearch.value.toLowerCase().trim();
      let visibleCount = 0;

      cards.forEach((card) => {
        const cardCategory = card.getAttribute("data-category");
        const cardText = card.textContent.toLowerCase();

        const matchesCategory = currentCategory === "all" || cardCategory === currentCategory;
        const matchesSearch = cardText.includes(searchTerm);

        const isVisible = matchesCategory && matchesSearch;
        card.hidden = !isVisible;

        if (isVisible) {
          visibleCount++;
        }
      });

      if (resourcesEmptyState) {
        resourcesEmptyState.hidden = visibleCount !== 0;
      }
    };

    // Category button click handlers
    resourcesCategories.addEventListener("click", (event) => {
      const btn = event.target.closest(".category-btn");
      if (!btn) return;

      categoryBtns.forEach((b) => b.classList.remove("is-active"));
      btn.classList.add("is-active");

      currentCategory = btn.getAttribute("data-category") || "all";
      
      // Update URL query parameter
      try {
        const url = new URL(window.location);
        if (currentCategory === "all") {
          url.searchParams.delete("category");
        } else {
          url.searchParams.set("category", currentCategory);
        }
        window.history.replaceState({}, "", url);
      } catch (e) {}

      filterResources();
    });

    // Search input handler
    resourcesSearch.addEventListener("input", filterResources);

    // Check query params on load
    try {
      const params = new URLSearchParams(window.location.search);
      const catParam = params.get("category");
      if (catParam) {
        const targetBtn = categoryBtns.find((b) => b.getAttribute("data-category") === catParam);
        if (targetBtn) {
          categoryBtns.forEach((b) => b.classList.remove("is-active"));
          targetBtn.classList.add("is-active");
          currentCategory = catParam;
          filterResources();
        }
      }
    } catch (e) {}
  }
})();
