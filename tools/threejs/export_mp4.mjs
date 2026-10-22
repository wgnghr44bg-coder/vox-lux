// Renders a timeline page (?render=1) frame by frame to MP4, with its generated soundtrack.
// Needs: node + playwright (npm i playwright), Chromium, ffmpeg on PATH.
//   node tools/threejs/export_mp4.mjs tools/threejs/never-stopped-raining.html out.mp4 [--fps 30] [--width 1080] [--from 0] [--to 80] [--three node_modules/three]
// Standing 9:16 by default (1080x1920). --landscape renders 16:9 (default 1920x1080); --height sets any other height.
// --three serves three.js from a local copy instead of the CDN (for machines without internet access to jsdelivr).
// --gpu uses the real graphics card (on a pc); without it Chromium renders in software (cloud machines).
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : def; };
const flags = ['--gpu', '--landscape'];
const [page_, out] = args.filter((a, i) => !a.startsWith('--') && !(args[i - 1]?.startsWith('--') && !flags.includes(args[i - 1])));
const landscape = args.includes('--landscape');
const fps = +opt('fps', 30), width = +opt('width', landscape ? 1920 : 1080), height = +opt('height', Math.round(landscape ? width * 9 / 16 : width * 16 / 9));
const three = opt('three', null), exe = opt('chromium', process.env.CHROMIUM_PATH);

const gpu = args.includes('--gpu');
const browser = await chromium.launch({ executablePath: exe, headless: !gpu, args: gpu ? ['--ignore-gpu-blocklist', '--enable-gpu'] : ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width, height } });
page.on('pageerror', e => console.error('page error:', e.message));
if (three) await page.route('**/cdn.jsdelivr.net/npm/three@*/**', r => r.fulfill({ path: path.join(three, r.request().url().split(/three@[^/]+\//)[1]), contentType: 'application/javascript' }));
await page.goto(pathToFileURL(path.resolve(page_)).href + '?render=1');
await page.waitForFunction(() => window.renderReady === true, null, { timeout: 120000 });
await page.evaluate(() => document.fonts.ready);
const duration = +opt('to', await page.evaluate(() => +document.getElementById('scrub').max));
const from = +opt('from', 0);

// soundtrack first (fast), then the frames
const wav = out.replace(/\.mp4$/, '') + '-sfx.wav';
fs.writeFileSync(wav, Buffer.from(await page.evaluate(() => window.renderSoundtrack()), 'base64'));
console.log('soundtrack:', wav);

const stage = await page.$('#stage'), box = await stage.boundingBox();
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-ss', String(from), '-i', wav, '-t', String(duration - from),
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(fps),
  '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const total = Math.round((duration - from) * fps), t0 = Date.now();
for (let i = 0; i < total; i++) {
  await page.evaluate(t => window.renderAt(t), from + i / fps);
  const jpg = await page.screenshot({ type: 'jpeg', quality: 92, clip: box });
  if (!ff.stdin.write(jpg)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % fps === 0) { const s = (Date.now() - t0) / 1000; console.log(`frame ${i}/${total}  ${(s / (i + 1)).toFixed(2)} s/frame  ~${Math.round(s / (i + 1) * (total - i) / 60)} min left`); }
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log('done:', out);
