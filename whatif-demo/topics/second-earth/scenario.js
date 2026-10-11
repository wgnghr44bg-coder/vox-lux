// What if a second Earth appeared in the sky?  (Short #45, stijl A – POV; script in the style of Alteraqon "sky countdown")
// Place: mountain village by the lake, force 'day' (the clock drives the light), TL.moon.earth = a twin Earth at the Moon's distance.
// Physics: Earth 12,742 km vs Moon 3,474 km wide -> 3.7× as wide at the same distance; 13.5× the area and ~3× the reflectivity
// -> more than 30× the light of a full Moon; 81× the Moon's mass -> 81× its (tidal) pull; ocean tides of ~0.5 m -> tens of metres;
// the solid-Earth tide (a few dm today) -> many metres, but the whole region moves together, so you feel nothing.
// Two Earths at 384,400 km circle each other in ~19 days -> full on night 1, a thin crescent ~9 days later.
// New climax (not used before): city lights appearing on the night side of the twin.
export const topic = {
  number: 45, slug: 'second-earth', place: 'mountain-village', force: 'day', padSilence: true,
  question: 'What if a second Earth appeared in the sky?',
  title: 'What if a second Earth<br>appeared in the sky?',
};

export const lines = [
  ['imagine', 'Imagine… you look up, and there is a second Earth in the sky.', 'pause'],
  ['blue', 'Blue oceans. White clouds. Hanging right where the Moon should be.', 'pause'],
  ['nobody', 'And nobody knows… where it came from.', 'long'],
  ['sunset', 'It starts on an ordinary evening. Just after sunset, a planet rises over the mountains.', 'pause'],
  ['wide', 'It is as far away as the Moon. But it looks almost four times as wide.', 'long'],
  ['night', 'Night one. The sky never gets dark.', 'pause'],
  ['light', 'This Earth reflects more than thirty times as much light as a full Moon. Your shadow lies sharp on the snow.', 'pause'],
  ['world', 'Within an hour, half the planet is outside, looking up.', 'long'],
  ['problem', 'But here’s the first problem. It is eighty-one times heavier than the Moon.', 'pause'],
  ['tides', 'Day two. Its pull drags the oceans. On the coasts, the tides would rise tens of metres. Twice a day.', 'pause'],
  ['rock', 'Even the rock under your feet rises and falls, by many metres. You just can’t feel it.', 'long'],
  ['day9', 'Day nine. At dusk, the other Earth is only a thin crescent.', 'pause'],
  ['side', 'Its night side is facing you.', 3],
  ['lights', 'And across the darkness… tiny lights appear.', 'long'],
  ['cities', 'Cities.', 'long'],
  ['twist', 'And here’s the twist. Somewhere up there, someone is standing by a lake… looking up. At you.', 'long'],
  ['ask', 'If you could send them one message… what would you say?', 'none'],
];

const EAST = [.7, .55, -.45], WEST = [-.074, .53, -.845];
const toward = (pos, d, fov, el = 0, drift = [0, 0, 0]) => {
  const n = Math.hypot(...d), v = d.map(x => x / n);
  return { pos, look: [pos[0] + v[0] * 1000, pos[1] + (v[1] + el) * 1000, pos[2] + v[2] * 1000], drift, fov };
};

