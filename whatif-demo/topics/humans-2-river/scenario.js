// Imagine every human disappeared – hoofdstuk 2: the first days (rivierstad, nacht → maand 1).
export const topic = { number: 442, slug: 'humans-2-river', place: 'river-city', force: 'calm', wide: true, voOffset: 1.2,
  question: 'What if every human disappeared?', title: '' };

export const lines = [
  ['day1', 'Day one.', 'long'],
  ['night', 'The first night falls on a city with no one in it.', 'pause'],
  ['burn', 'For now, the lights still burn.', 'long'],
  ['grid', 'Power stations can run on their own for a while.', 'pause'],
  ['fault', 'But with no one to feed them fuel, or fix a single fault, the grid starts to break apart.', 'long'],
  ['out', 'One by one, the lights go out.', 3],
  ['quiet', 'Within a day, most of the city is dark.', 'pause'],
  ['thaw', 'Freezers thaw. Phones die. The internet goes silent.', 'long'],
  ['pumps', 'Deep below the streets, the pumps that kept the water out have stopped.', 'pause'],
  ['metro', 'Without them, many metro tunnels would flood in just a couple of days.', 'long'],
  ['week', 'By the end of the first week, the pets left behind are on their own.', 'pause'],
  ['dogs', 'Hungry dogs form packs, and roam the empty streets in search of food.', 'long'],
  ['month', 'One month in, the city is still standing.', 'pause'],
  ['ours', 'But it no longer belongs to us.', 'long'],
  ['cliff', 'Because something else is already moving in.', 'none'],
];

export default function (at) {
  const offA = at('out').s - .3, offB = at('out').e + 2.6, T_END = at('cliff').e + 1.6;
  const dayKeys = [[0, 0], [offB, .16], [at('thaw').e + .5, .45], [at('metro').s - .5, 1.6], [at('metro').e, 1.72], [at('week').e, 7], [at('month').s, 30], [T_END, 30.4]];
  const d0 = at('dogs').s - 4.5, f0 = at('cliff').s - 1.5;
  return {
    T_END, tripod: true, brand: false, post: true, noTraffic: true, nightExposure: 1.3,
    time: { days: dayKeys, hour: 20.6, doy: 140, clouds: .3, rain: [[at('pumps').s - 1, at('metro').e + .5]] },
    metro: [{ x: 55, z: 18.5, ry: 0, water: [at('pumps').s + 1, T_END + 1] }],
    animals: [
      { kind: 'dog', n: 4, spread: 1.4, lag: .3, colors: [0x2a2622, 0x8a6a48, 0xd8cdb8, 0x6b4a32], path: [[d0, 22, -21.5], [d0 + 6.5, 44, -22], [d0 + 9, 47, -22.5], [d0 + 20, 47, -22.5]], act: 'sniff',
        shot: { name: 'dogs', at: 1, from: [-7, 1.2, 5.5], fov: 44 } },
      { kind: 'fox', path: [[f0, 75, -24], [f0 + 4.5, 66, -23], [f0 + 20, 66, -23]], act: 'look', shot: { name: 'fox', at: 1, from: [-4.5, 1.1, 3.2], fov: 40 } },
    ],
    extraShots: {
      'pov-metro': { pos: [55, 1.65, 12.2], look: [55, -2.8, 21], drift: [0, 0, .5], fov: 62 },
      lights: { pos: [40, 2, -26], look: [40, 14, 34], drift: [-1.5, 0, 0], fov: 50 },
    },
    hud: { label: 'TIME WITHOUT HUMANS', fmt: v => v < 29.5 ? `DAY ${Math.max(1, Math.floor(v + .84))}` : 'MONTH 1' },
    counter: dayKeys, range: [0, 30],
    captions: [],
    shots: [[0, 'wide'], [at('night').s + 2, 'lights'], [at('grid').s + 1, 'north'], [at('out').s - .4, 'towers'], [offB + .6, 'wide'],
            [at('quiet').s + 3, 'quay'], [at('pumps').s - .2, 'road'], [at('metro').s - .4, 'pov-metro'], [at('week').s - .2, 'wide'],
            [at('dogs').s - .2, 'dogs'], [at('dogs').e + .4, 'pov-walk'], [at('month').s + .5, 'far'], [at('cliff').s - .2, 'fox']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: 0, vanish: 0, powerOff: [offA, offB], climax: offB, falls: [], stop: T_END + 1, fade: 1e9 },
    events: [{ t: at('night').s, kind: 'alarm', dur: at('out').s - at('night').s, e: .5, x: 80 }, { t: at('grid').s, kind: 'buzz', dur: offB - at('grid').s, e: 1 }],
    audio: { quiet: 0, riser: [at('grid').s, offA], heartbeat: [at('grid').s + 2, offB] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'What if every human disappeared?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
