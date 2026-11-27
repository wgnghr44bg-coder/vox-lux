// De wereld van de haai-proef: buitenwijk met garage, oprit, stoep, straat, huizen, bomen, lucht en wolken,
// gebouwd met de bouwstenen van de skill (twoTone-materialen, geschilderde texturen, inktlijnen via InkPass),
// plus onze figuren als belichte kaartjes (cardShade) op de NOINK-laag. update(f, cam) zet alles per frame.
import * as THREE from "three";
import { Batch, V, lam, boxGeo, house, quad, tri } from "../bridge/build";
import { ctex, rep, grassHD, cloudHD, stoneHD } from "../bridge/paint";
import { Pen, bodyFront, KID, Outfit, Expr, fxBurst, fxPuff } from "../bridge/toon";
import { LIGHTS, LOOK } from "../bridge/lights";
import { TONE, CHAR, untone } from "../bridge/shade";
import { NOINK } from "../bridge/ink";
import { cardShade, blobMaterial, CARD_K } from "../bridge/cardshade";
import { drawShark, drawBlob, drawSplinters } from "./figures";
import { FPS, shotAt, camAt, sharkAt, KID_IN, KID_OUT, T_DEUR, T_BONK, V3, smooth, clamp01 } from "./story";
import { WORDS } from "./words";

// ---------------- kaartjes ----------------
const texCache = new Map<string, THREE.CanvasTexture>();
const cardTex = (key: string, w: number, h: number, k: number, draw: (p: Pen) => void) => {
  let t = texCache.get(key);
  if (t) return t;
  if (texCache.size > 160) { for (const [kk, tt] of texCache) { tt.dispose(); texCache.delete(kk); if (texCache.size < 80) break; } }
  const cv = document.createElement("canvas"); cv.width = Math.round(w * k); cv.height = Math.round(h * k);
  const g = cv.getContext("2d")!; g.setTransform(k, 0, 0, k, 0, 0); draw(new Pen(g));
  t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
  texCache.set(key, t);
  return t;
};
class Card {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial;
  constructor(parent: THREE.Object3D, w: number, h: number, footY: number, lit = true) {
    const g = new THREE.PlaneGeometry(w, h); g.translate(0, h / 2 - footY, 0);
    this.mat = lit ? cardShade(new THREE.MeshLambertMaterial({ alphaTest: 0.5, side: THREE.DoubleSide }))
      : (new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, toneMapped: true }) as unknown as THREE.MeshLambertMaterial);
    this.mesh = new THREE.Mesh(g, this.mat);
    this.mesh.layers.set(NOINK); this.mesh.renderOrder = lit ? 1 : 2; this.mesh.receiveShadow = lit;
    if (lit) this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    parent.add(this.mesh);
  }
  set(tex: THREE.Texture, pos: V3, cam: THREE.Vector3, mirror = false) {
    this.mat.map = tex; this.mat.needsUpdate = this.mat.userData.t !== tex.uuid ? (this.mat.userData.t = tex.uuid, true) : false;
    this.mesh.position.set(...pos);
    this.mesh.rotation.set(0, Math.atan2(cam.x - pos[0], cam.z - pos[2]), 0);
    this.mesh.scale.x = mirror ? -1 : 1;
    this.mesh.visible = true;
  }
}

const YOU: Outfit = { ...KID, jacket: "#2f80ed", pants: "#2d3142", boots: "#f4f1ea", cap: "#f2c94c", hat: "cap" };
const inWord = (t: number) => WORDS.some(([, a, b, z]) => z === 1 && t >= a + 0.03 && t < b - 0.04 && Math.floor(((t - a) * 9)) % 2 === 0);

