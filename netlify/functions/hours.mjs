// Hours feed for the check-in pages ("Where the hours went").
//
// Reads LIM's current prepaid block from Time (time.orbisdesign.com) and returns
// the block, the hours used and the client-facing line for every entry. Time only
// serves cleared client lines on this endpoint, never internal notes.
//
// TIME_API_KEY is a read-only key scoped to the one project below. It lives in
// Netlify's environment and must never be committed: Netlify's secrets scan
// blocks every deploy if a value lands in the repo.
//
// Hours are full effort (wall): work done in parallel counts in full for each
// project (Gary, 19 Oct 2026).
//
// ?until=YYYY-MM-DD limits the log to a meeting date, so a dated agenda keeps
// matching what was said in the meeting.

const TIME_BASE = 'https://time.orbisdesign.com';
const PROJECT = 'lim-maint-2';

const r2 = (n) => Math.round(n * 100) / 100;

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=300' },
  });
}

export default async (req) => {
  const key = process.env.TIME_API_KEY;
  if (!key) return json(500, { error: 'TIME_API_KEY is not set on this site.' });

  const until = new URL(req.url).searchParams.get('until');
  if (until && !/^\d{4}-\d{2}-\d{2}$/.test(until)) return json(400, { error: 'until must be YYYY-MM-DD' });

  try {
    const res = await fetch(`${TIME_BASE}/api/report/burndown?project=${PROJECT}&log=365`, {
      headers: {
        Authorization: `Bearer ${key}`,
        Accept: 'application/json',
        'User-Agent': 'lim2026-checkin/1.0 (+https://www.lutheranindianministries.org/checkin)',
      },
    });
    if (!res.ok) return json(502, { error: `Time returned ${res.status}.` });
    const p = ((await res.json()).projects || [])[0];
    if (!p) return json(502, { error: 'Time returned no project.' });

    const entries = (p.log || [])
      .filter((w) => w.summary && (!until || w.date <= until))
      .map((w) => ({ date: w.date, hours: r2(w.hours || 0), note: w.summary }));
    const used = until ? r2(entries.reduce((s, e) => s + e.hours, 0)) : r2(p.used?.hours || 0);
    const block = p.block?.hours ?? null;

    return json(200, {
      project: p.project,
      blockHours: block,
      usedHours: used,
      remainingHours: block != null ? r2(block - used) : null,
      until: until || null,
      hoursBasis: p.hoursBasis,
      entries,
      fetchedAt: new Date().toISOString(),
    });
  } catch {
    return json(502, { error: 'Could not reach Time.' });
  }
};
