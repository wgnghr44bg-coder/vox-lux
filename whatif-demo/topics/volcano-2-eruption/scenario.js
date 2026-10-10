// What if a supervolcano erupted? Long video (16:9), chapter 2: the eruption. Nature park, 40 km from the caldera.
// Bricks: place nature-park, force eruption (column, lightning, glow, glowing ash clouds, forest fires, ash, rain, lahar, black sky).
export const topic = {
  number: 3502, slug: 'volcano-2-eruption', place: 'nature-park', force: 'eruption', wide: true, voOffset: 1.2, padSilence: true,
  question: 'What if a supervolcano erupted?', title: '',
};

export const lines = [
  ['zero', 'Hour zero.', 5],
  ['krakatoa', 'When Krakatoa erupted in 1883, people heard it almost five thousand kilometres away.', 'pause'],
  ['bigger', 'This would be far bigger.', 'long'],
  ['column', 'Within minutes, a column of ash could rise more than thirty kilometres, punching straight through the clouds.', 'pause'],
  ['lightning', 'Inside it: lightning. Thousands of strikes, sparked by ash grains rubbing against each other.', 'long'],
  ['ten', 'Minute ten.', 'pause'],
  ['collapse', 'Then the column could collapse under its own weight.', 'pause'],
  ['flows', 'Avalanches of glowing ash and gas, hotter than three hundred degrees, would race down the slopes faster than a car on a motorway.', 'pause'],
  ['forests', 'Forests would vanish in seconds.', 'long'],
  ['six', 'Hour six.', 'pause'],
  ['rain', 'Rain mixes with the fresh ash, thick as wet concrete.', 'pause'],
  ['lahars', 'Rivers of mud, called lahars, could roll through the valleys, dragging whole trees along.', 'pause'],
  ['black', 'And at midday… the sky turns completely black.', 'pause'],
  ['worst', 'But for the rest of the continent, the worst hasn\'t even arrived.', 'none'],
];

export default function (at) {
  const T_END = at('worst').e + 1.6;
  const boom = at('zero').e + .6, col = [boom, boom + 16], coll = at('collapse').s + 1.2;
  const lah = at('lahars');
  return {
    T_END, tripod: true, brand: false, post: true, alarm: false,
    hud: { label: 'DISTANCE TO THE VOLCANO', unit: ' KM', decimals: 0, sub: 'HOUR 0',
           subAt: [[0, 'HOUR 0'], [at('ten').s, 'MINUTE 10'], [at('six').s, 'HOUR 6']] },
    counter: [[0, 40], [T_END, 40]],
    forceParams: {
      H: 1500, column: col, lightning: [at('lightning').s - 1.5, T_END], glow: [boom + 1],
      collapse: coll, flowSpeed: 95, flowReach: 1500, fires: true,
      dark: [[0, 0], [at('six').s, .25], [at('black').s, .55], [at('black').e + .5, .92], [T_END, .95]],
      ash: [[0, 0], [at('six').s - 1, 0], [at('six').s + 2, .6], [at('black').e, 1], [T_END, 1]],
      cover: [[0, 0], [at('six').s - .5, 0], [at('six').s + .5, .45], [T_END, .75]],
      rain: [at('rain').s - 1, lah.e + 1], lahar: [lah.s - 300 / 22, 22],
    },
    captions: [[at('krakatoa').s + 1, at('krakatoa').e + .3, 'Heard 4,800 km away.'], [at('flows').s + 1.5, at('flows').e + .3, 'Over 300 °C.']],
    shots: [[0, 'volcano'], [at('krakatoa').s - .2, 'vista'], [at('bigger').s - .2, 'group'], [at('column').s - .2, 'pov-plume'],
            [at('lightning').s - .2, 'volcano'], [at('ten').s - .2, 'vista'], [at('forests').s - .2, 'viewpoint'],
            [at('six').s - .2, 'lodge'], [lah.s - .2, 'creek'], [at('black').s - .2, 'volcano'], [at('worst').s - .2, 'pov-lot']],
    groups: [{ at: [12, -14.5], n: 6, face: Math.PI, y: .05, lamp: false, shot: { name: 'group', from: [3, 1.7, 8], fov: 50 } }],
    beats: { lookUp: boom + .8, shelter: at('ten').s, evacuate: 1e9, carsStop: 1e9, climax: boom, falls: [], stop: T_END + 2, fade: 1e9, end: 1e9 },
    audio: { heartbeat: [at('ten').s, coll + 2], riser: [at('collapse').s - 2, coll] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if a supervolcano erupted?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
