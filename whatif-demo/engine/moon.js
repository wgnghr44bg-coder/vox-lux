// THE MOON IN THE SKY (baksteen "Hemel", okt 2026). TL.moon = { km: [[t, km], ...], dir: [x, y, z], halo: 1 }
// A full moon at its true apparent size for its distance from the centre of the Earth (diameter 3,474 km):
// today (384,400 km) 0.52°, at 200,000 km 1°, at 100,000 km 2.1°, at 18,000 km about 17° (seen from the ground,
// you stand ~6,400 km closer). It hangs on a sphere around the camera (no parallax between shots), glows a little
// more as it comes closer, and gives places E.moonKm(t), E.moonDir and E.moonBright(t) (× today's moonlight)
// for their light and shadows. moonTexture() is shared with space.js.
import * as THREE from 'three';
import { monotone, rng } from './util.js';

export const MOON_R = 1737, EARTH_R = 6371, MOON_TODAY = 384400;

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

export function createMoon(E, TL) {
  const M = TL.moon; if (!M) return;
  const km = monotone(M.km), dir = new THREE.Vector3(...(M.dir || [-.26, .12, -.96])).normalize();
  E.moonKm = t => km(Math.min(t, TL.beats.stop));
  E.moonDir = dir;
  E.moonBright = t => (MOON_TODAY / E.moonKm(t)) ** 2;
  const D = 3000;
  const mat = new THREE.ShaderMaterial({
    fog: false, uniforms: { map: { value: moonTexture() }, gain: { value: 1 } },
    vertexShader: `varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vUv = uv; vec4 mv = modelViewMatrix * vec4(position, 1.); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform sampler2D map; uniform float gain; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ float mu = max(dot(normalize(vN), normalize(vV)), 0.); vec3 c = texture2D(map, vUv).rgb;
        gl_FragColor = vec4(c * gain * (.55 + .45 * pow(mu, .45)) * vec3(1., .99, .95), 1.); }`,
  });
  const moon = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), mat);
  moon.rotation.y = -Math.PI / 2 - .35;          // the maria side towards us
  moon.frustumCulled = false; moon.renderOrder = -1;
  // halo: soft glow around the disc (stronger as it comes closer)
  const hc = document.createElement('canvas'); hc.width = hc.height = 128; const hx = hc.getContext('2d');
  const g = hx.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(.25, 'rgba(220,228,255,.35)'); g.addColorStop(1, 'rgba(200,210,255,0)');
  hx.fillStyle = g; hx.fillRect(0, 0, 128, 128);
  const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(hc), transparent: true, depthWrite: false, fog: false, blending: THREE.AdditiveBlending }));
  halo.frustumCulled = false;
  E.scene.add(moon); if (!TL.post) E.scene.add(halo);     // film look: the bloom makes the glow (the AO pass would darken a sprite)
  let cur = 0;
  const place = cam => {
    const d = Math.max(1000, cur - EARTH_R * .95), r = D * MOON_R / d;          // seen from the ground
    moon.position.copy(cam.position).addScaledVector(dir, D); moon.scale.setScalar(r); moon.updateMatrixWorld();
    halo.position.copy(cam.position).addScaledVector(dir, D * 1.02); halo.scale.setScalar(r * (M.halo ?? 1) * 7); halo.updateMatrixWorld();
  };
  moon.onBeforeRender = (r, s, cam) => place(cam);
  halo.onBeforeRender = (r, s, cam) => place(cam);
  E.updates.push((t, F, tv) => {
    cur = E.moonKm(t);
    const b = E.moonBright(t);
    mat.uniforms.gain.value = (M.gain ?? 1.15) * Math.min(1.6, .9 + .1 * Math.log2(b));
    halo.material.opacity = Math.min(.55, .12 + .05 * Math.log2(b)) * (M.halo ?? 1);
    moon.visible = halo.visible = M.visible ? M.visible(tv) : true;
  });
  return moon;
}
