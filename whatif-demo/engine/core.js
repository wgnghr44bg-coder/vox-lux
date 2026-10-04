// Shared 3D core: renderer, sky, light, materials, facades and the registry that places fill
// (what can bend, break, fall, float, light up or freeze) and forces act on.
import * as THREE from 'three';
import { rng, hash } from './util.js';

export const W = 720, H = 1280, FPS = 30;

export function createEngine() {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H); renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
  document.body.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, W / H, 0.3, 5000);
  scene.fog = new THREE.Fog(0xcfdce4, 120, 900);

  const skyMat = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() },
                sunDir: { value: new THREE.Vector3(0, 1, 0) }, sunCol: { value: new THREE.Color(0) }, stars: { value: 0 }, sunSize: { value: 1 } },
    vertexShader: `varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader: `uniform vec3 top; uniform vec3 hor; uniform vec3 sunDir; uniform vec3 sunCol; uniform float stars; uniform float sunSize; varying vec3 vP;
      float h21(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      void main(){ float h = clamp(vP.y*2.0, 0., 1.); vec3 c = mix(hor, top, pow(h, .6));
        float s = max(dot(normalize(vP), normalize(sunDir)), 0.); float r = .018 * sunSize; c += vec3(1., .55, .2) * smoothstep(cos(r * 1.5), cos(r * 1.05), s) * min(1., (sunSize - 1.) / 2.) * .6; c += sunCol * (smoothstep(cos(r * 1.15), cos(r), s) * 2.5 + pow(s, 12. * sunSize) * .25 + pow(s, 2500. / (sunSize * sunSize)) * .5 * min(1., (sunSize - 1.) / 3.));
        if (stars > 0.) { vec2 g = floor(vec2(atan(vP.z, vP.x) * 260., vP.y * 420.)); float r = h21(g);
          c += vec3(.85, .88, .95) * step(.9965, r) * stars * smoothstep(.02, .25, vP.y); }
        gl_FragColor = vec4(c, 1.); }`
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(4000, 32, 16), skyMat);
  scene.add(sky);
  const hemi = new THREE.HemisphereLight(0xe3ecf4, 0x5a5448, 1.5);
  const sun = new THREE.DirectionalLight(0xffeedd, 2.4);
  sun.position.set(-90, 110, 120); sun.target.position.set(0, 0, -40);
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -110, right: 110, top: 110, bottom: -110, near: 10, far: 900 });
  sun.shadow.bias = -0.0008;
  scene.add(hemi, sun, sun.target);

  const lam = (color, o = {}) => new THREE.MeshLambertMaterial({ color, flatShading: true, ...o });
  const shadowed = (m, cast = true) => { m.castShadow = cast; m.receiveShadow = true; return m; };
  const add = (m, parent = scene) => { parent.add(m); return m; };

  // ---------- facades ----------
  function facadeTex(base, kind) {
    const cv = document.createElement('canvas'); cv.width = 64; cv.height = 64;
    const x = cv.getContext('2d');
    const c = new THREE.Color(base), hex = k => '#' + c.clone().multiplyScalar(k).getHexString();
    if (!kind.endsWith('Glow')) { x.fillStyle = hex(1); x.fillRect(0, 0, 64, 64); x.fillStyle = hex(.82); x.fillRect(0, 60, 64, 4); }
    const glow = kind.endsWith('Glow'); if (glow) kind = kind.slice(0, -4);
    const glass = glow ? '#f0c27a' : { win: '#46555f', broken: '#101010', dark: '#1d2328' }[kind] || '#46555f';
    if (glow) { x.fillStyle = '#000'; x.fillRect(0, 0, 64, 64); }
    if (kind === 'shop') {
      x.fillStyle = '#2f3a42'; x.fillRect(4, 10, 56, 44); x.fillStyle = '#56656e'; x.fillRect(4, 10, 56, 6);
    } else if (kind === 'tower') {
      x.fillStyle = glow ? '#c9a066' : '#5b6b78'; for (let i = 0; i < 4; i++) x.fillRect(2 + i * 16, 12, 12, 40);
    } else if (kind === 'chalet') {             // timber with small windows
      x.fillStyle = hex(.86); for (let i = 0; i < 64; i += 8) x.fillRect(0, i, 64, 1);
      if (glow) { x.fillStyle = '#000'; x.fillRect(0, 0, 64, 64); }
      x.fillStyle = glass; x.fillRect(22, 18, 20, 24); x.fillStyle = glow ? '#000' : hex(.6); x.fillRect(31, 18, 2, 24);
    } else {
      if (!glow) { x.fillStyle = hex(1.12); x.fillRect(14, 48, 36, 4); }
      x.fillStyle = glass; x.fillRect(16, 14, 32, 34);
      if (glow) { x.fillStyle = '#000'; x.fillRect(31, 14, 2, 34); }
      if (kind === 'broken') { x.fillStyle = '#46555f'; x.beginPath(); x.moveTo(16, 14); x.lineTo(30, 14); x.lineTo(16, 30); x.fill(); }
      else if (kind === 'win' && !glow) { x.fillStyle = '#5d6d77'; x.fillRect(16, 14, 32, 8); x.fillStyle = hex(.9); x.fillRect(31, 14, 2, 34); }
      else if (!glow) { x.fillStyle = hex(.9); x.fillRect(31, 14, 2, 34); }
    }
    const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 4; return t;
  }
  const matCache = {};
  function facadeMats(color, kind = 'win', roof) {
    const key = color + kind + (roof ?? '');
    if (!matCache[key]) {
      const side = lam(0xffffff, { map: facadeTex(color, kind) }), top = lam(roof ?? new THREE.Color(color).multiplyScalar(.75));
      matCache[key] = [side, side, top, top, side, side];
      frost.push(side, top);
      if (kind === 'win' || kind === 'chalet' || kind === 'tower') {      // windows glow in the dark (E.night)
        side.emissive = new THREE.Color(0xffffff); side.emissiveMap = facadeTex(color, kind + 'Glow'); side.emissiveIntensity = 0;
        side.emissiveMap.wrapS = side.emissiveMap.wrapT = THREE.RepeatWrapping; windowMats.push(side);
      }
    }
    return matCache[key];
  }
  function facadeBox(w, h, d, bay = 5, storey = 3.5) {
    const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv;
    const rep = [[d / bay, h / storey], [d / bay, h / storey], [1, 1], [1, 1], [w / bay, h / storey], [w / bay, h / storey]];
    for (let f = 0; f < 6; f++) for (let i = 0; i < 4; i++) { const k = f * 4 + i; uv.setXY(k, uv.getX(k) * rep[f][0], uv.getY(k) * rep[f][1]); }
    return g;
  }

  // ---------- instanced debris pools ----------
  const DUMMY = new THREE.Object3D();
  function instanced(geo, mat, n) {
    const im = new THREE.InstancedMesh(geo, mat, n); im.castShadow = true; im.receiveShadow = true;
    im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); im.frustumCulled = false; im.count = n; scene.add(im); im.used = 0;
    for (let i = 0; i < n; i++) { DUMMY.scale.set(0, 0, 0); DUMMY.updateMatrix(); im.setMatrixAt(i, DUMMY.matrix); }
    return im;
  }
  const IM = {
    paper: instanced(new THREE.PlaneGeometry(.45, .6), new THREE.MeshLambertMaterial({ color: 0xe6e1d6, side: THREE.DoubleSide }), 80),
    leaf: instanced(new THREE.CircleGeometry(.12, 3), new THREE.MeshLambertMaterial({ color: 0x6d7a45, side: THREE.DoubleSide }), 120),
    shard: instanced(new THREE.CircleGeometry(.35, 3), new THREE.MeshLambertMaterial({ color: 0x9fb0b9, side: THREE.DoubleSide }), 300),
    chunk: instanced(new THREE.BoxGeometry(1, 1, 1), lam(0xffffff), 420),
  };
  const slot = (im, scale = 1, color) => { if (im.used >= im.count) return null; const i = im.used++;
    if (color !== undefined) im.setColorAt(i, new THREE.Color(color)); return { im, i, scale }; };

  // ---------- registry ----------
  const frost = [];               // materials that frost over in the cold
  const windowMats = [];          // facade materials whose windows light up in the dark
  const E = {
    THREE, W, H, FPS, renderer, scene, camera, sky, skyMat, hemi, sun, lam, shadowed, add, rng, hash,
    facadeTex, facadeMats, facadeBox, IM, slot, DUMMY,
    PALETTE: [0x9c4a3a, 0xc9b896, 0x7a5a44, 0x8e8e8a, 0xc4a85a, 0xb5653f, 0xd2c6ae, 0x6f6a64],
    TOWER_PAL: [0xb9bcbc, 0xa7a49b, 0xc9c1ae, 0x8f969b, 0xd0cdc4],
    bodies: [],          // simulated debris / vehicles (physics.js)
    bend: [],            // { pose(t, F) } things that bend or sag
    breaks: [],          // { src, strength, ...body params } things that break off
    falls: [],           // { g, h, w, cx, cz, strength, dir } structures that can collapse
    floods: [],          // { mesh, y } water surfaces that rise or fall with the water force
    lights: [],          // { mat, on: color, off: color, at } lamps that light up in the dark
    windowMats,          // facade materials with glowing windows (emissiveIntensity follows the dark)
    frost,               // materials that frost over
    melt: [],            // snow that melts in the heat: { mat, bare } (colour) or { mesh, to } (shrinks)
    people: [],          // { update(t, F) }
    updates: [],         // per-frame place callbacks (t, F)
    emitters: [],        // dust/snow/spray emitters (t, add, cam)
    EVENTS: [],          // sound + shake cues
  };
  E.body = o => { const b = Object.assign({ k: .05, lift: 0, mu: .6, bounce: .25, spin: .3, heavy: 0, hx: .5, hy: .5, hz: .5,
    tRel: 1e9, v0: [0, 0, 0], hidden: false, p: [0, 0, 0], r: [0, 0, 0], density: 2.5 }, o); E.bodies.push(b); return b; };
  // a piece that breaks off an existing mesh: the body starts at the mesh's world pose at release time
  E.part = (src, o) => { const m = src.clone(); m.visible = false; scene.add(m);
    return E.body({ kind: 'part', obj: m, src, hidden: true, ...o }); };
  E.groundAt = () => 0;            // place may override (river bed, slopes)
  E.collide = null;                // place may add walls: (p, v) => void
  return E;
}
