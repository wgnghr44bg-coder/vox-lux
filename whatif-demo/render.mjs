// node render.mjs stills 0 8 15 22 28        -> still-<t>.jpg
// node render.mjs video out.mp4 [fps]          -> silent mp4 (720x1280)
import { createRequire } from 'module';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const ROOT = path.dirname(new URL(import.meta.url).pathname);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const server = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(r);
}).listen(0);
const port = server.address().port;

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 720, height: 1280 } });
page.on('console', m => console.log('page:', m.text()));
page.on('pageerror', e => console.log('ERR', e.message));
await page.goto(`http://localhost:${port}/scene.html`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });

const [mode, ...rest] = process.argv.slice(2);
if (mode === 'stills') {
  for (const t of rest) {
    const n = await page.evaluate(t => window.renderAt(+t), t);
    await page.screenshot({ path: path.join(ROOT, `still-${t}.jpg`), type: 'jpeg', quality: 88 });
    console.log('still', t, 'particles', n);
  }
} else {
  const out = rest[0], fps = +(rest[1] || 30);
  const tEnd = await page.evaluate(() => window.T_END);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(tEnd * fps), t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.renderAt(t), i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log(`frame ${i}/${frames}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
}
await browser.close();
server.close();
