// Netlify Function: signups
// Live healing-group sign-up counts for staff (/signups). Reads the
// healing-group-registration and registration-cancellation Netlify Forms
// through the Netlify API, so there is nothing to keep in sync by hand.
// The password is checked HERE, on the server — registrant names and contact
// details never reach the browser until it passes.
//
// Required env vars (Netlify → Site settings → Environment variables):
//   SIGNUPS_PASSWORD  — shared password staff type to view sign-ups
//   NETLIFY_API_TOKEN — personal access token that can read this site's forms
//
// POST JSON body:
//   { password } → { ok, items: [{ session, name, email, phone, city, state,
//                    dietary, receivedAt, cancelled }] } newest first

const SITE_ID = process.env.SITE_ID || "34cb397d-c3b9-4261-adfa-10e60a9fe794";
const API = "https://api.netlify.com/api/v1";
const REG_FORM = "healing-group-registration";
const CANCEL_FORM = "registration-cancellation";

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store" },
  });
}

// Length-independent comparison so a wrong password can't be narrowed by timing
function pwMatches(given, expected) {
  if (typeof given !== "string" || typeof expected !== "string") return false;
  if (given.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < given.length; i++) diff |= given.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

async function api(path, token) {
  const res = await fetch(API + path, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error(`Netlify API ${res.status} on ${path}`);
  return res.json();
}

// All verified submissions for one form, following pagination
async function submissions(formId, token) {
  const out = [];
  for (let page = 1; page <= 50; page++) {
    const batch = await api(`/forms/${formId}/submissions?per_page=100&page=${page}`, token);
    out.push(...batch);
    if (batch.length < 100) break;
  }
  return out;
}

const norm = (s) => String(s || "").trim().toLowerCase();

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const expected = process.env.SIGNUPS_PASSWORD;
  const token = process.env.NETLIFY_API_TOKEN;
  if (!expected || !token) {
    return json(500, { error: "Server not configured: SIGNUPS_PASSWORD or NETLIFY_API_TOKEN missing." });
  }

  let body;
  try { body = await req.json(); }
  catch { return json(400, { error: "Invalid JSON body" }); }

  if (!pwMatches(body.password, expected)) {
    return json(401, { error: "Incorrect password." });
  }

  try {
    const forms = await api(`/sites/${SITE_ID}/forms`, token);
    const byName = Object.fromEntries(forms.map((f) => [f.name, f]));
    const regs = byName[REG_FORM] ? await submissions(byName[REG_FORM].id, token) : [];
    const cans = byName[CANCEL_FORM] ? await submissions(byName[CANCEL_FORM].id, token) : [];

    // A cancellation matches a registration by session + email
    const cancelled = new Set(cans.map((c) => norm(c.data.session) + "|" + norm(c.data.email)));

    const items = regs.map((s) => {
      const d = s.data || {};
      return {
        session: d.session || "(no session chosen)",
        name: `${d["first-name"] || ""} ${d["last-name"] || ""}`.trim() || "(no name)",
        email: d.email || "",
        phone: d.phone || "",
        city: d.city || "",
        state: d.state || "",
        // "No" / "None" answers are noise in the list; keep real needs only
        dietary: /^(no|none|n\/?a|-)?$/i.test(String(d["dietary-needs"] || "").trim()) ? "" : d["dietary-needs"],
        receivedAt: s.created_at,
        cancelled: cancelled.has(norm(d.session) + "|" + norm(d.email)),
      };
    });
    items.sort((a, b) => String(b.receivedAt).localeCompare(String(a.receivedAt)));
    return json(200, { ok: true, items, checkedAt: new Date().toISOString() });
  } catch (err) {
    return json(502, { error: "Couldn't read sign-ups from Netlify. Try again in a minute." });
  }
};
