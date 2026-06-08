// Netlify Function: events-ai
// Turns plain text (or a chat instruction) into a structured healing-group event.
// Uses the Anthropic Messages API via global fetch — no bundled deps.
//
// Required env vars (set in Netlify → Site settings → Environment variables):
//   ANTHROPIC_API_KEY        — your Anthropic API key
//   EVENTS_PUBLISH_PASSWORD  — shared password Roberta types in the admin tool
//
// POST JSON body:
//   { mode: "parse",  text: "...",                  password }   → structure free text
//   { mode: "chat",   event: {...}, instruction: "...", password } → refine an event

const MODEL = "claude-haiku-4-5-20251001";

const SCHEMA = `Event JSON shape (return ALL fields):
{
  "title":     string,  // e.g. "Community Healing Group"
  "loc":       string,  // e.g. "Bethel, AK"  or  "Zoom — Online"
  "datelabel": string,  // human label shown on the card, e.g. "Dec 4–5, 2026". Use an en dash – for ranges.
  "sub":       string,  // short duration line, e.g. "2 Days · Fri–Sat" or "1 Day · Saturday" or "2 Weeks · Online"
  "type":      "in-person" | "online" | "facilitator" | "military",
  "end":       string,  // ISO YYYY-MM-DD of the LAST day (card auto-removes the day after this)
  "open":      boolean,  // true = accepting registrations, false = full / waitlist
  "cta":       "register" | "waitlist" | "interest",  // waitlist if full; interest for not-yet-open trainings; else register
  "desc":      string,  // 1–3 sentence description with location, times, and any notes
  "modalId":   ""        // always empty string for new events
}`;

function json(status, obj) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function extractJson(text) {
  // Pull the first {...} block out of the model response.
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end === -1 || end < start) throw new Error("No JSON in model response");
  return JSON.parse(text.slice(start, end + 1));
}

export default async (req) => {
  if (req.method !== "POST") return json(405, { error: "Method not allowed" });

  const key = process.env.ANTHROPIC_API_KEY;
  const pw = process.env.EVENTS_PUBLISH_PASSWORD;
  if (!key) return json(500, { error: "Server not configured: ANTHROPIC_API_KEY missing." });

  let body;
  try { body = await req.json(); } catch { return json(400, { error: "Invalid JSON body" }); }

  if (!pw || body.password !== pw) return json(401, { error: "Incorrect publish password." });

  const today = new Date().toISOString().slice(0, 10);
  let userContent;

  if (body.mode === "chat") {
    userContent =
      `Today is ${today}. Here is an existing healing-group event as JSON:\n` +
      JSON.stringify(body.event || {}, null, 2) +
      `\n\nApply this change from the user, keeping everything else the same:\n"${body.instruction || ""}"\n\n` +
      `Return the FULL updated event as a single JSON object. ${SCHEMA}`;
  } else {
    userContent =
      `Today is ${today}. Turn the following notes into one structured healing-group event.\n\n` +
      `Notes:\n"""${body.text || ""}"""\n\n` +
      `If a detail is missing, make a sensible, conservative guess (e.g. type "in-person" unless it says online; ` +
      `cta "register" unless it says full/waitlist or it is a not-yet-open training). ` +
      `Compute "end" as the ISO date of the last day. Return ONE JSON object. ${SCHEMA}`;
  }

  let resp;
  try {
    resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1024,
        system:
          "You convert event notes into a single strict JSON object for a Native-led ministry's healing-group calendar. " +
          "Respond with ONLY the JSON object — no prose, no markdown fences.",
        messages: [{ role: "user", content: userContent }],
      }),
    });
  } catch (e) {
    return json(502, { error: "Could not reach the AI service.", detail: String(e) });
  }

  if (!resp.ok) {
    const detail = await resp.text().catch(() => "");
    return json(502, { error: "AI service error.", detail });
  }

  const data = await resp.json();
  const text = (data.content || []).map((c) => c.text || "").join("");
  let event;
  try { event = extractJson(text); } catch (e) {
    return json(502, { error: "AI returned an unexpected format. Try rephrasing.", raw: text });
  }

  if (!event.modalId) event.modalId = "";
  return json(200, { event });
};
