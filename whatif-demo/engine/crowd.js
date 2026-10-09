// People that walk along a lane (axis 'x' or 'z'), react to the force, and go inside before the
// destruction starts (no one is ever hurt on screen). Beats used: lookUp, shelter.
import { person } from './props.js';
import { rng, smooth, clamp } from './util.js';

export function crowd(E, TL, o) {
  const { n, axis = 'x', lane, range, door, seed = 31, y = .2 } = o;     // lane: [min, max] across; range: [a, b] along
  const B = TL.beats, R = rng(seed);
  const lookUp = B.lookUp ?? 1e9, shelter = B.shelter ?? 1e9;
  for (let i = 0; i < n; i++) {
    const across = lane[0] + R() * (lane[1] - lane[0]), s0 = range[0] + R() * (range[1] - range[0]);
    const dir = R() < .5 ? -1 : 1, v = 1.1 + R() * .4, look = lookUp + R() * 1.5, go = shelter + R() * 2.5;
    const sitter = o.benches && R() < .25 ? o.benches[Math.floor(R() * o.benches.length)] : null;
    const len = range[1] - range[0];
    const wrap = q => range[0] + ((q - range[0]) % len + len) % len;
    person(E, seed * 100 + i, { y, coat: o.coats ? o.coats[Math.floor(R() * o.coats.length)] : undefined, hat: o.hats && R() < .5 ? o.hats[Math.floor(R() * o.hats.length)] : undefined,
      path(t, F) {
        const d = F.droop(t), kind = F.kind;
        // distance walked: integrate the speed, which drops as gravity grows
        const steps = 24, tt = Math.min(t, go); let dist = 0;
        for (let k = 0; k < steps; k++) { const tk = tt * (k + .5) / steps; dist += v / (1 + 2.2 * F.droop(tk)) * (tk > look ? 0 : 1); }
        dist *= tt / steps;
        let along = wrap(s0 + dir * dist), acr = across, rot = axis === 'x' ? (dir > 0 ? Math.PI / 2 : -Math.PI / 2) : (dir > 0 ? 0 : Math.PI);
        let moving = t < go ? 1 : 0, speed = v / (1 + 2.2 * d), stoop = clamp(d * .32 + (kind === 'cold' ? F.level(t) * .15 : 0), 0, .45), headUp = 0;
        if (kind === 'wind' && t > look && t < go) { moving = 0; headUp = smooth(look, look + .8, t) * .5; rot += Math.sin((t - look) * .9 + i) * 1.2; }
        else if (t > look && t < go) { moving = 0; headUp = smooth(look, look + 1.2, t) * .7; rot += Math.sin(i * 2.3) * .9 * smooth(look, look + 1.5, t); }   // stop and stare at the sky
        if (t >= go) {                       // walk (or hurry) to the nearest door and go in
          const target = door(along, acr), tr = t - go, vs = kind === 'gravity' ? .9 / (1 + d) : kind === 'wind' ? 4.2 : 2.2;
          const dd = Math.abs(target - acr), mv = Math.min(dd, tr * vs);
          acr += Math.sign(target - acr) * mv;
          rot = axis === 'x' ? (target > acr ? 0 : Math.PI) : (target > acr ? Math.PI / 2 : -Math.PI / 2);
          moving = kind === 'wind' ? 2 : 1; speed = vs; headUp = 0;
          if (mv >= dd - .3) return { visible: false };
        }
        if (sitter && t > (B.sit ?? 1e9) && t < go) { along = sitter[0]; acr = sitter[1]; moving = 0; rot = sitter[2]; return { x: axis === 'x' ? along : acr, z: axis === 'x' ? acr : along, y: -.35, rot, moving: 0, speed: 0, stoop: stoop * .5 }; }
        return axis === 'x' ? { x: along, z: acr, rot, moving, speed, stoop, headUp } : { x: acr, z: along, rot, moving, speed, stoop, headUp };
      } });
  }
}

