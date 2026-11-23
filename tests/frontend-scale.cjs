// Runs the actual browser script with a small DOM adapter; no duplicate filter/sort implementation.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
const script=fs.readFileSync(path.join(root,'dist/app.js'),'utf8');
const release=JSON.parse(fs.readFileSync(path.join(root,'dist/palettes.json'),'utf8'));
const seed=release[0];
const data=Array.from({length:500},(_,i)=>({...seed,id:`p${i}`,order:i,name:`Model ${i}`,title:`Paper ${i}`,domain:i%2?'领域甲':'领域乙',tags:[i%2?'领域甲':'领域乙',i===499?'rare-tag':'common-tag'],image:`assets/original-${i}.png`,thumbnail:`assets/thumb-${i}.webp`}));
const flush=()=>new Promise(resolve=>setImmediate(resolve));

async function boot(responses,stored={}){
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 const events={},elements={},storage={...stored},exports=[];
 function element(){return {innerHTML:'',textContent:'',hidden:false,disabled:false,value:'',attrs:{},classList:{add(){},remove(){}},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,v){this[k]=v},focus(){},scrollIntoView(){},showModal(){this.open=true},close(){this.open=false}}}
 ids.forEach(id=>elements['#'+id]=element());elements.meta=element();
 const context={console,Blob,setTimeout:()=>1,clearTimeout(){},window:{},CSS:{escape:s=>s},navigator:{clipboard:{writeText:async()=>{}}},
  localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>{storage[k]=v}},
  URL:{createObjectURL:b=>{exports.push(b);return 'blob:test'},revokeObjectURL(){}},
  fetch:async()=>{const response=responses.shift();if(response instanceof Error)throw response;return {ok:true,json:async()=>response}},
  document:{activeElement:{tagName:'BODY'},body:{append(){}},createElement:()=>({...element(),click(){},select(){},remove(){}}),addEventListener:(k,v)=>{events[k]=v},querySelectorAll:()=>[],querySelector:s=>{
   if(s==='meta[name="description"]')return elements.meta;
   if(s==='dialog[open]')return Object.values(elements).find(e=>e.open)||null;
   if(s.startsWith('[data-like='))return {focus(){}};
   assert(s in elements,`Unmatched UI selector: ${s}`);return elements[s];
  }}
 };
 vm.createContext(context);vm.runInContext(script,context);await flush();
 return {elements,storage,exports,context,click:dataset=>events.click({target:{closest:()=>({dataset})}}),search:value=>elements['#search'].input({target:{value}})};
}
const cardCount=x=>(x.elements['#cards'].innerHTML.match(/<article class="card">/g)||[]).length;

(async()=>{
 const ui=await boot([data]);const e=ui.elements;
 assert.equal(e['#paper-count'].textContent,'500');assert.equal(e['#domain-count'].textContent,'2');
 assert.equal(e['#colour-count'].textContent,(500*seed.colors.length).toLocaleString());
 assert.equal(cardCount(ui),24);assert(!e['#pagination'].hidden);
 assert(e['#cards'].innerHTML.includes('assets/thumb-0.webp'));assert(!e['#cards'].innerHTML.includes('assets/original-0.png'));
 e['#load-more'].onclick();assert.equal(cardCount(ui),48);
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
 const retry=await boot([Error('offline'),data]);assert(!retry.elements['#load-error'].hidden);assert.equal(retry.elements['#cards'].attrs['aria-busy'],'false');await retry.elements['#retry-load'].onclick();assert(retry.elements['#load-error'].hidden);assert.equal(cardCount(retry),24);
 const empty=await boot([[]]);assert.equal(empty.elements['#paper-count'].textContent,'0');assert(empty.elements['#download-all'].disabled);assert(!empty.elements['#empty'].hidden);
 const twoColours=await boot([[{...seed,id:'two-colour-model',colors:['#97CBD9','#EF8E77']}]]);assert.equal(cardCount(twoColours),1);assert(twoColours.elements['#load-error'].hidden);assert.equal(twoColours.elements['#colour-count'].textContent,'2');
 const invalid=await boot([[{...data[0],colors:['not-a-colour']}]]);assert(!invalid.elements['#load-error'].hidden);
 console.log('PASS: actual app.js with 500 records; dynamic counters, 24-card batches, full-data search/tags, local vote persistence/order, original-image details, complete export, empty/error/retry states.');
 if(process.argv.includes('--require-release'))assert.equal(release.length,500,'The real released collection must contain 500 papers');
 if(release.length===500){
  const real=await boot([release]);assert.equal(cardCount(real),24);assert.equal(real.elements['#paper-count'].textContent,'500');
  assert.equal(real.elements['#domain-count'].textContent,new Set(release.map(p=>p.domain)).size.toLocaleString());
  for(const p of release){
   real.search(p.title);assert(real.elements['#cards'].innerHTML.includes(`data-detail="${p.id}"`),`Real article missing from search: ${p.id}`);
   real.click({detail:p.id});assert(real.elements['#detail-body'].innerHTML.includes(p.image),`Real article detail missing: ${p.id}`);
   real.elements['#close-detail'].onclick();
  }
  const last=release[499];real.click({like:last.id});real.elements['#reset'].onclick();
  assert(real.elements['#cards'].innerHTML.indexOf(`data-detail="${last.id}"`)<real.elements['#cards'].innerHTML.indexOf(`data-detail="${release[0].id}"`));
  real.elements['#download-all'].onclick();const out=JSON.parse(await real.exports[0].text());
  assert.deepEqual(out.map(p=>p.id),release.map(p=>p.id));assert.deepEqual(out.map(p=>p.colors),release.map(p=>p.colors));
  console.log('PASS: all 500 real released articles searchable, original details open, real-ID vote order works, and full colour export matches.');
 }
})().catch(error=>{console.error(error);process.exitCode=1});
