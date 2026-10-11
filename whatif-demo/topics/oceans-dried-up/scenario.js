// STANDAARD-video (regels/standaard-video.md): plek 'boulevard' + kracht 'tide' (zeespiegel zakt ver onder 0) +
// baksteen diepe zeebodem (engine/seabed.js). Eén doorlopende camerabeweging van de boulevard tot hoog boven de diepzee.
// Schaal in beeld is samengeperst; de teller (SEA LEVEL) toont het echte verhaal: ± 455 m per uur, 24 uur lang.
export const topic = {
  number: 7, slug: 'oceans-dried-up', place: 'boulevard', force: 'tide',
  question: 'What if every ocean dried up?',
  title: 'What if every<br>ocean dried up?',
  voOffset: 1.0,
};

// [id, text, pause after]: 'pause' (0,5 s), 'long' (1 s) or seconds of silence (the climax).
// Opbouw van de gravity-video (regels/standaard-video.md), aangepast aan het onderwerp.
export const lines = [
  ['imagine', 'Imagine…', 'pause'],
  ['intro', 'in a single day, every ocean on Earth drains away.', 'pause'],
  ['mean', 'Almost three quarters of the planet becomes dry land.', 'long'],
  ['place', 'You are standing on a beach boulevard.', 'pause'],
  ['tide', 'Normally, the tide moves the water a few meters.', 'long'],
  ['now', 'Now, it drops almost eight meters every minute.', 'long'],
  ['quiet', 'The waves fall silent.', 'pause'],
  ['hour', 'After one hour, the sea is more than four hundred meters lower.', 'long'],
  ['people', 'People stop. Lifeguards wave everyone off the beach.', 'pause'],
  ['boats', 'Boats lie on their sides in the mud.', 'long'],
  ['volume', 'The oceans hold about one point three billion cubic kilometers of water.', 'pause'],
  ['depth', 'On average, they are about three point seven kilometers deep.', 'long'],
  ['more', 'But the sea was doing much more than holding water.', 'pause'],
  ['heat', 'It soaked up most of the extra heat in our climate.', 'pause'],
  ['oxygen', 'Its plankton made around half of the oxygen produced on Earth.', 'long'],
  ['last', 'By the end of the day, the last water runs into the Mariana Trench.', 'pause'],
  ['trench', 'Almost eleven kilometers down.', 3.5],
  ['salt', 'Then, the wind blows salt across the empty sea floor.', 'long'],
  ['rain', 'Most of the rain on Earth begins as water rising from the sea.', 'pause'],
  ['q', 'Without it, the sky above you would slowly run dry.', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 2.4, start = at('tide').e, gone = at('trench').e + 3;
  // sea level in the SCENE (compressed: shelf edge ± -110 m, deep plain -1700 m, trench -2700 m)
  const tide = [[0, 0], [start, 0], [at('now').e, -1.5], [at('hour').e, -9], [at('boats').e, -30], [at('depth').e, -90],
                [at('more').e, -400], [at('heat').e, -1000], [at('oxygen').e, -1600],
                [at('last').e, -1820], [at('trench').s + 1, -2050], [gone, -2760], [T_END, -2760]];
  // sea level on the COUNTER (the real story): 0 -> -10 900 m in 24 hours
  const counter = [[0, 0], [start, 0], [at('now').e, 15], [at('hour').e, 455], [at('boats').e, 900], [at('depth').e, 2000],
                   [at('heat').e, 4500], [at('oxygen').e, 6200], [at('last').e, 8500], [gone, 10900], [T_END, 10900]];
  const hoursAt = (v) => v / 10900 * 24;
  return {
    T_END, titleOut: at('place').e + .4, hudIn: at('place').e + .7,
    hud: { label: 'SEA LEVEL', fmt: v => (v < .5 ? '0' : '−' + Math.round(v).toLocaleString('en-US')) + ' m',
           second: { label: 'TIME', fn: v => hoursAt(v), unit: ' h', decimals: 0, prefix: '+', showAt: at('now').s } },
    counter, range: [0, 10900],
    forceParams: { tide, calm: 1, top: 6 },
    seabed: { boats: true, salt: [at('salt').s - .5, at('salt').e + 3],
              fog: [[0, 180, 1600], [at('depth').s, 300, 2600], [at('more').s, 1500, 8000], [at('oxygen').s, 3500, 15000], [T_END, 4000, 16000]] },
    captions: [[at('now').s, at('now').e + .8, '≈ 7.6 m per minute.'],
               [at('hour').s, at('hour').e + .6, '1 hour: −455 m.'],
               [at('volume').s, at('depth').e + .6, '1.3 billion km³ of water.'],
               [at('oxygen').s, at('oxygen').e + .6, '≈ half of Earth\'s oxygen.'],
               [at('trench').s, at('trench').e + 1.5, 'Mariana Trench: ≈ 11 km deep.']],
    // one continuous move: [t, camera position, look at]   (shore at z 0, sea toward -z, boulevard at z 38..90, y 3)
    camPath: [
      [0, [3.8, 5.0, 50], [2, 3, -200]],
      [at('place').e, [3.8, 5.6, 44], [2, 2, -220]],
      [at('now').e, [3, 8, 39], [0, -1, -200]],
      [at('hour').s + .5, [0, 11, 34], [0, -3, -190]],
      [at('people').s, [-30, 11, 6], [6, 3, 40]],
      [at('people').e + .4, [-34, 12, 2], [8, 3, 42]],
      [at('boats').e + .8, [-14, 30, -10], [10, -6, -140]],
      [at('depth').s, [0, 60, -20], [0, -20, -500]],
      [at('more').e, [0, 260, -400], [0, -500, -2000]],
      [at('oxygen').s, [0, 600, -1100], [0, -1800, -3800]],
      [at('last').e, [0, 1100, -1800], [0, -2600, -4300]],
      [gone, [60, 1100, -1950], [0, -2650, -4300]],
      [at('rain').s, [250, 950, -2150], [0, -500, -800]],
      [T_END, [330, 800, -2300], [0, -60, 0]],
    ],
    fov: 58,
    wakeAt: [at('people').s - .3, at('people').s + 1.6], sunRun: 1,   // sunbathers get up and leave when the lifeguards wave
    beats: { carsStop: 1e9, shelter: at('people').s + .6, lookUp: at('quiet').s, stop: T_END, climax: at('trench').s + 1 },
  };
}

export const upload = {
  title: 'What if every ocean dried up?',
  description: 'A sunny beach. Then the sea starts to pull back… and it doesn\'t stop. 🌊\n\nWhat would be left of the ocean floor?\n\nWhat would you miss most about the sea? 👇\n\n#whatif #ocean #science #shorts',
  tags: ['what if', 'ocean', 'oceans dried up', 'sea floor', 'mariana trench', 'science', 'simulation', '3d animation', 'IfScape3D'],
  tiktok: 'What if every ocean dried up? 🌊 In one day the sea drains… all the way down to the Mariana Trench. What would you miss most? #whatif #ocean #science #fyp',
  sources: [
    'Ocean volume ≈ 1.335 billion km³, mean depth ≈ 3.7 km: NOAA / Charette & Smith (2010), Oceanography 23(2) "The volume of Earth\'s ocean" – https://tos.org/oceanography/article/the-volume-of-earths-ocean',
    'Ocean ≈ 71% of Earth\'s surface: USGS "How much water is there on Earth?" – https://www.usgs.gov/special-topics/water-science-school/science/how-much-water-there-earth',
    'Mariana Trench, Challenger Deep ≈ 10,900–10,935 m: NOAA Ocean Exploration – https://oceanexplorer.noaa.gov/facts/mariana-trench.html',
    'Ocean took up > 90% of the excess heat (IPCC AR6 WG1 SPM A.1 / NASA) and ≈ a quarter of CO2 emissions (Global Carbon Budget): https://www.ipcc.ch/report/ar6/wg1/ – https://globalcarbonbudget.org',
    'Phytoplankton produce roughly half of Earth\'s oxygen: NOAA Ocean Service "How much oxygen comes from the ocean?" – https://oceanservice.noaa.gov/facts/ocean-oxygen.html',
    'Most of Earth\'s evaporation (≈ 86%) and so most precipitation comes from the ocean: NASA Earth Observatory "The Water Cycle" / Trenberth et al. (2007) – https://earthobservatory.nasa.gov/features/Water',
    'Tidal range is typically a few metres on most coasts: NOAA "What are tides?" – https://oceanservice.noaa.gov/facts/tides.html',
    'Fiction: 0 → −10,900 m in 24 h ≈ 7.6 m per minute (≈ 455 m per hour).',
  ],
};
