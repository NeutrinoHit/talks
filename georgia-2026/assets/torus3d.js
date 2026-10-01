/* Interactive 3D torus for the modular-symmetry slides (georgia-2026).
 *
 * Geometry. A lattice cell with sides 1 and tau is a point set z = s + t*tau,
 * 0 <= s,t < 1. Gluing opposite sides gives the flat torus C/(Z + Z tau).
 * The doughnut drawn here is a picture of that torus. For Re tau = 0 the
 * picture is conformal: a round torus of revolution with ring-to-tube radius
 * ratio rho = sqrt(1 + (Im tau)^2) carries exactly the conformal class of the
 * rectangle 1 x Im tau, and the tube angle phi(s) below makes little squares
 * of the cell into little squares on the surface. For Re tau != 0 no torus of
 * revolution is conformal to the sheared cell; the round test disc shows the
 * resulting distortion honestly.
 */
(function () {
  "use strict";

  const PI = Math.PI;
  const TWO_PI = 2 * Math.PI;
  const CYAN = "#85d4e8", AMBER = "#ffcc8a", PALE = "#e9f1f4", PURPLE = "#d7a7ff";
  const BG = "#08121d", DIM = "#5f7d8c";

  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const smooth = x => x * x * (3 - 2 * x);
  const fmt = (x, d = 2) => (x < -0.5 * Math.pow(10, -d) ? "−" : "") + Math.abs(x).toFixed(d);
  const fmtTexTau = (re, im, d = 2) => `${re < 0 ? "-" : ""}${Math.abs(re).toFixed(d)}${im < 0 ? "-" : "+"}${Math.abs(im).toFixed(d)}i`;

  /* ---------- modular group helpers ---------- */
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
  function reduceToF(re, im) {
    let M = I2;
    const steps = [];
    for (let k = 0; k < 80; k++) {
      const n = Math.round(re);
      if (n !== 0) {
        const g = [1, -n, 0, 1];
        [re, im] = mobius(g, re, im);
        M = mul2(g, M);
        steps.push(n > 0 ? `T${n > 1 ? "^" + (-n) : "⁻¹"}` : `T${n < -1 ? "^" + (-n) : ""}`);
      }
      if (re * re + im * im < 1 - 1e-12) {
        [re, im] = mobius(MS, re, im);
        M = mul2(MS, M);
        steps.push("S");
      } else break;
    }
    return {re, im, M, steps};
  }

  /* ---------- conformal tube angle ---------- */
  function tubeAngle(s, kappa) {
    // phi(s) = 2 atan2(sin(pi s), kappa cos(pi s)), continuous from 0 to 2 pi
    return 2 * Math.atan2(Math.sin(PI * s), kappa * Math.cos(PI * s));
  }

  /* ---------- texture painters ---------- */
  function arrowHead(ctx, x, y, dx, dy, len, wid) {
    const n = Math.hypot(dx, dy) || 1;
    dx /= n; dy /= n;
    ctx.beginPath();
    ctx.moveTo(x + dx * len, y + dy * len);
    ctx.lineTo(x - dx * len * 0.35 - dy * wid, y - dy * len * 0.35 + dx * wid);
    ctx.lineTo(x - dx * len * 0.35 + dy * wid, y - dy * len * 0.35 - dx * wid);
    ctx.closePath();
    ctx.fill();
  }
  function line(ctx, x1, y1, x2, y2) {
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  }
  function unitSquare(ctx, size) { ctx.setTransform(size, 0, 0, -size, 0, size); }
  function zPlane(ctx, size, re, im) {
    // pixel = M (x, y) with z = x + i y = s + t tau
    ctx.setTransform(size, 0, -size * re / im, -size / im, 0, size);
  }
  function paintBase(ctx, size, checker) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = "#0d2c3e"; ctx.fillRect(0, 0, size, size);
    unitSquare(ctx, size);
    const N = 8;
    if (checker) {
      ctx.fillStyle = "#123a50";
      for (let i = 0; i < N; i++) for (let j = 0; j < N; j++)
        if ((i + j) % 2 === 0) ctx.fillRect(i / N, j / N, 1 / N, 1 / N);
    }
    ctx.strokeStyle = "rgba(170, 214, 230, 0.20)"; ctx.lineWidth = 2 / size;
    for (let k = 0; k <= N; k++) { line(ctx, k / N, 0, k / N, 1); line(ctx, 0, k / N, 1, k / N); }
  }
  function paintCycles(ctx, size, p, q, color, width, glow, arrows) {
    // closed curve of class (p, q): (s, t) = u (p, q) + shift, drawn with wrap-around
    unitSquare(ctx, size);
    const span = Math.max(Math.abs(p), Math.abs(q)) + 2;
    for (let pass = 0; pass < 2; pass++) {
      ctx.strokeStyle = color;
      ctx.globalAlpha = pass === 0 ? 0.28 : 1;
      ctx.lineWidth = (pass === 0 ? glow : width) / size;
      ctx.lineCap = "round";
      for (let i = -span; i <= span; i++) for (let j = -span; j <= span; j++)
        line(ctx, i, j, i + p, j + q);
    }
    ctx.globalAlpha = 1;
    if (arrows) {
      ctx.fillStyle = color;
      for (let i = -span; i <= span; i++) for (let j = -span; j <= span; j++)
        arrowHead(ctx, i + p * 0.5, j + q * 0.5, p, q, 0.05 * 1.2, 0.028);
    }
  }
  function paintCell(ctx, size, tau) {
    paintBase(ctx, size, true);
    const re = tau.re, im = tau.im;
    // round test disc and compass, drawn in the z-plane so they are round there
    const sc = 0.80, tc = 0.74, rd = 0.10;
    const zx = sc + tc * re, zy = tc * im;
    for (let m = -1; m <= 1; m++) for (let n = -1; n <= 1; n++) {
      zPlane(ctx, size, re, im);
      const cx = zx + m + n * re, cy = zy + n * im;
      ctx.beginPath(); ctx.arc(cx, cy, rd, 0, TWO_PI);
      ctx.fillStyle = "rgba(233, 241, 244, 0.13)"; ctx.fill();
      ctx.strokeStyle = PALE; ctx.lineWidth = 0.011; ctx.stroke();
      ctx.lineWidth = 0.007; ctx.lineCap = "round";
      ctx.strokeStyle = PALE;
      line(ctx, cx - rd * 0.9, cy, cx + rd * 0.9, cy);
      ctx.strokeStyle = PURPLE;
      line(ctx, cx, cy - rd * 0.9, cx, cy + rd * 0.9);
    }
    // asymmetric marker "F" fixes the orientation of the cell
    unitSquare(ctx, size);
    const s0 = 0.69, t0 = 0.10, ws = 0.21, wt = 0.38;
    const rect = (x, y, w, h) => ctx.fillRect(s0 + x * ws, t0 + y * wt, w * ws, h * wt);
    ctx.fillStyle = "#ffe3bd";
    rect(0.10, 0.0, 0.24, 1.0); rect(0.10, 0.78, 0.80, 0.22); rect(0.10, 0.42, 0.62, 0.20);
    // the two cycles: a along period 1 (cyan), b along period tau (amber)
    paintCycles(ctx, size, 1, 0, CYAN, 12, 34, true);
    paintCycles(ctx, size, 0, 1, AMBER, 12, 34, true);
  }
  function paintModular(ctx, size, M) {
    paintBase(ctx, size, false);
    // original basis: thin pale cycles
    paintCycles(ctx, size, 1, 0, "rgba(233,241,244,0.95)", 8, 16, false);
    paintCycles(ctx, size, 0, 1, "rgba(233,241,244,0.95)", 8, 16, false);
    // new basis omega1' = c tau + d  ->  (s,t) winding (d, c);  omega2' = a tau + b -> (b, a)
    paintCycles(ctx, size, M[3], M[2], CYAN, 13, 34, true);
    paintCycles(ctx, size, M[1], M[0], AMBER, 13, 34, true);
  }

  /* ---------- WebGL torus ---------- */
  const VERT = `
    attribute vec3 aPos; attribute vec3 aNor; attribute vec2 aUV;
    uniform mat4 uVP;
    varying vec3 vPos; varying vec3 vNor; varying vec2 vUV;
    void main() { vPos = aPos; vNor = aNor; vUV = aUV; gl_Position = uVP * vec4(aPos, 1.0); }`;
  const FRAG = `
    precision mediump float;
    uniform sampler2D uTex; uniform vec3 uEye; uniform vec3 uLight;
    varying vec3 vPos; varying vec3 vNor; varying vec2 vUV;
    void main() {
      vec3 N = normalize(vNor);
      vec3 V = normalize(uEye - vPos);
      float facing = dot(N, V);
      if (facing < 0.0) N = -N;
      vec3 base = texture2D(uTex, vUV).rgb;
      if (facing < 0.0) base *= 0.55;
      vec3 L = normalize(uLight);
      float diff = max(dot(N, L), 0.0);
      float wrap = 0.5 + 0.5 * dot(N, L);
      vec3 H = normalize(L + V);
      float spec = pow(max(dot(N, H), 0.0), 60.0) * 0.32;
      float rim = pow(1.0 - max(dot(N, V), 0.0), 3.0) * 0.28;
      vec3 col = base * (0.30 + 0.50 * diff + 0.28 * wrap) + vec3(spec) + vec3(0.30, 0.55, 0.65) * rim;
      gl_FragColor = vec4(col, 1.0);
    }`;

  function perspective(fovy, aspect, near, far) {
    const f = 1 / Math.tan(fovy / 2), nf = 1 / (near - far);
    return [f / aspect, 0, 0, 0, 0, f, 0, 0, 0, 0, (far + near) * nf, -1, 0, 0, 2 * far * near * nf, 0];
  }
  function lookAt(eye, center, up) {
    let zx = eye[0] - center[0], zy = eye[1] - center[1], zz = eye[2] - center[2];
    let l = Math.hypot(zx, zy, zz); zx /= l; zy /= l; zz /= l;
    let xx = up[1] * zz - up[2] * zy, xy = up[2] * zx - up[0] * zz, xz = up[0] * zy - up[1] * zx;
    l = Math.hypot(xx, xy, xz); xx /= l; xy /= l; xz /= l;
    const yx = zy * xz - zz * xy, yy = zz * xx - zx * xz, yz = zx * xy - zy * xx;
    return {
      m: [xx, yx, zx, 0, xy, yy, zy, 0, xz, yz, zz, 0,
          -(xx * eye[0] + xy * eye[1] + xz * eye[2]),
          -(yx * eye[0] + yy * eye[1] + yz * eye[2]),
          -(zx * eye[0] + zy * eye[1] + zz * eye[2]), 1],
      right: [xx, xy, xz], up: [yx, yy, yz], back: [zx, zy, zz]
    };
  }
  function mat4mul(a, b) {
    const o = new Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++)
      o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
    return o;
  }

  function fitCanvas(canvas) {
    const reveal = window.Reveal && typeof Reveal.getScale === "function" ? Reveal.getScale() : 1;
    const scale = Math.max(1, reveal) * Math.min(2, window.devicePixelRatio || 1);
    const w = Math.max(2, Math.round(canvas.clientWidth * scale));
    const h = Math.max(2, Math.round(canvas.clientHeight * scale));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; return true; }
    return false;
  }

  class TorusView {
    constructor(canvas, options = {}) {
      this.canvas = canvas;
      this.ns = options.ns || 128;
      this.nt = options.nt || 176;
      this.gl = canvas.getContext("webgl", {antialias: true, alpha: false, preserveDrawingBuffer: true})
        || canvas.getContext("experimental-webgl");
      this.ok = !!this.gl;
      this.geometryDirty = true;
      this.textureDirty = true;
      this.camera = {yaw: -0.95, pitch: 0.0, userYaw: 0, userPitch: 0, dist: 11.5};
      this.lastInteraction = -1e9;
      this.dragging = false;
      if (!this.ok) return;
      this.initGL();
      this.initPointer();
    }

    initGL() {
      const gl = this.gl;
      const compile = (type, src) => {
        const sh = gl.createShader(type);
        gl.shaderSource(sh, src); gl.compileShader(sh);
        if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh));
        return sh;
      };
      const prog = gl.createProgram();
      gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT));
      gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG));
      gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
      this.prog = prog;
      this.loc = {
        pos: gl.getAttribLocation(prog, "aPos"), nor: gl.getAttribLocation(prog, "aNor"),
        uv: gl.getAttribLocation(prog, "aUV"), vp: gl.getUniformLocation(prog, "uVP"),
        tex: gl.getUniformLocation(prog, "uTex"), eye: gl.getUniformLocation(prog, "uEye"),
        light: gl.getUniformLocation(prog, "uLight")
      };
      const ns = this.ns, nt = this.nt, nv = (ns + 1) * (nt + 1);
      this.pos = new Float32Array(nv * 3);
      this.nor = new Float32Array(nv * 3);
      const uv = new Float32Array(nv * 2);
      for (let j = 0; j <= nt; j++) for (let i = 0; i <= ns; i++) {
        const k = j * (ns + 1) + i;
        uv[2 * k] = i / ns; uv[2 * k + 1] = j / nt;
      }
      const idx = new Uint32Array(ns * nt * 6);
      let n = 0;
      for (let j = 0; j < nt; j++) for (let i = 0; i < ns; i++) {
        const a = j * (ns + 1) + i, b = a + 1, c = a + ns + 1, d = c + 1;
        idx[n++] = a; idx[n++] = b; idx[n++] = c; idx[n++] = b; idx[n++] = d; idx[n++] = c;
      }
      this.indexCount = idx.length;
      this.uint32 = gl.getExtension("OES_element_index_uint");
      if (!this.uint32) throw new Error("OES_element_index_uint unavailable");
      this.posBuf = gl.createBuffer(); this.norBuf = gl.createBuffer();
      this.uvBuf = gl.createBuffer(); this.idxBuf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, this.uvBuf); gl.bufferData(gl.ARRAY_BUFFER, uv, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.idxBuf); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, idx, gl.STATIC_DRAW);
      this.texture = gl.createTexture();
      this.aniso = gl.getExtension("EXT_texture_filter_anisotropic");
      gl.enable(gl.DEPTH_TEST);
    }

    initPointer() {
      const c = this.canvas;
      let x0 = 0, y0 = 0;
      c.style.touchAction = "none";
      c.addEventListener("pointerdown", e => {
        this.dragging = true; x0 = e.clientX; y0 = e.clientY;
        c.setPointerCapture(e.pointerId); this.touch();
      });
      c.addEventListener("pointermove", e => {
        if (!this.dragging) return;
        const scale = window.Reveal && Reveal.getScale ? Reveal.getScale() : 1;
        this.camera.userYaw -= (e.clientX - x0) / scale * 0.008;
        this.camera.userPitch = clamp(this.camera.userPitch + (e.clientY - y0) / scale * 0.006, -1.2, 1.2);
        x0 = e.clientX; y0 = e.clientY; this.touch();
      });
      const end = () => { this.dragging = false; this.touch(); };
      c.addEventListener("pointerup", end);
      c.addEventListener("pointercancel", end);
      c.addEventListener("dblclick", () => {
        this.camera.userYaw = 0; this.camera.userPitch = 0; this.touch();
      });
    }

    touch() { this.lastInteraction = performance.now(); this.needsDraw = true; }

    setTextureSource(source) {
      this.textureSource = source; this.textureDirty = true; this.needsDraw = true;
    }

    uploadTexture() {
      const gl = this.gl;
      gl.bindTexture(gl.TEXTURE_2D, this.texture);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, this.textureSource);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
      if (this.aniso) {
        const max = gl.getParameter(this.aniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT);
        gl.texParameterf(gl.TEXTURE_2D, this.aniso.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(8, max));
      }
      this.textureDirty = false;
    }

    /* Surface point for cell coordinates (s, t) at fold f in [0, 1]:
       f = 0 flat parallelogram, f = 1/2 closed cylinder, f = 1 round torus. */
    buildGeometry(re, im, fold) {
      const ns = this.ns, nt = this.nt, pos = this.pos;
      const m1 = smooth(clamp(fold / 0.5, 0, 1));
      const m2 = smooth(clamp((fold - 0.5) / 0.5, 0, 1));
      const rho = Math.sqrt(1 + im * im);
      const kappa = Math.sqrt((rho - 1) / (rho + 1));
      const delta = PI / 2;                    // puts the seam (the b-cycle) on the outer equator
      const m2s = Math.max(m2, 1e-5);
      const Rb = im / m2s + (rho - im) * m2 * m2 * m2;
      const phi = new Float64Array(ns + 1);
      for (let i = 0; i <= ns; i++) phi[i] = tubeAngle(i / ns, kappa);
      let sx = 0, sy = 0, sz = 0;
      for (let j = 0; j <= nt; j++) {
        const t = j / nt;
        const ys = TWO_PI * t * im - PI * im;
        for (let i = 0; i <= ns; i++) {
          const s = i / ns;
          const X = TWO_PI * (s + t * re);
          let px, py, pz;
          if (m2 <= 0) {
            const xs = X - PI;
            if (m1 < 1e-4) { px = xs; pz = 0; }
            else { px = Math.sin(m1 * xs) / m1; pz = (Math.cos(m1 * xs) - 1) / m1; }
            py = ys;
          } else {
            const psi = 1.5 * PI + delta * m2 - ((1 - m2) * X + m2 * phi[i]);
            const ur = Math.cos(psi), w = Math.sin(psi);
            const th = m2 * ys / im;
            px = Rb * (Math.cos(th) - 1) + ur * Math.cos(th);
            py = (Rb + ur) * Math.sin(th);
            pz = w;
          }
          const k = 3 * (j * (ns + 1) + i);
          pos[k] = px; pos[k + 1] = py; pos[k + 2] = pz;
          sx += px; sy += py; sz += pz;
        }
      }
      const nv = (ns + 1) * (nt + 1);
      sx /= nv; sy /= nv; sz /= nv;
      if (m2 >= 1) sz = 0;
      let ex = 0, ey = 0, ez = 0;
      for (let k = 0; k < nv; k++) {
        pos[3 * k] -= sx; pos[3 * k + 1] -= sy; pos[3 * k + 2] -= sz;
        ex = Math.max(ex, Math.abs(pos[3 * k])); ey = Math.max(ey, Math.abs(pos[3 * k + 1])); ez = Math.max(ez, Math.abs(pos[3 * k + 2]));
      }
      this.extent = {x: ex, y: ey, z: ez};
      this.computeNormals(m1 >= 0.999, m2 >= 0.999);
      const gl = this.gl;
      gl.bindBuffer(gl.ARRAY_BUFFER, this.posBuf); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.DYNAMIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.norBuf); gl.bufferData(gl.ARRAY_BUFFER, this.nor, gl.DYNAMIC_DRAW);
      this.geometryDirty = false;
    }

    computeNormals(wrapS, wrapT) {
      const ns = this.ns, nt = this.nt, pos = this.pos, nor = this.nor, w = ns + 1;
      const at = (i, j) => 3 * (j * w + i);
      for (let j = 0; j <= nt; j++) for (let i = 0; i <= ns; i++) {
        let i0 = i - 1, i1 = i + 1, j0 = j - 1, j1 = j + 1;
        if (wrapS) { if (i0 < 0) i0 = ns - 1; if (i1 > ns) i1 = 1; } else { i0 = Math.max(i0, 0); i1 = Math.min(i1, ns); }
        if (wrapT) { if (j0 < 0) j0 = nt - 1; if (j1 > nt) j1 = 1; } else { j0 = Math.max(j0, 0); j1 = Math.min(j1, nt); }
        const a = at(i1, j), b = at(i0, j), c = at(i, j1), d = at(i, j0);
        const ux = pos[a] - pos[b], uy = pos[a + 1] - pos[b + 1], uz = pos[a + 2] - pos[b + 2];
        const vx = pos[c] - pos[d], vy = pos[c + 1] - pos[d + 1], vz = pos[c + 2] - pos[d + 2];
        let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
        const l = Math.hypot(nx, ny, nz) || 1;
        const k = at(i, j);
        nor[k] = nx / l; nor[k + 1] = ny / l; nor[k + 2] = nz / l;
      }
    }

    draw(state) {
      if (!this.ok) return;
      const gl = this.gl;
      fitCanvas(this.canvas);
      if (this.textureDirty && this.textureSource) this.uploadTexture();
      if (this.geometryDirty) this.buildGeometry(state.re, state.im, state.fold);
      const cam = this.camera;
      const flat = 1 - smooth(clamp(state.fold / 0.4, 0, 1));
      const pitch = (1.42 - 0.50 * (1 - flat)) + cam.userPitch;   // top-down -> three-quarter view
      const yaw = cam.yaw * (1 - flat) + cam.userYaw;
      const cp = Math.cos(pitch), sp = Math.sin(pitch);
      const ext = this.extent, rxy = Math.max(ext.x, ext.y);
      const aspect0 = this.canvas.width / this.canvas.height;
      const cy = Math.abs(Math.cos(yaw)), sy = Math.abs(Math.sin(yaw));
      const need = Math.max(Math.hypot((cy * ext.y + sy * ext.x) * sp, ext.z * cp), rxy / aspect0) * 1.10 + 0.1;
      const dist = need / Math.tan(0.31) + ext.z;
      const eye = [dist * cp * Math.sin(yaw), -dist * cp * Math.cos(yaw), dist * sp];
      const view = lookAt(eye, [0, 0, 0], [0, 0, 1]);
      const aspect = this.canvas.width / this.canvas.height;
      const vp = mat4mul(perspective(0.62, aspect, 0.5, 80), view.m);
      const light = [0, 1, 2].map(k => 0.55 * view.back[k] + 0.75 * view.up[k] - 0.45 * view.right[k]);
      gl.viewport(0, 0, this.canvas.width, this.canvas.height);
      gl.clearColor(0.031, 0.071, 0.114, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      gl.useProgram(this.prog);
      gl.uniformMatrix4fv(this.loc.vp, false, new Float32Array(vp));
      gl.uniform3fv(this.loc.eye, new Float32Array(eye));
      gl.uniform3fv(this.loc.light, new Float32Array(light));
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.texture);
      gl.uniform1i(this.loc.tex, 0);
      const bind = (buf, loc, size) => {
        gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.enableVertexAttribArray(loc);
        gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
      };
      bind(this.posBuf, this.loc.pos, 3); bind(this.norBuf, this.loc.nor, 3); bind(this.uvBuf, this.loc.uv, 2);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.idxBuf);
      gl.drawElements(gl.TRIANGLES, this.indexCount, gl.UNSIGNED_INT, 0);
      this.needsDraw = false;
    }

    autoRotating(state) {
      return state.fold >= 0.98 && !this.dragging && performance.now() - this.lastInteraction > 2500;
    }
  }

  /* ---------- shared widget plumbing ---------- */
  function el(tag, attrs = {}, children = []) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.className = v;
      else if (k === "text") node.textContent = v;
      else if (k === "html") node.innerHTML = v;
      else node.setAttribute(k, v);
    }
    for (const c of children) node.append(c);
    return node;
  }
  function slider(label, min, max, step, value, onInput) {
    const input = el("input", {type: "range", min, max, step, value});
    const out = el("output");
    const title = el("span");
    window.NHInteractiveMath.setHTML(title, label);
    const wrap = el("label", {}, [title, input, out]);
    input.addEventListener("input", () => onInput(Number(input.value)));
    return {wrap, input, out};
  }
  function button(text, onClick, title) {
    const b = el("button", {type: "button", text});
    if (title) b.title = title;
    b.addEventListener("click", onClick);
    return b;
  }
  function visible(node) { return node.offsetParent !== null; }
  function placeMathLabel(label, canvas, x, y) {
    label.style.left = `${100 * x / canvas.width}%`;
    label.style.top = `${100 * y / canvas.height}%`;
  }
  function onReady(fn) {
    let done = false;
    const once = () => { if (!done) { done = true; fn(); } };
    if (window.Reveal && typeof Reveal.on === "function") {
      Reveal.on("ready", once);
      if (Reveal.isReady && Reveal.isReady()) once();
    } else if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", once, {once: true});
    } else once();
  }

  /* ================= Widget 1: from a cell to a torus ================= */
  function buildFoldWidget(root) {
    const math = window.NHInteractiveMath;
    const state = {re: -0.20, im: 1.07, fold: 0.0};
    let tween = null;
    const texCanvas = document.createElement("canvas");
    texCanvas.width = texCanvas.height = 1024;
    const texCtx = texCanvas.getContext("2d");

    const planeCanvas = el("canvas", {class: "nh-t3d-plane", role: "img",
      "aria-label": "Complex plane with a lattice cell whose sides are 1 and tau"});
    const planeLabels = el("div", {class: "nh-t3d-math-labels", "aria-hidden": "true"});
    const pointLabels = {
      zero: el("span"), one: el("span"), tau: el("span", {class: "c-amber"}), oneTau: el("span")
    };
    for (const label of Object.values(pointLabels)) planeLabels.append(label);
    math.setMath(pointLabels.zero, "0");
    math.setMath(pointLabels.one, "1");
    math.setMath(pointLabels.tau, String.raw`\tau`);
    math.setMath(pointLabels.oneTau, String.raw`1+\tau`);
    const glCanvas = el("canvas", {class: "nh-t3d-gl", role: "img",
      "aria-label": "Three-dimensional view of the cell rolled into a cylinder and closed into a torus"});
    const poster = el("img", {class: "nh-poster", alt: "Torus obtained by gluing the cell", src: root.dataset.poster || ""});
    const capLeft = el("div", {class: "nh-t3d-cap"});
    math.setHTML(capLeft, String.raw`<b>The plane.</b> Points that differ by <span class="c-cyan">\(a=1\)</span> or <span class="c-amber">\(b=\tau\)</span> are the same point of the torus.`);
    const capRight = el("div", {class: "nh-t3d-cap"});
    math.setHTML(capRight, String.raw`<b>The surface.</b> <span class="c-cyan">\(a\)</span> runs around the tube, <span class="c-amber">\(b\)</span> around the ring. Drag to rotate.`);
    const grid = el("div", {class: "nh-t3d-grid"}, [
      el("div", {class: "nh-t3d-pane"}, [planeCanvas, planeLabels, capLeft]),
      el("div", {class: "nh-t3d-pane"}, [glCanvas, poster, capRight])
    ]);

    const foldOut = el("output");
    const foldInput = el("input", {type: "range", min: 0, max: 1, step: 0.005, value: 0});
    const foldLabel = el("label", {}, [document.createTextNode("Glue "), foldInput, foldOut]);
    foldInput.addEventListener("input", () => { tween = null; setFold(Number(foldInput.value)); });
    const play = button("▶ Glue it", () => animateTo(state.fold > 0.5 ? 0 : 1, 4200));
    const stepButtons = [
      button("Cell", () => animateTo(0, 1400)),
      button("Cylinder", () => animateTo(0.5, 1800)),
      button("Torus", () => animateTo(1, 1800))
    ];
    const reS = slider(String.raw`\(\operatorname{Re}\tau\)`, -1, 1, 0.01, state.re, v => { state.re = v; changedTau(); });
    const imS = slider(String.raw`\(\operatorname{Im}\tau\)`, 0.4, 2.2, 0.01, state.im, v => { state.im = v; changedTau(); });
    const presets = [
      button("Square torus", () => setTau(0, 1), "square torus"),
      button("Hexagonal torus", () => setTau(-0.5, Math.sqrt(3) / 2), "hexagonal torus"),
      button("Fitted shape", () => setTau(-0.2, 1.07), "the modulus of the 2O fit shown later")
    ];
    math.setMath(presets[0], String.raw`\tau=i`);
    math.setMath(presets[1], String.raw`\tau=e^{2\pi i/3}`);
    math.setHTML(presets[2], String.raw`Fit: \(\tau\approx-0.20+1.07i\)`);
    const info = el("p", {class: "nh-t3d-info"});
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [foldLabel, play, ...stepButtons]),
      grid,
      el("div", {class: "nh-interactive-controls"}, [reS.wrap, imS.wrap, ...presets]),
      info);
    root.dataset.preventSwipe = "";
    root.setAttribute("data-prevent-swipe", "");

    const view = new TorusView(glCanvas);
    if (!view.ok) { root.classList.add("nh-no-webgl"); }
    view.setTextureSource(texCanvas);

    function repaintTexture() { paintCell(texCtx, 1024, state); view.setTextureSource(texCanvas); }
    function setFold(f) {
      state.fold = clamp(f, 0, 1); foldInput.value = state.fold;
      view.geometryDirty = true; view.needsDraw = true; planeDirty = true; updateInfo();
    }
    function changedTau() {
      repaintTexture(); view.geometryDirty = true; view.needsDraw = true; planeDirty = true; updateInfo();
    }
    function setTau(re, im) {
      state.re = re; state.im = im; reS.input.value = re; imS.input.value = im; changedTau();
    }
    function animateTo(target, ms) {
      tween = {from: state.fold, to: target, t0: performance.now(), ms: ms * Math.max(0.35, Math.abs(target - state.fold))};
    }
    function updateInfo() {
      reS.out.textContent = fmt(state.re); imS.out.textContent = state.im.toFixed(2);
      foldOut.textContent = state.fold < 0.02 ? "cell" : state.fold > 0.98 ? "torus" : state.fold > 0.49 && state.fold < 0.51 ? "cylinder" : `${Math.round(state.fold * 100)}%`;
      play.textContent = state.fold > 0.5 ? "◀ Unglue" : "▶ Glue it";
      let text;
      if (state.fold < 0.02) text = String.raw`Start with one cell: the parallelogram \(0,1,1+\tau,\tau\). Its translated copies tile the whole plane.`;
      else if (state.fold < 0.5) text = String.raw`Roll the cell and glue its left and right sides (translation by \(1\)). The \(a\)-side becomes a circle.`;
      else if (state.fold < 0.98) text = String.raw`Bend the cylinder and glue its two ends (translation by \(\tau\)). The \(b\)-side becomes a loop around the ring.`;
      else text = String.raw`Every point of the plane sits on exactly one point of this surface, and the surface has no boundary. Change \(\tau\) and the torus changes shape.`;
      math.setHTML(info, String.raw`<b>\(\tau=${fmtTexTau(state.re, state.im)}\)</b> &nbsp; ${text}`);
    }

    /* plane drawing */
    let planeDirty = true;
    const win = {cx: 0.6, cy: 1.05, w: 3.6, h: 2.9};
    function planeMap(canvas) {
      const k = Math.min(canvas.width / win.w, canvas.height / win.h);
      return {k, X: x => canvas.width / 2 + k * (x - win.cx), Y: y => canvas.height / 2 - k * (y - win.cy)};
    }
    function drawPlane() {
      fitCanvas(planeCanvas);
      const c = planeCanvas, ctx = c.getContext("2d"), {k, X, Y} = planeMap(c);
      const u = c.width / 660;      // pixel unit relative to the 660-px reference layout
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, c.width, c.height);
      const re = state.re, im = state.im;
      // tiles: the texture in every lattice cell (main cell brightest)
      const S = texCanvas.width;
      for (let m = -3; m <= 3; m++) for (let n = -2; n <= 3; n++) {
        const ox = X(m + n * re), oy = Y(n * im);
        const cornerX = [ox, ox + k, ox + k * re, ox + k * (1 + re)];
        const cornerY = [oy, oy, oy - k * im, oy - k * im];
        if (Math.max(...cornerX) < 0 || Math.min(...cornerX) > c.width || Math.max(...cornerY) < 0 || Math.min(...cornerY) > c.height) continue;
        ctx.globalAlpha = (m === 0 && n === 0) ? 1 : 0.11;
        ctx.setTransform(k / S, 0, -k * re / S, k * im / S, ox + k * re, oy - k * im);
        ctx.drawImage(texCanvas, 0, 0);
      }
      ctx.globalAlpha = 1; ctx.setTransform(1, 0, 0, 1, 0, 0);
      // axes
      ctx.strokeStyle = "rgba(160, 190, 205, 0.55)"; ctx.lineWidth = 1.4 * u;
      line(ctx, X(win.cx - win.w / 2), Y(0), X(win.cx + win.w / 2), Y(0));
      line(ctx, X(0), Y(win.cy - win.h / 2), X(0), Y(win.cy + win.h / 2));
      ctx.font = `${17 * u}px system-ui, sans-serif`; ctx.fillStyle = "#9db8c6"; ctx.textAlign = "left";
      ctx.fillText("real axis", X(win.cx + win.w / 2) - 46 * u, Y(0) + 22 * u);
      ctx.fillText("imaginary axis", X(0) + 8 * u, Y(win.cy + win.h / 2) + 20 * u);
      // lattice points
      for (let m = -3; m <= 4; m++) for (let n = -2; n <= 3; n++) {
        const x = X(m + n * re), y = Y(n * im);
        if (x < 0 || x > c.width || y < 0 || y > c.height) continue;
        ctx.beginPath(); ctx.arc(x, y, 3.6 * u, 0, TWO_PI); ctx.fillStyle = "#b9d7e3"; ctx.fill();
      }
      // main cell outline and vertex labels
      const P = [[0, 0], [1, 0], [1 + re, im], [re, im]];
      ctx.beginPath(); P.forEach(([x, y], i) => i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y))); ctx.closePath();
      ctx.strokeStyle = "rgba(255,255,255,0.9)"; ctx.lineWidth = 1.6 * u; ctx.stroke();
      placeMathLabel(pointLabels.zero, c, X(0) - 15 * u, Y(0) + 26 * u);
      placeMathLabel(pointLabels.one, c, X(1) + 4 * u, Y(0) + 27 * u);
      placeMathLabel(pointLabels.oneTau, c, X(1 + re) + 33 * u, Y(im) - 8 * u);
      placeMathLabel(pointLabels.tau, c, X(re) - 20 * u, Y(im) - 6 * u);
      // draggable handle at tau
      ctx.beginPath(); ctx.arc(X(re), Y(im), 10 * u, 0, TWO_PI);
      ctx.fillStyle = "rgba(255, 204, 138, 0.22)"; ctx.fill();
      ctx.strokeStyle = AMBER; ctx.lineWidth = 2.6 * u; ctx.stroke();
      ctx.beginPath(); ctx.arc(X(re), Y(im), 4.3 * u, 0, TWO_PI); ctx.fillStyle = "#fff"; ctx.fill();
      // side labels
      ctx.font = `bold ${21 * u}px system-ui, sans-serif`;
      ctx.textAlign = "center";
      ctx.fillStyle = CYAN; ctx.fillText("first period", X(0.5), Y(0) + 25 * u);
      ctx.fillStyle = AMBER; ctx.textAlign = "right"; ctx.fillText("second period", X(re / 2) - 12 * u, Y(im / 2) - 6 * u);
      planeDirty = false;
    }
    // dragging the tau handle
    let dragTau = false;
    function pointerToTau(e) {
      const r = planeCanvas.getBoundingClientRect();
      const {k} = planeMap(planeCanvas);
      const scaleX = planeCanvas.width / r.width, scaleY = planeCanvas.height / r.height;
      const px = (e.clientX - r.left) * scaleX, py = (e.clientY - r.top) * scaleY;
      const x = win.cx + (px - planeCanvas.width / 2) / k, y = win.cy - (py - planeCanvas.height / 2) / k;
      return [x, y, px, py];
    }
    planeCanvas.style.touchAction = "none";
    planeCanvas.addEventListener("pointerdown", e => {
      const [x, y] = pointerToTau(e);
      if (Math.hypot(x - state.re, y - state.im) < 0.32) {
        dragTau = true; planeCanvas.setPointerCapture(e.pointerId); planeCanvas.classList.add("nh-grabbing");
      }
    });
    planeCanvas.addEventListener("pointermove", e => {
      if (!dragTau) return;
      const [x, y] = pointerToTau(e);
      setTau(clamp(x, -1, 1), clamp(y, 0.4, 2.2));
    });
    const endDrag = () => { dragTau = false; planeCanvas.classList.remove("nh-grabbing"); };
    planeCanvas.addEventListener("pointerup", endDrag);
    planeCanvas.addEventListener("pointercancel", endDrag);

    repaintTexture(); updateInfo();
    function frame(now) {
      requestAnimationFrame(frame);
      if (!visible(root) || document.hidden) return;
      if (tween) {
        const p = clamp((now - tween.t0) / tween.ms, 0, 1);
        setFold(tween.from + (tween.to - tween.from) * (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2));
        if (p >= 1) tween = null;
      }
      if (view.autoRotating(state)) { view.camera.userYaw += 0.0035; view.needsDraw = true; }
      if (fitCanvas(planeCanvas)) planeDirty = true;
      if (planeDirty) drawPlane();
      if (view.ok && (view.needsDraw || view.canvas.clientWidth * 1 !== view.lastW)) {
        view.lastW = view.canvas.clientWidth; view.draw(state);
      }
    }
    requestAnimationFrame(frame);
    root.__nh = {state, view, setFold, setTau, animateTo};
  }

  /* ================= Widget 2: same torus, many cells ================= */
  function buildModularWidget(root) {
    const math = window.NHInteractiveMath;
    const state = {re: 0.31, im: 1.32, M: I2, fold: 1};
    const texCanvas = document.createElement("canvas");
    texCanvas.width = texCanvas.height = 1024;
    const texCtx = texCanvas.getContext("2d");

    const uhpCanvas = el("canvas", {class: "nh-t3d-uhp", role: "img", "aria-label": "Upper half plane of tau with the modular fundamental domain"});
    const uhpLabels = el("div", {class: "nh-t3d-math-labels", "aria-hidden": "true"});
    const uhpPointLabels = {domain: el("span", {class: "c-amber"}), tau: el("span"), transformed: el("span", {class: "c-cyan"})};
    for (const label of Object.values(uhpPointLabels)) uhpLabels.append(label);
    math.setMath(uhpPointLabels.domain, "F");
    math.setMath(uhpPointLabels.tau, String.raw`\tau`);
    math.setMath(uhpPointLabels.transformed, String.raw`\tau'`);
    const zCanvas = el("canvas", {class: "nh-t3d-zplane", role: "img", "aria-label": "Two different cells of the same lattice"});
    const zLabels = el("div", {class: "nh-t3d-math-labels", "aria-hidden": "true"});
    const periodLabels = {a: el("span"), b: el("span"), aNew: el("span", {class: "c-cyan"}), bNew: el("span", {class: "c-amber"}), zero: el("span")};
    for (const label of Object.values(periodLabels)) zLabels.append(label);
    math.setMath(periodLabels.a, "a");
    math.setMath(periodLabels.b, "b");
    math.setMath(periodLabels.aNew, String.raw`a'`);
    math.setMath(periodLabels.bNew, String.raw`b'`);
    math.setMath(periodLabels.zero, "0");
    const glCanvas = el("canvas", {class: "nh-t3d-gl", role: "img", "aria-label": "One torus with two choices of a and b cycles"});
    const poster = el("img", {class: "nh-poster", alt: "One torus and two bases", src: root.dataset.poster || ""});
    const cap1 = el("div", {class: "nh-t3d-cap"});
    math.setHTML(cap1, String.raw`<b>The \(\tau\)-plane.</b> Every point is a cell shape. Shaded: the fundamental domain <span class="c-amber">\(F\)</span>.`);
    const cap2 = el("div", {class: "nh-t3d-cap", html: `<b>One lattice, two cells.</b> Same points, same area, different periods.`});
    const cap3 = el("div", {class: "nh-t3d-cap"});
    math.setHTML(cap3, String.raw`<b>One torus.</b> White: old \(a,b\). <span class="c-cyan">Cyan</span> and <span class="c-amber">amber</span>: new cycles.`);
    const grid = el("div", {class: "nh-t3d-grid nh-t3d-grid3"}, [
      el("div", {class: "nh-t3d-pane"}, [uhpCanvas, uhpLabels, cap1]),
      el("div", {class: "nh-t3d-pane"}, [zCanvas, zLabels, cap2]),
      el("div", {class: "nh-t3d-pane"}, [glCanvas, poster, cap3])
    ]);
    const hist = [];
    const gBtns = [
      button("T", () => apply(MT), "translate the period basis by one"),
      button("Inverse T", () => apply(MTI), "translate by minus one"),
      button("S", () => apply(MS), "swap the period basis"),
      button("Undo", () => { state.M = hist.length ? hist.pop() : I2; refresh(); }),
      button("Back to the old cell", () => { hist.length = 0; state.M = I2; refresh(); }),
      button("Reduce to domain", () => reduceAnimated())
    ];
    const reS = slider(String.raw`\(\operatorname{Re}\tau\)`, -1.5, 1.5, 0.01, state.re, v => { state.re = v; refresh(); });
    const imS = slider(String.raw`\(\operatorname{Im}\tau\)`, 0.3, 2.3, 0.01, state.im, v => { state.im = v; refresh(); });
    const info = el("p", {class: "nh-t3d-info"});
    const matrixBox = el("span", {class: "nh-t3d-matrix"});
    root.replaceChildren(
      el("div", {class: "nh-interactive-controls"}, [reS.wrap, imS.wrap, el("span", {class: "nh-t3d-sep"}), matrixBox, ...gBtns]),
      grid, info);
    root.setAttribute("data-prevent-swipe", "");

    const view = new TorusView(glCanvas);
    if (!view.ok) root.classList.add("nh-no-webgl");
    view.setTextureSource(texCanvas);
    view.camera.yaw = -0.95;

    function apply(g) { hist.push(state.M); state.M = mul2(g, state.M); refresh(); }
    let reducing = null;
    function reduceAnimated() {
      if (reducing) return;
      const tick = () => {
        const before = state.M;
        reduceStep();
        if (state.M === before) { reducing = null; return; }
        reducing = setTimeout(tick, 850);
      };
      reducing = 1; tick();
    }
    function reduceStep() {
      const [re, im] = mobius(state.M, state.re, state.im);
      const n = Math.round(re);
      let g;
      if (n !== 0) g = [1, -n, 0, 1];
      else if (re * re + im * im < 1 - 1e-12) g = MS;
      else return;
      apply(g);
    }
    function det(M) { return M[0] * M[3] - M[1] * M[2]; }
    function refresh() {
      reS.out.textContent = fmt(state.re); imS.out.textContent = state.im.toFixed(2);
      const [re2, im2] = mobius(state.M, state.re, state.im);
      const M = state.M;
      math.setMath(matrixBox, String.raw`\gamma=\begin{pmatrix}${M[0]}&${M[1]}\\${M[2]}&${M[3]}\end{pmatrix}`);
      const rep = reduceToF(state.re, state.im);
      const inF = Math.abs(re2) <= 0.5 + 1e-9 && re2 * re2 + im2 * im2 >= 1 - 1e-9;
      math.setHTML(info, String.raw`Old cell: \(\tau=${fmtTexTau(state.re, state.im)}\). New cell: <span class="c-cyan">\(\tau'=\frac{a\tau+b}{c\tau+d}=${fmtTexTau(re2, im2)}\)</span>. `
        + (inF ? String.raw`\(\tau'\) lies in <span class="c-amber">\(F\)</span>: the shape is in its standard form.`
               : String.raw`Representative in <span class="c-amber">\(F\)</span>: \(${fmtTexTau(rep.re, rep.im)}\). Same torus.`));
      paintModular(texCtx, 1024, state.M);
      view.setTextureSource(texCanvas);
      // ring/tube proportions follow Im tau of the *old* cell
      view.geometryDirty = true; view.needsDraw = true;
      dirty.uhp = dirty.z = true;
    }
    const dirty = {uhp: true, z: true};

    /* --- upper half plane --- */
    const uwin = {x0: -1.75, x1: 1.75, y0: 0, y1: 3.05};
    function uMap(c) {
      const k = Math.min(c.width / (uwin.x1 - uwin.x0), (c.height - 30 * (c.width / 500)) / (uwin.y1 - uwin.y0));
      const left = (c.width - k * (uwin.x1 - uwin.x0)) / 2;
      return {k, X: x => left + k * (x - uwin.x0), Y: y => c.height - 26 * (c.width / 500) - k * (y - uwin.y0)};
    }
    const tiles = [];
    (function buildTiles() {
      const seen = new Set();
      const queue = [{M: I2, d: 0}];
      const key = M => { const s = (M[0] < 0 || (M[0] === 0 && M[1] < 0)) ? -1 : 1; return M.map(v => s * v).join(","); };
      seen.add(key(I2));
      while (queue.length) {
        const {M, d} = queue.shift();
        tiles.push(M);
        if (d >= 9 || tiles.length > 1400) continue;
        for (const g of [MT, MTI, MS]) {
          const N = mul2(M, g);
          const kk = key(N);
          if (!seen.has(kk)) { seen.add(kk); queue.push({M: N, d: d + 1}); }
        }
      }
    })();
    const Fpoly = (function () {
      const pts = [];
      const H = 4.0;
      for (let i = 0; i <= 12; i++) pts.push([-0.5, Math.sqrt(3) / 2 + (H - Math.sqrt(3) / 2) * i / 12]);
      pts.push([0.5, H]);
      for (let i = 0; i <= 12; i++) pts.push([0.5, H - (H - Math.sqrt(3) / 2) * i / 12]);
      for (let i = 1; i <= 40; i++) { const a = (PI / 3) + (PI / 3) * i / 40; pts.push([Math.cos(a), Math.sin(a)]); }
      return pts;
    })();
    function drawUHP() {
      fitCanvas(uhpCanvas);
      const c = uhpCanvas, ctx = c.getContext("2d"), {k, X, Y} = uMap(c);
      const u = c.width / 500;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, c.width, c.height);
      // tessellation by images of F
      ctx.save();
      ctx.beginPath(); ctx.rect(X(uwin.x0), Y(uwin.y1), X(uwin.x1) - X(uwin.x0), Y(0) - Y(uwin.y1)); ctx.clip();
      const shade = ["rgba(88, 140, 165, 0.13)", "rgba(88, 140, 165, 0.05)"];
      for (const M of tiles) {
        const pts = Fpoly.map(([x, y]) => mobius(M, x, y));
        if (pts.every(([x, y]) => y < 0.006)) continue;
        let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
        for (const [x, y] of pts) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
        if (M !== I2 && k * (x1 - x0) < 6 * u && k * (y1 - y0) < 6 * u) continue;
        ctx.beginPath();
        pts.forEach(([x, y], i) => i ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y)));
        ctx.closePath();
        const isF = M === I2;
        ctx.fillStyle = isF ? "rgba(255, 204, 138, 0.30)" : shade[(Math.abs(M[0] + M[1] + M[2] + M[3])) % 2];
        ctx.fill();
        ctx.strokeStyle = isF ? AMBER : "rgba(150, 190, 208, 0.34)"; ctx.lineWidth = (isF ? 2.6 : 1) * u; ctx.stroke();
      }
      ctx.restore();
      // axes
      ctx.strokeStyle = "rgba(160, 190, 205, 0.6)"; ctx.lineWidth = 1.4 * u;
      line(ctx, X(uwin.x0), Y(0), X(uwin.x1), Y(0));
      line(ctx, X(0), Y(0), X(0), Y(uwin.y1));
      ctx.font = `${15 * u}px system-ui, sans-serif`; ctx.fillStyle = "#9db8c6"; ctx.textAlign = "center";
      for (const x of [-1, -0.5, 0, 0.5, 1]) ctx.fillText(String(x).replace("-", "−"), X(x), Y(0) + 19 * u);
      ctx.textAlign = "left"; ctx.fillText("real part", X(1.32), Y(0) + 19 * u);
      ctx.fillText("imaginary part", X(0) + 8 * u, Y(uwin.y1) + 14 * u);
      placeMathLabel(uhpPointLabels.domain, c, X(0), Y(1.55));
      // orbit points of the current tau under the tessellation group (a few)
      ctx.fillStyle = "rgba(233,241,244,0.55)";
      let drawn = 0;
      for (const M of tiles) {
        if (drawn > 220) break;
        const [x, y] = mobius(M, state.re, state.im);
        if (y < 0.16 || x < uwin.x0 || x > uwin.x1 || y > uwin.y1) continue;
        ctx.beginPath(); ctx.arc(X(x), Y(y), 2.4 * u, 0, TWO_PI); ctx.fill(); drawn++;
      }
      // representative in F
      const rep = reduceToF(state.re, state.im);
      ctx.beginPath(); ctx.arc(X(rep.re), Y(rep.im), 7.5 * u, 0, TWO_PI);
      ctx.strokeStyle = AMBER; ctx.lineWidth = 2.6 * u; ctx.stroke();
      // old tau (draggable)
      ctx.beginPath(); ctx.arc(X(state.re), Y(state.im), 6 * u, 0, TWO_PI); ctx.fillStyle = "#fff"; ctx.fill();
      // new tau'
      const [re2, im2] = mobius(state.M, state.re, state.im);
      if (state.M !== I2 && !(Math.abs(re2 - state.re) < 1e-9 && Math.abs(im2 - state.im) < 1e-9)) {
        ctx.beginPath(); ctx.arc(X(re2), Y(im2), 8 * u, 0, TWO_PI);
        ctx.fillStyle = "rgba(133, 212, 232, 0.35)"; ctx.fill();
        ctx.strokeStyle = CYAN; ctx.lineWidth = 3 * u; ctx.stroke();
        placeMathLabel(uhpPointLabels.transformed, c, X(re2) + 11 * u, Y(im2) - 8 * u);
        uhpPointLabels.transformed.hidden = false;
      } else {
        uhpPointLabels.transformed.hidden = true;
      }
      placeMathLabel(uhpPointLabels.tau, c, X(state.re) + 9 * u, Y(state.im) - 8 * u);
      dirty.uhp = false;
    }
    let dragU = false;
    function uPointer(e) {
      const r = uhpCanvas.getBoundingClientRect();
      const {k, X, Y} = uMap(uhpCanvas);
      const px = (e.clientX - r.left) * uhpCanvas.width / r.width, py = (e.clientY - r.top) * uhpCanvas.height / r.height;
      const left = X(0) - k * (0 - uwin.x0);
      return [uwin.x0 + (px - left) / k, (Y(0) - py) / k];
    }
    uhpCanvas.style.touchAction = "none";
    uhpCanvas.addEventListener("pointerdown", e => { dragU = true; uhpCanvas.setPointerCapture(e.pointerId); moveU(e); });
    uhpCanvas.addEventListener("pointermove", e => { if (dragU) moveU(e); });
    uhpCanvas.addEventListener("pointerup", () => { dragU = false; });
    uhpCanvas.addEventListener("pointercancel", () => { dragU = false; });
    function moveU(e) {
      const [x, y] = uPointer(e);
      state.re = clamp(x, -1.5, 1.5); state.im = clamp(y, 0.3, 2.3);
      reS.input.value = state.re; imS.input.value = state.im; refresh();
    }

    /* --- z plane with two cells --- */
    function drawZ() {
      fitCanvas(zCanvas);
      const c = zCanvas, ctx = c.getContext("2d");
      const u = c.width / 500;
      const pre = state.re, pim = state.im, PM = state.M;
      const v1 = [PM[3] + PM[2] * pre, PM[2] * pim], v2 = [PM[1] + PM[0] * pre, PM[0] * pim];
      const xs = [0, 1, pre, 1 + pre, v1[0], v2[0], v1[0] + v2[0]], ys = [0, 0, pim, pim, v1[1], v2[1], v1[1] + v2[1]];
      const bx0 = Math.min(...xs), bx1 = Math.max(...xs), by0 = Math.min(...ys), by1 = Math.max(...ys);
      const asp = c.width / c.height;
      let ww = Math.max(3.6, (bx1 - bx0) * 1.3), hh = Math.max(3.0, (by1 - by0) * 1.3);
      if (ww / hh < asp) ww = hh * asp; else hh = ww / asp;
      const w = {cx: (bx0 + bx1) / 2, cy: (by0 + by1) / 2, w: ww, h: hh};
      const k = Math.min(c.width / w.w, c.height / w.h);
      const X = x => c.width / 2 + k * (x - w.cx), Y = y => c.height / 2 - k * (y - w.cy);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, c.width, c.height);
      const re = state.re, im = state.im, M = state.M;
      const w1 = [M[3] + M[2] * re, M[2] * im];        // omega1' = c tau + d
      const w2 = [M[1] + M[0] * re, M[0] * im];        // omega2' = a tau + b
      // lattice
      const span = 12;
      ctx.fillStyle = "#b9d7e3";
      for (let m = -span; m <= span; m++) for (let n = -span; n <= span; n++) {
        const x = X(m + n * re), y = Y(n * im);
        if (x < 0 || x > c.width || y < 0 || y > c.height) continue;
        ctx.beginPath(); ctx.arc(x, y, 3.4 * u, 0, TWO_PI); ctx.fill();
      }
      const poly = (a, b, fill, stroke, lw, dash) => {
        ctx.beginPath();
        ctx.moveTo(X(0), Y(0)); ctx.lineTo(X(a[0]), Y(a[1])); ctx.lineTo(X(a[0] + b[0]), Y(a[1] + b[1])); ctx.lineTo(X(b[0]), Y(b[1]));
        ctx.closePath();
        if (fill) { ctx.fillStyle = fill; ctx.fill(); }
        ctx.strokeStyle = stroke; ctx.lineWidth = lw * u; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]);
      };
      const sameBasis = state.M[0] === 1 && state.M[1] === 0 && state.M[2] === 0 && state.M[3] === 1;
      poly([1, 0], [re, im], "rgba(233,241,244,0.10)", "rgba(233,241,244,0.85)", 1.8, [7 * u, 6 * u]);
      if (!sameBasis) poly(w1, w2, "rgba(133,212,232,0.16)", "rgba(255,255,255,0.9)", 2.2);
      const vec = (v, color, label, dx, dy) => {
        ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = 4.2 * u; ctx.lineCap = "round";
        line(ctx, X(0), Y(0), X(v[0]), Y(v[1]));
        const ang = Math.atan2(-(Y(v[1]) - Y(0)), X(v[0]) - X(0));
        arrowHead(ctx, X(v[0]), Y(v[1]), Math.cos(ang), -Math.sin(ang), 15 * u, 8 * u);
        placeMathLabel(label, c, X(v[0] / 2) + dx * u, Y(v[1] / 2) + dy * u);
      };
      vec([1, 0], "rgba(233,241,244,0.9)", periodLabels.a, 0, 24);
      vec([re, im], "rgba(233,241,244,0.9)", periodLabels.b, -18, 0);
      if (!sameBasis) {
        vec(w1, CYAN, periodLabels.aNew, 14, 26);
        vec(w2, AMBER, periodLabels.bNew, -22, -6);
      }
      const matchesOld = v =>
        (Math.hypot(v[0] - 1, v[1]) < 1e-9 || Math.hypot(v[0] - re, v[1] - im) < 1e-9);
      periodLabels.aNew.hidden = sameBasis || matchesOld(w1);
      periodLabels.bNew.hidden = sameBasis || matchesOld(w2);
      ctx.fillStyle = PALE; ctx.beginPath(); ctx.arc(X(0), Y(0), 5.5 * u, 0, TWO_PI); ctx.fill();
      placeMathLabel(periodLabels.zero, c, X(0) - 14 * u, Y(0) + 25 * u);
      dirty.z = false;
    }

    refresh();
    function frame(now) {
      requestAnimationFrame(frame);
      if (!visible(root) || document.hidden) return;
      if (fitCanvas(uhpCanvas)) dirty.uhp = true;
      if (fitCanvas(zCanvas)) dirty.z = true;
      if (dirty.uhp) drawUHP();
      if (dirty.z) drawZ();
      if (view.autoRotating(state)) { view.camera.userYaw += 0.0035; view.needsDraw = true; }
      if (view.ok && (view.needsDraw || view.canvas.clientWidth !== view.lastW)) {
        view.lastW = view.canvas.clientWidth; view.draw(state);
      }
    }
    requestAnimationFrame(frame);
    root.__nh = {state, view, refresh, apply};
  }

  onReady(() => {
    const a = document.getElementById("nh-torus3d");
    if (a) buildFoldWidget(a);
    const b = document.getElementById("nh-modular3d");
    if (b) buildModularWidget(b);
  });
})();
