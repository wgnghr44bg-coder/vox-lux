// What if the Sun went out? Long video (owner's script), chapter 4: the frozen coast, year 100 -> year 1,000.
export const topic = {
  number: 414, slug: 'sun-c4-coast', place: 'boulevard', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['y100', 'Year one hundred.', 'pause'],
  ['waste', 'A hundred years later, the surface is a frozen wasteland.', 'pause'],
  ['no', 'No sunlight. No forests. No normal ecosystems.', 'pause'],
  ['dark', 'Just darkness and ice.', 'long'],
  ['deep', 'Yet deep beneath the oceans, life could still survive.', 'pause'],
  ['vents', "Because some organisms don't need sunlight at all. They live on heat and chemicals from deep inside the Earth.", 'pause'],
  ['continue', 'So even without the Sun, life might continue.', 'pause'],
  ['know', 'Just not the life we know.', 'long'],
  ['y1000', 'Year one thousand.', 'pause'],
  ['drifting', 'Earth would now be a frozen planet, drifting silently through space.', 'long'],
  ['most', 'And that is perhaps the most terrifying part.', 'pause'],
  ['notexplode', "The Earth wouldn't explode. Humanity wouldn't disappear instantly.", 'pause'],
  ['freeze', 'The planet would simply, slowly, freeze.', 6],
  ['memory', 'Until almost everything we know became a memory.', 'long'],
  ['question', 'So if the Sun disappeared tomorrow, how long do you think humanity would actually survive?', 'none'],
];

export default function (at) {
  const climax = at('freeze').e + .4, T_END = at('question').e + 4.6;
  return {
    T_END, tripod: true, brand: false, sunbathers: 0,
    hud: { label: 'YEARS WITHOUT THE SUN', unit: '', decimals: 0 },
    counter: [[0, 100], [at('know').e, 100], [at('y1000').s, 300], [at('y1000').e + .3, 1000], [T_END, 1000]],
    range: [0, 100], forceParams: { darkAt: [-1, 0], frostAt: [-1, 0], snow: 0 },
    captions: [[at('y100').s, at('y100').e + .8, 'Year 100.'], [at('vents').s, at('vents').e + .4, 'Life without sunlight.'],
               [at('y1000').s, at('y1000').e + .8, 'Year 1,000.']],
    shots: [[0, 'sea'], [at('waste').s - .2, 'beach'], [at('no').s - .2, 'boulevard'], [at('dark').s - .2, 'sea'],
            [at('deep').s - .2, 'sea'], [at('vents').s - .2, 'hotels'], [at('know').s - .2, 'beach'],
            [at('y1000').s - .2, 'beach'], [at('drifting').s - .2, 'sea'], [at('most').s - .2, 'hotels'],
            [at('notexplode').s - .2, 'boulevard'], [at('freeze').s - .2, 'hotels'], [climax + 2.8, 'sea'],
            [at('question').s - .2, 'sea']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, climax, falls: [], stop: at('question').s - 1, dark: at('question').s - .5, end: at('question').e + .3, fade: 1e9 },
    audio: { heartbeat: [at('most').s, climax + 2], riser: [at('notexplode').s, climax] },
    end: { title: 'What if<br>the Sun went out?', lines: 'How long would humanity survive?' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
