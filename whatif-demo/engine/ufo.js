// UFOs (baksteen "Ufo", okt 2026): a huge mothership over the city, smaller ships, light beams, hovering, landing.
// Any place, any force. TL.ufo = {
//   ships: [{ id, kind: 'mother' | 'scout', r: radius m, keys: [[t, x, y, z], ...] (smooth path), spin: rad/s,
//             bob: m (hover), haze: 0..1 (distance tint), lights: true, legs: t (legs out), door: t (ramp opens, light pours out),
//             look: weight (POV camera looks at it), hull: color }],
//   beams: [{ ship: id, t0, t1, r: radius on the ground, keys: [[t, x, z], ...] (where it points), color, opacity }],
// }
// Mothership: dark low-poly disc with panel rings, a ring of lights under the rim and a glowing core.
// Scout: small disc with a dome, light ring, three legs and a ramp. Ships use no fog (they are kilometres away).
import * as THREE from 'three';
import { clamp, smooth, lerp } from './util.js';

const HAZE = new THREE.Color(0xa9b6c2);

function path(keys) {           // smooth (cosine-eased) interpolation through [t, x, y, z] keys
  return t => {
    if (t <= keys[0][0]) return keys[0].slice(1);
    for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
      const a = keys[i - 1], b = keys[i], u = (t - a[0]) / (b[0] - a[0] || 1), e = .5 - .5 * Math.cos(Math.PI * u);
      return a.slice(1).map((v, k) => lerp(v, b[k + 1], e));
    }
    return keys[keys.length - 1].slice(1);
  };
}

function mat(color, haze, o = {}) {
  // seen from below a ship gets little sun: a soft sky glow (emissive) keeps its panels readable, more with distance (haze)
  const c = new THREE.Color(color).lerp(HAZE, haze), em = new THREE.Color(color).multiplyScalar(.35).lerp(HAZE, haze * .55);
  return new THREE.MeshLambertMaterial({ color: c, emissive: em, flatShading: true, fog: false, side: THREE.DoubleSide, ...o });
}
const glowMat = (color, o = {}) => new THREE.MeshBasicMaterial({ color, fog: false, ...o });

function mothership(s) {
  const g = new THREE.Group(), r = s.r, hz = s.haze ?? .35, hull = s.hull ?? 0x3b4048;
  // profile (radius, height) in units of r: flat top dome, sharp rim, shallow underside
  const top = [[0, .16], [.18, .155], [.4, .13], [.62, .09], [.82, .045], [.97, .012], [1, 0]];
  const bot = [[1, 0], [.96, -.02], [.8, -.05], [.55, -.07], [.3, -.08], [0, -.085]];
  const lathe = (pts, m) => { const geo = new THREE.LatheGeometry(pts.map(([x, y]) => new THREE.Vector2(x * r, y * r)), 40); return new THREE.Mesh(geo, m); };
  g.add(lathe([...top].reverse(), mat(hull, hz)));
  g.add(lathe(bot, mat(new THREE.Color(hull).multiplyScalar(.7), hz)));
  // panel rings and radial ribs (darker / lighter bands) on the underside
  for (const [rr, w, k] of [[.92, .025, 1.25], [.72, .02, .8], [.5, .02, 1.2], [.34, .015, .75]]) {
    const ring = new THREE.Mesh(new THREE.RingGeometry((rr - w) * r, rr * r, 40), mat(new THREE.Color(hull).multiplyScalar(k), hz, { side: THREE.DoubleSide }));
    ring.rotation.x = Math.PI / 2; ring.position.y = -(.02 + (1 - rr) * .07) * r - .5; g.add(ring);
  }
  for (let i = 0; i < 24; i++) {
    const a = i / 24 * Math.PI * 2, rib = new THREE.Mesh(new THREE.BoxGeometry(.012 * r, .012 * r, .5 * r), mat(new THREE.Color(hull).multiplyScalar(.9), hz));
    rib.position.set(Math.sin(a) * .62 * r, -.06 * r, Math.cos(a) * .62 * r); rib.rotation.y = a; g.add(rib);
  }
  // top: superstructure blocks
  for (let i = 0; i < 10; i++) {
    const a = i / 10 * Math.PI * 2 + .3, d = (.25 + (i % 3) * .14) * r, b = new THREE.Mesh(new THREE.BoxGeometry(.06 * r, .05 * r, .12 * r), mat(new THREE.Color(hull).multiplyScalar(1.15), hz));
    b.position.set(Math.sin(a) * d, .14 * r, Math.cos(a) * d); b.rotation.y = a; g.add(b);
  }
  // lights: ring under the rim, inner ring, glowing core
  const lights = [];
  if (s.lights !== false) {
    for (const [rr, n, col, sz] of [[.9, 64, 0xffe7b8, .008], [.58, 36, 0x9fd8ff, .007]]) {
      const im = new THREE.InstancedMesh(new THREE.SphereGeometry(sz * r, 6, 4), glowMat(col), n), o = new THREE.Object3D();
      for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; o.position.set(Math.sin(a) * rr * r, -(.02 + (1 - rr) * .07) * r - sz * r, Math.cos(a) * rr * r); o.updateMatrix(); im.setMatrixAt(i, o.matrix); }
      g.add(im); lights.push(im);
    }
    const core = new THREE.Mesh(new THREE.CircleGeometry(.14 * r, 32), glowMat(0xbfe6ff, { side: THREE.DoubleSide, transparent: true, opacity: .9 }));
    core.rotation.x = Math.PI / 2; core.position.y = -.086 * r; g.add(core); lights.push(core);
    const halo = new THREE.Mesh(new THREE.RingGeometry(.14 * r, .2 * r, 32), glowMat(0x6fb8e8, { side: THREE.DoubleSide, transparent: true, opacity: .35, blending: THREE.AdditiveBlending, depthWrite: false }));
    halo.rotation.x = Math.PI / 2; halo.position.y = -.0855 * r; g.add(halo); lights.push(halo);
  }
  return { g, lights, bottom: -.086 * r };
}

