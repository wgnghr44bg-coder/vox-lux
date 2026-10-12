// What if you were playing zombies and they became real?  (onderwerpen.md #48; idee van de eigenaar, okt 2026)
// Plek 'gameroom' (gamekamer 5e verdieping, nacht, ledstrips, balkon, smalle straat; voorbeeldbeelden eigenaar) + kracht 'calm'.
// Cartoon-zombies (engine/zombies.js): geen bloed, niemand wordt aangeraakt, alleen vluchten (regels: geen geweld).
// STAP 1 (deze versie): tv-game -> balkon -> de horde dringt het gebouw binnen (t/m regel inside).
// STAP 2 (later): bonken op je deur, gang, brandtrap (5 verdiepingen), naar buiten (regels floors-q).
export const topic = {
  number: 48, slug: 'zombies-real', place: 'gameroom', force: 'calm',
  question: 'What if your zombie game became real?',
  title: 'Imagine if there was<br>a zombie apocalypse…',   // in beeld bij de start
  voOffset: 1.0,
};

export const lines = [
  ['imagine', 'Imagine if there was a zombie apocalypse…', 'pause'],          // = de titel in beeld
  ['intro', 'And it starts tonight, while you are playing a video game.', 'pause'],
  ['mean', 'Just you, the screen, and round twelve.', 'long'],
  ['place', 'Fifth floor. Your apartment is quiet.', 'pause'],
  ['game', 'Then you hear it. Noise outside. Not from the game.', 'long'],
  ['sound', 'Screaming. A car alarm. Something heavy falling over.', 'long'],
  ['balcony', 'You put the controller down, step onto the balcony, and look outside.', 'pause'],
  ['street', 'Down in the street, people are walking strangely. Slowly. Arms out in front of them.', 'long'],
  ['speed', 'These are not players. These are real zombies.', 'long'],
  ['door', 'And they are not walking past. They are heading for your apartment complex.', 'pause'],
  ['inside', 'The front door gives way. They are inside.', 'long'],
  ['floors', 'Five floors between you and them. You need a way out.', 'long'],
  ['bang', 'Then something bangs on your own door.', 3.5],
  ['keys', 'No time. You grab your keys and slip out the back, toward the fire stairs.', 'pause'],
  ['stairs', 'Down, two steps at a time. Third floor. Second. First.', 'long'],
  ['outside', 'You push open the emergency exit into the cold night air, and you run.', 'long'],
  ['behind', 'Upstairs, the game is still running. Round thirteen.', 'pause'],
  ['q', 'Would you have found a way out?', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 2.4, OUT = -15;
  const S = id => at(id).s, Ee = id => at(id).e, BAL = S('balcony'), DOOR = S('door');
  const lin = (pts, t) => { if (t <= pts[0][0]) return pts[0][1]; for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) { const [a, va] = pts[i - 1], [b, vb] = pts[i]; return va + (vb - va) * (t - a) / (b - a); } return pts[pts.length - 1][1]; };
  // trappenhuis: per verdieping 4 punten (overloop A, halverwege trap 1, overloop B, halverwege trap 2), oogpunt 1,6 m
  const stairs = (t0, t1) => { const K = [], n = 5 * 4, dt = (t1 - t0) / n;
    for (let f = 0; f < 5; f++) { const y = -3 * f + 1.6;
      K.push([t0 + (f * 4) * dt, [-1.6, y, 3.1], [-3.2, y - 1.2, 5.2], 72, 0],          // kijkt naar het rode cijfer op de muur
             [t0 + (f * 4 + 1) * dt, [-2.5, y - .75, 4.8], [-2.5, y - 2, 7], 72, 3],
             [t0 + (f * 4 + 2) * dt, [-1.8, y - 1.5, 6.2], [-1.1, y - 2.5, 3.5], 72, 0],
             [t0 + (f * 4 + 3) * dt, [-1.1, y - 2.25, 4.8], [-1.1, y - 3.5, 2.5], 72, -3]); }
    return K; };
  const SEEN = S('street') + .4;                                    // het moment dat jij ze ziet
  // meters tussen jou en de dichtstbijzijnde zombie: straat beneden (± 15 m hoog, 25 m verderop) -> voordeur -> trappenhuis -> jouw deur; daarna vlucht je
  const dist = [[SEEN, 32], [S('door'), 22], [Ee('door'), 17], [S('inside'), 16], [S('floors'), 12], [S('bang'), 1], [Ee('bang'), 1], [S('stairs'), 4], [Ee('stairs'), 9], [Ee('outside'), 25], [T_END, 45]];
  return {
    T_END, brand: false, post: { bloom: .8, ao: 1 },               // nacht: gloed op de ledstrips, de tv en de lantaarns
    hands: [[0, S('balcony') + .4]],
    escape: { bang: [S('bang'), Ee('bang') + 3.2], push: S('outside') + .3, dropController: S('balcony') + .4 },                               // handen met controller, tot je hem neerlegt
    tv: { channel: 'GAME', feed: [[0, 'game', { text: 'ROUND 12', sub: 'POINTS 21,300', hp: 'HP: 100', ammo: 'AMMO 24/30' }],
                                  [S('game'), 'game', { text: 'ROUND 12', sub: 'POINTS 24,850', hp: 'HP: 100', ammo: 'AMMO 12/30' }],
                                  [S('behind'), 'game', { text: 'ROUND 13', sub: 'POINTS 24,850', hp: 'HP: 100', ammo: 'AMMO 12/30' }]] },

    showTitle: true, titleIn: .3, titleOut: Ee('intro') - .2, hudIn: Ee('intro') - .6,   // titel bij de start; dan de timer
    // HUD: eerst een TIMER die aftelt tot jij ze ziet (regel 'street'), daarna DISTANCE: hoe ver ze van je af zijn
    hud: { label: 'TIMER', labelAt: [[SEEN, 'DISTANCE']],
           fmt: (v, t) => { if (t >= SEEN) return `${Math.round(lin(dist, t))} m`; const r = Math.ceil(SEEN - t); return `${String(Math.floor(r / 60)).padStart(2, '0')}:${String(r % 60).padStart(2, '0')}`; } },
    counter: [[0, 0], [T_END, 1]],
    range: [0, 1],

    captions: [],                                                   // eigenaar: geen tekst in beeld (alleen de stem)

    // camera: [t, positie, kijkt naar, fov, kanteling°]
    camPath: [
      [0, [.4, 1.05, 1.5], [1.4, 1.0, -2.2], 55],                          // POV: game op tv, handen met controller
      [Ee('game'), [.35, 1.05, 1.2], [1.4, 1.0, -2.2], 50],
      [Ee('sound'), [.3, 1.1, 1.2], [-1.4, 1.2, -4], 56],                  // hoofd naar de balkondeur
      [BAL + 1.2, [-1.0, 1.65, -1.6], [-1.4, 1.2, -7], 62],                // naar buiten
      [Ee('balcony'), [-1.4, 1.75, -3.95], [-14, OUT, -13.5], 62],         // over het hek naar beneden: de straat
      [Ee('speed'), [-1.4, 1.75, -3.98], [-8, OUT, -11], 60],
      [DOOR + 1, [-1.4, 1.75, -4.0], [-5, OUT, -8], 56],                   // de horde bij de voordeur
      [Ee('inside'), [-1.4, 1.75, -4.0], [-2.6, OUT, -6.2], 48, 3],
      [S('floors') + .8, [-.4, 1.6, -1.4], [2.6, 1.4, .7], 62, -4],          // terug de kamer in, naar de gang
      [S('bang') - .3, [1.9, 1.6, .65], [6.4, 1.1, .65], 58, 0],            // de gang in: je voordeur
      [Ee('bang') + 1.2, [2.3, 1.6, .65], [6.4, 1.1, .65], 50, 2],          // de deur schokt bij elke klap
      [S('keys') + 1.0, [.2, 1.6, 1.6], [-1.8, 1.4, 4], 64, -5],            // omdraaien: de achterdeur
      [S('keys') + 2.4, [-1.8, 1.6, 2.6], [-2.5, .4, 6], 68, 0],            // door de achterdeur, het trappenhuis in
      ...stairs(S('keys') + 2.9, S('outside') - .4),                       // vijf verdiepingen naar beneden
      [S('outside') + .2, [-1.9, OUT + 1.6, 3.1], [-3.4, OUT + 1.3, 3.1], 64, 0],   // de groene nooduitgang
      [S('outside') + 1.2, [-3.6, OUT + 1.6, 3.4], [-30, OUT + 1.4, 3.8], 66, 0],   // erdoor, het steegje in
      [Ee('outside') + .6, [-12, OUT + 1.65, 3.8], [-40, OUT + 1.4, 3.8], 70, 0],    // rennen
      [S('behind') - .1, [-13, OUT + 1.65, 3.8], [-40, OUT + 1.4, 3.8], 70, 0],
      [S('behind') - .05, [-13, OUT + 1.65, 3.8], [-40, OUT + 1.4, 3.8], 70, 0],
      [S('behind'), [1.2, 1.5, 2.1], [1.2, .7, -2.2], 62, 0],               // knip: de lege kamer, controller op het kleed
      [S('behind') + .05, [1.2, 1.5, 2.1], [1.2, .7, -2.2], 62, 0],
      [T_END, [1.0, 1.45, 1.9], [1.3, .85, -2.2], 56, 0],
    ],
    fov: 60,

    zombies: [
      { n: 16, y: OUT + .4, lag: .7, spread: 2.0, gather: true, path: [[0, -36, -8.5], [DOOR - 2, -6, -6.5], [DOOR + 2, -1.6, -4.4]] },
      { n: 12, y: OUT + .4, lag: .8, spread: 1.8, gather: true, path: [[1, 32, -9.5], [DOOR - 1, 3, -6.8], [DOOR + 3, -1.2, -4.6]] },
      { n: 8, y: OUT + .4, lag: 1.2, spread: 2.5, gather: true, path: [[3, -14, -13.5], [DOOR, -4, -9], [DOOR + 4, -2.2, -5.4]] },
    ],

    beats: { stop: T_END, climax: S('bang'), lookUp: 1e9, shelter: 1e9, carsStop: 1e9 },
  };
}

export const upload = {
  title: 'What if your zombie game became real?',
  description: 'You are playing a video game late at night. Then you hear noise outside… and the zombies are real. 🧟\n\nWould you have found a way out? 👇\n\n#whatif #zombie #pov #shorts #gaming',
  tags: ['what if', 'zombie', 'pov', 'escape', 'flat', 'gaming', '3d animation', 'IfScape3D'],
  tiktok: 'POV: your zombie game becomes real 🧟 Would you have found a way out? #whatif #zombie #pov #fyp',
  sources: [
    'Average human walking speed ≈ 5 km/h; a slow shuffle ≈ 3 km/h (fiction: zombies) – e.g. Bohannon (1997), Age and Ageing 26(1)',
    'Most adults can sprint at 20–25 km/h for a short distance',
    'One storey of an apartment building ≈ 3 m, so five floors ≈ 15 m',
  ],
};
