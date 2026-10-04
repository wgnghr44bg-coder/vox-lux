// Things in the sky (asteroid, falling satellite, a second sun...): TL.skyObjects =
// [{ t0, t1, from: [x,y,z], to: [x,y,z], r, color, trail: true, ease: 2, weight }]
// Each one is a low-poly rock moving from -> to (accelerating with `ease`), with a smoke trail;
// it is also a look target for the camera (camera.js), so the viewer looks up at it.
import * as THREE from 'three';
import { clamp, hash, lerp } from './util.js';

export function createSkyObjects(E, TL) {
  E.skyObjects = (TL.skyObjects || []).map((o, i) => {
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(o.r ?? 20, 0), E.lam(o.color ?? 0x5d5650));
    E.scene.add(m);
    const glow = new THREE.Mesh(new THREE.IcosahedronGeometry((o.r ?? 20) * 1.15, 1), new THREE.MeshBasicMaterial({ color: o.glow ?? 0xffb070, transparent: true, opacity: 0 }));
    m.add(glow);
    const u = t => Math.pow(clamp((t - o.t0) / (o.t1 - o.t0)), o.ease ?? 2);
    const pos = t => [lerp(o.from[0], o.to[0], u(t)), lerp(o.from[1], o.to[1], u(t)), lerp(o.from[2], o.to[2], u(t))];
    E.updates.push((t, F, tv) => { const tt = Math.min(tv, TL.beats.stop); m.visible = tt >= o.t0 - 3 && tt <= o.t1;
      const p = pos(Math.max(tt, o.t0)); m.position.set(p[0], p[1], p[2]); m.rotation.set(tt * .3, tt * .2 + i, 0);
      glow.material.opacity = (o.hot ?? .35) * u(tt); });
    if (o.trail !== false) E.emitters.push((tv, add) => {
      const tt = Math.min(tv, TL.beats.stop); if (tt < o.t0 || tt > o.t1) return;
      for (let k = 0; k < 60; k++) { const back = k * .06, tb = tt - back; if (tb < o.t0) break;
        const p = pos(tb), s = (o.r ?? 20) * (1.2 + back * 1.5);
        add(p[0] + (hash(k, i) - .5) * s * .3, p[1] + (hash(k, i + 5) - .5) * s * .3, p[2], s, .35 * (1 - k / 60), .8, .76, .7, hash(k, 3) * 6); }
    });
    return { ...o, pos, weight: o.weight ?? 3 };
  });
}
