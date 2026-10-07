// What if the Sun went out? Chapter 5 of 5: the river city, one year later (-52 -> -73 °C).
// The big moment, like gravity-doubled: brittle steel, a hanger snaps, the deck gives way; then the stars and an end card.
export const topic = {
  number: 205, slug: 'sun-out-5-river', place: 'river-city', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['year', 'After one year, the average temperature would be around minus seventy-three degrees.', 'long'],
  ['city', 'Picture a city on a wide river, under a great suspension bridge.', 'pause'],
  ['river', 'The river would be frozen solid at the top, a road of ice from bank to bank.', 'pause'],
  ['deep', "Deep below, the water would still be liquid, kept from freezing by Earth's own inner heat.", 'pause'],
  ['vents', 'Near hot springs on the ocean floor, tiny life could carry on, never needing the Sun at all.', 'long'],
  ['built', 'But every bridge and every tower around you was built for a world warmed by the Sun.', 'pause'],
  ['steel', 'In this cold, ordinary steel turns brittle, almost like glass.', 'pause'],
  ['shrink', 'And the cold makes it shrink, pulling every cable tighter.', 'long'],
  ['hold', 'For a while, it would hold.', 'pause'],
  ['creak', 'The bridge would creak and groan in the dark.', 'pause'],
  ['colder', 'Every week, a little colder than the last.', 'long'],
  ['snap', 'Then, one cable snaps.', 6],
  ['deck', 'The deck tilts. One by one, the others follow.', 'long'],
  ['drift', 'And Earth itself would no longer circle anything.', 'pause'],
  ['line', "Without the Sun's pull, it would fly off in a straight line, about thirty kilometers every second.", 'long'],
  ['away', 'Every day, more than two and a half million kilometers farther from where the Sun used to be.', 'long'],
  ['bright', 'The stars would be brighter than you have ever seen them.', 'pause'],
  ['every', 'Every bit of warmth you have ever felt came from one star.', 'long'],
  ['final', 'And it would never come back.', 'none'],
];

export default function (at) {
  const climax = at('snap').e + .4, stop = at('drift').s - .1;   // 'deck' is said while the deck goes
  const SEQ = ['far', 'wide', 'quay', 'under', 'span', 'deck', 'north'];
  const gen = lines.map(([id], k) => [k ? at(id).s - .2 : 0, SEQ[k % SEQ.length]]).filter(([t]) => t < at('creak').s || t > climax + 6);
  return {
    T_END: at('final').e + 4.6, tripod: true, brand: false, endStyle: 'card',
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'YEAR 1', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, -52], [at('year').e, -73], [stop, -73]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: 0 },
    captions: [[at('year').s + .5, at('year').e + .6, 'One year: about −73 °C.'],
               [at('steel').s, at('steel').e + .5, 'Steel turns brittle.'],
               [at('line').s + 1, at('line').e + .5, '30 km every second.']],
    // like gravity-doubled around the break: north -> span -> wide -> far (the bridge stays in view)
    shots: [...gen, [at('creak').s - .2, 'north'], [at('snap').s, 'span'], [climax + 3.3, 'wide'], [climax + 5.6, 'far']]
      .sort((a, b) => a[0] - b[0]),
    beats: {
      lookUp: 1e9, shelter: 0, carsStop: 0,
      hangers: at('snap').s + .3, deckBreak: climax + .9,
      falls: [], climax, stop, dark: at('every').s, end: at('final').s - .2,
    },
    audio: { heartbeat: [at('steel').s, climax + 1], riser: [at('creak').s, climax + .5] },
    end: { title: 'What if the Sun<br>went out?',
           lines: 'Eight minutes of light.<br>Then a long, cold dark.' },
  };
}
