// PROEF nieuwe serie: groottevergelijkingen in 3D (eigenaar, 11-12 okt 2026): een VERGELIJKINGSRIJ van golven, klein -> groot,
// elk met maatobject en bordje (naam, jaar, hoogte); camera rijdt langs de rij; finale Lituya Bay (run-up 524 m) naast 300 m-toren.
// Standaard-look (regels/standaard-video.md): plek 'boulevard' (zonder hotels) + kracht 'calm' + baksteen Golf (engine/wave.js).
// Feiten en bronnen: upload.sources.
export const topic = {
  number: 3510, slug: 'biggest-wave', place: 'boulevard', force: 'calm',
  question: 'What if the biggest wave ever recorded hit your city?',
  title: 'What if the biggest<br>wave ever recorded<br>hit your city?',
  voOffset: 1.0, padSilence: true,
};

// [id, text, pause after]: 'pause', 'long' or seconds of silence (the climax). Documentairetempo.
export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'the biggest wave ever recorded.', 'long'],
  ['normal', 'A normal wave: about two meters.', 'long'],
  ['nazare', 'Nazaré, 2020: the biggest wave ever surfed. Twenty-six meters.', 'long'],
  ['japan', 'Japan, 2011: up to forty meters.', 'long'],
  ['aceh', 'Indonesia, 2004: about fifty meters.', 'long'],
  ['tower', 'This skyscraper: three hundred meters.', 'long'],
  ['lituya', 'And then… Lituya Bay, Alaska, 1958.', 'pause'],
  ['slide', 'A landslide hit the bay. The water raced up the mountain…', 3],
  ['num', 'five hundred and twenty-four meters. The highest wave ever recorded.', 'long'],
  ['q', 'What in your city would still be above it?', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 1.8;
  const ns = at('nazare').s, js = at('japan').s, as = at('aceh').s, ts = at('tower').s, c0 = at('slide').e - .3;
  const runEnd = at('num').s + .6;
  return {
    textScale: 1.3, sunbathers: 0, noHotels: true, sunOffset: [60, 170, 150],
    T_END, titleOut: at('intro').e + .8, hudIn: at('intro').e + 1,
    hud: { label: 'HEIGHT', fmt: v => Math.round(v) + ' m',
           subAt: [[0, 'A NORMAL WAVE'], [ns, 'NAZARÉ · 2020'], [js, 'JAPAN · 2011'], [as, 'INDONESIA · 2004'], [ts, 'SKYSCRAPER'], [at('lituya').s, 'LITUYA BAY · 1958'], [c0, 'RUN-UP · LITUYA BAY 1958']] },
    counter: [[0, 2], [ns - .2, 2], [ns + 1, 26], [js - .2, 26], [js + 1, 40], [as - .2, 40], [as + 1, 51], [ts - .2, 51], [ts + 1.4, 300], [c0, 300], [runEnd, 524], [T_END, 524]],
    range: [0, 524],
    captions: [[as + .3, at('aceh').e + .8, 'Run-up: how high the water reached on land.'],
               [at('num').s, at('num').e + .6, 'Run-up: 524 m up the mountain slope.']],
    wave: {
      waves: [
        { h: 2, x: [-26, -8], front: -8, sign: { top: 'NORMAL WAVE', big: '≈ 2 m', at: [at('normal').s - .3, ns + .5] } },
        { h: 26, x: [8, 48], front: -8, sign: { top: 'NAZARÉ · 2020', big: '26 m', at: [ns, js + .6] } },
        { h: 40, x: [78, 132], front: -8, sign: { top: 'JAPAN · 2011', big: '40 m', at: [js, as + .6] } },
        { h: 51, x: [168, 236], front: -8, sign: { top: 'INDONESIA · 2004', big: '51 m', at: [as, ts + .6] } },
      ],
      sizes: [{ kind: 'house', x: 60, z: 1, w: 8, d: 8, h: 10, name: 'HOUSE', label: [ns + .4, js + .6] },
              { kind: 'flat', x: 150, z: 0, w: 18, d: 12, h: 40, name: 'APARTMENTS', label: [js + .4, ts + .6] },
              { kind: 'tower', x: 300, z: 14, w: 30, d: 26, h: 300, name: 'SKYSCRAPER', k: .9, label: [ts, T_END] }],
      runup: { h: [[0, 0], [c0, 0], [c0 + 1.2, 90], [runEnd - 1.2, 470], [runEnd, 524], [T_END, 524]], at: [900, -150], r: [400, 420], peak: 920, face: [-.769, -.639, 596.2],
               name: 'LITUYA BAY · 1958', label: [runEnd, T_END], labelAt: [667, -343], lineRy: -.693 },
      town: { n: 380, x: [-700, 1400], z: [260, 1600] },
    },
    groups: [{ at: [-13, 5], n: 3, spread: 2, face: Math.PI, lamp: false }],
    camPath: [   // [t, position, look at, fov]: along the row from small to big (looking out to sea), then out over the sea for the finale
      [0, [-15, 1.7, 13], [-15, 1.5, -8], 62],
      [at('normal').s, [-16, 1.8, 12], [-16, 1.7, -8], 62],
      [at('normal').e + .8, [-12, 2.4, 14], [-12, 2, -8], 62],
      [ns + .3, [34, 16, 72], [34, 20, -8], 60],
      [at('nazare').e, [38, 17, 74], [38, 21, -8], 60],
      [js + .3, [116, 24, 112], [116, 31, -8], 60],
      [as + .3, [198, 30, 138], [198, 40, -8], 60],
      [at('aceh').e + .5, [204, 32, 142], [204, 42, -8], 60],
      [ts + .3, [250, 40, 200], [300, 120, 10], 60],
      [at('tower').e + .8, [250, 220, 450], [262, 250, 10], 56],
      [at('lituya').s + 1.2, [-300, 300, -300], [500, 330, -150], 50],
      [c0, [-1050, 230, -1700], [493, 520, -176], 46],
      [at('num').e, [-1190, 210, -1887], [493, 520, -176], 44],
      [T_END, [-1210, 208, -1910], [493, 520, -176], 44],
    ],
    beats: { lookUp: 1e9, climax: c0, stop: T_END },
  };
}

