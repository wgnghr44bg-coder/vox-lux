import { createRequire } from 'module'; const { chromium } = createRequire('/opt/node22/lib/node_modules/')('playwright'); import http from 'http'; import fs from 'fs'; import path from 'path';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, q.url.split('?')[0]); if (!fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }).listen(0);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } }); p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => console.log(m.text()));
await p.goto(`http://localhost:${srv.address().port}/engine/test/dino-test.html`); await p.waitForFunction(() => window.done, null, { timeout: 120000 });
await p.screenshot({ path: process.argv[2], type: 'jpeg', quality: 90 }); await b.close(); srv.close();
