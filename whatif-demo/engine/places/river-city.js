// RIVER CITY WITH A SUSPENSION BRIDGE
// River along x (z -330..-30, water y -10), bridge along z at x = 0 (towers at z -45 and -315,
// 270 m main span). South quay (camera side): promenade, trees, lamps, road, a row of houses.
// North quay: old brick warehouses and a water tower in front, modern towers behind.
//   can bend:   trees, lamp posts, the bridge deck and its cables (sag), car suspension
//   can break:  branches, chimneys, balconies, bridge hangers, the middle of the deck (beats.deckBreak)
//   can fall:   warehouses, water tower (rank 0..3, scripted by beats.falls)
//   can flood:  river rises over both quays (water force)
// Beats: carsStop, hangers, deckBreak, lookUp, shelter, falls[]
import * as THREE from 'three';
import { rng, hash, smooth, clamp, colorKeys, lerp, noise } from '../util.js';
import { coneTree, roundTree, lamp, bench, car } from '../props.js';
import { block, tower, waterTower } from '../blocks.js';
import { crowd } from '../crowd.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats, STOP = B.stop;
  const WATER = -10, BED = -18, S_QUAY = -30, N_QUAY = -330;
  E.waterBase = WATER;
  E.dustColor = [.68, .6, .52];
  E.groundAt = (x, z) => z < S_QUAY && z > N_QUAY ? BED : 0;
  E.windArea = { x: 60, z0: -20, z1: -300 };

  // ---------- land, quays, river ----------
  const ground = (w, d, x, z, col) => { const g = new THREE.Mesh(new THREE.PlaneGeometry(w, d), lam(col)); g.rotation.x = -Math.PI / 2; g.position.set(x, 0, z); g.receiveShadow = true; scene.add(g); E.frost.push(g.material); return g; };
  ground(3000, 700, 0, S_QUAY + 350, 0x8c877c);
  ground(3000, 1400, 0, N_QUAY - 700, 0x86817a);
  ground(3000, 10, 0, S_QUAY + 5, 0xb3aa98);                                   // promenade paving
  for (const [z, s] of [[S_QUAY, 1], [N_QUAY, -1]]) {
    const wall = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3000, 18.6, 3), lam(0x8f8778)), false); wall.position.set(0, -9 + .3, z - s * 1.5); scene.add(wall);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(3000, .5, 1.6), lam(0xc2b9a6)); cap.position.set(0, .25, z + s * .4); scene.add(cap);
  }
  const bed = new THREE.Mesh(new THREE.PlaneGeometry(3000, 300), lam(0x3d3a33)); bed.rotation.x = -Math.PI / 2; bed.position.set(0, BED, (S_QUAY + N_QUAY) / 2); scene.add(bed);
  { const g = new THREE.PlaneGeometry(4000, 1400, 80, 28); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(3);
    for (let i = 0; i < p.count; i++) p.setY(i, (R() - .5) * .35);
    g.computeVertexNormals();
    const water = new THREE.Mesh(g, lam(0x3e6670)); water.position.set(0, WATER, (S_QUAY + N_QUAY) / 2 - 300 + 300); water.receiveShadow = true;
    water.scale.z = 300 / 1400; scene.add(water);
    E.floods.push({ mesh: water, y: WATER, wave: true });
    // a second, large sheet that only shows once the river leaves its banks
    const flood = new THREE.Mesh(new THREE.PlaneGeometry(4000, 3000), lam(0x4a6a70)); flood.rotation.x = -Math.PI / 2; flood.position.set(0, WATER - .4, 0); scene.add(flood);
    E.floods.push({ mesh: flood, y: WATER - .4 });
  }
  // far hills
  for (let i = 0; i < 9; i++) { const h = new THREE.Mesh(new THREE.IcosahedronGeometry(260 + hash(i, 1) * 200, 1), lam(0x7a876e)); h.scale.y = .22; h.position.set(-1600 + i * 420, -10, -2100 - hash(i, 2) * 300); scene.add(h); }

  // ---------- the bridge ----------
  const T1 = -45, T2 = -315, MID = (T1 + T2) / 2, HALF = (T1 - T2) / 2, DECK0 = 9, CREST = 4, TOP = 74;
  const SAG = TL.place_?.sag ?? 7;           // metres the deck sags at the full force
  const breakT = B.deckBreak ?? 1e9, GAP = [MID - 16, MID + 16];
  const sagAt = t => SAG * Math.pow(clamp(F.droop(t)), 1.3) + (F.kind === 'wind' ? 0 : 0);
  const hangAt = (z, t) => { const a = smooth(breakT, breakT + 2.2, t); if (!a) return 0;
    const dz = z > GAP[1] ? z - GAP[1] : z < GAP[0] ? GAP[0] - z : 0; return a * 9 * Math.exp(-dz / 30); };
  const deckY = (z, t) => {
    if (z > T1 || z < T2) return DECK0;
    const u = (z - MID) / HALF; return DECK0 + CREST * (1 - u * u) - sagAt(t) * (1 - u * u) - hangAt(z, t);
  };
  E.deckY = deckY;
  const asphalt = lam(0x4a4c4e), steel = lam(0x6b5f55), steelD = lam(0x55504a), rail = lam(0x8a8478);
  const deckMats = [steel, steel, asphalt, steelD, steel, steel];
  const segs = [], SEG = 6;
  for (let z = 100; z > -420; z -= SEG) {
    const zc = z - SEG / 2, g = new THREE.Group(); scene.add(g);
    const d = shadowed(new THREE.Mesh(new THREE.BoxGeometry(21, 2, SEG + .05), deckMats)); g.add(d);
    for (const sx of [-1, 1]) { const r = new THREE.Mesh(new THREE.BoxGeometry(.2, 1.1, SEG), rail); r.position.set(sx * 10.3, 1.5, 0); g.add(r);
      const w = new THREE.Mesh(new THREE.BoxGeometry(2.6, .25, SEG), lam(0x9a958a)); w.position.set(sx * 9, 1.1, 0); g.add(w); }
    for (const lx of [-5, 0, 5]) { const m = new THREE.Mesh(new THREE.PlaneGeometry(.15, 3), new THREE.MeshLambertMaterial({ color: lx ? 0xd9d6cc : 0xc9a94a }));
      m.rotation.x = -Math.PI / 2; m.position.set(lx, 1.02, 0); g.add(m); }
    const inGap = zc > GAP[0] && zc < GAP[1];
    segs.push({ g, zc, inGap });
    if (z > T1 + 4 || z < T2 - 4) {   // approach viaduct piers
      if (Math.round(zc) % 24 === 0 || Math.abs(zc - S_QUAY) < 3) for (const sx of [-7, 7]) {
        const p = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2, DECK0 - BED, 2), lam(0x9a9284))); p.position.set(sx, (DECK0 + BED) / 2 - 1, zc); scene.add(p);
      }
    }
  }
  // the middle of the deck breaks away and drops into the river
  segs.filter(s => s.inGap).forEach((s, i) => {
    E.body({ kind: 'deck', obj: s.g, tRel: breakT + Math.abs(i - 2.5) * .05, p: [0, deckY(s.zc, breakT), s.zc], r: [0, 0, 0], k: .002, mu: .7, spin: .08, heavy: 3, hx: 10.5, hy: 1, hz: SEG / 2, density: 3,
      drive: t => ({ p: [0, deckY(s.zc, t), s.zc], r: [0, 0, 0], v: [0, 0, 0] }), v0: [(i % 2 ? 1 : -1) * .6, -2, (i - 2.5) * .5] });
    s.body = true;
  });
  // towers
  const towerM = lam(0x7a6e62), towerL = lam(0x8e8274);
  for (const tz of [T1, T2]) {
    for (const sx of [-1, 1]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.6, TOP - BED + 2, 3.6), towerM)); l.position.set(sx * 11.5, (TOP + BED) / 2 + 1, tz); scene.add(l); }
    for (const y of [DECK0 - 3, 40, TOP - 1]) { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(25.6, 2.4, 3), towerL)); b.position.set(0, y, tz); scene.add(b); }
    const pier = shadowed(new THREE.Mesh(new THREE.BoxGeometry(30, 10, 9), lam(0x8f8778))); pier.position.set(0, BED + 5 + 2, tz); scene.add(pier);
  }
  // main cables: parabola from tower top to just above the deck, sinking with the deck
  const cableY = (z, t) => {
    if (z <= T1 && z >= T2) { const u = (z - MID) / HALF; return 15.5 + (TOP - 15.5) * u * u - sagAt(t) * (1 - u * u) - hangAt(z, t) * .25; }
    const [za, ya] = z > T1 ? [100, DECK0 + 2] : [-420, DECK0 + 2], zt = z > T1 ? T1 : T2, u = (z - zt) / (za - zt);
    return TOP + (ya - TOP) * (u * .75 + u * u * .25);
  };
  const cableM = lam(0x3f3a36), NC = 70, cables = [];
  const cylY = new THREE.CylinderGeometry(.42, .42, 1, 5); cylY.rotateX(Math.PI / 2);
  for (const sx of [-10.6, 10.6]) {
    const pts = []; for (let i = 0; i <= NC; i++) pts.push(100 - i * (520 / NC));
    const ms = pts.slice(0, -1).map(() => { const m = new THREE.Mesh(cylY, cableM); m.castShadow = true; scene.add(m); return m; });
    cables.push({ sx, pts, ms });
  }
  // hangers every 9 m on the main span; some snap (beats.hangers), all in the gap go with the deck
  const hangers = [], hangM = lam(0x2f2c2a), R = rng(17);
  for (let z = T1 - 9; z > T2 + 4; z -= 9) for (const sx of [-10.6, 10.6]) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(.14, 1, .14), hangM); scene.add(m);
    const inGap = z > GAP[0] - 6 && z < GAP[1] + 6, near = Math.abs(z - MID) < 70;
    const snap = inGap ? breakT - .15 - R() * .4 : (near && R() < .4 && B.hangers != null) ? B.hangers + R() * Math.max(.5, breakT - B.hangers - 1) : 1e9;
    hangers.push({ m, z, sx, snap });
    if (snap < STOP) E.EVENTS.push({ t: snap, kind: 'snap', e: .5, x: sx, z });
  }
  E.gritSources = [{ x: 0, y: 12, z: MID, w: 20, d: 60 }];

  E.updates.push((t, F) => {
    for (const s of segs) {
      if (s.body) continue;
      const y0 = deckY(s.zc + SEG / 2, t), y1 = deckY(s.zc - SEG / 2, t);
      s.g.position.set(0, (y0 + y1) / 2, s.zc); s.g.rotation.set(Math.atan2(y0 - y1, SEG) * -1, 0, 0);
    }
    for (const c of cables) for (let i = 0; i < c.ms.length; i++) {
      const za = c.pts[i], zb = c.pts[i + 1], ya = cableY(za, t), yb = cableY(zb, t), m = c.ms[i];
      m.position.set(c.sx, (ya + yb) / 2, (za + zb) / 2); m.scale.set(1, 1, Math.hypot(za - zb, ya - yb) + .1);
      m.rotation.set(Math.atan2(-(ya - yb), za - zb), 0, 0);
    }
    for (const h of hangers) {
      const yc = cableY(h.z, t), yd = deckY(h.z, t) + 1;
      let top = yc, bot = yd;
      if (t > h.snap) { const a = t - h.snap; bot = Math.max(yd, yc - 4 - 2 * Math.exp(-a * 3) * Math.sin(a * 14)); }   // dangling end
      h.m.position.set(h.sx, (top + bot) / 2, h.z); h.m.scale.y = Math.max(.1, top - bot);
    }
  });

  // cars on the bridge: stop well before the middle (no one is on the span when it breaks)
  const lanes = [[-7.5, -1], [-2.5, -1], [2.5, 1], [7.5, 1]];
  lanes.forEach(([x, dir], li) => {
    const v = 11 + li * .6, brake = (B.carsStop ?? 1e9) + li * .7;
    const z0s = [0, 1, 2].map(k => -60 - k * 170 - hash(li, k) * 30);
    let shift = 0;
    const stopZ = z0 => { const a = -470, b = 150, len = b - a, d = v * (brake + shift) + v * 1.1; return a + (((z0 + dir * d) - a) % len + len) % len; };
    for (let k = 0; k < 60 && z0s.some(z0 => { const z = stopZ(z0); return z < -40 && z > -330; }); k++) shift += .1;
    z0s.forEach((z0, k) => {
      const c = car(E, li * 10 + k, { x0: x, z0, dir, v, axis: 'z', a: -470, b: 150, brakeT: brake + shift, F, strength: { wind: .35 + hash(li, k) * .1 } });
      const base = c.drive; c.drive = t => { const d = base(t); d.p[1] = deckY(d.p[2], t) + 1.8; return d; };
    });
  });
  // the quay road along the south bank, under the viaduct
  [[6, 1], [10, -1]].forEach(([z, dir], li) => [0, 1, 2, 3].forEach(k => {
    const brake = (B.carsStop ?? 1e9) + 1 + k * .4 + li;
    const c = car(E, 100 + li * 10 + k, { x0: -300 + k * 160 + li * 60, z0: z, dir, v: 10, axis: 'x', a: -400, b: 400, brakeT: brake, F });
  }));
  { const road = new THREE.Mesh(new THREE.PlaneGeometry(3000, 12), lam(0x3c3e41)); road.rotation.x = -Math.PI / 2; road.position.set(0, .02, 8); road.receiveShadow = true; scene.add(road); }

  // ---------- south quay: promenade ----------
  for (let x = -260, i = 0; x < 260; x += 16, i++) {
    if (Math.abs(x) < 14) continue;
    roundTree(E, x, -18.5, 1 + hash(i, 4) * .25, 300 + i);
    if (i % 2 === 0) lamp(E, x + 8, -27, 1);
    if (i % 3 === 1) bench(E, x + 4, -25, Math.PI);
  }
  for (let x = -300; x < 300; x += 2.4) { const p = new THREE.Mesh(new THREE.BoxGeometry(.12, 1.1, .12), lam(0x3d3f42)); p.position.set(x, .75, S_QUAY + .6); scene.add(p); }
  { const r = new THREE.Mesh(new THREE.BoxGeometry(600, .1, .1), lam(0x3d3f42)); r.position.set(0, 1.3, S_QUAY + .6); scene.add(r); }
  // row of houses behind the road
  { const R2 = rng(8); let x = -320;
    while (x < 320) { const w = 14 + R2() * 12; if (Math.abs(x + w / 2) > 18) block(E, { x: x + w / 2, z: 34, w, d: 20, floors: 3 + Math.floor(R2() * 4), color: E.PALETTE[Math.floor(R2() * 8)], balconies: [0, -1], chimneys: 1 }); x += w + .5; } }
  crowd(E, TL, { n: 26, axis: 'x', lane: [-24, -16], range: [-60, 92], door: () => 23, seed: 41 });

  // ---------- north quay: warehouses, water tower; towers behind ----------
  { const R3 = rng(9); let x = -380; let rank = 0;
    const featured = { '40': 0, '128': 2, '-64': 3 };
    while (x < 420) {
      const w = 22 + R3() * 18, cx = x + w / 2, floors = 4 + Math.floor(R3() * 4), brick = [0x8f4a3a, 0x9c5a44, 0x7a4636, 0xa8846a][Math.floor(R3() * 4)];
      let fall = null;
      for (const k in featured) if (Math.abs(cx - +k) < w / 2 + 2) { fall = { rank: featured[k], big: 1.2 }; delete featured[k]; break; }
      if (!fall && R3() < .2) fall = { strength: { gravity: .97 + R3() * .2 }, big: .9 };
      block(E, { x: cx, z: N_QUAY - 16, w, d: 26, floors, color: brick, storey: 3.8, chimneys: 2, fall });
      x += w + 1 + (R3() < .25 ? 12 : 0);
    }
    waterTower(E, { x: 92, z: N_QUAY - 46, y: 0, h: 36, fall: { rank: 1, big: .8 } });
    for (let i = 0; i < 26; i++) {
      const h = 50 + R3() * 120, w = 22 + R3() * 18;
      tower(E, { x: -500 + i * 40 + R3() * 20, z: N_QUAY - 90 - R3() * 260, w, h, color: E.TOWER_PAL[Math.floor(R3() * 5)] });
    }
    for (let x2 = -380; x2 < 420; x2 += 14) roundTree(E, x2, N_QUAY - 2.5, 1.1, 700 + x2);
  }

  // ---------- light ----------
  E.brandSpot = { pos: [46, 5.2, -28.6], ry: Math.PI / 2, w: 6, h: 3, posts: 3.6, shot: 'quay' };   // billboard on the promenade
  const sky = colorKeys(THREE, [[0, 0x7aa3cc, 0xd3dde2]]);
  E.sunOffset = new THREE.Vector3(-170, 230, 110);
  const P = {
    ambience: 'rivier',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 220, fogFar: 1900, hemi: 1.45, hemiColor: new THREE.Color(0xe3ecf4), groundColor: new THREE.Color(0x5a5448),
      sun: 2.4, sunColor: new THREE.Color(0xffeedd), sunDisc: new THREE.Color(0x998866) }),
    shots: {
      wide: { pos: [-150, 9, -12], look: [-12, 24, -185], drift: [4, .3, -4], fov: 54 },
      deck: { pos: [.5, DECK0 + 5.2, 34], look: [0, 19, -160], drift: [0, 0, -6], fov: 62 },
      span: { pos: [52, -4, -112], look: [0, 8, -182], drift: [-2, .2, -1], fov: 50 },
      under: { pos: [34, WATER + 3, -72], look: [0, 14, -175], drift: [0, .3, -4], fov: 60 },
      quay: { pos: [80, 2.6, -24.5], look: [0, 6, -14], drift: [-5, 0, 0], fov: 60 },
      north: { pos: [70, 3, -26], look: [70, 22, -360], drift: [-5, 0, 0], fov: 34, shake: .5 },
      towers: { pos: [125, 3, -26], look: [108, 24, -360], drift: [-3, 0, 0], fov: 30, shake: .4 },
    },
  };
  return P;
}
