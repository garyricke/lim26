import json, html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import BOOKS, chapter, search
from data import THEMES, STORIES, QUESTIONS, PATHS, CONCORDANCE_WORDS
import build  # reuses verses()/clean()/esv_link() and (re)writes the long page
OUT="/Users/garyricke/Documents/lim2026/docs-scripture-anger-explore.html"

def passage(book,spec):
    label,vs=build.verses(book,spec)
    return {"label":label,"link":build.esv_link(book,spec),"verses":vs}

themes=[{"n":i,"title":t,"intro":intro,"passages":[passage(b,s) for b,s in refs]} for i,(t,intro,refs) in enumerate(THEMES,1)]
stories=[]
for i,st in enumerate(STORIES,1):
    title,book,rng,summary,quotes,lesson=st[:6]; extra=st[6] if len(st)>6 else []
    stories.append({"n":i,"title":title,"where":f"{book} {rng}","summary":summary,
        "passages":[passage(book,q) for q in quotes]+[passage(b,s) for b,s in extra],
        "lesson":lesson,"question":QUESTIONS[i-1]})
paths=[]
for pid,title,intro,stops in PATHS:
    ss=[]
    for s in stops:
        if s[0]=="passage": ss.append({"kind":"passage","p":passage(s[1],s[2])})
        else: ss.append({"kind":s[0],"n":s[1]})
    paths.append({"id":pid,"title":title,"intro":intro,"stops":ss})
conc=[{"b":BOOKS[b-1],"c":c,"v":v,"t":t} for (b,c,v),t in sorted(build.hits.items())]
data=json.dumps({"themes":themes,"stories":stories,"paths":paths,"conc":conc},ensure_ascii=False).replace("</","<\\/")

gate=open("/Users/garyricke/Documents/lim2026/docs-scripture-anger.html").read()
gate=gate[gate.index("<script>\n(function(){"):gate.index("</script>",gate.index("<script>\n(function(){"))+9]

