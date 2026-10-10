// What if the Moon started falling toward Earth? Chapter 2: the volcano park at night, 100,000 -> 25,000 km.
// Physics: apparent size ∝ 1/d (50,000 km ≈ 7.7× as wide), tidal pull ∝ 1/d³ (50,000 km ≈ 450×, 25,000 km ≈ 3,600×);
// solid-earth tides today: tens of centimetres; Io (Jupiter) is heated by tides into the most volcanic world;
// moonlight ∝ 1/d² (25,000 km ≈ 240× a full moon today: enough light to read by).
export const topic = {
  number: 502, slug: 'moon-c2-park', place: 'nature-park', force: 'quake', wide: true, voOffset: 1.2,
  question: 'What if the Moon started falling toward Earth?', title: '',
};

export const lines = [
  ['m50', 'Fifty thousand kilometres.', 'long'],
  ['wide', 'The Moon now looks almost eight times as wide as it does today.', 'pause'],
  ['rock', 'Even solid rock has tides. Right now, the ground beneath your feet rises and falls by tens of centimetres, twice a day, and you never notice.', 'long'],
  ['four', 'Now that pull is more than four hundred times stronger.', 'pause'],
  ['crust', 'The crust is squeezed and stretched, over and over. Old faults begin to slip.', 'long'],
  ['m25', 'Twenty-five thousand kilometres.', 'long'],
  ['thou', 'The pull is now thousands of times stronger than today.', 'pause'],
  ['io', 'Jupiter\'s moon Io is squeezed like this by Jupiter, and it is the most volcanic world in the Solar System.', 'long'],
  ['wake', 'Here on Earth, volcanoes that slept for centuries could wake up.', 3],
  ['read', 'And at night, the Moon shines so brightly that you could read a book by its light.', 'pause'],
  ['cliff', 'But it is now approaching a line that no moon can cross in one piece.', 'none'],
];

export default function (at) {
  const T_END = at('cliff').e + 2, climax = at('wake').e + .2;
  const km = [[0, 100000], [at('m50').s - .2, 100000], [at('m50').e + .4, 50000], [at('m25').s - .4, 50000], [at('m25').e + .4, 25000], [T_END, 25000]];
  const dir = [.1, .3, -.95];
  const up = (pos, fov, el = 0, yaw = 0) => { const c = Math.cos(yaw), s = Math.sin(yaw), x = dir[0] * c - dir[2] * s, z = dir[0] * s + dir[2] * c;
    return { pos, look: [pos[0] + x * 1000, pos[1] + (dir[1] + el) * 1000, pos[2] + z * 1000], drift: [0, 0, 0], fov }; };
  return {
    T_END, tripod: true, brand: false, post: { ao: false },
    moon: { km, dir, night: true },
    groups: [{ at: [26, 4], n: 6, face: Math.PI, lampPower: 18 }],
    extraShots: {
      'moon-lake': up([14, 3.6, 9], 58, -.12, .05),
      'group-moon': up([31, 1.9, 13], 62, -.1, -.25),
      'pov-up': up([22, 1.7, 8], 66, .02, .1),
    },
    hud: { label: 'MOON DISTANCE', unit: ' km', decimals: 0,
           second: { label: 'TIDAL PULL', prefix: '×', fn: v => (384400 / v) ** 3, decimals: 0, showAt: 0 } },
    counter: km, range: [100000, 25000],
    forceParams: {
      tremors: [[at('crust').s + .5, .25, 3], [at('crust').e, .35, 3], [at('thou').s, .45, 4], [at('io').s + 2, .4, 3], [at('wake').s, .7, 3], [climax, 1, 5]],
      steamAt: [at('crust').s, climax + 2],
    },
    glows: [{ pos: [-300, 25, -1250], t0: at('wake').s, t1: climax + 3, size: 2 }],
    captions: [[at('rock').s + 4, at('rock').e, 'Solid-earth tide: tens of cm, twice a day'], [at('io').s + .5, at('io').e, 'Io: the most volcanic world we know']],
    shots: [[0, 'moon-lake'], [at('wide').e - 1, 'group-moon'], [at('rock').s + 4, 'road'], [at('four').s - .2, 'vista'], [at('crust').s + 1.5, 'lake'],
            [at('m25').s - .2, 'moon-lake'], [at('thou').e - .5, 'pov-up'], [at('io').s + 2.5, 'lodge'], [at('wake').s - .2, 'vista'], [climax + 2, 'tower'],
            [at('read').s - .1, 'group-moon'], [at('cliff').s - .2, 'moon-lake']],
    beats: { lookUp: .8, shelter: at('wake').s - 2, evacuate: at('io').s, climax, falls: [climax + .8], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('thou').s, climax], riser: [at('io').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Moon started falling toward Earth?', description: 'Hoofdstuk 2, niet uploaden.', tags: [], tiktok: '' };
