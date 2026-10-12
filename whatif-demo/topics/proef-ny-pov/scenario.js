// Proef (geen video): POV-wandeling door de New York-straat, mensen lopen, duiven vliegen op. Geen kracht.
export const topic = { number: 993, slug: 'proef-ny-pov', place: 'newyork', force: 'calm', question: 'Proef NY POV', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 8.5, X = 14.6, z = t => 26 - 1.2 * t;
  return {
    T_END, look: 'blender', hudIn: 1e9, titleOut: 0, showTitle: false,
    camPath: [
      [0, [X, 1.7, z(0)], [13.4, 1.9, z(0) - 30], 70],
      [3, [X, 1.7, z(3)], [13.8, 1.6, z(3) - 12], 70],             // kijkt naar de duiven
      [5.5, [X, 1.7, z(5.5)], [6, 4, z(5.5) - 24], 70, -2],         // kijkt de straat in, naar de taxi's
      [T_END, [X, 1.7, z(T_END)], [13, 3, z(T_END) - 30], 70, 0],   // weer vooruit
    ],
    fov: 70, walkBob: [[0, T_END, .035]],
    animals: [
      { kind: 'birds', n: 14, color: 0x4f555e, scale: .8, land: -6, fly: 3.4, center: [10, 9, 6], radius: 8,
        perch: Array.from({ length: 14 }, (_, i) => [13.6 + (i % 4) * .45, .26, 18 - Math.floor(i / 4) * .9 - (i % 2) * .3]) },
    ],
    counter: [[0, 0]], range: [0, 1], hud: { label: '', unit: '' }, captions: [],
    beats: { stop: T_END + 1, lookUp: 1e9, shelter: 1e9, carsStop: 1e9, climax: 1e9, falls: [] },
  };
}
export const upload = { title: 'proef', description: 'proef, niet uploaden', tags: [], tiktok: '' };
