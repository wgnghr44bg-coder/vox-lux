// ARMY (baksteen "Leger", okt 2026): tanks, army trucks, helicopters, soldiers and concrete road barriers. Any place.
// Nobody fights: vehicles drive in and park, soldiers stand guard and look up (beats.lookUp). No weapons are drawn.
// TL.army = {
//   vehicles: [{ kind: 'truck' | 'tank' | 'jeep', keys: [[t, x, z], ...], ry }]   drives along the keys, faces where it goes
//   helis:    [{ keys: [[t, x, y, z], ...], ry }]                                   flies; or orbit: { c: [x, y, z], r, period, t0 }
//   soldiers: [{ at: [x, z], n, face, spread, line: true }]                           a squad (line: in a row along x)
//   barriers: [{ at: [x, z], ry, n }]                                                 concrete blocks in a row
//   roadblocks: [{ at: [x, z], ry, on }]                                              striped barriers with blinking lamps (props-alarm.js)
// }
// Sound: TL.audio.heli = [[a, b]] (rotor thump), TL.audio.engines = [[a, b]] (diesel rumble), see make_audio.py.
import * as THREE from 'three';
import { rng, smooth, lerp } from './util.js';
import { person } from './props.js';
import { roadblock } from './props-alarm.js';

const OLIVE = 0x4f5a3c, OLIVE_D = 0x3c452e, TRACK = 0x2b2b29, CANVAS = 0x5d6447;

function track(keys) {          // eased path through [t, ...v] keys -> { p(t), heading(t) }
  const at = t => {
    if (t <= keys[0][0]) return keys[0].slice(1);
    for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
      const a = keys[i - 1], b = keys[i], u = (t - a[0]) / (b[0] - a[0] || 1), e = u * u * (3 - 2 * u);
      return a.slice(1).map((v, k) => lerp(v, b[k + 1], e));
    }
    return keys[keys.length - 1].slice(1);
  };
  return at;
}

function wheels(E, g, xs, z, r, w = .35) {
  const geo = new THREE.CylinderGeometry(r, r, w, 10); geo.rotateZ(Math.PI / 2);
  for (const x of xs) for (const s of [-1, 1]) { const m = E.shadowed(new THREE.Mesh(geo, E.lam(0x1d1d1c))); m.position.set(s * z, r, x); g.add(m); }
}

function truck(E) {
  const g = new THREE.Group(), L = E.lam, S = E.shadowed;
  const chassis = S(new THREE.Mesh(new THREE.BoxGeometry(2.4, .5, 7.6), L(OLIVE_D))); chassis.position.set(0, 1.0, 0); g.add(chassis);
  const cab = S(new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.5, 1.9), L(OLIVE))); cab.position.set(0, 1.95, 2.75); g.add(cab);
  const glass = new THREE.Mesh(new THREE.BoxGeometry(2.1, .6, .05), L(0x2a3036)); glass.position.set(0, 2.3, 3.71); g.add(glass);
  const bed = S(new THREE.Mesh(new THREE.BoxGeometry(2.45, .7, 5.2), L(OLIVE))); bed.position.set(0, 1.6, -1.15); g.add(bed);
  const cover = S(new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 5.2, 10, 1, false, -Math.PI / 2, Math.PI), L(CANVAS))); cover.rotation.x = Math.PI / 2; cover.scale.set(1, 1, .75); cover.position.set(0, 1.95, -1.15); g.add(cover);
  wheels(E, g, [2.6, -.9, -2.6], 1.15, .55);
  return g;
}
function jeep(E) {
  const g = new THREE.Group(), L = E.lam, S = E.shadowed;
  const body = S(new THREE.Mesh(new THREE.BoxGeometry(2.0, .9, 4.4), L(OLIVE))); body.position.y = 1.0; g.add(body);
  const top = S(new THREE.Mesh(new THREE.BoxGeometry(1.9, .7, 2.2), L(OLIVE_D))); top.position.set(0, 1.8, -.4); g.add(top);
  wheels(E, g, [1.4, -1.4], 1.0, .45, .3);
  return g;
}
function tank(E) {
  const g = new THREE.Group(), L = E.lam, S = E.shadowed;
  for (const s of [-1, 1]) {      // tracks with road wheels
    const tr = S(new THREE.Mesh(new THREE.BoxGeometry(.7, 1.0, 7.2), L(TRACK))); tr.position.set(s * 1.55, .55, 0); g.add(tr);
    for (let i = 0; i < 6; i++) { const w = new THREE.Mesh(new THREE.CylinderGeometry(.36, .36, .1, 10), L(0x3a3a36)); w.rotation.z = Math.PI / 2; w.position.set(s * 1.92, .45, -2.6 + i * 1.04); g.add(w); }
    const skirt = S(new THREE.Mesh(new THREE.BoxGeometry(.12, .45, 7.0), L(OLIVE))); skirt.position.set(s * 1.92, 1.0, 0); g.add(skirt);
  }
  const hull = S(new THREE.Mesh(new THREE.BoxGeometry(3.3, .8, 6.8), L(OLIVE))); hull.position.y = 1.35; g.add(hull);
  const glacis = S(new THREE.Mesh(new THREE.BoxGeometry(3.3, .2, 1.4), L(OLIVE))); glacis.position.set(0, 1.55, 3.5); glacis.rotation.x = -.35; g.add(glacis);
  const turret = new THREE.Group(); turret.position.set(0, 1.75, -.4); g.add(turret);
  const tb = S(new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.45, .75, 8), L(OLIVE_D))); tb.position.y = .38; turret.add(tb);
  const mant = S(new THREE.Mesh(new THREE.BoxGeometry(.8, .5, .6), L(OLIVE_D))); mant.position.set(0, .42, 1.4); turret.add(mant);
  const barrel = S(new THREE.Mesh(new THREE.CylinderGeometry(.11, .14, 4.6, 8), L(OLIVE_D))); barrel.rotation.x = Math.PI / 2 - .05; barrel.position.set(0, .48, 3.9); turret.add(barrel);
  const hatch = new THREE.Mesh(new THREE.CylinderGeometry(.35, .35, .12, 8), L(OLIVE)); hatch.position.set(-.4, .82, -.3); turret.add(hatch);
  g.userData.turret = turret;
  return g;
}

