(function () {
  "use strict";

  let initialized = false;
  function initialize() {
  if (initialized) return;
  initialized = true;

  const root = document.getElementById("nh-flavor-model");
  const data = window.NH_FLAVOR_MODEL_DATA;
  if (!root || !data) return;
  const math = window.NHInteractiveMath;
  const reInput = root.querySelector('[data-control="re"]');
  const imInput = root.querySelector('[data-control="im"]');
  const plotHost = root.querySelector("[data-plots]");
  const names = data.names;
  const reAxis = data.re_axis;
  const imAxis = data.im_axis;
  const center = data.center;
  const specs = [
    {key: "sin2_theta12_pmns", name: "sin²θ₁₂ · PMNS", tex: String.raw`\sin^2\theta_{12}\;\mathrm{PMNS}`, digits: 4, color: "#85d4e8", target: 0.3036},
    {key: "sin2_theta13_pmns", name: "sin²θ₁₃ · PMNS", tex: String.raw`\sin^2\theta_{13}\;\mathrm{PMNS}`, digits: 5, color: "#85d4e8"},
    {key: "sin2_theta23_pmns", name: "sin²θ₂₃ · PMNS", tex: String.raw`\sin^2\theta_{23}\;\mathrm{PMNS}`, digits: 4, color: "#85d4e8"},
    {key: "delta_cp_pmns_deg", name: "δCP · PMNS (°)", tex: String.raw`\delta_{\rm CP}\;\mathrm{PMNS}\ ({}^\circ)`, digits: 1, color: "#85d4e8"},
    {key: "theta12_ckm", name: "θ₁₂ · CKM (rad)", tex: String.raw`\theta_{12}\;\mathrm{CKM}\ (\mathrm{rad})`, digits: 4, color: "#d7a7ff"},
    {key: "delta_cp_ckm_deg", name: "δCP · CKM (°)", tex: String.raw`\delta_{\rm CP}\;\mathrm{CKM}\ ({}^\circ)`, digits: 1, color: "#d7a7ff"},
    {key: "m3_mev", name: "m₃ (meV)", tex: String.raw`m_3\ (\mathrm{meV})`, digits: 2, color: "#ffcc8a"},
    {key: "md_over_ms", name: "m_d / m_s", tex: String.raw`m_d/m_s`, digits: 5, color: "#ffcc8a"},
    {key: "dm21_over_dm31", name: "Δm²₂₁ / Δm²₃₁", tex: String.raw`\Delta m^2_{21}/\Delta m^2_{31}`, digits: 5, color: "#ffcc8a", target: 7.388e-5 / 2.509e-3}
  ];

  function bounds(axis, value) {
    const step = axis[1] - axis[0];
    const position = Math.max(0, Math.min(axis.length - 1, (value - axis[0]) / step));
    const lo = Math.floor(position);
    return [lo, Math.min(lo + 1, axis.length - 1), position - lo];
  }
  function sample(re, im, index) {
    const [x0, x1, fx] = bounds(reAxis, re);
    const [y0, y1, fy] = bounds(imAxis, im);
    const v00 = data.grid[y0][x0][index], v10 = data.grid[y0][x1][index];
    const v01 = data.grid[y1][x0][index], v11 = data.grid[y1][x1][index];
    return (1 - fy) * ((1 - fx) * v00 + fx * v10)
      + fy * ((1 - fx) * v01 + fx * v11);
  }
  const ranges = specs.map(spec => {
    const index = names.indexOf(spec.key);
    let min = Infinity, max = -Infinity;
    for (const row of data.grid) {
      for (const point of row) {
        min = Math.min(min, point[index]);
        max = Math.max(max, point[index]);
      }
    }
    if (spec.target !== undefined) {
      min = Math.min(min, spec.target);
      max = Math.max(max, spec.target);
    }
    const pad = Math.max((max - min) * 0.07, 1e-8);
    return [min - pad, max + pad];
  });
  const cards = specs.map(spec => {
    const card = document.createElement("div");
    card.className = "nh-response-card";
    const name = document.createElement("span");
    math.setMath(name, spec.tex);
    const value = document.createElement("strong");
    const canvas = document.createElement("canvas");
    canvas.width = 360; canvas.height = 86;
    canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", `Exact 2O-model response for ${spec.name}`);
    card.append(name, value, canvas);
    plotHost.append(card);
    return {spec, value, canvas};
  });

  function drawPlot(card, re, im, range) {
    const {spec, canvas} = card;
    const ctx = canvas.getContext("2d");
    const index = names.indexOf(spec.key);
    const left = 15, right = canvas.width - 15, top = 11, bottom = canvas.height - 13;
    const xPixel = x => left + (x - reAxis[0]) / (reAxis.at(-1) - reAxis[0]) * (right - left);
    const yPixel = y => bottom - (y - range[0]) / (range[1] - range[0]) * (bottom - top);
    ctx.fillStyle = "#071824";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.setLineDash([6, 6]);
    if (spec.target !== undefined) {
      const targetY = yPixel(spec.target);
      ctx.beginPath(); ctx.moveTo(left, targetY); ctx.lineTo(right, targetY);
      ctx.strokeStyle = "#ffcc8a"; ctx.lineWidth = 2; ctx.stroke();
    }
    const fittedValue = sample(center[0], center[1], index);
    ctx.beginPath(); ctx.moveTo(left, yPixel(fittedValue)); ctx.lineTo(right, yPixel(fittedValue));
    ctx.strokeStyle = "#566d7c"; ctx.lineWidth = 1.3; ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath();
    for (let n = 0; n < reAxis.length; n++) {
      const x = xPixel(reAxis[n]);
      const y = yPixel(sample(reAxis[n], im, index));
      if (!n) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = spec.color; ctx.lineWidth = 3; ctx.stroke();
    const current = sample(re, im, index);
    ctx.beginPath(); ctx.arc(xPixel(re), yPixel(current), 6, 0, 2 * Math.PI);
    ctx.fillStyle = "#ffffff"; ctx.fill();
    ctx.strokeStyle = spec.color; ctx.lineWidth = 2; ctx.stroke();
    card.value.textContent = current.toFixed(spec.digits);
  }

  function draw() {
    const re = Number(reInput.value), im = Number(imInput.value);
    root.querySelector('[data-value="re"]').textContent = re.toFixed(5);
    root.querySelector('[data-value="im"]').textContent = im.toFixed(5);
    math.setMath(root.querySelector('[data-tau]'), String.raw`\tau=${re.toFixed(5)}+${im.toFixed(5)}i`);
    const chi2 = sample(re, im, names.indexOf("chi2"));
    math.setHTML(root.querySelector('[data-chi2]'), String.raw`\(\chi^2\approx${chi2.toFixed(2)}\) (other fitted parameters held fixed)`);
    cards.forEach((card, i) => drawPlot(card, re, im, ranges[i]));
  }

  reInput.min = reAxis[0]; reInput.max = reAxis.at(-1);
  imInput.min = imAxis[0]; imInput.max = imAxis.at(-1);
  reInput.step = reAxis[1] - reAxis[0];
  imInput.step = imAxis[1] - imAxis[0];
  reInput.value = center[0]; imInput.value = center[1];
  reInput.addEventListener("input", draw);
  imInput.addEventListener("input", draw);
  root.querySelector('[data-action="reset"]').addEventListener("click", () => {
    reInput.value = center[0]; imInput.value = center[1]; draw();
  });
  draw();
  }

  if (window.Reveal && typeof Reveal.on === "function") {
    Reveal.on("ready", initialize);
    if (Reveal.isReady()) initialize();
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, {once: true});
  } else initialize();
})();