// ---------------- texturen ----------------
const concrete = () => ctex("concrete", 1024, 1024, (g, r) => {
  g.fillStyle = "#cfc9bf"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${r() < 0.5 ? "255,255,255" : "70,60,60"},${0.04 + r() * 0.05})`; g.beginPath(); g.arc(r() * 1024, r() * 1024, 4 + r() * 22, 0, 7); g.fill(); }
  g.strokeStyle = "rgba(60,50,60,0.35)"; g.lineWidth = 5; g.beginPath(); g.moveTo(0, 512); g.lineTo(1024, 512); g.moveTo(512, 0); g.lineTo(512, 1024); g.stroke();
});
const floorTex = () => ctex("garfloor", 1024, 1024, (g, r) => {
  g.fillStyle = "#b9b5ae"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(60,55,60,${0.03 + r() * 0.05})`; g.beginPath(); g.arc(r() * 1024, r() * 1024, 4 + r() * 18, 0, 7); g.fill(); }
  g.fillStyle = "rgba(40,35,45,0.25)"; g.beginPath(); g.ellipse(520, 560, 150, 90, 0.3, 0, 7); g.fill(); // olievlek
});
const asphalt = () => ctex("asphalt", 1024, 1024, (g, r) => {
  g.fillStyle = "#62667a"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 1500; i++) { g.fillStyle = `rgba(${r() < 0.5 ? "255,255,255" : "20,20,30"},${0.04 + r() * 0.06})`; g.fillRect(r() * 1024, r() * 1024, 3 + r() * 6, 3 + r() * 6); }
});
const pegboard = () => ctex("peg", 1024, 512, (g) => {
  g.fillStyle = "#d6b98c"; g.fillRect(0, 0, 1024, 512);
  g.fillStyle = "rgba(80,50,30,0.35)"; for (let y = 24; y < 512; y += 40) for (let x = 24; x < 1024; x += 40) { g.beginPath(); g.arc(x, y, 5, 0, 7); g.fill(); }
  g.lineCap = "round"; g.strokeStyle = "#241726"; g.lineWidth = 10;
  const tool = (x: number, col: string, kind: number) => {
    g.fillStyle = col; g.lineWidth = 9;
    if (kind === 0) { g.fillRect(x - 12, 120, 24, 220); g.strokeRect(x - 12, 120, 24, 220); g.fillStyle = "#8a8f9a"; g.fillRect(x - 50, 100, 100, 40); g.strokeRect(x - 50, 100, 100, 40); }
    if (kind === 1) { g.beginPath(); g.moveTo(x, 110); g.lineTo(x, 330); g.stroke(); g.fillStyle = col; g.fillRect(x - 16, 250, 32, 90); g.strokeRect(x - 16, 250, 32, 90); }
    if (kind === 2) { g.beginPath(); g.arc(x, 160, 46, 0.5, 5.8); g.stroke(); g.beginPath(); g.moveTo(x, 200); g.lineTo(x, 340); g.lineWidth = 22; g.strokeStyle = col; g.stroke(); g.strokeStyle = "#241726"; g.lineWidth = 9; }
  };
  [[140, "#e8463a", 0], [300, "#f2c94c", 1], [450, "#2f80ed", 2], [620, "#e8463a", 1], [780, "#27ae60", 0], [920, "#f2994a", 2]].forEach(([x, c, k]) => tool(x as number, c as string, k as number));
});

export class World {
  root = new THREE.Group();
  private sun: THREE.DirectionalLight; private hemi: THREE.HemisphereLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#b8d0ec", 30, 260);
  private door: THREE.Mesh[] = [];
  private clouds: THREE.Mesh[] = [];
  private shark: Card; private sharkBlob: THREE.Mesh; private kid: Card; private kidBlob: THREE.Mesh;
  private fx: Card[] = [];

