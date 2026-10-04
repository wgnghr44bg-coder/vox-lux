// node render.mjs stills 5 30 45 58 70 82      -> stills/still-<t>.jpg
// node render.mjs thumb [t]                    -> thumbnail.jpg (1080x1920, frame t, default 0)
// node render.mjs timeline                     -> timeline.json (TL + physics events, used by make_audio.py)
// node render.mjs video out.mp4 [workers] [from] -> silent mp4 (720x1280, 30 fps), frames split over workers;
//                                                 from = start second (re-render only the tail)
import { createRequire } from 'module';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const HERE = path.dirname(new URL(import.meta.url).pathname);
const ROOT = path.dirname(HERE);                    // whatif-demo/ (node_modules lives there)
const PAGE = `/${path.basename(HERE)}/scene.html`;
const FPS = 30;
const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const server = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(r);
}).listen(0);
const port = server.address().port;

async function open(scale = 1) {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: scale });
  page.on('console', m => console.log('page:', m.text()));
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto(`http://localhost:${port}${PAGE}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
  return { browser, page };
}

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'stills') {
  const { browser, page } = await open();
  fs.mkdirSync(path.join(HERE, 'stills'), { recursive: true });
  for (const t of rest) {
    const t0 = Date.now();
    const n = await page.evaluate(t => window.renderAt(+t), t);
    await page.screenshot({ path: path.join(HERE, 'stills', `still-${t}.jpg`), type: 'jpeg', quality: 88 });
    console.log('still', t, 'particles', n, (Date.now() - t0) + 'ms');
  }
  await browser.close();
} else if (mode === 'thumb') {
  const { browser, page } = await open(1.5);
  await page.evaluate(t => window.renderAt(+t), rest[0] || 0);
  await page.screenshot({ path: path.join(HERE, 'thumbnail.jpg'), type: 'jpeg', quality: 92 });
  console.log('thumbnail.jpg');
  await browser.close();
} else if (mode === 'timeline') {
  const { browser, page } = await open();
  const data = await page.evaluate(() => ({ TL: window.TL, EVENTS: window.EVENTS }));
  fs.writeFileSync(path.join(HERE, 'timeline.json'), JSON.stringify(data, null, 1));
  console.log('events', data.EVENTS.length);
  await browser.close();
} else {
  const out = rest[0], workers = +(rest[1] || 2), from = Math.round(+(rest[2] || 0) * FPS);
  const probe = await open();
  const tEnd = await probe.page.evaluate(() => window.T_END);
  await probe.browser.close();
  const frames = Math.round(tEnd * FPS), per = Math.ceil((frames - from) / workers), t0 = Date.now();
  const segs = [];
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const a = from + w * per, b = Math.min(frames, a + per), seg = `${out}.part${w}.mp4`; segs[w] = seg;
    const { browser, page } = await open();
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = a; i < b; i++) {
      await page.evaluate(t => window.renderAt(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((i - a) % 90 === 0) console.log(`w${w} frame ${i - a}/${b - a}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close();
  }));
  fs.writeFileSync(`${out}.list`, segs.map(s => `file '${path.resolve(s)}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${out}.list`, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
  segs.forEach(s => fs.unlinkSync(s)); fs.unlinkSync(`${out}.list`);
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
server.close();
