// ERUPTION (baksteen Aarde beweegt): everything a big volcano does, each part switched on by TL.forceParams.
// Works in any place; places may give E.vent [x, y, z] (where it erupts), E.laharPath [[x, z], ...] (a valley/creek),
// E.ashGround / E.ashRoofs (materials that turn ash-grey; E.frost materials follow at half strength).
//   loud:     [[t, 0..1], ...]   overall intensity (sound, camera shake, tree sway); default from the parts below
//   vent:     [x, y, z]          override E.vent; null = no column in view (ash city, far away)
//   column:   [t0, t1]           the column shoots up (to height H, default 2400) and grows an umbrella cloud
//   lightning:[t0, t1]           bolts inside the cloud (thunder events), denser in the middle
//   glow:     [t0, t1]           red/orange glow at the base of the column and in the lower sky
//   collapse: t                  the column collapses: glowing ash clouds race outwards (flowSpeed, flowReach)
//   fires:    true               forest fires where the glowing clouds stop (or E.fireSpots, lit at fireAt)
//   dark:     [[t, 0..1], ...]   sky goes from day to black (1 = black at noon)
//   ash:      [[t, 0..1], ...]   ash falling around the camera (grey flakes)
//   cover:    [[t, 0..1], ...]   ash lying on ground, roofs, cars, trees
//   rain:     [a, b]             rain (mixes with the ash: lahars)
//   lahar:    [t0, speed]        a mud flow runs down E.laharPath, carrying logs
//   haze:     [[t, 0..1], ...]   yellow-grey sky far from the volcano (ash high up)
//   sunset:   [[t, 0..1], ...]   blood-red sky and sun (sulphur veil, months later)
//   winter:   [[t, 0..1], ...]   cold grey summer: pale sun, grey-blue light, sleet
//   alarm:    { siren: [x, z, on], block: [x, z, on, ry] }   sirens and a roadblock (props-alarm.js)
import { baseForce } from './base.js';
import { smooth, hash, noise, clamp, monotone, lerp } from '../util.js';
import { sirenPole, roadblock } from '../props-alarm.js';

