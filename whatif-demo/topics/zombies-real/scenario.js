// What if there was a zombie apocalypse?  (onderwerpen.md #48; verhaal van de eigenaar, okt 2026)
// Plek 'gameroom' (gamekamer 5e verdieping, nacht) + kracht 'calm'. De stem vertelt NIET wat je ziet:
// rustige nacht, gamen -> een geluid, luisteren -> balkon: "Who are all these people?" (langzame mensen, armen langs het lijf)
// -> gekrab aan je deur -> door het kijkgaatje: zombies -> via het zijraam de buitenbrandtrap af -> het steegje in, rennen.
// Cartoon-zombies (engine/zombies.js): geen bloed, niemand wordt aangeraakt.
export const topic = {
  number: 48, slug: 'zombies-real', place: 'gameroom', force: 'calm',
  question: 'What if there was a zombie apocalypse?',
  title: 'Imagine a zombie<br>apocalypse…',
  voOffset: 1.0,
};

// [id, tekst, pauze erna]; getallen = seconden stilte (daar vertellen beeld en geluid het verhaal)
export const lines = [
  ['imagine', 'Imagine a zombie apocalypse…', 'pause'],
  ['quiet', 'on a quiet night.', 'long'],
  ['play', 'You are playing a video game.', 3.0],          // gamegeluiden, dan een klap buiten
  ['hear', 'Did you hear that?', 6.5],                    // pauzeren, luisteren, nog een geluid, naar het balkon
  ['people', 'Who are all these people?', 14.5],          // naar beneden kijken; terug naar binnen; gekrab; het kijkgaatje
  ['out', 'You have to get out.', 10.5],                  // zijraam, de brandtrap af
  ['q', 'Would you make it out?', 'none'],                // het steegje in, rennen
];

