COMMAND PALETTE AI PROMPT: FILE MAP AND ARCHITECTURE

- DATA: _data/command_palette.json (Commands, links, icons, keywords)
- HTML: _includes/footer.html (Modal markup, search input, game containers)
- CSS: _sass/klise/_command-palette.scss (Palette styles, dark/light themes, game grids/tiles)
- JS: assets/js/main.js (PaletteModules API, game logic, input handling)

ARCHITECTURE FACTS:
- Modular System: Games are registered via PaletteModules.register() and started with PaletteModules.start(name, ctx).
- Context (ctx): Modules receive a ctx object containing DOM references (container, canvas, list, score, best, mouse).
- Keyboard: Navigation (Arrows/Enter/Esc) is in initCommandPalette. Game keys are bound in onStart and unbound in onStop.
- Scroll Lock: Scrolling is disabled via body.command-palette-open {overflow: hidden} and event.preventDefault() on arrow keys in the global keydown listener.
- 2048 Styling: Use .game-2048-cell[data-value="N"] with !important to override theme defaults.
- Persistence: High scores stored in localStorage (e.g., 2048-best).
