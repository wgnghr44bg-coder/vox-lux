// BEACH BOULEVARD: the sea along x (sea level y 0, waterline at z 0), a sandy beach rising to a
// sea wall, the boulevard at y 3 (promenade, palms, lamps, benches), a road and a row of hotels
// and apartment blocks. The ground rises gently inland, so rising water creeps up step by step.
//   can bend:   palms, lamps, beach umbrellas
//   can break:  palm fronds, lamp heads, umbrellas (wind), beach huts lift off (water)
//   can fall:   two old hotels (rank 0..1)
//   can flood:  beach (0..3 m), boulevard and road (3 m), the street behind (3..6 m)
// Beats: lookUp, shelter, carsStop, falls[]
import * as THREE from 'three';
import { rng, hash, smooth, clamp, colorKeys } from '../util.js';
import { palm, lamp, bench, car } from '../props.js';
import { block } from '../blocks.js';
import { crowd, sunbathers } from '../crowd.js';
import { lifebuoy } from '../lifebuoy.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  const WALL = 38, PROM = 3;
  E.waterBase = 0;
  E.dustColor = [.74, .7, .62];
  // ground height: sea bed, beach slope, boulevard terrace, town rising gently inland
  const groundAt = (x, z) => z < 0 ? Math.max(-12, z * .06) : z < WALL ? z / WALL * 2.4 : z < 90 ? PROM : PROM + (z - 90) * .025;
  E.groundAt = groundAt;
  E.windArea = { x: 80, z0: 120, z1: -40 };

  // sea (big faceted sheet that rises with the water force)
  { const g = new THREE.PlaneGeometry(5000, 2400, 90, 40); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(4);
    for (let i = 0; i < p.count; i++) p.setY(i, (R() - .5) * .3); g.computeVertexNormals();
    const sea = new THREE.Mesh(g, lam(0x3a7078)); sea.position.set(0, 0, -1150); sea.receiveShadow = true; scene.add(sea);
    E.floods.push({ mesh: sea, y: 0, wave: true });
    const inland = new THREE.Mesh(new THREE.PlaneGeometry(5000, 600), lam(0x4a7579)); inland.rotation.x = -Math.PI / 2; inland.position.set(0, -.25, 250); scene.add(inland);
    E.floods.push({ mesh: inland, y: -.25 });
    // surf: white lines that follow the waterline
    const foam = new THREE.Mesh(new THREE.PlaneGeometry(5000, 1.4), new THREE.MeshLambertMaterial({ color: 0xe8ecea, transparent: true, opacity: .7 }));
    foam.rotation.x = -Math.PI / 2; scene.add(foam);
    E.updates.push((t, F, tv) => { const wy = F.field(t).waterY ?? 0, z = wy <= 2.4 ? Math.max(0, wy) / 2.4 * WALL : wy < PROM ? WALL : 90 + (wy - PROM) / .025;
      foam.position.set(0, wy + .06, z - .7 + Math.sin(tv * .8) * .5); foam.visible = wy < PROM + 4; });
  }
  // beach: sloped sand
  { const g = new THREE.PlaneGeometry(5000, WALL + 40, 40, 20); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const z = p.getZ(i) + (WALL - 40) / 2; p.setZ(i, z); p.setY(i, groundAt(p.getX(i), z) + (hash(i, 1) - .5) * .08); }
    g.computeVertexNormals(); const sand = new THREE.Mesh(g, lam(0xd8c79e)); sand.receiveShadow = true; scene.add(sand); E.frost.push(sand.material); }
  // sea wall + boulevard terrace + town ground
  { const wall = shadowed(new THREE.Mesh(new THREE.BoxGeometry(5000, PROM, 2), lam(0xb3a98f)), false); wall.position.set(0, PROM / 2 - .3, WALL); scene.add(wall);
    const prom = new THREE.Mesh(new THREE.BoxGeometry(5000, .4, 52), lam(0xc8bca2)); prom.position.set(0, PROM - .2, WALL + 26); prom.receiveShadow = true; scene.add(prom);
    const road = new THREE.Mesh(new THREE.PlaneGeometry(5000, 12), lam(0x3f4144)); road.rotation.x = -Math.PI / 2; road.position.set(0, PROM + .02, 76); road.receiveShadow = true; scene.add(road);
    const g = new THREE.PlaneGeometry(5000, 600, 1, 30); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const z = p.getZ(i) + 390; p.setZ(i, z); p.setY(i, groundAt(0, z)); }
    g.computeVertexNormals(); const town = new THREE.Mesh(g, lam(0x9b968c)); town.receiveShadow = true; scene.add(town);
    for (let x = -400; x < 400; x += 2.2) { const p2 = new THREE.Mesh(new THREE.BoxGeometry(.1, 1, .1), lam(0xd9d6cc)); p2.position.set(x, PROM + .5, WALL + .6); scene.add(p2); }
    const rail = new THREE.Mesh(new THREE.BoxGeometry(800, .1, .12), lam(0xd9d6cc)); rail.position.set(0, PROM + 1, WALL + .6); scene.add(rail); }

  // beach: umbrellas, beach huts, a lifeguard tower
  { const R = rng(12);
    for (let i = 0; i < 52; i++) {
      const x = i < 12 ? -26 + R() * 52 : -160 + R() * 320, z = 8 + R() * 22, y = groundAt(x, z);
      if ((TL.clear || []).some(([cx, cz]) => Math.hypot(x - cx, z - cz) < 7)) continue;
      const g = new THREE.Group(); g.position.set(x, y, z); scene.add(g);
      const pole = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.04, .04, 2.4, 4), lam(0xe0dccf))); pole.position.y = 1.2; g.add(pole);
      const top = shadowed(new THREE.Mesh(new THREE.ConeGeometry(1.3, .5, 8), lam([0xb5543f, 0x2f6d86, 0xd9b44a, 0xe6e1d6][Math.floor(R() * 4)]))); top.position.y = 2.4; g.add(top);
      E.burn.push({ mats: [top.material], pos: [x, y + 2.5, z], size: .8, sun: 9.5 + R() * 3.5, shrink: [top] });
      const ph = R() * 6;
      E.bend.push({ pose(t, F) { const L = F.lateral(t); g.rotation.x = smooth(.05, .4, L.a) * .4 * L.dz + Math.sin(t * 7 + ph) * L.a * .1; } });
      E.breaks.push({ src: top, strength: { wind: .15 + R() * .2, water: y + 1.6 }, k: .25, lift: .9, mu: .5, spin: 2, hx: 1.3, hy: .25, hz: 1.3, density: .3 });
      if (R() < .5) { const towel = new THREE.Mesh(new THREE.PlaneGeometry(.9, 1.8), lam([0xd2cbb8, 0x5e6f80, 0xb5653f][Math.floor(R() * 3)])); towel.rotation.x = -Math.PI / 2; towel.rotation.z = R(); towel.position.set(x + 1.2, y + .04, z + .5); scene.add(towel); }
    }
    for (let i = 0; i < 14; i++) {
      const x = -130 + i * 19 + R() * 4, z = 33, y = groundAt(x, z), col = [0xe6e1d6, 0x6f9bb0, 0xd9b44a, 0xb5543f, 0x7d9a6a][i % 5];
      const g = new THREE.Group(); scene.add(g);
      const box = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.6, 2.4, 2.4), lam(col))); box.position.y = 1.2; g.add(box);
      E.burn.push({ mats: [box.material], pos: [x, y + 1.6, z], size: 1.3, sun: 13 + R() * 3, charT: 8 });
      const roof = shadowed(new THREE.Mesh(new THREE.ConeGeometry(2.1, 1, 4), lam(0xe9e4d8))); roof.rotation.y = Math.PI / 4; roof.position.y = 2.9; g.add(roof);
      const door = new THREE.Mesh(new THREE.PlaneGeometry(1, 1.8), lam(0x4a3a2e)); door.position.set(0, 1, -1.21); door.rotation.y = Math.PI; g.add(door);
      E.body({ kind: 'hut', obj: g, p: [x, y + .02, z], r: [0, 0, 0], k: .05, lift: .2, mu: .7, spin: .3, hx: 1.3, hy: .02, hz: 1.2, density: .35, strength: { water: y + 1.2, wind: .75 + R() * .2 }, wob: .5 });
    }
    { const g = new THREE.Group(); g.position.set(40, groundAt(40, 20), 20); scene.add(g);
      for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = new THREE.Mesh(new THREE.BoxGeometry(.15, 4, .15), lam(0xe9e4d8)); l.position.set(sx * 1, 2, sz * 1); g.add(l); }
      const c = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.8, 2.6), lam(0xd8473a))); c.position.y = 4.9; g.add(c);
      const r = shadowed(new THREE.Mesh(new THREE.BoxGeometry(3, .2, 3), lam(0xe9e4d8))); r.position.y = 5.9; g.add(r); }
  }
  // boulevard
  const burnPalm = (g, i) => { if (Math.abs(g.position.x) < 160) E.burn.push({ mats: g.userData.frondMats, pos: [g.position.x, g.position.y + g.userData.crown, g.position.z], size: 1.7, sun: 11.5 + hash(i, 9) * 4, charT: 4, shrink: g.userData.fronds }); };
  for (let x = -300, i = 0; x < 300; x += 15, i++) {
    burnPalm(palm(E, x, WALL + 6, 8 + hash(i, 1) * 3, 400 + i, { y: PROM }), i);
    if (i % 2) lamp(E, x + 7.5, WALL + 4, -1, { y: PROM });
    if (i % 3 === 0) bench(E, x + 4, WALL + 3, 0).position.y = PROM;
  }
  for (let x = -300, i = 0; x < 300; x += 15, i++) burnPalm(palm(E, x + 7, 69.5, 7 + hash(i, 3) * 3, 500 + i, { y: PROM }), i + 50);
  // TL.hand: a parked car with frost, and your own gloved hand resting on its roof (POV 'pov-car')
  let handShot = null;
  if (TL.hand) {
    const [hx, hz] = TL.hand.car, roofY = PROM + .75 + .92;   // top of the frosted roof
    car(E, 690, { x0: hx, z0: hz, dir: 1, v: 0, axis: 'x', a: -320, b: 320, y: PROM + .75, brakeT: -1, F, ground: PROM, snow: true, color: 0x6c7a86 });
    const cam = TL.hand.cam, hand = new THREE.Group(), glove = lam(0x2b2f36);
    const palmM = new THREE.Mesh(new THREE.BoxGeometry(.11, .05, .16), glove); hand.add(palmM);
    const thumb = new THREE.Mesh(new THREE.BoxGeometry(.04, .04, .08), glove); thumb.position.set(-.07, 0, .02); thumb.rotation.y = .5; hand.add(thumb);
    const tip = new THREE.Vector3(hx + (cam[0] - hx) * .45, roofY + .03, hz + (cam[2] - hz) * .35);
    hand.position.copy(tip); hand.lookAt(cam[0], roofY + .03, cam[2]); scene.add(hand);
    const sh = new THREE.Vector3(cam[0] + .3, cam[1] - .45, cam[2]), arm = new THREE.Mesh(new THREE.CylinderGeometry(.045, .06, 1, 6), lam(0x3a4350));
    arm.position.copy(tip).add(sh).multiplyScalar(.5); arm.scale.y = tip.distanceTo(sh) - .06;
    arm.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), sh.clone().sub(tip).normalize()); scene.add(arm);
    const [t0, t1] = TL.hand.t || [0, 1e9]; E.updates.push((t, F, tv) => { hand.visible = arm.visible = tv >= t0 && tv <= t1; });
    handShot = { pos: cam, look: [hx, roofY - .1, hz], drift: [0, 0, 0], fov: 62 };
  }
  // cars on the boulevard road
  [[73, 1], [79, -1]].forEach(([z, dir], li) => [0, 1, 2, 3, 4].forEach(k => {
    car(E, 600 + li * 10 + k, { x0: -300 + k * 120 + li * 50, z0: z, dir, v: 9, axis: 'x', a: -320, b: 320, y: PROM + .75, brakeT: (B.carsStop ?? 1e9) + k * .5 + li, F, ground: PROM, ...(TL.carWind != null && { strength: { wind: TL.carWind + hash(li, k) * .1, water: PROM + .6 } }) });
  }));
  // hotels and apartments
  { const R = rng(21); let x = -360;
    const featured = { '-24': 0, '70': 1 };
    while (x < 360) {
      const w = 16 + R() * 16, cx = x + w / 2, tall = R() < .35;
      let fall = null; for (const k in featured) if (Math.abs(cx - +k) < w / 2 + 2) { fall = { rank: featured[k], big: 1 }; delete featured[k]; break; }
      block(E, { x: cx, y: PROM, z: 98, w, d: 18, floors: tall ? 10 + Math.floor(R() * 8) : 4 + Math.floor(R() * 4), color: [0xe9e4d8, 0xd2c6ae, 0xc9b896, 0xb9c4c8, 0xe0d2b4][Math.floor(R() * 5)],
        balconies: [0, -1], fall });
      x += w + 4;
    }
  }
  crowd(E, TL, { n: 26, axis: 'x', lane: [WALL + 2, WALL + 14], range: [-90, 90], door: () => 88, seed: 61, y: PROM + .2 });
  crowd(E, TL, { n: 12, axis: 'x', lane: [6, 30], range: [-80, 80], door: () => WALL + 8, seed: 62 });
  sunbathers(E, TL, { n: TL.sunbathers ?? 18, area: { x: [-22, 22], z: [6, 30] }, exit: WALL - 1, seed: 63, wake: TL.wake }); 
  if (F.kind === 'heat') E.emitters.push((tv, add, cam) => {      // the sea starts to steam
    const lv = F.level(Math.min(tv, B.stop)); if (lv < .45) return;
    const d = smooth(.45, 1, lv);
    for (let k = 0; k < 160 * d; k++) {
      const u = (tv * .12 + hash(k, 1)) % 1, x = cam.x + (hash(k, 2) - .5) * 160, z = -8 - hash(k, 3) * 150;
      add(x + u * 6, .5 + u * (6 + hash(k, 4) * 10), z, 6 + u * 14, Math.sin(u * Math.PI) * (TL.steam ?? .22) * d, .96, .96, .95, hash(k, 5) * 6);
    }
  });

  if (TL.lifebuoy) { const b = lifebuoy(E, { pos: [TL.lifebuoy[0], 0, TL.lifebuoy[1]], ry: .4 });
    E.updates.push((t, F, tv) => { const wy = F.field(t).waterY ?? 0; b.position.y = wy + .06 + Math.sin(tv * 1.3) * .04; b.rotation.z = Math.sin(tv * .9) * .05; }); }
  E.brandSpot = { type: 'flag', pos: [-17, groundAt(-17, 19.5), 19.5], ry: -Math.PI / 2 + .35, height: 5.5, w: 1.8, h: 2.6, shot: 'pov-beach' };   // beach flag
  const sky = colorKeys(THREE, [[0, 0x6ea6d3, 0xdfe7e6]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [120, 160, -60]));
  return {
    ambience: 'zee',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 180, fogFar: 1600, hemi: 1.55, hemiColor: new THREE.Color(0xe8eef2), groundColor: new THREE.Color(0x7a705e),
      sun: 2.5, sunColor: new THREE.Color(0xfff0dc), sunDisc: new THREE.Color(0xaa9977) }),
    shots: {
      wide: { pos: [-70, 14, 46], look: [10, 4, -10], drift: [4, 0, 0], fov: 55 },
      beach: { pos: [-30, 1.8, 12], look: [30, 3, 30], drift: [3, 0, 0], fov: 60 },
      boulevard: { pos: [-60, PROM + 1.9, 50], look: [20, PROM + 3, 46], drift: [3, 0, 0], fov: 60 },
      sea: { pos: [0, PROM + 10, 64], look: [0, 3, -100], drift: [0, 0, -2], fov: 58 },
      hotels: { pos: [10, 12, 14], look: [10, 16, 100], drift: [-2, 0, 0], fov: 58 },
      // POV shots for a person standing on the beach (eye height above the sand)
      'pov-sea': { pos: [12, groundAt(0, 27) + 1.65, 27], look: [-4, 3, -150], drift: [0, 0, -.6], fov: 62 },
      'pov-beach': { pos: [-30, groundAt(0, 18) + 1.65, 18], look: [30, 1.2, 14], drift: [.8, 0, 0], fov: 60 },
      'pov-back': { pos: [2, groundAt(0, 4) + 1.65, 4], look: [0, 4, 70], drift: [0, 0, .5], fov: 62 },
      'pov-balcony': { pos: [2, PROM + 4.2 + 2 * 3.5 + 1.6, 88.3], look: [-1, PROM, 74], drift: [0, 0, 0], fov: 62 },
      'balcony-zoom': { pos: [2, PROM + 4.2 + 2 * 3.5 + 1.6, 88.3], look: [-1, 7, 76], drift: [0, 0, 0], fov: 9 },
      'pov-lie': { pos: [3, groundAt(0, 26) + .55, 26], look: [-12, 30, -200], drift: [0, 0, 0], fov: 64 },
      'pov-run': { pos: [2, groundAt(0, 12) + 1.6, 12], look: [-2, 3.5, 90], drift: [0, .9, 32], fov: 66, run: { amp: .08, freq: 1.4 } },
      'pov-glance': { pos: [2, groundAt(0, 24) + 1.6, 24], look: [-10, 12, -160], drift: [0, .4, 12], fov: 66, run: { amp: .06, freq: 1.4 } },
      'pov-prom': { pos: [-12, PROM + 1.65, 52], look: [60, 7, 46], drift: [6, 0, 0], fov: 64, run: { amp: .05, freq: 1.3 } },
      'pov-sky': { pos: [12, groundAt(0, 27) + 1.65, 27], look: [-15, 45, -200], drift: [0, 0, 0], fov: 64 },
      ...(handShot && { 'pov-car': handShot }),
      'slow-prom': { pos: [-40, PROM + 2.2, 56], look: [40, PROM + 2, 52], drift: [12, 0, 0], fov: 60 },   // slow move along the empty boulevard
    },
  };
}
