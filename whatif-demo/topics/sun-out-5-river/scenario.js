// What if the Sun went out? Chapter 5 of 5: a city on a frozen river, one year later (-52 -> -73 °C).
// No bridge story (used before): the frozen river, the deep ocean that stays liquid, and Earth drifting off under the stars.
// Shots avoid the bridge (quay, north, towers); quiet climax on the starry sky, then an end card.
export const topic = {
  number: 205, slug: 'sun-out-5-river', place: 'river-city', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['year', 'After one year, the average temperature would be around minus seventy-three degrees.', 'long'],
  ['city', 'Picture a city on a wide river.', 'pause'],
  ['river', 'The river would be frozen solid at the top, a road of ice from bank to bank.', 'pause'],
  ['deep', "Deep below, the water would still be liquid, kept from freezing by Earth's own inner heat.", 'pause'],
  ['vents', 'Near hot springs on the ocean floor, tiny life could carry on, never needing the Sun at all.', 'long'],
  ['frost', 'Up here, frost would cover every window, every railing, every lamp.', 'pause'],
  ['air', 'Your breath would turn to ice crystals the moment it left your mouth.', 'pause'],
  ['quiet', 'No wind. No clouds. No sound but the ice.', 'long'],
  ['later', 'And every year after, it would grow a little colder still.', 'long'],
  ['drift', 'Earth itself would no longer circle anything.', 'pause'],
  ['line', "Without the Sun's pull, it would fly off in a straight line, about thirty kilometers every second.", 'long'],
  ['away', 'Every day, more than two and a half million kilometers farther from where the Sun used to be.', 'long'],
  ['where', 'Look up, and you could not even tell which point of darkness it had been.', 5],
  ['bright', 'The stars would be brighter than you have ever seen them.', 'pause'],
  ['every', 'Every bit of warmth you have ever felt came from one star.', 'long'],
  ['final', 'And it would never come back.', 'none'],
];

export default function (at) {
  const climax = at('where').e + .4;
  const SHOT = { year: 'north', city: 'towers', river: 'quay', deep: 'quay', vents: 'north', frost: 'towers', air: 'quay', quiet: 'north',
    later: 'towers', drift: 'north', line: 'towers', away: 'quay', where: 'north', bright: 'towers', every: 'quay', final: 'north' };
  return {
    T_END: at('final').e + 4.6, tripod: true, brand: false, endStyle: 'card',
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'YEAR 1', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, -52], [at('year').e, -73], [at('later').e, -73], [climax, -75]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: 0 },
    captions: [[at('year').s + .5, at('year').e + .6, 'One year: about −73 °C.'],
               [at('deep').s, at('deep').e + .4, 'The deep ocean stays liquid.'],
               [at('line').s + 1, at('line').e + .5, '30 km every second.']],
    // every line shows what the voice says; the bridge stays out of the story
    shots: [...lines.map(([id], k) => [k ? at(id).s - .2 : 0, SHOT[id]]), [climax + 2.5, 'towers']].sort((a, b) => a[0] - b[0]),
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, hangers: 1e9, deckBreak: 1e9, falls: [], climax, stop: at('final').e + 6,
             dark: at('every').s, end: at('final').s - .2 },
    audio: { heartbeat: [at('drift').s, climax + 1], riser: [at('away').s, climax] },
    end: { title: 'What if the Sun<br>went out?', lines: 'Eight minutes of light.<br>Then a long, cold dark.' },
  };
}
