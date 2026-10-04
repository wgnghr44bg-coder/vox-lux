// Shared street kit (earth-stops look): road + pavements, low-poly people (optionally with a phone),
// cars with head/brake lights (optional police light bar), street lamps with light pools, planes with contrails.
//   import { makeStreet, makePerson, posePerson, carMesh, setCarLights, streetLamp, plane } from '../lib/street.js';
import * as THREE from 'three';
import { lam, glow, shadowed, glowSprite } from './core.js';

// road (4 lanes, |x| < road), pavements (road < |x| < walk), centre lines, lane dashes, optional zebra at z = zebra
export function makeStreet(scene, { road = 10, walk = 16, z0 = 70, z1 = -560, zebra = null, ground = 0x3c3e41, pave = 0x9b968c } = {}) {
  const len = z0 - z1, zc = (z0 + z1) / 2;
  const g = new THREE.Mesh(new THREE.PlaneGeometry(400, len + 200), lam(ground)); g.rotation.x = -Math.PI / 2; g.position.set(0, 0, zc); g.receiveShadow = true; scene.add(g);
  for (const s of [-1, 1]) {
    const w = shadowed(new THREE.Mesh(new THREE.BoxGeometry(walk - road, 0.2, len), lam(pave)), false);
    w.position.set(s * (road + walk) / 2, 0.1, zc); scene.add(w);
    const curb = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.22, len), lam(0xb7b2a8)); curb.position.set(s * road, 0.11, zc); scene.add(curb);
  }
  const paint = (w, d, x, z, col = 0xd9d6cc) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color: col }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, 0.02, z); m.receiveShadow = true; scene.add(m); };
  paint(0.15, len, -0.15, zc, 0xc9a94a); paint(0.15, len, 0.15, zc, 0xc9a94a);
  for (let z = z0 - 10; z > z1; z -= 9) { paint(0.15, 4.5, -road / 2, z); paint(0.15, 4.5, road / 2, z); }
  paint(0.2, len, -road + .4, zc); paint(0.2, len, road - .4, zc);
  if (zebra !== null) { for (let x = -road + 1; x <= road - 1; x += 1.6) paint(0.85, 4, x, zebra);
    paint(road * .95, 0.4, -road / 2, zebra - 3); paint(road * .95, 0.4, road / 2, zebra + 3); }
  return { road, walk, paint };
}

// ---------- people ----------
const SHIRTS = [0x8a6b4e, 0x5e6f80, 0xb9ae96, 0x7b4a42, 0x56624a, 0xd2cbb8, 0x3d4650, 0x9a8a5c, 0x2f3a4a, 0x6a6e72];
const phoneGeo = new THREE.BoxGeometry(.08, .15, .02);
export const phoneLit = glow(0x9fd0ff), phoneDark = lam(0x1a1c1f);
// R: rng. Returns { g, body, head, legs, arms, phone }. Phone sits in the right hand; arms[1].rotation.x raises it.
export function makePerson(scene, R, { phone = false, suit = R() < .5 } = {}) {
  const g = new THREE.Group(); scene.add(g);
  const col = suit ? [0x2b2f36, 0x3a3f47, 0x4a4540, 0x22252a][Math.floor(R() * 4)] : SHIRTS[Math.floor(R() * SHIRTS.length)];
  const body = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.2, .17, .75, 6), lam(col))); body.position.y = 1.2; g.add(body);
  const head = shadowed(new THREE.Mesh(new THREE.IcosahedronGeometry(.13, 0), lam([0x6b5444, 0x8c6a52, 0x4a382c, 0xb08a6e][Math.floor(R() * 4)])));
  head.position.y = 1.72; g.add(head);
  const legs = [-1, 1].map(s => { const p = new THREE.Group(); p.position.set(s * .08, .82, 0); g.add(p);
    const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.12, .82, .13), lam(0x2f3236))); l.position.y = -.41; p.add(l); return p; });
  const arms = [-1, 1].map(s => { const p = new THREE.Group(); p.position.set(s * .25, 1.52, 0); g.add(p);
    const a = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.09, .6, .1), lam(col))); a.position.y = -.3; p.add(a); return p; });
  let ph = null;
  if (phone) { ph = new THREE.Mesh(phoneGeo, phoneLit); ph.position.set(0, -.6, .05); ph.rotation.x = -.3; arms[1].add(ph); }
  return { g, body, head, legs, arms, phone: ph };
}
// o: { x, z, rot, walk (phase, rad), stride (0..1), headDown (rad), headYaw (rad), phoneUp (0..1), wave (0..1), t }
export function posePerson(p, o) {
  p.g.position.set(o.x, .2, o.z); p.g.rotation.y = o.rot || 0;
  const sw = Math.sin(o.walk || 0) * (o.stride ?? 0);
  p.legs[0].rotation.x = sw; p.legs[1].rotation.x = -sw;
  p.arms[0].rotation.x = -sw * .6; p.arms[1].rotation.x = sw * .6 * (1 - (o.phoneUp || 0));
  p.head.rotation.set(o.headDown || 0, o.headYaw || 0, 0);
  if (o.phoneUp) p.arms[1].rotation.x = -1.25 * o.phoneUp + p.arms[1].rotation.x;
  if (o.wave) { p.arms[0].rotation.x = -2.6 * o.wave; p.arms[0].rotation.z = Math.sin((o.t || 0) * 7) * .35 * o.wave; } else p.arms[0].rotation.z = 0;
}

