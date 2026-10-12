// GAME ROOM + NARROW STREET (baksteen, okt 2026; voorbeeldbeelden van de eigenaar): a gamer's room on the 5th floor at
// night – purple/cyan LED strips, a big TV with a game (tv.js), shelves with a speaker and headphones, a bean bag,
// pixel-art posters – a glass balcony door at the back (z -2.5, x -2.7..-.1) onto a small balcony with a railing and a
// plant, and below it a narrow street (along x): pavements, warm street lamps, parked cars and a taxi, bins, litter,
// a row of facades with lit windows across the street, and the lit front door of your own building (E.entrance).
//   Room: floor y 0, x -3..3, z -2.5..2.5. Balcony: y 0, z -2.6..-4.1. Street level OUT = -15; road z -7..-12.5.
//   TL.hands = [[t0, t1], ...]: low-poly hands with a controller in front of the camera (POV) during those times.
// Beats: powerOut (room and street lights out).
import * as THREE from 'three';
import { rng, hash } from '../util.js';
import { lamp as streetLamp, car } from '../props.js';
import { channel, tvSet } from '../tv.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed, facadeMats, facadeBox } = E, R = rng(23), OUT = -15;
  E.groundAt = (x, z) => (z > -2.6 && Math.abs(x) < 3.2) || (z > -4.2 && z <= -2.6 && x > -3.2 && x < .4) ? 0 : OUT;
  const ch = channel(E, TL);
  const box = (w, h, d, x, y, z, col, o = {}) => { const m = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), o.mat ?? lam(col, o))); m.position.set(x, y, z); scene.add(m); return m; };
  const glow = (w, h, d, x, y, z, col) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshBasicMaterial({ color: col })); m.position.set(x, y, z); scene.add(m); return m; };

  // ---------- room ----------
  const RW = 6, RD = 5, RH = 2.7, wall = 0x3d3752, BZ = -RD / 2, W0 = -2.7, W1 = -.1;
  box(RW, .1, RD, 0, -.05, 0, 0x4a3a30);                                          // floor
  box(RW + .2, .1, RD + .2, 0, RH + .05, 0, 0x332e44);                            // ceiling
  box(.1, RH, RD, -RW / 2, RH / 2, 0, wall); box(.1, RH, RD, RW / 2, RH / 2, 0, wall); box(RW, RH, .1, 0, RH / 2, RD / 2, wall);
  box(W0 + RW / 2, RH, .12, (-RW / 2 + W0) / 2, RH / 2, BZ, wall); box(RW / 2 - W1, RH, .12, (W1 + RW / 2) / 2, RH / 2, BZ, wall);
  box(W1 - W0, RH - 2.4, .12, (W0 + W1) / 2, (RH + 2.4) / 2, BZ, wall);
  for (const x of [W0 + .04, W1 - .04]) box(.08, 2.4, .1, x, 1.2, BZ, 0x2a2733);  // door frame (glass door slid open)
  box(.06, 2.3, .9, W0 + .5, 1.2, BZ - .05, 0x2a2733, { transparent: true, opacity: .35 });
  box(.4, 2.5, .12, W0 - .25, 1.3, BZ + .14, 0x26232f); box(.4, 2.5, .12, W1 + .25, 1.3, BZ + .14, 0x26232f);   // dark curtains
  box(2.6, .02, 2.0, .6, .01, .3, 0x2b2a3a);                                      // rug
  // LED strips: cyan along the ceiling edges, purple under the shelves and around the TV
  const C1 = 0x3fd8ff, C2 = 0xb04dff;
  glow(RW - .2, .04, .04, 0, RH - .04, BZ + .08, C1); glow(.04, .04, RD - .2, RW / 2 - .08, RH - .04, 0, C2); glow(.04, .04, RD - .2, -RW / 2 + .08, RH - .04, 0, C1);
  for (const [x, y, z, c, i] of [[1.4, 2.4, -2.1, C2, 6], [-2.2, 2.4, 1.2, C1, 4], [2.6, 1.0, -2.0, C2, 4]]) { const L = new THREE.PointLight(c, i, 7, 1.4); L.position.set(x, y, z); scene.add(L); }
  // TV wall: cabinet, TV, shelves with LED, speaker, headphones, games
  box(2.2, .5, .5, 1.4, .25, BZ + .3, 0x3a2f2a); box(2.1, .04, .46, 1.4, .52, BZ + .3, 0x2a221e);
  tvSet(E, ch, { x: 1.4, z: BZ + .35, size: 1.55, glow: 5 });
  for (const [y, w] of [[2.0, 2.2], [1.55, .7]]) { box(w, .05, .3, y > 1.8 ? 1.4 : -.05, y, BZ + .2, 0x3a2f2a); glow(w, .02, .02, y > 1.8 ? 1.4 : -.05, y - .04, BZ + .34, C2); }
  box(.22, .3, .2, .7, 2.18, BZ + .2, 0x15151a); { const ring = new THREE.Mesh(new THREE.TorusGeometry(.07, .015, 6, 16), new THREE.MeshBasicMaterial({ color: 0x4dff9a })); ring.position.set(.7, 2.18, BZ + .31); scene.add(ring); }
  for (let k = 0; k < 6; k++) box(.05, .24, .17, 1.5 + k * .07, 2.15, BZ + .2, [0x8c3b33, 0x3e5873, 0xc9b896, 0x2f5d46][k % 4]);
  { const hp = new THREE.Mesh(new THREE.TorusGeometry(.11, .025, 6, 12, Math.PI), lam(0x15151a)); hp.position.set(2.2, 2.12, BZ + .2); scene.add(hp); }
  // bean bag, side table with a drink, backpack
  { const bb = shadowed(new THREE.Mesh(new THREE.IcosahedronGeometry(.55, 1), lam(0x4b4466))); bb.scale.set(1.2, .6, 1.1); bb.position.set(-1.7, .3, .9); scene.add(bb); }
  box(.5, .45, .5, -1.0, .22, 1.9, 0x3a2f2a); box(.08, .14, .08, -1.0, .52, 1.9, 0xc98a3a, { transparent: true, opacity: .8 });
  box(.35, .45, .2, .2, .22, -1.85, 0x3a3f35);
  // pixel-art posters on the left wall (a skull and a zombie)
  const pixel = (rows, cols) => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const c = cv.getContext('2d'); c.fillStyle = '#1b1a26'; c.fillRect(0, 0, 64, 64);
    rows.forEach((r, y) => [...r].forEach((ch2, x) => { if (ch2 !== '.') { c.fillStyle = cols[ch2]; c.fillRect(8 + x * 6, 6 + y * 6, 6, 6); } }));
    const t = new THREE.CanvasTexture(cv); t.magFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace; return t; };
  const skull = pixel(['.wwwww..', 'wwwwwww.', 'wkwwwkw.', 'wkwwwkw.', 'wwwkwww.', '.wwwww..', '.w.w.w..', '.wwwww..'], { w: '#e8e4d8', k: '#111' });
  const zomb = pixel(['.gggg...', 'gggggg..', 'gkggkg..', 'gggggg..', 'g.rr.g..', '.gggg...', 'bbbbbb..', 'b.bb.b..'], { g: '#7fb069', k: '#111', r: '#5a2a2a', b: '#3e5873' });
  for (const [z, y, tex] of [[1.4, 1.65, skull], [.3, 1.4, zomb]]) { const p = new THREE.Mesh(new THREE.PlaneGeometry(.75, .75), lam(0xffffff, { map: tex })); p.position.set(-RW / 2 + .07, y, z); p.rotation.y = Math.PI / 2; scene.add(p); }
  E.hotRoom = true;

  // ---------- balcony: slab, railing, plant ----------
  box(3.6, .14, 1.6, -1.4, -.07, BZ - .85, 0x5c6066);
  for (let x = -3.15; x <= .35; x += .22) box(.04, 1.0, .04, x, .5, BZ - 1.6, 0x23262b);
  box(3.6, .06, .08, -1.4, 1.0, BZ - 1.6, 0x23262b); for (const x of [-3.2, .4]) for (let z = BZ - .1; z > BZ - 1.6; z -= .22) box(.04, 1.0, .04, x, .5, z, 0x23262b);
  box(.04, .06, 1.5, -3.2, 1.0, BZ - .85, 0x23262b); box(.04, .06, 1.5, .4, 1.0, BZ - .85, 0x23262b);
  box(.35, .3, .35, -2.85, .15, BZ - 1.3, 0x6b5039);
  for (let i = 0; i < 7; i++) { const l = new THREE.Mesh(new THREE.ConeGeometry(.06, .5, 4), lam(0x4d7a46)); l.position.set(-2.85 + (hash(i, 1) - .5) * .2, .5, BZ - 1.3 + (hash(i, 2) - .5) * .2); l.rotation.set((hash(i, 3) - .5) * 1.2, 0, (hash(i, 4) - .5) * 1.2); scene.add(l); }

  // ---------- your building (facade around and under the room) ----------
  const FC = 0x6d6a72;
  { const below = new THREE.Mesh(facadeBox(60, -OUT, .4), facadeMats(FC, 'win')); below.position.set(0, OUT / 2, -2.8); scene.add(below);
    const above = new THREE.Mesh(facadeBox(60, 12, .4), facadeMats(FC, 'win')); above.position.set(0, RH + 6, -2.8); scene.add(above);
    for (const s of [-1, 1]) { const side = new THREE.Mesh(facadeBox(27, RH, .4), facadeMats(FC, 'win')); side.position.set(s * (3.2 + 13.5), RH / 2, -2.8); scene.add(side); } }
  // the lit front door below the balcony
  box(2.4, 2.8, .12, -1.4, OUT + 1.6, -3.06, 0xffd9a0, { emissive: 0xffb860 });
  box(3.2, .14, 1.6, -1.4, OUT + 3.1, -3.8, 0x2a2d33);
  { const L = new THREE.PointLight(0xffc27a, 0, 14, 1.4); L.position.set(-1.4, OUT + 2.6, -4.2); scene.add(L);
    E.updates.push(t => { L.intensity = E.powerOut?.(t) ? 0 : 40; }); }
  E.entrance = [-1.4, OUT + .2, -3.3];

  // ---------- the narrow street ----------
  box(200, .2, 4, 0, OUT + .1, -5, 0x55575c);                                         // pavement (your side) z -3..-7
  { const road = new THREE.Mesh(new THREE.PlaneGeometry(200, 5.5), lam(0x2b2d33)); road.rotation.x = -Math.PI / 2; road.position.set(0, OUT + .02, -9.75); road.receiveShadow = true; scene.add(road); }
  for (let x = -96; x < 96; x += 6) box(2.6, .01, .12, x, OUT + .03, -9.75, 0x9a9890);
  box(200, .2, 3, 0, OUT + .1, -14, 0x55575c);                                        // pavement across z -12.5..-15.5
  { const g = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), lam(0x24252a)); g.rotation.x = -Math.PI / 2; g.position.set(0, OUT - .05, -200); scene.add(g); }
  // facades across the street, tall, many lit windows
  for (let x = -90; x < 90;) { const w = 9 + R() * 10, h = 22 + R() * 18, d = 12;
    const m = new THREE.Mesh(facadeBox(w - .3, h, d), facadeMats([0x6a5a4e, 0x5a5f6a, 0x7a6352, 0x4f5560][Math.floor(R() * 4)], 'win')); m.position.set(x + w / 2, OUT + h / 2, -15.6 - d / 2); m.receiveShadow = true; scene.add(m); x += w; }
  // far towers at the end of the street (city glow)
  for (let i = 0; i < 16; i++) { const h = 40 + R() * 80, m = new THREE.Mesh(facadeBox(18, h, 18), facadeMats(E.TOWER_PAL[Math.floor(R() * 5)], 'tower')); m.position.set((R() < .5 ? -1 : 1) * (110 + R() * 140), OUT + h / 2, -10 - R() * 120); scene.add(m); }
  // street lamps with real light pools
  for (const [x, z, s] of [[-26, -7.2, -1], [-12, -12.6, 1], [2, -7.2, -1], [16, -12.6, 1], [30, -7.2, -1], [-40, -12.6, 1]]) {
    streetLamp(E, x, z, s, { y: OUT + .2 });
    const L = new THREE.PointLight(0xffc27a, 0, 18, 1.3); L.position.set(x - s * 1.6, OUT + 7.6, z); scene.add(L);
    E.updates.push(t => { L.intensity = E.powerOut?.(t) ? 0 : 55; });
  }
  // parked cars (a taxi), bins, litter
  [[-18, -7.9, 1, 0xf2c218], [-9, -7.9, 1, 0x8e959c], [7, -7.9, 1, 0x3e5873], [13, -11.6, -1, 0xd8d6d0], [-24, -11.6, -1, 0x6a2e2a], [24, -7.9, 1, 0x2f3236]]
    .forEach(([x, z, dir, color], i) => car(E, 800 + i, { x0: x, z0: z, dir, v: 0, axis: 'x', y: OUT + .75, a: -300, b: 300, color, noBrakeLight: true }));
  for (const [x, z] of [[-6, -6.4], [4.5, -6.5], [9, -13.4], [-15, -13.3]]) box(.6, .9, .6, x, OUT + .65, z, 0x2d4f8a);
  for (let i = 0; i < 40; i++) { const p = new THREE.Mesh(new THREE.PlaneGeometry(.22, .3), lam(0xd8d4c8)); p.rotation.set(-Math.PI / 2, 0, R() * 6); p.position.set(-20 + R() * 40, OUT + .22, -4 - R() * 10); scene.add(p); }

  // ---------- POV hands with a controller (TL.hands) ----------
  if (TL.hands) {
    const cam = E.camera; if (!cam.parent) scene.add(cam);
    cam.near = .05; cam.updateProjectionMatrix(); E.nearFn = () => .05;               // the hands are close: keep them from clipping
    { const fill = new THREE.PointLight(0xc8b8ff, 2.5, 2, 1.5); fill.position.set(0, .3, .2); cam.add(fill); }
    const g = new THREE.Group(); g.position.set(0, -.27, -.62); g.rotation.x = .75; g.scale.setScalar(1.7); cam.add(g);
    const skin = lam(0xc99a78), sleeve = lam(0x2f4f7a), pad = lam(0x1b1c21);
    const body = new THREE.Mesh(new THREE.BoxGeometry(.2, .035, .09), pad); g.add(body);
    for (const s of [-1, 1]) {
      const grip = new THREE.Mesh(new THREE.BoxGeometry(.05, .04, .1), pad); grip.position.set(s * .1, -.01, .04); grip.rotation.y = s * .3; g.add(grip);
      const stick = new THREE.Mesh(new THREE.CylinderGeometry(.012, .012, .02, 8), lam(0x2a2b30)); stick.position.set(s * .04, .025, .015); g.add(stick);
      const hand = new THREE.Mesh(new THREE.IcosahedronGeometry(.055, 0), skin); hand.scale.set(1, .7, 1.3); hand.position.set(s * .11, .01, .06); g.add(hand);
      const thumb = new THREE.Mesh(new THREE.BoxGeometry(.02, .02, .06), skin); thumb.position.set(s * .06, .03, .02); thumb.rotation.y = -s * .5; g.add(thumb);
      const arm = new THREE.Mesh(new THREE.CylinderGeometry(.045, .055, .4, 7), sleeve); arm.rotation.x = Math.PI / 2 - .3; arm.position.set(s * .14, -.05, .27); g.add(arm);
    }
    const bar = new THREE.Mesh(new THREE.BoxGeometry(.08, .006, .01), new THREE.MeshBasicMaterial({ color: C1 })); bar.position.set(0, .02, -.046); g.add(bar);
    E.updates.push(t => { g.visible = TL.hands.some(([a, b]) => t >= a && t <= b); g.position.y = -.27 + Math.sin(t * 7) * .004; g.rotation.z = Math.sin(t * 3.3) * .03; });
  }

  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-60, 70, -150]));
  return {
    ambience: 'stad',
    look: () => ({ top: new THREE.Color(0x0b1230), hor: new THREE.Color(0x2a2d4a), fogNear: 60, fogFar: 600, fogColor: new THREE.Color(0x1c1e30),
      hemi: .35, hemiColor: new THREE.Color(0x6a70a8), groundColor: new THREE.Color(0x2a2533), sun: .25, sunColor: new THREE.Color(0x8a96d8), dark: 1, stars: .8 }),
    shots: {
      tv: { pos: [.4, 1.05, 1.5], look: [1.4, 1.0, -2.2], drift: [0, 0, -.05], fov: 55 },
      balcony: { pos: [-1.4, 1.7, -3.9], look: [-12, OUT, -9], drift: [0, 0, 0], fov: 60 },
    },
  };
}
