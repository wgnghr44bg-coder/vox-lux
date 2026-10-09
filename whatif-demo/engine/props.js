// Reusable low-poly props. Each prop registers what it can do:
//   E.bend    -> pose(t, F): bends sideways with F.lateral(t) or sags with F.droop(t)
//   E.breaks  -> pieces that come off; strength per force kind ({ wind: .3, gravity: .8 }), missing = never
//   E.lights  -> lamps/windows that light up in the dark
import * as THREE from 'three';
import { rng, hash, smooth, noise, clamp } from './util.js';

const FROND = (() => {
  const L = 3.6, pos = [], rows = 6;
  const row = j => { const u = j / rows, w = 0.75 * (1 - u * .85), z = u * L, y = -1.3 * u * u; return [[-w, y - .08, z], [0, y + .1, z], [w, y - .08, z]]; };
  for (let j = 0; j < rows; j++) { const a = row(j), b = row(j + 1);
    for (const [i0, i1] of [[0, 1], [1, 2]]) pos.push(...a[i0], ...b[i0], ...b[i1], ...a[i0], ...b[i1], ...a[i1]); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.computeVertexNormals(); return g;
})();

// lean a group by (a, dir) where dir is a horizontal unit vector [dx, dz]
function lean(obj, a, dx, dz) { obj.rotation.x = a * dz; obj.rotation.z = -a * dx; }

export function palm(E, x, z, hgt, seed, o = {}) {
  const { lam, shadowed } = E, R = rng(seed), g = new THREE.Group(); g.position.set(x, o.y ?? .2, z); E.scene.add(g);
  const N = 6, segL = hgt / N, segs = []; let parent = g; const tmat = lam(0x7a6852);
  for (let i = 0; i < N; i++) {
    const s = new THREE.Group(); s.position.y = i === 0 ? 0 : segL; parent.add(s);
    const c = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.2 - i * .012, .24 - i * .012, segL, 6), tmat)); c.position.y = segL / 2; s.add(c);
    segs.push(s); parent = s;
  }
  const crown = new THREE.Group(); crown.position.y = segL; parent.add(crown);
  const fronds = [];
  for (let k = 0; k < 9; k++) {
    const pivot = new THREE.Group(); pivot.rotation.y = k / 9 * Math.PI * 2 + R() * .3; crown.add(pivot);
    const m = shadowed(new THREE.Mesh(FROND, lam(R() < .5 ? 0x4e6a3a : 0x5b7341, { side: THREE.DoubleSide })));
    m.rotation.x = -0.25 - R() * .3; m.userData.rx = m.rotation.x; pivot.add(m); fronds.push({ pivot, m, ph: R() * 6 });
    if (R() < .8) E.breaks.push({ src: m, strength: { wind: .6 + R() * .8, gravity: 1.6 + R() }, k: .16, lift: .5, mu: .5, spin: 2.5, hx: .7, hy: .3, hz: 1.8 });
  }
  const ph = R() * 6, stiff = .8 + R() * .4;
  g.userData.frondMats = fronds.map(f => f.m.material); g.userData.crown = hgt; g.userData.fronds = fronds.map(f => f.m);
  E.bend.push({ pose(t, F) {
    const L = F.lateral(t), d = F.droop(t);
    const bend = Math.min(1.05, Math.pow(L.a, 1.15) * .85) / stiff;
    const sway = (0.025 + L.a * .15) * Math.sin(t * (1.1 + L.a * 2.5) + ph) + 0.02 * noise(t, ph);
    segs.forEach((s, i) => { const a = (bend + sway) / N * (0.6 + i * .15); lean(s, a, L.dx, L.dz); s.rotation.x += d * .05 * Math.sin(ph + i); });
    const stream = smooth(.05, .65, L.a);
    fronds.forEach(f => { f.m.rotation.z = Math.sin(t * (2 + L.a * 10) + f.ph) * (0.04 + stream * .12); f.m.rotation.x = f.m.userData.rx - d * .55; });
    crown.rotation.x = stream * .5 * L.dz; crown.rotation.z = -stream * .5 * L.dx;
  } });
  return g;
}

