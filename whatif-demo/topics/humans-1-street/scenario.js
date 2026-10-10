// Imagine every human disappeared (lange video, plan: long/humans-disappeared/plan.md). Hoofdstuk 1: the moment (straat).
export const topic = {
  number: 441, slug: 'humans-1-street', place: 'street', force: 'calm', wide: true, voOffset: 3.0,
  question: 'What if every human disappeared?',
  title: 'Imagine<br>every human<br>disappeared',
};

export const lines = [
  ['imagine', 'Imagine every human on Earth disappeared.', 'long'],
  ['not', 'Not slowly. Not through a war, or a disease.', 'pause'],
  ['gone', 'All eight billion of us, gone in the very same second.', 'long'],
  ['afternoon', 'It is an ordinary afternoon.', 'pause'],
  ['normal', 'People are talking, laughing, waiting for the lights to change.', 'pause'],
  ['then', 'And then...', 3],
  ['nosound', 'No scream. No flash of light.', 'pause'],
  ['phone', 'Every phone call ends in the middle of a word.', 'long'],
  ['cars', 'Right now, millions of cars are moving on the roads of the world.', 'pause'],
  ['driver', 'In this second, not one of them has a driver.', 'long'],
  ['roll', 'Most roll on, and slowly come to a stop.', 'pause'],
  ['others', 'Some don\'t.', 'long'],
  ['alarm', 'Within minutes, the first alarms begin to wail.', 'pause'],
  ['noone', 'There is no one left to switch them off.', 'long'],
  ['dog', 'A dog waits beside an empty lead, for someone who will never come back.', 'long'],
  ['hour', 'One hour in, the city still looks almost normal.', 'pause'],
  ['lights', 'The traffic lights still change. Red, amber, green. For nobody.', 'long'],
  ['fail', 'But everything that kept this city alive needed people.', 'pause'],
  ['cliff', 'And it is already beginning to fail.', 'none'],
];

const hms = s => [3600, 60, 1].map(k => String(Math.floor(s / k) % (k === 3600 ? 100 : 60)).padStart(2, '0')).join(':');

export default function (at) {
  const V = at('then').e + .5, crash = at('others').e + .4, T_END = at('cliff').e + 1.6;
  const dogX = 11.2, dogZ = -4.2;
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, cars: false, lightCycle: 9,
    time: { days: [[0, 0], [V, 0], [at('hour').s, 1 / 24]], hour: 15.2, doy: 140, clouds: .35 },
    groups: [
      { at: [13, -6], n: 7, face: -.6, y: .2, shot: { name: 'group', from: [-2.2, 1.5, 6.6], fov: 46 } },
      { at: [-13, 15], n: 5, face: 2.6, y: .2, shot: { name: 'kerb', from: [3.5, 1.5, -5.5], fov: 48 } },
    ],
    animals: [{ kind: 'dog', path: [[0, dogX, dogZ]], acts: [[0, 'sit'], [V + 1.5, 'look']], color: 0xb08a5a,
                leash: [10.6, -2.7], leashHand: [12.1, .95, -5.1], leashDrop: V, shot: { name: 'dog', from: [-2.4, 1.0, 2.6], fov: 38 } }],
    traffic: [{ x: -7.4, z: -45, dir: 1, v: 10 }, { x: -7.4, z: -75, dir: 1, v: 9 }, { x: -2.6, z: -6, dir: 1, v: 9.5 },
              { x: 2.6, z: 25, dir: -1, v: 9 }, { x: 7.4, z: -15, dir: -1, v: 10 }, { x: 7.4, z: 75, dir: -1, v: 9.5 }, { x: 7.4, z: -70, dir: -1, v: 9 }],
    bikes: [{ x: -9.3, z: 2, dir: 1, v: 4.5, side: 1 }],
    crashes: [
      { at: crash, point: [.6, -28], cars: [{ dir: [0, 1], v: 9, off: -3.2 }, { dir: [0, -1], v: 8, off: -2 }], smoke: 1, alarm: 60 },
      { at: crash + 1.6, point: [9.9, -29], cars: [{ dir: [0, -1], v: 7, off: 2.5, spin: .25, slide: .8 }], smoke: .7 },
    ],
    extraShots: {
      crash: { pos: [-4.5, 1.8, -16], look: [1.2, .9, -28.5], drift: [0, 0, -.4], fov: 48 },
      'pov-look': { pos: [12.6, 1.65, -1.5], look: [13, .3, -6.5], drift: [0, 0, 0], fov: 62 },
      'pov-walk': { pos: [8.8, 1.65, 11], look: [dogX, .5, dogZ], lookDrift: [0, 0, 0], drift: [.6, 0, -8], fov: 62, run: { amp: .03, freq: 1.8 } },
      lights: { pos: [-1.5, 1.7, 27], look: [6, 4.6, 13.5], drift: [0, 0, -.4], fov: 38 },
    },
    hud: { label: 'TIME WITHOUT HUMANS', fmt: (v, t) => t < V ? '' : v < 3599.5 ? hms(v) : 'HOUR 1' },
    counter: [[0, 0], [V, 0], [at('alarm').s, 140], [at('dog').e, 1100], [at('hour').s, 3600], [T_END, 3640]],
    range: [0, 3600],
    captions: [],
    shots: [[0, 'high'], [at('not').s - .2, 'avenue'], [at('afternoon').s - .2, 'group'], [at('then').s - .3, 'kerb'], [V + 1.6, 'crossing'],
            [at('nosound').s + 1.5, 'pov-look'], [at('cars').s - .2, 'corner'], [at('roll').s + 1, 'crash'], [at('alarm').s + 3, 'high'],
            [at('noone').e + .2, 'pov-walk'], [at('dog').s + 2.4, 'dog'], [at('hour').s - .2, 'lights'], [at('lights').s + 1, 'avenue'], [at('fail').s - .2, 'high']],
    beats: { lookUp: 1e9, shelter: 1e9, carsStop: 1e9, vanish: V, climax: V, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { quiet: V, riser: [at('afternoon').s, V], heartbeat: [at('normal').s, V] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if every human disappeared?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
