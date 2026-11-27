// Ondertitels: 1-3 woorden tegelijk (gedeeld door Haai.tsx en de 3D-controle scripts/wachter3d.ts).
import { WORDS } from "./words";

export const CAP = { top: 1220, size: 96, width: 960, regel: 106 };
export const chunks = (() => {
  const out: { a: number; b: number; w: [string, number, number, number][] }[] = [];
  let cur: [string, number, number, number][] = [];
  WORDS.forEach((w, i) => {
    cur.push(w);
    const next = WORDS[i + 1];
    const end = /[.,?!]$/.test(w[0]) || cur.length >= 3 || !next || next[3] !== w[3];
    if (end) { out.push({ a: cur[0][1], b: next && next[3] === w[3] ? next[1] : w[2] + 0.25, w: cur }); cur = []; }
  });
  return out;
})();
/** ruwe kader van de ondertitel op het 1080x1920 beeld (Arial Black 96 px ~ 0,72 em per teken, max 960 breed) */
export const capBox = (t: number): [number, number, number, number] | null => {
  const c = chunks.find((k) => t >= k.a - 0.05 && t < k.b);
  if (!c) return null;
  const woorden = c.w.map((w) => w[0].toUpperCase());
  const breed = (s: string) => s.length * CAP.size * 0.72;
  let regels = 1, cur = "";
  for (const w of woorden) { const n = cur ? cur + " " + w : w; if (breed(n) > CAP.width && cur) { regels++; cur = w; } else cur = n; }
  const w = Math.min(CAP.width, Math.max(...woorden.map(breed), breed(woorden.join(" ")) / regels));
  return [540 - w / 2 - 10, CAP.top, 540 + w / 2 + 10, CAP.top + regels * CAP.regel + 14];
};
