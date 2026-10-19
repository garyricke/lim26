/* "Where the hours went" — fills any <div data-hours-log> from /api/hours.
   Add data-until="YYYY-MM-DD" on a dated agenda so the list stops at the meeting.
   Grouped by month, newest first, each month with its subtotal, so a reader can
   scan where the time went and see it adds up to the hours shown above it. */
(function () {
  var el = document.querySelector('[data-hours-log]');
  if (!el) return;
  var until = el.getAttribute('data-until');
  var fmtH = function (h) { return (Math.round(h * 100) / 100).toFixed(2).replace(/0$/, '').replace(/\.0$/, '') + ' h'; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var day = function (d) { return new Date(d + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); };
  var month = function (d) { return new Date(d + 'T12:00:00').toLocaleDateString('en-US', { month: 'long', year: 'numeric' }); };

  fetch('/api/hours' + (until ? '?until=' + until : ''))
    .then(function (r) { if (!r.ok) throw r; return r.json(); })
    .then(function (d) {
      if (!d.entries || !d.entries.length) { el.innerHTML = '<p class="hl-msg">No hours logged in this block yet.</p>'; return; }
      var groups = [], byKey = {};
      d.entries.forEach(function (e) {
        var k = e.date.slice(0, 7);
        if (!byKey[k]) { byKey[k] = { label: month(e.date), hours: 0, rows: [] }; groups.push(byKey[k]); }
        byKey[k].hours += e.hours; byKey[k].rows.push(e);
      });
      el.innerHTML =
        '<details class="hl" open><summary><span class="q">Where the hours went</span>' +
        '<span class="hl-tot">' + fmtH(d.usedHours) + ' · ' + d.entries.length + ' entries</span>' +
        '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>' +
        groups.map(function (g) {
          return '<div class="hl-month"><span>' + esc(g.label) + '</span><span>' + fmtH(g.hours) + '</span></div>' +
            '<ul class="hl-list">' + g.rows.map(function (e) {
              return '<li><span class="hl-d">' + day(e.date) + '</span><span class="hl-n">' + esc(e.note) + '</span><span class="hl-h">' + fmtH(e.hours) + '</span></li>';
            }).join('') + '</ul>';
        }).join('') +
        '</details>';
    })
    .catch(function () { el.innerHTML = '<p class="hl-msg">The hours list could not load right now. The totals above are current.</p>'; });
})();
