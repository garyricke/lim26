// Fairbanks healing-group Facebook/Instagram ad images (1080x1350, details printed on the photo).
// Once Roberta sets dates:   node tools-ad-creatives/fairbanks.js "Wed–Fri · Nov 4–6"
// Output: assets/ads-fairbanks/ (not committed — upload those JPGs to Meta).
const { chromium } = require('/Users/garyricke/Documents/lim2026/print-export/node_modules/playwright');
const fs=require('fs');
const path=require('path'); const ROOT=path.resolve(__dirname,'..'); const S=__dirname;
const OUT=ROOT+'/assets/ads-fairbanks'; fs.mkdirSync(OUT,{recursive:true});
const WHEN=process.argv[2]||'Dates coming soon';
const tpl=fs.readFileSync(S+'/ad-tpl.html','utf8')
  .replace('KICKER','Fairbanks, Alaska')
  .replace('WHEN',WHEN.replace(/&/g,'&amp;'))
  .replace('ROW1','<b>3 days</b> &middot; Lunch provided every day')
  .replace('ROW2','<b>Zion Lutheran Church</b> &middot; 2982 Davis Road');
const photos={embrace:[ROOT+'/images-master/people-healing-embrace.jpg','50% 12%'],
              zion:['https://res.cloudinary.com/dsbllwpbh/image/upload/q_auto/lim2026/zion-2026/sign.jpg','50% 44%']};
(async()=>{const b=await chromium.launch();
 for(const [pn,[file,pos]] of Object.entries(photos)){
  const html=tpl.replace('PHOTO',file.startsWith('http')?file:'file://'+file).replace('<html>',`<html style="--h:1350px;--ph:720px;--pos:${pos};--freetop:612px;--pt:730px;--ft:1206px">`);
  fs.writeFileSync(`${S}/.tmp.html`,html);
  const p=await b.newPage({viewport:{width:1080,height:1350}});
  await p.goto('file://'+S+'/.tmp.html');
  // wait until the photo itself has loaded (it may come from Cloudinary)
  await p.evaluate(src=>new Promise((ok,bad)=>{const i=new Image();i.onload=ok;i.onerror=()=>bad(new Error('photo failed: '+src));i.src=src;}), file.startsWith('http')?file:'file://'+file);
  await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
  const png=`${OUT}/fairbanks-${pn}-feed-4x5.png`; await p.screenshot({path:png}); await p.close();
  require('child_process').execFileSync('sips',['-s','format','jpeg','-s','formatOptions','92',png,'--out',png.replace('.png','.jpg')]); fs.unlinkSync(png);
 }
 await b.close(); fs.unlinkSync(`${S}/.tmp.html`); console.log('Wrote',OUT);})();
