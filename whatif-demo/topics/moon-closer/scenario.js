// What if the Moon moved toward Earth?  (onderwerpen.md #44, Short, stijl A – POV)
// Based on topics/gravity-doubled + moon-c1-harbor. Beach boulevard by day, force tide, TL.moon at true size.
// Physics: tidal pull grows with 1/distance³ (1/2 → 8×, 1/3 → 27×, 1/4 → 64×); apparent width with 1/distance.
// Other climax than the long Moon video (harbour, ring): the sea pulls back, then floods the boulevard.
export const topic = {
  number: 44, slug: 'moon-closer', place: 'boulevard', force: 'tide', padSilence: true,
  question: 'What if the Moon moved toward Earth?',
  title: 'What if the Moon<br>moved toward Earth?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['imagine', 'Imagine the Moon moved toward Earth.', 'long'],
  ['beach', 'You are on the beach on a calm afternoon. The Moon is a pale disc above the sea.', 'pause'],
  ['pull', 'Its pull lifts the oceans twice a day. Here, the tide rises about one metre.', 'long'],
  ['rule', 'But that pull grows fast. Halve the distance, and it becomes eight times stronger.', 'long'],
  ['half', 'Half the distance. One hundred and ninety-two thousand kilometres.', 'pause'],
  ['wide', 'The Moon looks twice as wide. And the sea comes in, fast.', 'pause'],
  ['wall', 'High tide climbs the whole beach, all the way to the sea wall.', 'long'],
  ['third', 'One third of the distance. Twenty-seven times the pull.', 'pause'],
  ['back', 'Now the sea pulls back. Hundreds of metres. The sea floor lies bare.', 'long'],
  ['quarter', 'One quarter. Sixty-four times stronger.', 'pause'],
  ['comes', 'And then the water comes back…', 5],
  ['over', '…over the beach, over the boulevard, up to the doors of the hotels.', 'long'],
  ['sky', 'Above it all, the Moon is now four times as wide as today.', 'pause'],
  ['still', 'And it is still getting closer.', 'long'],
  ['ask', 'Where would you go?', 'none'],
];

export default function (at) {
  const T_END = at('ask').e + 3.4, climax = at('comes').e + .2;
  const km = [[0, 384400], [at('half').s - .3, 384400], [at('half').e + .3, 192000], [at('third').s - .3, 192000],
              [at('third').s + 1.6, 128133], [at('quarter').s - .3, 128133], [at('quarter').s + 1.4, 96100],
              [at('still').s, 96100], [T_END, 92000]];
  const p = at('pull'), w = at('wide'), b = at('back');
  return {
    T_END, tripod: true,
    moon: { km, dir: [-.1, .17, -.98] },
    hud: { label: 'MOON DISTANCE', unit: ' km', decimals: 0,
           second: { label: 'TIDAL PULL', prefix: '×', fn: v => (384400 / v) ** 3, decimals: 0, showAt: at('rule').s } },
    counter: km, range: [384400, 92000],
    forceParams: { calm: 2.6, top: 4.8, tide: [
      [0, -.2], [p.s + .5, -.2], [p.e, .8], [at('rule').e, .4], [w.s + .6, .4], [at('wall').e, 2.5],
      [at('third').e, 2.2], [b.s + .4, 1.6], [b.e + .5, -6], [climax - 5.6, -6.3],
      [climax + 1.2, 4.6], [at('over').e, 4.4], [at('sky').e + 1, 3.9], [T_END, 3.5]] },
    extraShots: {
      'moon-tele': { pos: [0, 20, 95], look: [-30, 46, -202], drift: [0, 0, 0], fov: 24 },   // the Moon over the sea, close up
      'moon-wide': { pos: [-40, 22, 90], look: [-70, 22, -210], drift: [1.5, 0, 0], fov: 50 },  // beach, sea and the Moon
      'pov-shore': { pos: [40, 2.3, 8], look: [10, 17, -292], drift: [0, 0, -.4], fov: 62 },   // at the waterline
      'pov-high': { pos: [2, 15.8, 88.3], look: [-2, 2, -60], drift: [0, 0, 0], fov: 62 },     // from a hotel balcony
    },
    captions: [[at('rule').s + 1.6, at('rule').e + .5, 'Half the distance → 8× the pull'],
               [at('half').s, at('half').e + .4, '192,000 km'],
               [at('third').s, at('third').e + .4, '27× the pull'],
               [at('quarter').s, at('quarter').e + .4, '64× stronger']],
    shots: [[0, 'moon-wide'], [at('beach').s, 'pov-shore'], [p.s, 'pov-beach'], [at('rule').s, 'sea'],
            [at('half').s, 'moon-tele'], [w.s + 2, 'wide'], [at('wall').s, 'pov-run'], [at('third').s, 'moon-tele'],
            [b.s, 'sea'], [at('quarter').s, 'wide'], [climax - 2.6, 'pov-high'], [climax + 1.4, 'wide'],
            [at('over').s + 1.6, 'hotels'], [at('sky').s, 'moon-tele'], [at('still').s, 'moon-wide']],
    beats: {
      brand: p.s + .6, lookUp: at('half').s, shelter: w.s, carsStop: b.s,
      falls: [], climax, stop: T_END + 1, dark: 1e9, end: 1e9, fade: at('ask').e + .4,
    },
    audio: { heartbeat: [at('quarter').s, climax + 2], riser: [b.s, at('comes').e] },
    end: { title: '', lines: '' },
  };
}

export const upload = {
  stijl: 'A-pov',
  title: 'What if the Moon moved toward Earth? #shorts',
  description: 'POV: you are on the beach while the Moon creeps closer to Earth.\n\n' +
    'The facts: the Moon is about 384,400 km away. Its tidal pull grows with the cube of how close it is: ' +
    'at half the distance the tides would be about 8 times stronger, at a third 27 times, at a quarter 64 times. ' +
    'At a quarter of the distance the Moon would also look four times as wide in the sky.\n\n' +
    '#whatif #moon #space #science #physics #shorts',
  tags: ['what if', 'moon', 'what if the moon moved closer', 'tides', 'tidal force', 'space', 'science', 'physics', 'shorts', 'hypothetical'],
  tiktok: 'POV: the Moon moves toward Earth 🌕 Half the distance means 8× the tides, a quarter means 64×. Where would you go? #whatif #moon #space #science #fyp',
};
