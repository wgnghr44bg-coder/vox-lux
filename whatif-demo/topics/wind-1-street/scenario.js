// What if the wind never stopped? Long video (16:9), chapter 1 of 3: the street, 20 -> 120 km/h.
// Counter = real wind speed (km/h); forceParams.wind maps it to the engine's wind scale (tuned per place).
export const topic = {
  number: 101, slug: 'wind-1-street', place: 'street', force: 'wind', wide: true,
  question: 'What if the wind never stopped?', title: '', voiceSpeed: .9,
};

export const lines = [
  ['imagine', 'Imagine the wind never stopped.', 'long'],
  ['never', 'Not for an hour. Not for a day. Not ever.', 'pause'],
  ['grow', 'And every hour, it would grow a little stronger.', 'long'],
  ['notice', 'At first, you would hardly notice.', 'pause'],
  ['twenty', 'Twenty kilometers per hour. A few leaves tumbling down the street.', 'pause'],
  ['sway', 'The palm trees would sway gently, the way they always do.', 'pause'],
  ['nice', 'Just a pleasant, breezy morning.', 'pause'],
  ['twice', 'Nobody would think twice about it.', 'long'],
  ['fifty', 'By fifty, something would start to feel wrong.', 'pause'],
  ['paper', 'Paper would race along the pavement. Leaves would whirl up between the buildings.', 'pause'],
  ['walk', 'Walking into it would take real effort.', 'pause'],
  ['signs', 'Shop signs would rattle and swing on their hooks.', 'long'],
  ['seventy', 'Seventy. The café chairs would start to slide, then tumble down the road.', 'pause'],
  ['trees', 'Every tree on the avenue would bend and roar.', 'pause'],
  ['howl', 'The wind would howl between the buildings, a sound that never fades.', 'long'],
  ['storm', 'At ninety, this would be a full storm.', 'pause'],
  ['inside', 'People would hurry indoors. Drivers would pull over and wait.', 'long'],
  ['bins', 'Then even the heavy bins would start to roll.', 'pause'],
  ['hurricane', 'One hundred and twenty. Hurricane force.', 'pause'],
  ['train', 'The wind would roar like a passing train. Except this train would never pass.', 'long'],
  ['pass', 'A real hurricane would pass within a day or two.', 'pause'],
  ['would', 'This one never would.', 'long'],
];

const lin = pts => v => { for (let i = 1; i < pts.length; i++) if (v <= pts[i][0]) { const [a, b] = pts[i - 1], [c, d] = pts[i]; return b + (d - b) * (v - a) / (c - a); } return pts[pts.length - 1][1]; };

export default function (at) {
  const T_END = at('would').e + 1.6;
  return {
    T_END, reach: 16, carWind: 2,
    hud: { label: 'WIND SPEED', unit: ' km/h', second: { label: '', fn: v => v / 1.609, unit: ' mph', showAt: 0 } },
    counter: [[0, 18], [at('twenty').e, 22], [at('nice').e, 30], [at('fifty').s, 50], [at('seventy').s, 70], [at('storm').s, 90],
              [at('bins').s, 108], [at('hurricane').s, 120], [T_END, 126]],
    range: [0, 1000], forceParams: { wind: lin([[0, 0], [20, 12], [50, 45], [90, 120], [120, 200], [200, 300]]), max: 800, dir: [0, 1] },
    captions: [[at('twenty').s, at('twenty').e + .6, 'A light breeze.'],
               [at('fifty').s, at('fifty').e + .8, 'Strong wind.'],
               [at('storm').s, at('storm').e + .8, 'Storm.'],
               [at('hurricane').s, at('hurricane').e + .8, 'Hurricane force.'],
               [at('would').s, at('would').e + .6, 'This one never would.']],
    shots: [[0, 'avenue'], [at('fifty').s, 'crossing'], [at('signs').s, 'avenue'], [at('seventy').s, 'crossing'], [at('trees').s, 'avenue'],
            [at('howl').s, 'sea'], [at('storm').s, 'avenue'], [at('inside').s, 'crossing'], [at('bins').s, 'avenue'], [at('hurricane').s + .4, 'crossing'],
            [at('train').s, 'avenue'], [at('pass').s, 'crossing'], [at('would').s - .3, 'avenue']],
    beats: { lookUp: at('fifty').s, shelter: at('inside').s, carsStop: at('inside').s, stop: T_END + 1, climax: 1e9, falls: [], fade: 1e9 },
    audio: { heartbeat: [at('storm').s, T_END], riser: [at('bins').s, at('hurricane').e] },
    end: { title: '', lines: '' },
  };
}
