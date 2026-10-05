// What if the wind never stopped? Long video (16:9), chapter 2 of 3: the beach boulevard, 120 -> 250 km/h.
export const topic = {
  number: 102, slug: 'wind-2-boulevard', place: 'boulevard', force: 'wind', wide: true,
  question: 'What if the wind never stopped?', title: '', voiceSpeed: .9,
};

export const lines = [
  ['coast', 'Down at the coast, the sea would already be wild.', 'pause'],
  ['umbrellas', 'Beach umbrellas would rip loose and cartwheel across the sand.', 'pause'],
  ['empty', 'The beach would be empty within minutes.', 'long'],
  ['sand', 'Sand would blast across the boulevard, hard enough to sting your skin.', 'pause'],
  ['brown', 'Slowly, the sky would turn a dusty brown.', 'long'],
  ['oneFifty', 'One hundred and fifty.', 'pause'],
  ['palms', 'The palm trees would bend almost flat. Their leaves would tear away, one by one.', 'long'],
  ['oneEighty', 'At one hundred and eighty, the street lamps would start to bend.', 'pause'],
  ['balconies', 'Balconies would rip away from the hotels.', 'pause'],
  ['chimneys', 'Chimneys would topple from the rooftops.', 'long'],
  ['twoFifty', 'Two hundred and fifty. The strength of a category five hurricane.', 'pause'],
  ['hours', 'Even the strongest hurricanes only keep this up for a few hours.', 'long'],
  ['passed', 'Any normal storm would have passed by now.', 'pause'],
  ['halfway', 'This one would only be getting started.', 'long'],
];

const lin = pts => v => { for (let i = 1; i < pts.length; i++) if (v <= pts[i][0]) { const [a, b] = pts[i - 1], [c, d] = pts[i]; return b + (d - b) * (v - a) / (c - a); } return pts[pts.length - 1][1]; };

export default function (at) {
  const T_END = at('halfway').e + 1.6;
  return {
    T_END, reach: 16, carWind: .62,
    hud: { label: 'WIND SPEED', unit: ' km/h', second: { label: '', fn: v => v / 1.609, unit: ' mph', showAt: 0 } },
    counter: [[0, 124], [at('umbrellas').s, 128], [at('sand').s, 140], [at('oneFifty').s, 150], [at('oneEighty').s, 180],
              [at('balconies').e, 215], [at('twoFifty').s, 250], [T_END, 262]],
    range: [0, 1000], forceParams: { wind: lin([[0, 0], [110, 40], [140, 140], [170, 260], [210, 360], [260, 460], [300, 520]]), max: 800, dir: [1, 0] },
    captions: [[at('oneFifty').s, at('oneFifty').e + 1, '150 km/h'],
               [at('oneEighty').s, at('oneEighty').s + 3, '180 km/h'],
               [at('twoFifty').s, at('twoFifty').e + .6, 'Category 5 hurricane.']],
    shots: [[0, 'beach'], [at('umbrellas').s, 'wide'], [at('empty').s, 'pov-beach'], [at('sand').s, 'boulevard'], [at('oneFifty').s, 'wide'],
            [at('palms').s, 'boulevard'], [at('oneEighty').s, 'hotels'], [at('balconies').s + .3, 'hotels'], [at('chimneys').s, 'wide'], [at('twoFifty').s, 'boulevard'], [at('hours').s, 'wide'], [at('halfway').s, 'sea']],
    beats: { lookUp: at('coast').s, shelter: at('umbrellas').s, carsStop: at('oneFifty').s, brand: at('empty').s + .4,
             stop: T_END + 1, climax: 1e9, falls: [], fade: 1e9 },
    audio: { heartbeat: [0, T_END], riser: [at('balconies').s, at('twoFifty').e] },
    end: { title: '', lines: '' },
  };
}
