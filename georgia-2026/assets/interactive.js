(function () {
  "use strict";

  function initializePmns() {
    const root = document.getElementById("nh-pmns-fit");
    if (!root) return;
    const math = window.NHInteractiveMath;
    const cells = [...root.querySelectorAll("[data-cell]")];
    const previous = root.querySelector('[data-action="previous"]');
    const next = root.querySelector('[data-action="next"]');
    const cellTeX = {
      e1: String.raw`\frac23`, e2: String.raw`\frac13`, e3: "0",
      mu1: String.raw`\frac16`, mu2: String.raw`\frac13`, mu3: String.raw`\frac12`,
      tau1: String.raw`\frac16`, tau2: String.raw`\frac13`, tau3: String.raw`\frac12`
    };
    const stages = [
      {
        heading: "Start with two different bases",
        explanation: "Weak interactions identify flavor. Propagation identifies mass. The nine squared moduli connect the two.",
        cells: []
      },
      {
        heading: "A solar clue",
        explanation: String.raw`For high-energy solar neutrinos, the adiabatic matter effect suggests \(|U_{e2}|^2\simeq\frac13\) in this simplified construction.`,
        cells: ["e2"]
      },
      {
        heading: "Normalize the electron row",
        explanation: String.raw`Set \(|U_{e3}|^2=0\) as a first approximation. The row sum \(\sum_i|U_{ei}|^2=1\) then gives \(|U_{e1}|^2=\frac23\).`,
        cells: ["e1", "e2", "e3"]
      },
      {
        heading: "Use atmospheric disappearance",
        explanation: String.raw`Near-maximal atmospheric mixing gives \(|U_{\mu3}|^2\simeq\frac12\). Column normalization with \(|U_{e3}|^2=0\) gives \(|U_{\tau3}|^2\simeq\frac12\).`,
        cells: ["e1", "e2", "e3", "mu3", "tau3"]
      },
      {
        heading: "A unitary starting point",
        explanation: String.raw`Normalization and orthogonality complete this real example. Reactor data give \(|U_{e3}|^2\simeq0.022\), so the full three-flavor fit needs a nonzero third entry and a possible complex phase.`,
        cells: Object.keys(cellTeX)
      }
    ];
    let step = 0;
    function draw() {
      const stage = stages[step];
      root.querySelector("[data-heading]").textContent = stage.heading;
      math.setHTML(root.querySelector("[data-explanation]"), stage.explanation);
      root.querySelector("[data-step]").textContent = `Step ${step} of ${stages.length - 1}`;
      cells.forEach(cell => {
        const known = stage.cells.includes(cell.dataset.cell);
        if (known) math.setMath(cell, cellTeX[cell.dataset.cell]);
        else {
          cell.textContent = "?";
          delete cell.dataset.mathTex;
        }
        cell.dataset.known = String(known);
      });
      const example = root.querySelector("[data-unitarity-example]");
      if (step === stages.length - 1) {
        math.setHTML(example, String.raw`With one consistent real sign choice: \(\frac23+\frac13+0=1,\quad 0+\frac12+\frac12=1,\quad\sum_i U_{\mu i}U_{\tau i}^{*}=-\frac16-\frac13+\frac12=0.\)`);
      } else {
        example.textContent = "";
        delete example.dataset.mathHtml;
      }
      previous.disabled = step === 0;
      next.disabled = step === stages.length - 1;
    }
    previous.addEventListener("click", () => { step = Math.max(0, step - 1); draw(); });
    next.addEventListener("click", () => { step = Math.min(stages.length - 1, step + 1); draw(); });
    draw();
  }

  function initializeKatrin() {
    const root = document.getElementById("nh-katrin-spectrum");
    if (!root) return;
    const math = window.NHInteractiveMath;
    const canvas = root.querySelector("canvas");
    const ctx = canvas.getContext("2d");
    const windowSlider = root.querySelector('[data-control="window"]');
    const massSlider = root.querySelector('[data-control="mass"]');
    const left = 86, right = 1080, top = 35, bottom = 370;
    const xMin = -12, xMax = 1;
    const xPixel = x => left + (x - xMin) / (xMax - xMin) * (right - left);
    const yPixel = y => bottom - y * (bottom - top);
    const shape = (x, mass) => {
      const energy = -x;
      return energy > mass ? energy * Math.sqrt(energy * energy - mass * mass) / 144 : 0;
    };
    function plotLine(fn, color, width) {
      ctx.beginPath();
      for (let i = 0; i <= 600; i++) {
        const x = xMin + (xMax - xMin) * i / 600;
        const y = fn(x);
        if (i === 0) ctx.moveTo(xPixel(x), yPixel(y));
        else ctx.lineTo(xPixel(x), yPixel(y));
      }
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.stroke();
    }
    function draw() {
      const window = Number(windowSlider.value);
      const mass = Number(massSlider.value);
      const threshold = -window;
      const transmission = x => Math.max(0, Math.min(1, (x - threshold) / 0.95));
      const accepted = x => shape(x, mass) * transmission(x);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#08121d";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = "#4b6678";
      ctx.lineWidth = 1;
      ctx.font = "22px system-ui, sans-serif";
      ctx.fillStyle = "#e5edf2";
      for (const tick of [-12, -9, -6, -3, 0]) {
        const x = xPixel(tick);
        ctx.beginPath(); ctx.moveTo(x, top); ctx.lineTo(x, bottom); ctx.stroke();
        ctx.fillText(String(tick), x - 13, bottom + 34);
      }
      for (const tick of [0, 0.25, 0.5, 0.75, 1]) {
        const y = yPixel(tick);
        ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(right, y); ctx.stroke();
        ctx.fillText(tick.toFixed(2), 15, y + 7);
      }
      ctx.beginPath();
      ctx.moveTo(xPixel(xMin), yPixel(0));
      for (let i = 0; i <= 600; i++) {
        const x = xMin + (xMax - xMin) * i / 600;
        ctx.lineTo(xPixel(x), yPixel(accepted(x)));
      }
      ctx.lineTo(xPixel(xMax), yPixel(0));
      ctx.closePath();
      ctx.fillStyle = "rgba(255, 179, 71, 0.34)";
      ctx.fill();
      plotLine(x => shape(x, 0), "#7cc7ff", 4);
      plotLine(x => shape(x, mass), "#d7a7ff", 4);
      plotLine(accepted, "#ffb347", 4);
      ctx.beginPath();
      ctx.setLineDash([9, 7]);
      ctx.moveTo(xPixel(threshold), top);
      ctx.lineTo(xPixel(threshold), bottom);
      ctx.strokeStyle = "#ffb347";
      ctx.lineWidth = 3;
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = "#e5edf2";
      ctx.font = "24px system-ui, sans-serif";
      ctx.fillText("Electron energy relative to endpoint (eV)", 235, 425);
      ctx.fillStyle = "#7cc7ff"; ctx.fillText("zero mass", 760, 75);
      ctx.fillStyle = "#d7a7ff"; ctx.fillText("selected mass", 760, 108);
      ctx.fillStyle = "#ffb347"; ctx.fillText("transmitted", 760, 141);
      let integral = 0;
      for (let i = 1; i <= 600; i++) {
        const x0 = xMin + (xMax - xMin) * (i - 1) / 600;
        const x1 = xMin + (xMax - xMin) * i / 600;
        integral += (accepted(x0) + accepted(x1)) * (x1 - x0) / 2;
      }
      math.setMath(root.querySelector('[data-value="window"]'), String.raw`${window}\,\mathrm{eV}`);
      math.setMath(root.querySelector('[data-value="mass"]'), String.raw`${mass.toFixed(1)}\,\mathrm{eV}`);
      math.setHTML(root.querySelector("[data-summary]"), String.raw`Transmitted area: \(A_{\rm tr}=${integral.toFixed(3)}\), proportional to the relative count rate.`);
    }
    windowSlider.addEventListener("input", draw);
    massSlider.addEventListener("input", draw);
    draw();
  }

  function initializeModular() {
    const root = document.getElementById("nh-modular-fit");
    if (!root) return;
    const math = window.NHInteractiveMath;
    const canvas = root.querySelector("canvas");
    const ctx = canvas.getContext("2d");
    const reSlider = root.querySelector('[data-control="tau-re"]');
    const imSlider = root.querySelector('[data-control="tau-im"]');
    const target21 = 7.388e-5, sigma21 = 0.078e-5;
    const target31 = 2.509e-3, sigma31 = 0.026e-3;
    const coefficients1 = [1, 24, 24, 96, 24, 144, 96];
    const coefficients2 = [1, 4, 6, 8, 13, 12, 14];
    const add = (a, b) => [a[0] + b[0], a[1] + b[1]];
    const multiply = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
    const scale = (a, s) => [a[0] * s, a[1] * s];
    const magnitude = a => Math.hypot(a[0], a[1]);

    function evaluate(re, im) {
      if (re * re + im * im < 1) return null;
      const qAbsolute = Math.exp(-2 * Math.PI * im);
      const phase = 2 * Math.PI * re;
      const q = [qAbsolute * Math.cos(phase), qAbsolute * Math.sin(phase)];
      const qHalf = [Math.sqrt(qAbsolute) * Math.cos(phase / 2), Math.sqrt(qAbsolute) * Math.sin(phase / 2)];
      let qPower = [1, 0], y1 = [0, 0], y2Series = [0, 0];
      for (let n = 0; n < coefficients1.length; n++) {
        y1 = add(y1, scale(qPower, coefficients1[n]));
        y2Series = add(y2Series, scale(qPower, coefficients2[n]));
        qPower = multiply(qPower, q);
      }
      const y2 = scale(multiply(qHalf, y2Series), 8 * Math.sqrt(3));
      const factors = [
        1 / (2 * magnitude(y1)),
        1 / magnitude(add(y1, scale(y2, -Math.sqrt(3)))),
        1 / magnitude(add(y1, scale(y2, Math.sqrt(3))))
      ].sort((a, b) => a - b);
      const a21 = factors[1] ** 2 - factors[0] ** 2;
      const a31 = factors[2] ** 2 - factors[0] ** 2;
      const w21 = 1 / sigma21 ** 2, w31 = 1 / sigma31 ** 2;
      const scaleSquared = (a21 * target21 * w21 + a31 * target31 * w31) /
        (a21 * a21 * w21 + a31 * a31 * w31);
      const massScale = Math.sqrt(scaleSquared);
      const d21 = scaleSquared * a21, d31 = scaleSquared * a31;
      const chi2 = ((d21 - target21) / sigma21) ** 2 + ((d31 - target31) / sigma31) ** 2;
      return {masses: factors.map(value => value * massScale), d21, d31, chi2};
    }

    const plot = {left: 60, right: 590, top: 22, bottom: 305};
    const xPixel = re => plot.left + (re + 0.5) * (plot.right - plot.left);
    const yPixel = im => plot.bottom - (im - 0.87) / (1.6 - 0.87) * (plot.bottom - plot.top);
    function draw() {
      const re = Number(reSlider.value), im = Number(imSlider.value);
      const result = evaluate(re, im);
      const cellsX = 100, cellsY = 72;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#08121d";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      for (let ix = 0; ix < cellsX; ix++) {
        const x = -0.5 + (ix + 0.5) / cellsX;
        for (let iy = 0; iy < cellsY; iy++) {
          const y = 0.87 + (iy + 0.5) * (1.6 - 0.87) / cellsY;
          const value = evaluate(x, y);
          if (!value) continue;
          const intensity = Math.exp(-Math.min(value.chi2, 50) / 9);
          ctx.fillStyle = `rgba(35, ${Math.round(80 + 150 * intensity)}, ${Math.round(110 + 125 * intensity)}, 0.9)`;
          ctx.fillRect(xPixel(x - 0.5 / cellsX), yPixel(y + (1.6 - 0.87) / (2 * cellsY)),
            (plot.right - plot.left) / cellsX + 1, (plot.bottom - plot.top) / cellsY + 1);
        }
      }
      ctx.strokeStyle = "#8aa2b2";
      ctx.lineWidth = 2;
      ctx.strokeRect(plot.left, plot.top, plot.right - plot.left, plot.bottom - plot.top);
      ctx.font = "18px system-ui, sans-serif";
      ctx.fillStyle = "#e5edf2";
      for (const x of [-0.5, 0, 0.5]) ctx.fillText(x.toFixed(1), xPixel(x) - 18, 335);
      for (const y of [0.9, 1.2, 1.5]) ctx.fillText(y.toFixed(1), 10, yPixel(y) + 6);
      ctx.fillText("real part", 290, 348);
      ctx.fillText("imaginary part", 8, 18);
      function dot(x, y, color, radius) {
        ctx.beginPath(); ctx.arc(xPixel(x), yPixel(y), radius, 0, 2 * Math.PI);
        ctx.fillStyle = color; ctx.fill();
        ctx.strokeStyle = "#061016"; ctx.lineWidth = 2; ctx.stroke();
      }
      dot(-0.19205, 1.08536, "#ffcc8a", 7);
      dot(re, im, "#ffffff", 6);
      root.querySelector('[data-value="tau-re"]').textContent = re.toFixed(3);
      root.querySelector('[data-value="tau-im"]').textContent = im.toFixed(3);
      math.setHTML(root.querySelector("[data-tau]"), String.raw`\(\tau=${re.toFixed(3)}+${im.toFixed(3)}i\); gold dot = published point.`);
      if (result) {
        const masses = result.masses.map(m => (1000 * m).toFixed(1)).join(String.raw`,\,`);
        math.setMath(root.querySelector("[data-masses]"), String.raw`(m_1,m_2,m_3)=(${masses})\,\mathrm{meV}`);
        math.setMath(root.querySelector("[data-splittings]"), String.raw`\Delta m^2_{21}=${(1e5 * result.d21).toFixed(3)}\times10^{-5}\,\mathrm{eV}^2,\quad\Delta m^2_{31}=${(1e3 * result.d31).toFixed(3)}\times10^{-3}\,\mathrm{eV}^2`);
        math.setHTML(root.querySelector("[data-chi2]"), String.raw`Profiled mass scale: \(\chi^2=${result.chi2.toFixed(2)}\) for the two JUNO inputs.`);
      } else {
        delete root.querySelector("[data-masses]").dataset.mathTex;
        math.setHTML(root.querySelector("[data-masses]"), String.raw`Choose \(\tau\) within the modular fundamental domain.`);
        root.querySelector("[data-splittings]").textContent = "";
        root.querySelector("[data-chi2]").textContent = "";
        delete root.querySelector("[data-splittings]").dataset.mathTex;
        delete root.querySelector("[data-chi2]").dataset.mathHtml;
      }
    }
    reSlider.addEventListener("input", () => {
      const re = Number(reSlider.value);
      const floor = Math.sqrt(1 - re * re);
      if (Number(imSlider.value) < floor) imSlider.value = floor.toFixed(3);
      draw();
    });
    imSlider.addEventListener("input", () => {
      const re = Number(reSlider.value);
      const floor = Math.sqrt(1 - re * re);
      if (Number(imSlider.value) < floor) imSlider.value = floor.toFixed(3);
      draw();
    });
    root.querySelector('[data-action="benchmark"]').addEventListener("click", () => {
      reSlider.value = "-0.192"; imSlider.value = "1.086"; draw();
    });
    root.querySelector('[data-action="fit"]').addEventListener("click", () => {
      let best = {chi2: Infinity, re: -0.192, im: 1.086};
      for (let ix = 0; ix <= 160; ix++) {
        const re = -0.5 + ix / 160;
        for (let iy = 0; iy <= 120; iy++) {
          const im = 0.87 + iy * (1.6 - 0.87) / 120;
          const value = evaluate(re, im);
          if (value && value.chi2 < best.chi2) best = {chi2: value.chi2, re, im};
        }
      }
      reSlider.value = best.re.toFixed(3);
      imSlider.value = best.im.toFixed(3);
      draw();
    });
    draw();
  }

  function initialize() {
    initializePmns();
    initializeKatrin();
    initializeModular();
  }
  let initialized = false;
  function initializeOnce() {
    if (initialized) return;
    initialized = true;
    initialize();
  }
  if (window.Reveal && typeof Reveal.on === "function") {
    Reveal.on("ready", initializeOnce);
    if (Reveal.isReady()) initializeOnce();
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeOnce, {once: true});
  } else initializeOnce();
})();
