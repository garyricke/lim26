import re, html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import BOOKS, chapter, search
from data import THEMES, STORIES, CONCORDANCE_WORDS

OUT="/Users/garyricke/Documents/lim2026/docs-scripture-anger.html"
def bnum(name): return BOOKS.index(name)+1
def clean(t):
    t=re.sub(r"<(?!/?mark)[^>]+>"," ",t)          # drop every tag except <mark>
    t=t.replace(" "," ")
    return re.sub(r"\s+"," ",t).strip()
def verses(book,spec):
    """spec 'c:v' or 'c:v-v' -> (label, [(v,text)])"""
    ch,vv=spec.split(":"); ch=int(ch)
    a,b=(vv.split("-")+[None])[:2]; a=int(a); b=int(b) if b else a
    data={d["verse"]:clean(d["text"]) for d in chapter(bnum(book),ch)}
    out=[(v,data[v]) for v in range(a,b+1) if v in data]
    assert len(out)==b-a+1, f"missing verses {book} {spec}"
    label=f"{'Psalm' if book=='Psalms' else book} {ch}:{a}" + (f"–{b}" if b!=a else "")
    return label,out
def esv_link(book,spec):
    return "https://www.esv.org/"+(('Psalm' if book=='Psalms' else book)+"+"+spec).replace(" ","+")+"/"
def render_passage(book,spec,cls="passage"):
    label,vs=verses(book,spec)
    body="".join(f'<sup>{v}</sup>{html.escape(t)} ' for v,t in vs)
    return (f'<div class="{cls}"><div class="ref"><a href="{esv_link(book,spec)}" target="_blank" rel="noopener">{label}</a></div>'
            f'<p class="txt">{body.strip()}</p></div>')

parts=[]
# ---------- Part 1 ----------
n_theme_verses=0
p1=[]
for i,(title,intro,refs) in enumerate(THEMES,1):
    p1.append(f'<section class="theme" id="t{i}"><h3>{i} · {html.escape(title)}</h3><p class="lede">{html.escape(intro)}</p>')
    for book,spec in refs:
        p1.append(render_passage(book,spec)); n_theme_verses+=len(verses(book,spec)[1])
    p1.append('</section>')
# ---------- Part 2 ----------
p2=[]; n_story_verses=0
for i,st in enumerate(STORIES,1):
    title,book,rng,summary,quotes,lesson=st[:6]; extra=st[6] if len(st)>6 else []
    p2.append(f'<section class="story" id="s{i}"><span class="era">Story {i}</span><h3 class="story-h">{html.escape(title)}</h3>'
              f'<p class="where">{html.escape(book)} {html.escape(rng)}</p><p>{html.escape(summary)}</p>')
    for q in quotes:
        p2.append(render_passage(book,q)); n_story_verses+=len(verses(book,q)[1])
    for eb,eq in extra:
        p2.append(render_passage(eb,eq)); n_story_verses+=len(verses(eb,eq)[1])
    p2.append(f'<p class="lesson"><strong>What it shows.</strong> {html.escape(lesson)}</p></section>')
# ---------- Part 3 ----------
pat=re.compile(r"\b("+"|".join(re.escape(w) for w in CONCORDANCE_WORDS)+r")\b",re.I)
hits={}
for w in CONCORDANCE_WORDS:
    for r in search(w)["results"]:
        t=clean(r["text"]).replace("<mark>","").replace("</mark>","")
        if pat.search(t): hits[(r["book"],r["chapter"],r["verse"])]=t
p3=[]; bybook={}
for k in sorted(hits): bybook.setdefault(k[0],[]).append(k)
for b,keys in bybook.items():
    p3.append(f'<details class="cbook" open><summary>{BOOKS[b-1]} <span class="cnt">{len(keys)}</span></summary>')
    for (bb,c,v) in keys:
        t=pat.sub(lambda m:f"<mark>{m.group(0)}</mark>",html.escape(hits[(bb,c,v)]))
        p3.append(f'<p class="cv"><a class="cref" href="{esv_link(BOOKS[b-1],f"{c}:{v}")}" target="_blank" rel="noopener">{c}:{v}</a>{t}</p>')
    p3.append('</details>')
n_conc=len(hits)
total_quoted=n_theme_verses+n_story_verses
print("theme verses",n_theme_verses,"story verses",n_story_verses,"concordance",n_conc,"books",len(bybook))

toc1="".join(f'<li><a href="#t{i}">{html.escape(t[0])}</a></li>' for i,t in enumerate(THEMES,1))
toc2="".join(f'<li><a href="#s{i}">{html.escape(s[0])}</a></li>' for i,s in enumerate(STORIES,1))
words=", ".join(CONCORDANCE_WORDS)

