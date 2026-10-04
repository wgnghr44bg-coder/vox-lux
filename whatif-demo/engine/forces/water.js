// WATER: the water level rises (or drops). The physical quantity is the absolute water level y (m);
// strengths for water are "the water level at which this lets go" (cars float at road + 0.6 m).
// TL.forceParams: { rise: metres at level 1 (negative = the water drains away), current: [vx, vz] }
import { baseForce } from './base.js';
import { smooth, lerp, hash } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const rise = P.rise ?? 6, cur = P.current || [0, 0];
  let y;
  const F = baseForce(E, TL, 'water', ({ level }) => { y = t => (E.waterBase ?? 0) + rise * level(t); return y; });
  Object.assign(F, {
    waterY: y,
    field: t => ({ g: 9.8, air: [0, 0, 0], waterY: y(t), current: [cur[0] * F.level(t), 0, cur[1] * F.level(t)] }),
    lateral: t => ({ a: .04 + .1 * F.level(t), dx: cur[0] ? Math.sign(cur[0]) : 0, dz: cur[1] ? Math.sign(cur[1]) : 1 }),
    fallMode: 'sink',
    rumble: t => smooth(.5, 1, F.level(t)) * .01,
    look(t, L) {      // the sky closes in: overcast, flat light
      const o = smooth(0, .6, F.level(t)) * (P.overcast ?? .7);
      L.top.lerp(new E.THREE.Color(0x7d8790), o); L.hor.lerp(new E.THREE.Color(0xaab2b6), o);
      L.sun *= 1 - o * .75; L.fogFar = lerp(L.fogFar, 380, o); L.fogNear = lerp(L.fogNear, 40, o);
    },
  });
  const delta = t => y(t) - (E.waterBase ?? 0);
  E.updates.push((t, _F, tv) => {
    for (const w of E.floods) { w.mesh.position.y = w.y + delta(t) + (w.wave ? Math.sin(tv * .9 + w.y) * .04 : 0); }
  });
  // foam along the waterline where it meets walls and streets
  E.emitters.push((tv, add) => {
    const t = Math.min(tv, F.STOP), lv = F.level(t); if (lv < .05) return;
    for (const s of E.foamLines || []) for (let k = 0; k < s.n; k++) {
      const ph = hash(k, s.z * 3 + s.x), a = (tv * .35 + ph) % 1;
      add(s.x + (hash(k, 1) - .5) * s.w, y(t) + .15, s.z + (hash(k, 2) - .5) * s.d, 1.4 + a * 1.5, Math.sin(a * Math.PI) * .25 * smooth(.05, .3, lv), .9, .93, .94, ph * 6);
    }
  });
  return F;
}
