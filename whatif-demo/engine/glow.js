// A VOLCANO WAKING UP in the distance (klein, okt 2026): an orange glow on the horizon and an ash plume lit from below.
//   TL.glows = [{ pos: [x, y, z], t0, t1, size: 1, color: 0xff7a30 }]   the glow grows between t0 and t1 and stays
// Uses the dust layer (E.emitters) and one point light, so it works in any place.
import * as THREE from 'three';
import { hash, smooth } from './util.js';

export function createGlows(E, TL) {
  for (const [gi, G] of (TL.glows || []).entries()) {
    const [x, y, z] = G.pos, s = G.size ?? 1, c = new THREE.Color(G.color ?? 0xff7a30);
    const k = t => smooth(G.t0, G.t1, Math.min(t, TL.beats.stop));
    const L = new THREE.PointLight(c, 0, 900 * s, 1.2); L.position.set(x, y + 30 * s, z); E.scene.add(L);
    E.updates.push((t, F, tv) => { L.intensity = k(t) * 4e4 * s * (.85 + .15 * Math.sin(tv * 7.3) * Math.sin(tv * 3.1)); });
    E.emitters.push((tv, add) => {
      const a = k(tv); if (a <= 0) return;
      for (let i = 0; i < 70; i++) {                         // ash column, lit orange at the base, grey higher up
        const u = (tv * .05 + hash(i, gi * 7 + 1)) % 1, h = u * 520 * s * a, r = 30 * s + u * 160 * s;
        const warm = 1 - smooth(0, .35, u);
        add(x + (hash(i, 2) - .5) * r + u * 120 * s, y + h, z + (hash(i, 3) - .5) * r * .6, (70 + u * 240) * s, .55 * Math.sin(u * Math.PI) * a,
            .32 + .6 * warm, .3 + .25 * warm, .3 + .02 * warm, hash(i, 4) * 6);
      }
      for (let i = 0; i < 20; i++) {                        // the glowing vent itself
        const u = (tv * .6 + hash(i, gi * 7 + 5)) % 1;
        add(x + (hash(i, 6) - .5) * 60 * s, y + u * 50 * s, z + (hash(i, 7) - .5) * 30 * s, (40 + u * 40) * s, .8 * (1 - u) * a, 1, .55, .22, 99);
      }
    });
  }
}
