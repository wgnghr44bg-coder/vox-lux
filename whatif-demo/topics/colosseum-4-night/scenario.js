// Trapped inside the Colosseum, chapter 4: EVENING -> NIGHT – panic at the exits, the bowl empties, night inside.
export const topic = { number: 863, slug: 'colosseum-4-night', place: 'colosseum', force: 'day', wide: true,
  question: 'What if you were trapped inside the Colosseum for one day?', title: '' };

export const lines = [
  ['climb', 'Evening. You climb back up into the stands, and walk straight into a wall of people.', 'long'],
  ['rush', 'Fifty thousand people, all trying to leave at the same time.', 'pause'],
  ['vom', 'The exits are called vomitoria. They were built to pour a full stadium into the streets, fast.', 'pause'],
  ['crush', 'But a panicking crowd can push harder than any wall was built to hold.', 'long'],
  ['grab', 'You lose your footing. Someone grabs your arm, and pulls you out of the stream.', 'long'],
  ['quiet', 'And then, slowly, it becomes quiet.', 5],
  ['night', 'Night. The stands are empty. Torches flicker along the wall.', 'pause'],
  ['gates', 'The gates are shut. The city is asleep. And you are still inside.', 'long'],
  ['tomorrow', 'Tomorrow, it all begins again. Ninety-nine more days.', 'long'],
  ['question', 'So, tell me. Would you survive a single day?', 'none'],
];

const name = h => h < 7 ? 'DAWN' : h < 11.9 ? 'MORNING' : h < 14 ? 'NOON' : h < 18 ? 'AFTERNOON' : h < 20 ? 'EVENING' : 'NIGHT';
const clockAt = hours => t => { let h = hours[0][1]; for (let i = 0; i < hours.length - 1; i++) if (t >= hours[i][0]) h = hours[i][1] + (hours[i + 1][1] - hours[i][1]) * Math.min(1, (t - hours[i][0]) / (hours[i + 1][0] - hours[i][0]));
  const m = Math.round(h * 60); return `${name(h)} — ${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };

export default function (at) {
  const climax = at('quiet').e + .3, q0 = at('quiet').s, T_END = at('question').e + 4.5;
  const hours = [[0, 18.5], [q0, 19.2], [climax + 1, 20.1], [at('night').s, 20.8], [T_END, 21.4]], ck = clockAt(hours);
  const subAt = []; for (let t = 0; t <= T_END; t += .5) subAt.push([t, ck(t)]);
  const fill = [[0, 1], [at('crush').s, .9], [q0, .35], [climax, .04], [at('night').s, 0]];
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, gateBay: 24, panic: 0,
    forceParams: { hours },
    crowd: { fill, stand: [[0, 1], [q0, 1]], cheer: [[0, .7], [at('crush').s, 1], [q0, .4], [climax, 0]] },
    velarium: [[0, .9], [q0, .9], [at('night').s, .05]],
    hud: { label: 'CROWD INSIDE', unit: '', decimals: 0, sub: ck(0), subAt },
    counter: fill.map(([t, f]) => [t, Math.round(f * 50000 / 100) * 100]),
    range: [0, 50000],
    captions: [[at('vom').s + .5, at('vom').s + 3.5, 'Vomitoria'], [at('tomorrow').s + 1.5, at('tomorrow').e + .5, '99 more days']],
    shots: [[0, 'pov-seat'], [at('rush').s - .2, 'bowl'], [at('vom').s - .2, 'reveal'], [at('crush').s - .2, 'reveal'],
            [at('grab').s + 2, 'pov-up'], [q0 - .2, 'bowl'], [at('night').s - .2, 'arena'], [at('gates').s - .2, 'gate'],
            [at('gates').s + 3.6, 'arena-up'], [at('tomorrow').s - .2, 'night']],
    beats: { climax, falls: [], stop: T_END + 1 },
    audio: { crowd: [[0, 1], [at('crush').s, 1], [q0, .5], [climax, .03], [T_END, 0]], roars: [[.5, .8], [at('crush').s + .5, 1]],
             heartbeat: [at('crush').s, at('grab').e], riser: [at('crush').s, at('grab').e] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: 'What if you were trapped inside the Colosseum for one day?', description: '', tags: [], tiktok: '' };