function scout(s) {
  const g = new THREE.Group(), r = s.r, hz = s.haze ?? 0, hull = s.hull ?? 0x6c727a;
  const pts = [[0, -.22], [.35, -.2], [.75, -.12], [1, 0], [.8, .1], [.42, .16], [0, .17]];
  g.add(new THREE.Mesh(new THREE.LatheGeometry(pts.map(([x, y]) => new THREE.Vector2(x * r, y * r)), 24), mat(hull, hz)));
  const dome = new THREE.Mesh(new THREE.SphereGeometry(.36 * r, 16, 6, 0, Math.PI * 2, 0, Math.PI / 2), mat(new THREE.Color(hull).multiplyScalar(.75), hz));
  dome.position.y = .15 * r; g.add(dome);
  const lights = [];
  const win = new THREE.Mesh(new THREE.CylinderGeometry(.362 * r, .362 * r, .05 * r, 16, 1, true), glowMat(0x9fe0ff, { side: THREE.DoubleSide }));
  win.position.y = .2 * r; g.add(win); lights.push(win);
  if (s.lights !== false) {
    const n = 16, im = new THREE.InstancedMesh(new THREE.SphereGeometry(.035 * r, 6, 4), glowMat(0xffe2a8), n), o = new THREE.Object3D();
    for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2; o.position.set(Math.sin(a) * .9 * r, -.04 * r, Math.cos(a) * .9 * r); o.updateMatrix(); im.setMatrixAt(i, o.matrix); }
    g.add(im); lights.push(im);
    const core = new THREE.Mesh(new THREE.CircleGeometry(.2 * r, 20), glowMat(0xc9ecff, { side: THREE.DoubleSide }));
    core.rotation.x = Math.PI / 2; core.position.y = -.221 * r; g.add(core); lights.push(core);
  }
  // three legs that slide out for landing
  const legs = [0, 1, 2].map(i => {
    const a = i / 3 * Math.PI * 2 + .5, L = new THREE.Group(); L.position.set(Math.sin(a) * .55 * r, -.15 * r, Math.cos(a) * .55 * r);
    const strut = new THREE.Mesh(new THREE.CylinderGeometry(.03 * r, .03 * r, .4 * r, 6), mat(0x4a4f56, hz)); strut.position.y = -.2 * r; L.add(strut);
    const foot = new THREE.Mesh(new THREE.CylinderGeometry(.09 * r, .11 * r, .03 * r, 8), mat(0x4a4f56, hz)); foot.position.y = -.4 * r; L.add(foot);
    g.add(L); return L;
  });
  // ramp on the side facing +z: hinged at the bottom of the hull, swings down to the ground; light behind it
  const hinge = new THREE.Group(); hinge.position.set(0, -.12 * r, .62 * r); g.add(hinge);
  const ramp = new THREE.Mesh(new THREE.BoxGeometry(.32 * r, .02 * r, .55 * r), mat(0x585e66, hz)); ramp.position.z = .275 * r; hinge.add(ramp);
  const open = new THREE.Mesh(new THREE.PlaneGeometry(.3 * r, .2 * r), glowMat(0xfff4dc, { side: THREE.DoubleSide }));
  open.position.set(0, -.03 * r, .6 * r); open.visible = false; g.add(open);
  const glow = new THREE.PointLight(0xfff0d0, 0, 14 * r / 10, 1.4); glow.position.set(0, -.15 * r, .9 * r); g.add(glow);
  // soft light spilling onto the ground in front of the ramp
  const spill = new THREE.Mesh(new THREE.CircleGeometry(.6 * r, 24), glowMat(0xfff1d6, { transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  spill.rotation.x = -Math.PI / 2; g.add(spill);
  return { g, lights, legs, hinge, open, glow, spill, bottom: -.6 * r };
}

export function createUfo(E, TL) {
  const U = TL.ufo; if (!U) return;
  // the sky dome must never hide ships beyond its radius
  E.scene.traverse(o => { if (o.material === E.skyMat) o.renderOrder = -10; });
  const ships = {};
  for (const s of U.ships || []) {
    const S = s.kind === 'mother' ? mothership(s) : scout(s);
    const pos = path(s.keys);
    E.scene.add(S.g);
    if (s.kind !== 'mother') S.g.traverse(o => { if (o.isMesh) o.castShadow = true; });
    ships[s.id] = { ...s, ...S, pos };
    E.updates.push((t, F, tv) => {
      const tt = Math.min(tv, TL.beats.stop ?? 1e9), p = pos(tt), r = s.r;
      const show = s.from == null || tt >= s.from;
      S.g.visible = show && (s.until == null || tt <= s.until);
      const landed = s.land != null ? smooth(s.land - .1, s.land + .4, tt) : 0;
      const bob = (s.bob ?? (s.kind === 'mother' ? 6 : .4)) * Math.sin(tt * .6 + r) * (1 - landed);
      S.g.position.set(p[0], p[1] + bob, p[2]);
      S.g.rotation.y = (s.ry ?? 0) + tt * (s.spin ?? (s.kind === 'mother' ? .004 : .15)) * (1 - landed);
      S.g.rotation.z = Math.sin(tt * .45 + r) * (s.kind === 'mother' ? .002 : .02) * (1 - landed);
      for (const l of S.lights) if (l.material) l.material.opacity = l.material.transparent ? lerp(.25, .9, .5 + .5 * Math.sin(tt * 2.2)) : 1;
      if (S.legs) {
        const out = s.legs != null ? smooth(s.legs, s.legs + 2, tt) : 0;
        S.legs.forEach(L => { L.scale.y = .05 + .95 * out; L.visible = out > .01; });
        const d = s.door != null ? smooth(s.door, s.door + 2.5, tt) : 0;
        S.hinge.rotation.x = d * 1.15; S.open.visible = d > .02;
        S.glow.intensity = d * (s.doorLight ?? 260); S.spill.material.opacity = d * .35;
        S.spill.position.set(0, -p[1] - bob + .05 + (E.groundAt ? E.groundAt(p[0], p[2]) : 0), .9 * r);
      }
    });
    if (s.look) (E.skyObjects ||= []).push({ t0: s.lookFrom ?? s.keys[0][0], t1: s.lookUntil ?? 1e9, pos: t => { const q = pos(t); return [q[0], q[1] + S.bottom, q[2]]; }, weight: s.look });
  }
  // light beams: open cones from the bottom of a ship to a point on the ground (sweeping along keys)
  for (const b of U.beams || []) {
    const ship = ships[b.ship]; if (!ship) continue;
    // cone: top ring (small) at y = 0, ground ring (radius 1) at y = -1; scaled to r and the length each frame
    const geo = new THREE.CylinderGeometry((b.top ?? ship.r * .12) / b.r, 1, 1, 28, 1, true).translate(0, -.5, 0);
    const cone = new THREE.Mesh(geo, glowMat(b.color ?? 0xbfe4ff, { transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    const spot = new THREE.Mesh(new THREE.CircleGeometry(1, 28), glowMat(b.color ?? 0xbfe4ff, { transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    spot.rotation.x = -Math.PI / 2;
    E.scene.add(cone, spot);
    const aim = path(b.keys.map(k => [k[0], k[1], 0, k[2]])), down = new THREE.Vector3(0, -1, 0), dir = new THREE.Vector3();
    E.updates.push((t, F, tv) => {
      const tt = Math.min(tv, TL.beats.stop ?? 1e9), a = smooth(b.t0, b.t0 + (b.fade ?? 1), tt) * (1 - smooth(b.t1 - (b.fade ?? 1), b.t1, tt));
      cone.visible = spot.visible = a > .005 && ship.g.visible; if (!cone.visible) return;
      const top = ship.g.position.clone(); top.y += ship.bottom;
      const g = aim(tt), tgt = new THREE.Vector3(g[0], (E.groundAt ? E.groundAt(g[0], g[2]) : 0) + .06, g[2]);
      dir.subVectors(tgt, top); const len = dir.length(); dir.normalize();
      const flick = 1 + .06 * Math.sin(tt * 9 + b.t0) + .04 * Math.sin(tt * 23);
      cone.position.copy(top); cone.quaternion.setFromUnitVectors(down, dir); cone.scale.set(b.r, len, b.r);
      cone.material.opacity = (b.opacity ?? .22) * a * flick;
      spot.position.copy(tgt); spot.scale.setScalar(b.r * 1.05); spot.material.opacity = (b.opacity ?? .22) * 1.8 * a * flick;
    });
  }
  E.camera.far = Math.max(E.camera.far, 12000); E.camera.updateProjectionMatrix();   // ships kilometres away
  E.ufoShips = ships;
}
