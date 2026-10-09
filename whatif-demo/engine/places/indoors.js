// INDOORS (bakstenen "Huiskamer" + "Tv-nieuws", okt 2026): three small sets in one scene, all showing one live TV
// channel (engine/tv.js, TL.tv):
//   living room (x 0):   flat on the 5th floor; sofa, coffee table, rug, TV on a cabinet, floor lamp, bookshelf, plants,
//                        a floor-to-ceiling window with the city (and TL.ufo) outside; people on the sofa (TL.room.people)
//   news studio (x 60):  video wall, curved desk with an anchor, side screens, light rig, studio cameras
//   shop window (x -60): electronics shop with a wall of TVs, pavement; passers-by hurry past, TL.groups stand and watch
// Beats: lookUp (people on the sofa turn to the window), shelter (unused), powerOut (room lights out).
// TL.room = { people: n (0..4), lamp: true }
import * as THREE from 'three';
import { rng, hash, smooth, colorKeys } from '../util.js';
import { person, lamp as streetLamp } from '../props.js';
import { crowd } from '../crowd.js';
import { channel, screen, tvSet } from '../tv.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed, facadeMats, facadeBox } = E, B = TL.beats, R = rng(17);
  const OUT = -15;                                     // street level outside the flat
  E.groundAt = (x, z) => Math.abs(x + 60) < 30 && z > -20 && z < 20 ? 0 : (Math.abs(x) < 4 && Math.abs(z) < 3 ? 0 : OUT);
  const ch = channel(E, TL);
  const box = (w, h, d, x, y, z, col, o = {}) => { const m = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), o.mat ?? lam(col, o))); m.position.set(x, y, z); scene.add(m); return m; };

  // ---------- the city below and around (seen through the window and above the shop) ----------
  { const g = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), lam(0x55575a)); g.rotation.x = -Math.PI / 2; g.position.set(0, OUT, -1000); g.receiveShadow = true; scene.add(g); }
  for (let i = 0; i < 140; i++) {
    const a = -Math.PI * .95 + R() * Math.PI * .9, d = 45 + R() * R() * 700, h = 12 + R() * 70 * (d > 250 ? 1.4 : 1), w = 14 + R() * 22;
    const x = Math.cos(a) * d * 1.3, z = Math.sin(a) * d - 20;
    if (z > -30 || Math.abs(x + 60) < 40 && z > -60) continue;
    const ratio = -x / -z;                              // keep a view corridor out of the living-room window (x/z between .3 and 1)
    if (ratio > .3 && ratio < 1.05 && d < 220) continue;
    const hh = ratio > .3 && ratio < 1.05 && d < 900 ? Math.min(h, 4 + d * .02) : h;   // low roofs in the corridor: you see over them
    const m = new THREE.Mesh(facadeBox(w, hh, w * (.7 + R() * .6)), facadeMats(R() < .3 ? E.TOWER_PAL[Math.floor(R() * 5)] : E.PALETTE[Math.floor(R() * 8)], R() < .3 ? 'tower' : 'win'));
    m.position.set(x, OUT + hh / 2, z); m.receiveShadow = true; scene.add(m);
  }

  // ---------- living room ----------
  const RW = 6, RD = 5, RH = 2.7, wall = 0xd9d2c3, ROOM = { x: 0, z: 0 };
  box(RW, .1, RD, 0, -.05, 0, 0x8a6a4c);                                   // wooden floor
  box(RW + .2, .1, RD + .2, 0, RH + .05, 0, 0xe6e1d8);                       // ceiling
  box(.1, RH, RD, -RW / 2, RH / 2, 0, wall); box(.1, RH, RD, RW / 2, RH / 2, 0, wall);
  // back wall with a wide window (x -2.7 .. -.1, y .15 .. 2.55)
  const W0 = -2.7, W1 = -.1, Y0 = .15, Y1 = 2.55, BZ = -RD / 2;
  box(W0 + RW / 2, RH, .12, (-RW / 2 + W0) / 2, RH / 2, BZ, wall); box(RW / 2 - W1, RH, .12, (W1 + RW / 2) / 2, RH / 2, BZ, wall);
  box(W1 - W0, Y0, .12, (W0 + W1) / 2, Y0 / 2, BZ, wall); box(W1 - W0, RH - Y1, .12, (W0 + W1) / 2, (RH + Y1) / 2, BZ, wall);
  for (const x of [W0 + .04, (W0 + W1) / 2, W1 - .04]) box(.07, Y1 - Y0, .1, x, (Y0 + Y1) / 2, BZ, 0xeeeae2);
  box(W1 - W0, .07, .1, (W0 + W1) / 2, Y0 + .03, BZ, 0xeeeae2); box(W1 - W0, .07, .1, (W0 + W1) / 2, Y1 - .03, BZ, 0xeeeae2);
  { const glass = new THREE.Mesh(new THREE.PlaneGeometry(W1 - W0, Y1 - Y0), new THREE.MeshBasicMaterial({ color: 0xbfd6e6, transparent: true, opacity: .07, depthWrite: false })); glass.position.set((W0 + W1) / 2, (Y0 + Y1) / 2, BZ); scene.add(glass); }
  box(.35, 2.5, .12, W0 - .2, 1.3, BZ + .14, 0x6e7f8c); box(.35, 2.5, .12, W1 + .2, 1.3, BZ + .14, 0x6e7f8c);   // curtains
  // rug, sofa, coffee table
  box(3.2, .02, 2.2, .2, .01, -.2, 0xa8614a);
  const sofaC = 0x55606b;
  box(2.6, .42, .95, .2, .21, 1.05, sofaC); box(2.6, .55, .22, .2, .7, 1.45, sofaC);
  box(.22, .62, .95, -1.0, .31, 1.05, sofaC); box(.22, .62, .95, 1.4, .31, 1.05, sofaC);
  for (const x of [-.45, .6]) box(1.0, .12, .75, x, .48, 1.0, 0x5e6a75);
  box(1.2, .06, .6, .2, .42, -.15, 0x6b5039); for (const [x, z] of [[-.3, -.38], [.7, -.38], [-.3, .08], [.7, .08]]) box(.05, .4, .05, x, .2, z, 0x4a3828);
  box(.25, .02, .18, .5, .46, -.2, 0xd8d0be);   // a magazine
  // TV on a cabinet against the back wall, right of the window
  tvSet(E, ch, { x: 1.55, z: BZ + .35, size: 1.3, glow: 3 });
  // bookshelf on the left wall, plants, floor lamp
  box(.35, 2, 1.4, -RW / 2 + .25, 1, .4, 0x6b5039);
  for (let i = 0; i < 4; i++) for (let k = 0; k < 7; k++) if (R() < .8) box(.25, .22 + R() * .08, .06 + R() * .05, -RW / 2 + .3, .3 + i * .45 + .13, .4 - .6 + k * .19, [0x8c3b33, 0x3e5873, 0xc9b896, 0x2f5d46, 0x7a5a44][Math.floor(R() * 5)]);
  for (let i = 0; i < 4; i++) box(.34, .03, 1.38, -RW / 2 + .25, .3 + i * .45, .4, 0x5a4330);
  const plant = (x, z, s) => { box(.3 * s, .35 * s, .3 * s, x, .175 * s, z, 0xb8b0a2);
    for (let i = 0; i < 7; i++) { const l = new THREE.Mesh(new THREE.ConeGeometry(.12 * s, .7 * s, 4), lam(0x4d7a46)); l.position.set(x + (hash(i, x) - .5) * .25 * s, .6 * s, z + (hash(i, z) - .5) * .25 * s); l.rotation.set((hash(i, 3) - .5) * .9, 0, (hash(i, 4) - .5) * .9); l.castShadow = true; scene.add(l); } };
  plant(2.5, -1.9, 1.2); plant(-2.6, 1.9, 1); plant(-2.95 + .3, -2.1, .9);
  box(.05, 1.55, .05, 2.5, .78, 1.6, 0x2a2a2a); box(.32, .05, .32, 2.5, .02, 1.6, 0x2a2a2a);
  { const shade = new THREE.Mesh(new THREE.CylinderGeometry(.16, .24, .3, 10, 1, true), lam(0xefe2c4, { side: THREE.DoubleSide, emissive: new THREE.Color(0x6b5a3a) })); shade.position.set(2.5, 1.62, 1.6); scene.add(shade);
    const L = new THREE.PointLight(0xffc98a, 0, 9, 1.5); L.position.set(2.5, 1.5, 1.6); scene.add(L);
    E.updates.push(t => { L.intensity = (TL.room?.lamp === false || E.powerOut?.(t)) ? 0 : 9; }); }
  // frames on the right wall
  for (const [z, w, c] of [[-.8, .7, 0x3e5873], [.3, .5, 0xb5653f]]) { box(.04, w * .75, w, RW / 2 - .07, 1.65, z, 0x2a2a2a); box(.02, w * .65, w * .88, RW / 2 - .1, 1.65, z, c); }
  // people on the sofa: they watch the TV, at beats.lookUp they turn to the window
  const np = TL.room?.people ?? 3;
  [[-.55, 'a'], [.25, 'b'], [1.0, 'c'], [-.15, 'd']].slice(0, np).forEach(([x], i) => {
    const look = (B.lookUp ?? 1e9) + i * .4;
    person(E, 7000 + i, { y: 0, react: 'head', path: t => {
      const turn = smooth(look, look + 1.5, t);
      const toTv = Math.atan2(1.55 - x, 1.0 - (BZ + .35)) * -1, toWin = Math.atan2(-1.4 - x, 1.0 - BZ) * -1;
      return { x, z: 1.0, y: -.36, rot: Math.PI + (toTv * (1 - turn) + toWin * turn) * .8 + Math.sin(t * .3 + i) * .04, moving: 0, speed: 0, headUp: turn * .12, stoop: -.08 };
    } });
  });

  // ---------- news studio (x 60) ----------
  const SX = 60;
  box(16, .1, 12, SX, -.05, 0, 0x1b2333); box(16, .1, 12, SX, 5.05, 0, 0x141820);
  box(16, 5, .2, SX, 2.5, -5.5, 0x1f2a3c); box(.2, 5, 12, SX - 8, 2.5, 0, 0x1f2a3c); box(.2, 5, 12, SX + 8, 2.5, 0, 0x1f2a3c);
  box(16, .06, .4, SX, .03, -2.8, 0x2f6fb0);                                                    // light strip on the floor
  screen(E, ch, { w: 7.2, h: 4.05, pos: [SX, 2.75, -5.35], glow: 8 });
  screen(E, ch, { w: 2.4, h: 1.35, pos: [SX - 5.6, 2.4, -4.6], ry: .5 });
  screen(E, ch, { w: 2.4, h: 1.35, pos: [SX + 5.6, 2.4, -4.6], ry: -.5 });
  { const desk = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 2.4, .95, 24, 1, true, -Math.PI * .32, Math.PI * .64), lam(0xd9dde3, { side: THREE.DoubleSide }));
    desk.position.set(SX, .475, -2.6); desk.castShadow = true; scene.add(desk);
    const top = new THREE.Mesh(new THREE.CylinderGeometry(2.55, 2.55, .06, 24, 1, false, -Math.PI * .32, Math.PI * .64), lam(0x2b3442)); top.position.set(SX, .97, -2.6); scene.add(top);
    const band = new THREE.Mesh(new THREE.CylinderGeometry(2.41, 2.41, .12, 24, 1, true, -Math.PI * .32, Math.PI * .64), new THREE.MeshBasicMaterial({ color: 0xb3201b, side: THREE.DoubleSide })); band.position.set(SX, .7, -2.6); scene.add(band); }
  person(E, 7100, { y: 0, coat: 0x23262c, path: t => ({ x: SX, z: -2.85 + 2.4 - 1.95, rot: Math.sin(t * .5) * .08, moving: 0, speed: 0, headUp: Math.sin(t * 1.3) * .04, stoop: .05 }) });
  for (let i = 0; i < 5; i++) { const pnl = new THREE.Mesh(new THREE.BoxGeometry(1.6, .06, .6), new THREE.MeshBasicMaterial({ color: 0xfff4e0 })); pnl.position.set(SX - 6 + i * 3, 4.95, 0); scene.add(pnl); }
  for (const [x, z] of [[-3, 3], [3, 3], [0, 4]]) { const L = new THREE.PointLight(0xfff0dc, 18, 16, 1.4); L.position.set(SX + x, 4.2, z); scene.add(L); }
  for (const x of [-2.6, 2.4]) {        // studio cameras on tripods
    box(.5, .4, .7, SX + x, 1.45, 3.4, 0x2a2c30); box(.25, .25, .3, SX + x, 1.5, 2.95, 0x18191b);
    for (let k = 0; k < 3; k++) { const a = k / 3 * Math.PI * 2, l = new THREE.Mesh(new THREE.CylinderGeometry(.025, .025, 1.4, 5), lam(0x3a3c40)); l.position.set(SX + x + Math.sin(a) * .25, .65, 3.4 + Math.cos(a) * .25); l.rotation.set(Math.cos(a) * .3, 0, -Math.sin(a) * .3); scene.add(l); }
  }

  // ---------- shop window (x -60) ----------
  const HX = -60;
  box(60, .3, 40, HX, -.15, 0, 0x9b968c);                                                      // pavement
  { const road = new THREE.Mesh(new THREE.PlaneGeometry(60, 8), lam(0x3c3e41)); road.rotation.x = -Math.PI / 2; road.position.set(HX, .01, 12); scene.add(road); }
  // shop front (z -4): wall with a big window, dark shop inside, a wall of TVs, a sign
  const SZ = -4, sw = 9, sh = 3.2;
  box(30, 1, .4, HX, .5, SZ, 0x6f6a64); box((30 - sw) / 2, sh, .4, HX - (sw + (30 - sw) / 2) / 2, 1 + sh / 2, SZ, 0x6f6a64); box((30 - sw) / 2, sh, .4, HX + (sw + (30 - sw) / 2) / 2, 1 + sh / 2, SZ, 0x6f6a64);
  const upper = new THREE.Mesh(facadeBox(30, 9, 8), facadeMats(0xc9b896, 'win')); upper.position.set(HX, 4.2 + 4.5, SZ - 3.8); upper.castShadow = upper.receiveShadow = true; scene.add(upper);
  box(sw + .4, .1, 6, HX, 4.25, SZ - 3, 0x6f6a64); box(sw, 3.4, .2, HX, 2.6, SZ - 6, 0x22252a); box(sw, .1, 6, HX, .95, SZ - 3, 0x30333a);
  { const glass = new THREE.Mesh(new THREE.PlaneGeometry(sw, sh), new THREE.MeshBasicMaterial({ color: 0xbfd6e6, transparent: true, opacity: .1, depthWrite: false })); glass.position.set(HX, 1 + sh / 2, SZ + .21); scene.add(glass); }
  for (let r = 0; r < 2; r++) for (let k = 0; k < 4; k++) screen(E, ch, { w: 1.5, h: .84, pos: [HX - 2.6 + k * 1.75, 1.75 + r * 1.05, SZ - 1.2], glow: r === 0 && k % 2 ? 2 : 0 });
  box(sw * .9, .06, .5, HX, 1.3, SZ - 1.2, 0x30333a);
  { const cv = document.createElement('canvas'); cv.width = 512; cv.height = 64; const c = cv.getContext('2d'); c.fillStyle = '#1f3b5c'; c.fillRect(0, 0, 512, 64);
    c.fillStyle = '#f2efe6'; c.font = '700 40px "Inter", Arial, sans-serif'; c.textAlign = 'center'; c.fillText('TV  •  AUDIO  •  PHONES', 256, 46);
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; const s = new THREE.Mesh(new THREE.PlaneGeometry(8, 1), lam(0xffffff, { map: t })); s.position.set(HX, 4.75, SZ + .22); scene.add(s); }
  streetLamp(E, HX + 8, 7.6, 1); streetLamp(E, HX - 10, 7.6, 1);
  // people hurrying past with shopping bags (beats: none; they never stop)
  crowd(E, TL, { n: 12, axis: 'x', lane: [1.5, 5], range: [HX - 26, HX + 26], door: () => 0, seed: 61 });

  // ---------- light ----------
  const sky = colorKeys(THREE, [[0, 0x7aa3cc, 0xd3dde2]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-60, 70, -150]));    // low sun beyond the window: light falls into the room
  return {
    ambience: 'stad',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 150, fogFar: 1400, hemi: 1.2, hemiColor: new THREE.Color(0xe3ecf4), groundColor: new THREE.Color(0x6a6052),
      sun: 2.2, sunColor: new THREE.Color(0xffe6c8), sunDisc: new THREE.Color(0xaa9977) }),
    shots: {
      sofa: { pos: [2.55, 1.5, 3.4], look: [-.9, 1.25, -2.5], drift: [-.08, 0, -.05], fov: 58 },       // behind the sofa: TV, people, the window and the city
      window: { pos: [1.0, 1.62, 2.1], look: [-1.9, 1.95, -6], drift: [-.06, 0, 0], fov: 60 },            // over their heads out of the window
      tv: { pos: [.4, 1.15, .4], look: [1.55, 1.05, -2.15], drift: [0, 0, -.06], fov: 44, hand: true },    // POV from the sofa: the TV
      faces: { pos: [1.4, 1.05, -1.5], look: [.1, 1.0, 1.0], drift: [0, 0, 0], fov: 50 },                // from the TV: their faces in its light
      studio: { pos: [SX + 2.2, 1.75, 6.2], look: [SX, 2.0, -4], drift: [-.15, 0, -.08], fov: 56 },
      anchor: { pos: [SX + .5, 1.6, 1.4], look: [SX, 1.55, -2], drift: [0, 0, -.03], fov: 36 },
      shop: { pos: [HX + 2.5, 1.7, 9], look: [HX, 2.1, -4], drift: [-.12, 0, -.1], fov: 54 },
      'shop-close': { pos: [HX + 3.6, 1.65, 1.6], look: [HX + .2, 2.0, -5.2], drift: [0, 0, -.05], fov: 50, hand: true },
    },
  };
}
