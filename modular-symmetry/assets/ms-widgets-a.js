/* Widgets for chapters 1-4 of the modular-symmetry lecture:
 *   nh-ms-world     a periodic world: a torus seen as a tiled plane, with a draggable point
 *   nh-ms-lattice   two period vectors; rotating/scaling both leaves tau = omega2/omega1 alone
 *   nh-ms-basis     the same lattice with another pair of periods (integer matrix, det check)
 *   nh-ms-symmetry  which rotations and mirrors map a lattice onto itself
 */
(function () {
  "use strict";
  const N = window.NHMS;
  const {COL, TWO_PI, PI, el, button, slider, toggle, ctxOf, pointer, text, arrow, dot, clamp, fmt, fmtC, num} = N;

  /* =================== nh-ms-world =================== */
  N.builders["nh-ms-world"] = function (root) {
    const st = {re: num(root.dataset.re, 0.35), im: num(root.dataset.im, 1.0), raw: [0.3, 0.35], trail: [], drag: false, copies: true};
    const canvas = el("canvas", {class: "nh-ms-canvas nh-ms-wide", role: "img",
      "aria-label": "Плоскость, замощённая копиями одной клетки; точку можно тянуть"});
    const info = el("p", {class: "nh-t3d-info"});
    const reS = slider("Re τ", -1, 1, 0.01, st.re, v => { st.re = v; w.dirty = true; });
    const imS = slider("Im τ", 0.4, 2, 0.01, st.im, v => { st.im = v; w.dirty = true; });
    const setTau = (re, im) => { st.re = re; st.im = im; reS.set(re); imS.set(im); w.dirty = true; };
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [
        reS.wrap, imS.wrap,
        button("Квадрат", () => setTau(0, 1)),
        button("Сдвиг", () => setTau(0.5, 1)),
        toggle("копии клетки", true, v => { st.copies = v; w.dirty = true; }),
        button("Стереть след", () => { st.trail = []; w.dirty = true; })]),
      canvas, info);
    root.setAttribute("data-prevent-swipe", "");

    let geo = {u: 100, ox: 0, oy: 0};
    function layout() {
      const W = canvas._w, H = canvas._h;
      const u = Math.min(W / 6.5, H / (st.im * 2.7));
      geo = {u, ox: W / 2 - (1 + st.re) * u / 2, oy: H / 2 + st.im * u / 2};
    }
    const P = (s, t) => [geo.ox + geo.u * (s + t * st.re), geo.oy - geo.u * t * st.im];
    const wrap1 = x => x - Math.floor(x);

    function glyph(g, m, n, fill) {
      // an asymmetric letter "F" in cell coordinates (s, t) -- orientation is preserved by gluing
      const rects = [[0.24, 0.14, 0.38, 0.86], [0.24, 0.74, 0.74, 0.86], [0.24, 0.46, 0.62, 0.58]];
      g.fillStyle = fill;
      for (const [s0, t0, s1, t1] of rects) {
        g.beginPath();
        for (const [s, t] of [[s0, t0], [s1, t0], [s1, t1], [s0, t1]]) {
          const [x, y] = P(s + m, t + n);
          if (s === s0 && t === t0) g.moveTo(x, y); else g.lineTo(x, y);
        }
        g.closePath(); g.fill();
      }
    }
    function cellPath(g, m, n) {
      g.beginPath();
      [[0, 0], [1, 0], [1, 1], [0, 1]].forEach(([s, t], k) => {
        const [x, y] = P(s + m, t + n);
        if (k) g.lineTo(x, y); else g.moveTo(x, y);
      });
      g.closePath();
    }
    function draw() {
      layout();
      const g = ctxOf(canvas), W = canvas._w, H = canvas._h;
      g.fillStyle = COL.bg; g.fillRect(0, 0, W, H);
      const rangeM = [-6, 7], rangeN = [-4, 4];
      // cells
      for (let n = rangeN[0]; n <= rangeN[1]; n++) for (let m = rangeM[0]; m <= rangeM[1]; m++) {
        const base = m === 0 && n === 0;
        if (!st.copies && !base) continue;
        cellPath(g, m, n);
        g.fillStyle = base ? "rgba(255,255,255,0.05)" : "rgba(255,255,255,0.0)"; g.fill();
        g.strokeStyle = base ? COL.pale : "rgba(233,241,244,0.16)"; g.lineWidth = base ? 2.4 : 1;
        g.stroke();
        glyph(g, m, n, base ? "rgba(255,204,138,0.95)" : "rgba(255,204,138,0.30)");
      }
      // side arrows on the base cell: cyan = omega1 = 1, amber = omega2 = tau
      const side = (s0, t0, s1, t1, color) => {
        const a = P(s0, t0), b = P(s1, t1);
        arrow(g, a[0], a[1], b[0], b[1], color, 3.2, 13);
      };
      side(0.38, 0, 0.62, 0, COL.cyan); side(0.38, 1, 0.62, 1, COL.cyan);
      side(0, 0.38, 0, 0.62, COL.amber); side(1, 0.38, 1, 0.62, COL.amber);
      // trail
      if (st.trail.length > 1) {
        const sh = [Math.floor(st.trail[0][0]), Math.floor(st.trail[0][1])];
        g.lineWidth = 2.2; g.strokeStyle = "rgba(133,212,232,0.85)"; g.lineJoin = "round";
        for (let n = rangeN[0]; n <= rangeN[1]; n++) for (let m = rangeM[0]; m <= rangeM[1]; m++) {
          if (!st.copies && (m !== 0 || n !== 0)) continue;
          g.beginPath();
          st.trail.forEach(([s, t], k) => {
            const [x, y] = P(s - sh[0] + m, t - sh[1] + n);
            if (k) g.lineTo(x, y); else g.moveTo(x, y);
          });
          g.stroke();
        }
      }
      // the point and its copies
      const s = wrap1(st.raw[0]), t = wrap1(st.raw[1]);
      for (let n = rangeN[0]; n <= rangeN[1]; n++) for (let m = rangeM[0]; m <= rangeM[1]; m++) {
        const base = m === 0 && n === 0;
        if (!st.copies && !base) continue;
        const [x, y] = P(s + m, t + n);
        dot(g, x, y, base ? 9 : 6, base ? COL.cyan : "rgba(133,212,232,0.55)", base ? "#fff" : null, 2);
      }
      text(g, "1", ...P(0.5, 0).map((v, i) => v + (i ? 18 : 0)), COL.cyan, 22, "center");
      text(g, "τ", ...P(0, 0.5).map((v, i) => v - (i ? 0 : 18)), COL.amber, 22, "center");
      const z = [s + t * st.re, t * st.im];
      info.innerHTML = `Точка в клетке: <b>(s, t) = (${s.toFixed(2)}, ${t.toFixed(2)})</b>, то есть z = s + tτ = ${fmtC(z[0], z[1])}. ` +
        `Выйдя за правую сторону, она вернётся слева; за верхнюю — снизу.`;
    }
    function setRaw(p) {
      const x = (p[0] - geo.ox) / geo.u, y = (geo.oy - p[1]) / geo.u;
      const t = y / st.im, s = x - t * st.re;
      st.raw = [s, t];
      if (st.drag) st.trail.push([s, t]);
      if (st.trail.length > 3000) st.trail.shift();
      w.dirty = true;
    }
    canvas.addEventListener("pointerdown", e => {
      canvas.setPointerCapture(e.pointerId); st.drag = true; st.trail = [];
      setRaw(pointer(canvas, e)); e.preventDefault();
    });
    canvas.addEventListener("pointermove", e => { if (st.drag) setRaw(pointer(canvas, e)); });
    const up = () => { st.drag = false; };
    canvas.addEventListener("pointerup", up); canvas.addEventListener("pointercancel", up);
    const w = N.register({root, canvases: [canvas], draw});
    root.__nh = {st, setTau};
  };

  /* =================== nh-ms-lattice =================== */
  N.builders["nh-ms-lattice"] = function (root) {
    const st = {b1: [1, 0], b2: [0.3, 1.1], rot: 0, lam: 1, drag: null};
    const plane = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Решётка из точек m·ω₁ + n·ω₂; концы векторов можно тянуть"});
    const hp = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Верхняя полуплоскость с точкой τ = ω₂/ω₁"});
    const info = el("p", {class: "nh-t3d-info"});
    const rotS = slider("поворот, °", -180, 180, 1, 0, v => { st.rot = v; w.dirty = true; }, 0);
    const lamS = slider("растяжение", 0.5, 2, 0.01, 1, v => { st.lam = v; w.dirty = true; });
    const reset = () => { st.b1 = [1, 0]; st.b2 = [0.3, 1.1]; st.rot = 0; st.lam = 1; rotS.set(0); lamS.set(1); w.dirty = true; };
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [rotS.wrap, lamS.wrap, button("Сначала", reset)]),
      el("div", {class: "nh-t3d-grid nh-ms-grid-lat"}, [plane, hp]),
      info);
    root.setAttribute("data-prevent-swipe", "");

    const rotc = () => [st.lam * Math.cos(st.rot * PI / 180), st.lam * Math.sin(st.rot * PI / 180)];
    const cm = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
    const cdiv = (a, b) => { const d = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d]; };
    const eff = () => { const r = rotc(); return [cm(r, st.b1), cm(r, st.b2)]; };
    const tauOf = () => cdiv(st.b2, st.b1);
    let geo = {u: 80, cx: 0, cy: 0};
    function draw() {
      const g = ctxOf(plane), W = plane._w, H = plane._h;
      geo = {u: H / 6.4, cx: W / 2, cy: H / 2};
      const X = x => geo.cx + geo.u * x, Y = y => geo.cy - geo.u * y;
      g.fillStyle = COL.bg; g.fillRect(0, 0, W, H);
      const [w1, w2] = eff();
      // cell
      g.beginPath();
      [[0, 0], [1, 0], [1, 1], [0, 1]].forEach(([m, n], k) => {
        const x = m * w1[0] + n * w2[0], y = m * w1[1] + n * w2[1];
        if (k) g.lineTo(X(x), Y(y)); else g.moveTo(X(x), Y(y));
      });
      g.closePath(); g.fillStyle = "rgba(255,204,138,0.14)"; g.fill();
      g.strokeStyle = "rgba(255,204,138,0.7)"; g.lineWidth = 1.5; g.stroke();
      // dots
      for (let m = -25; m <= 25; m++) for (let n = -25; n <= 25; n++) {
        const x = X(m * w1[0] + n * w2[0]), y = Y(m * w1[1] + n * w2[1]);
        if (x < -6 || y < -6 || x > W + 6 || y > H + 6) continue;
        dot(g, x, y, m === 0 && n === 0 ? 5.5 : 3.6, m === 0 && n === 0 ? COL.pale : "rgba(233,241,244,0.75)");
      }
      arrow(g, X(0), Y(0), X(w1[0]), Y(w1[1]), COL.cyan, 4, 15);
      arrow(g, X(0), Y(0), X(w2[0]), Y(w2[1]), COL.amber, 4, 15);
      dot(g, X(w1[0]), Y(w1[1]), 9, null, COL.cyan, 2.5);
      dot(g, X(w2[0]), Y(w2[1]), 9, null, COL.amber, 2.5);
      text(g, "ω₁", X(w1[0]) + 14, Y(w1[1]) + 20, COL.cyan, 24);
      text(g, "ω₂", X(w2[0]) + 14, Y(w2[1]) - 6, COL.amber, 24);
      // upper half plane
      const g2 = ctxOf(hp), W2 = hp._w, H2 = hp._h;
      const frame = N.drawUHP(g2, W2, H2, {x0: -1.6, x1: 1.6, y1: 2.6});
      const tau = tauOf();
      if (tau[1] > 0) {
        dot(g2, frame.X(tau[0]), frame.Y(tau[1]), 9, COL.amber, "#fff", 2);
        text(g2, "τ", frame.X(tau[0]) + 14, frame.Y(tau[1]) - 8, COL.amber, 24);
      } else {
        text(g2, "Im τ < 0: поменяйте ω₁ и ω₂ местами", W2 / 2, H2 / 2, COL.red, 19, "center", false);
      }
      const l1 = Math.hypot(...w1), l2 = Math.hypot(...w2);
      info.innerHTML = `|ω₁| = ${l1.toFixed(2)}, |ω₂| = ${l2.toFixed(2)}. ` +
        `<b>τ = ω₂/ω₁ = ${fmtC(tau[0], tau[1])}</b>` +
        (tau[1] > 0 ? "" : " — нижняя полуплоскость") +
        `. Тяните концы векторов; поворот и растяжение двигают оба вектора, а τ остаётся на месте.`;
    }
    plane.addEventListener("pointerdown", e => {
      const p = pointer(plane, e), [w1, w2] = eff();
      const pts = [[geo.cx + geo.u * w1[0], geo.cy - geo.u * w1[1]], [geo.cx + geo.u * w2[0], geo.cy - geo.u * w2[1]]];
      const d = pts.map(q => Math.hypot(q[0] - p[0], q[1] - p[1]));
      const k = d[0] < d[1] ? 0 : 1;
      if (d[k] < 34) { st.drag = k; plane.setPointerCapture(e.pointerId); e.preventDefault(); }
    });
    plane.addEventListener("pointermove", e => {
      if (st.drag === null) return;
      const p = pointer(plane, e);
      const v = [(p[0] - geo.cx) / geo.u, (geo.cy - p[1]) / geo.u];
      const r = rotc(), r2 = r[0] * r[0] + r[1] * r[1];
      const b = cm([r[0] / r2, -r[1] / r2], v);
      if (Math.hypot(...b) < 0.2) return;
      if (st.drag === 0) st.b1 = b; else st.b2 = b;
      w.dirty = true;
    });
    const up = () => { st.drag = null; };
    plane.addEventListener("pointerup", up); plane.addEventListener("pointercancel", up);
    const w = N.register({root, canvases: [plane, hp], draw});
    root.__nh = {st, reset};
  };

  /* =================== nh-ms-basis =================== */
  N.builders["nh-ms-basis"] = function (root) {
    const st = {re: num(root.dataset.re, 0.30), im: num(root.dataset.im, 1.20),
                M: (root.dataset.m || "1,0,0,1").split(",").map(Number), vis: null, tween: null};
    const plane = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Одна и та же решётка с двумя парами периодов"});
    const hp = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Точки τ и τ′ в верхней полуплоскости"});
    const info = el("div", {class: "nh-t3d-info nh-ms-basis-info"});
    const reS = slider("Re τ", -0.9, 0.9, 0.01, st.re, v => { st.re = v; jump(); });
    const imS = slider("Im τ", 0.5, 1.8, 0.01, st.im, v => { st.im = v; jump(); });
    const inputs = [0, 1, 2, 3].map(k => {
      const i = el("input", {type: "number", step: 1, value: st.M[k], class: "nh-ms-num"});
      i.addEventListener("input", () => {
        const v = parseInt(i.value, 10);
        if (Number.isFinite(v)) { const M = st.M.slice(); M[k] = clamp(v, -9, 9); setM(M, false); }
      });
      return i;
    });
    const mat = el("span", {class: "nh-ms-mat"}, inputs);
    const presets = [
      ["1", [1, 0, 0, 1], "исходные периоды"],
      ["T", [1, 1, 0, 1], "ω₂ → ω₂ + ω₁"],
      ["S", [0, -1, 1, 0], "ω₁ → ω₂, ω₂ → −ω₁"],
      ["ST", [0, -1, 1, 1], ""],
      ["T²", [1, 2, 0, 1], ""],
      ["ad−bc = 2", [2, 0, 0, 1], "слишком крупная клетка"],
      ["ad−bc = −1", [0, 1, 1, 0], "стороны поменяли без знака"]
    ].map(([label, M, tip]) => button(label, () => setM(M, true), tip));
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [reS.wrap, imS.wrap]),
      el("div", {class: "nh-interactive-controls"}, [document.createTextNode("Новые периоды: ω₂′ = aω₂ + bω₁, ω₁′ = cω₂ + dω₁;  (a b; c d) ="), mat, ...presets]),
      el("div", {class: "nh-t3d-grid nh-ms-grid-lat"}, [plane, hp]),
      info);
    root.setAttribute("data-prevent-swipe", "");

    function targets(M = st.M) {
      const [a, b, c, d] = M;
      return {w1: [c * st.re + d, c * st.im], w2: [a * st.re + b, a * st.im]};
    }
    function setM(M, syncInputs) {
      st.M = M;
      if (syncInputs) inputs.forEach((i, k) => { i.value = M[k]; });
      const to = targets(M), from = st.vis || to;
      st.tween = {t0: performance.now(), from: JSON.parse(JSON.stringify(from)), to};
      w.dirty = true;
    }
    function jump() { st.vis = targets(); st.tween = null; w.dirty = true; }
    st.vis = targets();

    function tick(now) {
      if (!st.tween) return false;
      const k = clamp((now - st.tween.t0) / 650, 0, 1), e = k * k * (3 - 2 * k);
      const L = (A, B) => [A[0] + (B[0] - A[0]) * e, A[1] + (B[1] - A[1]) * e];
      st.vis = {w1: L(st.tween.from.w1, st.tween.to.w1), w2: L(st.tween.from.w2, st.tween.to.w2)};
      if (k >= 1) st.tween = null;
      return true;
    }
    function draw() {
      const g = ctxOf(plane), W = plane._w, H = plane._h;
      const u = Math.min(W / 6.6, H / 5.4), cx = W * 0.36, cy = H * 0.64;
      const X = x => cx + u * x, Y = y => cy - u * y;
      g.fillStyle = COL.bg; g.fillRect(0, 0, W, H);
      const [a, b, c, d] = st.M, D = a * d - b * c;
      const {w1, w2} = st.vis;
      // new cell
      g.beginPath();
      [[0, 0], [1, 0], [1, 1], [0, 1]].forEach(([m, n], k) => {
        const x = m * w2[0] + n * w1[0], y = m * w2[1] + n * w1[1];
        if (k) g.lineTo(X(x), Y(y)); else g.moveTo(X(x), Y(y));
      });
      g.closePath();
      g.fillStyle = D === 1 ? "rgba(133,212,232,0.16)" : "rgba(255,123,123,0.14)"; g.fill();
      g.strokeStyle = D === 1 ? "rgba(133,212,232,0.8)" : "rgba(255,123,123,0.8)"; g.lineWidth = 1.6; g.stroke();
      // lattice points of the ORIGINAL lattice  m + n tau
      for (let m = -22; m <= 22; m++) for (let n = -22; n <= 22; n++) {
        const px = X(m + n * st.re), py = Y(n * st.im);
        if (px < -8 || py < -8 || px > W + 8 || py > H + 8) continue;
        let inSub = true;
        if (D !== 0) {
          const x = (d * n - c * m) / D, y = (-b * n + a * m) / D;
          inSub = Math.abs(x - Math.round(x)) < 1e-9 && Math.abs(y - Math.round(y)) < 1e-9;
        }
        if (inSub) dot(g, px, py, m === 0 && n === 0 ? 5.5 : 3.6, "rgba(233,241,244,0.8)");
        else dot(g, px, py, 5.5, null, COL.red, 2);
      }
      // old basis (thin) and new basis (thick)
      arrow(g, X(0), Y(0), X(1), Y(0), "rgba(233,241,244,0.55)", 1.8, 9);
      arrow(g, X(0), Y(0), X(st.re), Y(st.im), "rgba(233,241,244,0.55)", 1.8, 9);
      text(g, "ω₁", X(1) - 8, Y(0) + 22, "rgba(233,241,244,0.8)", 18, "center");
      text(g, "ω₂", X(st.re) - 24, Y(st.im) + 4, "rgba(233,241,244,0.8)", 18, "center");
      if (D !== 0) {
        arrow(g, X(0), Y(0), X(w1[0]), Y(w1[1]), COL.cyan, 4.2, 15);
        arrow(g, X(0), Y(0), X(w2[0]), Y(w2[1]), COL.amber, 4.2, 15);
        text(g, "ω₁′", X(w1[0]) + 16, Y(w1[1]) - 14, COL.cyan, 24);
        text(g, "ω₂′", X(w2[0]) + 16, Y(w2[1]) - 14, COL.amber, 24);
      }
      // upper half plane
      const g2 = ctxOf(hp), W2 = hp._w, H2 = hp._h;
      const frame = N.drawUHP(g2, W2, H2, {x0: -1.6, x1: 1.6, y1: 2.6});
      dot(g2, frame.X(st.re), frame.Y(st.im), 8, COL.pale, "#fff", 2);
      text(g2, "τ", frame.X(st.re) + 12, frame.Y(st.im) - 8, COL.pale, 22);
      const den = (c * st.re + d) ** 2 + (c * st.im) ** 2;
      let tp = null;
      if (den > 1e-12) tp = N.mobius(st.M, st.re, st.im);
      if (tp && D === 1) {
        const px = clamp(frame.X(tp[0]), 8, W2 - 8), py = clamp(frame.Y(tp[1]), 8, H2 - 8);
        dot(g2, px, py, 8, COL.amber, "#fff", 2);
        text(g2, "τ′", px + 12, py - 8, COL.amber, 22);
      }
      // text
      let html = `<b>ad − bc = ${D}.</b> Площадь новой клетки = |ad − bc|·Im τ = ${(Math.abs(D) * st.im).toFixed(2)}; у исходной ${st.im.toFixed(2)}. `;
      if (D === 1 && tp) {
        html += `<span class="c-cyan">Хорошая замена:</span> те же точки, та же площадь. τ′ = (aτ+b)/(cτ+d) = <b>${fmtC(tp[0], tp[1])}</b>; ` +
          `проверка Im τ′ = Im τ / |cτ+d|² = ${(st.im / den).toFixed(3)} (вычислено: ${tp[1].toFixed(3)}).`;
      } else if (D === 0) {
        html += `<span style="color:${COL.red}">Векторы лежат на одной прямой: клетка вырождена.</span>`;
      } else if (Math.abs(D) > 1) {
        html += `<span style="color:${COL.red}">Плохая замена:</span> в клетке ${Math.abs(D)} точки решётки вместо одной. Красные кольца — точки, до которых эти два вектора не дотянутся.`;
      } else { // D === -1
        html += `<span style="color:${COL.red}">Точки те же, но ориентация обращена:</span> Im τ′ = ${tp ? tp[1].toFixed(3) : "—"} < 0. Нужен знак: определитель должен быть +1.`;
      }
      info.innerHTML = html;
    }
    const w = N.register({root, canvases: [plane, hp], draw, tick});
    root.__nh = {st, setM};
  };

  /* =================== nh-ms-symmetry =================== */
  N.builders["nh-ms-symmetry"] = function (root) {
    const types = {
      generic: {label: "Общая", tau: [0.2, 1.3], name: "τ = 0.2 + 1.3i"},
      rect: {label: "Прямоугольная", tau: [0, 1.4], name: "τ = 1.4i"},
      rhomb: {label: "Ромбическая", tau: [Math.cos(70 * PI / 180), Math.sin(70 * PI / 180)], name: "|τ| = 1, arg τ = 70°"},
      square: {label: "Квадратная", tau: [0, 1], name: "τ = i"},
      hex: {label: "Шестиугольная", tau: [-0.5, Math.sqrt(3) / 2], name: "τ = e^{2πi/3}"}
    };
    const st = {type: types[root.dataset.type] ? root.dataset.type : "generic", theta: num(root.dataset.theta, 0),
                mirror: root.dataset.mirror === "1", play: false};
    const canvas = el("canvas", {class: "nh-ms-canvas nh-ms-sq", role: "img",
      "aria-label": "Решётка и её образ при повороте"});
    const side = el("div", {class: "nh-ms-side"});
    const thS = slider("угол θ, °", 0, 360, 0.5, st.theta, v => { st.theta = v; w.dirty = true; }, 1);
    const typeBtns = Object.entries(types).map(([k, t]) => button(t.label, () => { st.type = k; w.dirty = true; }));
    const playBtn = button("▶ Крутить", () => { st.play = !st.play; playBtn.textContent = st.play ? "❚❚ Стоп" : "▶ Крутить"; });
    const setTheta = v => { st.theta = v; thS.set(v); w.dirty = true; };
    const presetAngles = [60, 90, 120, 180].map(v => button(v + "°", () => setTheta(v)));
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, typeBtns),
      el("div", {class: "nh-interactive-controls"}, [thS.wrap, ...presetAngles, playBtn,
        toggle("сначала зеркало z → z̄", st.mirror, v => { st.mirror = v; w.dirty = true; })]),
      el("div", {class: "nh-t3d-grid nh-ms-grid-sym"}, [canvas, side]));
    root.setAttribute("data-prevent-swipe", "");

    const tauOf = () => types[st.type].tau;
    function inLattice(v, tol = 3e-3) {
      const [tr, ti] = tauOf();
      const n = v[1] / ti, m = v[0] - n * tr;
      return Math.abs(n - Math.round(n)) < tol && Math.abs(m - Math.round(m)) < tol;
    }
    function apply(p, theta, mirror) {
      const q = mirror ? [p[0], -p[1]] : p, c = Math.cos(theta * PI / 180), s = Math.sin(theta * PI / 180);
      return [c * q[0] - s * q[1], s * q[0] + c * q[1]];
    }
    function symmetries(mirror) {
      const [tr, ti] = tauOf(), out = [];
      for (let th = 0; th < 360; th++) {
        const a = apply([1, 0], th, mirror), b = apply([tr, ti], th, mirror);
        if (inLattice(a, 1e-6) && inLattice(b, 1e-6)) out.push(th);
      }
      return out;
    }
    function tick() {
      if (!st.play) return false;
      st.theta = (st.theta + 0.5) % 360; thS.set(st.theta);
      return true;
    }
    function draw() {
      const g = ctxOf(canvas), W = canvas._w, H = canvas._h;
      const u = H / 6.4, cx = W / 2, cy = H / 2;
      const X = x => cx + u * x, Y = y => cy - u * y;
      g.fillStyle = COL.bg; g.fillRect(0, 0, W, H);
      const [tr, ti] = tauOf();
      const P = (m, n) => [m + n * tr, n * ti];
      let allOk = true, any = false;
      for (let m = -14; m <= 14; m++) for (let n = -14; n <= 14; n++) {
        const p = P(m, n), q = apply(p, st.theta, st.mirror);
        const qx = X(q[0]), qy = Y(q[1]);
        if (qx > -10 && qy > -10 && qx < W + 10 && qy < H + 10) {
          any = true;
          if (inLattice(q)) dot(g, qx, qy, 8, "rgba(139,224,164,0.9)", null);
          else { dot(g, qx, qy, 6.5, null, COL.amber, 2); allOk = false; }
        }
      }
      for (let m = -14; m <= 14; m++) for (let n = -14; n <= 14; n++) {
        const p = P(m, n), x = X(p[0]), y = Y(p[1]);
        if (x > -10 && y > -10 && x < W + 10 && y < H + 10) dot(g, x, y, 3.6, "rgba(233,241,244,0.9)");
      }
      // basis and its image
      const b1 = [1, 0], b2 = [tr, ti];
      arrow(g, X(0), Y(0), X(b1[0]), Y(b1[1]), COL.cyan, 3.4, 13);
      arrow(g, X(0), Y(0), X(b2[0]), Y(b2[1]), COL.amber, 3.4, 13);
      const i1 = apply(b1, st.theta, st.mirror), i2 = apply(b2, st.theta, st.mirror);
      g.setLineDash([7, 6]);
      arrow(g, X(0), Y(0), X(i1[0]), Y(i1[1]), "rgba(133,212,232,0.8)", 2.4, 11);
      arrow(g, X(0), Y(0), X(i2[0]), Y(i2[1]), "rgba(255,204,138,0.8)", 2.4, 11);
      g.setLineDash([]);
      const ok = inLattice(i1) && inLattice(i2);
      // side panel
      const rots = symmetries(false), mirrors = symmetries(true);
      const t = types[st.type];
      side.innerHTML =
        `<p><b>${t.label} решётка</b><br><span class="nh-ms-muted">${t.name}</span></p>` +
        `<p class="${ok ? "nh-ms-ok" : "nh-ms-no"}">${st.mirror ? "Зеркало, затем поворот" : "Поворот"} на ${st.theta.toFixed(1)}°: ` +
        `${ok ? "решётка <b>совпала сама с собой</b>" : "решётка <b>не</b> совпала с собой"}.</p>` +
        `<p>Повороты, совмещающие решётку с собой: <b>${rots.map(v => v + "°").join(", ")}</b> (${rots.length}).</p>` +
        `<p>Зеркальных осей: <b>${mirrors.length}</b>.</p>` +
        `<p class="nh-ms-muted">Белые точки — решётка, зелёные — её образ, если он попал в узел; жёлтые кольца — не попал.</p>`;
    }
    const w = N.register({root, canvases: [canvas], draw, tick});
    root.__nh = {st, types};
  };
})();
