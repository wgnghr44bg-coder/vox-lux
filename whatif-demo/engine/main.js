// Boots a video: scenario (topics/<slug>/scenario.js) + measured voice timing (timing.json)
// -> TL, then place + force + physics, and window.renderAt(t) for the renderer.
//   scene.html?topic=<slug>                  the real video
//   scene.html?place=river-city&force=gravity  preview of a place/force pair without a topic
import * as THREE from 'three';
import { createEngine, FPS } from './core.js';
import { simulate, poseBodies } from './physics.js';
import { createDust } from './dust.js';
import { createHud } from './hud.js';
import { buildTL } from './timeline.js';
import { createCamera } from './camera.js';
import { createSkyObjects } from './sky-objects.js';
import { smooth, clamp, hash, lerp } from './util.js';

const qs = new URLSearchParams(location.search);
const slug = qs.get('topic');
let scen, timing = null;
if (slug) {
  scen = await import(`../topics/${slug}/scenario.js`);
  const r = await fetch(`../topics/${slug}/timing.json`);
  if (r.ok) timing = await r.json();
} else scen = await import('./demo-scenario.js');
const TL = buildTL(scen, timing, { place: qs.get('place'), force: qs.get('force'), shots: qs.get('shots') && JSON.parse(qs.get('shots')) });
const STOP = TL.beats.stop;

const E = createEngine();
E.TL = TL;
const F = (await import(`./forces/${TL.force}.js`)).create(E, TL);
const P = (await import(`./places/${TL.place}.js`)).build(E, TL, F);
E.F = F; E.P = P;
F.attach?.(P);
createSkyObjects(E, TL);

// pose of everything that bends (also used by physics to read where a piece is when it breaks off)
E.poseAll = t => { for (const b of E.bend) b.pose(t, F); E.scene.updateMatrixWorld(true); };

// ---------- schedule: what breaks and what falls, and when ----------
for (const it of E.breaks) {
  const s = it.strength?.[F.kind];
  if (s == null) continue;
  const tRel = it.at ?? F.timeOf(s);
  if (!(tRel < STOP - .2)) continue;
  E.part(it.src, { ...it, tRel, v0: it.v0 ?? F.kick?.(it) ?? [0, 0, 0] });
}
for (const b of E.bodies) if (b.strength && b.tRel >= 1e9) {     // loose things and cars: go when the force reaches them
  const s = b.strength[F.kind]; if (s == null) continue;
  const tr = F.timeOf(s);
  if (tr < STOP) b.tRel = b.kind === 'car' && F.kind === 'wind' ? Math.max(tr, b.brakeT + 2.5) : tr;
}
{ const featured = E.falls.filter(f => f.rank != null).sort((a, b) => a.rank - b.rank);
  (TL.beats.falls || []).forEach((t, i) => { if (featured[i]) featured[i].at = t; });
  for (const f of E.falls) if (f.at == null) { const s = f.strength?.[F.kind]; f.at = s == null ? 1e9 : F.timeOf(s); }
  for (const f of E.falls) if (f.at < STOP) E.EVENTS.push({ t: f.at, kind: 'collapse', e: f.big ?? 1, x: f.cx, z: f.cz }); }
for (const ev of TL.events || []) E.EVENTS.push(ev);

const t0 = performance.now();
simulate(E, F, STOP);
E.EVENTS.push({ t: STOP, kind: 'stop', e: 0 });
E.EVENTS.sort((a, b) => a.t - b.t);
console.log('sim', ((performance.now() - t0) / 1000).toFixed(1) + 's', 'bodies', E.bodies.length, 'events', E.EVENTS.length);

const dust = createDust(E);
const hud = createHud(TL);
E.counterAt = hud.counterAt;

// ---------- collapsing structures ----------
function poseFalls(t) {
  for (const f of E.falls) {
    const a = Math.max(0, t - f.at);
    if (a <= 0) { f.g.position.y = f.base; f.g.rotation.set(0, f.ry ?? 0, 0); continue; }
    const mode = f.mode || F.fallMode;
    if (mode === 'pancake') {     // straight down into its own dust, a slight lean
      const g = F.field(t).g * .32;
      f.g.position.y = f.base - Math.min(f.h * 1.02, .5 * g * a * a);
      f.g.rotation.set(Math.sin(hash(f.cx, 1) * 6) * .05 * smooth(0, 2, a), f.ry ?? 0, Math.sin(hash(f.cz, 2) * 6) * .05 * smooth(0, 2, a));
    } else if (mode === 'sink') {
      f.g.position.y = f.base - Math.min(f.h * .5, .25 * a * a);
      f.g.rotation.set(.12 * smooth(0, 6, a), f.ry ?? 0, .06 * smooth(0, 6, a));
    } else {                       // topple along dir
      const ang = Math.min(1.45, .5 * .22 * a * a + .01 * a), d = f.dir || [0, 1];
      f.g.rotation.set(ang * d[1], f.ry ?? 0, -ang * d[0]);
      f.g.position.y = f.base - Math.min(f.h * .5, 2.5 * a * a);
    }
  }
}