  constructor() {
    const R = this.root;
    // ---- lucht (5 kleurstops per hoogte, zoals de skill) ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el)); gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    const K = LOOK.day;
    K.sky.c.forEach((h, i) => untone(h, this.skyMat.uniforms["c" + i].value));
    const e = K.sky.e.map((d) => THREE.MathUtils.degToRad(d)); this.skyMat.uniforms.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); R.add(this.sky);
    for (let i = 0; i < 8; i++) {
      const a = -1.2 + i * 0.42, d = 420 + (i % 3) * 50, w = 110 + (i % 4) * 30;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: cloudHD(i % 4, K.cloud), color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      m.position.set(Math.sin(a) * d, 60 + (i % 3) * 28, -Math.cos(a) * d * 0.4 + (i % 2 ? 300 : -300)); m.scale.set(w, w * 0.5, 1);
      m.layers.set(NOINK); m.renderOrder = -0.5; R.add(m); this.clouds.push(m);
    }
    // ---- licht ----
    const L = LIGHTS.day;
    this.hemi = new THREE.HemisphereLight(L.sky, L.ground, L.hemiI);
    this.sun = new THREE.DirectionalLight(L.sunCol, L.sunI); this.sun.castShadow = true; this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...K.bounce); TONE.uSat.value = K.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    untone(L.fog, this.fog.color);

    // ---- grond ----
    const b = new Batch();
    const grass = lam("grassH", () => ({ map: rep(grassHD(), 30, 30) }));
    b.add(quad(V(-150, 0, 150), V(150, 0, 150), V(150, 0, -150), V(-150, 0, -150)), grass);
    const drive = lam("drive", () => ({ map: rep(concrete(), 2, 3) }));
    b.add(boxGeo(V(-2.6, 0, 0), V(2.6, 0.04, 9)), drive);
    const walk = lam("walk", () => ({ map: rep(stoneHD("walkHD", ["#d8d1c4", "#cfc7b9", "#e0d9cc", "#c9c1b3"], "#a59b8b"), 30, 1) }));
    b.add(boxGeo(V(-150, 0, 9), V(150, 0.12, 11)), walk);
    const road = lam("road", () => ({ map: rep(asphalt(), 40, 1) }));
    b.add(boxGeo(V(-150, 0, 11), V(150, 0.02, 19)), road);
    const paint = lam("lines", () => ({ color: "#f4f1ea" }));
    for (let x = -60; x < 60; x += 4) b.add(boxGeo(V(x, 0.02, 14.9), V(x + 2, 0.035, 15.1)), paint);
    b.add(boxGeo(V(-150, 0, 19), V(150, 0.12, 21)), walk);
    // ---- huizen (skill-huizen met reliëf) ----
    house(b, -11.5, -3.6, 0, 10, 8, 5.8, 1, 0);
    house(b, 12.5, -4.2, 0, 11, 8, 5.4, 2, 0);
    house(b, -14, 28, Math.PI, 10, 8, 5.6, 3, 0);
    house(b, 0, 28.5, Math.PI, 11, 8, 6.2, 0, 0);
    house(b, 14, 28, Math.PI, 10, 8, 5.4, 4, 0);
    house(b, 26, -4, 0, 10, 8, 5.8, 5, 0);
    house(b, -26, -4, 0, 10, 8, 5.4, 6, 0);
    // ---- bomen en heggen ----
    const trunk = lam("trunk", () => ({ color: "#8a5a3c" })), leafs = ["#62ae4c", "#56a447", "#72b853"].map((c, i) => lam("leaf" + i, () => ({ color: c })));
    const tree = (x: number, z: number, s: number, k: number) => {
      b.add(new THREE.CylinderGeometry(0.18 * s, 0.26 * s, 2.4 * s, 10).translate(x, 1.2 * s, z), trunk);
      b.add(new THREE.IcosahedronGeometry(1.5 * s, 2).translate(x, 3.1 * s, z), leafs[k % 3]);
      b.add(new THREE.IcosahedronGeometry(1.1 * s, 2).translate(x + 0.9 * s, 2.7 * s, z + 0.3 * s), leafs[(k + 1) % 3]);
      b.add(new THREE.IcosahedronGeometry(1.0 * s, 2).translate(x - 0.8 * s, 2.8 * s, z - 0.2 * s), leafs[(k + 2) % 3]);
    };
    tree(-6.5, 5.5, 1.1, 0); tree(7.5, 6, 1.2, 1); tree(-22, 7, 1.2, 2); tree(20, 7.5, 1.0, 0); tree(-6, 24, 1.1, 1); tree(7, 24, 1.2, 2); tree(-30, 24, 1.3, 0);
    const hedge = lam("hedge", () => ({ color: "#4f9a45" }));
    b.add(boxGeo(V(-6.2, 0, 8.2), V(-3.4, 0.9, 8.9)), hedge); b.add(boxGeo(V(3.4, 0, 8.2), V(6.5, 0.9, 8.9)), hedge);
    // brievenbus
    b.add(boxGeo(V(3.0, 0, 8.4), V(3.12, 1.0, 8.52)), lam("post", () => ({ color: "#5a3b2a" })));
    b.add(boxGeo(V(2.86, 1.0, 8.2), V(3.26, 1.3, 8.75)), lam("mailbox", () => ({ color: "#e8463a" })));
    b.build(R, true);

    // ---- garage (werpt geen schaduw, zodat het binnen licht blijft) ----
    const g = new Batch();
    const wall = lam("garWall", () => ({ color: "#efe2c6" })), trim = lam("garTrim", () => ({ color: "#ffffff" })), roofM = lam("garRoof", () => ({ color: "#c45a46" }));
    const W = 3.6, D = -8.4, H = 3.1;
    g.add(boxGeo(V(-W, 0, D), V(W, 0.03, 0), 0), lam("garFloor", () => ({ map: rep(floorTex(), 2, 2) })));
    g.add(boxGeo(V(-W - 0.2, 0, D - 0.2), V(-W, H, 0)), wall); g.add(boxGeo(V(W, 0, D - 0.2), V(W + 0.2, H, 0)), wall);
    g.add(boxGeo(V(-W - 0.2, 0, D - 0.2), V(W + 0.2, H, D)), wall);
    g.add(boxGeo(V(-W - 0.2, 0, -0.2), V(-1.75, H, 0)), wall); g.add(boxGeo(V(1.75, 0, -0.2), V(W + 0.2, H, 0)), wall);
    g.add(boxGeo(V(-1.75, 2.45, -0.2), V(1.75, H, 0)), wall);
    g.add(boxGeo(V(-1.9, 2.42, 0), V(1.9, 2.58, 0.12)), trim); g.add(boxGeo(V(-1.9, 0, 0), V(-1.75, 2.5, 0.12)), trim); g.add(boxGeo(V(1.75, 0, 0), V(1.9, 2.5, 0.12)), trim);
    // zadeldak
    const rh = 1.4, o = 0.35;
    g.add(quad(V(-W - 0.2 - o, H, 0.35), V(0, H + rh, 0.35), V(0, H + rh, D - 0.55), V(-W - 0.2 - o, H, D - 0.55)), roofM);
    g.add(quad(V(0, H + rh, 0.35), V(W + 0.2 + o, H, 0.35), V(W + 0.2 + o, H, D - 0.55), V(0, H + rh, D - 0.55)), roofM);
    g.add(tri(V(-W - 0.2, H, 0), V(W + 0.2, H, 0), V(0, H + rh, 0)), wall); g.add(tri(V(W + 0.2, H, D - 0.2), V(-W - 0.2, H, D - 0.2), V(0, H + rh, D - 0.2)), wall);
    g.add(boxGeo(V(-W - 0.2, H, D - 0.2), V(W + 0.2, H + 0.08, 0), 0, true), lam("ceil", () => ({ color: "#f6efe0" })));
    // binnen: werkbank, plank met dozen, gereedschapsbord, lamp
    const wood = lam("wood", () => ({ color: "#a8724a" }));
    g.add(boxGeo(V(-3.2, 0.9, D + 0.1), V(0.6, 1.0, D + 0.9)), wood);
    for (const x of [-3.1, 0.45]) g.add(boxGeo(V(x, 0, D + 0.15), V(x + 0.1, 0.9, D + 0.85)), wood);
    g.add(boxGeo(V(-3.2, 1.2, D + 0.02), V(0.6, 2.4, D + 0.06)), lam("peg", () => ({ map: pegboard() })));
    g.add(boxGeo(V(1.4, 1.6, D + 0.1), V(3.5, 1.68, D + 0.7)), wood);
    const boxes = ["#f2c94c", "#e8463a", "#2f80ed", "#c08a5a"];
    [[1.5, 0.55, 0], [2.15, 0.5, 1], [2.75, 0.6, 3], [1.55, 0.45, 2]].forEach(([x, s, k], i) =>
      g.add(boxGeo(V(x, i < 3 ? 1.68 : 0.03, D + 0.15), V(x + s, (i < 3 ? 1.68 : 0.03) + s * 0.8, D + 0.65)), lam("bx" + k, () => ({ color: boxes[k] }))));
    g.add(new THREE.CylinderGeometry(0.4, 0.4, 0.9, 16).translate(3.0, 0.45, D + 0.6), lam("barrel", () => ({ color: "#2f80ed" })));
    g.add(new THREE.CylinderGeometry(0.42, 0.42, 0.06, 16).translate(3.0, 0.92, D + 0.6), lam("barrelTop", () => ({ color: "#1f5fbf" })));
    // band tegen de muur
    g.add(new THREE.TorusGeometry(0.34, 0.13, 10, 20).translate(-3.3, 0.47, -3.0).rotateY(0), lam("tyre", () => ({ color: "#3a3a46" })));
    g.build(R, false);
    const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(3.2, 2.8, 1.8) }));
    bulb.position.set(0, 2.75, -4.2); R.add(bulb);
    const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.7, 6), lam("cord", () => ({ color: "#241726" }))); cord.position.set(0, 3.2, -4.2); R.add(cord);
    // ---- garagedeur: 4 panelen die bij de klap wegvliegen ----
    const doorM = lam("doorPanel", () => ({ map: ctex("doorTex", 512, 128, (gg) => {
      gg.fillStyle = "#f3eee3"; gg.fillRect(0, 0, 512, 128);
      gg.strokeStyle = "rgba(60,50,70,0.35)"; gg.lineWidth = 5; for (let i = 0; i < 4; i++) gg.strokeRect(14 + i * 124, 18, 110, 92);
    }) }));
    for (let i = 0; i < 4; i++) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.6, 0.08), doorM);
      m.castShadow = true; m.receiveShadow = true; R.add(m); this.door.push(m);
    }
    // ---- cast ----
    this.shark = new Card(R, 1100 * 0.0024, 1000 * 0.0024, 25 * 0.0024);
    this.kid = new Card(R, 600 * 0.00175, 1000 * 0.00175, 25 * 0.00175);
    const blobT = cardTex("blob", 600, 200, 1, drawBlob);
    const mkBlob = (w: number) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, w / 3).rotateX(-Math.PI / 2), blobMaterial(blobT)); m.layers.set(NOINK); m.renderOrder = 0.5; R.add(m); return m; };
    this.sharkBlob = mkBlob(2.4); this.kidBlob = mkBlob(0.7);
    for (let i = 0; i < 3; i++) this.fx.push(new Card(R, 1, 1, 0, false));
  }

  update(f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = shotAt(f), c = camAt(f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll ?? 0);
    cam.fov = c.fov; cam.near = 0.1; cam.far = 1200; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    cam.layers.enable(NOINK);
    const look = V(...c.look);
    // zon camera-relatief per shot (skill: az vanaf kijkrichting, el = hoogte), bevroren per shot
    const L = LIGHTS.day, CAM0 = camAt(s.a);
    const fw = V(CAM0.look[0] - CAM0.pos[0], 0, CAM0.look[2] - CAM0.pos[2]).normalize(), rt = V(-fw.z, 0, fw.x);
    const az = THREE.MathUtils.degToRad(s.place === "binnen" ? 140 : 160), el = THREE.MathUtils.degToRad(L.el);
    const dir = fw.clone().multiplyScalar(Math.cos(az)).addScaledVector(rt, Math.sin(az)).multiplyScalar(Math.cos(el)).add(V(0, Math.sin(el), 0)).normalize();
    this.sun.position.copy(look).addScaledVector(dir, 120); this.sun.target.position.copy(look);
    const sc = this.sun.shadow.camera, Rr = 22; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 10; sc.far = 300; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * 2;
    this.sky.position.copy(cam.position);
    this.fog.near = L.fogNear; this.fog.far = L.fogFar; scene.fog = this.fog; scene.background = null;
    for (const m of this.clouds) m.lookAt(cam.position.x, m.position.y, cam.position.z);

    // ---- deur ----
    const shakeK = T_BONK.reduce((a, tb) => a + Math.max(0, 1 - Math.abs(t - tb - 0.05) / 0.18), 0);
    this.door.forEach((m, i) => {
      const y0 = 0.33 + i * 0.6;
      if (t < T_DEUR) {
        m.position.set(0, y0, -0.06 + Math.sin(t * 90 + i) * 0.03 * shakeK + shakeK * 0.05); m.rotation.set(shakeK * 0.03 * (i % 2 ? 1 : -1), 0, 0);
      } else {
        const u = Math.min(t - T_DEUR, 1.5), side = [-1.3, 1.2, -1.0, 1.4][i];
        const vx = side * 2.4, vy = 1.4 + i * 0.5, vz = 3.6 - i * 0.4;
        const tl = (vy + Math.sqrt(vy * vy + 2 * 4.9 * 2 * (y0 - 0.05))) / (2 * 4.9); // landt op de grond
        const k = Math.min(u, tl), land = u >= tl;
        m.position.set(vx * k, land ? 0.05 + i * 0.02 : y0 + vy * k - 4.9 * k * k, 0.2 + vz * k);
        const spin = smooth(k / tl);
        m.rotation.set(-spin * Math.PI / 2, side * 0.25 * spin, land ? 0 : side * k * 1.4);
      }
    });

    // ---- haai ----
    const sh = sharkAt(t);
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const mv = V(...sh.dir);
    const mirror = mv.dot(right) < -0.05 || (Math.abs(mv.dot(right)) <= 0.05 && false);
    const arm = s.id === 3 ? 0.5 + 0.5 * Math.sin(t * 14) : 0.15 + 0.1 * Math.sin(t * 3);
    const look2 = s.id === 4 ? "dumb" : s.id === 6 && t > T_DEUR ? "happy" : "dumb";
    const blink = (t % 2.6) > 2.45 && s.id !== 4 && s.id !== 1 ? 1 : 0;
    const squash = shakeK > 0.3 && t < T_DEUR ? 0.4 : 0;
    const ph = Math.round(sh.phase * 24) / 24, wq = Math.round(sh.walk * 10) / 10, aq = Math.round(arm * 12) / 12;
    const close = s.id >= 2 && s.id <= 4 ? 2 : 1.3;
    const sT = cardTex(`shark|${ph}|${wq}|${aq}|${look2}|${blink}|${squash}|${close}`, 1100, 1000, close, (p) => drawShark(p, { phase: ph, walk: wq, arm: aq, look: look2 as any, blink, squash }));
    const showShark = !(s.id === 6 && t < T_DEUR - 0.05);
    this.shark.set(sT, sh.pos, cam.position, mirror);
    this.shark.mesh.visible = showShark;
    this.sharkBlob.position.set(sh.pos[0] + 0.15, 0.05, sh.pos[2]); this.sharkBlob.visible = showShark;
    this.sharkBlob.rotation.y = Math.atan2(cam.position.x - sh.pos[0], cam.position.z - sh.pos[2]);

    // ---- kind ("jij") ----
    const kidPos = s.place === "binnen" ? KID_IN : KID_OUT;
    const talking = s.id === 5 && inWord(t);
    let expr: Expr = s.id === 5 ? (talking ? "relief_open" : "smile_closed") : t > T_DEUR ? "shock" : t > T_BONK[0] ? "nervous" : "neutral";
    const facing = s.id === 5 ? -1 : 1;
    const kT = cardTex(`kid|${expr}|${facing}|${(t % 3.1) > 2.95 ? 1 : 0}`, 600, 1000, 1.6, (p) => bodyFront(p, YOU, { mode: "stand", expr, facing: facing as -1 | 1, blink: (t % 3.1) > 2.95, light: -2.1, seed: 3, wave: s.id === 5 && t > 6.2 && t < 7.0 ? 1 : 0 }));
    this.kid.set(kT, kidPos, cam.position, false);
    this.kid.mesh.visible = s.id === 5 || s.id === 6;
    this.kidBlob.position.set(kidPos[0], 0.05, kidPos[2]); this.kidBlob.visible = this.kid.mesh.visible;

    // ---- effecten bij de klap ----
    this.fx.forEach((x) => (x.mesh.visible = false));
    const u = (t - T_DEUR) / 0.6;
    if (u >= 0 && u < 1) {
      const bt = cardTex(`burst|${Math.round(u * 20)}`, 500, 500, 1.2, (p) => fxBurst(p, Math.round(u * 20) / 20, "#fff3b0", 12, 50, 240));
      this.fx[0].set(bt, [0, 0.0, 0.35], cam.position); this.fx[0].mesh.scale.set(3.6, 3.6, 1); this.fx[0].mesh.position.y = -0.2;
      const st = cardTex(`spl|${Math.round(u * 20)}`, 800, 800, 1, (p) => drawSplinters(p, Math.round(u * 20) / 20));
      this.fx[1].set(st, [0, 0.0, 0.5], cam.position); this.fx[1].mesh.scale.set(3.2, 3.2, 1); this.fx[1].mesh.position.y = -0.1;
    }
    const pu = (t - T_DEUR - 0.1) / 1.1;
    if (pu >= 0 && pu < 1) {
      const pt = cardTex(`puff|${Math.round(pu * 20)}`, 300, 300, 2, (p) => fxPuff(p, Math.round(pu * 20) / 20));
      this.fx[2].set(pt, [0.3, 0, 0.9], cam.position); this.fx[2].mesh.scale.set(4.5, 4.5, 1); this.fx[2].mesh.position.y = -0.6;
    }
    return look;
  }
}
