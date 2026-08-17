# Print export

**Rule: never ship a "Print / Save PDF" button that calls `window.print()`.**

People's print setups are not set up properly. Browser print dialogs default to
adding page headers and footers, dropping background graphics, and scaling to
fit — so what a person saves is almost never what we designed. Every printable
page on this site is rendered once here, checked, and served as a finished file
behind a **Download PDF** link.

A secondary "Print" button is fine as a convenience, but the download is primary.

## Running it

```
cd print-export
npm run export              # everything
npm run export -- tol-2026  # one target, by id
```

Each run:

1. Stamps the export time into the source HTML (toolbar + in-page stamp).
2. Rewrites the `id="dl-link"` href and `download` attribute to the new
   timestamped PDF, so the page always offers the current file.
3. Renders over a short-lived local HTTP server — **not** `file://`, because the
   pages use root-absolute asset paths (`/brand/…`, `/images-master/…`) which do
   not resolve under `file://` and would silently render blank.
4. Reports any request that returned >= 400 during the render.
5. Counts pages in the finished PDF and fails loudly if it doesn't match
   `expectPages`.

## Targets

| id | kind | expect | source |
|---|---|---|---|
| `fbx-healing-2026` | sheet | 1 page | `flyer-fairbanks-healing-groups-2026.html` |
| `tol-2026` | sheet | 1 page | `flyer-tree-of-life-fairbanks-2026.html` |
| `verse-jars` | sheet | 6 pages | `verse-jars.html` |
| `lim-history` | doc | — | `docs-lim-history.html` |
| `board-report` | doc | — | `docs-board-report.html` |

- **`sheet`** — fixed artwork. Pinned to exact 8.5×11 with zero margins.
- **`doc`** — flowing multi-page text. Uses `preferCSSPageSize`, so the page's own
  `@page { size; margin }` rule decides. Set margins in the CSS, not here.

## Gotchas already paid for

- **Responsive breakpoints apply to the PDF.** A letter page is 816px wide, so a
  `@media (max-width: 920px)` rule will fire during export. Scope layout
  breakpoints to `@media screen` or the print layout silently collapses — this
  turned six verse-jar pages into twelve.
- **Don't pin a height in `@media print`.** Absolute `in` units don't resolve at
  96dpi in the print context; a 10.96in box measured 1488px and overflowed every
  page. Let the page box size itself.
- **Re-run after editing any source page**, or the download link serves a stale
  PDF while the on-screen version shows your changes.
