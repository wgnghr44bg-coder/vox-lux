// SJABLOON standaard-video (eigenaar, 11 okt 2026; regels/standaard-video.md) – de sinkhole-video, nu op de engine:
// plek 'street' + kracht 'sinkhole'. Voor een nieuw onderwerp: kopieer deze map, pas topic, lines, counter/hud,
// camPath en beats aan. camPath maakt er vanzelf de standaard van (titel aan, geen logo, geen fade, één camerabeweging).
export const topic = {
  number: 46, slug: 'standaard-sinkhole', place: 'street', force: 'sinkhole',
  question: 'What if a giant sinkhole appeared downtown?',
  title: 'What if a giant<br>sinkhole appeared<br>downtown?',
  voOffset: 1.0,
};

// [id, text, pause after]: 'pause' (0,5 s), 'long' (1 s) or seconds of silence (the climax).
// Opbouw van de gravity-video (regels/standaard-video.md), aangepast aan het onderwerp. Geen [pause] binnen een regel: splits de regel.
export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'in a single minute, the street beneath a busy city drops away.', 'pause'],
  ['mean', 'A hole, ninety meters deep, opens right in the middle of downtown.', 'long'],
  ['calm', 'You are standing at a busy crossing.', 'pause'],
  ['pipe', 'Under the asphalt, a leaking pipe has been washing the soil away for years.', 'long'],
  ['left', 'Now, there is almost nothing left to hold the road up.', 'long'],
  ['dip', 'The road sinks a few centimeters.', 'pause'],
  ['cracks', 'Cracks race toward the curb.', 'long'],
  ['police', 'People stop. The police clear the crossing, and everyone steps back.', 'long'],
  ['lean', 'Traffic lights lean. Lampposts tilt toward the middle of the road.', 'long'],
  ['drop', 'Then, the crossing gives way.', 3.5],
  ['size', 'Twenty meters wide.', 'pause'],
  ['deep', 'Ninety meters deep.', 'long'],
  ['guat', 'In 2010, a hole roughly this size opened in the middle of Guatemala City.', 'pause'],
  ['grow', 'And some keep growing.', 'pause'],
  ['florida', 'In Florida, in 1981, one reached about one hundred meters across.', 'long'],
  ['settle', 'Slowly, the dust drifts away.', 'pause'],
  ['still', 'The city is still there, around a hole that was not there this morning.', 'long'],
  ['q', 'And somewhere under another street, the water is still running.', 'none'],
];

export default function (at) {
  const drop = at('drop').e + .35, grow = at('grow').s + .3, T_END = at('q').e + 2.2;
  const radius = [[0, 0], [drop, 0], [drop + .6, 4.5], [drop + 2.3, 10], [grow - .3, 10.4], [grow + 1.2, 17], [grow + 2.4, 24],
                  [grow + 4.2, 34], [grow + 5.8, 43], [at('florida').e + .8, 50], [T_END, 50.2]];
  const lin = (pts, t) => { if (t <= pts[0][0]) return pts[0][1]; for (let i = 1; i < pts.length; i++) if (t <= pts[i][0]) { const [a, va] = pts[i - 1], [b, vb] = pts[i]; return va + (vb - va) * (t - a) / (b - a); } return pts[pts.length - 1][1]; };
  return {
    T_END, titleOut: at('calm').e + .4, hudIn: at('calm').e + .7,
    hud: { label: 'DEPTH', fmt: v => (v < 1 ? v.toFixed(2) : v < 10 ? v.toFixed(1) : Math.round(v)) + ' m',
           second: { label: 'WIDTH', fn: (v, t) => 2 * lin(radius, t), unit: ' m', showAt: drop } },
    counter: [[0, 0], [at('dip').s + .4, 0], [at('dip').s + 2.2, .05], [at('cracks').e + .5, .12], [drop, .15],
              [drop + .5, 8], [drop + 2.6, 82], [at('deep').e, 90], [T_END, 90]],
    range: [0, 90],
    forceParams: { radius, center: [0, 0] },
    captions: [[at('pipe').s + .3, at('pipe').e + .7, 'A leaking pipe.'],
               [at('size').s, at('deep').e + .7, '20 m wide. 90 m deep.'],
               [at('guat').s + .2, at('guat').e + .5, 'Guatemala City, 2010.'],
               [at('florida').s, at('florida').e + .7, 'Florida, 1981: about 100 m.']],
    // one continuous move: [t, camera position, look at]
    camPath: [
      [0, [0, 4.2, 96], [0, 7, -60]],
      [at('pipe').s + 1.2, [0, 4.2, 80], [0, 2, -20]],
      [at('dip').s + .5, [0, 5, 60], [0, .5, -6]],
      [at('cracks').s + 1.2, [0, 8, 48], [0, 0, -3]],
      [at('lean').s, [1, 13, 50], [0, -1, -4]],
      [drop, [2, 20, 54], [0, -8, -4]],
      [drop + 3, [2, 44, 32], [0, -6, -2]],
      [at('guat').s, [3, 58, 28], [0, -12, -1]],
      [grow, [3, 86, 50], [0, -10, -2]],
      [at('settle').s, [0, 126, 86], [0, -10, -2]],
      [at('q').s, [-6, 154, 104], [0, -10, -2]],
      [T_END, [-9, 162, 110], [0, -10, -2]],
    ],
    flee: [0, 0],
    beats: { pipe: at('pipe').s + 1.2, cracks: at('cracks').s + .2, drop, carsStop: at('dip').s + .5, shelter: at('police').s + 1,
             lookUp: at('dip').s + .8, stop: T_END, climax: drop },
  };
}

export const upload = {
  title: 'What if a giant sinkhole appeared downtown?',
  description: 'Rush hour. A busy crossing. Then the road starts to sink… 🕳️\n\nIt has happened in real cities before. And some sinkholes don\'t stop growing.\n\nWhat do you think is under your street? 👇\n\n#whatif #sinkhole #science #shorts',
  tags: ['what if', 'sinkhole', 'giant sinkhole', 'science', 'geology', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'What if a giant sinkhole appeared downtown? 🕳️ 20 m wide, 90 m deep… and then it keeps growing. What\'s under your street? #whatif #sinkhole #science #fyp',
};
