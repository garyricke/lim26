// Netlify Function: events-publish
// Commits the events list to data/events.json on GitHub. Netlify then
// auto-rebuilds the site, so the change goes live within ~1–2 minutes.
//
// Required env vars (Netlify → Site settings → Environment variables):
//   GITHUB_TOKEN             — fine-grained PAT with Contents: read & write on the repo
//   EVENTS_PUBLISH_PASSWORD  — shared password Roberta types in the admin tool
// Optional:
//   GITHUB_REPO    (default "garyricke/lim26")
//   GITHUB_BRANCH  (default "main")
//   EVENTS_PATH    (default "data/events.json")
//
// POST JSON body:
//   { action: "upsert", event: {...}, password }   // add or update one event
//   { action: "delete", id: "...",   password }    // remove one event

const REPO = process.env.GITHUB_REPO || "garyricke/lim26";
const BRANCH = process.env.GITHUB_BRANCH || "main";
const PATH = process.env.EVENTS_PATH || "data/events.json";

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function slugify(s) {
  return (s || "event")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
}

const gh = (token, path, init = {}) =>
  fetch(`https://api.github.com/repos/${REPO}/${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "lim-events-publish",
      ...(init.headers || {}),
    },
  });

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const token = process.env.GITHUB_TOKEN;
  const pw = process.env.EVENTS_PUBLISH_PASSWORD;
  if (!token) return json(500, { error: "Server not configured: GITHUB_TOKEN missing." });

  let body;
  try { body = await req.json(); } catch { return json(400, { error: "Invalid JSON body" }); }
  if (!pw || body.password !== pw) return json(401, { error: "Incorrect publish password." });

  // 1) Read the current file (need its sha to update it)
  let sha = null, events = [];
  const getRes = await gh(token, `contents/${PATH}?ref=${BRANCH}`);
  if (getRes.ok) {
    const file = await getRes.json();
    sha = file.sha;
    try { events = JSON.parse(Buffer.from(file.content, "base64").toString("utf8")); }
    catch { events = []; }
  } else if (getRes.status !== 404) {
    const detail = await getRes.text().catch(() => "");
    return json(502, { error: "Could not read events.json from GitHub.", detail });
  }
  if (!Array.isArray(events)) events = [];

  // 2) Apply the change
  let message;
  if (body.action === "delete") {
    if (!body.id) return json(400, { error: "Missing id to delete." });
    const before = events.length;
    events = events.filter((e) => e.id !== body.id);
    if (events.length === before) return json(404, { error: "Event not found." });
    message = `Events: remove ${body.id}`;
  } else if (body.action === "upsert") {
    const ev = body.event;
    if (!ev || !ev.title) return json(400, { error: "Missing event data." });
    if (!ev.id) ev.id = `${slugify(ev.title)}-${slugify(ev.datelabel)}`.slice(0, 60) || `event-${Date.now()}`;
    if (ev.modalId == null) ev.modalId = "";
    const idx = events.findIndex((e) => e.id === ev.id);
    if (idx >= 0) { events[idx] = ev; message = `Events: update ${ev.id}`; }
    else { events.push(ev); message = `Events: add ${ev.id}`; }
  } else {
    return json(400, { error: "Unknown action." });
  }

  // Keep the list sorted by end date so the page reads chronologically
  events.sort((a, b) => String(a.end || "").localeCompare(String(b.end || "")));

  // 3) Commit it back
  const content = Buffer.from(JSON.stringify(events, null, 2) + "\n", "utf8").toString("base64");
  const putRes = await gh(token, `contents/${PATH}`, {
    method: "PUT",
    body: JSON.stringify({ message: `${message} (via Events Manager)`, content, branch: BRANCH, ...(sha ? { sha } : {}) }),
  });

  if (!putRes.ok) {
    const detail = await putRes.text().catch(() => "");
    return json(502, { error: "Could not publish to GitHub.", detail });
  }

  return json(200, { ok: true, events, message });
};
