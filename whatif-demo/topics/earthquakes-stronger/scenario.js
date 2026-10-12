// What if the earthquakes kept getting stronger?  (onderwerpen.md #47; aangeleverd door de eigenaar, passend gemaakt
// op de engine). Plek 'street' (laan naar zee, wolkenkrabbers bij het water) + kracht 'quake'. Blender-look.
// Je loopt achter iemand met een hond over de stoep langs de gevels (x ≈ 14,5–15,5; bomen/palmen staan op 12,4/13,6); de magnitude loopt van 3 naar 1000.
// Engine-feiten: elke hele stap = 10^1,5 ≈ 32× meer energie; E ≈ 10^(1,5·M + 4,8) J.
export const topic = {
  number: 47, slug: 'earthquakes-stronger', place: 'street', force: 'quake',
  question: 'What if the earthquakes kept getting stronger?',
  title: 'What if<br>earthquakes kept<br>getting stronger?',
  voOffset: 1.0,
};

export const lines = [
  ['imagine', 'Imagine you are standing on a quiet street in New York, a hot dog cart steaming next to you.', 'pause'],
  ['intro', 'What if the earthquakes kept getting stronger?', 'pause'],
  ['normal', 'Normally the ground barely trembles beneath your feet.', 'pause'],
  ['three', 'At magnitude three, only the pigeons notice.', 'long'],
  ['five', 'At magnitude five, New York matches its eighteen eighty four record and windows rattle.', 'pause'],
  ['six', 'Each whole step releases thirty two times more energy.', 'pause'],
  ['seven', 'At seven, the street is no longer flat and cars stop driving.', 'long'],
  ['nine', 'Nine point five is the strongest ever recorded, in Chile in nineteen sixty.', 'pause'],
  ['ten', 'At ten, no known fault is long enough and the ground moves like water.', 'long'],
  ['twelve', 'At twelve, the street splits wide open.', 'pause'],
  ['fifteen', 'At fifteen, the ground throws you into space.', 'long'],
  ['eighteen', 'Past eighteen, Earth cannot hold itself together anymore.', 'pause'],
  ['fifty', 'At fifty, it releases more energy than the entire universe has.', 'long'],
  ['scale', 'The scale itself has no upper limit.', 'pause'],
  ['q', 'So where would it finally stop?', 'none'],
];

// energie bij magnitude m, als tekst (10-machten zonder Infinity: we rekenen met de exponent)
const energy = m => {
  const x = 1.5 * m + 4.8;
  if (x < 6) return Math.round(10 ** x).toLocaleString('en-US') + ' J';
  const e = Math.floor(x), mant = 10 ** (x - e);
  return `${mant.toFixed(1)} × 10^${e} J`;
};

