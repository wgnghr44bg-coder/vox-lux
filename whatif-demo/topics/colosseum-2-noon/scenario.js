// Trapped inside the Colosseum, chapter 2: MORNING -> NOON – the heat, the sailors pull out the velarium, the hunts (sound only).
export const topic = { number: 861, slug: 'colosseum-2-noon', place: 'colosseum', force: 'day', wide: true,
  question: 'What if you were trapped inside the Colosseum for one day?', title: '' };

export const lines = [
  ['morning', 'Morning. By nine o\'clock, every seat is taken.', 'long'],
  ['heat', 'The Sun climbs over the walls, and the stone begins to burn. Thirty degrees. Then thirty-five.', 'pause'],
  ['shade', 'There is no roof. No shade. Fifty thousand people, packed shoulder to shoulder.', 'long'],
  ['sailors', 'Then you notice them, high up on the top of the wall. Sailors. Hundreds of them, sent from the Roman fleet.', 'pause'],
  ['ropes', 'They haul on ropes, tied to two hundred and forty wooden masts.', 'pause'],
  ['sail', 'And slowly, a giant sail starts to slide out over the crowd.', 5],
  ['velarium', 'The velarium. A roof made of cloth, big enough to shade most of the stands.', 'long'],
  ['hunt', 'Down in the arena, the morning shows begin. Hunters, and wild animals from three continents.', 'pause'],
  ['hear', 'You can\'t see it from here. But you can hear it. And you can feel fifty thousand people jump to their feet.', 'long'],
  ['noon', 'Noon. The heat is unbearable. You need water, and air, and a way out.', 'pause'],
  ['stairs', 'So you squeeze through the crowd, and take the first staircase you can find.', 'pause'],
  ['down', 'But it doesn\'t lead out. It leads down.', 'none'],
];

const name = h => h < 7 ? 'DAWN' : h < 11.9 ? 'MORNING' : h < 14 ? 'NOON' : h < 18 ? 'AFTERNOON' : h < 20 ? 'EVENING' : 'NIGHT';
const clockAt = hours => t => { let h = hours[0][1]; for (let i = 0; i < hours.length - 1; i++) if (t >= hours[i][0]) h = hours[i][1] + (hours[i + 1][1] - hours[i][1]) * Math.min(1, (t - hours[i][0]) / (hours[i + 1][0] - hours[i][0]));
  const m = Math.round(h * 60); return `${name(h)} — ${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`; };

export default function (at) {
  const climax = at('sail').e + .3, T_END = at('down').e + 1.6, roar = at('hear').s + 4.2;
  const hours = [[0, 9], [at('noon').s - .5, 9.9], [at('noon').s + .5, 12.3], [T_END, 12.6]], ck = clockAt(hours);
  const subAt = []; for (let t = 0; t <= T_END; t += .5) subAt.push([t, ck(t)]);
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true, gateBay: 24,
    forceParams: { hours },
    crowd: { fill: [[0, 1]], stand: [[0, 0], [roar - .3, 0], [roar + .4, .95], [roar + 5, .25], [T_END, .1]], cheer: [[0, .1], [roar, .2], [roar + .4, 1], [roar + 6, .2]] },
    velarium: [[0, .02], [at('sail').s, .02], [climax + 5, .92]],
    hud: { label: 'IN THE SUN', unit: ' °C', decimals: 0, sub: ck(0), subAt },
    counter: [[0, 24], [at('heat').s + 3, 30], [at('heat').e, 35], [climax, 36], [climax + 4, 31], [at('noon').s, 33], [T_END, 37]],
    range: [20, 40],
    captions: [[at('ropes').s + 1, at('ropes').e + .5, '240 masts'], [at('velarium').s, at('velarium').s + 3, 'The velarium']],
    shots: [[0, 'bowl'], [at('heat').s - .2, 'pov-seat'], [at('shade').s - .2, 'reveal'], [at('sailors').s - .2, 'attic'],
            [at('ropes').s - .2, 'sky'], [at('sail').s + 2, 'pov-up'], [at('velarium').s - .2, 'bowl'], [at('hunt').s - .2, 'reveal'],
            [at('hear').s + 2.5, 'pov-seat'], [at('noon').s - .2, 'aerial'], [at('stairs').s - .2, 'reveal']],
    panic: at('stairs').s - .2,
    beats: { climax, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { crowd: [[0, .55], [T_END, .7]], roars: [[at('hunt').e - .5, .7], [roar, 1.3], [roar + 9, .6]], riser: [at('ropes').s, climax] },
    end: { title: '', lines: '' },
  };
}
export const upload = { title: '', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
