// 3D-controle (eigenaar 27 nov: "vergeet de controles niet, ook niet in deze nieuwe stijl").
// Rekent voor elk frame met dezelfde camera en dezelfde posities als de video uit wat waar op het 1080x1920 beeld staat:
// voorwerpen (kaders), koppen (middelpunt + straal), gebaren en het kader van de ondertitel. Schrijft out/wachter3d.json;
// scripts/controle3d.py voert dat aan de gewone Market Doodle-wachters (tekstwachter, gezichten/LAYOUT, shortregels).
import * as THREE from "three";
import fs from "node:fs";
import { TOTAL, FPS, shotAt, camAt } from "../src/videos/haai/story";
import { castAt, voorwerpenAt, sharkAt, haaiZichtbaar, hoofd, HAAI_KOP, PXM, gebaarVan } from "../src/videos/haai/cast3d";
import { capBox } from "../src/videos/haai/captions";
import { HAAI_PX } from "../src/videos/haai/oudmaat";

const W = 1080, H = 1920;
const cam = new THREE.PerspectiveCamera(50, W / H, 0.1, 1200);
const v = new THREE.Vector3();
const scherm = (p: [number, number, number]) => {
  v.set(...p).project(cam);
  const voor = v.z < 1 && v.z > -1;
  return { x: (v.x + 1) / 2 * W, y: (1 - v.y) / 2 * H, voor };
};
const kader = (pts: [number, number, number][]) => {
  const s = pts.map(scherm).filter((q) => q.voor);
  if (!s.length) return null;
  const b = [Math.min(...s.map((q) => q.x)), Math.min(...s.map((q) => q.y)), Math.max(...s.map((q) => q.x)), Math.max(...s.map((q) => q.y))];
  if (b[2] < 0 || b[0] > W || b[3] < 0 || b[1] > H) return null;
  return b.map((x) => Math.round(x));
};
const straalPx = (p: [number, number, number], r: number) => {
  const d = v.set(...p).applyMatrix4(cam.matrixWorldInverse).z;
  return Math.abs(r / (-d * Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)))) * H / 2;
};

const frames: unknown[] = [];
for (let f = 0; f < TOTAL; f++) {
  const t = f / FPS, s = shotAt(f), c = camAt(f);
  cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll ?? 0);
  cam.fov = c.fov; cam.updateProjectionMatrix(); cam.updateMatrixWorld(); cam.matrixWorldInverse.copy(cam.matrixWorld).invert();
  const right = new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0);
  const voorwerpen: [string, number[]][] = [], koppen: Record<string, [number, number, number]> = {}, gebaren: Record<string, string | null> = {};
  // kaartje-as: de plaat draait om y naar de camera; lokale +x = (cos a, 0, -sin a)
  const as = (p: [number, number, number]) => { const a = Math.atan2(cam.position.x - p[0], cam.position.z - p[2]); return [Math.cos(a), -Math.sin(a)]; };
  if (haaiZichtbaar(t, s)) {
    const sh = sharkAt(t, s), [ax, az] = as(sh.pos);
    const mirror = new THREE.Vector3(...sh.dir).dot(right) < -0.05 ? -1 : 1;
    const hw = HAAI_PX.w * PXM / 2, top = (HAAI_PX.voet) * PXM;
    const p = sh.pos, pts: [number, number, number][] = [];
    for (const kx of [-hw, hw]) for (const ky of [0, top * 0.95]) pts.push([p[0] + ax * kx, p[1] + ky, p[2] + az * kx]);
    const b = kader(pts); if (b) voorwerpen.push(["haai", b]);
    const kp: [number, number, number] = [p[0] + ax * HAAI_KOP.x * mirror, p[1] + HAAI_KOP.y, p[2] + az * HAAI_KOP.x * mirror];
    const q = scherm(kp); if (q.voor) koppen["haai"] = [Math.round(q.x), Math.round(q.y), Math.round(straalPx(kp, HAAI_KOP.r))];
    if (koppen["haai"]) gebaren["haai"] = sh.walk > 0.5 ? "rennen" : null;
  }
  for (const fg of castAt(t, s)) {
    const h = hoofd(fg.naam), [ax, az] = as(fg.pos), hw = 0.35 * (h.y / 1.28);
    const pts: [number, number, number][] = [];
    for (const kx of [-hw, hw]) for (const ky of [0, h.y + h.r]) pts.push([fg.pos[0] + ax * kx, ky, fg.pos[2] + az * kx]);
    const b = kader(pts); if (b) voorwerpen.push([fg.naam, b]);
    const kp: [number, number, number] = [fg.pos[0], h.y, fg.pos[2]];
    const q = scherm(kp); if (q.voor) koppen[fg.naam] = [Math.round(q.x), Math.round(q.y), Math.round(straalPx(kp, h.r))];
    if (koppen[fg.naam]) gebaren[fg.naam] = gebaarVan(fg);
  }
  for (const o of voorwerpenAt(t, s)) { const b = kader(o.pts); if (b) voorwerpen.push([o.naam, b]); }
  frames.push({ t: +t.toFixed(3), shot: s.id, voorwerpen, koppen, gebaren, ondertitel: capBox(t) });
}
fs.writeFileSync("out/wachter3d.json", JSON.stringify(frames));
console.log("frames", frames.length);
