// De robotbutler: echt 3D (geen kaartje), uit eenvoudige vormen met de twee-toon-materialen van de skill, zodat de inktlijnen
// er net zo omheen lopen als om de rest van de wereld. Rolt op één bal, heeft een strikje (butler), een schermgezicht met
// gloeiende ogen (bloom) en een antenne. Alle bewegingen komen uit RobotPose (story.ts robotAt).
import * as THREE from "three";
import { lam } from "../bridge/build";
import { NOINK } from "../bridge/ink";

export type Ogen = "blij" | "gewoon" | "groot" | "x" | "dicht" | "hart";
export type RobotPose = {
  pos: [number, number, number]; yaw: number; bob: number;
  armL: number; armR: number;          // schouderhoek (0 = langs het lijf, 1.5 = recht vooruit, 2.8 = omhoog)
  elbL: number; elbR: number;          // elleboog
  head: number;                        // hoofd kantelen
  bow: number;                         // buiging (0-1)
  ogen: Ogen; praat: number;           // 0-1 mondbalkje
  schep?: boolean; blik?: boolean;     // sneeuwschep / bakplaat in de hand
  zicht?: boolean;
};

const ogenTex = new Map<string, THREE.CanvasTexture>();
const scherm = (o: Ogen, praat: number) => {
  const key = `${o}|${Math.round(praat * 4)}`;
  let t = ogenTex.get(key);
  if (t) return t;
  const c = document.createElement("canvas"); c.width = 256; c.height = 160;
  const g = c.getContext("2d")!;
  g.fillStyle = "#13233a"; g.fillRect(0, 0, 256, 160);
  g.strokeStyle = "#7ff3ff"; g.fillStyle = "#7ff3ff"; g.lineCap = "round"; g.lineWidth = 14;
  const oog = (x: number) => {
    const y = 66;
    if (o === "blij") { g.beginPath(); g.arc(x, y + 10, 22, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    else if (o === "dicht") { g.beginPath(); g.moveTo(x - 22, y); g.lineTo(x + 22, y); g.stroke(); }
    else if (o === "x") { g.beginPath(); g.moveTo(x - 18, y - 18); g.lineTo(x + 18, y + 18); g.moveTo(x + 18, y - 18); g.lineTo(x - 18, y + 18); g.stroke(); }
    else if (o === "hart") { g.beginPath(); g.moveTo(x, y + 20); g.bezierCurveTo(x - 34, y - 4, x - 14, y - 30, x, y - 10); g.bezierCurveTo(x + 14, y - 30, x + 34, y - 4, x, y + 20); g.fillStyle = "#ff7fa8"; g.fill(); }
    else { const r = o === "groot" ? 26 : 18; g.beginPath(); g.ellipse(x, y, r, r * 1.15, 0, 0, 7); g.fill(); g.fillStyle = "#e9ffff"; g.beginPath(); g.arc(x + r * 0.35, y - r * 0.4, r * 0.3, 0, 7); g.fill(); g.fillStyle = "#7ff3ff"; }
  };
  oog(80); oog(176);
  const m = Math.round(praat * 4) / 4;
  g.lineWidth = 10;
  if (m > 0) { g.beginPath(); g.ellipse(128, 124, 26, 6 + 14 * m, 0, 0, 7); g.fill(); }
  else if (o === "blij" || o === "hart") { g.beginPath(); g.arc(128, 108, 22, 0.2 * Math.PI, 0.8 * Math.PI); g.stroke(); }
  else { g.beginPath(); g.moveTo(108, 122); g.lineTo(148, 122); g.stroke(); }
  t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; ogenTex.set(key, t);
  return t;
};

export class Robot {
  root = new THREE.Group();
  private body = new THREE.Group(); private headG = new THREE.Group();
  private sL = new THREE.Group(); private sR = new THREE.Group(); private eL = new THREE.Group(); private eR = new THREE.Group();
  private face: THREE.Mesh; private faceMat: THREE.MeshBasicMaterial;
  private ball: THREE.Mesh; private tip: THREE.Mesh;
  private schep = new THREE.Group(); private blik = new THREE.Group();

  constructor(parent: THREE.Object3D) {
    const wit = lam("rbWit", () => ({ color: "#eef2f6" })), blauw = lam("rbBlauw", () => ({ color: "#3d7be0" })), grijs = lam("rbGrijs", () => ({ color: "#8d97a6" }));
    const zwart = lam("rbZwart", () => ({ color: "#2a2d3a" })), rood = lam("rbRood", () => ({ color: "#e0393e" }));
    const mesh = (g: THREE.BufferGeometry, m: THREE.Material, p: THREE.Object3D, x = 0, y = 0, z = 0) => { const o = new THREE.Mesh(g, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; p.add(o); return o; };
    // rolbal + kraag
    this.ball = mesh(new THREE.SphereGeometry(0.2, 24, 16), grijs, this.root, 0, 0.2, 0);
    mesh(new THREE.CylinderGeometry(0.2, 0.26, 0.12, 24), blauw, this.body, 0, 0.42, 0);
    // lijf: afgeronde ton, wit met blauwe band, zwart butlervest met knoopjes en rood strikje
    mesh(new THREE.CapsuleGeometry(0.33, 0.36, 8, 24), wit, this.body, 0, 0.86, 0);
    mesh(new THREE.CylinderGeometry(0.345, 0.345, 0.08, 24), blauw, this.body, 0, 0.62, 0);
    const vest = new THREE.Mesh(new THREE.SphereGeometry(0.335, 24, 16, -0.6, 1.2, 0.9, 1.15), zwart); vest.position.set(0, 0.86, 0.005); this.body.add(vest);
    [0.9, 0.78, 0.66].forEach((y) => mesh(new THREE.SphereGeometry(0.025, 10, 8), lam("rbGoud", () => ({ color: "#f2c94c" })), this.body, 0, y + 0.05, 0.335));
    mesh(new THREE.ConeGeometry(0.07, 0.13, 4).rotateZ(Math.PI / 2), rood, this.body, -0.06, 1.16, 0.3);
    mesh(new THREE.ConeGeometry(0.07, 0.13, 4).rotateZ(-Math.PI / 2), rood, this.body, 0.06, 1.16, 0.3);
    mesh(new THREE.SphereGeometry(0.035, 10, 8), rood, this.body, 0, 1.16, 0.32);
    // hoofd: afgeronde doos met scherm
    this.headG.position.set(0, 1.27, 0); this.body.add(this.headG);
    mesh(new THREE.CylinderGeometry(0.07, 0.09, 0.08, 16), grijs, this.headG, 0, 0.02, 0);
    const kop = mesh(new THREE.BoxGeometry(0.62, 0.44, 0.46, 2, 2, 2), wit, this.headG, 0, 0.27, 0);
    kop.geometry = roundBox(0.62, 0.44, 0.46, 0.09);
    this.faceMat = new THREE.MeshBasicMaterial({ map: scherm("gewoon", 0), color: new THREE.Color(1.6, 1.6, 1.6), toneMapped: true });
    this.face = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.31), this.faceMat); this.face.position.set(0, 0.27, 0.232); this.face.layers.set(NOINK); this.headG.add(this.face);
    [-1, 1].forEach((k) => mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.06, 18).rotateZ(Math.PI / 2), blauw, this.headG, k * 0.33, 0.27, 0));
    mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.2, 8), grijs, this.headG, 0, 0.58, 0);
    this.tip = new THREE.Mesh(new THREE.SphereGeometry(0.045, 14, 10), new THREE.MeshBasicMaterial({ color: new THREE.Color(4, 0.6, 0.5) }));
    this.tip.position.set(0, 0.7, 0); this.tip.layers.set(NOINK); this.headG.add(this.tip);
    // armen: schouder -> bovenarm -> elleboog -> onderarm -> klauwhand
    const arm = (s: THREE.Group, e: THREE.Group, k: number) => {
      s.position.set(k * 0.4, 1.0, 0); this.body.add(s);
      mesh(new THREE.SphereGeometry(0.085, 14, 10), blauw, s);
      mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.26, 10), grijs, s, 0, -0.15, 0);
      e.position.set(0, -0.3, 0); s.add(e);
      mesh(new THREE.SphereGeometry(0.06, 12, 8), blauw, e);
      mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.24, 10), grijs, e, 0, -0.14, 0);
      mesh(new THREE.TorusGeometry(0.065, 0.025, 8, 16, Math.PI * 1.4).rotateZ(-Math.PI * 0.2), wit, e, 0, -0.31, 0);
    };
    arm(this.sL, this.eL, -1); arm(this.sR, this.eR, 1);
    // sneeuwschep (rechterhand) en bakplaat (beide handen)
    mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.0, 8).rotateX(Math.PI / 2), lam("rbHout", () => ({ color: "#a8724a" })), this.schep, 0, 0, 0.35);
    mesh(new THREE.BoxGeometry(0.42, 0.03, 0.34), rood, this.schep, 0, -0.05, 0.95);
    this.schep.position.set(0, -0.34, 0); this.eR.add(this.schep);
    mesh(new THREE.BoxGeometry(0.62, 0.025, 0.42), grijs, this.blik, 0, 0, 0);
    this.blik.position.set(0, 0.95, 0.5); this.body.add(this.blik);
    this.root.add(this.body); parent.add(this.root);
  }

  set(p: RobotPose) {
    this.root.visible = p.zicht !== false;
    this.root.position.set(p.pos[0], p.pos[1], p.pos[2]); this.root.rotation.y = p.yaw;
    this.body.position.y = p.bob; this.body.rotation.x = p.bow * 0.55;
    this.ball.rotation.x = p.pos[2] * 3 + p.pos[0] * 2;
    this.headG.rotation.z = p.head; this.headG.rotation.x = -p.bow * 0.2;
    this.sL.rotation.set(-p.armL, 0, -0.18); this.sR.rotation.set(-p.armR, 0, 0.18);
    this.eL.rotation.x = -p.elbL; this.eR.rotation.x = -p.elbR;
    this.schep.visible = !!p.schep; this.blik.visible = !!p.blik;
    const t = scherm(p.ogen, p.praat);
    if (this.faceMat.map !== t) { this.faceMat.map = t; this.faceMat.needsUpdate = true; }
  }
  /** hoofd-midden in wereldcoördinaten (voor de controles en de camera) */
  kop(p: RobotPose): [number, number, number] { return [p.pos[0], p.pos[1] + p.bob + 1.54, p.pos[2]]; }
}

/** afgeronde doos (voor het hoofd) */
export const roundBox = (w: number, h: number, d: number, r: number) => {
  const s = new THREE.Shape(), x = -w / 2 + r, y = -h / 2 + r, W = w - 2 * r, H = h - 2 * r;
  s.moveTo(x, y - r); s.lineTo(x + W, y - r); s.quadraticCurveTo(x + W + r, y - r, x + W + r, y); s.lineTo(x + W + r, y + H);
  s.quadraticCurveTo(x + W + r, y + H + r, x + W, y + H + r); s.lineTo(x, y + H + r); s.quadraticCurveTo(x - r, y + H + r, x - r, y + H);
  s.lineTo(x - r, y); s.quadraticCurveTo(x - r, y - r, x, y - r);
  const g = new THREE.ExtrudeGeometry(s, { depth: d - 2 * r, bevelEnabled: true, bevelSize: r * 0.6, bevelThickness: r, bevelSegments: 4, curveSegments: 8 });
  g.translate(0, 0, -(d - 2 * r) / 2); g.computeVertexNormals();
  return g;
};
