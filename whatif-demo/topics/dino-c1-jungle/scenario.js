// What if dinosaurs never went extinct? Chapter 1: the miss (prehistoric valley, 66 million years ago).
export const topic = {
  number: 431, slug: 'dino-c1-jungle', place: 'prehistoric', force: 'calm', wide: true, padSilence: true,
  question: 'What if dinosaurs never went extinct?',
  title: 'Imagine<br>dinosaurs never<br>went extinct',
};

export const lines = [
  ['imagine', 'Imagine dinosaurs never went extinct.', 'long'],
  ['notbones', 'Not bones in a museum. Not a movie. Living, breathing giants… sharing the planet with you.', 'pause'],
  ['goback', 'To see how, we have to go back sixty-six million years.', 'long'],
  ['rock', 'A rock about ten kilometres wide is racing towards Earth at twenty kilometres per second.', 'pause'],
  ['history', 'In our history, it hits. Three out of every four species vanish.', 'long'],
  ['miss', 'But Earth moves fast through space. If that rock had arrived just a few minutes later… it would have missed.', 4],
  ['onekm', 'One kilometre. Across the river, a herd of long-necks keeps on eating, as if nothing happened.', 'pause'],
  ['forty', 'Forty metres. Triceratops, around ten tonnes each, wade in to drink.', 'long'],
  ['ancestors', 'Back then, our ancestors were tiny. Small furry mammals, hiding in the ferns.', 'pause'],
  ['never', 'Most scientists think we would never have appeared at all.', 'pause'],
  ['fence', 'But imagine we did. And imagine we tried to keep them… behind a fence.', 'none'],
];

export default function (at) {
  const T_END = at('fence').e + 1.5, climax = at('miss').e + .2;
  const a = at('onekm').s, b = at('forty').s;
  return {
    T_END, tripod: true, brand: false, showTitle: true, post: true, titleOut: at('imagine').e + .6,
    placeParams: { time: 'morning', smoke: 1, mist: 1 },
    hud: { label: 'NEAREST DINOSAUR', unit: ' M', decimals: 0, sub: '66,000,000 YEARS AGO' },
    counter: [[0, 1000], [b - .2, 1000], [b + 1.2, 40], [T_END, 40]],
    range: [1000, 0],
    captions: [[at('rock').s + .3, at('rock').e + .8, '10 km wide · 20 km per second'], [at('forty').s + .4, at('forty').e + .8, 'Triceratops · 9 m · ± 10 tonnes']],
    skyObjects: [
      { t0: at('rock').s - .5, t1: at('miss').s, from: [-2600, 650, -3000], to: [-1500, 800, -2000], r: 45, ease: 1, glow: 0xffc070, hot: 1, weight: 4, fog: false },
      { t0: at('miss').s, t1: climax + 4.5, from: [-1500, 800, -2000], to: [2600, 1500, 900], r: 30, ease: 1.4, glow: 0xffb060, hot: .9, weight: 6, fog: false },
    ],
    events: [{ t: at('miss').s + 2, kind: 'flyby', e: 1, dur: climax + 4 - at('miss').s - 2 }],
    animals: [
      { kind: 'sauropod', herd: { n: 6, spread: 45, seed: 3 }, path: [[0, -120, -960], [T_END, -150, -985]], rot: -1.4, look: [[climax - 1, [400, 900, -600]], [climax + 4, null]] },
      { kind: 'sauropod', herd: { n: 3, spread: 30, seed: 9 }, at: [-420, -760], rot: .8, drink: [[0, 40]], steps: false },
      { kind: 'triceratops', herd: { n: 4, spread: 7, depth: .6, seed: 4, lag: 2 }, path: [[0, -16, -24], [b, -14, -30], [b + 6, -10, -42], [T_END, -9, -44]], rot: Math.PI,
        drink: [[b + 6, T_END + 5]], look: [[climax - 2.5, [300, 700, -300]], [climax + 3, null]] },
      { kind: 'triceratops', path: [[0, -14, 35], [at('never').s - 1.5, -14, 35], [T_END + 4, 40, 33]], rot: Math.PI / 2, seed: 41 },
      { kind: 'shrew', path: [[0, 6.15, 44.9], [at('ancestors').s + 2, 6.15, 44.9], [at('ancestors').s + 3.5, 4.5, 42.5], [T_END, 4.5, 42.5]], rot: Math.PI, seed: 5, scale: 1.3 },
      { kind: 'pterosaur', herd: { n: 3, spread: 30, seed: 6 }, fly: { c: [-40, 55, -160], r: 70, period: 30, dir: 1 } },
    ],
    shots: [[0, 'valley'], [at('notbones').s - .2, 'riverbank'], [at('rock').s - .2, 'canopy'], [at('miss').s - .2, 'pov-sky'],
            [a - .2, 'across'], [b - .2, 'shore'], [at('ancestors').s - .2, 'ferns'], [at('fence').s - .2, 'valley']],
    beats: { lookUp: 1e9, shelter: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('rock').s, climax], riser: [at('history').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if dinosaurs never went extinct?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