// Sunbathers on towels (beach). They lie still until the force reaches them (strength = level
// at which they get up), then some run for the boulevard (they vanish at `exit`, a z value) and
// the others stay standing, looking up. Uses ground height E.groundAt.
export function sunbathers(E, TL, o) {
  const { n, area, exit, seed = 81, runFrac = .55, wake = o.wake || [.25, .55] } = o;
  const R = rng(seed);
  for (let i = 0; i < n; i++) {
    const x = area.x[0] + R() * (area.x[1] - area.x[0]), z = area.z[0] + R() * (area.z[1] - area.z[0]);
    const lieRot = R() * Math.PI * 2, runs = R() < runFrac, w = wake[0] + R() * (wake[1] - wake[0]), v = 3 + R() * 1.4, ph = R() * 6;
    const towel = new E.THREE.Mesh(new E.THREE.PlaneGeometry(.9, 1.9), E.lam([0xd2cbb8, 0x5e6f80, 0xb5653f, 0xc9a94a, 0x6f9bb0][Math.floor(R() * 5)]));
    E.burn.push({ mats: [towel.material], pos: [x - Math.sin(lieRot) * .9, E.groundAt(x, z) + .1, z - Math.cos(lieRot) * .9], size: .45, sun: 10 + R() * 3, charT: 3 });
    towel.rotation.x = -Math.PI / 2; towel.rotation.z = -lieRot; towel.position.set(x - Math.sin(lieRot) * .9, E.groundAt(x, z) + .03, z - Math.cos(lieRot) * .9); E.scene.add(towel);
    let tw = null;
    person(E, seed * 100 + i, { y: 0, coat: [0xd9b9a0, 0xb08a6e, 0x8a6b4e, 0xc9a08a][Math.floor(R() * 4)],
      path(t, F) {
        tw ??= F.timeOf(w);
        const gy = E.groundAt(x, z);
        if (t < tw) return { x, z, y: gy + .12, rot: lieRot, lie: true, moving: 0, speed: 0 };
        const a = t - tw, up = Math.min(1, a / 1.2);
        if (!runs || a < 1.2) {        // gets up, then stands and stares at the Sun
          return { x, z, y: gy, rot: Math.PI + Math.sin(a * .7 + ph) * .3 * up, moving: 0, speed: 0, headUp: smooth(.5, 2, a) * .75, stoop: (1 - up) * .5 };
        }
        const zz = z + (a - 1.2) * v, xx = x + Math.sin(ph) * (a - 1.2) * .6;
        if (zz > exit) return { visible: false };
        return { x: xx, z: zz, y: E.groundAt(xx, zz), rot: 0, moving: 2, speed: v };
      } });
  }
}

// TL.groups = [{ at: [x, z], n, spread, face, y, shot: { name, from: [dx, dy, dz] } }]: people standing close together
// (chatting, phones, waiting) near the camera. At beats.lookUp they stop and stare at the sky with a reaction
// (point, shade the eyes, hands on the head); at beats.shelter they walk off. Optional shot: adds a close shot on them.
export function groups(E, TL, shots) {
  const B = TL.beats;
  (TL.groups || []).forEach((G, gi) => {
    const R = rng(900 + gi), [cx, cz] = G.at, n = G.n ?? 6, sp = G.spread ?? 2.2, gy = G.y ?? (E.groundAt ? E.groundAt(cx, cz) : 0);
    for (let i = 0; i < n; i++) {
      const x = cx + (R() - .5) * sp * 2, z = cz + (R() - .5) * sp, face = (G.face ?? 0) + (R() - .5) * 2.2;
      const look = (B.lookUp ?? 1e9) + R() * 1.2, go = (B.shelter ?? 1e9) + R() * 2, away = R() < .5 ? -1 : 1;
      (E.personFn || person)(E, 5000 + gi * 50 + i, { y: gy + .02, kind: G.kinds?.[i % G.kinds.length], path(t) {
        if (t > go) { const w = (t - go) * 1.6; return { x: x + away * w, z, rot: away * Math.PI / 2, moving: 1, speed: 1.6, visible: w < 40 }; }
        const up = smooth(look, look + 1.2, t);
        return { x, z, rot: face + Math.sin(t * .4 + i) * .15 * (1 - up), moving: 0, speed: 0, headUp: up * .75, stoop: 0 };
      } });
    }
    if (G.lamp !== false) {   // a warm street light over the group: they stay visible (and moody) once it is dark
      const L = new E.THREE.PointLight(0xffd29a, 0, 22, 1.6); L.position.set(cx + (G.lampAt?.[0] ?? 1), gy + 5.2, cz + (G.lampAt?.[1] ?? 1.5)); E.scene.add(L);
      E.updates.push((t, F, tv) => { L.intensity = (E.dark ?? 0) * (E.powerOut?.(t) || (B.powerOff && t > B.powerOff[1] + 1.5) ? 0 : 1) * (G.lampPower ?? 60); });
    }
    if (G.shot && shots) { const [dx, dy, dz] = G.shot.from; shots[G.shot.name] = { pos: [cx + dx, gy + dy, cz + dz], look: [cx, gy + 1.3, cz], drift: G.shot.drift || [0, 0, 0], fov: G.shot.fov ?? 50 }; }
  });
}
