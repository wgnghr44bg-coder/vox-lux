// What if the Sun went out? Long video (16:9), chapter 1 of 5: the street, the first 8 minutes 20 seconds.
// Build like gravity-doubled (place -> why it matters -> "Now imagine" -> facts step by step -> silent climax),
// opening with "Imagine" + title after a short silent title card (voOffset). Counter = seconds since the Sun went out;
// the light only stops at 500 s (8 min 20 s), so the darkness (cold force, darkAt) falls exactly there.
export const topic = {
  number: 201, slug: 'sun-out-1-street', place: 'street', force: 'cold', wide: true, voOffset: 3.2,
  question: 'What if the Sun went out?', title: 'What if<br>the Sun<br>went out?',
};

export const lines = [
  ['imagine', 'Imagine the Sun went out.', 'long'],
  ['street', 'It is a warm afternoon on a busy street by the sea.', 'pause'],
  ['people', 'People are out shopping. Cars wait at the lights. The palm trees move in a soft breeze.', 'pause'],
  ['power', 'All of it, the warmth, the wind, the light on every wall, comes from one star.', 'pause'],
  ['star', 'The Sun.', 'long'],
  ['feel', 'Close your eyes and you can feel it on your skin.', 'pause'],
  ['now', 'Now imagine that, at this very second, it simply goes dark.', 'long'],
  ['nothing', 'At first, nothing would happen.', 'long'],
  ['light', 'Sunlight takes eight minutes and twenty seconds to travel to Earth.', 'pause'],
  ['left', 'The light falling on this street right now left the Sun before it went out.', 'pause'],
  ['onway', 'It is still on its way.', 'long'],
  ['blue', 'The sky would stay blue. The shadows would stay sharp.', 'pause'],
  ['look', 'If you looked up, the Sun would still be there, exactly where it always is.', 'pause'],
  ['ghost', 'But it would be a ghost. An image of a star that is no longer burning.', 'long'],
  ['normal', 'So for eight minutes, everything would look completely normal.', 'pause'],
  ['nobody', 'Nobody here would know.', 'pause'],
  ['kids', 'Children would keep playing. Someone would order another coffee.', 'pause'],
  ['traffic', 'The traffic would keep moving. The shops would stay open.', 'long'],
  ['faster', 'Nothing travels faster than light, so no warning could reach us any sooner.', 'long'],
  ['last', 'But every second, the last of the sunlight is closer to running out.', 'long'],
  ['five', 'Five minutes.', 'long'],
  ['six', 'Six.', 'long'],
  ['seven', 'Seven.', 'long'],
  ['eight', 'Eight.', 'long'],
  ['then', 'And then, at eight minutes and twenty seconds,', 5],
  ['gone', 'the last light arrives. And after it, there is no more.', 'long'],
  ['moon', 'The Moon would vanish too. It only ever shone with borrowed sunlight.', 'pause'],
  ['stars', 'Above the street, the stars would come out in the middle of the afternoon.', 'long'],
  ['cold', 'And the cold would begin.', 'long'],
];

export default function (at) {
  const climax = at('then').e + .4, T_END = at('cold').e + 3.0;
  return {
    T_END, reach: 16, showTitle: true, titleOut: at('imagine').s + 1.2,
    hud: { label: 'SINCE THE SUN WENT OUT', unit: ' s',
           second: { label: 'MINUTES', fn: v => v / 60, decimals: 1, unit: '', showAt: at('now').e } },
    counter: [[0, 0], [at('now').e, 0], [at('nothing').e, 20], [at('light').s, 60], [at('normal').s, 180],
              [at('five').s, 300], [at('eight').s, 480], [climax, 500], [climax + 3, 520], [T_END, 560]],
    range: [0, 1000], forceParams: { darkAt: [.5, .52], frostAt: [5, 6], snow: 0 },
    captions: [[at('now').s + .3, at('now').e + .8, 'The Sun goes dark.'],
               [at('light').s, at('light').e + .5, '8 minutes 20 seconds.'],
               [at('onway').s, at('onway').e + .6, 'Still on its way.'],
               [at('gone').s, at('gone').e + .6, 'No more light.'],
               [at('stars').s, at('stars').e + .5, 'Stars in the afternoon.']],
    shots: [[at('blue').s, 'sea'], [at('ghost').s, 'wide'], [at('faster').s, 'avenue'], [at('six').s, 'crossing'], [at('seven').s, 'avenue'],
            [0, 'wide'], [at('people').s, 'avenue'], [at('power').s, 'sea'], [at('now').s, 'wide'], [at('light').s, 'crossing'],
            [at('left').s, 'avenue'], [at('normal').s, 'crossing'], [at('traffic').s, 'crossing'], [at('last').s, 'avenue'],
            [at('five').s, 'sea'], [at('eight').s, 'crossing'], [at('then').s, 'wide'], [climax + 2.6, 'avenue'],
            [at('moon').s, 'sea'], [at('stars').s, 'wide'], [at('cold').s, 'avenue']].sort((a, b) => a[0] - b[0]),
    beats: { lookUp: climax + 1, carsStop: at('gone').s, shelter: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('last').s, climax + 3], riser: [at('five').s, climax] },
    end: { title: '', lines: '' },
  };
}
