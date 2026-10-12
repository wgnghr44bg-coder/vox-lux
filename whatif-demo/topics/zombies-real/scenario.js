// What if you were playing zombies and they became real?  (onderwerpen.md #48; idee van de eigenaar, okt 2026)
// Plek 'indoors' (flat op de 5e verdieping, room.building: eigen gevel + voordeur beneden) + kracht 'day' (avond).
// Cartoon-zombies (engine/zombies.js): geen bloed, niemand wordt aangeraakt, alleen vluchten (regels: geen geweld).
// STAP 1 (deze versie): tv-game -> raam -> de horde gaat het gebouw binnen (± 0-22 s).
// STAP 2 (later): gang + bonken op je deur, trappenhuis (3 verdiepingen), naar buiten rennen.
export const topic = {
  number: 48, slug: 'zombies-real', place: 'indoors', force: 'day',
  question: 'What if you were playing zombies and they became real?',
  title: 'What if you were<br>playing zombies and<br>they became real?',
  voOffset: 1.0,
};

export const lines = [
  ['imagine', 'Imagine you are alone in your flat, playing a zombie game late at night.', 'pause'],
  ['intro', 'What if the zombies you see on your screen became real outside?', 'pause'],
  ['normal', 'Normally it is just a game, with points and rounds.', 'pause'],
  ['look', 'Then you look down from your window and see them for real, shambling into your building.', 'long'],
  ['enter', 'They push through the front door downstairs, dozens of them.', 'pause'],
  ['panic', 'You hear screaming in the hallway and banging on your own door.', 'long'],
  ['escape', 'You have to run now, grabbing nothing but your keys.', 'pause'],
  ['stairs', 'Down the dark stairwell, three floors, with them right behind you.', 'long'],
  ['outside', 'You burst outside onto the street and keep running, not looking back.', 'pause'],
  ['q', 'Would you make it out?', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 3.0, L = at('look').s, EN = at('enter').s, OUT = -15;
  return {
    T_END, look: 'blender', brand: false,
    forceParams: { hours: [[0, 19.3], [T_END, 19.7]] },          // schemer: lampen gaan aan, de straat is nog te zien
    room: { people: 0, lamp: true, building: true },
    tv: { channel: 'GAME', feed: [[0, 'game', { text: 'ROUND 1', sub: 'POINTS 1,250' }], [at('normal').s, 'game', { text: 'ROUND 5', sub: 'POINTS 8,940' }],
                                  [L, 'game', { text: 'ROUND 12', sub: 'POINTS 21,300' }]] },

    titleOut: at('intro').e + .4, hudIn: at('normal').s,
    hud: { label: 'ROUND', unit: '', decimals: 0, second: { label: 'ZOMBIES', fn: v => v * 8, unit: '', decimals: 0, showAt: at('normal').s } },
    counter: [[0, 1], [at('normal').s, 5], [L, 12], [EN, 15], [at('panic').s, 18], [at('escape').s, 22], [at('stairs').s, 26], [at('outside').s, 28], [T_END, 30]],
    range: [1, 30],

    captions: [
      [L, at('look').e + .8, 'You look down and see them for real.'],
      [EN, at('enter').e + .8, 'They push through the front door.'],
      [at('panic').s, at('panic').e + .8, 'Banging on your door.'],
      [at('escape').s, at('escape').e + .8, 'You have to run now.'],
      [at('stairs').s, at('stairs').e + .8, 'Down three floors.'],
      [at('outside').s, at('outside').e + .8, 'Burst outside and keep running.'],
    ],

    // camera: [t, positie, kijkt naar, fov, kanteling°]
    camPath: [
      [0, [.1, 1.2, 1.1], [1.55, 1.0, -2.15], 50],                        // POV vanaf de bank: de game op tv
      [at('normal').e, [.3, 1.18, .5], [1.55, 1.0, -2.15], 42],
      [L - .6, [-.4, 1.6, -.6], [-1.6, 1.2, -8], 60],                      // opstaan, naar het raam
      [L + 1.4, [-1.4, 1.5, -3.2], [-7, OUT, -13], 66],              // leunt uit het raam: de straat en de voordeur                  // naar beneden kijken: straat en voordeur
      [EN, [-1.4, 1.5, -3.25], [-3, OUT, -8], 52],                    // inzoomen op de voordeur
      [at('enter').e, [-1.4, 1.5, -3.25], [-1.4, OUT, -4.6], 36, 3],
      [at('panic').s + .8, [.6, 1.6, .2], [2.6, 1.5, 2.4], 64, -6],        // (stap 2) whip-pan terug de kamer in
      [T_END, [.6, 1.6, .2], [2.6, 1.5, 2.4], 64, 0],
    ],
    fov: 60,

    zombies: [
      { n: 12, y: OUT + .4, lag: .9, spread: 1.6, path: [[0, -26, -9.5], [EN + 1.5, -4, -9], [EN + 3, -1.4, -6], [EN + 4.5, -1.4, -3.4]] },
      { n: 8, y: OUT + .4, lag: 1.1, spread: 1.4, path: [[2, 22, -10], [EN + 2.5, 2, -9], [EN + 4, -1.2, -6], [EN + 5.5, -1.4, -3.4]] },
    ],

    beats: { stop: T_END, climax: at('stairs').s, lookUp: 1e9, shelter: 1e9, carsStop: 1e9 },
  };
}

export const upload = {
  title: 'What if you were playing zombies and they became real?',
  description: 'You are alone in your flat playing a zombie game. Then you look down from your window… and they are real. 🧟\n\nWould you make it out? 👇\n\n#whatif #zombie #pov #shorts #gaming',
  tags: ['what if', 'zombie', 'pov', 'escape', 'flat', 'gaming', '3d animation', 'IfScape3D'],
  tiktok: 'POV: you are playing zombies and they become real outside your window 🧟 Would you make it out? #whatif #zombie #pov #fyp',
  sources: [],
};
