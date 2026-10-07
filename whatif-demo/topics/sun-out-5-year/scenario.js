// What if the Sun went out? Chapter 5 of 5: back on the street, one year later (-50 -> -73 °C). Fades out on the stars.
export const topic = {
  number: 205, slug: 'sun-out-5-year', place: 'street', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['year', 'After one year, the average temperature would be around minus seventy-three degrees.', 'long'],
  ['street', 'Back downtown, where it all began, everything would be still.', 'pause'],
  ['frozen', 'The palm trees frozen in place. The cars white with frost.', 'pause'],
  ['sea', 'Where the water used to move, a flat white plain.', 'long'],
  ['sound', 'No birds. No traffic. No sound at all.', 'long'],
  ['deep', 'But deep below that ice, the ocean would still be liquid.', 'pause'],
  ['inner', "Earth's own inner heat would keep the deep water from freezing for a very long time.", 'pause'],
  ['vents', 'Near hot springs on the ocean floor, tiny life could carry on, never needing the Sun at all.', 'long'],
  ['marble', 'From far away, Earth would look like a dark, frozen marble.', 'long'],
  ['drift', 'And Earth itself would no longer circle anything.', 'pause'],
  ['line', "Without the Sun's pull, it would fly off in a straight line, about thirty kilometers every second.", 'long'],
  ['away', 'Every day, it would carry us more than two and a half million kilometers farther from where the Sun used to be.', 'long'],
  ['into', 'Into the dark between the stars.', 5],
  ['bright', 'The stars would be brighter than you have ever seen them.', 'pause'],
  ['milky', 'The Milky Way would stretch across the sky, sharper than on any night you have known.', 'pause'],
  ['every', 'Every bit of warmth you have ever felt came from one star.', 'long'],
  ['final', 'And it would never come back.', 'none'],
];

export default function (at) {
  const climax = at('into').e + .4, T_END = at('final').e + 3.6;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'YEAR 1', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, -52], [at('year').e, -73], [T_END, -73]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: 0 },
    captions: [[at('year').s + .5, at('year').e + .6, 'One year: about −73 °C.'],
               [at('deep').s, at('deep').e + .4, 'The deep ocean stays liquid.'],
               [at('line').s + 1, at('line').e + .5, '30 km every second.']],
    // a new standpoint on every line (gravity style: observer shots, never the same twice in a row), one extra cut in the silent climax
    shots: [...lines.map(([id], k) => [k ? at(id).s - .2 : 0, ['high', 'balcony', 'corner', 'sea', 'avenue'][k % 5]]), [climax + 2.5, ['high', 'balcony', 'corner', 'sea', 'avenue', 'crossing'][(lines.length + 2) % 5]]]
      .sort((a, b) => a[0] - b[0]),
    beats: { lookUp: at('bright').s, shelter: 0, carsStop: 0, climax, falls: [], stop: T_END + 1, fade: at('final').s - .2 },
    audio: { heartbeat: [at('drift').s, climax + 2], riser: [at('line').s, climax] },
    end: { title: '', lines: '' },
  };
}
