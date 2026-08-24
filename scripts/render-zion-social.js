// Renders each artboard in zion-social-cards.html to an exact-size PNG.
// Served over HTTP, not file://, so the root-relative brand logo resolves.
const { chromium } = require('../print-export/node_modules/playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT  = process.env.OUT || path.join(ROOT, 'generated_imgs', 'zion-social');
const CARDS = ['c1350', 'c1080', 'c1920', 'c630'];
const TYPES = {'.html':'text/html','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.css':'text/css','.js':'text/javascript'};

const server = http.createServer((req, res) => {
  const file = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404).end('not found'); return;
  }
  res.writeHead(200, {'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream'});
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, r));
  const base = `http://127.0.0.1:${server.address().port}`;
  fs.mkdirSync(OUT, {recursive: true});

  const browser = await chromium.launch();
  const page = await browser.newPage({viewport: {width: 1400, height: 1000}, deviceScaleFactor: 1});

  const bad = [];
  page.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });

  await page.goto(`${base}/zion-social-cards.html`, {waitUntil: 'networkidle'});
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1200);

  for (const id of CARDS) {
    const el = await page.$('#' + id);
    const box = await el.boundingBox();
    const out = path.join(OUT, `zion-${id.slice(1)}.png`);
    await el.screenshot({path: out});
    console.log(`${path.basename(out)}  ${Math.round(box.width)}x${Math.round(box.height)}`);
  }

  // A card that silently lost its logo still screenshots into a clean-looking PNG.
  console.log(bad.length ? 'FAILED REQUESTS:\n  ' + bad.join('\n  ') : 'all requests OK');
  await browser.close();
  server.close();
})();
