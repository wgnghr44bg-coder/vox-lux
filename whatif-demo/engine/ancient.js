// ANCIENT ROME bricks (reusable): people in toga / tunic / stola / soldier / sailor, people walking in a stream,
// a seated crowd of thousands (one instanced mesh, cheap), oil lamps and torches, Roman houses (insulae with
// shops), a temple, market stalls, amphorae and a cone fountain. Used by places/colosseum.js.
import * as THREE from 'three';
import { person } from './props.js';
import { rng, hash, smooth, clamp } from './util.js';

const TUNIC = [0xd8cdb4, 0xc2ad86, 0xb79c74, 0x8a6e4e, 0x9b4a35, 0x6f7a5a, 0x5b6d82, 0xa98a5c, 0x7d5a44];
const STOLA = [0x8a5a7a, 0x4f6a8a, 0xc49a5a, 0xb86b4a, 0x6f8a6a, 0xd6c8a8];
const TOGA = 0xe9e4d6;

// one Roman: kind 'tunic' (default), 'toga', 'stola', 'soldier', 'sailor'; o as in props.person (path, y, react …)
export function roman(E, seed, o = {}) {
  const R = rng(seed * 31 + 7), kind = o.kind || 'tunic', pick = a => a[Math.floor(R() * a.length)];
  const top = kind === 'toga' ? TOGA : kind === 'stola' ? pick(STOLA) : kind === 'soldier' ? 0x9c2f26 : kind === 'sailor' ? pick([0x5d6e7e, 0x7b8a94, 0x4f5f6a]) : pick(TUNIC);
  return person(E, seed, { ...o, coat: top, skirt: true, shoe: 0x5a3d24, dress(p) {
    const { E: e, upper, headG, top: topM, skin } = p, M = c => e.lam(c), S = m => e.shadowed(m);
    if (kind === 'toga' || kind === 'stola') {           // long robe to the ankles
      const rob = S(new THREE.Mesh(new THREE.CylinderGeometry(.24, .3, .5, 8), topM)); rob.position.y = -.56; upper.add(rob);
    }
    if (kind === 'toga') {                               // the drape: over the left shoulder, across the chest
      const d = S(new THREE.Mesh(new THREE.BoxGeometry(.2, .7, .26), M(0xf1ede2))); d.position.set(-.06, .3, 0); d.rotation.z = .55; upper.add(d);
      if (R() < .3) { const st = new THREE.Mesh(new THREE.BoxGeometry(.04, .66, .27), M(0x7a2e48)); st.position.set(.02, .32, 0); st.rotation.z = .55; upper.add(st); }   // purple stripe
    }
    if (kind === 'stola' && R() < .6) {                  // palla over the head
      const pa = S(new THREE.Mesh(new THREE.SphereGeometry(.135, 8, 6, 0, Math.PI * 2, 0, Math.PI * .6), M(pick(STOLA)))); pa.position.set(0, .01, -.01); pa.rotation.x = -.35; headG.add(pa);
    }
    if (kind === 'soldier') {                            // segmented armour, helmet with crest, red cloak, short sword belt
      const ar = S(new THREE.Mesh(new THREE.CylinderGeometry(.2, .18, .4, 8), M(0x8d9096))); ar.position.y = .38; upper.add(ar);
      for (let k = 0; k < 3; k++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(.205, .19, .02, 8), M(0x5f6266)); b.position.y = .24 + k * .1; upper.add(b); }
      const h = S(new THREE.Mesh(new THREE.SphereGeometry(.13, 8, 6, 0, Math.PI * 2, 0, Math.PI * .55), M(0x9a8a5a))); h.position.y = .02; headG.add(h);
      const cr = S(new THREE.Mesh(new THREE.BoxGeometry(.04, .1, .26), M(0xa3241c))); cr.position.y = .16; headG.add(cr);
      const cl = S(new THREE.Mesh(new THREE.BoxGeometry(.4, .75, .04), M(0x8a2a22))); cl.position.set(0, .2, -.17); cl.rotation.x = .08; upper.add(cl);
      if (o.spear !== false) { const sp = new THREE.Mesh(new THREE.CylinderGeometry(.018, .018, 2.1, 5), M(0x5a4430)); sp.position.set(.3, .2, .1); upper.add(sp);
        const tip = new THREE.Mesh(new THREE.ConeGeometry(.04, .2, 5), M(0xb0b4b8)); tip.position.set(.3, 1.3, .1); upper.add(tip); }
    }
    if (kind === 'sailor') { const cap = S(new THREE.Mesh(new THREE.ConeGeometry(.12, .16, 7), M(0x8a6e4e))); cap.position.y = .14; headG.add(cap); }
    const belt = new THREE.Mesh(new THREE.CylinderGeometry(.165, .165, .04, 8), M(0x4a3424)); belt.position.y = .1; upper.add(belt);
    o.dress?.(p);
  } });
}