export const upload = {
  title: 'What if the biggest wave ever recorded hit your city?',
  description: 'A normal wave. Nazaré. Japan. Indonesia… and then Alaska, 1958. 🌊\n\nWhat in your city would still be above it? 👇\n\n#whatif #tsunami #science #shorts',
  tags: ['biggest wave', 'lituya bay', 'megatsunami', 'size comparison', 'tsunami', 'nazare', '3d animation', 'IfScape3D'],
  tiktok: 'What if the biggest wave ever recorded hit your city? 🌊 2 m → 26 m → 40 m → 51 m → 524 m. What in your city would still be above it? #whatif #tsunami #sizecomparison #fyp',
  sources: [
    'Lituya Bay 1958, run-up 524 m (1,720 ft): Miller, D.J. (1960), Giant waves in Lituya Bay, Alaska, USGS Professional Paper 354-C – https://pubs.usgs.gov/pp/0354c/report.pdf ; https://en.wikipedia.org/wiki/1958_Lituya_Bay_earthquake_and_megatsunami',
    'Japan 2011, run-up up to 40.5 m (Miyako): NASA – https://www.naturalhazards.nasa.gov/images/148036/ten-years-after-the-tsunami',
    'Indian Ocean 2004, max run-up ≈ 51 m (Aceh): NOAA – https://sos.noaa.gov/catalog/datasets/tsunami-wave-run-ups-indian-ocean-2004/',
    'Nazaré 2020, 26.21 m, largest wave surfed (Sebastian Steudtner): Guinness World Records – https://www.guinnessworldrecords.com/news/2022/5/sebastian-steudtner-surfs-giant-wave-and-smashes-world-record-705874',
    'Normal wave ≈ 2 m (moderate sea 1.25–2.5 m): https://en.wikipedia.org/wiki/Sea_state',
  ],
};
