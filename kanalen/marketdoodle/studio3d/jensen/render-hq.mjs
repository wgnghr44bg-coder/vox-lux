// CEO-proef (27 nov): scene.html in Edge op 270x480, PNG per beeldje, ffmpeg schaalt met 'neighbor' (scherpe pixels) naar 1080x1920.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import puppeteer from 'puppeteer-core';
const HIER = path.dirname(new URL(import.meta.url).pathname).replace(/^\/([A-Z]:)/, '$1');
const ROOT = path.dirname(HIER);
const TYPE = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, data) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': TYPE[path.extname(p)] || 'application/octet-stream' }); res.end(data); });
}).listen(0);
const poort = server.address().port;
const browser = await puppeteer.launch({ executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless: 'new',
  args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-webgl', '--no-sandbox'] });
const page = await browser.newPage();
page.on('console', m => console.log('[pagina]', m.text())); page.on('pageerror', e => console.log('[FOUT]', e.message));
await page.setViewport({ width: 1080, height: 1920 });
await page.goto(`http://127.0.0.1:${poort}/jensen/scene-hq.html`);
await page.waitForFunction('window.klaar === true', { timeout: 60000 });
const D = JSON.parse(fs.readFileSync(path.join(HIER, 'data.json'), 'utf8'));
const n = Math.floor(D.EIND * D.FPS);
const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'png', '-r', String(D.FPS), '-i', '-', '-i', path.join(HIER, 'stem.wav'),
  '-filter_complex', '[0:v]scale=1080:1920:flags=neighbor[v];[1:a]apad,loudnorm=I=-14:TP=-1.5[a]', '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '160k', '-shortest', path.join(HIER, 'jensen-proef-hq.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i < n; i++) {
  const url = await page.evaluate(t => window.render(t), i / D.FPS);
  if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await browser.close(); server.close(); console.log('KLAAR jensen-proef-hq.mp4');
