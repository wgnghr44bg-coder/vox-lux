// Wie en wat staat waar (pure functies van tijd + shot). world.ts tekent hiermee, scripts/wachter3d.ts controleert hiermee,
// zodat de controles precies over hetzelfde beeld gaan als de video.
import {
  Shot, V3, sharkAt, KID_IN, KID_OUT, KID_BEACH, T_DEUR, T_BONK, T_NOBODY, T_HAP, T_SLOK, T_KEER, T_LAMP, KX, BX, AX, sisAt, bullyAt, DAD_POS,
} from "./story";

export const PXM = 0.0026;                    // meter per pixel van de oude plaatjes (haai 2 m in 2D -> 2,6 m hier)
export const GROOT: Record<string, number> = { you: 1.0, sis: 0.8, dad: 1.15, friend: 0.95, rich: 1.05 };
/** hoofd: hoogte boven de voet en straal (m), uit pop_short (hoofd 246*S boven de voet, straal ~60*S, s = 2) */
export const hoofd = (naam: string) => ({ y: 492 * GROOT[naam] * PXM, r: 125 * GROOT[naam] * PXM });
/** haaienkop t.o.v. het midden van het kaartje (neus naar +x van het kaartje) */
export const HAAI_KOP = { x: 0.8, y: 1.48, r: 0.42 };

export type Fig = { naam: string; slot: number; pos: V3; g?: string; verb?: boolean; loop?: number; zinnen?: number[]; k?: number; mirror?: boolean };
/** gebaar voor de tekstwachter (DOEN/GEVOEL) */
export const gebaarVan = (f: Fig) => (f.loop !== undefined ? "rennen" : f.g && f.g !== "none" ? f.g.replace(/[0-9]+$/, "") : null);

// gebaren op het verhaal (eigenaar 27 nov: "bewegingen van de personen ... wat bij het verhaal past")
const anim = (g: string, n: number, t: number, dt: number) => `${g}${Math.floor(t / dt) % n}`;
export const castAt = (t: number, s: Shot): Fig[] => {
  const out: Fig[] = [];
  // garage: "Okay, buddy." zwaaien, "Just one step." naar de haai wijzen (de haai staat links -> gespiegeld)
  if (s.id === 5) out.push({ naam: "you", slot: 0, pos: KID_IN, g: t < 6.67 ? anim("zwaai", 4, t, 0.07) : t < 7.7 ? "wijs" : "none", zinnen: [1], mirror: t >= 6.67 && t < 7.7 });
  // oprit: rustig -> schrikken bij de bonken -> handen op het hoofd als de deur breekt
  if (s.id === 6) out.push({ naam: "you", slot: 0, pos: KID_OUT, g: t > T_DEUR ? "hoofdhanden" : t > T_BONK[0] ? anim("schrik", 2, t, 0.05) : "none", verb: t > T_BONK[0] });
  if (s.place === "straat") {
    if (t < 16.9) out.push({ naam: "sis", slot: 1, pos: sisAt(t), loop: (t / 0.9) % 1 });
    else out.push({ naam: "sis", slot: 1, pos: sisAt(t), g: anim("juich", 4, t, 0.17), zinnen: [4], k: 5 });
    // pestkoppen: stoer (handen in de zij) -> schrikken van de haai -> wegrennen
    [0, 1].forEach((i) => {
      const run = t > T_NOBODY + 0.55 + i * 0.12, bang = t > T_NOBODY + 0.2;
      out.push({ naam: i ? "rich" : "friend", slot: 2 + i, pos: bullyAt(i, t),
        ...(run ? { loop: (t / 0.45) % 1, verb: true } : { g: bang ? anim("schrik", 2, t, 0.05) : "heupen", verb: bang, k: 7 + i }) });
    });
  }
  // keuken: vader schrikt bij de eerste hap (handen op het hoofd), "That was a brand new fridge!" armen open
  if (s.place === "keuken" && s.id >= 12)
    out.push({ naam: "dad", slot: 4, pos: DAD_POS, g: s.id === 13 ? (t < 24.5 ? "armen-open" : "wijs") : t > T_HAP[0] + 0.1 ? "hoofdhanden" : "none", verb: t > T_HAP[0] + 0.1, zinnen: [6], k: 9 });
  // strand: blij juichen -> naar de zee wijzen -> schrikken als de haai terugrent -> "Wait." armen open, "scared of water?" nadenken
  if (s.place === "strand") {
    let g = "none", verb = false, mirror = false;
    if (s.id === 14) g = anim("juich", 4, t, 0.17);
    else if (s.id === 15) { if (t < T_KEER) { g = "wijs"; mirror = true; } else { g = anim("schrik", 2, t, 0.05); verb = true; } }
    else g = t < 32.55 ? "armen-open" : "denk";
    out.push({ naam: "you", slot: 0, pos: KID_BEACH, g, verb, zinnen: [8], mirror });
  }
  return out;
};
export const haaiZichtbaar = (t: number, s: Shot) => !(s.id === 6 && t < T_DEUR - 0.05);
export const koelkastSchaal = (t: number) => (t >= T_SLOK ? 0 : 1 - T_HAP.filter((th) => t >= th + 0.06).length / 3);

/** voorwerpen in de wereld als een paar punten (voor "genoemd = gezien") */
export const voorwerpenAt = (t: number, s: Shot): { naam: string; pts: V3[] }[] => {
  const v: { naam: string; pts: V3[] }[] = [];
  const box = (x0: number, x1: number, y0: number, y1: number, z0: number, z1: number): V3[] =>
    [[x0, y0, z0], [x1, y0, z0], [x0, y1, z0], [x1, y1, z0], [x0, y0, z1], [x1, y0, z1], [x0, y1, z1], [x1, y1, z1], [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]];
  if (s.place === "binnen" || s.place === "buiten" || s.place === "straat") v.push({ naam: "garage", pts: box(-3.6, 3.6, 0, 3.1, -8.4, 0) });
  if (t < T_DEUR) v.push({ naam: "garagedeur", pts: box(-1.75, 1.75, 0.05, 2.4, -0.1, 0) });
  else if (t < T_DEUR + 3) v.push({ naam: "garagedeur", pts: box(-4, 4, 0, 2.5, 0, 5) });     // planken vliegen/liggen op de oprit
  if (s.place === "straat") v.push({ naam: "schoolbord", pts: box(-18.7, -16.3, 1.6, 2.4, 8.7, 8.8) });
  const fs = koelkastSchaal(t);
  if (s.place === "keuken" && fs > 0.01) v.push({ naam: "koelkast", pts: box(KX + 2.37, KX + 3.33, 0, 1.95 * fs, -3.95, -3.15) });
  if (s.place === "strand") v.push({ naam: "zee", pts: [[BX - 3, 0, -2], [BX + 3, 0, -2], [BX, 0, -8], [BX - 8, 0, -15], [BX + 8, 0, -15], [BX, 0, -40]] });
  if (s.place === "bad") {
    v.push({ naam: "bad", pts: box(AX - 1.8, AX + 1.6, 0.12, 0.75, -3.2, -1.7) });
    v.push({ naam: "nachtlampje", pts: [[AX + 2.1, 0.45, -3.05]] });
  }
  return v;
};
export { sharkAt, T_LAMP };
