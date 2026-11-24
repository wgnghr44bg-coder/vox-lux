// Neemt scene.html beeld voor beeld op (30 fps) naar frames/00000.jpg ...  node render.mjs [poort] [alleen-tijden,komma]
import puppeteer from '../node_modules/puppeteer-core/lib/esm/puppeteer/puppeteer-core.js';
import fs from 'fs';
const poort = process.argv[2] || 8781, los = process.argv[3];
const browser = await puppeteer.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true,
  args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage(); await page.setViewport({ width: 1080, height: 1920 });
page.on('console', m => console.log('[pagina]', m.text())); page.on('pageerror', e => console.log('[FOUT]', e.message));
await page.goto(`http://127.0.0.1:${poort}/proef-goud/scene.html`); await page.waitForFunction('window.klaar === true', { timeout: 120000 });
const D = JSON.parse(fs.readFileSync(new URL('./data.json', import.meta.url))); fs.mkdirSync(new URL('./frames/', import.meta.url), { recursive: true });
const tijden = los ? los.split(',').map(Number) : [...Array(Math.ceil(D.EIND * 30)).keys()].map(i => i / 30);
const t0 = Date.now();
for (const [i, t] of tijden.entries()) {
  const url = await page.evaluate(t => window.render(t), t);
  const naam = los ? `test_${String(t).replace('.', '_')}.jpg` : String(i).padStart(5, '0') + '.jpg';
  fs.writeFileSync(new URL('./frames/' + naam, import.meta.url), Buffer.from(url.split(',')[1], 'base64'));
  if (i % 60 === 0) console.log(`${i}/${tijden.length}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
}
console.log('KLAAR', tijden.length, 'beelden'); await browser.close();
