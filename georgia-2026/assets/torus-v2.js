(function () {
  "use strict";

  let initialized = false;
  function initialize() {
  if (initialized) return;
  initialized = true;

  const root = document.getElementById("nh-torus");
  if (!root) return;
  const canvas = root.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  const reInput = root.querySelector('[data-control="re"]');
  const imInput = root.querySelector('[data-control="im"]');
  const cyan = "#85d4e8";
  const amber = "#ffcc8a";
  const pale = "#e9f1f4";
  let step = 0;
  let basis = "I";

  const descriptions = [
    "The conventional names a and b denote two independent loops: one trip along period 1 and one along period τ. On this complex plane τ is the point (Re τ, Im τ).",
    "The four points 0, 1, τ and 1+τ enclose one cell. Its copies tile the plane.",
    "Glue the cyan sides by translation by 1. Going once around the cylinder is the a-cycle; its amber rims are still open.",
    "Glue the amber rims by translation by τ. The b-cycle runs around the new central hole: the surface now has no boundary.",
    "Move τ: Re τ shears the cell and Im τ changes its height. The flat torus changes shape, while its topology stays a torus.",
    "T and S choose new integer combinations of the same two periods. They relabel the same lattice and torus."
  ];

  function stroke(x1, y1, x2, y2, color, width = 2, dash = []) {
    ctx.beginPath(); ctx.setLineDash(dash); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
    ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke(); ctx.setLineDash([]);
  }
  function arrow(x1, y1, x2, y2, color, width = 3) {
    stroke(x1, y1, x2, y2, color, width);
    const angle = Math.atan2(y2 - y1, x2 - x1);
    ctx.beginPath(); ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - 12 * Math.cos(angle - 0.42), y2 - 12 * Math.sin(angle - 0.42));
    ctx.lineTo(x2 - 12 * Math.cos(angle + 0.42), y2 - 12 * Math.sin(angle + 0.42));
    ctx.closePath(); ctx.fillStyle = color; ctx.fill();
  }
  function label(text, x, y, color = pale, size = 22, align = "center") {
    ctx.font = `${size}px system-ui, sans-serif`;
    ctx.fillStyle = color; ctx.textAlign = align; ctx.fillText(text, x, y);
  }
  function dot(x, y, color = pale, radius = 5) {
    ctx.beginPath(); ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = color; ctx.fill();
  }
  function cell(p0, p1, p2, p3, ghost = false) {
    ctx.beginPath(); ctx.moveTo(...p0); ctx.lineTo(...p1); ctx.lineTo(...p2);
    ctx.lineTo(...p3); ctx.closePath();
    ctx.fillStyle = ghost ? "rgba(85, 111, 122, 0.09)" : "rgba(101, 180, 197, 0.19)";
    ctx.fill();
    const blue = ghost ? "#47616d" : cyan;
    const orange = ghost ? "#75624c" : amber;
    stroke(...p0, ...p3, blue, ghost ? 2 : 4, ghost ? [6, 7] : []);
    stroke(...p1, ...p2, blue, ghost ? 2 : 4, ghost ? [6, 7] : []);
    stroke(...p0, ...p1, orange, ghost ? 2 : 4, ghost ? [6, 7] : []);
    stroke(...p3, ...p2, orange, ghost ? 2 : 4, ghost ? [6, 7] : []);
  }

  function drawPlane(re, im) {
    const o = [260, 283], e1 = [128, 0], e2 = [128 * re, -128 * im];
    const one = [o[0] + e1[0], o[1] + e1[1]];
    const tau = [o[0] + e2[0], o[1] + e2[1]];
    const oneTau = [one[0] + e2[0], one[1] + e2[1]];

    label("Complex plane", 290, 34, pale, 27);
    arrow(40, o[1], 567, o[1], "#496b79", 2);
    arrow(o[0], 369, o[0], 67, "#496b79", 2);
    stroke(tau[0], tau[1], tau[0], o[1], "#7095a4", 1.5, [5, 5]);
    stroke(tau[0], o[1], o[0], o[1], "#7095a4", 1.5, [5, 5]);
    label("Re z", 536, 311, "#91afbd", 19);
    label("Im z", 302, 79, "#91afbd", 19);

    for (let m = -3; m <= 3; m++) {
      for (let n = -2; n <= 2; n++) {
        const x = o[0] + m * e1[0] + n * e2[0];
        const y = o[1] + m * e1[1] + n * e2[1];
        if (x > 38 && x < 568 && y > 66 && y < 367) dot(x, y, "#587b8b", 3);
      }
    }

    if (step >= 1) {
      if (step === 5 && basis !== "I") cell(o, one, oneTau, tau, true);
      const a = basis === "S" ? e2 : e1;
      const b = basis === "T" ? [e1[0] + e2[0], e1[1] + e2[1]]
        : basis === "S" ? [-e1[0], -e1[1]] : e2;
      const p1 = [o[0] + a[0], o[1] + a[1]];
      const p3 = [o[0] + b[0], o[1] + b[1]];
      const p2 = [p1[0] + b[0], p1[1] + b[1]];
      cell(o, p1, p2, p3);
      label("a", o[0] + a[0] / 2, o[1] + a[1] / 2 + (basis === "S" ? -12 : 24), amber, 19);
      label("b", o[0] + b[0] / 2 + (basis === "S" ? 0 : -15),
        o[1] + b[1] / 2 + (basis === "S" ? -16 : 0), cyan, 19);
    }

    if (step === 0) {
      arrow(...o, ...one, cyan, 4);
      arrow(...o, ...tau, amber, 4);
      label("a: period 1", 337, o[1] - 15, cyan, 19);
      label("b: period τ", tau[0] - 54, tau[1] + 69, amber, 19);
    }
    dot(...o, pale, 5); dot(...one, pale, 5); dot(...tau, pale, 5);
    if (step >= 1) dot(...oneTau, pale, 5);
    label("0", o[0] - 16, o[1] + 27, pale, 22);
    label("1", one[0] + 14, one[1] + 26, pale, 22);
    label("τ", tau[0] - 15, tau[1] - 12, amber, 27);
    if (step >= 1) label("1+τ", oneTau[0] + 26, oneTau[1] - 12, pale, 22);
    if (step === 0) label("τ = Re τ + i Im τ", 285, 393, amber, 23);
    if (step === 1) label("cyan sides  ·  amber sides", 290, 393, pale, 20);
    if (step === 2) label("first: identify cyan sides", 290, 393, cyan, 22);
    if (step === 3) label("then: identify amber rims", 290, 393, amber, 22);
    if (step === 4) label("changing τ changes this cell", 290, 393, pale, 21);
    if (step === 5) label("lattice points stay fixed", 290, 393, pale, 21);
  }

  function drawCylinder() {
    const x = 807, top = 124, width = 205, bottom = 329, center = x + width / 2;
    const fill = ctx.createLinearGradient(x, top, x + width, bottom);
    fill.addColorStop(0, "#5ba8bc"); fill.addColorStop(1, "#173c54");
    ctx.fillStyle = fill; ctx.fillRect(x, top, width, bottom - top);
    ctx.fillStyle = "#08121d";
    ctx.beginPath(); ctx.ellipse(center, top, width / 2, 34, 0, 0, 2 * Math.PI); ctx.fill();
    ctx.beginPath(); ctx.ellipse(center, bottom, width / 2, 34, 0, 0, 2 * Math.PI);
    ctx.fillStyle = "#15354c"; ctx.fill();
    ctx.strokeStyle = amber; ctx.lineWidth = 5; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(center, top, width / 2, 34, 0, 0, 2 * Math.PI);
    ctx.strokeStyle = amber; ctx.stroke();
    stroke(x, top, x, bottom, cyan, 3);
    stroke(x + width, top, x + width, bottom, cyan, 3);
    label("open rim", center + 154, top + 10, amber, 22, "left");
    label("open rim", center + 154, bottom + 9, amber, 22, "left");
    label("cylinder: one pair glued", 900, 388, pale, 23);
  }

  function drawTorus(title) {
    const cx = 910, cy = 208;
    const fill = ctx.createLinearGradient(cx - 190, cy - 120, cx + 160, cy + 125);
    fill.addColorStop(0, "#75cadb"); fill.addColorStop(0.48, "#285f78");
    fill.addColorStop(1, "#102b3e");
    ctx.beginPath();
    ctx.ellipse(cx, cy, 188, 128, 0, 0, 2 * Math.PI);
    ctx.ellipse(cx, cy, 76, 52, 0, 0, 2 * Math.PI, true);
    ctx.fillStyle = fill; ctx.fill("evenodd");
    ctx.strokeStyle = "#a4e1ea"; ctx.lineWidth = 3; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy, 76, 52, 0, 0, 2 * Math.PI);
    ctx.strokeStyle = "#061724"; ctx.lineWidth = 8; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx, cy, 134, 89, 0, Math.PI * 0.12, Math.PI * 0.86);
    ctx.strokeStyle = amber; ctx.lineWidth = 5; ctx.stroke();
    ctx.beginPath(); ctx.ellipse(cx + 125, cy, 30, 81, 0.28, -Math.PI * 0.59, Math.PI * 0.59);
    ctx.strokeStyle = cyan; ctx.lineWidth = 5; ctx.stroke();
    label("a", cx + 173, cy - 9, cyan, 22);
    label("b", cx - 75, cy + 111, amber, 22);
    label(title, cx, 389, pale, 23);
  }

  function draw() {
    const re = Number(reInput.value), im = Number(imInput.value);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#08121d"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawPlane(re, im);
    if (step < 2) {
      label(step === 0 ? "Two periods generate a lattice" : "One cell tiles the plane", 910, 34, pale, 27);
      label(step === 0 ? "Choose 1 and τ" : "Next: identify opposite sides", 910, 210, "#9ab7c4", 30);
    } else if (step === 2) {
      label("Glue the cyan pair", 910, 34, pale, 27); drawCylinder();
    } else {
      label(step === 5 ? "Same lattice, new basis" : "Glue the amber pair", 910, 34, pale, 27);
      drawTorus(step === 5 ? "same torus, new period basis" : "closed surface: a torus");
    }
    let suffix = `  τ = ${re.toFixed(2)} + ${im.toFixed(2)}i`;
    if (step === 5 && basis === "T") suffix += `;  T: τ′ = ${(re + 1).toFixed(2)} + ${im.toFixed(2)}i`;
    if (step === 5 && basis === "S") {
      const denominator = re * re + im * im;
      suffix += `;  S: τ′ = ${(-re / denominator).toFixed(2)} + ${(im / denominator).toFixed(2)}i`;
    }
    root.querySelector('[data-value="re"]').textContent = re.toFixed(2);
    root.querySelector('[data-value="im"]').textContent = im.toFixed(2);
    root.querySelector("[data-step]").textContent = `Step ${step + 1} of 6`;
    root.querySelector("[data-explanation]").textContent = descriptions[step] + suffix;
    root.querySelector('[data-action="back"]').disabled = step === 0;
    root.querySelector('[data-action="next"]').disabled = step === 5;
  }

  root.querySelector('[data-action="back"]').addEventListener("click", () => {
    step = Math.max(0, step - 1); draw();
  });
  root.querySelector('[data-action="next"]').addEventListener("click", () => {
    step = Math.min(5, step + 1); draw();
  });
  for (const input of [reInput, imInput]) {
    input.addEventListener("input", () => { basis = "I"; step = Math.max(step, 4); draw(); });
  }
  for (const mode of ["T", "S"]) {
    root.querySelector(`[data-action="${mode}"]`).addEventListener("click", () => {
      basis = mode; step = 5; draw();
    });
  }
  root.querySelector('[data-action="reset-basis"]').addEventListener("click", () => {
    basis = "I"; draw();
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
