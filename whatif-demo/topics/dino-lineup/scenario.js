// Test sheet for the animals brick (animals.js): every species side by side in the prehistoric valley. Not a video.
export const topic = { number: 439, slug: 'dino-lineup', place: 'prehistoric', force: 'calm', wide: true, question: 'test', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 12, z = 30;
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, placeParams: { time: 'day', mist: 0, clear: [-70, 50, -5, 90] },
    hud: { label: 'TEST', unit: '', decimals: 0 }, counter: [[0, 0]], range: [0, 1], captions: [],
    animals: [
      { kind: 'sauropod', path: [[0, -62, z - 34], [12, -50, z - 34]], scale: .8 },
      { kind: 'trex', path: [[0, -26, z - 4], [12, -14, z - 4]], roar: [4], look: [[0, [0, 6, 75]]] },
      { kind: 'triceratops', path: [[0, -9, z + 8], [12, -2, z + 8]] },
      { kind: 'raptor', path: [[0, 3, z + 14], [12, 12, z + 14]] },
      { kind: 'velociraptor', at: [15, z + 20], rot: -1.2 },
      { kind: 'elephant', path: [[0, 12, z - 2], [12, 18, z - 2]] },
      { kind: 'mammoth', path: [[0, 26, z - 6], [12, 32, z - 6]], roar: [4.5] },
      { kind: 'pterosaur', fly: { c: [0, 30, z - 30], r: 25, period: 20 } },
      { kind: 'shrew', at: [7, z + 22], rot: 1.6, scale: 5 },
    ],
    shots: [[0, 'lineup']],
    beats: { lookUp: 1e9, shelter: 1e9, climax: 1e9, falls: [], stop: T_END, fade: 1e9 },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'test' };
