// What if the Sun went out? Long video (owner's script), chapter 3: the mountain village, month 1 -> year 1.
export const topic = {
  number: 413, slug: 'sun-c3-village', place: 'mountain-village', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['month1', 'Month one.', 'none'],
  ['onemonth', 'One month without the Sun.', 'none'],
  ['extreme', 'Temperatures have fallen to extreme levels.', 'none'],
  ['oceans', 'Lakes and oceans begin freezing from the surface.', 'pause'],
  ['empty', 'Streets become dark and empty.', 'none'],
  ['normally', 'Humanity is no longer trying to live normally.', 'none'],
  ['survive', "We're simply trying to survive.", 'pause'],
  ['year1', 'Year one.', 'none'],
  ['unrecog', 'After one year, Earth is almost unrecognizable. The average temperature would be around minus seventy-three degrees.', 'none'],
  ['ice', 'The surface is covered in ice.', 'none'],
  ['gone', 'Most plants are gone. Most animals are gone.', 'pause'],
  ['underground', 'And the only humans still alive may be those sheltering underground, using nuclear or geothermal energy to stay warm.', 3],
  ['notdead', 'But Earth itself would not be completely dead.', 'none'],
];

export default function (at) {
  const climax = at('underground').e + .4, T_END = at('notdead').e + 1.5;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'MONTH 1',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'MONTH 1'], [at('year1').s, 'YEAR 1']] },
    counter: [[0, -30], [at('oceans').e, -38], [at('survive').e, -50], [at('year1').s, -62], [at('unrecog').e, -73], [T_END, -73]],
    range: [0, -80], forceParams: { darkAt: [-1, 0], frostAt: [.35, .9], snow: 0 },
    captions: [[at('month1').s, at('month1').e + .8, 'Month 1.'], [at('oceans').s, at('oceans').e + .5, 'Freezing from the top.'],
               [at('year1').s, at('year1').e + .8, 'Year 1.'], [at('unrecog').s + 3, at('unrecog').e + .5, '−73 °C.']],
    shots: [[0, 'wide'], [at('oceans').s - .2, 'lake'], [at('empty').s - .2, 'wide'], [at('year1').s - .2, 'mountains'],
            [at('ice').s - .2, 'lake'], [at('underground').s - .2, 'mountains'], [climax + 1.5, 'wide'], [at('notdead').s - .2, 'lake']],
    beats: { lookUp: 1e9, shelter: 0, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { hiss: -40, ice: -32, heartbeat: [at('year1').s, climax + 2], riser: [at('gone').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
