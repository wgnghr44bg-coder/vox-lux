// What if aliens landed tomorrow? Chapter 4: contact (beach at dawn), WEEK 1 -> a ship lands, the door opens.
import { lines } from './lines.js';
export { lines };
export const topic = {
  number: 504, slug: 'aliens-4-contact', place: 'boulevard', force: 'alien', wide: true,
  question: 'What if aliens landed tomorrow?', title: '',
};

const LX = -170, LZ = 12, GY = LZ / 38 * 2.4, LY = GY + .55 * 24;     // landing spot on the sand

export default function (at) {
  const T_END = at('ask').e + 3.2, land = at('silent').s + 2.4, door = at('door').s - .2;
  const groups = [[-118, 46], [-100, 50], [-136, 48], [-84, 45], [-108, 58], [-128, 56]].map(([x, z], i) =>
    ({ at: [x, z], n: 9, face: -Math.PI / 2, spread: 3, lamp: false, ...(i === 0 && { shot: { name: 'faces', from: [-6, 1.2, -3], fov: 44 } }) }));
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, sunbathers: 0, sunOffset: [-60, 22, -320],
    groups,
    hud: { label: 'SHIP ALTITUDE', unit: ' m', decimals: 0, sub: 'WEEK 1 — 06:12' },
    counter: [[0, 900], [at('line').s, 120], [at('silent').s + .3, 10], [land, 0], [T_END, 0]], range: [12000, 0],
    forceParams: { shade: [[0, .1], [T_END, .1]], dawn: 1, hum: [[0, .7], [at('silent').s, .8], [at('silent').s + 1.2, .05], [T_END, .05]] },
    ufo: { ships: [
      { id: 'mother', kind: 'mother', r: 1400, haze: .45, keys: [[0, 300, 1300, -2700], [T_END, 300, 1290, -2700]] },
      { id: 'lander', kind: 'scout', r: 24, spin: 0, ry: Math.PI / 2, legs: at('line').e - 1, land, door, doorLight: 90, look: 6,
        keys: [[0, -300, 230, -520], [8, -210, 95, -150], [at('line').s, LX + 6, 60, LZ - 6], [at('silent').s + .4, LX, 24, LZ], [land, LX, LY, LZ], [T_END, LX, LY, LZ]] },
    ] },
    army: {
      vehicles: [{ kind: 'truck', keys: [[0, -96, 66]], ry: Math.PI / 2 }, { kind: 'truck', keys: [[0, -82, 66]], ry: Math.PI / 2 }, { kind: 'jeep', keys: [[0, -112, 31]], ry: -Math.PI / 2 }],
      helis: [{ orbit: { c: [-170, 70, -60], r: 140, period: 40, ph: 2 } }],
      soldiers: [{ at: [-128, 20], n: 10, face: -Math.PI / 2, line: 'z', spread: 2.6, headUp: .25 }],
    },
    extraShots: {
      bay: { pos: [-40, 7, 44], look: [-130, 70, -320], drift: [-1, 0, 0], fov: 60 },
      line: { pos: [-60, 3.4, 30], look: [-205, 55, -120], drift: [0, 0, -.3], fov: 50 },
      'pov-crowd': { pos: [-104, 3 + 1.65, 47], look: [-170, 40, 14], fov: 62, hand: true },
      crowd: { pos: [-70, 13, 78], look: [-165, 24, 10], drift: [-.6, 0, 0], fov: 56 },
      landing: { pos: [-118, 2.4, 30], look: [-170, 9, 11], drift: [-.25, 0, 0], fov: 52 },
      door: { pos: [-108, 1.8, 21], look: [-160, 5, 12], drift: [-.2, 0, 0], fov: 46 },
      high: { pos: [-60, 28, 84], look: [-200, 18, -190], drift: [0, 1.2, .8], fov: 60 },
    },
    shots: [[0, 'bay'], [at('ahead').s - .2, 'line'], [at('ahead').s + 3.4, 'pov-crowd'], [at('line').s - .2, 'crowd'],
            [at('silent').s - .2, 'landing'], [door - .4, 'door'], [at('alone').s - .2, 'faces'], [at('ask').s - .2, 'high']],
    captions: [],
    beats: { lookUp: 1, shelter: 1e9, carsStop: -20, climax: land, falls: [], stop: T_END + 1, fade: at('ask').e - .4 },
    audio: { heli: [[0, at('silent').s]], heartbeat: [at('line').s, land + 1], riser: [at('line').s, at('silent').s] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if aliens landed tomorrow?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
