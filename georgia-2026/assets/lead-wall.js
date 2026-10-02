/* "How much lead stops a neutrino?" for georgia-2026.
 * Lead bricks are added one after another along the path of neutrinos coming from the Sun
 * or from Alpha Centauri. A neutrino of about 1 MeV travels, on average, of order one
 * light-year of lead before it interacts once (order-of-magnitude figure), so the fraction that
 * passes a wall of thickness L is exp(-L/lambda) with lambda = 1 light-year.
 * The neutrinos leave the centre of the Sun in three rays towards Alpha Centauri. Their stopping depths
 * are stratified quantiles of the exponential law, so any 100 consecutive neutrinos show the expected
 * fraction exactly (50 of 100 pass 0.7 light-years of lead, 1 of 100 passes the way to Alpha Centauri).
 * Click on the picture to jump to the next stage.
 */
(function () {
  "use strict";

  const CYAN = "#85d4e8", AMBER = "#ffcc8a", PALE = "#e9f1f4", RED = "#ff7a6e", BG = "#050d16";
  const LY = 9.4607e15;          // metres in a light-year
  const LAMBDA = LY;             // mean free path of a ~1 MeV neutrino in lead, order of magnitude
  const SCENES = [
    {key: "sun", L: 1.496e11,
     head: "A lead wall 150 million km long",
     note: "Still all of them pass. About one neutrino in 60 000 is stopped."},
    {key: "half", L: Math.LN2 * LY,
     head: "A lead wall 0.7 light-years long",
     note: "Half of the neutrinos pass."},
    {key: "alpha", L: 4.367 * LY,
     head: "Lead all the way from the Sun to Alpha Centauri",
     note: "Only one neutrino in a hundred gets through."}
  ];

  const NB = 20, T0 = 0.7, BI = 0.26, DROP = 0.3, HOLD = 3.6;
  const T_BUILT = T0 + (NB - 1) * BI + DROP, T_END = T_BUILT + HOLD;
  const RATE = 51, SPEED = 640;
  const SUN = {x: 120, y: 230, r: 62};
  const THETA = 4 * Math.PI / 180, RAYS = [-THETA, 0, THETA];
  const WX0 = 215, WW = 980, BW = WW / NB, WY0 = 120, WY1 = 340;
  const DX = 1245;
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));

  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v; else if (k === "html") node.innerHTML = v; else if (k === "text") node.textContent = v; else node.setAttribute(k, v);
    }
    for (const c of children) node.append(c);
    return node;
  }
  function onReady(fn) {
    let done = false;
    const once = () => { if (!done) { done = true; fn(); } };
    if (window.Reveal && typeof Reveal.on === "function") {
      Reveal.on("ready", once);
      if (Reveal.isReady && Reveal.isReady()) once();
    } else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", once, {once: true});
    else once();
  }
  const visible = node => node.offsetParent !== null;
  function fit(canvas) {
    const reveal = window.Reveal && typeof Reveal.getScale === "function" ? Reveal.getScale() : 1;
    const scale = Math.max(1, reveal) * Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(2, Math.round(canvas.clientWidth * scale));
    const h = Math.max(2, Math.round(canvas.clientHeight * scale));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; return true; }
    return false;
  }
  const sig = x => x >= 100 ? String(Math.round(x)) : x >= 9.95 ? x.toFixed(0) : x >= 1 ? x.toFixed(1).replace(/\.0$/, "") : x.toFixed(2);
  function fmtLen(m) {
    if (m < 1) return Math.round(m * 100) + " cm";
    if (m < 1e3) return (m < 10 ? m.toFixed(1).replace(/\.0$/, "") : Math.round(m)) + " m";
    if (m < 1e9) return Math.round(m / 1e3).toLocaleString("en-US") + " km";
    if (m < 1e12) return sig(m / 1e9) + " million km";
    if (m < 0.01 * LY) return sig(m / 1e12) + " billion km";
    const ly = m / LY;
    return (ly < 0.1 ? ly.toFixed(3) : ly < 1 ? ly.toFixed(2) : sig(ly)) + " light-years";
  }
  function pct(p) {
    const q = 100 * p;
    if (q >= 99.9995) return "100 %";
    if (q >= 99.9) return q.toFixed(3) + " %";
    if (q >= 10) return q.toFixed(0) + " %";
    return q.toFixed(1) + " %";
  }

  // background stars: fixed, reproducible
  function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const STARS = (() => {
    const r = rng(2026), out = [], tints = ["#ffffff", "#cfe0ff", "#fff2d0", "#ffd9bf", "#bcd4ff"];
    for (let i = 0; i < 170; i++) out.push({x: r() * 1400, y: r() * 480, s: 0.5 + Math.pow(r(), 3) * 1.9, c: tints[Math.floor(r() * tints.length)], ph: r() * 6.28, big: r() > 0.96});
    return out;
  })();

  function build(root) {
    const canvas = el("canvas", {class: "nh-lw-canvas", role: "img",
      "aria-label": "Neutrinos leave the Sun in three rays towards Alpha Centauri and cross lead bricks added one by one; the neutrinos that pass are counted"});
    const poster = el("img", {class: "nh-lw-poster", alt: "Lead all the way from the Sun to Alpha Centauri stops all but about one neutrino in a hundred", src: root.dataset.poster || ""});
    const title = el("span", {class: "nh-lw-title"});
    const note = el("span", {class: "nh-lw-note"});
    const head = el("div", {class: "nh-lw-head"}, [title, note]);
    const info = el("p", {class: "nh-lw-info"});
    root.replaceChildren(head, canvas, poster, info);

    let sc = 0, t = 0, nid = 0, emitAcc = 0, clock = 0;
    let nus = [], bursts = [], outcomes = [], flash = 0;
    function reset() { t = 0; emitAcc = 0; nus = []; bursts = []; outcomes = []; flash = 0; }
    function select(i) { sc = ((i % SCENES.length) + SCENES.length) % SCENES.length; reset(); labels(); }
    function labels() { title.textContent = SCENES[sc].head; }
    canvas.addEventListener("click", () => select(sc + 1));
    const landed = () => clamp(Math.floor((t - T0 - DROP) / BI) + 1, 0, NB);
    const thickness = () => SCENES[sc].L * landed() / NB;

    function spawn() {
      const j = nid++;
      const u = (((j * 37) % 100) + 0.5) / 100;          // stratified quantiles, scattered in time
      const th = RAYS[j % 3];
      nus.push({x: SUN.x, th, y: SUN.y, depth: -Math.log(u) * LAMBDA, decided: false, stopX: 0, stops: false});
    }
    function step(dt) {
      t += dt; clock += dt;
      const S = SCENES[sc], Lc = thickness();
      emitAcc += dt * RATE;
      while (emitAcc >= 1) { emitAcc -= 1; spawn(); }
      const keep = [];
      for (const n of nus) {
        n.x += SPEED * dt;
        n.y = SUN.y + (n.x - SUN.x) * Math.tan(n.th);
        if (!n.decided && n.x >= WX0) {
          n.decided = true;
          n.stops = n.depth < Lc;
          if (n.stops) n.stopX = WX0 + WW * n.depth / S.L;
          outcomes.push(n.stops ? 0 : 1); if (outcomes.length > 100) outcomes.shift();
        }
        if (n.decided && n.stops && n.x >= n.stopX) { bursts.push({x: n.stopX, y: n.y, age: 0}); continue; }
        if (n.x >= DX) { flash = Math.min(1, flash + 0.12); continue; }
        keep.push(n);
      }
      nus = keep;
      for (const b of bursts) b.age += dt;
      bursts = bursts.filter(b => b.age < 0.6);
      flash = Math.max(0, flash - dt * 3);
      if (t >= T_END && sc < SCENES.length - 1) select(sc + 1);
    }
    function run(seconds) { for (let k = 0; k < seconds * 60; k++) step(1 / 60); draw(); updateText(); }

    function disc(ctx, cx, cy, r, c0, c1, glow) {
      const gl = ctx.createRadialGradient(cx, cy, r * 0.9, cx, cy, r + glow);
      gl.addColorStop(0, c1 + "99"); gl.addColorStop(1, c1 + "00");
      ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(cx, cy, r + glow, 0, 2 * Math.PI); ctx.fill();
      const g = ctx.createRadialGradient(cx - r * 0.25, cy - r * 0.25, r * 0.1, cx, cy, r);
      g.addColorStop(0, c0); g.addColorStop(1, c1);
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 2 * Math.PI); ctx.fill();
    }
    function label(ctx, text, x, y) {
      ctx.font = "bold 26px system-ui, sans-serif"; ctx.textAlign = "center"; ctx.lineJoin = "round";
      ctx.lineWidth = 6; ctx.strokeStyle = BG; ctx.strokeText(text, x, y);
      ctx.fillStyle = "#fff"; ctx.fillText(text, x, y);
    }
    function drawSpace(ctx) {
      for (const s of STARS) {
        const tw = 0.65 + 0.35 * Math.sin(clock * 1.3 + s.ph);
        ctx.globalAlpha = (s.s > 1.2 ? 0.95 : 0.7) * tw; ctx.fillStyle = s.c;
        ctx.beginPath(); ctx.arc(s.x, s.y, s.s, 0, 2 * Math.PI); ctx.fill();
        if (s.big) { ctx.globalAlpha = 0.35 * tw; ctx.fillRect(s.x - 7, s.y - 0.4, 14, 0.8); ctx.fillRect(s.x - 0.4, s.y - 7, 0.8, 14); }
      }
      ctx.globalAlpha = 1;
    }
    function drawStars(ctx) {
      disc(ctx, SUN.x, SUN.y, SUN.r, "#fff6c0", "#ffab26", 46);
      label(ctx, "Sun", SUN.x, SUN.y + SUN.r + 40);
      const f = flash * 0.5;
      disc(ctx, 1300, 185, 58, "#ffffff", "#ffd45c", 38 + 22 * f);
      disc(ctx, 1332, 300, 42, "#ffe2b8", "#ff8f3a", 34 + 20 * f);
      label(ctx, "Alpha Centauri", 1272, 424);
    }
    function drawBrick(ctx, k) {
      const tk = T0 + k * BI, p = clamp((t - tk) / DROP, 0, 1);
      if (p <= 0) return;
      const e = 1 - Math.pow(1 - p, 3), x = WX0 + k * BW, off = -(1 - e) * 90;
      ctx.globalAlpha = e;
      const g = ctx.createLinearGradient(0, WY0, 0, WY1);
      g.addColorStop(0, "#8b97a4"); g.addColorStop(0.5, "#697583"); g.addColorStop(1, "#4f5a66");
      ctx.fillStyle = g; ctx.fillRect(x + 1, WY0 + off, BW - 2, WY1 - WY0);
      ctx.strokeStyle = "#b4bfca"; ctx.lineWidth = 1.4; ctx.strokeRect(x + 1.5, WY0 + off + 0.5, BW - 3, WY1 - WY0 - 1);
      ctx.fillStyle = "rgba(255,255,255,0.12)"; ctx.fillRect(x + 3, WY0 + off + 3, BW - 6, 10);
      if (k === 0) { ctx.fillStyle = "#e9f1f4"; ctx.font = "bold 22px system-ui, sans-serif"; ctx.textAlign = "center"; ctx.fillText("Pb", x + BW / 2, WY0 + off + 36); }
      ctx.globalAlpha = 1;
    }
    function draw() {
      fit(canvas);
      const W = canvas.width, u = W / 1400, ctx = canvas.getContext("2d");
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, W, canvas.height);
      ctx.setTransform(u, 0, 0, u, 0, 0);
      const S = SCENES[sc];
      drawSpace(ctx);
      // the three rays
      ctx.strokeStyle = "rgba(133,212,232,0.16)"; ctx.lineWidth = 1.5;
      for (const th of RAYS) { ctx.beginPath(); ctx.moveTo(SUN.x, SUN.y); ctx.lineTo(DX, SUN.y + (DX - SUN.x) * Math.tan(th)); ctx.stroke(); }
      drawStars(ctx);
      for (let k = 0; k < NB; k++) drawBrick(ctx, k);
      // scale of the wall
      ctx.strokeStyle = "#8aa2b2"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(WX0, 372); ctx.lineTo(WX0 + WW, 372);
      ctx.moveTo(WX0, 364); ctx.lineTo(WX0, 380); ctx.moveTo(WX0 + WW, 364); ctx.lineTo(WX0 + WW, 380); ctx.stroke();
      ctx.fillStyle = AMBER; ctx.font = "bold 24px system-ui, sans-serif"; ctx.textAlign = "center";
      ctx.fillText("wall: " + fmtLen(S.L), WX0 + WW / 2, 412);
      ctx.fillStyle = "#c3d2dc"; ctx.font = "20px system-ui, sans-serif";
      ctx.fillText("each brick: " + fmtLen(S.L / NB), WX0 + WW / 2, 441);
      // neutrinos
      for (const n of nus) {
        const inside = n.x > WX0 && n.x < WX0 + WW;
        ctx.fillStyle = "rgba(133,212,232,0.25)"; ctx.beginPath(); ctx.arc(n.x, n.y, 8, 0, 2 * Math.PI); ctx.fill();
        ctx.fillStyle = inside ? "#bff0ff" : CYAN; ctx.strokeStyle = "#04101a"; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(n.x, n.y, 4.6, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
      }
      for (const b of bursts) {
        const a = 1 - b.age / 0.6;
        ctx.strokeStyle = `rgba(255,122,110,${a})`; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(b.x, b.y, 5 + b.age * 55, 0, 2 * Math.PI); ctx.stroke();
        ctx.fillStyle = `rgba(255,170,150,${a})`; ctx.beginPath(); ctx.arc(b.x, b.y, 4, 0, 2 * Math.PI); ctx.fill();
      }
    }
    function updateText() {
      const Lc = thickness(), p = Math.exp(-Lc / LAMBDA);
      const n = outcomes.length, pass = outcomes.reduce((a, b) => a + b, 0);
      const count = n ? `${pass} of the last ${n}` : "–";
      info.innerHTML = `Lead so far: <b>${fmtLen(Lc)}</b> &nbsp;·&nbsp; Neutrinos that pass: <b class="c-cyan">${pct(p)}</b> &nbsp;·&nbsp; ${count}`;
      note.textContent = t >= T_BUILT ? SCENES[sc].note : "";
    }

    labels();
    let last = performance.now(), wasVisible = false;
    function frame(now) {
      requestAnimationFrame(frame);
      const dt = clamp((now - last) / 1000, 0, 0.05); last = now;
      const vis = visible(root);
      if (!vis) { wasVisible = false; return; }
      if (!wasVisible) {
        wasVisible = true;
        if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) { select(SCENES.length - 1); t = T_END; }
        else select(0);
      }
      step(dt); draw(); updateText();
    }
    requestAnimationFrame(frame);
    root.__nh = {select, run, step, draw, state: () => ({sc, t, outcomes})};
  }

  onReady(() => { const root = document.getElementById("nh-lead-wall"); if (root) build(root); });
})();
