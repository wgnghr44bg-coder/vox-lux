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
  ['hour', 'After one hour, the sea is more than four hundred meters lower.', 'long'],
  ['people', 'People stop. Lifeguards wave everyone off the beach.', 'pause'],
  ['boats', 'Boats lie on their sides in the mud.', 'long'],
  ['ship', 'Further out, a container ship tips over, and its cargo slides into the mud.', 'long'],
  ['trade', 'About eighty percent of the world\'s goods travel by sea. Today, none of them move.', 'long'],
  ['white', 'Then, the salt appears. The sea floor turns white.', 'long'],
  ['layer', 'Spread over all the land on Earth, that salt would be about one hundred and fifty meters deep.', 'long'],
  ['air', 'With no sea to cool it, the coast heats up like a desert.', 'long'],
  ['clouds', 'And the clouds start to thin out.', 'pause'],
  ['rain', 'Most of the rain on Earth begins as water rising from the sea.', 'long'],
  ['last', 'By the end of the day, the last water runs into the Mariana Trench.', 'pause'],
  ['trench', 'Almost eleven kilometers down.', 3.5],
  ['storm', 'Then, the wind lifts the salt into huge white storms.', 'long'],
  ['blue', 'The blue planet is not blue anymore.', 'pause'],
  ['q', 'And the sky above you slowly runs dry.', 'none'],
];

export default function (at) {
  const T_END = at('q').e + 2.4, start = at('tide').e, gone = at('trench').e + 3;
  // sea level in the SCENE (compressed: shelf edge ± -110 m, deep plain -1700 m, trench -2700 m)
  const tide = [[0, 0], [start, 0], [at('now').e, -1.5], [at('hour').e, -9], [at('boats').e, -20],                 [at('ship').s + 1, -60], [at('trade').e, -120], [at('white').s, -300], [at('white').e, -1100], [at('layer').e, -1600],
                [at('air').e, -1700], [at('rain').e, -1770], [at('last').e, -1860], [at('trench').s + 1, -2050], [gone, -2760], [T_END, -2760]];
  // sea level on the COUNTER (the real story): 0 -> -10 900 m in 24 hours
  const counter = [[0, 0], [start, 0], [at('now').e, 15], [at('hour').e, 455], [at('boats').e, 700], [at('ship').e, 1200],
                   [at('trade').e, 1700], [at('white').e, 3000], [at('layer').e, 4200], [at('air').e, 5500], [at('rain').e, 7000],
                   [at('last').e, 8500], [gone, 10900], [T_END, 10900]];
  const hoursAt = (v) => v / 10900 * 24;
  return {
    T_END, titleOut: at('place').e + .4, hudIn: at('place').e + .7,
    hud: { label: 'SEA LEVEL', fmt: v => (v < .5 ? '0' : '−' + Math.round(v).toLocaleString('en-US')) + ' m',
           second: { label: 'TIME', fn: v => hoursAt(v), unit: ' h', decimals: 0, prefix: '+', showAt: at('now').s } },
    counter, range: [0, 10900],
    forceParams: { tide, calm: 1, top: 6 },
    seabed: { boats: true, salt: [at('white').s, at('storm').e + 2], storm: at('storm').s - .3,
              heat: [at('air').s, at('air').e + 3], clouds: [at('clouds').s, at('rain').e + 2],
              fog: [[0, 180, 1600], [at('ship').s, 400, 3000], [at('white').s, 1200, 7000], [at('white').e, 1500, 8000], [at('air').s, 3500, 15000], [T_END, 4000, 16000]] },
    captions: [[at('now').s, at('now').e + .8, '≈ 7.6 m per minute.'],
               [at('hour').s, at('hour').e + .6, '1 hour: −455 m.'],
               [at('trade').s, at('trade').e + .6, '≈ 80% of world trade goes by sea.'],
               [at('white').s, at('white').e + .6, '≈ 35 g of salt in every litre.'],
               [at('layer').s, at('layer').e + .6, 'A layer of salt ≈ 150 m deep.'],
               [at('trench').s, at('trench').e + 1.5, 'Mariana Trench: ≈ 11 km deep.']],
    // one continuous move: [t, camera position, look at]   (shore at z 0, sea toward -z, boulevard at z 38..90, y 3)
    camPath: [
      [0, [3.8, 5.0, 50], [2, 3, -200]],
      [at('place').e, [3.8, 5.6, 44], [2, 2, -220]],
      [at('now').e, [3, 8, 39], [0, -1, -200]],
      [at('hour').s + .5, [0, 11, 34], [0, -3, -190]],
      [at('people').s, [-30, 11, 6], [40, 3, 70]],
      [at('people').e + .4, [-34, 12, 2], [50, 3, 66]],
      [at('boats').e, [-6, 24, 4], [40, -6, -90]],
      [at('boats').e + 2.5, [-36, 16, -40], [-64, 0, -150]],
      [at('ship').e, [-90, 55, -360], [-200, -20, -620]],
      [at('trade').e, [-230, 140, -760], [-420, -20, -1180]],
      [at('white').e, [-120, 480, -900], [0, -700, -2600]],
      [at('layer').e, [0, 700, -1200], [0, -1500, -3300]],
      [at('air').e, [0, 850, -1400], [0, -1700, -3900]],
      [at('rain').s, [0, 950, -1600], [0, 200, -5000]],
      [at('last').e, [0, 1100, -1800], [0, -2600, -4300]],
      [gone, [60, 1100, -1950], [0, -2650, -4300]],
      [at('blue').s, [250, 950, -2150], [0, -500, -800]],
      [T_END, [330, 800, -2300], [0, -60, 0]],
    ],
    fov: 58,
    wakeAt: [at('people').s - .3, at('people').s + 1.6], sunRun: 1,   // sunbathers get up and leave when the lifeguards wave
    beats: { carsStop: 1e9, shelter: at('people').s + .6, lookUp: at('hour').s, stop: T_END, climax: at('trench').s + 1 },
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
    '≈ 80% of world trade by volume goes by sea: UNCTAD Review of Maritime Transport – https://unctad.org/topic/transport-and-trade-logistics/review-of-maritime-transport',
    'Seawater ≈ 35 g of salt per litre (salinity ≈ 35 ‰): NOAA "Why is the ocean salty?" – https://oceanservice.noaa.gov/facts/whysalty.html',
    'Salt spread over all land ≈ 150 m thick: USGS "Why is the ocean salty?" (> 500 ft / 166 m) – https://www.usgs.gov/special-topics/water-science-school/science/why-ocean-salty; own check: ≈ 4.8·10^19 kg salt / 2.16 t/m³ ≈ 2.2·10^7 km³ over 1.49·10^8 km² land ≈ 150 m',
    'The sea moderates coastal temperatures (maritime vs. continental/desert climate): NOAA / NWS "Ocean influence on climate" – https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean-currents',
    'Most of Earth\'s evaporation (≈ 86%) and so most precipitation comes from the ocean: NASA Earth Observatory "The Water Cycle" / Trenberth et al. (2007) – https://earthobservatory.nasa.gov/features/Water',
    'Tidal range is typically a few metres on most coasts: NOAA "What are tides?" – https://oceanservice.noaa.gov/facts/tides.html',
    'Fiction: 0 → −10,900 m in 24 h ≈ 7.6 m per minute (≈ 455 m per hour).',
  ],
};
