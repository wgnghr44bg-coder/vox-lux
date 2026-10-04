// Shared basics for 'What if' scenes (same look as earth-stops): math helpers, renderer + sky + lights,
// low-poly materials and facade textures.   import { ... } from '../lib/core.js';
import * as THREE from 'three';

export const W = 720, H = 1280, FPS = 30;
export function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
export const hash = (i, k = 0) => rng(i * 7919 + k * 104729 + 13)();
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const lerp = (a, b, t) => a + (b - a) * t;
export const noise = (t, s) => Math.sin(t * 1.31 + s * 7.1) * .5 + Math.sin(t * 2.97 + s * 3.3) * .3 + Math.sin(t * 6.1 + s * 1.7) * .2;
export const C = hex => new THREE.Color(hex);

// monotone cubic through [[t, v], ...] (counters never overshoot)
export function monotone(pts) {
  const n = pts.length, xs = pts.map(p => p[0]), ys = pts.map(p => p[1]), d = [], m = [];
  for (let i = 0; i < n - 1; i++) d.push((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]));
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) m[i] = d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2;
  for (let i = 0; i < n - 1; i++) {
    if (d[i] === 0) { m[i] = m[i + 1] = 0; continue; }
    const a = m[i] / d[i], b = m[i + 1] / d[i], s = a * a + b * b;
    if (s > 9) { const tau = 3 / Math.sqrt(s); m[i] = tau * a * d[i]; m[i + 1] = tau * b * d[i]; }
  }
  return x => {
    if (x <= xs[0]) return ys[0]; if (x >= xs[n - 1]) return ys[n - 1];
    let i = 0; while (x > xs[i + 1]) i++;
    const h = xs[i + 1] - xs[i], t = (x - xs[i]) / h, t2 = t * t, t3 = t2 * t;
    return (2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h * m[i + 1];
  };
}

// colour keyframes [[t, colA, colB, ...], ...] -> colour j at time t
export function keyframes(K) {
  return (t, j) => { let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++;
    const [a, b] = [K[i], K[i + 1]]; return a[j].clone().lerp(b[j], smooth(a[0], b[0], t)); };
}

