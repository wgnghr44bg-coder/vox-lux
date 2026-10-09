// Imagine the Sun went out (owner's shot list). Chapter 4: the mountain village, day 30, the last light.
export const topic = {
  number: 424, slug: 'sun-d4-village', place: 'mountain-village', force: 'cold', wide: true, voOffset: 1.5,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['month', 'After one month, the Earth is no longer simply cold.', 'pause'],
  ['frozen', 'It is becoming frozen.', 'long'],
  ['lake', 'The lake beside this village has frozen over. Ice floats, so it seals the water underneath like a lid.', 'pause'],
  ['nolight', 'There is no light here anymore. The power went out weeks ago.', 'long'],
  ['clock', 'The church clock still keeps time.', 'long'],
  ['noone', 'But no one is outside to hear it.', 'long'],
  ['walk', 'Out here, the air is so cold that it hurts to breathe.', 'pause'],
  ['minus', 'Minus thirty, and still falling.', 'long'],
  ['strange', 'And the strangest part...', 'long'],
  ['stars', 'The stars would be brighter than you have ever seen them.', 'pause'],
  ['why', 'No sunlight. No moonlight. No city glow. Nothing left to hide them.', 'long'],
  ['because', 'Because without the Sun...', 'long'],
  ['world', 'Earth would no longer be a world of light.', 'long'],
  ['beginning', 'And this would only be the beginning.', 'none'],
];

export default function (at) {
  const T_END = at('beginning').e + 4.8;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', decimals: 0, sub: 'DAY 30',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 },
           subAt: [[0, 'DAY 30'], [at('world').s, '30 DAYS — NO SUNLIGHT']] },
    counter: [[0, -27], [at('minus').s, -30], [at('world').e, -33], [T_END, -33]],
    range: [0, -40], forceParams: { darkAt: [-1, 0], frostAt: [.2, .5], snow: 0, breath: [[at('walk').s - .2, at('strange').s - .2]] },
    captions: [[at('month').s, at('month').e + .5, 'Day 30.'], [at('lake').s + 2, at('lake').e + .3, 'Frozen from the top down.']],
    shots: [[0, 'wide'], [at('lake').s - .2, 'lake'], [at('nolight').s - .2, 'wide'], [at('clock').s - .2, 'wide'],
            [at('noone').s - .2, 'mountains'], [at('walk').s - .2, 'pov-walk'], [at('strange').s - .2, 'pov-up'],
            [at('because').s - .2, 'vast']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, powerOut: -1, climax: 1e9, falls: [],
             stop: at('beginning').s - .6, dark: at('beginning').s - .3, end: at('beginning').e + .6, fade: 1e9 },
    audio: { hiss: -60, ice: -60, steps: [[at('walk').s, at('strange').s - .6]], bell: [at('clock').e + .1, at('clock').e + 2.6] },
    end: { title: 'What if the Sun<br>never came back?', lines: 'IFSCAPE3D' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
