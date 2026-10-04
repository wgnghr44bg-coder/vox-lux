// What if the Sun came closer to Earth?  (onderwerpen.md #31)
// POV on a summer beach, told in order from the start (no flash-forward). People get up,
// some run, some stare; you run too; towels, parasols and palms catch fire (dry cloth and leaves
// ignite at roughly 10-16x today's sunlight). No end card: the picture burns out to white.
export const topic = {
  number: 31, slug: 'sun-closer', place: 'boulevard', force: 'heat',
  question: 'What if the Sun came closer to Earth?',
  title: 'What if<br>the Sun came closer<br>to Earth?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['intro', "Imagine you're lying on a beach. The sun feels perfect.", 'pause'],
  ['dist', "It's ninety-three million miles away.", 'long'],
  ['now', 'Now Earth starts falling toward it.', 'long'],
  ['square', 'Ten percent closer, and the sunlight is already a quarter stronger.', 'pause'],
  ['sand', 'The sand burns under your feet.', 'pause'],
  ['people', 'People grab their things. Some run. Some just stare.', 'long'],
  ['half', 'At half the distance, the Sun looks twice as wide. Four times the sunlight.', 'pause'],
  ['skin', 'Your skin would burn in minutes.', 'pause'],
  ['run', 'You run.', 'long'],
  ['quarter', 'At a quarter of the distance, sixteen times the sunlight.', 'pause'],
  ['fire', 'Towels, parasols, dry palm leaves. They start to smoke, then catch fire.', 5],
  ['works', 'Earth only works because of exactly where it is.', 'pause'],
  ['final', 'Not too hot. Not too cold.', 'none'],
];

export default function (at) {
  const climax = at('fire').e + .3, stop = at('works').s - .2;
  const runA = at('run').s - .3, runB = at('fire').s, steps = [];
  for (let t = runA; t < climax + 2.5; t += 1 / 2.8) steps.push({ t, kind: 'step', e: .5 });
  return {
    T_END: at('final').e + 2.2,
    titleOut: at('dist').e + .2,
    endStyle: 'white',
    forceParams: { sunGrow: 1.3, wash: .15, haze: .35 }, steam: .12,
    clear: [[12, 27], [2, 4], [-30, 18], [3, 26], [2, 18], [2, 30]],
    sunOffset: [-15, 42, -200],
    hud: { label: 'DISTANCE TO THE SUN', unit: ' million mi', decimals: 1,
           second: { label: 'SUNLIGHT', prefix: '×', fn: d => (93 / d) ** 2, decimals: 1, unit: '', showAt: at('square').s } },
    counter: [[0, 93], [at('now').e, 93], [at('square').e, 84], [at('sand').e, 75], [at('people').e, 62],
              [at('half').s + 1, 46.5], [at('skin').e, 41], [at('run').e, 34], [at('quarter').s + 1.5, 23.3], [climax, 23], [stop, 23]],
    captions: [[at('square').s + 1, at('square').e + .4, '10% closer = 23% more sunlight.'],
               [at('half').s, at('half').e + .3, 'Half the distance, 4× the light.'],
               [at('quarter').s, at('quarter').e + .4, '16× the sunlight.'],
              ],
    shots: [[0, 'pov-lie'], [at('now').s, 'pov-beach'], [at('sand').s, 'pov-back'], [at('half').s, 'pov-sea'],
            [runA, 'pov-run'], [at('quarter').s, 'pov-glance'], [at('fire').s + 1.6, 'pov-prom'],
            [climax - 1.2, 'pov-sky']],
    looks: [[at('dist').s + .2, [-150, 420, -2000], 2.5, 8],
            [at('people').s + 1.5, [0, 1.5, 34], 2.5, 6],
            [at('half').s + .3, [-150, 420, -2000], 2.5, 8]],
    events: steps,
    audio: { heartbeat: [at('people').s, stop], riser: [at('half').s, climax + 1], breath: [runA, climax + 1.5] },
    beats: { shelter: at('people').s, climax, stop, dark: 1e9, end: 1e9, fade: at('works').s - .5 },     // the Sun burns the picture to white
    sunbathers: 22, wake: [.033, .085],
    end: { title: '', lines: '' },
  };
}

export const upload = {
  title: 'What if the Sun came closer to Earth?',
  description: "POV: you're lying on a summer beach when Earth starts falling toward the Sun. ☀️🔥\n\n" +
    'At half the distance the Sun looks twice as wide. At a quarter, sunlight is 16 times stronger and towels, parasols and palm trees catch fire.\n\n' +
    'Would you run or stay? 👇\n\n' +
    'Animated with code, AI voice.\n\n#whatif #sun #space #shorts',
  tags: ['what if', 'what if the sun came closer', 'sun', 'space', 'science', 'physics', 'beach', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'POV: Earth starts falling toward the Sun ☀️🔥 At a quarter of the distance, sunlight is 16× stronger. Would you run or stay? #whatif #space #science #fyp',
};
