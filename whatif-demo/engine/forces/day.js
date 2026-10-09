// DAY / TIME OF DAY: no destruction; the clock drives the light. The counter is free (crowd, heat …);
// its 0..1 level is the "excitement" the sound follows (crowd murmur → roar in make_audio.py).
// TL.forceParams: { hours: [[t, hour], ...] (24 h clock, e.g. [[0, 5.6], [60, 6.6]]),
//                   sunrise: 6, sunset: 19.6, azimuth: degrees the sun turns from east (default 0 = +x) }
// Sets L.dark (lamps, torches, windows) from the sun height; place lights read E.dark.
import { baseForce } from './base.js';
import { smooth, lerp, monotone, clamp } from '../util.js';

export function create(E, TL) {
  const P = TL.forceParams || {};
  const F = baseForce(E, TL, 'day');
  const hourAt = monotone(P.hours || [[0, 9]]), rise = P.sunrise ?? 6, set = P.sunset ?? 19.6;
  const N = c => new E.THREE.Color(c), D = Math.PI / 180;
  // sky keys by hour: [hour, top, horizon, sun colour, sun strength, hemi]
  const K = [[0, 0x070b16, 0x141c2c, 0x000000, 0, .25], [4.6, 0x0b1222, 0x1e2536, 0x000000, 0, .3],
             [5.4, 0x27345a, 0x8a6a62, 0x000000, 0, .5], [5.9, 0x45608f, 0xe3a173, 0xff9a5a, .5, .8],
             [6.6, 0x6286b8, 0xf0c48e, 0xffc48a, 1.4, 1.1], [8, 0x6d99c9, 0xdcdcd0, 0xffe2bc, 2.1, 1.4],
             [11, 0x5b93cd, 0xd6e0e4, 0xfff4e4, 2.6, 1.55], [14, 0x5b93cd, 0xdfe2df, 0xfff1dc, 2.6, 1.55],
             [17, 0x6c94c0, 0xe6d4ac, 0xffdcaa, 2.1, 1.35], [18.9, 0x5a6f9c, 0xf0a46a, 0xff9a52, 1.2, 1],
             [19.7, 0x34406a, 0xa86a5c, 0xc0603a, .2, .6], [20.4, 0x111a30, 0x2b2c3c, 0x000000, 0, .32], [24, 0x070b16, 0x141c2c, 0x000000, 0, .25]];
  const key = (h, j) => { let i = 0; while (i < K.length - 2 && h > K[i + 1][0]) i++; const a = K[i], b = K[i + 1], u = smooth(a[0], b[0], h);
    return j < 4 ? N(a[j]).lerp(N(b[j]), u) : lerp(a[j], b[j], u); };
  const elev = h => Math.sin(Math.PI * clamp((h - rise) / (set - rise), -.1, 1.1)) * 66;     // degrees above the horizon
  const dark = h => 1 - smooth(-6, 6, h < 12 ? (h - rise) * 12 : (set - h) * 12);           // 1 at night, 0 by day
  Object.assign(F, {
    hour: t => hourAt(Math.min(t, TL.T_END)),
    dark: t => dark(F.hour(t)),
    fallMode: 'pancake',
    look(t, L) {
      const h = F.hour(t), d = dark(h);
      L.top = key(h, 1); L.hor = key(h, 2); L.fogColor = L.hor.clone().lerp(N(0x9a9488), .15);
      L.sunColor = key(h, 3); L.sun = key(h, 4) * (L.sunScale ?? 1); L.hemi = key(h, 5); L.sunDisc = L.sunColor.clone().multiplyScalar(.8);
      L.hemiColor = N(0xe3ecf4).lerp(N(0x6a7aa0), d).lerp(N(0xf0c8a0), smooth(4.8, 6, h) * (1 - smooth(6.5, 8, h)) * .5);
      L.stars = smooth(.6, 1, d); L.dark = d; L.dustLight = 1 - d * .5;
      L.fogFar = lerp(L.fogFar ?? 900, 900, d);
      // sun path: rises in the east (+x), highest in the south (+z), sets in the west
      const az = (P.azimuth ?? 0) * D + Math.PI * clamp((h - rise) / (set - rise), -.1, 1.1), el = Math.max(2, elev(h)) * D;
      E.sunOffset?.set(Math.cos(az) * Math.cos(el) * 220, Math.sin(el) * 220, Math.sin(az) * Math.cos(el) * 220);
    },
  });
  return F;
}
