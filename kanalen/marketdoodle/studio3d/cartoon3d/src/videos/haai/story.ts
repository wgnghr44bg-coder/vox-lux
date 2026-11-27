// Tijdlijn van de hele haai-short ("What If You Built A Shark That Can Walk?", 42,5 s) in de cartoon-3D-stijl,
// getimed op short-haai/woorden.json en sfx.wav. Camera-grammatica van de skill: trage push-ins, cuts op de woorden,
// korte kick-schok bij klappen. Plekken liggen ver uit elkaar in één wereld (garage/straat rond x=0, keuken KX, strand BX, bad AX).
export const FPS = 30;
export const EIND = 41.846 + 0.7;                 // zelfde einde als de 2D-short (loop naar de eerste zin)
export const TOTAL = Math.round(EIND * FPS);
export type V3 = [number, number, number];
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };

// tijden (s) uit de stem / sfx.wav van short-haai
export const T_BONK = [8.53, 8.93];
export const T_DEUR = 10.21;
export const T_STAP0 = 10.41;
export const T_NOBODY = 14.9;
export const T_NAAR = 20.46, T_EET = 21.97, T_SLOK = 23.27;
export const T_HAP = [T_EET, T_EET + 0.4, T_EET + 0.8];
export const T_ZEE = 28.84, T_IN = 29.6, T_KEER = 30.45, T_UIT = 30.95;
export const T_LAMP = 37.09;

export const KX = 200, BX = -1000, AX = 400;
export type Place = "binnen" | "buiten" | "straat" | "keuken" | "strand" | "bad";
export type Shot = { id: number; a: number; b: number; place: Place };
export const SHOTS: Shot[] = [
  { id: 1, a: 0, b: 77, place: "binnen" },      // hook: "What if you built a shark that can walk?"
  { id: 2, a: 77, b: 110, place: "binnen" },    // "Big legs."
  { id: 3, a: 110, b: 143, place: "binnen" },   // "Tiny arms."
  { id: 4, a: 143, b: 172, place: "binnen" },   // "Zero brain."
  { id: 5, a: 172, b: 232, place: "binnen" },   // jij: "Okay, buddy. Just one step."
  { id: 6, a: 232, b: 370, place: "buiten" },   // "It takes one step. Then it walks straight through the garage door."
  { id: 7, a: 370, b: 447, place: "straat" },   // "Day 1. It walks your sister to school."
  { id: 8, a: 447, b: 508, place: "straat" },   // "Nobody bullies her ever again."
  { id: 9, a: 508, b: 559, place: "straat" },   // zus: "Best bodyguard ever!"
  { id: 10, a: 559, b: 614, place: "keuken" },  // "Day 2. It's hungry."
  { id: 11, a: 614, b: 657, place: "keuken" },  // "It walks to the fridge..."
  { id: 12, a: 657, b: 709, place: "keuken" },  // "...and eats the whole fridge."
  { id: 13, a: 709, b: 772, place: "keuken" },  // vader: "That was a brand new fridge!"
  { id: 14, a: 772, b: 860, place: "strand" },  // "Day 3. You take it to the beach."
  { id: 15, a: 860, b: 955, place: "strand" },  // "It walks into the sea... and walks right back out."
  { id: 16, a: 955, b: 1027, place: "strand" }, // jij: "Wait. Are you scared of water?"
  { id: 17, a: 1027, b: 1150, place: "bad" },   // "So now your shark sleeps in your bathtub. With a night light."
  { id: 18, a: 1150, b: TOTAL, place: "bad" },  // "And that's why you never build a shark that can walk."
];
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];

