// ZOMBIES (baksteen, okt 2026): low-poly cartoon zombies (props.js person with o.zombie: grey-green skin, drab clothes,
// arms out in front, a slow shuffle, head on one side). No gore, nobody gets touched: they only walk.
//   TL.zombies = [{ n, path: [[t, x, z], ...], spread: 1.5, lag: .6, speed: .8, hideAfter: true, y }]
//   path: waypoints in video time (the group shuffles along it, each one `lag` s later and a little to the side);
//   hideAfter: gone after the last waypoint (e.g. through a door). gather: true = stay there, crowded, arms up (at a door).
//   y: ground height (default .2).
import { person } from './props.js';
import { rng, clamp, lerp } from './util.js';

function along(pts, t) {
  if (t <= pts[0][0]) return { x: pts[0][1], z: pts[0][2], rot: Math.atan2(pts[1][1] - pts[0][1], pts[1][2] - pts[0][2]), moving: 0, before: true };
  for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) {
    const [ta, xa, za] = pts[i - 1], [tb, xb, zb] = pts[i], k = clamp((t - ta) / (tb - ta || 1));
    return { x: lerp(xa, xb, k), z: lerp(za, zb, k), rot: Math.atan2(xb - xa, zb - za), moving: Math.hypot(xb - xa, zb - za) > .05 ? 1 : 0 };
  }
  const n = pts.length, [, xa, za] = pts[n - 2], [, xb, zb] = pts[n - 1];
  return { x: xb, z: zb, rot: Math.atan2(xb - xa, zb - za), moving: 0, after: true };
}

export function zombies(E, TL) {
  (TL.zombies || []).forEach((G, gi) => {
    const R = rng(4400 + gi);
    for (let i = 0; i < (G.n ?? 6); i++) {
      const lag = i * (G.lag ?? .6) + R() * .3, side = (R() - .5) * 2 * (G.spread ?? 1.5), back = (R() - .5) * .8;
      const pts = G.path.map(([t, x, z]) => [t + lag, x, z]);
      person(E, 9000 + gi * 100 + i, { zombie: true, skirt: false, y: G.y ?? .2, path(t) {
        const p = along(pts, t);
        if (p.after && !G.gather && G.hideAfter !== false) return { visible: false };
        const sx = Math.cos(p.rot), sz = -Math.sin(p.rot);
        return { x: p.x + sx * side + Math.sin(p.rot) * back, z: p.z + sz * side + Math.cos(p.rot) * back, rot: p.rot + Math.sin(t * .7 + i) * .12,
                 moving: p.moving, speed: (G.speed ?? .8) * .55, arms: p.after && G.gather ? 'zombieUp' : 'zombie' };
      } });
    }
  });
}
