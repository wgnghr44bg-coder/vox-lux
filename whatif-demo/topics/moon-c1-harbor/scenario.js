// What if the Moon started falling toward Earth? Chapter 1: the harbour at night, 384,400 -> 100,000 km.
// Physics: tidal pull grows with 1/distance³ (half the distance = 8×; 200,000 km ≈ 7×; 100,000 km ≈ 57×);
// apparent size grows with 1/distance (200,000 km ≈ 1.9× as wide).
export const topic = {
  number: 501, slug: 'moon-c1-harbor', place: 'harbor', force: 'tide', wide: true, voOffset: 2.5,
  question: 'What if the Moon started falling toward Earth?',
  title: 'What if the Moon<br>started falling?',
};

export const lines = [
  ['imagine', 'Imagine looking up… and every night, the Moon is a little bigger.', 'long'],
  ['notcrash', 'No impact. No explosion. It just keeps creeping closer, night after night.', 'long'],
  ['today', 'Right now, the Moon is about three hundred and eighty-four thousand kilometres away.', 'pause'],
  ['pull', 'You cannot feel its pull. But the oceans can. Twice a day, it lifts them into the tides.', 'long'],
  ['halve', 'And tidal pull follows a frightening rule: halve the distance, and it becomes eight times stronger.', 'long'],
  ['m200', 'Two hundred thousand kilometres.', 'long'],
  ['wide', 'The Moon looks almost twice as wide. And the tides are about seven times stronger.', 'pause'],
  ['quay', 'High tide no longer stops at the quay.', 'long'],
  ['m100', 'One hundred thousand kilometres.', 'long'],
  ['fifty', 'Now the pull on the oceans is more than fifty times stronger than today.', 'pause'],
  ['rush', 'With every high tide, the sea pours into the harbour…', 5],
  ['left', '…and when it pulls back, it leaves the ships behind, stranded in the streets.', 'pause'],
  ['cliff', 'But water is not the only thing the Moon can pull on.', 'none'],
];

export default function (at) {
  const T_END = at('cliff').e + 2;
  const QY = 3.2, climax = at('rush').e + .2;   // silent climax: the sea floods the quay (rush.e -> left.s)
  const km = [[0, 384400], [at('m200').s - .6, 384400], [at('m200').e + .3, 200000], [at('m100').s - .6, 200000], [at('m100').e + .3, 100000], [T_END, 100000]];
  const p = at('pull'), q = at('quay');
  return {
    T_END, tripod: true, brand: false, showTitle: true, post: true,
    titleOut: at('imagine').e + .3,
    moon: { km, dir: [-.26, .12, -.96] },
    space: [[at('today').s - .4, p.s - .3, { frame: .9, yaw: .2, focus: .5 }], [at('m100').s - .4, at('fifty').s - .3, { frame: .9, yaw: .55, focus: .5 }]],
    groups: [{ at: [44, 14], n: 7, face: Math.PI, shot: { name: 'group', from: [-6.5, 1.7, 5.5], fov: 48 }, lampAt: [2, 2], lampPower: 25 }],
    hud: { label: 'MOON DISTANCE', unit: ' km', decimals: 0,
           second: { label: 'TIDAL PULL', prefix: '×', fn: v => (384400 / v) ** 3, decimals: 0, showAt: at('halve').s } },
    counter: km, range: [384400, 100000],
    forceParams: { calm: QY - .5, top: QY + 3.6, tide: [
      [0, -.4], [p.s, -.9], [(p.s + p.e) / 2, 1.1], [p.e + .6, -.9], [at('m200').s, -1.6],
      [q.e + .4, QY + .55], [q.e + 2.4, QY + .3], [at('m100').e, -3], [at('fifty').e, -6],
      [at('rush').s, -6.2], [at('left').s + .3, QY + 3.6], [at('left').s + 1.5, QY + 3.4], [at('left').e + 1.5, -7], [T_END, -7.2]] },
    captions: [[at('today').s + .5, at('today').e + .6, '384,400 km'], [at('halve').s + 1.5, at('halve').e + .5, 'Half the distance → 8× the pull']],
    shots: [[0, 'moon-tele'], [at('notcrash').s - .2, 'group'], [p.s - .3, 'quay'], [at('halve').s - .2, 'harbor'],
            [at('m200').s - .2, 'moon-tele'], [at('wide').s + 2.6, 'quay'], [q.s - .2, 'harbor-low'],
            [at('fifty').s - .3, 'high'], [at('rush').e + .3, 'street'], [at('cliff').s - .2, 'moon-sky']],
    beats: { lookUp: at('notcrash').s + .4, shelter: at('fifty').s, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('m100').s, climax + 3], riser: [at('fifty').s, climax] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Moon started falling toward Earth?', description: 'Proef hoofdstuk 1, niet uploaden.', tags: [], tiktok: '' };
