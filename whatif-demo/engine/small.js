// KLEINE DINGEN (baksteen): the small things that tell a big story. Works with any place.
//   beats.vanish: t                 every person disappears in one click (drivers too); some drop a bag or phone
//   TL.traffic = [{ x, z, dir, v, axis, coast }]   cars in a lane ('z': x fixed; z = where the car is at beats.vanish);
//                                   from beats.vanish on nobody drives: they roll on and coast to a stop (no brake lights)
//   TL.bikes = [{ x, z, dir, v, axis, fall: [dx, dz] }]   a cyclist (z/x = where at vanish); without rider the bike rolls on, wobbles, falls
//   TL.crashes = [{ at, point: [x, z], cars: [{ dir: [dx, dz], v, off }], smoke: 1, alarm: 20 }]
//                                   driverless cars drift (off = metres beside the line at vanish) and meet at `point` at `at`:
//                                   bang, slide, hazard lights, smoke from the bonnet, a car alarm for `alarm` s
//   TL.smoke = [[t, x, y, z, size]]   a smoke column from t on
//   TL.metro = [{ x, z, ry, water: [t0, t1] }]   a metro entrance: stairs down into the ground, water pouring down them
//   TL.extraShots = { name: shot }  shots of the scenario itself (POV walks etc.)
//   Sounds (make_audio.py): events 'click', 'drop', 'crash', 'alarm' { dur }, 'buzz' { dur }; TL.audio.quiet = t (city hush)
import * as THREE from 'three';
import { rng, hash, smooth, clamp, lerp } from './util.js';
import { car, person } from './props.js';

