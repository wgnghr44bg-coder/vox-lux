// What if the Sun went out? Chapter 4 of 5: the coast, months later (-17 -> -50 °C).
export const topic = {
  number: 204, slug: 'sun-out-4-coast', place: 'boulevard', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['months', 'Weeks would turn into months.', 'pause'],
  ['coast', 'On the coast, the sea would hold out the longest.', 'pause'],
  ['heat', 'Oceans store enormous amounts of heat, so the shore would cool more slowly than the land.', 'long'],
  ['beach', 'But the beach would freeze solid, and the waves would turn thick and slow.', 'pause'],
  ['crust', 'Then a crust of ice would spread across the water.', 'long'],
  ['thick', 'Each week, the ice would grow a little thicker and push farther out to sea.', 'long'],
  ['plants', 'On land, most plants would be dead within weeks.', 'pause'],
  ['trees', 'Even the palm trees along the boulevard would freeze solid.', 'long'],
  ['minus30', 'Minus thirty.', 'pause'],
  ['animals', 'The beach umbrellas would stand frozen, as if summer had stopped in the middle of an afternoon.', 'pause'],
  ['farms', 'Behind the hotel windows, people would gather around whatever heat they had left.', 'pause'],
  ['people', 'People would survive only where they had power, fuel and shelter.', 'long'],
  ['under', 'Those glowing windows would be the only warm color left on the coast.', 'pause'],
  ['cities', 'Cities would shrink to a few warm islands of light in an endless dark.', 'long'],
  ['sky', 'With almost no water left to evaporate, the clouds would thin out and the snow would stop.', 'pause'],
  ['clear', 'Just a clear, black sky.', 'long'],
  ['minus50', 'Minus fifty.', 4],
  ['sea', 'Out on the frozen sea, nothing would move.', 'pause'],
  ['still', 'Not a wave. Not a breath of wind.', 'long'],
  ['crack', 'Just the crack of ice, settling in the dark.', 'long'],
];

export default function (at) {
  const climax = at('minus50').e + .4, T_END = at('still').e + 3.8;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'MONTH 3', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, -18], [at('beach').s, -22], [at('minus30').s, -30], [at('sky').s, -40], [at('minus50').s, -50], [T_END, -52]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: .25 },
    captions: [[at('months').s, at('months').e + .8, 'Months later.'], [at('heat').s, at('heat').e + .4, 'The sea cools slowest.'],
               [at('crust').s, at('crust').e + .5, 'The sea freezes over.'],
               [at('clear').s, at('clear').e + .6, 'No more clouds.']],
    // every line shows what the voice says (observer shots); one extra cut in the silent climax
    shots: [...lines.map(([id], k) => [k ? at(id).s - .2 : 0, { months: 'wide', coast: 'sea', heat: 'sea', beach: 'beach', crust: 'sea', thick: 'wide', plants: 'boulevard', trees: 'boulevard', minus30: 'wide', animals: 'beach', farms: 'hotels', people: 'hotels', under: 'hotels', cities: 'wide', sky: 'sea', clear: 'sea', minus50: 'beach', sea: 'sea', still: 'wide', crack: 'beach' }[id]]), [climax + 2.5, 'wide']]
      .sort((a, b) => a[0] - b[0]),
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('minus30').s, climax + 2], riser: [at('clear').s, climax] },
    end: { title: '', lines: '' },
  };
}