// ---------- camera (handheld POV that looks at what happens: camera.js) ----------
const camera = createCamera(E, TL, P, F);
window.camTarget = tv => { const k = camera.targetAt(tv); return k < 0 ? null : E.lookTargets[k].kind; };
function cameraAt(tv, fixed) {
  const look = camera.apply(tv, fixed);
  if (E.sunOffset) {        // keep the shadow map around what the camera sees
    const c = E.camera.position, dx = look.x - c.x, dz = look.z - c.z, l = Math.hypot(dx, dz) || 1, k2 = Math.min(70, l * .5);
    E.sun.target.position.set(c.x + dx / l * k2, 0, c.z + dz / l * k2);
    E.sun.position.copy(E.sun.target.position).add(E.sunOffset);
  }
}

// ---------- light ----------
const C = h => new THREE.Color(h);
function applyLook(t) {
  const L = P.look(t);
  F.look?.(t, L);
  E.skyMat.uniforms.top.value.copy(L.top); E.skyMat.uniforms.hor.value.copy(L.hor);
  E.skyMat.uniforms.sunDir.value.copy(E.sunOffset ?? E.sun.position).normalize(); E.skyMat.uniforms.sunCol.value.copy(L.sunDisc || C(0));
  E.skyMat.uniforms.stars.value = L.stars || 0; E.skyMat.uniforms.sunSize.value = L.sunSize || 1;
  E.scene.fog.color.copy(L.fogColor || L.hor); E.scene.fog.near = L.fogNear; E.scene.fog.far = L.fogFar;
  dust.mat.uniforms.fogColor.value.copy(E.scene.fog.color); dust.mat.uniforms.fogNear.value = L.fogNear; dust.mat.uniforms.fogFar.value = L.fogFar;
  dust.mat.uniforms.light.value = L.dustLight ?? 1;
  E.hemi.intensity = L.hemi; E.hemi.color.copy(L.hemiColor); E.hemi.groundColor.copy(L.groundColor || C(0x5a5448));
  E.sun.intensity = L.sun; E.sun.color.copy(L.sunColor);
  const dark = L.dark || 0;
  for (const l of E.lights) l.mat.color.setHex(dark > .25 + l.at && !(E.powerOut?.(t)) ? l.on : l.off);
  for (const m of E.windowMats) m.emissiveIntensity = E.powerOut?.(t) ? 0 : smooth(.25, .7, dark) * .85;
  E.renderer.toneMappingExposure = 1;
  document.getElementById('haze').style.opacity = L.haze || 0;
  document.getElementById('haze').style.background = L.hazeColor || '#6e604f';
}

function renderScene(tv, fixed) {
  const ts = fixed ? fixed.t : tv, t = Math.min(ts, STOP);
  applyLook(t);
  E.poseAll(t);
  for (const u of E.updates) u(t, F, ts);
  for (const p of E.people) p.update(t, F);
  poseBodies(E, t, F);
  poseFalls(t);
  cameraAt(tv, fixed);
  const n = dust.render(ts, E.camera.position);
  E.renderer.render(E.scene, E.camera);
  return n;
}

// motion blur: average a few subframes over half a frame (only where render.mjs asks for it)
const blurCv = document.createElement('canvas'); blurCv.width = E.W; blurCv.height = E.H;
blurCv.style.cssText = 'position:absolute;left:0;top:0;display:none';
E.renderer.domElement.after(blurCv);
const bctx = blurCv.getContext('2d');
function renderBlur(n, at) {
  for (let k = 0; k < n; k++) { at(k / (n - 1) - 1); bctx.globalAlpha = 1 / (k + 1); bctx.drawImage(E.renderer.domElement, 0, 0); }
  blurCv.style.display = 'block';
}

// opening hook (?hook=1): a few seconds from later in the story, shown first (TL.hook = { at, dur, shot, text, slow })
const HOOK = qs.get('hook') && TL.hook;
window.renderAt = function (tv, n = 1) {
  blurCv.style.display = 'none';
  const sub = HOOK ? (dt => renderScene(tv + dt / FPS * .5, { shot: HOOK.shot, t: HOOK.at + (tv + dt / FPS * .5) * (HOOK.slow ?? .5) }))
                   : (dt => renderScene(tv + dt / FPS * .5));
  if (n > 1) renderBlur(n, sub); else sub(0);
  if (HOOK) {
    hud.update(HOOK.at + tv * (HOOK.slow ?? .5));
    for (const id of ['title', 'end', 'fade', 'black']) document.getElementById(id).style.opacity = 0;
    const c = document.getElementById('cap'); c.textContent = HOOK.text; c.style.opacity = smooth(.1, .5, tv) * (1 - smooth(HOOK.dur - .4, HOOK.dur, tv));
  } else hud.update(tv);
  return 0;
};
// how many subframes this frame needs: fast camera turns, running, the climax
window.blurAt = tv => {
  if (HOOK) return 2;
  const sp = camera.speedAt(tv), hot = tv > TL.beats.climax - 1 && tv < STOP;
  return sp > 40 || hot || (camera.runningAt(tv) && sp > 12) ? 3 : sp > 20 || camera.runningAt(tv) ? 2 : 1;
};
window.T_END = HOOK ? HOOK.dur : TL.T_END; window.TL = TL; window.EVENTS = E.EVENTS;
window.AUDIO = { place: TL.place, force: TL.force, ambience: P.ambience, level: Array.from({ length: Math.ceil(TL.T_END * 10) }, (_, i) => +F.level(Math.min(i / 10, STOP)).toFixed(3)) };
document.fonts.ready.then(() => { window.ready = true; });
