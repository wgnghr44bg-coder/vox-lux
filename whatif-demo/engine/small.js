// KLEINE DINGEN (baksteen): the small things that tell a big story. Works with any place.
//   beats.vanish: t                 every person disappears in one click (drivers too); some drop a bag or phone
//   TL.traffic = [{ x, z, dir, v, axis, coast }]   cars in a lane ('z': x fixed; z = where the car is at beats.vanish);
//                                   from beats.vanish on nobody drives: they roll on and coast to a stop (no brake lights)
//   TL.bikes = [{ x, z, dir, v, axis, fall: [dx, dz] }]   a cyclist (z/x = where at vanish); without rider the bike rolls on, wobbles, falls
//   TL.crashes = [{ at, point: [x, z], cars: [{ dir: [dx, dz], v, off }], smoke: 1, alarm: 20 }]
//                                   driverless cars drift (off = metres beside the line at vanish) and meet at `point` at `at`:
//                                   bang, slide, hazard lights, smoke from the bonnet, a car alarm for `alarm` s
//   TL.smoke = [[t, x, y, z, size]]   a smoke column from t on
//   TL.extraShots = { name: shot }  shots of the scenario itself (POV walks etc.)
//   Sounds (make_audio.py): events 'click', 'drop', 'crash', 'alarm' { dur }, 'buzz' { dur }; TL.audio.quiet = t (city hush)
import * as THREE from 'three';
import { rng, hash, smooth, clamp, lerp } from './util.js';
import { car, person } from './props.js';

