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
    const pre = h.querySelector(".rouge-code pre") || h.querySelector("pre");
    const wrap = h.closest(".highlighter-rouge") || h;
    if (!pre || wrap.querySelector(".copy-code-button")) return;
    const b = document.createElement("button");
    b.className = "copy-code-button";
    b.type = "button";
    b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>';
    b.addEventListener("click", async () => {
      try {
        await copyText(pre.innerText.trimEnd());
        b.innerHTML = '<i class="bi bi-check2" aria-hidden="true"></i><span>Copied</span>';
        b.classList.add("is-copied");
      } catch (e) {
        b.innerHTML = '<i class="bi bi-exclamation-circle" aria-hidden="true"></i><span>Failed</span>';
      }
      window.setTimeout(() => {
        b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>';
        b.classList.remove("is-copied");
      }, 1600);
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

  const projectSearch = document.getElementById("search-input");
  const projectGrid = document.getElementById("project-grid");
  const viewToggle = document.getElementById("view-toggle");
  const noProjectsFound = document.getElementById("no-projects-found");

  if (projectSearch && projectGrid && viewToggle) {
    const cards = Array.from(document.querySelectorAll(".project-card"));

    const updateView = (view) => {
      const isList = view === "list";
      projectGrid.classList.toggle("is-list", isList);
      viewToggle.setAttribute("aria-pressed", isList ? "true" : "false");
      viewToggle.setAttribute("aria-label", isList ? "Switch to grid view" : "Switch to list view");
      viewToggle.setAttribute("title", isList ? "Switch to grid view" : "Switch to list view");
      viewToggle.innerHTML = isList ? '<i class="bi bi-list" aria-hidden="true"></i>' : '<i class="bi bi-grid-fill" aria-hidden="true"></i>';
    };

    let currentView = "grid";
    try {
      currentView = localStorage.getItem("project-view") || "grid";
    } catch (error) {}
    updateView(currentView);

    viewToggle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      currentView = currentView === "grid" ? "list" : "grid";
      updateView(currentView);
      try {
        localStorage.setItem("project-view", currentView);
      } catch (error) {}
    });

    projectSearch.addEventListener("input", () => {
      const searchTerm = projectSearch.value.toLowerCase().trim();
      let visibleCount = 0;

      cards.forEach((card) => {
        const text = card.textContent.toLowerCase();
        const isMatch = text.includes(searchTerm);
        card.hidden = !isMatch;
        if (isMatch) visibleCount++;
      });

      if (noProjectsFound) {
        noProjectsFound.hidden = visibleCount !== 0;
      }
    });
  }
})();
