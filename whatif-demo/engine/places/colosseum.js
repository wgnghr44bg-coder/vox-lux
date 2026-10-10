// ANCIENT ROME, 80 AD: a street (Via Sacra style) with insulae, shops, a temple and market stalls, an open square
// with a cone fountain, and the COLOSSEUM (Flavian Amphitheatre) at real scale: 188 x 156 m, 48 m high, 80 arches
// per storey (76 numbered gates), three seating tiers + a wooden top tier for ~50,000 people (instanced crowd),
// the sand arena with trapdoors, the emperor's box, the velarium (sun sails on 240 masts, worked by sailors).
// Force: `day` (time of day, forces/day.js). Nothing breaks here.
//   TL.crowd: { fill: [[t, 0..1]], stand: [[t, 0..1]], cheer: [[t, 0..1]] }   seats taken / standing / wild cheering
//   TL.velarium: [[t, 0..1]]   how far the sun sails are pulled out (0 = furled at the rim, 1 = full)
//   TL.streamStart: time the people in the street start walking; TL.gateBay: the bay of the "your gate" shots
// Beats: lookUp (groups look up at the building), shelter (groups walk off)
import * as THREE from 'three';
import { rng, hash, smooth, clamp, monotone } from '../util.js';
import { coneTree, roundTree } from '../props.js';
import { roman, stream, spectators, torch, oilLamp, insula, temple, stall, coneFountain, amphora, romanTex } from '../ancient.js';

