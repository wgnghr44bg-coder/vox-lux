// Proef baksteen Dieren (geen video): hond bij lege riem, herten, vos, groepje honden, vogels.
export const topic = { number: 991, slug: 'proef-dieren', place: 'street', force: 'calm', wide: true, question: 'Proef Dieren', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 22;
  return {
    T_END, tripod: true, brand: false, post: true,
    animals: [
      { kind: 'dog', path: [[0, 12.6, 8.2]], act: 'sit', leash: [11.6, 9.8], color: 0xb08a5a, shot: { name: 'dog', from: [-2.6, 1.1, 2.6], fov: 38 } },
      { kind: 'deer', n: 3, spread: 2.2, antlers: true, path: [[4, -1, -30], [7, -1, -12], [40, -1, -12]], shot: { name: 'deer', at: 1, from: [1, 1.5, 12], fov: 40 } },
      { kind: 'fox', path: [[8, 14.5, -2], [10.5, 12.5, 4], [30, 12.5, 4]], act: 'look', shot: { name: 'fox', at: 1, from: [-3.5, 1.1, -1.5], fov: 40 } },
      { kind: 'dog', n: 4, spread: 1.6, lag: .25, path: [[12, 0, -30], [15.5, 0, 2], [30, 0, 2]], shot: { name: 'dogs', at: 1, from: [-3, 1.3, 7], fov: 42 } },
      { kind: 'birds', n: 14, center: [-4, 10, -2], radius: 9, perch: [[-7.9, 6.25, 6.5], [-6.6, 6.25, 6.5]], land: 16 },
    ],
    hud: { label: '', unit: '', decimals: 0, sub: '' }, counter: [[0, 0]], range: [0, 1],
    captions: [], shots: [[0, 'dog'], [4, 'deer'], [8.6, 'fox'], [12, 'dogs'], [16, 'crossing']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: .3, climax: 1e9, falls: [], stop: T_END + 1, fade: 1e9 },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'proef', description: 'proef, niet uploaden', tags: [], tiktok: '' };