// a stream of people walking along a polyline (pts [[x, z], ...]) and vanishing at its end (a gate);
// n people spread along it, speed v, lateral spread w. Kinds are mixed (mostly tunics, some togas, stolas).
// o.start: time they begin to walk (before that they stand and chat); o.torches: share that carries a torch.
export function stream(E, TL, o) {
  const { pts, n = 40, v = 1.25, w = 3, seed = 61, y = .2 } = o, R = rng(seed);
  const seg = [], L = [0];
  for (let i = 1; i < pts.length; i++) { const dx = pts[i][0] - pts[i - 1][0], dz = pts[i][1] - pts[i - 1][1], l = Math.hypot(dx, dz); seg.push([dx / l, dz / l, l]); L.push(L[i - 1] + l); }
  const total = L[L.length - 1];
  const at = s => { let i = 0; while (i < seg.length - 1 && s > L[i + 1]) i++; const u = s - L[i]; return [pts[i][0] + seg[i][0] * u, pts[i][1] + seg[i][1] * u, Math.atan2(seg[i][0], seg[i][1])]; };
  const kinds = o.kinds || ['tunic', 'tunic', 'tunic', 'toga', 'stola', 'tunic', 'stola'];
  for (let i = 0; i < n; i++) {
    const off = (R() - .5) * 2 * w, s0 = R() * total, vv = v * (.85 + R() * .3), kind = kinds[Math.floor(R() * kinds.length)];
    const torch = R() < (o.torches ?? 0);
    const p = roman(E, seed * 100 + i, { kind, y, path(t) {
      const s = o.loop === false ? s0 + vv * Math.max(0, t - (o.start ?? 0)) : (s0 + vv * Math.max(0, t - (o.start ?? 0))) % total;
      if (s > total) return { visible: false };
      const [x, z, rot] = at(s), ang = rot + Math.PI / 2;
      return { x: x + Math.sin(ang) * off, z: z + Math.cos(ang) * off, rot, moving: t > (o.start ?? 0) ? 1 : 0, speed: vv, arms: torch ? 'torch' : undefined };
    } });
    if (torch) handTorch(E, p);
  }
  return { total, at };
}

// a torch held up in the right hand of a person (flame + a small warm light only for the first few)
let torchLights = 0;
function handTorch(E, p) {
  const g = new THREE.Group(), stick = new THREE.Mesh(new THREE.CylinderGeometry(.025, .03, .6, 5), E.lam(0x4a3424)); g.add(stick);
  const fl = flame(E, .16); fl.position.y = .38; g.add(fl);
  g.position.set(.3, 1.75, .15); p.g.add(g);
  if (torchLights++ < 3) { const L = new THREE.PointLight(0xff9a48, 0, 9, 1.8); L.position.y = .5; g.add(L); E.updates.push(t => { L.intensity = (E.dark ?? 0) * 6 * (1 + Math.sin(t * 17 + hash(torchLights, 2) * 9) * .12); }); }
  E.updates.push(t => { fl.scale.setScalar(1 + Math.sin(t * 19 + p.ph) * .12); fl.material.opacity = .65 + .35 * (E.dark ?? 0); });
}

// a flame: two crossed cones, additive (glows in the film look)
export function flame(E, s = .2) {
  const m = new THREE.MeshBasicMaterial({ color: 0xffa040, transparent: true, opacity: .9, blending: THREE.AdditiveBlending, depthWrite: false });
  const g = new THREE.Group();
  const a = new THREE.Mesh(new THREE.ConeGeometry(s * .45, s * 1.6, 6), m); a.position.y = s * .7; g.add(a);
  const b = new THREE.Mesh(new THREE.ConeGeometry(s * .25, s, 6), new THREE.MeshBasicMaterial({ color: 0xffe2a0, transparent: true, opacity: .95, blending: THREE.AdditiveBlending, depthWrite: false })); b.position.y = s * .45; g.add(b);
  g.material = m; return g;
}

