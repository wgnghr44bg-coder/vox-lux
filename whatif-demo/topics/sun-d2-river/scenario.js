// Imagine the Sun went out (owner's shot list). Chapter 2: the river city, day 1.
export const topic = {
  number: 422, slug: 'sun-d2-river', place: 'river-city', force: 'cold', wide: true, voOffset: 1.5,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['day1', 'Day one.', 'long'],
  ['dark', 'There was no sunrise this morning. The only light on the river comes from the lamps along the quay.', 'pause'],
  ['inside', 'People hurry inside. On the road along the water, the traffic slowly comes to a stop.', 'pause'],
  ['driver', 'One driver steps out, and looks up at a sky that should be blue.', 'long'],
  ['grid', 'Right now, almost every heater and every light is switched on at the same time.', 'pause'],
  ['limit', 'Power grids were never built for a night without end. Within hours, they are pushed past their limits.', 'long'],
  ['out', 'And then, one by one, the lights go out.', 3],
  ['walk', 'Without the Sun, the ground keeps losing its heat to space, and nothing comes to replace it.', 'pause'],
  ['breath', 'By midnight, your breath turns white in the air.', 'pause'],
  ['fall', 'On a clear night, the temperature can drop a degree or two every hour. This night will never end.', 'long'],
  ['river', 'At the edges of the river, the water begins to freeze. Frost creeps over the cars. The trees turn white.', 'long'],
  ['danger', 'And now, the real danger begins.', 'none'],
];

export default function (at) {
  const offA = at('out').s, offB = at('out').e + 2.4, climax = at('out').e + .4, T_END = at('danger').e + 1.6;
  return {
    T_END, tripod: true, brand: false, post: true,
    groups: [{ at: [70, -20], n: 6, face: 3.1, y: .2, shot: { name: 'group', from: [0, 1.5, -5.8], fov: 50 } }],
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'DAY 1',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'DAY 1'], [at('walk').s, 'DAY 1 — TEMPERATURE FALLING']] },
    counter: [[0, 12], [at('limit').e, 9], [at('walk').s, 6], [at('fall').e, -2], [at('river').e, -6], [T_END, -6]],
    range: [15, -40], forceParams: { darkAt: [-1, 0], frostAt: [.2, .6], snow: 0, breath: [[at('walk').s - .2, at('fall').s - .2]] },
    captions: [[at('day1').s, at('day1').e + .8, 'Day 1.'], [at('limit').s + 3, at('limit').e + .3, 'Grids past their limits.']],
    shots: [[0, 'wide'], [at('dark').s + 3, 'group'], [at('inside').s - .2, 'quay'], [at('driver').s - .2, 'road'], [at('grid').s - .2, 'wide'],
            [at('out').s - .2, 'north'], [offB + 1.2, 'wide'], [at('walk').s - .2, 'pov-walk'],
            [at('fall').s - .2, 'quay'], [at('river').s - .2, 'under'], [at('danger').s - .2, 'wide']],
    beats: { lookUp: at('driver').s, shelter: at('inside').s, carsStop: at('inside').s, driver: at('inside').s + 1, powerOff: [offA, offB],
             climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { hiss: -60, ice: -60, steps: [[at('walk').s, at('fall').s - .3]], heartbeat: [at('limit').s, climax + 2], riser: [at('limit').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
