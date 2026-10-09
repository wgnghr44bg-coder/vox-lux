// Imagine the Sun went out (owner's shot list). Chapter 3: the boulevard, day 7.
export const topic = {
  number: 423, slug: 'sun-d3-boulevard', place: 'boulevard', force: 'cold', wide: true, voOffset: 1.5,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['week', 'One week has passed.', 'long'],
  ['changed', 'The sunny boulevard from the very first day is unrecognizable.', 'pause'],
  ['nopeople', 'No people. No traffic. No light.', 'long'],
  ['avg', 'By now, the average temperature on Earth would be around minus seventeen degrees. Colder than most of us have ever felt.', 'pause'],
  ['oceans', 'The oceans are beginning to freeze from the surface.', 'pause'],
  ['salt', 'Salt water only freezes at around minus two degrees, so the sea holds out longer than the land. But not forever.', 'long'],
  ['ice', 'Along the shore, a thin skin of ice grows a little thicker every hour.', 'pause'],
  ['outside', 'Most people are no longer outside.', 'pause'],
  ['shelter', 'They have gathered wherever there is still heat. Fuel. Firewood. A generator.', 'long'],
  ['car', 'This car has not moved in days. Its roof is covered in frost, as hard as stone.', 'pause'],
  ['breath', 'Every breath hangs in the air like smoke.', 'none'],
];

export default function (at) {
  const T_END = at('breath').e + 1.8, carT = at('car').s - .2;
  return {
    T_END, tripod: true, brand: false, sunbathers: 0,
    hand: { car: [15, 73], cam: [14.4, 3 + 1.65, 75.1], t: [carT, T_END + 1] },
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'DAY 7',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'DAY 7'], [at('outside').s, 'DAY 7 — NO SUNLIGHT']] },
    counter: [[0, -10], [at('avg').e, -13], [at('ice').e, -16], [T_END, -17]],
    range: [0, -40], forceParams: { darkAt: [-1, 0], frostAt: [.2, .6], snow: .6, breath: [[carT, T_END + 1]] },
    captions: [[at('week').s, at('week').e + .8, 'Day 7.'], [at('avg').s, at('avg').s + 4, '−17 °C, worldwide.'],
               [at('salt').s, at('salt').s + 4, 'Seawater freezes at −2 °C.']],
    shots: [[0, 'slow-prom'], [at('nopeople').s - .2, 'wide'], [at('avg').s - .2, 'slow-prom'], [at('oceans').s - .2, 'sea'],
            [at('ice').s - .2, 'beach'], [at('outside').s - .2, 'hotels'], [carT, 'pov-car']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, powerOut: -1, climax: 1e9, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { hiss: -60, ice: -60 },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
