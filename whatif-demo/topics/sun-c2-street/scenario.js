// What if the Sun went out? Long video (owner's script), chapter 2: the street, day 0 -> day 7.
export const topic = {
  number: 412, slug: 'sun-c2-street', place: 'street', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['catastro', 'At first, nothing seems catastrophic.', 'pause'],
  ['lights', 'Cities turn on their lights. People look into the sky.', 'pause'],
  ['gov', 'Governments begin searching for answers.', 'long'],
  ['butthen', 'But then, the temperature starts dropping.', 'long'],
  ['day1', 'Day one.', 'pause'],
  ['colder', 'Within the first day, the world begins getting colder.', 'pause'],
  ['plants', 'Plants can no longer photosynthesize. Without sunlight, they would begin to die within weeks.', 'pause'],
  ['begin', 'But this is only the beginning.', 'long'],
  ['day3', 'Day three.', 'pause'],
  ['falling', 'Temperatures are falling fast. Below zero, and still dropping.', 'pause'],
  ['crops', 'Crops are failing. Animals are struggling. And people are beginning to panic.', 'pause'],
  ['understand', 'Because everyone now understands the same thing.', 'pause'],
  ['notback', "The Sun isn't coming back.", 'long'],
  ['day7', 'Day seven.', 'pause'],
  ['frozen', 'After one week, the average temperature on Earth would be around minus seventeen degrees. Huge parts of the planet are frozen.', 'pause'],
  ['power', 'Power becomes critical. Food supplies run low.', 'pause'],
  ['compete', 'People compete for heat and shelter.', 'pause'],
  ['hostile', 'And the surface of Earth is becoming more hostile every day.', 5],
  ['truly', 'But then comes the truly terrifying part.', 'none'],
];

export default function (at) {
  const climax = at('hostile').e + .4, T_END = at('truly').e + 3;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'DAY 0',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'DAY 0'], [at('day1').s, 'DAY 1'], [at('day3').s, 'DAY 3'], [at('day7').s, 'DAY 7']] },
    counter: [[0, 22], [at('butthen').e, 20], [at('day1').s, 14], [at('begin').e, 6], [at('day3').s, 2], [at('falling').e, -4],
              [at('notback').e, -8], [at('day7').s, -12], [at('frozen').e, -17], [climax, -18], [T_END, -18]],
    range: [0, -40], forceParams: { darkAt: [-1, 0], frostAt: [.03, .4], snow: 2.2 },
    captions: [[at('day1').s, at('day1').e + .8, 'Day 1.'], [at('day3').s, at('day3').e + .8, 'Day 3.'],
               [at('day7').s, at('day7').e + .8, 'Day 7.'], [at('frozen').s, at('frozen').s + 4, '−17 °C, worldwide.']],
    shots: [[0, 'high'], [at('lights').s - .2, 'crossing'], [at('gov').s - .2, 'balcony'], [at('butthen').s - .2, 'avenue'],
            [at('day1').s - .2, 'high'], [at('plants').s - .2, 'corner'], [at('begin').s - .2, 'avenue'],
            [at('day3').s - .2, 'high'], [at('falling').s - .2, 'crossing'], [at('crops').s - .2, 'corner'],
            [at('notback').s - .2, 'balcony'], [at('day7').s - .2, 'high'], [at('power').s - .2, 'avenue'],
            [at('compete').s - .2, 'corner'], [at('hostile').s - .2, 'high'], [climax + 2.4, 'avenue'], [at('truly').s - .2, 'high']],
    beats: { lookUp: at('lights').s, shelter: at('crops').s, carsStop: at('falling').s, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('day7').s, climax + 2], riser: [at('compete').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
