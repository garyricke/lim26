// Netlify Function: promo-ai
// Turns plain notes into a structured "promotion" (flyer + email + social copy)
// for a Lutheran Indian Ministries healing group. Anthropic Messages API via global fetch.
//
// Required env vars (already used by events-ai):
//   ANTHROPIC_API_KEY        — Anthropic API key
//   EVENTS_PUBLISH_PASSWORD  — shared password the admin types in the tool
//
// POST JSON:  { text: "plain description", password }  →  { ...promo fields }

const MODEL = "claude-haiku-4-5-20251001";

const SCHEMA = `Return ONE JSON object with EXACTLY these fields (fill every field; make sensible, conservative guesses for anything not stated — do not invent a specific address or phone if none is given, leave venue/address as given defaults):
{
  "eyebrow":       string,  // short kicker, e.g. "2026 Healing Groups"
  "loc":           string,  // city + state spelled out, e.g. "Fairbanks, Alaska"
  "lede":          string,  // 1–2 warm sentences for the flyer hero
  "venue":         string,  // venue name if given, else ""
  "address":       string,  // street · city, ST ZIP if given, else ""
  "regUrl":        string,  // registration URL if given, else "limhope.org"
  "pills":         string[],// 2–4 short audience/logistics chips, e.g. ["All adults 18+ welcome","Lunch provided"]
  "sessions":      string[],// EXACTLY 6 short session titles (keep the standard Healing-the-Wounds-of-Trauma set unless told otherwise)
  "events":        [ { "month": string, "dates": string, "req": string,
                       "schedule": [ { "day": string, "time": string } ] } ],  // 1 or 2 date panels; schedule may be [] if no per-day times given
  "emailSubject":  string,  // compelling, warm subject line
  "emailIntro":    string,  // 1–2 sentence email opening
  "captionSquare": string,  // Instagram/Facebook caption with a couple of tasteful emoji + 2–3 hashtags
  "captionStory":  string   // very short Story/Reel caption (2–3 short lines)
}`;

const STANDARD_SESSIONS = [
  "What is a wound of the heart?",
  "What happens when someone is grieving?",
  "If God loves us, why do we suffer?",
  "Bringing our pain to the cross",
  "What can help our heart wounds heal?",
  "How can we forgive others?",
];

function json(status, obj) {
  return new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });
}
function extractJson(text) {
  const start = text.indexOf("{"), end = text.lastIndexOf("}");
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

  const userContent =
    `Turn the following notes into promotional copy for a Lutheran Indian Ministries healing group. ` +
    `LIM is a Native-led, Christ-centered ministry; the "Healing the Wounds of Trauma" groups are free, ` +
    `confidential, scripture-based, and open to all adults 18+. Voice: warm, hopeful, respectful, plain — ` +
    `never clinical or "trauma-porn." The standard six sessions are:\n${STANDARD_SESSIONS.map((s,i)=>`${i+1}. ${s}`).join("\n")}\n\n` +
    `Notes:\n"""${body.text || ""}"""\n\n${SCHEMA}`;

  let resp;
  try {
    resp = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 1500,
        system:
          "You are a nonprofit copywriter for a Native-led Christian ministry. You turn brief notes into a single strict JSON object of promotional copy. " +
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
  let promo;
  try { promo = extractJson(text); } catch (e) {
    return json(502, { error: "AI returned an unexpected format. Try rephrasing.", raw: text });
  }
  if (!Array.isArray(promo.sessions) || promo.sessions.length !== 6) promo.sessions = STANDARD_SESSIONS;
  return json(200, promo);
};
