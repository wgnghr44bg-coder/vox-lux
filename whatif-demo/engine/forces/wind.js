// WIND: air moving over the ground (Earth stops spinning, hurricanes, ...).
// The physical quantity is wind speed in mph / 400 (1 = 400 mph, a strong tornado).
// TL.forceParams: { wind: v => mph from the counter value (default: the counter itself), dir: [dx, dz] }
import { baseForce } from './base.js';
import { smooth, hash, noise, clamp, lerp } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const toMph = P.wind || (v => v);
  const STOP = TL.beats.stop;
  let mph;
  const F = baseForce(E, TL, 'wind', ({ counter }) => { mph = t => Math.max(0, toMph(counter(Math.min(t, STOP)))); return t => mph(t) / 400; });
  const dir = P.dir || [0, 1];
  const airV = w => w <= 0 ? 0 : 15 * Math.pow(w / 100, 0.6);           // visual air speed (m/s)
  // cumulative air displacement, for dust that travels with the wind
  const DT = 1 / 60, D = [0];
  for (let i = 1; i <= (STOP + 1) / DT; i++) D.push(D[i - 1] + (airV(mph(i * DT)) + 1.2) * DT);
  const Dair = t => { const f = clamp(t, 0, STOP) / DT, i = Math.floor(f); return lerp(D[i], D[Math.min(i + 1, D.length - 1)], f - i); };
  Object.assign(F, {
    mph, Dair, dir,
    level: t => clamp(mph(t) / (P.max || 1037)),
    lateral: t => ({ a: mph(t) / 400, dx: dir[0], dz: dir[1] }),
    field: t => { const v = airV(mph(t)); return { g: 9.8, air: [dir[0] * v, 0, dir[1] * v], waterY: E.waterBase ?? -1e9 }; },
    fallMode: 'topple',
    wobble: t => smooth(30, 200, mph(t)) * .06,
    rumble: t => smooth(120, 400, mph(t)) * .025 + smooth(400, 700, mph(t)) * .05,
    kick: it => [dir[0] * 3, 1, dir[1] * 3],
    look(t, L) {
      const w = mph(t), haze = smooth(60, 250, w) * .3 + smooth(250, 450, w) * .35 + smooth(450, 800, w) * .25;
      L.fogNear = lerp(L.fogNear, 5, haze); L.fogFar = lerp(L.fogFar, 110, haze);
      L.hemi = lerp(L.hemi, L.hemi * .5, haze); L.sun = L.sun * (1 - smooth(.15, .9, haze) * .9);
      L.hemiColor.lerp(new E.THREE.Color(0xb9a88f), haze);
      L.fogColor = L.hor.clone().lerp(new E.THREE.Color(0x8a7b66), haze);
      L.haze = smooth(80, 400, w) * .14 + smooth(450, 800, w) * .2;
    },
  });
  F.dirFall = dir;
  // wind-borne dust: thin streaks low over the ground, then a brown fog of dust
  const DC = E.dustColor || [.6, .54, .46];
  E.emitters.push((tv, add, cam) => {
    const t = Math.min(tv, STOP), w = mph(t);
    const dens = smooth(40, 120, w) * .7 + smooth(180, 450, w) * .9 + smooth(450, 750, w) * 1.2;
    if (dens > 0) {
      const rate = 70, life = 4.5, A = E.windArea || { x: 30, z0: -20, z1: -180 };
      for (let k = Math.floor((t - life) * rate); k <= t * rate; k++) {
        if (k < 0) continue;
        const b = k / rate + hash(k, 1) / rate, a = t - b; if (a < 0 || a > life || hash(k, 2) > dens / 2.6) continue;
        const z0 = A.z0 + hash(k, 3) * (A.z1 - A.z0), x = (hash(k, 4) - .5) * A.x + noise(t, k) * 2;
        const z = z0 + (Dair(t) - Dair(b)) * .75 * dir[1], xx = x + (Dair(t) - Dair(b)) * .75 * dir[0], y = hash(k, 5) * hash(k, 5) * 18 + a * 1.2;
        if (z > cam.z - 6 && dir[1] > 0) continue;
        const s = 4 + hash(k, 6) * 9 + a * 2, al = smooth(0, .8, a) * (1 - smooth(life * .6, life, a)) * .26 * Math.min(1.4, dens), d = .9 + hash(k, 7) * .2;
        add(xx, y, z, s, al, DC[0] * d, DC[1] * d, DC[2] * d, hash(k, 8) * 6);
      }
    }
  });
  return F;
}
