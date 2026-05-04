import { chromium } from 'playwright';
import { mkdirSync, existsSync, writeFileSync, readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(__dirname, '..');
const EXPORTS_DIR = resolve(PROJECT_ROOT, 'print-export/exports');

// Letter size at 96 CSS DPI = 816 x 1056 layout px.
const LAYOUT_WIDTH = 816;
const LAYOUT_HEIGHT = 1056;

const FLYERS = [
  {
    id: 'fbx-healing-2026',
    html: 'flyer-fairbanks-healing-groups-2026.html',
    file: 'flyer-fairbanks-healing-groups-2026'
  }
];

function pickTargets(args) {
  if (args.length === 0) return FLYERS;
  return FLYERS.filter(f => args.includes(f.id) || args.includes(f.file));
}

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
      `$1print-export/exports/${pdfFile}$2`
    );
    html = html.replace(
      /(id="dl-link"[\s\S]*?download=")[^"]+(")/,
      `$1LIM-Fairbanks-Healing-Groups-2026_${stampFile}.pdf$2`
    );

    writeFileSync(htmlPath, html);
  }
  console.log(`Stamped: ${stampHuman}`);

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
    const fileUrl = pathToFileURL(htmlPath).href;
    console.log(`→ ${flyer.id}`);
    await page.goto(fileUrl, { waitUntil: 'load' });

    // Wait for web fonts (Merriweather, Barlow Condensed, Open Sans).
    await page.evaluate(() => document.fonts.ready);

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
    await page.pdf({
      path: pdfPath,
      width: '8.5in',
      height: '11in',
      printBackground: true,
      pageRanges: '1',
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });
    console.log(`  PDF: ${pdfPath}`);

    await page.close();
  }

  await context.close();
  await browser.close();
  console.log(`\nDone. ${targets.length} flyer${targets.length === 1 ? '' : 's'} exported.`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
