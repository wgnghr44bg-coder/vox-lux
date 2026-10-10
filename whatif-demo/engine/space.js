// EARTH AND MOON FROM SPACE (baksteen "Hemel", okt 2026). A separate little scene at true scale (1 unit = 1 km):
// the Earth (oceans, land, ice, clouds, a thin blue atmosphere), the Moon at E.moonKm(t) (TL.moon, moon.js) and stars.
//   TL.space = [[t0, t1, { yaw, pitch, frame, drift, ring }], ...]   during [t0, t1) the video shows this view
//     frame: how much of the Earth–Moon line fills the picture (1 = both just fit), yaw/pitch: where we look from (rad),
//     drift: slow orbit of the camera (rad per 10 s), ring: optional debris ring (ring.js) shown around the Earth.
// main.js asks E.space.render(tv) first; when it returns true the street/harbour scene is skipped for that frame.
import * as THREE from 'three';
import { rng, clamp, lerp, hash, smooth } from './util.js';
import { moonTexture, MOON_R, EARTH_R } from './moon.js';

function fbm3(R) {         // cheap 3D value noise (hash lattice), a few octaves
  const P = new Uint8Array(512); for (let i = 0; i < 256; i++) P[i] = i; for (let i = 255; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [P[i], P[j]] = [P[j], P[i]]; }
  for (let i = 0; i < 256; i++) P[i + 256] = P[i];
  const h = (x, y, z) => P[P[P[x & 255] + (y & 255)] + (z & 255)] / 255;
  const f = t => t * t * (3 - 2 * t);
  const n = (x, y, z) => { const X = Math.floor(x), Y = Math.floor(y), Z = Math.floor(z), u = f(x - X), v = f(y - Y), w = f(z - Z);
    const L = (a, b, t) => a + (b - a) * t;
    return L(L(L(h(X, Y, Z), h(X + 1, Y, Z), u), L(h(X, Y + 1, Z), h(X + 1, Y + 1, Z), u), v), L(L(h(X, Y, Z + 1), h(X + 1, Y, Z + 1), u), L(h(X, Y + 1, Z + 1), h(X + 1, Y + 1, Z + 1), u), v), w); };
  return (x, y, z, o = 5) => { let s = 0, a = .5, k = 1; for (let i = 0; i < o; i++) { s += a * n(x * k, y * k, z * k); a *= .5; k *= 2.03; } return s; };
}

function earthTextures() {
  const W = 1024, H = 512, R = rng(5), N = fbm3(R), C = fbm3(rng(9));
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const x = cv.getContext('2d'), img = x.createImageData(W, H);
  const cc = document.createElement('canvas'); cc.width = W; cc.height = H; const y = cc.getContext('2d'), cim = y.createImageData(W, H);
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const lon = i / W * Math.PI * 2, lat = (.5 - j / H) * Math.PI, px = Math.cos(lat) * Math.cos(lon), py = Math.sin(lat), pz = Math.cos(lat) * Math.sin(lon);
    const e = N(px * 2.2 + 5, py * 2.2 + 5, pz * 2.2 + 5), al = Math.abs(lat) / (Math.PI / 2), k = (j * W + i) * 4;
    let c;
    if (al > .82 + (e - .5) * .2) c = [236, 240, 244];                                   // ice caps
    else if (e > .54) { const d = clamp((e - .54) * 6), dry = clamp(1 - Math.abs(al - .3) * 5) * .8;   // land: green, deserts near 25-35°
      c = [lerp(lerp(70, 120, d), 196, dry), lerp(lerp(104, 112, d), 172, dry), lerp(lerp(52, 70, d), 118, dry)]; }
    else { const s = clamp((.54 - e) * 5); c = [lerp(38, 14, s), lerp(92, 48, s), lerp(140, 104, s)]; }   // ocean, shallow -> deep
    img.data.set([c[0], c[1], c[2], 255], k);
    const cl = C(px * 3 + 1, py * 3 + 1, pz * 3 + 1, 6), band = .6 + .4 * Math.cos(lat * 6);
    cim.data.set([255, 255, 255, Math.round(clamp((cl - .5) * 3.2 * band) * 235)], k);
  }
  x.putImageData(img, 0, 0); y.putImageData(cim, 0, 0);
  const a = new THREE.CanvasTexture(cv), b = new THREE.CanvasTexture(cc); a.colorSpace = b.colorSpace = THREE.SRGBColorSpace;
  return [a, b];
}

