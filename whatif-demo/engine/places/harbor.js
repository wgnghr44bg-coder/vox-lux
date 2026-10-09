// HARBOUR AT NIGHT (baksteen "haven met schepen", okt 2026): the sea along x (mean sea level y 0) against a
// concrete quay wall (top QY = 3.2 m) with fenders, ladders and a dark tide band; a container terminal with three
// gantry cranes and a moored cargo ship; a tug, fishing boats and a yacht along the quay; a road and warehouses
// behind it, the town rising gently inland; a breakwater with a lighthouse out at sea. Night, lit by the Moon
// (moon.js: brighter as it comes closer) and the lamps.
//   floats:     every ship follows the water (force tide.js or water.js); small boats are carried inland when the
//               water goes over the quay and stay behind on the quay / in the street when it drains (TL.boats:
//               [[x0, x1, z1], ...] overrides where the small boats end up)
//   can flood:  quay (QY), road (QY), the town (above QY, 1 m every 20 m inland); the quay darkens once wet
//   moorings:   lines from the cargo ship to the quay bollards
// Beats: lookUp, shelter (groups / people on the quay)
import * as THREE from 'three';
import { rng, hash, smooth, clamp, lerp } from '../util.js';
import { lamp } from '../props.js';
import { block } from '../blocks.js';

export const QY = 3.2;

function hullGeo(len, beam, h, bow = .3) {
  const g = new THREE.BoxGeometry(beam, h, len, 1, 2, 8), p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i), f = z / (len / 2);          // f = 1 at the bow (+z)
    let k = f > 1 - bow * 2 ? 1 - Math.pow((f - (1 - bow * 2)) / (bow * 2), 1.6) * .88 : 1;
    if (y < 0) k *= .78;                                                             // narrower keel
    if (f < -.92) k *= .92;                                                          // squarer stern
    p.setX(i, x * k); if (f > .9 && y > 0) p.setY(i, y + h * .12);                  // the bow rises a little
  }
  g.computeVertexNormals(); return g;
}

// a ship: group with its pivot on the waterline (keel at -draft), long axis along local z
function ship(E, o) {
  const { lam, shadowed } = E, g = new THREE.Group(), R = rng(o.seed || 1);
  const { len, beam, h, draft, color } = o;
  const hull = shadowed(new THREE.Mesh(hullGeo(len, beam, h, o.bow), lam(color))); hull.position.y = h / 2 - draft; g.add(hull);
  const boot = new THREE.Mesh(hullGeo(len * .995, beam * 1.01, draft * .75, o.bow), lam(o.boot ?? 0x7a2e26)); boot.position.y = -draft * .62; g.add(boot);
  const deckY = h - draft;
  const deck = new THREE.Mesh(new THREE.BoxGeometry(beam * .9, .2, len * .82), lam(o.deck ?? 0x6b6258)); deck.position.set(0, deckY + .1, -len * .04); g.add(deck);
  if (o.kind === 'cargo') {
    const br = shadowed(new THREE.Mesh(E.facadeBox(beam * .9, 11, 9, 4, 2.8), E.facadeMats(0xe9e4d8, 'win'))); br.position.set(0, deckY + 5.5, -len * .38); g.add(br);
    const wing = shadowed(new THREE.Mesh(new THREE.BoxGeometry(beam * 1.05, .6, 3), lam(0xe9e4d8))); wing.position.set(0, deckY + 10.6, -len * .38 + 3); g.add(wing);
    const fun = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3, 6, 4), lam(0x2c3e50))); fun.position.set(0, deckY + 13, -len * .44); g.add(fun);
    const cols = [0xb5543f, 0x2f6d86, 0xd9b44a, 0x7d9a6a, 0x8e8e8a, 0xc9c1ae, 0x3e5873];
    const n = Math.floor(len * .55 / 12.6);
    for (let i = 0; i < n; i++) for (let j = 0; j < 6; j++) {
      const hgt = 1 + Math.floor(R() * 4); for (let k = 0; k < hgt; k++) {
        const c = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.55, 12.1), lam(cols[Math.floor(R() * cols.length)])));
        c.position.set(-beam * .38 + j * beam * .152, deckY + 1.5 + k * 2.6, -len * .27 + 6.3 + i * 12.6); g.add(c);
      }
    }
    const top = new THREE.Mesh(new THREE.BoxGeometry(.3, .3, .3), new THREE.MeshBasicMaterial({ color: 0xff3020 })); top.position.set(0, deckY + 16.4, -len * .44); g.add(top);
  } else {
    const cab = shadowed(new THREE.Mesh(new THREE.BoxGeometry(beam * .7, o.cabinH ?? 2.4, len * .28), lam(o.cabin ?? 0xe9e4d8)));
    cab.position.set(0, deckY + (o.cabinH ?? 2.4) / 2 + .2, o.kind === 'tug' ? len * .08 : -len * .12); g.add(cab);
    const win = new THREE.Mesh(new THREE.BoxGeometry(beam * .71, .5, len * .1), lam(0x2a3338)); win.position.set(0, deckY + (o.cabinH ?? 2.4) * .72, cab.position.z + len * .1); g.add(win);
    if (o.kind === 'tug') { const st = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.6, .7, 3.4, 8), lam(0x2f2f30))); st.position.set(0, deckY + 4.4, len * .02); g.add(st);
      for (const s of [-1, 1]) { const t = new THREE.Mesh(new THREE.TorusGeometry(.5, .22, 6, 10), lam(0x26282a)); t.rotation.y = Math.PI / 2; t.position.set(s * beam * .5, deckY - .4, 0); g.add(t); } }
    if (o.kind === 'fishing') { const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.12, .15, 7, 5), lam(0xd9d6cc))); m.position.set(0, deckY + 3.5, len * .15); g.add(m);
      const boom = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, 6, 4), lam(0xd9d6cc)); boom.position.set(0, deckY + 4, -len * .05); boom.rotation.x = .9; g.add(boom); }
    if (o.kind === 'yacht') { const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.08, .1, 13, 5), lam(0xe0ddd6))); m.position.set(0, deckY + 6.5, len * .08); g.add(m); }
    if (o.light !== false) { const l = new THREE.Mesh(new THREE.BoxGeometry(.25, .25, .25), new THREE.MeshBasicMaterial({ color: 0xffe2a8 })); l.position.set(0, deckY + (o.cabinH ?? 2.4) + .6, cab.position.z); g.add(l); }
  }
  E.scene.add(g); return g;
}

