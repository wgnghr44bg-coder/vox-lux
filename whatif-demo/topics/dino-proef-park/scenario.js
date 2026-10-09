// Test sheet for the fences brick (fences.js) + big animals: a dinosaur park in the prehistoric valley, daytime. Not a video.
export const topic = { number: 438, slug: 'dino-proef-park', place: 'prehistoric', force: 'calm', wide: true, question: 'test', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 12;
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, placeParams: { time: 'day', mist: 0, smoke: .6, clear: [-100, 100, -18, 70] },
    hud: { label: 'NEAREST DINOSAUR', unit: ' M', decimals: 0, sub: 'TODAY — 10:00' }, counter: [[0, 15]], range: [0, 1], captions: [],
    fences: [{ pts: [[-110, 20], [-26, 20]], h: 6, double: 3, electric: true, lamps: 3 }, { pts: [[-14, 20], [110, 20]], h: 6, double: 3, electric: true, lamps: 3 }],
    towers: [{ at: [34, 30], ry: Math.PI, h: 9, name: 'tower' }],
    gates: [{ at: [-20, 21.5], w: 11, h: 8, sign: 'RESTRICTED AREA', open: [[0, 0]] }],
    groups: [{ at: [6, 33], n: 8, face: Math.PI, lamp: false }, { at: [-28, 38], n: 5, face: Math.PI * .9, lamp: false }],
    animals: [
      { kind: 'sauropod', at: [8, 9], rot: .15, look: [[0, [6, 2, 33]]] },
      { kind: 'trex', path: [[0, 14, -14], [12, 40, 2]], roar: [6.5], look: [[5, [34, 12, 30]]] },
      { kind: 'triceratops', path: [[0, 60, -6], [12, 66, -2]] },
    ],
    extraShots: {
      'park-wide': { pos: [70, 6, 62], look: [-10, 6, 5], drift: [0, 0, 0], fov: 56 },
      'gate-view': { pos: [-20, 2.5, 52], look: [-20, 6, 10], drift: [0, 0, 0], fov: 56 },
      'pov-neck': { pos: [22, 1.65, 33], look: [9, 11, 19], drift: [0, 0, 0], fov: 70 },
    },
    shots: [[0, 'park-wide'], [3, 'gate-view'], [6, 'tower'], [9, 'pov-neck']],
    beats: { lookUp: 1, shelter: 1e9, climax: 1e9, falls: [], stop: T_END, fade: 1e9 },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'test' };
