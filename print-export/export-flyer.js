import { chromium } from 'playwright';
import { mkdirSync, existsSync, writeFileSync, readFileSync, createReadStream, statSync } from 'node:fs';
import { resolve, dirname, extname, normalize, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..');
const EXPORTS_DIR = resolve(PROJECT_ROOT, 'print-export/exports');

// Flyer assets are referenced root-absolute (/images-master/…, /brand/…) because
// the flyers are served from clean stems like /tree-of-life/flyer, where a
// relative path would resolve against /tree-of-life/ and 404. Under file://
// those same paths resolve to the filesystem root and load nothing — so render
// over a local static server instead, which matches production exactly.
const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif',
  '.json': 'application/json', '.pdf': 'application/pdf',
  '.woff': 'font/woff', '.woff2': 'font/woff2'
};

function startStaticServer(root) {
  const server = createServer((req, res) => {
    // Strip the query string, decode, and clamp the path inside `root`.
    const rel = decodeURIComponent(req.url.split('?')[0]);
    const filePath = join(root, normalize(rel).replace(/^(\.\.[/\\])+/, ''));
    if (!filePath.startsWith(root)) { res.writeHead(403).end(); return; }
    try {
      if (!statSync(filePath).isFile()) { res.writeHead(404).end(); return; }
    } catch { res.writeHead(404).end(); return; }
    res.writeHead(200, { 'content-type': MIME[extname(filePath).toLowerCase()] || 'application/octet-stream' });
    createReadStream(filePath).pipe(res);
  });
  return new Promise(ok => server.listen(0, '127.0.0.1', () => ok({ server, port: server.address().port })));
}

// Letter size at 96 CSS DPI = 816 x 1056 layout px.
const LAYOUT_WIDTH = 816;
const LAYOUT_HEIGHT = 1056;

// Nobody should ever be asked to "Print to PDF" from their own browser. Print
// dialogs default to adding headers and footers, dropping background graphics,
// and scaling to fit — so what a person saves is rarely what we designed. Every
// printable page here is rendered once, checked, and served as a finished file.
//
//   kind: 'sheet' — fixed-size artwork (flyers). Exact 8.5x11, no margins.
//   kind: 'doc'   — flowing multi-page documents. Let the page's own @page rule
//                   set size and margins via preferCSSPageSize.
const FLYERS = [
  {
    id: 'fbx-healing-2026',
    kind: 'sheet',
    html: 'flyer-fairbanks-healing-groups-2026.html',
    file: 'flyer-fairbanks-healing-groups-2026',
    download: 'LIM-Fairbanks-Healing-Groups-2026',
    expectPages: 1
  },
  {
    id: 'tol-2026',
    kind: 'sheet',
    html: 'flyer-tree-of-life-fairbanks-2026.html',
    file: 'flyer-tree-of-life-fairbanks-2026',
    download: 'LIM-Tree-of-Life-Fairbanks-2026',
    expectPages: 1
  },
  {
    id: 'zion-poster',
    kind: 'sheet',
    html: 'flyer-zion-songs-stories-2026.html',
    file: 'flyer-zion-songs-stories-2026',
    download: 'LIM-Zion-Songs-and-Stories-2026',
    expectPages: 1
  },
  {
    // Two 8.5 x 5.5in handouts on one letter sheet, guillotined down the middle.
    id: 'zion-half',
    kind: 'sheet',
    html: 'flyer-zion-songs-stories-half.html',
    file: 'flyer-zion-songs-stories-half',
    download: 'LIM-Zion-Songs-and-Stories-Half-Page',
    expectPages: 1
  },
  {
    id: 'verse-jars',
    kind: 'sheet',
    html: 'verse-jars.html',
    file: 'verse-jars-web',
    download: 'LIM-Verse-Jars',
    expectPages: 6,
    settle: 2500          // waits on the verse JSON fetch before rendering
  },
  {
    id: 'lim-history',
    kind: 'doc',
    html: 'docs-lim-history.html',
    file: 'lim-history-draft',
    download: 'LIM-History-Draft'
  },
  {
    id: 'board-report',
    kind: 'doc',
    html: 'docs-board-report.html',
    file: 'board-report-2026-08',
    download: 'LIM-Board-Report-Aug-2026'
  },
  {
    id: 'camp-report',
    kind: 'doc',
    html: 'docs-camp-perkins-report.html',
    file: 'camp-perkins-report-2026',
    download: 'LIM-Camp-Perkins-2026-Report'
  }
];

function pickTargets(args) {
  if (args.length === 0) return FLYERS;
  return FLYERS.filter(f => args.includes(f.id) || args.includes(f.file));
}

let exitCode = 0;

