// What if Earth lost its atmosphere for one minute?  (onderwerpen.md #43, Short, stijl B)
// Based on topics/gravity-doubled. Nature park (lookout over a mountain lake), force cold used as
// "air gone": sky fades to black with stars, the lake freezes over; the counter is air pressure.
export const topic = {
  number: 43, slug: 'atmosphere-lost', place: 'nature-park', force: 'cold', padSilence: true,
  question: 'What if Earth lost its atmosphere for one minute?',
  title: 'What if<br>Earth lost its<br>atmosphere<br>for one minute?',
};

// [id, text, pause after]  pause: 'pause' (0.5 s), 'long' (1 s) or seconds of silence (climax)
export const lines = [
  ['intro', 'Imagine you are standing at a lookout above a mountain lake, on a clear and quiet morning.', 'pause'],
  ['blanket', 'Above you lies a thin blanket of air.', 'pause'],
  ['tonnes', 'It presses on every square metre of you with the weight of ten tonnes, and you never feel it.', 'long'],
  ['now', 'Now imagine that Earth loses its atmosphere. Not forever. For one minute.', 'long'],
  ['one', 'Second one. The pressure starts to fall.', 'pause'],
  ['sky', 'The blue sky fades to black, and the stars come out in the middle of the day.', 'long'],
  ['silent', 'Then everything goes silent. Sound needs air to travel.', 'pause'],
  ['siren', 'The siren down the road is still flashing. But you hear nothing at all.', 'long'],
  ['ten', 'Second ten. The air in your lungs rushes out on its own.', 'pause'],
  ['body', 'You would have only seconds before you passed out.', 'long'],
  ['worse', 'But the strangest part is still to come.', 'long'],
  ['thirty', 'Second thirty. The pressure drops below ten hectopascals.', 'pause'],
  ['boil', 'At that point, even ice cold water boils.', 'pause'],
  ['lake', 'The whole lake bubbles, and it loses heat so fast that its surface, and the dew on every tree, freezes over.', 5],
  ['sixty', 'Second sixty. The air comes back.', 'pause'],
  ['blue', 'The sky turns blue again, and the ice slowly melts away.', 'long'],
  ['ask', 'One minute without air. Do you think you would make it?', 'none'],
];

export default function (at) {
  const climax = at('lake').e + .3, back = at('sixty').s + .3, blue = at('blue').e;
  return {
    T_END: at('ask').e + 4.6, tripod: true, showTitle: true, endStyle: 'card',
    titleOut: at('blanket').s - .1,
    hud: { label: 'AIR PRESSURE', unit: ' hPa', decimals: 0, sub: '',
           subAt: [[at('one').s, 'SECOND 1'], [at('ten').s, 'SECOND 10'], [at('thirty').s, 'SECOND 30'], [at('sixty').s, 'SECOND 60']] },
    counter: [[0, 1013], [at('one').s, 1013], [at('sky').s + 1, 420], [at('silent').s, 160], [at('ten').s, 60],
              [at('thirty').s, 12], [at('boil').s, 9], [climax, 0], [back, 0], [back + 2.5, 600], [blue, 1013]],
    range: [1013, 0], forceParams: { darkAt: [.15, 1.4], frostAt: [.988, 1], snow: 0 },
    extraShots: {
      overlook: { pos: [14, 14, -30], look: [10, -14, -330], drift: [-.6, 0, 0], fov: 55 },   // over the railing, down on the lake
      lodge: { pos: [-105, 2.3, 21], look: [-112, 2.6, 8.3], drift: [-.3, 0, 0], fov: 52 },    // by the visitor centre, the logo sign
      siren: { pos: [128, 1.8, 1], look: [150, 8.5, 9], drift: [0, 0, 0], fov: 50 },          // the siren pole against the sky
    },
    alarm: { siren: at('silent').s, block: 1e9 },
    captions: [[at('tonnes').s + .3, at('tonnes').e + .4, '10 tonnes per m².'],
               [at('now').s + .3, at('now').e + .8, 'For one minute.'],
               [at('silent').s + .2, at('silent').e + .6, 'Sound needs air.'],
               [at('boil').s, at('boil').e + .6, 'Ice cold water boils.'],
               [at('sixty').s, at('sixty').e + .6, 'The air comes back.']],
    shots: [[0, 'overlook'], [at('blanket').s, 'lodge'], [at('now').s, 'vista'], [at('one').s, 'overlook'],
            [at('siren').s, 'siren'], [at('ten').s, 'tower'], [at('worse').s, 'vista'],
            [at('thirty').s, 'lake'], [climax, 'overlook'], [at('blue').s, 'vista'], [at('ask').s, 'overlook']],
    beats: {
      brand: at('blanket').s + .4, shelter: at('silent').s, carsStop: 1e9,
      falls: [], climax, stop: blue + 1, dark: at('ask').e + 1, end: at('ask').e - .3,
    },
    audio: { hiss: -40, ice: -32, quiet: at('silent').s, heartbeat: [at('ten').s, climax], riser: [at('thirty').s, at('lake').s] },
    end: { title: 'What if Earth lost its<br>atmosphere for one minute?',
           lines: 'Black sky, total silence, a boiling lake.<br>Sixty seconds without air.' },
  };
}

export const upload = {
  stijl: 'B-gravity',
  title: 'What if Earth lost its atmosphere for one minute? #shorts',
  description: 'The air above you presses on every square metre with the weight of about ten tonnes. ' +
    'What would happen if it disappeared for just sixty seconds?\n\n' +
    'The facts: without air there is nothing to scatter sunlight, so the sky turns black and stars show in daylight. ' +
    'Sound cannot travel without air, so the world goes silent. Below roughly 10 hPa even near-freezing water boils, ' +
    'and the evaporation cools the rest so fast that the surface freezes. A person exposed to vacuum stays conscious ' +
    'for only about ten to fifteen seconds.\n\n' +
    '#whatif #science #physics #atmosphere #space #shorts',
  tags: ['what if', 'atmosphere', 'earth without air', 'vacuum', 'science', 'physics', 'space', 'what if earth lost its atmosphere', 'shorts', 'hypothetical'],
  tiktok: 'What if Earth lost its atmosphere for one minute? 🌍 Black sky, total silence and a lake that boils and freezes at the same time. Would you make it? #whatif #science #physics #space #fyp',
};
