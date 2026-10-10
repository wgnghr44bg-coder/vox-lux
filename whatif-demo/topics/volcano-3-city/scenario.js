// What if a supervolcano erupted? Long video (16:9), chapter 3: the ash (part 1). River city, 600 km away.
// Bricks: force eruption without a column (haze, ash fall, ash cover, alarm), place river-city.
export const topic = {
  number: 3503, slug: 'volcano-3-city', place: 'river-city', force: 'eruption', wide: true, voOffset: 1.2, padSilence: true,
  question: 'What if a supervolcano erupted?', title: '',
};

export const lines = [
  ['day', 'Day one.', 'long'],
  ['snow', 'Six hundred kilometres away, it begins to snow.', 'pause'],
  ['grey', 'Except this snow is grey… and it will never melt.', 'long'],
  ['glass', 'Volcanic ash isn\'t soft like smoke.', 'pause'],
  ['sharp', 'It is shattered rock and glass, sharp enough to sting your eyes and lungs.', 'long'],
  ['heavy', 'And it is heavy.', 'pause'],
  ['kilos', 'Ten centimetres of wet ash could press up to two hundred kilos onto every square metre of a roof.', 'long'],
  ['sirens', 'Sirens.', 'pause'],
  ['close', 'Roads close.', 'pause'],
  ['choke', 'Engines choke as the ash clogs them.', 'long'],
];

export default function (at) {
  const T_END = at('choke').e + 1.2;
  return {
    T_END, tripod: true, brand: false, post: true,
    hud: { label: 'DISTANCE TO THE VOLCANO', unit: ' KM', decimals: 0, sub: 'DAY 1' },
    counter: [[0, 600], [T_END, 600]],
    forceParams: {
      vent: null,
      haze: [[0, .35], [at('snow').s, .55], [T_END, .9]],
      dark: [[0, 0], [at('grey').s, .1], [T_END, .3]],
      ash: [[0, 0], [at('snow').s, 0], [at('snow').e, .5], [at('sharp').e, .9], [T_END, 1]],
      cover: [[0, 0], [at('snow').e, .05], [at('heavy').s, .45], [T_END, .8]],
      alarm: { siren: [64, -14, at('sirens').s - .4], block: [24, 6, at('sirens').s, 0] },
      loud: [[0, .05], [T_END, .2]],
    },
    captions: [[at('kilos').s + 1, at('kilos').e + .3, 'Up to 200 kg per m².']],
    shots: [[0, 'north'], [at('snow').s - .2, 'quay'], [at('grey').s - .2, 'pov-walk'], [at('glass').s - .2, 'wide'],
            [at('heavy').s - .2, 'far'], [at('sirens').s - .2, 'road']],
    beats: { lookUp: at('snow').s + 1, shelter: at('glass').s + 2, carsStop: at('sirens').s + 1.5, climax: 1e9, falls: [], stop: T_END + 2, fade: 1e9, end: 1e9 },
    audio: { siren: [[at('sirens').s - .4, T_END + 1]] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if a supervolcano erupted?', description: 'Hoofdstuk 3a, niet los uploaden.', tags: [], tiktok: '' };