export default function (at) {
  const T_END = at('ask').e + 3.4, d9 = at('day9').s - .3, n1 = at('night').s - .3, d2 = at('tides').s - .3;
  const climax = at('side').e + .2;
  return {
    T_END, tripod: true,
    forceParams: { sunset: 19.6, hours: [[0, 19.7], [n1 - .01, 20.05], [n1, 23], [d2 - .01, 23.4], [d2, 12.5], [d9 - .01, 13], [d9, 19.95], [T_END, 20.3]] },
    moon: { km: [[0, 384400]], dirs: [[0, EAST], [d9, WEST]], halo: .5,
            earth: { phase: [[0, 0], [d2 - .01, 0], [d2, .5], [d9 - .01, .5], [d9, .7], [T_END, .72]],
                     stars: [[0, 0], [n1 - .01, 0], [n1, 1], [at('problem').s - .01, 1], [at('problem').s, 0], [d2, 1], [at('day9').e, 1], [at('day9').e + .01, 0], [at('twist').s + 1.3, 0], [at('twist').s + 1.4, 1]],
                     lights: [[0, 0], [at('side').s + .6, 0], [climax + .4, .55], [at('cities').s, 1], [T_END, 1]] },
            earthLight: [[0, 0], [n1 - .01, .2], [n1, 1], [d2, 1], [d9, .12], [T_END, .1]] },
    hud: { label: 'BRIGHTER THAN A FULL MOON', prefix: '×', decimals: 0, sub: 'EVENING',
           subAt: [[n1, 'NIGHT 1'], [d2, 'DAY 2'], [d9, 'DAY 9']],
           second: { label: 'PULL vs THE MOON', prefix: '×', fn: () => 81, decimals: 0, showAt: at('problem').s + 1.8 } },
    counter: [[0, 1], [at('light').s, 1], [at('light').s + 2.8, 33], [d9 - .01, 33], [d9, 2], [T_END, 2]], range: [1, 33],
    groups: [{ at: [4, 8], n: 7, face: -1.05, lampPower: 25 }, { at: [-34.6, -62], n: 1, spread: .1, face: 2.5, lamp: false }],
    extraShots: {
      'earth-tele': toward([12, 2, 30], EAST, 9, -.012),
      'earth-close': toward([12, 2, 30], EAST, 4.2),
      'earth-mid': toward([12, 2, 30], EAST, 34, -.17, [0, .3, 0]),
      'pov-earth': toward([12, 1.65, 12], EAST, 66, -.2, [.6, 0, -.6]),
      'crowd-up': toward([-3, 1.5, 12], EAST, 58, -.3),
      'earth-day': toward([12, 2, 30], EAST, 30, -.12),
      'lake-dusk': toward([-34, 2.5, -55], WEST, 52, -.12, [-.8, 0, -.6]),
      'crescent-tele': toward([-34, 2.5, -55], WEST, 7.5),
      'crescent-close': toward([-34, 2.5, -55], WEST, 3.4),
      'shore': toward([-34, 1.75, -55], WEST, 46, -.25),
    },
    captions: [[at('wide').s + 1.8, at('wide').e + .4, '3.7× as wide as the Moon'],
               [at('tides').s + 2, at('tides').e + .3, 'Tides: tens of metres']],
    shots: [[0, 'earth-tele'], [at('blue').s, 'earth-close'], [at('nobody').s, 'crowd-up'], [at('sunset').s, 'earth-mid'],
            [at('wide').s, 'pov-earth'], [n1, 'wide'], [at('light').s + 2.5, 'pov-earth'], [at('world').s, 'crowd-up'],
            [at('problem').s, 'earth-tele'], [d2, 'earth-day'], [at('rock').s, 'vast'],
            [d9, 'lake-dusk'], [at('side').s - .2, 'crescent-tele'], [at('cities').s - .1, 'crescent-close'],
            [at('twist').s + 1.4, 'shore'], [at('ask').s, 'lake-dusk']],
    beats: { lookUp: at('nobody').s - .8, brand: at('rock').s + .6, falls: [], climax, stop: T_END + 1, dark: 1e9, end: 1e9, fade: at('ask').e + .4 },
    audio: { heartbeat: [at('day9').s, climax + 1], riser: [at('side').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = {
  stijl: 'A-pov',
  title: 'What if a second Earth appeared in the sky? 🌍 #shorts',
  description: 'One evening, a second Earth rises over the mountains, right where the Moon should be. What would it do to our nights, our oceans… and to us?\n\n' +
    'What would you say to them? 👇\n\n#whatif #space #earth #shorts',
  tags: ['what if', 'second earth', 'what if a second earth appeared in the sky', 'science'],
  tiktok: 'POV: a second Earth rises over the mountains 🌍 And then you see its city lights… What would you say to them? #whatif #space #earth #fyp',
};