export function create(E, TL) {
  const P = TL.forceParams || {}, THREE = E.THREE, C = h => new THREE.Color(h);
  const curve = (k, d = 0) => P[k] ? monotone(P[k]) : () => d;
  const dark = curve('dark'), ash = curve('ash'), cover = curve('cover'), haze = curve('haze'), sunset = curve('sunset'), winter = curve('winter');
  const H = P.H ?? 2400, col = P.column, glowP = P.glow, lit = P.lightning && [P.lightning[0], Math.min(P.lightning[1], TL.T_END ?? 600)];   // never past the end (1e9 would hang)
  const colK = t => col ? smooth(col[0], col[1], t) : 0;
  const glowK = t => glowP ? smooth(glowP[0], glowP[0] + 3, t) * (glowP[1] != null ? 1 - smooth(glowP[1], glowP[1] + 3, t) * .5 : 1) : 0;
  const rainK = t => P.rain ? smooth(P.rain[0], P.rain[0] + 2, t) * (1 - smooth(P.rain[1] - 2, P.rain[1], t)) : 0;
  const loudDef = t => Math.max(colK(t) * (1 - smooth(col ? col[1] + 4 : 0, col ? col[1] + 14 : 1, t) * .5), ash(t) * .45, dark(t) * .4,
    P.collapse != null ? smooth(P.collapse, P.collapse + 2, t) * .9 : 0);
  const loud = P.loud ? monotone(P.loud) : loudDef;
  const F = baseForce(E, TL, 'eruption', () => t => loud(Math.min(t, TL.beats.stop)));
  F.level = F.phys;
  const ventAt = () => P.vent === null ? null : (P.vent || E.vent || [0, 60, -2400]);

  // lightning: a fixed list of bolts (time, place in the cloud)
  const bolts = [];
  if (lit) for (let t = lit[0], i = 0; t < lit[1]; i++) { bolts.push({ t, i, dur: .16 + hash(i, 3) * .12 }); t += .25 + hash(i, 1) * 1.3 * (1 - .6 * Math.sin(Math.PI * (t - lit[0]) / (lit[1] - lit[0]))); }
  const flash = t => { let m = 0; for (const b of bolts) { const a = t - b.t; if (a > 0 && a < b.dur) m = Math.max(m, (1 - a / b.dur) * (.6 + hash(b.i, 9) * .4)); } return m; };

  Object.assign(F, {
    dark, ash, cover, flash,
    shake: t => (col ? smooth(col[0], col[0] + .3, t) * (1 - smooth(col[0] + 3, col[0] + 8, t)) * .5 : 0) + loud(t) * .06,
    lateral: t => { const a = loud(t) * .18 + rainK(t) * .1; return { a, dx: .7 + .3 * Math.sin(t * .7), dz: .3 }; },
    fallMode: 'topple',
    look(t, L) {
      const dk = dark(t), hz = haze(t), ss = sunset(t), wn = winter(t), fl = flash(t), gl = glowK(t);
      // far away: yellow-grey haze of high ash
      L.top.lerp(C(0x9a9784), hz * .75); L.hor.lerp(C(0xc9b88e), hz * .8); L.sun *= 1 - hz * .65; L.hemi *= 1 - hz * .15; L.sunColor.lerp(C(0xffd9a0), hz);
      // months later: blood-red sunsets (sulphur veil), then a cold grey summer
      L.top.lerp(C(0x5b3a4a), ss * .8); L.hor.lerp(C(0xe0562a), ss * .9); L.sunColor.lerp(C(0xff7a3a), ss); L.sunDisc = (L.sunDisc || C(0x998877)).clone().lerp(C(0xff5a2a), ss).multiplyScalar(1 + ss);
      L.hemi *= 1 - ss * .3; L.hemiColor = L.hemiColor.clone().lerp(C(0xf0a080), ss * .6);
      L.sunDisc = L.sunDisc.clone().multiplyScalar(1 - wn * .75); L.hemi *= 1 - wn * .2; L.top.lerp(C(0x7c858c), wn * .85); L.hor.lerp(C(0xa9b0b4), wn * .85); L.sun *= 1 - wn * .6; L.sunColor.lerp(C(0xdfe6ee), wn); L.hemiColor = L.hemiColor.clone().lerp(C(0xc4ccd4), wn);
      if (wn > .01) { L.fogNear = lerp(L.fogNear, 60, wn * .7); L.fogFar = lerp(L.fogFar, 900, wn * .7); }
      // the column: open the far fog so the cloud can be seen, then the ash takes the light away
      if (col) { L.fogFar = Math.max(L.fogFar, lerp(L.fogFar, 7000, colK(t) * (1 - dk))); }
      L.top.lerp(C(0x1e1c1b), dk); L.hor.lerp(C(0x3a3430), dk * .95);
      L.hor.lerp(C(0x6a2a14), gl * dk * .35);                       // red glow low in the dark sky
      L.sun *= 1 - dk * .97; L.hemi *= 1 - dk * .78; L.hemiColor = L.hemiColor.clone().lerp(C(0x8a5a40), dk * .6);
      L.sunDisc = (L.sunDisc || C(0x998877)).clone().multiplyScalar(1 - dk);
      if (dk > .01) { L.fogNear = lerp(L.fogNear, 40, dk * .8); L.fogFar = lerp(L.fogFar, 1600, dk * .7); L.fogColor = L.hor.clone(); }
      L.dark = Math.max(L.dark || 0, dk * .9);
      L.dustLight = 1 - dk * .55;
      if (fl > 0) { L.hemi += fl * 1.6; L.hemiColor = L.hemiColor.clone().lerp(C(0xdfe4ff), fl * .7); L.top.lerp(C(0x8890b0), fl * .4); L.hor.lerp(C(0xa8b0d0), fl * .3); }
      const a = ash(t); L.haze = Math.max(L.haze || 0, a * .1 + dk * .05); L.hazeColor = '#6e665c';
      if (rainK(t) > 0) { L.fogNear = lerp(L.fogNear, 30, rainK(t) * .4); L.fogFar = lerp(L.fogFar, L.fogFar * .6, rainK(t)); }
    },
  });

  // ---------- ash cover on everything ----------
  const ASH = C(0x8d877e);
  E.updates.push(t => {
    const k = cover(t); if (k <= 0 && !E._ashOn) return; E._ashOn = true;
    const tint = (m, f) => { m.userData.ash0 ??= m.color.clone(); m.color.copy(m.userData.ash0).lerp(ASH, f); };
    for (const m of E.ashGround || []) tint(m, k * .95);
    for (const m of E.ashRoofs || []) tint(m, k * .85);
    for (const m of E.frost || []) if (!(E.ashGround || []).includes(m)) tint(m, k * .7);
    if (E.forestMat) tint(E.forestMat, k * .55);
  });

  // ---------- lightning bolts: jagged lines inside the cloud ----------
  const boltMat = new THREE.LineBasicMaterial({ color: 0xe8ecff, transparent: true, fog: false });
  const boltObjs = bolts.slice(0, 60).map(b => { const pts = []; let x = 0, y = 0;
    for (let k = 0; k < 9; k++) { pts.push(new THREE.Vector3(x, y, 0)); x += (hash(b.i, k) - .5) * 160; y -= 90 + hash(b.i, k + 20) * 80; }
    const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), boltMat.clone()); l.visible = false; E.scene.add(l); return { b, l }; });

  F.attach = () => {
    const V = ventAt();
    if (P.cover && !E.ashGround) {          // places without a list: every flat ground plane (not water) gets ash
      const water = new Set(E.floods.map(f => f.mesh.material)), list = new Set();
      E.scene.traverse(o => { if (o.isMesh && o.geometry?.type === 'PlaneGeometry' && Math.abs(o.rotation.x + Math.PI / 2) < .01 && !water.has(o.material) && o.material.color) list.add(o.material); });
      E.ashGround = [...list];
    }
    if (P.alarm?.siren) sirenPole(E, TL, P.alarm.siren[0], P.alarm.siren[1], { on: P.alarm.siren[2] });
    if (P.alarm?.block) roadblock(E, TL, P.alarm.block[0], P.alarm.block[1], { on: P.alarm.block[2], ry: P.alarm.block[3] ?? 0 });
    if (V) {
      for (const { b, l } of boltObjs) {
        const u = hash(b.i, 5), h = H * (.35 + u * .55) * Math.max(.3, colK(b.t)), r = (hash(b.i, 6) - .5) * (200 + h * .35);
        l.position.set(V[0] + r, V[1] + h, V[2] + (hash(b.i, 7) - .5) * 200); l.rotation.y = hash(b.i, 8) * 6;
      }
      E.updates.push((t, _F, tv) => { for (const { b, l } of boltObjs) { const a = tv - b.t; l.visible = a > 0 && a < b.dur; l.material.opacity = 1 - a / b.dur; } });
      for (const b of bolts) if (b.t < TL.beats.stop) E.EVENTS.push({ t: b.t, kind: 'thunder', e: .5 + hash(b.i, 9) * .5, delay: 2 + hash(b.i, 4) * 3 });
      if (col) E.EVENTS.push({ t: col[0], kind: 'blast', e: 1 });
    }
    if (P.collapse != null && V) E.EVENTS.push({ t: P.collapse, kind: 'flow', e: 1 });
    // fires: where the glowing clouds stop (or the place's fire spots)
    if (P.fires && V) {
      const spots = []; const reach = P.flowReach ?? 1500, vs = P.flowSpeed ?? 90;
      for (let i = 0; i < 9; i++) { const a = Math.PI + (i / 8 - .5) * 1.6, d = reach * (.6 + hash(i, 2) * .4);
        const x = V[0] + Math.sin(a) * d * 1.4, z = V[2] - Math.cos(a) * d; spots.push({ p: [x, E.groundAt(x, z) + 4, z], t0: P.collapse + d / vs, s: 30 + hash(i, 4) * 30 }); }
      F.fires = spots;
      for (const s of spots) if (s.t0 < TL.beats.stop) E.EVENTS.push({ t: s.t0, kind: 'fire', e: .5, x: s.p[0], y: s.p[1], z: s.p[2] });
    }
    // lahar: a mud ribbon that runs down the path, with logs riding the front
    if (P.lahar && E.laharPath) buildLahar();
  };

  function buildLahar() {
    const [t0, v] = P.lahar, path = E.laharPath, segs = [], W = P.laharWidth ?? 14;
    let L = 0; const cum = [0]; for (let i = 1; i < path.length; i++) { L += Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]); cum.push(L); }
    const at = s => { let i = 1; while (i < path.length - 1 && cum[i] < s) i++; const k = clamp((s - cum[i - 1]) / (cum[i] - cum[i - 1]));
      const x = lerp(path[i - 1][0], path[i][0], k), z = lerp(path[i - 1][1], path[i][1], k); return [x, z, Math.atan2(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1])]; };
    const mud = E.lam(0x6a5a48), N = Math.ceil(L / 4);
    for (let i = 0; i < N; i++) { const [x, z, a] = at(i * 4 + 2), m = new THREE.Mesh(new THREE.BoxGeometry(W * (.9 + hash(i, 1) * .2), .9, 7), mud);
      m.position.set(x, E.groundAt(x, z) + (E.laharLift ?? 0) + .1, z); m.rotation.y = a; m.visible = false; E.scene.add(m); segs.push({ m, s: i * 4, y: m.position.y }); }
    const logs = Array.from({ length: 7 }, (_, k) => { const g = new THREE.Mesh(new THREE.CylinderGeometry(.35, .4, 9, 6), E.lam(0x5b4a3a)); g.rotation.z = Math.PI / 2; E.scene.add(g); g.visible = false;
      const tree = new THREE.Mesh(new THREE.ConeGeometry(2, 5, 6), E.lam(0x3a4a32)); tree.position.y = 5; tree.rotation.z = -Math.PI / 2; g.add(tree); return { g, off: 6 + k * 9, ph: hash(k, 3) * 6 }; });
    E.updates.push((t, _F, tv) => {
      const front = Math.max(0, (Math.min(tv, TL.beats.stop + 20) - t0) * v);
      for (const s of segs) { const a = front - s.s; s.m.visible = a > 0; if (a > 0) { s.m.scale.y = smooth(0, 12, a) * 1.6 + .2; s.m.position.y = s.y + s.m.scale.y * .3 + Math.sin(tv * 3 + s.s) * .05; } }
      for (const lg of logs) { const s = front - lg.off; lg.g.visible = s > 0 && s < L; if (s > 0 && s < L) { const [x, z, a] = at(s); lg.g.position.set(x, E.groundAt(x, z) + (E.laharLift ?? 0) + 1.4, z); lg.g.rotation.set(Math.sin(tv + lg.ph) * .2, a + lg.ph, Math.PI / 2); } }
    });
    E.laharFront = tv => Math.max(0, (tv - t0) * v);
    if (t0 < TL.beats.stop) E.EVENTS.push({ t: t0, kind: 'lahar', e: 1 });
  }

  // ---------- particles: the column, the umbrella, glowing flows, fires, ash fall, rain ----------
  E.emitters.push((tv, add, cam) => {
    const t = tv, V = ventAt();
    if (V && col && t > col[0]) {
      const k = colK(t), h = H * k, top = Math.max(0, t - col[1]), dk = dark(t);
      const shade = (u, gl) => { const b = .1 + u * .1 - dk * .05, g2 = gl * Math.max(0, 1 - u * 3); return [b + g2 * .5, b * .95 + g2 * .14, b * .9]; };
      const gl = glowK(t);
      for (let i = 0; i < 260; i++) {           // the column: puffs that rise and spread
        const u = (t * .05 + hash(i, 1)) % 1; if (u * H > h + 50) continue;
        const y = V[1] + u * h, rad = 180 + u * 420 + u * u * 500 + (hash(i, 2) - .5) * 160, ang = hash(i, 3) * 6.28 + t * .05;
        const [r, g, b] = shade(u, gl), fl = flash(t) * (hash(i, 9) < .3 ? 1 : 0);
        add(V[0] + Math.cos(ang) * rad * .55, y, V[2] + Math.sin(ang) * rad * .35, 380 + u * 600, .58 * smooth(0, .05, u), r + fl * .5, g + fl * .5, b + fl * .6, hash(i, 4) * 6);
      }
      for (let i = 0; i < 160; i++) {           // the umbrella: spreads out at the top, wider every second
        if (k < .8) break;
        const R = 300 + top * 160 + smooth(col[1] - 2, col[1] + 2, t) * 400, a = hash(i, 11) * 6.28, d = Math.sqrt(hash(i, 12)) * R;
        add(V[0] + Math.cos(a) * d * 1.3, V[1] + h - 120 + (hash(i, 13) - .5) * 240 - d * .08, V[2] + Math.sin(a) * d * .7 + d * .25, 480 + hash(i, 14) * 420, .55, .14 - dk * .05, .13 - dk * .05, .12 - dk * .05, hash(i, 15) * 6);
      }
      if (gl > 0) for (let i = 0; i < 26; i++) {   // red glow at the base
        const a = hash(i, 21) * 6.28, d = hash(i, 22) * 140;
        add(V[0] + Math.cos(a) * d, V[1] + hash(i, 23) * 160, V[2] + Math.sin(a) * d * .5, 160 + hash(i, 24) * 160, gl * (.35 + .25 * Math.sin(t * 6 + i)), 1, .38, .1, 0);
      }
    }
    if (V && P.collapse != null && t > P.collapse) {   // glowing ash clouds racing outwards along the ground
      const a = t - P.collapse, vs = P.flowSpeed ?? 90, reach = P.flowReach ?? 1500, R = Math.min(reach, a * vs);
      for (let i = 0; i < 220; i++) {
        const ang = Math.PI + (hash(i, 31) - .5) * 2.2, d = R * (.4 + .6 * Math.sqrt(hash(i, 32))), x = V[0] + Math.sin(ang) * d * 1.4, z = V[2] - Math.cos(ang) * d;
        const front = d / Math.max(1, R), hot = smooth(.6, 1, front) * (1 - smooth(reach * .9, reach, R) * .6);
        add(x, E.groundAt(x, z) + 30 + hash(i, 33) * 90 * (1 - front * .5), z, 140 + hash(i, 34) * 120, .45, .38 + hot * .5, .3 + hot * .14, .26, hash(i, 35) * 6);
      }
    }
    for (const s of F.fires || []) {                // forest fires: flames and a column of smoke
      const a = t - s.t0; if (a < 0) continue;
      for (let k = 0; k < 10; k++) { const u = (tv * 1.3 + hash(k, s.s)) % 1;
        add(s.p[0] + (hash(k, 2) - .5) * s.s, s.p[1] + u * s.s * .8, s.p[2] + (hash(k, 3) - .5) * s.s * .5, s.s * (1.4 - u), (1 - u) * .7 * smooth(0, 1, a), 1, .5 + u * .3, .12, hash(k, 4) * 6); }
      for (let k = 0; k < 30; k++) { const u = (tv * .06 + hash(k, s.s + 1)) % 1;
        add(s.p[0] + u * 80, s.p[1] + s.s + u * (200 + a * 30), s.p[2] + (hash(k, 5) - .5) * 40, s.s * (1.5 + u * 4), (1 - u) * .45 * smooth(0, 2, a), .2, .18, .17, hash(k, 6) * 6); }
    }
    const fa = ash(t), rk = rainK(t), wn = winter(t);
    if (fa > 0 || rk > 0 || wn > .3) {               // ash flakes / rain / sleet in a box around the camera
      const c = cam, n = Math.round(fa * 700 + rk * 260 + (wn > .3 ? smooth(.3, 1, wn) * 260 : 0));
      for (let i = 0; i < n; i++) {
        const kind = i < fa * 700 ? 'ash' : i < fa * 700 + rk * 260 ? 'rain' : 'sleet';
        const sp = kind === 'rain' ? 9 : kind === 'sleet' ? 2.2 : .9, box = kind === 'ash' ? 26 : 40;
        const x0 = hash(i, 41) * box * 2 - box, z0 = hash(i, 42) * box * 2 - box, y0 = hash(i, 43) * 30;
        const y = ((y0 - tv * sp) % 30 + 30) % 30 - 4, drift = kind === 'rain' ? 0 : Math.sin(tv * .7 + i) * 1.2;
        const px = c.x + (((x0 + drift + tv * (kind === 'ash' ? .6 : .3)) % (box * 2)) + box * 2) % (box * 2) - box, pz = c.z + ((z0 % (box * 2)) + box * 2) % (box * 2) - box;
        if (kind === 'ash') add(px, c.y + y, pz, .3 + hash(i, 44) * .35, .85, .3, .29, .27, 60 + hash(i, 45) * 6);
        else if (kind === 'sleet') add(px, c.y + y, pz, .18, .6, .85, .88, .9, 0);
        else add(px, c.y + y, pz, .12, .35, .7, .74, .8, 0);
      }
    }
  });
  return F;
}