export default function (at) {
  const T_END = at('q').e + 4.5;
  const s3 = at('three').s, s5 = at('five').s, s6 = at('six').s, s7 = at('seven').s, s9 = at('nine').s, s10 = at('ten').s,
        s12 = at('twelve').s, s15 = at('fifteen').s, s18 = at('eighteen').s;
  // wandeling over de stoep richting zee (-z); bij magnitude 7 blijven ze staan
  const z0 = 26, v = 1.15, dogZ = t => z0 - v * Math.min(t, s7);
  return {
    T_END,
    look: 'blender',

    // ---- titel en teller ----
    titleOut: at('intro').e + .4,
    hudIn: at('three').s - .3,
    hud: { label: 'MAGNITUDE', unit: '', decimals: 1,
           second: { label: 'ENERGY', fn: v => v, fmt: m => energy(m), showAt: at('six').s } },
    counter: [[0, 3], [s3, 3], [s5, 5], [s6, 6], [s7, 7], [s9, 9.5], [s10, 10], [s12, 12], [s15, 15], [s18, 18],
              [at('fifty').s, 50], [at('scale').s, 100], [at('q').s, 1000], [T_END, 1000]],
    range: [3, 18],

    // ---- de aardbeving: [t, sterkte 0..1, duur s]; daarna houdt het schudden niet meer op ----
    forceParams: {
      tremors: [[at('normal').s, .03, 3], [s3, .06, 3.5], [s5, .2, 4.5], [s6, .3, 3.5], [s7, .5, 6.5], [s9, .7, 5],
                [s10, .85, 6.5], [s12, 1, 9], [s15, 1, T_END - s15 + 1]],
      crackK: 3,
    },

    captions: [
      [at('three').s, at('three').e + .8, 'Only the pigeons notice.'],
      [at('five').s, at('five').e + .8, 'At 5, New York matches its 1884 record.'],
      [at('six').s, at('six').e + .8, 'Each step releases 32 times more energy.'],
      [at('seven').s, at('seven').e + .8, 'At 7, the street is no longer flat.'],
      [at('nine').s, at('nine').e + .8, '9.5 is the strongest ever recorded.'],
      [at('ten').s, at('ten').e + .8, 'At 10, the ground moves like water.'],
      [at('twelve').s, at('twelve').e + .8, 'At 12, the street splits wide open.'],
      [at('fifteen').s, at('fifteen').e + .8, 'At 15, the ground throws you into space.'],
      [at('eighteen').s, at('eighteen').e + .8, 'Past 18, Earth cannot hold itself together.'],
      [at('fifty').s, at('fifty').e + .8, 'At 50, more energy than the universe has.'],
      [at('scale').s, at('q').e, 'The scale itself has no upper limit.'],
    ],

    // ---- camera: achter de wandelaar aan, omhoog naar de gevels, omlaag naar de scheuren, dan steeds hoger ----
    camPath: [
      [0, [15.1, 1.6, dogZ(0) + 4.4], [13.4, 2.2, dogZ(0) - 30]],
      [s3, [15.1, 1.6, dogZ(s3) + 4.4], [13.4, 2.2, dogZ(s3) - 30]],
      [s5, [15.6, 1.65, dogZ(s5) + 4.2], [11, 12, dogZ(s5) - 30]],             // kijkt omhoog naar de gevels
      [s7, [15.6, 1.5, dogZ(s7) + 4.0], [11, 0, dogZ(s7) - 9]],                 // omlaag: de straat is niet meer vlak
      [s10, [15.5, 4.5, dogZ(s7) + 9], [4, 0, dogZ(s7) - 25]],
      [s12, [16, 16, dogZ(s7) + 26], [0, 0, dogZ(s7) - 50]],                   // de straat splijt
      [s15, [10, 60, dogZ(s7) + 80], [0, 0, -90]],
      [s18, [0, 140, 150], [0, 0, -110]],
      [T_END, [-10, 260, 240], [0, 0, -120]],
    ],
    fov: 62,

    // ---- mensen en dieren ----
    groups: [{ at: [13.4, -12], n: 5, spread: 1.6, face: 0, coats: [0x2f5d8a, 0x8a3b2f, 0x3a7a4a], lamp: false }],
    animals: [
      { kind: 'dog', path: [[0, 14.9, dogZ(0)], [s7, 14.9, dogZ(s7)], [T_END, 14.9, dogZ(s7)]], act: 'look', color: 0xb08a5a,
        walker: { side: -.5, behind: 1.1, coat: 0x27324f, pants: 0x1e2a40 } },
      { kind: 'birds', n: 14, center: [6, 9, 2], radius: 10 },                // de duiven
    ],
    smoke: [[s10 + 1, -4, 0, -60, 8], [s12 + .5, 6, 0, -120, 12]],

    // ---- momenten ----
    beats: {
      stop: T_END, climax: s12,
      lookUp: s5, shelter: s7, carsStop: s6,
      windows: s5 + .8, walls: s7 + 1, floors: s10 + .5, powerOut: s10,
      falls: [s12 + .3, s12 + 1.6, s15],
    },
  };
}

export const upload = {
  title: 'What if the earthquakes kept getting stronger?',
  description: 'What if magnitude 3 became 5, 7, 10, 15 and kept going? Starting on a quiet street with pigeons, then each step releases 32 times more energy until the street is no longer flat, the ground moves like water and Earth cannot hold itself together.\n\n#whatif #earthquake #science #simulation #shorts',
  tags: ['what if', 'earthquake', 'magnitude', 'science', 'simulation', '3d animation', 'IfScape3D', 'New York'],
  tiktok: 'What if earthquakes kept getting stronger? From pigeons to planet shattering #whatif #earthquake #science #fyp',
  sources: [
    'USGS – Magnitude and energy: each whole magnitude step ≈ 32× more energy – https://www.usgs.gov/programs/earthquake-hazards/how-much-bigger-earthquake',
    'USGS – 10 August 1884 New York earthquake, magnitude ≈ 5.2 (largest in the New York City area)',
    'USGS – 1960 Valdivia, Chile, M 9.5: largest earthquake ever recorded – https://earthquake.usgs.gov/earthquakes/eventpage/official19600522191120_30',
    'Energy: log10 E ≈ 1.5 M + 4.8 (E in joules), Gutenberg–Richter energy relation',
    'Own check: Earth\'s gravitational binding energy ≈ 2.2 × 10³² J  →  M ≈ (32.35 − 4.8) / 1.5 ≈ 18.4',
    'Own check: M 50 ≈ 10^79.8 J; mass-energy of the observable universe ≈ 10^70 J (≈ 10^53 kg × c²)',
    'No magnitude above ≈ 10 is possible on known faults (rupture length limits): USGS FAQ – https://www.usgs.gov/faqs/can-megaquakes-really-happen-a-magnitude-10-or-larger',
  ],
};
