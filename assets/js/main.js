(() => {
  const normalizePath = (value) => {
    if (!value) return "/";
    try {
      return new URL(value, window.location.origin).pathname.replace(/\/index\.html$/, "/");
    } catch (error) {
      return value;
    }
  };

  const buildCommandPaletteItems = () => {
    const dataElement = document.getElementById("command-palette-data");
    if (!dataElement) return { items: [], error: "Data element missing" };
    try {
      const items = JSON.parse(dataElement.textContent);
      return { items, error: null };
    } catch (e) {
      console.error("Failed to parse command palette data", e);
      return { items: [], error: e.message };
    }
  };

  /**
   * Command Palette Module API
   * Modules are full-screen apps triggered by specific keywords.
   */
  const PaletteModules = {
    registry: {},
    active: null,
    
    register(name, config) {
      this.registry[name.toLowerCase()] = config;
    },
    
    get(name) {
      return this.registry[name.toLowerCase()];
    },
    
    start(name, context) {
      const module = this.get(name);
      if (!module) return false;
      
      this.stop();
      this.active = { name, module, context };
      if (module.onStart) module.onStart(context);
      return true;
    },
    
    stop() {
      if (this.active && this.active.module.onStop) {
        this.active.module.onStop(this.active.context);
      }
      this.active = null;
    }
  };

  window.startModule = (name) => {
    const palette = document.getElementById("command-palette");
    const input = document.getElementById("command-palette-input");
    if (!palette) return;
    const body = palette.querySelector(".command-palette__body");
    const list = document.getElementById("command-palette-list");
    const empty = palette.querySelector(".command-palette__empty");
    
    const contexts = {
      sinewave: {
        canvas: palette.querySelector(".command-palette__sinewave"),
        body, list, mouse: { x: 0, y: 0 }
      },
      pingpong: {
        container: palette.querySelector(".command-palette__game"),
        canvas: document.getElementById("pong-canvas"),
        list, mouse: { x: 0, y: 0 }
      },
      tictactoe: {
        container: palette.querySelector(".command-palette__tictactoe"),
        btns: Array.from(palette.querySelectorAll(".tictactoe-grid button") || []),
        status: palette.querySelector(".tictactoe-status"),
        resetBtn: palette.querySelector(".tictactoe-reset"),
        list
      },
      snake: {
        container: palette.querySelector(".command-palette__snake"),
        canvas: document.getElementById("snake-canvas"),
        overlay: palette.querySelector(".command-palette__snake .game-overlay"),
        restartBtn: palette.querySelector(".command-palette__snake .game-restart"),
        list
      },
      breakout: {
        container: palette.querySelector(".command-palette__breakout"),
        canvas: document.getElementById("breakout-canvas"),
        overlay: palette.querySelector(".command-palette__breakout .game-overlay"),
        restartBtn: palette.querySelector(".command-palette__breakout .game-restart"),
        list, mouse: { x: 0, y: 0 }
      },
      dice: {
        container: palette.querySelector(".command-palette__dice"),
        result: palette.querySelector(".dice-result"),
        history: palette.querySelector(".dice-history"),
        rollBtn: palette.querySelector(".dice-roll"),
        list
      }
    };

    if (contexts[name]) {
      if (input) {
        input.value = name;
        sessionStorage.setItem("command-palette-query", name);
      }
      if (empty) empty.hidden = true;
      PaletteModules.start(name, contexts[name]);
    }
  };

  // --- MODULE: Calculator ---
  PaletteModules.register("calculator", {
    onStart(ctx) {
      ctx.container.hidden = false;
      ctx.list.hidden = true;
    },
    onStop(ctx) {
      ctx.container.hidden = true;
      ctx.list.hidden = false;
    },
    render(ctx, query, result) {
      const cleanExpr = query.trim().replace(/\s*=$/, "");
      ctx.expr.textContent = `${cleanExpr} =`;
      ctx.res.textContent = Number.isInteger(result) ? result : result.toFixed(4).replace(/\.?0+$/, "");
    }
  });

  // --- MODULE: Sinewave ---
  PaletteModules.register("sinewave", {
    frameId: null,
    onStart(ctx) {
      ctx.canvas.hidden = false;
      ctx.list.hidden = true;
      ctx.body.classList.add("is-sinewave");
      this.loop(ctx);
    },
    onStop(ctx) {
      ctx.canvas.hidden = true;
      ctx.list.hidden = false;
      ctx.body.classList.remove("is-sinewave");
      cancelAnimationFrame(this.frameId);
      this.frameId = null;
    },
    loop(ctx) {
      const { canvas, mouse } = ctx;
      const cctx = canvas.getContext("2d");
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      if (canvas.width !== rect.width * dpr || canvas.height !== rect.height * dpr) {
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        cctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }

      const w = rect.width, h = rect.height;
      const isDark = document.body.getAttribute("data-theme") === "dark";
      cctx.clearRect(0, 0, w, h);
      
      const waveCount = 12, waveGap = h / (waveCount + 1), time = Date.now() / 1000;
      const stagger = (mouse.x / w) * 2, freq = (mouse.y / h) * 0.04 + 0.01, amp = waveGap * 0.8;

      cctx.lineWidth = 1.5;
      for (let i = 0; i < waveCount; i++) {
        cctx.beginPath();
        const phase = (i / (waveCount - 1)) * Math.PI;
        const cycle = (i / waveCount + time * 0.2) % 1;
        const sat = 50 + cycle * 40, light = isDark ? (30 + cycle * 40) : (40 + cycle * 30); 
        cctx.strokeStyle = `hsla(225, ${sat}%, ${light}%, ${0.3 + (i / waveCount) * 0.5})`;
        
        for (let x = 0; x <= w; x += 2) {
          const y = (waveGap * (i + 1)) + Math.sin(x * freq + (time + i * stagger) * 2.0 + phase) * amp;
          if (x === 0) cctx.moveTo(x, y); else cctx.lineTo(x, y);
        }
        cctx.stroke();
      }
      this.frameId = requestAnimationFrame(() => this.loop(ctx));
    }
  });

  // --- MODULE: PingPong ---
  PaletteModules.register("pingpong", {
    frameId: null,
    state: {
      player: { x: 0, score: 0 }, cpu: { x: 0, score: 0 },
      ball: { x: 0, y: 0, dx: 0, dy: 0 },
      width: 800, height: 500, pW: 100, pH: 12, bS: 10
    },
    onStart(ctx) {
      ctx.container.hidden = false;
      ctx.list.hidden = true;
      this.state.player.score = 0;
      this.state.cpu.score = 0;
      this.resetBall();
      this.loop(ctx);
    },
    onStop(ctx) {
      ctx.container.hidden = true;
      ctx.list.hidden = false;
      cancelAnimationFrame(this.frameId);
      this.frameId = null;
    },
    resetBall() {
      this.state.ball.x = this.state.width / 2;
      this.state.ball.y = this.state.height / 2;
      this.state.ball.dx = (Math.random() - 0.5) * 8;
      this.state.ball.dy = (Math.random() > 0.5 ? 1 : -1) * 4;
    },
    loop(ctx) {
      const { canvas, mouse } = ctx;
      const cctx = canvas.getContext("2d");
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      const s = this.state;

      if (canvas.width !== rect.width * dpr || canvas.height !== rect.height * dpr) {
        canvas.width = rect.width * dpr; canvas.height = rect.height * dpr;
      }

      const sX = (rect.width * dpr) / s.width, sY = (rect.height * dpr) / s.height;
      const isDark = document.body.getAttribute("data-theme") === "dark";
      const color = isDark ? "#ffffff" : "#000000";

      // Logic
      s.ball.x += s.ball.dx; s.ball.y += s.ball.dy;
      if (s.ball.x <= 0 || s.ball.x >= s.width) s.ball.dx *= -1;
      if (s.ball.y <= 0) { s.player.score++; this.resetBall(); }
      else if (s.ball.y >= s.height) { s.cpu.score++; this.resetBall(); }

      const relMouseX = (mouse.x - rect.left) * (s.width / rect.width);
      s.player.x = Math.max(0, Math.min(s.width - s.pW, relMouseX - s.pW / 2));
      s.cpu.x += (s.ball.x - s.pW / 2 - s.cpu.x) * 0.1;
      s.cpu.x = Math.max(0, Math.min(s.width - s.pW, s.cpu.x));

      if (s.ball.y > s.height - s.pH - 20 && s.ball.x > s.player.x && s.ball.x < s.player.x + s.pW) {
        s.ball.dy *= -1.05; s.ball.y = s.height - s.pH - 20;
        s.ball.dx += (s.ball.x - (s.player.x + s.pW/2)) * 0.2;
      }
      if (s.ball.y < s.pH + 20 && s.ball.x > s.cpu.x && s.ball.x < s.cpu.x + s.pW) {
        s.ball.dy *= -1.05; s.ball.y = s.pH + 20;
        s.ball.dx += (s.ball.x - (s.cpu.x + s.pW/2)) * 0.2;
      }

      // Draw
      cctx.clearRect(0, 0, canvas.width, canvas.height);
      cctx.save(); cctx.scale(sX, sY);
      cctx.fillStyle = color; cctx.globalAlpha = 0.05; cctx.font = "bold 150px monospace";
      cctx.textAlign = "center"; cctx.textBaseline = "middle";
      cctx.fillText(`${s.cpu.score} - ${s.player.score}`, s.width / 2, s.height / 2);
      cctx.globalAlpha = 0.8;
      cctx.fillRect(s.cpu.x, 20, s.pW, s.pH);
      cctx.fillRect(s.player.x, s.height - s.pH - 20, s.pW, s.pH);
      cctx.beginPath(); cctx.arc(s.ball.x, s.ball.y, s.bS / 2, 0, Math.PI * 2); cctx.fill();
      cctx.restore();

      this.frameId = requestAnimationFrame(() => this.loop(ctx));
    }
  });

  // --- MODULE: TicTacToe ---
  PaletteModules.register("tictactoe", {
    state: { board: Array(9).fill(null), xIsNext: true, winner: null },
    onStart(ctx) {
      ctx.container.hidden = false; ctx.list.hidden = true;
      this.reset(ctx);
      this.bindEvents(ctx);
    },
    onStop(ctx) {
      ctx.container.hidden = true; ctx.list.hidden = false;
      this.unbindEvents(ctx);
    },
    reset(ctx) {
      this.state = { board: Array(9).fill(null), xIsNext: true, winner: null, isThinking: false };
      ctx.btns.forEach(btn => { btn.textContent = ""; btn.classList.remove("winner"); btn.disabled = false; });
      ctx.status.textContent = "Your turn (X)";
    },
    handleMove(ctx, index) {
      if (this.state.isThinking) return;
      if (this.state.winner || !this.state.board.includes(null)) {
        this.reset(ctx);
        return;
      }
      if (this.state.board[index]) return;
      
      // Player move
      this.makeMove(ctx, index);
      
      if (!this.state.winner && this.state.board.includes(null)) {
        this.makeAIMove(ctx);
      }
    },
    makeMove(ctx, index) {
      const symbol = this.state.xIsNext ? "X" : "O";
      this.state.board[index] = symbol;
      ctx.btns[index].textContent = symbol;
      this.state.xIsNext = !this.state.xIsNext;
      this.checkWinner(ctx);
      
      if (this.state.winner) {
        ctx.status.textContent = this.state.winner === "X" ? "You win!" : "AI wins!";
      } else if (!this.state.board.includes(null)) {
        ctx.status.textContent = "Draw!";
      } else {
        ctx.status.textContent = this.state.xIsNext ? "Your turn (X)" : "AI is thinking...";
      }
    },
    makeAIMove(ctx) {
      this.state.isThinking = true;
      const delay = 400 + Math.random() * 1000;
      
      setTimeout(() => {
        if (this.state.winner || !PaletteModules.active || PaletteModules.active.name !== "tictactoe") return;
        
        // Simple AI: Prefer center, then corners, then random
        const empty = this.state.board.map((v, i) => v === null ? i : null).filter(v => v !== null);
        let move;
        
        // 1. Can AI win?
        move = this.findWinningMove("O");
        // 2. Can Player win? (Block)
        if (move === null) move = this.findWinningMove("X");
        // 3. Take center
        if (move === null && this.state.board[4] === null) move = 4;
        // 4. Random
        if (move === null) move = empty[Math.floor(Math.random() * empty.length)];
        
        this.state.isThinking = false;
        this.makeMove(ctx, move);
      }, delay);
    },
    findWinningMove(symbol) {
      const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
      for (let [a,b,c] of lines) {
        const brd = this.state.board;
        if (brd[a] === symbol && brd[b] === symbol && brd[c] === null) return c;
        if (brd[a] === symbol && brd[c] === symbol && brd[b] === null) return b;
        if (brd[b] === symbol && brd[c] === symbol && brd[a] === null) return a;
      }
      return null;
    },
    checkWinner(ctx) {
      const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
      for (let [a,b,c] of lines) {
        if (this.state.board[a] && this.state.board[a] === this.state.board[b] && this.state.board[a] === this.state.board[c]) {
          this.state.winner = this.state.board[a];
          [a,b,c].forEach(i => ctx.btns[i].classList.add("winner"));
          ctx.btns.forEach(btn => btn.disabled = true);
          return;
        }
      }
    },
    bindEvents(ctx) {
      this._moveHandler = (e) => this.handleMove(ctx, parseInt(e.target.dataset.index));
      ctx.btns.forEach(btn => btn.addEventListener("click", this._moveHandler));
      this._resetHandler = () => this.reset(ctx);
      ctx.resetBtn.addEventListener("click", this._resetHandler);
    },
    unbindEvents(ctx) {
      ctx.btns.forEach(btn => btn.removeEventListener("click", this._moveHandler));
      ctx.resetBtn.removeEventListener("click", this._resetHandler);
    }
  });

  // --- MODULE: Snake ---
  PaletteModules.register("snake", {
    frameId: null, lastTime: 0,
    state: { snake: [], dir: { x: 1, y: 0 }, nextDir: { x: 1, y: 0 }, food: { x: 0, y: 0 }, score: 0, gameOver: false, gridSize: 20 },
    onStart(ctx) {
      ctx.container.hidden = false; ctx.list.hidden = true;
      this.reset(ctx);
      this.bindEvents(ctx);
      this.loop(ctx, 0);
    },
    onStop(ctx) {
      ctx.container.hidden = true; ctx.list.hidden = false;
      cancelAnimationFrame(this.frameId);
      this.unbindEvents(ctx);
    },
    reset(ctx) {
      const g = this.state.gridSize;
      this.state = { snake: [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }], dir: { x: 1, y: 0 }, nextDir: { x: 1, y: 0 }, food: { x: 5, y: 5 }, score: 0, gameOver: false, gridSize: g };
      ctx.overlay.hidden = true;
      this.placeFood();
    },
    placeFood() {
      this.state.food = { x: Math.floor(Math.random() * 30), y: Math.floor(Math.random() * 20) };
    },
    bindEvents(ctx) {
      this._keyHandler = (e) => {
        const d = this.state.dir;
        if (e.key === "ArrowUp" && d.y === 0) this.state.nextDir = { x: 0, y: -1 };
        else if (e.key === "ArrowDown" && d.y === 0) this.state.nextDir = { x: 0, y: 1 };
        else if (e.key === "ArrowLeft" && d.x === 0) this.state.nextDir = { x: -1, y: 0 };
        else if (e.key === "ArrowRight" && d.x === 0) this.state.nextDir = { x: 1, y: 0 };
      };
      window.addEventListener("keydown", this._keyHandler);
      this._restartHandler = () => { this.reset(ctx); this.loop(ctx, 0); };
      ctx.restartBtn.addEventListener("click", this._restartHandler);
    },
    unbindEvents(ctx) {
      window.removeEventListener("keydown", this._keyHandler);
      ctx.restartBtn.removeEventListener("click", this._restartHandler);
    },
    loop(ctx, timestamp) {
      if (this.state.gameOver) return;
      this.frameId = requestAnimationFrame((t) => this.loop(ctx, t));
      if (timestamp - this.lastTime < 100) return;
      this.lastTime = timestamp;

      const s = this.state; s.dir = s.nextDir;
      const head = { x: s.snake[0].x + s.dir.x, y: s.snake[0].y + s.dir.y };

      // Border Wrapping
      if (head.x < 0) head.x = 33;
      else if (head.x >= 34) head.x = 0;
      if (head.y < 0) head.y = 20;
      else if (head.y >= 21) head.y = 0;

      if (s.snake.some(p => p.x === head.x && p.y === head.y)) {
        s.gameOver = true; ctx.overlay.hidden = false; return;
      }

      s.snake.unshift(head);
      if (head.x === s.food.x && head.y === s.food.y) { s.score++; this.placeFood(); }
      else { s.snake.pop(); }

      const cctx = ctx.canvas.getContext("2d"), dpr = window.devicePixelRatio || 1;
      const rect = ctx.canvas.getBoundingClientRect();
      if (ctx.canvas.width !== rect.width * dpr) { ctx.canvas.width = rect.width * dpr; ctx.canvas.height = rect.height * dpr; }
      cctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cctx.clearRect(0, 0, rect.width, rect.height);

      const isDark = document.body.getAttribute("data-theme") === "dark";
      const color = isDark ? "#ffffff" : "#000000";

      // Draw faint score
      cctx.save();
      cctx.fillStyle = color; cctx.globalAlpha = 0.05; cctx.font = "bold 150px monospace";
      cctx.textAlign = "center"; cctx.textBaseline = "middle";
      cctx.fillText(s.score, rect.width / 2, rect.height / 2);
      cctx.restore();

      cctx.fillStyle = color;
      s.snake.forEach(p => cctx.fillRect(p.x * 20, p.y * 20, 18, 18));
      cctx.fillStyle = "#ff4444";
      cctx.fillRect(s.food.x * 20, s.food.y * 20, 18, 18);
    }
  });

  // --- MODULE: Breakout ---
  PaletteModules.register("breakout", {
    frameId: null,
    state: { ball: { x: 0, y: 0, dx: 4, dy: -4 }, paddle: { x: 0, w: 100 }, bricks: [], gameOver: false, score: 0 },
    onStart(ctx) {
      ctx.container.hidden = false; ctx.list.hidden = true;
      this.reset(ctx);
      this.bindEvents(ctx);
      this.loop(ctx);
    },
    onStop(ctx) {
      ctx.container.hidden = true; ctx.list.hidden = false;
      cancelAnimationFrame(this.frameId);
      this.unbindEvents(ctx);
    },
    reset(ctx) {
      const rect = ctx.canvas.getBoundingClientRect();
      this.state = { ball: { x: rect.width / 2, y: rect.height - 30, dx: 4, dy: -4 }, paddle: { x: rect.width / 2 - 50, w: 100 }, bricks: [], gameOver: false, score: 0 };
      for (let c = 0; c < 8; c++) for (let r = 0; r < 5; r++) this.state.bricks.push({ x: c * 80 + 25, y: r * 30 + 50, status: 1 });
      ctx.overlay.hidden = true;
    },
    bindEvents(ctx) {
      this._restartHandler = () => { this.reset(ctx); this.loop(ctx); };
      ctx.restartBtn.addEventListener("click", this._restartHandler);
    },
    unbindEvents(ctx) {
      ctx.restartBtn.removeEventListener("click", this._restartHandler);
    },
    loop(ctx) {
      if (this.state.gameOver) return;
      this.frameId = requestAnimationFrame(() => this.loop(ctx));
      const s = this.state, rect = ctx.canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
      if (ctx.canvas.width !== rect.width * dpr) { ctx.canvas.width = rect.width * dpr; ctx.canvas.height = rect.height * dpr; }
      const cctx = ctx.canvas.getContext("2d");
      cctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cctx.clearRect(0, 0, rect.width, rect.height);

      // Move paddle with mouse
      const relX = ctx.mouse.x;
      s.paddle.x = Math.max(0, Math.min(rect.width - s.paddle.w, relX - s.paddle.w / 2));

      // Ball Logic
      s.ball.x += s.ball.dx; s.ball.y += s.ball.dy;
      if (s.ball.x < 10 || s.ball.x > rect.width - 10) s.ball.dx *= -1;
      if (s.ball.y < 10) s.ball.dy *= -1;
      else if (s.ball.y > rect.height - 20) {
        if (s.ball.x > s.paddle.x && s.ball.x < s.paddle.x + s.paddle.w) { s.ball.dy *= -1; s.ball.y = rect.height - 21; }
        else { s.gameOver = true; ctx.overlay.hidden = false; }
      }

      // Brick Collision
      s.bricks.forEach(b => {
        if (b.status === 1 && s.ball.x > b.x && s.ball.x < b.x + 70 && s.ball.y > b.y && s.ball.y < b.y + 20) {
          s.ball.dy *= -1; b.status = 0; s.score++;
        }
      });

      // Draw
      const isDark = document.body.getAttribute("data-theme") === "dark";
      const color = isDark ? "#ffffff" : "#000000";
      cctx.fillStyle = color;
      cctx.fillRect(s.paddle.x, rect.height - 15, s.paddle.w, 10);
      cctx.beginPath(); cctx.arc(s.ball.x, s.ball.y, 8, 0, Math.PI * 2); cctx.fill();
      s.bricks.forEach(b => { if (b.status === 1) cctx.fillRect(b.x, b.y, 70, 20); });
    }
  });

  // --- MODULE: Dice ---
  PaletteModules.register("dice", {
    onStart(ctx) {
      ctx.container.hidden = false; ctx.list.hidden = true;
      this.bindEvents(ctx);
    },
    onStop(ctx) {
      ctx.container.hidden = true; ctx.list.hidden = false;
      this.unbindEvents(ctx);
    },
    roll(ctx) {
      const res = Math.floor(Math.random() * 6) + 1;
      ctx.result.textContent = res;
      ctx.result.classList.remove("rolling");
      void ctx.result.offsetWidth;
      ctx.result.classList.add("rolling");
      const item = document.createElement("span"); item.textContent = res;
      ctx.history.prepend(item);
      if (ctx.history.children.length > 10) ctx.history.lastChild.remove();
    },
    bindEvents(ctx) {
      this._rollHandler = () => this.roll(ctx);
      ctx.rollBtn.addEventListener("click", this._rollHandler);
    },
    unbindEvents(ctx) {
      ctx.rollBtn.removeEventListener("click", this._rollHandler);
    }
  });

  // --- MODULE: 2048 ---
  PaletteModules.register("2048", {
    state: { grid: Array(16).fill(null), score: 0, gameOver: false },
    onStart(ctx) {
      ctx.container.hidden = false; ctx.list.hidden = true;
      this.reset(ctx);
      this.bindEvents(ctx);
    },
    onStop(ctx) {
      ctx.container.hidden = true; ctx.list.hidden = false;
      this.unbindEvents(ctx);
    },
    reset(ctx) {
      this.state = { grid: Array(16).fill(null), score: 0, gameOver: false };
      ctx.overlay.hidden = true;
      ctx.score.textContent = "0";
      this.addRandomTile();
      this.addRandomTile();
      this.draw(ctx);
    },
    addRandomTile() {
      const empty = this.state.grid.map((v, i) => v === null ? i : null).filter(v => v !== null);
      if (empty.length === 0) return;
      const idx = empty[Math.floor(Math.random() * empty.length)];
      this.state.grid[idx] = Math.random() < 0.9 ? 2 : 4;
    },
    move(ctx, direction) {
      if (this.state.gameOver) return;
      let moved = false;
      const size = 4;
      
      const getRow = (i) => this.state.grid.slice(i * size, (i + 1) * size);
      const getCol = (i) => [this.state.grid[i], this.state.grid[i+size], this.state.grid[i+size*2], this.state.grid[i+size*3]];
      const setRow = (i, row) => row.forEach((v, j) => this.state.grid[i * size + j] = v);
      const setCol = (i, col) => col.forEach((v, j) => this.state.grid[i + j * size] = v);

      const slide = (arr, reverse = false) => {
        if (reverse) arr.reverse();
        let result = arr.filter(v => v !== null);
        for (let i = 0; i < result.length - 1; i++) {
          if (result[i] === result[i+1]) {
            result[i] *= 2;
            this.state.score += result[i];
            result.splice(i+1, 1);
            moved = true;
          }
        }
        while (result.length < size) result.push(null);
        if (reverse) result.reverse();
        return result;
      };

      for (let i = 0; i < size; i++) {
        let line = (direction === "up" || direction === "down") ? getCol(i) : getRow(i);
        let newLine = slide(line, direction === "right" || direction === "down");
        if (line.some((v, idx) => v !== newLine[idx])) moved = true;
        if (direction === "up" || direction === "down") setCol(i, newLine);
        else setRow(i, newLine);
      }

      if (moved) {
        this.addRandomTile();
        this.draw(ctx);
        if (this.isGameOver()) {
          this.state.gameOver = true;
          ctx.overlay.hidden = false;
        }
      }
    },
    isGameOver() {
      if (this.state.grid.includes(null)) return false;
      for (let i = 0; i < 4; i++) {
        for (let j = 0; j < 4; j++) {
          const val = this.state.grid[i * 4 + j];
          if (j < 3 && val === this.state.grid[i * 4 + j + 1]) return false;
          if (i < 3 && val === this.state.grid[(i + 1) * 4 + j]) return false;
        }
      }
      return true;
    },
    draw(ctx) {
      ctx.score.textContent = this.state.score;
      ctx.cells.forEach((cell, i) => {
        const val = this.state.grid[i];
        cell.textContent = val || "";
        cell.setAttribute("data-value", val || "");
      });
    },
    bindEvents(ctx) {
      this._keyHandler = (e) => {
        if (e.key === "ArrowUp") { e.preventDefault(); this.move(ctx, "up"); }
        else if (e.key === "ArrowDown") { e.preventDefault(); this.move(ctx, "down"); }
        else if (e.key === "ArrowLeft") { e.preventDefault(); this.move(ctx, "left"); }
        else if (e.key === "ArrowRight") { e.preventDefault(); this.move(ctx, "right"); }
      };
      window.addEventListener("keydown", this._keyHandler);
      this._resetHandler = () => this.reset(ctx);
      ctx.resetBtn.addEventListener("click", this._resetHandler);
      ctx.restartBtn.addEventListener("click", this._resetHandler);
    },
    unbindEvents(ctx) {
      window.removeEventListener("keydown", this._keyHandler);
      ctx.resetBtn.removeEventListener("click", this._resetHandler);
      ctx.restartBtn.removeEventListener("click", this._resetHandler);
    }
  });

  const initCommandPalette = () => {
    const palette = document.getElementById("command-palette");
    const input = document.getElementById("command-palette-input");
    const list = document.getElementById("command-palette-list");
    const empty = palette?.querySelector(".command-palette__empty");
    const error = palette?.querySelector(".command-palette__error");
    const errorDetail = error?.querySelector(".command-palette__error-detail");
    const body = palette?.querySelector(".command-palette__body");

    // Module Contexts
    const ctxCalc = {
      container: palette?.querySelector(".command-palette__calculator"),
      expr: palette?.querySelector(".command-palette__calc-expression"),
      res: palette?.querySelector(".command-palette__calc-result"),
      list
    };
    const ctxSine = {
      canvas: palette?.querySelector(".command-palette__sinewave"),
      body, list, mouse: { x: 0, y: 0 }
    };
    const ctxPong = {
      container: palette?.querySelector(".command-palette__game"),
      canvas: document.getElementById("pong-canvas"),
      list, mouse: { x: 0, y: 0 }
    };
    const tttRoot = palette?.querySelector(".command-palette__tictactoe");
    const ctxTTT = {
      container: tttRoot,
      btns: Array.from(tttRoot?.querySelectorAll(".tictactoe-grid button") || []),
      status: tttRoot?.querySelector(".tictactoe-status"),
      resetBtn: tttRoot?.querySelector(".tictactoe-reset"),
      list
    };
    const snakeRoot = palette?.querySelector(".command-palette__snake");
    const ctxSnake = {
      container: snakeRoot,
      canvas: document.getElementById("snake-canvas"),
      overlay: snakeRoot?.querySelector(".game-overlay"),
      restartBtn: snakeRoot?.querySelector(".game-restart"),
      list
    };
    const breakoutRoot = palette?.querySelector(".command-palette__breakout");
    const ctxBreakout = {
      container: breakoutRoot,
      canvas: document.getElementById("breakout-canvas"),
      overlay: breakoutRoot?.querySelector(".game-overlay"),
      restartBtn: breakoutRoot?.querySelector(".game-restart"),
      list, mouse: { x: 0, y: 0 }
    };
    const diceRoot = palette?.querySelector(".command-palette__dice");
    const ctxDice = {
      container: diceRoot,
      result: diceRoot?.querySelector(".dice-result"),
      history: diceRoot?.querySelector(".dice-history"),
      rollBtn: diceRoot?.querySelector(".dice-roll"),
      list
    };

    if (!palette || !input || !list || !empty || !error || !body) return;

    const { items, error: loadError } = buildCommandPaletteItems();
    let activeIndex = 0, isOpen = false;

    const render = (query = "") => {
      if (loadError || items.length === 0) {
        error.hidden = false;
        if (errorDetail) errorDetail.textContent = loadError || "No items found.";
        list.innerHTML = ""; empty.hidden = true;
        PaletteModules.stop();
        return;
      }
      error.hidden = true;
      empty.hidden = true;
      const normalized = query.trim().toLowerCase();

      // 1. Module Handling
      if (normalized === "sinewave") {
        PaletteModules.start("sinewave", ctxSine);
        return;
      } else if (normalized === "pingpong") {
        PaletteModules.start("pingpong", ctxPong);
        return;
      } else if (normalized === "tictactoe") {
        PaletteModules.start("tictactoe", ctxTTT);
        return;
      } else if (normalized === "snake") {
        PaletteModules.start("snake", ctxSnake);
        return;
      } else if (normalized === "breakout") {
        PaletteModules.start("breakout", ctxBreakout);
        return;
      } else if (normalized === "dice") {
        PaletteModules.start("dice", ctxDice);
        return;
      }

      // Calculator logic
      const mathWords = ["sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "log", "exp", "abs", "round", "ceil", "floor", "pow", "min", "max", "pi", "e"];
      const isMath = normalized && /^[\d\s\+\-\*\/\(\)\%\.\^,a-z]+$/.test(normalized) && /[+\-\*\/\%\^\(\)a-z]/.test(normalized) && /[\d]/.test(normalized);

      if (isMath) {
        try {
          const mathRegex = new RegExp(`\\b(${mathWords.join("|")})\\b`, "g");
          let sanitized = normalized.replace(/\^/g, "**").replace(mathRegex, m => (m === "pi" || m === "e") ? `Math.${m.toUpperCase()}` : `Math.${m}`);
          const result = new Function(`return ${sanitized}`)();
          if (typeof result === "number" && !isNaN(result)) {
            PaletteModules.start("calculator", ctxCalc);
            PaletteModules.get("calculator").render(ctxCalc, query, result);
            return;
          }
        } catch (e) {}
      }

      // Reset if no module matches
      PaletteModules.stop();

      // 2. Normal List Filtering
      const isListAll = normalized === "listall";
      const currentPath = normalizePath(window.location.pathname);
      
      let filtered = [];
      if (isListAll) {
        // Show ONLY hidden commands
        filtered = items.filter(item => item.hidden === true);
      } else {
        // Normal filtering: exclude hidden items and current page
        filtered = items.filter(item => {
          const isHidden = item.hidden === true;
          const isCurrent = normalizePath(item.href) === currentPath && item.href !== "/";
          if (isHidden || isCurrent) return false;
          if (!normalized) return true;
          return [item.title, item.href, item.description, ...(item.keywords || [])].join(" ").toLowerCase().includes(normalized);
        });
      }

      list.innerHTML = "";
      empty.hidden = filtered.length > 0;
      filtered.forEach((item, index) => {
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.className = "command-palette__item"; link.href = item.href; link.dataset.index = String(index);
        link.innerHTML = `<div class="command-palette__item-content"><i class="bi bi-${item.icon || 'link-45deg'}"></i><div><strong>${item.title}</strong><span>${item.description}</span></div></div>`;
        
        link.addEventListener("click", (e) => {
          if (item.href.startsWith("javascript:")) {
            e.preventDefault();
            const code = item.href.slice(11);
            new Function(code)();
            if (!item.href.includes("random") && !item.href.includes("startModule")) closePalette();
          }
        });

        li.appendChild(link); list.appendChild(li);
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
        
        if (active) {
          link.scrollIntoView({ block: "nearest", behavior: "smooth" });
        }
      });
    };

    const openPalette = (restoreQuery = "") => {
      if (isOpen && !restoreQuery) return;
      isOpen = true; palette.hidden = false; palette.setAttribute("aria-hidden", "false");
      document.documentElement.classList.add("command-palette-open");
      document.body.classList.add("command-palette-open");
      if (restoreQuery) input.value = restoreQuery;
      render(input.value);
      sessionStorage.setItem("command-palette-open", "true");
      window.requestAnimationFrame(() => input.focus());
    };

    const closePalette = () => {
      if (!isOpen) return;
      isOpen = false; palette.hidden = true; palette.setAttribute("aria-hidden", "true");
      document.documentElement.classList.remove("command-palette-open");
      document.body.classList.remove("command-palette-open");
      input.value = "";
      sessionStorage.removeItem("command-palette-open");
      sessionStorage.removeItem("command-palette-query");
      PaletteModules.stop();
    };

    // Global Events
    const savedOpen = sessionStorage.getItem("command-palette-open");
    const savedQuery = sessionStorage.getItem("command-palette-query") || "";
    if (savedOpen === "true") openPalette(savedQuery); else render();

    Array.from(document.querySelectorAll("[data-command-palette-open]")).forEach(t => t.addEventListener("click", () => openPalette()));
    Array.from(document.querySelectorAll("[data-command-palette-close]")).forEach(t => t.addEventListener("click", closePalette));

    palette.addEventListener("click", e => { if (e.target === palette || e.target.classList.contains("command-palette__backdrop")) closePalette(); });
    palette.addEventListener("mousemove", e => { 
      const rect = palette.getBoundingClientRect();
      ctxSine.mouse.x = ctxPong.mouse.x = e.clientX - rect.left; 
      ctxSine.mouse.y = ctxPong.mouse.y = e.clientY - rect.top; 
    });

    input.addEventListener("input", () => { sessionStorage.setItem("command-palette-query", input.value); render(input.value); });
    input.addEventListener("keydown", (event) => {
      const links = Array.from(list.querySelectorAll(".command-palette__item"));
      if (event.key === "ArrowDown") { event.preventDefault(); activeIndex = links.length ? (activeIndex + 1) % links.length : 0; updateActive(links); }
      else if (event.key === "ArrowUp") { event.preventDefault(); activeIndex = links.length ? (activeIndex - 1 + links.length) % links.length : 0; updateActive(links); }
      else if (event.key === "Enter") { 
        event.preventDefault(); 
        const current = links[activeIndex]; 
        if (current) { 
          sessionStorage.removeItem("command-palette-open"); 
          sessionStorage.removeItem("command-palette-query"); 
          if (current.href.startsWith("javascript:")) {
            const code = current.href.slice(11);
            new Function(code)();
          } else {
            window.location.href = current.href; 
          }
        } 
      }
      else if (event.key === "Escape") { event.preventDefault(); closePalette(); }
    });

    document.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();
      if ((event.metaKey || event.ctrlKey) && key === "k") { event.preventDefault(); if (isOpen) closePalette(); else openPalette(); }
      if (key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey) {
        const target = event.target;
        if (target instanceof HTMLElement && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
        event.preventDefault(); openPalette();
      }
      if (key === "escape") closePalette();
    });
  };

  initCommandPalette();

  // --- Theme ---
  const body = document.body;
  const lamp = document.getElementById("mode");
  const toggleTheme = (state) => {
    lamp?.classList.remove("theme-toggle-rotating");
    void lamp?.offsetWidth;
    lamp?.classList.add("theme-toggle-rotating");
    if (state === "dark") { localStorage.setItem("theme", "light"); body.removeAttribute("data-theme"); }
    else if (state === "light") { localStorage.setItem("theme", "dark"); body.setAttribute("data-theme", "dark"); }
  };
  if (lamp) {
    lamp.addEventListener("click", () => toggleTheme(localStorage.getItem("theme")));
    lamp.addEventListener("animationend", () => lamp.classList.remove("theme-toggle-rotating"));
  }

  // --- TOC ---
  const tocRoot = document.querySelector("[data-toc]");
  if (tocRoot) {
    const btn = tocRoot.querySelector(".toc-button"), pnl = tocRoot.querySelector(".toc-panel"), lst = tocRoot.querySelector(".toc-list"), cls = tocRoot.querySelector(".toc-close");
    const heads = Array.from(document.querySelectorAll(".page-content h2, .page-content h3, .page-content h4")).filter(h => h.id);
    if (!btn || !pnl || !lst || heads.length < 2) { tocRoot.hidden = true; } else {
      const mQ = window.matchMedia("(max-width: 767px)"), oC = "is-open";
      const cT = () => { document.documentElement.classList.remove("toc-open"); document.body.classList.remove("toc-open"); tocRoot.classList.remove(oC); btn.setAttribute("aria-expanded", "false"); pnl.hidden = true; };
      const oT = () => { tocRoot.classList.add(oC); btn.setAttribute("aria-expanded", "true"); pnl.hidden = false; document.documentElement.classList.toggle("toc-open", mQ.matches); document.body.classList.toggle("toc-open", mQ.matches); };
      heads.forEach(h => { const a = document.createElement("a"); a.className = `toc-link toc-link-${h.tagName.toLowerCase()}`; a.href = `#${h.id}`; a.textContent = h.textContent.trim(); a.addEventListener("click", cT); lst.appendChild(a); });
      btn.addEventListener("click", () => tocRoot.classList.contains(oC) ? cT() : oT());
      cls.addEventListener("click", cT);
      document.addEventListener("click", e => { if (!tocRoot.classList.contains(oC)) return; if (!tocRoot.contains(e.target)) cT(); });
      document.addEventListener("keydown", e => { if (e.key === "Escape") cT(); });
      mQ.addEventListener("change", () => { if (!tocRoot.classList.contains(oC)) return; document.documentElement.classList.toggle("toc-open", mQ.matches); document.body.classList.toggle("toc-open", mQ.matches); });
    }
  }

  // --- Copy Buttons ---
  const copyText = async (text) => {
    if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); return; }
    const t = document.createElement("textarea"); t.value = text; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.left = "-9999px"; document.body.appendChild(t); t.select(); document.execCommand("copy"); t.remove();
  };
  document.querySelectorAll(".highlight").forEach(h => {
    const pre = h.querySelector("pre"), wrap = h.closest(".highlighter-rouge") || h;
    if (!pre || wrap.querySelector(".copy-code-button")) return;
    const b = document.createElement("button"); b.className = "copy-code-button"; b.type = "button"; b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>';
    b.addEventListener("click", async () => {
      try { await copyText(pre.innerText.trimEnd()); b.innerHTML = '<i class="bi bi-check2" aria-hidden="true"></i><span>Copied</span>'; b.classList.add("is-copied"); }
      catch (e) { b.innerHTML = '<i class="bi bi-exclamation-circle" aria-hidden="true"></i><span>Failed</span>'; }
      window.setTimeout(() => { b.innerHTML = '<i class="bi bi-copy" aria-hidden="true"></i><span>Copy</span>'; b.classList.remove("is-copied"); }, 1600);
    });
    wrap.appendChild(b);
  });

  // --- Misc ---
  const mTrig = document.getElementById("menu-trigger");
  if (mTrig) {
    mTrig.addEventListener("change", function () { const a = document.querySelector(".wrapper"); this.checked ? a.classList.add("blurry") : a.classList.remove("blurry"); });
    const mOver = document.querySelector(".trigger");
    if (mOver) mOver.addEventListener("click", e => { if (e.target === mOver) { mTrig.checked = false; mTrig.dispatchEvent(new Event("change")); } });
  }

  // --- Dock ---
  const dRoot = document.querySelector(".trigger-container"), canH = window.matchMedia("(hover: hover) and (pointer: fine)"), rMot = window.matchMedia("(prefers-reduced-motion: reduce)");
  const dEff = { maxD: 92, boost: 0.24, lift: 4, exp: 3.4 };
  if (dRoot && canH.matches && !rMot.matches) {
    const dLinks = Array.from(dRoot.querySelectorAll(".menu-link"));
    let fId = null, lP = null;
    const updD = () => {
      fId = null; if (!lP) { dLinks.forEach(l => { l.style.setProperty("--dock-scale", "1"); l.style.setProperty("--dock-translate-y", "0px"); }); return; }
      dLinks.forEach(l => {
        const r = l.getBoundingClientRect(), d = Math.hypot(lP.clientX - (r.left + r.width / 2), lP.clientY - (r.top + r.height / 2));
        const inf = Math.max(0, 1 - d / dEff.maxD), foc = Math.pow(inf, dEff.exp);
        l.style.setProperty("--dock-scale", (1 + foc * dEff.boost).toFixed(3));
        l.style.setProperty("--dock-translate-y", `${(-foc * dEff.lift).toFixed(1)}px`);
      });
    };
    dRoot.addEventListener("pointermove", e => { lP = e; if (!fId) fId = requestAnimationFrame(updD); });
    dRoot.addEventListener("pointerleave", () => { lP = null; updD(); });
  }
})();
