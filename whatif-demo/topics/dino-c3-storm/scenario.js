// What if dinosaurs never went extinct? Chapter 3: the storm (21:40), power out, raptors at the gate, a second gate opens.
import { LAYOUT } from '../dino-c2-park/scenario.js';

export const topic = {
  number: 433, slug: 'dino-c3-storm', place: 'prehistoric', force: 'calm', wide: true, padSilence: true,
  question: 'What if dinosaurs never went extinct?',
};

export const lines = [
  ['storm', 'Twenty-one forty. A storm rolls over the park.', 'pause'],
  ['strike', 'Lightning strikes a pole. The power goes out.', 'pause'],
  ['fence', 'And with it… the electric fence.', 'long'],
  ['fifty', 'Fifty metres. Something moves between the trees.', 'pause'],
  ['movies', 'Forget the movies. A real Velociraptor was about the size of a turkey, and covered in feathers.', 'pause'],
  ['utah', 'But its bigger cousin, Utahraptor, could weigh as much as a horse.', 'pause'],
  ['groups', 'And animals like these may have hunted in groups.', 'long'],
  ['staff', 'The last keepers hurry away and lock the gates behind them.', 'pause'],
  ['five', 'Five metres.', 4],
  ['holds', 'The fence holds.', 'pause'],
  ['other', 'But on the far side of the park, another gate has swung open. And the biggest hunter of them all just walked through it.', 'none'],
];

export default function (at) {
  const T_END = at('other').e + 1.5, climax = at('five').e + .2, f = at('fifty').s, five = at('five').s, strike = at('strike').s + 1;
  return {
    T_END, tripod: true, brand: false, post: true, nightExposure: 2.2,
    placeParams: { time: 'day', mist: .6, smoke: 0, clear: LAYOUT.clear, shots: {
      'park-night': { pos: [64, 5, 60], look: [4, 6, 14], drift: [-.6, 0, 0], fov: 50 },
      'fence-line': { pos: [70, 2.6, 27], look: [-40, 4, 19], drift: [-.5, 0, 0], fov: 52 },
      'pov-fence': { pos: [-44, 1.65, 24.5], look: [-55, 2.2, -4], drift: [0, 0, 0], fov: 64, hand: true },
      'raptor-close': { pos: [-33, 1.8, 8], look: [-52, 1.4, -4], drift: [0, 0, 0], fov: 48 },
      'gate-out': { pos: [-31.2, 1.6, 20.7], look: [-32.4, 1.8, 14], drift: [0, 0, 0], fov: 58 },
      'gate2-view': { pos: [100, 3.2, 58], look: [90, 4.5, 20], drift: [0, 0, 0], fov: 54 },
    } },
    time: { hour: 21.66, doy: 160, days: [[0, 0], [T_END, T_END / 86400]], rain: [[-2, T_END + 5]], clouds: .9 },
    lightning: [strike, at('fifty').s + 3, at('staff').s + 1.5, at('other').s + 1],
    ...LAYOUT,
    gates: [{ at: [-20, 21.5], w: 11, h: 8, sign: 'NO ENTRY', open: [[0, 0]] }, { at: [90, 21.5], w: 11, h: 8, sign: 'NO ENTRY', open: [[at('other').s - 3, 0], [at('other').s + 1, 1]] }],
    groups: [{ at: [30, 37], n: 4, face: Math.PI, lamp: true, lampPower: 40 }],
    hud: { label: 'NEAREST DINOSAUR', unit: ' M', decimals: 0, sub: 'TODAY — 21:40' },
    counter: [[0, 50], [five - .2, 50], [five + 1, 5], [T_END, 5]], range: [50, 0],
    captions: [[at('movies').s + .5, at('movies').e + .4, 'Velociraptor · ± 15 kg'], [at('utah').s + .3, at('utah').e + .4, 'Utahraptor · ± 5.5 m · ± 400 kg']],
    animals: [
      { kind: 'raptor', herd: { n: 3, spread: 3, depth: .3, lag: 1, seed: 7 }, path: [[0, -70, -12], [f, -60, -6], [at('groups').e, -42, 4], [five - 1.2, -32, 15.3], [T_END + 4, -32, 15.5]],
        look: [[five - 1, [-32, 1.6, 20.6]]], roar: [at('holds').s + .2] },
      { kind: 'velociraptor', path: [[0, -52, -3], [at('movies').s, -52, -3], [at('utah').s + 2, -46, 2], [T_END, -44, 4]] },
      { kind: 'trex', path: [[0, 86, -10], [at('other').s, 89, 10], [T_END + 4, 92, 46]], roar: [at('other').e - 1] },
    ],
    shots: [[0, 'park-night'], [at('strike').s - .2, 'tower-view'], [at('fence').s - .2, 'fence-line'], [f - .2, 'pov-fence'], [at('movies').s - .2, 'raptor-close'],
            [at('staff').s - .2, 'park-night'], [five - .2, 'gate-out'], [at('other').s - .2, 'gate2-view']],
    beats: { lookUp: 1e9, shelter: at('staff').s, powerOut: strike, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('groups').s, climax + 1], riser: [at('staff').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if dinosaurs never went extinct?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
