// Small helpers shared by the engine, the places and the forces.
export function rng(seed) {
  return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
export const hash = (i, k = 0) => rng(i * 7919 + k * 104729 + 13)();
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
export const lerp = (a, b, t) => a + (b - a) * t;
export const noise = (t, s) => Math.sin(t * 1.31 + s * 7.1) * .5 + Math.sin(t * 2.97 + s * 3.3) * .3 + Math.sin(t * 6.1 + s * 1.7) * .2;

// monotone cubic interpolation through [[x, y], ...] (no overshoot)
export function monotone(pts) {
  if (pts.length === 1) return () => pts[0][1];
  const n = pts.length, xs = pts.map(p => p[0]), ys = pts.map(p => p[1]), d = [], m = [];
  for (let i = 0; i < n - 1; i++) d.push((ys[i + 1] - ys[i]) / Math.max(1e-6, xs[i + 1] - xs[i]));
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

// piecewise colour keys: [[t, 0xtop, 0xhorizon], ...] -> (t, j) => THREE.Color
export function colorKeys(THREE, keys) {
  const K = keys.map(([t, ...cs]) => [t, ...cs.map(c => new THREE.Color(c))]);
  return (t, j) => {
    let i = 0; while (i < K.length - 2 && t > K[i + 1][0]) i++;
    if (K.length === 1) return K[0][j].clone();
    const a = K[i], b = K[i + 1]; return a[j].clone().lerp(b[j], smooth(a[0], b[0], t));
  };
}
