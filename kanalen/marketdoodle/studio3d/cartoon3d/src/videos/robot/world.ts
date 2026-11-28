// De wereld van de robotbutler: woonkamer met kerstboom en open haard, keuken, besneeuwde tuin met het huis van de buren.
// Rijker dan de haai (eigenaar 28 nov: "meer details, betere achtergronden"): Kenney-meubels (CC0), lichtsnoeren met
// gloeiende lampjes (bloom), ramen met sneeuw, plafond met lamp. Mensen zijn de bean-head-kaartjes van de eerste 3D-haai.
import * as THREE from "three";
import { Batch, V, lam, boxGeo, quad, tri } from "../bridge/build";
import { ctex, rep, cloudHD } from "../bridge/paint";
import { Pen, bodyFront, KID, PARENT, Outfit, Expr, fxBurst, fxPuff, fxStars, LIP } from "../bridge/toon";
import { LIGHTS, LOOK } from "../bridge/lights";
import { TONE, CHAR, untone } from "../bridge/shade";
import { NOINK } from "../bridge/ink";
import { cardShade, blobMaterial, CARD_K } from "../bridge/cardshade";
import { drawBlob } from "../haai/figures";
import { mondOp } from "./lipsync";
import { zet, los, KIT } from "./kenney";
import { Robot } from "./robotbouw";
import { castAt, SC } from "./cast";
import {
  FPS, shotAt, camAt, robotAt, doosAt, T, KX, BX, V3, smooth, clamp01, KAMER, DAD_K, BUUR, ONS, KICKS,
} from "./story";

// ---------------- kaartjes (zoals de eerste 3D-haai) ----------------
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
const O_YOU: Outfit = { ...KID, jacket: "#d6453d", pants: "#2d3142", boots: "#f4f1ea", cap: "#2f80ed", hat: "cap" };
const O_SIS: Outfit = { jacket: "#e85d9a", pants: "#2d3142", boots: "#f4f1ea", hat: "hair", hair: "#7a4a2a", dress: "#e85d9a", build: "kid", skin: "#f5c9a0" };
const O_DAD: Outfit = { ...PARENT, jacket: "#3c8d5a", moustache: "#5a3b2a", build: "stout" };
const O_MOM: Outfit = { ...PARENT, jacket: "#9b5ac9", dress: "#9b5ac9", hair: "#a0522d", skin: "#f5c9a0" };

