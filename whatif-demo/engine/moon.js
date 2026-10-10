// THE MOON IN THE SKY (baksteen "Hemel", okt 2026). TL.moon = { km: [[t, km], ...], dir | orbit, night, breakAt, halo }
// A full moon at its true apparent size for its distance (diameter 3,474 km): today 0.52°, at 100,000 km 2°,
// at 25,000 km ~10°, at the Roche limit (~18,000 km from the Earth's centre) ~15° seen from the ground.
//   dir:   fixed direction in the scene ([x, y, z], -z = towards the sea / the equator), or
//   orbit: { lat: 30, theta: 1.2 } the Moon on its orbit in the equatorial plane, seen from latitude `lat`
//          (theta 0 = east, π/2 = due south and highest); it then moves in the sky as it comes closer (true parallax).
//          The same geometry places the debris ring (ring.js).
//   night: true  -> any place becomes night lit by the Moon (brighter as it comes closer: × (384,400 / km)²)
//   breakAt: [t0, t1] the Moon is stretched and torn apart between t0 and t1 (Roche limit); its pieces spread
//          along its orbit (they become the ring, ring.js) -> E.moonBroken(t) 0..1
// Gives places E.moonKm(t), E.moonDir, E.moonDirAt(t), E.moonBright(t) for light and shadows.
// moonTexture() and skyGeo() are shared with space.js / ring.js; moonShot() helps scenarios aim a camera at the Moon.
import * as THREE from 'three';
import { monotone, rng, smooth, clamp, hash } from './util.js';

export const MOON_R = 1737, EARTH_R = 6371, MOON_TODAY = 384400;

// observer on the ground at latitude lat (deg): Earth's centre and the equatorial plane in scene axes
// (x east, y up, -z towards the equator). Point on the equatorial circle of radius r at angle theta, relative to you.
export function skyGeo(lat = 30) {
  const f = lat * Math.PI / 180, C = new THREE.Vector3(0, -EARTH_R, 0);
  const e1 = new THREE.Vector3(1, 0, 0), e2 = new THREE.Vector3(0, Math.cos(f), -Math.sin(f));
  return { C, e1, e2, at: (r, th) => C.clone().addScaledVector(e1, r * Math.cos(th)).addScaledVector(e2, r * Math.sin(th)) };
}
// a camera standpoint looking at the Moon (km from the Earth's centre) from pos: for scenario.extraShots
export function moonShot(M, km, pos, fov, o = {}) {
  const d = M.orbit ? skyGeo(M.orbit.lat).at(km, M.orbit.theta).normalize() : new THREE.Vector3(...M.dir).normalize();
  const c = Math.cos(o.yaw || 0), s = Math.sin(o.yaw || 0), x = d.x * c - d.z * s, z = d.x * s + d.z * c;
  return { pos, look: [pos[0] + x * 1000, pos[1] + (d.y + (o.el || 0)) * 1000, pos[2] + z * 1000], drift: o.drift || [0, 0, 0], fov };
}

let TEX = null;
export function moonTexture() {
  if (TEX) return TEX;
  const W = 1024, H = 512, cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const x = cv.getContext('2d'), R = rng(77);
  x.fillStyle = '#b9b5ac'; x.fillRect(0, 0, W, H);
  // maria (dark plains), mostly on the side that faces the Earth (u 0.15..0.45)
  for (const [u, v, r] of [[.3, .38, .09], [.24, .45, .07], [.36, .5, .06], [.2, .6, .05], [.33, .3, .05], [.42, .42, .045], [.27, .55, .06], [.16, .4, .04]]) {
    const g = x.createRadialGradient(u * W, v * H, 0, u * W, v * H, r * W);
    g.addColorStop(0, 'rgba(92,90,88,.85)'); g.addColorStop(.7, 'rgba(100,98,95,.6)'); g.addColorStop(1, 'rgba(110,108,104,0)');
    x.fillStyle = g; x.fillRect(0, 0, W, H);
  }
  // craters: light rim, darker floor
  for (let i = 0; i < 420; i++) {
    const cx = R() * W, cy = H * (.08 + R() * .84), r = Math.pow(R(), 3) * 26 + 2;
    x.fillStyle = 'rgba(70,68,64,.28)'; x.beginPath(); x.ellipse(cx, cy, r, r * .9, 0, 0, Math.PI * 2); x.fill();
    x.strokeStyle = 'rgba(225,222,214,.35)'; x.lineWidth = Math.max(1, r * .18); x.beginPath(); x.ellipse(cx, cy, r, r * .9, 0, 0, Math.PI * 2); x.stroke();
  }
  // a bright ray crater (Tycho-like)
  const tx = .3 * W, ty = .78 * H; x.strokeStyle = 'rgba(235,232,225,.25)'; x.lineWidth = 2;
  for (let k = 0; k < 18; k++) { const a = R() * Math.PI * 2, l = 40 + R() * 120; x.beginPath(); x.moveTo(tx, ty); x.lineTo(tx + Math.cos(a) * l, ty + Math.sin(a) * l * .6); x.stroke(); }
  TEX = new THREE.CanvasTexture(cv); TEX.colorSpace = THREE.SRGBColorSpace; TEX.anisotropy = 4;
  return TEX;
}

