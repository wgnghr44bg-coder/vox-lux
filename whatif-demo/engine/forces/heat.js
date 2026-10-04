// HEAT / THE SUN COMES CLOSER: the counter is the distance to the Sun (any unit; the first value
// is "today"). Sunlight scales with 1/d², the Sun's disc with 1/d. The physical quantity for
// strengths (`heat`) is the level 0..1 = extra sunlight / extra sunlight at the end.
//   snow melts (E.melt), snow slabs slide off roofs, the light turns harsh and white, the air
//   hazes, and late in the story smoke rises from forest fires (E.fireSpots).
// TL.forceParams: { fireAt: level where fires start (default .75) }
import { baseForce } from './base.js';
import { smooth, lerp, hash, clamp } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const d0 = TL.counter[0][1], dEnd = Math.min(...TL.counter.map(c => c[1]));
  const sMax = (d0 / dEnd) ** 2;
  let sun;
  const F = baseForce(E, TL, 'heat', ({ counter }) => {
    sun = t => (d0 / counter(Math.min(t, TL.beats.stop))) ** 2;     // sunlight relative to today
    return t => (sun(t) - 1) / (sMax - 1);
  });
  F.level = F.phys;
  const C = c => new E.THREE.Color(c);
  const fireAt = P.fireAt ?? .75;
  Object.assign(F, {
    sunlight: t => sun(t),
    fallMode: 'sink',
    lateral: t => ({ a: .02 + .06 * F.level(t), dx: 0, dz: 1 }),
    look(t, L) {
      const s = sun(t), lv = F.level(t);
      L.sun *= Math.min(2.2, s); L.hemi *= 1 + (s - 1) * .25;
      L.sunColor.lerp(C(0xffffff), smooth(0, .5, lv));
      L.sunDisc = (L.sunDisc || C(0x998877)).clone().lerp(C(0xffe9b8), smooth(0, .4, lv)).multiplyScalar(1 + lv);
      L.sunSize = Math.sqrt(s) * (1 + lv * (P.sunGrow ?? .35));       // the disc grows with 1/d (a little extra so it reads on a phone)
      L.top.lerp(C(0x9fb6c8), smooth(.2, 1, lv) * (P.wash ?? .7));   // a washed-out, hazy sky
      L.hor.lerp(C(0xe6dcc4), smooth(.2, 1, lv) * (P.wash ?? .7) * 1.1);
      const haze = (smooth(.3, 1, lv) * .6 + smooth(fireAt, 1, lv) * .3) * (P.haze ?? 1);
      L.fogColor = L.hor.clone().lerp(C(0xb9a588), smooth(fireAt, 1, lv) * .6);
      L.fogNear = lerp(L.fogNear, 60, haze); L.fogFar = lerp(L.fogFar, 700, haze);
      L.haze = smooth(.4, 1, lv) * .08 + smooth(fireAt, 1, lv) * .1; L.hazeColor = '#c8a46e';
    },
  });
  E.updates.push(t => {
    const lv = F.level(t);
    for (const m of E.melt) {
      const k = m.late ? smooth(.45, 1, lv) : smooth(.08, .6, lv);
      if (m.mat) { m.base ??= m.mat.color.clone(); m.mat.color.copy(m.base).lerp(C(m.bare), k); }
      else { m.s0 ??= m.mesh.scale.clone(); const f = lerp(1, m.to, k); m.mesh.scale.set(m.s0.x * f, m.s0.y * f, m.s0.z * f); m.mesh.visible = f > .02; }
    }
  });
  // forest fires on the hills: tall columns of smoke, an orange glow at the base
  // things that catch fire: dry cloth, palm leaves and wood ignite at roughly 10-16× today's sunlight
  const timeOfSun = x => { for (let t = 0; t < TL.beats.stop; t += 1 / 30) if (sun(t) >= x) return t; return 1e9; };
  const CHAR = C(0x1c1917);
  E.updates.push((t, _F, tv) => {
    for (const b of E.burn) {
      b.t0 ??= timeOfSun(b.sun);
      const a = Math.min(tv, TL.beats.stop + 30) - b.t0, k = smooth(0, b.charT ?? 5, a);
      for (const m of b.mats) { m.userData.burnBase ??= m.color.clone(); m.color.copy(m.userData.burnBase).lerp(CHAR, k); }
      if (b.shrink) for (const o of b.shrink) { o.userData.s0 ??= o.scale.clone(); const f = 1 - smooth(1, 7, a) * .7; o.scale.set(o.userData.s0.x * f, o.userData.s0.y * f, o.userData.s0.z * f); }
    }
  });
  E.emitters.push((tv, add) => {
    for (const [i, b] of E.burn.entries()) {
      const t0 = b.t0 ?? 1e9, a = tv - t0; if (a < 0) continue;
      const s = b.size ?? 1, grow = smooth(0, 1.2, a), out = 1 - smooth(b.burnT ?? 30, (b.burnT ?? 30) + 6, a);
      for (let k = 0; k < 10; k++) {          // flames: flickering orange-yellow tongues
        const u = (tv * 1.6 + hash(k, i)) % 1;
        add(b.pos[0] + (hash(k, i + 2) - .5) * s * 1.4, b.pos[1] + u * s * 2.2, b.pos[2] + (hash(k, i + 4) - .5) * s * 1.4,
          s * (1.6 - u) * 1.1, (1 - u) * .65 * grow * out, 1, .45 + u * .35, .12, hash(k, 9) * 6);
      }
      for (let k = 0; k < 14; k++) {          // smoke rising and drifting inland
        const u = (tv * .22 + hash(k, i + 7)) % 1;
        add(b.pos[0] + (hash(k, i + 8) - .5) * s + u * 3, b.pos[1] + s + u * (8 + s * 10), b.pos[2] + u * u * 10,
          s * (1.5 + u * 6), (1 - u) * .38 * grow, .24, .22, .21, hash(k, 11) * 6);
      }
    }
  });
  F.timeOfSun = timeOfSun;
  F.attach = () => {
    for (const b of E.burn) { b.t0 = timeOfSun(b.sun); if (b.t0 < TL.beats.stop) E.EVENTS.push({ t: b.t0, kind: 'fire', e: Math.min(1, .4 + (b.size ?? 1) * .3), x: b.pos[0], y: b.pos[1], z: b.pos[2] }); } (E.fireSpots || []).forEach((p, i) => { const t = F.timeOf(fireAt + i * .05); if (t < TL.beats.stop) E.EVENTS.push({ t, kind: 'fire', e: .8, x: p[0], y: p[1] + 30, z: p[2] }); }); };
  E.emitters.push((tv, add) => {
    const t = Math.min(tv, TL.beats.stop);
    (E.fireSpots || []).forEach((p, i) => {
      const t0 = F.timeOf(fireAt + i * .05); if (t < t0) return;
      const a = t - t0, n = 70;
      for (let k = 0; k < n; k++) {
        const u = ((tv * .08 + hash(k, i)) % 1), h = u * (40 + a * 25), drift = u * u * 60;
        add(p[0] + (hash(k, 2) - .5) * 14 + drift, p[1] + h, p[2] + (hash(k, 3) - .5) * 14, 14 + u * 40, smooth(0, 1.5, a) * (1 - u) * .45, .32, .29, .27, hash(k, 4) * 6);
      }
      for (let k = 0; k < 12; k++) add(p[0] + (hash(k, 5) - .5) * 16, p[1] + 2 + hash(k, 6) * 4, p[2] + (hash(k, 7) - .5) * 10, 8, smooth(0, 1, a) * (.5 + .3 * Math.sin(tv * 9 + k)) * .6, 1, .55, .2, 0);
    });
  });
  return F;
}
