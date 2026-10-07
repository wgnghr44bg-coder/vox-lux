// What if the Sun went out? Chapter 2 of 5: mountain village, the first day (15 -> 3 °C).
// Chapters 2-5 share range [15, -73] so darkness, frost and snow carry on from chapter to chapter.
export const topic = {
  number: 202, slug: 'sun-out-2-village', place: 'mountain-village', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['hours', 'In the first hours, the dark would feel like any other night.', 'pause'],
  ['village', 'Picture a small village high in the mountains.', 'pause'],
  ['warm', 'The ground, the walls and the lake still hold the warmth of yesterday.', 'pause'],
  ['night', 'On a normal night, that warmth would carry the village through until sunrise.', 'pause'],
  ['leak', 'But that heat would slowly leak away into space, and nothing would come to replace it.', 'long'],
  ['plants', 'Every plant on Earth would stop making food the moment the light was gone.', 'pause'],
  ['grass', 'The grass, the crops, the trees on these slopes.', 'pause'],
  ['wait', 'For now, they would wait, living on what they had stored.', 'pause'],
  ['solar', 'Solar panels on the roofs would produce nothing at all.', 'long'],
  ['temp', 'The temperature would keep falling, hour after hour.', 'pause'],
  ['ten', 'Ten degrees.', 'pause'],
  ['five', 'Five.', 'long'],
  ['lake', 'The lake would steam in the freezing air, giving up its heat.', 'pause'],
  ['people', 'People would light fires and turn up the heating.', 'pause'],
  ['candles', 'Shops would sell out of candles, blankets and firewood.', 'pause'],
  ['inside', 'The square would empty as everyone went indoors.', 'long'],
  ['fuel', 'Power stations would burn through fuel faster than ever, as the whole world tried to keep warm.', 'long'],
  ['frost', 'By the end of the first day, frost would creep over the rooftops.', 'pause'],
  ['snow', 'Moisture in the air would start to fall as snow.', 4],
  ['morning', 'And there would be no morning.', 'long'],
  ['clock', 'The clocks would say it is day. The sky would say it is night.', 'pause'],
  ['birds', 'Birds would stay in their nests, waiting for a dawn that never comes.', 'pause'],
  ['forever', 'And it would stay night.', 'long'],
];

export default function (at) {
  const climax = at('snow').e + .4, T_END = at('forever').e + 3.0;
  return {
    T_END, tripod: true, brand: false,
    hud: { label: 'TEMPERATURE', unit: '°C', sub: 'DAY 1', second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 0 } },
    counter: [[0, 15], [at('leak').e, 14], [at('temp').s, 12], [at('ten').s, 10], [at('five').s, 5], [at('frost').s, 3], [T_END, 2]],
    range: [15, -73], forceParams: { darkAt: [-1, 0], frostAt: [.1, .9], snow: 2.2 },
    captions: [[at('hours').s, at('hours').e + .8, 'The first night.'], [at('plants').s, at('plants').e + .5, 'Plants stop making food.'],
               [at('solar').s, at('solar').e + .4, 'No solar power.'],
               [at('frost').s, at('frost').e + .4, 'Frost on the rooftops.'],
               [at('morning').s, at('morning').e + .6, 'No morning.']],
    // a new standpoint on every line (gravity style: observer shots, never the same twice in a row), one extra cut in the silent climax
    shots: [...lines.map(([id], k) => [k ? at(id).s - .2 : 0, ['wide', 'village', 'square', 'mountains', 'lake'][k % 5]]), [climax + 2.5, ['wide', 'village', 'square', 'mountains', 'lake'][(lines.length + 2) % 5]]]
      .sort((a, b) => a[0] - b[0]),
    beats: { lookUp: at('hours').s, shelter: at('inside').s, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('temp').s, climax + 2], riser: [at('frost').s, climax] },
    end: { title: '', lines: '' },
  };
}
