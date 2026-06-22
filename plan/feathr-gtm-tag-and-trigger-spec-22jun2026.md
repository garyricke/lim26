# Feathr Conversion Tracking — GTM Tag + Trigger Spec

**Drafted 22 Jun 2026; revised after Angie's reply + inspecting the live form.**
Install path for the *current Squarespace site*, which already runs GTM
container `GTM-TD3Z4XNG` (installed by John/Meyer 10/6/2025). Do everything
through GTM — no raw Code Injection edits.

Conversion ID: `6a0bb2f14647de16ae5b1ccb`

**Ownership:** John (Meyer) manages the container, so Gary hands him the tags +
triggers below ready to paste and John publishes them. Gary does not edit the
container directly.

---

## The donation form — confirmed setup (22 Jun)

Per Angie (Blackbaud admin) + inspection of `lutheranindianministries.org/donate`:

- It's the **older Online Express (OLX)**, embedded via **BBOX webforms**:
  `bbox.showForm('82adc758-cd1c-42f0-981c-36c79eaabd08')` loading
  `https://bbox.blackbaudhosting.com/webforms/bbox-min.js`.
- OLX has **no native GTM/GA integration** and **cannot auto-redirect** after a
  gift. So Option A (redirect to `/thank-you`) is **dead**, and the native
  Google-tracking path is **out**.
- BUT the form (and its confirmation) **renders inline in the `/donate` DOM**
  — confirmed because the page's own CSS styles the BBOX field classes
  (`.BBFormSection`, `.BBFormFieldLabel`). So our own JS on `/donate` *can* see
  the form and the confirmation.
- The OLX confirmation/thank-you renders as a DOM node with the
  well-documented id **`#bboxdonation_divThanks`** (refs: Ailm Consulting,
  DigitalWerks, Lazy Ferret OLX-tracking guides). That is our fire trigger.

**Net:** fire the Feathr conversion on `/donate` itself, via a MutationObserver
that waits for the inline confirmation, capturing the amount from the form. No
action needed from Angie.

---

## Prerequisites (blocking)

1. **Feathr account/init ID + base pixel** — the base `feathr()` loader must be
   present on `/donate`. Confirm whether it's already in GTM and get the account
   ID from John. (Email sent 22 Jun — awaiting reply.)
2. Confirm `6a0bb2f14647de16ae5b1ccb` is the **conversion** ID, not campaign ID.
3. **Verify the form's field/confirmation selectors in GTM Preview** against
   LIM's actual form (the confirmation id is standard; the *amount* field id
   varies per form — adjust the selector in Tag 2 after a Preview/test gift).

---

## Tag 1 — Base / Super Pixel (only if NOT already in GTM)

- **Tag type:** Custom HTML · **Trigger:** All Pages (must include `/donate`)
- Skip if John confirms the base pixel already fires.

```html
<script>
(function(f,e,a,t,h,r){
  f.feathr=h=function(){h.q.push(arguments)};h.q=[];
  r=e.createElement(a);r.async=1;r.src=t;
  e.getElementsByTagName('head')[0].appendChild(r);
})(window,document,'script','https://cdn.feathr.co/js/feathr.min.js');
feathr('init','<FEATHR_ACCOUNT_ID>');   // <-- from John
feathr('sprinkle');
</script>
```

---

## Tag 2 — OLX conversion (fires on the inline Thank-You)

- **Tag type:** Custom HTML
- **Trigger:** Page View — Page Path **contains** `/donate`
- **Sequencing:** fire after Tag 1 if Tag 1 is in this container; the
  `typeof feathr` guard also protects against ordering.

```html
<script>
(function(){
  // Feathr conversion for the OLX/BBOX donation form (renders inline on /donate).
  // Requires the Feathr base pixel present so feathr() is defined (Tag 1 / John).
  var CONVERSION_ID = '6a0bb2f14647de16ae5b1ccb';
  var lastAmount = 0;

  // 1) Capture the gift amount as the donor fills the form (OLX confirms async,
  //    so grab it before submission). VERIFY these selectors in GTM Preview.
  function captureAmount(){
    var el = document.querySelector(
      '#bboxdonation_radioAmt input[type=radio]:checked, #bboxdonation_txtAmt, ' +
      'input[id*="Amt"], input[name*="mount"]');
    var v = el ? parseFloat(String(el.value||'').replace(/[^0-9.]/g,'')) : NaN;
    if (!isNaN(v) && v > 0) lastAmount = v;
  }
  document.addEventListener('change', captureAmount, true);
  document.addEventListener('click',  captureAmount, true);

  // 2) Fire once when the inline confirmation (#bboxdonation_divThanks) appears.
  function fire(){
    if (sessionStorage.getItem('lim_feathr_converted')) return;
    if (typeof feathr !== 'function') return;
    var thanks = document.getElementById('bboxdonation_divThanks');
    var amt = lastAmount;
    if (thanks) {                                  // prefer amount shown on confirmation
      var m = thanks.textContent.match(/\$\s*([0-9,]+(?:\.[0-9]{2})?)/);
      if (m) { var t = parseFloat(m[1].replace(/,/g,'')); if (!isNaN(t) && t > 0) amt = t; }
    }
    feathr('convert', CONVERSION_ID, { amount: amt || 0, currency: 'USD', category: 'Donation' });
    sessionStorage.setItem('lim_feathr_converted','1');
  }
  new MutationObserver(function(){
    var t = document.getElementById('bboxdonation_divThanks');
    if (t && t.offsetParent !== null) fire();        // visible confirmation
  }).observe(document.documentElement, { childList:true, subtree:true });
})();
</script>
```

---

## Fallback (only if the inline approach can't be verified)

Angie noted OLX lets you add a **link in the confirmation message**. We could
point that link at a LIM `/thank-you?amount=…` page that fires the pixel — but
it only counts donors who *click* it, so it badly undercounts. Use the inline
MutationObserver approach above; keep this link idea only as a last resort.

---

## New site (this repo) — migration task

At migration the donation form may move to a modern Blackbaud Optimized
Donation Form (native GTM/GA + redirect support) or a new processor — re-spec
then. Reuse the same conversion ID `6a0bb2f14647de16ae5b1ccb` for continuity.

---

## Test plan

1. In GTM Preview on `/donate`, confirm `feathr` is defined and the observer
   is installed.
2. Inspect the live form: confirm the amount field selector and that the
   confirmation really is `#bboxdonation_divThanks` (adjust Tag 2 if not).
3. Make a real (or $1 test) gift end-to-end; confirm one `convert` event with
   the correct amount fires when the Thank-You shows, and it does **not**
   re-fire on reload (sessionStorage guard).
4. Confirm the conversion + amount land in the Feathr dashboard (John watches).
5. John publishes the container.
