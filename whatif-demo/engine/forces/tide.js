// TIDE (baksteen "extreem getij", okt 2026): the sea goes up AND back down again (water.js only rises or only drains).
//   TL.forceParams = { tide: [[t, y], ...] absolute water level in m (mean sea level 0) at video time t,
//                      calm: y up to which nothing happens (default 1), top: y at which level() = 1 (default 6) }
// The counter stays free for something else (e.g. the Moon's distance). Strengths for this force are water levels
// (like water.js): "lets go when the water reaches y". level(t) = how far the water is above its calm range (0..1,
// for sound and shake). field(t).current flows inland while the water rises and back out while it falls.
import { baseForce } from './base.js';
import { smooth, clamp, monotone } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const y = monotone(P.tide || [[0, 0]]), calm = P.calm ?? 1, top = P.top ?? 6;
  const F = baseForce(E, TL, 'water', () => t => y(Math.min(t, TL.beats.stop)));
  const Y = t => y(Math.min(t, F.STOP));
  const rate = t => (Y(t + .25) - Y(t - .25)) * 2;        // m/s, + = rising
  Object.assign(F, {
    kind: 'water',
    waterY: Y, rate,
    level: t => clamp((Y(t) - calm) / (top - calm)),
    field: t => ({ g: 9.8, air: [0, 0, 0], waterY: Y(t), current: [0, 0, clamp(rate(t) * 1.5, -3, 3)] }),
    lateral: t => ({ a: clamp(Math.abs(rate(t)) * .08), dx: 0, dz: Math.sign(rate(t)) || 1 }),
    fallMode: 'sink',
    rumble: t => smooth(.3, 1.2, Math.abs(rate(t))) * .012,
  });
  // the place sets E.waterBase; every flood surface follows the tide
  E.updates.push((t, _F, tv) => {
    const d = Y(t) - (E.waterBase ?? 0);
    for (const w of E.floods) w.mesh.position.y = w.y + d + (w.wave ? Math.sin(tv * .9 + w.y) * .04 : 0);
  });
  return F;
}
