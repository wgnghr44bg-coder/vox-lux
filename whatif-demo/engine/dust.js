// Soft particle clouds (dust, snow, spray). Emitters are functions (t, add, cam) that call
// add(x, y, z, size, alpha, r, g, b, rot) for every puff alive at time t (stateless, so any
// frame renders on its own). Puffs close to the camera fade out, so silhouettes stay readable.
import * as THREE from 'three';
import { rng, hash, smooth } from './util.js';

function puffTexture() {
  const cv = document.createElement('canvas'); cv.width = cv.height = 128;
  const x = cv.getContext('2d'), R = rng(99);
  for (let i = 0; i < 26; i++) {
    const px = 64 + (R() - .5) * 60, py = 64 + (R() - .5) * 60, r = 18 + R() * 26;
    const gr = x.createRadialGradient(px, py - r * 0.3, 0, px, py, r);
    gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.6, 'rgba(235,235,235,0.25)'); gr.addColorStop(1, 'rgba(200,200,200,0)');
    x.fillStyle = gr; x.beginPath(); x.arc(px, py, r, 0, 7); x.fill();
  }
  const fade = x.createRadialGradient(64, 64, 30, 64, 64, 64);
  x.globalCompositeOperation = 'destination-in';
  fade.addColorStop(0, 'rgba(0,0,0,1)'); fade.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = fade; x.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function createDust(E) {
  const MAXP = 3500, H = E.H;
  const geo = new THREE.BufferGeometry();
  const P = { pos: new Float32Array(MAXP * 3), col: new Float32Array(MAXP * 3), size: new Float32Array(MAXP), alpha: new Float32Array(MAXP), rot: new Float32Array(MAXP) };
  geo.setAttribute('position', new THREE.BufferAttribute(P.pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(P.col, 3));
  geo.setAttribute('size', new THREE.BufferAttribute(P.size, 1));
  geo.setAttribute('alpha', new THREE.BufferAttribute(P.alpha, 1));
  geo.setAttribute('rot', new THREE.BufferAttribute(P.rot, 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false,
    uniforms: { map: { value: puffTexture() }, scale: { value: H / (2 * Math.tan(THREE.MathUtils.degToRad(30))) },
                fogColor: { value: new THREE.Color() }, fogNear: { value: 120 }, fogFar: { value: 900 }, light: { value: 1 } },
    vertexShader: `attribute float size; attribute float alpha; attribute float rot; attribute vec3 color;
      uniform float scale; varying float vA; varying float vR; varying vec3 vC; varying float vD;
      void main(){ vec4 mv = modelViewMatrix*vec4(position,1.); vA = alpha; vR = rot; vC = color; vD = -mv.z;
        gl_PointSize = min(size*scale/max(-mv.z, .1), 1400.); gl_Position = projectionMatrix*mv; vA *= rot > 50. ? 1. : smoothstep(2., 12., -mv.z); }`,   // rot > 50: close-up particle (e.g. your own breath), no near fade
    fragmentShader: `uniform sampler2D map; uniform vec3 fogColor; uniform float fogNear; uniform float fogFar; uniform float light;
      varying float vA; varying float vR; varying vec3 vC; varying float vD;
      void main(){ vec2 p = gl_PointCoord - .5; float cs = cos(vR), sn = sin(vR);
        p = vec2(cs*p.x - sn*p.y, sn*p.x + cs*p.y) + .5;
        vec4 t = texture2D(map, p); float shade = mix(.8, 1.06, 1. - gl_PointCoord.y);
        vec3 col = vC*shade*light; col = mix(col, fogColor, smoothstep(fogNear, fogFar, vD)*.7);
        gl_FragColor = vec4(col, min(t.a*vA, .6)); if (gl_FragColor.a < .003) discard; }`
  });
  const points = new THREE.Points(geo, mat); points.frustumCulled = false; E.scene.add(points);
  const list = [];
  const add = (x, y, z, size, alpha, r, g, b, rot) => { if (alpha > .004 && size > 0) list.push([x, y, z, size, alpha, r, g, b, rot]); };

  // generic emitters: impact clouds, collapse clouds, splashes
  E.emitters.push((t, add, cam) => {
    for (const ev of E.EVENTS) {
      if (ev.t > t || t - ev.t > 5) continue;
      const a = t - ev.t;
      if (ev.kind === 'impact') {
        const n = 5 + Math.round(ev.e * 12), c = E.dustColor || [.7, .64, .56];
        for (let i = 0; i < n; i++) {
          const ang = hash(i, ev.t * 100 | 0) * 6.28, sp = 2 + hash(i, 3) * 4;
          add(ev.x + Math.cos(ang) * sp * Math.sqrt(a), ev.y - .3 + a * .9 + hash(i, 4) * 2, ev.z + Math.sin(ang) * sp * Math.sqrt(a),
            (3 + a * 3) * (.6 + ev.e), smooth(0, .25, a) * (1 - smooth(1.5, 5, a)) * .42, c[0], c[1], c[2], hash(i, 5) * 6);
        }
      } else if (ev.kind === 'splash' && a < 2.5) {
        for (let i = 0; i < 10 + ev.e * 30; i++) {
          const ang = hash(i, ev.t * 100 | 0) * 6.28, sp = (1 + hash(i, 3) * 4) * (.5 + ev.e), up = 7 + hash(i, 6) * 14 * ev.e;
          const ta = Math.max(0, a - hash(i, 7) * .3);
          add(ev.x + Math.cos(ang) * sp * ta * 2, Math.max(ev.y + .3, ev.y + up * ta - 4.9 * ta * ta + .3), ev.z + Math.sin(ang) * sp * ta * 2,
            1 + ta * 3 + ev.e * 1.5, smooth(0, .1, ta) * (1 - smooth(.8, 2.5, ta)) * .32, .88, .92, .93, hash(i, 5) * 6);
        }
      }
    }
    for (const f of E.falls) if (f.at < 1e8 && t > f.at) {
      const a = t - f.at, c = E.dustColor || [.62, .57, .5], big = f.big ?? 1;
      for (let i = 0; i < 46 * big; i++) {
        const ang = hash(i, 7) * 6.28, rr = Math.sqrt(hash(i, 8)) * (f.w * .6 + a * 6 * big);
        add(f.cx + Math.cos(ang) * rr, f.base + hash(i, 9) * f.h * smooth(0, 2.5, a) * .55 + 3, f.cz + Math.sin(ang) * rr,
          (10 + a * 4) * Math.min(1.4, f.w / 16), smooth(0, .8, a) * .5 * (1 - smooth(6, 14, a) * .6), c[0], c[1], c[2], hash(i, 10) * 6);
      }
    }
  });

  return {
    mat,
    render(t, cam) {
      list.length = 0;
      for (const em of E.emitters) em(t, add, cam);
      const cp = cam;
      list.sort((a, b) => ((b[0] - cp.x) ** 2 + (b[1] - cp.y) ** 2 + (b[2] - cp.z) ** 2) - ((a[0] - cp.x) ** 2 + (a[1] - cp.y) ** 2 + (a[2] - cp.z) ** 2));
      const n = Math.min(list.length, MAXP);
      for (let i = 0; i < n; i++) { const p = list[list.length - n + i];
        P.pos.set([p[0], p[1], p[2]], i * 3); P.size[i] = p[3]; P.alpha[i] = p[4]; P.col.set([p[5], p[6], p[7]], i * 3); P.rot[i] = p[8]; }
      geo.setDrawRange(0, n);
      for (const k of ['position', 'color', 'size', 'alpha', 'rot']) geo.attributes[k].needsUpdate = true;
      return n;
    },
  };
}
