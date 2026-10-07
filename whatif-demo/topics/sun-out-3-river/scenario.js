// What if the Sun went out? Chapter 3 of 5: river city, the first week (3 -> -17 °C). The bridge stays up.
export const topic = {
  number: 203, slug: 'sun-out-3-river', place: 'river-city', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['week', 'Now jump ahead a few days.', 'pause'],
  ['city', 'A city on a wide river, under a great suspension bridge.', 'pause'],
  ['lights', 'Its windows still glow, powered by fuel burning in the dark.', 'pause'],
  ['stars', 'Above it, the sky would be full of stars, day and night.', 'pause'],
  ['zero', 'The temperature here would drop below zero, and keep going.', 'long'],
  ['river', 'The river would be the first to change.', 'pause'],
  ['ice', 'Ice would form along the banks, then reach out toward the middle.', 'pause'],
  ['floats', 'Ice floats, so the river would freeze from the top down.', 'pause'],
  ['below', 'Beneath it, the water would stay liquid, as if under a lid.', 'long'],
  ['fish', 'Fish would gather in the deep water, where it stays a few degrees above freezing.', 'long'],
  ['minus10', 'Minus ten.', 'pause'],
  ['cars', 'Car engines would struggle to start. Pipes would freeze and burst.', 'pause'],
  ['buses', 'Buses and trains would slow down, then stop running.', 'pause'],
  ['breath', 'Your breath would hang in the air like smoke.', 'pause'],
  ['quiet', 'The city would grow quieter every day.', 'long'],
  ['roads', 'Snow on the roads would never melt. Not even by day, because there is no day.', 'long'],
  ['bridge', 'The steel of the bridge would shrink in the cold, creaking as it settles.', 'long'],
  ['avg', 'By the end of the first week, the average temperature on Earth would be about minus seventeen degrees.', 5],
  ['colder', 'Colder than almost any winter most of us have ever known.', 'pause'],
  ['everywhere', 'And not just here. Everywhere on Earth, at the same time.', 'pause'],
  ['only', 'And it would only be the beginning.', 'long'],
];

export default function (at) {
  const climax = at('avg').e + .4, T_END = at('only').e + 3.0;
  return {
    T_END, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, 2], [at('zero').s, 0], [at('ice').s, -4], [at('minus10').s, -10], [at('bridge').s, -14], [climax, -17], [T_END, -18]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: .8, breath: at('breath').s },
    captions: [[at('floats').s, at('floats').e + .4, 'Frozen from the top down.'],
               [at('breath').s, at('breath').e + .4, 'Your breath freezes.'],
               [at('avg').s + 1, climax + 1.5, 'Week one: about −17 °C.']],
    shots: [[at('stars').s, 'far'], [at('fish').s, 'under'], [at('roads').s, 'north'], [at('everywhere').s, 'wide'],
            [0, 'far'], [at('city').s, 'wide'], [at('lights').s, 'north'], [at('river').s, 'under'], [at('floats').s, 'span'],
            [at('minus10').s, 'wide'], [at('cars').s, 'north'], [at('breath').s, 'quay'], [at('quiet').s, 'far'],
            [at('bridge').s, 'deck'], [at('avg').s, 'wide'], [climax + 2.5, 'towers'], [at('colder').s, 'span'], [at('only').s, 'far']].sort((a, b) => a[0] - b[0]),
    beats: { carsStop: at('cars').s, lookUp: 1e9, shelter: at('quiet').s, hangers: 1e9, deckBreak: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('minus10').s, climax + 2], riser: [at('bridge').s, climax] },
    end: { title: '', lines: '' },
  };
}