export function coneTree(E, x, z, s, seed, o = {}) {
  const { lam, shadowed } = E, g = new THREE.Group(); g.position.set(x, o.y ?? .2, z); E.scene.add(g);
  const piv = new THREE.Group(); g.add(piv);
  const tr = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.15, .2, 1.6, 5), lam(0x5a4636))); tr.position.y = .8; piv.add(tr);
  const m = lam(o.color ?? 0x3f5634), tiers = [];
  for (let k = 0; k < 3; k++) { const c = shadowed(new THREE.Mesh(new THREE.ConeGeometry(1.5 - k * .35, 2.2, 7), m)); c.position.y = 2 + k * 1.1; piv.add(c); tiers.push(c); }
  if (o.snow) for (const c of tiers) { const sn = new THREE.Mesh(new THREE.ConeGeometry(.75, .9, 7), lam(0xeef2f5)); sn.position.y = .7; c.add(sn); E.melt.push({ mesh: sn, to: 0 }); }
  E.frost.push(m);
  g.scale.setScalar(s); const ph = hash(seed, 3) * 6;
  E.bend.push({ pose(t, F) { const L = F.lateral(t), d = F.droop(t);
    lean(piv, Math.min(.8, Math.pow(L.a, 1.3) * .6) + (.02 + L.a * .13) * Math.sin(t * (1.5 + L.a * 3.3) + ph), L.dx, L.dz);
    tiers.forEach((c, k) => { c.scale.set(1 + d * .12, 1 - d * .18, 1 + d * .12); c.position.y = (2 + k * 1.1) * (1 - d * .1); }); } });
  if (hash(seed, 65) < .7) E.breaks.push({ src: g, strength: { wind: 1.2 + hash(seed, 66) * .6 }, k: .025, lift: .3, mu: .7, spin: .8, hx: 1.2, hy: 2.5, hz: 1.2, heavy: 1, keepScale: true });
  return g;
}

// broad deciduous tree: trunk + two branches + clumps of leaves (the branches can snap)
export function roundTree(E, x, z, s, seed, o = {}) {
  const { lam, shadowed } = E, R = rng(seed), g = new THREE.Group(); g.position.set(x, o.y ?? .2, z); g.scale.setScalar(s); E.scene.add(g);
  const piv = new THREE.Group(); g.add(piv);
  const bark = lam(0x5b4a3a), leaf = lam(o.color ?? [0x56703f, 0x617a43, 0x4d653a][Math.floor(R() * 3)]);
  E.frost.push(leaf); E.leaves.push(leaf);
  const tr = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.22, .32, 3.2, 6), bark)); tr.position.y = 1.6; piv.add(tr);
  const top = shadowed(new THREE.Mesh(new THREE.IcosahedronGeometry(1.9, 0), leaf)); top.position.y = 4.4; top.scale.set(1, .85, 1); piv.add(top);
  const branches = [];
  for (const sd of [-1, 1]) {
    const b = new THREE.Group(); b.position.set(0, 2.6, 0); b.rotation.z = sd * (.9 + R() * .2); b.rotation.y = R() * 6; piv.add(b);
    const st = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.08, .14, 1.8, 5), bark)); st.position.y = .9; b.add(st);
    const cl = shadowed(new THREE.Mesh(new THREE.IcosahedronGeometry(1.15, 0), leaf)); cl.position.y = 1.9; b.add(cl);
    branches.push({ b, z0: b.rotation.z, sd });
    E.breaks.push({ src: b, strength: { wind: .5 + R() * .3, gravity: .45 + R() * .4 }, k: .04, lift: .2, mu: .7, spin: .8, hx: .9, hy: .9, hz: .9, heavy: 0, keepScale: true });
  }
  const ph = R() * 6;
  E.bend.push({ pose(t, F) { const L = F.lateral(t), d = F.droop(t);
    lean(piv, Math.min(.6, Math.pow(L.a, 1.3) * .45) + (.015 + L.a * .1) * Math.sin(t * (1.3 + L.a * 3) + ph), L.dx, L.dz);
    branches.forEach(br => { br.b.rotation.z = br.z0 + br.sd * d * .5; });
    top.scale.set(1 + d * .1, .85 - d * .2, 1 + d * .1); top.position.y = 4.4 - d * .5; } });
  return g;
}