function crane(E, x, color) {
  const { lam, shadowed } = E, g = new THREE.Group(), m = lam(color); g.position.set(x, QY, 0); E.scene.add(g);
  for (const sx of [-8, 8]) for (const z of [2.5, 26]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1, 36, 1), m)); l.position.set(sx, 18, z); g.add(l); }
  for (const z of [2.5, 26]) { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(17, 1.4, 1.2), m)); b.position.set(0, 12, z); g.add(b); }
  for (const sx of [-8, 8]) { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 24), m)); b.position.set(sx, 34, 14); g.add(b);
    const s = new THREE.Mesh(new THREE.BoxGeometry(.6, .6, 30), m); s.position.set(sx, 30, 14); s.rotation.x = .35; g.add(s); }
  const boom = shadowed(new THREE.Mesh(new THREE.BoxGeometry(5, 2.6, 92), m)); boom.position.set(0, 37.5, -12); g.add(boom);
  const house = shadowed(new THREE.Mesh(new THREE.BoxGeometry(8, 5, 9), lam(0xd9d6cc))); house.position.set(0, 41, 26); g.add(house);
  const apex = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.2, 14, 1.2), m)); apex.position.set(0, 45, 14); g.add(apex);
  const cab = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3, 2.4, 3), lam(0xe9e4d8))); cab.position.set(0, 34.5, -6); g.add(cab);
  const red = new THREE.Mesh(new THREE.BoxGeometry(.5, .5, .5), new THREE.MeshBasicMaterial({ color: 0xff2a1a })); red.position.set(0, 52.4, 14); g.add(red);
  const red2 = red.clone(); red2.position.set(0, 39.2, -57.5); g.add(red2);
  return g;
}

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  E.waterBase = 0;
  E.dustColor = [.8, .82, .84];
  const groundAt = (x, z) => z < -40 ? -12 : z < 0 ? -10 : z < 56 ? QY : QY + (z - 56) * .05;
  E.groundAt = groundAt;
  const W = t => F.field(t).waterY ?? 0;
  // water level history (for boats and the wet quay): max so far, sampled at 30 fps
  const NT = Math.ceil((TL.T_END + 1) * 30), wmaxA = new Float32Array(NT);
  let wm = -1e9; for (let i = 0; i < NT; i++) { wm = Math.max(wm, W(i / 30)); wmaxA[i] = wm; }
  const wmax = t => wmaxA[clamp(Math.round(t * 30), 0, NT - 1)];
  const shoreZ = w => w <= QY ? -.6 : 56 + (w - QY) / .05;

  // sea (rises and falls with the tide), the harbour bed, the quay wall
  { const g = new THREE.PlaneGeometry(5000, 2400, 90, 40); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(4);
    for (let i = 0; i < p.count; i++) p.setY(i, (R() - .5) * .25); g.computeVertexNormals();
    const sea = new THREE.Mesh(g, new THREE.MeshPhongMaterial({ color: 0x2c5566, specular: 0x9aa8bc, shininess: 70, flatShading: true }));   // the moon glitters on the waves
    sea.position.set(0, 0, -1100 + 1.2); sea.receiveShadow = true; scene.add(sea);
    E.floods.push({ mesh: sea, y: 0, wave: true });
    const bed = new THREE.Mesh(new THREE.PlaneGeometry(5000, 2400, 60, 30), lam(0x3b3a33));
    { const q = bed.geometry; q.rotateX(-Math.PI / 2); q.translate(0, 0, -1200); const a = q.attributes.position;
      for (let i = 0; i < a.count; i++) a.setY(i, groundAt(a.getX(i), Math.min(-.5, a.getZ(i))) + (hash(i, 3) - .5) * .4);
      q.computeVertexNormals(); }
    bed.receiveShadow = true; scene.add(bed);
    const wall = shadowed(new THREE.Mesh(new THREE.BoxGeometry(5000, QY + 11, 1.2), lam(0x8a867d)), false); wall.position.set(0, (QY - 11) / 2, -.6); scene.add(wall);
    const band = new THREE.Mesh(new THREE.PlaneGeometry(5000, 3.4), lam(0x3f4a3c)); band.position.set(0, -.3, -1.22); band.rotation.y = Math.PI; scene.add(band);
    const band2 = new THREE.Mesh(new THREE.PlaneGeometry(5000, 7), lam(0x2c3329)); band2.position.set(0, -5.6, -1.22); band2.rotation.y = Math.PI; scene.add(band2);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(5000, .3, 1.6), lam(0xb3ada0)); cap.position.set(0, QY + .05, -.4); scene.add(cap);
    for (let x = -400; x < 400; x += 9) { const f = shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.6, 3, .6), lam(0x1d1e1f))); f.position.set(x, .9, -1.5); scene.add(f); }
    for (let x = -390; x < 400; x += 42) for (const dx of [-.25, .25]) { const r = new THREE.Mesh(new THREE.BoxGeometry(.08, 12, .08), lam(0x6b6a66)); r.position.set(x + dx, QY - 6, -1.3); scene.add(r); }
    E.foamLines = [];
    const foam = new THREE.Mesh(new THREE.PlaneGeometry(5000, 1.6), new THREE.MeshLambertMaterial({ color: 0xdfe6e8, transparent: true, opacity: .55 }));
    foam.rotation.x = -Math.PI / 2; scene.add(foam);
    E.updates.push((t, F, tv) => { const w = W(t); foam.position.set(0, w + .05, shoreZ(w) - (w <= QY ? 1.4 : .6) + Math.sin(tv * .8) * .3); });
  }
  // quay apron, road, town ground
  const apronMat = lam(0x8c8981), dryCol = new THREE.Color(0x8c8981), wetCol = new THREE.Color(0x4c4c4a);
  { const ap = new THREE.Mesh(new THREE.BoxGeometry(5000, .4, 56), apronMat); ap.position.set(0, QY - .2, 28); ap.receiveShadow = true; scene.add(ap);
    const road = new THREE.Mesh(new THREE.PlaneGeometry(5000, 11), lam(0x34363a)); road.rotation.x = -Math.PI / 2; road.position.set(0, QY + .02, 49); road.receiveShadow = true; scene.add(road);
    for (let x = -400; x < 400; x += 8) { const d = new THREE.Mesh(new THREE.PlaneGeometry(3.5, .16), lam(0xcfcac0)); d.rotation.x = -Math.PI / 2; d.position.set(x, QY + .03, 49); scene.add(d); }
    for (const z of [2.5, 26]) { const r = new THREE.Mesh(new THREE.PlaneGeometry(5000, .3), lam(0x55524c)); r.rotation.x = -Math.PI / 2; r.position.set(0, QY + .02, z); scene.add(r); }
    const g = new THREE.PlaneGeometry(5000, 700, 1, 40); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const z = p.getZ(i) + 56 + 350; p.setZ(i, z); p.setY(i, groundAt(0, z)); }
    g.computeVertexNormals(); const town = new THREE.Mesh(g, lam(0x77746c)); town.receiveShadow = true; scene.add(town);
    E.updates.push(t => { apronMat.color.copy(dryCol).lerp(wetCol, smooth(QY, QY + .25, wmax(t))); });
    for (let x = -390; x < 400; x += 18) { const b = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.35, .4, .7, 8), lam(0x2a2b2d))); b.position.set(x, QY + .35, 1.2); scene.add(b); }
  }
  // cranes and container stacks (west), sheds and the town (north)
  crane(E, -120, 0x2f5f8a); crane(E, -78, 0x2f5f8a); crane(E, -36, 0xc9692f);
  { const R = rng(31), cols = [0xb5543f, 0x2f6d86, 0xd9b44a, 0x7d9a6a, 0x8e8e8a, 0xc9c1ae, 0x3e5873, 0x8c3b33];
    const geo = new THREE.BoxGeometry(12.1, 2.55, 2.4), im = new THREE.InstancedMesh(geo, lam(0xffffff), 900); im.castShadow = im.receiveShadow = true;
    const D = new THREE.Object3D(); let n = 0;
    for (let x = -230; x < -14; x += 13.2) for (let z = 31; z < 44; z += 2.6) { const h = 1 + Math.floor(R() * 4);
      for (let k = 0; k < h && n < 900; k++) { D.position.set(x, QY + 1.28 + k * 2.56, z); D.updateMatrix(); im.setMatrixAt(n, D.matrix); im.setColorAt(n, new THREE.Color(cols[Math.floor(R() * cols.length)])); n++; } }
    im.count = n; scene.add(im); }
  { const R = rng(41); let x = -260;
    while (x < 330) { const w = 22 + R() * 26, cx = x + w / 2, z = 70 + R() * 6;
      if (cx > -20 && cx < 200 && R() < .6) block(E, { x: cx, y: groundAt(0, z - 9), z, w, d: 16, floors: 3 + Math.floor(R() * 4), color: [0xc9b896, 0x9c4a3a, 0xd2c6ae, 0x8e8e8a, 0xb5653f][Math.floor(R() * 5)], balconies: [0, -1] });
      else { const sh = shadowed(new THREE.Mesh(E.facadeBox(w, 9, 18, 6, 4.5), E.facadeMats([0x8f969b, 0xa7a49b, 0x6f7f86][Math.floor(R() * 3)], 'win'))); sh.position.set(cx, groundAt(0, z - 9) + 4.5, z); scene.add(sh);
        const rf = new THREE.Mesh(new THREE.BoxGeometry(w + .6, .6, 18.6), lam(0x55595c)); rf.position.set(cx, groundAt(0, z - 9) + 9.3, z); scene.add(rf); }
      x += w + 5; }
    for (let i = 0; i < 70; i++) { const bx = -400 + R() * 800, bz = 105 + R() * 260, w = 14 + R() * 18;
      block(E, { x: bx, y: groundAt(0, bz - 8), z: bz, w, d: 14 + R() * 6, floors: 2 + Math.floor(R() * 7), color: E.PALETTE[Math.floor(R() * E.PALETTE.length)], shop: R() < .4, cast: false }); }
  }
  // lamps along the quay and the road
  for (let x = -300, i = 0; x < 300; x += 26, i++) { lamp(E, x, 8, 1, { y: QY }); lamp(E, x + 13, 55.5, -1, { y: QY }); }
  // breakwater with a lighthouse out at sea
  { const R = rng(51), x0 = -330, x1 = -60, z = -255;
    for (let x = x0; x <= x1; x += 4) { const r = shadowed(new THREE.Mesh(new THREE.DodecahedronGeometry(4 + R() * 2.5, 0), lam(0x55534e))); r.position.set(x, -1 + R() * 2.5, z + (R() - .5) * 4); r.rotation.set(R() * 6, R() * 6, 0); scene.add(r); }
    const lh = new THREE.Group(); lh.position.set(x1 + 2, 2, z); scene.add(lh);
    const tw = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(1.5, 2.3, 18, 10), lam(0xe9e4d8))); tw.position.y = 9; lh.add(tw);
    for (const y of [5, 11]) { const s = new THREE.Mesh(new THREE.CylinderGeometry(2.05 - y * .04, 2.12 - y * .04, 2.4, 10), lam(0xb03a2e)); s.position.y = y; lh.add(s); }
    const lamp2 = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1.6, 8), new THREE.MeshBasicMaterial({ color: 0xfff1c0 })); lamp2.position.y = 18.8; lh.add(lamp2);
    const cap = new THREE.Mesh(new THREE.ConeGeometry(1.4, 1.4, 8), lam(0x2c3036)); cap.position.y = 20.3; lh.add(cap);
    E.updates.push((t, F, tv) => { lamp2.material.color.setHex((tv % 5) < 1.2 ? 0xfff6d8 : 0x6a5f40); });
  }

  // ---------- ships ----------
  const ships = [];
  const cargo = ship(E, { kind: 'cargo', len: 150, beam: 22, h: 13, draft: 7, color: 0x3a6688, seed: 3 });
  cargo.rotation.y = -Math.PI / 2; ships.push({ g: cargo, x0: -78, z0: -13.5, draft: 7, big: true, ph: 0 });
  const small = [
    { kind: 'tug', len: 24, beam: 9, h: 4.2, draft: 3, color: 0xb5402f, cabin: 0xe9e4d8, cabinH: 3.2, x0: 22, z0: -6.8 },
    { kind: 'fishing', len: 17, beam: 6, h: 3.2, draft: 1.7, color: 0x2f6d86, x0: 55, z0: -5.2 },
    { kind: 'fishing', len: 15, beam: 5.5, h: 3, draft: 1.6, color: 0xd9b44a, cabin: 0xd2c6ae, x0: 78, z0: -5 },
    { kind: 'yacht', len: 12, beam: 4, h: 2.4, draft: 1.4, color: 0xeeeeea, deck: 0xa48a64, cabinH: 1.4, x0: 100, z0: -4.4 },
    { kind: 'fishing', len: 16, beam: 5.8, h: 3.1, draft: 1.7, color: 0x8c3b33, x0: 124, z0: -5.1 },
  ];
  const ends = TL.boats || [[22, 18, 22], [55, 60, 47], [78, 86, 33], [100, 108, 50], [124, 126, 40]];
  small.forEach((o, i) => { const g = ship(E, { ...o, seed: 10 + i }); g.rotation.y = -Math.PI / 2 + (hash(i, 2) - .5) * .1;
    const [, x1, z1] = ends[i] || [o.x0, o.x0, 30]; ships.push({ g, x0: o.x0, z0: o.z0, x1, z1, draft: o.draft, ph: hash(i, 5) * 6, turn: (hash(i, 7) - .5) * 1.4, len: o.len }); });
  // mooring lines of the cargo ship
  const lines = [[-140, -60], [-110, -40], [-46, -40], [-16, -60]].map(([bx, lx]) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, 1, 4), lam(0xd8d2c0)); scene.add(m); return { m, bx, lx }; });
  const peak = Math.max(...wmaxA);
  const _a = new THREE.Vector3(), _b = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0);
  E.updates.push((t, F, tv) => {
    const w = W(t), wm = wmax(t);
    for (const s of ships) {
      let x = s.x0, z = s.z0, yaw = 0;
      if (!s.big) { const k = smooth(QY + s.draft + .2, Math.max(QY + s.draft + .6, peak - .3), wm); x = lerp(s.x0, s.x1, k); z = lerp(s.z0, s.z1, k * (2 - k)); yaw = s.turn * k; }
      const gnd = groundAt(x, z) + s.draft, y = Math.max(w, gnd + (s.big ? 0 : .02)), grounded = gnd > w - .05;     // pivot on the waterline, keel at -draft
      const bob = grounded ? 0 : Math.sin(tv * .8 + s.ph) * .12;
      s.g.position.set(x, y + bob, z); s.g.rotation.set(0, -Math.PI / 2 + yaw, 0);
      const lean = grounded ? clamp((gnd - w) / 2, 0, 1) * (s.big ? .035 : .16) : 0;
      s.g.rotateZ(Math.sin(tv * .6 + s.ph) * (grounded ? 0 : .02) + lean * (s.ph > 3 ? 1 : -1));
    }
    for (const L of lines) {        // deck edge of the cargo ship -> bollard
      _a.set(L.lx + 0, cargo.position.y + 5.8, cargo.position.z + 11); _b.set(L.bx, QY + .6, 1.2);
      L.m.position.copy(_a).add(_b).multiplyScalar(.5); L.m.scale.y = _a.distanceTo(_b);
      L.m.quaternion.setFromUnitVectors(up, _b.clone().sub(_a).normalize());
    }
  });
  // water pouring back off the quay when the sea drains
  E.emitters.push((tv, add) => {
    const t = Math.min(tv, B.stop), w = W(t), r = F.rate ? F.rate(t) : 0;
    if (wmax(t) < QY + .3 || w > QY + .3 || w < -8 || r > -.05) return;
    const k = smooth(.05, .6, -r) * (1 - smooth(QY - 6, QY - 9, w));
    for (let i = 0; i < 240 * k; i++) { const x = -200 + hash(i, 1) * 400, a = (tv * .9 + hash(i, 2)) % 1;
      add(x, QY - a * (QY - w), -1.2 - a * 1.2, 1.1 + a * 1.6, .32 * (1 - a) * k, .86, .9, .92, hash(i, 3) * 6); }
  });
  // spray where the rising sea hits the quay wall
  E.emitters.push((tv, add) => {
    const t = Math.min(tv, B.stop), w = W(t), r = F.rate ? F.rate(t) : 0;
    if (r < .08 || w < QY - 2.5) return;
    const k = smooth(.08, .5, r);
    for (let i = 0; i < 160 * k; i++) { const x = -220 + hash(i, 4) * 440, a = (tv * 1.3 + hash(i, 5)) % 1, zz = shoreZ(w);
      add(x, w + Math.sin(a * Math.PI) * 1.4, zz - 1.5 + a * 3, 1 + a * 1.2, .12 * Math.sin(a * Math.PI) * k, .9, .93, .95, hash(i, 6) * 6); }
  });

  E.brandSpot = null;
  E.sunOffset = (E.moonDir ? E.moonDir.clone() : new THREE.Vector3(-.26, .3, -.96).normalize()).multiplyScalar(220);
  if (E.sunOffset.y < 40) E.sunOffset.y = 40;          // a low moon still casts readable shadows
  const md = E.moonDir || new THREE.Vector3(-.26, .12, -.96).normalize();
  const tele = (pos, fov, el = 0, yaw = 0) => { const c = Math.cos(yaw), s = Math.sin(yaw), x = md.x * c - md.z * s, z = md.x * s + md.z * c;
    return { pos, look: [pos[0] + x * 1000, pos[1] + (md.y + el) * 1000, pos[2] + z * 1000], drift: [0, 0, 0], fov }; };
  return {
    ambience: 'zee',
    look: t => {
      const b = E.moonBright ? E.moonBright(t) : 1, k = clamp(Math.log2(b) / 6);       // 0 today .. 1 at ~64× brighter
      return { top: new THREE.Color(0x060c18).lerp(new THREE.Color(0x14223a), k), hor: new THREE.Color(0x15223a).lerp(new THREE.Color(0x2c3e5c), k),
        stars: 1 - k * .6, fogNear: 220, fogFar: 1900, fogColor: new THREE.Color(0x0d1626).lerp(new THREE.Color(0x1d2c44), k),
        hemi: .95 + .5 * k, hemiColor: new THREE.Color(0x7a8aa8), groundColor: new THREE.Color(0x24262a),
        sun: 1.1 + 1.1 * k, sunColor: new THREE.Color(0xc4d2f2), sunDisc: new THREE.Color(0), dark: 1, dustLight: .6 };
    },
    shots: {
      harbor: { pos: [150, 24, -160], look: [-50, 4, 10], drift: [-4, 0, 0], fov: 55 },
      'harbor-low': { pos: [130, 12, 54], look: [0, 4, -20], drift: [-3, 0, 0], fov: 55 },
      high: { pos: [-210, 48, 56], look: [40, 0, -10], drift: [3, 0, 0], fov: 55 },
      quay: { pos: [70, QY + 3.2, -22], look: [-30, QY - 1.4, -1], drift: [-2, 0, 0], fov: 55 },
      ship: { pos: [-10, 14, 22], look: [-80, 8, -14], drift: [-2, 0, 0], fov: 55 },
      street: { pos: [175, QY + 9, 60], look: [80, QY + 1, 36], drift: [-2, 0, 0], fov: 52 },
      'moon-tele': tele([20, 10, 30], 30, .02, -.1),
      'moon-sky': tele([40, QY + 1.7, 30], 60, .05),
    },
  };
}
