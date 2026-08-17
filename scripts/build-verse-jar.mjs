/**
 * Bible verse jar builder — Robert's "jars for grief, loneliness, teens, kids" idea.
 *
 * Answers his actual question ("can AI search a particular version and pull verses
 * tied to a theme?") without the two traps that would sink the product:
 *
 *  1. HALLUCINATED SCRIPTURE. The references below are curated by theme, but every
 *     word of verse TEXT is fetched from bible-api.com and never written from memory.
 *     Any reference that fails to fetch is reported, not quietly dropped.
 *  2. TRANSLATION COPYRIGHT. Defaults to the World English Bible — public domain, so
 *     LIM can print and sell without permission. NIV/ESV/NLT are licensed and cap how
 *     much you may reproduce; a product whose entire content IS verses blows past those
 *     caps and needs written permission. KJV is the other safe option.
 *
 * Usage: node scripts/build-verse-jar.mjs [web|kjv]
 */
import { writeFileSync, mkdirSync, existsSync, readFileSync } from 'node:fs';

const TRANSLATION = (process.argv[2] || 'web').toLowerCase();
const LICENCE = {
  web: 'World English Bible — public domain',
  kjv: 'King James Version — public domain'
};
if (!LICENCE[TRANSLATION]) {
  console.error(`Refusing "${TRANSLATION}". Only public-domain translations are safe to print: ${Object.keys(LICENCE).join(', ')}`);
  process.exit(1);
}

const THEMES = {
  'Grief & Loss': ['Psalm 34:18','Matthew 5:4','Revelation 21:4','Psalm 147:3','John 11:25','Psalm 23:4','Isaiah 41:10','Lamentations 3:22-23','Psalm 30:5','Isaiah 61:3','Romans 8:38-39','2 Corinthians 1:3-4','John 14:1','Psalm 56:8','Deuteronomy 31:8'],
  'Loneliness': ['Deuteronomy 31:6','Psalm 25:16','Hebrews 13:5','Psalm 68:6','Isaiah 43:2','Matthew 28:20','Psalm 139:7-10','John 14:18','Psalm 27:10','Zephaniah 3:17','Genesis 28:15','Psalm 46:1','1 Peter 5:7','Joshua 1:9','Psalm 145:18'],
  'Anxiety & Fear': ['Philippians 4:6-7','Isaiah 41:10','Matthew 6:34','Psalm 56:3','John 14:27','2 Timothy 1:7','Psalm 94:19','Proverbs 3:5-6','Isaiah 26:3','Matthew 11:28','Psalm 4:8','Psalm 118:6','Romans 15:13','Psalm 91:1-2','1 Peter 5:7'],
  'For Teens': ['1 Timothy 4:12','Jeremiah 29:11','Psalm 139:14','Proverbs 3:5-6','Joshua 1:9','Romans 12:2','Philippians 4:13','Galatians 6:9','Ephesians 2:10','Micah 6:8','Colossians 3:23','1 Corinthians 10:13','Psalm 119:105','James 1:5','Isaiah 40:31'],
  'For Little Kids': ['Psalm 56:3','John 3:16','Genesis 1:1','Psalm 136:1','1 John 4:19','Psalm 23:1','Matthew 19:14','Psalm 118:24','Psalm 139:14','Philippians 4:13','Psalm 121:3','Proverbs 3:5','1 Samuel 3:10','Psalm 100:5','Mark 10:14'],
  'Hope & Healing': ['Jeremiah 29:11','Isaiah 40:31','Psalm 147:3','Romans 15:13','Jeremiah 17:14','Psalm 103:2-3','Isaiah 53:5','James 5:16','Romans 8:28','Psalm 71:20','Hebrews 10:23','Lamentations 3:22-23','Psalm 42:11','Revelation 21:5','2 Corinthians 4:17']
};

const tidy = t => t.replace(/\s*\n\s*/g, ' ').replace(/\s{2,}/g, ' ').trim();
const sleep = ms => new Promise(r => setTimeout(r, ms));

// bible-api.com is a free service and rate-limits hard (HTTP 429). Cache every
// verse to disk so re-runs cost nothing, throttle politely, and back off long on
// a 429 rather than hammering it.
const CACHE_PATH = `scripts/.verse-cache-${TRANSLATION}.json`;
const cache = existsSync(CACHE_PATH) ? JSON.parse(readFileSync(CACHE_PATH, 'utf8')) : {};
let fetched = 0;

async function fetchVerse(ref) {
  if (cache[ref]) return cache[ref];
  const url = `https://bible-api.com/${encodeURIComponent(ref)}?translation=${TRANSLATION}`;
  for (let attempt = 1; attempt <= 5; attempt++) {
    try {
      const r = await fetch(url);
      if (r.status === 429) { await sleep(3000 * attempt); continue; }
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      if (!j.text) throw new Error('no text in response');
      const v = { ref: j.reference, text: tidy(j.text), translation: j.translation_name };
      cache[ref] = v;
      writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
      fetched++;
      await sleep(900);
      return v;
    } catch (e) {
      if (attempt === 5) return { ref, error: e.message };
      await sleep(900 * attempt);
    }
  }
  return { ref, error: 'rate-limited after 5 attempts' };
}

const out = {};
const failures = [];
for (const [theme, refs] of Object.entries(THEMES)) {
  out[theme] = [];
  for (const ref of refs) {
    const v = await fetchVerse(ref);
    if (v.error) { failures.push(`${theme} · ${ref} → ${v.error}`); continue; }
    out[theme].push(v);
    process.stdout.write('.');
  }
  process.stdout.write(` ${theme} (${out[theme].length}/${refs.length})\n`);
}

mkdirSync('data', { recursive: true });
writeFileSync(`data/verse-jars-${TRANSLATION}.json`,
  JSON.stringify({ translation: LICENCE[TRANSLATION], builtFrom: 'bible-api.com', themes: out }, null, 2));

// A verse can be a valid reference and still read badly alone on a strip — one
// that begins mid-sentence ("to provide for those who mourn...") looks like a
// typo to whoever pulls it out of the jar. Flag those for a human to re-pick.
const awkward = [];
for (const [theme, vs] of Object.entries(out)) {
  for (const v of vs) {
    const first = v.text.replace(/^[\u201c"'(\s]+/, '').charAt(0);
    if (first && first === first.toLowerCase() && first !== first.toUpperCase()) {
      awkward.push(`${theme} · ${v.ref} → "${v.text.slice(0, 58)}…"`);
    }
  }
}

const total = Object.values(out).reduce((n, a) => n + a.length, 0);
console.log(`\n${total} verses across ${Object.keys(out).length} themes · ${LICENCE[TRANSLATION]}`);
console.log(`→ data/verse-jars-${TRANSLATION}.json`);
if (failures.length) {
  console.log(`\n${failures.length} reference(s) FAILED — fix or replace these, do not ship as-is:`);
  failures.forEach(f => console.log('  ' + f));
} else {
  console.log('Every reference fetched cleanly.');
}
if (awkward.length) {
  console.log(`\n${awkward.length} verse(s) begin mid-sentence and read oddly on their own — consider re-picking:`);
  awkward.forEach(a => console.log('  ' + a));
}