export function lamp(E, x, z, s, o = {}) {
  const { lam, shadowed } = E, g = new THREE.Group(); g.position.set(x, o.y ?? .2, z); E.scene.add(g);
  const mpole = lam(0x4a4d50);
  const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.09, .12, 8, 6), mpole)); pole.position.y = 4; g.add(pole);
  const top = new THREE.Group(); top.position.y = 7.9; g.add(top);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(1.8, .1, .1), mpole); arm.position.set(-s * .8, 0, 0); top.add(arm);
  const head = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.8, .2, .35), lam(0x5d6063))); head.position.set(-s * 1.6, -.1, 0); top.add(head);
  const bulb = new THREE.Mesh(new THREE.BoxGeometry(.6, .05, .25), new THREE.MeshBasicMaterial({ color: 0x3a3a36 })); bulb.position.y = -.12; head.add(bulb);
  E.lights.push({ mat: bulb.material, off: 0x3a3a36, on: 0xffd9a0, at: hash(x * 3 + z, 4) * .1 });
  const ph = hash(x + z * 7, 9) * 6;
  E.bend.push({ pose(t, F) { const L = F.lateral(t), d = F.droop(t);
    lean(g, smooth(.7, 1.3, L.a) * .55 + (L.a * .04) * Math.sin(t * 9 + ph), L.dx, L.dz);
    top.rotation.z = s * d * .35; g.rotation.x += (o.lean ?? 0) * d; } });
  E.breaks.push({ src: head, strength: { wind: 1.05 + hash(x, z) * .38, gravity: 1.3 }, k: .04, lift: .3, mu: .5, spin: 1.5, hx: .4, hy: .1, hz: .2, heavy: 1 });
  return g;
}

export function sign(E, x, z, col, w = 1.4, h = .8, y = 3) {
  const { lam, shadowed } = E, g = new THREE.Group(); g.position.set(x, .2, z); E.scene.add(g);
  const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.05, .05, y, 5), lam(0x8a8d90))); pole.position.y = y / 2; g.add(pole);
  const pan = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, .05), lam(col))); pan.position.y = y; g.add(pan);
  const bar = new THREE.Mesh(new THREE.PlaneGeometry(w * .7, h * .14), new THREE.MeshBasicMaterial({ color: 0xe6e2d8 })); bar.position.set(0, 0, .03); pan.add(bar);
  const ph = hash(x * 13 + z, 21) * 6;
  E.bend.push({ pose(t, F) { const L = F.lateral(t), d = F.droop(t), a = smooth(.1, .62, L.a);
    pan.rotation.x = a * .35 + a * .25 * Math.sin(t * (6 + L.a * 13) + ph); pan.rotation.y = a * .15 * Math.sin(t * 11 + ph);
    lean(g, smooth(.5, 1.25, L.a) * .5 + d * .08 * Math.sin(ph), L.dx || 0, L.dz || 1); } });
  E.breaks.push({ src: pan, strength: { wind: .62 + hash(x, z) * .28, gravity: 1.5 }, k: .09, lift: .45, mu: .5, spin: 2, hx: .7, hy: .4, hz: .05 });
  return g;
}

export function bench(E, x, z, ry = 0) {
  const { lam, shadowed } = E, g = new THREE.Group(), c = lam(0x6e5a44), m = lam(0x3d3f42);
  const seat = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.8, .08, .5), c)); seat.position.y = .45; g.add(seat);
  const back = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.8, .4, .06), c)); back.position.set(0, .75, -.24); g.add(back);
  for (const sx of [-.8, .8]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.06, .45, .45), m); l.position.set(sx, .22, 0); g.add(l); }
  g.position.set(x, .2, z); g.rotation.y = ry; E.scene.add(g); return g;
}

