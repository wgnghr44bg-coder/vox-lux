// Tijdlijn van de haai-proef (eerste 12,3 s van "What If You Built A Shark That Can Walk?"), getimed op woorden.json.
// Camera-grammatica van de skill: trage push-ins, cuts op de woorden, korte kick-schok bij de klap.
export const FPS = 30;
export const TOTAL = 370;
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };

// tijden (s) uit de stem / sfx.wav van short-haai
export const T_BONK = [8.53, 8.93];      // haai bonkt tegen de dichte deur (sfx "bonk")
export const T_DEUR = 10.21;             // deur breekt (sfx "krak")
export const T_STAP0 = 10.41;            // stappen elke 0,45 s

export type Shot = { id: number; a: number; b: number; place: "binnen" | "buiten" };
export const SHOTS: Shot[] = [
  { id: 1, a: 0, b: 77, place: "binnen" },    // hook: "What if you built a shark that can walk?"
  { id: 2, a: 77, b: 110, place: "binnen" },  // "Big legs."
  { id: 3, a: 110, b: 143, place: "binnen" }, // "Tiny arms."
  { id: 4, a: 143, b: 172, place: "binnen" }, // "Zero brain."
  { id: 5, a: 172, b: 232, place: "binnen" }, // jij: "Okay, buddy. Just one step."
  { id: 6, a: 232, b: 370, place: "buiten" }, // "It takes one step. Then it walks straight through the garage door."
];
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];

// haai staat in de garage op x = 0, z = -4.6 (neus naar +x). Na de klap loopt hij naar buiten (+z).
export const SHARK_HOME: V3 = [-0.2, 0, -4.4];
export const sharkAt = (t: number): { pos: V3; dir: V3; walk: number; phase: number } => {
  if (t < T_DEUR - 0.25) {
    const step = t >= 7.9 && t < T_DEUR ? 1 : 0;      // "takes one step": loopt tegen de deur
    const z = t < 7.9 ? SHARK_HOME[2] : -4.4 + Math.min(3.2, (t - 7.9) * 1.6);
    return { pos: [SHARK_HOME[0], 0, z], dir: step ? [0, 0, 1] : [1, 0, 0], walk: step ? 1 : 0.12, phase: (t * 1.1) % 1 };
  }
  const u = t - (T_DEUR - 0.25), z = -1.2 + u * 1.55;
  return { pos: [SHARK_HOME[0], 0, z], dir: [0, 0, 1], walk: 1, phase: ((t - T_STAP0) / 0.9 + 10) % 1 };
};
export const KID_IN: V3 = [2.1, 0, -1.6];
export const KID_OUT: V3 = [2.7, 0, 3.2];

type Cam = { pos: V3; look: V3; fov: number; roll?: number };
type Key = { f: number; c: Cam };
const lerp3 = (a: V3, b: V3, k: number): V3 => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
const along = (keys: Key[], f: number, ease = smooth): Cam => {
  if (f <= keys[0].f) return keys[0].c;
  for (let i = 1; i < keys.length; i++) if (f <= keys[i].f) {
    const a = keys[i - 1], b = keys[i], k = ease((f - a.f) / (b.f - a.f));
    return { pos: lerp3(a.c.pos, b.c.pos, k), look: lerp3(a.c.look, b.c.look, k), fov: a.c.fov + (b.c.fov - a.c.fov) * k, roll: (a.c.roll ?? 0) + ((b.c.roll ?? 0) - (a.c.roll ?? 0)) * k };
  }
  return keys[keys.length - 1].c;
};
const lin = (u: number) => clamp01(u);

export const CAMS: Record<number, Key[]> = {
  1: [{ f: 0, c: { pos: [1.2, 1.25, -0.35], look: [0.15, 1.05, -4.5], fov: 54 } }, { f: 77, c: { pos: [0.95, 1.2, -1.0], look: [0.2, 1.05, -4.5], fov: 50 } }],
  2: [{ f: 77, c: { pos: [1.0, 0.35, -1.9], look: [0.4, 0.45, -4.4], fov: 46, roll: 0.03 } }, { f: 110, c: { pos: [0.95, 0.3, -2.2], look: [0.4, 0.42, -4.4], fov: 44, roll: 0.03 } }],
  3: [{ f: 110, c: { pos: [0.75, 1.1, -2.7], look: [0.5, 1.02, -4.4], fov: 36 } }, { f: 143, c: { pos: [0.72, 1.1, -2.95], look: [0.5, 1.02, -4.4], fov: 33 } }],
  4: [{ f: 143, c: { pos: [0.85, 1.7, -2.75], look: [0.72, 1.62, -4.4], fov: 34 } }, { f: 172, c: { pos: [0.83, 1.7, -3.0], look: [0.72, 1.62, -4.4], fov: 30 } }],
  5: [{ f: 172, c: { pos: [-0.2, 1.2, -2.45], look: [2.1, 0.95, -1.6], fov: 42 } }, { f: 232, c: { pos: [0.1, 1.2, -2.3], look: [2.1, 0.95, -1.6], fov: 40 } }],
  6: [{ f: 232, c: { pos: [5.6, 1.55, 9.6], look: [-0.6, 1.3, 0.6], fov: 50 } }, { f: 300, c: { pos: [5.2, 1.5, 9.0], look: [-0.6, 1.3, 0.6], fov: 48 } },
      { f: 370, c: { pos: [4.6, 1.4, 8.6], look: [-0.4, 1.2, 1.6], fov: 47 } }],
};
// kick: 7 frames, teken wisselt elke frame (skill), op de klap en zachter op de bonks
const KICKS: [number, number][] = [[Math.round(T_DEUR * FPS), 1], [Math.round(T_BONK[0] * FPS), 0.35], [Math.round(T_BONK[1] * FPS), 0.35]];
export const camAt = (f: number): Cam => {
  const s = shotAt(f), c = along(CAMS[s.id], f, s.id === 6 ? lin : smooth);
  let dy = 0, rl = 0;
  for (const [kf, a] of KICKS) { const d = f - kf; if (d >= 0 && d < 7 && s.id === 6) { const k = a * (1 - d / 7) * (d % 2 ? -1 : 1); dy += 0.06 * k; rl += 0.012 * k; } }
  return { pos: [c.pos[0], c.pos[1] + dy, c.pos[2]], look: c.look, fov: c.fov, roll: (c.roll ?? 0) + rl };
};
// lensblur per shot: cInf (px bij oneindig), focus = kijkpunt
export const DOF: Record<number, number> = { 1: 9, 2: 12, 3: 16, 4: 16, 5: 12, 6: 7 };
// wit flitsje na de hook-vraag (skill: FLASH_AT na de hook)
export const FLASH_AT = 77;
