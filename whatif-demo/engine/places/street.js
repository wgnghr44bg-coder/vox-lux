// CITY STREET BY THE SEA (from earth-stops): a wide avenue along z running down to the sea,
// shops with flats above, palms and trees, lamps, signs, traffic lights, café furniture, cars in
// four lanes, people walking and crossing; skyscrapers near the sea.
//   can bend:   palms, trees, lamps, signs, traffic lights
//   can break:  palm fronds, trees, lamp heads, signs, loose things (paper, leaves, chairs, bins),
//               windows (beats.windows), facade chunks (beats.walls), whole top floors (beats.floors)
//   can fall:   the skyscrapers near the sea (rank 0..2 -> beats.falls)
//   can flood:  the sea at the end of the avenue rises up the street (water force)
// Beats: redLight [a, b], lookUp, shelter, carsStop, powerOut, windows, walls, floors, climax, falls[]
import * as THREE from 'three';
import { rng, hash, smooth, clamp, colorKeys } from '../util.js';
import { palm, coneTree, lamp, sign, car } from '../props.js';
import { crowd } from '../crowd.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed, facadeMats, facadeBox } = E, B = TL.beats, STOP = B.stop;
  const ROAD = 10, WALK = 16, ZEBRA = 10, SEA = -560;
  E.waterBase = -1.2;
  E.windArea = { x: 30, z0: -20, z1: -180 };
  E.groundAt = (x, z) => z < SEA ? -6 : 0;
  E.collide = (p, v, b) => {
    if (Math.abs(p[0]) > WALK - .3 && p[1] < 30 && b.kind !== 'floor' && p[0] * v[0] > 0) { p[0] = Math.sign(p[0]) * (WALK - .3); v[0] = -v[0] * .3; }
    // big pieces never reach the camera: they pile up before the crossing
    if ((b.kind === 'floor' || b.heavy >= 2 && b.kind !== 'car') && p[2] > (TL.debrisStop ?? -15) && v[2] > 0) { p[2] = TL.debrisStop ?? -15; v[2] = -v[2] * .15; }
  };

  { const g = new THREE.Mesh(new THREE.PlaneGeometry(400, 700), lam(0x3c3e41)); g.rotation.x = -Math.PI / 2; g.position.set(0, 0, -210); g.receiveShadow = true; scene.add(g); }
  for (const s of [-1, 1]) {
    const w = shadowed(new THREE.Mesh(new THREE.BoxGeometry(WALK - ROAD, 0.2, 620), lam(0x9b968c)), false); w.position.set(s * (ROAD + WALK) / 2, 0.1, -240); scene.add(w);
    const curb = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.22, 620), lam(0xb7b2a8)); curb.position.set(s * ROAD, 0.11, -240); scene.add(curb);
  }
  const paint = (w, d, x, z, col = 0xd9d6cc) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshLambertMaterial({ color: col }));
    m.rotation.x = -Math.PI / 2; m.position.set(x, 0.02, z); m.receiveShadow = true; scene.add(m); };
  paint(0.15, 620, -0.15, -240, 0xc9a94a); paint(0.15, 620, 0.15, -240, 0xc9a94a);
  for (let z = 60; z > -520; z -= 9) { paint(0.15, 4.5, -5, z); paint(0.15, 4.5, 5, z); }
  for (let x = -9; x <= 9; x += 1.6) paint(0.85, 4, x, ZEBRA);
  { const sea = new THREE.Mesh(new THREE.PlaneGeometry(6000, 3000), lam(0x2d6a72)); sea.rotation.x = -Math.PI / 2; sea.position.set(0, -1.2, SEA - 1500); scene.add(sea);
    E.floods.push({ mesh: sea, y: -1.2 });
    const flood = new THREE.Mesh(new THREE.PlaneGeometry(400, 800), lam(0x3d6f74)); flood.rotation.x = -Math.PI / 2; flood.position.set(0, -1.6, -200); scene.add(flood);
    E.floods.push({ mesh: flood, y: -1.6 });
    const prom = new THREE.Mesh(new THREE.BoxGeometry(400, 0.6, 12), lam(0xb9b1a0)); prom.position.set(0, 0.1, SEA + 5); scene.add(prom); }

  // buildings: near ones storey by storey (floors can tear away), far ones in one piece
  const floorsNear = [];
  { const R = rng(5);
    for (const s of [-1, 1]) {
      let z = 70, lot = 0;
      while (z > -540) {
        const len = 14 + R() * 14;
        if (lot > 0 && lot % 3 === 0) z -= 16;
        lot++;
        const depth = 14 + R() * 10, cz = z - len / 2, cx = s * (WALK + depth / 2), near = cz > -130;
        const floors = cz < -260 ? 0 : near ? 3 + Math.floor(R() * 7) : 5 + Math.floor(R() * 9);
        const color = E.PALETTE[Math.floor(R() * 8)];
        if (floors === 0) { z -= len; continue; }
        const gf = shadowed(new THREE.Mesh(facadeBox(depth, 4.2, len - .4), facadeMats(color, 'shop'))); gf.position.set(cx, 2.1, cz); scene.add(gf);
        const b = { s, cz, cx, len, depth, color, floors: [] };
        if (near) { for (let f = 0; f < floors; f++) { const m = shadowed(new THREE.Mesh(facadeBox(depth, 3.5, len - .4), facadeMats(color, 'win'))); m.position.set(cx, 4.2 + 1.75 + f * 3.5, cz); scene.add(m); b.floors.push(m); } floorsNear.push(b); }
        else { const h = floors * 3.5, m = new THREE.Mesh(facadeBox(depth, h, len - .4), facadeMats(color, 'win')); m.position.set(cx, 4.2 + h / 2, cz); m.receiveShadow = true; scene.add(m); }
        z -= len;
      }
      for (let z2 = 40; z2 > -520; z2 -= 22 + R() * 10) { const h = 14 + R() * 40, m = new THREE.Mesh(facadeBox(20, h, 20), facadeMats(E.PALETTE[Math.floor(R() * 8)], 'win')); m.position.set(s * (WALK + 30 + R() * 10), h / 2, z2); scene.add(m); }
      for (let i = 0; i < 6; i++) {
        const h = 70 + R() * 110, w = 18 + R() * 12, cz = -280 - i * 42 - R() * 10, cx = s * (WALK + w / 2 + R() * 26);
        const g = new THREE.Group(); g.position.set(cx, 0, cz + w / 2); scene.add(g);
        const m = new THREE.Mesh(facadeBox(w, h, w, 4), facadeMats(E.TOWER_PAL[Math.floor(R() * 5)], 'tower')); m.position.set(0, h / 2, -w / 2); g.add(m);
        E.falls.push({ g, h, w, cx, cz, base: 0, dir: [0, 1], near: Math.abs(cx) + (cz + 280) * .3 });
      }
    }
    E.falls.sort((a, b) => a.near - b.near).forEach((f, i) => { if (i < 3) f.rank = i; });
  }

  // props
  for (let z = 26, i = 0; z > -200; z -= 17, i++) { palm(E, -13.6, z - (i % 2) * 4, 8 + hash(i, 1) * 3, 100 + i); palm(E, 13.6, z - 8 - (i % 2) * 3, 8 + hash(i, 2) * 3, 200 + i); }
  for (let z = 18, i = 0; z > -160; z -= 17, i++) { coneTree(E, -12.4, z - 8, 1 + hash(i, 4) * .3, i); coneTree(E, 12.4, z, 1 + hash(i, 5) * .3, i + 50); }
  for (let z = 34, i = 0; z > -260; z -= 26, i++) for (const s of [-1, 1]) lamp(E, s * 10.8, z - (s > 0 ? 13 : 0), s);
  sign(E, -11.2, 2, 0x2f5d46); sign(E, 11.2, -12, 0x2f5d46); sign(E, -11.2, -30, 0x2d4f7a, 1, 1); sign(E, 11.2, -44, 0x2f5d46);
  sign(E, -11.2, -66, 0x8a3a30, .8, .8, 2.6); sign(E, 11.2, -80, 0x2d4f7a, 1, 1); sign(E, -11.2, -100, 0x2f5d46);
  // traffic lights at the crossing (red during beats.redLight, dead after beats.powerOut)
  const tl = [];
  for (const [x, z, face] of [[10.6, ZEBRA + 3.5, 1], [-10.6, ZEBRA - 3.5, -1]]) {
    const g = new THREE.Group(); g.position.set(x, .2, z); scene.add(g);
    const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.12, .14, 6, 6), lam(0x3f4245))); pole.position.y = 3; g.add(pole);
    const arm = new THREE.Mesh(new THREE.BoxGeometry(5, .14, .14), lam(0x3f4245)); arm.position.set(-Math.sign(x) * 2.5, 5.9, 0); g.add(arm);
    const head = new THREE.Group(); head.position.set(-Math.sign(x) * 4.6, 5.2, 0); g.add(head);
    head.add(shadowed(new THREE.Mesh(new THREE.BoxGeometry(.45, 1.3, .35), lam(0x2a2c2e))));
    const bulbs = [0, 1, 2].map(i => { const b = new THREE.Mesh(new THREE.CircleGeometry(.13, 10), new THREE.MeshBasicMaterial({ color: 0x222222 }));
      b.position.set(0, .4 - i * .4, face * .18); if (face < 0) b.rotation.y = Math.PI; head.add(b); return b; });
    tl.push({ g, head, bulbs });
    E.bend.push({ pose(t, F) { const L = F.lateral(t); head.rotation.x = smooth(.08, .75, L.a) * .5; g.rotation.x = smooth(.75, 1.6, L.a) * .45; } });
  }
  E.powerOut = t => t > (B.powerOut ?? 1e9);
  E.updates.push(t => { const [r0, r1] = B.redLight || [1e9, 1e9];
    const st = E.powerOut(t) ? -1 : t > r0 - 1 && t < r0 ? 1 : t >= r0 && t < r1 ? 0 : 2;
    tl.forEach(l => l.bulbs.forEach((b, i) => b.material.color.setHex(st === i ? [0xc4392f, 0xd99a2b, 0x4fae6a][i] : 0x222222))); });

  // cars in four lanes
  { const R = rng(44);
    [[-7.4, 1], [-2.6, 1], [2.6, -1], [7.4, -1]].forEach(([x, dir], li) => { for (let k = 0; k < 4; k++) {
      const z0 = dir > 0 ? -20 - k * (30 + R() * 25) : 30 - k * (30 + R() * 25) - 10;
      car(E, li * 7 + k, { x0: x, z0, dir, v: 9 + R() * 3, axis: 'z', a: -280, b: 60, brakeT: (B.carsStop ?? 1e9) + R() * 2.2, F, ...(TL.carWind != null && { strength: { wind: TL.carWind + hash(li, k) * .1 } }) });
    } }); }
  // loose things: they go when the force passes their strength
  { const R = rng(51);
    for (let i = 0; i < 60; i++) { const sd = R() < .5 ? -1 : 1, st = { wind: (14 + R() * 40) / 400 };
      const inst = E.slot(E.IM.paper, 1); E.body({ kind: 'paper', inst, k: .7, lift: .35, mu: .4, spin: 3, hy: .01, hx: .16, hz: .2, p: [sd * (10.5 + R() * 5), .22, 10 - R() * 90], r: [-Math.PI / 2, R() * 6, 0], strength: st }); }
    for (let i = 0; i < 90; i++) { const sd = R() < .5 ? -1 : 1, st = { wind: (10 + R() * 50) / 400 };
      const inst = E.slot(E.IM.leaf, 1, R() < .5 ? 0x6d7a45 : 0x8c7a4a); E.body({ kind: 'leaf', inst, k: .9, lift: .4, mu: .4, spin: 4, hy: .01, hx: .1, hz: .1, p: [sd * (11 + R() * 4), .22, 18 - R() * 120], r: [-Math.PI / 2, R() * 6, 0], strength: st }); }
    for (let i = 0; i < 12; i++) { const g = new THREE.Group(), c = lam(0x6e5a44);
      const seat = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.45, .06, .45), c)); g.add(seat);
      const back = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.45, .45, .05), c)); back.position.set(0, .25, -.2); g.add(back);
      for (const [x, z] of [[-.2, -.2], [.2, -.2], [-.2, .2], [.2, .2]]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.04, .45, .04), c); l.position.set(x, -.24, z); g.add(l); }
      scene.add(g); E.body({ kind: 'chair', obj: g, k: .07, lift: .25, mu: .5, spin: 1.2, hx: .25, hy: .47, hz: .25, p: [12 + R() * 3, .67, -18 - R() * 10], r: [0, R() * 6, 0], strength: { wind: (65 + R() * 40) / 400, water: .9 } }); }
    for (let i = 0; i < 6; i++) { const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.3, .26, .9, 7), lam(0x3f5446))); scene.add(m);
      E.body({ kind: 'bin', obj: m, k: .035, lift: .15, mu: .6, spin: 1, hx: .3, hy: .45, hz: .3, p: [(i % 2 ? -1 : 1) * 10.6, .65, 6 - i * 16], r: [0, 0, 0], strength: { wind: (130 + R() * 50) / 400 }, density: .5 }); }
  }

  // scripted damage: windows, wall chunks, whole top floors (only if the scenario has these beats)
  const nearB = floorsNear.filter(b => b.cz > -95 && b.cz < 30), R = rng(71), dir = F.dirFall || [0, 1];
  if (B.windows != null) {
    for (let i = 0; i < 300; i++) {
      const b = nearB[Math.floor(R() * nearB.length)], f = Math.floor(R() * Math.max(1, b.floors.length));
      const t0 = B.windows + Math.max(0, (b.cz - 20) / -40) * 1.4 + R() * 1.2 + (i > 200 ? 4 + R() * 8 : 0);
      E.body({ kind: 'shard', inst: E.slot(E.IM.shard, .4 + R() * 1.2), k: .32, lift: .25, mu: .5, spin: 6, hy: .02, hx: .2, hz: .2,
        p: [b.s * (WALK - .1), 4.2 + 1.5 + f * 3.5 + (R() - .5) * 1.5, b.cz + (R() - .5) * (b.len - 2)], r: [R() * 6, R() * 6, R() * 6], v0: [-b.s * (3 + R() * 6), R() * 3, R() * 4], tRel: t0, hidden: true });
    }
    E.EVENTS.push({ t: B.windows, kind: 'glass', e: .6 });
    E.updates.push(t => { for (const b of floorsNear) { const broken = t > B.windows + Math.max(0, (b.cz - 20) / -40) * 1.4 && b.cz > -95 && b.cz < 30;
      for (const m of b.floors) m.material = facadeMats(b.color, broken ? 'broken' : 'win'); } });
  }
  if (B.walls != null) {
    for (let i = 0; i < 200; i++) {
      const b = nearB[Math.floor(R() * nearB.length)], f = Math.floor(R() * Math.max(1, b.floors.length)), sz = .5 + R() * R() * 2.6;
      const inst = E.slot(E.IM.chunk, sz, new THREE.Color(b.color).multiplyScalar(.85 + R() * .25)); if (!inst) break;
      inst.sv = [sz * (1 + R()), sz * (.4 + R() * .6), sz * (.6 + R())];
      E.body({ kind: 'chunk', inst, k: .05 / sz, lift: .3, mu: .7, spin: 1.2 / sz, heavy: sz > 1.2 ? 1 : 0, hx: sz * .7, hy: sz * .35, hz: sz * .6,
        p: [b.s * (WALK - sz * .4), 4.2 + 1.5 + f * 3.5, b.cz + (R() - .5) * (b.len - 2)], r: [R(), R(), R()], v0: [-b.s * (1 + R() * 4), R() * 2, R() * 3],
        tRel: B.walls + R() * (STOP - B.walls - 1) * Math.pow(R(), .6), hidden: true });
    }
    E.EVENTS.push({ t: B.walls, kind: 'crack', e: .6 });
  }
  if (B.floors != null) {
    const sched = [];
    nearB.forEach(b => b.floors.forEach((m, f) => sched.push({ b, m, f, top: b.floors.length - 1 - f })));
    sched.sort((a, c) => a.top - c.top || (c.b.cz - a.b.cz) * (hash(a.f, 3) - .5));
    sched.forEach((s, i) => { if (s.top > 3) return;
      const at = B.floors + (i < 3 ? i * .7 : 2 + Math.pow((i - 3) / sched.length, .8) * (STOP - B.floors - 3)) + hash(i, 9) * .6;
      E.body({ kind: 'floor', obj: s.m, k: .0032, lift: .5, mu: .6, bounce: .12, spin: .12, heavy: 3, hx: s.b.depth / 2, hy: 1.75, hz: (s.b.len - .4) / 2,
        p: [s.m.position.x, s.m.position.y, s.m.position.z], r: [0, 0, 0], v0: [-s.b.s * 4.5 + dir[0] * 3, 2, dir[1] * 3], tRel: at });
      if (at < STOP) E.EVENTS.push({ t: at, kind: 'tear', e: .5 }); });
  }
  crowd(E, TL, { n: 26, axis: 'z', lane: [11, 15], range: [-140, 25], door: (along, acr) => Math.sign(acr || 1) * 16.6, seed: 31 });
  crowd(E, TL, { n: 14, axis: 'z', lane: [-15, -11], range: [-140, 25], door: () => -16.6, seed: 32 });

  E.brandSpot = { pos: [11.5, 14.5, -52], ry: -.18, w: 10, h: 5.8, posts: 11.6, shot: 'avenue' };   // billboard on two poles on the pavement, facing down the avenue
  const sky = colorKeys(THREE, [[0, 0x7aa3cc, 0xd3dde2]]);
  E.sunOffset = new THREE.Vector3(-90, 110, 120);
  return {
    ambience: 'stad',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 120, fogFar: 900, hemi: 1.5, hemiColor: new THREE.Color(0xe3ecf4), groundColor: new THREE.Color(0x5a5448),
      sun: 2.4, sunColor: new THREE.Color(0xffeedd) }),
    shots: {
      avenue: { pos: [-1, 3.2, 42], look: [-1, 26, -200], drift: [0, 0, -1.8], fov: 60 },
      crossing: { pos: [-13, 1.7, 22], look: [4, 3, 0], drift: [.5, 0, -.5], fov: 60 },
      pavement: { pos: [15.3, 1.8, 4], look: [12.5, 5, -60], drift: [0, 0, -1.5], fov: 60 },
      sea: { pos: [-1, 12, -150], look: [0, 30, -400], drift: [0, 0, -2], fov: 55 },
      wide: { pos: [-1, 3.2, 42], look: [-1, 26, -200], drift: [0, 0, -1.8], fov: 60 },
    },
  };
}
