// Proef (geen video): baasje laat de hond uit op het parkpad (animals.js walker), Blender-look.
export const topic = { number: 992, slug: 'proef-hond', place: 'suburb', force: 'calm', question: 'Proef hond', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 12;
  return {
    T_END, tripod: true, brand: false, look: 'blender', hudIn: 1e9,
    animals: [
      { kind: 'dog', path: [[0, -42, 20.3], [12, -28, 20.3]], color: 0xb08a5a, walker: { side: -.45, coat: 0xb8322a, pants: 0x27324f } },
    ],
    extraShots: {
      walk: { pos: [-40.1, 1.2, 24.4], look: [-42.0, .95, 20.1], drift: [11.67, 0, 0], fov: 62 },   // meelopend, zoals de Blender-wandeling
    },
    hud: { label: '', unit: '', decimals: 0, sub: '' }, counter: [[0, 0]], range: [0, 1],
    captions: [], shots: [[0, 'walk']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: 1e9, climax: 1e9, falls: [], stop: T_END + 1, fade: 1e9 },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'proef', description: 'proef, niet uploaden', tags: [], tiktok: '' };