// ---------- cars ----------
const wheelGeo = new THREE.CylinderGeometry(.34, .34, .25, 8); wheelGeo.rotateZ(Math.PI / 2);
export const CAR_COL = [0x8c3b33, 0x3e5873, 0xc9c3b4, 0x2f3236, 0x7d8a6a, 0xb59a5a, 0x6c7075, 0xa9a49a, 0x1f2328, 0xdedad0];
const lightOff = { head: lam(0x8d8f8c), tail: lam(0x5a2420) };
const lightOn = { head: glow(0xfff2d0), tail: glow(0xd8342a), brake: glow(0xff4a3a) };
// front of the car points to -z in local space. police: adds a light bar (bars[0] red, bars[1] blue)
export function carMesh(scene, col, { police = false, taxi = false } = {}) {
  const g = new THREE.Group();
  if (police) col = 0xe8e6e0; if (taxi) col = 0xd8b23a;
  const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.8, .7, 4.3), lam(col))); b.position.y = -.1; g.add(b);
  const c = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.6, .6, 2.2), lam(police ? 0x23272e : col))); c.position.set(0, .55, .2); g.add(c);
  const gl = new THREE.Mesh(new THREE.BoxGeometry(1.62, .42, 2.0), lam(0x39444c)); gl.position.set(0, .56, .2); g.add(gl);
  const head = [-.6, .6].map(x => { const m = new THREE.Mesh(new THREE.BoxGeometry(.4, .16, .05), lightOff.head); m.position.set(x, .05, -2.16); g.add(m); return m; });
  const tail = [-.6, .6].map(x => { const m = new THREE.Mesh(new THREE.BoxGeometry(.4, .14, .05), lightOff.tail); m.position.set(x, .05, 2.16); g.add(m); return m; });
  for (const [x, z] of [[-.85, 1.35], [.85, 1.35], [-.85, -1.35], [.85, -1.35]]) { const w = new THREE.Mesh(wheelGeo, lam(0x1c1d1f)); w.position.set(x, -.43, z); g.add(w); }
  const halo = glowSprite(0xffe6b0, 3.2, 0); halo.position.set(0, .1, -2.6); g.add(halo);
  let bars = null;
  if (police) bars = [[-.35, 0xe0302a], [.35, 0x2f6bff]].map(([x, c]) => { const m = new THREE.Mesh(new THREE.BoxGeometry(.6, .14, .3), lam(0x333333));
    m.position.set(x, .92, .2); g.add(m); const s = glowSprite(c, 3, 0); s.position.set(x, 1.0, .2); g.add(s);
    return { m, s, on: glow(c), off: m.material }; });
  if (taxi) { const s = new THREE.Mesh(new THREE.BoxGeometry(.5, .18, .2), glow(0xfff1b0)); s.position.set(0, .94, .2); g.add(s); }
  scene.add(g); return { g, head, tail, halo, bars };
}
// head 0..1 (headlights + halo), brake bool, flash -1 off | 0..1 phase (police bar)
export function setCarLights(car, head, brake, flash = -1) {
  car.head.forEach(m => { m.material = head > .5 ? lightOn.head : lightOff.head; });
  car.tail.forEach(m => { m.material = brake ? lightOn.brake : head > .5 ? lightOn.tail : lightOff.tail; });
  car.halo.material.opacity = head * .55;
  if (car.bars) car.bars.forEach((b, i) => { const on = flash >= 0 && ((flash * 2 + i * .5) % 1) < .5;
    b.m.material = on ? b.on : b.off; b.s.material.opacity = on ? .9 : 0; });
}

