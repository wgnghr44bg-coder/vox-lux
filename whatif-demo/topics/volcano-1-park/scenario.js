// What if a supervolcano erupted? Long video (16:9), chapter 1: the warning. Nature park, 15 km from the caldera.
// Bricks: place nature-park, force quake (tremors, cracks, steam), alarm (siren pole, roadblock).
export const topic = {
  number: 3501, slug: 'volcano-1-park', place: 'nature-park', force: 'quake', wide: true, voOffset: 2.5, padSilence: true,
  question: 'What if a supervolcano erupted?', title: '',
};

export const lines = [
  ['imagine', 'Imagine a supervolcano erupted.', 'long'],
  ['not', 'Not a mountain with a peak.', 'pause'],
  ['not2', 'Not a slow river of lava.', 'pause'],
  ['crater', 'A crater so wide, you could drive across it for almost an hour… without knowing you were inside.', 'long'],
  ['watch', 'But here is what keeps scientists watching it.', 'pause'],
  ['chamber', 'Beneath it lies a chamber of hot, partly molten rock big enough to fill the Grand Canyon more than twice.', 'long'],
  ['before', 'And it has exploded before.', 'pause'],
  ['times', 'Three times.', 'long'],
  ['three', 'Three days before.', 'long'],
  ['tremble', 'The ground would start to tremble.', 'pause'],
  ['hundreds', 'Not once… hundreds of times a day.', 'pause'],
  ['rising', 'Rising magma could push the earth upwards, tilting roads until they crack open.', 'long'],
  ['oneday', 'One day before.', 'long'],
  ['steam', 'Steam and boiling water would burst out of the ground where yesterday there were only trees.', 'pause'],
  ['sirens', 'Sirens.', 'pause'],
  ['full', 'Every road out of the park is full.', 3],
  ['stops', 'Then, for a moment, the shaking stops.', 'pause'],
  ['pressure', 'But deep below, the pressure is still rising.', 'none'],
];

export default function (at) {
  const T_END = at('pressure').e + 1.6;
  const tre = at('tremble'), ris = at('rising'), sir = at('sirens'), climax = at('full').e + .3;
  const tremors = [
    [tre.s + .3, .22, 2.2], [at('hundreds').s + .2, .3, 2.4], [at('hundreds').e - .4, .36, 2.6],
    [ris.s + 1, .52, 3.4],                                            // the road cracks open
    [at('steam').s + 1.5, .4, 2.6],
    [sir.s + .4, .6, 2.8],
    [climax, .9, (at('stops').s - climax) + .3],                      // the big one, under the silence
  ];
  return {
    T_END, tripod: true, brand: false, showTitle: true, post: true, title: 'What if a supervolcano<br>erupted?',
    titleOut: at('imagine').e + 1.2,
    groups: [{ at: [12, -14.5], n: 6, face: Math.PI, y: .05, lamp: false, shot: { name: 'group', from: [3, 1.7, 8], fov: 50 } }],
    hud: { label: 'DISTANCE TO THE VOLCANO', unit: ' KM', decimals: 0, sub: '',
           subAt: [[0, ''], [at('three').s, '3 DAYS BEFORE'], [at('oneday').s, '1 DAY BEFORE']] },
    counter: [[0, 15], [T_END, 15]],
    forceParams: { tremors, steamAt: [at('steam').s - .5, at('steam').s + 3] },
    captions: [[at('chamber').s + 1, at('chamber').e + .3, 'Enough to fill the Grand Canyon twice.'],
               [at('hundreds').s + .5, at('hundreds').e + .3, 'Hundreds of quakes a day.']],
    shots: [[0, 'viewpoint'], [at('crater').s - .2, 'vista'], [at('chamber').s - .2, 'lake'], [at('before').s - .2, 'group'],
            [at('three').s - .2, 'lodge'], [ris.s - .2, 'road'], [ris.e + .6, 'viewpoint'],
            [at('steam').s - .2, 'lake'], [sir.s - .2, 'exit'], [climax - .3, 'tower'],
            [at('stops').s + .3, 'pov-lot'], [at('pressure').s - .2, 'vista']],
    beats: { lookUp: tre.s + .6, shelter: sir.s, evacuate: sir.s - 2, carsStop: 1e9, climax, falls: [climax + .2],
             stop: T_END + 2, fade: 1e9, end: 1e9 },
    alarm: { siren: sir.s - .3, block: sir.s - .3 },
    audio: { siren: [[sir.s - .3, T_END]], heartbeat: [at('oneday').s, climax], riser: [at('steam').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if a supervolcano erupted?', description: 'Hoofdstuk 1 (proef), niet los uploaden.', tags: [], tiktok: '' };
