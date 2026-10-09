// ALIEN ARRIVAL (baksteen "Ufo", okt 2026): nothing breaks; a ship takes over the sky. The counter is the ship's
// altitude (TL.range e.g. [12000, 0]); level 0..1 = how close it is (drives the low hum in make_audio.py).
// TL.forceParams: { shade: [[t, 0..1], ...]  how much of the sunlight the ship blocks (its shadow over the city),
//                   tint: 0x...  colour the shaded sky turns to (default cold blue-grey) }
// Pair with TL.ufo (engine/ufo.js) for the ships themselves, and beats.lookUp / carsStop for people and traffic.
import { baseForce } from './base.js';
import { monotone } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const F = baseForce(E, TL, 'alien');
  const shade = P.shade ? monotone(P.shade) : () => 0;
  Object.assign(F, {
    shade: t => Math.max(0, Math.min(1, shade(Math.min(t, F.STOP)))),
    fallMode: 'pancake',
    look(t, L) {
      const s = F.shade(t), N = c => new E.THREE.Color(c);
      L.sun *= 1 - .95 * s; L.sunDisc = (L.sunDisc || N(0)).clone().multiplyScalar(1 - s);
      L.hemi *= 1 - .45 * s; L.hemiColor.lerp(N(0x9fb0c8), s * .6);
      L.top.lerp(N(P.tint ?? 0x46546a), s * .55); L.hor.lerp(N(0x8d98a4), s * .45);
      L.fogColor = L.hor.clone();
      L.dark = Math.max(L.dark || 0, s * .3);     // windows start to glow a little in the shadow
    },
  });
  return F;
}