// ---------------- waar is iedereen ----------------
export type SharkState = { pos: V3; dir: V3; walk: number; phase: number; look: "dumb" | "happy" | "focus" | "sleep" | "scared"; chomp: number; shiver: number; arm: number };
export const SHARK_HOME: V3 = [-0.2, 0, -4.4];
const ST_X0 = -30, ST_V = 1.25, ST_T0 = 12.33, ST_STOP = 16.9;
export const streetX = (t: number) => ST_X0 + ST_V * (Math.min(t, ST_STOP) - ST_T0);
const beachZ = (t: number) => {
  if (t < T_ZEE) return 1.0;
  if (t < T_KEER) return 1.0 - 1.3 * (t - T_ZEE);
  const zk = 1.0 - 1.3 * (T_KEER - T_ZEE);
  return Math.min(1.8, zk + 2.0 * (t - T_KEER));
};
export const sharkAt = (t: number, s: Shot): SharkState => {
  const base = { chomp: 0, shiver: 0, arm: 0.15 + 0.1 * Math.sin(t * 3) };
  switch (s.place) {
    case "binnen": case "buiten": {
      if (t < T_DEUR - 0.25) {
        const step = t >= 7.9 && t < T_DEUR;
        const z = t < 7.9 ? SHARK_HOME[2] : -4.4 + Math.min(3.2, (t - 7.9) * 1.6);
        return { ...base, pos: [SHARK_HOME[0], 0, z], dir: step ? [0, 0, 1] : [1, 0, 0], walk: step ? 1 : 0.12, phase: (t * 1.1) % 1, look: "dumb",
          arm: s.id === 3 ? 0.5 + 0.5 * Math.sin(t * 14) : base.arm };
      }
      const u = t - (T_DEUR - 0.25);
      return { ...base, pos: [SHARK_HOME[0], 0, -1.2 + u * 1.55], dir: [0, 0, 1], walk: 1, phase: ((t - T_STAP0) / 0.9 + 10) % 1, look: "happy" };
    }
    case "straat": {
      const walking = t < ST_STOP;
      return { ...base, pos: [streetX(t) - 0.4, 0, 9.55], dir: [1, 0, 0], walk: walking ? 0.8 : 0.1, phase: ((t - ST_T0) / 0.9) % 1,
        look: t > T_NOBODY && t < 16.6 ? "focus" : "happy", chomp: t > T_NOBODY + 0.3 && t < T_NOBODY + 0.9 ? 0.6 : 0 };
    }
    case "keuken": {
      const x = t < T_NAAR ? KX - 0.6 : KX - 0.6 + 1.3 * Math.min(t - T_NAAR, 1.41);
      const walking = t >= T_NAAR && t < T_NAAR + 1.41;
      const ch = T_HAP.reduce((a, th) => a + Math.max(0, 1 - Math.abs(t - th - 0.08) / 0.16), 0);
      return { ...base, pos: [x, 0, -2.0], dir: [1, 0, 0], walk: walking ? 0.9 : 0.1, phase: ((t - T_NAAR) / 0.9 + 10) % 1,
        look: t < T_NAAR ? "focus" : t > T_SLOK ? "happy" : "dumb", chomp: Math.min(1, ch), arm: t < T_NAAR ? 0.6 + 0.3 * Math.sin(t * 8) : base.arm };
    }
    case "strand": {
      const z = beachZ(t), y = Math.min(0, z * 0.95);
      const into = t >= T_ZEE && t < T_KEER, back = t >= T_KEER && z < 1.79;
      return { ...base, pos: [BX - 0.2, y, z], dir: back ? [0, 0, 1] : [0, 0, -1], walk: into || back ? 1 : 0.1, phase: ((t - T_ZEE) / (back ? 0.6 : 0.9) + 10) % 1,
        look: t >= T_KEER ? "scared" : "happy", shiver: t >= T_KEER ? t : 0 };
    }
    case "bad":
      return { ...base, pos: [AX - 0.35, 0, -2.45], dir: [1, 0, 0], walk: 0, phase: 0, look: t > 34.6 ? "sleep" : "happy", arm: 0.1 };
  }
};
// het kind ("jij"), de zus, pestkoppen, vader
export const KID_IN: V3 = [2.1, 0, -1.6];
export const KID_OUT: V3 = [2.7, 0, 3.2];
export const KID_BEACH: V3 = [BX + 2.0, 0, 3.4];
export const sisAt = (t: number): V3 => [streetX(t) + 0.9, 0, 10.45];
export const BULLY0: V3[] = [[-21.2, 0, 10.0], [-20.3, 0, 10.6]];
export const bullyAt = (i: number, t: number): V3 => {
  const r = Math.max(0, t - (T_NOBODY + 0.55 + i * 0.12));
  return [BULLY0[i][0] + 4.2 * r, 0, BULLY0[i][2] + 1.2 * r * (i ? 1 : -0.4)];
};
export const DAD_POS: V3 = [KX - 2.3, 0, 0.9];

// ---------------- camera ----------------
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
const two = (a: number, b: number, c0: Cam, c1: Cam): Key[] => [{ f: a, c: c0 }, { f: b, c: c1 }];

