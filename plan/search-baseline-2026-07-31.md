# Search baseline — captured 31 July 2026, before the DNS switch

Google Search Console, property `https://www.lutheranindianministries.org/`.
This is the "before" record. Search Console measures the **domain**, not a
tracking tag, so numbers before and after the switch are directly comparable —
no cookie consent, no ad blockers, no methodology change. It is the only source
that gives an honest old-vs-new comparison.

## Headline

| Window | Clicks | Impressions | CTR | Avg position |
|---|---|---|---|---|
| Last 16 months (Mar 2025 – Jul 2026) | **5,910** | **497,000** | 1.2% | 13.9 |
| Last 3 months (Apr 30 – Jul 29 2026) | **888** | **78,500** | 1.1% | 9.7 |

Average position improved from 13.9 (16-month) to 9.7 (3-month) — the site has
been climbing, from roughly page two to the bottom of page one.

## Top queries — 16 months

| Query | Clicks | Impressions | CTR |
|---|---|---|---|
| lutheran indian ministries | 754 | 1,980 | 38% |
| **lutheran sacraments** | 51 | **7,569** | 0.7% |
| native american spirituality beliefs vs christianity | 43 | 1,179 | 3.6% |
| haskell light | 39 | 1,025 | 3.8% |
| matthew 26:41 devotional | 29 | 446 | 6.5% |
| **matthew 26:41** | 28 | **17,135** | 0.16% |

## What this actually says

**Half a million impressions, six thousand clicks.** Google is already showing
LIM to a very large audience and almost none of it converts. The brand query
converts at 38%; everything else is under 4%.

**The scripture and doctrine queries are the opportunity.** `matthew 26:41`
alone drew 17,135 impressions and 28 clicks. `lutheran sacraments` drew 7,569
and 51. That is enormous demand meeting a page that either ranks too low to be
clicked or gives Google nothing worth clicking.

**This validates two things already done:**

- The **"What Do Lutherans Believe?" series** rebuilt on 30 July directly
  targets `lutheran sacraments` — the second-biggest impression driver on the
  whole site. It had been redirecting to the homepage.
- The **redirect fixes** matter more than they looked. Bulk redirects to `/`
  are read as soft 404s; those URLs were on course to be dropped from the index
  along with their impressions.

**The devotion archive has search demand.** Scripture-keyed devotions —
`matthew 26:41`, `1 chronicles 16:34` — pull impressions on their own. That is
a concrete argument for rebuilding more of the 1,459 archived posts rather than
leaving them as redirects.

## How to compare after the switch

Use Search Console, not GA4, for the headline comparison. GA4 only counts
visitors who accept the cookie banner, so it will always read lower than
Squarespace Analytics did — comparing the two would make the new site look like
it lost traffic when it hasn't.

Watch, in order:

1. **Impressions** — should hold. A drop means indexing trouble, most likely a
   redirect that didn't land.
2. **Average position** — the number to beat is **9.7**.
3. **Clicks and CTR** — where the new site should win, through better titles,
   faster pages, and real destinations instead of homepage redirects.
4. **Coverage** (Indexing → Pages) — watch for a spike in "Not found (404)"
   in the first fortnight after cutover.

Allow four to six weeks. Google re-crawls a domain gradually, and the first two
weeks after any migration are noisy.
