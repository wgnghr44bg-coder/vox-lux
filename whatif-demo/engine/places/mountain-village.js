// SNOWY MOUNTAIN VILLAGE: a valley floor with chalets around a small square, a church with a
// steeple, a frozen-able lake, snowy pines, lamps, mountains all around.
//   can bend:   pines, lamps
//   can break:  chimneys, pine tops (wind), branches under snow load
//   can fall:   church steeple, barn (rank 0..1)
//   can flood:  the lake rises over the square (water force)
//   can freeze: lake, roofs, trees, ground (cold force); windows and lamps light up in the dark
// Beats: lookUp, shelter, falls[]
import * as THREE from 'three';
import { rng, hash, smooth, colorKeys } from '../util.js';
import { coneTree, lamp, car } from '../props.js';
import { house } from '../blocks.js';
import { crowd } from '../crowd.js';

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, B = TL.beats;
  const LAKE = { x: -60, z: -120, r: 70 };
  E.waterBase = -.6;
  E.dustColor = [.9, .92, .95];
  const inLake = (x, z) => Math.hypot(x - LAKE.x, (z - LAKE.z) * 1.4) < LAKE.r;
  E.groundAt = (x, z) => inLake(x, z) ? -3 : 0;
  E.windArea = { x: 60, z0: 20, z1: -150 };

  // snowy valley floor + lake
  { const g = new THREE.PlaneGeometry(3000, 3000, 60, 60); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(5);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), d = Math.hypot(x, z);
      p.setY(i, inLake(x, z) ? -3 : (R() - .5) * .25 + Math.max(0, d - 260) * .12); }
    g.computeVertexNormals(); const snow = new THREE.Mesh(g, lam(0xe9eef2)); snow.receiveShadow = true; scene.add(snow); E.melt.push({ mat: snow.material, bare: 0x7f7a58 }); }
  { const lake = new THREE.Mesh(new THREE.CircleGeometry(LAKE.r, 40), lam(0x46707c)); lake.rotation.x = -Math.PI / 2; lake.scale.y = 1 / 1.4;
    lake.position.set(LAKE.x, -.6, LAKE.z); scene.add(lake); E.floods.push({ mesh: lake, y: -.6 });
    const flood = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), lam(0x4d7480)); flood.rotation.x = -Math.PI / 2; flood.position.set(0, -.9, 0); scene.add(flood);
    E.floods.push({ mesh: flood, y: -.9 }); }
  // mountains: big faceted cones with snow caps
  { const R = rng(9);
    for (let i = 0; i < 16; i++) {
      const a = i / 16 * Math.PI * 2 + R() * .2, d = 520 + R() * 380, h = 260 + R() * 420, r = 260 + R() * 220;
      const x = Math.sin(a) * d, z = -Math.cos(a) * d - 80;
      const rock = shadowed(new THREE.Mesh(new THREE.ConeGeometry(r, h, 7 + Math.floor(R() * 3), 1), lam(0x6d6a66)), false); rock.position.set(x, h / 2 - 20, z); rock.rotation.y = R() * 6; scene.add(rock);
      const cap = new THREE.Mesh(new THREE.ConeGeometry(r * .45, h * .45, rock.geometry.parameters.radialSegments, 1), lam(0xf1f4f6)); cap.position.set(x, h - 20 - h * .225 + 1, z); cap.rotation.y = rock.rotation.y; scene.add(cap); E.melt.push({ mesh: cap, to: .45, late: true });
      E.fireSpots ??= []; if (i % 3 === 1) { const fx = x * .55, fz = z * .55 - 30; E.fireSpots.push([fx, Math.max(0, Math.hypot(fx, fz) - 260) * .12 + 2, fz]); }
      E.frost.push(rock.material);
    }
  }
  // the village
  const R = rng(14);
  const road = new THREE.Mesh(new THREE.PlaneGeometry(9, 600), lam(0x8f9294)); road.rotation.x = -Math.PI / 2; road.position.set(12, .03, -60); road.receiveShadow = true; scene.add(road);
  const square = new THREE.Mesh(new THREE.CircleGeometry(24, 24), lam(0xb8bcbf)); square.rotation.x = -Math.PI / 2; square.position.set(12, .04, -40); scene.add(square);
  const spots = [];
  for (let i = 0; i < 26; i++) {
    const side = i % 2 ? 1 : -1, along = -150 + Math.floor(i / 2) * 22 + R() * 6;
    const x = 12 + side * (20 + R() * 14), z = along;
    if (Math.hypot(x - 12, z + 40) < 26 || inLake(x, z) || inLake(x + 8, z)) continue;
    spots.push([x, z, side]);
  }
  spots.forEach(([x, z, side], i) => {
    const chalet = i % 3 !== 2;
    house(E, { x, z, w: 9 + R() * 4, d: 11 + R() * 4, h: chalet ? 6 : 8, ry: side > 0 ? -Math.PI / 2 : Math.PI / 2,
      color: chalet ? [0x7a5236, 0x8a5c3a, 0x6e4a32][i % 3] : [0xe6e1d6, 0xd9cdb4][i % 2], kind: chalet ? 'chalet' : 'win', roof: 0x4f3b2e, snow: true, roofH: 4.5 });
  });
  // church with a tall steeple at the square (can fall: rank 0)
  { const g = new THREE.Group(); g.position.set(-14, 0, -46); scene.add(g);
    const nave = shadowed(new THREE.Mesh(E.facadeBox(12, 10, 22, 6, 5), E.facadeMats(0xe9e4d8, 'win'))); nave.position.y = 5; g.add(nave);
    const sh = new THREE.Shape(); sh.moveTo(-6.6, 0); sh.lineTo(6.6, 0); sh.lineTo(0, 6); sh.closePath();
    const rg = new THREE.ExtrudeGeometry(sh, { depth: 23, bevelEnabled: false }); rg.translate(0, 0, -11.5);
    const roofM = lam(0xe9eef2); E.frost.push(roofM); E.melt.push({ mat: roofM, bare: 0x4a5a5e }); const r = shadowed(new THREE.Mesh(rg, roofM)); r.position.y = 10; g.add(r);
    const st = new THREE.Group(); st.position.set(0, 0, 14); g.add(st);
    const tw = shadowed(new THREE.Mesh(E.facadeBox(6, 26, 6, 6, 6), E.facadeMats(0xe9e4d8, 'win'))); tw.position.y = 13; st.add(tw);
    const sp = shadowed(new THREE.Mesh(new THREE.ConeGeometry(4.4, 14, 4), lam(0x4a5a5e))); sp.position.y = 33; sp.rotation.y = Math.PI / 4; st.add(sp);
    const cr = new THREE.Mesh(new THREE.BoxGeometry(.3, 2, .3), lam(0xc9a94a)); cr.position.y = 41; st.add(cr);
    E.falls.push({ g: st, h: 41, w: 7, cx: -14, cz: -32, base: 0, rank: 0, big: .8 });
  }
  // barn (rank 1)
  house(E, { x: 70, z: -150, w: 16, d: 24, h: 7, color: 0x6e4a32, kind: 'chalet', roof: 0x4f3b2e, snow: true, roofH: 6, fall: { rank: 1, big: .9 } });
  // pines all around
  for (let i = 0; i < 160; i++) { const a = R() * Math.PI * 2, d = 60 + R() * 220, x = 12 + Math.sin(a) * d, z = -60 - Math.cos(a) * d;
    if (inLake(x, z) || Math.abs(x - 12) < 8) continue; coneTree(E, x, z, 1.6 + R() * 1.6, 900 + i, { snow: true, color: 0x2f4a3a, y: 0 }); }
  for (let z = 30, i = 0; z > -160; z -= 20, i++) lamp(E, 12 + (i % 2 ? 6 : -6), z, i % 2 ? 1 : -1, { y: 0 });
  [[8, 1], [16, -1]].forEach(([x, dir], li) => [0, 1].forEach(k => car(E, 800 + li * 5 + k, { x0: x, z0: -40 - k * 120 - li * 60, dir, v: 8, axis: 'z', a: -260, b: 60, brakeT: (B.carsStop ?? 1e9) + k, F, snow: true })));
  crowd(E, TL, { n: 14, axis: 'z', lane: [3, 21], range: [-110, 20], door: (along, acr) => acr > 12 ? 30 : -6, seed: 71, coats: [0x7b4a42, 0x3d4650, 0x56624a, 0x8a6b4e, 0x2f3236], hats: [0xb5543f, 0x2f5d46, 0xd9cdb4] });

  E.brandSpot = { pos: [19, 3.6, -8], ry: -.4, w: 3.6, h: 1.6, posts: 2.8, shot: 'village' };   // shop sign at the square
  const sky = colorKeys(THREE, [[0, 0x5f8fbf, 0xd8e2ea]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || [-140, 120, 60]));
  return {
    ambience: 'berg',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 160, fogFar: 1700, hemi: 1.35, hemiColor: new THREE.Color(0xe8eef6), groundColor: new THREE.Color(0x9aa0a8),
      sun: 2.1, sunColor: new THREE.Color(0xfff3e4), sunDisc: new THREE.Color(0x998877) }),
    shots: {
      wide: { pos: [60, 18, 70], look: [0, 10, -80], drift: [-3, 0, -2], fov: 55 },
      village: { pos: [12, 1.8, 30], look: [10, 6, -60], drift: [0, 0, -3], fov: 60 },
      square: { pos: [12, 2, -10], look: [-12, 14, -40], drift: [-1, 0, 0], fov: 60 },
      lake: { pos: [-10, 2, -40], look: [-70, 6, -140], drift: [-2, 0, 0], fov: 58 },
      mountains: { pos: [12, 2, 40], look: [0, 120, -700], drift: [0, 0, -2], fov: 50 },
      lakeside: { pos: [14, 13, -76], look: [-60, 0, -125], drift: [-1, 0, 0], fov: 58 },      // observer shots (gravity style)
      church: { pos: [16, 4, -18], look: [-14, 15, -46], drift: [0, 0, -.6], fov: 58 },
    },
  };
}
