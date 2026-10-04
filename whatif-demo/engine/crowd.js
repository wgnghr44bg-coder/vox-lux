// People that walk along a lane (axis 'x' or 'z'), react to the force, and go inside before the
// destruction starts (no one is ever hurt on screen). Beats used: lookUp, shelter.
import { person } from './props.js';
import { rng, smooth, clamp } from './util.js';

export function crowd(E, TL, o) {
  const { n, axis = 'x', lane, range, door, seed = 31, y = .2 } = o;     // lane: [min, max] across; range: [a, b] along
  const B = TL.beats, R = rng(seed);
  const lookUp = B.lookUp ?? 1e9, shelter = B.shelter ?? 1e9;
  for (let i = 0; i < n; i++) {
    const across = lane[0] + R() * (lane[1] - lane[0]), s0 = range[0] + R() * (range[1] - range[0]);
    const dir = R() < .5 ? -1 : 1, v = 1.1 + R() * .4, look = lookUp + R() * 1.5, go = shelter + R() * 2.5;
    const sitter = o.benches && R() < .25 ? o.benches[Math.floor(R() * o.benches.length)] : null;
    const len = range[1] - range[0];
    const wrap = q => range[0] + ((q - range[0]) % len + len) % len;
    person(E, seed * 100 + i, { y, coat: o.coats ? o.coats[Math.floor(R() * o.coats.length)] : undefined, hat: o.hats && R() < .5 ? o.hats[Math.floor(R() * o.hats.length)] : undefined,
      path(t, F) {
        const d = F.droop(t), kind = F.kind;
        // distance walked: integrate the speed, which drops as gravity grows
        const steps = 24, tt = Math.min(t, go); let dist = 0;
        for (let k = 0; k < steps; k++) { const tk = tt * (k + .5) / steps; dist += v / (1 + 2.2 * F.droop(tk)) * (kind === 'wind' && tk > look ? 0 : 1); }
        dist *= tt / steps;
        let along = wrap(s0 + dir * dist), acr = across, rot = axis === 'x' ? (dir > 0 ? Math.PI / 2 : -Math.PI / 2) : (dir > 0 ? 0 : Math.PI);
        let moving = t < go ? 1 : 0, speed = v / (1 + 2.2 * d), stoop = clamp(d * .32 + (kind === 'cold' ? F.level(t) * .15 : 0), 0, .45), headUp = 0;
        if (kind === 'wind' && t > look && t < go) { moving = 0; headUp = smooth(look, look + .8, t) * .5; rot += Math.sin((t - look) * .9 + i) * 1.2; }
        if (t >= go) {                       // walk (or hurry) to the nearest door and go in
          const target = door(along, acr), tr = t - go, vs = kind === 'gravity' ? .9 / (1 + d) : kind === 'wind' ? 4.2 : 2.2;
          const dd = Math.abs(target - acr), mv = Math.min(dd, tr * vs);
          acr += Math.sign(target - acr) * mv;
          rot = axis === 'x' ? (target > acr ? 0 : Math.PI) : (target > acr ? Math.PI / 2 : -Math.PI / 2);
          moving = kind === 'wind' ? 2 : 1; speed = vs; headUp = 0;
          if (mv >= dd - .3) return { visible: false };
        }
        if (sitter && t > (B.sit ?? 1e9) && t < go) { along = sitter[0]; acr = sitter[1]; moving = 0; rot = sitter[2]; return { x: axis === 'x' ? along : acr, z: axis === 'x' ? acr : along, y: -.35, rot, moving: 0, speed: 0, stoop: stoop * .5 }; }
        return axis === 'x' ? { x: along, z: acr, rot, moving, speed, stoop, headUp } : { x: acr, z: along, rot, moving, speed, stoop, headUp };
      } });
  }
}
