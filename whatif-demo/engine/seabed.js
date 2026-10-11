// DEEP SEA BED (baksteen "zee valt droog", okt 2026): what lies under the sea in front of a coast place, for a sea
// that drains far below its normal level (force tide.js with negative water levels). Stylised and compressed:
// sandy shallows -> the continental shelf (rocks, weed) -> the shelf edge and a long slope into the deep -> the
// abyssal plain with underwater mountains -> one deep trench where the last water lies.
//   TL.seabed = { shelf: m (shelf width), edge: y at the shelf edge, deep: y of the abyssal plain, trench: [z, width, y],
//                 boats: true (moored boats that settle on the bottom), salt: [t0, t1] (the empty floor turns white),
//                 fog: [[t, near, far], ...] (see far when the camera climbs) }
//   The sea runs along x with the shore at z 0 and the sea at -z (boulevard, harbour). Replaces E.groundAt for z < 0.
import * as THREE from 'three';
import { rng, hash, smooth, clamp, lerp, monotone } from './util.js';
import { ship } from './places/harbor.js';

export function seabed(E, TL, F, shoreAt) {
  const S = TL.seabed, { scene, lam, shadowed } = E;
  const SHELF = S.shelf ?? 1300, EDGE = S.edge ?? -110, DEEP = S.deep ?? -1700, SLOPE = S.slope ?? 1500;
  const [TZ, TW, TY] = S.trench || [-4300, 420, -2700];
  const mounts = S.mounts || [[-1500, -3300, 380, 800], [1300, -3500, 450, 900], [-2300, -5200, 600, 1300], [2100, -5600, 500, 1100], [400, -6200, 650, 1300]];
  // depth profile along z (d = distance from the shore), plus low hills; the trench is a long groove along x
  const depth = (x, z) => {
    const d = -z;
    let y = d < SHELF ? shoreAt(-d) * (1 - smooth(0, 300, d)) + lerp(0, EDGE, Math.pow(d / SHELF, 1.3)) * smooth(0, 300, d)
      : d < SHELF + SLOPE ? lerp(EDGE, DEEP, smooth(0, 1, (d - SHELF) / SLOPE)) : DEEP;
    y += (Math.sin(x * .004 + d * .0013) * .5 + Math.sin(x * .011 - d * .003) * .3) * smooth(150, 1000, d) * (d < SHELF ? 12 : 70);
    for (const [mx, mz, h, r] of mounts) { const q = Math.hypot(x - mx, z - mz) / r; if (q < 1) y += h * Math.pow(1 - q * q, 1.6) * (1 + .15 * Math.sin(x * .02 + z * .017)); }
    const tq = (z - TZ - Math.sin(x * .0012) * 180) / TW; y += (TY - DEEP) * Math.exp(-tq * tq * 2.2);
    return y;
  };
  // the camera may fly kilometres out and down: a bigger sky and a longer view
  E.sky.scale.setScalar(4); E.camera.far = 20000; E.camera.near = .8; E.camera.updateProjectionMatrix();
  const old = E.groundAt; E.groundAt = (x, z) => z < 0 ? depth(x, z) : old(x, z);

  // the floor: one big faceted sheet, finer near the shore; colour by depth (sand -> mud -> dark rock)
  { const NX = 150, NZ = 170, XW = 9000, ZL = 7400, g = new THREE.BufferGeometry(), pos = [], col = [];
    const zAt = j => -Math.pow(j / NZ, 1.7) * ZL, xAt = i => (i / NX - .5) * XW;
    const sand = new THREE.Color(0xcdb98e), mud = new THREE.Color(0x8b8068), rock = new THREE.Color(0x4f4d4a), deep = new THREE.Color(0x3a3c40), c = new THREE.Color();
    const P = [];
    for (let j = 0; j <= NZ; j++) for (let i = 0; i <= NX; i++) { const x = xAt(i) + (j && i % NX ? (hash(i, j) - .5) * 14 : 0), z = zAt(j); P.push([x, depth(x, z) - (j ? 0 : .08), z]); }
    const colAt = (y, k) => { const d = -y; c.copy(sand).lerp(mud, smooth(4, 80, d)).lerp(rock, smooth(150, 900, d)).lerp(deep, smooth(1500, 2600, d));
      return c.multiplyScalar(.92 + hash(k, 3) * .16); };
    for (let j = 0; j < NZ; j++) for (let i = 0; i < NX; i++) {
      const a = j * (NX + 1) + i, b = a + 1, d = a + NX + 1, e = d + 1;
      for (const [p, q, r] of [[a, b, d], [b, e, d]]) { const m = (P[p][1] + P[q][1] + P[r][1]) / 3, cc = colAt(m, p * 3 + q);
        for (const v of [p, q, r]) { pos.push(...P[v]); col.push(cc.r, cc.g, cc.b); } }
    }
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    g.computeVertexNormals();
    const mat = new THREE.MeshLambertMaterial({ vertexColors: true, flatShading: true });
    const floor = new THREE.Mesh(g, mat); floor.receiveShadow = true; scene.add(floor);
    // the empty floor dries to a white crust of salt
    if (S.salt) { const [a, b] = S.salt, white = new THREE.Color(0xe8e4da), base = new THREE.Color(0xffffff);
      E.updates.push(t => { const k = smooth(a, b, t); mat.color.copy(base).lerp(white, k * .1); mat.emissive.setRGB(.13 * k, .125 * k, .115 * k); }); }
  }
  // rocks and weed on the shelf
  { const R = rng(71), rk = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), lam(0x6d6a63), 420), D = new THREE.Object3D();
    for (let n = 0; n < 420; n++) { const z = -60 - Math.pow(R(), 1.5) * 2400, x = (R() - .5) * 1600 * (1 + -z / 1500), s = 1 + R() * (2 + -z / 200);
      D.position.set(x, depth(x, z) + s * .2, z); D.rotation.set(R() * 3, R() * 3, R() * 3); D.scale.set(s * (1 + R()), s * (.6 + R() * .5), s * (1 + R())); D.updateMatrix(); rk.setMatrixAt(n, D.matrix); }
    rk.castShadow = rk.receiveShadow = true; scene.add(rk);
    const wd = new THREE.InstancedMesh(new THREE.ConeGeometry(.35, 1.6, 4), lam(0x4d5a2e), 900);
    for (let n = 0; n < 900; n++) { const z = -45 - R() * 520, x = (R() - .5) * 700, s = .7 + R() * .9;
      D.position.set(x, depth(x, z) + .5 * s, z); D.rotation.set((R() - .5) * .6, R() * 3, (R() - .5) * .6); D.scale.set(s, s * (1 + R()), s); D.updateMatrix(); wd.setMatrixAt(n, D.matrix); }
    scene.add(wd);
  }
  // a much bigger sea that can sink kilometres (the place's own sea stays for the start; both follow the tide)
  { const g = new THREE.PlaneGeometry(14000, 9000, 60, 40); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(5);
    for (let i = 0; i < p.count; i++) p.setY(i, (R() - .5) * .3); g.computeVertexNormals();
    const sea = new THREE.Mesh(g, lam(0x3a7078)); sea.position.set(0, -.05, -4500); scene.add(sea);
    E.floods.push({ mesh: sea, y: -.05, wave: true });
  }
  // moored boats offshore (they settle on the bottom when the water is gone) and one cargo ship out on the shelf
  if (S.boats !== false) {
    const list = S.boatList || [
      { kind: 'fishing', len: 15, beam: 5.5, h: 3, draft: 1.6, color: 0x2f6d86, x: -34, z: -70 },
      { kind: 'yacht', len: 12, beam: 4, h: 2.4, draft: 1.4, color: 0xeeeeea, deck: 0xa48a64, cabinH: 1.4, x: 8, z: -95 },
      { kind: 'fishing', len: 17, beam: 6, h: 3.2, draft: 1.7, color: 0xd9b44a, cabin: 0xd2c6ae, x: 46, z: -80 },
      { kind: 'yacht', len: 11, beam: 3.8, h: 2.2, draft: 1.3, color: 0xe8e2d4, deck: 0xa48a64, cabinH: 1.3, x: -70, z: -120 },
      { kind: 'tug', len: 22, beam: 8, h: 4, draft: 2.8, color: 0xb5402f, cabin: 0xe9e4d8, cabinH: 3, x: 90, z: -150 },
      { kind: 'cargo', len: 150, beam: 22, h: 13, draft: 7, color: 0x3a6688, x: -260, z: -820, big: true },
    ];
    const boats = list.map((o, i) => { const g = ship(E, { ...o, seed: 30 + i, light: false }); return { g, ...o, yaw: (o.big ? .4 : (hash(i, 2) - .5) * .8) + Math.PI / 2, ph: hash(i, 5) * 6, side: hash(i, 9) > .5 ? 1 : -1 }; });
    E.updates.push((t, F_, tv) => {
      const w = F.waterY(t);
      for (const s of boats) {
        const gnd = depth(s.x, s.z) + s.draft, y = Math.max(w, gnd), dry = gnd - w;
        const bob = dry > 0 ? 0 : Math.sin(tv * .8 + s.ph) * .1;
        s.g.position.set(s.x, y + bob, s.z); s.g.rotation.set(0, s.yaw, 0);
        s.g.rotateZ(smooth(0, s.draft * 1.4, dry) * (s.big ? .05 : .3) * s.side + (dry > 0 ? 0 : Math.sin(tv * .6 + s.ph) * .02));
      }
    });
  }
  // fog keys: the haze opens up when the camera climbs (TL.seabed.fog = [[t, near, far], ...])
  if (S.fog) { const nr = monotone(S.fog.map(([t, n]) => [t, n])), fr = monotone(S.fog.map(([t, , f]) => [t, f]));
    (E.lookMods ||= []).push((t, L) => { L.fogNear = nr(t); L.fogFar = fr(t); }); }
  return { depth };
}
