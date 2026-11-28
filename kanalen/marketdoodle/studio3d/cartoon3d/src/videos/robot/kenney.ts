// Gratis Kenney-modellen (CC0: Furniture Kit + Holiday Kit, public/kenney) voor rijke, gedetailleerde kamers
// (eigenaar 28 nov: "meer details, betere achtergronden", voorbeeld IFOLOGY). Eén keer vooraf geladen (delayRender).
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { staticFile } from "remotion";
import { Batch, Kit } from "../bridge/build";

export const NODIG = [
  // woonkamer
  "loungeSofa", "tree", "loungeSofaLong", "loungeChair", "tableCoffee", "rugRound", "rugRectangle", "lampRoundFloor", "lampSquareTable", "sideTable",
  "televisionModern", "cabinetTelevision", "bookcaseOpen", "books", "pottedPlant", "plantSmall1", "plantSmall2", "pillow", "pillowBlue", "radio", "speaker",
  "tree-decorated", "present-a-cube", "present-a-rectangle", "present-a-round", "present-b-cube", "present-b-rectangle", "present-b-round",
  "wreath-decorated", "sock-red", "sock-green-cane", "sock-red-cane", "lights-colored", "candy-cane-red", "nutcracker", "lantern",
  // keuken
  "kitchenCabinet", "kitchenCabinetDrawer", "kitchenCabinetUpper", "kitchenCabinetUpperDouble", "kitchenSink", "kitchenStove", "kitchenFridgeLarge",
  "kitchenMicrowave", "kitchenCoffeeMachine", "kitchenBlender", "toaster", "hoodModern", "table", "chair", "chairCushion", "gingerbread-man", "gingerbread-woman",
  // buiten
  "tree-snow-a", "tree-snow-b", "tree-snow-c", "snowman", "snowman-hat", "snow-pile", "snow-flat-large", "sled", "lantern-hanging", "rocks-medium", "cabin-fence", "reindeer",
];

let p: Promise<Kit> | null = null;
export const KIT: Kit = {};
export const laadKit = () => {
  if (!p) {
    const loader = new GLTFLoader();
    p = Promise.all(NODIG.map((n) => loader.loadAsync(staticFile(`kenney/${n}.glb`)).then((g) => { KIT[n] = g.scene; }).catch(() => { console.warn("kenney ontbreekt", n); })))
      .then(() => KIT);
  }
  return p;
};

const box = new Map<string, THREE.Box3>();
const maat = (n: string) => {
  let b = box.get(n);
  if (!b) { b = new THREE.Box3().setFromObject(KIT[n]); box.set(n, b); }
  return b;
};
/** model n in de batch: voet op y, geschaald naar hoogte h (of breedte w als h < 0), gedraaid om yaw, midden op x/z */
export const zet = (b: Batch, n: string, x: number, y: number, z: number, h: number, yaw = 0, sx = 1) => {
  const o = KIT[n]; if (!o) return;
  const bb = maat(n), s = h / Math.max(0.01, bb.max.y - bb.min.y);
  const cx = (bb.min.x + bb.max.x) / 2, cz = (bb.min.z + bb.max.z) / 2;
  const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), yaw);
  const off = new THREE.Vector3(-cx * s * sx, -bb.min.y * s, -cz * s).applyQuaternion(q);
  b.addObject(o, new THREE.Matrix4().compose(new THREE.Vector3(x + off.x, y + off.y, z + off.z), q, new THREE.Vector3(s * sx, s, s)));
};
/** model n als eigen object (om te bewegen/schalen), voet op 0, midden op 0 */
export const los = (n: string, h: number) => {
  const g = new THREE.Group(), b = new Batch(); zet(b, n, 0, 0, 0, h); b.build(g, true);
  g.traverse((x) => { (x as THREE.Mesh).matrixAutoUpdate = true; });
  return g;
};
/** breedte/diepte van model n bij hoogte h */
export const voet = (n: string, h: number) => { const bb = maat(n), s = h / (bb.max.y - bb.min.y); return [(bb.max.x - bb.min.x) * s, (bb.max.z - bb.min.z) * s]; };
