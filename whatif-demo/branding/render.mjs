// node branding/render.mjs  -> branding/profielfoto.png (800x800) + branding/banner.png (2560x1440)
import { createRequire } from 'module';
import http from 'http'; import fs from 'fs'; import path from 'path';
const require = createRequire('/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const HERE = path.dirname(new URL(import.meta.url).pathname), ROOT = path.dirname(HERE);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const server = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(0);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
for (const [mode, w, h, out] of [['avatar', 800, 800, 'profielfoto.png'], ['banner', 2560, 1440, 'banner.png']]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto(`http://localhost:${server.address().port}/branding/branding.html?mode=${mode}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
  await page.screenshot({ path: path.join(HERE, out) }); console.log(out);
}
await browser.close(); server.close();
