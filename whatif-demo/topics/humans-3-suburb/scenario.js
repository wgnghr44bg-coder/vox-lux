// Imagine every human disappeared – hoofdstuk 3: nature returns (buitenwijk + park + supermarkt, jaar 1 → jaar 10).
export const topic = { number: 443, slug: 'humans-3-suburb', place: 'suburb', force: 'calm', wide: true, voOffset: 1.2,
  question: 'What if every human disappeared?', title: '' };

export const lines = [
  ['year1', 'Year one.', 'long'],
  ['air', 'With no cars and no factories, the air is cleaner than it has been in more than a century.', 'long'],
  ['grass', 'Grass pushes up through every crack in the pavement.', 'pause'],
  ['ice', 'Each winter, water freezes inside those cracks, and splits them a little wider.', 'long'],
  ['deer', 'Deer wander down streets that were built for cars.', 'pause'],
  ['fox', 'Foxes raise their young under porches.', 'pause'],
  ['birds', 'Birds nest behind broken windows.', 'long'],
  ['shop', 'In the supermarkets, almost every scrap of food has rotted, or been eaten by rats and insects.', 'long'],
  ['year10', 'Year ten.', 3],
  ['roofs', 'Gutters fill with leaves, and rain gets in.', 'pause'],
  ['rot', 'Wooden roofs begin to rot, and sag.', 'long'],
  ['trees', 'Young trees are already taller than the cars they grow between.', 'long'],
  ['cliff', 'But the biggest change is still to come.', 'none'],
];

export default function (at) {
  const T_END = at('cliff').e + 1.6, c0 = at('year10').s - .2, c1 = at('year10').e + 2.6;
  const days = [[0, 365], [c0, 3 * 365], [c1, 3650], [T_END, 3650.08]];   // ends at midday
  const dx = 18, fx = -40.5, fz = 8.6;
  return {
    T_END, tripod: true, brand: false, post: true, noTraffic: true, parked: [[fx, fz, 1, 0x8c3b33]],
    time: { days, hour: 11, doy: 120, clouds: .4, rain: [[at('ice').e - 1, at('deer').s + .5]],
            avoid: [[-30, 46, 6], [-40, 1.5, 4], [-6, 7, 4], [-20, 52, 5], [32, 8, 5], [8, 4, 5], [-55, 52, 4], [fx, fz, 4]] },
    animals: [
      { kind: 'deer', n: 3, spread: 2.4, antlers: true, path: [[at('deer').s - 4, 42, -1], [at('deer').s + 2.5, dx, -1.5], [T_END, dx, -1.5]], act: 'graze',
        shot: { name: 'deer', at: 1, from: [-8, 1.7, 6], fov: 44 } },
      { kind: 'fox', path: [[0, fx, fz]], y: 1.62, act: 'look', shot: { name: 'fox', from: [-4.2, 2.2, 4.4], lookY: 1.9, fov: 40 } },
      { kind: 'birds', n: 12, center: [45, 14, 24], radius: 10, perch: [[38, 7.15, 28.6], [44, 7.15, 28.6], [52, 7.15, 28.6]], land: at('fox').s + 2 },
    ],
    hud: { label: 'TIME WITHOUT HUMANS', fmt: v => `YEAR ${Math.max(1, Math.floor(v / 365 + .02))}` },
    counter: days, range: [365, 3650],
    captions: [],
    shots: [[0, 'wide'], [at('air').s + 1.5, 'street'], [at('grass').s - .2, 'pov-street'], [at('deer').s - .2, 'deer'], [at('fox').s - .2, 'fox'],
            [at('birds').s - .2, 'shop'], [at('shop').s + 1.5, 'lot'], [c0, 'wide'], [at('roofs').s - .2, 'houses'], [at('trees').s - .2, 'pov-park'], [at('cliff').s - .2, 'park']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: 0, vanish: 0, powerOut: 0, climax: c0, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { quiet: 0, riser: [at('shop').s, c0 + 1] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'What if every human disappeared?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