export const ZC = -250, A = 94, B = 78, A0 = 43.5, B0 = 27.5, NB = 80;
const roman_ = n => { const r = [[50, 'L'], [40, 'XL'], [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']]; let s = ''; for (const [v, c] of r) while (n >= v) { s += c; n -= v; } return s; };

export function build(E, TL, F) {
  const { scene, lam, shadowed } = E, S = m => shadowed(m);
  E.personFn = (E2, seed, o) => roman(E2, seed, o);
  E.groundAt = () => 0;

  // ---------- ellipse helpers: 80 bays equally spaced along the outer wall ----------
  const ell = (d, th) => [(A0 + d) * Math.cos(th), ZC + (B0 + d) * Math.sin(th)];
  const thetas = (() => { const N = 4000, L = [0]; for (let i = 1; i <= N; i++) { const a = (i - 1) / N * 2 * Math.PI, b = i / N * 2 * Math.PI;
      L.push(L[i - 1] + Math.hypot(A * (Math.cos(b) - Math.cos(a)), B * (Math.sin(b) - Math.sin(a)))); }
    const out = []; for (let k = 0; k < NB; k++) { const s = k / NB * L[N]; let i = 0; while (L[i + 1] < s) i++; out.push((i + (s - L[i]) / (L[i + 1] - L[i])) / N * 2 * Math.PI + Math.PI / 2); } return out; })();
  // bay k: centre on ring d, outward normal angle, chord width
  const bay = (k, d) => { const th = thetas[k], th2 = thetas[(k + 1) % NB], tm = th + (((th2 - th + 3 * Math.PI) % (2 * Math.PI)) - Math.PI) / 2;
    const [x, z] = ell(d, tm), [x1, z1] = ell(d, th), [x2, z2] = ell(d, th2);
    const nx = Math.cos(tm) / (A0 + d), nz = Math.sin(tm) / (B0 + d), nl = Math.hypot(nx, nz);
    return { x, z, th: tm, n: [nx / nl, nz / nl], w: Math.hypot(x2 - x1, z2 - z1), ry: Math.atan2(nx / nl, nz / nl) }; };
  E.colo = { ell, bay, thetas, ZC };

  // ---------- ground: basalt street, travertine square, grass and earth beyond ----------
  { const g = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), lam(0x8a8466)); g.rotation.x = -Math.PI / 2; g.position.set(0, -.02, -200); g.receiveShadow = true; scene.add(g);
    const sq = new THREE.Mesh(new THREE.PlaneGeometry(420, 340), lam(0xc8bea6)); sq.rotation.x = -Math.PI / 2; sq.position.set(0, 0, -250); sq.receiveShadow = true; scene.add(sq);
    const tex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const x = cv.getContext('2d'); x.fillStyle = '#4f4b45'; x.fillRect(0, 0, 64, 64);
      const R = rng(3); for (let i = 0; i < 26; i++) { x.fillStyle = `hsl(30,6%,${26 + R() * 12}%)`; x.beginPath(); const cx = R() * 64, cy = R() * 64, r = 5 + R() * 6;
        for (let k = 0; k < 6; k++) { const a = k / 6 * 6.283 + R() * .4; x.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); } x.fill(); }
      const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3, 60); return t; })();
    const st = new THREE.Mesh(new THREE.PlaneGeometry(9, 190), lam(0xffffff, { map: tex })); st.rotation.x = -Math.PI / 2; st.position.set(0, .015, -15); st.receiveShadow = true; scene.add(st);
    for (const s of [-1, 1]) { const w = S(new THREE.Mesh(new THREE.BoxGeometry(2.4, .25, 190), lam(0xb9ae96))); w.position.set(s * 5.7, .12, -15); scene.add(w); } }

  // ---------- the street: insulae with shops, both sides, z +75 .. -95 ----------
  const shopFronts = [];
  { const R = rng(7), cols = [0xc9935a, 0xd8b07a, 0xb8693f, 0xe0c89a, 0xa85a3a, 0xcfa26a, 0xd9c2a0];
    for (const s of [-1, 1]) { let z = 78; while (z > -92) { const len = 12 + R() * 10, depth = 14 + R() * 8, fl = 2 + Math.floor(R() * 3);
        shopFronts.push(...insula(E, s * (6.9 + depth / 2), z - len / 2, len, depth, fl, s, cols[Math.floor(R() * cols.length)], R)); z -= len + (R() < .3 ? 4 : .3); }
      for (let z = 60; z > -90; z -= 30 + R() * 20) { const d = 18 + R() * 8, l = 16 + R() * 10, h = 3 + Math.floor(R() * 3); insula(E, s * (30 + d / 2 + R() * 6), z, l, d, h, s, cols[Math.floor(R() * cols.length)], R); } } }
  shopFronts.forEach(([x, z], i) => { if (i % 3 === 0) oilLamp(E, x - Math.sign(x) * .2, 1.0, z); });
  [[-5.2, 18], [5.2, -12], [-5.2, -46]].forEach(([x, z], i) => torch(E, x, 2.6, z, { light: true, power: 10, range: 14 }));

  // ---------- square: temple, market, fountain, trees ----------
  temple(E, -52, -112, 20, 34, Math.PI / 2);
  { const R = rng(17); for (let i = 0; i < 9; i++) stall(E, 18 + (i % 3) * 4.2, -106 - Math.floor(i / 3) * 4.5, -Math.PI / 2, R); }
  coneFountain(E, -40, -150, 17);
  for (let i = 0; i < 6; i++) coneTree(E, -24 - i * 7, -96, 1.2 + hash(i, 1) * .3, 400 + i);
  for (let i = 0; i < 5; i++) roundTree(E, 34 + i * 9, -95 - hash(i, 3) * 4, 1.4, 500 + i);
  for (let i = 0; i < 8; i++) amphora(E, 14 + hash(i, 2) * 3, -101 - i * .7, 1.1);
  // hills in the distance (Palatine, Esquiline) with pines and villas
  { const R = rng(23);
    for (const [x, z, r, h] of [[-330, -260, 150, 38], [300, -330, 170, 30], [-120, -560, 220, 45], [200, 120, 160, 26], [-280, 80, 140, 22]]) {
      const m = S(new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), lam(0x7a7a52))); m.scale.set(r, h, r * .8); m.position.set(x, -1, z); scene.add(m);
      for (let i = 0; i < 14; i++) { const a = R() * 6.28, q = Math.sqrt(R()) * .8, px = x + Math.cos(a) * r * q, pz = z + Math.sin(a) * r * .8 * q, py = h * Math.sqrt(Math.max(0, 1 - q * q)) - 1;
        if (R() < .6) { const t = roundTree(E, px, pz, 2.2, 600 + i * 7 + x); t.position.y = py; }
        else { const v = S(new THREE.Mesh(new THREE.BoxGeometry(12, 6, 9), lam([0xe0c89a, 0xc9935a, 0xd8cdb4][Math.floor(R() * 3)]))); v.position.set(px, py + 3, pz); scene.add(v); } } } }

  // ---------- THE COLOSSEUM ----------
  const stoneTex = romanTex(E, 0xd8ccb0, 'stone').clone(); stoneTex.needsUpdate = true; stoneTex.repeat.set(.25, .25);
  const TRAV = lam(0xffffff, { map: stoneTex }), TRAV2 = lam(0xb9ad94), DARK = lam(0x2a241e), INNER = lam(0x9e927a);
  const inst = (geo, mat, list, shadow = true) => { const im = new THREE.InstancedMesh(geo, mat, list.length), M4 = new THREE.Matrix4(), q = new THREE.Quaternion(), Y = new THREE.Vector3(0, 1, 0);
    list.forEach(([x, y, z, ry, sx = 1, sy = 1, sz = 1], i) => { q.setFromAxisAngle(Y, ry); M4.compose(new THREE.Vector3(x, y, z), q, new THREE.Vector3(sx, sy, sz)); im.setMatrixAt(i, M4); });
    im.castShadow = shadow; im.receiveShadow = true; scene.add(im); return im; };
  const W0 = 6.8, DEP = 2.4;
  const archGeo = (H, open, spring) => { const s = new THREE.Shape(); s.moveTo(-W0 / 2, 0); s.lineTo(W0 / 2, 0); s.lineTo(W0 / 2, H); s.lineTo(-W0 / 2, H); s.closePath();
    const h = new THREE.Path(), r = open / 2; h.moveTo(-r, 0); h.lineTo(r, 0); h.lineTo(r, spring); h.absarc(0, spring, r, 0, Math.PI, false); h.lineTo(-r, 0); s.holes.push(h);
    const g = new THREE.ExtrudeGeometry(s, { depth: DEP, bevelEnabled: false, curveSegments: 6 }); g.translate(0, 0, -DEP / 2); return g; };
  const ST = [[0, 10.5, 4.2, 5.2], [10.5, 11.8, 4.2, 5.4], [22.3, 11.6, 4.2, 5.3]];      // storey: y0, height, opening, spring height
  const dOut = 50.5 - DEP / 2, dIn = 44.5;
  ST.forEach(([y0, H, op, sp], si) => {
    const geo = archGeo(H, op, sp), out = [], inn = [], cols = [], band = [], floor = [];
    for (let k = 0; k < NB; k++) {
      const b = bay(k, dOut), bi = bay(k, dIn), sx = b.w / W0;
      out.push([b.x, y0, b.z, b.ry, sx, 1, 1]); inn.push([bi.x, y0, bi.z, bi.ry, bi.w / W0, 1, 1]);
      const [px, pz] = ell(dOut + DEP / 2 + .25, thetas[k]); cols.push([px, y0 + .6, pz, b.ry]);
      const bb = bay(k, dOut + .5); band.push([bb.x, y0 + H - .55, bb.z, b.ry, b.w * 1.02, 1, 1]);
      const bf = bay(k, (dOut + dIn) / 2); floor.push([bf.x, y0 + H - .3, bf.z, b.ry, b.w * 1.02, 1, 1]);
    }
    inst(geo, TRAV, out); inst(geo, INNER, inn);
    const cg = new THREE.CylinderGeometry(.5, .55, H - 1.8, 8, 1, false, -Math.PI / 2, Math.PI); cg.translate(0, (H - 1.8) / 2, 0); inst(cg, TRAV2, cols);
    inst(new THREE.BoxGeometry(1, 1.1, DEP + 1.1), TRAV2, band);
    if (si > 0) inst(new THREE.BoxGeometry(1, .6, dOut - dIn), INNER, floor, false);
  });
  { // attic (solid wall with small windows), corbels, masts for the velarium
    const y0 = 33.9, H = 14.6, wall = [], win = [], corb = [], masts = [], top = [];
    for (let k = 0; k < NB; k++) {
      const b = bay(k, dOut); wall.push([b.x, y0 + H / 2, b.z, b.ry, b.w * 1.01, 1, 1]);
      if (k % 2 === 0) { const bw = bay(k, dOut + DEP / 2 + .02); win.push([bw.x, y0 + 6.5, bw.z, b.ry]); }
      for (let j = 0; j < 3; j++) { const th = thetas[k] + (j + .5) / 3 * (2 * Math.PI / NB); const [cx, cz] = ell(dOut + DEP / 2 + .35, th), ry = b.ry;
        corb.push([cx, y0 + 10.6, cz, ry]); masts.push([cx, y0 + 11.2, cz, ry]); }
      const bt = bay(k, dOut + .3); top.push([bt.x, y0 + H + .3, bt.z, b.ry, b.w * 1.02, 1, 1]);
    }
    inst(new THREE.BoxGeometry(1, H, DEP), TRAV, wall);
    inst(new THREE.PlaneGeometry(1.3, 2.4), DARK, win, false);
    inst(new THREE.BoxGeometry(.6, .5, .7), TRAV2, corb);
    const mg = new THREE.CylinderGeometry(.16, .2, 12, 5); mg.translate(0, 6, 0); E.masts = inst(mg, lam(0x6a5038), masts);
    inst(new THREE.BoxGeometry(1, .7, DEP + .8), TRAV2, top);
    E.mastTops = masts.map(([x, y, z]) => [x, y + 12, z]);
  }
  // ground-floor gate numbers above the arches (76 numbered; the 4 gates on the axes have none)
  { const cv = document.createElement('canvas'); cv.width = 1024; cv.height = 1024; const x = cv.getContext('2d');
    x.fillStyle = '#d8ccb0'; x.fillRect(0, 0, 1024, 1024); x.fillStyle = '#3b3328'; x.font = '600 50px serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
    let num = 0; const nums = [];
    for (let k = 0; k < NB; k++) { const axis = k % 20 === 0; nums.push(axis ? '' : roman_(++num)); }
    nums.forEach((s, k) => { const cx = (k % 10) * 102.4 + 51.2, cy = Math.floor(k / 10) * 128 + 64; x.fillText(s, cx, cy); });
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const mat = lam(0xffffff, { map: tex });
    for (let k = 0; k < NB; k++) {
      const b = bay(k, dOut + DEP / 2 + .03), g = new THREE.PlaneGeometry(2.4, 1.2), uv = g.attributes.uv, u0 = (k % 10) / 10, v0 = 1 - (Math.floor(k / 10) + 1) / 8;
      for (let i = 0; i < 4; i++) uv.setXY(i, u0 + uv.getX(i) / 10, v0 + uv.getY(i) / 8);
      const m = new THREE.Mesh(g, mat); m.position.set(b.x, 9.4, b.z); m.rotation.y = b.ry; scene.add(m);
    }
    E.gateNums = nums;
  }

  // ---------- the cavea (seating bowl): profile [d, y, kind] around the arena ----------
  const PROF = [[0, 0, 'wall'], [0, 4, 'floor'], [3.5, 4, 'seat'], [15, 12.6, 'wall'], [15, 14.6, 'floor'], [15.6, 14.6, 'seat'], [29, 25, 'wall'], [29, 28.4, 'floor'],
                [29.6, 28.4, 'wood'], [40, 35.6, 'floor'], [46, 35.6, 'wall'], [46, 48.6, 'end']];
  { const seg = 200, seatTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const x = cv.getContext('2d');
      x.fillStyle = '#d6cbb2'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#8f8470'; x.fillRect(0, 40, 64, 24); x.fillStyle = '#b8ad96'; x.fillRect(0, 36, 64, 4);
      const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; return t; })();
    const wood = seatTex.clone(); wood.needsUpdate = true;
    const mats = { seat: lam(0xffffff, { map: seatTex, side: THREE.DoubleSide }), wood: lam(0xc49a6a, { map: wood, side: THREE.DoubleSide }),
      wall: lam(0xcfc3a8, { side: THREE.DoubleSide }), floor: lam(0xbdb197, { side: THREE.DoubleSide }) };
    const kinds = ['seat', 'wood', 'wall', 'floor'];
    const pos = [], uv = [], groups = kinds.map(() => []);
    for (let p = 0; p < PROF.length - 1; p++) {
      const [d0, y0, kind] = PROF[p], [d1, y1] = PROF[p + 1], rows = Math.max(1, Math.round(Math.hypot(d1 - d0, y1 - y0) / .8));
      for (let i = 0; i < seg; i++) {
        const t0 = i / seg * 2 * Math.PI, t1 = (i + 1) / seg * 2 * Math.PI;
        const q = (d, y, t) => { const [x, z] = ell(d, t); return [x, y, z]; };
        const a = q(d0, y0, t0), b = q(d0, y0, t1), c = q(d1, y1, t1), dd = q(d1, y1, t0);
        const base = pos.length / 3; pos.push(...a, ...b, ...c, ...a, ...c, ...dd);
        const u0 = i * 2, u1 = (i + 1) * 2; uv.push(u0, 0, u1, 0, u1, rows, u0, 0, u1, rows, u0, rows);
        groups[kinds.indexOf(kind)].push(base);
      }
    }
    // reorder by material so each material is one draw call
    const P2 = [], U2 = [], geo = new THREE.BufferGeometry(); let start = 0;
    kinds.forEach((k, mi) => { for (const b of groups[mi]) { P2.push(...pos.slice(b * 3, b * 3 + 18)); U2.push(...uv.slice(b * 2, b * 2 + 12)); }
      geo.addGroup(start, groups[mi].length * 6, mi); start += groups[mi].length * 6; });
    geo.setAttribute('position', new THREE.Float32BufferAttribute(P2, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(U2, 2)); geo.computeVertexNormals();
    const cav = new THREE.Mesh(geo.toNonIndexed ? geo : geo, kinds.map(k => mats[k])); cav.receiveShadow = true; cav.castShadow = true; scene.add(cav);
    geo.deleteAttribute('normal'); geo.computeVertexNormals();
  }
  // substructure: a solid ring under the stands (vaults), so the arches open onto a corridor, not onto the far stands
  { const ring = [], NR = 160; for (let k = 0; k < NR; k++) { const th = (k + .5) / NR * 2 * Math.PI, [x, z] = ell(dIn - 3, th), [x1, z1] = ell(dIn - 3, k / NR * 6.283), [x2, z2] = ell(dIn - 3, (k + 1) / NR * 6.283);
      ring.push([x, 17.5, z, Math.atan2(Math.cos(th) / (A0 + dIn - 3), Math.sin(th) / (B0 + dIn - 3)), Math.hypot(x2 - x1, z2 - z1) * 1.03, 1, 1]); }
    inst(new THREE.BoxGeometry(1, 35, 1.2), lam(0x8c816c), ring, false); }
  // vomitoria (dark doorways in the stands) and stair lines
  { const vom = [], stairs = [];
    for (const [d, y, n, len] of [[9, 8.2, 32, 0], [22, 20, 40, 0], [34, 31.5, 48, 0]]) for (let k = 0; k < n; k++) {
      const th = (k + .5) / n * 2 * Math.PI, [x, z] = ell(d, th), nx = Math.cos(th) / (A0 + d), nz = Math.sin(th) / (B0 + d), ry = Math.atan2(nx, nz);
      vom.push([x, y, z, ry]);
    }
    inst(new THREE.BoxGeometry(1.9, 1.5, 1.4).translate(0, -.35, 0), lam(0x3a3128), vom, false);
    inst(new THREE.BoxGeometry(2.5, .25, 1.5).translate(0, .52, 0), lam(0xd6ccb4), vom, false);
    for (const [dA, yA, dB, yB, n] of [[3.5, 4, 15, 12.6, 64], [15.6, 14.6, 29, 25, 80], [29.6, 28.4, 40, 35.6, 96]]) for (let k = 0; k < n; k++) {
      const th = k / n * 2 * Math.PI, [xa, za] = ell(dA, th), [xb, zb] = ell(dB, th), len = Math.hypot(xb - xa, zb - za, yB - yA);
      const m = new THREE.Mesh(new THREE.BoxGeometry(.9, .08, len), lam(0xe2d8c0)); m.position.set((xa + xb) / 2, (yA + yB) / 2 + .05, (za + zb) / 2);
      m.lookAt(xb, yB + .05, zb); m.receiveShadow = true; scene.add(m); stairs.push(m);
    }
  }
  // top gallery colonnade + roof (where the poorest stand)
  { const cols = [], NC = 160; for (let k = 0; k < NC; k++) { const th = k / NC * 2 * Math.PI, [x, z] = ell(41, th); cols.push([x, 35.6, z, 0]); }
    const cg = new THREE.CylinderGeometry(.35, .4, 8.6, 7); cg.translate(0, 4.3, 0); inst(cg, TRAV2, cols);
    const roofS = [], NR = 120; for (let k = 0; k < NR; k++) { const th = (k + .5) / NR * 2 * Math.PI, [x, z] = ell(43.5, th), [x1, z1] = ell(43.5, k / NR * 2 * Math.PI), [x2, z2] = ell(43.5, (k + 1) / NR * 2 * Math.PI);
      roofS.push([x, 44.4, z, Math.atan2(Math.cos(th) / (A0 + 43.5), Math.sin(th) / (B0 + 43.5)), Math.hypot(x2 - x1, z2 - z1) * 1.04, 1, 1]); }
    inst(new THREE.BoxGeometry(1, .5, 6.4), lam(0xa5583a), roofS); }
  // arena: sand floor with trapdoors, podium wall with a painted band and a net railing, emperor's box on the minor axis
  { const sand = new THREE.Mesh(new THREE.CircleGeometry(1, 64), lam(0xd9c49a)); sand.scale.set(A0, B0, 1); sand.rotation.x = -Math.PI / 2; sand.position.set(0, .03, ZC); sand.receiveShadow = true; sand.castShadow = !!TL.hypogeum; scene.add(sand);
    E.arenaFloor = sand;
    const R = rng(29), traps = [];
    for (let i = 0; i < 26; i++) { const a = R() * 6.283, q = Math.sqrt(R()) * .78; traps.push([Math.cos(a) * A0 * q, .04, ZC + Math.sin(a) * B0 * q, R() * .3]); }
    E.traps = traps;
    inst(new THREE.BoxGeometry(2.2, .02, 1.8), lam(0x8a7458), traps, false);
    const band = [], NBd = 120; for (let k = 0; k < NBd; k++) { const th = (k + .5) / NBd * 2 * Math.PI, [x, z] = ell(-.05, th), [x1, z1] = ell(-.05, k / NBd * 6.283), [x2, z2] = ell(-.05, (k + 1) / NBd * 6.283);
      band.push([x, 2.6, z, Math.atan2(Math.cos(th) / A0, Math.sin(th) / B0), Math.hypot(x2 - x1, z2 - z1) * 1.02, 1, 1]); }
    inst(new THREE.BoxGeometry(1, 1.4, .1), lam(0x8a3a30), band, false);
    const net = [], NN = 160; for (let k = 0; k < NN; k++) { const th = k / NN * 6.283, [x, z] = ell(.3, th); net.push([x, 4, z, 0]); }
    inst(new THREE.CylinderGeometry(.05, .05, 2.2, 4).translate(0, 1.1, 0), lam(0x5a4a3a), net);
    // emperor's box (pulvinar): south side, red cloth, four columns and a little roof
    const [px, pz] = ell(2, Math.PI / 2), g = new THREE.Group(); g.position.set(px, 4, pz); scene.add(g);
    const cl = S(new THREE.Mesh(new THREE.BoxGeometry(10, 1.2, .2), lam(0x8e2a2a))); cl.position.set(0, .6, -2.2); g.add(cl);
    for (const x of [-4.6, -1.6, 1.6, 4.6]) { const c = S(new THREE.Mesh(new THREE.CylinderGeometry(.22, .25, 4.6, 8), lam(0xe6dfcf))); c.position.set(x, 2.3, -2); g.add(c); }
    const rf = S(new THREE.Mesh(new THREE.BoxGeometry(11, .4, 4), lam(0xe6dfcf))); rf.position.set(0, 4.8, -.4); g.add(rf);
    const aw = S(new THREE.Mesh(new THREE.BoxGeometry(10.6, .05, 3.6), lam(0x7a1e3a))); aw.position.set(0, 5.1, -.4); g.add(aw);
  }
  // torches along the podium and in the gate arches (flames; a few with light)
  for (let k = 0; k < 24; k++) { const th = (k + .5) / 24 * 6.283, [x, z] = ell(.4, th); torch(E, x, 4.2, z, { light: k % 6 === 0, power: 18, range: 22 }); }

  // ---------- the velarium: sails between the mast tops and a rope ring over the arena ----------
  { const VEL = monotone(TL.velarium || [[0, 0]]), n = NB * 3, ringD = -14, rimD = dOut + DEP / 2 + .35, yRim = 33.9 + 11.2 + 11.6, yRing = 40;
    const ropePos = new Float32Array(n * 6);
    for (let k = 0; k < n; k++) { const th = thetas[Math.floor(k / 3)] + ((k % 3) + .5) / 3 * (2 * Math.PI / NB), [x0, z0] = ell(rimD, th), [x1, z1] = ell(ringD, th);
      ropePos.set([x0, yRim, z0, x1, yRing, z1], k * 6); }
    const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.BufferAttribute(ropePos, 3));
    const ropes = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x3a3028, transparent: true, opacity: .55 })); scene.add(ropes);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1, .012, 4, 96), lam(0x3a3028)); ring.scale.set(A0 + ringD, B0 + ringD, 1); ring.rotation.x = Math.PI / 2; ring.position.set(0, yRing, ZC); scene.add(ring);
    // sails: 80 sectors; each a strip from the rim inward to the pulled-out edge
    const SEG = NB, sp = new Float32Array(SEG * 6 * 3 * 4), sGeo = new THREE.BufferGeometry(); sGeo.setAttribute('position', new THREE.BufferAttribute(sp, 3));
    const colA = [], cs = [0xe6dcc4, 0xe6dcc4, 0xc98a4a, 0xe6dcc4, 0xb5553f, 0xe6dcc4];
    for (let k = 0; k < SEG; k++) { const c = new THREE.Color(cs[k % cs.length]); for (let v = 0; v < 24; v++) colA.push(c.r, c.g, c.b); }
    sGeo.setAttribute('color', new THREE.Float32BufferAttribute(colA, 3));
    const sails = new THREE.Mesh(sGeo, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide, flatShading: true }));
    sails.castShadow = true; sails.receiveShadow = true; sails.frustumCulled = false; scene.add(sails);
    let last = -1;
    E.updates.push(t => { const u = clamp(VEL(t)); if (Math.abs(u - last) < 1e-4) return; last = u; sails.visible = u > .01;
      const inner = rimD - (rimD - ringD - 6) * u;
      for (let k = 0; k < SEG; k++) { const ta = thetas[k] + .01, tb = thetas[(k + 1) % NB] - .01 + (k === NB - 1 ? 2 * Math.PI : 0);
        const pts = [];
        for (let j = 0; j < 4; j++) { const d0 = rimD + (inner - rimD) * j / 4, d1 = rimD + (inner - rimD) * (j + 1) / 4;
          const y = d => yRim + (yRing - yRim) * (rimD - d) / (rimD - ringD) - Math.sin(Math.PI * (rimD - d) / (rimD - ringD)) * 1.6;   // a little sag
          const [ax, az] = ell(d0, ta), [bx, bz] = ell(d0, tb), [cx, cz] = ell(d1, tb), [dx, dz] = ell(d1, ta);
          pts.push(ax, y(d0), az, bx, y(d0), bz, cx, y(d1), cz, ax, y(d0), az, cx, y(d1), cz, dx, y(d1), dz); }
        sp.set(pts, k * 72); }
      sGeo.attributes.position.needsUpdate = true; sGeo.computeVertexNormals(); sGeo.computeBoundingSphere(); });
  }
  // sailors from the fleet on top of the attic, at the masts
  { const R = rng(91); for (let i = 0; i < 26; i++) { const k = Math.floor(R() * NB), th = thetas[k] + R() * .06, [x, z] = ell(dOut - .2, th), face = Math.atan2(-Math.cos(th), -Math.sin(th) * .8);
      roman(E, 7000 + i, { kind: 'sailor', y: 48.7, path: t => ({ x, z, rot: face, moving: 0, speed: 0, headUp: .3, arms: R() < .5 ? 'point' : undefined }) }); } }

  // ---------- the seated crowd (instanced): rows on the three seating tiers ----------
  { const seats = [], R = rng(13);
    for (const [dA, yA, dB, yB] of [[3.5, 4, 15, 12.6], [15.6, 14.6, 29, 25], [29.6, 28.4, 40, 35.6]]) {
      const rows = Math.round(Math.hypot(dB - dA, yB - yA) / .8);
      for (let r = 0; r < rows; r++) { const d = dA + (dB - dA) * (r + .5) / rows, y = yA + (yB - yA) * (r + .3) / rows;
        const per = 2 * Math.PI * Math.sqrt(((A0 + d) ** 2 + (B0 + d) ** 2) / 2), n = Math.floor(per / .85);
        for (let i = 0; i < n; i++) { const th = (i + R() * .3) / n * 2 * Math.PI;
          if (Math.abs(Math.sin(th * 20)) < .06) continue;                 // keep the stair lanes free
          const [x, z] = ell(d, th); seats.push([x, y - .05, z, Math.atan2(-Math.cos(th), -Math.sin(th))]); } } }
    for (let i = 0; i < 1400; i++) { const th = R() * 6.283, [x, z] = ell(41.8 + R() * 3, th); seats.push([x, 35.6 + .3, z, 0]); }   // standing at the top
    const C = TL.crowd || {}, f = monotone(C.fill || [[0, 1]]), s = monotone(C.stand || [[0, 0]]), c = monotone(C.cheer || [[0, 0]]);
    E.crowdN = seats.length;
    spectators(E, TL, seats, { fill: t => f(t), stand: t => s(t), cheer: t => c(t), order: (i, R2) => R2() });
  }

  // ---------- people outside: the stream along the street to the gate, and over the square ----------
  const gk = TL.gateBay ?? 22, gb = bay(gk, dOut + 6);
  E.gateBay = gk; E.gate = gb;
  for (const G of TL.groups || []) if (G.gate) { const [dn, lat] = G.gate, b = bay(gk, dOut + DEP / 2 + dn); G.at = [b.x + b.n[1] * lat, b.z - b.n[0] * lat]; G.y = 0; G.face ??= Math.atan2(-b.n[0], -b.n[1]); if (G.shot) G.shot.from = [b.n[0] * 7 + b.n[1] * 2, 1.6, b.n[1] * 7 - b.n[0] * 2]; }
  stream(E, TL, { pts: [[0, 70], [0, -90], [gb.x * .6, -140], [gb.x, gb.z]], n: 90, w: 3.4, seed: 61, start: TL.streamStart ?? 0, torches: .05 });
  stream(E, TL, { pts: [[-120, -120], [-60, -150], [gb.x - 4, gb.z + 2]], n: 40, w: 4, seed: 62, start: TL.streamStart ?? 0 });
  stream(E, TL, { pts: [[130, -110], [60, -140], [gb.x + 4, gb.z + 2]], n: 40, w: 4, seed: 63, start: TL.streamStart ?? 0 });
  if (TL.panic) { const th0 = Math.PI / 2 + Math.PI * 3 / 20, pts = []; for (let k = 0; k <= 12; k++) { const [x, z] = ell(15.3, th0 + k * .05); pts.push([x, z]); }
    stream(E, TL, { pts, n: 46, w: .25, v: 2.4, seed: 71, y: 14.6, start: TL.panic, loop: true }); }
  // guards at the gate
  for (const s of [-1, 1]) { const [x, z] = ell(dOut + DEP / 2 + 1.5, thetas[gk] + (s > 0 ? 2 * Math.PI / NB * .95 : .02));
    roman(E, 8100 + s, { kind: 'soldier', y: .02, path: () => ({ x, z, rot: Math.atan2(gb.n[0], gb.n[1]), moving: 0, speed: 0 }) }); }


  // ---------- the hypogeum (TL.hypogeum): tunnels under the arena floor, cages, a lift with a winch ----------
  //   TL.lift = [a, b]: the lift with the cage rises from the tunnel floor up to the trapdoor between a and b (trapdoor opens at a + 1)
  const HY = -6.5, LX = 8, LZ = ZC + 5.3;
  if (TL.hypogeum) {
    const [la, lb] = TL.lift || [1e9, 1e9], liftY = t => HY + (-.35 - HY) * smooth(la, lb, t);
    const inEll = (x, z, d = 0) => (x / (A0 + d)) ** 2 + ((z - ZC) / (B0 + d)) ** 2 < 1;
    E._t = 0; E.updates.unshift((t) => { E._t = t; });
    E.groundAt = (x, z) => Math.abs(x - LX) < 1.3 && Math.abs(z - LZ) < 1.7 ? liftY(E._t) : inEll(x, z) ? HY : 0;
    const fl = new THREE.Mesh(new THREE.CircleGeometry(1, 48), lam(0x5a4a38)); fl.scale.set(A0, B0, 1); fl.rotation.x = -Math.PI / 2; fl.position.set(0, HY, ZC); fl.receiveShadow = true; scene.add(fl);
    const ce = new THREE.Mesh(new THREE.CircleGeometry(1, 48), lam(0x4a3828)); ce.scale.set(A0, B0, 1); ce.rotation.x = Math.PI / 2; ce.position.set(0, -.08, ZC); scene.add(ce);
    const beams = []; for (let x = -A0 + 1; x < A0; x += 2.2) beams.push([x, -.35, ZC, 0, 1, 1, 2 * B0 * Math.sqrt(Math.max(0, 1 - (x / A0) ** 2))]);
    inst(new THREE.BoxGeometry(.3, .45, 1), lam(0x5a4430), beams, false);
    const ring = [], NR = 90; for (let k = 0; k < NR; k++) { const th = (k + .5) / NR * 6.283, [x, z] = ell(0, th), [x1, z1] = ell(0, k / NR * 6.283), [x2, z2] = ell(0, (k + 1) / NR * 6.283);
      ring.push([x, HY / 2, z, Math.atan2(Math.cos(th) / A0, Math.sin(th) / B0), Math.hypot(x2 - x1, z2 - z1) * 1.05, 1, 1]); }
    inst(new THREE.BoxGeometry(1, -HY, 1), lam(0x7d6c56), ring, false);
    // tunnel walls parallel to the long axis, with doorways; the central corridor (|dz| < 3) stays open
    const walls = [];
    for (const dz of [-21, -16.5, -12, -7.5, -3, 3, 7.5, 12, 16.5, 21]) { const half = A0 * Math.sqrt(Math.max(0, 1 - (dz / B0) ** 2)) - 1;
      for (let x = -half; x < half - 2; x += 6) { if ((dz === 3 || dz === 7.5) && x + 4 > LX - 4.5 && x < LX + 4.5) continue; walls.push([x + 2, HY / 2, ZC + dz, 0, 4, 1, 1]); } }
    inst(new THREE.BoxGeometry(1, -HY, .8), lam(0x8f8270), walls, false);
    // the lift: four posts, a platform, a cage with bars (and a lion in it via TL.animals), a rope to the winch
    const lift = new THREE.Group(); scene.add(lift);
    const plat = S(new THREE.Mesh(new THREE.BoxGeometry(2.8, .2, 3.6), lam(0x6a5038))); lift.add(plat);
    const bar = lam(0x3a3430);
    for (let i = 0; i < 9; i++) for (const sx of [-1, 1]) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 2.1, 4), bar); b.position.set(sx * 1.3, 1.1, -1.7 + i * .425); lift.add(b); }
    for (let i = 0; i < 7; i++) for (const sz of [-1, 1]) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 2.1, 4), bar); b.position.set(-1.3 + i * .433, 1.1, sz * 1.7); lift.add(b); }
    const top = S(new THREE.Mesh(new THREE.BoxGeometry(2.8, .12, 3.6), lam(0x5a4430))); top.position.y = 2.2; lift.add(top);
    for (const [px, pz] of [[-1.5, -1.9], [1.5, -1.9], [-1.5, 1.9], [1.5, 1.9]]) { const p2 = S(new THREE.Mesh(new THREE.BoxGeometry(.25, -HY, .25), lam(0x5a4430))); p2.position.set(LX + px, HY / 2, LZ + pz); scene.add(p2); }
    // winch (capstan) in the corridor, pushed round by workers
    const cap = new THREE.Group(); cap.position.set(LX - 1, HY, ZC - .2); scene.add(cap);
    const drum = S(new THREE.Mesh(new THREE.CylinderGeometry(.45, .5, 1.6, 10), lam(0x6a5038))); drum.position.y = .8; cap.add(drum);
    for (let k = 0; k < 4; k++) { const sp = S(new THREE.Mesh(new THREE.BoxGeometry(3.2, .12, .12), lam(0x5a4430))); sp.position.y = 1.1; sp.rotation.y = k * Math.PI / 4; cap.add(sp); }
    const rot = t => 1.1 * Math.max(0, Math.min(t, lb) - la);
    E.updates.push(t => { const y = liftY(t); lift.position.set(LX, y + .1, LZ); cap.rotation.y = rot(t); });
    for (let i = 0; i < 4; i++) roman(E, 9100 + i, { kind: 'tunic', y: HY, path: t => { const a = rot(t) + i * Math.PI / 2;
      return { x: LX - 1 + Math.cos(a) * 1.5, z: ZC - .2 - Math.sin(a) * 1.5, rot: a + Math.PI, moving: t > la && t < lb ? 1 : 0, speed: 1, stoop: .25 }; } });
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 1, 4), lam(0x8a7458)); scene.add(rope);
    E.updates.push(t => { const a = new THREE.Vector3(LX - 1, HY + 1.2, ZC - .2), b = new THREE.Vector3(LX, -.4, LZ - 1.8); rope.position.copy(a).lerp(b, .5); rope.scale.y = a.distanceTo(b); rope.lookAt(b); rope.rotateX(Math.PI / 2); });
    // trapdoor: daylight pours in when it opens (a glowing patch in the ceiling + a soft beam)
    const glow = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 3.6), new THREE.MeshBasicMaterial({ color: 0xfff1d6 })); glow.rotation.x = Math.PI / 2; glow.position.set(LX, -.1, LZ); scene.add(glow);
    const beamM = new THREE.MeshBasicMaterial({ color: 0xffe6b8, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false });
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.7, -HY, 4, 1, true), beamM); beam.rotation.y = Math.PI / 4; beam.position.set(LX, HY / 2, LZ); scene.add(beam);
    const sunL = new THREE.SpotLight(0xffe2b0, 0, 14, .7, .5, 1.2); sunL.position.set(LX, -.2, LZ); sunL.target.position.set(LX, HY, LZ); scene.add(sunL, sunL.target);
    E.updates.push(t => { const o = smooth(la + 1, la + 2.2, t); glow.visible = o > .01; glow.material.color.setRGB(o, o * .95, o * .84); beamM.opacity = o * .07; sunL.intensity = o * 60; });
    // more cages along the corridor, lamps and torches, crates, amphorae, hay
    for (const [cx, cz] of [[-6, ZC + 5.3], [-18, ZC - 5.3], [20, ZC - 5.3]]) { for (let i = 0; i < 8; i++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.03, .03, 2.2, 4), bar); b.position.set(cx - 1.5 + i * .43, HY + 1.1, cz + (cz > ZC ? -1.9 : 1.9)); scene.add(b); } }
    for (const x of [-26, -12, 2, 16, 28]) torch(E, x, HY + 2.2, ZC + (x % 4 ? 2.6 : -2.6), { light: true, always: true, power: 7, range: 18, color: 0xffb868 });
    torch(E, LX - 2.2, HY + 2.3, ZC + 3.4, { light: true, always: true, power: 9, range: 12, color: 0xffb868 });
    for (let x = -30; x < 30; x += 7) oilLamp(E, x + 2, HY + 1.4, ZC + 2.6);
    for (let i = 0; i < 10; i++) { const c = S(new THREE.Mesh(new THREE.BoxGeometry(.8, .7, .8), lam(0x7a5a3a))); c.position.set(-24 + i * 4.3 + hash(i, 3) * 2, HY + .35, ZC + (i % 2 ? 2.4 : -2.4)); c.rotation.y = hash(i, 4); scene.add(c); }
    for (let i = 0; i < 6; i++) amphora(E, -10 + i * .6, ZC - 2.5, 1.2).position.y = HY;
    E.updates.push((t, F, tv) => { let nm = TL.shots[0][1]; for (const [a, n] of TL.shots) if (tv >= a) nm = n;
      if (!/hypo/.test(nm)) return;
      E.hemi.intensity = 1.15; E.hemi.color.setHex(0xd6c2a4); E.hemi.groundColor.setHex(0x3a3028); E.sun.intensity = 0; E.dark = 1;
      scene.fog.color.setHex(0x2a2018); scene.fog.near = 12; scene.fog.far = 95; });
  }

  // ---------- shots ----------
  const out = (k, d, y, look = [0, 20, ZC]) => { const b = bay(k, d); return [b.x, y, b.z]; };
  const gOut2 = bay(gk, dOut + 24), gFar = bay(gk, dOut + 60), gIn = bay(gk, dIn - 4), gOut = bay(gk, dOut + 14), gNear = bay(gk, dOut + 5);
  const [vx, vz] = ell(22.4, Math.PI / 2 + .35), [tx, tz] = ell(48, -Math.PI / 2 + .5);
  const shots = {
    aerial: { pos: [150, 120, 40], look: [0, 10, ZC + 30], drift: [-6, 0, -3], fov: 50 },
    rooftop: { pos: [10, 24, 72], look: [0, 22, ZC], drift: [0, 0, -2.5], fov: 55 },
    street: { pos: [-2.6, 1.7, 34], look: [0, 16, ZC], drift: [0, 0, -1.2], fov: 60 },
    'pov-street': { pos: [1.4, 1.65, 8], look: [.4, 14, ZC], drift: [0, 0, -12], fov: 62, run: { freq: 1.8, amp: .025 } },
    square: { pos: [-20, 4, -92], look: [0, 24, ZC + 40], drift: [3, 0, -.6], fov: 55 },
    market: { pos: [26, 2.2, -92], look: [5, 10, -160], drift: [-.6, 0, -1], fov: 55 },
    facade: { pos: [gFar.x + gb.n[1] * 25, 2, gFar.z - gb.n[0] * 25], look: [gb.x, 22, gb.z], drift: [-1.5, 0, 0], fov: 55 },
    gate: { pos: [gOut2.x, 1.8, gOut2.z], look: [gNear.x, 7.2, gNear.z], drift: [-gb.n[0] * 3, 0, -gb.n[1] * 3], fov: 52 },
    'pov-gate': { pos: [gNear.x, 1.65, gNear.z], look: [gIn.x, 2.6, gIn.z], drift: [-gb.n[0] * 11, 0, -gb.n[1] * 11], fov: 62, run: { freq: 1.8, amp: .02 } },
    reveal: { pos: [vx, 22, vz], look: [0, 9, ZC - 6], drift: [-Math.cos(Math.PI / 2 + .35) * 1.2, .2, -Math.sin(Math.PI / 2 + .35) * 1.2], fov: 62 },
    bowl: { pos: [-A0 - 10, 30, ZC + 40], look: [20, 6, ZC - 10], drift: [0, 0, -1.2], fov: 60 },
    attic: { pos: [tx, 50.4, tz], look: [0, 30, ZC + 20], drift: [0, 0, 0], fov: 60 },
    sky: { pos: [0, 160, ZC + 200], look: [0, 0, ZC], drift: [0, 0, -4], fov: 50 },
    'hypo-corridor': { pos: [-30, HY + 1.7, ZC + .4], look: [20, HY + 1.6, ZC], drift: [1.5, 0, 0], fov: 60 },
    'pov-hypo': { pos: [-16, HY + 1.65, ZC - 1], look: [10, HY + 1.6, ZC + 1], drift: [6, 0, 0], fov: 62, run: { freq: 1.8, amp: .02 } },
    'hypo-cage': { pos: [4.6, HY + 1.5, ZC + 1.6], look: [LX, HY + .9, LZ], drift: [.3, 0, 0], fov: 50 },
    'hypo-lift': { pos: [2.5, HY + 1.2, ZC - 2], look: [LX, HY + 4.5, LZ], drift: [0, 0, 0], fov: 62 },
    'pov-seat': { pos: [...(([x, z]) => [x, 0, z])(ell(20, Math.PI / 2 + Math.PI * 4 / 20))].map((v, i) => i === 1 ? 19.6 : v), look: [0, 2, ZC], drift: [0, 0, 0], fov: 62 },
    'pov-crowd': { pos: [...(([x, z]) => [x, 0, z])(ell(18, Math.PI / 2 + Math.PI * 6 / 20))].map((v, i) => i === 1 ? 18.6 : v), look: [...(([x, z]) => [x, 14.6, z])(ell(15.3, Math.PI / 2 + Math.PI * 4.5 / 20))], drift: [0, 0, 0], fov: 62 },
    'pov-up': { pos: [...(([x, z]) => [x, 0, z])(ell(20, Math.PI / 2 + Math.PI * 4 / 20))].map((v, i) => i === 1 ? 19.6 : v), look: [...(([x, z]) => [x, 52, z])(ell(-5, Math.PI / 2 + Math.PI * 4 / 20 + Math.PI))], drift: [0, 0, 0], fov: 66 },
    'arena-up': { pos: [-12, 1.7, ZC + 6], look: [6, 30, ZC - 30], drift: [.5, 0, 0], fov: 66 },
    night: { pos: [gOut2.x * 1.0 + gb.n[1] * 30, 2.2, gOut2.z - gb.n[0] * 30], look: [gb.x, 18, gb.z], drift: [-.8, 0, 0], fov: 55 },
    arena: { pos: [-20, 1.7, ZC + 10], look: [10, 12, ZC - 25], drift: [1, 0, 0], fov: 62 },
  };
  E.sunOffset = new THREE.Vector3(150, 60, 120);
  return {
    ambience: TL.ambience || 'rome',
    look: () => ({ top: new THREE.Color(0x6d99c9), hor: new THREE.Color(0xdcdcd0), fogNear: 300, fogFar: 1800, hemi: 1.4, hemiColor: new THREE.Color(0xe3ecf4),
      groundColor: new THREE.Color(0x6a604c), sun: 2.2, sunColor: new THREE.Color(0xffeedd) }),
    shots,
  };
}