export default function (at) {
  const OUT = -15, S = id => at(id).s, Ee = id => at(id).e;
  const H = S('hear'), PE = S('people'), O = S('out'), Q = S('q'), T_END = at('q').e + 2.6;
  const R = PE + 10.6;                                                     // reveal: zombies door het kijkgaatje
  const lin = (pts, t) => { if (t <= pts[0][0]) return pts[0][1]; for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) { const [a, va] = pts[i - 1], [b, vb] = pts[i]; return va + (vb - va) * (t - a) / (b - a); } return pts[pts.length - 1][1]; };
  const dist = [[R, 1], [O, 1], [O + 3, 4], [Q - 1, 14], [T_END, 26]];
  // de brandtrap af: per verdieping van platform naar platform (trap wisselt van richting)
  const fire = (t0, t1) => { const K = [], n = 4, dt = (t1 - t0) / n;
    for (let f = 0; f < n; f++) { const y = -3 * f + 1.6, a = f % 2 ? 1.3 : 3.3, b = f % 2 ? 3.3 : 1.3;
      K.push([t0 + f * dt, [-3.55, y, a], [-3.55, y - 3.4, b + (b - a) * .3], 74, 0],
             [t0 + (f + .55) * dt, [-3.55, y - 1.65, (a + b) / 2], [-3.55, y - 3.6, b + (b - a) * .6], 74, f % 2 ? 4 : -4]); }
    return K; };
  return {
    T_END, brand: false, post: { bloom: .8, ao: 1 },
    hands: [[0, H + 2.6]],
    escape: { route: 'fire', scratch: [PE + 6, O], peephole: [PE + 10.2, PE + 14.3], dropController: H + 2.6 },
    tv: { channel: 'GAME', feed: [[0, 'game', { text: 'ROUND 12', sub: 'POINTS 21,300', hp: 'HP: 100', ammo: 'AMMO 24/30' }],
                                  [H + 2.2, 'game', { text: 'ROUND 12', sub: 'POINTS 22,150', hp: 'HP: 100', ammo: 'AMMO 19/30', paused: true }]] },

    showTitle: true, titleIn: .3, titleOut: Ee('quiet') + .3, hudIn: Ee('quiet') + .5,
    // HUD: TIMER tot je ze door het kijkgaatje ziet, daarna DISTANCE
    hud: { label: 'TIMER', labelAt: [[R, 'DISTANCE']],
           fmt: (v, t) => { if (t >= R) return `${Math.round(lin(dist, t))} m`; const r = Math.ceil(R - t); return `${String(Math.floor(r / 60)).padStart(2, '0')}:${String(r % 60).padStart(2, '0')}`; } },
    counter: [[0, 0], [T_END, 1]], range: [0, 1],
    captions: [],

    // camera: [t, positie, kijkt naar, fov, kanteling°]
    camPath: [
      [0, [.4, 1.05, 1.5], [1.4, 1.0, -2.2], 55],                            // POV: gamen
      [H - .2, [.38, 1.05, 1.35], [1.4, 1.0, -2.2], 52],
      [H + 1.4, [.35, 1.1, 1.3], [-1.6, 1.3, -4], 58, -3],                    // "Did you hear that?" – hoofd naar de balkondeur
      [H + 2.6, [.35, 1.12, 1.3], [1.4, 1.0, -2.2], 56],                      // even terug: pauze
      [H + 4.2, [.3, 1.15, 1.2], [-1.6, 1.4, -4], 58],                        // nog een geluid: opstaan
      [PE - 1.2, [-1.0, 1.65, -1.7], [-1.4, 1.2, -7], 62],                    // naar het balkon
      [PE + .2, [-1.4, 1.75, -3.95], [-14, OUT, -13.5], 62],                  // naar beneden: "Who are all these people?"
      [PE + 4.0, [-1.4, 1.75, -3.98], [-5, OUT, -8], 58],                     // ze lopen allemaal naar jouw voordeur
      [PE + 5.6, [-.3, 1.6, -1.2], [3, 1.4, .7], 62],                         // terug naar binnen, naar de gang
      [PE + 8.6, [5.3, 1.6, .65], [6.4, 1.5, .65], 56],                       // langzaam naar je voordeur (gekrab)
      [PE + 10.0, [6.1, 1.62, .65], [6.4, 1.62, .65], 50],                    // oog bij het kijkgaatje
      [PE + 10.2, [6.62, 1.62, .65], [12, 1.4, .65], 118],                    // DOOR HET KIJKGAATJE: de gang vol zombies
      [PE + 14.3, [6.62, 1.62, .65], [10, 1.5, .65], 118],
      [PE + 14.4, [5.6, 1.6, .65], [-3, 1.6, .65], 64],                       // achteruit, omdraaien
      [O + 1.6, [-2.3, 1.55, 1.8], [-5, .6, 1.8], 66],                        // naar het zijraam
      [O + 2.6, [-3.4, 1.6, 2.6], [-3.55, -1.8, 1.0], 72],                    // naar buiten, op de brandtrap
      ...fire(O + 3.0, Q - 1.2),                                              // vier trappen naar beneden
      [Q - .6, [-3.55, -12 + 1.6, 1.4], [-3.6, OUT, 2.5], 72],                // de laatste ladder
      [Q + .3, [-4.6, OUT + 1.6, 2.4], [-30, OUT + 1.4, 3.8], 70],            // het steegje in
      [T_END, [-13, OUT + 1.65, 3.8], [-40, OUT + 1.4, 3.8], 72],             // rennen
    ],
    fov: 60,
    walkBob: [[PE - 2, PE + .2, .03], [PE + 5.6, PE + 9.6, .025], [Q + .3, T_END, .05]],

    zombies: [
      // in de straat: langzame "mensen" (armen langs het lijf), allemaal naar jouw voordeur, dan naar binnen
      { n: 16, y: OUT + .4, lag: .7, spread: 2.0, pose: 'shamble', speed: .5, path: [[0, -34, -8.5], [PE + 4, -5, -6.5], [PE + 7, -1.5, -3.6]] },
      { n: 14, y: OUT + .4, lag: .8, spread: 1.8, pose: 'shamble', speed: .5, path: [[0, 30, -9.5], [PE + 5, 3, -6.8], [PE + 8, -1.3, -3.6]] },
      { n: 10, y: OUT + .4, lag: 1.1, spread: 2.5, pose: 'shamble', speed: .5, path: [[0, -12, -13.5], [PE + 5, -4, -9], [PE + 9, -1.6, -3.6]] },
      // de gang voor je deur: armen omhoog, vlak voor het kijkgaatje
      { n: 9, y: .2, lag: .3, spread: 1.1, gather: true, path: [[0, 12, .65], [3, 7.3, .65]] },
    ],

    beats: { stop: T_END, climax: R, lookUp: 1e9, shelter: 1e9, carsStop: 1e9 },
  };
}

export const upload = {
  title: 'What if there was a zombie apocalypse?',
  description: 'A quiet night. You are playing a video game. Then you hear something outside… 🧟\n\nWould you make it out? 👇\n\n#whatif #zombie #pov #shorts #gaming',
  tags: ['what if', 'zombie', 'zombie apocalypse', 'pov', 'escape', 'gaming', '3d animation', 'IfScape3D'],
  tiktok: 'POV: a quiet night… until you look through the peephole 🧟 Would you make it out? #whatif #zombie #pov #fyp',
  sources: [],
};
