// What if aliens landed tomorrow? Chapter 2: breaking news (studio, living room, shop window), HOUR 1 -> HOUR 6.
import { lines as raw } from './lines.js';
import { split, group } from '../aliens-1-street/sentences.js';
export const lines = split(raw);
export const topic = {
  number: 502, slug: 'aliens-2-news', place: 'indoors', force: 'alien', wide: true,
  question: 'What if aliens landed tomorrow?', title: '',
};

export default function (at0) {
  const at = group(at0, lines);
  const black = at('black').s + .9, back = at('lower').s - .2, T_END = at('lower').e + 1.6;
  const tick = 'OBJECT ABOUT 3 KM WIDE HOVERING AT 2,000 M  •  AUTHORITIES URGE CALM  •  AIRSPACE CLOSED  •  NO CONTACT SO FAR';
  return {
    T_END, tripod: true, brand: false, showTitle: false, post: true,
    room: { people: 3 },
    groups: [{ at: [-60, 1.3], n: 8, face: Math.PI, spread: 2.8, lamp: false }],
    tv: {
      channel: 'WORLD NEWS 24',
      images: { under: '../topics/aliens-2-news/feed-under.jpg', road: '../topics/aliens-2-news/feed-road.jpg', sun: '../topics/aliens-2-news/feed-sun.jpg' },
      feed: [[0, 'news', { img: 'under', headline: 'UNKNOWN OBJECT OVER THE CITY', ticker: tick }],
             [at('phones').s, 'news', { img: 'sun', headline: 'PHONE NETWORKS OVERLOADED', ticker: tick }],
             [at('hour3').s + 1.2, 'market', { text: 'TRADING HALTED', sub: 'STOCK MARKETS WORLDWIDE' }],
             [at('shops').s, 'news', { img: 'road', headline: 'SHOPS EMPTIED WITHIN HOURS', ticker: tick }],
             [at('hour6').s, 'news', { img: 'under', headline: 'HOUR 6: NO MESSAGE. NO SOUND.', ticker: tick, zoom: .1 }],
             [black, 'black'],
             [back, 'news', { img: 'under', headline: 'THE SHIP IS DESCENDING', ticker: 'OBJECT NOW AT 1,600 M AND FALLING  •  STAY INDOORS', zoom: .5 }]],
    },
    hud: { label: 'SHIP ALTITUDE', unit: ' m', decimals: 0, sub: 'HOUR 1', subAt: [[0, 'HOUR 1'], [at('hour3').s, 'HOUR 3'], [at('hour6').s, 'HOUR 6']] },
    counter: [[0, 2000], [back, 2000], [T_END, 1600]], range: [12000, 0],
    forceParams: { shade: [[0, .55], [T_END, .6]] },
    ufo: { ships: [{ id: 'mother', kind: 'mother', r: 1400, haze: .55, keys: [[0, -4700, 760, -6500], [back, -4700, 760, -6500], [T_END, -4700, 600, -6500]] }] },
    captions: [[at('moon').s, at('moon').s + 3.5, 'Moon landing 1969: ± 600 million viewers']],
    shots: [[0, 'studio'], [at('moon').s - .2, 'sofa'], [at('phones').s - .2, 'faces'], [at('phones').s + 3.2, 'tv'],
            [at('hour3').s - .2, 'anchor'], [at('hour3').s + 3.4, 'tv'], [at('shops').s - .2, 'shop'], [at('shops').s + 3.6, 'shop-close'],
            [at('hour6').s - .2, 'window'], [at('black').s - .2, 'sofa'], [back - .1, 'tv']],
    beats: { lookUp: at('hour6').s + .5, shelter: 1e9, climax: black, falls: [], stop: T_END + 1, fade: 1e9 },
    audio: { heartbeat: [at('hour6').s, black + 2], riser: [at('hour6').e, black] },
    end: { title: '', lines: '' },
  };
}

export const upload = { title: 'What if aliens landed tomorrow?', description: 'Hoofdstuk 2, niet los uploaden.', tags: [], tiktok: '' };
