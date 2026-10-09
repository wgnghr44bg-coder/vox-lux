// COLD / DARKNESS: the light fades (sun out, long night), temperature drops, water freezes,
// everything frosts over. The physical quantity is the level 0..1 (1 = dark and deep-frozen).
// TL.forceParams: { darkAt: [0..1 level where darkness starts, full], frostAt: [a, b], snow: 0..1,
//                   breath: time from which your own breath shows as a small white cloud }
import { baseForce } from './base.js';
import { smooth, lerp, hash, noise } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const [d0, d1] = P.darkAt || [0, .6], [f0, f1] = P.frostAt || [.3, 1];
  const F = baseForce(E, TL, 'cold');
  const dark = t => smooth(d0, d1, F.level(t)), freeze = t => smooth(f0, f1, F.level(t));
  const FROST = new E.THREE.Color(0xdfe7ee), ICE = new E.THREE.Color(0xc9dbe4);
  Object.assign(F, {
    dark, freeze,
    fallMode: 'pancake',
    look(t, L) {
      const d = dark(t), N = c => new E.THREE.Color(c);
      L.top.lerp(N(0x05070c), d); L.hor.lerp(N(0x1a2230), d * .95);
      L.sun *= 1 - d; L.sunDisc = (L.sunDisc || N(0)).clone().multiplyScalar(1 - d);
      L.hemi = lerp(L.hemi, .28, d); L.hemiColor.lerp(N(0x8ea3c4), d);
      L.fogColor = L.hor.clone(); L.fogFar = lerp(L.fogFar, 420, d);
      L.stars = smooth(.5, 1, d); L.dark = d; L.dustLight = 1 - d * .6;
    },
  });
  E.updates.push(t => {
    const f = freeze(t);
    for (const m of E.frost) { m.userData.base ??= m.color.clone(); m.color.copy(m.userData.base).lerp(FROST, f * .55); }
    for (const w of E.floods) if (w.mesh.material.color) { w.base ??= w.mesh.material.color.clone(); w.mesh.material.color.copy(w.base).lerp(ICE, smooth(.2, .8, f)); }
  });
  // snow: light at first, then thicker
  const snow = P.snow ?? .7;
  E.emitters.push((tv, add, cam) => {
    const lv = F.level(Math.min(tv, F.STOP)) * snow; if (lv <= .02) return;
    const n = Math.floor(260 * lv);
    for (let k = 0; k < n; k++) {
      const fall = 1.2 + hash(k, 1) * .8, ph = hash(k, 2), h = 30;
      const y = h - ((tv * fall + ph * h) % h);
      const x = cam.x + (hash(k, 3) - .5) * 60 + noise(tv * .3, k) * 1.5, z = cam.z - 8 - hash(k, 4) * 70;
      add(x, y + cam.y - 6, z, .35 + hash(k, 5) * .3, .55, .95, .97, 1, 0);
    }
  });
  // your own breath (POV): a small white puff in front of the camera every few seconds
  if (P.breath != null) {
    const dir = new E.THREE.Vector3();
    E.emitters.push((tv, add, cam) => {
      const BR = Array.isArray(P.breath) ? P.breath : [[P.breath, 1e9]];
      if (!BR.some(([a, b]) => tv >= a && tv <= b) || tv > (TL.beats.fade ?? 1e9)) return;
      const a = (tv - P.breath) % 3.4; if (a > 1.6) return;
      E.camera.getWorldDirection(dir);
      for (let k = 0; k < 7; k++) {
        const u = a + hash(k, 3) * .2, d = 1.1 + u * .7;
        add(cam.x + dir.x * d + (hash(k, 4) - .5) * .12 * (1 + u), cam.y - .3 + u * .12 + dir.y * d, cam.z + dir.z * d + (hash(k, 5) - .5) * .12 * (1 + u),
            .15 + u * .35, .38 * smooth(0, .15, a) * (1 - smooth(.4, 1.6, a)), .95, .97, 1, 100 + hash(k, 6) * 6);   // rot > 50 = no near fade
      }
    });
  }
  return F;
}