function helicopter(E) {
  const g = new THREE.Group(), L = E.lam, S = E.shadowed;
  const body = S(new THREE.Mesh(new THREE.SphereGeometry(1.4, 10, 8), L(OLIVE))); body.scale.set(1, .9, 2.0); g.add(body);
  const glass = new THREE.Mesh(new THREE.SphereGeometry(1.0, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2), L(0x26303a)); glass.rotation.x = Math.PI / 2 + .5; glass.position.set(0, .15, 2.0); glass.scale.set(1, 1, .8); g.add(glass);
  const boom = S(new THREE.Mesh(new THREE.CylinderGeometry(.18, .38, 6, 8), L(OLIVE))); boom.rotation.x = Math.PI / 2; boom.position.set(0, .35, -4.6); g.add(boom);
  const fin = S(new THREE.Mesh(new THREE.BoxGeometry(.12, 1.5, .9), L(OLIVE_D))); fin.position.set(0, 1.0, -7.4); g.add(fin);
  const mast = new THREE.Mesh(new THREE.CylinderGeometry(.12, .12, .6, 6), L(0x2a2a28)); mast.position.y = 1.5; g.add(mast);
  for (const s of [-1, 1]) { const sk = new THREE.Mesh(new THREE.BoxGeometry(.1, .1, 3.6), L(0x2a2a28)); sk.position.set(s * .9, -1.45, .2); g.add(sk);
    for (const z of [-.8, 1.1]) { const st = new THREE.Mesh(new THREE.BoxGeometry(.08, .5, .08), L(0x2a2a28)); st.position.set(s * .8, -1.2, z); g.add(st); } }
  // rotor: a faint disc (motion blur) plus slowly turning blades, so it never strobes at 30 fps
  const rotor = new THREE.Group(); rotor.position.y = 1.85; g.add(rotor);
  for (let i = 0; i < 4; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(.32, .05, 6.4), L(0x222220)); b.position.z = 3.2; const p = new THREE.Group(); p.rotation.y = i * Math.PI / 2; p.add(b); rotor.add(p); }
  const disc = new THREE.Mesh(new THREE.CircleGeometry(6.6, 32), new THREE.MeshBasicMaterial({ color: 0x2a2a28, transparent: true, opacity: .16, depthWrite: false, side: THREE.DoubleSide }));
  disc.rotation.x = -Math.PI / 2; rotor.add(disc);
  const tail = new THREE.Mesh(new THREE.BoxGeometry(.05, 1.6, .16), L(0x222220)); tail.position.set(.2, 1.0, -7.4); g.add(tail);
  g.userData.rotor = rotor; g.userData.tail = tail;
  return g;
}

// soldier: a person in olive with a helmet and a vest
export function soldier(E, seed, path, o = {}) {
  return person(E, seed, { y: o.y ?? .2, coat: o.coat ?? [OLIVE, 0x55603f, 0x4a5538][seed % 3], pants: OLIVE_D, shoe: 0x1c1b18, skirt: false, react: o.react ?? 'shade',
    dress: ({ E, headG, hair, upper }) => {
      hair.visible = false; headG.children.forEach(c => { if (c !== hair && (c.geometry?.type === 'BoxGeometry' && c.position.y < 0 || c.position.z < -.05)) c.visible = false; });
      const helmet = E.shadowed(new THREE.Mesh(new THREE.SphereGeometry(.135, 10, 6, 0, Math.PI * 2, 0, Math.PI * .5), E.lam(0x48523a))); helmet.position.y = .03; headG.add(helmet);
      const brim = new THREE.Mesh(new THREE.CylinderGeometry(.15, .15, .02, 10), E.lam(0x48523a)); brim.position.y = .03; headG.add(brim);
      const vest = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(.4, .36, .3), E.lam(0x3b4330))); vest.position.y = .36; upper.add(vest);
    }, path });
}

