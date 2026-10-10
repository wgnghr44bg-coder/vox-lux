// What if the Moon started falling toward Earth? Chapter 4: a mountain village under the ring, day 1 -> year 1.
// Physics: debris from a low orbit enters the air at ~8 km/s (orbital speed), > 20× the speed of sound (343 m/s);
// small pieces burn up high, big ones could reach the ground; the Sun's tidal pull is ~46% of the Moon's, so tides
// driven by the Sun alone would be about a third of today's.
export const topic = {
  number: 504, slug: 'moon-c4-village', place: 'mountain-village', force: 'calm', wide: true, voOffset: 1.2,
  question: 'What if the Moon started falling toward Earth?', title: '',
};

export const lines = [
  ['d1', 'Day one.', 'long'],
  ['sky', 'The night sky is no longer dark. A bright band of rock arcs from one horizon to the other, still shining in sunlight long after sunset.', 'long'],
  ['grind', 'Inside the ring, the pieces keep colliding, grinding each other into smaller and smaller fragments.', 'pause'],
  ['fall', 'And some of them fall.', 'long'],
  ['y1', 'Year one.', 'long'],
  ['speed', 'Every night brings meteors. Falling pieces hit the air at around eight kilometres per second, more than twenty times the speed of sound.', 'pause'],
  ['most', 'Most would burn up high above us. But the biggest could reach the ground.', 4],
  ['tides', 'Without the Moon, the tides shrink to about a third of what they were, driven by the Sun alone.', 'long'],
  ['gone', 'No more full moons. Only a ring, made of what the Moon used to be.', 'long'],
  ['q', 'Would we survive the most beautiful sky in history?', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 3.5, climax = at('most').e + .2;
  const lat = 40, f = lat * Math.PI / 180;
  const ring = (pos, fov, el, yaw = 0) => ({ pos, look: [pos[0] + Math.sin(yaw) * 1000, pos[1] + Math.tan(el) * 1000, pos[2] - Math.cos(yaw) * 1000], drift: [0, 0, 0], fov });
  const c = climax - 4;
  return {
    T_END, tripod: true, brand: false, post: { ao: false },
    moon: { km: [[0, 384400]], orbit: { lat, theta: Math.PI / 2 }, night: true, visible: () => false },
    ring: { r: [9000, 20000], show: [[0, 1]], lit: .62 },
    meteors: { az: [-1.3, 1.3], rate: [[0, 0], [at('fall').s, 0], [at('fall').e, .6], [at('y1').s, .8], [at('speed').s, 2.2], [c, 3.5], [climax + 1, 3.5], [at('tides').e, 1.2], [T_END, 1]],
               fireballs: [[at('fall').e + .2, .5, .5, 3.2, .7], [at('speed').e - 1.5, -.6, .55, 3, .8], [c, -.35, .6, 3.4, 1.3], [c + 1.3, .45, .55, 3, 1], [c + 2.6, .05, .5, 3.6, 1.6], [at('gone').s + 1, -.8, .4, 3.4, .7]],
               flash: .55 },
    groups: [{ at: [10, 4], n: 7, face: Math.PI, lampPower: 14 }],
    extraShots: {
      'ring-wide': ring([60, 16, 70], 80, .22, -.2),
      'ring-up': ring([12, 1.8, 30], 84, .3),
      'group-ring': ring([16, 1.8, 13], 80, .26, -.3),
      'vast-ring': ring([140, 6, 170], 84, .25, -.5),
    },
    hud: { label: 'DAYS SINCE THE BREAK-UP', unit: '', decimals: 0, sub: 'DAY 1', subAt: [[at('y1').s - .3, 'YEAR 1']] },
    counter: [[0, 1], [at('y1').s - .4, 1], [at('y1').e + .4, 365], [T_END, 365]], range: [1, 365],
    captions: [[at('speed').s + 3.5, at('speed').e, '≈ 8 km/s — over 20× the speed of sound'], [at('tides').s + .5, at('tides').e, 'Tides: about ⅓ of today']],
    shots: [[0, 'vast-ring'], [at('sky').s + 3.5, 'ring-wide'], [at('grind').s - .2, 'ring-up'], [at('fall').s - .2, 'group-ring'],
            [at('y1').s - .2, 'ring-wide'], [at('speed').s + 3.5, 'pov-up'], [at('most').s - .2, 'ring-up'], [c + .9, 'group-ring'],
            [at('tides').s - .2, 'vast-ring'], [at('gone').s - .2, 'ring-up'], [at('q').s - .3, 'ring-wide']],
    beats: { lookUp: .6, climax, falls: [], stop: T_END + 1, fade: T_END - 2.6 },
    audio: { heartbeat: [at('speed').s, c], riser: [at('most').s, c] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Moon started falling toward Earth?', description: 'Hoofdstuk 4, niet uploaden.', tags: [], tiktok: '' };