// torch on a wall bracket or a pole; light: true adds a real point light (keep the number small, they are expensive)
export function torch(E, x, y, z, o = {}) {
  const g = new THREE.Group(); g.position.set(x, y, z); E.scene.add(g);
  const stick = E.shadowed(new THREE.Mesh(new THREE.CylinderGeometry(.04, .05, .7, 6), E.lam(0x3e2e20))); g.add(stick);
  const cup = new THREE.Mesh(new THREE.CylinderGeometry(.11, .06, .16, 6), E.lam(0x4a4440)); cup.position.y = .4; g.add(cup);
  const fl = flame(E, o.size ?? .3); fl.position.y = .46; g.add(fl);
  let L = null;
  if (o.light) { L = new THREE.PointLight(o.color ?? 0xff9a48, 0, o.range ?? 16, 1.7); L.position.y = .9; g.add(L); }
  const ph = hash(x * 13 + z, 5) * 10;
  E.updates.push(t => { const on = o.always ? 1 : E.dark ?? 0, fk = 1 + Math.sin(t * 17 + ph) * .1 + Math.sin(t * 7.3 + ph) * .06;
    fl.visible = on > .02; fl.scale.set(1, fk, 1); if (L) L.intensity = on * (o.power ?? 14) * fk; });
  return g;
}

// small clay oil lamp on a ledge (flame only, cheap)
export function oilLamp(E, x, y, z) {
  const g = new THREE.Group(); g.position.set(x, y, z); E.scene.add(g);
  const body = new THREE.Mesh(new THREE.SphereGeometry(.09, 7, 4), E.lam(0x9a5a38)); body.scale.set(1.4, .55, 1); g.add(body);
  const fl = flame(E, .07); fl.position.set(.12, .03, 0); g.add(fl);
  E.updates.push(t => { fl.visible = (E.dark ?? 0) > .05; fl.scale.set(1, 1 + Math.sin(t * 21 + x) * .15, 1); });
  return g;
}