// lit-moon shader: texture, limb darkening, glowing cracks (crack 0..1) where it tears
function moonMat() {
  return new THREE.ShaderMaterial({
    fog: false, uniforms: { map: { value: moonTexture() }, gain: { value: 1 }, crack: { value: 0 } },
    vertexShader: `varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position, 1.); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform sampler2D map; uniform float gain; uniform float crack; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ float mu = max(dot(normalize(vN), normalize(vV)), 0.); vec3 c = texture2D(map, vUv).rgb * gain * (.55 + .45 * pow(mu, .45)) * vec3(1., .99, .95);
        float l = abs(sin(vUv.x * 41. + sin(vUv.y * 23.) * 2.)) * abs(sin(vUv.y * 37. + sin(vUv.x * 19.) * 2.5));
        c = mix(c, vec3(1., .55, .2) * 1.6, smoothstep(1. - crack * .08, 1., 1. - l) * crack);
        gl_FragColor = vec4(c, 1.); }`,
  });
}

export function createMoon(E, TL) {
  const M = TL.moon; if (!M) return;
  const STOP = TL.beats.stop, km = monotone(M.km), G = M.orbit ? skyGeo(M.orbit.lat) : null;
  E.moonKm = t => km(Math.min(t, STOP));
  const fixed = new THREE.Vector3(...(M.dir || [-.26, .12, -.96])).normalize();
  const rel = (t, th = M.orbit?.theta) => G ? G.at(E.moonKm(t), th) : fixed.clone().multiplyScalar(E.moonKm(t) - EARTH_R * .95);   // Moon relative to you (km)
  E.moonDirAt = t => rel(t).normalize();
  E.moonDir = E.moonDirAt(0);
  E.moonBright = t => (MOON_TODAY / E.moonKm(t)) ** 2;
  E.moonBroken = t => M.breakAt ? smooth(M.breakAt[0], M.breakAt[1], Math.min(t, STOP)) : 0;
  E.moonGeo = G;
  const D = 3000;
  const mat = moonMat();
  const moon = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), mat);
  moon.rotation.y = -Math.PI / 2 - .35;          // the maria side towards us
  moon.frustumCulled = false; moon.renderOrder = -1;
  // fragments (only with breakAt): pieces of the Moon that drift apart along its orbit
  const NF = M.breakAt ? 26 : 0, R = rng(19), frags = [];
  for (let i = 0; i < NF; i++) {
    const g = new THREE.IcosahedronGeometry(1, 1), p = g.attributes.position;
    for (let k = 0; k < p.count; k++) { const s = .7 + hash(k + i * 50, 3) * .5; p.setXYZ(k, p.getX(k) * s, p.getY(k) * s, p.getZ(k) * s); }
    g.computeVertexNormals();
    const f = new THREE.Mesh(g, moonMat()); f.frustumCulled = false; f.visible = false;
    frags.push({ m: f, size: i < 4 ? .45 - i * .06 : .08 + R() * .16, dth: (R() - .5) * (i < 4 ? .25 : 1), off: [(R() - .5) * .5, (R() - .5) * .5], spin: R() * 2 });
  }
  // halo: soft glow around the disc (with the film look the bloom does this; the AO pass would darken a sprite)
  const hc = document.createElement('canvas'); hc.width = hc.height = 128; const hx = hc.getContext('2d');
  const g = hx.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.25, 'rgba(220,228,255,.35)'); g.addColorStop(1, 'rgba(200,210,255,0)');
  hx.fillStyle = g; hx.fillRect(0, 0, 128, 128);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(hc), transparent: true, depthWrite: false, fog: false, blending: THREE.AdditiveBlending }));
  halo.frustumCulled = false;
  E.scene.add(moon); for (const f of frags) E.scene.add(f.m);
  if (!TL.post || TL.post.ao === false) E.scene.add(halo);
  let cur = new THREE.Vector3(1, 0, 0), curT = 0;
  const _t = new THREE.Vector3();
  const place = cam => {
    const d = cur.length(), dir = _t.copy(cur).normalize(), r = D * MOON_R / d;
    moon.position.copy(cam.position).addScaledVector(dir, D); moon.updateMatrixWorld();
    halo.position.copy(cam.position).addScaledVector(dir, D * 1.02); halo.scale.setScalar(r * (M.halo ?? 1) * Math.min(7, 2.6 + 50 / r)); halo.updateMatrixWorld();
    const b = E.moonBroken(curT);
    if (NF && b > 0) {
      const km0 = E.moonKm(curT), u = smooth(.15, 1, b);
      for (const f of frags) {
        const p = rel(curT, M.orbit.theta + f.dth * u * (M.spread ?? 1.2)), dd = p.length();
        p.normalize(); const rr = D * MOON_R / dd;
        f.m.position.copy(cam.position).addScaledVector(p, D * .999).add(_t.set(f.off[0], f.off[1], 0).multiplyScalar(rr * (.3 + .6 * u) * smooth(0, .3, b)));
        f.m.scale.setScalar(rr * f.size * (1 + .3 * u) * (1 - .9 * smooth(.75, 1, b))); f.m.rotation.set(curT * .1 * f.spin, curT * .07 * f.spin, 0); f.m.updateMatrixWorld();
      }
    }
  };
  moon.onBeforeRender = (r, s, cam) => place(cam);
  halo.onBeforeRender = (r, s, cam) => place(cam);
  for (const f of frags) f.m.onBeforeRender = (r, s, cam) => place(cam);
  E.updates.push((t, F, tv) => {
    curT = t; cur = rel(t);
    const b = E.moonBroken(t), d = cur.length(), r = D * MOON_R / d;
    // stretch along the orbit while it starts to tear, then the whole disc gives way to the pieces
    const st = smooth(0, .25, b);
    moon.scale.set(r * (1 + st * .35), r * (1 - st * .12), r * (1 - st * .1));
    if (G) { const tan = G.e1.clone().multiplyScalar(-Math.sin(M.orbit.theta)).addScaledVector(G.e2, Math.cos(M.orbit.theta)); moon.quaternion.setFromUnitVectors(new THREE.Vector3(1, 0, 0), tan); moon.rotateX(-Math.PI / 2 - .35); }
    const gain = (M.gain ?? 1.15) * Math.min(1.6, .9 + .1 * Math.log2(E.moonBright(t)));
    mat.uniforms.gain.value = gain; mat.uniforms.crack.value = smooth(0, .3, b);
    for (const f of frags) { f.m.visible = b > .22 && b < .985; f.m.material.uniforms.gain.value = gain * .8; f.m.material.uniforms.crack.value = .6 * (1 - smooth(.5, 1, b)); }
    halo.material.opacity = Math.min(.55, .12 + .05 * Math.log2(E.moonBright(t))) * (M.halo ?? 1) * (1 - b);
    const vis = M.visible ? M.visible(tv) : true;
    moon.visible = vis && b < .3; halo.visible = vis;
  });
  // night lit by the Moon (any place): dark sky with stars, moonlight that grows as it comes closer
  if (M.night) (E.lookMods ||= []).push((t, L) => {
    const k = clamp(Math.log2(E.moonBright(t)) / 9), C = h => new THREE.Color(h);       // 0 today .. 1 at ~250× today's moonlight
    L.top = C(0x060c18).lerp(C(0x14223c), k); L.hor = C(0x15223a).lerp(C(0x2a3c5a), k); L.stars = 1 - k * .5;
    L.fogColor = C(0x0d1626).lerp(C(0x22324e), k); L.fogNear = Math.min(L.fogNear ?? 200, 250); L.fogFar = Math.max(L.fogFar ?? 1600, 2200);
    L.hemi = .95 + .35 * k; L.hemiColor = C(0x7a8aa8); L.groundColor = C(0x24262a);
    L.sun = 1.1 + .9 * k; L.sunColor = C(0xc4d2f2); L.sunDisc = C(0); L.dark = 1; L.haze = 0; L.dustLight = .6;
    const d = E.moonDirAt(t); E.sunOffset = d.clone().multiplyScalar(220); if (E.sunOffset.y < 60) E.sunOffset.y = 60;
  });
  return moon;
}
