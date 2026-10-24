// Quality check before (and after) rendering: a screenshot every second (or --step), all console errors/warnings
// per time, and contact sheets (10 per row, 4 rows per sheet) to look through for glitches.
//   node tools/threejs/check_frames.mjs <page.html> <out-folder> [--step 1] [--from 0] [--to <end>] [--width 360] [--times 3,7.5] [--three node_modules/three]
//   node tools/threejs/check_frames.mjs --video <video.mp4> <out-folder> [--step 1]      (contact sheets from a finished MP4)
// Needs playwright (npm i playwright) and ffmpeg. On a cloud machine: CHROMIUM_PATH=/opt/pw-browsers/chromium.
import fs from 'node:fs'; import path from 'node:path'; import { pathToFileURL } from 'node:url'; import { execFileSync } from 'node:child_process';
const args = process.argv.slice(2), opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const pos = args.filter((a, i) => !a.startsWith('--') && !args[i - 1]?.startsWith('--'));
const video = opt('video', null), [pg, out] = video ? [null, pos[0]] : pos;
fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const step = +opt('step', 1);
const ff = a => execFileSync('ffmpeg', ['-v', 'error', '-y', ...a]);
if (video) {
  ff(['-i', video, '-vf', `fps=1/${step},scale=360:-1`, path.join(out, 'frames', 'f%04d.jpg')]);
} else {
  const { chromium } = await import('playwright');
  const width = +opt('width', 360), height = Math.round(width * 16 / 9), three = opt('three', null);
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width, height } });
  let cur = 'load', problems = 0;
  page.on('console', m => { if (['error', 'warning'].includes(m.type()) && !m.text().includes('ERR_FAILED')) { problems++; console.log(`[t=${cur}] ${m.type()}: ${m.text().slice(0, 300)}`); } });
  page.on('pageerror', e => { problems++; console.log(`[t=${cur}] pageerror: ${e.message}`); });
  if (three) await page.route('**/cdn.jsdelivr.net/npm/three@*/**', r => r.fulfill({ path: path.join(three, r.request().url().split(/three@[^/]+\//)[1]), contentType: 'application/javascript' }));
  await page.route('**/fonts.googleapis.com/**', r => r.abort());
  await page.goto(pathToFileURL(path.resolve(pg)).href + '?render=1');
  await page.waitForFunction(() => window.renderReady === true, null, { timeout: 120000 });
  const end = +opt('to', await page.evaluate(() => +document.getElementById('scrub').max));
  let times = opt('times', null)?.split(',').map(Number);
  if (!times) { times = []; for (let t = +opt('from', 0); t <= end + 1e-6; t += step) times.push(+t.toFixed(2)); }
  const box = await (await page.$('#stage')).boundingBox();
  for (const [i, t] of times.entries()) { cur = t; await page.evaluate(t => window.renderAt(t), t); await page.screenshot({ path: path.join(out, 'frames', `f${String(i + 1).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 80, clip: box }); }
  await browser.close();
  fs.writeFileSync(path.join(out, 'times.txt'), times.join('\n') + '\n');
  console.log(problems ? `${problems} console problems (see above)` : 'no console errors or warnings');
}
// contact sheets: 40 frames each, the time in the corner
const files = fs.readdirSync(path.join(out, 'frames')).filter(f => f.endsWith('.jpg')).sort();
const times = fs.existsSync(path.join(out, 'times.txt')) && !video ? fs.readFileSync(path.join(out, 'times.txt'), 'utf8').trim().split('\n') : files.map((_, i) => (i * step).toFixed(1));
for (let s = 0; s * 40 < files.length; s++) {
  const part = files.slice(s * 40, s * 40 + 40), inputs = [], filters = [];
  part.forEach((f, i) => { inputs.push('-i', path.join(out, 'frames', f)); filters.push(`[${i}:v]scale=240:-2,drawtext=text='${times[s * 40 + i]}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6[v${i}]`); });
  const cols = 10, rows = Math.ceil(part.length / cols);
  const layout = part.map((_, i) => `${(i % cols) * 240}_${Math.floor(i / cols) * 427}`).join('|');
  ff([...inputs, '-filter_complex', `${filters.join(';')};${part.map((_, i) => `[v${i}]`).join('')}xstack=inputs=${part.length}:layout=${layout}:fill=black`, '-frames:v', '1', path.join(out, `sheet${s + 1}.jpg`)]);
}
console.log(`${files.length} frames -> ${out}/sheet*.jpg`);
