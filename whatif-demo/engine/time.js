// TIME (baksteen Tijd): days go by at any speed. Day/night (sun moves, stars, lamps), clouds, seasons
// (leaf colours, bare trees, snow), rain, and – as a function of the years – nature taking over
// (grass through the asphalt, ivy up the walls, young trees) and decay (dust, rust, broken windows).
// Works with any place and any force: main.js calls applyTime when the scenario has TL.time.
//   TL.time = {
//     days: [[t, d], ...]      video time -> days since the start (monotone; .5 = 12 hours, 365 = 1 year)
//     hour: 14, doy: 130       clock and day of the year (0 = 1 Jan) at d = 0; lat: 52 (sun height)
//     rain: [[a, b], ...]      video times with rain (darker sky, streaks, wet ground)
//     snow: true               snow cover in winter (Dec-Feb)
//     clouds: .5               cloud cover 0..1 (moves with the days)
//     area: { x: [a, b], z: [a, b] }   where young trees and grass tufts grow (default E.wildArea of the place)
//     trees: 36, tufts: 900, avoid: [[x, z, r], ...] no trees there (camera spots, a road you keep open)
//     grow: { grass: [.15, 18], ivy: [1, 22], trees: [1.5, 25], dust: [.02, 2], rust: [1, 15], windows: [2, 25] }   years from..to
//   }
// E.timeAt(t) -> { days, hour, years, season (0..1 from 1 Jan), day (0..1 daylight), rate (days per video s) }
import * as THREE from 'three';
import { monotone, smooth, clamp, lerp, rng, hash } from './util.js';
import { roundTree, coneTree } from './props.js';

const C = h => new THREE.Color(h);
const GROW = { grass: [.15, 18], ivy: [1, 22], trees: [1.5, 25], dust: [.02, 2], rust: [1, 15], windows: [2, 25] };
// leaves through the year (deciduous): bare in winter, light green in spring, dark in summer, orange in autumn
const LEAF = [[0, 0x6e6252], [.22, 0x6e6252], [.3, 0x8aa653], [.42, 0x5f7a40], [.68, 0x56703f], [.76, 0xb8822f], [.84, 0x9a5a2a], [.9, 0x6e6252], [1, 0x6e6252]];
const leafAt = s => { let i = 0; while (i < LEAF.length - 2 && s > LEAF[i + 1][0]) i++; const [a, ca] = LEAF[i], [b, cb] = LEAF[i + 1];
  return C(ca).lerp(C(cb), smooth(a, b, s)); };