async function main() {
  const allArgs = process.argv.slice(2);
  const positional = allArgs.filter(a => !a.startsWith('--'));
  const targets = pickTargets(positional);

  if (targets.length === 0) {
    console.error('No matching flyers. Available IDs:');
    FLYERS.forEach(f => console.error(`  ${f.id}  (${f.file})`));
    process.exit(1);
  }

  mkdirSync(EXPORTS_DIR, { recursive: true });

  // Bake a fresh export timestamp directly into the flyer HTML so
  // both the live page and the rendered PDF carry the stamp without
  // relying on async JS loading. The HTML carries marker comments
  // that are rewritten on every export.
  const now = new Date();
  const stampHuman = now.toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: 'numeric', minute: '2-digit', timeZoneName: 'short'
  });
  const stampFile = now.toISOString().replace(/[:.]/g, '-').slice(0, 16);

  for (const flyer of targets) {
    const htmlPath = resolve(PROJECT_ROOT, flyer.html);
    if (!existsSync(htmlPath)) continue;
    const pdfFile = `${flyer.file}_${stampFile}.pdf`;
    let html = readFileSync(htmlPath, 'utf8');

    // 1. Toolbar text (browser only): "Last export: …"
    html = html.replace(
      /(<span class="toolbar-stamp" id="toolbar-stamp">)[^<]*(<\/span>)/,
      `$1Last export: ${stampHuman}$2`
    );

    // 2. Print-visible stamp inside the PDF
    html = html.replace(
      /(<div class="print-stamp" id="print-stamp">)[^<]*(<\/div>)/,
      `$1Exported ${stampHuman}$2`
    );

    // 3. Download button: href points at the timestamped PDF, download
    //    attribute names the saved file with the timestamp too.
    html = html.replace(
      /(id="dl-link"\s+href=")[^"]+(")/,
      `$1/print-export/exports/${pdfFile}$2`
    );
    html = html.replace(
      /(id="dl-link"[\s\S]*?download=")[^"]+(")/,
      `$1${flyer.download}_${stampFile}.pdf$2`
    );

    writeFileSync(htmlPath, html);
  }
  console.log(`Stamped: ${stampHuman}`);

  const { server, port } = await startStaticServer(PROJECT_ROOT);
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: LAYOUT_WIDTH, height: LAYOUT_HEIGHT },
    deviceScaleFactor: 2
  });

  console.log(`Exporting ${targets.length} flyer${targets.length === 1 ? '' : 's'} as PDF`);
  console.log(`Output: ${EXPORTS_DIR}\n`);

  for (const flyer of targets) {
    const htmlPath = resolve(PROJECT_ROOT, flyer.html);
    if (!existsSync(htmlPath)) {
      console.warn(`  WARN: source not found: ${htmlPath} — skipping ${flyer.id}`);
      continue;
    }

    const page = await context.newPage();
    const url = `http://127.0.0.1:${port}/${flyer.html}`;
    const missing = [];
    page.on('response', r => { if (r.status() >= 400) missing.push(`${r.status()} ${r.url()}`); });
    console.log(`→ ${flyer.id}`);
    await page.goto(url, { waitUntil: 'load' });

    // Wait for web fonts (Merriweather, Barlow Condensed, Open Sans).
    await page.evaluate(() => document.fonts.ready);

    // Pages that build themselves from fetched data need a moment more.
    if (flyer.settle) await page.waitForTimeout(flyer.settle);

    // Wait for every <img> to fully decode (hero, aside, QR code).
    await page.evaluate(() => Promise.all(
      Array.from(document.images).map(img =>
        img.complete && img.naturalWidth > 0
          ? Promise.resolve()
          : new Promise(r => { img.onload = img.onerror = r; })
      )
    ));

    const pdfFile = `${flyer.file}_${stampFile}.pdf`;
    const pdfPath = resolve(EXPORTS_DIR, pdfFile);

    // 'sheet' artwork is pinned to exact letter with no margins and, for a
    // single-page flyer, clipped to page 1. 'doc' pages carry their own @page
    // rule, so let the CSS decide rather than overriding it.
    const opts = flyer.kind === 'doc'
      ? { path: pdfPath, preferCSSPageSize: true, printBackground: true }
      : {
          path: pdfPath, width: '8.5in', height: '11in', printBackground: true,
          margin: { top: 0, right: 0, bottom: 0, left: 0 },
          ...(flyer.expectPages === 1 ? { pageRanges: '1' } : {})
        };
    await page.pdf(opts);

    // Verify what we actually produced. A silently-wrong page count is the
    // failure mode here — six themes printing as twelve pages looked fine
    // until the file was opened.
    const bytes = readFileSync(pdfPath);
    const counts = [...bytes.toString('latin1').matchAll(/\/Count\s+(\d+)/g)].map(m => +m[1]);
    const pages = counts.length ? Math.max(...counts) : null;
    const kb = Math.round(bytes.length / 1024);
    let verdict = `${pages ?? '?'} page${pages === 1 ? '' : 's'}, ${kb}KB`;
    if (flyer.expectPages && pages !== flyer.expectPages) {
      verdict += `  ** EXPECTED ${flyer.expectPages} **`;
      exitCode = 1;
    }
    console.log(`  PDF: ${pdfFile}  (${verdict})`);
    // A flyer that silently loses its hero image still exports a clean-looking
    // PDF, so surface any failed asset rather than shipping a blank panel.
    if (missing.length) {
      console.warn(`  WARN: ${missing.length} asset(s) failed to load:`);
      missing.forEach(m => console.warn(`    ${m}`));
    }

    await page.close();
  }

  await context.close();
  await browser.close();
  server.close();
  console.log(`\nDone. ${targets.length} document${targets.length === 1 ? '' : 's'} exported.`);
  if (exitCode) console.error('One or more exports had the wrong page count — do not publish these.');
  process.exitCode = exitCode;
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
