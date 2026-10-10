// METEORS AND FIREBALLS (baksteen "Hemel", okt 2026): bright streaks across the night sky, camera-independent
// (they hang on a sphere around the camera, like the Moon), plus slow fireballs with a glowing head and a long
// trail that sink towards the horizon and light up the sky for a moment.
//   TL.meteors = { rate: [[t, per second], ...] streaks, az: [a, b] where they appear (rad, 0 = -z, + = towards +x),
//                  fireballs: [[t, az, el0, seconds, size], ...], flash: 0..1 how much a fireball lights the scene }
// Fireballs also give E.EVENTS { kind: 'fireball' } (sound: whoosh, then a low distant boom in make_audio.py).
import * as THREE from 'three';
import { monotone, hash, smooth, clamp } from './util.js';

export function createMeteors(E, TL) {
  const M = TL.meteors; if (!M) return;
  const STOP = TL.beats.stop, rate = monotone(M.rate || [[0, 0]]), [az0, az1] = M.az || [-1.2, 1.2];
  const dirOf = (az, el) => new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el));
  // pre-made list of streaks (deterministic)
  const list = [];
  let acc = 0;
  for (let t = 0, i = 0; t < TL.T_END; t += 1 / 30, i++) {
    acc += rate(Math.min(t, STOP)) / 30;
    while (acc >= 1 || (acc > 0 && hash(i, 3) < acc * .02)) {
      acc -= 1; const k = list.length;
      const az = az0 + hash(k, 1) * (az1 - az0), el = .12 + hash(k, 2) * .7, len = .05 + hash(k, 4) * .16, ang = -.5 - hash(k, 5) * 2.1 + (hash(k, 6) < .5 ? 0 : Math.PI - 2.6 + 2.1);
      list.push({ t0: t, dur: .35 + hash(k, 7) * .7, az, el, len, ang, w: 3 + hash(k, 8) * 4, b: .6 + hash(k, 9) * .4 });
    }
    if (acc < 0) acc = 0;
  }
  const FB = (M.fireballs || []).map(([t0, az, el, dur = 3, size = 1]) => ({ t0, az, el, dur, size, fb: true }));
  for (const f of FB) E.EVENTS.push({ t: f.t0, kind: 'fireball', e: f.size });
  const MAX = 160, D = 2600;
  const pos = new Float32Array(MAX * 4 * 3), al = new Float32Array(MAX * 4), col = new Float32Array(MAX * 4 * 3), idx = [];
  for (let i = 0; i < MAX; i++) { const a = i * 4; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('alpha', new THREE.BufferAttribute(al, 1)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3)); geo.setIndex(idx);
  const mat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, fog: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
    vertexShader: `attribute float alpha; attribute vec3 color; varying float vA; varying vec3 vC; void main(){ vA = alpha; vC = color; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
    fragmentShader: `varying float vA; varying vec3 vC; void main(){ gl_FragColor = vec4(vC * vA, vA); }` });
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false; mesh.renderOrder = 2;
  mesh.onBeforeRender = (r, s, cam) => { mesh.position.copy(cam.position); mesh.updateMatrixWorld(); };
  E.scene.add(mesh);
  const _a = new THREE.Vector3(), _b = new THREE.Vector3(), _w = new THREE.Vector3();
  let n = 0;
  const quad = (h, tl, wh, wt, ah, at, c) => {           // head, tail (directions), widths, alphas, colour
    if (n >= MAX) return;
    _a.copy(h).multiplyScalar(D); _b.copy(tl).multiplyScalar(D);
    _w.copy(_a).sub(_b).cross(_a).normalize();
    const p = n * 12, q = n * 4;
    pos.set([_a.x + _w.x * wh, _a.y + _w.y * wh, _a.z + _w.z * wh, _a.x - _w.x * wh, _a.y - _w.y * wh, _a.z - _w.z * wh,
             _b.x + _w.x * wt, _b.y + _w.y * wt, _b.z + _w.z * wt, _b.x - _w.x * wt, _b.y - _w.y * wt, _b.z - _w.z * wt], p);
    al.set([ah, ah, at, at], q); col.set([...c, ...c, ...c, ...c], p); n++;
  };
  // a streak: moves along `ang` on the sky from (az, el); u = 0..1 its life
  const pt = (o, s) => dirOf(o.az + Math.cos(o.ang) * s / Math.max(.3, Math.cos(o.el)), o.el + Math.sin(o.ang) * s);
  const flashAt = t => { let f = 0; for (const o of FB) { const u = (Math.min(t, STOP) - o.t0) / o.dur; if (u > 0 && u < 1) f = Math.max(f, smooth(0, .2, u) * (1 - smooth(.85, 1, u)) * o.size); } return f; };
  E.updates.push((t, F, tv) => {
    n = 0;
    const tt = Math.min(tv, STOP);
    for (const o of list) { const u = (tt - o.t0) / o.dur; if (u < 0 || u > 1) continue;
      const head = o.len * u, a = Math.sin(u * Math.PI) * o.b;
      quad(pt(o, head), pt(o, Math.max(0, head - o.len * .55)), o.w, 0, a, 0, [1, .95, .85]); }
    for (const o of FB) { const u = (tt - o.t0) / o.dur; if (u < 0 || u > 1.6) continue;
      const g = { az: o.az, el: o.el, ang: -1.25 }, s = clamp(u) * (o.el + .02), head = pt(g, s), fade = 1 - smooth(1, 1.6, u);
      quad(head, pt(g, Math.max(0, s - .3 * o.size)), 22 * o.size, 4 * o.size, .9 * fade * (u < 1 ? 1 : 0), .0, [1, .62, .3]);      // hot trail
      quad(pt(g, Math.max(0, s - .02)), pt(g, Math.max(0, s - .55 * o.size)), 9 * o.size, 26 * o.size, .25 * fade, 0, [.8, .7, .62]);   // smoke-lit wake
      if (u < 1) quad(pt(g, s + .008 * o.size), pt(g, s - .03 * o.size), 16 * o.size, 16 * o.size, .7, .7, [1, .85, .6]); }      // glowing head
    for (let i = n; i < MAX; i++) al.fill(0, i * 4, i * 4 + 4);
    geo.attributes.position.needsUpdate = geo.attributes.alpha.needsUpdate = geo.attributes.color.needsUpdate = true;
  });
  (E.lookMods ||= []).push((t, L) => { const f = flashAt(t) * (M.flash ?? .5); if (!f) return;
    L.hor = L.hor.clone().lerp(new THREE.Color(0xd99060), f * .45); L.hemi += f * .8; L.hemiColor = L.hemiColor.clone().lerp(new THREE.Color(0xffb27a), f * .5); });
}