export function applyTime(E, TL, F, P) {
  const T = TL.time, G = { ...GROW, ...(T.grow || {}) }, STOP = TL.beats.stop;
  const days = monotone(T.days || [[0, 0]]), d = t => days(Math.min(t, STOP));
  const yr = t => d(t) / 365, g = (k, t) => smooth(G[k][0], G[k][1], yr(t));
  const lat = (T.lat ?? 52) * Math.PI / 180;
  const rate = t => (d(t + .25) - d(t - .25)) / .5;
  const rainAt = t => (T.rain || []).reduce((m, [a, b]) => Math.max(m, smooth(a, a + 1.5, t) * (1 - smooth(b - 1.5, b, t))), 0);
  function sunDir(t) {        // hour angle + declination -> direction to the sun (x east, y up, z south = +z)
    const dd = d(t), hour = ((T.hour ?? 12) + dd * 24) % 24, doy = ((T.doy ?? 172) + dd) % 365;
    const dec = 23.44 * Math.PI / 180 * Math.sin(2 * Math.PI * (doy - 80) / 365), H = (hour - 12) / 24 * 2 * Math.PI;
    const el = Math.asin(Math.sin(lat) * Math.sin(dec) + Math.cos(lat) * Math.cos(dec) * Math.cos(H));
    const az = Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(lat) - Math.tan(dec) * Math.cos(lat));   // 0 = south, + = west
    return { hour, doy, el, v: new THREE.Vector3(-Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el)) };
  }
  const daylight = el => smooth(-.08, .22, Math.sin(el));
  E.timeAt = t => { const s = sunDir(t), r = rate(t), k = smooth(1.2, 5, r);
    return { days: d(t), hour: s.hour, years: yr(t), season: s.doy / 365, rate: r, day: lerp(daylight(s.el), .8, k) }; };

  // ---------- light: day and night, seasons, rain ----------
  const base = E.sunOffset ? E.sunOffset.clone() : new THREE.Vector3(-90, 110, 120), R0 = base.length();
  E.sunOffset = base.clone();
  const noonDir = base.clone().normalize();
  const prevLook = F.look;
  F.look = (t, L) => {
    prevLook?.(t, L);
    const s = sunDir(t), r = rate(t), fast = smooth(1.2, 5, r);           // fast time-lapse: no strobing, an even "average day"
    const k = lerp(daylight(s.el), .8, fast), low = (1 - smooth(.05, .35, Math.sin(s.el))) * smooth(-.1, .05, Math.sin(s.el)) * (1 - fast);
    const dir = s.v.clone().lerp(noonDir, fast); if (dir.y < .12) dir.y = .12; dir.normalize();
    E.sunOffset.copy(dir).multiplyScalar(R0);
    const rain = rainAt(t), N = C;
    L.top.lerp(N(0x05080f), 1 - k); L.hor.lerp(N(0x121826), (1 - k) * .95);
    L.hor.lerp(N(0xd88a52), low * .55); L.top.lerp(N(0x55607a), low * .3);
    L.top.lerp(N(0x6c737b), rain * .8 * k); L.hor.lerp(N(0x9aa0a5), rain * .7 * k);
    L.sun *= k * (1 - rain * .85); L.sunColor = (L.sunColor || N(0xffeedd)).clone().lerp(N(0xff9a55), low * .8);
    L.sunDisc = (L.sunDisc || N(0)).clone().multiplyScalar(k * (1 - rain));
    L.hemi = lerp(.3, L.hemi, k) * (1 - rain * .25); L.hemiColor.lerp(N(0x7d8fb3), 1 - k);
    L.fogColor = L.hor.clone(); L.fogFar = lerp(L.fogFar, Math.min(L.fogFar, 380), Math.max(1 - k, rain * .8));
    L.stars = Math.max(L.stars || 0, smooth(.35, .05, k) * (1 - rain));
    L.dark = Math.max(L.dark || 0, 1 - k); L.dustLight = Math.min(L.dustLight ?? 1, .4 + .6 * k);
  };

  // ---------- materials: grass, ivy, dust, rust, snow, wet (one shader patch on every lit material) ----------
  const U = { uGrass: { value: 0 }, uIvy: { value: 0 }, uDust: { value: 0 }, uRust: { value: 0 }, uSnow: { value: 0 }, uWet: { value: 0 } };
  const skip = new Set(), metal = new Set();
  const mark = (o, set) => o?.traverse?.(m => m.material && [].concat(m.material).forEach(x => set.add(x)));
  for (const p of E.people) mark(p.g, skip);
  for (const a of E.animals || []) mark(a.g, skip);
  for (const w of E.floods) mark(w.mesh, skip);
  for (const b of E.bodies) if (b.kind === 'car' || b.kind === 'bike') mark(b.obj, metal);
  for (const m of [...(T.metal || [])]) metal.add(m);
  const patch = m => {
    if (m.userData.aged || skip.has(m) || !(m.isMeshLambertMaterial || m.isMeshStandardMaterial)) return;
    m.userData.aged = true; const uMetal = { value: metal.has(m) ? 1 : 0 }, uWall = { value: m.userData.facade || m.userData.wall ? 1 : .15 };
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U, { uMetal, uWall });
      sh.vertexShader = 'varying vec3 vAgeW; varying vec3 vAgeN;\n' + sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
        vec4 aw = vec4(transformed, 1.);
        #ifdef USE_INSTANCING
          aw = instanceMatrix * aw;
        #endif
        vAgeW = (modelMatrix * aw).xyz; vAgeN = normalize(mat3(modelMatrix) * objectNormal);`);
      sh.fragmentShader = `varying vec3 vAgeW; varying vec3 vAgeN; uniform float uGrass, uIvy, uDust, uRust, uSnow, uWet, uMetal, uWall;
        float aH(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
        float aN(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f);
          return mix(mix(aH(i), aH(i + vec2(1, 0)), f.x), mix(aH(i + vec2(0, 1)), aH(i + vec2(1, 1)), f.x), f.y); }
        float aF(vec2 p){ return aN(p) * .55 + aN(p * 2.3 + 7.) * .3 + aN(p * 5.1 + 3.) * .15; }
        ` + sh.fragmentShader.replace('#include <color_fragment>', `#include <color_fragment>
        { vec3 w = vAgeW; float up = vAgeN.y, n = aF(w.xz * .35), n2 = aF(vec2((w.x + w.z) * .9, w.y * .22)) * .8 + aN(vec2(w.x + w.z, w.y) * 2.5) * .2;
          vec3 c = diffuseColor.rgb;
          float l = dot(c, vec3(.3, .59, .11));
          c = mix(c, mix(vec3(l), c, .65) * .86 + vec3(.035, .03, .02), uDust);                              // dust, faded paint
          if (uMetal > .5) c = mix(c, mix(vec3(.42, .22, .12), vec3(.3, .17, .1), aN(w.xz * 3.)), smoothstep(1. - uRust * 1.1, 1.05 - uRust * 1.1, aF(w.xy * 1.7 + w.zz)));
          float crack = 1. - smoothstep(.0, .05 + .05 * uGrass, abs(fract(w.x * .19 + w.z * .07 + n * 1.6) - .5) * abs(fract(w.z * .13 - w.x * .05 + n) - .5) * 4.);   // cracks first, then patches
          float grass = up > .55 && w.y > -.3 && w.y < .6 ? max(crack * smoothstep(0., .25, uGrass), smoothstep(1. - uGrass * .62, 1.06 - uGrass * .62, n + .12 * aN(w.xz * 3.1))) : 0.;
          c = mix(c, mix(vec3(.30, .42, .17), vec3(.40, .48, .2), aN(w.xz * 1.7)), grass);
          float ivy = abs(up) < .45 && w.y < 40. ? smoothstep(0., .06, uIvy * uWall * (1. - w.y / (2. + uIvy * 11.)) * .95 - n2 + .12) : 0.;
          c = mix(c, mix(vec3(.18, .30, .13), vec3(.26, .38, .16), aN(w.xy * 2.3 + w.zy)), ivy);
          c *= 1. - uWet * .32 * smoothstep(.3, .8, up);
          c = mix(c, vec3(.93, .95, .97), uSnow * smoothstep(.35, .75, up) * smoothstep(.25, .5, n + .3));
          diffuseColor.rgb = c; }`);
    };
    m.needsUpdate = true;
  };
  let patched = false;
  const patchAll = () => { E.scene.traverse(o => o.isMesh && [].concat(o.material).forEach(patch)); patched = true; };

  // broken windows: facades swap to the 'broken' texture one by one over the years
  const facades = [];
  E.scene.traverse(o => o.isMesh && [].concat(o.material).forEach(m => { const f = m.userData.facade; if (f && (f.kind === 'win' || f.kind === 'tower') && !facades.includes(m)) facades.push(m); }));
  const brokenTex = {};

  // ---------- young trees and grass tufts ----------
  const A = T.area || E.wildArea || { x: [-20, 20], z: [-60, 20] }, avoid = T.avoid || [];
  const ok = (x, z) => avoid.every(([ax, az, r]) => Math.hypot(x - ax, z - az) > r);
  const R = rng(4242), trees = [];
  for (let i = 0, tries = 0; i < (T.trees ?? 36) && tries < 2000; tries++) {
    const x = lerp(A.x[0], A.x[1], R()), z = lerp(A.z[0], A.z[1], R());
    if (!ok(x, z)) continue;
    const s = .55 + R() * .5, g0 = R() < .75 ? roundTree(E, x, z, s, 7000 + i) : coneTree(E, x, z, s * .9, 7000 + i);
    trees.push({ g: g0, s, a: R() * .55 }); g0.scale.setScalar(.001); i++;
  }
  const tuftGeo = new THREE.IcosahedronGeometry(.32, 0); tuftGeo.scale(1, .7, 1); tuftGeo.translate(0, .12, 0);
  const tufts = new THREE.InstancedMesh(tuftGeo, E.lam(0xffffff), T.tufts ?? 900); tufts.receiveShadow = true; E.scene.add(tufts);
  skip.add(tufts.material);
  const TU = [];
  for (let i = 0; i < tufts.count; i++) {      // along kerbs and wall bases first (cracks), then anywhere
    let x = lerp(A.x[0], A.x[1], R()), z = lerp(A.z[0], A.z[1], R());
    if (E.wildEdges?.length && R() < .65) { const ex = E.wildEdges[Math.floor(R() * E.wildEdges.length)]; x = ex + (R() - .5) * .8; }
    TU.push({ x, z, y: (E.groundAt?.(x, z) ?? 0) + (Math.abs(x) > (E.kerbX ?? 1e9) ? .2 : 0), s: .6 + R() * 1.1, a: R(), r: R() * 6 });
    tufts.setColorAt(i, C([0x5d7a3a, 0x6c8743, 0x4f6b33, 0x7a8a48][i % 4]));
  }
  const DM = new THREE.Object3D();

  // ---------- clouds: one big layer that drifts with the days ----------
  let clouds = null;
  if (T.clouds !== false) {
    const cv = document.createElement('canvas'); cv.width = cv.height = 256; const x = cv.getContext('2d'), Rc = rng(77);
    for (let i = 0; i < 70; i++) { const px = Rc() * 256, py = Rc() * 256, r = 14 + Rc() * 34;
      for (const [ox, oy] of [[0, 0], [256, 0], [-256, 0], [0, 256], [0, -256]]) { const gr = x.createRadialGradient(px + ox, py + oy, 0, px + ox, py + oy, r);
        gr.addColorStop(0, 'rgba(255,255,255,.5)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.beginPath(); x.arc(px + ox, py + oy, r, 0, 7); x.fill(); } }
    const tex = new THREE.CanvasTexture(cv); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.repeat.set(5, 5);
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, fog: false, opacity: 0 });
    clouds = new THREE.Mesh(new THREE.PlaneGeometry(7000, 7000), mat); clouds.rotation.x = Math.PI / 2; clouds.position.y = 650; clouds.renderOrder = -1; E.scene.add(clouds);
    skip.add(mat);
  }

  // ---------- rain: streaks around the camera ----------
  const NR = 2400, rainGeo = new THREE.BufferGeometry(), rp = new Float32Array(NR * 6);
  rainGeo.setAttribute('position', new THREE.BufferAttribute(rp, 3));
  const rainMat = new THREE.LineBasicMaterial({ color: 0xbfc8d0, transparent: true, opacity: 0, fog: false, depthWrite: false });
  const rainL = new THREE.LineSegments(rainGeo, rainMat); rainL.frustumCulled = false; E.scene.add(rainL);

  E.updates.push((t, F2, tv) => {
    if (!patched) patchAll();
    const s = sunDir(t), season = s.doy / 365, fast = smooth(30, 150, rate(t)), rain = rainAt(tv ?? t);
    U.uGrass.value = g('grass', t); U.uIvy.value = g('ivy', t); U.uDust.value = g('dust', t) * .8; U.uRust.value = g('rust', t);
    U.uWet.value = rain; U.uSnow.value = T.snow ? (1 - fast) * smooth(.9, .97, season < .5 ? season + 1 : season) * (1 - smooth(.08, .16, season < .5 ? season : 0)) : 0;
    // leaves follow the season (in a very fast time-lapse: an average late-summer green, no flicker)
    for (const m of E.leaves || []) { m.userData.base ??= m.color.clone(); m.color.copy(m.userData.base).lerp(leafAt(season), .85 * (1 - fast)).lerp(C(0x5f7340), fast * .5); }
    // windows break one facade at a time
    const wb = g('windows', t);
    facades.forEach((m, i) => { const br = hash(i, 31) < wb * .85; if (br === !!m.userData.isBroken) return;
      const f = m.userData.facade; m.userData.origMap ??= m.map;
      m.map = br ? (brokenTex[f.color] ??= E.facadeTex(f.color, 'broken')) : m.userData.origMap; if (m.map !== m.userData.origMap) { m.map.repeat.copy(m.userData.origMap.repeat); }
      m.userData.isBroken = br; m.needsUpdate = true; });
    // young trees and tufts grow
    const yt = g('trees', t);
    for (const tr of trees) tr.g.scale.setScalar(Math.max(.001, tr.s * smooth(tr.a, 1, yt) * (.25 + .75 * yt)));
    const gs = g('grass', t);
    TU.forEach((u, i) => { const k = smooth(u.a * .7, u.a * .7 + .3, gs); DM.position.set(u.x, u.y, u.z); DM.rotation.set(0, u.r, 0); DM.scale.setScalar(Math.max(.001, k * u.s)); DM.updateMatrix(); tufts.setMatrixAt(i, DM.matrix); });
    tufts.instanceMatrix.needsUpdate = true;
    if (clouds) {
      const dd = d(t), k = E.timeAt(t).day, cov = clamp((T.clouds ?? .5) + rain * .6);
      clouds.material.map.offset.set(dd * .35 + (tv ?? t) * .004, dd * .12);
      clouds.material.opacity = cov * (1 - smooth(4, 40, rate(t)) * .6);
      clouds.material.color.copy(C(0x1a1f2a).lerp(C(rain > .3 ? 0x9aa0a6 : 0xf4f1ea), k));
      clouds.position.x = E.camera.position.x; clouds.position.z = E.camera.position.z;
    }
    rainMat.opacity = rain * .45;
    if (rain > .01) {
      const c = E.camera.position, tt = tv ?? t;
      for (let i = 0; i < NR; i++) { const h = 24, sp = 22 + hash(i, 1) * 6, y = h - ((tt * sp + hash(i, 2) * h) % h);
        const x = c.x + (hash(i, 3) - .5) * 50, z = c.z + (hash(i, 4) - .5) * 50, j = i * 6;
        rp[j] = x; rp[j + 1] = c.y - 6 + y; rp[j + 2] = z; rp[j + 3] = x + .05; rp[j + 4] = c.y - 6 + y - .7; rp[j + 5] = z; }
      rainGeo.attributes.position.needsUpdate = true;
    }
  });
}
