// REGIONAL AIRPORT IN FARMLAND: a runway (along x) with a taxiway, an apron with parked airliners, a glass
// terminal, a control tower, a fence, and fields all around (crop strips, a farm). Flat country, far horizon.
//   can cover:  fields, apron, planes, roofs (eruption ash cover, cold frost)
//   can bend:   trees, windsock
// Beats: lookUp, shelter (people at the terminal), carsStop
import * as THREE from 'three';
import { rng, hash, colorKeys } from '../util.js';
import { roundTree, coneTree, lamp, car } from '../props.js';
import { block } from '../blocks.js';
import { crowd } from '../crowd.js';
import { airliner } from '../props-air.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  E.groundAt = () => 0; E.waterBase = -50; E.dustColor = [.6, .58, .52];
  E.ashGround = []; E.ashRoofs ||= [];
  const flat = (w, d, x, z, col, y = .02) => { const m = lam(col, { flatShading: false }); const g = new THREE.Mesh(new THREE.PlaneGeometry(w, d), m); g.rotation.x = -Math.PI / 2; g.position.set(x, y, z); g.receiveShadow = true; scene.add(g); E.ashGround.push(m); return g; };
  flat(6000, 6000, 0, 0, 0x7f8a55, 0);
  // fields: long strips of crops in different colours
  { const R = rng(3), cols = [0xb9a85a, 0x8a9a4a, 0x6f8a45, 0xa48e52, 0x7a6a48, 0x9aa860];
    for (let i = 0; i < 70; i++) { const x = -1800 + (i % 10) * 360 + R() * 40, z = 160 + Math.floor(i / 10) * -260 + (Math.floor(i / 10) > 1 ? -420 : 0);
      if (z < 120 && z > -420) continue; flat(330, 230, x, z, cols[Math.floor(R() * cols.length)], .03); } }
  // runway, taxiway, apron
  flat(2400, 46, 0, -260, 0x4a4c4f, .05); flat(1600, 22, 0, -170, 0x55575a, .05); flat(380, 110, 0, -80, 0x6a6c6e, .05);
  for (let x = -1150; x < 1150; x += 40) { const l = new THREE.Mesh(new THREE.PlaneGeometry(22, .9), lam(0xe8e4d8)); l.rotation.x = -Math.PI / 2; l.position.set(x, .07, -260); scene.add(l); E.ashGround.push(l.material); }
  for (let k = 0; k < 6; k++) { const l = new THREE.Mesh(new THREE.PlaneGeometry(.6, 60), lam(0xd9c25a)); l.rotation.x = -Math.PI / 2; l.position.set(-150 + k * 60, .07, -105); scene.add(l); }
  // parked airliners on the apron (stand numbers along the terminal), one on the taxiway
  [[-150, -95], [-90, -95], [-30, -95], [30, -95], [90, -95]].forEach(([x, z], i) => airliner(E, x, z, Math.PI, { color: [0xe9ebec, 0xe9ebec, 0xf1efe6, 0xe9ebec, 0xe4e6e8][i], stripe: [0x2f5d8a, 0xb8352b, 0x2f6b5a, 0x8a2f5d, 0x3a3f8a][i] }));
  airliner(E, 260, -170, -Math.PI / 2, { stripe: 0xc98a2a });
  // terminal: long low glass building with a deep roof; control tower
  { const t = shadowed(new THREE.Mesh(E.facadeBox(320, 12, 34, 6, 4), E.facadeMats(0xb9bcbc, 'tower', 0x5a5e62))); t.position.set(0, 6, -16); scene.add(t);
    const roof = shadowed(new THREE.Mesh(new THREE.BoxGeometry(330, 1.2, 42), lam(0x8a8e92))); roof.position.set(0, 12.6, -16); scene.add(roof); E.ashRoofs.push(roof.material);
    const tw = new THREE.Group(); tw.position.set(200, 0, -40); scene.add(tw);
    const shaft = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(3, 3.6, 34, 10), lam(0xc9c6bc))); shaft.position.y = 17; tw.add(shaft);
    const cab = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(6.5, 5, 5, 10), lam(0x3c4a52))); cab.position.y = 36.5; tw.add(cab);
    const cap = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(7.2, 7.2, 1, 10), lam(0x8a8e92))); cap.position.y = 39.5; tw.add(cap); E.ashRoofs.push(cap.material);
    const beacon = new THREE.Mesh(new THREE.SphereGeometry(.5, 8, 6), new THREE.MeshBasicMaterial({ color: 0x5a2420 })); beacon.position.y = 41; tw.add(beacon);
    E.updates.push(t => beacon.material.color.setHex(Math.sin(t * 6) > .6 ? 0xff3a2a : 0x5a2420));
  }
  // land side: parking, a road with cars, hangars, a farm with trees
  flat(300, 60, 0, 40, 0x55575a, .04);
  for (let i = 0; i < 4; i++) block(E, { x: 340 + i * 70, z: -70, w: 60, d: 40, floors: 3, color: 0x9aa0a4, storey: 5, kind: 'dark' });
  { const R = rng(7); for (let i = 0; i < 40; i++) { const x = -260 + R() * 520, z = 30 + R() * 22; if (R() < .55) car(E, 900 + i, { x0: x, z0: z, dir: 1, v: 0, axis: 'x', a: -400, b: 400, brakeT: -1, F, strength: {} }); } }
  [[2, 1], [6, -1]].forEach(([dz, dir], li) => [0, 1, 2].forEach(k => car(E, 950 + li * 5 + k, { x0: -500 + k * 260 + li * 90, z0: 80 + dz, dir, v: 12, axis: 'x', a: -900, b: 900, brakeT: (B.carsStop ?? 1e9) + k * .6, F, strength: {} })));
  flat(1800, 9, 0, 84, 0x3c3e41, .05);
  for (let x = -400, i = 0; x < 400; x += 36, i++) lamp(E, x, 72, 1, { y: 0 });
  { const R = rng(11); for (let i = 0; i < 90; i++) { const x = -900 + R() * 1800, z = 110 + R() * 50; if (R() < .6) roundTree(E, x, z, 1.3 + R(), 1200 + i); else coneTree(E, x, z, 2 + R(), 1300 + i); } }
  // fence along the apron
  for (let x = -400; x < 400; x += 6) { const p = new THREE.Mesh(new THREE.BoxGeometry(.1, 2.4, .1), lam(0x6d6f72)); p.position.set(x, 1.2, -140); scene.add(p); }
  crowd(E, TL, { n: 16, axis: 'x', lane: [24, 34], range: [-120, 120], door: () => 2, seed: 77 });

  E.brandSpot = { pos: [30, 4, 1.2], ry: 0, w: 6, h: 2.4, posts: 0, shot: 'landside' };
  const sky = colorKeys(THREE, [[0, 0x6f9cc8, 0xd2dbe0]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-140, 180, 120]));
  return {
    ambience: 'stad',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 300, fogFar: 3200, hemi: 1.4, hemiColor: new THREE.Color(0xe6ecf2), groundColor: new THREE.Color(0x6e6a52),
      sun: 2.3, sunColor: new THREE.Color(0xfff1dc), sunDisc: new THREE.Color(0x998877) }),
    shots: {
      apron: { pos: [-75, 9, -40], look: [0, 3, -100], drift: [2, 0, 0], fov: 56 },                  // in front of the terminal, over the parked planes                    // from the terminal roof over the parked planes
      runway: { pos: [-260, 5, -150], look: [-50, 4, -95], drift: [2, 0, 0], fov: 50 },              // along the taxiway at the grounded planes               // empty runway, nobody takes off
      tower: { pos: [150, 2, -10], look: [200, 30, -40], drift: [0, 0, 0], fov: 58 },
      'pov-window': { pos: [-40, 4.6, -33.6], look: [-30, 3.5, -100], drift: [1, 0, 0], fov: 62 },    // behind the terminal glass, at the planes
      landside: { pos: [60, 2.2, 66], look: [10, 4, -10], drift: [-1, 0, 0], fov: 56 },               // parking and the terminal front
      fields: { pos: [-700, 70, 300], look: [200, -20, -700], drift: [4, 0, -2], fov: 58 },             // high over the fields and the airport
    },
  };
}
