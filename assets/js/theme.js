(() => {
  const body = document.body;
  const lamp = document.getElementById("mode");

  const syncThemeButton = () => {
    if (!lamp) return;
    const isDark = body.getAttribute("data-theme") === "dark";
    lamp.setAttribute("aria-pressed", isDark ? "true" : "false");
    lamp.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
  };

  const toggleTheme = (state) => {
    lamp?.classList.remove("theme-toggle-rotating");
    void lamp?.offsetWidth;
    lamp?.classList.add("theme-toggle-rotating");
    if (state === "dark") {
      localStorage.setItem("theme", "light");
      body.removeAttribute("data-theme");
    } else if (state === "light") {
      localStorage.setItem("theme", "dark");
      body.setAttribute("data-theme", "dark");
    }
    syncThemeButton();
  };

  if (lamp) {
    syncThemeButton();
    lamp.addEventListener("click", () => toggleTheme(localStorage.getItem("theme")));
    lamp.addEventListener("animationend", () => lamp.classList.remove("theme-toggle-rotating"));
  }
})();
