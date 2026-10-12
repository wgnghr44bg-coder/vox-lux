// What if you were playing zombies and they became real?  (onderwerpen.md #48; idee van de eigenaar, okt 2026)
// Plek 'gameroom' (gamekamer 5e verdieping, nacht, ledstrips, balkon, smalle straat; voorbeeldbeelden eigenaar) + kracht 'calm'.
// Cartoon-zombies (engine/zombies.js): geen bloed, niemand wordt aangeraakt, alleen vluchten (regels: geen geweld).
// STAP 1 (deze versie): tv-game -> balkon -> de horde dringt het gebouw binnen (t/m regel inside).
// STAP 2 (later): bonken op je deur, gang, brandtrap (5 verdiepingen), naar buiten (regels floors-q).
export const topic = {
  number: 48, slug: 'zombies-real', place: 'gameroom', force: 'calm',
  question: 'What if you were playing zombies and they became real?',
  title: 'What if you were<br>playing zombies and<br>they became real?',   // eerste zin: Imagine… (regels/standaard-video.md)
  voOffset: 1.0,
};

export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'one night, the zombies in your game become real.', 'pause'],
  ['mean', 'Not on the screen. Outside, in your street.', 'long'],
  ['place', 'You are sitting in your room on the fifth floor, controller in your hands.', 'pause'],
  ['game', 'Round twelve. Sixty zombies, and you have not been hit once.', 'long'],
  ['sound', 'Then you hear something outside. Not from the speakers.', 'long'],
  ['balcony', 'You step out onto the balcony and look down.', 'pause'],
  ['street', 'The street is full of them, shuffling slowly between the parked cars.', 'long'],
  ['speed', 'They walk at about three kilometres an hour. You can sprint at more than twenty.', 'long'],
  ['door', 'But they are not walking past. They are crowding around your front door.', 'pause'],
  ['inside', 'The lock gives way. They are inside the building.', 'long'],
  ['floors', 'Five floors. About fifteen metres of stairs between you and them.', 'long'],
  ['bang', 'Then it starts. Banging, on your own door.', 3.5],
  ['keys', 'You grab your keys. The fire stairs are at the end of the hallway.', 'pause'],
  ['stairs', 'Down, two steps at a time. Third floor. Second. First.', 'long'],
  ['outside', 'You push open the back door into the cold night air.', 'long'],
  ['behind', 'Upstairs, the game is still running. Round thirteen.', 'pause'],
  ['q', 'And this time, nobody is holding the controller.', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 2.4, OUT = -15;
  const S = id => at(id).s, Ee = id => at(id).e, BAL = S('balcony'), DOOR = S('door');
  const lin = (pts, t) => { if (t <= pts[0][0]) return pts[0][1]; for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) { const [a, va] = pts[i - 1], [b, vb] = pts[i]; return va + (vb - va) * (t - a) / (b - a); } return pts[pts.length - 1][1]; };
  const dist = [[0, 15], [S('inside'), 15], [S('bang'), 1], [S('keys'), 1], [S('stairs'), 3], [Ee('outside'), 25], [T_END, 40]];   // metres between you and them
  return {
    T_END, brand: false, post: { bloom: .8, ao: 1 },               // nacht: gloed op de ledstrips, de tv en de lantaarns
    hands: [[0, S('sound') + .6]],                                  // handen met controller in beeld
    tv: { channel: 'GAME', feed: [[0, 'game', { text: 'ROUND 12', sub: 'POINTS 21,300', hp: 'HP: 100', ammo: 'AMMO 24/30' }],
                                  [S('game'), 'game', { text: 'ROUND 12', sub: 'POINTS 24,850', hp: 'HP: 100', ammo: 'AMMO 12/30' }],
                                  [S('behind'), 'game', { text: 'ROUND 13', sub: 'POINTS 24,850', hp: 'HP: 100', ammo: 'AMMO 12/30' }]] },

    showTitle: false, hudIn: 1e9,                                   // eigenaar: geen titel en geen teller in beeld, alleen de handen met controller
    hud: { label: 'ZOMBIES', unit: '', decimals: 0,
           second: { label: 'DISTANCE', fn: (v, t) => lin(dist, t), unit: ' m', decimals: 0, showAt: S('inside') } },
    counter: [[0, 0], [S('street'), 0], [Ee('speed'), 60], [S('inside'), 60], [T_END, 60]],
    range: [0, 60],

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
      [S('floors') + 1.2, [-.6, 1.6, -1.6], [1.5, 1.4, 2.4], 64, -6],      // (stap 2) terug de kamer in, naar je voordeur
      [T_END, [-.6, 1.6, -1.6], [1.5, 1.4, 2.4], 64, 0],
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
  title: 'What if you were playing zombies and they became real?',
  description: 'You are alone in your flat playing a zombie game. Then you look down from your window… and they are real. 🧟\n\nWould you make it out? 👇\n\n#whatif #zombie #pov #shorts #gaming',
  tags: ['what if', 'zombie', 'pov', 'escape', 'flat', 'gaming', '3d animation', 'IfScape3D'],
  tiktok: 'POV: you are playing zombies and they become real outside your window 🧟 Would you make it out? #whatif #zombie #pov #fyp',
  sources: [
    'Average human walking speed ≈ 5 km/h; a slow shuffle ≈ 3 km/h (fiction: zombies) – e.g. Bohannon (1997), Age and Ageing 26(1)',
    'Most adults can sprint at 20–25 km/h for a short distance',
    'One storey of an apartment building ≈ 3 m, so five floors ≈ 15 m',
  ],
};
