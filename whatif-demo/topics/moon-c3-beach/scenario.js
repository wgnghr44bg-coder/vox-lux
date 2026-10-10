// What if the Moon started falling toward Earth? Chapter 3: the beach at night, 25,000 -> 18,000 km: the Roche limit.
// Physics: Roche limit (fluid body) d ≈ 2.44 R_E (ρ_E/ρ_M)^(1/3) ≈ 18,400 km from the Earth's centre; inside it the
// difference in pull between near and far side beats the Moon's own gravity: it is torn apart, the pieces spread along
// its orbit into a ring. Moon mass 7.35×10^22 kg = ~73 billion billion tonnes.
export const topic = {
  number: 503, slug: 'moon-c3-beach', place: 'boulevard', force: 'calm', wide: true, voOffset: 1.2,
  question: 'What if the Moon started falling toward Earth?', title: '',
};

export const lines = [
  ['roche', 'Every moon has an invisible line around its planet. Scientists call it the Roche limit.', 'long'],
  ['cross', 'Inside that line, the planet pulls much harder on the moon\'s near side than on its far side, until the moon\'s own gravity can no longer hold it together.', 'long'],
  ['ours', 'For our Moon, that line lies about eighteen thousand kilometres from the centre of the Earth.', 'long'],
  ['m20', 'Twenty thousand kilometres.', 'long'],
  ['huge', 'The Moon covers a huge part of the sky now. Night looks like a strange, silver day.', 'pause'],
  ['m18', 'Eighteen thousand kilometres.', 'long'],
  ['nocrash', 'The Moon does not crash into us.', 'pause'],
  ['torn', 'It is torn apart.', 6],
  ['rock', 'Seventy-three billion billion tonnes of rock spread out along its old path…', 'pause'],
  ['wrap', '…until the pieces wrap all the way around the Earth.', 'long'],
  ['cliff', 'Our planet now has a ring. But not all of that rock will stay up there.', 'none'],
];

export default function (at) {
  const T_END = at('cliff').e + 2, climax = at('torn').e + .2;
  const km = [[0, 25000], [at('m20').s - .2, 25000], [at('m20').e + .5, 20000], [at('m18').s - .3, 20000], [at('m18').e + .5, 18000], [T_END, 18000]];
  const orbit = { lat: 55, theta: 1.72 };
  // direction of the Moon (same geometry as engine/moon.js skyGeo) -> camera standpoints that look at it
  const f = orbit.lat * Math.PI / 180, dirAt = k => { const x = k * Math.cos(orbit.theta), y = -6371 + k * Math.sin(orbit.theta) * Math.cos(f), z = -k * Math.sin(orbit.theta) * Math.sin(f), l = Math.hypot(x, y, z); return [x / l, y / l, z / l]; };
  const d = dirAt(19000);
  const up = (pos, fov, el = 0, yaw = 0) => { const c = Math.cos(yaw), s = Math.sin(yaw), x = d[0] * c - d[2] * s, z = d[0] * s + d[2] * c;
    return { pos, look: [pos[0] + x * 1000, pos[1] + (d[1] + el) * 1000, pos[2] + z * 1000], drift: [0, 0, 0], fov }; };
  const brk = [at('m18').e + .8, climax + 4];
  return {
    T_END, tripod: true, brand: false, post: { ao: false }, sunbathers: 0,
    moon: { km, orbit, night: true, breakAt: brk, spread: 1.1 },
    ring: { r: [9000, 20000], show: [[0, 0], [climax - 2.5, 0], [at('wrap').e, .9], [T_END, 1]], arc: [[0, .1], [climax - 2.5, .12], [at('rock').e, 1.2], [at('wrap').e + .5, Math.PI], [T_END, Math.PI]] },
    space: [[at('ours').s - .3, at('m20').s - .3, { frame: .9, yaw: .3, pitch: .25, focus: .5 }],
            [climax + .8, at('wrap').e - .5, { frame: 1.6, yaw: .9, pitch: .55, focus: .4, span: 46000 }]],
    groups: [{ at: [6, 22], n: 7, face: Math.PI, lampPower: 15, lampAt: [3, 3] }],
    extraShots: {
      'moon-sea': up([0, 3 + 10, 64], 70, -.1),
      'moon-beach': up([-26, 2.6, 14], 78, -.13, .25),
      'group-up': up([12, 2.6, 30], 70, -.12, -.3),
      'pov-moon': up([4, 2.4, 26], 82, -.02),
    },
    hud: { label: 'MOON DISTANCE', unit: ' km', decimals: 0, sub: '', subAt: [[brk[0] + 1, 'ROCHE LIMIT']] },
    counter: km, range: [25000, 18000],
    captions: [[at('ours').s + .5, at('ours').e + .3, 'Roche limit ≈ 18,000 km'], [at('rock').s + .3, at('rock').e, '73 billion billion tonnes']],
    shots: [[0, 'moon-sea'], [at('cross').s + 2, 'group-up'], [at('ours').s - .3, 'moon-sea'], [at('m20').s - .3, 'moon-beach'], [at('huge').s + 2.5, 'pov-moon'],
            [at('m18').s - .2, 'group-up'], [at('nocrash').s - .2, 'moon-sea'], [at('wrap').e - .5, 'moon-beach'], [at('cliff').s - .2, 'group-up']],
    beats: { lookUp: 1, sit: 1e9, climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('m18').s, climax - 2], riser: [at('nocrash').s, climax - 2.4] },
    events: [{ t: brk[0] + 1.5, kind: 'fireball', e: .6 }],
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if the Moon started falling toward Earth?', description: 'Hoofdstuk 3, niet uploaden.', tags: [], tiktok: '' };
