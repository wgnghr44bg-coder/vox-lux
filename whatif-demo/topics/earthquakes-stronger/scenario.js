// What if the earthquakes kept getting stronger?  (onderwerpen.md #47; tijdlijn van de eigenaar, okt 2026)
// GEEN STEM, alleen tekst: 83 s, de tijden staan vast in timing.json (VO_OFFSET 0; de ids hieronder = de hoofdstukken).
// Plek 'newyork' (places/newyork.js) + kracht 'quake'. Eerste persoon (POV), Blender-look.
// Stap 1 (deze versie): de straat t/m magnitude 12 (0-50 s). Stap 2 (later): de ruimte, de brekende aarde (55-75 s) en de
// zwarte leegte met gebroken glas (75-83 s); tot die er zijn stijgt de camera na 50 s hoog boven de stad.
export const topic = {
  number: 47, slug: 'earthquakes-stronger', place: 'newyork', force: 'quake',
  question: 'What if the earthquakes kept getting stronger?',
  title: 'What if the<br>earthquakes kept<br>getting stronger?',
  voOffset: 0, textOnly: true,
};

// [id, tekst (alleen als ondertitel, niet gesproken), -]; tijden: timing.json
export const lines = [
  ['title', 'What if the earthquakes kept getting stronger?', 'none'],
  ['three', 'Magnitude 3. Only the pigeons notice.', 'none'],
  ['five', 'At 5, New York matches its 1884 record.', 'none'],
  ['six', 'Each step releases 32 times more energy.', 'none'],
  ['seven', 'At 7, the street is no longer flat.', 'none'],
  ['nine', '9.5 is the strongest ever recorded.', 'none'],
  ['ten', 'At 10, the ground moves like water.', 'none'],
  ['twelve', 'At 12, the street splits wide open.', 'none'],
  ['fifteen', 'At 15, the ground throws you into space.', 'none'],
  ['eighteen', 'Past 18, Earth cannot hold itself together.', 'none'],
  ['fifty', 'At 50, more energy than the universe has.', 'none'],
  ['scale', 'The scale itself has no upper limit.', 'none'],
];

// ENERGY zoals in de referentie: 10^(1,5·M − 1,2) (M3 → 2.000, M5 → 2.000.000, M6 → 63.100.000), zonder Infinity
const energy = m => {
  const x = 1.5 * m - 1.2;
  if (x < 15) return Math.round(10 ** x).toLocaleString('en-US');
  const e = Math.floor(x); return `${(10 ** (x - e)).toFixed(1)} × 10^${e}`;
};

