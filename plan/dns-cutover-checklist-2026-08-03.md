# DNS cutover — lutheranindianministries.org (Network Solutions)

Recorded 3 Aug 2026, before any change. If anything breaks, this is what it
looked like beforehand.

## Change exactly two things

| Type | Name | New value |
|---|---|---|
| A | `@` | `75.2.60.5` |
| CNAME | `www` | `lim2026.netlify.app` |

Some Network Solutions panels accept a second apex A record — add
`99.83.190.102` if the field exists. If not, one A record is fine.

**Add both domains in Netlify first** (Site settings → Domain management), so
the TLS certificate provisions the moment the records resolve.

## Leave every one of these alone

**Email — Microsoft 365. Touching any of these breaks staff email.**

| Type | Name | Value | Why |
|---|---|---|---|
| MX | `@` | `lutheranindianministries-org.mail.protection.outlook.com` | All inbound mail |
| TXT | `@` | `v=spf1 include:spf.protection.outlook.com -all` | SPF. Remove it and LIM's outbound mail starts landing in spam |
| TXT | `@` | `MS=ms16032921` | Microsoft domain ownership |
| CNAME | `autodiscover` | `autodiscover.outlook.com` | Outlook auto-configuration |
| CNAME | `msoid` | `clientconfig.microsoftonline-p.net` | Microsoft sign-in |
| CNAME | `lyncdiscover` | `webdir.online.lync.com` | Teams / Skype for Business |
| CNAME | `sip` | `sipdir.online.lync.com` | Teams / Skype for Business |
| SRV | `_sip._tls` | `sipdir.online.lync.com` | Teams |
| SRV | `_sipfederationtls._tcp` | `sipfed.online.lync.com` | Teams federation |

**Search Console — do not remove.**

| Type | Name | Value |
|---|---|---|
| TXT | `@` | `google-site-verification=GgNPMyPCkGf4crNG-cubY_vcfSItgUG_dJQ4U2fy4vQ` |

This is what verifies the Search Console property. Search Console is the only
tool that compares old site to new on identical methodology — it measures the
domain, not a tracking tag. Delete this record and the verification lapses,
taking the baseline comparison with it: **5,910 clicks / 497,000 impressions /
position 13.9** over 16 months. See `plan/search-baseline-2026-07-31.md`.

## Squarespace leftovers — remove later, not now

| Type | Name | Value |
|---|---|---|
| CNAME | `lsyea8x5jhg973wsabz4` | `verify.squarespace.com` |

Squarespace's domain-verification record. Harmless, and worth leaving until the
subscription actually lapses in June 2027 — removing it early could complicate
getting back into the old site.

## Two records not visible in the 3 Aug screenshot

The capture starts at the CNAME section, so check these before changing anything:

1. **The existing A record(s) for `@`** — currently pointing at Squarespace
   (`198.185.159.144/145`, `198.49.23.144/145`). These are what you replace.
2. **The `www` CNAME** — sits under SHOW MORE in the CNAME block, currently
   `ext-cust.squarespace.com`. This is the one that becomes
   `lim2026.netlify.app`.

## After the change

- Netlify domain panel turns green when it sees the records
- `https://lutheranindianministries.org` and `https://www.…` both padlocked
- `/donate` renders the Blackbaud form
- `/healing-wounds-of-trauma` redirects to healing-groups
- Accept the cookie banner, then GA4 → Realtime shows you within seconds
- **Send yourself an email at an @lutheranindianministries.org address** — the
  single most important check, and the one people forget
- Submit `sitemap.xml` in Search Console
- Record the cutover date in `status.html` as the analytics baseline
