// What if the Sun went out? Long video (gravity style), chapter 2: the street, day 1 -> week 1.
export const topic = {
  number: 402, slug: 'sun-out-b2-street', place: 'street', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['day1', 'Day one. A city street, a few kilometers inland.', 'pause'],
  ['noon', 'The clocks say it is just past noon.', 'pause'],
  ['lamps', 'But the street lamps have switched on by themselves. Their sensors only know that it is dark.', 'long'],
  ['look', 'People stop on the pavement and stare up at a sky full of stars.', 'pause'],
  ['heat', 'The walls and the asphalt still hold the warmth of the morning.', 'pause'],
  ['leak', 'Without the Sun, that warmth would leak away into space, a degree or two every hour.', 'long'],
  ['inside', 'Shop owners would pull down their shutters. One by one, people would head inside.', 'pause'],
  ['heating', 'Behind every window, the heating would switch on.', 'long'],
  ['day3', 'Day three.', 'pause'],
  ['zero', 'The temperature would drop below zero, and keep going.', 'pause'],
  ['frost', 'Frost would spread over the cars, the benches and the roofs.', 'pause'],
  ['car', 'Down the street, a car would refuse to start. Its driver would give up and walk home.', 'long'],
  ['week', 'One week.', 'pause'],
  ['average', 'By now, the average temperature on Earth would be around minus seventeen degrees.', 'pause'],
  ['snow', 'Then the water in the air would start to fall as snow.', 6],
  ['palms', 'Snow on the palm trees, in the middle of summer.', 'pause'],
  ['only', 'And this is only the first week.', 'none'],
];

export default function (at) {
  const climax = at('snow').e + .4, T_END = at('only').e + 3.2;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'DAY 1',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'DAY 1'], [at('day3').s, 'DAY 3'], [at('week').s, 'WEEK 1']] },
    counter: [[0, 22], [at('leak').e, 18], [at('heating').e, 9], [at('day3').s, 2], [at('zero').e, -2], [at('car').e, -8],
              [at('week').s, -12], [at('average').e, -17], [climax, -18], [T_END, -18]],
    range: [0, -40], forceParams: { darkAt: [-1, 0], frostAt: [.03, .4], snow: 2.2 },
    captions: [[at('day1').s, at('day1').e + .5, 'Day 1.'], [at('lamps').s + 1, at('lamps').e + .3, 'Lamps on at noon.'],
               [at('day3').s, at('day3').e + .8, 'Day 3.'], [at('week').s, at('week').e + .8, 'Week 1.'],
               [at('average').s, at('average').e + .5, '−17 °C, worldwide.']],
    shots: [[0, 'high'], [at('noon').s - .2, 'corner'], [at('lamps').s - .2, 'avenue'], [at('look').s - .2, 'crossing'],
            [at('heat').s - .2, 'balcony'], [at('leak').s - .2, 'high'], [at('inside').s - .2, 'corner'],
            [at('heating').s - .2, 'balcony'], [at('day3').s - .2, 'high'], [at('frost').s - .2, 'crossing'],
            [at('car').s - .2, 'avenue'], [at('week').s - .2, 'high'], [at('snow').s - .2, 'corner'],
            [climax + 2.5, 'high'], [at('palms').s - .2, 'avenue'], [at('only').s - .2, 'high']],
    beats: { lookUp: at('look').s - .5, shelter: at('inside').s, carsStop: at('car').s, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('week').s, climax + 2], riser: [at('average').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
