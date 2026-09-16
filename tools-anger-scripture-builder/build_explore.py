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
    --serif:'Merriweather',Georgia,serif;--cond:'Barlow Condensed','Arial Narrow',sans-serif;--body:'Open Sans',system-ui,sans-serif}
  *{margin:0;padding:0;box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{font-family:var(--body);color:var(--charcoal);background:var(--stone);line-height:1.65;min-height:100vh}
  a{color:inherit}
  .bar{background:var(--charcoal);color:#fff;padding:.7rem 1rem;display:flex;align-items:center;gap:.8rem;position:sticky;top:0;z-index:50}
  .bar .home{font-family:var(--cond);font-size:1rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;text-decoration:none;color:#fff;margin-right:auto;display:flex;align-items:center;gap:.5rem}
  .bar .home svg{width:22px;height:22px;stroke:var(--yellow)}
  .bar a.lnk{color:rgba(255,255,255,.75);text-decoration:none;font-family:var(--cond);font-size:.82rem;letter-spacing:.08em;text-transform:uppercase}
  .bar a.lnk:hover{color:var(--yellow)}
  .wrap{max-width:720px;margin:0 auto;padding:1.2rem 1rem 5rem}
  .screen{animation:fade .25s ease}
  @keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  .eyebrow{font-family:var(--cond);font-size:.76rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--sage-d);display:block;margin-bottom:.3rem}
  h1{font-family:var(--serif);font-size:1.7rem;font-weight:900;line-height:1.2;margin-bottom:.5rem}
  h2{font-family:var(--cond);font-size:1.15rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;margin:1.6rem 0 .6rem}
  p{margin-bottom:.8rem;font-size:.95rem}
  .lede{font-family:var(--serif);font-size:1rem;color:var(--muted);font-style:italic;line-height:1.7}
  .crumb{font-family:var(--cond);font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:.8rem}
  .crumb a{text-decoration:none;color:var(--sky-d)}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.7rem;margin:.4rem 0 1.2rem}
  .card{display:block;background:#fff;border:1px solid var(--border);border-radius:12px;padding:.95rem 1rem;text-decoration:none;color:inherit;transition:transform .12s,box-shadow .12s;position:relative}
  .card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(0,0,0,.09)}
  .card .num{font-family:var(--cond);font-size:.75rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--sage-d)}
  .card .t{font-family:var(--serif);font-weight:700;font-size:.98rem;line-height:1.35;margin:.15rem 0 .2rem}
  .card .s{font-size:.82rem;color:var(--muted)}
  .card.done::after{content:"✓";position:absolute;top:.7rem;right:.8rem;background:var(--yellow);color:var(--charcoal);font-weight:700;font-size:.75rem;width:1.3rem;height:1.3rem;border-radius:50%;display:flex;align-items:center;justify-content:center}
  .card.path{border-left:5px solid var(--red)}
  .card.big{padding:1.2rem 1.1rem;background:var(--charcoal);color:#fff;border:0}
  .card.big .num{color:var(--yellow)} .card.big .s{color:rgba(255,255,255,.7)}
  .tiles{display:grid;grid-template-columns:repeat(3,1fr);gap:.7rem}
  @media (max-width:560px){.tiles{grid-template-columns:1fr}}
  .panel{background:#fff;border:1px solid var(--border);border-radius:14px;padding:1.2rem 1.15rem;margin-bottom:1rem}
  .passage{margin:0 0 1rem}
  .passage .ref{font-family:var(--cond);font-size:.82rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--sky-d);margin-bottom:.1rem}
  .passage .ref a{text-decoration:none} .passage .ref a:hover{color:var(--red)}
  .passage .txt{font-family:var(--serif);font-size:1rem;line-height:1.8;margin:0;padding-left:.9rem;border-left:3px solid var(--stone)}
  sup{font-family:var(--body);font-size:.6em;color:var(--sage-d);margin-right:.15em;font-weight:700}
  .where{font-family:var(--cond);font-size:1rem;font-weight:700;letter-spacing:.05em;color:var(--sky-d);margin:0 0 .7rem}
  .lesson{background:#fffbe6;border-left:4px solid var(--yellow);padding:.7rem .9rem;font-size:.92rem;border-radius:0 8px 8px 0;margin:.4rem 0 .9rem}
  .question{background:var(--charcoal);color:#fff;border-radius:12px;padding:1rem 1.1rem;margin:.4rem 0 1rem}
  .question .eyebrow{color:var(--yellow)} .question p{font-family:var(--serif);font-size:1rem;margin:0;line-height:1.6}
  .nav{display:flex;gap:.6rem;justify-content:space-between;align-items:stretch;margin-top:1rem}
  .btn{font-family:var(--cond);font-size:.95rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:.75rem 1.1rem;border-radius:8px;border:0;background:var(--yellow);color:var(--charcoal);text-decoration:none;cursor:pointer;display:inline-flex;align-items:center;gap:.4rem;line-height:1.1}
  .btn.ghost{background:#fff;border:1.5px solid var(--border);color:var(--charcoal)}
  .btn.ghost:hover{border-color:var(--charcoal)}
  .btn small{display:block;font-family:var(--body);font-weight:400;letter-spacing:0;text-transform:none;font-size:.75rem;color:var(--muted);margin-top:.15rem}
  .btn.next{flex:1;justify-content:space-between;text-align:left;flex-direction:column;align-items:flex-start;gap:.1rem}
  .btn.next .lbl{display:flex;align-items:center;gap:.4rem}
  .prog{height:6px;background:#fff;border-radius:3px;overflow:hidden;margin:.4rem 0 1rem;border:1px solid var(--border)}
  .prog i{display:block;height:100%;background:var(--red);transition:width .3s}
  .steps{list-style:none;margin:.6rem 0 1rem}
  .steps li{display:flex;gap:.7rem;align-items:baseline;padding:.45rem 0;border-bottom:1px dashed var(--border);font-size:.92rem}
  .steps li b{font-family:var(--cond);color:var(--sage-d);font-size:.85rem;letter-spacing:.1em;min-width:1.6rem}
  .steps li a{text-decoration:none}
  .dots{display:flex;gap:.35rem;flex-wrap:wrap;margin:.2rem 0 .9rem}
  .dots a{width:.6rem;height:.6rem;border-radius:50%;background:#fff;border:1.5px solid var(--sage);display:block}
  .dots a.on{background:var(--red);border-color:var(--red)}
  .search{width:100%;font:inherit;font-size:1.05rem;padding:.85rem 1rem;border:1.5px solid var(--border);border-radius:10px;background:#fff;outline:none}
  .search:focus{border-color:var(--charcoal)}
  .chips{display:flex;gap:.4rem;flex-wrap:wrap;margin:.7rem 0 1rem}
  .chip{font-family:var(--cond);font-size:.85rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:.3rem .7rem;border-radius:20px;background:#fff;border:1.5px solid var(--border);text-decoration:none;cursor:pointer}
  .chip:hover,.chip.on{background:var(--charcoal);color:#fff;border-color:var(--charcoal)}
  .cv{background:#fff;border:1px solid var(--border);border-radius:10px;padding:.7rem .9rem;margin-bottom:.5rem;font-size:.92rem;line-height:1.6}
  .cv .cref{font-family:var(--cond);font-weight:700;color:var(--sky-d);letter-spacing:.05em;text-decoration:none;margin-right:.4rem}
  mark{background:#fff1a8;color:inherit;padding:0 .1em;border-radius:2px}
  .count{font-size:.85rem;color:var(--muted);margin:.2rem 0 .8rem}
  .kbd{font-size:.78rem;color:var(--muted);text-align:center;margin-top:1.2rem}
  .kbd b{display:inline-block;border:1px solid var(--border);border-radius:4px;padding:0 .35rem;background:#fff;font-weight:600}
  .foot{font-size:.75rem;color:var(--muted);margin-top:2.5rem;border-top:1px solid var(--border);padding-top:.8rem}
</style>
__GATE__
</head>
<body>
<div class="bar">
  <a class="home" href="#/"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>Anger in Scripture</a>
  <a class="lnk" href="#/search">Find a verse</a>
  <a class="lnk" href="/anger-scripture">Full document</a>
</div>
<div class="wrap" id="app"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
(function(){
  var D=JSON.parse(document.getElementById('data').textContent);
  var app=document.getElementById('app');
  var READ_KEY='lim_anger_read';
  function readSet(){try{return JSON.parse(localStorage.getItem(READ_KEY)||'[]')}catch(e){return[]}}
  function markRead(n){var s=readSet();if(s.indexOf(n)<0){s.push(n);try{localStorage.setItem(READ_KEY,JSON.stringify(s))}catch(e){}}}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function passage(p){return '<div class="passage"><div class="ref"><a href="'+p.link+'" target="_blank" rel="noopener">'+esc(p.label)+'</a></div><p class="txt">'+p.verses.map(function(v){return '<sup>'+v[0]+'</sup>'+esc(v[1])}).join(' ')+'</p></div>'}
  function storyCard(s){return '<a class="card'+(readSet().indexOf(s.n)>=0?' done':'')+'" href="#/story/'+s.n+'"><span class="num">Story '+s.n+'</span><div class="t">'+esc(s.title)+'</div><div class="s">'+esc(s.where)+'</div></a>'}
  function themeCard(t){return '<a class="card" href="#/theme/'+t.n+'"><span class="num">Theme '+t.n+'</span><div class="t">'+esc(t.title)+'</div><div class="s">'+t.passages.length+' passages</div></a>'}
  function pathCard(p){return '<a class="card path" href="#/path/'+p.id+'"><div class="t">'+esc(p.title)+'</div><div class="s">'+p.stops.length+' stops</div></a>'}
  function stopTitle(st){if(st.kind==='story')return 'Story: '+D.stories[st.n-1].title;if(st.kind==='theme')return 'Theme: '+D.themes[st.n-1].title;return st.p.label}
  var prevNext=null; // for arrow keys

  function home(){
    var r=readSet().length;
    return '<div class="screen"><span class="eyebrow">Christ-Centered Anger Management · ESV</span><h1>Where do you want to start?</h1>'
      +'<p class="lede">Pick the question closest to you and walk a short path through what the Bible says — or browse the stories and themes on your own.</p>'
      +'<div class="cards">'+D.paths.map(pathCard).join('')+'</div>'
      +'<h2>Or explore on your own</h2><div class="tiles">'
      +'<a class="card big" href="#/stories"><span class="num">'+D.stories.length+' stories</span><div class="t">Where anger drives the plot</div><div class="s">'+(r?r+' read so far':'Cain to Ephesus, one at a time')+'</div></a>'
      +'<a class="card big" href="#/themes"><span class="num">'+D.themes.length+' themes</span><div class="t">The teaching passages</div><div class="s">God\'s anger, ours, Jesus, forgiveness</div></a>'
      +'<a class="card big" href="#/search"><span class="num">'+D.conc.length+' verses</span><div class="t">Find a verse</div><div class="s">Every ESV verse that speaks of anger</div></a>'
      +'</div><p class="foot">Scripture quotations are from The ESV® Bible (The Holy Bible, English Standard Version®), © 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved. Working draft for LIM staff — not for distribution.</p></div>';
  }
  function stories(){return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › Stories</div><h1>Stories where anger drives the plot</h1><p class="lede">In Bible order. Each one: what happened, the verses that carry it, what it shows, and a question to sit with.</p><div class="cards">'+D.stories.map(storyCard).join('')+'</div></div>'}
  function themes(){return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › Themes</div><h1>The teaching passages</h1><p class="lede">Nine themes, each one a session\'s worth of Scripture.</p><div class="cards">'+D.themes.map(themeCard).join('')+'</div></div>'}
  function storyBody(s){
    return '<span class="eyebrow">Story '+s.n+' of '+D.stories.length+'</span><h1>'+esc(s.title)+'</h1><p class="where">'+esc(s.where)+'</p><p>'+esc(s.summary)+'</p>'
      +s.passages.map(passage).join('')
      +'<div class="lesson"><b>What it shows.</b> '+esc(s.lesson)+'</div>'
      +'<div class="question"><span class="eyebrow">To sit with</span><p>'+esc(s.question)+'</p></div>';
  }
  function story(n){
    var s=D.stories[n-1]; if(!s)return home(); markRead(n);
    var p=D.stories[n-2],nx=D.stories[n];
    prevNext=[p?'#/story/'+p.n:null,nx?'#/story/'+nx.n:null];
    return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › <a href="#/stories">Stories</a></div><div class="panel">'+storyBody(s)+'</div>'
      +'<div class="nav">'+(p?'<a class="btn ghost" href="#/story/'+p.n+'">‹ Prev</a>':'<a class="btn ghost" href="#/stories">‹ All stories</a>')
      +(nx?'<a class="btn next" href="#/story/'+nx.n+'"><span class="lbl">Next story ›</span><small>'+esc(nx.title)+'</small></a>':'<a class="btn next" href="#/"><span class="lbl">Finished ›</span><small>Back to the start</small></a>')+'</div>'
      +'<p class="kbd">Use <b>←</b> <b>→</b> to move between stories</p></div>';
  }
  function themeBody(t,i,inPath){
    var m=t.passages.length; i=Math.min(Math.max(i||0,0),m-1);
    var dots='<div class="dots">'+t.passages.map(function(_,k){return '<a href="#/theme/'+t.n+'/'+(k+1)+'" class="'+(k===i?'on':'')+'" title="'+esc(t.passages[k].label)+'"></a>'}).join('')+'</div>';
    if(inPath) return '<span class="eyebrow">Theme '+t.n+'</span><h1>'+esc(t.title)+'</h1><p class="lede">'+esc(t.intro)+'</p>'+t.passages.map(passage).join('');
    return '<span class="eyebrow">Theme '+t.n+' of '+D.themes.length+' · passage '+(i+1)+' of '+m+'</span><h1>'+esc(t.title)+'</h1><p class="lede">'+esc(t.intro)+'</p>'+dots+passage(t.passages[i]);
  }
  function theme(n,i){
    var t=D.themes[n-1]; if(!t)return home(); i=(parseInt(i,10)||1)-1; var m=t.passages.length;
    var prev=i>0?'#/theme/'+n+'/'+i:(D.themes[n-2]?'#/theme/'+(n-1)+'/'+D.themes[n-2].passages.length:null);
    var next=i<m-1?'#/theme/'+n+'/'+(i+2):(D.themes[n]?'#/theme/'+(n+1)+'/1':null);
    prevNext=[prev,next];
    var nl=i<m-1?'Next passage ›':(D.themes[n]?'Next theme ›':'Finished ›');
    var ns=i<m-1?t.passages[i+1].label:(D.themes[n]?D.themes[n].title:'Back to the start');
    return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › <a href="#/themes">Themes</a></div><div class="panel">'+themeBody(t,i)+'</div>'
      +'<div class="nav">'+(prev?'<a class="btn ghost" href="'+prev+'">‹ Prev</a>':'<a class="btn ghost" href="#/themes">‹ All themes</a>')
      +'<a class="btn next" href="'+(next||'#/')+'"><span class="lbl">'+nl+'</span><small>'+esc(ns)+'</small></a></div>'
      +'<p class="kbd">Use <b>←</b> <b>→</b> to move through the passages · <a href="/anger-scripture#t'+n+'">read this theme as one page</a></p></div>';
  }
  function path(id,step){
    var p=null;D.paths.forEach(function(x){if(x.id===id)p=x});if(!p)return home();
    if(!step){prevNext=null;
      return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › Path</div><span class="eyebrow">A path · '+p.stops.length+' stops</span><h1>'+esc(p.title)+'</h1><p class="lede">'+esc(p.intro)+'</p>'
        +'<ol class="steps">'+p.stops.map(function(st,k){return '<li><b>'+(k+1)+'</b><a href="#/path/'+id+'/'+(k+1)+'">'+esc(stopTitle(st))+'</a></li>'}).join('')+'</ol>'
        +'<div class="nav"><a class="btn ghost" href="#/">‹ Back</a><a class="btn next" href="#/path/'+id+'/1"><span class="lbl">Begin ›</span><small>'+esc(stopTitle(p.stops[0]))+'</small></a></div></div>';}
    var k=Math.min(Math.max(parseInt(step,10)||1,1),p.stops.length),st=p.stops[k-1],body='';
    if(st.kind==='story'){markRead(st.n);body=storyBody(D.stories[st.n-1]);}
    else if(st.kind==='theme'){body=themeBody(D.themes[st.n-1],0,true);}
    else{body='<span class="eyebrow">Passage</span><h1>'+esc(st.p.label)+'</h1>'+passage(st.p);}
    var prev=k>1?'#/path/'+id+'/'+(k-1):'#/path/'+id, next=k<p.stops.length?'#/path/'+id+'/'+(k+1):null;
    prevNext=[prev,next];
    var others=D.paths.filter(function(x){return x.id!==id}).slice(0,3);
    return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › <a href="#/path/'+id+'">'+esc(p.title)+'</a></div>'
      +'<span class="eyebrow">Stop '+k+' of '+p.stops.length+'</span><div class="prog"><i style="width:'+Math.round(k/p.stops.length*100)+'%"></i></div>'
      +'<div class="panel">'+body+'</div>'
      +'<div class="nav"><a class="btn ghost" href="'+prev+'">‹ Prev</a>'
      +(next?'<a class="btn next" href="'+next+'"><span class="lbl">Next stop ›</span><small>'+esc(stopTitle(p.stops[k]))+'</small></a>':'<a class="btn next" href="#/"><span class="lbl">End of path ›</span><small>Back to the start</small></a>')+'</div>'
      +(next?'':'<h2>Another path</h2><div class="cards">'+others.map(pathCard).join('')+'</div>')
      +'<p class="kbd">Use <b>←</b> <b>→</b> to move along the path</p></div>';
  }
  var CHIPS=['anger','angry','wrath','rage','fury','indignation','provoke','slow to anger'];
  function searchScreen(q){
    prevNext=null; q=(q||'').trim();
    var res=[],rx=null;
    if(q){var qq=q.toLowerCase();rx=new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');
      res=D.conc.filter(function(v){return v.t.toLowerCase().indexOf(qq)>=0||(v.b+' '+v.c+':'+v.v).toLowerCase().indexOf(qq)===0||v.b.toLowerCase()===qq})}
    var list=q?(res.length?res.slice(0,150).map(function(v){var t=esc(v.t);if(rx)t=t.replace(rx,'<mark>$1</mark>');return '<div class="cv"><a class="cref" target="_blank" rel="noopener" href="https://www.esv.org/'+encodeURIComponent((v.b==='Psalms'?'Psalm':v.b)+' '+v.c+':'+v.v)+'/">'+esc(v.b==='Psalms'?'Psalm':v.b)+' '+v.c+':'+v.v+'</a>'+t+'</div>'}).join('')+(res.length>150?'<p class="count">Showing 150 of '+res.length+' — narrow the search.</p>':''):'<p class="count">Nothing matches that. Try a word like <i>wrath</i> or a book like <i>Proverbs</i>.</p>'):'';
    return '<div class="screen"><div class="crumb"><a href="#/">Start</a> › Find a verse</div><h1>Find a verse</h1><p class="lede">Every verse in the ESV that speaks of anger — '+D.conc.length+' of them. Type a word, a phrase, or a book name.</p>'
      +'<input class="search" id="q" type="search" placeholder="e.g. slow to anger · Proverbs · sun go down" value="'+esc(q)+'" autocomplete="off">'
      +'<div class="chips">'+CHIPS.map(function(c){return '<a class="chip'+(c===q?' on':'')+'" href="#/search/'+encodeURIComponent(c)+'">'+c+'</a>'}).join('')+'</div>'
      +(q?'<p class="count">'+res.length+' verse'+(res.length===1?'':'s')+'</p>':'')+list+'</div>';
  }
  function route(){
    var h=location.hash.replace(/^#\/?/,''),parts=h.split('/').map(decodeURIComponent),v=parts[0]||'';
    var out;
    if(v==='')out=home();
    else if(v==='stories')out=stories();
    else if(v==='story')out=story(parseInt(parts[1],10));
    else if(v==='themes')out=themes();
    else if(v==='theme')out=theme(parseInt(parts[1],10),parts[2]);
    else if(v==='path')out=path(parts[1],parts[2]);
    else if(v==='search')out=searchScreen(parts.slice(1).join('/'));
    else out=home();
    app.innerHTML=out; window.scrollTo(0,0);
    var q=document.getElementById('q');
    if(q){var t;q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){history.replaceState(null,'','#/search/'+encodeURIComponent(q.value));var pos=q.selectionStart;route();var q2=document.getElementById('q');q2.focus();q2.setSelectionRange(pos,pos);},250)});if(!q.value)q.focus();}
  }
  document.addEventListener('keydown',function(e){if(!prevNext||e.target.tagName==='INPUT')return;if(e.key==='ArrowLeft'&&prevNext[0])location.hash=prevNext[0];if(e.key==='ArrowRight'&&prevNext[1])location.hash=prevNext[1];});
  window.addEventListener('hashchange',route); route();
})();
</script>
</body>
</html>'''
page=page.replace("__GATE__",gate).replace("__DATA__",data)
open(OUT,"w").write(page); print("wrote",OUT,len(page)//1024,"KB")
