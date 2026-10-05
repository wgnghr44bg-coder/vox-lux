// What if the temperature dropped to -100°C?  (onderwerpen.md #32)
export const topic = {
  number: 32, slug: 'deep-freeze', place: 'river-city', force: 'cold',
  question: 'What if the temperature dropped to minus 100 degrees?',
  title: 'What if it got<br>−100°C?',
};

export const lines = [
  ['imagine', 'Imagine the temperature dropped to minus one hundred degrees.', 'long'],
  ['intro', 'You are standing by a river in a city, on a mild autumn afternoon.', 'pause'],
  ['calm', 'Twenty degrees. People walk along the water. Cars cross the bridge.', 'long'],
  ['now', 'Then the cold arrives. And it keeps falling.', 'long'],
  ['zero', 'Zero degrees. Frost creeps over the trees and the cars.', 'pause'],
  ['twenty', 'Minus twenty. The river starts to freeze at its edges.', 'pause'],
  ['forty', 'Minus forty. As cold as a winter night in Siberia.', 'pause'],
  ['breath', 'Your breath would freeze into tiny ice crystals the moment it leaves your mouth.', 'pause'],
  ['skin', 'Bare skin would freeze within minutes. Everyone hurries inside.', 'long'],
  ['cars', 'Car batteries fail. Engines stop. Drivers leave their cars and run.', 'long'],
  ['sixty', 'Minus sixty.', 'pause'],
  ['ice', 'The air glitters with ice. The whole river turns white.', 'long'],
  ['ninety', 'Minus ninety. Colder than any weather station on Earth has ever recorded.', 'pause'],
  ['steel', 'In this cold, steel turns brittle. The bridge shrinks by more than a foot.', 'pause'],
  ['bang', 'Then, a sharp crack.', 6],
  ['hundred', 'Minus one hundred degrees.', 'long'],
  ['still', 'The city stands silent, frozen in a single afternoon.', 'pause'],
  ['final', 'And nothing outside would move again until the warmth returned.', 'none'],
];

export default function (at) {
  const climax = at('bang').e + .6, stop = at('hundred').e;
  return {
    T_END: at('final').e + 2.6,
    hud: { label: 'TEMPERATURE', unit: '°C',
           second: { label: '', scale: 1.8, offset: 32, min: -1e9, unit: '°F', showAt: 1 } },
    counter: [[0, 20], [at('now').e, 20], [at('zero').s, 0], [at('twenty').s, -20], [at('forty').s, -40],
              [at('sixty').s, -60], [at('ninety').s, -90], [at('steel').e, -95], [at('hundred').s, -100], [stop, -100]],
    range: [20, -100], forceParams: { darkAt: [5, 6], frostAt: [.1, .75], snow: .35, breath: at('breath').s },
    captions: [[at('breath').s, at('breath').e + .5, 'Your breath freezes.'],
               [at('cars').s, at('cars').e + .4, 'Engines stop.'],
               [at('ninety').s, at('ninety').e + .5, 'Colder than ever recorded.'],
               [at('steel').s, at('steel').e + .4, 'Steel turns brittle.']],
    shots: [[0, 'wide'], [at('intro').s + 1, 'quay'], [at('now').s, 'wide'], [at('twenty').s, 'under'], [at('forty').s, 'quay'],
            [at('cars').s, 'deck'], [at('sixty').s, 'wide'], [at('ice').s, 'under'], [at('ninety').s, 'quay'],
            [at('steel').s, 'span'], [climax + 3.5, 'under'], [at('still').s, 'wide']],
    beats: {
      brand: at('intro').s + 2, carsStop: at('cars').s, lookUp: at('now').e, shelter: at('skin').s + 1,
      hangers: at('bang').s + .3, deckBreak: climax, climax, falls: [], stop,
      fade: at('final').s - .2,
    },
    audio: { heartbeat: [at('forty').s, stop], riser: [at('steel').s, climax + .5] },
    end: { title: '', lines: '' },
  };
}

export const upload = {
  title: 'What if the temperature dropped to −100°C?',
  description: "POV: you're standing by a city river when the temperature starts falling and doesn't stop. 🥶\n\n" +
    'At −90°C it would be colder than any weather station on Earth has ever recorded.\n\n' +
    'How long would you last outside? 👇\n\n' +
    '#whatif #cold #physics #shorts',
  tags: ['what if', 'what if it was minus 100 degrees', 'extreme cold', 'cold', 'ice', 'physics', 'science', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: "POV: the temperature drops to −100°C 🥶 Colder than anywhere ever recorded. #whatif #cold #science #fyp",
};
