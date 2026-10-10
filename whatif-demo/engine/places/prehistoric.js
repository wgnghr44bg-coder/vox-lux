// PREHISTORIC VALLEY: a wide river through a plain of ferns, tree ferns, cycads and tall
// monkey-puzzle conifers, a smoking volcano far away, mist over the water. No buildings.
// For dinosaurs (TL.animals, animals.js) and any "long ago / untouched nature" story.
//   ground:  E.groundAt drops into the river bed (animals can wade in); the camera side rises a little
//   options: TL.placeParams = { time: 'morning' | 'day' | 'evening', smoke: 1 (volcano plume), mist: 1, clear: [x0, x1, z0, z1] | [[...], ...], shots: { name: { pos, look, fov } } (heights above the ground) }
//   shots:   valley, riverbank, across (telephoto to the far plain), ferns (low, between the ferns),
//            pov-sky (look up past the canopy), canopy, volcano, shore (close, along the bank)
// Beats: none (the animals and sky objects carry the story)
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { rng, hash, smooth, colorKeys } from '../util.js';

export const RIVER = { z: -60, w: 42 };
export const riverZ = x => RIVER.z + Math.sin(x * .006) * 30 + Math.sin(x * .017 + 1) * 8;

export function build(E, TL, F) {
  const { scene, lam } = E, PP = TL.placeParams || {};
  E.dustColor = [.85, .86, .8];
  const inRiver = (x, z) => Math.abs(z - riverZ(x)) < RIVER.w / 2;
  const height = (x, z) => {
    const dz = Math.abs(z - riverZ(x)), bank = smooth(RIVER.w / 2 - 6, RIVER.w / 2 + 4, dz);
    const near = (1 - bank) * -2.2;                                         // river bed
    const roll = Math.sin(x * .021) * 1.1 + Math.cos(z * .018 + x * .006) * 1.3;
    const far = Math.max(0, Math.hypot(x, z) - 1150) * .16;                   // hills at the edge
    const camSide = Math.max(0, z - 40) * .035;                              // our side climbs a little (overlook)
    return near + roll * bank + far + camSide * bank;
  };
  E.groundAt = (x, z) => height(x, z);
  E.waterBase = -.45;

  // ---------- ground ----------
  { const g = new THREE.PlaneGeometry(4000, 4000, 200, 200); g.rotateX(-Math.PI / 2); const p = g.attributes.position, R = rng(3);
    const col = new Float32Array(p.count * 3), c = new THREE.Color(), moss = new THREE.Color(0x5f6f36), mud = new THREE.Color(0x6e5f45), dry = new THREE.Color(0x7c7a4a);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), h = height(x, z) + (R() - .5) * .25; p.setY(i, h);
      const dz = Math.abs(z - riverZ(x)); c.copy(moss).lerp(dry, hash(Math.round(x / 9), Math.round(z / 9)) * .5).lerp(mud, 1 - smooth(RIVER.w / 2 - 2, RIVER.w / 2 + 7, dz));
      col.set([c.r, c.g, c.b], i * 3); }
    g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.computeVertexNormals();
    const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: 0xffffff, vertexColors: true, flatShading: true })); m.receiveShadow = true; scene.add(m); }
  // river surface: a strip that follows the bends
  { const L = 3000, n = 300, g = new THREE.PlaneGeometry(L, RIVER.w + 4, n, 1); g.rotateX(-Math.PI / 2); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) p.setZ(i, p.getZ(i) + riverZ(p.getX(i)));
    g.computeVertexNormals();
    const water = new THREE.Mesh(g, lam(0x51706c, { transparent: true, opacity: .92 })); water.position.y = E.waterBase; water.receiveShadow = true; scene.add(water);
    E.floods.push({ mesh: water, y: E.waterBase });
    // light streaks on the water that drift downstream
    const streak = new THREE.MeshBasicMaterial({ color: 0xc9d6cf, transparent: true, opacity: .22 }), R = rng(8), sg = [];
    for (let i = 0; i < 140; i++) { const x = (R() - .5) * 1600, g2 = new THREE.PlaneGeometry(4 + R() * 9, .25); g2.rotateX(-Math.PI / 2); g2.translate(x, E.waterBase + .03, riverZ(x) + (R() - .5) * RIVER.w * .8); sg.push(g2); }
    const sm = new THREE.Mesh(mergeGeometries(sg), streak); scene.add(sm);
    E.updates.push((t, F_, tv) => { sm.position.x = (tv * 1.2) % 40; });
  }

  const VX = 1100, VZ = -2700;      // the volcano, far away
  const SHOTS = {
    valley: { pos: [40, 22, 120], look: [-20, 6, -200], drift: [-2, 0, -1], fov: 52 },              // overlook: river, plain, volcano
    riverbank: { pos: [10, 3.5, -20], look: [-60, 6, -95], drift: [-1, 0, 0], fov: 56 },            // at the water, looking across
    across: { pos: [6, 14, -18], look: [-120, 12, -950], drift: [0, 0, 0], fov: 16 },                 // telephoto: the far plain (~ 1 km)
    shore: { pos: [24, 1.8, -20], look: [-12, 1.2, -44], drift: [-.8, 0, 0], fov: 50, clear: 22 },               // close, along our bank (~ 40 m)
    ferns: { pos: [6, .45, 46], look: [6, 1.2, -40], drift: [0, 0, -1.2], fov: 62, run: { amp: .015, freq: 1.2 } }, // low, between the ferns
    'pov-sky': { pos: [6, 1.6, 40], look: [-60, 400, -200], drift: [0, 0, 0], fov: 74, frame: true },  // tree ferns around it frame the sky              // look up past the canopy
    canopy: { pos: [-30, 6, 60], look: [-260, 70, -700], drift: [1.5, 0, 0], fov: 60 },
    lineup: { pos: [0, 7, 75], look: [0, 5, 20], drift: [0, 0, 0], fov: 62 },      // test sheet: animals side by side
    volcano: { pos: [20, 12, 40], look: [VX, 700, VZ], drift: [0, 0, 0], fov: 38 },
  };
  Object.assign(SHOTS, PP.shots || {});    // scenario shots, also given above the local ground
  for (const S of Object.values(SHOTS)) {   // standpoints are given above the local ground
    S.pos[1] += height(S.pos[0], S.pos[2]);
    if (Math.hypot(S.look[0], S.look[2]) < 600) S.look[1] += height(S.look[0], S.look[2]);
  }
  const nearCam = (x, z) => Object.values(SHOTS).some(S => Math.hypot(x - S.pos[0], z - S.pos[2]) < (S.pos[1] < 1 ? 1.5 : 9) || (S.clear && Math.hypot(x - S.look[0], z - S.look[2]) < S.clear));

  // ---------- plants (instanced, merged low-poly shapes) ----------
  const R = rng(11);
  const frond = (len, w, droop) => { const g = new THREE.ConeGeometry(w, len, 4, 1); g.translate(0, len / 2, 0); g.scale(1, 1, .22); g.rotateX(droop); return g; };
  function treeFernGeo(h) {
    const parts = [new THREE.CylinderGeometry(.22, .38, h, 6).translate(0, h / 2, 0)];
    for (let i = 0; i < 10; i++) { const f = frond(3.8, .55, 1.2 + (i % 2) * .25); f.rotateY(i / 10 * Math.PI * 2); f.translate(0, h, 0); parts.push(f); }
    return parts;
  }
  function conifer(h) {         // monkey-puzzle: bare trunk, an umbrella of tiers at the top
    const parts = [new THREE.CylinderGeometry(.35, .8, h, 6).translate(0, h / 2, 0)];
    for (let k = 0; k < 4; k++) { const r = 5.5 - k * 1.2, y = h - 5 + k * 1.6; parts.push(new THREE.ConeGeometry(r, 2.6, 7).translate(0, y, 0)); }
    return parts;
  }
  function cycad() {
    const parts = [new THREE.CylinderGeometry(.45, .6, 1.4, 7).translate(0, .7, 0)];
    for (let i = 0; i < 12; i++) { const f = frond(2.2, .35, .75 + (i % 3) * .2); f.rotateY(i / 12 * Math.PI * 2); f.translate(0, 1.35, 0); parts.push(f); }
    return parts;
  }
  function fernClump() { const parts = []; for (let i = 0; i < 7; i++) { const f = frond(1.6, .3, 1.0 + (i % 2) * .3); f.rotateY(i / 7 * Math.PI * 2 + .3); parts.push(f); } return parts; }
  // colour each part: first part trunk/bark, the rest leaves
  function coloured(parts, bark, leaf) {
    parts.forEach((g, i) => { const n = g.attributes.position.count, c = new THREE.Color(i === 0 && bark != null ? bark : leaf), a = new Float32Array(n * 3);
      for (let k = 0; k < n; k++) a.set([c.r, c.g, c.b], k * 3); g.setAttribute('color', new THREE.BufferAttribute(a, 3)); if (g.index) g.toNonIndexed(); });
    return mergeGeometries(parts.map(g => g.index ? g.toNonIndexed() : g));
  }
  const plantMat = new THREE.MeshLambertMaterial({ color: 0xffffff, vertexColors: true, flatShading: true });
  function plant(geo, list, shadow = true) {
    const im = new THREE.InstancedMesh(geo, plantMat, list.length), M = new THREE.Matrix4(), Q = new THREE.Quaternion(), c = new THREE.Color();
    list.forEach(([x, z, s, ry, tint], i) => { Q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), ry); M.compose(new THREE.Vector3(x, height(x, z) - .1, z), Q, new THREE.Vector3(s, s, s));
      im.setMatrixAt(i, M); im.setColorAt(i, c.setHSL(0, 0, .85 + tint * .3)); });
    im.castShadow = shadow; im.receiveShadow = true; scene.add(im); return im;
  }
  // where things may grow: not in the river, not on the camera lanes
  const CL = PP.clear && (Array.isArray(PP.clear[0]) ? PP.clear : [PP.clear]);   // [x0, x1, z0, z1] (or a list): open clearings (no plants)
  const free = (x, z, m = 3) => Math.abs(z - riverZ(x)) > RIVER.w / 2 + m && !(CL && CL.some(c => x > c[0] && x < c[1] && z > c[2] && z < c[3])) && !nearCam(x, z);
  const scatter = (n, rx, z0, z1, m, s0, s1) => { const L = []; for (let i = 0; i < n * 3 && L.length < n; i++) {
    const x = (R() - .5) * rx * 2, z = z0 + R() * (z1 - z0); if (free(x, z, m)) L.push([x, z, s0 + R() * (s1 - s0), R() * 6.3, R()]); } return L; };
  plant(coloured(treeFernGeo(6), 0x5a4632, 0x4f6e2e), scatter(260, 420, -420, 160, 4, .7, 1.5));
  { const S = SHOTS['pov-sky'], L = [];
    for (let k = 0; k < 3; k++) { const a = -1.6 + k * 1.6; L.push([S.pos[0] + Math.sin(a) * 8, S.pos[2] - Math.cos(a) * 8 - 3, 1.2 + (k % 2) * .3, k, .5]); }
    plant(coloured(treeFernGeo(6), 0x5a4632, 0x4f6e2e), L); }
  plant(coloured(conifer(28), 0x5e4a36, 0x34502c), scatter(90, 700, -900, 220, 8, .7, 1.25));
  plant(coloured(cycad(), 0x6a5a3a, 0x5c7a34), scatter(220, 300, -300, 140, 3, .7, 1.4));
  plant(coloured(fernClump(), null, 0x56772f), scatter(1600, 260, -260, 120, 1.5, .6, 1.6), false);
  plant(coloured(fernClump(), null, 0x6a8a38), (() => { const L = []; for (let i = 0; i < 260; i++) { const x = 6 + (R() - .5) * 24, z = 30 + R() * 30; if (Math.abs(x - 6) > 1.2 && free(x, z, -99)) L.push([x, z, .8 + R() * .9, R() * 6.3, R()]); } return L; })(), false);
  // rocks along the bank
  { const g = new THREE.DodecahedronGeometry(1, 0), im = new THREE.InstancedMesh(g, lam(0x7b766c), 90), M = new THREE.Matrix4(), Q = new THREE.Quaternion();
    for (let i = 0; i < 90; i++) { const x = (R() - .5) * 500, side = R() < .5 ? -1 : 1, z = riverZ(x) + side * (RIVER.w / 2 + R() * 6), s = Object.values(SHOTS).some(S => Math.hypot(x - S.pos[0], z - S.pos[2]) < 30) ? 0 : .4 + R() * 1.6;
      Q.setFromEuler(new THREE.Euler(R(), R() * 6, R())); M.compose(new THREE.Vector3(x, height(x, z) + s * .2, z), Q, new THREE.Vector3(s, s * .7, s)); im.setMatrixAt(i, M); }
    im.castShadow = im.receiveShadow = true; scene.add(im); }

  // ---------- volcano with a smoke plume ----------
  { const g = new THREE.ConeGeometry(520, 560, 11, 3, true), p = g.attributes.position, Rv = rng(4);
    for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y > 260) { p.setX(i, p.getX(i) * .9); p.setZ(i, p.getZ(i) * .9); } p.setX(i, p.getX(i) * (1 + (Rv() - .5) * .08)); }
    g.computeVertexNormals(); const v = new THREE.Mesh(g, lam(0x6d665f, { fog: false })); v.position.set(VX, 260, VZ); scene.add(v);
    const glow = new THREE.Mesh(new THREE.CylinderGeometry(52, 70, 12, 11), new THREE.MeshBasicMaterial({ color: 0xff8a3c })); glow.position.set(VX, 536, VZ); scene.add(glow); }
  const smoke = PP.smoke ?? 1;
  if (smoke) E.emitters.push((tv, add) => {
    for (let k = 0; k < 70; k++) { const life = 60, a = ((tv + hash(k, 1) * life) % life) / life, h = a * 900;
      add(VX + a * 260 + (hash(k, 2) - .5) * 60 * (1 + a * 3), 560 + h, VZ + (hash(k, 3) - .5) * 60 * (1 + a * 2), 90 + a * 360, (1 - a) * .55 * smoke, .55, .53, .5, hash(k, 4) * 6); } });
  // mist low over the water
  if (PP.mist ?? 1) E.emitters.push((tv, add) => {
    for (let k = 0; k < 90; k++) { const x0 = (hash(k, 7) - .5) * 700, x = x0 + ((tv * .8 + hash(k, 8) * 200) % 200) - 100;
      add(x, E.waterBase + .8 + hash(k, 9) * 1.5, riverZ(x) + (hash(k, 10) - .5) * RIVER.w * .9, 10 + hash(k, 11) * 10, .055 * (PP.mist ?? 1), .8, .83, .82, hash(k, 12) * 6); } });

  // ---------- light ----------
  const T = PP.time || 'morning';
  const SKY = { morning: [0x5f8fc0, 0xd9dccf, 0xffe2b8, 1.9], day: [0x5f8fc4, 0xd8e2e6, 0xfff4e4, 2.2], evening: [0x4d5f86, 0xe8a774, 0xffb27a, 1.5] }[T];
  const sky = colorKeys(THREE, [[0, SKY[0], SKY[1]]]);
  E.sunOffset = new THREE.Vector3(...(TL.sunOffset || (T === 'day' ? [-120, 160, 60] : [-200, 70, -120])));
  return {
    ambience: 'oerwoud',
    look: t => ({ top: sky(t, 1), hor: sky(t, 2), fogNear: 160, fogFar: 4200, fogColor: sky(t, 2).lerp(new THREE.Color(0xaab3a8), .2),
      hemi: 1.35, hemiColor: new THREE.Color(0xe6e9e0), groundColor: new THREE.Color(0x5d5a40),
      sun: SKY[3], sunColor: new THREE.Color(SKY[2]), sunDisc: new THREE.Color(T === 'day' ? 0x998877 : 0xffc890), haze: 0 }),
    shots: SHOTS,
  };
}
