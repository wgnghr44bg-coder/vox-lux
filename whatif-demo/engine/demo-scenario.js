// Preview of a place + force without a topic: scene.html?place=river-city&force=gravity
export const lines = [['a', 'One two three four five six seven eight nine ten.', 'long']];
export default function (at, o) {
  return {
    title: `${o.place}<br>${o.force}`, T_END: 60, titleOut: 3,
    hud: { label: 'LEVEL', unit: '', decimals: 2 },
    counter: [[0, 0], [8, 0], [40, 1]],
    captions: [[4, 7, 'A preview of the place.']],
    shots: o.shots || [[0, 'wide']],
    beats: { stop: 44, climax: 38, end: 50, falls: [36, 38.5, 41], windows: 30, walls: 33, floors: 35, shelter: 20, carsStop: 22 },
    forceParams: { wind: v => v * 650, max: 650, rise: 7 },
    lifebuoy: o.force === 'water' ? [-1, 76] : null,
    skyObjects: [{ t0: 13, t1: 25, from: [-900, 700, -1500], to: [300, 40, -700], r: 22, ease: 1.6 }],
    end: { title: 'Preview', lines: `${o.place} / ${o.force}` },
  };
}
