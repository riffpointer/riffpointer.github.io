(() => {
  const COMMAND_PALETTE_SCRIPT =
    document.currentScript?.dataset.commandPaletteScript || "/assets/js/command-palette.js";
  let commandPaletteScriptPromise = null;

  const isCommandPaletteLoaded = () => Boolean(window.CommandPaletteAPI?.loaded);

  const loadCommandPaletteScript = () => {
    if (isCommandPaletteLoaded()) return Promise.resolve(true);
    if (!commandPaletteScriptPromise) {
      commandPaletteScriptPromise = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = COMMAND_PALETTE_SCRIPT;
        script.defer = true;
        script.dataset.commandPaletteScript = "true";
        script.addEventListener("load", () => resolve(true), { once: true });
        script.addEventListener("error", () => reject(new Error("Failed to load command palette script")), { once: true });
        document.head.appendChild(script);
      }).catch((error) => {
        commandPaletteScriptPromise = null;
        throw error;
      });
    }

    return commandPaletteScriptPromise;
  };

  const requestCommandPaletteOpen = async (query = "") => {
    try {
      sessionStorage.setItem("command-palette-open", "true");
      if (query) {
        sessionStorage.setItem("command-palette-query", query);
      } else {
        sessionStorage.removeItem("command-palette-query");
      }
    } catch (error) {}

    await loadCommandPaletteScript();
    return true;
  };

  const handleOpenTrigger = async (event) => {
    if (isCommandPaletteLoaded()) return;
    const trigger = event.target instanceof Element ? event.target.closest("[data-command-palette-open]") : null;
    if (!trigger) return;
    event.preventDefault();
    await requestCommandPaletteOpen();
  };

  document.addEventListener("click", handleOpenTrigger);

  document.addEventListener("keydown", async (event) => {
    if (isCommandPaletteLoaded()) return;
    const key = event.key.toLowerCase();
    if ((event.metaKey || event.ctrlKey) && key === "k") {
      event.preventDefault();
      await requestCommandPaletteOpen();
    }
    if (key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey) {
      const target = event.target;
      if (target instanceof HTMLElement && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
      event.preventDefault();
      await requestCommandPaletteOpen();
    }
  });
})();
