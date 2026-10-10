// What if aliens landed tomorrow? Chapter 3: the army (river city), DAY 1 -> the small ships break away and scan.
import { lines as raw } from './lines.js';
import { split, group } from '../aliens-1-street/sentences.js';
import { rng } from '../../engine/util.js';
export const lines = split(raw);
export const topic = {
  number: 503, slug: 'aliens-3-army', place: 'river-city', force: 'alien', wide: true,
  question: 'What if aliens landed tomorrow?', title: '',
};

const MOTHER = [-320, 1500, -1900];

export default function (at0) {
  const at = group(at0, lines);
  const T_END = at('week').e + 1.6, d0 = at('dozens').s, R = rng(77);
  // the column: tanks and trucks drive in along the quay road and park in a row
  const kinds = ['tank', 'truck', 'truck', 'tank', 'truck', 'jeep', 'truck'];
  const vehicles = kinds.map((kind, i) => ({ kind, keys: [[0, 150 + i * 14, 7], [9 + i * .9, 52 + i * 13, 7]] }));
  vehicles.push({ kind: 'tank', keys: [[0, 18, 10.5]], ry: -Math.PI / 2, aim: [at('dozens').s, .5] }, { kind: 'jeep', keys: [[0, 28, 2.6]], ry: Math.PI / 2 });
  // small ships: they leave the mothership and spread out over the city
  const targets = [[90, 150, -12], [-30, 170, -160], [62, 125, -55], [-220, 240, -260], [240, 260, -320], [-420, 300, -520], [380, 300, -600], [-120, 280, -700], [150, 230, -480], [-600, 340, -900], [560, 340, -950], [0, 320, -1100]];
  const ships = [{ id: 'mother', kind: 'mother', r: 1400, haze: .3, look: 2, keys: [[0, ...MOTHER], [T_END, MOTHER[0], MOTHER[1] - 60, MOTHER[2]]] }];
  targets.forEach((p, i) => { const t1 = d0 + 2.5 + i * .35 + R() * 1.5;
    ships.push({ id: 's' + i, kind: 'scout', r: 22, from: d0 - .2 + i * .25, spin: .25,
      keys: [[0, MOTHER[0] + (R() - .5) * 600, MOTHER[1] - 220, MOTHER[2] + (R() - .5) * 600], [d0 + i * .25, MOTHER[0] + (R() - .5) * 600, MOTHER[1] - 220, MOTHER[2] + (R() - .5) * 600], [t1, ...p], [T_END, p[0], p[1] - 10, p[2]]] }); });
  const b0 = at('beams').s - .6, b1 = T_END;
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, noTraffic: true,
    hud: { label: 'SHIP ALTITUDE', unit: ' m', decimals: 0, sub: 'DAY 1', subAt: [[0, 'DAY 1 — 08:00'], [at('hours').s, 'DAY 1 — 15:00']] },
    counter: [[0, 1600], [T_END, 1540]], range: [12000, 0],
    forceParams: { shade: [[0, .5], [T_END, .55]] },
    ufo: { ships, beams: [
      { ship: 's1', t0: b0, t1: b1, r: 14, opacity: .16, keys: [[b0, -150, -150], [b0 + 4, 60, -170], [b0 + 9, -60, -120], [b1, 40, -200]] },
      { ship: 's0', t0: b0 + .4, t1: b1, r: 10, opacity: .15, keys: [[b0, 140, 8], [b0 + 4, 60, 7], [b0 + 8, 110, 9], [b1, 70, 7]] },
      { ship: 's2', t0: b0 + .8, t1: b1, r: 9, opacity: .15, keys: [[b0, 95, -21], [b0 + 5, 45, -21], [b0 + 10, 75, -20], [b1, 55, -21]] },
      { ship: 's3', t0: b0 + 1.2, t1: b1, r: 18, opacity: .15, keys: [[b0, -260, -60], [b1, -120, -40]] },
    ] },
    army: {
      vehicles,
      helis: [{ orbit: { c: [-40, 75, -170], r: 170, period: 34, ph: 1 } }, { orbit: { c: [120, 95, -260], r: 230, period: 44, dir: -1 } }],
      soldiers: [{ at: [41, 8], n: 6, face: Math.PI / 2, spread: 2.2 }, { at: [64, -21], n: 9, face: Math.PI, line: true, spread: 3.2 },
                 { at: [88, 2.2], n: 5, face: Math.PI * .9, spread: 1.8 }],
      roadblocks: [{ at: [33, 8], ry: Math.PI / 2 }],
      barriers: [{ at: [28, 8], ry: Math.PI / 2, n: 6 }],
    },
    extraShots: {
      column: { pos: [58, 2.4, -3], look: [150, 1.4, 8], drift: [0, 0, 0], fov: 50 },
      block: { pos: [22, 1.8, 17], look: [46, 1.8, 5], drift: [.3, 0, -.2], fov: 56 },
      river: { pos: [110, 9, -26], look: [-200, 260, -1500], drift: [-1.5, 0, 0], fov: 64 },
      'pov-soldier': { pos: [59.2, 1.7, -20.2], look: [-150, 380, -1500], fov: 66, hand: true },
      ship: { pos: [-90, 2, -27], look: [-330, 880, -1900], drift: [0, 0, 0], fov: 66 },
      quay: { pos: [150, 14, 26], look: [62, 0, -30], drift: [-1, 0, 0], fov: 56 },
      'pov-beam': { pos: [52, 1.7, -18], look: [62, 125, -55], fov: 64, hand: true },
    },
    shots: [[0, 'column'], [at('noplan').s - .2, 'block'], [at('order').s - .2, 'river'], [at('order').s + 2.8, 'pov-soldier'],
            [at('hours').s - .2, 'ship'], [d0 - .2, 'river'], [at('beams').s - .2, 'quay'], [at('scan').s - .2, 'pov-beam'], [at('week').s - .2, 'ship']],
    captions: [],
    beats: { lookUp: at('hours').s, shelter: -40, climax: at('beams').e + .3, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heli: [[0, T_END]], engines: [[0, 14]], heartbeat: [at('dozens').s, at('beams').e + 2], riser: [at('dozens').s, at('beams').e] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if aliens landed tomorrow?', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
