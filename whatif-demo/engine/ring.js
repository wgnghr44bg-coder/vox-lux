// A RING AROUND THE EARTH, seen from the ground (baksteen "Hemel", okt 2026). Needs TL.moon.orbit (moon.js) for the
// geometry: the ring lies in the Moon's orbital plane, so from latitude `lat` it is an arc from the eastern to the
// western horizon, highest towards the equator (-z), its inner part lower in the sky.
//   TL.ring = { r: [9000, 20000] km from the Earth's centre, show: [[t, 0..1], ...] how much of it exists,
//              arc: [[t, radians], ...] half-width of the arc around the Moon's old place (while it forms; default π),
//              lit: 0..1 brightness (sunlit band; default 1) }
// The band has fine gaps and denser lanes (like Saturn's) and fades into the haze near the horizon.
import * as THREE from 'three';
import { monotone, hash } from './util.js';

export function createRing(E, TL) {
  const RG = TL.ring; if (!RG || !E.moonGeo) return;
  const G = E.moonGeo, [r0, r1] = RG.r || [9000, 20000], th0 = TL.moon.orbit.theta;
  const show = monotone(RG.show || [[0, 1]]), arc = monotone(RG.arc || [[0, Math.PI]]);
  const NT = 360, NR = 24, D = 2900, pos = [], uv = [], idx = [];
  for (let i = 0; i <= NT; i++) for (let j = 0; j <= NR; j++) {
    const th = -.35 + (Math.PI + .7) * i / NT, r = r0 + (r1 - r0) * j / NR, p = G.at(r, th).normalize().multiplyScalar(D);
    pos.push(p.x, p.y, p.z); uv.push(j / NR, th);
  }
  for (let i = 0; i < NT; i++) for (let j = 0; j < NR; j++) { const a = i * (NR + 1) + j, b = a + NR + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, fog: false, side: THREE.DoubleSide,
    uniforms: { show: { value: 0 }, arc: { value: Math.PI }, th0: { value: th0 }, lit: { value: RG.lit ?? 1 } },
    vertexShader: `varying vec2 vUv; varying float vY; void main(){ vUv = uv; vY = normalize(position).y; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
    fragmentShader: `uniform float show, arc, th0, lit; varying vec2 vUv; varying float vY;
      float h(float x){ return fract(sin(x * 127.1) * 43758.5); }
      void main(){ float u = vUv.x, d = abs(vUv.y - th0);
        float lanes = .55 + .45 * sin(u * 61.) * sin(u * 23. + 1.3) + .25 * sin(u * 173.);
        float gap = smoothstep(.0, .02, abs(u - .62)) * smoothstep(.0, .012, abs(u - .31));
        float edge = smoothstep(0., .06, u) * smoothstep(1., .9, u);
        float dens = clamp(lanes, 0., 1.) * gap * edge * (.75 + .25 * h(floor(u * 90.)));
        float a = dens * show * smoothstep(arc, arc * .7, d) * smoothstep(-.01, .08, vY);
        vec3 c = mix(vec3(.72, .70, .66), vec3(.95, .92, .86), dens) * lit;
        gl_FragColor = vec4(c, a * .85); }`,
  });
  const ring = new THREE.Mesh(geo, mat); ring.frustumCulled = false; ring.renderOrder = -2;
  ring.onBeforeRender = (r, s, cam) => { ring.position.copy(cam.position); ring.updateMatrixWorld(); };
  E.scene.add(ring);
  E.updates.push(t => { mat.uniforms.show.value = show(Math.min(t, TL.beats.stop)); mat.uniforms.arc.value = arc(Math.min(t, TL.beats.stop)); });
  E.ringShow = show; E.ringArc = arc;
  return ring;
}
