// What if the Sun went out? Long video (owner's script), chapter 1: the beach, day 0, 00:00 -> 08:20.
export const topic = {
  number: 411, slug: 'sun-c1-beach', place: 'boulevard', force: 'cold', wide: true,
  question: 'What if the Sun went out?',
  title: 'What if<br>the Sun<br>went out?',
};

export const lines = [
  ['wake', 'Imagine waking up tomorrow, and the Sun is gone.', 'long'],
  ['notexp', 'Not exploding. Not slowly disappearing.', 'pause'],
  ['gone', 'Just gone.', 'long'],
  ['terr', "But here's the terrifying part.", 'pause'],
  ['notice', "You wouldn't notice immediately.", 'pause'],
  ['light', 'Because sunlight takes about eight minutes and twenty seconds to reach Earth.', 'pause'],
  ['normal', 'So for those final eight minutes, everything would look completely normal.', 'long'],
  ['birds', 'The birds are still singing. Cars are still driving. People are going about their day.', 'long'],
  ['then', 'Then.', 5],
  ['dark', 'Darkness.', 'long'],
  ['last', 'The last sunlight disappears.', 'pause'],
  ['flying', 'And suddenly, Earth is flying through space without its Sun.', 'none'],
];

const clock = s => { s = Math.round(s); return `DAY 0 — 00:${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`; };

export default function (at) {
  const t0 = at('notice').s, climax = at('then').e + 1.2, dark = climax + 3.5, T_END = at('flying').e + 3.2;
  const subAt = [];
  for (let t = 0; t <= climax; t += .25) subAt.push([t, clock(t < t0 ? 0 : 500 * Math.min(1, (t - t0) / (climax - t0)))]);
  return {
    T_END, tripod: true, brand: false, showTitle: true,
    titleOut: at('gone').e + .3,
    sunOffset: [-15, 42, -200],
    hud: { label: 'DAYLIGHT', unit: '%', decimals: 0, sub: clock(0), subAt },
    counter: [[0, 100], [climax, 100], [climax + 1.5, 60], [dark, 0], [T_END, 0]],
    range: [100, 0], forceParams: { darkAt: [0, 1], frostAt: [2, 3], snow: 0 },
    captions: [[at('light').s, at('light').e + .4, '8 min 20 s.'], [at('dark').s, at('dark').e + .6, 'Darkness.']],
    shots: [[0, 'boulevard'], [at('notexp').s - .2, 'sea'], [at('terr').s - .2, 'beach'], [at('light').s - .2, 'sea'],
            [at('normal').s - .2, 'wide'], [at('birds').s - .2, 'boulevard'], [at('then').s - .2, 'sea'],
            [climax + 2.6, 'wide'], [at('last').s - .2, 'beach'], [at('flying').s - .2, 'sea']],
    beats: { lookUp: climax + .5, shelter: 1e9, carsStop: 1e9, climax, falls: [], stop: T_END + 1 },
    audio: { heartbeat: [at('normal').s, climax + 2], riser: [at('birds').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 1, niet los uploaden.', tags: [], tiktok: '' };
