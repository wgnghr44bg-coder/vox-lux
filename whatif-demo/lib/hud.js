// Shared HUD / titles / captions / end card in the earth-stops style (fonts from ../node_modules).
//   import { makeHud } from '../lib/hud.js';
//   const hud = makeHud(TL);              // TL.title, titleIn/Out, hud{label,sub}, captions, beats.end/fade, end{title,lines}
//   hud(t, { num: '75%', second: 'PEOPLE ONLINE  4.1 billion', secondOpacity, hudOpacity, black });
const CSS = `
@font-face { font-family: PF; font-weight: 600; font-style: normal; src: url(../node_modules/@fontsource/playfair-display/files/playfair-display-latin-600-normal.woff2); }
@font-face { font-family: PF; font-weight: 600; font-style: italic; src: url(../node_modules/@fontsource/playfair-display/files/playfair-display-latin-600-italic.woff2); }
@font-face { font-family: CG; font-weight: 600; src: url(../node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-600-normal.woff2); }
html, body { margin: 0; width: 720px; height: 1280px; overflow: hidden; background: #000; }
canvas { display: block; }
#haze { position: absolute; inset: 0; background: #6e604f; opacity: 0; }
#shade { position:absolute;left:0;top:0;width:720px;height:520px;background:radial-gradient(ellipse 520px 320px at 120px 230px, rgba(0,0,0,.32), rgba(0,0,0,0)) }
#black { position: absolute; inset: 0; background: #050505; opacity: 0; }
#hud { position: absolute; left: 40px; top: 150px; color: #f3ede2; text-shadow: 0 2px 10px rgba(0,0,0,.6), 0 0 3px rgba(0,0,0,.5); }
#lab { font: 600 24px CG, serif; letter-spacing: 6px; opacity: .85; }
#num { font: 600 64px PF, serif; line-height: 1.05; }
#sub { font: 600 23px CG, serif; letter-spacing: 6px; opacity: .9; min-height: 24px; }
#second { font: 600 25px CG, serif; letter-spacing: 5px; opacity: 0; margin-top: 10px; }
#cap { position: absolute; left: 0; right: 0; top: 760px; text-align: center; color: #f6f1e7;
       font: 600 italic 42px PF, serif; text-shadow: 0 3px 14px rgba(0,0,0,.55); padding: 0 60px; }
#title { position: absolute; left: 0; right: 0; top: 400px; text-align: center; color: #f3ede2;
       font: 600 60px PF, serif; line-height: 1.15; text-shadow: 0 3px 16px rgba(0,0,0,.45); }
#end { position: absolute; left: 0; right: 0; top: 500px; text-align: center; color: #f3ede2; opacity: 0; padding: 0 50px; }
#endT { font: 600 italic 54px PF, serif; line-height: 1.18; text-shadow: 0 3px 16px rgba(0,0,0,.6); }
#endS { font: 600 27px CG, serif; line-height: 1.45; margin-top: 34px; opacity: .82; letter-spacing: .5px; }
#fade { position: absolute; inset: 0; background: #000; opacity: 0; }`;
const HTML = `<div id="haze"></div><div id="shade"></div><div id="black"></div>
<div id="hud"><div id="lab"></div><div id="num"></div><div id="sub"></div><div id="second"></div></div>
<div id="title"></div><div id="cap"></div><div id="end"><div id="endT"></div><div id="endS"></div></div><div id="fade"></div>`;

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
export const $ = id => document.getElementById(id);

export function makeHud(TL) {
  const st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
  document.body.insertAdjacentHTML('beforeend', HTML);
  $('title').innerHTML = TL.title; $('endT').innerHTML = TL.end.title; $('endS').innerHTML = TL.end.lines;
  $('lab').textContent = TL.hud.label; $('sub').textContent = TL.hud.sub;
  return (t, o) => {
    $('num').textContent = o.num;
    $('second').textContent = o.second || ''; $('second').style.opacity = o.secondOpacity ?? 0;
    $('hud').style.opacity = o.hudOpacity ?? smooth(.4, 1.4, t);
    $('title').style.opacity = smooth(TL.titleIn, TL.titleIn + 1, t) * (1 - smooth(TL.titleOut - 1.2, TL.titleOut, t));
    let ct = '', ca = 0;
    for (const [a, b, s] of TL.captions) if (t >= a - .1 && t <= b + .1) { ct = s; ca = smooth(a, a + .6, t) * (1 - smooth(b - .6, b, t)); }
    $('cap').textContent = ct; $('cap').style.opacity = ca;
    $('end').style.opacity = smooth(TL.beats.end, TL.beats.end + 1.4, t);
    $('fade').style.opacity = smooth(TL.beats.fade, TL.T_END - .15, t);
    $('black').style.opacity = o.black ?? 0;
    $('haze').style.opacity = o.haze ?? 0;
  };
}