// a walking person; behaviour comes from the place: (t) => { x, z, rot, moving, speed, visible, headUp, stoop }
const SHIRTS = [0x8a6b4e, 0x5e6f80, 0xb9ae96, 0x7b4a42, 0x56624a, 0xd2cbb8, 0x3d4650, 0x9a8a5c];
// People (eigenaar, okt 2026: "mensen dichtbij"): hips, torso, shoulders, two arms with elbows and hands, a head
// with hair (short, long, bun or ponytail) and eyes, trousers or a skirt, shoes. Skin, hair and clothes vary per person.
// path(t) may also return arms: 'point' | 'shade' | 'head' | 'down' to override the reaction pose.
const SKIN = [0xf1c9a5, 0xe3b08c, 0xc98d66, 0xa06a48, 0x75492f];
const HAIR = [0x2a1d14, 0x4a3020, 0x7a5530, 0xc9a46a, 0x1c1c1c, 0x8d8a86, 0x9a4a2a];
const PANTS = [0x2f3236, 0x3e4a5c, 0x5b4a3a, 0x6b6f74, 0x2b3a4a, 0x8a7d63, 0x46543f];
const TOPS = [...SHIRTS, 0xb8503e, 0x3f6f9a, 0xd9b04a, 0x6b8f5a, 0xe8e2d4, 0x7a3e5c, 0x2f6b6b];
export function person(E, seed, o = {}) {
  const { lam, shadowed } = E, R = rng(seed), g = new THREE.Group(); E.scene.add(g); g.rotation.order = 'YXZ';
  const pick = a => a[Math.floor(R() * a.length)], M = c => lam(c), S = m => shadowed(m);
  const skin = M(pick(SKIN)), hairC = M(pick(HAIR)), top = M(o.coat ?? pick(TOPS)), pants = M(pick(PANTS)), shoe = M(0x24221f);
  const skirt = R() < .3, hairType = pick(['short', 'short', 'long', 'bun', 'tail', 'short']), big = .92 + R() * .16;
  g.scale.setScalar(big);
  const upper = new THREE.Group(); upper.position.y = .82; g.add(upper);
  const hips = S(new THREE.Mesh(new THREE.BoxGeometry(.34, .16, .2), skirt ? top : pants)); hips.position.y = .04; upper.add(hips);
  const torso = S(new THREE.Mesh(new THREE.CylinderGeometry(.18, .15, .5, 8), top)); torso.position.y = .34; upper.add(torso);
  const sh = S(new THREE.Mesh(new THREE.BoxGeometry(.44, .11, .22), top)); sh.position.y = .58; upper.add(sh);
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(.05, .055, .08, 6), skin); neck.position.y = .67; upper.add(neck);
  const headG = new THREE.Group(); headG.position.y = .79; upper.add(headG);
  const head = S(new THREE.Mesh(new THREE.SphereGeometry(.112, 10, 8), skin)); head.scale.set(1, 1.12, 1.02); headG.add(head);
  const hair = S(new THREE.Mesh(new THREE.SphereGeometry(.122, 10, 6, 0, Math.PI * 2, 0, Math.PI * .55), hairC)); hair.position.y = .02; hair.rotation.x = -.25; headG.add(hair);
  if (hairType === 'long') { const l = S(new THREE.Mesh(new THREE.BoxGeometry(.22, .26, .07), hairC)); l.position.set(0, -.1, -.08); headG.add(l); }
  if (hairType === 'bun') { const b2 = S(new THREE.Mesh(new THREE.SphereGeometry(.06, 8, 6), hairC)); b2.position.set(0, .09, -.1); headG.add(b2); }
  if (hairType === 'tail') { const t2 = S(new THREE.Mesh(new THREE.BoxGeometry(.05, .2, .05), hairC)); t2.position.set(0, -.04, -.13); t2.rotation.x = .3; headG.add(t2); }
  const eyeM = new THREE.MeshBasicMaterial({ color: 0x1b1a19 });
  [-1, 1].forEach(sx => { const e = new THREE.Mesh(new THREE.BoxGeometry(.022, .022, .01), eyeM); e.position.set(sx * .04, .015, .108); headG.add(e); });
  if (o.hat) { const h = S(new THREE.Mesh(new THREE.ConeGeometry(.15, .18, 8), M(o.hat))); h.position.y = .16; headG.add(h); }
  if (skirt) { const sk = S(new THREE.Mesh(new THREE.CylinderGeometry(.17, .27, .42, 8), top)); sk.position.y = -.2; upper.add(sk); }
  const arms = [-1, 1].map(sx => {
    const a = new THREE.Group(); a.position.set(sx * .24, .56, 0); upper.add(a);
    const up = S(new THREE.Mesh(new THREE.BoxGeometry(.09, .3, .1), top)); up.position.y = -.15; a.add(up);
    const el = new THREE.Group(); el.position.y = -.3; a.add(el);
    const lo = S(new THREE.Mesh(new THREE.BoxGeometry(.08, .27, .09), R() < .4 ? skin : top)); lo.position.y = -.13; el.add(lo);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(.045, 6, 5), skin); hand.position.y = -.29; el.add(hand);
    return { a, el };
  });
  const legs = [-1, 1].map(sx => { const p = new THREE.Group(); p.position.set(sx * .085, .82, 0); g.add(p);
    const l = S(new THREE.Mesh(new THREE.BoxGeometry(.13, .78, .14), skirt ? skin : pants)); l.position.y = -.39; p.add(l);
    const f = S(new THREE.Mesh(new THREE.BoxGeometry(.13, .07, .24), shoe)); f.position.set(0, -.79, .04); p.add(f); return p; });
  if (o.logo) {        // channel logo on the jacket: o.logo = 'front' (chest, local +z) or 'back'
    const m = new THREE.MeshBasicMaterial({ transparent: true, alphaTest: .05 }), lg = new THREE.Mesh(new THREE.PlaneGeometry(.32, .32), m);
    const back = o.logo === 'back'; lg.position.set(0, .38, back ? -.2 : .2); lg.rotation.y = back ? Math.PI : 0; upper.add(lg);
    (E.loading ||= []).push(new Promise(ok => new THREE.TextureLoader().load('../branding/logo-cut.png', t => { t.colorSpace = THREE.SRGBColorSpace; m.map = t; m.needsUpdate = true; ok(); }, undefined, ok)));
  }
  const ph = R() * 6, react = o.react ?? pick(['point', 'shade', 'head', 'down', 'shade', 'point']);
  const P = { g, R, ph, path: o.path, baseY: o.y ?? .2, update(t, F) {
    const s = o.path(t, F, P);
    g.visible = s.visible !== false; if (!g.visible) return;
    g.position.set(s.x, (o.y ?? .2) + (s.y ?? 0), s.z); g.rotation.y = s.rot; g.rotation.x = s.lie ? -Math.PI / 2 : 0;
    const hu = s.headUp ?? 0; headG.rotation.x = -hu; upper.rotation.x = s.stoop ?? 0;
    const sw = s.moving ? Math.sin(t * s.speed * 4.2 + ph) * (s.moving === 2 ? .9 : .45) * (1 - (s.stoop ?? 0)) : 0;
    legs[0].rotation.x = sw; legs[1].rotation.x = -sw;
    // arms: swing while walking; when looking up they react (point, shade the eyes, hands on the head)
    const pose = s.arms ?? (hu > .25 && !s.moving ? react : null), k = Math.min(1, (hu - .25) / .3);
    arms[0].a.rotation.set(-sw * .8, 0, -.06); arms[1].a.rotation.set(sw * .8, 0, .06); arms[0].el.rotation.x = arms[1].el.rotation.x = -.25 - Math.abs(sw) * .3;
    if (pose === 'point') { arms[1].a.rotation.x = -2.5 * k; arms[1].el.rotation.x = -.1; }
    else if (pose === 'shade') { arms[1].a.rotation.x = -2.1 * k; arms[1].a.rotation.z = -.35 * k; arms[1].el.rotation.x = -1.7 * k; }
    else if (pose === 'head') { for (const [i, A] of arms.entries()) { A.a.rotation.x = -2.7 * k; A.a.rotation.z = (i ? -.5 : .5) * k; A.el.rotation.x = -1.9 * k; } }
    else if (s.lie) { arms[0].a.rotation.z = -.3; arms[1].a.rotation.z = .3; }
  } };
  E.people.push(P); return P;
}

