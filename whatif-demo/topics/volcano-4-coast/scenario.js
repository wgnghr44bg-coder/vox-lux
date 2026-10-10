// What if a supervolcano erupted? Long video (16:9), chapter 4: the volcanic winter. European coast (boulevard), 8,000 km away.
// Bricks: force eruption far away (blood-red sunsets from the sulphur veil, then a cold grey summer with sleet), people in coats.
export const topic = {
  number: 3505, slug: 'volcano-4-coast', place: 'boulevard', force: 'eruption', wide: true, voOffset: 1.2, padSilence: true,
  question: 'What if a supervolcano erupted?', title: '',
};

export const lines = [
  ['month', 'Month one.', 'long'],
  ['red', 'Eight thousand kilometres away, in Europe, the evening sky turns blood red.', 'long'],
  ['veil', 'High above the clouds, sulphur gas from the volcano would spread into a thin veil around the planet, reflecting sunlight back into space.', 'long'],
  ['year', 'Year one.', 'long'],
  ['summer', 'Summer never comes.', 'long'],
  ['cool', 'The whole Earth could cool by a few degrees.', 'pause'],
  ['small', 'That sounds small.', 'pause'],
  ['isnt', 'It isn\'t.', 'long'],
  ['tambora', 'In 1815, a far smaller eruption, Tambora, caused the year without a summer.', 'pause'],
  ['june', 'Snow fell in June.', 'pause'],
  ['harvest', 'Harvests failed across Europe, and food prices soared.', 3],
  ['worse', 'A supereruption could be many times worse.', 'long'],
  ['chance', 'The chance of it happening in any given year is tiny, about one in seven hundred thousand.', 'pause'],
  ['again', 'But somewhere on Earth, it has happened before… and it will happen again.', 'long'],
  ['question', 'So if it happened tomorrow… how far away would you want to be?', 'none'],
];

export default function (at) {
  const q = at('question'), endT = q.e + 1.2, T_END = endT + 4.5;
  const yr = at('year').s;
  return {
    T_END, tripod: true, brand: false, post: true, endStyle: 'card', sunbathers: 0, sunOffset: [-90, 38, -320],
    hud: { label: 'DISTANCE TO THE VOLCANO', unit: ' KM', decimals: 0, sub: 'MONTH 1', subAt: [[0, 'MONTH 1'], [yr, 'YEAR 1']] },
    counter: [[0, 8000], [T_END, 8000]],
    forceParams: {
      vent: null,
      sunset: [[0, .55], [at('red').s, .7], [at('red').e, 1], [yr - 1, 1], [yr + 1.5, 0], [T_END, 0]],
      winter: [[0, 0], [yr - 1, 0], [yr + 2, .8], [at('june').s, .9], [at('harvest').e + 3, 1], [T_END, .9]],
      loud: [[0, .02], [T_END, .05]],
    },
    groups: [{ at: [-6, 18], n: 6, face: Math.PI, coats: [0x3d4650, 0x5a3a32, 0x2f3236, 0x56624a, 0x6b5a48, 0x3e4a5c], lamp: false,
               shot: { name: 'group', from: [2.5, 1.7, 8], fov: 50 } }],
    captions: [[at('cool').s + .5, at('isnt').e, 'A few degrees colder.'], [at('chance').s + 1, at('chance').e + .3, 'About 1 in 700,000 per year.']],
    shots: [[0, 'sea'], [at('red').s - .2, 'group'], [at('veil').s - .2, 'wide'], [yr - .2, 'beach'], [at('summer').s - .2, 'boulevard'],
            [at('cool').s - .2, 'pov-beach'], [at('tambora').s - .2, 'hotels'], [at('june').s - .2, 'sea'], [at('worse').s - .2, 'group'],
            [at('chance').s - .2, 'pov-sea'], [at('again').s - .2, 'wide'], [q.s - .2, 'sea']],
    beats: { lookUp: at('red').s + 1, shelter: 1e9, carsStop: 1e9, climax: 1e9, falls: [], stop: endT, dark: endT + 1, end: endT + .3 },
    end: { title: 'What if a supervolcano<br>erupted?', lines: 'IFSCAPE3D' },
  };
}

export const upload = { title: 'What if a supervolcano erupted?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