export function applySmall(E, TL, F, P) {
  const B = TL.beats, V = B.vanish ?? 1e9;
  Object.assign(P.shots, TL.extraShots || {});
  if (B.vanish != null) E.EVENTS.push({ t: V, kind: 'click', e: 1 });

  // ---------- things people drop when they vanish ----------
  if (B.vanish != null) {
    const R = rng(515);
    for (const p of [...E.people]) {
      if (!p.path || R() > (TL.dropFrac ?? .45)) continue;
      const s = p.path(V, F, p); if (!s || s.visible === false || s.lie) continue;
      const bag = R() < .65, g = new THREE.Group(); E.scene.add(g);
      const col = [0x3a3430, 0x6b4a32, 0x2f3e52, 0x8a3a30, 0xb59a5a][Math.floor(R() * 5)];
      if (bag) { const b = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.36, .28, .13), E.lam(col))); g.add(b);
        const st = new THREE.Mesh(new THREE.TorusGeometry(.13, .012, 4, 10, Math.PI), E.lam(col)); st.position.y = .14; g.add(st); }
      else { const ph = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.075, .012, .15), E.lam(0x1d1f22))); g.add(ph); }
      const side = R() < .5 ? -1 : 1, h0 = bag ? .75 : 1.05, x = s.x + Math.cos(s.rot) * .25 * side, z = s.z - Math.sin(s.rot) * .25 * side;
      const gy = (E.groundAt?.(x, z) ?? 0) + (p.baseY ?? .2), tf = Math.sqrt(2 * h0 / 9.8), rz = (R() - .5) * (bag ? 2.6 : .4), ry = R() * 6;
      E.EVENTS.push({ t: V + tf, kind: 'drop', e: bag ? .6 : .25, x, z });
      E.updates.push(t => {
        g.visible = t >= V; if (!g.visible) return;
        const a = t - V, k = Math.min(1, a / tf), bounce = a > tf ? Math.abs(Math.sin((a - tf) * 9)) * .05 * Math.exp(-(a - tf) * 6) : 0;
        const lie = bag ? smooth(tf * .7, tf + .25, a) : 1;
        g.position.set(x, gy + (bag ? .07 + .07 * (1 - lie) : .01) + h0 * (1 - k * k) + bounce, z);
        g.rotation.set(bag ? -lie * Math.PI / 2 * (rz > 0 ? 1 : .6) : 0, ry, bag ? rz * lie * .3 : 0);
      });
    }
  }

  // ---------- traffic without drivers ----------
  for (const [i, c] of (TL.traffic || []).entries()) {
    const ax = c.axis || 'z', dir = c.dir, v = c.v ?? 10, coast = c.coast ?? 6 + hash(i, 3) * 4;
    const o = ax === 'z' ? { x0: c.x, z0: c.z - dir * v * V } : { z0: c.z, x0: c.x - dir * v * V };
    car(E, 900 + i, { ...o, dir, v, axis: ax, a: -1e5, b: 1e5, brakeT: V + hash(i, 4) * .5, Tb: coast, noBrakeLight: true, F, strength: {} });
  }

  // ---------- bikes ----------
  for (const [i, bk] of (TL.bikes || []).entries()) bike(E, TL, F, i, bk, V);

  // ---------- crashes ----------
  for (const [ci, C] of (TL.crashes || []).entries()) {
    const at = C.at, [px, pz] = C.point;
    C.cars.forEach((cc, k) => {
      const [dx, dz] = cc.dir, L = Math.hypot(dx, dz), ux = dx / L, uz = dz / L, nx = uz, nz = -ux, v = cc.v ?? 9, off = cc.off ?? 0;
      const cx = px - ux * 2.3, cz = pz - uz * 2.3, spin = (cc.spin ?? (k ? -.5 : .4)), slide = cc.slide ?? 2.2;
      const yaw0 = Math.atan2(-ux, -uz);
      const b = car(E, 950 + ci * 10 + k, { x0: 0, z0: 0, dir: 1, v: 0, F, strength: {}, noBrakeLight: true });
      const lat = t => off * (1 - smooth(Math.min(V, at - .5), at, t));        // drifts out of its lane once nobody steers
      b.drive = t => {
        if (t <= at) { const s = v * (at - t); return { p: [cx - ux * s + nx * lat(t), .75, cz - uz * s + nz * lat(t)], r: [0, yaw0 + (off ? -Math.sign(off) * .12 * smooth(V, at, t) * (t < at ? 1 : 0) : 0), 0], v: [ux * v, 0, uz * v] }; }
        const a = t - at, m = 1 - Math.exp(-a * 3.2), j = Math.exp(-a * 9) * Math.sin(a * 40) * .03;
        return { p: [cx + (ux * .5 + nx * .3 * Math.sign(spin)) * slide * m, .75 + j, cz + (uz * .5 + nz * .3 * Math.sign(spin)) * slide * m], r: [j, yaw0 + spin * m, j * 2], v: [0, 0, 0] };
      };
      const pose0 = b.onPose;
      b.onPose = (t, st, w) => { pose0?.(t, st, w); b.obj.children[0].children.forEach(m => { if (m.geometry?.parameters?.width === 1.5 && m.geometry.parameters.depth === .05)
        m.material.color.setHex(t > at + .4 && Math.floor((t - at) * 1.6) % 2 === 0 ? 0xe39a2a : 0x5a2420); }); };   // hazard lights
      if (C.smoke !== false && k === 0) (TL.smoke ||= []).push([at + .6, px, 1.1, pz, C.smoke ?? 1]);
    });
    E.EVENTS.push({ t: at, kind: 'crash', e: 1, x: px, z: pz });
    if (C.alarm) E.EVENTS.push({ t: at + 1.2, kind: 'alarm', dur: C.alarm, e: 1, x: px, z: pz });
  }

  // ---------- smoke columns ----------
  for (const [t0, x, y, z, size = 1] of TL.smoke || []) {
    E.emitters.push((tv, add) => {
      const tt = Math.min(tv, B.stop) - t0; if (tt < 0) return;
      const n = Math.floor(tt / .14);
      for (let i = Math.max(0, n - 40); i <= n; i++) {
        const age = tt - i * .14; if (age < 0) continue;
        const gr = .42 + hash(i, 7) * .12, life = 5.5;
        add(x + (hash(i, 1) - .5) * .6 + age * .5, y + age * (1.1 + hash(i, 3) * .4), z + (hash(i, 2) - .5) * .6 + age * .15,
            (.5 + age * .8) * size, .42 * smooth(0, .4, age) * (1 - smooth(life * .5, life, age)) * smooth(0, 1.5, tt), gr, gr, gr * 1.02, hash(i, 4) * 6);
      }
    });
  }
}

