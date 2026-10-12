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
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

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
  box(.1, RH, RD, -RW / 2, RH / 2, 0, wall);
  if (TL.escape) {   // right wall with an opening to the entry hall (z .2..1.1); front wall with a back door to the stairs (x -2.25..-1.35)
    box(.1, RH, 2.7, RW / 2, RH / 2, -1.15, wall); box(.1, RH, 1.4, RW / 2, RH / 2, 1.8, wall); box(.1, RH - 2.1, .9, RW / 2, (RH + 2.1) / 2, .65, wall);
    box(.75, RH, .1, -2.625, RH / 2, RD / 2, wall); box(4.35, RH, .1, .825, RH / 2, RD / 2, wall); box(.9, RH - 2.1, .1, -1.8, (RH + 2.1) / 2, RD / 2, wall);
  } else { box(.1, RH, RD, RW / 2, RH / 2, 0, wall); box(RW, RH, .1, 0, RH / 2, RD / 2, wall); }
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

  // ---------- the way out (TL.escape = { bang: [t0, t1], push: t, dropController: t }) ----------
  // Entry hall (x 3..6.4, z .1..1.2) to your front door, which shakes under the blows (purple light at its edges, a
  // flickering lamp, splinters). Back door (front wall) -> concrete stairwell (x -3.2..-.4, z 2.6..6.6), five floors down
  // (red floor numbers) -> green emergency exit (x -3.2, y OUT, z 3.1) -> a snowy back alley (x < -3.2, z .8..7.2).
  if (TL.escape) {
    const X = TL.escape, [b0, b1] = X.bang || [1e9, 1e9];
    const hit = t => { if (t < b0 || t > b1) return 0; const ph = (t - b0) * 2.6 % 1; return Math.exp(-ph * 9); };   // a blow every ~0.4 s
    // entry hall
    const hw = 0x34304a; box(3.4, .1, 1.1, 4.7, -.05, .65, 0x2b2a33); box(3.4, .1, 1.1, 4.7, 2.5, .65, 0x2b2a33);
    box(3.4, 2.5, .1, 4.7, 1.25, .05, hw); box(3.4, 2.5, .1, 4.7, 1.25, 1.25, hw);
    box(.12, .22, .08, 3.6, 1.4, 1.18, 0x9a9aa0);                                                   // intercom
    const door = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.08, 2.06, .9), lam(0x5a4130))); door.position.set(6.36, 1.03, .65); scene.add(door);
    for (const y of [.55, 1.45]) { const p2 = new THREE.Mesh(new THREE.BoxGeometry(.02, .7, .6), lam(0x4a3426)); p2.position.set(-.05, y - 1.03, 0); door.add(p2); }
    const edge = []; for (const [y, z, h, d] of [[1.03, .19, 2.06, .03], [1.03, 1.11, 2.06, .03], [2.08, .65, .03, .94], [.02, .65, .03, .94]]) edge.push(glow(.02, h, d, 6.42, y, z, C2));
    const lampH = new THREE.PointLight(0xfff0dd, 3, 5, 1.6); lampH.position.set(5.2, 2.3, .65); scene.add(lampH); glow(.4, .04, .4, 5.2, 2.44, .65, 0xfff0dd);
    const leak = new THREE.PointLight(C2, 0, 4, 1.4); leak.position.set(6.1, 1.0, .65); scene.add(leak);
    const chips = []; for (let i = 0; i < 24; i++) { const c = new THREE.Mesh(new THREE.BoxGeometry(.04, .02, .06), lam(0x6a4a34)); c.visible = false; scene.add(c); chips.push({ c, t0: b0 + 1 + i * .3, x: 6.3, y: .4 + hash(i, 1) * 1.6, z: .25 + hash(i, 2) * .8, vx: -.6 - hash(i, 3), vy: hash(i, 4) * .8 }); }
    E.updates.push(t => { const h = hit(t), on = t >= b0 && t <= b1;
      door.position.x = 6.36 - h * .06; door.rotation.z = h * .03 * Math.sin(t * 40);
      leak.intensity = on ? 1.5 + h * 6 : 0; edge.forEach(e => e.visible = on);
      lampH.intensity = on ? (h > .4 || Math.sin(t * 29) > .6 ? 0 : 3) : 3;
      for (const k of chips) { const a = t - k.t0; k.c.visible = a > 0 && a < 1.2 && t < b1 + 1; if (k.c.visible) k.c.position.set(k.x + k.vx * a, Math.max(.02, k.y + k.vy * a - 4.9 * a * a), k.z); k.c.rotation.set(a * 9, a * 7, 0); } });
    for (let k = 0; k < 16; k++) { const t0 = b0 + k * .385; if (t0 < b1) E.EVENTS.push({ t: t0, kind: 'impact', e: .7 }); }
    { const back = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.86, 2.06, .06), lam(0x6b6e74))); back.position.set(-2.22, 1.03, RD / 2 + .43); back.rotation.y = Math.PI / 2; scene.add(back); }   // back door, open
    // stairwell
    box(.1, -OUT + RH, 3, -3.2, (OUT + RH) / 2, 5.1, 0x8d8b86); box(.1, -OUT + RH - 2.2, 1, -3.2, (OUT + 2.2 + RH) / 2, 3.1, 0x8d8b86);   // left wall with the exit opening at the bottom (z 2.6..3.6)
    box(.1, -OUT + RH, 4, -.4, (OUT + RH) / 2, 4.6, 0x8d8b86); box(2.8, -OUT + RH, .1, -1.8, (OUT + RH) / 2, 6.6, 0x8d8b86);
    box(2.8, .1, 4, -1.8, RH + .05, 4.6, 0x8d8b86);
    for (let f = 0; f <= 5; f++) {
      const yA = -3 * f; box(2.8, .14, 1.0, -1.8, yA - .07, 3.1, 0x6f6d68);
      if (f < 5) { box(2.8, .14, .6, -1.8, yA - 1.57, 6.3, 0x6f6d68);
        for (let i = 0; i < 10; i++) { box(1.2, .15, .24, -2.5, yA - .075 - i * .15, 3.72 + i * .24, 0x7a7873); box(1.2, .15, .24, -1.1, yA - 1.575 - i * .15, 5.88 - i * .24, 0x7a7873); }
        box(.08, 1.6, 2.4, -1.8, yA - 1.0, 4.8, 0x5e5c58); }
      const cv = document.createElement('canvas'); cv.width = cv.height = 128; const c = cv.getContext('2d'); c.fillStyle = '#8d8b86'; c.fillRect(0, 0, 128, 128);
      c.fillStyle = '#c4302b'; c.font = '900 118px Inter, Arial, sans-serif'; c.textAlign = 'center'; c.fillText(String(5 - f), 64, 108);
      const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
      const num = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 1.3), lam(0xffffff, { map: tex })); num.position.set(-3.14, yA + .2, 4.6); num.rotation.y = Math.PI / 2; if (f < 5) scene.add(num);   // on the left wall along flight 1
      glow(.9, .04, .1, -1.8, yA + 2.6, 3.4, 0xe8f0ff);
      const L = new THREE.PointLight(0xdfe8ff, 3.2, 7, 1.5); L.position.set(-1.8, yA + 2.2, 4.0); scene.add(L);
      if (f === 2) E.updates.push(t => { L.intensity = Math.sin(t * 23) > .3 ? 3.2 : .8; });          // one tube flickers
    }
    // green emergency exit with a push bar, swings open at X.push
    const exitG = new THREE.Group(); exitG.position.set(-3.12, OUT, 2.66); scene.add(exitG);
    { const d = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.06, 2.1, .88), lam(0x2f7a4a))); d.position.set(0, 1.05, .44); exitG.add(d);
      const bar = new THREE.Mesh(new THREE.BoxGeometry(.08, .06, .7), lam(0xb8bcc0)); bar.position.set(.06, 1.0, .44); exitG.add(bar);
      const sign = glow(.04, .22, .55, -3.12, OUT + 2.35, 3.1, 0x3ad47a); void sign; }
    E.updates.push(t => { exitG.rotation.y = -Math.min(1, Math.max(0, (t - (X.push ?? 1e9)) / .5)) * 1.7; });
    // the back alley: walls with lit windows and fire escapes, dumpsters, lamps, snow
    { const g = new THREE.Mesh(new THREE.PlaneGeometry(60, 6.4), lam(0x3a3c44)); g.rotation.x = -Math.PI / 2; g.position.set(-33, OUT + .01, 4); g.receiveShadow = true; scene.add(g); }
    for (const z of [.8, 7.2]) { const w = new THREE.Mesh(facadeBox(60, 22, .4), facadeMats(z < 4 ? 0x5a4a44 : 0x4f4a58, 'win')); w.position.set(-33.2, OUT + 11, z + (z < 4 ? -.2 : .2)); scene.add(w);
      for (let x = -8; x > -60; x -= 9) for (let f = 0; f < 5; f++) { const s2 = z < 4 ? 1 : -1;
        box(2.4, .06, .9, x, OUT + 3.4 + f * 3.4, z + s2 * .45, 0x1a1a1c); box(2.4, .5, .04, x, OUT + 3.65 + f * 3.4, z + s2 * .9, 0x1a1a1c);
        const lad = box(.5, .05, 3.6, x + .6, OUT + 1.7 + f * 3.4, z + s2 * .45, 0x1a1a1c); lad.rotation.x = .9 * s2; lad.rotation.y = Math.PI / 2; } }
    for (const [x, z] of [[-7, 1.6], [-13, 6.3], [-19, 1.6], [-27, 6.3]]) { box(1.8, 1.2, 1.1, x, OUT + .6, z, 0x2d5a3a); box(1.9, .1, 1.2, x, OUT + 1.25, z, 0x24482e); }
    for (const [x, z] of [[-10, 1.2], [-21, 6.8], [-33, 1.2]]) { const L = new THREE.PointLight(0xffc27a, 26, 13, 1.4); L.position.set(x, OUT + 3.8, z); scene.add(L); glow(.3, .4, .3, x, OUT + 4, z, 0xffd9a0); }
    { const n = 1800, pos = new Float32Array(n * 3), base = [];
      for (let i = 0; i < n; i++) { base.push([-45 + R() * 42, R() * 14, .9 + R() * 6.2]); }
      const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      const snow = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xeef2ff, size: .06, transparent: true, opacity: .9 })); scene.add(snow);
      E.updates.push(t => { for (let i = 0; i < n; i++) { const [x, y, z] = base[i]; pos[i * 3] = x + Math.sin(t * .7 + i) * .3; pos[i * 3 + 1] = OUT + ((y - t * 1.1) % 14 + 14) % 14; pos[i * 3 + 2] = z; } geo.attributes.position.needsUpdate = true; }); }
    // POV arm that pushes the exit open
    if (X.push != null) { const cam = E.camera; if (!cam.parent) scene.add(cam);
      const arm = new THREE.Group(); arm.position.set(.12, -.2, -.35); cam.add(arm);
      const sl = new THREE.Mesh(new THREE.CylinderGeometry(.05, .065, .42, 7), lam(0x2c3a50, { flatShading: true })); sl.rotation.x = Math.PI / 2 - .2; sl.position.set(0, -.02, .12); arm.add(sl);
      const hd = new THREE.Mesh(new THREE.IcosahedronGeometry(.045, 0), lam(0xd6a27c, { flatShading: true })); hd.scale.set(1.2, .7, 1.4); hd.position.set(0, .02, -.12); arm.add(hd);
      E.updates.push(t => { const a = t - X.push; arm.visible = a > -.6 && a < .9; arm.position.z = -.35 - Math.max(0, Math.min(1, (a + .6) / .6)) * .12; }); }
    // the controller you put down, on the rug
    { const ctl = shadowed(new THREE.Mesh(new RoundedBoxGeometry(.16, .04, .1, 2, .015), lam(0x1d1e24))); ctl.position.set(1.15, .03, .55); ctl.rotation.y = .5; scene.add(ctl);
      const lb = new THREE.Mesh(new THREE.BoxGeometry(.08, .006, .01), new THREE.MeshBasicMaterial({ color: C1 })); lb.position.set(0, .015, -.05); ctl.add(lb);
      E.updates.push(t => { ctl.visible = t >= (X.dropController ?? 0); }); }
  }

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
    { const fill = new THREE.PointLight(0xe8d8ff, 1.6, 1.6, 1.5); fill.position.set(0, .25, -.1); cam.add(fill); }
    // a DualShock-like controller held low in front of you, seen from above; faceted low-poly hands grip it, thumbs on the sticks
    const g = new THREE.Group(); g.position.set(0, -.115, -.34); g.rotation.x = .62; cam.add(g);
    const skin = lam(0xd6a27c, { flatShading: true }), knuckle = lam(0xc28e6a, { flatShading: true }), sleeve = lam(0x2c4a74, { flatShading: true }), cuff = lam(0x233b5e, { flatShading: true });
    const pad = lam(0x1d1e24), padTop = lam(0x2a2c33), rb = (w, h, d, r = .008) => new RoundedBoxGeometry(w, h, d, 2, r);
    const add = (geo, mat, x, y, z, rx = 0, ry = 0, rz = 0, sx = 1, sy = 1, sz = 1) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.rotation.set(rx, ry, rz); m.scale.set(sx, sy, sz); g.add(m); return m; };
    add(rb(.14, .032, .066, .012), pad, 0, 0, 0);                                                   // body
    add(rb(.062, .005, .036, .002), padTop, 0, .017, -.008);                                       // touchpad
    add(new THREE.BoxGeometry(.07, .004, .006), new THREE.MeshBasicMaterial({ color: C1 }), 0, .008, -.034);   // light bar
    for (const s of [-1, 1]) {
      add(rb(.048, .036, .092, .016), pad, s * .066, -.006, .04, -.32, s * .32, 0);              // grip, angled toward you
      add(new THREE.CylinderGeometry(.009, .011, .012, 10), padTop, s * .028, .021, .014);           // stick
      add(new THREE.CylinderGeometry(.012, .012, .004, 10), lam(0x34363d), s * .028, .028, .014);    // stick cap
      add(rb(.03, .01, .012, .003), padTop, s * .052, .014, -.036);                                   // shoulder button
    }
    for (const [x, z, c] of [[.052, -.016, 0x6fd3c4], [.064, -.004, 0xe0606a], [.052, .008, 0x7d9ee8], [.040, -.004, 0xd889c9]])
      add(new THREE.SphereGeometry(.0045, 6, 4), lam(c), x, .018, z);                                // face buttons
    add(new THREE.BoxGeometry(.022, .005, .007), padTop, -.052, .018, -.004); add(new THREE.BoxGeometry(.007, .005, .022), padTop, -.052, .018, -.004);   // d-pad
    for (const s of [-1, 1]) {
      const ico = r => new THREE.IcosahedronGeometry(r, 0);
      add(ico(.04), skin, s * .078, -.004, .058, .2, s * .3, 0, 1.0, .72, 1.45);                     // palm around the grip
      for (let k = 0; k < 3; k++) add(rb(.016, .016, .046, .006), knuckle, s * (.05 + k * .006), -.026 - k * .004, .035 + k * .016, .5, s * .5, 0);   // fingers under the grip
      add(rb(.019, .016, .056, .007), skin, s * .045, .022, .036, -.15, -s * .62, 0);                 // thumb on the stick
      add(rb(.016, .014, .04, .006), skin, s * .064, .016, -.024, 0, s * .2, 0);                      // index on the shoulder button
      add(new THREE.CylinderGeometry(.03, .036, .1, 7), skin, s * .1, -.02, .13, Math.PI / 2 - .25, 0, s * .15);    // wrist
      add(new THREE.CylinderGeometry(.044, .046, .03, 7), cuff, s * .108, -.03, .18, Math.PI / 2 - .25, 0, s * .15);  // cuff
      add(new THREE.CylinderGeometry(.05, .07, .4, 7), sleeve, s * .13, -.07, .38, Math.PI / 2 - .25, 0, s * .15);   // sleeve toward the bottom corner
    }
    E.updates.push(t => { g.visible = TL.hands.some(([a, b]) => t >= a && t <= b); g.position.y = -.115 + Math.sin(t * 7) * .003; g.rotation.z = Math.sin(t * 3.3) * .025; });
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
