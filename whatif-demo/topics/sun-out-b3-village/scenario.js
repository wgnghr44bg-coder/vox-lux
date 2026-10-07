// What if the Sun went out? Long video (gravity style), chapter 3: the mountain village, month 1 -> year 1.
export const topic = {
  number: 403, slug: 'sun-out-b3-village', place: 'mountain-village', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['month', 'One month.', 'pause'],
  ['village', 'High in the mountains, a small village sits beside a lake, lit only by its own windows.', 'pause'],
  ['plants', 'Every pine on these slopes would be dying. Without light, no plant can make food.', 'pause'],
  ['food', 'And without plants, every food chain on Earth would start to collapse.', 'long'],
  ['lake', 'The lake has been losing its heat for a month. Now the ice is reaching out from the shore.', 'long'],
  ['float', 'Ice floats, because water expands when it freezes.', 'pause'],
  ['lid', 'So the lake would freeze from the top down, like a lid.', 'pause'],
  ['below', 'Underneath, the water would stay liquid for a long time.', 'long'],
  ['six', 'Six months.', 'pause'],
  ['dry', 'The air would be too cold to hold any water. The clouds would fade, and the snow would stop.', 'pause'],
  ['wood', 'In the houses, people would burn whatever they could find to stay warm.', 'pause'],
  ['square', 'The square would stay empty.', 'long'],
  ['year', 'One year.', 'pause'],
  ['minus73', 'Minus seventy-three degrees.', 6],
  ['stars', 'With no Sun and no Moon, the Milky Way would stretch from peak to peak.', 'pause'],
  ['light', 'Every bit of light left on this mountain would come from the people who still live here.', 'long'],
  ['final', 'And the Sun would never rise again.', 'none'],
];

export default function (at) {
  const climax = at('minus73').e + .4, T_END = at('final').e + 4.6;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'MONTH 1',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'MONTH 1'], [at('six').s, 'MONTH 6'], [at('year').s, 'YEAR 1']] },
    counter: [[0, -30], [at('lake').e, -35], [at('six').s, -50], [at('square').e, -58], [at('year').s, -66],
              [at('minus73').s + .5, -73], [T_END, -73]],
    range: [0, -80], forceParams: { darkAt: [-1, 0], frostAt: [.35, .9], snow: 0 },
    captions: [[at('month').s, at('month').e + .8, 'Month 1.'], [at('lid').s, at('lid').e + .5, 'Frozen from the top down.'],
               [at('six').s, at('six').e + .8, 'Month 6.'], [at('year').s, at('year').e + .8, 'Year 1.']],
    shots: [[0, 'wide'], [at('village').s - .2, 'wide'], [at('plants').s - .2, 'mountains'], [at('food').s - .2, 'wide'],
            [at('lake').s - .2, 'lake'], [at('float').s - .2, 'lake'], [at('lid').s - .2, 'lake'], [at('below').s - .2, 'lake'],
            [at('six').s - .2, 'wide'], [at('dry').s - .2, 'mountains'], [at('wood').s - .2, 'square'], [at('square').s - .2, 'square'],
            [at('year').s - .2, 'wide'], [at('minus73').s - .2, 'lake'], [climax + 2.5, 'lake'],
            [at('stars').s - .2, 'mountains'], [at('light').s - .2, 'square'], [at('final').s - .2, 'wide']],
    beats: { lookUp: 1e9, shelter: 0, climax, falls: [], stop: at('final').s - 1, dark: at('final').s - .5, end: at('final').e + .3, fade: 1e9 },
    audio: { heartbeat: [at('year').s, climax + 2], riser: [at('square').s, climax] },
    end: { title: 'What if<br>the Sun went out?', lines: 'One year later: −73 °C.<br>And no sunrise, ever again.' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
