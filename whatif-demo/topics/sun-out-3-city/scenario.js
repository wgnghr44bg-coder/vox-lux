// What if the Sun went out? Chapter 3 of 5: back in the city, the first week (2 -> -17 °C). Things start to give up; climax: the power grid fails, the whole city goes dark.
export const topic = {
  number: 203, slug: 'sun-out-3-city', place: 'street', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['week', 'Now jump ahead a few days.', 'pause'],
  ['city', 'Back in the city, the streets are dark and white with frost.', 'pause'],
  ['lights', 'Windows still glow, powered by fuel burning in the dark.', 'pause'],
  ['stars', 'Above the towers, the sky is full of stars, day and night.', 'pause'],
  ['zero', 'The temperature would drop below zero, and keep going.', 'long'],
  ['trees', 'The palm trees would be the first to give up. They were never made for frost.', 'pause'],
  ['leaves', 'Their leaves would turn brittle and dark.', 'long'],
  ['birds', 'Frost would creep up the walls, floor by floor.', 'long'],
  ['minus10', 'Minus ten.', 'pause'],
  ['cars', 'Car engines would struggle to start. One by one, the cars would stop where they stand.', 'pause'],
  ['buses', 'Inside the walls, pipes would freeze and burst.', 'pause'],
  ['quiet', 'The city would grow quieter every day.', 'long'],
  ['roads', 'Snow on the roads would never melt. Not even by day, because there is no day.', 'long'],
  ['lamps', 'Only the street lamps would still burn, over empty sidewalks.', 'long'],
  ['grid', 'Every heater in the city would be running at once.', 'pause'],
  ['strain', 'The power grid was never built for a night that never ends.', 'long'],
  ['avg', 'By the end of the first week, the average temperature on Earth would be about minus seventeen degrees.', 'long'],
  ['out', 'And then, the power fails.', 5],
  ['colder', 'In the dark, it would be colder than almost any winter most of us have ever known.', 'pause'],
  ['everywhere', 'And not just here. Everywhere on Earth, at the same time.', 'pause'],
  ['only', 'And it would only be the beginning.', 'long'],
];

export default function (at) {
  const climax = at('out').e + .4, T_END = at('only').e + 3.8;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'WEEK 1', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, 2], [at('zero').s, 0], [at('trees').s, -4], [at('minus10').s, -10], [at('roads').s, -14], [at('avg').e, -17], [T_END, -18]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: .8 },
    captions: [[at('week').s, at('week').e + .8, 'A few days later.'],
               [at('trees').s, at('trees').e + .4, 'Never made for frost.'],
               [at('cars').s, at('cars').e + .4, 'The cars stop.'], [at('buses').s, at('buses').e + .4, 'Pipes burst.'],
               [at('avg').s + 1, at('avg').e + .6, 'Week one: about −17 °C.'], [at('out').e, climax + 2.5, 'The power fails.']],
    // every line shows what the voice says (observer shots); one extra cut in the silent climax
    shots: [...lines.map(([id], k) => [k ? at(id).s - .2 : 0, { week: 'high', city: 'avenue', lights: 'balcony', stars: 'high', zero: 'corner', trees: 'corner', leaves: 'avenue', birds: 'balcony', minus10: 'high', cars: 'avenue', buses: 'balcony', quiet: 'high', roads: 'avenue', lamps: 'corner', grid: 'balcony', strain: 'high', out: 'high', avg: 'high', colder: 'sea', everywhere: 'high', only: 'corner' }[id]]), [climax + 2.5, 'avenue']]
      .sort((a, b) => a[0] - b[0]),
    beats: { carsStop: at('cars').s, shelter: at('quiet').s, powerOut: at('out').e + .3, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('minus10').s, climax + 2], riser: [at('strain').s, at('out').e + .3] },
    end: { title: '', lines: '' },
  };
}
