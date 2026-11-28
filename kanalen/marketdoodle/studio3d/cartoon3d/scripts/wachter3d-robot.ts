// 3D-controle voor de robotbutler (zelfde opzet als wachter3d.ts van de haai): per frame met dezelfde camera en dezelfde
// posities als de video (cast.ts / story.ts) wat waar op het 1080x1920 beeld staat. Schrijft out/wachter3d-robot.json;
// scripts/controle3d_robot.py voert dat aan de Market Doodle-wachters.
import * as THREE from "three";
import fs from "node:fs";
import { TOTAL, FPS, shotAt, camAt, robotAt } from "../src/videos/robot/story";
import { castAt, voorwerpenAt, hoofd, ROBOT_KOP, gebaarVan, robotZichtbaar } from "../src/videos/robot/cast";
import { capBox } from "../src/videos/robot/captions";

const W = 1080, H = 1920;
const cam = new THREE.PerspectiveCamera(50, W / H, 0.05, 1200);
const v = new THREE.Vector3();
const scherm = (p: [number, number, number]) => { v.set(...p).project(cam); return { x: (v.x + 1) / 2 * W, y: (1 - v.y) / 2 * H, voor: v.z < 1 && v.z > -1 }; };
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
  const voorwerpen: [string, number[]][] = [], koppen: Record<string, [number, number, number]> = {}, gebaren: Record<string, string | null> = {};
  const as = (p: [number, number, number]) => { const a = Math.atan2(cam.position.x - p[0], cam.position.z - p[2]); return [Math.cos(a), -Math.sin(a)]; };
  if (robotZichtbaar(t, s)) {
    const r = robotAt(t, s, 0), p = r.pos, [ax, az] = as(p), pts: [number, number, number][] = [];
    for (const kx of [-0.4, 0.4]) for (const ky of [0, 1.9]) pts.push([p[0] + ax * kx, p[1] + ky + r.bob, p[2] + az * kx]);
    const b = kader(pts); if (b) voorwerpen.push(["robot", b]);
    const kp: [number, number, number] = [p[0], p[1] + r.bob + ROBOT_KOP.y, p[2]];
    const q = scherm(kp); if (q.voor) koppen["robot"] = [Math.round(q.x), Math.round(q.y), Math.round(straalPx(kp, ROBOT_KOP.r))];
    if (koppen["robot"]) gebaren["robot"] = null;
  }
  for (const fg of castAt(t, s)) {
    const h = hoofd(fg.naam), [ax, az] = as(fg.pos), hw = h.r * 1.4;
    const pts: [number, number, number][] = [];
    for (const kx of [-hw, hw]) for (const ky of [0, h.y + h.r]) pts.push([fg.pos[0] + ax * kx, ky, fg.pos[2] + az * kx]);
    const b = kader(pts); if (b) voorwerpen.push([fg.naam, b]);
    const kp: [number, number, number] = [fg.pos[0], h.y + (fg.hop ?? 0), fg.pos[2]];
    const q = scherm(kp); if (q.voor) koppen[fg.naam] = [Math.round(q.x), Math.round(q.y), Math.round(straalPx(kp, h.r))];
    if (koppen[fg.naam]) gebaren[fg.naam] = gebaarVan(fg);
  }
  for (const o of voorwerpenAt(t, s)) { const b = kader(o.pts); if (b) voorwerpen.push([o.naam, b]); }
  frames.push({ t: +t.toFixed(3), shot: s.id, voorwerpen, koppen, gebaren, ondertitel: capBox(t) });
}
fs.writeFileSync("out/wachter3d-robot.json", JSON.stringify(frames));
console.log("frames", frames.length);
