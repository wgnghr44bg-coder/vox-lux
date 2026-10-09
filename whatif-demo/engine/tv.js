// TV NEWS (baksteen "Tv-nieuws", okt 2026): one live channel (a canvas) that every screen in the scene shows,
// and the screens themselves (flat TV on a stand, video wall, shop-window TVs). Any place.
// TL.tv = {
//   images: { name: url },        // pictures the channel can show (e.g. a still of another chapter), relative to engine/
//   feed: [[t, mode, opts], ...]  // what is on air from t on. mode: 'news' (picture + BREAKING NEWS band + ticker),
//                                 //   'market' (red chart, big text), 'nosignal', 'black', 'text' (big centred text)
//                                 //   opts: { img, headline, ticker, text, zoom, live }
//   channel: 'WORLD NEWS 24',
// }
// Use: const ch = channel(E, TL); screen(E, ch, { w, h, pos, ry, frame }) / tvSet(E, ch, { x, y, z, ry, size }).
import * as THREE from 'three';
import { smooth, clamp } from './util.js';

export function channel(E, TL) {
  if (E.tvChannel) return E.tvChannel;
  const T = TL.tv || {}, W = 640, H = 360;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
  const imgs = {};
  for (const [k, url] of Object.entries(T.images || {})) {
    const im = new Image(); imgs[k] = im;
    (E.loading ||= []).push(new Promise(ok => { im.onload = ok; im.onerror = ok; im.src = url; }));
  }
  const feed = (T.feed || [[0, 'news', {}]]).slice().sort((a, b) => a[0] - b[0]);
  const at = t => { let f = feed[0], i = 0; feed.forEach((x, k) => { if (t >= x[0]) { f = x; i = k; } }); return { mode: f[1], o: f[2] || {}, t0: f[0], i }; };
  const font = (s, w = 700) => `${w} ${s}px "Inter", "Helvetica Neue", Arial, sans-serif`;
  let last = -1;
  function draw(t) {
    const fr = Math.round(t * 15); if (fr === last) return; last = fr;          // 15 updates a second is plenty for a TV
    const { mode, o, t0 } = at(t), a = t - t0;
    c.fillStyle = '#000'; c.fillRect(0, 0, W, H);
    if (mode === 'black') { tex.needsUpdate = true; return; }
    if (mode === 'nosignal') {
      const bars = ['#c0c0c0', '#c0c000', '#00c0c0', '#00c000', '#c000c0', '#c00000', '#0000c0'];
      bars.forEach((b, i) => { c.fillStyle = b; c.fillRect(i * W / 7, 0, W / 7 + 1, H * .72); });
      c.fillStyle = '#111'; c.fillRect(0, H * .72, W, H * .28);
      c.fillStyle = '#fff'; c.font = font(34); c.textAlign = 'center'; c.fillText(o.text || 'NO SIGNAL', W / 2, H * .88);
      tex.needsUpdate = true; return;
    }
    if (mode === 'market') {
      c.fillStyle = '#0d1420'; c.fillRect(0, 0, W, H);
      c.strokeStyle = '#26324a'; c.lineWidth = 1; for (let y = 60; y < H - 60; y += 40) { c.beginPath(); c.moveTo(30, y); c.lineTo(W - 30, y); c.stroke(); }
      c.strokeStyle = '#e0453a'; c.lineWidth = 4; c.beginPath();
      const n = 60, k = clamp(a / 3);
      for (let i = 0; i <= n * k; i++) { const x = 30 + i / n * (W - 60), y = 80 + (i / n) ** 2 * 170 + Math.sin(i * 1.7) * 6; i ? c.lineTo(x, y) : c.moveTo(x, y); }
      c.stroke();
      c.fillStyle = '#e0453a'; c.font = font(44, 800); c.textAlign = 'center'; c.fillText(o.text || 'TRADING HALTED', W / 2, H - 40);
      c.fillStyle = '#9fb0c8'; c.font = font(22, 600); c.fillText(o.sub || 'MARKETS WORLDWIDE', W / 2, 44);
      tex.needsUpdate = true; return;
    }
    if (mode === 'text') {
      c.fillStyle = '#0e1622'; c.fillRect(0, 0, W, H); c.fillStyle = '#fff'; c.font = font(40, 800); c.textAlign = 'center';
      (o.text || '').split('\n').forEach((l, i, A) => c.fillText(l, W / 2, H / 2 + (i - (A.length - 1) / 2) * 50 + 14));
      tex.needsUpdate = true; return;
    }
    // news: picture (slow push-in), red band, headline, ticker, LIVE badge, channel name
    const im = imgs[o.img];
    if (im && im.width) {
      const z = 1 + (o.zoom ?? .06) * clamp(a / 12), w = W * z, h = w * im.height / im.width;
      c.drawImage(im, (W - w) / 2, (H - h) / 2, w, h);
    } else { c.fillStyle = '#334'; c.fillRect(0, 0, W, H); }
    const band = H - 92;
    c.fillStyle = '#b3201b'; c.fillRect(0, band, 230, 34);
    c.fillStyle = '#fff'; c.font = font(22, 800); c.textAlign = 'left'; c.fillText('BREAKING NEWS', 14, band + 25);
    c.fillStyle = 'rgba(245,245,245,.95)'; c.fillRect(0, band + 34, W, 38);
    c.fillStyle = '#121212'; c.font = font(25, 800); c.fillText(o.headline || '', 14, band + 62);
    c.fillStyle = '#1d2433'; c.fillRect(0, H - 20, W, 20);
    const tick = (o.ticker || '') + '   •   ', tw = (c.font = font(14, 600), c.measureText(tick).width);
    c.fillStyle = '#e8e8e8'; for (let x = -((t * 70) % tw); x < W; x += tw) c.fillText(tick, x, H - 5);
    if (o.live !== false && Math.sin(t * 4) > -.6) { c.fillStyle = '#d42a22'; c.fillRect(W - 86, 14, 70, 28); c.fillStyle = '#fff'; c.font = font(18, 800); c.fillText('LIVE', W - 72, 35); }
    c.fillStyle = 'rgba(255,255,255,.85)'; c.font = font(15, 700); c.fillText(T.channel || 'WORLD NEWS 24', 16, 30);
    tex.needsUpdate = true;
  }
  const ch = { tex, draw, at };
  E.updates.push((t, F, tv) => draw(tv));
  E.tvChannel = ch; return ch;
}

