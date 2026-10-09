// NATURE PARK / VOLCANO COUNTRY: a park road (along x) through pine forest and meadows, a viewpoint
// pull-out with a railing over a big lake, a log visitor centre with a parking lot, far ridges of an old
// caldera on the horizon (E.vent: where an eruption would come from), mountains all around.
//   can shake:  trees, lamps, signs (quake force: F.lateral oscillates)
//   can crack:  road, viewpoint, parking lot (E.crackSpots, quake force)
//   can steam:  vents in forest and meadow (E.steamSpots, quake / eruption force)
//   can fall:   sign panels, bins, picnic stuff (E.breaks, strength.quake); the watchtower (E.falls rank 0)
//   can burn:   forest patches (E.fireSpots, heat / eruption)
//   can flood:  the lake (water force)
// Beats: lookUp, shelter, evacuate (cars leave in a line), carsStop; TL.alarm (sirens + roadblock, props-alarm.js)
import * as THREE from 'three';
import { rng, hash, colorKeys, smooth } from '../util.js';
import { coneTree, roundTree, lamp, car } from '../props.js';
import { crowd } from '../crowd.js';
import { sirenPole, roadblock } from '../props-alarm.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  const LAKE = { x: -30, z: -290, r: 230 };
  const inLake = (x, z) => Math.hypot(x - LAKE.x, (z - LAKE.z) * 1.5) < LAKE.r;
  const hill = (x, z) => { const d = Math.hypot(x, z + 100); return Math.max(0, d - 420) * .1 + Math.sin(x * .011) * Math.cos(z * .013) * 2.2 * Math.min(1, Math.abs(z) / 40); };
  const drop = z => -15 * smooth(-22, -135, z);          // from the road the land falls away to the lake (the viewpoint looks down on it)
  E.groundAt = (x, z) => inLake(x, z) ? -18 : drop(z) + (Math.abs(z) < 30 ? 0 : hill(x, z));
  E.waterBase = -15.5;
  E.dustColor = [.62, .58, .5];
  E.vent = [120, 60, -2400];          // the caldera, far beyond the lake (eruption force)
  E.windArea = { x: 0, z0: 40, z1: -200 };

  // ground: meadow green with darker forest floor, gentle hills
  { const g = new THREE.PlaneGeometry(4000, 4000, 90, 90); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(3);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, E.groundAt(x, z) + (R() - .5) * .3 - (inLake(x, z) ? 0 : 0)); }
    g.computeVertexNormals(); const m = lam(0x7d8a52); const gr = new THREE.Mesh(g, m); gr.receiveShadow = true; scene.add(gr); E.ashGround = [m]; E.frost.push(m); }
  { const lake = new THREE.Mesh(new THREE.CircleGeometry(LAKE.r, 48), lam(0x4f7e8c)); lake.rotation.x = -Math.PI / 2; lake.scale.y = 1 / 1.5;
    lake.position.set(LAKE.x, -15.5, LAKE.z); scene.add(lake); E.floods.push({ mesh: lake, y: -15.5 }); E.lake = lake; }
  // far mountains and the low, long caldera rim (flat-topped ridges, not a cone)
  { const R = rng(19), rock = [0x4f5a4c, 0x5a6352, 0x4a5246];
    for (let i = 0; i < 18; i++) {
      const a = i / 18 * Math.PI * 2 + R() * .15, d = 1500 + R() * 800, h = 120 + R() * 170, r = 600 + R() * 340;
      const x = Math.sin(a) * d, z = -Math.cos(a) * d - 200;
      if (Math.abs(a - Math.PI * 2) < .5 || a < .5) continue;     // keep the view to the caldera open
      const m = shadowed(new THREE.Mesh(new THREE.ConeGeometry(r, h, 6 + Math.floor(R() * 3), 1), lam(rock[i % 3])), false);
      m.position.set(x, h / 2 - 30, z); m.rotation.y = R() * 6; scene.add(m); (E.ashTops ||= []).push(m.material);
    }
    for (let i = 0; i < 7; i++) {             // the rim: wide flat ridges along the horizon
      const x = -1500 + i * 520 + R() * 120, z = -2300 - R() * 300, w = 700 + R() * 300, h = 150 + R() * 90;
      const g = new THREE.CylinderGeometry(w * .55, w, h, 7, 1); g.scale(1, 1, .35);
      const m = shadowed(new THREE.Mesh(g, lam(0x55604f)), false); m.position.set(x, h / 2 - 20, z); scene.add(m); E.ashTops.push(m.material);
    }
  }

  // the park road (along x) with a centre line, the viewpoint pull-out and the visitor centre lot
  const asphalt = lam(0x55585a);
  const road = new THREE.Mesh(new THREE.PlaneGeometry(1400, 9), asphalt); road.rotation.x = -Math.PI / 2; road.position.set(0, .04, 0); road.receiveShadow = true; scene.add(road);
  for (let x = -690; x < 700; x += 9) { const l = new THREE.Mesh(new THREE.PlaneGeometry(4, .18), lam(0xd9c25a)); l.rotation.x = -Math.PI / 2; l.position.set(x, .06, 0); scene.add(l); }
  const pull = new THREE.Mesh(new THREE.PlaneGeometry(46, 14), asphalt); pull.rotation.x = -Math.PI / 2; pull.position.set(10, .045, -11); pull.receiveShadow = true; scene.add(pull);
  const lot = new THREE.Mesh(new THREE.PlaneGeometry(56, 26), asphalt); lot.rotation.x = -Math.PI / 2; lot.position.set(-120, .045, 19); lot.receiveShadow = true; scene.add(lot);
  for (let i = 0; i < 12; i++) { const s = new THREE.Mesh(new THREE.PlaneGeometry(.15, 5), lam(0xe6e2d8)); s.rotation.x = -Math.PI / 2; s.position.set(-146 + i * 4.6, .06, 26); scene.add(s); }
  E.crackSpots = [
    { x: 64, z: -1, len: 26, ang: .5, w: .5, at: .25 },        // across the road (POV shot 'road')
    { x: 92, z: 2, len: 18, ang: 2.3, w: .35, at: .45 },
    { x: 8, z: -12, len: 20, ang: .15, w: .3, at: .35 },       // viewpoint
    { x: -116, z: 18, len: 22, ang: 2.7, w: .35, at: .55 },    // parking lot
  ];

  // railing + benches + info board at the viewpoint
  { const m = lam(0x6b5038);
    for (let x = -12; x <= 32; x += 2.2) { const p = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.14, 1.1, .14), m)); p.position.set(x, .55, -17.6); scene.add(p); }
    const rail = shadowed(new THREE.Mesh(new THREE.BoxGeometry(44.2, .12, .12), m)); rail.position.set(10, 1.05, -17.6); scene.add(rail);
    const board = new THREE.Group(); board.position.set(26, 0, -15); scene.add(board);
    for (const sx of [-.9, .9]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.14, 2, .14), m)); l.position.set(sx, 1, 0); board.add(l); }
    const pan = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.2, .1), lam(0x5a4632))); pan.position.y = 2.1; board.add(pan);
    const face = new THREE.Mesh(new THREE.PlaneGeometry(1.9, .9), lam(0xc9b98e)); face.position.set(0, 0, .06); pan.add(face);
    E.breaks.push({ src: pan, strength: { quake: .62, wind: .7 }, k: .05, mu: .6, spin: 1, hx: 1.1, hy: .6, hz: .05, heavy: 1, v0: [0, 1, 1.5] });
  }
  // the visitor centre: a long log lodge with a deep roof, a porch, flag, bins and picnic tables
  { const g = new THREE.Group(); g.position.set(-120, 0, 44); scene.add(g);
    const hall = shadowed(new THREE.Mesh(E.facadeBox(30, 7, 14, 4, 3.5), E.facadeMats(0x7a5236, 'chalet'))); hall.position.y = 3.5; g.add(hall);
    const sh = new THREE.Shape(); sh.moveTo(-9, 0); sh.lineTo(9, 0); sh.lineTo(0, 6); sh.closePath();
    const rg = new THREE.ExtrudeGeometry(sh, { depth: 33, bevelEnabled: false }); rg.translate(0, 0, -16.5); rg.rotateY(Math.PI / 2);
    const roofM = lam(0x4a4a44); const roof = shadowed(new THREE.Mesh(rg, roofM)); roof.position.y = 7; g.add(roof); (E.ashRoofs ||= []).push(roofM);
    const glass = new THREE.Mesh(new THREE.PlaneGeometry(10, 4), lam(0x3c4a52)); glass.position.set(0, 2.4, -7.02); glass.rotation.y = Math.PI; g.add(glass);
    const porch = shadowed(new THREE.Mesh(new THREE.BoxGeometry(16, .3, 4), lam(0x6b5038))); porch.position.set(0, .15, -9); g.add(porch);
    const sign = new THREE.Group(); sign.position.set(-120, 0, 8); scene.add(sign);
    for (const sx of [-1.6, 1.6]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.3, 2.6, .3), lam(0x5a4632))); l.position.set(sx, 1.3, 0); sign.add(l); }
    const sp = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.2, .2), lam(0x5a4632))); sp.position.y = 2.6; sign.add(sp);
    const bar = new THREE.Mesh(new THREE.PlaneGeometry(3, .25), new THREE.MeshBasicMaterial({ color: 0xe6dcc0 })); bar.position.set(0, .15, .11); sp.add(bar);
    const bar2 = bar.clone(); bar2.scale.x = .6; bar2.position.y = -.25; sp.add(bar2);
    E.breaks.push({ src: sp, strength: { quake: .7 }, k: .05, mu: .6, spin: 1, hx: 1.9, hy: .6, hz: .1, heavy: 1, v0: [0, .5, -1] });
    const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.06, .08, 10, 6), lam(0xb9bcbc))); pole.position.set(-100, 5, 30); scene.add(pole);
    const flag = new THREE.Mesh(new THREE.PlaneGeometry(2.2, 1.3), lam(0x3f6f9a, { side: THREE.DoubleSide })); flag.position.set(-98.9, 9.2, 30); scene.add(flag);
    E.updates.push((t, Fo) => { flag.rotation.y = Math.sin(t * 2.3) * .25; flag.rotation.z = (Fo.lateral(t).dx || 0) * .2; });
    const R = rng(41);
    for (let i = 0; i < 6; i++) {        // bins and picnic tables: things that topple in a quake
      const bin = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.35, .3, 1, 8), lam(0x3d4a3a))); bin.position.set(-140 + i * 7 + R() * 2, .5, 34 + R() * 2); scene.add(bin);
      E.breaks.push({ src: bin, strength: { quake: .5 + R() * .3 }, k: .05, mu: .5, spin: 2, hx: .35, hy: .5, hz: .35, heavy: .5, v0: [(R() - .5) * 2, .5, (R() - .5) * 2] });
    }
    for (let i = 0; i < 4; i++) { const tg = new THREE.Group(); tg.position.set(-80 + i * 6, 0, 40 + (i % 2) * 4); scene.add(tg);
      const top = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2, .08, .9), lam(0x7a5a3e))); top.position.y = .75; tg.add(top);
      for (const sz of [-.75, .75]) { const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2, .06, .3), lam(0x7a5a3e))); b.position.set(0, .45, sz); tg.add(b); }
      for (const sx of [-.8, .8]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.08, .75, 1.6), lam(0x5a4632)); l.position.set(sx, .37, 0); tg.add(l); } }
  }
  // fire lookout tower on a hill (rank 0: can fall)
  { const g = new THREE.Group(); const x = 210, z = -95, y0 = E.groundAt(x, z); g.position.set(x, y0, z); scene.add(g); const m = lam(0x6b5038);
    for (const [sx, sz] of [[-2, -2], [2, -2], [-2, 2], [2, 2]]) { const l = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.3, 16, .3), m)); l.position.set(sx * .8, 8, sz * .8); l.rotation.set(sz * -.03, 0, sx * .03); g.add(l); }
    const cab = shadowed(new THREE.Mesh(E.facadeBox(5, 3, 5, 2.5, 3), E.facadeMats(0x7a5236, 'win'))); cab.position.y = 17.5; g.add(cab);
    const rf = shadowed(new THREE.Mesh(new THREE.ConeGeometry(4.4, 2, 4), lam(0x4a4a44))); rf.position.y = 20; rf.rotation.y = Math.PI / 4; g.add(rf);
    E.falls.push({ g, h: 21, w: 6, cx: x, cz: z, base: y0, rank: 0, big: .5, mode: 'topple', dir: [.3, 1] });
  }

  // forest: pines and some broadleaf trees, kept off the road, the lot, the viewpoint view and the lake
  const R = rng(14), wedge = (x, z) => z < -8 && z > -150 && Math.abs(x - 10) < 40 + (-z) * 1.1, free = (x, z) => !(inLake(x, z) || Math.abs(z) < 16 || (x > 165 && x < 310 && z > -40 && z < 45) || (x > 140 && x < 230 && z < -10 && z > -110 && Math.abs((z + 20) / -75 * 60 + 150 - x) < 22) || (x > -160 && x < -70 && z > 0 && z < 60) || (wedge(x, z) && (z > -70 || hash(Math.round(x), Math.round(z)) > .12)) || (x > 195 && x < 225 && z > -110 && z < -80));
  E.fireSpots = [];
  for (let i = 0; i < 520; i++) {          // near trees: real props (they sway and shake)
    const x = (R() - .5) * 560, z = 90 - R() * 380;
    if (!free(x, z)) continue;
    const y = E.groundAt(x, z);
    if (R() < .8) coneTree(E, x, z, 2.2 + R() * 2.2, 3000 + i, { color: [0x2f4a32, 0x35523a, 0x2a4230][i % 3], y });
    else roundTree(E, x, z, 1.8 + R() * 1.2, 3000 + i, { y });
    if (i % 90 === 7) E.fireSpots.push([x, y + 3, z]);
  }
  { // far forest: one instanced mesh of simple pine cones out to the hills
    const geo = new THREE.ConeGeometry(2.6, 9, 6); geo.translate(0, 4.5, 0);
    const m = lam(0x2e4631), N = 5000, im = new THREE.InstancedMesh(geo, m, N), D = new THREE.Object3D(); let k = 0;
    for (let i = 0; i < N * 3 && k < N; i++) {
      const a = R() * Math.PI * 2, d = 260 + Math.pow(R(), .7) * 1100, x = Math.sin(a) * d, z = -Math.cos(a) * d - 120;
      if (!free(x, z) || z > 260) continue;
      D.position.set(x, E.groundAt(x, z) - .3, z); D.scale.setScalar(1 + R() * 1.4); D.rotation.y = R() * 6; D.updateMatrix(); im.setMatrixAt(k++, D.matrix);
    }
    im.count = k; im.castShadow = false; im.receiveShadow = true; scene.add(im); E.frost.push(m); E.forestMat = m;
  }
  // steam vents in the forest and meadow (hot springs that wake up)
  E.steamSpots = [[-30, 0, -120, 1], [70, 0, -170, 1.4], [150, 0, -60, .9], [-180, 0, -90, 1.2], [260, 0, -220, 1.6], [40, 0, -60, .8]]
    .map(([x, , z, s]) => [x, E.groundAt(x, z), z, s]);

  // traffic: tourists drive slowly; at beats.evacuate everyone leaves in a long line (lane z = +2.2, +x)
  const ev = B.evacuate ?? 1e9;
  { const v = ev < 1e8 ? 6 : 11, t0 = ev < 1e8 ? ev + 4 : 0;   // the queue passes the exit shot a few seconds after the alarm
    for (let k = 0; k < 18; k++) car(E, 640 + k, { x0: 70 + k * 11 - v * t0, z0: 2.2, dir: 1, v, axis: 'x', a: -700, b: 700, brakeT: 1e9, F, strength: {} }); }
  crowd(E, TL, { n: 14, axis: 'x', lane: [26, 34], range: [-150, -90], door: () => 46, seed: 73 });

  // alarm (small brick): siren pole by the road, a roadblock on the way in
  if (TL.alarm !== false) {
    sirenPole(E, TL, 150, 9, { on: TL.alarm?.siren ?? B.evacuate });
    roadblock(E, TL, 250, -2.2, { on: TL.alarm?.block ?? B.evacuate, ry: 0 });
  }

  E.brandSpot = { pos: [-112, 2.6, 8.3], ry: 0, w: 3, h: 1, posts: 0, shot: 'lodge' };
  const sky = colorKeys(THREE, [[0, 0x4f86c0, 0xcfdde6]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [120, 140, 90]));
  return {
    ambience: 'park',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 250, fogFar: 2600, hemi: 1.3, hemiColor: new THREE.Color(0xe6eef4), groundColor: new THREE.Color(0x6e6a52),
      sun: 2.3, sunColor: new THREE.Color(0xfff1dc), sunDisc: new THREE.Color(0x998877) }),
    shots: {
      viewpoint: { pos: [14, 3.4, 9], look: [20, -30, -700], drift: [0, 0, -1], fov: 52 },                     // behind the railing: lake, forest, the rim
      lake: { pos: [100, -5, -110], look: [-150, -14, -380], drift: [-1, 0, 0], fov: 55 },                     // lake shore, steam over the forest
      lodge: { pos: [-92, 3, -6], look: [-125, 4, 34], drift: [-1.2, 0, 0], fov: 56 },                        // visitor centre and lot
      road: { pos: [76, 1.65, -6.8], look: [60, -1.6, 1], drift: [-.5, 0, 0], fov: 62 },                           // POV: the crack runs over the asphalt
      exit: { pos: [276, 3.2, 13], look: [205, 2, -2], drift: [0, 0, .5], fov: 52 },                             // siren, roadblock, cars leaving
      'pov-lot': { pos: [-104, 1.65, 4], look: [-125, 1.5, 22], drift: [0, 0, 0], fov: 64, run: { amp: .03, freq: 1.6 } },   // empty lot, alone
      tower: { pos: [150, 4, -20], look: [210, 14, -95], drift: [-.5, 0, 0], fov: 50 },
      vista: { pos: [-40, 40, 160], look: [60, 20, -1200], drift: [2, 0, -1], fov: 58 },                     // high over the forest to the caldera
    },
  };
}