// a bicycle (+ rider until beats.vanish): rides along a lane; without rider it coasts, wobbles and falls over
function bike(E, TL, F, i, o, V) {
  const { lam, shadowed } = E, g = new THREE.Group(), frame = new THREE.Group(); g.add(frame); E.scene.add(g);
  const col = lam(o.color ?? [0x2f5d8a, 0x8a3a30, 0x2a2c2e, 0x3f6f4a][i % 4]), dark = lam(0x1c1d1f);
  const wheels = [-.52, .52].map(z => { const w = shadowed(new THREE.Mesh(new THREE.TorusGeometry(.33, .028, 5, 16), dark)); w.rotation.y = Math.PI / 2; w.position.set(0, .35, z); frame.add(w); return w; });
  const tube = (a, b, r = .022) => { const A = new THREE.Vector3(...a), Bv = new THREE.Vector3(...b), m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(r, r, A.distanceTo(Bv), 5), col));
    m.position.copy(A).lerp(Bv, .5); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), Bv.clone().sub(A).normalize()); frame.add(m); };
  tube([0, .35, .52], [0, .95, .38]); tube([0, .95, .38], [0, .82, -.18]); tube([0, .82, -.18], [0, .38, 0]); tube([0, .38, 0], [0, .95, .38]);
  tube([0, .38, 0], [0, .35, -.52]); tube([0, .82, -.18], [0, .35, -.52]);
  const bar = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.55, .03, .03), dark)); bar.position.set(0, 1.0, .36); frame.add(bar);
  const seat = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.12, .05, .24), dark)); seat.position.set(0, .88, -.2); frame.add(seat);
  const ax = o.axis || 'z', dir = o.dir, v = o.v ?? 4.5, roll = 2.2, fallSide = o.side ?? (hash(i, 9) < .5 ? -1 : 1);
  const p0 = ax === 'z' ? o.z - dir * v * V : o.x - dir * v * V;
  const along = t => t < V ? p0 + dir * v * t : p0 + dir * (v * V + v * Math.min(t - V, roll) - v * Math.min(t - V, roll) ** 2 / (2 * roll));
  const tFall = V + roll * .8;
  E.EVENTS.push({ t: tFall + .55, kind: 'drop', e: 1, x: o.x, z: o.z });
  E.updates.push(t => {
    const s = along(t), wob = t > V ? Math.sin((t - V) * 7) * .08 * smooth(V, V + 1, t) : 0, fall = smooth(tFall, tFall + .6, t);
    if (ax === 'z') g.position.set(o.x + wob * .3, 0, s); else g.position.set(s, 0, o.z + wob * .3);
    g.rotation.set(0, ax === 'z' ? (dir > 0 ? 0 : Math.PI) : (dir > 0 ? Math.PI / 2 : -Math.PI / 2), 0);
    frame.rotation.z = fallSide * (wob + fall * 1.45 + (t > tFall + .6 ? Math.abs(Math.sin((t - tFall - .6) * 12)) * .04 * Math.exp(-(t - tFall - .6) * 5) : 0));
    frame.position.y = -fall * .02;
    const spinA = (along(t) - p0) * dir / .33; wheels.forEach(w => { w.rotation.x = spinA; });
  });
  // the rider (a person pedalling) until the click
  {
    person(E, 4000 + i, { y: .45, path(t) { const s = along(t);
      return ax === 'z' ? { x: o.x, z: s - dir * .05, rot: dir > 0 ? 0 : Math.PI, moving: 1, speed: 1.1, stoop: .35, visible: t < V } : { x: s, z: o.z, rot: dir > 0 ? Math.PI / 2 : -Math.PI / 2, moving: 1, speed: 1.1, stoop: .35, visible: t < V }; } });
  }
}
