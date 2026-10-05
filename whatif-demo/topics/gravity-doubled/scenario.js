// What if gravity suddenly doubled?  (onderwerpen.md #1)
// Only this file changes per video: topic, place, force, counter, lines, timing and end text.
export const topic = {
  number: 1, slug: 'gravity-doubled', place: 'river-city', force: 'gravity',
  question: 'What if gravity suddenly doubled?',
  title: 'What if<br>gravity suddenly<br>doubled?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['intro', 'Imagine you are standing by a wide river, under a great suspension bridge.', 'pause'],
  ['calm', 'It is a quiet afternoon.', 'pause'],
  ['built', 'Every bridge, every building, every tree around you was made for one force.', 'pause'],
  ['oneg', 'The pull of the Earth.', 'long'],
  ['now', 'Now imagine that, in one minute, gravity doubles.', 'long'],
  ['tired', 'At first, you only feel tired. Your arms hang heavy. Every single step takes effort.', 'long'],
  ['half', 'At one and a half g, standing up feels like carrying a child on your back.', 'pause'],
  ['bow', 'Trees bow. Branches snap. Cars sink low on their springs.', 'long'],
  ['bridge', 'The bridge was built to hold its own weight. Now that weight keeps growing.', 'pause'],
  ['cables', 'Its steel cables stretch. The deck begins to sag.', 'long'],
  ['two', 'At two g, you would weigh twice as much as you do now.', 'pause'],
  ['heart', 'Your heart would have to work much harder to push blood up to your head.', 'long'],
  ['walls', 'Old brick walls crack. Steel groans under the strain.', 6],
  ['fall', 'Anything you dropped would hit the ground forty percent faster.', 'pause'],
  ['air', 'The air would press down twice as hard.', 'long'],
  ['made', 'Everything we have ever built was made for one gravity.', 'pause'],
  ['final', 'Not two.', 'none'],
];

export default function (at) {
  const climax = at('walls').e + .4, stop = at('fall').s - .1;
  return {
    T_END: at('final').e + 4.6,
    titleOut: at('calm').e + .2,
    hud: { label: 'GRAVITY', unit: ' g', decimals: 2,
           second: { label: 'YOU WEIGH', scale: 160, unit: ' lb', showAt: at('built').s } },
    counter: [[0, 1], [at('now').e, 1], [at('tired').e, 1.25], [at('half').s + .5, 1.5], [at('bridge').s, 1.72],
              [at('two').s + .4, 2], [stop, 2]],
    range: [1, 2], forceParams: { gMax: 2 },
    captions: [[at('oneg').s - .1, at('oneg').e + .8, 'One g.'],
               [at('now').s + .3, at('now').e + 1, 'Gravity doubles.'],
               [at('half').s, at('half').e + .3, 'Like carrying a child.'],
               [at('cables').s, at('cables').e + .8, 'The deck begins to sag.'],
               [at('two').s, at('two').e + .3, 'Twice your weight.'],
               [at('air').s, at('air').e + .6, 'Twice the air pressure.']],
    shots: [[0, 'wide'], [at('built').s, 'quay'], [at('now').s, 'wide'], [at('tired').s, 'quay'],
            [at('bridge').s, 'deck'], [at('cables').s, 'under'], [at('two').s, 'span'], [at('heart').s, 'quay'],
            [at('walls').s, 'north'], [at('walls').s + 2.4, 'span'],
            [climax, 'span'], [climax + 3.3, 'towers'], [climax + 5.6, 'wide']],
    beats: {
      carsStop: at('bow').s, shelter: at('heart').s - 1.5,
      hangers: at('walls').s + 2.2, deckBreak: climax + .9,
      falls: [at('walls').s + .6, climax + 3.6, climax + 4.6, climax + 2.2],
      climax, stop, dark: at('made').s, end: at('made').s - .2,
    },
    end: { title: 'What if gravity<br>suddenly doubled?',
           lines: 'You would weigh twice as much.<br>Everything we build is made for one g.' },
  };
}

export const upload = {
  title: 'What if gravity suddenly doubled? #shorts',
  description: 'Imagine gravity doubling in a single minute. You would weigh twice as much, trees would bow, ' +
    'and a great suspension bridge, built to carry its own weight, would suddenly carry twice as much.\n\n' +
    'The facts: at 2 g everything weighs twice as much, a dropped object hits the ground about 40% faster ' +
    '(√2 times the speed from the same height), and the air presses down twice as hard. Our structures are ' +
    'designed for 1 g with safety margins; doubling every load would push many of them past their limits.\n\n' +
    '#whatif #physics #science #gravity #shorts',
  tags: ['what if', 'gravity', 'physics', 'science', 'suspension bridge', 'what if gravity doubled', 'shorts', 'hypothetical'],
  tiktok: 'What if gravity suddenly doubled? 🌍 You would weigh twice as much, and every bridge was built for one g. #whatif #physics #science #gravity #fyp',
};
