// Imagine the Sun went out (owner's shot list, okt 2026). Chapter 1: the street, day 0, 12:00 -> 12:08 PM.
export const topic = {
  number: 421, slug: 'sun-d1-street', place: 'street', force: 'cold', wide: true,
  question: 'What if the Sun went out?',
  title: 'Imagine<br>the Sun<br>went out',
};

export const lines = [
  ['imagine', 'Imagine looking up at the sky, and watching the Sun disappear.', 'long'],
  ['energy', 'In a single hour, the Sun delivers about as much energy to Earth as all of humanity uses in an entire year.', 'pause'],
  ['every', 'Every plant, every meal, every breath of wind starts with that light.', 'long'],
  ['now', 'Now imagine that, at exactly twelve o\'clock, it simply stops shining.', 'long'],
  ['nothing', 'At first, nothing seems to happen.', 'pause'],
  ['old', 'The light hitting this street left the Sun eight minutes ago. It is still on its way, so the sky stays blue and the shadows stay sharp.', 'pause'],
  ['warning', 'Nothing in the universe travels faster than light. So no warning could reach us any sooner.', 'long'],
  ['eight', 'Twelve oh eight.', 3],
  ['seconds', 'In just a few seconds, noon turns into night.', 'pause'],
  ['nosunset', 'No sunset. No twilight. Without sunlight to scatter, the sky does not fade. It simply turns black.', 'long'],
  ['lamps', 'The street lights switch on by themselves. Their sensors think it is night.', 'pause'],
  ['lost', 'But the world has just lost the most important source of energy it has.', 'none'],
];

const clock = s => { const m = Math.floor(s / 60), x = Math.round(s % 60); return `DAY 0 — 12:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')} PM`; };

export default function (at) {
  const t0 = at('now').e, climax = at('eight').e + .2, dark = climax + 2.5, T_END = at('lost').e + 2;
  const subAt = [];
  for (let t = 0; t <= T_END; t += .25) {
    const s = t < t0 ? 0 : t < climax ? 488 * (t - t0) / (climax - t0) : 488 + (t - climax);
    subAt.push([t, clock(Math.min(s, 599))]);
  }
  return {
    T_END, tripod: true, brand: false, showTitle: true, post: true,
    groups: [{ at: [13, -6], n: 7, face: -.6, y: .2, shot: { name: 'group', from: [-3.1, 1.5, 6], fov: 46 } }],
    titleOut: at('imagine').e + .4,
    hud: { label: 'DAYLIGHT', unit: '%', decimals: 0, sub: clock(0), subAt },
    counter: [[0, 100], [climax, 100], [climax + .8, 55], [dark, 0], [T_END, 0]],
    range: [100, 0], forceParams: { darkAt: [0, 1], frostAt: [2, 3], snow: 0 },
    captions: [[at('old').s, at('old').s + 3.5, 'Light takes 8 min 20 s.'], [at('eight').s, at('eight').e + 1.5, '12:08 PM.']],
    shots: [[0, 'high'], [at('energy').s - .2, 'corner'], [at('every').s - .2, 'group'], [at('now').s - .2, 'avenue'],
            [at('old').s - .2, 'pov-up'], [at('old').s + 4, 'crossing'], [at('warning').s - .2, 'high'],
            [at('eight').s - .2, 'corner'], [climax + 2.2, 'group'],
            [at('nosunset').s - .2, 'pov-up'], [at('lamps').s - .2, 'avenue'], [at('lost').s - .2, 'high']],
    beats: { lookUp: climax + .6, carsStop: climax + .3, shelter: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { hiss: -60, ice: -60, heartbeat: [at('warning').s, climax + 2], riser: [at('warning').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
