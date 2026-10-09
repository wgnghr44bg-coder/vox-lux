// What if you were trapped inside the Colosseum for one day? Chapter 1: DAWN – the street, the gates, the bowl fills.
export const topic = {
  number: 860, slug: 'colosseum-1-dawn', place: 'colosseum', force: 'day', wide: true,
  question: 'What if you were trapped inside the Colosseum for one day?',
  title: 'Trapped inside<br>the Colosseum',
};

export const lines = [
  ['imagine', 'Imagine opening your eyes… and the year is 80 AD.', 'long'],
  ['street', 'You are standing in a narrow street in Rome. The Sun is not even up yet.', 'pause'],
  ['walking', 'But the street is already full. Thousands of people, all walking in the same direction.', 'long'],
  ['not', 'Not to the market. Not to the temple.', 'pause'],
  ['there', 'To the largest building the Roman world has ever seen.', 'long'],
  ['name', 'The Flavian Amphitheatre. Today, we call it the Colosseum.', 'pause'],
  ['size', 'Forty-eight metres high. Built in about ten years. Room for around fifty thousand people.', 'long'],
  ['gates', 'At ground level it has eighty arches. Seventy-six of them are numbered, so every visitor can find the way to their seat.', 'pause'],
  ['token', 'Someone presses a small clay token into your hand. Gate twenty-three.', 'pause'],
  ['games', 'Today, the emperor Titus opens the games. They will go on for one hundred days.', 'long'],
  ['arch', 'You walk through the arch.', 5],
  ['voices', 'Fifty thousand voices, inside a single ring of stone.', 'pause'],
  ['out', 'And once the games begin… there is no easy way out.', 'none'],
];

const clock = h => { const m = Math.round(h * 60); return `DAWN — ${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };

export default function (at) {
  const climax = at('arch').e + .3, reveal = climax + 2.6, T_END = at('out').e + 1.6;
  const hours = [[0, 5.72], [at('gates').s, 6.05], [climax, 6.3], [T_END, 6.5]];
  const subAt = []; for (let t = 0; t <= T_END; t += .5) { let h = hours[0][1]; for (let i = 0; i < hours.length - 1; i++) if (t >= hours[i][0]) h = hours[i][1] + (hours[i + 1][1] - hours[i][1]) * Math.min(1, (t - hours[i][0]) / (hours[i + 1][0] - hours[i][0])); subAt.push([t, clock(h)]); }
  const fill = [[0, .04], [at('name').s, .1], [at('gates').s, .22], [climax, .62], [reveal + 1, .86], [T_END, .92]];
  return {
    T_END, tripod: true, brand: false, showTitle: true, post: true, gateBay: 24, streamStart: 0,
    titleOut: at('imagine').e + .6,
    forceParams: { hours },
    crowd: { fill, stand: [[0, 0], [reveal, 0], [reveal + 3, .15]], cheer: [[0, 0], [reveal, .1], [T_END, .2]] },
    velarium: [[0, 0]],
    groups: [{ gate: [7, 3], n: 7, spread: 2, shot: { name: 'group', from: [3.5, 1.5, 5], fov: 46 } }],
    hud: { label: 'CROWD INSIDE', unit: '', decimals: 0, sub: clock(5.72), subAt },
    counter: fill.map(([t, f]) => [t, Math.round(f * 50000 / 100) * 100]),
    range: [0, 50000],
    captions: [[at('imagine').s + 2, at('imagine').e + 1.2, '80 AD'], [at('size').s, at('size').e, '48 m · 50,000 people'], [at('token').s + 2.5, at('token').e + 1, 'Gate XXIII']],
    shots: [[0, 'aerial'], [at('street').s - .2, 'street'], [at('walking').s + 1.5, 'rooftop'], [at('not').s - .2, 'pov-street'],
            [at('name').s - .2, 'square'], [at('size').s - .2, 'facade'], [at('gates').s + 1, 'gate'], [at('token').s - .2, 'group'],
            [at('games').s - .2, 'attic'], [at('arch').s - .3, 'pov-gate'], [reveal, 'reveal'], [at('voices').e + .4, 'bowl']],
    beats: { lookUp: at('there').s, shelter: at('games').s, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('games').s, climax], riser: [at('arch').s - 1, reveal] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if you were trapped inside the Colosseum for one day?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