export function applySmall(E, TL, F, P) {
  const B = TL.beats, V = B.vanish ?? 1e9;
  Object.assign(P.shots, TL.extraShots || {});
  if (B.vanish > 0) E.EVENTS.push({ t: V, kind: 'click', e: 1 });   // vanish: 0 = nobody there from the start (later chapters)

  // ---------- things people drop when they vanish ----------
  if (B.vanish > 0) {
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

  for (const M of TL.metro || []) metro(E, TL, M);

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

// metro entrance: railings + a sign on the pavement, stairs going down (seen through a 'hole' in the ground:
// the stairs draw first, an invisible lid writes depth so the street surface skips the opening), water running down
function metro(E, TL, M) {
  const { lam, shadowed } = E, g = new THREE.Group(); g.position.set(M.x, 0, M.z); g.rotation.y = M.ry ?? 0; E.scene.add(g);
  const W = 3.2, L = 7, D = 4.2, steps = 16, stone = lam(0x8d8a84), dark = lam(0x2a2c30), under = [];
  const add = (m, o = -3) => { m.renderOrder = o; g.add(m); under.push(m); return m; };
  for (let i = 0; i < steps; i++) { const st = add(new THREE.Mesh(new THREE.BoxGeometry(W, D / steps, L / steps), stone)); st.position.set(0, -(i + .5) * D / steps, -L / 2 + (i + .5) * L / steps); }
  for (const sx of [-1, 1]) { const w = add(new THREE.Mesh(new THREE.BoxGeometry(.2, D + .5, L + 3), lam(0xb9b4aa))); w.position.set(sx * (W / 2 + .1), -D / 2, .6); }
  const back = add(new THREE.Mesh(new THREE.BoxGeometry(W, D, .2), dark)); back.position.set(0, -D / 2 - .4, L / 2 + 2);
  const roof = add(new THREE.Mesh(new THREE.BoxGeometry(W + .4, .2, 3), lam(0x6b6862))); roof.position.set(0, -D * .45, L / 2 + .8);
  const floor = add(new THREE.Mesh(new THREE.BoxGeometry(W, .2, 3), dark)); floor.position.set(0, -D - .1, L / 2 + .9);
  const lid = new THREE.Mesh(new THREE.PlaneGeometry(W, L), new THREE.MeshBasicMaterial({ colorWrite: false })); lid.rotation.x = -Math.PI / 2; lid.position.y = .025; lid.renderOrder = -2; g.add(lid);
  for (const m of under) m.renderOrder = -3;
  // railings and the sign
  const rail = lam(0x3c4a3f);
  for (const sx of [-1, 1]) { const r = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.06, .06, L), rail)); r.position.set(sx * (W / 2 + .05), 1.0, 0); g.add(r);
    for (let k = 0; k <= 4; k++) { const p = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.05, 1, .05), rail)); p.position.set(sx * (W / 2 + .05), .5, -L / 2 + k * L / 4); g.add(p); } }
  { const r = shadowed(new THREE.Mesh(new THREE.BoxGeometry(W + .1, .06, .06), rail)); r.position.set(0, 1.0, -L / 2); g.add(r); }
  const post = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, 3, 6), rail)); post.position.set(W / 2 + .5, 1.5, -L / 2 - .3); g.add(post);
  const sg = new THREE.Mesh(new THREE.BoxGeometry(.8, .8, .12), lam(0x2d5aa0)); sg.position.set(W / 2 + .5, 3.1, -L / 2 - .3); g.add(sg);
  const cv = document.createElement('canvas'); cv.width = cv.height = 64; const x = cv.getContext('2d'); x.fillStyle = '#fff'; x.font = 'bold 50px sans-serif'; x.textAlign = 'center'; x.fillText('M', 32, 50);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  for (const sd of [-1, 1]) { const f = new THREE.Mesh(new THREE.PlaneGeometry(.7, .7), new THREE.MeshBasicMaterial({ map: tex, transparent: true })); f.position.set(W / 2 + .5, 3.1, -L / 2 - .3 + sd * .065); if (sd < 0) f.rotation.y = Math.PI; g.add(f); }
  const lampM = new THREE.MeshBasicMaterial({ color: 0x777777 }); const bulb = new THREE.Mesh(new THREE.SphereGeometry(.12, 8, 6), lampM); bulb.position.set(0, -D * .45 - .15, L / 2 + .8); bulb.renderOrder = -3; g.add(bulb);
  // water: a sheet over the steps with streaks that run down, a pool at the bottom, splashes
  const wcv = document.createElement('canvas'); wcv.width = 64; wcv.height = 256; const wx = wcv.getContext('2d');
  wx.fillStyle = 'rgba(120,150,165,.55)'; wx.fillRect(0, 0, 64, 256); const R = rng(9);
  for (let i = 0; i < 60; i++) { wx.fillStyle = `rgba(225,238,242,${.25 + R() * .45})`; wx.fillRect(R() * 64, R() * 256, 1 + R() * 3, 10 + R() * 40); }
  const wt = new THREE.CanvasTexture(wcv); wt.wrapS = wt.wrapT = THREE.RepeatWrapping; wt.repeat.set(2, 2);
  const wm = new THREE.MeshBasicMaterial({ map: wt, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide });
  const sheet = new THREE.Mesh(new THREE.PlaneGeometry(W - .2, Math.hypot(L, D)), wm); sheet.renderOrder = -1;
  sheet.position.set(0, -D / 2 + .08, 0); sheet.rotation.x = -Math.PI / 2 - Math.atan2(D, L); g.add(sheet);
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(W, 3), new THREE.MeshBasicMaterial({ color: 0x3e5560, transparent: true, opacity: 0 })); pool.rotation.x = -Math.PI / 2; pool.position.set(0, -D + .15, L / 2 + .9); pool.renderOrder = -1; g.add(pool);
  const [w0, w1] = M.water || [1e9, 1e9];
  E.updates.push((t, F, tv) => { const k = smooth(w0, w0 + 1.5, t) * (1 - smooth(w1, w1 + 1, t)); wm.opacity = k * .8; wt.offset.y = (tv ?? t) * 1.6; pool.material.opacity = k * .85;
    lampM.color.setHex(E.powerOut?.(t) || (TL.beats.powerOff && t > TL.beats.powerOff[1]) ? 0x333333 : 0xfff0c8); });
  const wp = new THREE.Vector3();
  E.emitters.push((tv, addP) => { const k = smooth(w0, w0 + 1.5, tv) * (1 - smooth(w1, w1 + 1, tv)); if (k <= 0) return;
    for (let i = 0; i < 26; i++) { const a = (tv * 1.3 + hash(i, 1)) % 1;
      wp.set((hash(i, 2) - .5) * (W - .4), -D + .3 + a * .6, L / 2 + .2 + hash(i, 3)).applyAxisAngle(new THREE.Vector3(0, 1, 0), M.ry ?? 0).add(g.position);
      addP(wp.x, wp.y, wp.z, .35 + a * .4, .3 * k * (1 - a), .85, .9, .93, 100 + hash(i, 4) * 6); } });
  if (M.water) E.EVENTS.push({ t: w0, kind: 'water', dur: w1 - w0, e: 1, x: M.x, z: M.z });
}