// renderer, scene, camera, gradient sky, hemisphere + sun with shadows
export function setup({ fov = 60, fog = [0xcfdce4, 120, 900] } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H); renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
  document.body.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(fov, W / H, 0.3, 4000);
  scene.fog = new THREE.Fog(...fog);
  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() } },
    vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform vec3 top; uniform vec3 hor; varying vec3 vP;
      void main(){ float h = clamp(vP.y*2.0, 0., 1.); gl_FragColor = vec4(mix(hor, top, pow(h, .6)), 1.); }`
  });
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(3000, 32, 16), skyMat));
  const hemi = new THREE.HemisphereLight(0xe3ecf4, 0x5a5448, 1.5);
  const sun = new THREE.DirectionalLight(0xffeedd, 2.4);
  sun.position.set(-90, 110, 120); sun.target.position.set(0, 0, -40);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -80, right: 80, top: 120, bottom: -120, near: 10, far: 500 });
  sun.shadow.bias = -0.0008;
  scene.add(hemi, sun, sun.target);
  return { renderer, scene, camera, skyMat, hemi, sun };
}

export const lam = (color, o = {}) => new THREE.MeshLambertMaterial({ color, flatShading: true, ...o });
export const glow = color => new THREE.MeshBasicMaterial({ color });     // unlit: screens, lamps, lights
export const shadowed = (m, cast = true) => { m.castShadow = cast; m.receiveShadow = true; return m; };

// ---------- facades ----------
export const PALETTE = [0x9c4a3a, 0xc9b896, 0x7a5a44, 0x8e8e8a, 0xc4a85a, 0xb5653f, 0xd2c6ae, 0x6f6a64];
export const TOWER_PAL = [0xb9bcbc, 0xa7a49b, 0xc9c1ae, 0x8f969b, 0xd0cdc4];
export function canvasTex(w, h, draw, repeat = true) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; draw(cv.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; return t;
}
// kind: 'win' | 'shop' | 'tower' | 'broken' | 'glass' (curtain wall) ; one 64px texture = one bay of one floor
export function facadeTex(base, kind) {
  const c = new THREE.Color(base), hex = k => '#' + c.clone().multiplyScalar(k).getHexString();
  return canvasTex(64, 64, x => {
    x.fillStyle = hex(1); x.fillRect(0, 0, 64, 64);
    x.fillStyle = hex(.82); x.fillRect(0, 60, 64, 4);
    if (kind === 'shop') { x.fillStyle = '#2f3a42'; x.fillRect(4, 10, 56, 44); x.fillStyle = '#56656e'; x.fillRect(4, 10, 56, 6); }
    else if (kind === 'tower') { x.fillStyle = '#5b6b78'; for (let i = 0; i < 4; i++) x.fillRect(2 + i * 16, 12, 12, 40); }
    else if (kind === 'glass') { x.fillStyle = '#4e5f6c'; x.fillRect(0, 6, 64, 54); x.fillStyle = '#6b7d89'; x.fillRect(0, 6, 64, 10);
      x.fillStyle = hex(.9); for (let i = 0; i < 4; i++) x.fillRect(i * 16, 6, 2, 54); }
    else {
      const glass = kind === 'broken' ? '#101010' : '#46555f';
      x.fillStyle = hex(1.12); x.fillRect(14, 48, 36, 4);
      x.fillStyle = glass; x.fillRect(16, 14, 32, 34);
      if (kind === 'broken') { x.fillStyle = '#46555f'; x.beginPath(); x.moveTo(16, 14); x.lineTo(30, 14); x.lineTo(16, 30); x.fill();
        x.beginPath(); x.moveTo(48, 48); x.lineTo(48, 34); x.lineTo(38, 48); x.fill(); }
      else { x.fillStyle = '#5d6d77'; x.fillRect(16, 14, 32, 8); x.fillStyle = hex(.9); x.fillRect(31, 14, 2, 34); }
    }
  });
}
const matCache = {};
export function facadeMats(color, kind) {
  const key = color + kind;
  if (!matCache[key]) {
    const side = lam(0xffffff, { map: facadeTex(color, kind) }), top = lam(new THREE.Color(color).multiplyScalar(.75));
    matCache[key] = [side, side, top, top, side, side];
  }
  return matCache[key];
}
// box whose UVs repeat one texture per bay (bay m wide, 3.5 m floors)
export function facadeBox(w, h, d, bay = 5) {
  const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv;
  const rep = [[d / bay, h / 3.5], [d / bay, h / 3.5], [1, 1], [1, 1], [w / bay, h / 3.5], [w / bay, h / 3.5]];
  for (let f = 0; f < 6; f++) for (let i = 0; i < 4; i++) { const k = f * 4 + i; uv.setXY(k, uv.getX(k) * rep[f][0], uv.getY(k) * rep[f][1]); }
  return g;
}

// soft round puff for particle clouds (dust, steam, crowd haze)
export function puffTexture() {
  return canvasTex(128, 128, x => {
    const R = rng(99);
    for (let i = 0; i < 26; i++) {
      const px = 64 + (R() - .5) * 60, py = 64 + (R() - .5) * 60, r = 18 + R() * 26;
      const gr = x.createRadialGradient(px, py - r * 0.3, 0, px, py, r);
      gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.6, 'rgba(235,235,235,0.25)'); gr.addColorStop(1, 'rgba(200,200,200,0)');
      x.fillStyle = gr; x.beginPath(); x.arc(px, py, r, 0, 7); x.fill();
    }
    const fade = x.createRadialGradient(64, 64, 30, 64, 64, 64);
    x.globalCompositeOperation = 'destination-in';
    fade.addColorStop(0, 'rgba(0,0,0,1)'); fade.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = fade; x.fillRect(0, 0, 128, 128);
  }, false);
}
// soft radial glow (light pools, headlight halos); additive sprite material
export function glowSprite(color, size, opacity = 1) {
  const tex = canvasTex(64, 64, x => { const g = x.createRadialGradient(32, 32, 0, 32, 32, 32);
    g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.35, 'rgba(255,255,255,.35)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = g; x.fillRect(0, 0, 64, 64); }, false);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false }));
  s.scale.set(size, size, 1); return s;
}
