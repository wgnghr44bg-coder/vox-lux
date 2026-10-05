// Text layer: title, info block (top left) with counter, one key sentence at a time, end card.
import { smooth, monotone } from './util.js';

export function createHud(TL) {
  const $ = id => document.getElementById(id);
  const H = TL.hud, dec = H.decimals ?? 0;
  const fmt = (n, d = dec) => (Math.abs(n) < .5 * 10 ** -d ? 0 : n).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }).replace('-', '−');
  const counterAt = monotone(TL.counter);
  $('title').innerHTML = TL.title; $('endT').innerHTML = TL.end.title; $('endS').innerHTML = TL.end.lines;
  $('lab').textContent = H.label; $('sub').textContent = H.sub || '';
  const B = TL.beats;
  return {
    counterAt,
    update(t) {
      const v = counterAt(Math.min(t, B.stop));
      $('num').textContent = (H.prefix || '') + fmt(v) + (H.unit || '');
      if (H.second) {
        const S = H.second, v2 = S.fn ? S.fn(v) : (S.offset ?? 0) + (S.scale ?? 1) * v;
        $('second').textContent = `${S.label}  ${S.prefix || ''}${fmt(Math.max(S.min ?? 0, v2), S.decimals ?? 0)}${S.unit || ''}`;
        $('second').style.opacity = smooth(S.showAt ?? 0, (S.showAt ?? 0) + 1.5, t) * .85;
      }
      $('hud').style.opacity = smooth(.4, 1.4, t) * (1 - smooth(B.end - 1.6, B.end - .4, t)) * (TL.endStyle === 'card' ? 1 : 1 - smooth(B.fade - .5, B.fade + 1, t));
      // no title on screen by default: the voice opens with "Imagine …" (TL.showTitle to bring it back)
      $('title').style.opacity = TL.showTitle ? smooth(TL.titleIn, TL.titleIn + 1, t) * (1 - smooth(TL.titleOut - 1.2, TL.titleOut, t)) : 0;
      let ct = '', ca = 0;
      for (const [a, b, s] of TL.captions) if (t >= a - .1 && t <= b + .1 && (TL.endStyle === 'card' || a < B.fade - .5)) { ct = s; ca = smooth(a, a + .6, t) * (1 - smooth(b - .6, b, t)); }
      $('cap').textContent = ct; $('cap').style.opacity = ca;
      const style = TL.endStyle || 'fade', white = style === 'white', card = style === 'card';
      $('end').style.opacity = card ? smooth(B.end, B.end + 1.4, t) : 0;
      $('fade').style.background = white ? '#fffaf0' : '#000';
      $('fade').style.opacity = B.fade < TL.T_END ? smooth(B.fade, TL.T_END - (white ? .6 : .1), t) : 0;   // fade >= T_END: no fade (chapters of a long video)
      $('black').style.opacity = !card ? 0 : smooth(B.stop + .3, B.dark ?? B.end, t) * (TL.dim ?? .6) + smooth(B.end - 1, B.end + 1, t) * .3;
    },
  };
}