page=r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#282924">
<link rel="icon" type="image/svg+xml" href="/brand/lim-favicon-2026-black-back.svg">
<title>Anger in Scripture — Explore</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,400;0,700;0,900;1,400&family=Barlow+Condensed:wght@400;600;700;800&family=Open+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{--red:#ED1C24;--yellow:#FFDE16;--charcoal:#282924;--sage:#B2AC88;--sage-d:#8a8665;--sky:#A2C2D1;--sky-d:#6fa3b8;--stone:#EBE9E4;--muted:#5a5a52;--border:#d9d6ce;
    --serif:'Merriweather',Georgia,serif;--cond:'Barlow Condensed','Arial Narrow',sans-serif;--body:'Open Sans',system-ui,sans-serif;
    --hdr:56px;--ftr:72px}
  *{margin:0;padding:0;box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{font-family:var(--body);color:var(--charcoal);background:var(--stone);line-height:1.65;min-height:100vh;overscroll-behavior-y:none}
  a{color:inherit}
  /* ── app header ── */
  .hdr{position:fixed;top:0;left:0;right:0;height:calc(var(--hdr) + env(safe-area-inset-top));padding-top:env(safe-area-inset-top);background:var(--charcoal);color:#fff;z-index:60;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;box-shadow:0 2px 10px rgba(0,0,0,.18)}
  .hdr .ib{display:inline-flex;align-items:center;gap:.3rem;height:var(--hdr);padding:0 .9rem;text-decoration:none;color:#fff;font-family:var(--cond);font-size:.95rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
  .hdr .ib svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;flex:none}
  .hdr .ib.right{justify-self:end}
  .hdr .ib:active{background:rgba(255,255,255,.08)}
  .hdr .ttl{text-align:center;font-family:var(--cond);font-size:.95rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:55vw}
  .hdr .ttl small{display:block;font-family:var(--body);font-weight:400;letter-spacing:0;text-transform:none;font-size:.7rem;color:rgba(255,255,255,.6);line-height:1.1}
  .hdr .prog{position:absolute;left:0;right:0;bottom:0;height:4px;background:rgba(255,255,255,.12)}
  .hdr .prog i{display:block;height:100%;background:var(--yellow);transition:width .35s}
  /* ── content ── */
  .wrap{max-width:720px;margin:0 auto;padding:calc(var(--hdr) + env(safe-area-inset-top) + 1.1rem) 1rem calc(var(--ftr) + env(safe-area-inset-bottom) + 1.5rem)}
  .screen{animation:slide .28s cubic-bezier(.2,.7,.2,1)}
  @keyframes slide{from{opacity:0;transform:translateX(14px)}to{opacity:1;transform:none}}
  .screen.back{animation-name:slideb}
  @keyframes slideb{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:none}}
  .eyebrow{font-family:var(--cond);font-size:.76rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--sage-d);display:block;margin-bottom:.3rem}
  h1{font-family:var(--serif);font-size:1.6rem;font-weight:900;line-height:1.2;margin-bottom:.5rem}
  h2{font-family:var(--cond);font-size:1.1rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:1.5rem 0 .6rem;color:var(--muted)}
  p{margin-bottom:.8rem;font-size:.95rem}
  .lede{font-family:var(--serif);font-size:1rem;color:var(--muted);font-style:italic;line-height:1.7}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.7rem;margin:.4rem 0 1.2rem}
  .card{display:flex;align-items:center;gap:.8rem;background:#fff;border:1px solid var(--border);border-radius:14px;padding:.95rem 1rem;text-decoration:none;color:inherit;transition:transform .12s,box-shadow .12s;position:relative;min-height:64px}
  .card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(0,0,0,.09)}
  .card:active{transform:scale(.985)}
  .card .body{flex:1;min-width:0}
  .card .num{font-family:var(--cond);font-size:.74rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--sage-d)}
  .card .t{font-family:var(--serif);font-weight:700;font-size:.97rem;line-height:1.35;margin:.1rem 0 .15rem}
  .card .s{font-size:.8rem;color:var(--muted)}
  .chev{flex:none;width:20px;height:20px;stroke:var(--sage);fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  .card.done .num::after{content:"· read";color:var(--sage-d)}
  .card.done .ico{background:var(--yellow)}
  .card .ico{flex:none;width:40px;height:40px;border-radius:12px;background:var(--stone);display:flex;align-items:center;justify-content:center;font-family:var(--cond);font-weight:800;font-size:1rem;color:var(--charcoal)}
  .card.path .ico{background:#fde3e4;color:var(--red)}
  .card.big{background:var(--charcoal);color:#fff;border:0}
  .card.big .num{color:var(--yellow)} .card.big .s{color:rgba(255,255,255,.7)} .card.big .ico{background:rgba(255,255,255,.1);color:var(--yellow)} .card.big .chev{stroke:rgba(255,255,255,.5)}
  .tiles{display:grid;grid-template-columns:1fr;gap:.7rem}
  .panel{background:#fff;border:1px solid var(--border);border-radius:16px;padding:1.2rem 1.15rem;margin-bottom:1rem}
  .passage{margin:0 0 1rem}
  .passage .ref{font-family:var(--cond);font-size:.82rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--sky-d);margin-bottom:.1rem}
  .passage .ref a{text-decoration:none} .passage .ref a:hover{color:var(--red)}
  .passage .txt{font-family:var(--serif);font-size:1rem;line-height:1.8;margin:0;padding-left:.9rem;border-left:3px solid var(--stone)}
  sup{font-family:var(--body);font-size:.6em;color:var(--sage-d);margin-right:.15em;font-weight:700}
  .where{font-family:var(--cond);font-size:1rem;font-weight:700;letter-spacing:.05em;color:var(--sky-d);margin:0 0 .7rem}
  .lesson{background:#fffbe6;border-left:4px solid var(--yellow);padding:.7rem .9rem;font-size:.92rem;border-radius:0 8px 8px 0;margin:.4rem 0 .9rem}
  .question{background:var(--charcoal);color:#fff;border-radius:14px;padding:1rem 1.1rem;margin:.4rem 0 .4rem}
  .question .eyebrow{color:var(--yellow)} .question p{font-family:var(--serif);font-size:1rem;margin:0;line-height:1.6}
  .steps{list-style:none;margin:.6rem 0 1rem;background:#fff;border:1px solid var(--border);border-radius:14px;overflow:hidden}
  .steps li a{display:flex;gap:.8rem;align-items:center;}
  .steps li a .body{flex:1;min-width:0}
  .steps li a .num{font-family:var(--cond);font-size:.72rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--sage-d)}
  .steps li a{padding:.75rem 1rem;border-bottom:1px solid var(--border);font-size:.93rem;text-decoration:none;min-height:52px}
  .steps li:last-child a{border-bottom:0}
  .steps li b{font-family:var(--cond);color:var(--charcoal);background:var(--stone);width:1.7rem;height:1.7rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex:none}
  .steps li.done b{background:var(--yellow)}
  .dots{display:flex;gap:.35rem;flex-wrap:wrap;margin:.2rem 0 .9rem}
  .dots a{width:.62rem;height:.62rem;border-radius:50%;background:#fff;border:1.5px solid var(--sage);display:block}
  .dots a.on{background:var(--red);border-color:var(--red)}
  .search{width:100%;font:inherit;font-size:1.05rem;padding:.9rem 1rem .9rem 2.6rem;border:1.5px solid var(--border);border-radius:12px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%238a8665' stroke-width='2.2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-3.5-3.5'/%3E%3C/svg%3E") .9rem center/20px no-repeat;outline:none;-webkit-appearance:none}
  .search:focus{border-color:var(--charcoal)}
  .chips{display:flex;gap:.4rem;flex-wrap:wrap;margin:.7rem 0 1rem}
  .chip{font-family:var(--cond);font-size:.85rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:.35rem .75rem;border-radius:20px;background:#fff;border:1.5px solid var(--border);text-decoration:none;cursor:pointer}
  .chip:hover,.chip.on{background:var(--charcoal);color:#fff;border-color:var(--charcoal)}
  .cv{background:#fff;border:1px solid var(--border);border-radius:12px;padding:.7rem .9rem;margin-bottom:.5rem;font-size:.92rem;line-height:1.6}
  .cv .cref{font-family:var(--cond);font-weight:700;color:var(--sky-d);letter-spacing:.05em;text-decoration:none;margin-right:.4rem}
  mark{background:#fff1a8;color:inherit;padding:0 .1em;border-radius:2px}
  .count{font-size:.85rem;color:var(--muted);margin:.2rem 0 .8rem}
  .foot{font-size:.74rem;color:var(--muted);margin-top:2rem;border-top:1px solid var(--border);padding-top:.8rem}
  /* ── fixed bottom bar: prev/next OR tabs ── */
  .ftr{position:fixed;left:0;right:0;bottom:0;z-index:60;background:rgba(255,255,255,.96);backdrop-filter:saturate(1.2) blur(8px);-webkit-backdrop-filter:saturate(1.2) blur(8px);border-top:1px solid var(--border);padding:.55rem .8rem calc(.55rem + env(safe-area-inset-bottom))}
  .ftr .in{max-width:720px;margin:0 auto;display:flex;gap:.6rem;align-items:stretch}
  .btn{font-family:var(--cond);font-size:.95rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:.6rem 1rem;border-radius:12px;border:0;background:var(--yellow);color:var(--charcoal);text-decoration:none;cursor:pointer;display:inline-flex;align-items:center;gap:.4rem;line-height:1.1;min-height:52px}
  .btn:active{transform:scale(.98)}
  .btn svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;flex:none}
  .btn.ghost.sq{padding:0;width:52px;justify-content:center}
  .btn.ghost{background:#fff;border:1.5px solid var(--border);color:var(--charcoal)}
  .btn.disabled{opacity:.35;pointer-events:none}
  .btn small{display:block;font-family:var(--body);font-weight:400;letter-spacing:0;text-transform:none;font-size:.74rem;color:rgba(40,41,36,.7);margin-top:.15rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:60vw}
  .btn.next{flex:1;justify-content:center;text-align:left;flex-direction:column;align-items:flex-start;gap:.05rem;min-width:0}
  .btn.next .lbl{display:flex;align-items:center;gap:.4rem}
  .btn.end{background:var(--charcoal);color:#fff} .btn.end small{color:rgba(255,255,255,.7)}
  .tabs{display:flex;justify-content:space-around;width:100%}
  .tab{flex:1;display:flex;flex-direction:column;align-items:center;gap:.15rem;text-decoration:none;font-family:var(--cond);font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:.2rem 0}
  .tab svg{width:24px;height:24px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .tab.on{color:var(--red)}
  .kbd{display:none}
  @media (min-width:700px){.kbd{display:block;font-size:.76rem;color:var(--muted);text-align:center;margin-top:1rem}.kbd b{display:inline-block;border:1px solid var(--border);border-radius:4px;padding:0 .35rem;background:#fff;font-weight:600}.tiles{grid-template-columns:repeat(3,1fr)}.hdr .ttl{max-width:none}}
</style>
__GATE__
</head>
<body>
<header class="hdr" id="hdr"></header>
<main class="wrap" id="app"></main>
<footer class="ftr" id="ftr"></footer>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent);
  var app=document.getElementById('app'),hdr=document.getElementById('hdr'),ftr=document.getElementById('ftr');
  var READ_KEY='lim_anger_read';
  function readSet(){try{return JSON.parse(localStorage.getItem(READ_KEY)||'[]')}catch(e){return[]}}
  function markRead(n){var s=readSet();if(s.indexOf(n)<0){s.push(n);try{localStorage.setItem(READ_KEY,JSON.stringify(s))}catch(e){}}}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  var I={home:'<svg viewBox="0 0 24 24"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>',
         back:'<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>',
         chev:'<svg class="chev" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>',
         book:'<svg viewBox="0 0 24 24"><path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/></svg>',
         list:'<svg viewBox="0 0 24 24"><path d="M8 6h13M8 12h13M8 18h13"/><circle cx="3.5" cy="6" r="1"/><circle cx="3.5" cy="12" r="1"/><circle cx="3.5" cy="18" r="1"/></svg>',
         find:'<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
         doc:'<svg viewBox="0 0 24 24"><path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5M9 13h6M9 17h6"/></svg>'};
  function passage(p){return '<div class="passage"><div class="ref"><a href="'+p.link+'" target="_blank" rel="noopener">'+esc(p.label)+'</a></div><p class="txt">'+p.verses.map(function(v){return '<sup>'+v[0]+'</sup>'+esc(v[1])}).join(' ')+'</p></div>'}
  function storyCard(s){return '<a class="card'+(readSet().indexOf(s.n)>=0?' done':'')+'" href="#/story/'+s.n+'"><span class="ico">'+s.n+'</span><span class="body"><span class="num">Story</span><div class="t">'+esc(s.title)+'</div><div class="s">'+esc(s.where)+'</div></span>'+I.chev+'</a>'}
  function themeCard(t){return '<a class="card" href="#/theme/'+t.n+'"><span class="ico">'+t.n+'</span><span class="body"><span class="num">Theme</span><div class="t">'+esc(t.title)+'</div><div class="s">'+t.passages.length+' passages</div></span>'+I.chev+'</a>'}
  function pathCard(p,k){return '<a class="card path" href="#/path/'+p.id+'"><span class="ico">'+(k+1)+'</span><span class="body"><div class="t">'+esc(p.title)+'</div><div class="s">'+p.stops.length+' stops</div></span>'+I.chev+'</a>'}
  function stopTitle(st){if(st.kind==='story')return D.stories[st.n-1].title;if(st.kind==='theme')return D.themes[st.n-1].title;return st.p.label}
  function stopKind(st){return st.kind==='story'?'Story':st.kind==='theme'?'Theme':'Passage'}

  // Each screen returns {title, sub, back, body, prev, next, nextLabel, nextSub, progress, tab}
  function home(){
    var r=readSet().length;
    return {title:'Anger in Scripture',sub:'ESV · Christ-Centered Anger Management',back:null,tab:'home',body:
      '<span class="eyebrow">Start here</span><h1>Where do you want to start?</h1>'
      +'<p class="lede">Pick the question closest to you and walk a short path through what the Bible says — or browse on your own.</p>'
      +'<div class="cards">'+D.paths.map(pathCard).join('')+'</div>'
      +'<h2>Browse on your own</h2><div class="tiles">'
      +'<a class="card big" href="#/stories"><span class="ico">'+D.stories.length+'</span><span class="body"><span class="num">Stories</span><div class="t">Where anger drives the plot</div><div class="s">'+(r?r+' of '+D.stories.length+' read':'Cain to Ephesus, one at a time')+'</div></span>'+I.chev+'</a>'
      +'<a class="card big" href="#/themes"><span class="ico">'+D.themes.length+'</span><span class="body"><span class="num">Themes</span><div class="t">The teaching passages</div><div class="s">God\'s anger, ours, Jesus, forgiveness</div></span>'+I.chev+'</a>'
      +'<a class="card big" href="#/search"><span class="ico">'+D.conc.length+'</span><span class="body"><span class="num">Verses</span><div class="t">Find a verse</div><div class="s">Every ESV verse that speaks of anger</div></span>'+I.chev+'</a>'
      +'</div><p class="foot">Scripture quotations are from The ESV® Bible (The Holy Bible, English Standard Version®), © 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved. Working draft for LIM staff — not for distribution. <a href="/anger-scripture">Read it as one document</a>.</p>'};
  }
  function stories(){return {title:'Stories',sub:D.stories.length+' in Bible order',back:'#/',tab:'stories',body:'<h1>Where anger drives the plot</h1><p class="lede">Each one: what happened, the verses that carry it, what it shows, and a question to sit with.</p><div class="cards">'+D.stories.map(storyCard).join('')+'</div>'}}
  function themes(){return {title:'Themes',sub:D.themes.length+' sessions of Scripture',back:'#/',tab:'themes',body:'<h1>The teaching passages</h1><p class="lede">Nine themes, each one a session\'s worth of Scripture.</p><div class="cards">'+D.themes.map(themeCard).join('')+'</div>'}}
  function storyBody(s){
    return '<span class="eyebrow">Story '+s.n+' of '+D.stories.length+'</span><h1>'+esc(s.title)+'</h1><p class="where">'+esc(s.where)+'</p><p>'+esc(s.summary)+'</p>'
      +s.passages.map(passage).join('')+'<div class="lesson"><b>What it shows.</b> '+esc(s.lesson)+'</div>'
      +'<div class="question"><span class="eyebrow">To sit with</span><p>'+esc(s.question)+'</p></div>';
  }
  function story(n){
    var s=D.stories[n-1]; if(!s)return home(); markRead(n);
    var p=D.stories[n-2],nx=D.stories[n];
    return {title:'Story '+n+' of '+D.stories.length,sub:s.title,back:'#/stories',tab:'stories',progress:n/D.stories.length,
      body:'<div class="panel">'+storyBody(s)+'</div><p class="kbd">Use <b>←</b> <b>→</b> to move between stories</p>',
      prev:p?'#/story/'+p.n:null,next:nx?'#/story/'+nx.n:'#/',nextLabel:nx?'Next story':'Finished',nextSub:nx?nx.title:'Back to the start',end:!nx};
  }
  function themeBody(t,i,inPath){
    var m=t.passages.length; i=Math.min(Math.max(i||0,0),m-1);
    if(inPath) return '<span class="eyebrow">Theme '+t.n+'</span><h1>'+esc(t.title)+'</h1><p class="lede">'+esc(t.intro)+'</p>'+t.passages.map(passage).join('');
    var dots='<div class="dots">'+t.passages.map(function(_,k){return '<a href="#/theme/'+t.n+'/'+(k+1)+'" class="'+(k===i?'on':'')+'" title="'+esc(t.passages[k].label)+'"></a>'}).join('')+'</div>';
    return '<span class="eyebrow">Passage '+(i+1)+' of '+m+'</span><h1>'+esc(t.title)+'</h1><p class="lede">'+esc(t.intro)+'</p>'+dots+passage(t.passages[i]);
  }
  function theme(n,i){
    var t=D.themes[n-1]; if(!t)return home(); i=(parseInt(i,10)||1)-1; var m=t.passages.length;
    var prev=i>0?'#/theme/'+n+'/'+i:(D.themes[n-2]?'#/theme/'+(n-1)+'/'+D.themes[n-2].passages.length:null);
    var next=i<m-1?'#/theme/'+n+'/'+(i+2):(D.themes[n]?'#/theme/'+(n+1)+'/1':'#/');
    return {title:'Theme '+n+' of '+D.themes.length,sub:t.title,back:'#/themes',tab:'themes',progress:(i+1)/m,
      body:'<div class="panel">'+themeBody(t,i)+'</div><p class="kbd">Use <b>←</b> <b>→</b> to move through the passages · <a href="/anger-scripture#t'+n+'">read this theme as one page</a></p>',
      prev:prev,next:next,nextLabel:i<m-1?'Next passage':(D.themes[n]?'Next theme':'Finished'),nextSub:i<m-1?t.passages[i+1].label:(D.themes[n]?D.themes[n].title:'Back to the start'),end:!(i<m-1||D.themes[n])};
  }
  function path(id,step){
    var p=null;D.paths.forEach(function(x){if(x.id===id)p=x});if(!p)return home();
    var rs=readSet();
    if(!step){
      return {title:'A path',sub:p.stops.length+' stops',back:'#/',tab:'home',
        body:'<span class="eyebrow">A path · '+p.stops.length+' stops</span><h1>'+esc(p.title)+'</h1><p class="lede">'+esc(p.intro)+'</p>'
        +'<ol class="steps">'+p.stops.map(function(st,k){return '<li'+(st.kind==='story'&&rs.indexOf(st.n)>=0?' class="done"':'')+'><a href="#/path/'+id+'/'+(k+1)+'"><b>'+(k+1)+'</b><span class="body"><span class="num">'+stopKind(st)+'</span><div class="t" style="font-family:var(--serif);font-weight:700;font-size:.95rem">'+esc(stopTitle(st))+'</div></span>'+I.chev+'</a></li>'}).join('')+'</ol>',
        prev:null,next:'#/path/'+id+'/1',nextLabel:'Begin',nextSub:stopKind(p.stops[0])+': '+stopTitle(p.stops[0])};
    }
    var k=Math.min(Math.max(parseInt(step,10)||1,1),p.stops.length),st=p.stops[k-1],body='';
    if(st.kind==='story'){markRead(st.n);body=storyBody(D.stories[st.n-1]);}
    else if(st.kind==='theme'){body=themeBody(D.themes[st.n-1],0,true);}
    else{body='<span class="eyebrow">Passage</span><h1>'+esc(st.p.label)+'</h1>'+passage(st.p);}
    var nx=p.stops[k], others=D.paths.filter(function(x){return x.id!==id}).slice(0,3);
    return {title:'Stop '+k+' of '+p.stops.length,sub:p.title,back:'#/path/'+id,tab:'home',progress:k/p.stops.length,
      body:'<div class="panel">'+body+'</div>'+(nx?'':'<h2>Another path</h2><div class="cards">'+others.map(pathCard).join('')+'</div>')+'<p class="kbd">Use <b>←</b> <b>→</b> to move along the path</p>',
      prev:k>1?'#/path/'+id+'/'+(k-1):'#/path/'+id,next:nx?'#/path/'+id+'/'+(k+1):'#/',nextLabel:nx?'Next stop':'End of path',nextSub:nx?stopKind(nx)+': '+stopTitle(nx):'Back to the start',end:!nx};
  }
  var CHIPS=['anger','angry','wrath','rage','fury','indignation','provoke','slow to anger'];
  function searchScreen(q){
    q=(q||'').trim(); var res=[],rx=null;
    if(q){var qq=q.toLowerCase();rx=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');
      res=D.conc.filter(function(v){return v.t.toLowerCase().indexOf(qq)>=0||(v.b+' '+v.c+':'+v.v).toLowerCase().indexOf(qq)===0||v.b.toLowerCase()===qq})}
    var list=q?(res.length?res.slice(0,150).map(function(v){var t=esc(v.t);if(rx)t=t.replace(rx,'<mark>$1</mark>');var bn=v.b==='Psalms'?'Psalm':v.b;return '<div class="cv"><a class="cref" target="_blank" rel="noopener" href="https://www.esv.org/'+encodeURIComponent(bn+' '+v.c+':'+v.v)+'/">'+esc(bn)+' '+v.c+':'+v.v+'</a>'+t+'</div>'}).join('')+(res.length>150?'<p class="count">Showing 150 of '+res.length+' — narrow the search.</p>':''):'<p class="count">Nothing matches that. Try a word like <i>wrath</i> or a book like <i>Proverbs</i>.</p>'):'';
    return {title:'Find a verse',sub:D.conc.length+' verses',back:'#/',tab:'search',
      body:'<input class="search" id="q" type="search" placeholder="A word, a phrase, or a book…" value="'+esc(q)+'" autocomplete="off">'
      +'<div class="chips">'+CHIPS.map(function(c){return '<a class="chip'+(c===q?' on':'')+'" href="#/search/'+encodeURIComponent(c)+'">'+c+'</a>'}).join('')+'</div>'
      +(q?'<p class="count">'+res.length+' verse'+(res.length===1?'':'s')+'</p>':'<p class="lede">Every verse in the ESV that speaks of anger. Type a word, a phrase, or a book name.</p>')+list};
  }
  function renderHdr(s){
    hdr.innerHTML=(s.back?'<a class="ib" href="'+s.back+'">'+I.back+'Back</a>':'<span class="ib" style="opacity:.0"></span>')
      +'<div class="ttl">'+esc(s.title)+(s.sub?'<small>'+esc(s.sub)+'</small>':'')+'</div>'
      +'<a class="ib right" href="#/" title="Start">'+I.home+'<span class="hx">Start</span></a>'
      +(s.progress!=null?'<div class="prog"><i style="width:'+Math.round(s.progress*100)+'%"></i></div>':'');
  }
  function renderFtr(s){
    if(s.next){
      ftr.innerHTML='<div class="in">'+(s.prev?'<a class="btn ghost sq" href="'+s.prev+'" title="Previous">'+I.back+'</a>':'<span class="btn ghost sq disabled">'+I.back+'</span>')
        +'<a class="btn next'+(s.end?' end':'')+'" href="'+s.next+'"><span class="lbl">'+esc(s.nextLabel)+' ›</span><small>'+esc(s.nextSub||'')+'</small></a>'
        +'<a class="btn ghost sq" href="#/" title="Start">'+I.home+'</a></div>';
    }else{
      var t=s.tab;
      ftr.innerHTML='<div class="in"><nav class="tabs">'
        +'<a class="tab'+(t==='home'?' on':'')+'" href="#/">'+I.home+'Start</a>'
        +'<a class="tab'+(t==='stories'?' on':'')+'" href="#/stories">'+I.book+'Stories</a>'
        +'<a class="tab'+(t==='themes'?' on':'')+'" href="#/themes">'+I.list+'Themes</a>'
        +'<a class="tab'+(t==='search'?' on':'')+'" href="#/search">'+I.find+'Find</a>'
        +'<a class="tab" href="/anger-scripture">'+I.doc+'Document</a></nav></div>';
    }
  }
  var cur=null,lastHash='';
  function route(){
    var h=location.hash.replace(/^#\/?/,''),parts=h.split('/').map(decodeURIComponent),v=parts[0]||'',s;
    if(v==='')s=home();
    else if(v==='stories')s=stories();
    else if(v==='story')s=story(parseInt(parts[1],10));
    else if(v==='themes')s=themes();
    else if(v==='theme')s=theme(parseInt(parts[1],10),parts[2]);
    else if(v==='path')s=path(parts[1],parts[2]);
    else if(v==='search')s=searchScreen(parts.slice(1).join('/'));
    else s=home();
    var goingBack=cur&&cur.back===('#'+('/'+h).replace(/\/+$/,''))||(cur&&h.length<lastHash.length&&h.split('/')[0]===lastHash.split('/')[0]&&v!=='search');
    cur=s; lastHash=h;
    app.innerHTML='<div class="screen'+(goingBack?' back':'')+'">'+s.body+'</div>';
    renderHdr(s); renderFtr(s); window.scrollTo(0,0);
    var q=document.getElementById('q');
    if(q){var t;q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){history.replaceState(null,'','#/search/'+encodeURIComponent(q.value));var pos=q.selectionStart;route();var q2=document.getElementById('q');q2.focus();q2.setSelectionRange(pos,pos);},250)});if(!q.value)q.focus();}
  }
  document.addEventListener('keydown',function(e){if(!cur||!cur.next||e.target.tagName==='INPUT')return;if(e.key==='ArrowLeft'&&cur.prev)location.hash=cur.prev;if(e.key==='ArrowRight'&&cur.next)location.hash=cur.next;});
  // swipe left/right on sequential screens
  var tx=null,ty=null;
  document.addEventListener('touchstart',function(e){tx=e.touches[0].clientX;ty=e.touches[0].clientY},{passive:true});
  document.addEventListener('touchend',function(e){if(tx==null||!cur||!cur.next)return;var dx=e.changedTouches[0].clientX-tx,dy=e.changedTouches[0].clientY-ty;tx=null;if(Math.abs(dx)>70&&Math.abs(dy)<50){if(dx<0&&cur.next)location.hash=cur.next;if(dx>0&&cur.prev)location.hash=cur.prev;}},{passive:true});
  window.addEventListener('hashchange',route); route();
})();
</script>
</body>
</html>'''
page=page.replace("__GATE__",gate).replace("__DATA__",data)
open(OUT,"w").write(page); print("wrote",OUT,len(page)//1024,"KB")