// ---------------- texturen ----------------
const planken = () => ctex("rbPlank", 1024, 1024, (g, r) => {
  for (let i = 0; i < 8; i++) { const c = ["#c48a5a", "#b97f50", "#cf9563", "#bd8455"][i % 4]; g.fillStyle = c; g.fillRect(0, i * 128, 1024, 128);
    for (let k = 0; k < 30; k++) { g.fillStyle = `rgba(90,50,30,${0.05 + r() * 0.07})`; g.fillRect(r() * 1024, i * 128 + r() * 128, 60 + r() * 200, 2 + r() * 3); }
    g.fillStyle = "rgba(70,40,25,0.55)"; g.fillRect(0, i * 128, 1024, 4); const x = ((i * 389) % 1024); g.fillRect(x, i * 128, 4, 128); }
});
const behang = () => ctex("rbBehang", 512, 512, (g) => {
  g.fillStyle = "#f3e3c4"; g.fillRect(0, 0, 512, 512);
  g.fillStyle = "#ead3ab"; for (let x = 0; x < 512; x += 64) g.fillRect(x, 0, 26, 512);
  g.fillStyle = "rgba(196,70,60,0.35)"; for (let y = 32; y < 512; y += 128) for (let x = 45; x < 512; x += 128) { g.beginPath(); g.arc(x, y, 7, 0, 7); g.fill(); g.beginPath(); g.arc(x + 64, y + 64, 7, 0, 7); g.fill(); }
});
const raam = (nacht: boolean) => ctex("rbRaam" + nacht, 512, 640, (g, r) => {
  const gr = g.createLinearGradient(0, 0, 0, 640);
  if (nacht) { gr.addColorStop(0, "#14204a"); gr.addColorStop(1, "#3c4f86"); } else { gr.addColorStop(0, "#7fb2ea"); gr.addColorStop(1, "#dfeefb"); }
  g.fillStyle = gr; g.fillRect(0, 0, 512, 640);
  g.fillStyle = nacht ? "#2a3a62" : "#e9f1f8"; g.beginPath(); g.ellipse(130, 640, 260, 150, 0, 0, 7); g.fill(); g.beginPath(); g.ellipse(430, 650, 240, 170, 0, 0, 7); g.fill();
  const boom = (x: number, s: number) => { g.fillStyle = nacht ? "#1d3a3a" : "#3f7d5a"; for (let k = 0; k < 3; k++) { g.beginPath(); g.moveTo(x, 360 - 60 * s * k); g.lineTo(x - 55 * s + k * 10, 470 - 60 * s * k); g.lineTo(x + 55 * s - k * 10, 470 - 60 * s * k); g.fill(); }
    g.fillStyle = nacht ? "#d0dcf2" : "#ffffff"; g.beginPath(); g.moveTo(x, 360 - 120 * s); g.lineTo(x - 18 * s, 395 - 120 * s); g.lineTo(x + 18 * s, 395 - 120 * s); g.fill(); };
  boom(90, 1.1); boom(400, 1.3); boom(250, 0.8);
  g.fillStyle = nacht ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.9)"; for (let i = 0; i < 70; i++) { g.beginPath(); g.arc(r() * 512, r() * 640, 2 + r() * 4, 0, 7); g.fill(); }
  if (nacht) { g.fillStyle = "#fff6c8"; g.beginPath(); g.arc(400, 110, 34, 0, 7); g.fill(); }
});
const tegels = () => ctex("rbTegel", 512, 512, (g) => {
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = (x + y) % 2 ? "#f4f1ea" : "#c9473f"; g.fillRect(x * 64, y * 64, 64, 64); }
});
const wandtegel = () => ctex("rbWandtegel", 512, 256, (g) => {
  g.fillStyle = "#e6f1ee"; g.fillRect(0, 0, 512, 256); g.strokeStyle = "#b9d3cc"; g.lineWidth = 4;
  for (let y = 0; y <= 256; y += 32) { g.beginPath(); g.moveTo(0, y); g.lineTo(512, y); g.stroke(); }
  for (let y = 0; y < 256; y += 32) for (let x = (y / 32) % 2 ? 32 : 0; x <= 512; x += 64) { g.beginPath(); g.moveTo(x, y); g.lineTo(x, y + 32); g.stroke(); }
});
const sneeuw = () => ctex("rbSneeuw", 1024, 1024, (g, r) => {
  g.fillStyle = "#f2f6fb"; g.fillRect(0, 0, 1024, 1024);
  for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(${r() < 0.5 ? "255,255,255" : "150,170,210"},${0.05 + r() * 0.08})`; g.beginPath(); g.ellipse(r() * 1024, r() * 1024, 10 + r() * 50, 4 + r() * 14, 0, 0, 7); g.fill(); }
});
const baksteen = () => ctex("rbSteen", 512, 512, (g, r) => {
  g.fillStyle = "#e8dccd"; g.fillRect(0, 0, 512, 512);
  for (let y = 0; y < 16; y++) for (let x = -1; x < 9; x++) { g.fillStyle = ["#b5543c", "#a84b36", "#c25f45", "#9c4532"][(x * 7 + y * 3 + 16) % 4]; g.fillRect(x * 64 + (y % 2) * 32 + 3, y * 32 + 3, 58, 26); }
});
const gevel = (kleur: string, deur: string) => ctex("rbGevel" + kleur, 1024, 640, (g) => {
  g.fillStyle = kleur; g.fillRect(0, 0, 1024, 640);
  g.fillStyle = "rgba(0,0,0,0.06)"; for (let y = 0; y < 640; y += 40) g.fillRect(0, y, 1024, 5);
  const win = (x: number, y: number) => { g.fillStyle = "#ffffff"; g.fillRect(x - 8, y - 8, 196, 176); g.fillStyle = "#ffe7a3"; g.fillRect(x, y, 180, 160); g.strokeStyle = "#ffffff"; g.lineWidth = 12; g.beginPath(); g.moveTo(x + 90, y); g.lineTo(x + 90, y + 160); g.moveTo(x, y + 80); g.lineTo(x + 180, y + 80); g.stroke(); };
  win(90, 200); win(754, 200); g.fillStyle = "#ffffff"; g.fillRect(412, 250, 200, 390); g.fillStyle = deur; g.fillRect(426, 264, 172, 376);
  g.fillStyle = "#f2c94c"; g.beginPath(); g.arc(570, 460, 12, 0, 7); g.fill();
  g.fillStyle = "#3f7d5a"; g.beginPath(); g.arc(512, 330, 44, 0, 7); g.fill(); g.fillStyle = deur; g.beginPath(); g.arc(512, 330, 22, 0, 7); g.fill();
});

// lampjes: één InstancedMesh met gloeiende bolletjes (kleuren > 1 -> bloom)
const KLEUR = [[4, 0.6, 0.5], [0.6, 3.2, 0.8], [0.6, 1.2, 4.2], [4, 3.0, 0.6], [3.6, 0.8, 3.0]];
class Lampjes {
  mesh: THREE.InstancedMesh; n = 0; private aan: number[] = []; private c = new THREE.Color();
  constructor(parent: THREE.Object3D, max: number, r = 0.035) {
    this.mesh = new THREE.InstancedMesh(new THREE.SphereGeometry(r, 10, 8), new THREE.MeshBasicMaterial({ color: "#ffffff" }), max);
    this.mesh.layers.set(NOINK); this.mesh.count = 0; this.mesh.frustumCulled = false; parent.add(this.mesh);
  }
  zet(p: V3, groep: number) {
    const m = new THREE.Matrix4().setPosition(p[0], p[1], p[2]); this.mesh.setMatrixAt(this.n, m);
    this.aan.push(groep); this.n++; this.mesh.count = this.n;
  }
  /** aan(groep) -> 0..1 helderheid per groep */
  update(t: number, aan: (g: number) => number) {
    for (let i = 0; i < this.n; i++) {
      const k = KLEUR[i % KLEUR.length], a = aan(this.aan[i]), knip = 0.75 + 0.25 * Math.sin(t * 5 + i * 1.7);
      const f = a > 0 ? a * knip : 0.18;
      this.c.setRGB(a > 0 ? k[0] * f : 0.35 + k[0] * 0.05, a > 0 ? k[1] * f : 0.35 + k[1] * 0.05, a > 0 ? k[2] * f : 0.38 + k[2] * 0.05);
      this.mesh.setColorAt(i, this.c);
    }
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;
  }
}

export class World {
  root = new THREE.Group();
  private sun: THREE.DirectionalLight; private hemi: THREE.HemisphereLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#dfe9f5", 30, 260);
  private clouds: THREE.Mesh[] = [];
  private robot: Robot;
  private people: [Card, THREE.Mesh][] = [];
  private fx: Card[] = [];
  private lampjes: Lampjes;
  private boomKaal!: THREE.Object3D; private boomVol!: THREE.Object3D;
  private koekjes!: THREE.InstancedMesh; private koekPos: { p: V3; r: number; t: number }[] = [];
  private eenKoek!: THREE.Object3D;
  private berg!: THREE.Mesh; private ballen!: THREE.InstancedMesh; private vlokken!: THREE.Points;
  private cadeaus: THREE.Object3D[] = []; private doos = new THREE.Group(); private deksel = new THREE.Group();
  private vuur!: THREE.Mesh; private plafondLamp!: THREE.Mesh;

  constructor() {
    const R = this.root;
    // ---- lucht (alleen in de tuin te zien) ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() }, c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el)); c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el)); c = mix(c, c4, smoothstep(e.z, e.w, el)); gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    ["#e4edf7", "#cfe0f3", "#a9c8ec", "#86b1e4", "#5f95da"].forEach((h, i) => untone(h, this.skyMat.uniforms["c" + i].value));
    this.skyMat.uniforms.e.value.set(...[3, 8, 16, 40].map((d) => THREE.MathUtils.degToRad(d)) as [number, number, number, number]);
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(900, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK); R.add(this.sky);
    for (let i = 0; i < 6; i++) {
      const a = -1.0 + i * 0.4, d = 420 + (i % 3) * 50, w = 120 + (i % 4) * 30;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: cloudHD(i % 4, LOOK.day.cloud), color: new THREE.Color(1.1, 1.1, 1.12), transparent: true, depthWrite: false, fog: false }));
      m.position.set(BX + Math.sin(a) * d, 70 + (i % 3) * 25, -Math.cos(a) * d); m.scale.set(w, w * 0.5, 1);
      m.layers.set(NOINK); m.renderOrder = -0.5; R.add(m); this.clouds.push(m);
    }
    // ---- licht ----
    const L = LIGHTS.day;
    this.hemi = new THREE.HemisphereLight(L.sky, L.ground, L.hemiI);
    this.sun = new THREE.DirectionalLight(L.sunCol, L.sunI); this.sun.castShadow = true; this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    this.lampjes = new Lampjes(R, 700);
    this.robot = new Robot(R);
    // ---- cast ----
    const blobT = cardTex("blob", 600, 200, 1, drawBlob);
    const mkBlob = (w: number) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, w / 3).rotateX(-Math.PI / 2), blobMaterial(blobT)); m.layers.set(NOINK); m.renderOrder = 0.5; R.add(m); return m; };
    ["you", "sis", "dad", "mom"].forEach((n) => { const sc = SC[n]; this.people.push([new Card(R, 600 * sc, 1000 * sc, 25 * sc), mkBlob(0.7)]); });
    for (let i = 0; i < 4; i++) this.fx.push(new Card(R, 1, 1, 0, false));
    this.kamer(R); this.keuken(R); this.tuin(R);
  }

  // ---------------- woonkamer ----------------
  private kamer(R: THREE.Object3D) {
    const b = new Batch(), binnen = new Batch(), H = 2.8, X0 = -4, X1 = 4, Z0 = -3.5, Z1 = 5.5;
    binnen.add(boxGeo(V(X0, 0, Z0), V(X1, 0.02, Z1)), lam("rbVloer", () => ({ map: rep(planken(), 3, 3) })));
    const wand = lam("rbWand", () => ({ map: rep(behang(), 6, 2) })), plint = lam("rbPlint", () => ({ color: "#ffffff" }));
    binnen.add(boxGeo(V(X0 - 0.2, 0, Z0 - 0.2), V(X1 + 0.2, H, Z0)), wand);
    binnen.add(boxGeo(V(X0 - 0.2, 0, Z0), V(X0, H, Z1)), wand); binnen.add(boxGeo(V(X1, 0, Z0), V(X1 + 0.2, H, Z1)), wand);
    binnen.add(boxGeo(V(X0, 0, Z0), V(X1, 0.12, Z0 + 0.03)), plint); binnen.add(boxGeo(V(X0, 0, Z0), V(X0 + 0.03, 0.12, Z1)), plint); binnen.add(boxGeo(V(X1 - 0.03, 0, Z0), V(X1, 0.12, Z1)), plint);
    binnen.add(boxGeo(V(X0, H - 0.12, Z0), V(X1, H, Z0 + 0.06)), plint);
    binnen.add(boxGeo(V(X0 - 0.2, H, Z0 - 0.2), V(X1 + 0.2, H + 0.1, Z1), 0, true), lam("rbPlafond", () => ({ color: "#fbf4e6" })));
    // ramen met sneeuwuitzicht + gordijnen
    const ramen: [number, number][] = [[-0.9, 1.1], [2.1, 1.1]];
    for (const [x, w] of ramen) {
      b.add(boxGeo(V(x - w / 2, 0.95, Z0 + 0.01), V(x + w / 2, 2.25, Z0 + 0.02)), lam("rbRaamDag", () => ({ map: raam(false) })));
      const kozijn = lam("rbKozijn", () => ({ color: "#ffffff" }));
      binnen.add(boxGeo(V(x - w / 2 - 0.08, 0.87, Z0), V(x + w / 2 + 0.08, 0.95, Z0 + 0.16)), kozijn);
      binnen.add(boxGeo(V(x - w / 2 - 0.08, 2.25, Z0), V(x + w / 2 + 0.08, 2.32, Z0 + 0.06)), kozijn);
      binnen.add(boxGeo(V(x - w / 2 - 0.08, 0.95, Z0), V(x - w / 2, 2.25, Z0 + 0.06)), kozijn); binnen.add(boxGeo(V(x + w / 2, 0.95, Z0), V(x + w / 2 + 0.08, 2.25, Z0 + 0.06)), kozijn);
      binnen.add(boxGeo(V(x - 0.025, 0.95, Z0), V(x + 0.025, 2.25, Z0 + 0.05)), kozijn); binnen.add(boxGeo(V(x - w / 2, 1.58, Z0), V(x + w / 2, 1.62, Z0 + 0.05)), kozijn);
      const gordijn = lam("rbGordijn", () => ({ color: "#b8313a" }));
      binnen.add(boxGeo(V(x - w / 2 - 0.42, 0.6, Z0 + 0.05), V(x - w / 2 - 0.08, 2.45, Z0 + 0.16)), gordijn);
      binnen.add(boxGeo(V(x + w / 2 + 0.08, 0.6, Z0 + 0.05), V(x + w / 2 + 0.42, 2.45, Z0 + 0.16)), gordijn);
      binnen.add(new THREE.CylinderGeometry(0.025, 0.025, w + 1.1, 8).rotateZ(Math.PI / 2).translate(x, 2.5, Z0 + 0.12), lam("rbRail", () => ({ color: "#8a5a3c" })));
    }
    // open haard op de linkerwand met kousen
    const steen = lam("rbHaard", () => ({ map: rep(baksteen(), 2, 2) })), schouw = lam("rbSchouw", () => ({ color: "#f3efe6" }));
    binnen.add(boxGeo(V(X0, 0, -0.2), V(X0 + 0.45, 1.25, 1.6)), steen);
    binnen.add(boxGeo(V(X0, 1.25, -0.35), V(X0 + 0.6, 1.36, 1.75)), schouw);
    binnen.add(boxGeo(V(X0 + 0.44, 0.12, 0.25), V(X0 + 0.47, 0.8, 1.15)), lam("rbGat", () => ({ color: "#1d1416" })));
    this.vuur = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.45), new THREE.MeshBasicMaterial({ map: ctex("rbVuur", 256, 160, (g) => {
      const gr = g.createRadialGradient(128, 160, 10, 128, 150, 140); gr.addColorStop(0, "#fff5b0"); gr.addColorStop(0.4, "#ffae3c"); gr.addColorStop(1, "rgba(220,60,30,0)");
      g.fillStyle = gr; g.beginPath(); g.moveTo(10, 160); g.quadraticCurveTo(40, 40, 80, 90); g.quadraticCurveTo(110, 0, 140, 70); g.quadraticCurveTo(190, 20, 200, 100); g.quadraticCurveTo(230, 70, 246, 160); g.fill(); }),
      color: new THREE.Color(2.2, 1.8, 1.4), transparent: true, depthWrite: false }));
    this.vuur.position.set(X0 + 0.49, 0.36, 0.7); this.vuur.rotation.y = Math.PI / 2; this.vuur.layers.set(NOINK); R.add(this.vuur);
    ["sock-red", "sock-green-cane", "sock-red-cane"].forEach((n, i) => zet(b, n, X0 + 0.66, 0.85, -0.05 + i * 0.6, 0.42, Math.PI / 2));
    zet(b, "lantern", X0 + 0.35, 1.36, -0.15, 0.3); zet(b, "nutcracker", X0 + 0.32, 1.36, 1.6, 0.45, Math.PI / 2);
    zet(b, "wreath-decorated", X0 + 0.05, 1.75, 0.7, 0.7, Math.PI / 2);
    // meubels
    zet(b, "loungeSofaLong", KAMER.sofa[0], 0, KAMER.sofa[2], 0.85);
    zet(b, "pillow", KAMER.sofa[0] - 0.6, 0.45, KAMER.sofa[2] + 0.1, 0.32, 0.2); zet(b, "pillowBlue", KAMER.sofa[0] + 0.7, 0.45, KAMER.sofa[2] + 0.1, 0.32, -0.2);
    zet(b, "rugRound", 0.4, 0.02, -0.9, 0.03); zet(b, "tableCoffee", 0.5, 0.02, -2.0, 0.36);
    zet(b, "lampRoundFloor", 2.1, 0, -2.95, 1.7); zet(b, "sideTable", -1.25, 0, -2.95, 0.55); zet(b, "lampSquareTable", -1.25, 0.55, -2.95, 0.5);
    zet(b, "cabinetTelevision", X1 - 0.35, 0, -0.3, 0.55, -Math.PI / 2); zet(b, "televisionModern", X1 - 0.35, 0.55, -0.3, 0.75, -Math.PI / 2);
    zet(b, "speaker", X1 - 0.35, 0, -1.4, 0.95, -Math.PI / 2); zet(b, "speaker", X1 - 0.35, 0, 0.8, 0.95, -Math.PI / 2);
    zet(b, "bookcaseOpen", X1 - 0.3, 0, -2.6, 1.9, -Math.PI / 2); zet(b, "books", X1 - 0.3, 0.95, -2.6, 0.3, -Math.PI / 2); zet(b, "books", X1 - 0.3, 1.42, -2.6, 0.3, -Math.PI / 2); zet(b, "radio", X1 - 0.3, 0.5, -2.6, 0.22, -Math.PI / 2);
    zet(b, "loungeChair", X1 - 1.2, 0, 1.9, 0.85, -2.2); zet(b, "pottedPlant", 3.3, 0, -3.05, 1.1); zet(b, "plantSmall2", 0.45, 0.38, -2.0, 0.22);
    zet(b, "candy-cane-red", 0.8, 0.38, -1.9, 0.26, 0.4);
    // kerstboom: kaal tot de robot hem versiert, dan vol
    this.boomKaal = los("tree", 2.45); this.boomKaal.position.set(...KAMER.tree); R.add(this.boomKaal);
    this.boomVol = los("tree-decorated", 2.45); this.boomVol.position.set(...KAMER.tree); R.add(this.boomVol);
    [["present-a-cube", -2.15, -2.0, 0.32], ["present-b-rectangle", -3.25, -1.75, 0.28], ["present-a-round", -2.55, -1.65, 0.3]].forEach(([n, x, z, h], i) => {
      const o = los(n as string, h as number); o.position.set(x as number, 0, z as number); o.rotation.y = i * 0.7; R.add(o); this.cadeaus.push(o); });
    // plafondlamp
    binnen.add(new THREE.CylinderGeometry(0.01, 0.01, 0.5, 6).translate(0.4, H - 0.25, -0.9), lam("rbSnoer", () => ({ color: "#241726" })));
    binnen.add(new THREE.ConeGeometry(0.32, 0.25, 20, 1, true).translate(0.4, H - 0.55, -0.9), lam("rbKap", () => ({ color: "#2f6b5a", side: THREE.DoubleSide })));
    this.plafondLamp = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(3, 2.6, 1.9) }));
    this.plafondLamp.position.set(0.4, H - 0.66, -0.9); this.plafondLamp.layers.set(NOINK); R.add(this.plafondLamp);
    b.build(R, true); binnen.build(R, false);
    // lichtsnoer langs de bovenkant van de achterwand (groep 0, altijd aan) en op de schouw
    for (let i = 0; i < 60; i++) { const u = i / 59, x = X0 + 0.2 + u * (X1 - X0 - 0.4), boog = (u * 6) % 1; this.lampjes.zet([x, H - 0.2 - 0.18 * Math.sin(boog * Math.PI), Z0 + 0.08], 0); }
    for (let i = 0; i < 16; i++) this.lampjes.zet([X0 + 0.6, 1.36 + 0.02, -0.3 + i * 0.13], 0);
    // boom (groep 1): spiraal over de kegel
    for (let i = 0; i < 70; i++) { const u = i / 69, y = 0.35 + u * 1.85, r = 0.62 * (1 - u * 0.85) + 0.04, a = u * Math.PI * 11;
      this.lampjes.zet([KAMER.tree[0] + Math.cos(a) * r, y, KAMER.tree[2] + Math.sin(a) * r], 1); }
    // bank (groep 2): langs de rugleuning en de armleuningen
    const sx = KAMER.sofa[0], sz = KAMER.sofa[2];
    for (let i = 0; i < 26; i++) { const u = i / 25; this.lampjes.zet([sx - 1.05 + u * 2.1, 0.88 + 0.05 * Math.sin(u * 20), sz - 0.32], 2); }
    for (let i = 0; i < 8; i++) { this.lampjes.zet([sx - 1.1, 0.62, sz - 0.3 + i * 0.09], 2); this.lampjes.zet([sx + 1.1, 0.62, sz - 0.3 + i * 0.09], 2); }
    // vader (groep 3): spiraal om zijn kaartje (straal klein, voor en achter het lijf)
    for (let i = 0; i < 46; i++) { const u = i / 45, a = u * Math.PI * 9; this.lampjes.zet([DAD_K[0] + Math.sin(a) * 0.3, 0.25 + u * 1.15, DAD_K[2] + Math.cos(a) * 0.16], 3); }
    // cadeaudoos (avond): rood met goud lint en strik, om de robot heen
    const rood = lam("rbPapier", () => ({ map: ctex("rbPapierTex", 256, 256, (g) => { g.fillStyle = "#d1343c"; g.fillRect(0, 0, 256, 256); g.fillStyle = "#f6f1e6";
      for (let y = 16; y < 256; y += 64) for (let x = 16; x < 256; x += 64) { g.beginPath(); g.arc(x + (y % 128 ? 32 : 0), y, 7, 0, 7); g.fill(); } }) })), goud = lam("rbLint", () => ({ color: "#f2c94c" }));
    const d = new Batch(), dl = new Batch();
    d.add(boxGeo(V(-0.48, 0, -0.48), V(0.48, 1.0, 0.48)), rood); d.add(boxGeo(V(-0.07, 0, 0.481), V(0.07, 1.0, 0.5)), goud);
    dl.add(boxGeo(V(-0.52, 0, -0.52), V(0.52, 0.14, 0.52)), rood);
    dl.add(boxGeo(V(-0.07, 0, -0.53), V(0.07, 0.15, 0.53)), goud); dl.add(boxGeo(V(-0.53, 0, -0.07), V(0.53, 0.15, 0.07)), goud);
    dl.add(new THREE.TorusGeometry(0.17, 0.06, 10, 20).rotateY(0.5).translate(-0.16, 0.27, 0), goud); dl.add(new THREE.TorusGeometry(0.17, 0.06, 10, 20).rotateY(-0.5).translate(0.16, 0.27, 0), goud);
    d.build(this.doos, true); dl.build(this.deksel, true); this.deksel.position.y = 1.0; this.doos.add(this.deksel);
    this.doos.traverse((x) => { (x as THREE.Mesh).matrixAutoUpdate = true; }); R.add(this.doos);
    // extra cadeaus voor kerstavond (verschijnen een voor een terwijl de robot inpakt)
    const namen = ["present-a-cube", "present-b-cube", "present-a-rectangle", "present-b-round", "present-a-round", "present-b-rectangle"];
    for (let i = 0; i < 18; i++) { const o = los(namen[i % 6], 0.24 + ((i * 37) % 10) / 40); const ring = Math.floor(i / 6);
      o.position.set(-2.6 + Math.cos(i * 1.3) * (0.7 + ring * 0.3) + 0.3, ring === 2 ? 0.28 : 0, -2.2 + Math.sin(i * 1.3) * (0.5 + ring * 0.25) + 0.4); o.rotation.y = i; o.visible = false; R.add(o); this.cadeaus.push(o); }
  }

  // ---------------- keuken ----------------
  private keuken(R: THREE.Object3D) {
    const b = new Batch(), binnen = new Batch(), H = 2.8, X0 = KX - 3.6, X1 = KX + 3.6, Z0 = -3.0, Z1 = 5;
    binnen.add(boxGeo(V(X0, 0, Z0), V(X1, 0.02, Z1)), lam("rbKVloer", () => ({ map: rep(tegels(), 3, 4) })));
    const wand = lam("rbKWand", () => ({ color: "#f6ead2" }));
    binnen.add(boxGeo(V(X0 - 0.2, 0, Z0 - 0.2), V(X1 + 0.2, H, Z0)), wand);
    binnen.add(boxGeo(V(X0 - 0.2, 0, Z0), V(X0, H, Z1)), wand); binnen.add(boxGeo(V(X1, 0, Z0), V(X1 + 0.2, H, Z1)), wand);
    binnen.add(boxGeo(V(X0, 0.92, Z0), V(X1, 1.55, Z0 + 0.02)), lam("rbKTegel", () => ({ map: rep(wandtegel(), 4, 1) })));
    binnen.add(boxGeo(V(X0 - 0.2, H, Z0 - 0.2), V(X1 + 0.2, H + 0.1, Z1), 0, true), lam("rbKPlafond", () => ({ color: "#fbf6ec" })));
    // rij keukenkastjes tegen de achterwand (Kenney, schaal naar 0,92 m hoog)
    const h = 0.92, w = 0.88;
    const rij = ["kitchenCabinetDrawer", "kitchenCabinet", "kitchenSink", "kitchenCabinetDrawer", "kitchenStove", "kitchenCabinet", "kitchenCabinetDrawer"];
    const x0 = KX - 3.0;
    rij.forEach((n, i) => zet(b, n, x0 + i * w + w / 2, 0, Z0 + 0.48, h));
    zet(b, "kitchenFridgeLarge", x0 + rij.length * w + 0.45, 0, Z0 + 0.42, 2.0);
    zet(b, "hoodModern", x0 + 4 * w + w / 2, 1.75, Z0 + 0.35, 0.7);
    [0, 1, 5, 6].forEach((i) => zet(b, "kitchenCabinetUpper", x0 + i * w + w / 2, 1.65, Z0 + 0.25, 0.8));
    zet(b, "kitchenMicrowave", x0 + 0.5, h, Z0 + 0.4, 0.3); zet(b, "kitchenCoffeeMachine", x0 + 5.3, h, Z0 + 0.35, 0.35); zet(b, "toaster", x0 + 3.2, h, Z0 + 0.4, 0.2); zet(b, "kitchenBlender", x0 + 6.0, h, Z0 + 0.35, 0.38);
    // raam boven het aanrecht
    b.add(boxGeo(V(x0 + 2.0, 1.6, Z0 + 0.01), V(x0 + 3.2, 2.45, Z0 + 0.02)), lam("rbRaamDag", () => ({ map: raam(false) })));
    const kozijn = lam("rbKozijn", () => ({ color: "#ffffff" }));
    binnen.add(boxGeo(V(x0 + 1.92, 1.55, Z0), V(x0 + 3.28, 1.6, Z0 + 0.12)), kozijn); binnen.add(boxGeo(V(x0 + 1.92, 2.45, Z0), V(x0 + 3.28, 2.52, Z0 + 0.05)), kozijn);
    binnen.add(boxGeo(V(x0 + 2.58, 1.6, Z0), V(x0 + 2.62, 2.45, Z0 + 0.05)), kozijn);
    // tafel met stoelen, kerstkrans, lampjes langs de kastjes
    zet(b, "table", KX + 2.4, 0, 1.6, 0.78); zet(b, "chairCushion", KX + 1.8, 0, 1.6, 0.95, Math.PI / 2); zet(b, "chairCushion", KX + 3.0, 0, 1.6, 0.95, -Math.PI / 2);
    zet(b, "wreath-decorated", KX + 2.9, 1.9, Z0 + 0.06, 0.55);
    b.build(R, true); binnen.build(R, false);
    for (let i = 0; i < 40; i++) { const u = i / 39; this.lampjes.zet([x0 + u * 6.2, 2.47 - 0.08 * Math.sin(((u * 5) % 1) * Math.PI), Z0 + 0.1], 0); }
    // koekjes: één op de bakplaat, daarna een lawine (InstancedMesh, groeiend aantal)
    this.eenKoek = los("gingerbread-man", 0.18); this.eenKoek.rotation.x = -Math.PI / 2; R.add(this.eenKoek);
    let geo: THREE.BufferGeometry | null = null, mat: THREE.Material | null = null;
    const g0 = los("gingerbread-man", 0.22);
    g0.traverse((x) => { const m = x as THREE.Mesh; if (m.isMesh && !geo) { geo = m.geometry; mat = m.material as THREE.Material; } });
    const N = 1400;
    this.koekjes = new THREE.InstancedMesh(geo!, mat!, N); this.koekjes.castShadow = true; this.koekjes.receiveShadow = true; this.koekjes.count = 0; this.koekjes.frustumCulled = false; R.add(this.koekjes);
    let s = 7; const r = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    const hoog = new Map<string, number>();
    for (let i = 0; i < N; i++) {
      // dichter bij de oven -> hogere stapel; ook rond de zus (knie-hoog)
      const rr = Math.pow(r(), 0.7) * 4.2, a = r() * Math.PI * 2;
      const x = Math.max(X0 + 0.2, Math.min(X1 - 0.2, KX + 0.3 + Math.cos(a) * rr * 1.2)), z = Math.max(Z0 + 0.6, Math.min(3.8, -1.6 + Math.abs(Math.sin(a)) * rr * 1.1));
      const cel = `${Math.round(x * 3)}|${Math.round(z * 3)}`, y = hoog.get(cel) ?? 0.0; hoog.set(cel, y + 0.05);
      this.koekPos.push({ p: [x, y, z], r: r() * 6.28, t: i / N });
    }
  }

  // ---------------- tuin ----------------
  private tuin(R: THREE.Object3D) {
    const b = new Batch();
    b.add(boxGeo(V(BX - 120, -0.02, -60), V(BX + 120, 0.0, 60)), lam("rbSneeuw", () => ({ map: rep(sneeuw(), 30, 30) })));
    b.add(boxGeo(V(BX - 2.2, 0.0, -4.5), V(BX + 0.6, 0.012, 5)), lam("rbOprit", () => ({ map: rep(ctex("rbOpritTex", 512, 512, (g, r) => { g.fillStyle = "#9aa0aa"; g.fillRect(0, 0, 512, 512);
      for (let i = 0; i < 500; i++) { g.fillStyle = `rgba(255,255,255,${0.05 + r() * 0.1})`; g.fillRect(r() * 512, r() * 512, 4, 4); } }), 2, 4) })));
    const huis = (x: number, z: number, w: number, d: number, h: number, kleur: string, deur: string) => {
      const muur = lam("rbMuur" + kleur, () => ({ color: kleur })), dak = lam("rbDakSneeuw", () => ({ color: "#f4f8fc" })), voor = lam("rbVoor" + kleur, () => ({ map: gevel(kleur, deur) }));
      const hw = w / 2;
      b.add(boxGeo(V(x - hw, 0, z - d), V(x + hw, h, z - 0.02)), muur);
      b.add(quad(V(x - hw, 0, z), V(x + hw, 0, z), V(x + hw, h, z), V(x - hw, h, z)), voor);
      const rh = d * 0.45, o = 0.45;
      b.add(quad(V(x - hw - o, h - 0.1, z + o), V(x + hw + o, h - 0.1, z + o), V(x + hw + o, h + rh, z - d / 2), V(x - hw - o, h + rh, z - d / 2)), dak);
      b.add(quad(V(x + hw + o, h - 0.1, z - d - o), V(x - hw - o, h - 0.1, z - d - o), V(x - hw - o, h + rh, z - d / 2), V(x + hw + o, h + rh, z - d / 2)), dak);
      b.add(tri(V(x - hw, h, z - 0.02), V(x + hw, h, z - 0.02), V(x, h + rh, z - d / 2)), muur);
      b.add(boxGeo(V(x + hw * 0.4, h, z - d * 0.7), V(x + hw * 0.4 + 0.6, h + rh + 0.7, z - d * 0.7 + 0.6)), lam("rbSchoorsteen", () => ({ map: rep(baksteen(), 1, 2) })));
      for (let i = 0; i < 28; i++) this.lampjes.zet([x - hw - o + (i / 27) * (w + 2 * o), h - 0.18 - 0.06 * Math.sin(((i / 27) * 7 % 1) * Math.PI), z + o + 0.02], 0);
    };
    huis(ONS[0], ONS[2], 8, 7, 3.4, "#e9d7b9", "#c0353a");
    huis(BUUR[0], BUUR[2], 8, 7, 3.4, "#b9d3e9", "#2f6b5a");
    [["tree-snow-a", -12, -9, 4.2], ["tree-snow-b", 13, -10, 4.6], ["tree-snow-c", -1.5, -9.5, 3.4], ["tree-snow-a", 3.6, -8.5, 3.0], ["tree-snow-b", -16, 2, 3.8], ["tree-snow-c", 15, 3, 3.6],
      ["tree-snow-a", -9, 12, 4.0], ["tree-snow-b", 9, 14, 4.4]].forEach(([n, x, z, h]) => zet(b, n as string, BX + (x as number), 0, z as number, h as number));
    zet(b, "snowman-hat", BX - 4.6, 0, 1.2, 1.5, 0.5); zet(b, "sled", BX - 3.9, 0, 3.6, 0.35, 0.9); zet(b, "lantern-hanging", BX - 2.4, 0, -2.2, 1.9);
    for (let i = 0; i < 7; i++) zet(b, "cabin-fence", BX - 9 + i * 1.6, 0, 5.2, 0.8);
    for (let i = 0; i < 7; i++) zet(b, "cabin-fence", BX + 3 + i * 1.6, 0, 5.2, 0.8);
    zet(b, "rocks-medium", BX + 2.2, 0, 3.4, 0.4); zet(b, "snow-pile", BX - 2.8, 0, -1.0, 0.35); zet(b, "snow-pile", BX + 1.4, 0, 1.5, 0.4);
    b.build(R, true);
    // sneeuwberg op het huis van de buren (groeit), sneeuwballen in de lucht, vallende vlokken
    this.berg = new THREE.Mesh(new THREE.SphereGeometry(1, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), lam("rbBerg", () => ({ map: rep(sneeuw(), 3, 3) })));
    this.berg.castShadow = true; this.berg.receiveShadow = true; this.berg.position.set(BUUR[0], 0, BUUR[2] - 2.5); R.add(this.berg);
    this.ballen = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(0.16, 1), lam("rbBal", () => ({ color: "#f6f9fd" })), 80);
    this.ballen.count = 0; this.ballen.frustumCulled = false; this.ballen.castShadow = true; R.add(this.ballen);
    const n = 1500, pos = new Float32Array(n * 3);
    let s = 3; const r = () => ((s = (s * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < n; i++) { pos[i * 3] = BX - 14 + r() * 28; pos[i * 3 + 1] = r() * 9; pos[i * 3 + 2] = -12 + r() * 22; }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    this.vlokken = new THREE.Points(g, new THREE.PointsMaterial({ color: "#ffffff", size: 0.05, sizeAttenuation: true, transparent: true, opacity: 0.9, depthWrite: false }));
    this.vlokken.layers.set(NOINK); this.vlokken.frustumCulled = false; R.add(this.vlokken);
  }

  update(f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = shotAt(f), c = camAt(f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll ?? 0);
    cam.fov = c.fov; cam.near = 0.05; cam.far = 1200; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    cam.layers.enable(NOINK);
    const look = V(...c.look);
    // ---- licht: zon camera-relatief per shot (skill), binnen vanuit het raam ----
    const L = LIGHTS.day, CAM0 = camAt(s.a);
    const fw = V(CAM0.look[0] - CAM0.pos[0], 0, CAM0.look[2] - CAM0.pos[2]).normalize(), rt = V(-fw.z, 0, fw.x);
    const az = THREE.MathUtils.degToRad(({ kamer: 135, keuken: 130, tuin: 150, avond: 120 } as Record<string, number>)[s.place]), el = THREE.MathUtils.degToRad(L.el);
    const dir = fw.clone().multiplyScalar(Math.cos(az)).addScaledVector(rt, Math.sin(az)).multiplyScalar(Math.cos(el)).add(V(0, Math.sin(el), 0)).normalize();
    this.sun.position.copy(look).addScaledVector(dir, 120); this.sun.target.position.copy(look);
    const sc = this.sun.shadow.camera, Rr = s.place === "tuin" ? 26 : 10; sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 10; sc.far = 300; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * 2;
    this.sky.position.copy(cam.position);
    this.fog.near = s.place === "tuin" ? 30 : 60; this.fog.far = s.place === "tuin" ? 220 : 400; scene.fog = this.fog; scene.background = null;
    for (const m of this.clouds) m.lookAt(cam.position.x, m.position.y, cam.position.z);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...LOOK.day.bounce); TONE.uSat.value = LOOK.day.sat;
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad; CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    if (s.place === "kamer" || s.place === "keuken") {   // binnen: iets warmer
      TONE.uLitCol.value.set(L.lit[0] * 1.02, L.lit[1] * 0.97, L.lit[2] * 0.88); TONE.uShadeCol.value.set(L.shade[0] * 1.25, L.shade[1] * 1.15, L.shade[2] * 1.0);
    }
    if (s.place === "avond") {                             // kerstavond: donker blauw buiten, warm binnen, lampjes stralen
      TONE.uLitCol.value.set(L.lit[0] * 0.62, L.lit[1] * 0.5, L.lit[2] * 0.42); TONE.uShadeCol.value.set(L.shade[0] * 0.7, L.shade[1] * 0.62, L.shade[2] * 0.85);
      CHAR.uCharTint.value.set(0.82, 0.7, 0.62);
    }
    const raamM = lam("rbRaamDag", () => ({})) as THREE.MeshLambertMaterial;
    const nachtT = raam(true), dagT = raam(false);
    if (raamM.map !== (s.place === "avond" ? nachtT : dagT)) { raamM.map = s.place === "avond" ? nachtT : dagT; raamM.needsUpdate = true; }
    (this.vuur.material as THREE.MeshBasicMaterial).color.setScalar(1.6 + 0.5 * Math.sin(t * 11) * Math.sin(t * 7.3));
    this.vuur.scale.y = 1 + 0.08 * Math.sin(t * 13);

    // ---- robot ----
    const praat = s.id === 5 ? (mondOp(t, [1]) ? 1 : 0) : 0;
    const rp = robotAt(t, s, praat);
    this.robot.set(rp);
    const dk = s.place === "avond" ? doosAt(t) : 0;
    this.doos.visible = dk > 0;
    if (dk > 0) {
      const wiebel = t > T.slot && t < T.pop ? 1 : 0, w = 1 + 0.07 * Math.sin(t * 9) * wiebel;
      this.doos.position.set(rp.pos[0], 0, rp.pos[2]); this.doos.scale.set(1.0 * w, 1.6 * dk, 1.0 / w); this.doos.rotation.y = 0.2 + 0.06 * Math.sin(t * 6) * wiebel;
      const op = t >= T.pop ? smooth((t - T.pop) / 0.3) : 0;            // deksel vliegt omhoog en kantelt als de robot eruit springt
      this.deksel.position.set(-0.35 * op, 1.0 + 0.9 * op, 0); this.deksel.rotation.z = 0.9 * op;
    }

    // ---- lampjes ----
    const aan = (g: number) => g === 0 ? 1 : g === 1 ? (t >= T.boom + 0.25 ? 1 : 0) : g === 2 ? (t >= T.bank + 0.2 ? 1 : 0) : (t >= T.papa + 0.15 ? 1 : 0);
    this.lampjes.update(t, aan);
    const versierd = t >= T.boom + 0.25;
    this.boomKaal.visible = !versierd; this.boomVol.visible = versierd;

    // ---- cadeaus (avond: steeds meer) ----
    this.cadeaus.forEach((o, i) => { o.visible = i < 3 || (s.place === "avond" && t > T.eve + 0.6 + (i - 3) * 0.12); });

    // ---- keuken: één koekje, dan de lawine ----
    this.eenKoek.visible = s.place === "keuken" && s.id >= 12;
    this.eenKoek.position.set(rp.pos[0] + Math.sin(rp.yaw) * 0.5, 0.0 + 0.95 + 0.03 + rp.bob, rp.pos[2] + Math.cos(rp.yaw) * 0.5);
    const lawine = s.place === "keuken" ? clamp01((t - T.tien - 0.1) / 1.6) : 0;
    const oven: V3 = [KX - 3.0 + 4 * 0.88 + 0.44, 0.45, -2.5];
    const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler();
    let n = 0;
    if (lawine > 0) for (const k of this.koekPos) {
      const u = clamp01((lawine - k.t * 0.85) / 0.15); if (u <= 0) continue;
      const p: V3 = [oven[0] + (k.p[0] - oven[0]) * u, oven[1] + (k.p[1] - oven[1]) * u + Math.sin(u * Math.PI) * 1.2, oven[2] + (k.p[2] - oven[2]) * u];
      e.set(u < 1 ? k.r * 3 * u : -Math.PI / 2 + 0.25 * Math.sin(k.r * 5), k.r, 0); q.setFromEuler(e);
      m4.compose(V(...p), q, V(1, 1, 1)); this.koekjes.setMatrixAt(n++, m4);
    }
    this.koekjes.count = n; this.koekjes.instanceMatrix.needsUpdate = true;

    // ---- tuin: sneeuwballen van de schep naar het buurhuis, berg groeit ----
    const schep = s.place === "tuin" ? clamp01((t - T.schep) / Math.max(0.5, (T.oops + 0.3) - T.schep)) : 0;
    this.berg.scale.set(5.6, 0.2 + 4.6 * smooth(schep * 1.15), 4.6); this.berg.visible = s.place === "tuin";
    let nb = 0;
    // losse sneeuwklonten met elk een eigen ritme, doel verspreid over het buurhuis (eerst leek het een rups)
    if (s.place === "tuin" && t > T.schep && t < T.oops + 0.4) for (let i = 0; i < 60; i++) {
      const h1 = (i * 0.618) % 1, h2 = (i * 0.414 + 0.3) % 1, h3 = (i * 0.732 + 0.6) % 1;
      const dur = 0.9 + 0.5 * h1, k = ((t - T.schep) / dur + h2) % 1;
      if (t - T.schep < h2 * dur) continue;
      const a: V3 = [rp.pos[0] + 0.7, 0.6, rp.pos[2] + 0.4], z: V3 = [BUUR[0] - 3.5 + 7 * h1, 1.5 + smooth(schep) * 3 + 1.5 * h3, BUUR[2] - 0.5 - 5 * h3];
      const sz = 0.5 + 1.1 * h3;
      m4.compose(V(a[0] + (z[0] - a[0]) * k, a[1] + (z[1] - a[1]) * k + Math.sin(k * Math.PI) * (2.5 + 2 * h2), a[2] + (z[2] - a[2]) * k), q.setFromEuler(e.set(h1 * 6, h2 * 6, 0)), V(sz, sz * 0.8, sz));
      this.ballen.setMatrixAt(nb++, m4);
    }
    this.ballen.count = nb; this.ballen.instanceMatrix.needsUpdate = true;
    const pp = this.vlokken.geometry.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < pp.count; i++) { const y0 = (i * 0.6173) % 9; pp.setY(i, 9 - ((9 - y0 + t * 0.6) % 9)); }
    pp.needsUpdate = true; this.vlokken.visible = s.place === "tuin";

    // ---- mensen (cast.ts: zelfde lijst als de controles) ----
    const blinkOf = (k: number) => ((t + k * 0.7) % 3.1) > 2.95;
    const KLEREN: Record<string, Outfit> = { you: O_YOU, sis: O_SIS, dad: O_DAD, mom: O_MOM };
    for (const [cd, bl] of this.people) { cd.mesh.visible = false; bl.visible = false; }
    for (const fg of castAt(t, s)) {
      const [cd, blob] = this.people[fg.slot];
      const m = fg.zinnen ? mondOp(t, fg.zinnen) : null, bl = blinkOf(fg.k);
      const tx = cardTex(`${fg.key}|${fg.expr}|${fg.facing}|${bl}|${m}|${fg.wave ?? "x"}`, 600, 1000, 1.6, (p) => {
        LIP.m = m; bodyFront(p, KLEREN[fg.naam], { mode: "stand", phase: 0, expr: fg.expr, facing: fg.facing as any, blink: bl, light: -2.1, seed: fg.k, wave: fg.wave }); LIP.m = null; });
      cd.set(tx, [fg.pos[0], fg.pos[1] + (fg.hop ?? 0), fg.pos[2]], cam.position, false);
      blob.position.set(fg.pos[0], 0.03, fg.pos[2]); blob.visible = true;
    }

    // ---- effecten ----
    this.fx.forEach((x) => (x.mesh.visible = false));
    const fxAt = (i: number, tex: THREE.Texture, pos: V3, sc: number) => { this.fx[i].set(tex, pos, cam.position); this.fx[i].mesh.scale.set(sc, sc, 1); };
    const knal = (i: number, t0: number, pos: V3, sc: number, kleur = "#fff3b0") => { const u = (t - t0) / 0.5; if (u >= 0 && u < 1) fxAt(i, cardTex(`burst|${kleur}|${Math.round(u * 20)}`, 500, 500, 1.2, (p) => fxBurst(p, Math.round(u * 20) / 20, kleur, 12, 50, 240)), pos, sc); };
    if (s.id === 2) { const u = ((t - T.shiny) / 0.8) % 1; fxAt(0, cardTex(`stars|${Math.round(u * 24)}`, 420, 220, 1.4, (p) => fxStars(p, Math.round(u * 24) / 24)), [rp.pos[0], rp.pos[1] + 1.75, rp.pos[2] + 0.1], 0.75); }
    if (s.place === "kamer") { knal(0, T.boom + 0.2, [KAMER.tree[0], 1.3, KAMER.tree[2] + 0.5], 2.4); knal(1, T.bank + 0.15, [KAMER.sofa[0], 0.8, KAMER.sofa[2] + 0.4], 2.4); knal(2, T.papa + 0.1, [DAD_K[0], 0.9, DAD_K[2] + 0.3], 2.0); }
    if (s.place === "keuken") { const u = (t - T.tien - 0.1) / 1.0; if (u >= 0 && u < 1) fxAt(0, cardTex(`puff|${Math.round(u * 20)}`, 300, 300, 2, (p) => fxPuff(p, Math.round(u * 20) / 20)), [oven[0], 0.5, oven[2] + 0.7], 2.4); }
    if (s.place === "avond") knal(0, T.zelf + 0.85, [rp.pos[0], 1.3, rp.pos[2] + 0.6], 2.2, "#ffe08a");
    return look;
  }
}

export { KICKS };
