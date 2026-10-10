// What if a supervolcano erupted? Long video (16:9), chapter 3 (part 2): grounded planes, buried fields. Airport, 600 km away.
// Bricks: place airport (planes on the ground), force eruption (haze, ash fall, ash cover).
export const topic = {
  number: 3504, slug: 'volcano-3b-airport', place: 'airport', force: 'eruption', wide: true, voOffset: .6, padSilence: true,
  question: 'What if a supervolcano erupted?', title: '',
};

export const lines = [
  ['iceland', 'In 2010, a small volcano in Iceland cancelled around one hundred thousand flights.', 'pause'],
  ['larger', 'This eruption could be thousands of times larger.', 3],
  ['week', 'Week one.', 'long'],
  ['fields', 'Grey dust buries farmland across half a continent.', 'long'],
  ['invisible', 'And yet the most dangerous part of this eruption… is something you can\'t see at all.', 'none'],
];

export default function (at) {
  const T_END = at('invisible').e + 1.6;
  return {
    T_END, tripod: true, brand: false, post: true,
    hud: { label: 'DISTANCE TO THE VOLCANO', unit: ' KM', decimals: 0, sub: 'DAY 1', subAt: [[0, 'DAY 1'], [at('week').s, 'WEEK 1']] },
    counter: [[0, 600], [T_END, 600]],
    forceParams: {
      vent: null,
      haze: [[0, .85], [T_END, .95]],
      dark: [[0, .25], [at('week').s, .3], [T_END, .2]],
      ash: [[0, .9], [at('week').s, .7], [T_END, .3]],
      cover: [[0, .45], [at('week').s - .5, .5], [at('week').e + .5, .9], [T_END, .95]],
      loud: [[0, .15], [T_END, .1]],
    },
    captions: [[at('iceland').s + 2, at('iceland').e + .3, '2010: ~100,000 flights cancelled.']],
    shots: [[0, 'apron'], [at('larger').s - .2, 'pov-window'], [at('larger').e + 1.2, 'runway'], [at('week').s - .2, 'fields'], [at('invisible').s - .2, 'apron']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, climax: 1e9, falls: [], stop: T_END + 2, fade: 1e9, end: 1e9 },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if a supervolcano erupted?', description: 'Hoofdstuk 3b, niet los uploaden.', tags: [], tiktok: '' };