// ---------- street lamps ----------
// s = side (-1 left, 1 right), head over the road. setOn(k) 0..1 lights the head + a pool of light on the ground.
export function streetLamp(scene, x, z, s) {
  const g = new THREE.Group(); g.position.set(x, .2, z); scene.add(g);
  const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.09, .12, 8, 6), lam(0x4a4d50))); pole.position.y = 4; g.add(pole);
  const arm = new THREE.Mesh(new THREE.BoxGeometry(1.8, .1, .1), lam(0x4a4d50)); arm.position.set(-s * .8, 7.9, 0); g.add(arm);
  const headOff = lam(0x5d6063), headOn = glow(0xffd9a0);
  const head = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.8, .2, .35), headOff)); head.position.set(-s * 1.6, 7.8, 0); g.add(head);
  const halo = glowSprite(0xffcf8a, 4, 0); halo.position.set(-s * 1.6, 7.5, 0); g.add(halo);
  const pool = new THREE.Mesh(new THREE.CircleGeometry(6, 20), new THREE.MeshBasicMaterial({ map: halo.material.map, color: 0xffc27a,
    transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  pool.rotation.x = -Math.PI / 2; pool.position.set(x - s * 1.6, .25, z); scene.add(pool);
  return { g, head, setOn: k => { head.material = k > .5 ? headOn : headOff; halo.material.opacity = k * .8; pool.material.opacity = k * .45; } };
}

// ---------- planes ----------
// a small airliner + contrail; fly(t01) places it along a straight path from a to b (world coords)
export function plane(scene, size = 60) {
  const g = new THREE.Group(); scene.add(g);
  const m = lam(0xe9ecef, { fog: false });
  const f = new THREE.Mesh(new THREE.CylinderGeometry(size * .05, size * .045, size, 6), m); f.rotation.x = Math.PI / 2; g.add(f);
  const w = new THREE.Mesh(new THREE.BoxGeometry(size * .95, size * .01, size * .14), m); w.position.z = -size * .02; g.add(w);
  const tw = new THREE.Mesh(new THREE.BoxGeometry(size * .32, size * .01, size * .08), m); tw.position.z = size * .45; g.add(tw);
  const fin = new THREE.Mesh(new THREE.BoxGeometry(size * .01, size * .14, size * .1), m); fin.position.set(0, size * .07, size * .45); g.add(fin);
  const trail = new THREE.Mesh(new THREE.BoxGeometry(size * .06, size * .03, 1), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .55, fog: false }));
  trail.geometry.translate(0, 0, .5); scene.add(trail);
  return { g, trail, fly(a, b, u, len = 900, vis = 1) {
    const p = new THREE.Vector3().lerpVectors(a, b, u); g.position.copy(p); g.lookAt(b); g.rotateY(Math.PI);
    const back = Math.min(len, a.distanceTo(b) * u);
    trail.position.copy(p); trail.lookAt(a); trail.scale.set(1, 1, back); trail.material.opacity = .5 * vis;
    g.visible = trail.visible = vis > 0 && u > 0 && u < 1; } };
}
