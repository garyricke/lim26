// Netlify Function: tol-submit
// Receives a Tree of Life application, stores the full record in Netlify Blobs,
// and sends staff a MINIMAL notification containing no health information.
//
// Why it works this way: the application asks about suicidal ideation, domestic
// violence, abuse history, and housing safety. Those answers must never sit in
// an inbox. Staff get "a new application arrived from <name>" and sign in to
// read it. The full record lives in Blobs, reachable only through tol-admin,
// which checks a password server-side.
//
// Required env vars (Netlify → Site settings → Environment variables):
//   TOL_ADMIN_PASSWORD — shared password staff type to read applications
// Optional:
//   TOL_ALERT_FORM  (default "tree-of-life-alert") — Netlify form used to email staff
//
// POST JSON body: { ...application fields }

import { getStore } from "@netlify/blobs";

const STORE = "tol-applications";
const ALERT_FORM = process.env.TOL_ALERT_FORM || "tree-of-life-alert";

// Fields safe to put in a notification email. Everything else stays behind auth.
const SAFE_FIELDS = ["firstName", "lastName", "email", "phone", "city", "state"];

// Every field the form is allowed to submit. Anything else is dropped, so a
// tampered payload can't stuff arbitrary data into the store.
const ALLOWED = new Set([
  "firstName", "lastName", "address", "city", "state", "zip", "phone", "email",
  "emergencyName", "emergencyPhone",
  "ageRange", "gender", "ethnicity", "education",
  "accommodations", "attendAll", "attendAllExplain", "needHousing",
  "dvHistory", "behavioralHealth", "receivingCare",
  "unsafeRelationship", "unsafeRelationshipExplain",
  "unsafeHome", "unsafeHomeExplain",
  "unusualStress", "unusualStressExplain",
  "suicidalThoughts", "suicidalThoughtsDetail",
  "recentTrauma", "recentTraumaDetail",
  "supportSystem",
  "agreeAdult", "agreeAttend", "agreeSubstances", "agreeConfidentiality", "agreeFollowUp",
  "photoPermission", "participantSignature",
]);

const REQUIRED = [
  "firstName", "lastName", "address", "city", "state", "zip", "phone", "email",
  "emergencyName", "emergencyPhone", "ageRange", "gender", "ethnicity",
  "education", "attendAll", "needHousing", "dvHistory", "behavioralHealth", "receivingCare",
  "unsafeRelationship", "unsafeHome", "unusualStress", "suicidalThoughts",
  "recentTrauma", "photoPermission", "participantSignature",
];

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function clean(v) {
  if (typeof v !== "string") return v;
  return v.trim().slice(0, 5000);
}

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  let body;
  try { body = await req.json(); }
  catch { return json(400, { error: "Invalid JSON body" }); }

  // Honeypot — bots fill hidden fields, humans don't. Accept silently so the
  // bot doesn't learn it was caught.
  if (body["bot-field"]) return json(200, { ok: true });

  // Keep only known fields
  const app = {};
  for (const [k, v] of Object.entries(body)) {
    if (ALLOWED.has(k)) app[k] = clean(v);
  }

  const missing = REQUIRED.filter((f) => !app[f]);
  if (missing.length) {
    return json(400, { error: "Please complete every required question.", missing });
  }

  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(app.email)) {
    return json(400, { error: "That email address doesn't look right." });
  }

  // All four conditions must be agreed to
  for (const box of ["agreeAdult", "agreeAttend", "agreeSubstances", "agreeConfidentiality", "agreeFollowUp"]) {
    if (app[box] !== true && app[box] !== "true" && app[box] !== "yes") {
      return json(400, { error: "All conditions must be agreed to before applying, including confirming you are 18 or older." });
    }
  }

  const receivedAt = new Date().toISOString();
  const ref = `TOL-${receivedAt.slice(0, 10).replace(/-/g, "")}-${Math.random().toString(36).slice(2, 7).toUpperCase()}`;

  const record = {
    ref,
    receivedAt,
    status: "new",
    ...app,
  };

  // 1) Store the full application. Key sorts newest-last by time.
  try {
    const store = getStore(STORE);
    await store.setJSON(`${receivedAt}__${ref}`, record);
  } catch (err) {
    return json(502, {
      error: "We couldn't save your application. Please call (262) 439-5663 so we can take it by phone.",
      detail: String(err && err.message || err),
    });
  }

  // 2) Notify staff — name and contact only, never the health answers.
  //    Routed through Netlify Forms so there's no extra email vendor to manage.
  try {
    const site = process.env.URL;
    if (site) {
      const alert = new URLSearchParams({ "form-name": ALERT_FORM });
      alert.set("applicant", `${app.firstName} ${app.lastName}`);
      for (const f of SAFE_FIELDS) if (app[f]) alert.set(f, app[f]);
      alert.set("received", receivedAt);
      alert.set("reference", ref);
      alert.set("review", `${site}/admin-tree-of-life.html`);
      await fetch(site, {
        method: "POST",
        headers: { "content-type": "application/x-www-form-urlencoded" },
        body: alert.toString(),
      });
    }
  } catch {
    // The application is already saved. A failed notification must not tell the
    // applicant something went wrong — staff will still see it in the admin list.
  }

  return json(200, { ok: true, ref });
};