export function createSpace(E, TL) {
  const S = TL.space; if (!S || !S.length) return;
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, E.W / E.H, 50, 4e6);
  scene.background = new THREE.Color(0x010103);
  const [eTex, cTex] = earthTextures();
  const earth = new THREE.Mesh(new THREE.SphereGeometry(EARTH_R, 96, 64), new THREE.MeshLambertMaterial({ map: eTex }));
  const clouds = new THREE.Mesh(new THREE.SphereGeometry(EARTH_R * 1.008, 96, 64), new THREE.MeshLambertMaterial({ map: cTex, transparent: true, depthWrite: false }));
  const atmo = new THREE.Mesh(new THREE.SphereGeometry(EARTH_R * 1.045, 96, 64), new THREE.ShaderMaterial({
    side: THREE.BackSide, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { sun: { value: new THREE.Vector3() } },
    vertexShader: `varying vec3 vN; varying vec3 vW; void main(){ vN = normalize(mat3(modelMatrix) * normal); vec4 w = modelMatrix * vec4(position, 1.); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 sun; varying vec3 vN; varying vec3 vW;
      void main(){ vec3 v = normalize(cameraPosition - vW); float rim = pow(1. - abs(dot(v, -vN)), 3.2); float lit = clamp(dot(-vN, sun) * .8 + .35, 0., 1.);
        gl_FragColor = vec4(vec3(.35, .6, 1.) * rim * lit * 1.6, rim * lit); }` }));
  const moon = new THREE.Mesh(new THREE.SphereGeometry(MOON_R, 64, 48), new THREE.MeshLambertMaterial({ map: moonTexture() }));
  moon.rotation.y = Math.PI;                                                 // the maria side towards the Earth
  const sunDir = new THREE.Vector3(.35, .25, 1).normalize();
  const sun = new THREE.DirectionalLight(0xfff6ea, 3.2); sun.position.copy(sunDir).multiplyScalar(1e6);
  scene.add(earth, clouds, atmo, moon, sun, new THREE.AmbientLight(0x223044, .25));
  atmo.material.uniforms.sun.value.copy(sunDir);
  { const R = rng(3), n = 4000, p = new Float32Array(n * 3), c = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const u = R() * 2 - 1, a = R() * Math.PI * 2, s = Math.sqrt(1 - u * u), b = .35 + Math.pow(R(), 3) * .65;
      p.set([s * Math.cos(a) * 3e6, u * 3e6, s * Math.sin(a) * 3e6], i * 3); c.set([b, b, b * (1.05 - R() * .15)], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('color', new THREE.BufferAttribute(c, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 1.6, sizeAttenuation: false, vertexColors: true }))); }
  const mdir = new THREE.Vector3(1, 0, -.15).normalize();      // where the Moon is, seen from the Earth
  const ph0 = Math.atan2(mdir.z, mdir.x), R = rng(23);
  // TL.moon.breakAt: the Moon tears into pieces that spread along its orbit; TL.ring: the ring they become
  const frags = TL.moon?.breakAt ? Array.from({ length: 40 }, (_, i) => {
    const g = new THREE.IcosahedronGeometry(MOON_R, 1), p = g.attributes.position;
    for (let k = 0; k < p.count; k++) { const q = .7 + hash(k + i * 50, 3) * .5; p.setXYZ(k, p.getX(k) * q, p.getY(k) * q, p.getZ(k) * q); }
    g.computeVertexNormals(); const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ map: moonTexture() })); m.visible = false; scene.add(m);
    return { m, size: i < 4 ? .5 - i * .07 : .05 + R() * .14, dth: (R() - .5) * (i < 4 ? .3 : 1), dr: (R() - .5) * .12, dy: (R() - .5) * .02, spin: R() * 2 }; }) : [];
  let ringMat = null;
  if (TL.ring) {
    const [r0, r1] = TL.ring.r || [9000, 20000], g = new THREE.RingGeometry(r0, r1, 360, 12); g.rotateX(-Math.PI / 2);
    ringMat = new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide,
      uniforms: { show: { value: 0 }, arc: { value: Math.PI }, ph0: { value: ph0 }, r0: { value: r0 }, r1: { value: r1 } },
      vertexShader: `varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
      fragmentShader: `uniform float show, arc, ph0, r0, r1; varying vec3 vP;
        void main(){ float u = (length(vP.xz) - r0) / (r1 - r0), a = atan(vP.z, vP.x), d = abs(atan(sin(a - ph0), cos(a - ph0)));
          float lanes = clamp(.68 + .2 * sin(u * 61.) * sin(u * 23. + 1.3) + .1 * sin(u * 173.), 0., 1.);
          float gap = smoothstep(.0, .02, abs(u - .62)) * smoothstep(.0, .012, abs(u - .31)), edge = smoothstep(0., .06, u) * smoothstep(1., .9, u);
          float shadow = vP.x * ${'${sx}'} + vP.z * ${'${sz}'} < 0. && abs(vP.x * ${'${sz}'} - vP.z * ${'${sx}'}) < ${EARTH_R.toFixed(1)} ? .25 : 1.;
          float dens = lanes * gap * edge; gl_FragColor = vec4(mix(vec3(.6, .58, .55), vec3(.95, .92, .86), dens) * shadow, dens * show * smoothstep(arc, arc * .7, d) * .9); }`
        .replace(/\$\{sx\}/g, sunDir.x.toFixed(4)).replace(/\$\{sz\}/g, sunDir.z.toFixed(4)) });
    scene.add(new THREE.Mesh(g, ringMat));
  }
  E.spaceScene = scene;
  E.space = {
    scene, earth, moon,
    on: tv => S.find(s => tv >= s[0] && tv < s[1]),
    render(tv) {
      const s = this.on(tv); if (!s) return false;
      const v = s[2] || {}, t = Math.min(tv, TL.beats.stop), km = E.moonKm ? E.moonKm(t) : 384400;
      moon.position.copy(mdir).multiplyScalar(km);
      const b = E.moonBroken ? E.moonBroken(t) : 0, u = smooth(.15, 1, b);
      moon.visible = !v.noMoon && b < .3; moon.scale.set(1 + smooth(0, .25, b) * .35, 1 - smooth(0, .25, b) * .1, 1 - smooth(0, .25, b) * .12);
      moon.rotation.set(0, Math.PI + ph0, 0);
      for (const f of frags) { f.m.visible = b > .22; const a = ph0 - f.dth * u * (TL.moon.spread ?? 1.2), r = km * (1 + f.dr * u);
        f.m.position.set(Math.cos(a) * r, f.dy * u * km, Math.sin(a) * r); f.m.scale.setScalar(f.size * (1 + .3 * u)); f.m.rotation.set(t * .1 * f.spin, t * .07 * f.spin, 0); }
      if (ringMat) { ringMat.uniforms.show.value = E.ringShow(t); ringMat.uniforms.arc.value = E.ringArc(t); }
      earth.rotation.y = tv * .01; clouds.rotation.y = tv * .013;
      for (const u of this.updates) u(t, tv, v);
      // frame the Earth–Moon line: camera to the side, far enough that both fit (frame < 1 = closer)
      const mid = mdir.clone().multiplyScalar(km * (v.focus ?? .45));
      const yaw = (v.yaw ?? .25) + (v.drift ?? .02) * (tv - s[0]) / 10, pitch = v.pitch ?? .18;
      const off = new THREE.Vector3(Math.sin(yaw) * Math.cos(pitch), Math.sin(pitch), Math.cos(yaw) * Math.cos(pitch));
      const span = v.span ?? (km + EARTH_R * 3), dist = span * (v.frame ?? 1) / (2 * Math.tan(cam.fov * Math.PI / 360) * cam.aspect) * 1.15;
      cam.position.copy(mid).addScaledVector(off, dist); cam.lookAt(mid); cam.updateProjectionMatrix();
      const r = E.renderer, tm = r.toneMapping; r.toneMapping = THREE.NoToneMapping;
      r.render(scene, cam); r.toneMapping = tm;
      return true;
    },
    updates: [],
  };
}