export function createArmy(E, TL) {
  const A = TL.army; if (!A) return;
  const B = TL.beats, gy = (x, z) => (E.groundAt ? E.groundAt(x, z) : 0);
  for (const [i, v] of (A.vehicles || []).entries()) {
    const g = { truck, tank, jeep }[v.kind || 'truck'](E); E.scene.add(g);
    const at = track(v.keys); let head = v.ry ?? 0;
    E.updates.push((t, F, tv) => {
      const p = at(tv), q = at(tv + .25), dx = q[0] - p[0], dz = q[1] - p[1];
      if (Math.hypot(dx, dz) > .02) head = Math.atan2(dx, dz);
      const moving = Math.hypot(dx, dz) > .02;
      g.position.set(p[0], gy(p[0], p[1]) + (moving ? Math.sin(tv * 9 + i) * .02 : 0), p[1]); g.rotation.y = head;
      if (g.userData.turret && v.aim != null) g.userData.turret.rotation.y = smooth(v.aim[0], v.aim[0] + 3, tv) * v.aim[1];   // turret slowly turns (never fires)
    });
  }
  for (const [i, h] of (A.helis || []).entries()) {
    const g = helicopter(E); E.scene.add(g);
    const O = h.orbit, at = O ? (t => { const a = (t - (O.t0 ?? 0)) / O.period * Math.PI * 2 * (O.dir ?? 1) + (O.ph ?? 0); return [O.c[0] + Math.cos(a) * O.r, O.c[1] + Math.sin(t * .4 + i) * 1.5, O.c[2] + Math.sin(a) * O.r]; }) : track(h.keys);
    E.updates.push((t, F, tv) => {
      const p = at(tv), q = at(tv + .3), dx = q[0] - p[0], dz = q[2] - p[2], sp = Math.hypot(dx, dz) / .3;
      g.position.set(p[0], p[1], p[2]); g.rotation.order = 'YXZ';
      g.rotation.y = sp > .5 ? Math.atan2(dx, dz) : (h.ry ?? 0); g.rotation.x = Math.min(.18, sp * .006);
      g.rotation.z = O ? -.12 * (O.dir ?? 1) : 0;
      g.userData.rotor.rotation.y = tv * 3.1; g.userData.tail.rotation.x = tv * 9;
    });
  }
  for (const [si, s] of (A.soldiers || []).entries()) {
    const R = rng(4000 + si), n = s.n ?? 6, sp = s.spread ?? 1.6;
    for (let k = 0; k < n; k++) {
      const off = (k - (n - 1) / 2) * sp, jit = (R() - .5) * .3;     // line: true = a row along x, 'z' = along z
      const x = s.at[0] + (s.line === 'z' ? jit : s.line ? off : (R() - .5) * sp * 2), z = s.at[1] + (s.line === 'z' ? off : s.line ? jit : (R() - .5) * sp * 2);
      const look = (B.lookUp ?? 1e9) + R() * 1.5, face = (s.face ?? 0) + (s.line ? 0 : (R() - .5) * 1.2);
      soldier(E, 300 + si * 40 + k, t => ({ x, z, rot: face + Math.sin(t * .3 + k) * .05, moving: 0, speed: 0, headUp: smooth(look, look + 1.5, t) * (s.headUp ?? .55), stoop: 0 }), { y: gy(x, z) + .02 });
    }
  }
  for (const r of A.roadblocks || []) roadblock(E, TL, r.at[0], r.at[1], { on: r.on ?? 0, appear: -1, ry: r.ry ?? 0 });
  for (const b of A.barriers || []) {
    const n = b.n ?? 4, c = Math.cos(b.ry ?? 0), s = Math.sin(b.ry ?? 0);
    for (let k = 0; k < n; k++) {
      const off = (k - (n - 1) / 2) * 2.1, x = b.at[0] + c * off, z = b.at[1] - s * off;
      const m = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(2, .85, .6), E.lam(0xb9b4a8))); m.position.set(x, gy(x, z) + .43, z); m.rotation.y = b.ry ?? 0; E.scene.add(m);
      const foot = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(2, .2, .9), E.lam(0xaaa598))); foot.position.set(x, gy(x, z) + .1, z); foot.rotation.y = b.ry ?? 0; E.scene.add(foot);
    }
  }
}
