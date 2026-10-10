// Imagine every human disappeared – hoofdstuk 4: 25 years later (dezelfde straat en camera als hoofdstuk 1).
export const topic = { number: 444, slug: 'humans-4-street', place: 'street', force: 'calm', wide: true, voOffset: 1.5,
  question: 'What if every human disappeared?', title: '' };

export const lines = [
  ['year25', 'Twenty-five years later.', 'long'],
  ['same', 'This is the same street. The same corner where, one ordinary afternoon, everyone vanished.', 'long'],
  ['trees', 'Trees now grow straight out of the road. Their roots lift the asphalt, and the cars beneath them are slowly rusting away.', 'pause'],
  ['windows', 'Most of the windows are gone. Ivy climbs the walls, and every storm pulls a little more of the city down.', 'long'],
  ['real', 'And this is not just imagination.', 'pause'],
  ['pripyat', 'In nineteen eighty-six, the city of Pripyat was abandoned in a single day. Today, forest grows through its streets, and trees stand inside its buildings.', 'long'],
  ['silence', 'No engines. No voices. Only wind, birds, and the slow sound of a city returning to the earth.', 4],
  ['question', 'After just twenty-five years... would anyone still recognize this as a city?', 'none'],
];

export default function (at) {
  const T_END = at('question').e + 5, Y = 365;
  const days = [[0, .05], [at('same').s, 40], [at('trees').s, 8 * Y], [at('windows').e, 20 * Y], [at('pripyat').s - 1, 9124.85], [T_END, 9124.93]];
  const c1 = (at, point, cars, smoke) => ({ at, point, cars, smoke: false });
  return {
    T_END, tripod: true, brand: false, post: true, cars: false, lightCycle: 9, trafficStill: true, endStyle: 'card',
    time: { days, hour: 15.2, doy: 140, clouds: .4, snow: true, rain: [[at('windows').s, at('windows').e + .5]],
            avoid: [[-1, 42, 7], [-6, 64, 7], [-9.4, 33, 4], [-13, 22, 4], [8.8, 11, 3], [-1, 30, 3]] },
    traffic: [{ x: -7.4, z: -45, dir: 1, v: 10 }, { x: -7.4, z: -75, dir: 1, v: 9 }, { x: -2.6, z: -6, dir: 1, v: 9.5 },
              { x: 2.6, z: 25, dir: -1, v: 9 }, { x: 7.4, z: -15, dir: -1, v: 10 }, { x: 7.4, z: 75, dir: -1, v: 9.5 }, { x: 7.4, z: -70, dir: -1, v: 9 }],
    crashes: [c1(-100, [.6, -28], [{ dir: [0, 1], v: 9, off: -3.2 }, { dir: [0, -1], v: 8, off: -2 }]),
              c1(-98, [9.9, -29], [{ dir: [0, -1], v: 7, off: 2.5, spin: .25, slide: .8 }])],
    animals: [
      { kind: 'deer', n: 2, spread: 2, antlers: true, path: [[0, -3, -14], [at('pripyat').s, -3, -14], [at('pripyat').s + 6, 1, -4], [T_END, 1, -4]], act: 'graze' },
      { kind: 'birds', n: 16, center: [0, 18, -20], radius: 14, from: at('silence').s - 3 },
    ],
    extraShots: {
      'pov-walk': { pos: [-4, 1.65, 20], look: [0, 1.6, -30], drift: [.4, 0, -7], fov: 62, run: { amp: .03, freq: 1.7 } },
      sign: { pos: [-9.6, 2.6, 5], look: [-11.2, 2.9, 2], drift: [0, 0, 0], fov: 40 },
      rise: { pos: [-1, 3, 22], look: [-1, 4, -150], drift: [0, 13, -2], lookDrift: [0, 6, 0], fov: 60 },
    },
    hud: { label: 'TIME WITHOUT HUMANS', fmt: v => v < 1 ? 'HOUR 1' : v < 300 ? `MONTH ${Math.max(1, Math.round(v / 30))}` : `YEAR ${Math.max(1, Math.round(v / 365))}` },
    counter: days, range: [0, 9125],
    captions: [],
    shots: [[0, 'high'], [at('windows').s - .2, 'corner'], [at('real').s - .2, 'sign'], [at('pripyat').s - .2, 'pov-walk'], [at('silence').s - .2, 'rise']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: 0, vanish: 0, powerOut: 0, climax: at('silence').s, falls: [],
             stop: at('question').e + .4, dark: at('question').e + 1.4, end: at('question').e + .9, fade: 1e9 },
    audio: { quiet: 0, riser: [at('pripyat').e - 4, at('silence').s + 1] },
    end: { title: 'What if every human<br>disappeared?', lines: 'IFSCAPE3D' },
  };
}
export const upload = { title: 'What if every human disappeared?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