// ---------- the seated crowd: thousands of spectators in ONE instanced mesh ----------
// seats: [[x, y, z, ry], ...]. Uniforms (driven by o.fill(t), o.stand(t), o.cheer(t)):
//   fill 0..1  how many seats are taken (they fill in a random order),
//   stand 0..1 how many stand up, cheer 0..1 how wildly they move (arms up, bounce).
export function spectators(E, TL, seats, o = {}) {
  const n = seats.length, R = rng(o.seed ?? 5);
  const torso = new THREE.BoxGeometry(.42, .55, .3); torso.translate(0, .28, 0);
  const head = new THREE.OctahedronGeometry(.13, 0); head.translate(0, .7, 0);
  const geo = mergeGeos([torso, head]);
  const cols = [...TUNIC, TOGA, TOGA, TOGA, ...STOLA];
  const mat = new THREE.MeshLambertMaterial({ color: 0xffffff, flatShading: true });
  const U = { uFill: { value: 0 }, uStand: { value: 0 }, uCheer: { value: 0 }, uTime: { value: 0 } };
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec2 aSeat; uniform float uFill, uStand, uCheer, uTime;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        float on = step(aSeat.x, uFill);
        float st = step(aSeat.x * .7 + aSeat.y * .3, uStand);
        float jump = uCheer * max(0., sin(uTime * (6. + aSeat.y * 4.) + aSeat.y * 40.)) * .22;
        transformed.y += st * .45 + jump * st;
        transformed *= on;`);
  };
  const im = new THREE.InstancedMesh(geo, mat, n); im.castShadow = false; im.receiveShadow = true; im.frustumCulled = false;
  const seat = new Float32Array(n * 2), M4 = new THREE.Matrix4(), q = new THREE.Quaternion(), Y = new THREE.Vector3(0, 1, 0), sc = new THREE.Vector3();
  seats.forEach(([x, y, z, ry], i) => {
    const s = .9 + R() * .2; sc.set(s, s * (.92 + R() * .16), s); q.setFromAxisAngle(Y, ry + (R() - .5) * .5);
    M4.compose(new THREE.Vector3(x + (R() - .5) * .12, y, z + (R() - .5) * .12), q, sc); im.setMatrixAt(i, M4);
    im.setColorAt(i, new THREE.Color(o.colors ? o.colors(i, R) : cols[Math.floor(R() * cols.length)]).multiplyScalar(.85 + R() * .25));
    seat[i * 2] = o.order ? o.order(i, R) : R(); seat[i * 2 + 1] = R();
  });
  geo.setAttribute('aSeat', new THREE.InstancedBufferAttribute(seat, 2));
  E.scene.add(im);
  E.updates.push((t, F, tv) => { U.uFill.value = o.fill ? o.fill(t) : 1; U.uStand.value = o.stand ? o.stand(t) : 0; U.uCheer.value = o.cheer ? o.cheer(t) : 0; U.uTime.value = tv; });
  return im;
}

export function mergeGeos(list) {
  const pos = [], nor = [];
  for (const g0 of list) { const g = g0.index ? g0.toNonIndexed() : g0; pos.push(...g.attributes.position.array); nor.push(...g.attributes.normal.array); }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
  return g;
}

// ---------- Roman buildings ----------
const texCache = {};
// plaster facade with small shuttered windows (kind 'insula') or travertine blocks (kind 'stone')
export function romanTex(E, base, kind = 'insula') {
  const key = base + kind; if (texCache[key]) return texCache[key];
  const cv = document.createElement('canvas'); cv.width = 64; cv.height = 64; const x = cv.getContext('2d');
  const c = new THREE.Color(base), hex = k => '#' + c.clone().multiplyScalar(k).getHexString();
  x.fillStyle = hex(1); x.fillRect(0, 0, 64, 64);
  const R = rng(base & 0xffff);
  for (let i = 0; i < 40; i++) { x.fillStyle = hex(.9 + R() * .18); x.fillRect(R() * 64, R() * 64, 3 + R() * 8, 2 + R() * 5); }   // weathered plaster
  if (kind === 'insula') {
    x.fillStyle = hex(.78); x.fillRect(0, 58, 64, 6);
    x.fillStyle = '#2a2420'; x.fillRect(24, 18, 16, 22);
    x.fillStyle = '#6a4a30'; x.fillRect(18, 18, 6, 22); x.fillRect(40, 18, 6, 22);    // shutters
  } else if (kind === 'shop') {
    x.fillStyle = '#231d18'; x.fillRect(6, 8, 52, 56); x.fillStyle = hex(.85); x.fillRect(0, 0, 64, 8);
    x.fillStyle = '#7a5a3a'; x.fillRect(6, 44, 52, 20);                                // wooden counter
  } else if (kind === 'stone') {
    x.strokeStyle = hex(.8); x.lineWidth = 1;
    for (let r = 0; r < 4; r++) { x.beginPath(); x.moveTo(0, r * 16 + .5); x.lineTo(64, r * 16 + .5); x.stroke();
      for (let k = 0; k < 2; k++) { const xx = (k * 32 + (r % 2) * 16) + .5; x.beginPath(); x.moveTo(xx, r * 16); x.lineTo(xx, r * 16 + 16); x.stroke(); } }
  }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return (texCache[key] = t);
}
function boxUV(w, h, d, bay, storey) {
  const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv;
  const rep = [[d / bay, h / storey], [d / bay, h / storey], [1, 1], [1, 1], [w / bay, h / storey], [w / bay, h / storey]];
  for (let f = 0; f < 6; f++) for (let i = 0; i < 4; i++) { const k = f * 4 + i; uv.setXY(k, uv.getX(k) * rep[f][0], uv.getY(k) * rep[f][1]); }
  return g;
}
const ROOF = 0xa5583a;
function roof(E, w, d, h, x, y, z, ry = 0, col = ROOF) {     // pitched tile roof, ridge along local x
  const s = new THREE.Shape(); s.moveTo(-d / 2 - .4, 0); s.lineTo(d / 2 + .4, 0); s.lineTo(0, h); s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: w + .6, bevelEnabled: false }); g.translate(0, 0, -(w + .6) / 2); g.rotateY(Math.PI / 2);
  const m = E.shadowed(new THREE.Mesh(g, E.lam(col))); m.position.set(x, y, z); m.rotation.y = ry; E.scene.add(m); return m;
}
// insula: shops on the ground floor, 2-4 plaster storeys above, tile roof, sometimes a wooden balcony.
// Front faces +x (side 1) or -x (side -1) when along z. Returns the shop front positions (for lamps).
export function insula(E, cx, cz, len, depth, floors, side, color, R) {
  const fr = [], mats = k => { const t = romanTex(E, color, k); const m = E.lam(0xffffff, { map: t }); return m; };
  const shopM = mats('shop'), upM = mats('insula'), topM = E.lam(new THREE.Color(color).multiplyScalar(.8));
  const gf = E.shadowed(new THREE.Mesh(boxUV(depth, 4, len, 4.5, 4), [shopM, shopM, topM, topM, shopM, shopM])); gf.position.set(cx, 2, cz); E.scene.add(gf);
  const h = floors * 3.2, up = E.shadowed(new THREE.Mesh(boxUV(depth, h, len, 4, 3.2), [upM, upM, topM, topM, upM, upM])); up.position.set(cx, 4 + h / 2, cz); E.scene.add(up);
  roof(E, len, depth, 2.2, cx, 4 + h, cz, Math.PI / 2);
  // awning (cloth) over the shops and a brick cornice between shops and flats
  const aw = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(1.8, .06, len - 1), E.lam([0xb5653f, 0xc9a94a, 0x8a5a3a, 0xd8cdb4][Math.floor(R() * 4)])));
  aw.position.set(cx - side * (depth / 2 + .8), 3.7, cz); aw.rotation.z = side * -.18; E.scene.add(aw);
  const co = new THREE.Mesh(new THREE.BoxGeometry(depth + .3, .3, len + .1), E.lam(0x9a5a3e)); co.position.set(cx, 4.1, cz); E.scene.add(co);
  if (R() < .5) { const b = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(1, .15, len * .6), E.lam(0x6a4a30))); b.position.set(cx - side * (depth / 2 + .5), 7.4, cz); E.scene.add(b);
    const rail = new THREE.Mesh(new THREE.BoxGeometry(.06, .8, len * .6), E.lam(0x5a3e28)); rail.position.set(cx - side * (depth / 2 + .95), 7.8, cz); E.scene.add(rail); }
  for (let k = 0; k < Math.floor(len / 4.5); k++) fr.push([cx - side * (depth / 2 + .2), cz - len / 2 + 2.25 + k * 4.5]);
  return fr;
}
// temple: podium, front stairs, columns on all sides (peripteral, low-poly), pediment, cella
export function temple(E, cx, cz, w, d, ry = 0, o = {}) {
  const g = new THREE.Group(); g.position.set(cx, 0, cz); g.rotation.y = ry; E.scene.add(g);
  const stone = E.lam(0xffffff, { map: romanTex(E, o.color ?? 0xd9d2c0, 'stone') }), plain = E.lam(o.color ?? 0xd9d2c0), S = m => E.shadowed(m);
  const ph = 3.2, podium = S(new THREE.Mesh(new THREE.BoxGeometry(w, ph, d), stone)); podium.position.y = ph / 2; g.add(podium);
  for (let k = 0; k < 8; k++) { const st = S(new THREE.Mesh(new THREE.BoxGeometry(w * .6, ph * (k + 1) / 8, .5), plain)); st.position.set(0, ph * (k + 1) / 16, d / 2 + 4 - k * .5); g.add(st); }
  const ch = 12, cr = .55, nx = 6, nz = 10;
  for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) {
    if (i > 0 && i < nx - 1 && j > 0 && j < nz - 1) continue;
    if (j > 1 && (i === 0 || i === nx - 1) && o.prostyle) continue;
    const c = S(new THREE.Mesh(new THREE.CylinderGeometry(cr * .85, cr, ch, 10), plain)); c.position.set(-w / 2 + 1 + i * (w - 2) / (nx - 1), ph + ch / 2, d / 2 - 1 - j * (d - 2) / (nz - 1)); g.add(c);
  }
  const cella = S(new THREE.Mesh(new THREE.BoxGeometry(w - 5, ch, d - 9), stone)); cella.position.set(0, ph + ch / 2, -2.5); g.add(cella);
  const door = new THREE.Mesh(new THREE.PlaneGeometry(3, 6.5), E.lam(0x2a2018)); door.position.set(0, ph + 3.25, -2.5 + (d - 9) / 2 + .02); g.add(door);
  const ent = S(new THREE.Mesh(new THREE.BoxGeometry(w + .4, 1.6, d + .4), plain)); ent.position.y = ph + ch + .8; g.add(ent);
  const s = new THREE.Shape(); s.moveTo(-w / 2 - .2, 0); s.lineTo(w / 2 + .2, 0); s.lineTo(0, 3.6); s.closePath();
  const pg = new THREE.ExtrudeGeometry(s, { depth: d + .4, bevelEnabled: false }); pg.translate(0, 0, -(d + .4) / 2);
  const ped = S(new THREE.Mesh(pg, plain)); ped.position.y = ph + ch + 1.6; g.add(ped);
  const rf = S(new THREE.Mesh(new THREE.BoxGeometry(.3, .3, d + .6), E.lam(ROOF))); rf.position.y = ph + ch + 1.6 + 3.6; g.add(rf);
  return g;
}
// market stall: four posts, a cloth roof, a table with baskets of fruit or amphorae
export function stall(E, x, z, ry, R) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = ry; E.scene.add(g);
  const wood = E.lam(0x6a4a30), S = m => E.shadowed(m);
  for (const [px, pz] of [[-1.2, -.8], [1.2, -.8], [-1.2, .8], [1.2, .8]]) { const p = S(new THREE.Mesh(new THREE.BoxGeometry(.1, 2.4, .1), wood)); p.position.set(px, 1.2, pz); g.add(p); }
  const cl = S(new THREE.Mesh(new THREE.BoxGeometry(2.8, .05, 2), E.lam([0xb5653f, 0xc9a94a, 0xd8cdb4, 0x7a3e5c, 0x4f6a8a][Math.floor(R() * 5)]))); cl.position.y = 2.45; cl.rotation.x = .12; g.add(cl);
  const tb = S(new THREE.Mesh(new THREE.BoxGeometry(2.3, .1, 1.1), wood)); tb.position.y = .9; g.add(tb);
  const fr = [0xc0392b, 0xd99a2b, 0x6b8f3a, 0x7a3e5c, 0xe0c060];
  for (let k = 0; k < 4; k++) {
    const b = S(new THREE.Mesh(new THREE.CylinderGeometry(.22, .17, .2, 8), E.lam(0x8a6a40))); b.position.set(-.8 + k * .53, 1.05, 0); g.add(b);
    const f = new THREE.Mesh(new THREE.SphereGeometry(.2, 7, 4, 0, Math.PI * 2, 0, Math.PI / 2), E.lam(fr[Math.floor(R() * fr.length)])); f.position.set(-.8 + k * .53, 1.15, 0); g.add(f);
  }
  for (let k = 0; k < 3; k++) amphora(E, x + Math.cos(ry) * (-.6 + k * .5) + Math.sin(ry) * 1.1, z - Math.sin(ry) * (-.6 + k * .5) + Math.cos(ry) * 1.1);
  return g;
}
export function amphora(E, x, z, s = 1) {
  const pts = [[0, 0], [.08, .02], [.17, .25], [.2, .5], [.16, .72], [.06, .8], [.05, .95], [0, .97]].map(([a, b]) => new THREE.Vector2(a * s, b * s));
  const m = E.shadowed(new THREE.Mesh(new THREE.LatheGeometry(pts, 7), E.lam(0xb0663f))); m.position.set(x, 0, z); E.scene.add(m); return m;
}
// cone fountain (like the Meta Sudans next to the Colosseum): round basin, drum, tall cone with water sheen
export function coneFountain(E, x, z, h = 17) {
  const g = new THREE.Group(); g.position.set(x, 0, z); E.scene.add(g);
  const st = E.lam(0xffffff, { map: romanTex(E, 0xcfc6b2, 'stone') }), S = m => E.shadowed(m);
  const basin = S(new THREE.Mesh(new THREE.CylinderGeometry(8, 8.3, 1, 24), E.lam(0xcfc6b2))); basin.position.y = .5; g.add(basin);
  const water = new THREE.Mesh(new THREE.CircleGeometry(7.6, 24), E.lam(0x4f7f88)); water.rotation.x = -Math.PI / 2; water.position.y = .95; g.add(water);
  const drum = S(new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.8, h * .45, 14), st)); drum.position.y = h * .225; g.add(drum);
  const cone = S(new THREE.Mesh(new THREE.ConeGeometry(2.4, h * .55, 14), st)); cone.position.y = h * .45 + h * .275; g.add(cone);
  return g;
}
