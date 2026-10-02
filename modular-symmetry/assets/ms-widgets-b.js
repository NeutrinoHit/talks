/* Widgets for chapters 6-9 of the modular-symmetry lecture:
 *   nh-ms-reduce   step-by-step reduction of tau into the fundamental domain F
 *   nh-ms-tiling   the tiling of the upper half plane by copies of F (plane and Poincare disk)
 */
(function () {
  "use strict";
  const N = window.NHMS;
  const {COL, PI, el, button, slider, toggle, ctxOf, pointer, text, arrow, dot, clamp, fmt, fmtC, num} = N;

  /* =================== nh-ms-reduce =================== */
  N.builders["nh-ms-reduce"] = function (root) {
    const START = [1.32, 0.34];
    const st = {tau: START.slice(), start: START.slice(), path: [START.slice()], log: [], M: N.I2,
                anim: null, auto: false, wait: 0, drag: false};
    const hp = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Верхняя полуплоскость: траектория точки τ при приведении к области F"});
    const lat = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Решётка с периодами 1 и τ; кратчайший вектор выделен"});
    const info = el("div", {class: "nh-t3d-info nh-ms-log"});
    const stepBtn = button("Шаг ▸", () => { st.auto = false; doStep(); });
    const autoBtn = button("▶ Авто", () => { st.auto = !st.auto; autoBtn.textContent = st.auto ? "❚❚ Стоп" : "▶ Авто"; });
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [stepBtn, autoBtn,
        button("Сначала", () => restart(st.start)),
        button("Случайная точка", () => restart([(Math.random() - 0.5) * 5, 0.12 + Math.random() * 0.7])),
        document.createTextNode("Или перетащите τ в плоскости слева.")]),
      el("div", {class: "nh-t3d-grid nh-ms-grid-lat"}, [hp, lat]),
      info);
    root.setAttribute("data-prevent-swipe", "");

    function restart(p) {
      st.tau = p.slice(); st.start = p.slice(); st.path = [p.slice()]; st.log = []; st.M = N.I2;
      st.anim = null; w.dirty = true;
    }
    function doStep() {
      if (st.anim) return;
      const s = N.reduceStep(st.tau[0], st.tau[1]);
      if (!s) return;
      const entry = {kind: s.kind, n: s.n, from: st.tau.slice(), to: [s.re, s.im]};
      st.anim = {t0: performance.now(), from: st.tau.slice(), to: [s.re, s.im], entry, M: s.M};
      w.dirty = true;
    }
    function tick(now) {
      let d = false;
      if (st.anim) {
        const k = clamp((now - st.anim.t0) / 650, 0, 1), e = k * k * (3 - 2 * k);
        st.tau = [st.anim.from[0] + (st.anim.to[0] - st.anim.from[0]) * e,
                  st.anim.from[1] + (st.anim.to[1] - st.anim.from[1]) * e];
        if (k >= 1) {
          st.tau = st.anim.to.slice(); st.path.push(st.tau.slice()); st.log.push(st.anim.entry);
          st.M = N.mul2(st.anim.M, st.M); st.anim = null; st.wait = now + 450;
        }
        d = true;
      } else if (st.auto && now > st.wait) {
        if (N.reduceStep(st.tau[0], st.tau[1])) doStep(); else st.auto = false;
        d = true;
      }
      return d;
    }
    const view = {x0: -2, x1: 2, y1: 2.6};
    let frame = null;
    function draw() {
      const g = ctxOf(hp), W = hp._w, H = hp._h;
      frame = N.drawUHP(g, W, H, view);
      // unit circle and geodesic hints
      g.strokeStyle = "rgba(95,125,140,0.55)"; g.lineWidth = 1.2; g.setLineDash([5, 5]);
      g.beginPath();
      for (let k = 0; k <= 80; k++) {
        const a = PI * k / 80;
        const x = frame.X(Math.cos(a)), y = frame.Y(Math.sin(a));
        if (k) g.lineTo(x, y); else g.moveTo(x, y);
      }
      g.stroke(); g.setLineDash([]);
      // path
      for (let k = 1; k < st.path.length; k++) {
        const a = st.path[k - 1], b = st.path[k];
        arrow(g, frame.X(a[0]), frame.Y(a[1]), frame.X(b[0]), frame.Y(b[1]), "rgba(255,204,138,0.8)", 2.2, 11);
      }
      for (const p of st.path) dot(g, frame.X(p[0]), frame.Y(p[1]), 4.5, "rgba(255,204,138,0.9)");
      const done = N.inF(st.tau[0], st.tau[1]);
      dot(g, frame.X(st.tau[0]), frame.Y(st.tau[1]), 9, done ? COL.green : COL.amber, "#fff", 2);
      text(g, "τ", frame.X(st.tau[0]) + 13, frame.Y(st.tau[1]) - 9, COL.pale, 24);

      // lattice for the current tau
      const g2 = ctxOf(lat), W2 = lat._w, H2 = lat._h;
      g2.fillStyle = COL.bg; g2.fillRect(0, 0, W2, H2);
      const [tr, ti] = st.tau;
      const u = Math.min(W2 / 5.6, H2 / 4.4), cx = W2 * 0.42, cy = H2 * 0.62;
      const X = x => cx + u * x, Y = y => cy - u * y;
      let minD = 1e9; const pts = [];
      for (let m = -12; m <= 12; m++) for (let n = -12; n <= 12; n++) {
        if (m === 0 && n === 0) continue;
        const x = m + n * tr, y = n * ti, d = Math.hypot(x, y);
        pts.push([x, y, d]); if (d < minD) minD = d;
      }
      g2.beginPath();
      [[0, 0], [1, 0], [1, 1], [0, 1]].forEach(([m, n], k) => {
        const x = m + n * tr, y = n * ti;
        if (k) g2.lineTo(X(x), Y(y)); else g2.moveTo(X(x), Y(y));
      });
      g2.closePath(); g2.fillStyle = "rgba(255,204,138,0.12)"; g2.fill();
      for (let m = -12; m <= 12; m++) for (let n = -12; n <= 12; n++) {
        const x = X(m + n * tr), y = Y(n * ti);
        if (x < -6 || y < -6 || x > W2 + 6 || y > H2 + 6) continue;
        dot(g2, x, y, m === 0 && n === 0 ? 5.5 : 3.6, "rgba(233,241,244,0.75)");
      }
      for (const [x, y, d] of pts) if (d < minD + 1e-9) dot(g2, X(x), Y(y), 11, null, "#ffe38a", 2.6);
      arrow(g2, X(0), Y(0), X(1), Y(0), COL.cyan, 4, 15);
      arrow(g2, X(0), Y(0), X(tr), Y(ti), COL.amber, 4, 15);
      text(g2, "1", X(0.5), Y(0) + 18, COL.cyan, 22, "center");
      text(g2, "τ", X(tr) + 10, Y(ti) - 14, COL.amber, 22);
      text(g2, "жёлтое кольцо — самые короткие векторы решётки", 10, H2 - 14, "#ffe38a", 15, "left", false);

      // log
      const cur = st.tau, next = st.anim ? null : N.reduceStep(cur[0], cur[1]);
      let html = "";
      st.log.forEach((s, k) => {
        if (s.kind === "T") html += `<div>${k + 1}. |Re τ| = ${Math.abs(s.from[0]).toFixed(2)} &gt; ½ → сдвиг на ${s.n > 0 ? "+" : "−"}${Math.abs(s.n)} (T${Math.abs(s.n) === 1 ? (s.n > 0 ? "" : "⁻¹") : (s.n > 0 ? "^" + s.n : "^−" + Math.abs(s.n))}). Im τ = ${s.to[1].toFixed(3)}</div>`;
        else html += `<div>${k + 1}. |τ| = ${Math.hypot(...s.from).toFixed(2)} &lt; 1 → инверсия S: τ → −1/τ. Im τ: ${s.from[1].toFixed(3)} → <b>${s.to[1].toFixed(3)}</b></div>`;
      });
      if (!st.anim) {
        if (!next) html += `<div class="nh-ms-ok"><b>Готово: τ = ${fmtC(cur[0], cur[1])} лежит в F</b> (|Re τ| ≤ ½, |τ| ≥ 1). Шагов: ${st.log.length}. Кратчайший вектор решётки теперь равен ω₁ = 1.</div>`;
        else if (next.kind === "T") html += `<div class="nh-ms-next">Дальше: |Re τ| = ${Math.abs(cur[0]).toFixed(2)} &gt; ½ — сдвигаем на целое число.</div>`;
        else html += `<div class="nh-ms-next">Дальше: |τ| = ${Math.hypot(...cur).toFixed(2)} &lt; 1 — единица не самая короткая; применяем S.</div>`;
      }
      info.innerHTML = html;
    }
    hp.addEventListener("pointerdown", e => { st.drag = true; hp.setPointerCapture(e.pointerId); move(e); e.preventDefault(); });
    hp.addEventListener("pointermove", e => { if (st.drag) move(e); });
    const up = () => { st.drag = false; };
    hp.addEventListener("pointerup", up); hp.addEventListener("pointercancel", up);
    function move(e) {
      if (!frame) return;
      const p = pointer(hp, e);
      restart([clamp(frame.invX(p[0]), -3, 3), Math.max(0.08, frame.invY(p[1]))]);
    }
    const w = N.register({root, canvases: [hp, lat], draw, tick});
    root.__nh = {st, restart, doStep};
  };

  /* =================== nh-ms-tiling =================== */
  N.builders["nh-ms-tiling"] = function (root) {
    const st = {view: root.dataset.view === "disk" ? "disk" : "plane", color: root.dataset.color === "inv" ? "inv" : "group", orbit: root.dataset.orbit !== "0",
                tau: [num(root.dataset.re, 0.31), num(root.dataset.im, 1.32)], lock: root.dataset.lock === "1", cache: null};
    const canvas = el("canvas", {class: "nh-ms-canvas nh-ms-tile", role: "img",
      "aria-label": "Верхняя полуплоскость, разбитая на копии области F"});
    const side = el("div", {class: "nh-ms-side"});
    const viewBtns = [["plane", "Плоскость τ"], ["disk", "Диск Пуанкаре"]].map(([k, t]) => button(t, () => { st.view = k; w.dirty = true; }));
    const colBtns = [["group", "Цвет: элемент группы"], ["inv", "Цвет: высота Im τ_F"]].map(([k, t]) => button(t, () => { st.color = k; w.dirty = true; }));
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [...viewBtns, ...colBtns,
        toggle("орбита точки", st.orbit, v => { st.orbit = v; w.dirty = true; })]),
      el("div", {class: "nh-t3d-grid nh-ms-grid-tile"}, [canvas, side]));
    root.setAttribute("data-prevent-swipe", "");

    /* ----- view geometry ----- */
    function geom() {
      const W = canvas._w, H = canvas._h;
      if (st.view === "plane") {
        const u = W / 5;
        return {W, H, u, toPix: (x, y) => [W / 2 + u * x, H - u * y],
                fromPix: (px, py) => [(px - W / 2) / u, (H - py) / u]};
      }
      const R = Math.min(W, H) / 2 - 6, cx = W / 2, cy = H / 2;
      return {W, H, R, cx, cy,
        toPix: (x, y) => {
          const den = x * x + (y + 1) * (y + 1);
          const a = (x * x + y * y - 1) / den, b = -2 * x / den;
          return [cx + R * a, cy - R * b];
        },
        fromPix: (px, py) => {
          const a = (px - cx) / R, b = (cy - py) / R, r2 = a * a + b * b;
          if (r2 >= 1) return null;
          const den = (1 - a) * (1 - a) + b * b;
          return [-2 * b / den, (1 - r2) / den];
        }};
    }
    /* ----- pixel colouring ----- */
    const hsl = (h, s, l) => {
      s /= 100; l /= 100;
      const k = n => (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
      const f = n => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
      return [f(0) * 255, f(8) * 255, f(4) * 255];
    };
    const RAMP = [[0, [13, 43, 69]], [0.45, [34, 120, 150]], [0.8, [133, 212, 232]], [1, [255, 204, 138]]];
    function ramp(t) {
      t = clamp(t, 0, 1);
      for (let k = 1; k < RAMP.length; k++) if (t <= RAMP[k][0]) {
        const [t0, c0] = RAMP[k - 1], [t1, c1] = RAMP[k], f = (t - t0) / (t1 - t0);
        return [c0[0] + (c1[0] - c0[0]) * f, c0[1] + (c1[1] - c0[1]) * f, c0[2] + (c1[2] - c0[2]) * f];
      }
      return RAMP[RAMP.length - 1][1];
    }
    function render(geo) {
      const rs = Math.min(canvas._scale, 1.5);
      const pw = Math.max(2, Math.round(geo.W * rs)), ph = Math.max(2, Math.round(geo.H * rs));
      const key = `${st.view}|${st.color}|${pw}x${ph}`;
      if (st.cache && st.cache.key === key) return st.cache.canvas;
      const off = document.createElement("canvas"); off.width = pw; off.height = ph;
      const ctx = off.getContext("2d"), img = ctx.createImageData(pw, ph), data = img.data;
      const keys = new Int32Array(pw * ph), vals = new Float32Array(pw * ph);
      for (let py = 0; py < ph; py++) for (let px = 0; px < pw; px++) {
        const t = geo.fromPix((px + 0.5) / rs, (py + 0.5) / rs);
        const i = py * pw + px;
        if (!t) { keys[i] = -1; continue; }
        let re = t[0], im = t[1], a = 1, b = 0, c = 0, d = 1, ok = false;
        for (let k = 0; k < 120; k++) {
          const n = Math.round(re);
          if (n !== 0) { re -= n; a -= n * c; b -= n * d; }
          const r2 = re * re + im * im;
          if (r2 < 1 - 1e-12) { re = -re / r2; im = im / r2; const na = -c, nb = -d; c = a; d = b; a = na; b = nb; }
          else { ok = true; break; }
        }
        if (!ok) { keys[i] = -2; continue; }
        if (c < 0 || (c === 0 && d < 0)) { a = -a; b = -b; c = -c; d = -d; }
        keys[i] = ((Math.imul(a | 0, 73856093) ^ Math.imul(b | 0, 19349663) ^ Math.imul(c | 0, 83492791) ^ Math.imul(d | 0, 2654435761)) >>> 1) | 0;
        if (a === 1 && b === 0 && c === 0 && d === 1) keys[i] = 1;
        vals[i] = im;
      }
      for (let py = 0; py < ph; py++) for (let px = 0; px < pw; px++) {
        const i = py * pw + px, k = keys[i];
        let rgb;
        if (k === -1) rgb = [8, 18, 29];
        else if (k === -2) rgb = [60, 60, 60];
        else if (st.color === "group") rgb = k === 1 ? [255, 204, 138] : hsl(Math.abs(k) % 360, 42, 30 + (Math.abs(k >> 9) % 3) * 5);
        else rgb = ramp(Math.log(vals[i] / 0.866) / Math.log(4.2));
        const edge = k >= 0 && ((px + 1 < pw && keys[i + 1] !== k) || (py + 1 < ph && keys[i + pw] !== k));
        const f = edge ? 0.35 : 1;
        data[i * 4] = rgb[0] * f; data[i * 4 + 1] = rgb[1] * f; data[i * 4 + 2] = rgb[2] * f; data[i * 4 + 3] = 255;
      }
      ctx.putImageData(img, 0, 0);
      st.cache = {key, canvas: off};
      return off;
    }
    /* ----- orbit ----- */
    const pairs = [];
    for (let c = 0; c <= 14; c++) for (let d = -14; d <= 14; d++) {
      if (c === 0 && d !== 1) continue;
      let gcd = (x, y) => (y ? gcd(y, x % y) : Math.abs(x));
      if (c > 0 && gcd(c, d) !== 1) continue;
      let a = 1, b = 0;
      if (c > 0) { for (a = 0; a < c; a++) if (((a * d - 1) % c + c) % c === 0) break; b = (a * d - 1) / c; }
      pairs.push([a, b, c, d]);
    }
    function orbitPoints(tau, geo) {
      const out = [];
      for (const [a, b, c, d] of pairs) {
        const [x, y] = N.mobius([a, b, c, d], tau[0], tau[1]);
        for (let k = -12; k <= 12; k++) {
          if (y < 0.05) continue;
          const px = geo.toPix(x + k, y);
          if (px[0] < 0 || px[1] < 0 || px[0] > geo.W || px[1] > geo.H) continue;
          if (st.view === "disk" && Math.hypot(px[0] - geo.cx, px[1] - geo.cy) > geo.R) continue;
          out.push(px);
        }
      }
      return out;
    }
    function fBoundary(geo) {
      const pts = [], top = st.view === "plane" ? 3 : 400;
      const s3 = Math.sqrt(3) / 2;
      for (let k = 0; k <= 60; k++) pts.push([-0.5, top - (top - s3) * k / 60]);
      for (let k = 0; k <= 60; k++) { const a = 2 * PI / 3 - PI / 3 * k / 60; pts.push([Math.cos(a), Math.sin(a)]); }
      for (let k = 0; k <= 60; k++) pts.push([0.5, s3 + (top - s3) * k / 60]);
      return pts.map(([x, y]) => geo.toPix(x, y));
    }
    function draw() {
      const geo = geom(), g = ctxOf(canvas), W = geo.W, H = geo.H;
      g.fillStyle = COL.bg; g.fillRect(0, 0, W, H);
      g.imageSmoothingEnabled = true;
      g.drawImage(render(geo), 0, 0, W, H);
      // F outline
      g.beginPath();
      fBoundary(geo).forEach(([x, y], k) => { if (k) g.lineTo(x, y); else g.moveTo(x, y); });
      g.strokeStyle = "#fff"; g.lineWidth = 2.2; g.stroke();
      // special points
      const mark = (x, y, lab, dx, dy) => {
        const [px, py] = geo.toPix(x, y);
        dot(g, px, py, 5, "#fff", "#08121d", 1.5);
        text(g, lab, px + dx, py + dy, "#fff", 22);
      };
      mark(0, 1, "i", 0, st.view === "plane" ? 16 : -14);
      mark(-0.5, Math.sqrt(3) / 2, "ρ", -16, 14);
      mark(0.5, Math.sqrt(3) / 2, "ρ+1", 24, 14);
      const red = N.reduceAll(st.tau[0], st.tau[1]);
      if (st.orbit) {
        for (const [x, y] of orbitPoints(st.tau, geo)) dot(g, x, y, 4.2, "rgba(255,255,255,0.95)", "rgba(8,18,29,0.9)", 1.2);
        const [fx, fy] = geo.toPix(red.re, red.im);
        dot(g, fx, fy, 9, null, "#fff", 3);
      }
      const [tx, ty] = geo.toPix(st.tau[0], st.tau[1]);
      dot(g, tx, ty, 6.5, COL.cyan, "#fff", 2);
      // side
      const M = red.M;
      const word = red.steps.map(s => s.kind === "S" ? "S" : `T${s.n > 0 ? "+" : "−"}${Math.abs(s.n)}`).join(" → ") || "— (τ уже в F)";
      side.innerHTML =
        `<p><b>τ = ${fmtC(st.tau[0], st.tau[1], 3)}</b>${st.lock ? " (зафиксировано)" : ""}</p>` +
        `<p>Приведение к F: <span class="nh-ms-muted">${word}</span></p>` +
        `<p>τ<sub>F</sub> = ${fmtC(red.re, red.im, 3)}</p>` +
        `<p>Матрица (a b; c d) = (${M[0]} ${M[1]}; ${M[2]} ${M[3]}), ad − bc = ${M[0] * M[3] - M[1] * M[2]}</p>` +
        `<p class="nh-ms-muted">${st.color === "group"
          ? "Каждая плитка — одна матрица из группы; светлая плитка — сама область F. Белые точки — всё, во что τ переходит под действием группы: один и тот же тор."
          : "Яркость = Im τ<sub>F</sub> — высота самой высокой точки орбиты. В каждой плитке картина одна и та же: функция от тора, а не от выбора клетки."}</p>` +
        `<p class="nh-ms-muted">Щелчок фиксирует точку.</p>`;
    }
    function setFromEvent(e) {
      const geo = geom(), p = pointer(canvas, e), t = geo.fromPix(p[0], p[1]);
      if (!t || t[1] < 0.02) return;
      st.tau = t; w.dirty = true;
    }
    canvas.addEventListener("pointermove", e => { if (!st.lock) setFromEvent(e); });
    canvas.addEventListener("pointerdown", e => { st.lock = !st.lock; if (!st.lock) setFromEvent(e); w.dirty = true; });
    const w = N.register({root, canvases: [canvas], draw});
    root.__nh = {st};
  };

  N.onReady(() => {
    document.querySelectorAll("[data-ms]").forEach(node => {
      const build = N.builders["nh-ms-" + node.dataset.ms];
      if (build) build(node);
    });
    N.start();
  });
})();
