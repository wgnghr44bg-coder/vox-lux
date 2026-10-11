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
import { ship, hullGeo } from './places/harbor.js';
import { lamp } from './props.js';

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
    { const k = smooth(SHELF - 150, SHELF + 200, d) * (1 - smooth(SHELF + SLOPE - 300, SHELF + SLOPE + 200, d));   // gullies down the slope
      y += k * (Math.sin(x * .011 + Math.sin(d * .004) * 1.5) * 70 + Math.sin(x * .027 + d * .002) * 25); }
    for (const [mx, mz, h, r] of mounts) { const q = Math.hypot(x - mx, z - mz) / r; if (q < 1) y += h * Math.pow(1 - q * q, 1.6) * (1 + .15 * Math.sin(x * .02 + z * .017)); }
    const tq = (z - TZ - Math.sin(x * .0012) * 180) / TW; y += (TY - DEEP) * Math.exp(-tq * tq * 2.2);
    return y;
  };
  // the camera may fly kilometres out and down: a bigger sky and a longer view
  E.sky.scale.setScalar(4); E.camera.far = 20000; E.camera.updateProjectionMatrix();
  // no flicker: the near plane and the shadow box grow with the camera's height above the ground
  E.nearFn = p => clamp((p[1] - (p[2] < 0 ? depth(p[0], p[2]) : 3)) * .04, .3, 60);
  { const sc = E.sun.shadow.camera;
    E.updates.push(() => { const c = E.camera.position, h = Math.max(0, c.y - (c.z < 0 ? depth(c.x, c.z) : 3));
      const r = clamp(110 + h * 1.6, 110, 2400); if (Math.abs(sc.right - r) > 1) { Object.assign(sc, { left: -r, right: r, top: r, bottom: -r, far: 900 + r * 2 }); sc.updateProjectionMatrix(); }
      E.shadowStep = Math.max(8, r / 64); E.sunOffset.setLength(Math.max(220, r)); }); }
  const old = E.groundAt; E.groundAt = (x, z) => z < 0 ? depth(x, z) : old(x, z);

  // the floor: one big faceted sheet, finer near the shore; colour by depth (sand -> mud -> dark rock)
  { const NX = 150, NZ = 170, XW = 9000, ZL = 7400, g = new THREE.BufferGeometry(), pos = [], col = [];
    const zAt = j => -Math.pow(j / NZ, 1.7) * ZL, xAt = i => (i / NX - .5) * XW;
    const sand = new THREE.Color(0xcdb98e), mud = new THREE.Color(0x8b8068), rock = new THREE.Color(0x6a645a), deep = new THREE.Color(0x585b60), c = new THREE.Color();
    const P = [];
    for (let j = 0; j <= NZ; j++) for (let i = 0; i <= NX; i++) { const x = xAt(i) + (j && i % NX ? (hash(i, j) - .5) * 14 : 0), z = zAt(j); P.push([x, depth(x, z) - (-z < 45 ? .3 : 0), z]); }
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
      E.updates.push(t => { const k = smooth(a, b, t); mat.color.copy(base).lerp(white, k * .35); mat.emissive.setRGB(.3 * k, .29 * k, .27 * k); }); }
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
  const STOP = TL.beats.stop, W = t => F.waterY(Math.min(t, STOP));
  const firstBelow = y => { for (let t = 0; t < STOP; t += .05) if (W(t) < y) return t; return 1e9; };   // when the sea drops below y
  const steel = c => lam(c), wood = lam(0x8a6a4a), algae = lam(0x3f5a3a), rust = lam(0x7a4a32);
  // moored boats offshore (they settle on the bottom when the water is gone) and big ships out on the shelf
  if (S.boats !== false) {
    const list = S.boatList || [
      { kind: 'fishing', len: 15, beam: 5.5, h: 3, draft: 1.6, color: 0x2f6d86, x: -34, z: -70 },
      { kind: 'yacht', len: 12, beam: 4, h: 2.4, draft: 1.4, color: 0xeeeeea, deck: 0xa48a64, cabinH: 1.4, x: 8, z: -95 },
      { kind: 'fishing', len: 17, beam: 6, h: 3.2, draft: 1.7, color: 0xd9b44a, cabin: 0xd2c6ae, x: 46, z: -80 },
      { kind: 'yacht', len: 11, beam: 3.8, h: 2.2, draft: 1.3, color: 0xe8e2d4, deck: 0xa48a64, cabinH: 1.3, x: -70, z: -120 },
      { kind: 'tug', len: 22, beam: 8, h: 4, draft: 2.8, color: 0xb5402f, cabin: 0xe9e4d8, cabinH: 3, x: 90, z: -150 },
      { kind: 'yacht', len: 10, beam: 3.6, h: 2.1, draft: 1.2, color: 0x2f4f6f, deck: 0xa48a64, cabinH: 1.2, x: 25, z: -60 },
      { kind: 'fishing', len: 14, beam: 5, h: 2.9, draft: 1.5, color: 0x7d9a6a, cabin: 0xe9e4d8, x: -110, z: -85 },
      { kind: 'yacht', len: 13, beam: 4.2, h: 2.5, draft: 1.4, color: 0xf2efe6, deck: 0xa48a64, cabinH: 1.5, x: 130, z: -110 },
      { kind: 'fishing', len: 18, beam: 6.2, h: 3.3, draft: 1.8, color: 0xb5543f, cabin: 0xd2c6ae, x: -150, z: -190 },
      { kind: 'cargo', len: 150, beam: 22, h: 13, draft: 7, color: 0x3a6688, x: -200, z: -620, big: true, cargo: true },
      { kind: 'cargo', len: 120, beam: 18, h: 11, draft: 6, color: 0x8c3b33, x: 420, z: -1050, big: true },
    ];
    const boats = list.map((o, i) => { const g = ship(E, { ...o, seed: 30 + i, light: false });
      return { g, ...o, yaw: (o.big ? .4 + i * .3 : (hash(i, 2) - .5) * .8) + Math.PI / 2, ph: hash(i, 5) * 6, side: hash(i, 9) > .5 ? 1 : -1 }; });
    // the container ship lists over and part of its deck cargo slides off into the mud
    const cs = boats.find(b => b.cargo);
    if (cs) {
      const tSlide = firstBelow(depth(cs.x, cs.z) + cs.draft - 10), deckY = cs.h - cs.draft, low = -cs.side;   // rotateZ(+) lifts +x
      const cols = [0xb5543f, 0x2f6d86, 0xd9b44a, 0x7d9a6a, 0xc9c1ae, 0x3e5873];
      cs.boxes = Array.from({ length: 12 }, (_, i) => { const m = shadowed(new THREE.Mesh(new THREE.BoxGeometry(2.4, 2.55, 12.1), lam(cols[i % cols.length])));
        const z0 = -cs.len * .27 + 6.3 + (i % 6) * 12.6, y0 = deckY + 1.5 + (4 + Math.floor(i / 6)) * 2.6, x0 = low * cs.beam * (.3 - Math.floor(i / 6) * .15);
        m.position.set(x0, y0, z0); cs.g.add(m); return { m, x0, y0, z0, d: tSlide + hash(i, 3) * 1.6 + Math.floor(i / 6) * .5, sp: hash(i, 4) }; });
      cs.slide = tSlide;
      if (tSlide < STOP) for (const k of [0, .8, 1.6]) E.EVENTS.push({ t: tSlide + 1.2 + k, kind: 'impact', e: .9, x: cs.x, z: cs.z });
    }
    E.updates.push((t, F_, tv) => {
      const w = W(t);
      for (const s of boats) {
        const gnd = depth(s.x, s.z) + s.draft, y = Math.max(w, gnd), dry = gnd - w;
        const bob = dry > 0 ? 0 : Math.sin(tv * .8 + s.ph) * .1;
        s.g.position.set(s.x, y + bob, s.z); s.g.rotation.set(0, s.yaw, 0);
        s.g.rotateZ(smooth(0, s.draft * 1.6, dry) * (s.big ? .13 : .3) * s.side + (dry > 0 ? 0 : Math.sin(tv * .6 + s.ph) * .02));
        if (s.boxes) for (const b of s.boxes) { const a = Math.max(0, t - b.d);     // slide to the low side, tip over the edge, drop to the mud
          const sl = Math.min(a * a * 3, s.beam * .55 + 3), fall = Math.max(0, a - .9);
          b.m.position.set(b.x0 - s.side * sl, Math.max(-s.draft + 1.3, b.y0 - 4.9 * fall * fall * 2), b.z0 + (b.sp - .5) * sl * .4);
          b.m.rotation.set((b.sp - .5) * Math.min(1, fall) * .6, (b.sp - .5) * .3 * Math.min(1, a), s.side * Math.min(1.3, fall * 1.6)); }
      }
    });
  }

  // a long pier on piles: the piles show their green, wet feet when the sea goes
  { const PX = S.pierX ?? -64, Z1 = 37, Z0 = -170, DY = 4.4;
    const deck = shadowed(new THREE.Mesh(new THREE.BoxGeometry(5, .4, Z1 - Z0), wood)); deck.position.set(PX, DY, (Z1 + Z0) / 2); scene.add(deck);
    for (const sx of [-1, 1]) { const r = new THREE.Mesh(new THREE.BoxGeometry(.12, .12, Z1 - Z0), lam(0xe9e4d8)); r.position.set(PX + sx * 2.4, DY + 1.1, (Z1 + Z0) / 2); scene.add(r); }
    for (let z = Z1 - 6; z > Z0; z -= 8) for (const sx of [-1, 1]) {
      const gy = depth(PX + sx * 2, z), top = DY - .2, wet = Math.min(.6, top);
      const up = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.28, .28, top - wet, 6), wood)); up.position.set(PX + sx * 2, (top + wet) / 2, z); scene.add(up);
      if (wet > gy) { const lo = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.32, .34, wet - gy + .5, 6), algae)); lo.position.set(PX + sx * 2, (wet + gy - .5) / 2, z); scene.add(lo); }
      if (Math.round((Z1 - 6 - z) / 8) % 3 === 0) lamp(E, PX + sx * 2.6, z, -sx, { y: DY });
    }
    const hut = shadowed(new THREE.Mesh(new THREE.BoxGeometry(8, 3.2, 7), lam(0xe9e4d8))); hut.position.set(PX, DY + 1.8, Z0 + 4); scene.add(hut);
    const roof = shadowed(new THREE.Mesh(new THREE.ConeGeometry(6.2, 2, 4), lam(0x2f6d86))); roof.rotation.y = Math.PI / 4; roof.position.set(PX, DY + 4.4, Z0 + 4); scene.add(roof);
  }

  // rock pools left behind in the hollows, shining until they dry up too
  { const R = rng(91), mat = new THREE.MeshPhongMaterial({ color: 0x4f8b92, specular: 0xbfd6dc, shininess: 80, flatShading: true });
    const pools = [];
    for (let i = 0; i < 34; i++) { const z = -35 - Math.pow(R(), 1.3) * 520, x = (R() - .5) * 520, r = 2 + R() * 7, y = depth(x, z) + .22;
      const m = new THREE.Mesh(new THREE.CircleGeometry(r, 7), mat); m.rotation.x = -Math.PI / 2; m.rotation.z = R() * 3; m.scale.set(1, .6 + R() * .6, 1); m.position.set(x, y, z); scene.add(m);
      pools.push({ m, y, gone: 20 + R() * 40 }); }
    E.updates.push(t => { const w = W(t); for (const p of pools) p.m.visible = w < p.y - .05; });
  }

  // reefs: bright patches of coral and sea fans on the shelf
  { const R = rng(93), N = 900, im = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), new THREE.MeshLambertMaterial({ flatShading: true }), N);
    const fan = new THREE.InstancedMesh(new THREE.ConeGeometry(1, 2.2, 3), new THREE.MeshLambertMaterial({ flatShading: true }), 300), D = new THREE.Object3D();
    const cols = [0xe07a8a, 0xe8964a, 0x9a6ab0, 0xe0c050, 0xd8d0c0, 0xd05a4a, 0x5ab0a0].map(c => new THREE.Color(c));
    const patches = Array.from({ length: 30 }, () => [(R() - .5) * 900, -110 - R() * 900, 10 + R() * 22]);
    for (let n = 0; n < N; n++) { const [px, pz, pr] = patches[n % patches.length], a = R() * 6.3, d = Math.sqrt(R()) * pr, x = px + Math.cos(a) * d, z = pz + Math.sin(a) * d, s = 1 + R() * 2.6;
      D.position.set(x, depth(x, z) + s * .3, z); D.rotation.set(R(), R() * 3, R()); D.scale.set(s, s * (.6 + R() * .8), s); D.updateMatrix(); im.setMatrixAt(n, D.matrix); im.setColorAt(n, cols[Math.floor(R() * cols.length)]); }
    for (let n = 0; n < 300; n++) { const [px, pz, pr] = patches[n % patches.length], a = R() * 6.3, d = Math.sqrt(R()) * pr, x = px + Math.cos(a) * d, z = pz + Math.sin(a) * d, s = 1 + R() * 1.5;
      D.position.set(x, depth(x, z) + s, z); D.rotation.set((R() - .5) * .3, R() * 3, (R() - .5) * .3); D.scale.set(s * 1.4, s, s * .12); D.updateMatrix(); fan.setMatrixAt(n, D.matrix); fan.setColorAt(n, cols[Math.floor(R() * 4)]); }
    im.castShadow = im.receiveShadow = true; scene.add(im, fan);
  }

  // an old wreck on the shelf and another one far out on the deep floor
  for (const [wx, wz, len, sc] of [[150, -430, 42, 1], [-230, -1850, 70, 1.8], [260, -2500, 60, 1.6], [-520, -3150, 60, 1.6]]) {
    const g = new THREE.Group(), gy = depth(wx, wz); g.position.set(wx, gy - 2 * sc, wz); g.rotation.set(.08, .9 + wx * .001, .35); scene.add(g);
    const hull = shadowed(new THREE.Mesh(hullGeo(len, len * .24, len * .16, .35), lam(0x5a4632))); hull.position.y = len * .08; g.add(hull);
    const brk = shadowed(new THREE.Mesh(new THREE.BoxGeometry(len * .2, len * .1, len * .12), lam(0x2e2620))); brk.position.set(0, len * .17, len * .05); g.add(brk);
    for (const [mz, mh, tilt] of [[len * .2, len * .5, .25], [-len * .12, len * .3, -.5]]) {
      const m = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.25 * sc, .35 * sc, mh, 5), lam(0x4a3a2a))); m.position.set(0, len * .16 + mh / 2, mz); m.rotation.x = tilt; g.add(m); }
  }

  // a sea cable running from the coast down into the deep
  { const pts = []; for (let d = 320; d < 5200; d += 40) { const x = 40 + d * .05 + Math.sin(d * .002) * 60; pts.push(new THREE.Vector3(x, depth(x, -d) + 1.2, -d)); }
    const cab = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 400, 1.2, 5), lam(0x2a2a2c)); scene.add(cab); }
  // an oil platform: four legs, now standing on bare steel feet in the mud
  { const [ox, oz] = S.rig || [-420, -1180], gy = depth(ox, oz), TOP = 26, g = new THREE.Group(); g.position.set(ox, 0, oz); g.rotation.y = .5; scene.add(g);
    const legM = lam(0xd8b84a);
    for (const [lx, lz] of [[-16, -16], [16, -16], [-16, 16], [16, 16]]) {
      const lo = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(3, 3.4, -gy + 2, 8), rust)); lo.position.set(lx, (gy - 2) / 2 - 1, lz); g.add(lo);
      const hi = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(3, 3, TOP + 1, 8), legM)); hi.position.set(lx, TOP / 2 - 1, lz); g.add(hi); }
    for (let y = gy + 15; y < TOP - 4; y += 22) { const m = y < 0 ? rust : legM;
      for (const sz of [-16, 16]) { const br = new THREE.Mesh(new THREE.BoxGeometry(32, 1, 1), m); br.position.set(0, y, sz); g.add(br); }
      for (const sx of [-16, 16]) { const br = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 32), m); br.position.set(sx, y, 0); g.add(br); } }
    const deckM = shadowed(new THREE.Mesh(new THREE.BoxGeometry(46, 6, 46), lam(0x8e8e8a))); deckM.position.y = TOP + 3; g.add(deckM);
    for (const [bx, bz, w, h, d, c] of [[-10, -8, 18, 9, 16, 0xe9e4d8], [10, 6, 14, 7, 20, 0xb5543f], [-8, 14, 12, 5, 10, 0x2f6d86]]) {
      const b = shadowed(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), lam(c))); b.position.set(bx, TOP + 6 + h / 2, bz); g.add(b); }
    const der = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(1.2, 4.5, 34, 4), lam(0xd9d6cc))); der.position.set(12, TOP + 23, -12); g.add(der);
    const heli = shadowed(new THREE.Mesh(new THREE.CylinderGeometry(9, 9, .6, 10), lam(0x3a5a4a))); heli.position.set(-18, TOP + 16, 16); g.add(heli);
    const flare = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.2, 30), legM); flare.position.set(30, TOP + 10, 0); flare.rotation.y = Math.PI / 2; flare.rotation.x = -.4; g.add(flare);
    const fl = new THREE.Mesh(new THREE.ConeGeometry(1.6, 5, 6), new THREE.MeshBasicMaterial({ color: 0xffa040 })); fl.position.set(44, TOP + 16, 0); g.add(fl);
    E.updates.push((t, F_, tv) => { fl.scale.set(1 + Math.sin(tv * 9) * .15, 1 + Math.sin(tv * 6.3) * .25, 1); });
  }

  // gulls over the beach and the drying sand
  { const R = rng(95), mat = lam(0xf2f0ea), wingG = new THREE.PlaneGeometry(.8, .28); wingG.translate(.4, 0, 0);
    const wm = new THREE.MeshLambertMaterial({ color: 0xf2f0ea, side: THREE.DoubleSide });
    const gulls = Array.from({ length: 26 }, (_, i) => { const g = new THREE.Group(); scene.add(g);
      const b = new THREE.Mesh(new THREE.SphereGeometry(.16, 6, 4), mat); b.scale.set(1, .9, 2.4); g.add(b);
      const w = [-1, 1].map(sx => { const m = new THREE.Mesh(wingG, wm); m.rotation.x = -Math.PI / 2; m.scale.x = sx; g.add(m); return m; });
      g.scale.setScalar(1.6); return { g, w, c: [(R() - .5) * 140, 8 + R() * 16, -20 - R() * 140], r: 10 + R() * 30, sp: (.25 + R() * .25) * (R() < .5 ? 1 : -1), ph: R() * 6.3 }; });
    E.updates.push((t, F_, tv) => { for (const q of gulls) { const a = tv * q.sp + q.ph, x = q.c[0] + Math.cos(a) * q.r, z = q.c[2] + Math.sin(a) * q.r * .7;
      q.g.position.set(x + Math.sin(tv * .2 + q.ph) * 20, q.c[1] + Math.sin(tv * .7 + q.ph) * 1.5, z - tv * .6); q.g.rotation.set(0, -a + (q.sp > 0 ? Math.PI : 0), Math.sin(a) * .2);
      const f = Math.sin(tv * 7 + q.ph) * .5; q.w[0].rotation.y = -f; q.w[1].rotation.y = f; } });
  }

  // steam from vents on the deep floor once the water is gone, and salt blowing over the empty floor at the end
  { const vents = [[-300, -2900], [600, -3300], [-900, -3800], [250, -4700]].map(([x, z]) => ({ x, z, y: depth(x, z), t0: firstBelow(depth(x, z) - 5) }));
    const sa = S.storm ?? (S.salt || [1e9])[0], sb = sa + 4;
    E.emitters.push((tv, add) => {
      const t = Math.min(tv, STOP);
      for (const v of vents) { if (t < v.t0) continue; const k = smooth(v.t0, v.t0 + 3, t);
        for (let i = 0; i < 26; i++) { const u = (tv * .08 + hash(i, v.x)) % 1; add(v.x + u * 60 + (hash(i, 2) - .5) * 30, v.y + u * 520, v.z + (hash(i, 3) - .5) * 30, 40 + u * 160, Math.sin(u * Math.PI) * .32 * k, .93, .93, .92, hash(i, 4) * 6); } }
      if (t > sa) { const k = smooth(sa, sb, t);
        for (let i = 0; i < 420; i++) { const u = (tv * .06 + hash(i, 7)) % 1, x = -2400 + u * 4800, z = -1000 - hash(i, 8) * 3400, y = depth(x, z) + 10 + hash(i, 9) * (60 + u * 260);
          add(x, y, z, 80 + hash(i, 10) * 220, Math.sin(u * Math.PI) * .3 * k, .97, .96, .93, hash(i, 11) * 6); } }
    });
  }
  // heat: with no sea to cool it, the air turns hot and hazy (TL.seabed.heat = [t0, t1])
  if (S.heat) { const [a, b] = S.heat;
    (E.lookMods ||= []).push((t, L) => { const k = smooth(a, b, t); if (!k) return;
      L.hor.lerp(new THREE.Color(0xeadcbc), .55 * k); L.top.lerp(new THREE.Color(0x9ab4c8), .35 * k); L.sun *= 1 + .2 * k;
      L.haze = Math.max(L.haze || 0, .16 * k); L.hazeColor = '#e6cf9e'; }); }
  // clouds over the sea that thin out and vanish (TL.seabed.clouds = [t0, t1])
  { const R = rng(97), mat = new THREE.MeshLambertMaterial({ color: 0xffffff, transparent: true, opacity: .92, flatShading: true }), cl = [];
    for (let i = 0; i < 46; i++) { const g = new THREE.Group(), x = (R() - .5) * 7000, z = -600 - R() * 6500, y = 900 + R() * 500;
      for (let j = 0; j < 5; j++) { const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 0), mat); m.position.set((R() - .5) * 220, (R() - .5) * 30, (R() - .5) * 120);
        m.scale.set(90 + R() * 90, 35 + R() * 30, 70 + R() * 60); g.add(m); }
      g.position.set(x, y, z); scene.add(g); cl.push({ g, d: R() }); }
    const [a, b] = S.clouds || [1e9, 1e9];
    E.updates.push((t, F_, tv) => { const k = smooth(a, b, t); mat.opacity = .92 * (1 - k);
      for (const c of cl) { const q = 1 - smooth(a + c.d * (b - a) * .5, b, t); c.g.scale.setScalar(Math.max(.001, q)); c.g.visible = q > .01; c.g.position.x += 0; } });
  }
  // fog keys: the haze opens up when the camera climbs (TL.seabed.fog = [[t, near, far], ...])
  if (S.fog) { const nr = monotone(S.fog.map(([t, n]) => [t, n])), fr = monotone(S.fog.map(([t, , f]) => [t, f]));
    (E.lookMods ||= []).push((t, L) => { L.fogNear = nr(t); L.fogFar = fr(t); }); }
  return { depth };
}
