// SUBURB WITH A PARK AND A SUPERMARKET (baksteen park/buitenwijk): a residential road along x (z = 0),
// gabled houses with front lawns and cars in the driveways on the north side, a park with paths, a pond,
// benches and big trees on the south side, and a supermarket with a parking lot (abandoned trolleys, cars).
//   time.js: E.wildArea (road, lot, paths), E.roofs (roofs that sag over the years)
//   can bend:   trees, lamps (wind)
//   can flood:  the pond (water force)
// Beats: carsStop (the few driving cars stop), lookUp, shelter. Shots: wide, street, park, pond, shop, lot, houses, 'pov-park', 'pov-street'
import * as THREE from 'three';
import { rng, hash, colorKeys } from '../util.js';
import { roundTree, coneTree, lamp, bench, car } from '../props.js';
import { house } from '../blocks.js';
import { crowd } from '../crowd.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  E.waterBase = -.6;
  E.groundAt = () => 0;
  E.roofs = [];
  const plane = (w, d, x, z, col, y = .01) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), lam(col)); m.rotation.x = -Math.PI / 2; m.position.set(x, y, z); m.receiveShadow = true; scene.add(m); return m; };
  plane(1600, 1600, 0, 0, 0x6c7a4c, 0);                       // lawns and fields
  plane(600, 8, 0, 0, 0x45474a, .02);                          // road
  for (const s of [-1, 1]) { const w = shadowed(new THREE.Mesh(new THREE.BoxGeometry(600, .15, 2.4), lam(0xa8a398)), false); w.position.set(0, .075, s * 5.2); scene.add(w); }
  for (let x = -290; x < 290; x += 9) plane(4.5, .15, x, 0, 0xd9d6cc, .03);

  // ---------- north side: houses, lawns, driveways, cars ----------
  const R = rng(17), HCOL = [0xd2c6ae, 0xc9b896, 0xb9a48a, 0xe0d8c8, 0xa7685a, 0x9fa6a0, 0xc4a85a], ROOF = [0x7a4a3a, 0x5d5a58, 0x6e3e33, 0x4f4a48];
  for (let x = -140, i = 0; x < 140; x += 15 + R() * 4, i++) {
    const w = 8 + R() * 2, d = 9 + R() * 2, h = 5.4 + R() * 1.2, z = -15 - R() * 1.5;
    const H = house(E, { x, z, w, d, h, color: HCOL[Math.floor(R() * HCOL.length)], roof: ROOF[Math.floor(R() * ROOF.length)], chimney: R() < .6 });
    E.roofs.push({ m: H.g.children[1], h, side: R() < .5 ? -1 : 1, k: R() });
    plane(5.4, 9, x + w / 2 + 3.4, -9.6, 0x77736c, .025);                                  // driveway
    if (R() < .7) car(E, 500 + i, { x0: x + w / 2 + 3.4, z0: -10.5, dir: R() < .5 ? 1 : -1, v: 0, axis: 'z', brakeT: 0, F, strength: {} });
    if (R() < .6) roundTree(E, x - w / 2 - 2.5, -8.5, .8 + R() * .3, 520 + i);
    if (i % 3 === 0) lamp(E, x, -6.6, 1);
  }
  // ---------- south side: park ----------
  const PX0 = -120, PX1 = 8;
  for (let k = 0; k < 2; k++) plane(PX1 - PX0, 2.6, (PX0 + PX1) / 2, 20 + k * 22, 0xb5a789, .02);   // two paths along the park
  plane(2.6, 50, -55, 30, 0xb5a789, .021);
  { const pond = new THREE.Mesh(new THREE.CircleGeometry(14, 24), lam(0x3e6a70)); pond.rotation.x = -Math.PI / 2; pond.position.set(-85, -.05, 31); pond.scale.set(1.4, 1, 1); scene.add(pond);
    E.floods.push({ mesh: pond, y: -.05 });
    const rim = new THREE.Mesh(new THREE.RingGeometry(14, 15, 24), lam(0x8d8a7c)); rim.rotation.x = -Math.PI / 2; rim.position.set(-85, .03, 31); rim.scale.set(1.4, 1, 1); scene.add(rim); }
  for (let i = 0; i < 46; i++) { const x = PX0 + R() * (PX1 - PX0), z = 12 + R() * 48;
    if (Math.hypot((x + 85) / 1.4, z - 31) < 17 || Math.abs(z - 20) < 2.5 || Math.abs(z - 42) < 2.5 || Math.abs(x + 55) < 2.5) continue;
    (R() < .7 ? roundTree : coneTree)(E, x, z, 1.1 + R() * .7, 600 + i); }
  for (let x = PX0 + 10; x < PX1; x += 14) { bench(E, x, 18.2, 0); lamp(E, x + 5, 18.4, 1); }
  // ---------- supermarket + parking lot ----------
  const SX = 45, SZ = 40;
  plane(70, 28, SX, 18.5, 0x55575a, .022);
  for (let x = SX - 32; x < SX + 34; x += 3) plane(.12, 5, x, 15, 0xd9d6cc, .03);
  { const g = new THREE.Group(); g.position.set(SX, 0, SZ); scene.add(g);
    const body = shadowed(new THREE.Mesh(E.facadeBox(44, 6.5, 22, 4, 6.5), E.facadeMats(0xc9c3b4, 'shop'))); body.position.y = 3.25; g.add(body);
    const top = new THREE.Mesh(new THREE.BoxGeometry(45, .6, 23), lam(0x8a3a30)); top.position.y = 6.8; g.add(top);
    const cv = document.createElement('canvas'); cv.width = 512; cv.height = 96; const x = cv.getContext('2d');
    x.fillStyle = '#8a3a30'; x.fillRect(0, 0, 512, 96); x.fillStyle = '#f3ede2'; x.font = 'bold 64px sans-serif'; x.textAlign = 'center'; x.fillText('SUPERMARKET', 256, 72);
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(16, 3), new THREE.MeshLambertMaterial({ map: tex })); sign.position.set(0, 8.4, -11.6); sign.rotation.y = Math.PI; g.add(sign);
    const sb = new THREE.Mesh(new THREE.BoxGeometry(16.4, 3.4, .3), lam(0x5a2a24)); sb.position.set(0, 8.4, -11.4); g.add(sb);
    const glass = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.4), lam(0x2f3a42)); glass.position.set(0, 1.9, -11.02); glass.rotation.y = Math.PI; g.add(glass);
    E.shopGlass = glass; }
  const RL = rng(23);
  for (let i = 0; i < 9; i++) car(E, 560 + i, { x0: SX - 28 + i * 6.5 + RL() * 2, z0: 15 + (RL() - .5) * .5, dir: RL() < .5 ? 1 : -1, v: 0, axis: 'z', brakeT: 0, F, strength: {} });
  for (let i = 0; i < 7; i++) {                                // shopping trolleys left in the lot
    const g = new THREE.Group(), m = lam(0x9aa0a6); g.position.set(SX - 25 + RL() * 50, 0, 21 + RL() * 8); g.rotation.y = RL() * 6; scene.add(g);
    const bask = shadowed(new THREE.Mesh(new THREE.BoxGeometry(.6, .5, .9), new THREE.MeshLambertMaterial({ color: 0x9aa0a6, wireframe: true }))); bask.position.y = .75; g.add(bask);
    const base = new THREE.Mesh(new THREE.BoxGeometry(.5, .05, .8), m); base.position.y = .2; g.add(base);
    for (const [a, b] of [[-.22, -.35], [.22, -.35], [-.22, .35], [.22, .35]]) { const w = new THREE.Mesh(new THREE.CylinderGeometry(.06, .06, .04, 6), lam(0x1c1d1f)); w.rotation.z = Math.PI / 2; w.position.set(a, .06, b); g.add(w); }
  }
  for (const [i, [x, z, dir, color]] of (TL.parked || []).entries()) car(E, 590 + i, { x0: x, z0: z, dir, color, v: 0, axis: 'z', brakeT: 0, F, strength: {} });   // TL.parked: [[x, z, dir]] extra parked cars (e.g. a fox on the roof)
  // driving cars and people (only before the scenario empties the place)
  if (!TL.noTraffic) [[-2, 1], [2, -1]].forEach(([z, dir], li) => [0, 1].forEach(k => car(E, 580 + li * 3 + k, { x0: -200 + k * 140 + li * 50, z0: z, dir, v: 9, axis: 'x', a: -300, b: 300, brakeT: (B.carsStop ?? 1e9) + k, F })));
  crowd(E, TL, { n: 10, axis: 'x', lane: [4.4, 6], range: [-90, 70], door: () => -9, seed: 61 });

  E.wildArea = { x: [-120, 80], z: [-8, 32] };
  E.brandSpot = { pos: [SX - 14, 4, SZ - 11.3], ry: Math.PI, w: 6, h: 3.5, shot: 'shop' };
  const sky = colorKeys(THREE, [[0, 0x86aed2, 0xd6e0e4]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-100, 120, 90]));
  return {
    ambience: 'stad',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 140, fogFar: 900, hemi: 1.55, hemiColor: new THREE.Color(0xe6eef2), groundColor: new THREE.Color(0x5a5a46),
      sun: 2.4, sunColor: new THREE.Color(0xfff0dc), sunDisc: new THREE.Color(0xaa9977) }),
    shots: {
      wide: { pos: [-30, 22, 46], look: [10, 2, -10], drift: [3, 0, 0], fov: 55 },
      street: { pos: [-40, 1.8, 1.5], look: [40, 2, -3], drift: [2, 0, 0], fov: 55 },
      houses: { pos: [-6, 2.2, 7], look: [-10, 3.5, -16], drift: [1.5, 0, 0], fov: 55 },
      park: { pos: [-20, 2.2, 52], look: [-70, 3, 25], drift: [-1, 0, 0], fov: 55 },
      pond: { pos: [-58, 2.4, 49], look: [-88, 1, 30], drift: [-1, 0, 0], fov: 50 },
      shop: { pos: [32, 2, 8], look: [48, 4, 32], drift: [1.2, 0, 0], fov: 55 },
      lot: { pos: [8, 9, 4], look: [45, 1, 22], drift: [1.5, 0, 0], fov: 50 },
      'pov-park': { pos: [-55, 1.65, 52], look: [-50, 1.8, 0], drift: [0, 0, -9], fov: 62, run: { amp: .03, freq: 1.8 } },
      'pov-street': { pos: [-30, 1.65, 1.8], look: [30, 1.7, 4], drift: [9, 0, 0], fov: 62, run: { amp: .03, freq: 1.8 } },
    },
  };
}
