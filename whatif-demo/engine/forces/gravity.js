// GRAVITY: everything gets heavier. The physical quantity is the extra g (0 = normal, 1 = doubled).
// Things sag and droop, weak parts snap and drop straight down, structures collapse into themselves.
// TL.forceParams: { gMax: 2 } (g at level 1)
import { baseForce } from './base.js';
import { smooth, lerp, hash } from '../util.js';

export function create(E, TL) {
  const gMax = TL.forceParams?.gMax ?? 2;
  let gF;
  const F = baseForce(E, TL, 'gravity', ({ level }) => { gF = t => 1 + (gMax - 1) * level(t); return t => gF(t) - 1; });
  Object.assign(F, {
    gF,
    droop: t => gF(t) - 1,
    field: t => ({ g: 9.8 * gF(t), air: [0, 0, 0], waterY: E.waterBase ?? -1e9 }),
    fallMode: 'pancake',
    rumble: t => smooth(.4, 1, gF(t) - 1) * .02,
    look(t, L) {
      // dust from collapses hangs in the air afterwards; the light stays the same
      const after = E.falls.filter(f => f.at < t).length;
      const haze = Math.min(.45, after * .12) * smooth(0, 1, after);
      L.fogNear = lerp(L.fogNear, 30, haze); L.fogFar = lerp(L.fogFar, 300, haze);
      L.fogColor = (L.fogColor || L.hor).clone().lerp(new E.THREE.Color(0xa49784), haze);
      L.haze = (L.haze || 0) + haze * .15;
    },
  });
  // fine grit raining off sagging structures once the load gets serious
  E.emitters.push((tv, add) => {
    const t = Math.min(tv, F.STOP), d = gF(t) - 1; if (d < .55) return;
    for (const s of E.gritSources || []) for (let k = 0; k < 14; k++) {
      const ph = hash(k, s.x * 7), a = ((t * .5 + ph) % 1);
      add(s.x + (hash(k, 3) - .5) * s.w, s.y - a * a * s.y * 1.6, s.z + (hash(k, 4) - .5) * s.d, 1.2 + a * 2, (1 - a) * .18 * smooth(.55, .9, d), .66, .6, .52, ph * 6);
    }
  });
  return F;
}
