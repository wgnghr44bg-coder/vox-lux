// AUTO BLOCK crowd-jump: everybody jumps at the same moment - every person in the place bends the knees and jumps
// (about half a metre, real physics: up and down in ~0.65 s), optionally a few times; an extra crowd can be added
// so the street or square is full. Landing gives a small thud (E.EVENTS 'stomp').
// Use in scenario.js:  auto: [{ block: 'crowd-jump', at: 24, height: .5, count: 1, gap: 2, pos: [0, 0, 10], extra: 60, r: 22 }]
//   at: s of the (first) jump; height: metres (an average person ~0.4-0.5); count/gap: repeat jumps every gap s;
//   pos + extra + r: add `extra` people standing within r metres of pos (they look up / around, then jump too).
import { person } from '../props.js';

const rng = seed => () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;

export default function build(E, TL, o, F) {
  const at = o.at ?? 10, H = o.height ?? .5, count = o.count ?? 1, gap = o.gap ?? 2, R = rng(71);
  const v0 = Math.sqrt(2 * 9.81 * H), air = 2 * v0 / 9.81, crouch = .28;
  // the extra crowd: standing people facing roughly the same way, spread over a circle
  if (o.extra && o.pos) {
    const [cx, , cz] = o.pos, r = o.r ?? 20;
    for (let i = 0; i < o.extra; i++) {
      const a = R() * Math.PI * 2, d = Math.sqrt(R()) * r, x = cx + Math.cos(a) * d, z = cz + Math.sin(a) * d, rot = (R() - .5) * 1.2 + (o.face ?? 0);
      person(E, 4000 + i, { path: () => ({ x, z, rot, moving: 0, speed: 0 }) });
    }
  }
  for (let k = 0; k < count; k++) (E.EVENTS ||= []).push({ t: at + k * gap + crouch + air, kind: 'stomp', e: .25, x: o.pos?.[0] ?? 0, z: o.pos?.[2] ?? 0 });
  // each person a tiny bit early or late (people are not perfectly in sync)
  const lag = new Map();
  const offset = (p, t) => {
    if (!lag.has(p)) lag.set(p, (R() - .5) * .16);
    const t0 = t - at - lag.get(p);
    for (let k = 0; k < count; k++) {
      const u = t0 - k * gap;
      if (u < 0 || u > crouch + air + .2) continue;
      if (u < crouch) return { y: -.12 * Math.sin(u / crouch * Math.PI), s: 1 - .08 * Math.sin(u / crouch * Math.PI) };   // knees bend
      const f = u - crouch;
      if (f < air) return { y: v0 * f - 4.905 * f * f, s: 1 };                                                       // in the air
      return { y: -.08 * Math.sin((f - air) / .2 * Math.PI), s: 1 - .05 * Math.sin((f - air) / .2 * Math.PI) };      // landing
    }
    return null;
  };
  return (t) => {
    for (const p of E.people || []) {
      if (!p.g?.visible) continue;
      const j = offset(p, t); if (!j) continue;
      p.g.position.y += j.y; p.g.scale.y = p.g.scale.x * j.s;
    }
  };
}
