// Lipsync (vaste Market Doodle-regel, 27 nov): zelfde klankregels als tools/lipsync.py, van woordtijden naar mondvorm.
import { WORDS } from "./words";

const REGELS: [string, string][] = [["th", "L"], ["ee", "E"], ["ea", "E"], ["oo", "U"], ["ou", "O"], ["ow", "O"], ["oy", "O"], ["ai", "E"], ["ay", "E"],
  ["a", "A"], ["e", "E"], ["i", "E"], ["y", "E"], ["o", "O"], ["u", "U"], ["w", "U"],
  ["m", "M"], ["b", "M"], ["p", "M"], ["f", "F"], ["v", "F"], ["l", "L"], ["t", "L"], ["d", "L"], ["n", "L"],
  ["s", "E"], ["z", "E"], ["c", "E"], ["k", "E"], ["g", "E"], ["h", "A"], ["r", "O"], ["j", "E"], ["q", "U"], ["x", "E"]];
const GETAL: Record<string, string> = { "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine" };
const klanken = (woord: string) => {
  let w = woord.toLowerCase().replace(/[^a-z0-9]/g, "");
  w = w.split("").map((c) => GETAL[c] ?? c).join("");
  const uit: string[] = [];
  let i = 0;
  while (i < w.length) { const r = REGELS.find(([l]) => w.startsWith(l, i)); if (r) { uit.push(r[1]); i += r[0].length; } else i++; }
  const samen: string[] = [];
  for (const v of uit) if (!samen.length || samen[samen.length - 1] !== v) samen.push(v);
  return samen.length ? samen : ["E"];
};
const TL: [number, number, string, number][] = [];
for (const [w, t0, t1, z] of WORDS) {
  const ks = klanken(w), gew = ks.map((k) => ("AEOU".includes(k) ? 2 : 1)), tot = gew.reduce((a, b) => a + b, 0);
  let t = t0;
  ks.forEach((k, i) => { const d = ((t1 - t0) * gew[i]) / tot; TL.push([t, t + d, k, z]); t += d; });
}
/** mondvorm (toon.ts MouthK) voor zin z op tijd t, of null als hij niet praat */
const MOND: Record<string, string> = { A: "grin", E: "teeth", O: "O", U: "o", M: "dash", F: "teeth", L: "grin" };
export const mondOp = (t: number, zinnen: number[]): string | null => {
  const v = TL.find(([a, b, , z]) => zinnen.includes(z) && t >= a && t < b);
  return v ? MOND[v[2]] : null;
};
/** klank-letter (A/E/O/U/M/F/L) voor de oude poppetjes, of null */
export const visOp = (t: number, zinnen: number[]): string | null => {
  const v = TL.find(([a, b, , z]) => zinnen.includes(z) && t >= a && t < b);
  return v ? v[2] : null;
};
