// Tijdlijn van "What If You Got A Robot Butler For Christmas?" (3D-short, 28 nov 2026). Alle tijden komen uit de woordtijden
// (short-robot/woorden.json via words.ts), zodat elk beeld begint op het woord dat het laat zien. Plekken liggen ver uit elkaar
// in één wereld: woonkamer rond x=0, keuken KX, tuin BX.
import { WORDS, ZINNEN } from "./words";
import type { RobotPose, Ogen } from "./robotbouw";

export const FPS = 30;
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
const lerp3 = (a: V3, b: V3, u: number): V3 => [lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u)];

export const EIND = ZINNEN[ZINNEN.length - 1][1] + 0.7;
export const TOTAL = Math.round(EIND * FPS);
const zs = (z: number) => ZINNEN[z][0], ze = (z: number) => ZINNEN[z][1];
/** begin van het eerste woord in zin z dat met w begint (na woord nummer 'na' in die zin) */
export const kw = (z: number, w: string, na = 0) => {
  const ws = WORDS.filter((x) => x[3] === z);
  const v = ws.slice(na).find((x) => x[0].toLowerCase().replace(/[^a-z0-9']/g, "").startsWith(w.toLowerCase()));
  return v ? v[1] : zs(z);
};
export const T = {
  shiny: kw(0, "shiny"), polite: kw(0, "polite"), little: kw(0, "a", 8),
  dag1: zs(2), boom: kw(2, "it", 6), bank: kw(2, "sofa"), papa: kw(2, "dad"),
  dag2: zs(4), een: kw(4, "one"), dan: kw(4, "then"), tien: kw(4, "ten"),
  dag3: zs(6), schep: kw(6, "it", 7), onto: kw(6, "onto"), buren: kw(6, "neighbor"),
  oops: zs(7), eve: zs(8), zelf: kw(8, "then"), slot: zs(9), pop: kw(9, "robot"),
};
const F = (t: number) => Math.round(t * FPS);

export const KX = 200, BX = -200;
export type Place = "kamer" | "keuken" | "tuin" | "avond";
export type Shot = { id: number; a: number; b: number; place: Place };
const S = (id: number, a: number, b: number, place: Place): Shot => ({ id, a: F(a), b: F(b), place });
export const SHOTS: Shot[] = [
  S(1, 0, T.shiny, "kamer"),            // haak: robot rolt de kamer in, kerstboom en lichtjes
  S(2, T.shiny, T.polite, "kamer"),     // "Shiny." glans over het hoofd
  S(3, T.polite, T.little, "kamer"),    // "Polite." buiging
  S(4, T.little, zs(1), "kamer"),       // "A little too helpful." armen draaien, hartjesogen
  S(5, zs(1), zs(2), "kamer"),          // ROBOT: "Hello, family. I am here to help."
  S(6, zs(2), T.boom, "kamer"),         // "Day one. Mom asks it to decorate the tree."
  S(7, T.boom, T.bank, "kamer"),        // "It decorates the tree..."
  S(8, T.bank, T.papa, "kamer"),        // "the sofa..."
  S(9, T.papa, zs(3), "kamer"),         // "and Dad."
  S(10, zs(3), zs(4), "kamer"),         // DAD: "I can't feel my arms!"
  S(11, zs(4), T.een, "keuken"),        // "Day two. It bakes cookies."
  S(12, T.een, T.dan, "keuken"),        // "One cookie."
  S(13, T.dan, zs(5), "keuken"),        // "Then ten thousand cookies."
  S(14, zs(5), zs(6), "keuken"),        // SIS: "The cookies are everywhere!"
  S(15, zs(6), T.schep, "tuin"),        // "Day three. You ask it to shovel the snow."
  S(16, T.schep, T.onto, "tuin"),       // "It shovels all the snow..."
  S(17, T.onto, zs(7), "tuin"),         // "...onto the neighbor's house."
  S(18, zs(7), zs(8), "tuin"),          // YOU: "Oops. Sorry!"
  S(19, zs(8), T.zelf, "avond"),        // "Christmas Eve. It wraps every present."
  S(20, T.zelf, T.slot, "avond"),       // "Then it wraps itself."
  S(21, T.slot, EIND + 1, "avond"),     // "And that's why you never get a robot butler for Christmas."
];
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];

// ---------------- posities ----------------
export const KAMER = { tree: [-2.75, 0, -2.45] as V3, sofa: [0.6, 0, -2.75] as V3 };
export const MOM: V3 = [-0.55, 0, -1.4], MOM6: V3 = [-0.6, 0, -0.3], YOU: V3 = [0.95, 0, -1.0];       // shot 5 en 6 (verticaal beeld is smal: weinig mensen per shot)
export const DAD_K: V3 = [0.6, 0, -1.9];                  // vader na het versieren: voor de bank
export const SIS_K: V3 = [KX - 1.1, 0, 0.7];
export const YOU_A: V3 = [0.2, 0, -0.4];   // kerstavond (alleen in het slotshot, anders staat hij aan de rand)
export const YOU_T: V3 = [BX - 1.7, 0, 2.6];
export const BUUR: V3 = [BX + 7.5, 0, -6.5];              // huis van de buren (midden voorgevel)
export const ONS: V3 = [BX - 6.5, 0, -6.5];

// ---------------- robot ----------------
const pose = (o: Partial<RobotPose> & { pos: V3 }): RobotPose => ({ yaw: 0, bob: 0, armL: 0.25, armR: 0.25, elbL: 0.3, elbR: 0.3, head: 0, bow: 0, ogen: "gewoon", praat: 0, ...o });
const knipper = (t: number, o: Ogen): Ogen => (o === "gewoon" || o === "groot") && (t % 3.3) > 3.18 ? "dicht" : o;
export const robotAt = (t: number, s: Shot, praat: number): RobotPose => {
  const zweef = 0.03 * Math.sin(t * 3.1);
  switch (s.place) {
    case "kamer": {
      if (s.id <= 4) {
        const u = smooth(t / Math.max(0.1, T.shiny - 0.2));
        const pos = lerp3([1.5, 0, 1.3], [0.45, 0, 0.35], u);
        if (s.id === 1) return pose({ pos, yaw: lerp(-1.1, -0.15, u), bob: zweef, armR: 0.35 + 0.25 * Math.sin(t * 5), ogen: knipper(t, "gewoon") });
        if (s.id === 2) return pose({ pos: [0.45, 0, 0.35], yaw: -0.15, bob: zweef, ogen: "blij", head: 0.12 });
        if (s.id === 3) { const k = Math.sin(clamp01((t - T.polite) / 0.75) * Math.PI); return pose({ pos: [0.45, 0, 0.35], yaw: -0.15, bow: k, armR: 0.9 * k + 0.25, elbR: 1.4 * k + 0.3, ogen: k > 0.3 ? "dicht" : "gewoon" }); }
        return pose({ pos: [0.45, 0, 0.35], yaw: -0.15, bob: zweef, armL: 1.6 + 1.2 * Math.sin(t * 18), armR: 1.6 + 1.2 * Math.sin(t * 18 + 2), elbL: 0.2, elbR: 0.2, ogen: "hart" });
      }
      if (s.id === 5) return pose({ pos: [0.3, 0, 0.4], yaw: -0.25, bob: zweef, armR: 2.5 + 0.35 * Math.sin(t * 9), elbR: 0.4, ogen: praat > 0 ? "blij" : "gewoon", praat });
      if (s.id === 6) return pose({ pos: [-1.75, 0, -1.2], yaw: 0.9, bob: zweef, ogen: knipper(t, "groot"), head: -0.15 });
      // versieren: heen en weer zoeven met lichtjes (boom -> bank -> vader)
      const doel: V3 = s.id === 7 ? [-1.8, 0, -1.55] : s.id === 8 ? [2.3, 0, -1.4] : [2.2, 0, -1.3];
      const vorig: V3 = s.id === 7 ? [-1.75, 0, -1.2] : s.id === 8 ? [2.3, 0, -1.4] : [2.2, 0, -1.3];
      const u = smooth((t - s.a / FPS) / 0.35);
      if (s.id === 10) return pose({ pos: [1.9, 0, -0.85], yaw: -0.9, bob: zweef, ogen: "blij", armL: 0.4, armR: 2.6, elbR: 0.2 });
      return pose({ pos: lerp3(vorig, doel, u), yaw: s.id === 7 ? -2.2 : s.id === 8 ? 0.4 : -0.9, bob: zweef, armL: 1.5 + 0.9 * Math.sin(t * 22), armR: 1.5 + 0.9 * Math.sin(t * 22 + 1.5), elbL: 0.3, elbR: 0.3, ogen: "blij" });
    }
    case "keuken": {
      const pos: V3 = [KX + 0.35, 0, -1.75];
      if (s.id === 11) return pose({ pos, yaw: Math.PI * 0.92, bob: zweef, armL: 1.3, armR: 1.3, elbL: 0.6, elbR: 0.6, blik: true, ogen: knipper(t, "gewoon") });
      if (s.id === 12) return pose({ pos, yaw: 0.25, bob: zweef, armL: 1.35, armR: 1.35, elbL: 0.55, elbR: 0.55, blik: true, ogen: "blij" });
      return pose({ pos, yaw: 0.25 + 0.15 * Math.sin(t * 7), bob: zweef + 0.02 * Math.sin(t * 25), armL: 2.2 + 0.6 * Math.sin(t * 16), armR: 2.2 + 0.6 * Math.sin(t * 16 + 2), ogen: "groot" });
    }
    case "tuin": {
      const pos: V3 = [BX - 0.6, 0, 0.4];
      if (s.id === 15) return pose({ pos, yaw: -0.4, bob: zweef, armR: 1.1, elbR: 0.6, schep: true, ogen: knipper(t, "gewoon") });
      if (s.id === 16 || s.id === 17) {
        const k = (t * 3.2) % 1, zwaai = k < 0.55 ? lerp(0.3, 2.4, smooth(k / 0.55)) : lerp(2.4, 0.3, smooth((k - 0.55) / 0.45));
        return pose({ pos, yaw: 1.25, bob: zweef, armR: zwaai, elbR: 0.5, armL: zwaai * 0.8, elbL: 0.7, schep: true, ogen: "blij" });
      }
      return pose({ pos: [BX - 0.2, 0, 0.0], yaw: 0.9, bob: zweef, armR: 0.6, schep: true, ogen: "blij", head: 0.25 });
    }
    case "avond": {
      const pos: V3 = [-0.6, 0, -0.9];
      if (s.id === 19) return pose({ pos, yaw: 0.2, bob: zweef, armL: 1.5 + 0.9 * Math.sin(t * 24), armR: 1.5 + 0.9 * Math.sin(t * 24 + 2), ogen: "blij" });
      // slot: bij "robot butler" springt hij met zijn hoofd uit de doos (deksel omhoog) -> terug naar het begin (loop)
      if (s.id === 21 && t >= T.pop) { const u = smooth((t - T.pop) / 0.35); return pose({ pos: [pos[0], 0.62 * u, pos[2]], yaw: 0.2, armL: 2.6 * u, armR: 2.6 * u, elbL: 0.2, elbR: 0.2, ogen: "blij", head: 0.15 * Math.sin(t * 6) }); }
      return pose({ pos, yaw: 0.2, bob: 0, armL: 0.1, armR: 0.1, ogen: "groot", zicht: t < T.zelf + 0.9 });
    }
  }
};
/** cadeaudoos om de robot heen ("Then it wraps itself"): 0 = weg, 1 = dicht */
export const doosAt = (t: number) => (t < T.zelf + 0.2 ? 0 : smooth((t - T.zelf - 0.2) / 0.7));

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll?: number };
const K = (a: Cam, b: Cam, u: number): Cam => ({ pos: lerp3(a.pos, b.pos, smooth(u)), look: lerp3(a.look, b.look, smooth(u)), fov: lerp(a.fov, b.fov, smooth(u)) });
const C = (pos: V3, look: V3, fov = 42): Cam => ({ pos, look, fov });
const CAMS: Record<number, [Cam, Cam]> = {
  1: [C([1.6, 1.5, 4.6], [0.6, 1.05, 0.0], 46), C([0.7, 1.4, 3.4], [0.4, 1.1, -0.1], 44)],      // kijkt mee met de robot (camAt)
  2: [C([0.35, 1.62, 2.3], [0.45, 1.52, 0.35], 46), C([0.38, 1.6, 2.05], [0.45, 1.52, 0.35], 46)],
  3: [C([0.95, 1.2, 3.4], [0.45, 0.92, 0.35], 46), C([0.9, 1.2, 3.2], [0.45, 0.92, 0.35], 46)],
  4: [C([0.5, 1.2, 2.9], [0.45, 1.05, 0.2], 44), C([0.5, 1.25, 2.6], [0.45, 1.1, 0.2], 42)],
  5: [C([0.3, 1.35, 3.9], [0.25, 1.05, -0.8], 50), C([0.3, 1.35, 3.6], [0.25, 1.05, -0.8], 50)],
  6: [C([0.6, 1.5, 3.0], [-1.5, 1.1, -1.7], 50), C([0.45, 1.5, 2.75], [-1.5, 1.1, -1.7], 50)],
  7: [C([-0.6, 1.5, 1.9], [-2.4, 1.25, -2.2], 46), C([-0.7, 1.5, 1.7], [-2.4, 1.25, -2.2], 46)],
  8: [C([1.0, 1.35, 1.5], [0.5, 0.8, -2.7], 50), C([1.0, 1.35, 1.3], [0.5, 0.8, -2.7], 50)],
  9: [C([0.75, 1.35, 1.6], [0.75, 1.0, -1.9], 46), C([0.72, 1.33, 1.35], [0.75, 1.0, -1.9], 46)],
  10: [C([0.6, 1.15, 0.75], [0.6, 1.1, -1.9], 40), C([0.6, 1.15, 0.55], [0.6, 1.12, -1.9], 40)],
  11: [C([KX - 1.6, 1.6, 2.6], [KX + 0.3, 1.0, -2.2], 46), C([KX - 1.2, 1.55, 2.2], [KX + 0.3, 1.0, -2.2], 44)],
  12: [C([KX + 0.15, 1.45, -0.55], [KX + 0.4, 0.95, -1.2], 38), C([KX + 0.15, 1.4, -0.7], [KX + 0.4, 0.95, -1.2], 36)],
  13: [C([KX - 0.5, 1.7, 3.0], [KX + 0.2, 0.7, -1.8], 52), C([KX - 0.9, 1.9, 3.3], [KX + 0.2, 0.6, -1.6], 54)],
  14: [C([KX - 1.6, 0.95, 3.2], [KX - 1.15, 0.8, 0.0], 44), C([KX - 1.55, 0.95, 2.95], [KX - 1.15, 0.8, 0.0], 44)],
  15: [C([BX - 1.3, 1.1, 6.6], [BX - 1.15, 0.95, 1.0], 46), C([BX - 1.3, 1.1, 6.2], [BX - 1.15, 0.95, 1.0], 46)],
  16: [C([BX - 2.4, 1.5, 4.8], [BX + 1.2, 1.7, -3.0], 50), C([BX - 2.3, 1.5, 4.5], [BX + 1.2, 1.7, -3.0], 50)],
  17: [C([BX + 0.5, 3.0, 11.5], [BX + 5.2, 2.0, -4.5], 48), C([BX + 0.5, 3.4, 12.6], [BX + 5.0, 2.2, -4.5], 50)],
  18: [C([BX - 2.6, 1.0, 5.6], [BX + 0.3, 1.25, -2.0], 46), C([BX - 2.6, 1.0, 5.35], [BX + 0.3, 1.25, -2.0], 46)],
  19: [C([0.9, 1.5, 2.6], [-1.0, 0.9, -1.4], 46), C([0.7, 1.45, 2.2], [-1.0, 0.9, -1.4], 44)],
  20: [C([0.6, 1.4, 2.8], [-0.6, 0.95, -0.9], 46), C([0.5, 1.38, 2.5], [-0.6, 0.95, -0.9], 46)],
  21: [C([1.4, 1.4, 3.4], [-0.9, 1.0, -1.3], 46), C([1.0, 1.35, 2.8], [-0.8, 1.05, -1.2], 44)],
};
/** korte schok op klappen (seconden) */
export const KICKS = [T.tien + 0.3, T.onto + 0.5];
export const camAt = (f: number): Cam => {
  const s = shotAt(f), [a, b] = CAMS[s.id], u = (f - s.a) / Math.max(1, s.b - s.a);
  const c = K(a, b, u), t = f / FPS;
  if (s.id === 1) { const r = robotAt(t, s, 0).pos; c.look = [r[0] - 0.15, 1.05, r[2] - 0.3]; }
  const kick = KICKS.reduce((acc, k) => acc + Math.max(0, 1 - Math.abs(t - k) / 0.25) * Math.sin(t * 70), 0);
  c.pos = [c.pos[0] + kick * 0.03, c.pos[1] + kick * 0.04, c.pos[2]];
  return c;
};
/** scherptediepte per shot (lensblur cInf; groter = waziger achter het onderwerp) */
export const DOF: Record<number, number> = { 1: 8, 2: 14, 3: 10, 4: 10, 5: 8, 6: 9, 7: 9, 8: 8, 9: 10, 10: 14, 11: 8, 12: 14, 13: 6, 14: 9, 15: 6, 16: 8, 17: 4, 18: 3, 19: 9, 20: 12, 21: 9 };
