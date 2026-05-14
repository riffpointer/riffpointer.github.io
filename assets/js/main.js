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

    if (!pre || highlight.querySelector(".copy-code-button")) {
      return;
    }

    const button = document.createElement("button");
    button.className = "copy-code-button";
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", "Copy code to clipboard");

    button.addEventListener("click", async () => {
      try {
        await copyText(pre.innerText.trimEnd());
        button.textContent = "Copied";
        button.classList.add("is-copied");
      } catch (error) {
        button.textContent = "Failed";
      }

      window.setTimeout(() => {
        button.textContent = "Copy";
        button.classList.remove("is-copied");
      }, 1600);
    });

    highlight.appendChild(button);
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
  }
})();
