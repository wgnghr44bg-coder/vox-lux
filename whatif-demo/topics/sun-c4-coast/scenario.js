// What if the Sun went out? Long video (owner's script), chapter 4: the frozen coast, year 100 -> year 1,000.
export const topic = {
  number: 414, slug: 'sun-c4-coast', place: 'boulevard', force: 'cold', wide: true,
  question: 'What if the Sun went out?', title: '',
};

export const lines = [
  ['y100', 'Year one hundred.', 'none'],
  ['waste', 'A hundred years later, the surface is a frozen wasteland.', 'none'],
  ['no', 'No sunlight. No forests. No normal ecosystems.', 'none'],
  ['dark', 'Just darkness and ice.', 'pause'],
  ['deep', 'Yet deep beneath the oceans, life could still survive.', 'none'],
  ['vents', "Because some organisms don't need sunlight at all. They live on heat and chemicals from deep inside the Earth.", 'none'],
  ['continue', 'So even without the Sun, life might continue.', 'none'],
  ['know', 'Just not the life we know.', 'pause'],
  ['y1000', 'Year one thousand.', 'none'],
  ['drifting', 'Earth would now be a frozen planet, drifting silently through space.', 'pause'],
  ['most', 'And that is perhaps the most terrifying part.', 'none'],
  ['notexplode', "The Earth wouldn't explode. Humanity wouldn't disappear instantly.", 'none'],
  ['freeze', 'The planet would simply, slowly, freeze.', 3],
  ['memory', 'Until almost everything we know became a memory.', 'pause'],
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
    shots: [[0, 'sea'], [at('waste').s - .2, 'beach'], [at('deep').s - .2, 'sea'], [at('vents').s - .2, 'hotels'],
            [at('y1000').s - .2, 'beach'], [at('most').s - .2, 'hotels'], [at('freeze').s - .2, 'sea'], [climax + 1.5, 'beach'],
            [at('memory').s - .2, 'sea']],
    beats: { lookUp: 1e9, shelter: 0, carsStop: 0, powerOut: -1,   // year 100+: no lights left anywhere
             climax, falls: [], stop: at('question').s - 1, dark: at('question').s - .5, end: at('question').e + .3, fade: 1e9 },
    audio: { hiss: -40, ice: -32, heartbeat: [at('most').s, climax + 2], riser: [at('notexplode').s, climax] },
    end: { title: 'What if<br>the Sun went out?', lines: 'How long would humanity survive?' },
  };
}

export const upload = { title: 'What if the Sun went out?', description: 'Hoofdstuk 4, niet los uploaden.', tags: [], tiktok: '' };
