/* Two widgets for the flavor slides of georgia-2026:
 *   #nh-mass-map   neutrino masses as functions of tau alone (2O model, Ding et al. 2023)
 *   #nh-scorecard  pulls of every fitted quantity for the published point and for our refit
 * Numbers for the scorecard come from window.NH_FLAVOR_MODEL_DATA, written by
 * assets/flavor_fit_2o.py. The q-series below is the same one used in that script
 * (weight-2 doublet of 2O, truncated after q^6; |q| is about 0.001 near the fit).
 */
(function () {
  "use strict";

  const CYAN = "#85d4e8", AMBER = "#ffcc8a", PALE = "#e9f1f4", PURPLE = "#d7a7ff", BG = "#08121d";
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const fmt = (x, d = 2) => (x < 0 ? "−" : "") + Math.abs(x).toFixed(d);

  function fit(canvas) {
    const reveal = window.Reveal && typeof Reveal.getScale === "function" ? Reveal.getScale() : 1;
    const scale = Math.max(1, reveal) * Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(2, Math.round(canvas.clientWidth * scale));
    const h = Math.max(2, Math.round(canvas.clientHeight * scale));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; return true; }
    return false;
  }
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

  /* ---------- modular forms and neutrino masses ---------- */
  const C1 = [1, 24, 24, 96, 24, 144, 96];
  const C2 = [1, 4, 6, 8, 13, 12, 14];
  function forms(re, im) {
    const qa = Math.exp(-2 * Math.PI * im), ph = 2 * Math.PI * re;
    const q = [qa * Math.cos(ph), qa * Math.sin(ph)];
    const qh = [Math.sqrt(qa) * Math.cos(ph / 2), Math.sqrt(qa) * Math.sin(ph / 2)];
    let p = [1, 0], y1 = [0, 0], s2 = [0, 0];
    for (let n = 0; n < C1.length; n++) {
      y1 = [y1[0] + C1[n] * p[0], y1[1] + C1[n] * p[1]];
      s2 = [s2[0] + C2[n] * p[0], s2[1] + C2[n] * p[1]];
      p = [p[0] * q[0] - p[1] * q[1], p[0] * q[1] + p[1] * q[0]];
    }
    const y2 = [8 * Math.sqrt(3) * (qh[0] * s2[0] - qh[1] * s2[1]), 8 * Math.sqrt(3) * (qh[0] * s2[1] + qh[1] * s2[0])];
    return {y1, y2};
  }
  const target = {ratio: 7.388e-5 / 2.509e-3, sigma: 0.000436, d21: 7.388e-5};
  function neutrinos(re, im) {
    const {y1, y2} = forms(re, im);
    const abs = z => Math.hypot(z[0], z[1]);
    const s3 = Math.sqrt(3);
    const f = [1 / (2 * abs(y1)),
               1 / abs([y1[0] - s3 * y2[0], y1[1] - s3 * y2[1]]),
               1 / abs([y1[0] + s3 * y2[0], y1[1] + s3 * y2[1]])].sort((a, b) => a - b);
    const a21 = f[1] * f[1] - f[0] * f[0], a31 = f[2] * f[2] - f[0] * f[0];
    const ratio = a21 / a31;
    const scale = Math.sqrt(target.d21 / a21);        // overall scale fixed by the solar splitting
    return {f, ratio, pull: (ratio - target.ratio) / target.sigma,
            masses: f.map(v => v * scale * 1000), d31: scale * scale * a31,
            y1: abs(y1), y2: abs(y2)};
  }

  /* ================= mass map ================= */
  function buildMassMap(root) {
    const math = window.NHInteractiveMath;
    const data = window.NH_FLAVOR_MODEL_DATA;
    const published = data ? [data.reference.params.tau_re, data.reference.params.tau_im] : [-0.19991, 1.07381];
    const refit = data ? [data.fit.params.tau_re, data.fit.params.tau_im] : [-0.19787, 1.07743];
    const state = {re: published[0], im: published[1]};
    const canvas = el("canvas", {class: "nh-fw-map", role: "img", "aria-label": "Map of the predicted ratio of neutrino mass splittings in the tau plane"});
    const panel = el("div", {class: "nh-fw-readout"});
    const caption = el("div", {class: "nh-t3d-cap"});
    math.setHTML(caption, String.raw`<b>Where is JUNO's number?</b> Colour: the predicted ratio \(\Delta m^2_{21}/\Delta m^2_{31}\). Amber line: the measured value. Drag the point.`);
    root.replaceChildren(
      el("div", {class: "nh-fw-mapgrid"}, [
        el("div", {}, [canvas, caption]),
        panel]));
    root.setAttribute("data-prevent-swipe", "");
    const win = {x0: -0.5, x1: 0.5, y0: 0.85, y1: 1.6};
    const margin = {l: 62, r: 14, t: 30, b: 50};
    let dirty = true, cache = null, cacheKey = "";
    function geom() {
      const u = canvas.width / 700;
      return {u, l: margin.l * u, r: canvas.width - margin.r * u, t: margin.t * u, b: canvas.height - margin.b * u};
    }
    const X = (g, x) => g.l + (x - win.x0) / (win.x1 - win.x0) * (g.r - g.l);
    const Y = (g, y) => g.b - (y - win.y0) / (win.y1 - win.y0) * (g.b - g.t);
    const ramp = t => {
      t = clamp(t, 0, 1);
      const stops = [[0, [12, 32, 52]], [0.5, [34, 96, 128]], [1, [176, 220, 230]]];
      const i = t < 0.5 ? 0 : 1, a0 = stops[i], a1 = stops[i + 1], f = (t - a0[0]) / (a1[0] - a0[0]);
      return a0[1].map((v, k) => v + (a1[1][k] - v) * f);
    };
    const LOGMIN = -2.6, LOGMAX = 0;
    function buildMap(g) {
      const key = `${canvas.width}x${canvas.height}`;
      if (cache && cacheKey === key) return cache;
      const w = Math.round(g.r - g.l), h = Math.round(g.b - g.t);
      const off = document.createElement("canvas"); off.width = w; off.height = h;
      const octx = off.getContext("2d"), img = octx.createImageData(w, h);
      const at = (i, j) => [win.x0 + (i + 0.5) / w * (win.x1 - win.x0), win.y1 - (j + 0.5) / h * (win.y1 - win.y0)];
      const lr = new Float32Array(w * h);
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
        const [re, im] = at(i, j), k = 4 * (j * w + i);
        if (re * re + im * im < 1) { img.data[k] = 10; img.data[k + 1] = 18; img.data[k + 2] = 28; img.data[k + 3] = 255; lr[j * w + i] = NaN; continue; }
        const r = neutrinos(re, im).ratio;
        lr[j * w + i] = Math.log10(Math.max(r, 1e-6));
        const col = ramp((lr[j * w + i] - LOGMIN) / (LOGMAX - LOGMIN));
        img.data[k] = col[0]; img.data[k + 1] = col[1]; img.data[k + 2] = col[2]; img.data[k + 3] = 255;
      }
      octx.putImageData(img, 0, 0);
      // contour at the measured ratio (marching squares on the pixel grid)
      const lt = Math.log10(target.ratio);
      octx.strokeStyle = AMBER; octx.lineWidth = Math.max(3, w / 220); octx.lineCap = "round";
      octx.shadowColor = "rgba(255,204,138,0.7)"; octx.shadowBlur = 8;
      octx.beginPath();
      const step = 2;
      for (let j = 0; j + step < h; j += step) for (let i = 0; i + step < w; i += step) {
        const v = [lr[j * w + i], lr[j * w + i + step], lr[(j + step) * w + i + step], lr[(j + step) * w + i]];
        if (v.some(Number.isNaN)) continue;
        const pts = [], corners = [[i, j], [i + step, j], [i + step, j + step], [i, j + step]];
        for (let e = 0; e < 4; e++) {
          const a0 = v[e] - lt, a1 = v[(e + 1) % 4] - lt;
          if ((a0 < 0) !== (a1 < 0)) {
            const f = a0 / (a0 - a1), p0 = corners[e], p1 = corners[(e + 1) % 4];
            pts.push([p0[0] + f * (p1[0] - p0[0]), p0[1] + f * (p1[1] - p0[1])]);
          }
        }
        if (pts.length >= 2) { octx.moveTo(pts[0][0], pts[0][1]); octx.lineTo(pts[1][0], pts[1][1]); }
        if (pts.length === 4) { octx.moveTo(pts[2][0], pts[2][1]); octx.lineTo(pts[3][0], pts[3][1]); }
      }
      octx.stroke();
      cache = off; cacheKey = key;
      return off;
    }
    function draw() {
      fit(canvas);
      const ctx = canvas.getContext("2d"), g = geom(), u = g.u;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(buildMap(g), g.l, g.t);
      ctx.strokeStyle = "#8aa2b2"; ctx.lineWidth = 1.6 * u; ctx.strokeRect(g.l, g.t, g.r - g.l, g.b - g.t);
      // fundamental-domain floor: the arc |tau| = 1
      ctx.beginPath();
      for (let i = 0; i <= 80; i++) {
        const re = win.x0 + (win.x1 - win.x0) * i / 80, im = Math.sqrt(1 - re * re);
        i ? ctx.lineTo(X(g, re), Y(g, im)) : ctx.moveTo(X(g, re), Y(g, im));
      }
      ctx.strokeStyle = "rgba(233,241,244,0.75)"; ctx.setLineDash([6 * u, 5 * u]); ctx.lineWidth = 1.6 * u; ctx.stroke(); ctx.setLineDash([]);
      ctx.font = `${17 * u}px system-ui, sans-serif`; ctx.fillStyle = "#c3d2dc"; ctx.textAlign = "center";
      for (const x of [-0.5, -0.25, 0, 0.25, 0.5]) ctx.fillText(fmt(x, x % 0.5 === 0 ? 1 : 2), X(g, x), g.b + 24 * u);
      ctx.fillText("real part", (g.l + g.r) / 2, g.b + 46 * u);
      ctx.textAlign = "right";
      for (const y of [0.9, 1.0, 1.2, 1.4, 1.6]) ctx.fillText(y.toFixed(1), g.l - 8 * u, Y(g, y) + 6 * u);
      ctx.textAlign = "left"; ctx.fillText("imaginary part", 4 * u, Y(g, 1.5) + 6 * u);
      ctx.fillStyle = "rgba(233,241,244,0.75)"; ctx.textAlign = "left"; ctx.fillText("unit circle", X(g, 0.06), Y(g, 0.9));
      // colour bar for the predicted ratio
      const bx = g.r - 150 * u, by = g.t + 14 * u, bw = 130 * u, bh = 12 * u;
      const grad = ctx.createLinearGradient(bx, 0, bx + bw, 0);
      for (let k = 0; k <= 8; k++) { const c = ramp(k / 8); grad.addColorStop(k / 8, `rgb(${c[0]|0},${c[1]|0},${c[2]|0})`); }
      ctx.fillStyle = grad; ctx.fillRect(bx, by, bw, bh);
      ctx.strokeStyle = "#8aa2b2"; ctx.lineWidth = u; ctx.strokeRect(bx, by, bw, bh);
      ctx.fillStyle = "#e5edf2"; ctx.font = `${14 * u}px system-ui, sans-serif`; ctx.textAlign = "center";
      for (const v of [0.01, 0.1, 1]) ctx.fillText(String(v), bx + (Math.log10(v) - LOGMIN) / (LOGMAX - LOGMIN) * bw, by + bh + 16 * u);
      ctx.textAlign = "right"; ctx.fillText("ratio", bx - 8 * u, by + bh - 1 * u);
      const mark = (pt, color, label, dx, dy, ring) => {
        ctx.beginPath(); ctx.arc(X(g, pt[0]), Y(g, pt[1]), 7 * u, 0, 2 * Math.PI);
        if (ring) { ctx.strokeStyle = color; ctx.lineWidth = 2.6 * u; ctx.stroke(); } else { ctx.fillStyle = color; ctx.fill(); ctx.strokeStyle = "#061016"; ctx.lineWidth = 2 * u; ctx.stroke(); }
        ctx.fillStyle = color; ctx.font = `bold ${17 * u}px system-ui, sans-serif`; ctx.textAlign = "left";
        ctx.fillText(label, X(g, pt[0]) + dx * u, Y(g, pt[1]) + dy * u);
      };
      // the published point and our refit sit on top of each other (differences in tau of order 0.002)
      ctx.beginPath(); ctx.arc(X(g, published[0]), Y(g, published[1]), 13 * u, 0, 2 * Math.PI); ctx.strokeStyle = PALE; ctx.lineWidth = 2.6 * u; ctx.stroke();
      ctx.font = `bold ${17 * u}px system-ui, sans-serif`; ctx.textAlign = "right";
      ctx.lineJoin = "round"; ctx.lineWidth = 5 * u; ctx.strokeStyle = "#061016";
      ctx.strokeText("published ≈ our refit", X(g, published[0]) - 20 * u, Y(g, published[1]) - 14 * u);
      ctx.fillStyle = "#fff"; ctx.fillText("published ≈ our refit", X(g, published[0]) - 20 * u, Y(g, published[1]) - 14 * u);
      ctx.beginPath(); ctx.arc(X(g, state.re), Y(g, state.im), 8 * u, 0, 2 * Math.PI); ctx.fillStyle = "#fff"; ctx.fill(); ctx.strokeStyle = "#061016"; ctx.lineWidth = 2.5 * u; ctx.stroke();
      dirty = false;
    }
    function readout() {
      const res = neutrinos(state.re, state.im);
      const [m1, m2, m3] = res.masses;
      const bar = (m, color) => `<span class="nh-fw-bar"><i style="width:${clamp(m / 60 * 100, 0, 100)}%;background:${color}"></i></span>`;
      math.setHTML(panel, String.raw`
        <div class="nh-fw-tau">\(\tau=${fmt(state.re, 3)}+${state.im.toFixed(3)}i\)</div>
        <div class="nh-fw-row"><span>\(|Y_1|,\ |Y_2|\)</span><b>\(${res.y1.toFixed(3)},\ ${res.y2.toFixed(3)}\)</b></div>
        <div class="nh-fw-row"><span>\(\Delta m^2_{21}/\Delta m^2_{31}\)</span><b>\(${res.ratio.toFixed(5)}\)</b></div>
        <div class="nh-fw-row"><span>measured</span><b class="c-amber">\(${target.ratio.toFixed(5)}\pm${target.sigma.toFixed(5)}\)</b></div>
        <div class="nh-fw-row"><span>pull</span><b class="${Math.abs(res.pull) <= 1 ? "c-amber" : ""}">\(${Math.abs(res.pull) > 50 ? ">50" : fmt(res.pull, 1)}\,\sigma\)</b></div>
        <div class="nh-fw-masses">
          <div><span>\(m_1\)</span>${bar(m1, CYAN)}<b>\(${m1.toFixed(1)}\,\mathrm{meV}\)</b></div>
          <div><span>\(m_2\)</span>${bar(m2, CYAN)}<b>\(${m2.toFixed(1)}\,\mathrm{meV}\)</b></div>
          <div><span>\(m_3\)</span>${bar(m3, CYAN)}<b>\(${m3.toFixed(1)}\,\mathrm{meV}\)</b></div>
        </div>
        <div class="nh-fw-note">The overall scale is set by \(\Delta m^2_{21}=7.388\times10^{-5}\,\mathrm{eV}^2\). Nothing else is adjusted.</div>`);
    }
    function move(e) {
      const r = canvas.getBoundingClientRect(), g = geom();
      const px = (e.clientX - r.left) * canvas.width / r.width, py = (e.clientY - r.top) * canvas.height / r.height;
      let re = win.x0 + (px - g.l) / (g.r - g.l) * (win.x1 - win.x0);
      let im = win.y0 + (g.b - py) / (g.b - g.t) * (win.y1 - win.y0);
      re = clamp(re, -0.5, 0.5);
      im = clamp(im, Math.sqrt(Math.max(0, 1 - re * re)) + 0.001, 1.6);
      state.re = re; state.im = im; dirty = true; readout();
    }
    let drag = false;
    canvas.style.touchAction = "none";
    canvas.addEventListener("pointerdown", e => { drag = true; canvas.setPointerCapture(e.pointerId); move(e); });
    canvas.addEventListener("pointermove", e => { if (drag) move(e); });
    canvas.addEventListener("pointerup", () => { drag = false; });
    canvas.addEventListener("pointercancel", () => { drag = false; });
    readout();
    (function frame() {
      requestAnimationFrame(frame);
      if (!visible(root)) return;
      if (fit(canvas)) { dirty = true; cache = null; }
      if (dirty) draw();
    })();
    root.__nh = {state, neutrinos};
  }

  /* ================= scorecard ================= */
  const ROWS = [
    ["sin2_theta12_pmns", String.raw`\sin^2\theta_{12}`, "lepton"], ["sin2_theta13_pmns", String.raw`\sin^2\theta_{13}`, "lepton"],
    ["sin2_theta23_pmns", String.raw`\sin^2\theta_{23}`, "lepton"], ["delta_cp_pmns_deg", String.raw`\delta_{\rm CP}`, "lepton"],
    ["me_over_mmu", String.raw`m_e/m_\mu`, "lepton"], ["mmu_over_mtau", String.raw`m_\mu/m_\tau`, "lepton"],
    ["dm21_over_dm31", String.raw`\Delta m^2_{21}/\Delta m^2_{31}`, "lepton"],
    ["theta12_ckm", String.raw`\theta_{12}`, "quark"], ["theta13_ckm", String.raw`\theta_{13}`, "quark"], ["theta23_ckm", String.raw`\theta_{23}`, "quark"],
    ["delta_cp_ckm_deg", String.raw`\delta_{\rm CP}`, "quark"], ["mu_over_mc", String.raw`m_u/m_c`, "quark"], ["mc_over_mt", String.raw`m_c/m_t`, "quark"],
    ["md_over_ms", String.raw`m_d/m_s`, "quark"], ["ms_over_mb", String.raw`m_s/m_b`, "quark"]
  ];
  function buildScorecard(root) {
    const math = window.NHInteractiveMath;
    const data = window.NH_FLAVOR_MODEL_DATA;
    if (!data || !data.reference) { root.textContent = "Fit data are not available."; return; }
    const modes = [
      {id: "pub23", label: "Published point · 2023 data", pulls: data.reference["paper-2023"].residuals, chi2: data.reference["paper-2023"].chi2, color: CYAN,
       note: "The point printed in the paper, scored against the inputs the paper used."},
      {id: "pub26", label: "Published point · JUNO draft", pulls: data.reference["juno-aug-2026"].residuals, chi2: data.reference["juno-aug-2026"].chi2, color: PURPLE,
       note: String.raw`The same point after replacing \(\sin^2\theta_{12}\) and \(\Delta m^2_{21}/\Delta m^2_{31}\) by the 31 August 2026 JUNO values.`},
      {id: "refit", label: "Our refit · JUNO draft", pulls: data.fit.residuals, chi2: data.fit.chi2, color: AMBER,
       note: String.raw`All ten shape parameters refitted; the four overall scales follow from \(m_\tau,m_t,m_b\) and \(\Delta m^2_{21}\).`}
    ];
    const dof = data.counts.degrees_of_freedom;
    let mode = 2;
    const current = {}; ROWS.forEach(([k]) => current[k] = modes[mode].pulls[k]);
    const canvas = el("canvas", {class: "nh-fw-score", role: "img", "aria-label": "Pull of each fitted quantity in units of its standard deviation"});
    const labelLayer = el("div", {class: "nh-fw-score-labels", "aria-hidden": "true"});
    const chartWrap = el("div", {class: "nh-fw-score-wrap"}, [canvas, labelLayer]);
    const rowLabels = new Map();
    ROWS.forEach(([key, tex]) => {
      const label = el("span");
      labelLayer.append(label);
      math.setMath(label, tex);
      rowLabels.set(key, label);
    });
    const buttons = modes.map((m, i) => {
      const b = el("button", {type: "button", text: m.label}); b.addEventListener("click", () => { mode = i; update(); }); return b;
    });
    const info = el("p", {class: "nh-t3d-info"});
    root.replaceChildren(el("div", {class: "nh-interactive-controls"}, buttons), chartWrap, info);
    root.setAttribute("data-prevent-swipe", "");
    let dirty = true;
    function update() {
      buttons.forEach((b, i) => b.classList.toggle("nh-active", i === mode));
      const m = modes[mode];
      const worst = ROWS.map(([k, name, grp]) => [Math.abs(m.pulls[k]), name, grp, m.pulls[k]]).sort((a, b) => b[0] - a[0]).slice(0, 3);
      math.setHTML(info, `<b style="color:${m.color}">\\(\\chi^2=${m.chi2.toFixed(1)}\\)</b> for ${dof} degrees of freedom `
        + `(19 measured quantities, 14 parameters). Largest pulls: ${worst.map(w => `\\(${w[1]}: ${fmt(w[3], 1)}\\sigma\\)`).join(", ")}. ${m.note} `
        + String.raw`Pull \(p=(\mathrm{model}-\mathrm{data})/\sigma\).`);
      dirty = true;
    }
    function draw() {
      fit(canvas);
      const ctx = canvas.getContext("2d"), W = canvas.width, H = canvas.height, u = W / 1400;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
      const left = 300 * u, right = W - 60 * u, top = 12 * u, bottom = H - 46 * u;
      const lim = 6.5;
      const X = p => left + (p + lim) / (2 * lim) * (right - left);
      const nRows = ROWS.length + 2;
      const rowH = (bottom - top) / nRows;
      // grid and shaded 1-sigma band
      ctx.fillStyle = "rgba(255, 204, 138, 0.08)"; ctx.fillRect(X(-1), top, X(1) - X(-1), bottom - top);
      ctx.lineWidth = 1.2 * u; ctx.font = `${17 * u}px system-ui, sans-serif`; ctx.textAlign = "center";
      for (const p of [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]) {
        ctx.strokeStyle = p === 0 ? "#b9d7e3" : (Math.abs(p) === 3 || Math.abs(p) === 5) ? "rgba(255,120,120,0.45)" : "rgba(140,170,185,0.22)";
        ctx.beginPath(); ctx.moveTo(X(p), top); ctx.lineTo(X(p), bottom); ctx.stroke();
        ctx.fillStyle = "#c3d2dc"; ctx.fillText((p < 0 ? "−" : "") + Math.abs(p), X(p), bottom + 22 * u);
      }
      ctx.fillStyle = "#c3d2dc"; ctx.fillText("pull in standard deviations", (left + right) / 2, bottom + 42 * u);
      const m = modes[mode];
      let row = 0;
      for (const group of ["lepton", "quark"]) {
        ctx.fillStyle = group === "lepton" ? CYAN : AMBER; ctx.font = `bold ${19 * u}px system-ui, sans-serif`; ctx.textAlign = "left";
        ctx.fillText(group === "lepton" ? "LEPTONS" : "QUARKS", 14 * u, top + (row + 0.7) * rowH);
        row++;
        for (const [key, name, grp] of ROWS) {
          if (grp !== group) continue;
          const y = top + (row + 0.5) * rowH;
          const target = m.pulls[key];
          current[key] += (target - current[key]) * 0.35;
          const v = clamp(current[key], -lim, lim);
          const label = rowLabels.get(key);
          label.style.top = `${y / H * canvas.clientHeight}px`;
          label.style.width = `${(left - 16 * u) / W * canvas.clientWidth}px`;
          const bad = Math.abs(v) > 3;
          ctx.fillStyle = bad ? "#ff8f8f" : m.color; ctx.globalAlpha = 0.9;
          ctx.fillRect(Math.min(X(0), X(v)), y - rowH * 0.3, Math.abs(X(v) - X(0)), rowH * 0.6);
          ctx.globalAlpha = 1;
          if (Math.abs(target) > 1.5) {
            ctx.fillStyle = "#fff"; ctx.font = `bold ${17 * u}px system-ui, sans-serif`;
            ctx.textAlign = v >= 0 ? "left" : "right";
            ctx.fillText(fmt(target, 1), X(v) + (v >= 0 ? 8 : -8) * u, y + 6 * u);
          }
          row++;
        }
      }
      dirty = false;
      for (const [k] of ROWS) if (Math.abs(current[k] - m.pulls[k]) > 0.01) dirty = true;
    }
    update();
    (function frame() {
      requestAnimationFrame(frame);
      if (!visible(root)) return;
      if (fit(canvas)) dirty = true;
      if (dirty) draw();
    })();
    root.__nh = {modes, update};
  }

  function whenData(fn) {
    if (window.NH_FLAVOR_MODEL_DATA) fn();
    else window.addEventListener("load", fn, {once: true});
  }
  onReady(() => whenData(() => {
    const a = document.getElementById("nh-mass-map"); if (a) buildMassMap(a);
    const b = document.getElementById("nh-scorecard"); if (b) buildScorecard(b);
  }));
})();
