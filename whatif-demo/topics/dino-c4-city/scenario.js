// What if dinosaurs never went extinct? Chapter 4: the city at night (23:50 -> 06:00), the T. rex walks down the avenue.
export const topic = {
  number: 434, slug: 'dino-c4-city', place: 'street', force: 'calm', wide: true, padSilence: true,
  question: 'What if dinosaurs never went extinct?',
};

export const lines = [
  ['night', 'Twenty-three fifty. [pause] Ten kilometres away, the city is asleep.', 'long'],
  ['alert', 'Then every phone buzzes at once. [pause] Emergency alert. [pause] Stay inside.', 'pause'],
  ['two', 'Two hundred metres. [pause] You don\'t see it yet. [pause] You feel it.', 'long'],
  ['print', 'A T. rex footprint was almost a metre long. [pause] Every step would send a small shock through the ground… and the puddles start to ripple.', 'pause'],
  ['fifty', 'Fifty metres. [pause] Car alarms go off, one by one.', 'long'],
  ['three', 'Three metres.', 3],
  ['smell', 'It may smell you, more than it sees you. [pause] Its sense of smell was one of the best of any dinosaur.', 'pause'],
  ['walks', 'And then… it simply walks on.', 'long'],
  ['six', 'Six o\'clock. [pause] Sunrise. [pause] Only its footprints are left in the street.', 'pause'],
  ['rock', 'For sixty-six million years, one rock decided who would rule this planet.', 'long'],
  ['question', 'So tell me… if that rock had missed, do you think we would ever have stood a chance?', 'none'],
];

export default function (at) {
  const T_END = at('question').e + 4.5, climax = at('three').e + .2, th = at('three').s, six = at('six').s;
  const alarms = [0, 1, 2, 3].map(k => ({ t: at('fifty').s + 1.6 + k * .7, kind: 'caralarm', e: 1 - k * .15, x: [-7, 7, -2.5, 2.5][k], z: [-30, -10, 5, 20][k], dur: 9 }));
  return {
    T_END, tripod: true, brand: false, post: true, nightExposure: 2, endStyle: 'card',
    time: { hour: 23.83, doy: 160, days: [[0, 0], [six - 1.2, (six - 1.2) / 86400], [six + 1.5, .255], [T_END, .256]], clouds: .4 },
    extraShots: {
      'puddle-pov': { pos: [3.6, 1.55, 33], look: [2.2, 0, 29.5], drift: [0, 0, 0], fov: 62 },
      'by-car': { pos: [3.4, 1.15, 16], look: [-.5, 3.8, 4], drift: [0, 0, 0], fov: 66, hand: true },
      'phone': { pos: [12.5, 1.6, 10], look: [14, 1.7, -6], drift: [0, 0, -.4], fov: 50 },
    },
    groups: [-60, -30, -5, 14, 34].map((z, i) => ({ at: [i % 2 ? 6 : -6, z], n: 0, lamp: true, lampPower: 140, lampAt: [0, 0] })),   // street lights that light the T. rex
    puddles: [[2.2, 29.5, 1.4], [-3, 18, 1.8]],
    hud: { label: 'NEAREST DINOSAUR', unit: ' M', decimals: 0, sub: 'TONIGHT — 23:50',
           subAt: [[0, 'TONIGHT — 23:50'], [six, 'TOMORROW — 06:00']] },
    counter: [[0, 10000], [at('two').s - .2, 10000], [at('two').s + 1, 200], [at('fifty').s - .2, 130], [at('fifty').s + 1, 50], [th - .2, 40], [th + .8, 3],
              [at('walks').s + 2, 3], [at('walks').e + 2, 60], [six, 900], [T_END, 900]], range: [10000, 0],
    captions: [[at('alert').s + 1.5, at('alert').e + 1, 'EMERGENCY ALERT · STAY INSIDE'], [at('print').s + .3, at('print').s + 4, 'Footprint · ± 0.9 m']],
    animals: [
      { kind: 'trex', path: [[0, -1, -260], [at('two').s, -1, -120], [at('fifty').s, .5, -15], [th, 0, 9], [climax + 3, 0, 13], [at('walks').e + 4, -.5, 60], [six - 1.2, -1, 140]],
        look: [[th - 1, [3.4, 1.2, 16]], [at('walks').s, null]], roar: [at('fifty').e + .3], prints: true, loud: 1.2 },
    ],
    events: alarms,
    shots: [[0, 'high'], [at('alert').s - .2, 'phone'], [at('two').s - .2, 'avenue'], [at('print').s + 2.5, 'puddle-pov'], [at('fifty').s - .2, 'crossing'],
            [th - .2, 'by-car'], [at('walks').s - .2, 'balcony'], [six - .2, 'high'], [at('rock').s - .2, 'wide']],
    beats: { lookUp: 1e9, shelter: at('alert').s + .5, carsStop: at('alert').s, climax, falls: [], stop: T_END, dark: at('question').e + .5, end: at('question').e + 1, fade: 1e9 },
    audio: { heartbeat: [at('two').s, climax + 1], riser: [at('fifty').s, climax] },
    end: { title: 'What if dinosaurs<br>never went extinct?', lines: 'IFSCAPE3D' },
  };
}

export const upload = { title: 'What if dinosaurs never went extinct?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