export default function (at) {
  const T_END = 83;
  const cap = id => [at(id).s + .2, at(id).e - .2, lines.find(l => l[0] === id)[1]];
  // POV-wandeling over de rechterstoep (vrije strook x 14-15,8), richting -z, 1,15 m/s tot 13 s
  const X = 14.6, z = t => 24 - 1.15 * Math.min(t, 13);
  return {
    T_END, look: 'blender', brand: false,
    titleOut: 5, hudIn: 0,
    hud: { label: 'MAGNITUDE', unit: '', decimals: 1, second: { label: 'ENERGY', fn: v => v, fmt: m => energy(m), showAt: 0 } },
    counter: [[0, 3], [5, 3], [6, 3.9], [8, 3.9], [9, 4.5], [12.5, 5], [14, 6], [22, 6], [23, 7], [31, 7.5], [33, 8], [39, 9.5],
              [41, 10], [46, 10], [47, 12], [50, 12], [51, 15], [55, 15], [56, 18], [61, 20], [63, 32], [73, 50], [76, 100], [80, 1000], [83, 1000]],
    range: [3, 18],
    forceParams: {
      tremors: [[0, .01, 5], [5, .04, 3.2], [8, .12, 5.2], [13, .45, 9.2], [22, .55, 10.2], [32, .75, 8.2], [40, .9, 6.2], [46, 1, 40]],
      crackK: 4,
    },
    captions: [cap('three'), cap('five'), cap('six'), cap('seven'), cap('nine'), cap('ten'), cap('twelve'), cap('fifteen'),
               cap('eighteen'), cap('fifty'), [75.2, 79.8, 'The scale itself has no upper limit.'], [80, 83, 'MAGNITUDE 1,000 HERE']],

    // camera: [t, positie, kijkt naar, fov, kanteling°]
    camPath: [
      [0, [X, 1.7, z(0)], [13.6, 2, -20], 75, 0],                  // POV ooghoogte, loopt
      [5, [X, 1.7, z(5)], [13.6, 2, -20], 75, 0],                  // duiven vliegen op
      [8, [X, 1.7, z(8)], [13.6, 2.2, -20], 60, 0],
      [9.6, [X, 1.7, z(9.6)], [-16, 9, z(9.6) - 6], 60, -8],        // whip-pan naar links
      [11.2, [X, 1.7, z(11.2)], [16.6, 26, z(11.2) - 9], 60, 10],   // en rechts omhoog langs de gevels (Dutch angle)
      [13, [X, 1.7, z(13)], [15, 28, z(13) - 14], 60, 10],
      [15, [X, 1.7, z(13)], [6, 11, -80], 85, 4],                   // breed: torens storten in
      [22, [14.4, 1.6, z(13) - .3], [4, 14, -90], 85, -3],
      [23.5, [14.2, 1.2, z(13) - .4], [8, 0, z(13) - 14], 70, 25],  // laag, kijkt omlaag naar de golvende straat
      [32, [14.2, 1.0, z(13) - .6], [6, 0, z(13) - 18], 70, 22],
      [34, [10, .9, z(13) - 3], [2, -1, z(13) - 20], 95, 10],       // duikt naar de scheuren
      [40, [3, .5, -2], [0, -2, -14], 100, 0],
      [42, [1, .3, -6], [3, 40, -12], 100, 0],                       // laag in de straat, kijkt omhoog
      [46, [1, .6, -6], [2, 36, -14], 95, 0],
      [50, [6, 35, 24], [0, 0, -40], 60, 0],                         // dolly-out naar 35 m: de straat splijt
      [55, [10, 300, 200], [0, 0, -60], 55, 0],                      // (stap 2: de ruimte in)
      [T_END, [20, 600, 400], [0, 0, -80], 55, 0],
    ],
    fov: 75,
    walkBob: [[0, 13, .035]],

    groups: [{ at: [13.6, -4], n: 5, spread: 1.4, face: 0, coats: [0x2f5d8a, 0x8a3b2f, 0x3a7a4a], lamp: false }],
    animals: [
      { kind: 'birds', n: 14, color: 0x8e9094, land: -6, fly: 5.2,     // duiven op de stoep, vliegen op bij 5 s
        center: [8, 10, 14], radius: 9,
        perch: Array.from({ length: 14 }, (_, i) => [13.6 + (i % 4) * .45, .26, 19 - Math.floor(i / 4) * .9 - (i % 2) * .3]) },
    ],
    smoke: [[16, -4, 0, -60, 8], [20, 6, 0, -110, 12], [33, -2, 0, -20, 6]],

    beats: {
      stop: T_END, climax: 46,
      lookUp: 8.5, carsStop: 13, shelter: 13.5,
      windows: 9.5, walls: 13.5, floors: 15, powerOut: 32,
      falls: [16.5, 18, 20],
    },
  };
}

export const upload = {
  title: 'What if the earthquakes kept getting stronger?',
  description: 'Magnitude 3: only the pigeons notice. Magnitude 7: the street is no longer flat. And it keeps going… 🌍\n\nWhere do you think it would stop? 👇\n\n#whatif #earthquake #science #simulation #shorts',
  tags: ['what if', 'earthquake', 'magnitude', 'science', 'simulation', '3d animation', 'IfScape3D', 'New York'],
  tiktok: 'What if earthquakes kept getting stronger? From pigeons to planet shattering 🌍 #whatif #earthquake #science #fyp',
  sources: [
    'USGS – each whole magnitude step ≈ 32× more energy – https://www.usgs.gov/programs/earthquake-hazards/how-much-bigger-earthquake',
    'USGS – 10 August 1884 New York earthquake, magnitude ≈ 5.2',
    'USGS – 1960 Valdivia, Chile, M 9.5: largest earthquake ever recorded',
    'Own check: Earth\'s gravitational binding energy ≈ 2.2 × 10³² J  →  M ≈ 18.4 (log10 E ≈ 1.5 M + 4.8)',
    'Own check: M 50 ≈ 10^79.8 J; mass-energy of the observable universe ≈ 10^70 J',
    'ENERGY on screen: relative number 10^(1.5·M − 1.2), as in the reference timeline (not joules)',
  ],
};
