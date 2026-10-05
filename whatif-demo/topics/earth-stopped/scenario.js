// What if Earth suddenly stopped rotating?  (onderwerpen.md #28; new-style remake of earth-stops/)
export const topic = {
  number: 28, slug: 'earth-stopped', place: 'street', force: 'wind',
  question: 'What if Earth suddenly stopped rotating?',
  title: 'What if<br>Earth stopped<br>spinning?',
};

export const lines = [
  ['imagine', 'Imagine the Earth stopped spinning.', 'long'],
  ['intro', 'You are standing on the equator, in a city by the sea.', 'pause'],
  ['calm', 'It is a calm, warm morning.', 'pause'],
  ['feel', 'You feel nothing.', 'pause'],
  ['speed', 'But the ground beneath your feet is moving east at one thousand and thirty-seven miles per hour.', 'pause'],
  ['all', 'So is the air. So are the oceans. So are you.', 'pause'],
  ['together', 'You never feel it, because everything moves together.', 'long'],
  ['now', 'Now imagine the Earth begins to stop.', 'pause'],
  ['slow', 'The ground slows down. The air does not.', 'long'],
  ['breeze', 'At first, it is only a breeze. Loose paper drifts across the street. People look up.', 'long'],
  ['hundred', 'Within minutes, the wind passes one hundred miles per hour. Signs shake. Palm trees bend. Cars start to slide.', 'long'],
  ['tornado', 'At three hundred miles per hour, it is stronger than the worst tornado ever measured.', 'pause'],
  ['windows', 'Windows burst. Walls crack open.', 'pause'],
  ['floors', 'Whole floors tear away from the buildings.', 'long'],
  ['keeps', 'And the ground keeps slowing.', 'pause'],
  ['five', 'Five hundred.', 'pause'],
  ['seven', 'Seven hundred.', 'pause'],
  ['sound', 'Faster than the speed of sound.', 6],
  ['still', 'Then, the planet is still.', 'long'],
  ['racing', 'The air and the oceans keep racing east.', 'pause'],
  ['survive', 'The Earth itself would survive this.', 'pause'],
  ['final', 'Almost nothing standing on it would.', 'none'],
];

export default function (at) {
  const climax = at('sound').e + .3, stop = at('still').s - .1;
  return {
    T_END: at('final').e + 2.6,
    hud: { label: "EARTH'S SPIN", sub: 'AT THE EQUATOR', unit: ' mph',
           second: { label: 'WIND', offset: 1037, scale: -1, unit: ' mph', showAt: at('now').s } },
    counter: [[0, 1037], [at('now').e, 1037], [at('slow').e, 1032], [at('breeze').e, 1000], [at('hundred').s + 2, 937],
              [at('hundred').e, 850], [at('tornado').e, 737], [at('floors').e, 640], [at('five').s, 537], [at('seven').s, 337],
              [at('sound').s, 265], [climax + 1.5, 130], [climax + 4, 30], [stop, 0]],
    range: [1037, 0], forceParams: { wind: v => 1037 - v, max: 1037, dir: [0, 1] },
    captions: [[at('feel').s, at('feel').e + 1, 'You feel nothing.'],
               [at('together').s, at('together').e + .6, 'Everything moves together.'],
               [at('slow').s, at('slow').e + .8, 'The ground slows. The air does not.'],
               [at('hundred').s, at('hundred').s + 4, 'Hurricane force.'],
               [at('tornado').s, at('tornado').e + .4, 'Worse than any tornado.'],
               [at('sound').s, at('sound').e + .8, 'Faster than sound.']],
    shots: [[0, 'avenue'], [at('all').s, 'crossing'], [at('now').s, 'avenue'], [at('breeze').s, 'pavement'],
            [at('hundred').s, 'avenue'], [at('tornado').s, 'crossing'], [at('windows').s, 'pavement'], [at('floors').s, 'avenue'],
            [at('five').s, 'avenue'], [climax + 3.5, 'sea'], [stop + 1.5, 'avenue']],
    beats: {
      redLight: [at('calm').s, at('together').e], lookUp: at('breeze').e - 1.2, shelter: at('hundred').s + 2,
      carsStop: at('hundred').s, powerOut: at('tornado').s, windows: at('windows').s, walls: at('windows').s + 1.3,
      floors: at('floors').s, climax, falls: [climax + .8, climax + 2.6, climax + 4.3], stop,
      fade: at('final').s - .2,
    },
    audio: { heartbeat: [at('breeze').s, stop], riser: [at('keeps').s, climax + .5] },
    end: { title: '', lines: '' },
  };
}

export const upload = {
  title: 'What if Earth suddenly stopped spinning?',
  description: "POV: you're standing on a city street at the equator when Earth suddenly stops spinning. 🌍\n\n" +
    'The ground stops. The air keeps moving at 1,037 mph, faster than the speed of sound.\n\n' +
    'Where would you hide? 👇\n\n' +
    '#whatif #earth #physics #shorts',
  tags: ['what if', 'what if earth stopped spinning', 'earth', 'physics', 'science', 'wind', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: "POV: Earth suddenly stops spinning 🌍 The air keeps moving at 1,037 mph. #whatif #earth #physics #fyp",
};
