// What if aliens landed tomorrow? (long video, okt 2026). Chapter 1: the street, HOUR 0, 15:00 -> the mothership arrives.
export const topic = {
  number: 501, slug: 'aliens-1-street', place: 'street', force: 'alien', wide: true,
  question: 'What if aliens landed tomorrow?',
  title: 'Imagine<br>aliens landed<br>tomorrow',
};

import { lines as raw } from './lines.js';
import { split, group } from './sentences.js';
export const lines = split(raw);

// mothership hover point: straight toward the Sun from the street, 2,000 m up (it slides in front of the Sun)
const SUN = [-70, 120, -170], k = 2000 / SUN[1], HOVER = [SUN[0] * k, 2000, SUN[2] * k];
const clock = s => { const m = Math.floor(s / 60), x = Math.floor(s % 60); return `HOUR 0 — 15:${String(m).padStart(2, '0')}:${String(x).padStart(2, '0')}`; };

export default function (at0) {
  const at = group(at0, lines);
  const arrive0 = at('three').s - 2, arrive1 = at('wide').s + 1, climax = at('still').e + .2, T_END = at('listening').e + 1.6;
  const subAt = []; for (let t = 0; t <= T_END; t += .5) subAt.push([t, clock(t * 1.6)]);
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, sunOffset: SUN,
    groups: [{ at: [13, -6], n: 7, face: -.6, y: .2, lamp: false, shot: { name: 'group', from: [-2.6, 1.6, 7.2], fov: 46 } },
             { at: [-13, 14], n: 5, face: 2.4, y: .2, lamp: false }],
    hud: { label: 'SHIP ALTITUDE', unit: ' m', decimals: 0, sub: clock(0), subAt },
    counter: [[0, 12000], [arrive0, 12000], [arrive1, 2100], [climax, 2000], [T_END, 2000]],
    range: [12000, 0],
    forceParams: { shade: [[0, 0], [at('three').e - 1.5, 0], [at('stop').e, .55], [arrive1, .88], [T_END, .9]] },
    ufo: {
      ships: [{ id: 'mother', kind: 'mother', r: 1400, haze: .25, spin: .003,
                keys: [[0, 5200, 6800, -7000], [arrive0, 5200, 6800, -7000], [arrive1, ...HOVER], [T_END, ...HOVER]] }],
    },
    extraShots: {
      under: { pos: [-4, 1.8, 40], look: [-300, 520, -1300], drift: [0, 0, -1], fov: 64 },              // street level, looking up at the ship over the roofs
      city: { pos: [1, 1.7, 22], look: [-160, 380, -1500], drift: [0, 0, -1.5], fov: 66 },           // far and high: the ship over the whole city
      'pov-sky': { pos: [14.6, 1.7, 9], look: [HOVER[0] * .3, HOVER[1] * .3, HOVER[2] * .3], fov: 66, hand: true },   // POV: you look up
      'pov-street': { pos: [-3, 1.7, 30], look: [2, 3, -80], fov: 64, hand: true },
    },
    captions: [[at('wide').s + .3, at('wide').s + 3.8, '≈ 3 km wide'], [at('star').s, at('star').s + 3.5, 'Nearest star: 4.2 light-years']],
    shots: [[0, 'high'], [at('notx').s - .2, 'group'], [at('three').s - .2, 'avenue'], [at('stop').s - .2, 'pov-sky'],
            [at('wide').s - .2, 'under'], [at('star').s - .2, 'city'], [at('built').s - .2, 'corner'],
            [at('still').s - .2, 'under'], [climax + 1.4, 'pov-street'], [at('terrifying').s - .2, 'group'], [at('listening').s - .2, 'pov-sky']],
    beats: { lookUp: at('stop').s, carsStop: at('stop').s + .5, shelter: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('built').s, climax + 2], riser: [at('star').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if aliens landed tomorrow?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
