// Wie en wat staat waar (pure functies van tijd + shot). world.ts tekent hiermee en scripts/wachter3d-robot.ts controleert
// hiermee, zodat de controles precies over hetzelfde beeld gaan als de video.
import type { Expr } from "../bridge/toon";
import { Shot, V3, T, KX, BX, KAMER, MOM, MOM6, YOU, DAD_K, SIS_K, YOU_A, YOU_T, BUUR, robotAt, doosAt } from "./story";

/** kaartschaal (m per px van het 600x1000-doek) */
export const SC: Record<string, number> = { you: 0.00175, sis: 0.0016, dad: 0.0021, mom: 0.002 };
/** hoofd: hoogte boven de voet en straal (m), nagemeten op de stills (kind 519 px / 119 px, volwassene 695 / 120) */
export const hoofd = (naam: string) => (naam === "you" || naam === "sis" ? { y: 519 * SC[naam], r: 119 * SC[naam] } : { y: 695 * SC[naam], r: 120 * SC[naam] });
export const ROBOT_KOP = { y: 1.54, r: 0.31 };

export type Fig = { naam: string; slot: number; pos: V3; expr: Expr; facing: -1 | 0 | 1; wave?: number; zinnen?: number[]; k: number; hop?: number; key: string };
export const gebaarVan = (f: Fig) => (f.wave !== undefined ? "zwaai" : null);

export const castAt = (t: number, s: Shot): Fig[] => {
  const out: Fig[] = [];
  const wiebel = (k: number) => (Math.round(t * 8 + k) % 2 ? 1 : 0);
  // verticaal beeld is smal: per shot alleen wie erover gaat (shot 5: mama en jij; 6: mama; 9-10: papa in de lampjes)
  if (s.id === 5) {
    out.push({ naam: "you", slot: 0, key: "you", pos: YOU, expr: "grin", facing: -1, k: 1 });
    out.push({ naam: "mom", slot: 3, key: "mom", pos: MOM, expr: "smile", facing: 1, wave: wiebel(1), k: 2 });
  }
  if (s.id === 6) out.push({ naam: "mom", slot: 3, key: "mom6", pos: MOM6, expr: "smile_closed", facing: -1, wave: wiebel(0), k: 2 });
  if (s.id === 9 || s.id === 10) out.push({ naam: "dad", slot: 2, key: "dad", pos: DAD_K, expr: "shock", facing: 0, zinnen: [3], k: 7, hop: s.id === 9 ? 0.04 * Math.abs(Math.sin(t * 20)) : 0 });
  if (s.place === "keuken" && s.id === 14) out.push({ naam: "sis", slot: 1, key: "sisk", pos: SIS_K, expr: "shock", facing: 1, zinnen: [5], k: 4 });
  if (s.id === 15 || s.id === 18) out.push({ naam: "you", slot: 0, key: "yout", pos: YOU_T, expr: s.id === 18 ? "nervous" : s.id === 15 ? "smile" : "shock", facing: 1, zinnen: [7], k: 1,
    wave: s.id === 15 || s.id === 18 ? wiebel(0) : undefined });
  if (s.id === 21) out.push({ naam: "you", slot: 0, key: "youa", pos: YOU_A, expr: t >= T.pop ? "laugh" : "grin", facing: -1, k: 1 });
  return out;
};
export const robotZichtbaar = (t: number, s: Shot) => robotAt(t, s, 0).zicht !== false;

/** voorwerpen in de wereld als een paar punten (voor "genoemd = gezien" en de geluidcheck) */
export const voorwerpenAt = (t: number, s: Shot): { naam: string; pts: V3[] }[] => {
  const v: { naam: string; pts: V3[] }[] = [];
  const box = (x0: number, x1: number, y0: number, y1: number, z0: number, z1: number): V3[] =>
    [[x0, y0, z0], [x1, y0, z0], [x0, y1, z0], [x1, y1, z0], [x0, y0, z1], [x1, y0, z1], [x0, y1, z1], [x1, y1, z1], [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]];
  if (s.place === "kamer" || s.place === "avond") {
    const [tx, , tz] = KAMER.tree; v.push({ naam: "boom", pts: box(tx - 0.55, tx + 0.55, 0.1, 2.3, tz - 0.55, tz + 0.55) });
    const [sx, , sz] = KAMER.sofa; v.push({ naam: "bank", pts: box(sx - 0.95, sx + 0.95, 0.05, 0.85, sz - 0.38, sz + 0.38) });
  }
  if (s.place === "avond") {
    if (t > T.eve + 0.6) v.push({ naam: "cadeaus", pts: box(-3.3, -1.6, 0, 0.6, -2.9, -1.4) });
    if (doosAt(t) > 0) { const p = robotAt(t, s, 0).pos; v.push({ naam: "doos", pts: box(p[0] - 0.5, p[0] + 0.5, 0, 1.6 * doosAt(t), p[2] - 0.5, p[2] + 0.5) }); }
  }
  if (s.place === "keuken") {
    if (s.id >= 12) { const r = robotAt(t, s, 0); v.push({ naam: "koekje", pts: [[r.pos[0] + Math.sin(r.yaw) * 0.5, 0.98, r.pos[2] + Math.cos(r.yaw) * 0.5]] }); }
    if (t > T.tien + 0.2) v.push({ naam: "koekjes", pts: box(KX - 3, KX + 3, 0, 0.5, -2.5, 2.5) });
  }
  if (s.place === "tuin") {
    v.push({ naam: "sneeuw", pts: box(BX - 4, BX + 2, 0, 0.05, -3, 4) });
    v.push({ naam: "buurhuis", pts: box(BUUR[0] - 4, BUUR[0] + 4, 0, 5.5, BUUR[2] - 7, BUUR[2]) });
  }
  return v;
};
export { MOM };
