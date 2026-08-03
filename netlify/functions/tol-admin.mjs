// Netlify Function: tol-admin
// Reads Tree of Life applications for staff. The password is checked HERE, on
// the server — application data never reaches the browser until it passes.
//
// This is deliberately different from the site's admin badge (a client-side
// password used to hide internal links). That approach is readable in View
// Source and is not suitable for the health answers this form collects.
//
// Required env vars (Netlify → Site settings → Environment variables):
//   TOL_ADMIN_PASSWORD — shared password staff type to read applications
//
// POST JSON body:
//   { action: "list",   password }              // summaries only, newest first
//   { action: "get",    key, password }         // one full application
//   { action: "csv",    password }              // all applications as CSV
//   { action: "status", key, status, password } // mark reviewed/accepted/etc.

import { getStore } from "@netlify/blobs";

const STORE = "tol-applications";
const STATUSES = ["new", "reviewed", "accepted", "waitlisted", "declined"];

// Column order for the CSV export
const CSV_FIELDS = [
  "ref", "receivedAt", "status", "firstName", "lastName", "address", "city",
  "state", "zip", "phone", "email", "emergencyName", "emergencyPhone",
  "ageRange", "gender", "ethnicity", "education", "accommodations",
  "attendAll", "attendAllExplain", "needHousing", "dvHistory", "behavioralHealth",
  "receivingCare", "unsafeRelationship", "unsafeRelationshipExplain",
  "unsafeHome", "unsafeHomeExplain", "unusualStress", "unusualStressExplain",
  "suicidalThoughts", "suicidalThoughtsDetail", "recentTrauma",
  "recentTraumaDetail", "supportSystem", "photoPermission", "participantSignature",
];

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
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

function csvCell(v) {
  const s = v == null ? "" : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const expected = process.env.TOL_ADMIN_PASSWORD;
  if (!expected) {
    return json(500, { error: "Server not configured: TOL_ADMIN_PASSWORD missing." });
  }

  let body;
  try { body = await req.json(); }
  catch { return json(400, { error: "Invalid JSON body" }); }

  if (!pwMatches(body.password, expected)) {
    return json(401, { error: "Incorrect password." });
  }

  const store = getStore(STORE);

  // ── list ────────────────────────────────────────────────────────────────
  if (body.action === "list") {
    const { blobs } = await store.list();
    const items = [];
    for (const b of blobs) {
      const rec = await store.get(b.key, { type: "json" }).catch(() => null);
      if (!rec) continue;
      // Summary only — no health answers in the list view
      items.push({
        key: b.key,
        ref: rec.ref,
        receivedAt: rec.receivedAt,
        status: rec.status || "new",
        name: `${rec.firstName || ""} ${rec.lastName || ""}`.trim(),
        email: rec.email || "",
        phone: rec.phone || "",
        city: rec.city || "",
        state: rec.state || "",
        attendAll: rec.attendAll || "",
        // Surfaced so staff can triage urgent applications first
        flagged: rec.suicidalThoughts === "yes" || rec.unsafeHome === "yes" || rec.unsafeRelationship === "yes",
      });
    }
    items.sort((a, b) => String(b.receivedAt).localeCompare(String(a.receivedAt)));
    return json(200, { ok: true, items, count: items.length });
  }

  // ── get ─────────────────────────────────────────────────────────────────
  if (body.action === "get") {
    if (!body.key) return json(400, { error: "Missing key." });
    const rec = await store.get(body.key, { type: "json" }).catch(() => null);
    if (!rec) return json(404, { error: "Application not found." });
    return json(200, { ok: true, application: rec });
  }

  // ── status ──────────────────────────────────────────────────────────────
  if (body.action === "status") {
    if (!body.key) return json(400, { error: "Missing key." });
    if (!STATUSES.includes(body.status)) return json(400, { error: "Unknown status." });
    const rec = await store.get(body.key, { type: "json" }).catch(() => null);
    if (!rec) return json(404, { error: "Application not found." });
    rec.status = body.status;
    rec.statusUpdatedAt = new Date().toISOString();
    await store.setJSON(body.key, rec);
    return json(200, { ok: true, status: rec.status });
  }

  // ── csv ─────────────────────────────────────────────────────────────────
  if (body.action === "csv") {
    const { blobs } = await store.list();
    const rows = [];
    for (const b of blobs) {
      const rec = await store.get(b.key, { type: "json" }).catch(() => null);
      if (rec) rows.push(rec);
    }
    rows.sort((a, b) => String(b.receivedAt).localeCompare(String(a.receivedAt)));
    const lines = [CSV_FIELDS.join(",")];
    for (const r of rows) lines.push(CSV_FIELDS.map((f) => csvCell(r[f])).join(","));
    return json(200, { ok: true, csv: lines.join("\n"), count: rows.length });
  }

  return json(400, { error: "Unknown action." });
};
