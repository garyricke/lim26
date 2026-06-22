# Feathr Conversion Tracking — GTM Tag + Trigger Spec

**Drafted 22 Jun 2026.** Recommended install path for the *current Squarespace
site*, given that GTM container `GTM-TD3Z4XNG` is already live (header gtm.js +
footer noscript iframe, installed by John/Meyer 10/6/2025). Do everything
through GTM — no raw Code Injection edits.

Conversion ID: `6a0bb2f14647de16ae5b1ccb`
Confirmed approach: **Option A** — Blackbaud redirects a completed gift to a
LIM-controlled `/thank-you` page; the pixel fires there with the gift amount.

---

## Prerequisites (blocking — confirm before publishing)

1. **Feathr account/init ID** — needed for the base pixel. Get from John.
   *Do not duplicate the base pixel if it's already firing in GTM.* (Email sent.)
2. **Blackbaud redirect + amount param** — confirm `/thank-you` redirect is
   possible and the exact query-param name for the amount. From Angie via
   Jaylene. (Email sent.) Spec below assumes `?amount=` — change one line if not.
3. Confirm `6a0bb2f14647de16ae5b1ccb` is the **conversion** ID, not campaign ID.

---

## Tag 1 — Base / Super Pixel (only if NOT already in GTM)

- **Tag type:** Custom HTML
- **Trigger:** All Pages (Page View)
- **Skip entirely** if John confirms the base pixel is already firing.

```html
<script>
(function(f,e,a,t,h,r){
  f.feathr=h=function(){h.q.push(arguments)};h.q=[];
  r=e.createElement(a);r.async=1;r.src=t;
  e.getElementsByTagName('head')[0].appendChild(r);
})(window,document,'script','https://cdn.feathr.co/js/feathr.min.js');
feathr('init','<FEATHR_ACCOUNT_ID>');   // <-- from John
feathr('sprinkle');                      // page-view breadcrumb
</script>
```

---

## Tag 2 — Conversion (the one that closes the loop)

- **Tag type:** Custom HTML
- **Trigger:** see Trigger below (fires only on `/thank-you`)
- **Tag sequencing:** if Tag 1 is in this container, set this tag to fire only
  after Tag 1. The `typeof feathr` guard below also protects against ordering.

```html
<script>
(function(){
  if (typeof feathr !== 'function') return;                 // base pixel must be loaded
  if (sessionStorage.getItem('lim_feathr_converted')) return; // double-fire / refresh guard
  var params = new URLSearchParams(window.location.search);
  var amount = parseFloat(params.get('amount')) || 0;        // <-- CONFIRM param name w/ Angie
  feathr('convert', '6a0bb2f14647de16ae5b1ccb', {
    amount: amount,
    currency: 'USD',
    category: 'Donation'
  });
  sessionStorage.setItem('lim_feathr_converted', '1');
})();
</script>
```

### Trigger for Tag 2

- **Type:** Page View
- **Fire on:** Page Path **contains** `/thank-you`
- Optional tighten: also require Page URL contains `amount=` so it only fires
  on a real redirect, never a stray visit to the page.

---

## New site (this repo) — migration task, not now

Same two parts, same conversion ID. At migration, build a `thank-you.html` and
drop the equivalent inline script before `</head>` (base pixel) plus the
conversion snippet. Don't build it yet — the Blackbaud redirect target and
amount param aren't confirmed, and the new site isn't the live ad destination.

Standalone version of the conversion snippet for the new-site `/thank-you`:

```html
<script>
  var params = new URLSearchParams(window.location.search);
  var amount = parseFloat(params.get('amount')) || 0;
  if (typeof feathr === 'function' && !sessionStorage.getItem('lim_feathr_converted')) {
    feathr('convert', '6a0bb2f14647de16ae5b1ccb', {
      amount: amount, currency: 'USD', category: 'Donation'
    });
    sessionStorage.setItem('lim_feathr_converted', '1');
  }
</script>
```

---

## Test plan

1. Publish tags in GTM **Preview mode** first.
2. Visit `…/thank-you?amount=1` — confirm Tag 2 fires once, `feathr` defined,
   and a `convert` event with `amount: 1` appears in the GTM debug + network tab.
3. Reload the page — confirm it does **not** fire again (sessionStorage guard).
4. Run a real $1 test gift end-to-end; confirm the conversion + amount land in
   the Feathr dashboard (have John watch the dashboard side).
5. Publish the container.
