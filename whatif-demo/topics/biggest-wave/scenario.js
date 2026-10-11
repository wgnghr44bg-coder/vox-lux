// PROEF nieuwe serie: groottevergelijkingen in 3D (eigenaar, 11 okt 2026). Standaard-look (regels/standaard-video.md):
// plek 'boulevard' + kracht 'calm' + baksteen Golf (engine/wave.js). Feiten en bronnen: upload.sources.
export const topic = {
  number: 3510, slug: 'biggest-wave', place: 'boulevard', force: 'calm',
  question: 'How tall was the biggest wave ever recorded?',
  title: 'How tall was<br>the biggest wave<br>ever recorded?',
  voOffset: 1.0, padSilence: true,
};

// [id, text, pause after]: 'pause', 'long' or seconds of silence (the climax). Documentairetempo.
export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'a wave taller than anything in this city.', 'long'],
  ['normal', 'A normal wave: about two meters.', 'long'],
  ['house', 'As tall as a house: ten meters.', 'long'],
  ['japan', 'The tsunami in Japan, in 2011, surged up to about forty meters.', 'long'],
  ['tower', 'This office tower: three hundred meters.', 'long'],
  ['lituya', 'But in 1958, in Lituya Bay, Alaska, a landslide crashed into the water.', 'pause'],
  ['climb', 'The water raced up the mountain…', 3],
  ['num', 'five hundred and twenty-four meters.', 'long'],
  ['record', 'The highest wave ever recorded.', 'long'],
  ['q', 'Is anything in your city that tall?', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 1.8;
  const hs = at('house').s, js = at('japan').s, ts = at('tower').s, c0 = at('climb').s;
  const runEnd = at('num').s + .6;
  return {
    textScale: 1.3, sunbathers: 0,
    T_END, titleOut: at('intro').e + .8, hudIn: at('intro').e + 1, fov: 60,
    hud: { label: 'HEIGHT', fmt: v => Math.round(v) + ' m',
           subAt: [[0, 'A NORMAL WAVE'], [hs, 'A HOUSE'], [js, 'TSUNAMI · JAPAN 2011'], [ts, 'OFFICE TOWER'], [at('lituya').s, 'LITUYA BAY · 1958'], [c0, 'RUN-UP · LITUYA BAY 1958']] },
    counter: [[0, 2], [hs + .3, 2], [hs + 2.2, 10], [js - .4, 10], [js + 1.2, 40], [ts - .3, 40], [ts + 1.6, 300], [c0, 300], [c0 + .2, 300], [runEnd, 524], [T_END, 524]],
    range: [0, 524],
    captions: [[at('japan').s + 1.3, at('japan').e + .8, 'Japan, 2011: up to 40 m.'],
               [at('lituya').s + .2, at('lituya').e + .6, 'Lituya Bay, Alaska, 1958.'],
               [at('num').s, at('record').e + .6, 'Run-up: 524 m up the mountain slope.']],
    wave: {
      h: [[0, 2], [hs + .3, 2], [hs + 2.2, 10], [js - .4, 10], [js + 1.2, 40], [T_END, 40]],
      front: -10, x: [-260, 320], label: [at('normal').s, at('tower').e], labelX: -20,
      sizes: [{ kind: 'house', x: -38, z: 49, h: 10, label: [hs, at('tower').e] },
              { kind: 'tower', x: 90, z: 132, h: 300, w: 34, d: 30, label: [ts, T_END] }],
      runup: { h: [[0, 0], [c0, 0], [c0 + 1.2, 90], [runEnd - 1.2, 470], [runEnd, 524], [T_END, 524]], at: [-850, -250], r: [550, 600], peak: 950, face: [.818, -.575, 552],
               label: [runEnd, T_END], labelAt: [-507, -491], lineRy: .613 },
    },
    placeParams: {}, clear: [[-40, 25], [-34, 21], [-26, 19], [-48, 26], [-18, 18], [-140, 14], [-128, 16], [-116, 20], [-104, 24], [-150, 22]],
    groups: [{ at: [-10, 17], n: 6, spread: 2.4, face: Math.PI, lamp: false }],
    camPath: [   // [t, position, look at, fov]
      [0, [-40, 2.4, 25], [30, 3, -4], 62],
      [at('normal').s, [-34, 2.3, 21], [14, 2, -8], 62],
      [hs + .6, [-130, 8, 14], [-35, 7, 20], 70],
      [js + .3, [-150, 14, 30], [-20, 12, 10], 66],
      [js + 3.5, [-180, 30, 50], [-10, 26, 0], 62],
      [ts + .2, [-230, 60, 70], [60, 110, 110], 60],
      [at('tower').e + 1, [-60, 200, -300], [90, 220, 132], 58],
      [at('lituya').s + 1.8, [600, 280, -1000], [-100, 290, -100], 54],
      [c0, [1420, 170, -1820], [-300, 470, -250], 56],
      [at('record').s, [1500, 150, -1900], [-300, 520, -250], 56],
      [T_END, [1470, 150, -1870], [-300, 520, -250], 56],
    ],
    beats: { lookUp: hs + 1, climax: c0, stop: T_END },
  };
}

export const upload = {
  title: 'How tall was the biggest wave ever recorded?',
  description: 'A normal wave. A house. A tsunami. A skyscraper… and then Alaska, 1958. 🌊\n\nIs there anything in your city that tall? 👇\n\n#whatif #tsunami #science #shorts',
  tags: ['biggest wave', 'lituya bay', 'megatsunami', 'size comparison', 'tsunami', '3d animation', 'IfScape3D'],
  tiktok: 'How tall was the biggest wave ever recorded? 🌊 From 2 m to… Lituya Bay, 1958. Is anything in your city that tall? #whatif #tsunami #sizecomparison #fyp',
  sources: [
    'Lituya Bay 1958, run-up 524 m (1,720 ft): Miller, D.J. (1960), Giant waves in Lituya Bay, Alaska, USGS Professional Paper 354-C – https://pubs.usgs.gov/pp/0354c/report.pdf',
    'https://en.wikipedia.org/wiki/1958_Lituya_Bay_earthquake_and_megatsunami',
    'Japan 2011, run-up up to 40.5 m (Miyako): NASA Earth Observatory – https://www.naturalhazards.nasa.gov/images/148036/ten-years-after-the-tsunami',
    'Normal wave ≈ 2 m (moderate sea 1.25–2.5 m): https://en.wikipedia.org/wiki/Sea_state',
  ],
};
