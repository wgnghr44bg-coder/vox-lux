// What if the wind never stopped? Long video (16:9), chapter 3 of 3: the river city, 250 -> 1,000 km/h, the bridge fails.
export const topic = {
  number: 103, slug: 'wind-3-river', place: 'river-city', force: 'wind', wide: true,
  question: 'What if the wind never stopped?', title: '', voiceSpeed: .9,
};

export const lines = [
  ['city', 'In the city by the river, the great bridge would begin to move.', 'pause'],
  ['built', 'Bridges like this are built to sway a little in a storm.', 'pause'],
  ['notThis', 'Not like this.', 'long'],
  ['twist', 'The deck would swing from side to side, like a ribbon.', 'long'],
  ['empty', 'By now, the streets would be empty. Everyone would be sheltering indoors.', 'pause'],
  ['thrown', 'Parked cars would be lifted and thrown.', 'long'],
  ['threeTwenty', 'Three hundred and twenty. As strong as the most violent tornadoes.', 'pause'],
  ['stripped', 'Chimneys and balconies would break away. Trees would be stripped bare.', 'long'],
  ['fourFifty', 'Four hundred and fifty.', 'pause'],
  ['record', 'Faster than any gust ever measured on the surface of the Earth.', 'pause'],
  ['dust', 'The air would be thick with dust. You could barely see across the river.', 'long'],
  ['tower', 'The old water tower would lean, and then fall.', 'long'],
  ['cables', 'Out on the bridge, the steel cables would begin to snap.', 'pause'],
  ['gunshot', 'Each one would crack like a gunshot.', 'long'],
  ['sixHundred', 'Six hundred.', 'pause'],
  ['eightHundred', 'Eight hundred.', 'pause'],
  ['jet', 'Faster than a passenger jet.', 9],
  ['thousand', 'One thousand kilometers per hour.', 'pause'],
  ['sound', 'Almost the speed of sound.', 'long'],
  ['real', 'In the real world, no wind could last like this.', 'pause'],
  ['energy', 'Every storm runs out of energy. Every storm ends.', 'pause'],
  ['final', 'And that is the only reason our cities are still standing.', 'none'],
];

const lin = pts => v => { for (let i = 1; i < pts.length; i++) if (v <= pts[i][0]) { const [a, b] = pts[i - 1], [c, d] = pts[i]; return b + (d - b) * (v - a) / (c - a); } return pts[pts.length - 1][1]; };

export default function (at) {
  const climax = at('jet').e + .3, T_END = at('final').e + 3.2;
  return {
    T_END, reach: 16, carWind: .78, brand: false,
    hud: { label: 'WIND SPEED', unit: ' km/h', second: { label: '', fn: v => v / 1.609, unit: ' mph', showAt: 0 } },
    counter: [[0, 252], [at('twist').s, 262], [at('thrown').s, 285], [at('threeTwenty').s, 320], [at('fourFifty').s, 450],
              [at('cables').s, 530], [at('sixHundred').s, 600], [at('eightHundred').s, 800], [climax + 1.5, 900], [at('thousand').s, 1000],
              [at('sound').e, 1000], [at('energy').e, 60], [at('final').s, 15]],
    range: [0, 1000], forceParams: { wind: lin([[0, 0], [240, 280], [250, 300], [320, 420], [450, 560], [600, 700], [1000, 850]]), max: 850, dir: [1, 0] },
    captions: [[at('notThis').s, at('notThis').e + .8, 'Not like this.'],
               [at('threeTwenty').s, at('threeTwenty').e + .4, 'Tornado strength.'],
               [at('record').s, at('record').e + .4, 'Faster than any wind ever measured.'],
               [at('jet').s, at('jet').e + .8, 'Faster than a jet.'],
               [at('energy').s, at('energy').e + .6, 'Every storm ends.']],
    shots: [[0, 'wide'], [at('built').s, 'span'], [at('twist').s, 'under'], [at('empty').s, 'quay'], [at('thrown').s - .5, 'road'],
            [at('threeTwenty').s, 'wide'], [at('stripped').s, 'quay'], [at('fourFifty').s, 'span'], [at('dust').s, 'wide'], [at('tower').s - .4, 'north'],
            [at('cables').s, 'span'], [at('eightHundred').s, 'deck'], [climax - .3, 'wide'],
            [at('thousand').s + .4, 'span'], [at('real').s, 'under'], [at('energy').s + .5, 'wide']],
    beats: { lookUp: -5, shelter: -5, carsStop: -8, hangers: at('cables').s, deckBreak: climax + 2.2,
             falls: [climax + 6.6, at('tower').s + 1.6, climax + 7.6, climax + 8.8], climax, stop: at('final').s, fade: at('final').s + .4 },
    audio: { heartbeat: [0, climax], riser: [at('cables').s, climax + .5] },
    end: { title: '', lines: '' },
  };
}
