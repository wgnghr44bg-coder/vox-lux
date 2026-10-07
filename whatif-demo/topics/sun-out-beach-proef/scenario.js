// What if the Sun went out? Long video, new version (gravity style, observer shots). Chapter 1 proof: the beach.
export const topic = {
  number: 401, slug: 'sun-out-beach-proef', place: 'boulevard', force: 'cold', wide: true,
  question: 'What if the Sun went out?',
  title: 'What if<br>the Sun<br>went out?',
};

export const lines = [
  ['intro', 'Imagine a long beach on a summer afternoon.', 'pause'],
  ['waves', 'Waves roll in. Umbrellas lean in the breeze. The sand is almost too hot to walk on.', 'pause'],
  ['watts', 'Right now, every square meter of this beach receives about a thousand watts of sunlight.', 'pause'],
  ['star', 'All of it comes from one star, a hundred and fifty million kilometers away.', 'long'],
  ['now', 'Now imagine that, without any warning, the Sun goes out.', 'long'],
  ['nothing', 'Down here, nothing would change. Not yet.', 'pause'],
  ['light', 'Light needs eight minutes and twenty seconds to cross that distance.', 'pause'],
  ['onway', 'So the sunshine on this beach is already on its way.', 'long'],
  ['sparkle', 'For eight minutes, the sea would keep sparkling, and nobody would know.', 'long'],
  ['last', 'Then the last light would land.', 6],
  ['night', 'In a few seconds, the afternoon would turn into night.', 'pause'],
  ['stars', 'Stars would appear over the sea, in the middle of the day.', 'long'],
  ['sand', 'And the sand would slowly begin to give up its heat.', 'none'],
];

export default function (at) {
  const climax = at('last').e + .4, dark = climax + 4.5, T_END = at('sand').e + 3.5;
  return {
    T_END, tripod: true, showTitle: true, showTitle: true, showTitle: true, brand: false, endStyle: 'black',
    titleOut: at('waves').e + .2,
    sunOffset: [-15, 42, -200],
    hud: { label: 'DAYLIGHT', unit: '%', decimals: 0 },
    counter: [[0, 100], [climax, 100], [climax + 1.5, 60], [dark, 0], [T_END, 0]],
    range: [100, 0], forceParams: { darkAt: [0, 1], frostAt: [2, 3], snow: 0 },
    captions: [[at('watts').s, at('watts').e + .4, '1,000 watts per m².'],
               [at('star').s, at('star').e + .6, '150 million km away.'],
               [at('light').s, at('light').e + .4, '8 min 20 s.'],
               [at('stars').s, at('stars').e + .6, 'Stars at noon.']],
    shots: [[0, 'boulevard'], [at('waves').s - .2, 'beach'], [at('watts').s - .2, 'sea'], [at('star').s - .2, 'wide'],
            [at('now').s - .2, 'sea'], [at('nothing').s - .2, 'boulevard'], [at('light').s - .2, 'hotels'],
            [at('onway').s - .2, 'beach'], [at('sparkle').s - .2, 'wide'],
            [at('last').s - .2, 'sea'], [climax + 2.6, 'wide'], [at('night').s - .2, 'hotels'],
            [at('stars').s - .2, 'sea'], [at('sand').s - .2, 'beach']],
    beats: { lookUp: climax + .5, shelter: at('sand').s, carsStop: 1e9, climax, falls: [], stop: T_END + 1 },
    audio: { heartbeat: [at('sparkle').s, climax + 2], riser: [at('sparkle').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Proef, niet uploaden.', tags: [], tiktok: '' };
