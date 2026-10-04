// What if the Sun came closer to Earth?  (onderwerpen.md #31)
export const topic = {
  number: 31, slug: 'sun-closer', place: 'mountain-village', force: 'heat',
  question: 'What if the Sun came closer to Earth?',
  title: 'What if<br>the Sun came closer<br>to Earth?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['intro', 'Imagine you are standing in a quiet mountain village, deep in winter snow.', 'pause'],
  ['dist', 'Above you, the Sun is ninety-three million miles away.', 'pause'],
  ['right', 'Just far enough.', 'long'],
  ['now', 'Now imagine that Earth slowly begins to drift closer to it.', 'long'],
  ['square', 'Sunlight grows with the square of the distance. Move only ten percent closer, and you get almost a quarter more sunlight.', 'long'],
  ['bigger', 'The Sun looks a little bigger. A little whiter. The snow on the roofs starts to slide.', 'long'],
  ['melt', 'Glaciers melt into rivers. Lakes rise. And warmer air holds more water vapor, a greenhouse gas that traps even more heat.', 'long'],
  ['half', 'At seventy-five million miles, Earth would get half again as much sunlight as today.', 'pause'],
  ['fires', 'Forests dry out. Fires start on the hills.', 6],
  ['venus', 'Venus is only about a quarter closer to the Sun than we are.', 'pause'],
  ['lead', 'Its surface is hot enough to melt lead.', 'long'],
  ['band', 'We live in a narrow band around our star.', 'pause'],
  ['final', 'Not too hot. Not too cold.', 'none'],
];

export default function (at) {
  const climax = at('fires').e + .4, stop = at('venus').s - .1;
  const sunlight = d => ((93 / d) ** 2 - 1) * 100;
  return {
    T_END: at('final').e + 4.6,
    titleOut: at('intro').e + .4,
    sunOffset: [-60, 95, -210],          // the Sun low in the south, in front of the camera
    hud: { label: 'DISTANCE TO THE SUN', unit: ' million mi', decimals: 1,
           second: { label: 'SUNLIGHT', prefix: '+', fn: sunlight, unit: '%', showAt: at('square').s } },
    counter: [[0, 93], [at('now').e, 93], [at('square').s + 1, 90], [at('square').e, 84], [at('bigger').e, 81],
              [at('melt').e, 77], [at('half').s + 1, 75], [climax, 71], [stop, 70]],
    forceParams: { fireAt: .72 },
    captions: [[at('right').s - .2, at('right').e + .8, 'Just far enough.'],
               [at('square').s + 3, at('square').e + .6, '10% closer = 23% more sunlight.'],
               [at('melt').s + 2.5, at('melt').e + .4, 'Warmer air traps more heat.'],
               [at('half').s, at('half').e + .4, '1.5× the sunlight.'],
               [at('lead').s, at('lead').e + .6, 'Hot enough to melt lead.'],
               [at('band').s, at('band').e + .5, 'A narrow band.']],
    shots: [[0, 'wide'], [at('dist').s, 'mountains'], [at('now').s, 'village'], [at('bigger').s, 'square'],
            [at('melt').s, 'lake'], [at('half').s, 'wide'], [at('fires').s, 'mountains'], [climax + 2.5, 'village'],
            [climax + 4.8, 'wide']],
    looks: [[at('dist').s + .4, [-600, 950, -2100], 3, 8]],     // look up at the Sun when it is mentioned
    beats: { shelter: at('melt').s, climax, stop, dark: at('band').s, end: at('band').s - .2 },
    end: { title: 'What if the Sun<br>came closer to Earth?',
           lines: '10% closer means 23% more sunlight.<br>We live in a narrow band: not too hot, not too cold.' },
  };
}

export const upload = {
  title: 'What if the Sun came closer to Earth?',
  description: "POV: you're in a snowy mountain village when Earth starts drifting toward the Sun. ☀️\n\n" +
    'Just 10% closer means almost a quarter more sunlight. The snow slides off the roofs, lakes rise, and the hills start to burn.\n\n' +
    'How close could we get before it all goes wrong? 👇\n\n' +
    'New what-ifs every week on IfScape3D.\nAnimated with code, AI voice.\n\n#whatif #sun #space #shorts',
  tags: ['what if', 'what if the sun came closer', 'sun', 'space', 'science', 'physics', 'climate', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'What if the Sun came closer to Earth? ☀️ Just 10% closer = 23% more sunlight. #whatif #space #science #fyp',
};
