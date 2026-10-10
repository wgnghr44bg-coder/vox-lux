// What if dinosaurs never went extinct? Chapter 2: the park (today, 10:00), fences, tower, T. rex and a long-neck.
export const topic = {
  number: 432, slug: 'dino-c2-park', place: 'prehistoric', force: 'calm', wide: true, padSilence: true,
  question: 'What if dinosaurs never went extinct?',
};

export const lines = [
  ['today', 'Today. Ten o\'clock. The gates open.', 'long'],
  ['three', 'Two hundred metres. Behind a double fence, six metres high, walks the most famous predator that ever lived.', 'pause'],
  ['rex', 'Tyrannosaurus rex. Twelve metres long. Around eight tonnes.', 'pause'],
  ['bite', 'Its bite was the strongest of any land animal we know: more than three tonnes of force.', 'long'],
  ['fifteen', 'Fifteen metres. A long-neck lifts its head over the fence, right above the visitors.', 'pause'],
  ['argentino', 'The biggest of them, Argentinosaurus, could weigh around seventy tonnes. As much as ten elephants.', 'pause'],
  ['feel', 'You would feel every footstep through your shoes.', 'long'],
  ['stops', 'Then the T. rex stops. And slowly turns its head… towards the tower.', 3],
  ['eyes', 'Its eyes faced forward, like ours. It could judge distance.', 'pause'],
  ['storm', 'And tonight, a storm is coming.', 'none'],
];

export const LAYOUT = {      // shared with chapter 3 (same park)
  fences: [{ pts: [[-140, 20], [-26, 20]], h: 6, double: 3, electric: true, lamps: 3 }, { pts: [[-14, 20], [84, 20]], h: 6, double: 3, electric: true, lamps: 3 },
           { pts: [[96, 20], [160, 20]], h: 6, double: 3, electric: true, lamps: 3 }],
  towers: [{ at: [34, 30], ry: Math.PI, h: 9, name: 'tower' }],
  clear: [[-150, 170, -16, 75], [-170, -60, -150, -103]],
};

export default function (at) {
  const T_END = at('storm').e + 1.5, climax = at('stops').e + .2, f = at('fifteen').s;
  return {
    T_END, tripod: true, brand: false, post: true,
    placeParams: { time: 'day', mist: 0, smoke: .7, clear: LAYOUT.clear, shots: {
      entrance: { pos: [-4, 2.4, 44], look: [0, 5, 64], drift: [0, 0, -.6], fov: 56 },
      'rex-tele': { pos: [33, 11.2, 24.2], look: [-108, 4, -110], drift: [0, 0, 0], fov: 16 },
      'rex-zoom': { pos: [33, 11.2, 24.2], look: [-112, 4.5, -108], drift: [0, 0, 0], fov: 7 },
      'park-wide': { pos: [64, 5, 60], look: [4, 7, 14], drift: [-.6, 0, 0], fov: 50 },
      'pov-neck': { pos: [22, 1.65, 33], look: [9, 11, 19], drift: [0, 0, 0], fov: 70 },
      'pov-puddle': { pos: [12, 1.6, 35.5], look: [11, 0, 31.5], drift: [0, 0, 0], fov: 64 },
      storm: { pos: [40, 14, 110], look: [-20, 30, -300], drift: [-1, 0, 0], fov: 56 },
    } },
    time: { hour: 10, doy: 160, days: [[0, 0], [T_END, .2]], clouds: .3 },
    ...LAYOUT,
    gates: [{ at: [0, 64], ry: 0, w: 12, h: 8, sign: 'DINOSAUR VALLEY', open: [[.6, 0], [4.5, 1]] }, { at: [-20, 21.5], w: 11, h: 8, sign: 'NO ENTRY', open: [[0, 0]] },
            { at: [90, 21.5], w: 11, h: 8, sign: 'NO ENTRY', open: [[0, 0]] }],
    groups: [{ at: [0, 70], n: 9, face: Math.PI, lamp: false }, { at: [6, 33], n: 8, face: Math.PI, lamp: false }, { at: [-26, 38], n: 5, face: Math.PI * .9, lamp: false }],
    puddles: [[11, 31.5, 1.3]],
    hud: { label: 'NEAREST DINOSAUR', unit: ' M', decimals: 0, sub: 'TODAY — 10:00' },
    counter: [[0, 200], [f - .2, 200], [f + 1.2, 15], [T_END, 15]], range: [200, 0],
    captions: [[at('rex').s + .3, at('rex').e + .6, 'T. rex · 12 m · ± 8 tonnes'], [at('argentino').s + .3, at('argentino').e + .4, 'Argentinosaurus · ± 35 m · ± 70 tonnes']],
    animals: [
      { kind: 'trex', path: [[0, -140, -108], [climax - 3.5, -100, -112], [T_END + 5, -100, -112]], roar: [at('bite').s + 1], look: [[at('stops').s + 1, [34, 12, 30]]], loud: .5 },
      { kind: 'sauropod', at: [8, 9], rot: .15, look: [[0, [6, 2, 33]]], steps: false },
      { kind: 'sauropod', path: [[0, -40, -2], [T_END, 26, -6]], rot: Math.PI / 2, loud: 1.4, look: [[0, [40, 6, 30]]] },
      { kind: 'triceratops', herd: { n: 3, spread: 6 }, path: [[0, 60, -6], [T_END, 75, 0]] },
      { kind: 'pterosaur', herd: { n: 2, spread: 40, seed: 2 }, fly: { c: [-60, 70, -120], r: 90, period: 34 } },
    ],
    shots: [[0, 'entrance'], [at('three').s - .2, 'rex-tele'], [at('rex').s - .2, 'rex-zoom'], [f - .2, 'park-wide'], [at('argentino').s - .2, 'pov-neck'],
            [at('feel').s - .2, 'pov-puddle'], [at('stops').s - .2, 'rex-tele'], [at('eyes').s - .2, 'park-wide'], [at('storm').s - .2, 'storm']],
    beats: { lookUp: f, shelter: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('stops').s - 1, climax + 1] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if dinosaurs never went extinct?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