export const CAMS: Record<number, Key[]> = {
  1: two(0, 77, { pos: [1.2, 1.25, -0.35], look: [0.15, 1.05, -4.5], fov: 54 }, { pos: [0.95, 1.2, -1.0], look: [0.2, 1.05, -4.5], fov: 50 }),
  2: two(77, 110, { pos: [1.0, 0.35, -1.9], look: [0.4, 0.45, -4.4], fov: 46, roll: 0.03 }, { pos: [0.95, 0.3, -2.2], look: [0.4, 0.42, -4.4], fov: 44, roll: 0.03 }),
  3: two(110, 143, { pos: [0.75, 1.1, -2.7], look: [0.5, 1.02, -4.4], fov: 36 }, { pos: [0.72, 1.1, -2.95], look: [0.5, 1.02, -4.4], fov: 33 }),
  4: two(143, 172, { pos: [0.85, 1.7, -2.75], look: [0.72, 1.62, -4.4], fov: 34 }, { pos: [0.83, 1.7, -3.0], look: [0.72, 1.62, -4.4], fov: 30 }),
  5: two(172, 232, { pos: [-0.2, 1.2, -2.45], look: [2.1, 0.95, -1.6], fov: 42 }, { pos: [0.1, 1.2, -2.3], look: [2.1, 0.95, -1.6], fov: 40 }),
  6: [{ f: 232, c: { pos: [5.6, 1.55, 9.6], look: [-0.6, 1.3, 0.6], fov: 50 } }, { f: 300, c: { pos: [5.2, 1.5, 9.0], look: [-0.6, 1.3, 0.6], fov: 48 } },
      { f: 370, c: { pos: [4.6, 1.4, 8.6], look: [-0.4, 1.2, 1.6], fov: 47 } }],
  8: two(447, 508, { pos: [-15.5, 1.4, 15.5], look: [-22.8, 1.0, 10.2], fov: 46 }, { pos: [-15.8, 1.4, 15.1], look: [-22.4, 1.0, 10.2], fov: 44 }),
  9: two(508, 559, { pos: [-22.2, 1.05, 14.6], look: [-23.6, 0.72, 10.2], fov: 40 }, { pos: [-22.4, 1.05, 14.2], look: [-23.6, 0.72, 10.2], fov: 38 }),
  10: two(559, 614, { pos: [KX - 0.4, 1.65, 3.6], look: [KX + 0.6, 1.0, -2.2], fov: 56 }, { pos: [KX - 0.2, 1.6, 3.2], look: [KX + 0.6, 1.0, -2.2], fov: 53 }),
  11: two(614, 657, { pos: [KX - 0.2, 1.6, 3.2], look: [KX + 0.8, 1.0, -2.2], fov: 53 }, { pos: [KX + 0.4, 1.55, 2.6], look: [KX + 1.6, 1.0, -2.4], fov: 50 }),
  12: two(657, 709, { pos: [KX + 1.3, 1.3, 0.9], look: [KX + 2.3, 1.15, -2.7], fov: 48 }, { pos: [KX + 1.4, 1.3, 0.6], look: [KX + 2.3, 1.1, -2.7], fov: 46 }),
  13: two(709, 772, { pos: [KX - 0.5, 1.25, 3.4], look: [KX - 2.1, 1.0, 0.9], fov: 42 }, { pos: [KX - 0.7, 1.25, 3.2], look: [KX - 2.1, 1.0, 0.9], fov: 39 }),
  14: two(772, 860, { pos: [BX + 1.2, 1.7, 10.5], look: [BX + 0.2, 1.0, 0.5], fov: 50 }, { pos: [BX + 1.0, 1.6, 9.4], look: [BX + 0.2, 1.0, 0.5], fov: 48 }),
  15: two(860, 955, { pos: [BX + 5.2, 1.35, 4.6], look: [BX - 0.2, 0.7, -0.2], fov: 46 }, { pos: [BX + 4.8, 1.3, 4.3], look: [BX - 0.2, 0.7, -0.2], fov: 44 }),
  16: two(955, 1027, { pos: [BX + 3.6, 1.15, 7.4], look: [BX + 1.1, 0.75, 2.7], fov: 44 }, { pos: [BX + 3.4, 1.15, 7.0], look: [BX + 1.1, 0.75, 2.7], fov: 42 }),
  17: two(1027, 1150, { pos: [AX + 0.9, 1.55, 2.5], look: [AX, 1.1, -2.4], fov: 52 }, { pos: [AX + 0.8, 1.5, 1.6], look: [AX, 1.1, -2.4], fov: 50 }),
  18: two(1150, TOTAL, { pos: [AX + 0.85, 1.75, 0.6], look: [AX + 0.6, 1.62, -2.45], fov: 40 }, { pos: [AX + 0.75, 1.75, -0.3], look: [AX + 0.6, 1.62, -2.45], fov: 36 }),
};
// shot 7: meerijdende camera langs de stoep
const cam7 = (f: number): Cam => { const t = f / FPS, x = streetX(t); return { pos: [x + 0.6, 1.45, 17.6], look: [x + 0.6, 1.0, 10.0], fov: 46 }; };

const KICKS: [number, number][] = [[Math.round(T_DEUR * FPS), 1], [Math.round(T_BONK[0] * FPS), 0.35], [Math.round(T_BONK[1] * FPS), 0.35],
  ...T_HAP.map((t) => [Math.round(t * FPS), 0.45] as [number, number]), [Math.round(T_IN * FPS), 0.3]];
export const camAt = (f: number): Cam => {
  const s = shotAt(f), c = s.id === 7 ? cam7(f) : along(CAMS[s.id], f, s.id === 6 ? lin : smooth);
  let dy = 0, rl = 0;
  for (const [kf, a] of KICKS) { const d = f - kf; if (d >= 0 && d < 7 && s.id !== 2 && s.id !== 1) { const k = a * (1 - d / 7) * (d % 2 ? -1 : 1); dy += 0.06 * k; rl += 0.012 * k; } }
  return { pos: [c.pos[0], c.pos[1] + dy, c.pos[2]], look: c.look, fov: c.fov, roll: (c.roll ?? 0) + rl };
};
// lensblur per shot: cInf (px bij oneindig)
export const DOF: Record<number, number> = { 1: 9, 2: 12, 3: 16, 4: 16, 5: 12, 6: 7, 7: 8, 8: 8, 9: 12, 10: 8, 11: 8, 12: 12, 13: 12, 14: 7, 15: 8, 16: 11, 17: 9, 18: 13 };
export const FLASH_AT = 77;
