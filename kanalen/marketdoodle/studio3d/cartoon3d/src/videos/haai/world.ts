// De wereld van de haai-proef: buitenwijk met garage, oprit, stoep, straat, huizen, bomen, lucht en wolken,
// gebouwd met de bouwstenen van de skill (twoTone-materialen, geschilderde texturen, inktlijnen via InkPass),
// plus onze figuren als belichte kaartjes (cardShade) op de NOINK-laag. update(f, cam) zet alles per frame.
import * as THREE from "three";
import { Batch, V, lam, boxGeo, house, quad, tri } from "../bridge/build";
import { ctex, rep, grassHD, cloudHD, stoneHD } from "../bridge/paint";
import { Pen, bodyFront, KID, PARENT, Outfit, Expr, fxBurst, fxPuff, fxSplash, LIP } from "../bridge/toon";
import { LIGHTS, LOOK } from "../bridge/lights";
import { TONE, CHAR, untone } from "../bridge/shade";
import { NOINK } from "../bridge/ink";
import { cardShade, blobMaterial, CARD_K } from "../bridge/cardshade";
import { drawShark, drawBlob, drawSplinters, drawZzz, drawSchoolSign, drawCrumbs } from "./figures";
import { mondOp } from "./lipsync";
import { FPS, shotAt, camAt, sharkAt, KID_IN, KID_OUT, KID_BEACH, T_DEUR, T_BONK, T_NOBODY, T_HAP, T_SLOK, T_IN, T_UIT, T_KEER, T_LAMP, KX, BX, AX, sisAt, bullyAt, DAD_POS, V3, smooth, clamp01 } from "./story";

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
const SIS: Outfit = { jacket: "#e85d9a", pants: "#2d3142", boots: "#f4f1ea", hat: "hair", hair: "#7a4a2a", dress: "#e85d9a", build: "kid", skin: "#f5c9a0" };
const BULLIES: Outfit[] = [{ ...KID, jacket: "#5b5f6b", cap: "#2d3142", skin: "#ecd0b6" }, { ...KID, jacket: "#8a5a3c", hat: "hair", hair: "#2a2a30", cap: undefined, skin: "#c99067" }];
const DAD: Outfit = { ...PARENT, jacket: "#3c8d5a", moustache: "#5a3b2a", build: "stout" };

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
  private shark: Card; private sharkBlob: THREE.Mesh;
  private fx: Card[] = [];
  private people: [Card, THREE.Mesh][] = [];
  private fridge = new THREE.Group();
  private nightBulb!: THREE.Mesh;

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
    b.add(quad(V(KX - 60, 0, 60), V(AX + 60, 0, 60), V(AX + 60, 0, -60), V(KX - 60, 0, -60)), grass);
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
    const blobT = cardTex("blob", 600, 200, 1, drawBlob);
    const mkBlob = (w: number) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, w / 3).rotateX(-Math.PI / 2), blobMaterial(blobT)); m.layers.set(NOINK); m.renderOrder = 0.5; R.add(m); return m; };
    this.sharkBlob = mkBlob(2.4);
    for (let i = 0; i < 5; i++) { const sc = i === 4 ? 0.0021 : i === 0 ? 0.00175 : 0.0016; this.people.push([new Card(R, 600 * sc, 1000 * sc, 25 * sc), mkBlob(0.7)]); }
    for (let i = 0; i < 3; i++) this.fx.push(new Card(R, 1, 1, 0, false));
    this.buildPlaces(R);
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
    const az = THREE.MathUtils.degToRad(({ binnen: 140, buiten: 160, straat: 150, keuken: 130, strand: 150, bad: 130 } as Record<string, number>)[s.place]), el = THREE.MathUtils.degToRad(L.el);
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
    const sh = sharkAt(t, s);
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const mirror = V(...sh.dir).dot(right) < -0.05;
    const blink = (t % 2.6) > 2.45 && s.id !== 4 && s.id !== 1 && sh.look !== "sleep" ? 1 : 0;
    const squash = shakeK > 0.3 && t < T_DEUR ? 0.4 : 0;
    const ph = Math.round(sh.phase * 24) / 24, wq = Math.round(sh.walk * 10) / 10, aq = Math.round(sh.arm * 12) / 12;
    const cq = Math.round(sh.chomp * 6) / 6, sv = sh.shiver ? Math.round(sh.shiver * 30) % 8 : 0;
    const close = [2, 3, 4, 12, 18].includes(s.id) ? 2 : 1.3;
    const sT = cardTex(`shark|${ph}|${wq}|${aq}|${sh.look}|${blink}|${squash}|${close}|${cq}|${sv}`, 1100, 1000, close,
      (p) => drawShark(p, { phase: ph, walk: wq, arm: aq, look: sh.look, blink, squash, chomp: cq, shiver: sv ? sv / 8 + 0.01 : 0 }));
    const showShark = !(s.id === 6 && t < T_DEUR - 0.05);
    this.shark.set(sT, sh.pos, cam.position, mirror);
    this.shark.mesh.visible = showShark;
    this.sharkBlob.position.set(sh.pos[0] + 0.15, 0.05, sh.pos[2]); this.sharkBlob.visible = showShark && sh.pos[1] > -0.05 && s.place !== "bad";
    this.sharkBlob.rotation.y = Math.atan2(cam.position.x - sh.pos[0], cam.position.z - sh.pos[2]);

    // ---- mensen (bodyFront-kaartjes, lipsync op hun eigen zinnen) ----
    const blinkOf = (k: number) => ((t + k * 0.7) % 3.1) > 2.95;
    const person = (c: Card, blob: THREE.Mesh, o: Outfit, key: string, pos: V3, opts: { expr: Expr; facing: -1 | 0 | 1; mode?: "stand" | "stroll"; phase?: number; wave?: number; zinnen?: number[]; k?: number }) => {
      const m = opts.zinnen ? mondOp(t, opts.zinnen) : null;
      const ph2 = opts.mode === "stroll" ? Math.round((opts.phase ?? 0) * 16) / 16 : 0, bl = blinkOf(opts.k ?? 0);
      const tx = cardTex(`${key}|${opts.expr}|${opts.facing}|${bl}|${m}|${ph2}|${opts.wave ?? 0}`, 600, 1000, 1.6, (p) => {
        LIP.m = m; bodyFront(p, o, { mode: opts.mode ?? "stand", phase: ph2, expr: opts.expr, facing: opts.facing as any, blink: bl, light: -2.1, seed: opts.k ?? 3, wave: opts.wave ?? 0 }); LIP.m = null; });
      c.set(tx, pos, cam.position, false);
      blob.position.set(pos[0], 0.05, pos[2]); blob.visible = true;
    };
    for (const [c, b] of this.people) { c.mesh.visible = false; b.visible = false; }
    const [kidC, sisC, b1C, b2C, dadC] = this.people;
    if (s.id === 5) person(kidC[0], kidC[1], YOU, "kid", KID_IN, { expr: "smile_closed", facing: -1, wave: t > 6.2 && t < 7.0 ? 1 : 0, zinnen: [1] });
    if (s.id === 6) person(kidC[0], kidC[1], YOU, "kid", KID_OUT, { expr: t > T_DEUR ? "shock" : t > T_BONK[0] ? "nervous" : "neutral", facing: -1 });
    if (s.place === "straat") {
      const walking = t < 16.9;
      person(sisC[0], sisC[1], SIS, "sis", sisAt(t), { expr: s.id === 9 ? "grin" : "smile", facing: s.id === 9 ? -1 : 1, mode: walking ? "stroll" : "stand", phase: (t / 0.9) % 1, zinnen: [4], k: 5 });
      [b1C, b2C].forEach((c, i) => {
        const run = t > T_NOBODY + 0.55 + i * 0.12;
        person(c[0], c[1], BULLIES[i], "bully" + i, bullyAt(i, t), { expr: t > T_NOBODY + 0.2 ? "shock" : "stern", facing: run ? 1 : -1, mode: run ? "stroll" : "stand", phase: (t / 0.45) % 1, k: 7 + i });
      });
    }
    if (s.place === "keuken" && s.id >= 12) person(dadC[0], dadC[1], DAD, "dad", DAD_POS, { expr: t > T_HAP[0] + 0.1 ? "shock" : "neutral", facing: 1, zinnen: [6], k: 9 });
    if (s.place === "strand") person(kidC[0], kidC[1], YOU, "kidb", KID_BEACH, { expr: t > T_KEER ? (s.id === 16 ? "nervous" : "shock") : "smile", facing: -1, zinnen: [8] });

    // ---- keuken: koelkast wordt in drie happen opgegeten ----
    const bites = T_HAP.filter((th) => t >= th + 0.06).length;
    const fs = t >= T_SLOK ? 0 : 1 - bites / 3;
    this.fridge.visible = fs > 0.01; this.fridge.scale.set(1, Math.max(0.01, fs), 1);
    // ---- bad: nachtlampje ----
    const night = s.place === "bad" && t >= T_LAMP;
    (this.nightBulb.material as THREE.MeshBasicMaterial).color.copy(night ? new THREE.Color(5, 3.6, 1.6) : new THREE.Color(0.9, 0.85, 0.7));
    if (night) {
      TONE.uLitCol.value.set(L.lit[0] * 0.28, L.lit[1] * 0.3, L.lit[2] * 0.52); TONE.uShadeCol.value.set(L.shade[0] * 0.5, L.shade[1] * 0.55, L.shade[2] * 0.9);
      CHAR.uCharTint.value.set(0.42, 0.44, 0.68);
    } else { TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); CHAR.uCharTint.value.set(...L.charTint); }

    // ---- effecten ----
    this.fx.forEach((x) => (x.mesh.visible = false));
    const fxAt = (i: number, tex: THREE.Texture, pos: V3, sc: number, dy: number) => { this.fx[i].set(tex, pos, cam.position); this.fx[i].mesh.scale.set(sc, sc, 1); this.fx[i].mesh.position.y += dy; };
    const u = (t - T_DEUR) / 0.6;
    if (s.id === 6 && u >= 0 && u < 1) {
      fxAt(0, cardTex(`burst|${Math.round(u * 20)}`, 500, 500, 1.2, (p) => fxBurst(p, Math.round(u * 20) / 20, "#fff3b0", 12, 50, 240)), [0, 0, 0.35], 3.6, -0.2);
      fxAt(1, cardTex(`spl|${Math.round(u * 20)}`, 800, 800, 1, (p) => drawSplinters(p, Math.round(u * 20) / 20)), [0, 0, 0.5], 3.2, -0.1);
    }
    const pu = (t - T_DEUR - 0.1) / 1.1;
    if (s.id === 6 && pu >= 0 && pu < 1) fxAt(2, cardTex(`puff|${Math.round(pu * 20)}`, 300, 300, 2, (p) => fxPuff(p, Math.round(pu * 20) / 20)), [0.3, 0, 0.9], 4.5, -0.6);
    if (s.place === "keuken") T_HAP.forEach((th, i) => {
      const k = (t - th) / 0.5;
      if (k >= 0 && k < 1) fxAt(i, cardTex(`crumb|${Math.round(k * 16)}`, 400, 400, 1.2, (p) => drawCrumbs(p, Math.round(k * 16) / 16)), [KX + 2.4, 0.6, -2.2], 1.6, 0);
    });
    if (s.place === "strand") [T_IN, T_UIT].forEach((ts, i) => {
      const k = (t - ts) / 0.7;
      if (k >= 0 && k < 1) fxAt(i, cardTex(`splash|${Math.round(k * 16)}`, 500, 500, 1.2, (p) => fxSplash(p, Math.round(k * 16) / 16)), [BX - 0.2, -0.3, i ? 0.1 : -0.1], 2.8, 0);
    });
    if (s.place === "bad" && t > 34.8) fxAt(0, cardTex(`zzz|${Math.round((t * 20) % 100)}`, 500, 500, 1, (p) => drawZzz(p, Math.round((t * 20) % 100) / 20)), [AX + 0.6, 1.55, -2.3], 1.1, 0);
    return look;
  }

  // ---------------- keuken, strand, badkamer, school ----------------
  private buildPlaces(R: THREE.Object3D) {
    const b = new Batch();
    // schoolbord langs de stoep
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.4, 0.66), new THREE.MeshLambertMaterial({ map: cardTex("schoolsign", 800, 220, 1, drawSchoolSign) }));
    sign.position.set(-17.5, 2.0, 8.75); R.add(sign);
    b.add(boxGeo(V(-18.6, 0, 8.68), V(-18.5, 2.1, 8.74)), lam("signpost", () => ({ color: "#5a3b2a" }))); b.add(boxGeo(V(-16.5, 0, 8.68), V(-16.4, 2.1, 8.74)), lam("signpost", () => ({ color: "#5a3b2a" })));
    b.build(R, true);

    // ---- keuken (binnen, geen schaduw van muren/plafond) ----
    const k = new Batch(), H = 2.8;
    const kw = lam("kWall", () => ({ color: "#f6e7c8" })), kf = lam("kFloor", () => ({ map: rep(ctex("kTiles", 512, 512, (g) => {
      for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = (x + y) % 2 ? "#f4f1ea" : "#3f6fb5"; g.fillRect(x * 64, y * 64, 64, 64); } }), 3, 3) }));
    k.add(boxGeo(V(KX - 4.6, 0, -4.1), V(KX + 4.6, 0.02, 4.1)), kf);
    k.add(boxGeo(V(KX - 4.8, 0, -4.3), V(KX + 4.8, H, -4.1)), kw);
    k.add(boxGeo(V(KX - 4.8, 0, -4.3), V(KX - 4.6, H, 4.3)), kw); k.add(boxGeo(V(KX + 4.6, 0, -4.3), V(KX + 4.8, H, 4.3)), kw);
    k.add(boxGeo(V(KX - 4.8, 0, 4.1), V(KX + 4.8, H, 4.3)), kw);
    k.add(boxGeo(V(KX - 4.8, H, -4.3), V(KX + 4.8, H + 0.1, 4.3), 0, true), lam("kCeil", () => ({ color: "#fbf6ec" })));
    const cab = lam("kCab", () => ({ color: "#7fb7a4" })), top = lam("kTop", () => ({ color: "#efe9df" })), handle = lam("kHandle", () => ({ color: "#3a3a46" }));
    k.add(boxGeo(V(KX - 4.5, 0, -4.1), V(KX + 2.2, 0.9, -3.45)), cab); k.add(boxGeo(V(KX - 4.55, 0.9, -4.1), V(KX + 2.25, 0.96, -3.4)), top);
    for (let x = KX - 4.3; x < KX + 2.0; x += 0.75) k.add(boxGeo(V(x, 0.7, -3.44), V(x + 0.3, 0.74, -3.4)), handle);
    k.add(boxGeo(V(KX - 4.5, 1.7, -4.1), V(KX - 1.5, 2.5, -3.7)), cab);
    k.add(boxGeo(V(KX - 0.9, 1.25, -4.12), V(KX + 1.4, 2.35, -4.08)), lam("kWin", () => ({ map: ctex("kWinTex", 512, 256, (g) => {
      const gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, "#5a9be0"); gr.addColorStop(1, "#cfe6fb"); g.fillStyle = gr; g.fillRect(0, 0, 512, 256);
      g.fillStyle = "#6aab4f"; g.beginPath(); g.ellipse(120, 250, 160, 70, 0, 0, 7); g.fill(); g.beginPath(); g.ellipse(400, 260, 190, 80, 0, 0, 7); g.fill();
      g.strokeStyle = "#ffffff"; g.lineWidth = 18; g.strokeRect(9, 9, 494, 238); g.beginPath(); g.moveTo(256, 0); g.lineTo(256, 256); g.stroke(); }) })));
    k.add(new THREE.CylinderGeometry(0.6, 0.6, 0.06, 24).translate(KX - 2.8, 0.78, 1.0), lam("kTable", () => ({ color: "#c08a5a" })));
    k.add(new THREE.CylinderGeometry(0.06, 0.08, 0.76, 10).translate(KX - 2.8, 0.38, 1.0), lam("kTable", () => ({ color: "#c08a5a" })));
    k.add(new THREE.CylinderGeometry(0.12, 0.1, 0.2, 14).translate(KX - 2.7, 0.9, 0.9), lam("kMug", () => ({ color: "#e8463a" })));
    k.build(R, false);
    // koelkast (eigen groep, schaalt omlaag bij elke hap)
    const fr = new Batch(), fw = lam("fridge", () => ({ color: "#f2f4f8" })), fh = lam("fridgeH", () => ({ color: "#9aa3b0" }));
    fr.add(boxGeo(V(-0.48, 0, -0.4), V(0.48, 1.95, 0.4)), fw);
    fr.add(boxGeo(V(-0.46, 1.25, 0.4), V(0.46, 1.27, 0.42)), fh);
    fr.add(boxGeo(V(-0.38, 1.4, 0.4), V(-0.33, 1.8, 0.47)), fh); fr.add(boxGeo(V(-0.38, 0.5, 0.4), V(-0.33, 1.1, 0.47)), fh);
    fr.build(this.fridge, true);
    this.fridge.position.set(KX + 2.85, 0, -3.55); R.add(this.fridge);

    // ---- strand ----
    const s = new Batch();
    const sand = lam("sand", () => ({ map: rep(ctex("sandTex", 512, 512, (g, r) => {
      g.fillStyle = "#f3d99b"; g.fillRect(0, 0, 512, 512);
      for (let i = 0; i < 1200; i++) { g.fillStyle = `rgba(${r() < 0.5 ? "255,255,255" : "160,120,60"},${0.08 + r() * 0.1})`; g.fillRect(r() * 512, r() * 512, 3, 3); } }), 20, 20) }));
    s.add(boxGeo(V(BX - 120, -0.02, 0), V(BX + 120, 0.01, 80)), sand);
    const sea = lam("sea", () => ({ map: rep(ctex("seaTex", 512, 512, (g, r) => {
      g.fillStyle = "#2fa9c9"; g.fillRect(0, 0, 512, 512);
      g.strokeStyle = "rgba(255,255,255,0.55)"; g.lineWidth = 6; g.lineCap = "round";
      for (let i = 0; i < 40; i++) { const x = r() * 512, y = r() * 512; g.beginPath(); g.arc(x, y, 18, 3.6, 5.8); g.stroke(); } }), 30, 30) }));
    s.add(boxGeo(V(BX - 160, -0.05, -500), V(BX + 160, 0.04, 0)), sea);
    s.add(boxGeo(V(BX - 120, 0.0, -0.25), V(BX + 120, 0.06, 0.25)), lam("foam", () => ({ color: "#ffffff" })));
    // parasol, handdoek, emmertje
    s.add(new THREE.CylinderGeometry(0.04, 0.04, 2.3, 8).translate(BX - 3.2, 1.15, 4.6), lam("pole", () => ({ color: "#f4f1ea" })));
    s.add(new THREE.ConeGeometry(1.5, 0.6, 12).translate(BX - 3.2, 2.35, 4.6), lam("umb", () => ({ map: ctex("umbTex", 512, 64, (g) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? "#ffffff" : "#e8463a"; g.fillRect(i * 64, 0, 64, 64); } }) })));
    s.add(boxGeo(V(BX - 4.3, 0.01, 5.0), V(BX - 2.6, 0.03, 6.0)), lam("towel", () => ({ map: ctex("towelTex", 256, 256, (g) => { for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? "#f2c94c" : "#2f80ed"; g.fillRect(0, i * 32, 256, 32); } }) })));
    s.add(new THREE.CylinderGeometry(0.16, 0.12, 0.26, 14).translate(BX + 3.0, 0.13, 4.2), lam("bucket", () => ({ color: "#e8463a" })));
    s.add(new THREE.SphereGeometry(0.3, 16, 12).translate(BX + 3.6, 0.3, 5.2), lam("ball", () => ({ map: ctex("ballTex", 256, 128, (g) => { ["#e8463a", "#ffffff", "#2f80ed", "#ffffff", "#f2c94c", "#ffffff"].forEach((c, i) => { g.fillStyle = c; g.fillRect(i * 43, 0, 43, 128); }); }) })));
    s.build(R, true);

    // ---- badkamer ----
    const a = new Batch(), HB = 2.7;
    const tiles = lam("bTiles", () => ({ map: rep(ctex("bTileTex", 512, 512, (g) => {
      g.fillStyle = "#bfe3ea"; g.fillRect(0, 0, 512, 512); g.strokeStyle = "#8fc1cc"; g.lineWidth = 6;
      for (let i = 0; i <= 512; i += 64) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 512); g.moveTo(0, i); g.lineTo(512, i); g.stroke(); } }), 3, 2) }));
    a.add(boxGeo(V(AX - 3.2, 0, -3.2), V(AX + 3.2, 0.02, 3.2)), lam("bFloor", () => ({ map: rep(ctex("bFloorTex", 256, 256, (g) => { for (let y = 0; y < 4; y++) for (let x = 0; x < 4; x++) { g.fillStyle = (x + y) % 2 ? "#f4f1ea" : "#d9d4cc"; g.fillRect(x * 64, y * 64, 64, 64); } }), 4, 4) })));
    a.add(boxGeo(V(AX - 3.4, 0, -3.4), V(AX + 3.4, HB, -3.2)), tiles);
    a.add(boxGeo(V(AX - 3.4, 0, -3.4), V(AX - 3.2, HB, 3.4)), tiles); a.add(boxGeo(V(AX + 3.2, 0, -3.4), V(AX + 3.4, HB, 3.4)), tiles);
    a.add(boxGeo(V(AX - 3.4, 0, 3.2), V(AX + 3.4, HB, 3.4)), tiles);
    a.add(boxGeo(V(AX - 3.4, HB, -3.4), V(AX + 3.4, HB + 0.1, 3.4), 0, true), lam("bCeil", () => ({ color: "#fbf6ec" })));
    const tub = lam("tub", () => ({ color: "#ffffff" })), tubFeet = lam("tubFeet", () => ({ color: "#e8c45a" }));
    a.add(boxGeo(V(AX - 1.8, 0.12, -3.2), V(AX + 1.6, 0.75, -2.95)), tub);   // achterkant
    a.add(boxGeo(V(AX - 1.8, 0.12, -1.95), V(AX + 1.6, 0.75, -1.7)), tub);   // voorkant (verbergt de benen)
    a.add(boxGeo(V(AX - 1.8, 0.12, -3.2), V(AX - 1.55, 0.75, -1.7)), tub); a.add(boxGeo(V(AX + 1.35, 0.12, -3.2), V(AX + 1.6, 0.75, -1.7)), tub);
    a.add(boxGeo(V(AX - 1.55, 0.12, -2.95), V(AX + 1.35, 0.5, -1.95)), lam("bathWater", () => ({ color: "#7cc8e8" })));
    for (const [x, z] of [[-1.7, -3.1], [1.5, -3.1], [-1.7, -1.8], [1.5, -1.8]]) a.add(new THREE.SphereGeometry(0.1, 10, 8).translate(AX + x, 0.1, z), tubFeet);
    a.add(new THREE.SphereGeometry(0.12, 14, 10).translate(AX + 1.2, 0.86, -1.82), lam("duck", () => ({ color: "#f2c94c" })));
    a.add(new THREE.SphereGeometry(0.07, 12, 8).translate(AX + 1.27, 0.99, -1.8), lam("duck", () => ({ color: "#f2c94c" })));
    a.add(boxGeo(V(AX + 1.33, 0.95, -1.82), V(AX + 1.4, 0.98, -1.76)), lam("duckBeak", () => ({ color: "#f2994a" })));
    a.add(boxGeo(V(AX - 3.2, 1.4, -1.2), V(AX - 3.1, 1.44, 0.4)), lam("rack", () => ({ color: "#9aa3b0" })));
    a.add(boxGeo(V(AX - 3.15, 0.8, -1.0), V(AX - 3.05, 1.45, 0.2)), lam("towelB", () => ({ color: "#e85d9a" })));
    a.add(boxGeo(V(AX + 2.0, 0.3, -3.2), V(AX + 2.2, 0.5, -3.12)), lam("plug", () => ({ color: "#f4f1ea" })));
    a.add(boxGeo(V(AX - 1.0, 0.0, 0.3), V(AX + 0.6, 0.03, 1.2)), lam("bMat", () => ({ color: "#2f80ed" })));
    a.build(R, false);
    this.nightBulb = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 12), new THREE.MeshBasicMaterial({ color: new THREE.Color(0.9, 0.85, 0.7) }));
    this.nightBulb.position.set(AX + 2.1, 0.45, -3.05); this.nightBulb.layers.set(NOINK); R.add(this.nightBulb);
  }
}
