// Generic renderer for the What if engine (Playwright + Chromium + ffmpeg).
//   node engine/render.mjs <slug> stills 5 30 45        -> topics/<slug>/stills/still-<t>.jpg
//   node engine/render.mjs <slug> timeline              -> topics/<slug>/timeline.json (TL + EVENTS + AUDIO)
//   node engine/render.mjs <slug> video out.mp4 [workers] [from]     (TO=60 renders only up to 60 s, e.g. a preview)
//   node engine/render.mjs preview:<place>:<force> stills ...   (no topic; writes to engine/previews/)
import { createRequire } from 'module';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn, execSync } from 'child_process';
import { fileURLToPath } from 'url';

// Playwright: local node_modules, the cloud's global install, or the global npm folder (Windows pc: npm i -g playwright)
function loadPlaywright() {
  const roots = [import.meta.url, '/opt/node22/lib/node_modules/'];
  try { roots.push(path.join(execSync('npm root -g', { encoding: 'utf8', shell: true }).trim(), '/')); } catch {}
  for (const r of roots) { try { return createRequire(r)('playwright'); } catch {} }
  throw new Error('Playwright not found: run  npm install -g playwright  and  npx playwright install chromium');
}
const { chromium } = loadPlaywright();
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));   // whatif-demo/ (also C:\\... on Windows)
// Default: software WebGL (SwiftShader), identical on every machine. WHATIF_GPU=1 uses the graphics card (faster, may differ slightly).
const GL_ARGS = process.env.WHATIF_GPU === '1' ? ['--ignore-gpu-blocklist', '--use-angle=default'] : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
const FPS = 30;
const [slug, mode, ...rest] = process.argv.slice(2);
let query, OUT;
if (slug.startsWith('preview:')) {
  const [, place, force, shots] = slug.split(':');
  query = `place=${place}&force=${force}` + (shots ? `&shots=${encodeURIComponent(shots)}` : '');
  OUT = path.join(ROOT, 'engine', 'previews', `${place}-${force}`);
} else { const [s, flag] = slug.split('+'); query = `topic=${s}` + (flag === 'hook' ? '&hook=1' : ''); OUT = path.join(ROOT, 'topics', s); }
const WIDE = /\bwide:\s*true/.test(slug.startsWith('preview:') ? '' : fs.readFileSync(path.join(OUT, 'scenario.js'), 'utf8')) || process.env.WIDE === '1';
if (WIDE) query += '&wide=1';
fs.mkdirSync(OUT, { recursive: true });

const types = { '.png': 'image/png', '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.woff2': 'font/woff2' };
const server = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(f).pipe(r);
}).listen(0);
const port = server.address().port;

async function open(w = WIDE ? 1280 : 720, h = WIDE ? 720 : 1280) {
  const browser = await chromium.launch({ args: GL_ARGS });
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.setDefaultTimeout(600000);
  page.on('console', m => { if (!/GPU stall|WebGL/.test(m.text())) console.log('page:', m.text()); });
  page.on('pageerror', e => { console.log('ERR', e.message, e.stack?.split('\n')[1] || ''); if (!page.isReady) process.exit(1); });
  await page.goto(`http://localhost:${port}/engine/scene.html?${query}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 300000 });
  return { browser, page };
}

if (mode === 'stills') {
  const { browser, page } = await open();
  fs.mkdirSync(path.join(OUT, 'stills'), { recursive: true });
  if (process.env.NOHUD) await page.addStyleTag({ content: '#hud,#cap,#title{visibility:hidden!important}' });   // clean picture (e.g. a TV feed)
  for (const t of rest) {
    const t0 = Date.now();
    const n = await page.evaluate(t => window.renderAt(+t, window.blurAt ? window.blurAt(+t) : 1), t);
    await page.screenshot({ path: path.join(OUT, 'stills', `still-${t}.jpg`), type: 'jpeg', quality: 88 });
    console.log('still', t, 'particles', n, 'look', await page.evaluate(t => window.camTarget?.(+t), t), (Date.now() - t0) + 'ms');
  }
  await browser.close();
} else if (mode === 'timeline') {
  const { browser, page } = await open();
  const data = await page.evaluate(() => ({ TL: window.TL, EVENTS: window.EVENTS, AUDIO: window.AUDIO }));
  fs.writeFileSync(path.join(OUT, 'timeline.json'), JSON.stringify(data));
  console.log('events', data.EVENTS.length, 'T_END', data.TL.T_END);
  await browser.close();
} else if (mode === 'video') {
  const out = rest[0], workers = +(rest[1] || 3), from = Math.round(+(rest[2] || 0) * FPS);
  const probe = await open();
  const tEnd = await probe.page.evaluate(() => window.T_END);
  await probe.browser.close();
  const frames = Math.round(Math.min(tEnd, +(process.env.TO || 1e9)) * FPS), per = Math.ceil((frames - from) / workers), t0 = Date.now();
  const segs = [];
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const a = from + w * per, b = Math.min(frames, a + per), seg = `${out}.part${w}.mp4`; segs[w] = seg;
    const { browser, page } = await open();
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = a; i < b; i++) {
      await page.evaluate(t => window.renderAt(t, window.blurAt ? window.blurAt(t) : 1), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((i - a) % 150 === 0) console.log(`w${w} frame ${i - a}/${b - a}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close();
  }));
  fs.writeFileSync(`${out}.list`, segs.map(s => `file '${path.resolve(s)}'`).join('\n'));
  await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', `${out}.list`, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
  segs.forEach(s => fs.unlinkSync(s)); fs.unlinkSync(`${out}.list`);
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
}
server.close();
