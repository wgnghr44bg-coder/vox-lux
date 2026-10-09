// Proef baksteen Tijd (geen video): de straat van dag 0 tot jaar 25, dag/nacht, regen, seizoenen, groei en verval.
export const topic = { number: 990, slug: 'proef-tijd', place: 'street', force: 'calm', wide: true, question: 'Proef Tijd', title: '' };
export const lines = [['a', 'Test.', 'none']];
export default function () {
  const T_END = 40;
  return {
    T_END, tripod: true, brand: false, post: true,
    time: { days: [[0, 0], [4, .02], [12, 3], [16, 40], [22, 365], [30, 3650], [38, 9125]], hour: 14, doy: 130, rain: [[13, 16]], snow: true, clouds: .45,
            avoid: [[-1, 42, 8], [-6, 64, 8], [-9.4, 33, 5], [15.3, 4, 4], [10.5, 12, 4]] },
    hud: { label: 'TIME WITHOUT HUMANS', unit: '', decimals: 0, sub: '' },
    counter: [[0, 0], [T_END, 25]], range: [0, 25],
    captions: [], shots: [[0, 'high'], [36.5, 'pavement'], [37.5, 'corner']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: .5, climax: 1e9, falls: [], stop: T_END + 1, fade: 1e9, powerOff: [3, 6] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'proef', description: 'proef, niet uploaden', tags: [], tiktok: '' };
