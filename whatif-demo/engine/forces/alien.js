// ALIEN ARRIVAL (baksteen "Ufo", okt 2026): nothing breaks; a ship takes over the sky. The counter is the ship's
// altitude (TL.range e.g. [12000, 0]); level 0..1 = how close it is (drives the low hum in make_audio.py).
// TL.forceParams: { shade: [[t, 0..1], ...]  how much of the sunlight the ship blocks (its shadow over the city),
//                   tint: 0x...  colour the shaded sky turns to (default cold blue-grey),
//                   dawn: 0..1   sunrise light (warm low sun, pink horizon, dim blue sky),
//                   hum: [[t, 0..1], ...]  loudness of the ship's hum (default: from the altitude counter) }
// Pair with TL.ufo (engine/ufo.js) for the ships themselves, and beats.lookUp / carsStop for people and traffic.
import { baseForce } from './base.js';
import { monotone } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const F = baseForce(E, TL, 'alien');
  const shade = P.shade ? monotone(P.shade) : () => 0;
  if (P.hum) { const h = monotone(P.hum); F.level = t => Math.max(0, Math.min(1, h(Math.min(t, F.STOP)))); }
  Object.assign(F, {
    shade: t => Math.max(0, Math.min(1, shade(Math.min(t, F.STOP)))),
    fallMode: 'pancake',
    look(t, L) {
      const s = F.shade(t), N = c => new E.THREE.Color(c);
      if (P.dawn) {
        const d = P.dawn;
        L.top.lerp(N(0x3d5378), d); L.hor.lerp(N(0xe9b48e), d); L.sunColor.lerp(N(0xffb070), d); L.sunDisc = N(0xffc890).multiplyScalar(1.4 * d);
        L.sun *= 1 - .35 * d; L.hemi *= 1 - .35 * d; L.hemiColor.lerp(N(0xc9a9b4), d * .6); L.sunSize = 1.6;
      }
      L.sun *= 1 - .95 * s; L.sunDisc = (L.sunDisc || N(0)).clone().multiplyScalar(1 - s);
      L.hemi *= 1 - .45 * s; L.hemiColor.lerp(N(0x9fb0c8), s * .6);
      L.top.lerp(N(P.tint ?? 0x46546a), s * .55); L.hor.lerp(N(0x8d98a4), s * .45);
      L.fogColor = L.hor.clone();
      L.dark = Math.max(L.dark || 0, s * .3);     // windows start to glow a little in the shadow
    },
  });
  return F;
}
