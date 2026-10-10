// Trapped inside the Colosseum, chapter 3: AFTERNOON – the hypogeum under the arena, the lion, the lift.
export const topic = { number: 862, slug: 'colosseum-3-below', place: 'colosseum', force: 'day', wide: true,
  question: 'What if you were trapped inside the Colosseum for one day?', title: '' };

export const lines = [
  ['below', 'Afternoon. Six metres under the arena, the roar of the crowd becomes a dull rumble.', 'long'],
  ['maze', 'This is the hypogeum. A maze of tunnels beneath the sand, lit only by flames.', 'pause'],
  ['lifts', 'In its finished form, it would hide dozens of lifts and trapdoors, all worked by hand.', 'pause'],
  ['smell', 'The air is hot. It smells of smoke, sweat, and animals.', 'long'],
  ['bars', 'Because behind these bars… something is breathing.', 'long'],
  ['lion', 'A lion. Shipped across the sea from North Africa.', 'pause'],
  ['winch', 'Workers lean on a wooden winch. And the cage begins to rise.', 5],
  ['light', 'Above you, a trapdoor opens. Daylight pours in. And fifty thousand people roar at once.', 'pause'],
  ['gone', 'The cage is gone. Up into the arena.', 'long'],
  ['changes', 'And then, high above your head, the sound of the crowd changes.', 'pause'],
  ['panic', 'It is not cheering anymore. It is panic.', 'none'],
];

const name = h => h < 7 ? 'DAWN' : h < 11.9 ? 'MORNING' : h < 14 ? 'NOON' : h < 18 ? 'AFTERNOON' : h < 20 ? 'EVENING' : 'NIGHT';
const clockAt = hours => t => { let h = hours[0][1]; for (let i = 0; i < hours.length - 1; i++) if (t >= hours[i][0]) h = hours[i][1] + (hours[i + 1][1] - hours[i][1]) * Math.min(1, (t - hours[i][0]) / (hours[i + 1][0] - hours[i][0]));
  const m = Math.round(h * 60); return `${name(h)} — ${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };
const ZC = -250, LX = 8, LZ = ZC + 5.3;

export default function (at) {
  const climax = at('winch').e + .3, T_END = at('panic').e + 1.6, lift = [at('winch').s + .6, climax + 3.5], up = at('light').s + 1;
  const hours = [[0, 15], [T_END, 16.2]], ck = clockAt(hours);
  const subAt = []; for (let t = 0; t <= T_END; t += .5) subAt.push([t, ck(t)]);
  const pace = []; for (let t = 0; t < lift[0] - 1; t += 4.5) pace.push([t, LX, LZ - .9], [t + 2.2, LX, LZ + .9]);
  pace.push([lift[0] - .5, LX, LZ], [T_END + 2, LX, LZ]);
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, gateBay: 24, hypogeum: true, lift,
    forceParams: { hours },
    crowd: { fill: [[0, 1]], stand: [[0, .1], [up, .1], [up + .6, 1], [T_END, .9]], cheer: [[0, .15], [up + .4, 1], [T_END, .9]] },
    velarium: [[0, .92]],
    animals: [{ kind: 'lion', path: pace, act: 'look' }, { kind: 'lion', path: [[0, -6, ZC + 5.6], [T_END + 2, -6, ZC + 5.6]], act: 'sit', color: 0xb88a4e }],
    hud: { label: 'BELOW THE ARENA', unit: ' m', decimals: 1, sub: ck(0), subAt },
    counter: [[0, 0], [at('below').s + 1, 0], [at('below').e, 6], [T_END, 6]],
    range: [0, 6],
    captions: [[at('maze').s, at('maze').s + 3, 'The hypogeum']],
    shots: [[0, 'pov-hypo'], [at('maze').s - .2, 'hypo-corridor'], [at('lifts').s + 2, 'hypo-lift'], [at('smell').s - .2, 'pov-hypo'],
            [at('bars').s - .2, 'hypo-cage'], [at('winch').s - .2, 'hypo-lift'], [at('gone').s - .2, 'bowl'],
            [at('changes').s - .2, 'hypo-corridor'], [at('panic').s - .2, 'hypo-cage']],
    beats: { climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { crowd: [[0, .18], [up, .2], [up + .5, .6], [at('changes').s, .45], [at('panic').s, .8], [T_END, .8]], roars: [[up + .3, 1.4], [at('panic').s, 1]],
             lion: [at('bars').e - .6, lift[0] + 2], creak: [lift], heartbeat: [at('bars').s, climax] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: '', description: 'Hoofdstuk 3, niet los uploaden.', tags: [], tiktok: '' };
