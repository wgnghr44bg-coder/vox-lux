// EARTHQUAKE: tremors that shake everything (trees, lamps, signs sway; the camera shakes, also on a tripod),
// cracks that open in asphalt and ground (E.crackSpots), loose things that topple (E.breaks with strength.quake),
// structures that fall (E.falls with strength.quake or beats.falls) and steam from hot ground (E.steamSpots).
// The counter is free (e.g. distance, magnitude); the shaking comes from TL.forceParams:
//   tremors: [[t, strength 0..1, seconds], ...]   individual quakes (default: a few, growing, from the counter level)
//   steamAt: [t0, t1]                              steam vents wake up between t0 and t1 (default: never)
//   crackK:  how wide cracks open (default 1)
// The physical quantity (for strength.quake and timeOf) is the shaking 0..1; F.level is the same (sound).
import { baseForce } from './base.js';
import { smooth, hash, noise, clamp } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  let TR = P.tremors;
  const F = baseForce(E, TL, 'quake', ({ level }) => {
    if (!TR) { TR = []; for (let t = 2; t < TL.beats.stop; t += 3 + hash(t, 3) * 4) { const s = level(t); if (s > .05) TR.push([t, s, 2 + s * 4]); } }
    const env = t => { let m = 0; for (const [t0, s, d] of TR) { const a = t - t0; if (a < 0 || a > d) continue;
      m = Math.max(m, s * smooth(0, Math.min(.4, d * .15), a) * (1 - smooth(d * .45, d, a))); } return m; };
    return t => env(Math.min(t, TL.beats.stop));
  });
  const shakeAt = t => F.phys(t) * (.75 + .25 * noise(t * 3.1, 5));
  const DT = 1 / 30, maxTab = []; { let m = 0; for (let t = 0; t <= TL.T_END + 1; t += DT) { m = Math.max(m, F.phys(t)); maxTab.push(m); } }
  const reached = t => maxTab[clamp(Math.round(t / DT), 0, maxTab.length - 1)];     // strongest shaking so far
  F.level = F.phys;
  Object.assign(F, {
    tremors: () => TR,
    reached,
    shake: t => shakeAt(t) * .3,                           // camera.js: fast handheld-like jolts while it shakes
    lateral: t => { const a = shakeAt(t); return { a: a * .38, dx: Math.sin(t * 17.3) * .7 + Math.sin(t * 11.1) * .3, dz: Math.cos(t * 13.7) * .5 }; },
    kick: it => [(hash(it.hx * 31, 1) - .5) * 2.5, 1 + hash(it.hz * 17, 2), (hash(it.hy * 23, 3) - .5) * 2.5],
    fallMode: 'topple',
  });

  // cracks: a jagged dark strip that runs open along its length, then widens with every stronger tremor
  F.attach = () => {
    const THREE = E.THREE, m = new THREE.MeshBasicMaterial({ color: 0x141210 }), rim = E.lam(0x6e6656);
    for (const [i, c] of (E.crackSpots || []).entries()) {
      const n = 16, top = [], bot = [];
      for (let k = 0; k <= n; k++) { const u = k / n, w = c.w * (.35 + .65 * Math.sin(Math.PI * u)) * (.7 + hash(k, i) * .6), off = (hash(k, i + 9) - .5) * c.w * 1.6;
        top.push([u * c.len - c.len / 2, off + w / 2]); bot.push([u * c.len - c.len / 2, off - w / 2]); }
      const sh = new THREE.Shape(); sh.moveTo(...top[0]); top.forEach(p => sh.lineTo(...p)); bot.reverse().forEach(p => sh.lineTo(...p)); sh.closePath();
      const geo = new THREE.ShapeGeometry(sh); geo.rotateX(-Math.PI / 2);
      const g = new THREE.Group(); g.position.set(c.x, (E.groundAt(c.x, c.z) ?? 0) + .07, c.z); g.rotation.y = c.ang; E.scene.add(g);
      const hole = new THREE.Mesh(geo, m); g.add(hole);
      const lip = new THREE.Mesh(geo, rim); lip.scale.set(1, 1, 1.9); lip.position.y = -.01; g.add(lip);     // broken asphalt edge
      const t0 = F.timeOf(c.at);
      if (t0 < TL.beats.stop) E.EVENTS.push({ t: t0, kind: 'rift', e: .8, x: c.x, y: .2, z: c.z });
      E.updates.push(t => { const a = t - t0; g.visible = a > 0; if (a <= 0) return;
        const run = smooth(0, .8, a), wide = (P.crackK ?? 1) * (.6 + 1.6 * clamp((reached(t) - c.at) / (1 - c.at)));
        g.scale.set(run, 1, wide); });
    }
    for (const tr of TR) if (tr[0] < TL.beats.stop) E.EVENTS.push({ t: tr[0], kind: 'quake', e: tr[1], dur: tr[2] });
  };

  // steam vents: white plumes that grow and lean a little in the breeze
  if (P.steamAt) E.emitters.push((tv, add) => {
    const [a, b] = P.steamAt, t = tv;
    (E.steamSpots || []).forEach(([x, y, z, s], i) => {
      const t0 = a + (b - a) * hash(i, 41); if (t < t0) return;
      const k = smooth(0, 4, t - t0) * s;
      for (let j = 0; j < 22; j++) { const u = (tv * .12 + hash(j, i)) % 1;
        add(x + (hash(j, i + 3) - .5) * 4 + u * u * 14, y + 1 + u * 26 * (.6 + k * .5), z + (hash(j, i + 5) - .5) * 4, 3 + u * 12 * (.5 + k * .5),
          (1 - u) * smooth(0, .15, u) * .5 * k, .93, .94, .95, hash(j, 7) * 6); }
    });
  });
  return F;
}
