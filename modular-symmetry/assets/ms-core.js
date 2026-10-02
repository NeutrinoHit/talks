/* Shared helpers for the modular-symmetry lecture widgets.
 *
 * Conventions used throughout the lecture:
 *   omega1 = 1      (cyan)   -- first period
 *   omega2 = tau    (amber)  -- second period, Im tau > 0
 *   a lattice is  Lambda = { m*omega1 + n*omega2 : m, n integers }
 *   a modular transformation  gamma = (a b; c d), ad - bc = 1, acts as
 *       omega2' = a*omega2 + b*omega1,   omega1' = c*omega2 + d*omega1,
 *       tau' = omega2'/omega1' = (a*tau + b)/(c*tau + d).
 */
(function () {
  "use strict";

  const PI = Math.PI, TWO_PI = 2 * Math.PI;
  const COL = {
    cyan: "#85d4e8", amber: "#ffcc8a", pale: "#e9f1f4", purple: "#d7a7ff",
    bg: "#08121d", dim: "#5f7d8c", grid: "#1d3646", red: "#ff7b7b", green: "#8be0a4"
  };
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const fmt = (x, d = 2) => (x < -0.5 * Math.pow(10, -d) ? "−" : "") + Math.abs(x).toFixed(d);
  const fmtC = (re, im, d = 2) => `${fmt(re, d)} ${im < 0 ? "−" : "+"} ${Math.abs(im).toFixed(d)}i`;

  /* ---------- DOM helpers ---------- */
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "html") node.innerHTML = v;
      else if (k === "text") node.textContent = v;
      else node.setAttribute(k, v);
    }
    for (const c of children) node.append(c);
    return node;
  }
  function button(text, onClick, title) {
    const b = el("button", {type: "button", text});
    if (title) b.title = title;
    b.addEventListener("click", onClick);
    return b;
  }
  function slider(label, min, max, step, value, onInput, digits = 2) {
    const input = el("input", {type: "range", min, max, step, value});
    const out = el("output");
    const wrap = el("label", {}, [document.createTextNode(label + " "), input, out]);
    const show = () => { out.textContent = fmt(Number(input.value), digits); };
    input.addEventListener("input", () => { show(); onInput(Number(input.value)); });
    show();
    return {wrap, input, out, set(v) { input.value = v; show(); }};
  }
  function toggle(label, checked, onChange) {
    const input = el("input", {type: "checkbox"});
    input.checked = checked;
    input.addEventListener("change", () => onChange(input.checked));
    return el("label", {}, [input, document.createTextNode(" " + label)]);
  }

  /* ---------- canvas helpers ---------- */
  function setupCanvas(c) {
    const rev = window.Reveal && typeof Reveal.getScale === "function" ? Reveal.getScale() : 1;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const scale = Math.max(1, rev) * dpr;
    const w = c.clientWidth, h = c.clientHeight;
    if (!w || !h) return false;
    const pw = Math.round(w * scale), ph = Math.round(h * scale);
    let changed = false;
    if (c.width !== pw || c.height !== ph) { c.width = pw; c.height = ph; changed = true; }
    if (c._w !== w || c._h !== h || c._scale !== scale) changed = true;
    c._w = w; c._h = h; c._scale = scale;
    return changed;
  }
  function ctxOf(c) {
    const g = c.getContext("2d");
    g.setTransform(c._scale, 0, 0, c._scale, 0, 0);
    return g;
  }
  function pointer(c, e) {
    const r = c.getBoundingClientRect();
    return [(e.clientX - r.left) * (c._w || c.clientWidth) / r.width,
            (e.clientY - r.top) * (c._h || c.clientHeight) / r.height];
  }
  function text(g, s, x, y, color = COL.pale, size = 20, align = "left", italic = true) {
    g.font = `${italic ? "italic " : ""}${size}px "STIX Two Text","Times New Roman",serif`;
    g.fillStyle = color; g.textAlign = align; g.textBaseline = "middle";
    g.fillText(s, x, y);
  }
  function arrow(g, x1, y1, x2, y2, color, width = 3, head = 11) {
    const dx = x2 - x1, dy = y2 - y1, n = Math.hypot(dx, dy);
    if (n < 1e-6) return;
    const ux = dx / n, uy = dy / n;
    g.strokeStyle = color; g.fillStyle = color; g.lineWidth = width; g.lineCap = "round";
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x2 - ux * head * 0.7, y2 - uy * head * 0.7); g.stroke();
    g.beginPath();
    g.moveTo(x2, y2);
    g.lineTo(x2 - ux * head - uy * head * 0.45, y2 - uy * head + ux * head * 0.45);
    g.lineTo(x2 - ux * head + uy * head * 0.45, y2 - uy * head - ux * head * 0.45);
    g.closePath(); g.fill();
  }
  function dot(g, x, y, r, fill, stroke, lw = 1.5) {
    g.beginPath(); g.arc(x, y, r, 0, TWO_PI);
    if (fill) { g.fillStyle = fill; g.fill(); }
    if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw; g.stroke(); }
  }

  /* ---------- modular arithmetic on 2x2 integer matrices ---------- */
  const I2 = [1, 0, 0, 1], MT = [1, 1, 0, 1], MTI = [1, -1, 0, 1], MS = [0, -1, 1, 0];
  function mul2(A, B) {
    return [A[0] * B[0] + A[1] * B[2], A[0] * B[1] + A[1] * B[3],
            A[2] * B[0] + A[3] * B[2], A[2] * B[1] + A[3] * B[3]];
  }
  function mobius(M, re, im) {
    const nr = M[0] * re + M[1], ni = M[0] * im;
    const dr = M[2] * re + M[3], di = M[2] * im;
    const den = dr * dr + di * di;
    return [(nr * dr + ni * di) / den, (ni * dr - nr * di) / den];
  }
  /* One elementary step of the reduction algorithm. Returns null when tau is in F,
     otherwise {kind: "T"|"S", n, M, re, im}. */
  function reduceStep(re, im) {
    const n = Math.round(re);
    if (n !== 0) {
      const M = [1, -n, 0, 1];
      const [r, i] = mobius(M, re, im);
      return {kind: "T", n: -n, M, re: r, im: i};
    }
    if (re * re + im * im < 1 - 1e-12) {
      const [r, i] = mobius(MS, re, im);
      return {kind: "S", n: 0, M: MS, re: r, im: i};
    }
    return null;
  }
  function reduceAll(re, im) {
    let M = I2;
    const steps = [];
    for (let k = 0; k < 200; k++) {
      const s = reduceStep(re, im);
      if (!s) break;
      steps.push({kind: s.kind, n: s.n, from: [re, im], to: [s.re, s.im]});
      re = s.re; im = s.im; M = mul2(s.M, M);
    }
    return {re, im, M, steps};
  }
  function inF(re, im) { return Math.abs(re) <= 0.5 + 1e-12 && re * re + im * im >= 1 - 1e-12; }

  /* ---------- the upper half plane panel ---------- */
  function drawUHP(g, w, h, view, opts = {}) {
    // view: {x0, x1, y1}; real axis sits at the bottom with a margin
    const padB = 26, padT = 6;
    const X = x => (x - view.x0) / (view.x1 - view.x0) * w;
    const Y = y => h - padB - y / view.y1 * (h - padB - padT);
    g.fillStyle = COL.bg; g.fillRect(0, 0, w, h);
    // grid
    g.lineWidth = 1; g.strokeStyle = COL.grid;
    for (let x = Math.ceil(view.x0); x <= view.x1; x++) {
      g.beginPath(); g.moveTo(X(x), Y(0)); g.lineTo(X(x), Y(view.y1)); g.stroke();
    }
    for (let y = 1; y <= view.y1; y++) {
      g.beginPath(); g.moveTo(X(view.x0), Y(y)); g.lineTo(X(view.x1), Y(y)); g.stroke();
    }
    // fundamental domain
    if (opts.showF !== false) {
      g.beginPath();
      g.moveTo(X(-0.5), Y(view.y1));
      g.lineTo(X(-0.5), Y(Math.sqrt(3) / 2));
      const N = 40;
      for (let k = 0; k <= N; k++) {
        const ang = (2 * PI / 3) - (PI / 3) * k / N;
        g.lineTo(X(Math.cos(ang)), Y(Math.sin(ang)));
      }
      g.lineTo(X(0.5), Y(view.y1));
      g.closePath();
      g.fillStyle = "rgba(255,204,138,0.15)"; g.fill();
      g.strokeStyle = "rgba(255,204,138,0.8)"; g.lineWidth = 1.6; g.stroke();
      text(g, "F", X(0), Y(Math.min(view.y1 - 0.35, 1.7)), COL.amber, 24);
    }
    // real axis
    g.strokeStyle = COL.dim; g.lineWidth = 1.6;
    g.beginPath(); g.moveTo(0, Y(0)); g.lineTo(w, Y(0)); g.stroke();
    for (let x = Math.ceil(view.x0); x <= view.x1; x++) text(g, String(x), X(x), Y(0) + 14, COL.dim, 15, "center", false);
    text(g, "Im τ", 6, 14, COL.dim, 15, "left", true);
    return {X, Y, invX: px => view.x0 + px / w * (view.x1 - view.x0),
            invY: py => (h - padB - py) / (h - padB - padT) * view.y1};
  }

  /* ---------- widget loop ---------- */
  const widgets = [];
  function visible(node) { return node.offsetParent !== null; }
  function register(w) {
    widgets.push(w); w.dirty = true; w.root.__ms = w;
    if (w.root.dataset.poster) w.root.append(el("img", {class: "nh-ms-poster", src: w.root.dataset.poster, alt: "Статичный кадр интерактивного рисунка"}));
    return w;
  }
  const num = (v, d) => (v === undefined || v === "" || !Number.isFinite(Number(v)) ? d : Number(v));
  function loop(now) {
    requestAnimationFrame(loop);
    if (document.hidden) return;
    for (const w of widgets) {
      if (!visible(w.root)) continue;
      let d = w.dirty;
      for (const c of w.canvases || []) if (setupCanvas(c)) d = true;
      if (w.tick && w.tick(now)) d = true;
      if (d) { w.dirty = false; w.draw(); }
    }
  }
  let started = false;
  function start() { if (!started) { started = true; requestAnimationFrame(loop); } }
  function onReady(fn) {
    const once = () => fn();
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", once);
    else once();
  }

  window.NHMS = {
    PI, TWO_PI, COL, clamp, fmt, fmtC, el, button, slider, toggle,
    setupCanvas, ctxOf, pointer, text, arrow, dot,
    I2, MT, MTI, MS, mul2, mobius, reduceStep, reduceAll, inF, num,
    drawUHP, register, start, onReady, visible, builders: {}
  };
})();
