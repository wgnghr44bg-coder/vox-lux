// What if the Sun came closer to Earth?  (onderwerpen.md #31)
// POV on a summer beach: people sunbathing, the Sun grows bigger and brighter, some run for the
// boulevard, others stand and stare. No end card: the picture burns out to white.
export const topic = {
  number: 31, slug: 'sun-closer', place: 'boulevard', force: 'heat',
  question: 'What if the Sun came closer to Earth?',
  title: 'What if<br>the Sun came closer<br>to Earth?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['intro', 'Imagine you are lying on a warm beach, on a perfect summer day.', 'pause'],
  ['calm', 'The sea is calm. The sky is blue.', 'pause'],
  ['dist', 'The Sun is ninety-three million miles away.', 'pause'],
  ['right', 'Just far enough.', 'long'],
  ['now', 'Now imagine that Earth slowly begins to drift toward it.', 'long'],
  ['square', 'Sunlight grows with the square of the distance. Only ten percent closer, and you get almost a quarter more sunlight.', 'long'],
  ['bigger', 'The Sun looks bigger. Whiter. The sand gets too hot to stand on.', 'long'],
  ['air', 'Above the sand, the hot air starts to shimmer.', 'pause'],
  ['people', 'People sit up. Some grab their things and run. Others just stand there, staring at the sky.', 'long'],
  ['half', 'At half the distance, the Sun would look twice as wide, and give four times the sunlight.', 'pause'],
  ['burn', 'Skin that burns in fifteen minutes today would burn in four.', 'pause'],
  ['sea', 'Out on the water, the sea begins to steam.', 6],
  ['mercury', "At Mercury's distance, sunlight is almost seven times stronger, and the ground reaches eight hundred degrees.", 'long'],
  ['band', 'Our planet lives in a narrow band around its star.', 'pause'],
  ['final', 'Not too hot. Not too cold.', 'none'],
];

export default function (at) {
  const climax = at('sea').e + .3, stop = at('mercury').s - .2;
  return {
    T_END: at('final').e + 2.2,
    titleOut: at('calm').e + .2,
    endStyle: 'white',
    forceParams: { sunGrow: 1.3, wash: .15, haze: .35 }, steam: .12,
    clear: [[3, 33], [2, 4], [-30, 18]],      // keep parasols away from the POV spots                       // no end card: burn out to white
    sunOffset: [-15, 42, -200],              // the Sun over the sea, in front of you
    hud: { label: 'DISTANCE TO THE SUN', unit: ' million mi', decimals: 1,
           second: { label: 'SUNLIGHT', prefix: '×', fn: d => (93 / d) ** 2, decimals: 1, unit: '', showAt: at('square').s } },
    counter: [[0, 93], [at('now').e, 93], [at('square').e, 84], [at('bigger').e, 72], [at('people').e, 58],
              [at('half').s + 1.5, 46.5], [at('burn').e, 42], [climax, 33], [stop, 26]],
    captions: [[at('right').s - .2, at('right').e + .8, 'Just far enough.'],
               [at('square').s + 3, at('square').e + .6, '10% closer = 23% more sunlight.'],
               [at('half').s, at('half').e + .3, 'Half the distance, 4× the light.'],
               [at('mercury').s, at('mercury').e + .4, 'Mercury: almost 7× the sunlight.'],
               [at('band').s, at('final').e + .6, 'Not too hot. Not too cold.']],
    shots: [[0, 'pov-sea'], [at('now').s, 'pov-beach'], [at('bigger').s, 'pov-sea'], [at('people').s, 'pov-back'],
            [at('half').s, 'pov-sea'], [at('burn').s, 'pov-beach'], [at('sea').s, 'pov-sea'], [climax + 3, 'pov-sky']],
    looks: [[at('dist').s + .2, [-150, 420, -2000], 2.8, 8],          // look up at the Sun
            [at('bigger').s + .2, [-150, 420, -2000], 2.5, 8],
            [at('people').s + 2.5, [0, 1.5, 34], 3, 6],                  // watch people run for the boulevard
            [climax + .5, [-150, 420, -2000], 6, 9]],
    beats: { shelter: at('people').s, climax, stop, dark: 1e9, end: 1e9, fade: at('final').s - .3 },
    sunbathers: 22, wake: [.04, .11],      // they get up between 1.5× and 2.3× today's sunlight
    end: { title: '', lines: '' },
  };
}

export const upload = {
  title: 'What if the Sun came closer to Earth?',
  description: "POV: you're lying on a summer beach when Earth starts drifting toward the Sun. ☀️\n\n" +
    'Just 10% closer means almost a quarter more sunlight. At half the distance the Sun looks twice as wide, and some people run while others just stare.\n\n' +
    'Would you run or stay? 👇\n\n' +
    'New what-ifs every week on IfScape3D.\nAnimated with code, AI voice.\n\n#whatif #sun #space #shorts',
  tags: ['what if', 'what if the sun came closer', 'sun', 'space', 'science', 'physics', 'beach', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'What if the Sun came closer to Earth? ☀️ Just 10% closer = 23% more sunlight. Would you run or stay? #whatif #space #science #fyp',
};