page=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" type="image/svg+xml" href="/brand/lim-favicon-2026-black-back.svg">
<title>What the Bible Says About Anger — ESV resource for Christ-Centered Anger Management</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&family=Barlow+Condensed:wght@400;600;700;800&family=Open+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{--red:#ED1C24;--yellow:#FFDE16;--charcoal:#282924;--sage:#B2AC88;--sage-d:#8a8665;--sky:#A2C2D1;--sky-d:#6fa3b8;--stone:#EBE9E4;--muted:#5a5a52;--border:#d9d6ce;
    --serif:'Merriweather',Georgia,serif;--cond:'Barlow Condensed','Arial Narrow',sans-serif;--body:'Open Sans',system-ui,sans-serif}}
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{font-family:var(--body);color:var(--charcoal);background:var(--stone);line-height:1.72}}
  .bar{{background:var(--charcoal);color:#fff;padding:.9rem 1.5rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;position:sticky;top:0;z-index:50}}
  .bar h1{{font-family:var(--cond);font-size:1.1rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin-right:auto}}
  .bar nav a{{color:rgba(255,255,255,.75);text-decoration:none;font-family:var(--cond);font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;margin-right:1rem}}
  .bar nav a:hover{{color:var(--yellow)}}
  .bar button{{font-family:var(--cond);font-size:.82rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;padding:.55rem 1.2rem;border:0;border-radius:5px;background:var(--yellow);color:var(--charcoal);cursor:pointer}}
  .doc{{max-width:7.4in;margin:2rem auto 4rem;background:#fff;padding:.85in .95in 1in;box-shadow:0 8px 30px rgba(0,0,0,.13)}}
  .mast{{border-bottom:3px solid var(--charcoal);padding-bottom:1rem;margin-bottom:1.6rem}}
  .mast img{{height:42px;margin-bottom:1.1rem}}
  .mast .lbl{{font-family:var(--cond);font-size:.74rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--sage-d);display:block;margin-bottom:.4rem}}
  .mast h2{{font-family:var(--serif);font-size:1.95rem;font-weight:900;line-height:1.2}}
  .mast .sub{{font-size:.9rem;color:var(--muted);margin-top:.55rem}}
  h3{{font-family:var(--cond);font-size:1.2rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:2.2rem 0 .5rem;padding-bottom:.3rem;border-bottom:1px solid var(--border);break-after:avoid}}
  .part{{font-family:var(--serif);font-size:1.5rem;font-weight:900;margin:3rem 0 .4rem;break-before:page}}
  .part small{{display:block;font-family:var(--cond);font-size:.78rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--sage-d);margin-bottom:.3rem}}
  p{{margin-bottom:.9rem;font-size:.95rem}}
  .lede{{font-family:var(--serif);font-size:.98rem;line-height:1.7;color:var(--muted);font-style:italic}}
  .editor{{background:#fff6f6;border-left:5px solid var(--red);border-radius:6px;padding:1.15rem 1.3rem;margin-bottom:2rem}}
  .editor h4{{font-family:var(--cond);font-size:.9rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;margin-bottom:.55rem}}
  .editor p,.editor li{{font-size:.87rem;color:var(--muted);margin-bottom:.5rem}}
  .editor ol{{margin:.4rem 0 .2rem 1.2rem}} .editor strong{{color:var(--charcoal)}}
  .toc{{columns:2;column-gap:2rem;font-size:.88rem;margin:0 0 1.2rem 1.1rem}} .toc li{{break-inside:avoid;margin-bottom:.2rem}}
  .toc a{{color:var(--charcoal);text-decoration:none;border-bottom:1px dotted var(--sage)}}
  .passage{{margin:0 0 1.1rem;break-inside:avoid}}
  .passage .ref{{font-family:var(--cond);font-size:.82rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--sky-d);margin-bottom:.1rem}}
  .passage .ref a{{color:inherit;text-decoration:none}} .passage .ref a:hover{{color:var(--red)}}
  .passage .txt{{font-family:var(--serif);font-size:.95rem;line-height:1.75;margin:0;padding-left:1rem;border-left:3px solid var(--stone)}}
  sup{{font-family:var(--body);font-size:.6em;color:var(--sage-d);margin-right:.15em;font-weight:700}}
  .story{{margin-bottom:1.6rem}} .story .era{{font-family:var(--cond);font-size:.74rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--sage-d);display:block;margin-top:2rem}}
  .story-h{{margin-top:0}} .where{{font-family:var(--cond);font-size:.95rem;font-weight:700;letter-spacing:.06em;color:var(--sky-d);margin:-.2rem 0 .6rem}}
  .lesson{{background:#fffbe6;border-left:4px solid var(--yellow);padding:.6rem .9rem;font-size:.9rem;border-radius:0 6px 6px 0}}
  .cbook{{margin-bottom:.6rem;border:1px solid var(--border);border-radius:6px;padding:.4rem .9rem;break-inside:avoid-page}}
  .cbook summary{{font-family:var(--cond);font-size:1.05rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;padding:.3rem 0}}
  .cnt{{display:inline-block;background:var(--stone);color:var(--muted);font-size:.75rem;border-radius:10px;padding:0 .55rem;margin-left:.4rem;vertical-align:middle}}
  .cv{{font-size:.86rem;line-height:1.55;margin:.35rem 0 .35rem 4.2rem;text-indent:-4.2rem}}
  .cref{{display:inline-block;width:3.9rem;text-indent:0;font-family:var(--cond);font-weight:700;color:var(--sky-d);text-decoration:none;letter-spacing:.04em}}
  mark{{background:#fff1a8;color:inherit;padding:0 .1em;border-radius:2px}}
  .foot{{margin-top:2.4rem;padding-top:1rem;border-top:1px solid var(--border);font-size:.78rem;color:var(--muted)}}
  @media (max-width:700px){{.doc{{padding:1.2rem 1rem;margin:0}} .toc{{columns:1}} .cv{{margin-left:0;text-indent:0}} .cref{{display:block;width:auto}}}}
  @media print{{@page{{size:letter;margin:.7in .8in}} body{{background:#fff}} .bar,.editor{{display:none!important}} .doc{{box-shadow:none;margin:0;padding:0;max-width:none}} .cbook{{border:0;padding:0}} .cbook summary::-webkit-details-marker{{display:none}} mark{{background:none;font-weight:700}} a{{color:inherit}}}}
</style>
<script>
(function(){{
  var KEY='lim_anger_auth',HASH='53d81e6c17c82d10718106513d7a21defa05a0d73b2c89f59be66b40f8a05aac';
  if(localStorage.getItem(KEY)==='ok')return;
  document.documentElement.style.visibility='hidden';
  function hexOf(buf){{return Array.from(new Uint8Array(buf)).map(function(b){{return b.toString(16).padStart(2,'0')}}).join('')}}
  function showGate(){{
    document.documentElement.style.visibility='';
    var o=document.createElement('div');o.id='auth-gate';
    o.innerHTML='<div style="background:#282924;position:fixed;inset:0;z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:2rem;font-family:\\'Open Sans\\',sans-serif">'
      +'<img src="/brand/lutheranindianMinistries-logo-horz-stacked-2026-over-dark-background.svg" alt="Lutheran Indian Ministries" style="width:200px;margin-bottom:2rem">'
      +'<h2 style="color:#fff;font-family:\\'Merriweather\\',serif;font-size:1.2rem;margin:0 0 .5rem;text-align:center">What the Bible Says About Anger</h2>'
      +'<p style="color:rgba(255,255,255,.45);font-size:.85rem;margin:0 0 2rem;text-align:center">Curriculum working draft &mdash; staff only</p>'
      +'<input id="ag-pw" type="password" placeholder="Enter password" style="width:100%;max-width:300px;padding:.75rem 1rem;border:1.5px solid rgba(255,255,255,.2);border-radius:6px;background:rgba(255,255,255,.07);color:#fff;font-size:1rem;outline:none;margin-bottom:1rem;box-sizing:border-box" autocomplete="current-password">'
      +'<div id="ag-err" style="color:#ED1C24;font-size:.85rem;min-height:1.2rem;margin-bottom:.75rem"></div>'
      +'<button id="ag-btn" style="background:#FFDE16;color:#282924;border:none;padding:.75rem 2.5rem;font-family:\\'Barlow Condensed\\',sans-serif;font-size:1.1rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;border-radius:6px;cursor:pointer;width:100%;max-width:300px">Enter</button></div>';
    document.body.appendChild(o);
    var inp=document.getElementById('ag-pw'),btn=document.getElementById('ag-btn'),err=document.getElementById('ag-err');
    function attempt(){{var pw=inp.value;if(!pw){{err.textContent='Please enter the password.';return;}}
      crypto.subtle.digest('SHA-256',new TextEncoder().encode(pw)).then(function(buf){{if(hexOf(buf)===HASH){{localStorage.setItem(KEY,'ok');o.remove();}}else{{err.textContent='Incorrect password.';inp.value='';inp.focus();}}}});}}
    btn.addEventListener('click',attempt);inp.addEventListener('keydown',function(e){{if(e.key==='Enter')attempt();}});setTimeout(function(){{inp.focus();}},100);
  }}
  if(document.body){{showGate();}}else{{document.addEventListener('DOMContentLoaded',showGate);}}
}})();
</script>
</head>
<body>
<div class="bar">
  <h1>Anger in Scripture — ESV</h1>
  <nav><a href="#part1">Passages</a><a href="#part2">Stories</a><a href="#part3">Every verse</a></nav>
  <button id="print" type="button">Print</button>
</div>

<div class="doc">
  <div class="mast">
    <img src="/brand/lutheranindianMinistries-logo-horz-stacked-2026.svg" alt="Lutheran Indian Ministries">
    <span class="lbl">Curriculum resource · Christ-Centered Anger Management</span>
    <h2>What the Bible Says About Anger</h2>
    <p class="sub">Every passage and story, in the English Standard Version. {len(THEMES)} themes · {len(STORIES)} stories · {n_conc} verses that use the word. Working draft, 16 September 2026.</p>
  </div>

  <div class="editor">
    <h4>Note to Robert and Joe — read first (this box does not print)</h4>
    <p><strong>Version.</strong> You asked for the "New English Standard version." I've taken that to mean the <strong>English Standard Version (ESV)</strong> — the translation in Lutheran Service Book and most LCMS material. If you meant the <strong>New American Standard (NASB)</strong>, say so and I'll regenerate the whole page in it; the structure stays the same.</p>
    <p><strong>How it's organised.</strong> Part 1 is the teaching passages, grouped into nine themes so a session can be built around each. Part 2 is the stories — {len(STORIES)} narratives where anger drives the plot — each with the reference, a short summary in my words, the key verses quoted, and a one-line "what it shows." Part 3 is the complete list: <strong>every verse in the ESV</strong> that uses <em>anger, angry, wrath, fury, rage, indignation, provoke</em> or their forms, by book, so nothing is missed. Every reference links to the full passage on esv.org.</p>
    <p><strong>Moses and the rock.</strong> Small correction to the version in your email: he was told to <em>speak</em> to the rock and struck it twice (Numbers 20). He did see the promised land — from Mount Nebo — but was not allowed to enter it (Deuteronomy 34). It's Story 7.</p>
    <p><strong>Copyright.</strong> Crossway allows up to 1,000 ESV verses to be quoted without permission as long as Scripture is under half of the finished work. This page quotes {total_quoted} verses in Parts 1–2 (Part 3 is a concordance). For the finished curriculum, keep the notice at the foot of this page; if the workbook ends up mostly Scripture, Crossway grants permission to ministries readily — I can draft that request.</p>
    <p><strong>What I'd like from you:</strong> which stories and themes belong in the course, and in what order. I'll then turn the selection into the participant handout.</p>
  </div>

  <h3 style="margin-top:0">Contents</h3>
  <p style="font-size:.85rem;color:var(--muted);margin-bottom:.3rem"><strong>Part 1 — Passages by theme</strong></p>
  <ol class="toc">{toc1}</ol>
  <p style="font-size:.85rem;color:var(--muted);margin-bottom:.3rem"><strong>Part 2 — Stories</strong></p>
  <ol class="toc">{toc2}</ol>
  <p style="font-size:.85rem;color:var(--muted)"><strong>Part 3 — Every verse</strong> · {n_conc} verses across {len(bybook)} books, <a href="#part3" style="color:var(--charcoal)">at the end</a>.</p>

  <h2 class="part" id="part1"><small>Part 1</small>Passages by theme</h2>
  {"".join(p1)}

  <h2 class="part" id="part2"><small>Part 2</small>Stories where anger drives the plot</h2>
  <p class="lede">Each story gives the reference for the whole passage, a summary, the verses that carry the weight, and what it shows about anger. Read the whole passage before teaching from it — the summaries are mine, the verses are Scripture.</p>
  {"".join(p2)}

  <h2 class="part" id="part3"><small>Part 3</small>Every ESV verse that speaks of anger</h2>
  <p class="lede">A word search of the whole ESV for <em>{words}</em> — {n_conc} verses in {len(bybook)} books. Most are about God's anger at sin, which is itself part of the teaching: his anger is just, slow, and satisfied in Christ. Click a book to collapse it; click a reference to read it in context.</p>
  {"".join(p3)}

  <div class="foot">
    <p>Scripture quotations are from The ESV&reg; Bible (The Holy Bible, English Standard Version&reg;), &copy; 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved. The ESV text may not be quoted in any publication made available to the public by a Creative Commons license. The ESV may not be translated in whole or in part into any other language.</p>
    <p>Summaries and theme notes prepared for Lutheran Indian Ministries, September 2026. Internal working draft — not for distribution.</p>
  </div>
</div>
<script>document.getElementById('print').addEventListener('click',function(){{window.print();}});</script>
</body>
</html>'''
open(OUT,"w").write(page); print("wrote",OUT,len(page)//1024,"KB")