// a car that drives along a straight lane (dir = +1/-1 along the axis), brakes at brakeT, then is a physics body
const CAR_COL = [0x8c3b33, 0x3e5873, 0xc9c3b4, 0x2f3236, 0x7d8a6a, 0xb59a5a, 0x6c7075, 0xa9a49a];
const wheelGeo = new THREE.CylinderGeometry(.34, .34, .25, 8); wheelGeo.rotateZ(Math.PI / 2);
export function car(E, seed, o) {
  const { lam, shadowed } = E, R = rng(seed), col = o.color ?? CAR_COL[Math.floor(R() * CAR_COL.length)];
  const g = new THREE.Group(), shell = new THREE.Group(); g.add(shell);
  const hull = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.8, .7, 4.3), lam(col))); hull.position.y = -.1; shell.add(hull);
  const c = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.6, .6, 2.2), lam(col))); c.position.set(0, .55, .2); shell.add(c);
  const gl = new THREE.Mesh(new THREE.BoxGeometry(1.62, .42, 2.0), lam(0x39444c)); gl.position.set(0, .56, .2); shell.add(gl);
  const roofSnow = o.snow ? new THREE.Mesh(new THREE.BoxGeometry(1.5, .12, 2.0), lam(0xeef2f5)) : null;
  if (roofSnow) { roofSnow.position.set(0, .9, .2); shell.add(roofSnow); E.melt.push({ mesh: roofSnow, to: 0 }); }
  const brake = new THREE.Mesh(new THREE.BoxGeometry(1.5, .14, .05), new THREE.MeshBasicMaterial({ color: 0x5a2420 })); brake.position.set(0, .05, 2.16); shell.add(brake);
  // front: two separate headlamps; rear: one long light bar (brake)
  const front = { material: new THREE.MeshBasicMaterial({ color: 0x55534c }) };
  for (const sx of [-.55, .55]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.32, .16, .05), front.material); l.position.set(sx, .05, -2.16); shell.add(l); }
  for (const [x, z] of [[-.85, 1.35], [.85, 1.35], [-.85, -1.35], [.85, -1.35]]) { const w = new THREE.Mesh(wheelGeo, lam(0x1c1d1f)); w.position.set(x, -.43, z); g.add(w); }
  E.scene.add(g);
  E.lights.push({ mat: front.material, off: 0x55534c, on: 0xfff1cf, at: R() * .1 });
  // lane: axis 'z' (x fixed) or 'x' (z fixed); path wraps within [a, b]
  const { x0, z0, dir, v, axis = 'z', a = -300, b = 80, brakeT = 1e9, y = .75 } = o;
  const len = b - a, Tb = o.Tb ?? 2.2;   // o.Tb: longer = the car rolls on and coasts to a stop (no driver)
  const s = t => { if (t < brakeT) return v * t; const tau = Math.min(t - brakeT, Tb); return v * brakeT + v * tau - v * tau * tau / (2 * Tb); };
  const wrap = q => a + ((q - a) % len + len) % len;
  const drive = t => {
    const d = s(t), sp = t < brakeT ? v : Math.max(0, v * (1 - (t - brakeT) / Tb));
    if (axis === 'z') return { p: [x0, y, wrap(z0 + dir * d)], r: [0, dir > 0 ? Math.PI : 0, 0], v: [0, 0, dir * sp] };   // front = local -z
    return { p: [wrap(x0 + dir * d), y, z0], r: [0, dir > 0 ? -Math.PI / 2 : Math.PI / 2, 0], v: [dir * sp, 0, 0] };
  };
  const body = E.body({ kind: 'car', obj: g, drive, k: .021, mu: .8, lift: .15, spin: .15, heavy: 2, hx: .9, hy: .75, hz: 2.15, density: .55,
    strength: o.strength ?? { wind: .3 + R() * .15, water: (o.ground ?? 0) + .55 + R() * .2 }, brakeT, wob: .3,
    onPose(t, st, w) { brake.material.color.setHex(!o.noBrakeLight && t > brakeT - .5 && t < brakeT + 30 && !E.powerOut?.(t) ? 0xc8352b : 0x5a2420);
      const d = o.F?.droop(t) ?? 0; shell.position.y = -d * .22; } });
  // o.driver = { out: s after the stop, to: [[x, z], ...] }: the driver gets out on the left and walks away (vanishes at the end)
  if (o.driver) {
    const D = o.driver, tOut = brakeT + Tb + (D.out ?? 1), vW = D.speed ?? 2.4;
    const at = t => {
      if (t < tOut) return { visible: false };
      const p = drive(tOut).p, side = axis === 'x' ? [0, -dir * 1.25] : [dir * 1.25, 0];
      const pts = [[p[0] + side[0], p[2] + side[1]], ...D.to];
      let d = (t - tOut) * vW;
      for (let i = 0; i < pts.length - 1; i++) {
        const [ax, az] = pts[i], [bx, bz] = pts[i + 1], L = Math.hypot(bx - ax, bz - az);
        if (d <= L) { const k = d / L; return { x: ax + (bx - ax) * k, z: az + (bz - az) * k, rot: Math.atan2(bx - ax, bz - az), moving: 1, speed: vW }; }
        d -= L;
      }
      return { visible: false };
    };
    person(E, seed + 7, { coat: D.coat ?? 0x2b3a4a, logo: D.logo, path: at });
    body.driverAt = at;
  }
  return body;
}
