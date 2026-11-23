// Runs the actual browser script with a small DOM adapter; no duplicate filter/sort implementation.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
const script=fs.readFileSync(path.join(root,'dist/app.js'),'utf8');
const i18nScript=fs.readFileSync(path.join(root,'dist/i18n.js'),'utf8');
const english=JSON.parse(fs.readFileSync(path.join(root,'dist/content-en.json'),'utf8'));
const chineseContent=JSON.parse(fs.readFileSync(path.join(root,'dist/content-zh.json'),'utf8'));
const release=JSON.parse(fs.readFileSync(path.join(root,'dist/palettes.json'),'utf8'));
const seed=release[0];
const data=Array.from({length:500},(_,i)=>({...seed,id:`p${i}`,order:i,name:`Model ${i}`,title:`Paper ${i}`,domain:i%2?'领域甲':'领域乙',tags:[i%2?'领域甲':'领域乙',i===499?'rare-tag':'common-tag'],image:`assets/original-${i}.png`,thumbnail:`assets/thumb-${i}.webp`}));
const flush=()=>new Promise(resolve=>setImmediate(resolve));

async function boot(responses,stored={}){
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 const events={},elements={},storage={...stored},exports=[];
 function element(){return {innerHTML:'',textContent:'',hidden:false,disabled:false,value:'',attrs:{},classList:{add(){},remove(){}},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,v){this[k]=v},focus(){},scrollIntoView(){},showModal(){this.open=true},close(){this.open=false}}}
 ids.forEach(id=>elements['#'+id]=element());elements.meta=element();
 const localized=[...html.matchAll(/<[^>]+\bdata-i18n(?:-[a-z]+)?="[^"]+"[^>]*>/g)].map(m=>{
  const id=m[0].match(/\bid="([^"]+)"/);const node=id?elements['#'+id[1]]:element();node.dataset={};
  for(const attr of m[0].matchAll(/data-(i18n(?:-[a-z]+)?)="([^"]+)"/g))node.dataset[attr[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=attr[2];
  return node;
 });
 const context={console,Blob,setTimeout:()=>1,clearTimeout(){},window:{},CSS:{escape:s=>s},navigator:{language:'zh-CN',clipboard:{writeText:async()=>{}}},
  localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>{storage[k]=v}},
  URL:{createObjectURL:b=>{exports.push(b);return 'blob:test'},revokeObjectURL(){}},
  fetch:async url=>{url=url.split('?')[0];if(url==='content-en.json')return {ok:true,json:async()=>english};if(url==='content-zh.json')return {ok:true,json:async()=>chineseContent};const response=responses.shift();if(response instanceof Error)throw response;return {ok:true,json:async()=>response}},
  document:{documentElement:{lang:'en'},activeElement:{tagName:'BODY'},body:{append(){}},createElement:()=>({...element(),click(){},select(){},remove(){}}),addEventListener:(k,v)=>{events[k]=v},querySelectorAll:selector=>{
   const attr=selector.match(/^\[data-(i18n(?:-[a-z]+)?)\]$/);if(!attr)return [];
   const key=attr[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase());return localized.filter(node=>node.dataset[key]);
  },querySelector:s=>{
   if(s==='meta[name="description"]')return elements.meta;
   if(s==='dialog[open]')return Object.values(elements).find(e=>e.open)||null;
   if(s.startsWith('[data-like='))return {focus(){}};
   assert(s in elements,`Unmatched UI selector: ${s}`);return elements[s];
  }}
 };
 vm.createContext(context);vm.runInContext(i18nScript,context);vm.runInContext(script,context);await flush();
 return {elements,storage,exports,context,click:dataset=>events.click({target:{closest:()=>({dataset})}}),search:value=>elements['#search'].input({target:{value}}),language:value=>elements['#language-select'].change({target:{value}})};
}
const cardCount=x=>(x.elements['#cards'].innerHTML.match(/<article class="card">/g)||[]).length;
const visibleCopy=markup=>markup.replace(/<[^>]*>/g,' ')+[...markup.matchAll(/(?:aria-label|alt|title)="([^"]*)"/g)].map(m=>m[1]).join(' ');