const screenMat = tex => new THREE.MeshBasicMaterial({ map: tex, toneMapped: false });

// a bare screen (video wall, shop TV) with an optional dark frame; pos = centre, ry = facing
export function screen(E, ch, o) {
  const g = new THREE.Group(); g.position.set(...o.pos); g.rotation.y = o.ry ?? 0; (o.parent ?? E.scene).add(g);
  if (o.frame !== false) { const f = new THREE.Mesh(new THREE.BoxGeometry(o.w + .06, o.h + .06, .06), E.lam(0x18191b)); f.position.z = -.035; g.add(f); }
  const s = new THREE.Mesh(new THREE.PlaneGeometry(o.w, o.h), screenMat(ch.tex)); s.position.z = .002; g.add(s);
  if (o.glow) { const L = new THREE.PointLight(0x9fc4ff, o.glow, Math.max(o.w, o.h) * 3, 1.6); L.position.z = .6; g.add(L);
    E.updates.push((t, F, tv) => { L.intensity = ch.at(tv).mode === 'black' ? 0 : o.glow; }); }   // TV light on the faces in the room
  return g;
}

// a flat TV on a low cabinet (living room) or on its own foot; size = screen width in m
export function tvSet(E, ch, o) {
  const s = o.size ?? 1.2, h = s * 9 / 16, g = new THREE.Group(); g.position.set(o.x, o.y ?? 0, o.z); g.rotation.y = o.ry ?? 0; E.scene.add(g);
  if (o.cabinet !== false) { const cab = E.shadowed(new THREE.Mesh(new THREE.BoxGeometry(s * 1.4, .45, .42), E.lam(o.wood ?? 0x5b4636))); cab.position.y = .225; g.add(cab); }
  const foot = new THREE.Mesh(new THREE.BoxGeometry(.3, .04, .2), E.lam(0x1d1e20)); foot.position.y = (o.cabinet === false ? 0 : .45) + .02; g.add(foot);
  const neck = new THREE.Mesh(new THREE.BoxGeometry(.06, .12, .04), E.lam(0x1d1e20)); neck.position.y = foot.position.y + .08; g.add(neck);
  screen(E, ch, { w: s, h, pos: [0, neck.position.y + .06 + h / 2, 0], glow: o.glow ?? 2.5, parent: g });
  return g;
}