(async()=>{
 const ui=await boot([data]);const e=ui.elements;
 assert.equal(ui.context.document.documentElement.lang,'en','English is the default even for a Chinese browser');
 assert.equal(e['#language-select'].value,'en');assert(e['#results'].textContent.includes('palettes'));
 const copy=vm.runInContext('ATLAS_I18N',ui.context);assert.deepEqual(Object.keys(copy.en).sort(),Object.keys(copy['zh-CN']).sort());
 assert.equal(e['#paper-count'].textContent,'500');assert.equal(e['#domain-count'].textContent,'2');
 assert.equal(e['#colour-count'].textContent,(500*seed.colors.length).toLocaleString());
 assert.equal(cardCount(ui),24);assert(!e['#pagination'].hidden);
 assert(e['#cards'].innerHTML.includes('assets/thumb-0.webp'));assert(!e['#cards'].innerHTML.includes('assets/original-0.png'));
 e['#load-more'].onclick();assert.equal(cardCount(ui),48);
 ui.language('zh-CN');assert.equal(cardCount(ui),48,'Language changes preserve the loaded page size');ui.language('en');
 ui.click({filter:'领域甲'});assert.equal(cardCount(ui),24);assert(e['#results'].textContent.includes('250'));
 ui.search('Paper 499');assert.equal(cardCount(ui),1);assert(e['#cards'].innerHTML.includes('Model 499'));
 ui.click({detail:'p499'});assert(e['#detail'].open);assert(e['#detail-body'].innerHTML.includes('assets/original-499.png'));assert(!e['#detail-body'].innerHTML.includes('assets/thumb-499.webp'));
 ui.click({like:'p499'});assert.equal(JSON.parse(ui.storage['colour-atlas-likes-v1']).p499,true);
 e['#reset'].onclick();assert.equal(cardCount(ui),24);assert(e['#cards'].innerHTML.indexOf('data-detail="p499"')<e['#cards'].innerHTML.indexOf('data-detail="p0"'));
 e['#liked-filter'].onclick();assert.equal(cardCount(ui),1);
 ui.click({like:'p499'});assert.equal(cardCount(ui),0);assert(!e['#empty'].hidden);assert.equal(JSON.parse(ui.storage['colour-atlas-likes-v1']).p499,false);
 e['#reset'].onclick();for(let i=0;i<20;i++)e['#load-more'].onclick();assert.equal(cardCount(ui),500);assert(e['#pagination'].hidden);
 ui.search('rare-tag');assert.equal(cardCount(ui),1);
 e['#download-all'].onclick();const exported=JSON.parse(await ui.exports[0].text());assert.equal(exported.length,500);assert(!('searchText' in exported[0]));assert(!('sourceOrder' in exported[0]));
 ui.search('no-such-paper');assert.equal(cardCount(ui),0);assert(!e['#empty'].hidden);assert(e['#pagination'].hidden);
 const restored=await boot([data],{'colour-atlas-likes-v1':JSON.stringify({p499:true})});assert(restored.elements['#cards'].innerHTML.indexOf('data-detail="p499"')<restored.elements['#cards'].innerHTML.indexOf('data-detail="p0"'));
 const retry=await boot([Error('offline'),data]);assert(!retry.elements['#load-error'].hidden);assert.equal(retry.elements['#cards'].attrs['aria-busy'],'false');retry.language('zh-CN');assert.equal(retry.elements['#results'].textContent,'暂时无法加载色卡');await retry.elements['#retry-load'].onclick();assert(retry.elements['#load-error'].hidden);assert.equal(cardCount(retry),24);
 const empty=await boot([[]]);assert.equal(empty.elements['#paper-count'].textContent,'0');assert(empty.elements['#download-all'].disabled);assert(!empty.elements['#empty'].hidden);
 const twoColours=await boot([[{...seed,id:'two-colour-model',colors:['#97CBD9','#EF8E77']}]]);assert.equal(cardCount(twoColours),1);assert(twoColours.elements['#load-error'].hidden);assert.equal(twoColours.elements['#colour-count'].textContent,'2');
 const invalid=await boot([[{...data[0],colors:['not-a-colour']}]]);assert(!invalid.elements['#load-error'].hidden);
 retry.language('zh-CN');assert.equal(retry.context.document.documentElement.lang,'zh-CN');
 const badLanguage=await boot([data],{'colour-atlas-language-v1':'fr'});assert.equal(badLanguage.context.document.documentElement.lang,'en');
 const chinese=await boot([data],{'colour-atlas-language-v1':'zh-CN'});assert.equal(chinese.elements['#language-select'].value,'zh-CN');assert(chinese.elements['#results'].textContent.includes('共'));
 console.log('PASS: actual app.js with 500 records; dynamic counters, 24-card batches, full-data search/tags, local vote persistence/order, original-image details, complete export, empty/error/retry states.');
 if(process.argv.includes('--require-release'))assert.equal(release.length,500,'The real released collection must contain 500 papers');
 if(release.length===500){
  const real=await boot([release]);assert.equal(cardCount(real),24);assert.equal(real.elements['#paper-count'].textContent,'500');
  const han=/[\u4e00-\u9fff]/;assert(!han.test(visibleCopy(real.elements['#cards'].innerHTML)),'English cards must not contain untranslated Chinese');
  assert.equal(real.elements['#domain-count'].textContent,new Set(release.map(p=>p.domain)).size.toLocaleString());
  for(const p of release){
   real.search(p.title);assert(real.elements['#cards'].innerHTML.includes(`data-detail="${p.id}"`),`Real article missing from search: ${p.id}`);
   real.click({detail:p.id});assert(real.elements['#detail-body'].innerHTML.includes(p.image),`Real article detail missing: ${p.id}`);
   assert(!han.test(visibleCopy(real.elements['#detail-body'].innerHTML)),`Untranslated English detail: ${p.id}`);
   real.elements['#close-detail'].onclick();
  }
  const last=release[499];real.click({like:last.id});real.elements['#reset'].onclick();
  assert(real.elements['#cards'].innerHTML.indexOf(`data-detail="${last.id}"`)<real.elements['#cards'].innerHTML.indexOf(`data-detail="${release[0].id}"`));
  real.elements['#download-all'].onclick();const out=JSON.parse(await real.exports[0].text());
  assert.deepEqual(out.map(p=>p.id),release.map(p=>p.id));assert.deepEqual(out.map(p=>p.colors),release.map(p=>p.colors));
  const target=release.find(p=>p.domain==='语义分割');assert(target);real.search(target.title);real.click({detail:target.id});
  const englishDetail=real.elements['#detail-body'].innerHTML;assert(englishDetail.includes('Colour notes'));
  real.language('zh-CN');assert(real.elements['#detail'].open);assert(real.elements['#detail-body'].innerHTML.includes('配色观察'));assert(real.elements['#detail-body'].innerHTML.includes(target.analysis));assert(real.elements['#detail-body'].innerHTML.includes(target.image));
  assert(real.elements['#cards'].innerHTML.includes(target.id));assert.equal(cardCount(real),1,'Switching language preserves the query');
  assert.equal(real.storage['colour-atlas-language-v1'],'zh-CN');assert.equal(JSON.parse(real.storage['colour-atlas-likes-v1'])[last.id],true);
  real.language('en');assert.equal(real.elements['#detail-body'].innerHTML,englishDetail);real.elements['#close-detail'].onclick();real.elements['#reset'].onclick();
  real.language('zh-CN');
  for(const p of release.filter(p=>chineseContent.strings[p.analysis])){real.click({detail:p.id});assert(real.elements['#detail-body'].innerHTML.includes(chineseContent.strings[p.analysis]),'Chinese description not displayed: '+p.id);real.elements['#close-detail'].onclick()}
  real.language('en');
  real.click({filter:'语义分割'});const filtered=cardCount(real);real.language('zh-CN');assert.equal(cardCount(real),filtered);assert(real.elements['#filters'].innerHTML.includes('语义分割'));
  real.language('en');assert(real.elements['#filters'].innerHTML.includes('Semantic segmentation'));
  real.elements['#reset'].onclick();real.search('semantic segmentation');assert(cardCount(real)>0,'English domain search covers Chinese source metadata');
  real.search('语义分割');assert(cardCount(real)>0,'Chinese domain search still works in English');
  for(const p of release){
   for(const value of [p.title,p.domain,p.mood,p.analysis,p.usage,p.sourceLabel,p.provenance,p.note,...p.tags])if(han.test(value))assert(english.strings[value]&&!han.test(english.strings[value]),'Missing English translation: '+value);
   if(!han.test(p.analysis))assert(chineseContent.strings[p.analysis]&&han.test(chineseContent.strings[p.analysis]),'Missing Chinese colour notes: '+p.id);
  }
  const persisted=await boot([release],real.storage);assert.equal(persisted.context.document.documentElement.lang,'en');
  console.log('PASS: English default, saved language, complete 500-card English content, Chinese round-trip, open-dialog updates, bilingual search, preserved filters/likes and unchanged exports.');
  console.log('PASS: all 500 real released articles searchable, original details open, real-ID vote order works, and full colour export matches.');
 }
})().catch(error=>{console.error(error);process.exitCode=1});
