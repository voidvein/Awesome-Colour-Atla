// Exercise the actual gradient page script, including CSS/HEX clipboard output.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/gradients.html'),'utf8');
const script=fs.readFileSync(path.join(root,'dist/gradients.js'),'utf8');
const common=fs.readFileSync(path.join(root,'dist/i18n.js'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(root,'dist/gradients.json'),'utf8'));
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function boot(responses,stored={},clipboardAllowed=true){
 const elements={},events={},storage={...stored},clipboard=[],requests=[];let selected='';
 function element(){return {dataset:{},innerHTML:'',textContent:'',hidden:false,value:'',attrs:{},classList:{add(){},remove(){}},setAttribute(k,v){this.attrs[k]=v},addEventListener(k,fn){this[k]=fn},focus(){},select(){selected=this.value},remove(){},showModal(){this.open=true},close(){this.open=false}}}
 for(const match of html.matchAll(/\bid="([^"]+)"/g))elements['#'+match[1]]=element();
 const meta=element();
 const localized=[...html.matchAll(/<[^>]+\bdata-gradient-(?:copy|aria|placeholder)="[^"]+"[^>]*>/g)].map(match=>{
  const id=match[0].match(/\bid="([^"]+)"/),node=id?elements['#'+id[1]]:element();
  for(const attr of match[0].matchAll(/data-(gradient-(?:copy|aria|placeholder))="([^"]+)"/g))node.dataset[attr[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=attr[2];
  return node;
 });
 const context={console,window:{},navigator:{language:'zh-CN',clipboard:{writeText:async value=>{if(!clipboardAllowed)throw Error('denied');clipboard.push(value)}}},setTimeout:()=>1,clearTimeout(){},
  localStorage:{getItem:key=>storage[key]||null,setItem:(key,value)=>storage[key]=value},
  fetch:async url=>{requests.push(url);const response=responses.shift();if(response instanceof Error)throw response;return {ok:true,json:async()=>response}},
  document:{documentElement:{lang:'en'},activeElement:{tagName:'BODY'},body:{append(){}},createElement:element,execCommand:()=>{clipboard.push(selected);return true},addEventListener:(key,fn)=>events[key]=fn,
   querySelector:selector=>{if(selector==='meta[name="description"]')return meta;assert(selector in elements,'Unexpected selector '+selector);return elements[selector]},
   querySelectorAll:selector=>{const match=selector.match(/^\[data-(gradient-(?:copy|aria|placeholder))\]$/);if(!match)return [];const key=match[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase());return localized.filter(node=>node.dataset[key])}
  }
 };
 vm.createContext(context);vm.runInContext(common,context);vm.runInContext(script,context);await flush();
 return {elements,context,storage,clipboard,requests,click:dataset=>events.click({target:{closest:()=>({dataset})}}),search:value=>elements['#gradient-search'].input({target:{value}}),angle:value=>elements['#gradient-angle'].input({target:{value}}),language:value=>elements['#language-select'].change({target:{value}})};
}
const count=ui=>(ui.elements['#gradient-grid'].innerHTML.match(/<article class="gradient-card">/g)||[]).length;
(async()=>{
 assert.equal(data.length,36);assert.equal(new Set(data.map(g=>g.id)).size,36);
 assert(fs.readFileSync(path.join(root,'dist/index.html'),'utf8').includes('href="gradients.html"'));
 const ui=await boot([data],{'colour-atlas-likes-v1':'{"existing-paper":true}'}),e=ui.elements;
 assert.equal(ui.context.document.documentElement.lang,'en');assert.equal(ui.context.document.title,'Colour Atlas');assert.equal(count(ui),36);assert.equal(e['#gradient-grid'].attrs['aria-busy'],'false');
 assert.deepEqual(ui.requests,['gradients.json?v=1'],'The independent page should not load the paper catalogue');
 const copy=vm.runInContext('GRADIENT_COPY',ui.context);assert.deepEqual(Object.keys(copy.en).sort(),Object.keys(copy['zh-CN']).sort());
 assert(e['#gradient-grid'].innerHTML.includes('linear-gradient(135deg, #9BADD0 0%, #E8A3B7 100%)'));
 ui.click({gradientCss:'morning-atlas'});await flush();assert.equal(ui.clipboard.at(-1),'background: linear-gradient(135deg, #9BADD0 0%, #E8A3B7 100%);');
 ui.click({gradientColour:'#9BADD0'});await flush();assert.equal(ui.clipboard.at(-1),'#9BADD0');
 ui.click({gradientColours:'saffron-draft'});await flush();assert.equal(ui.clipboard.at(-1),'#F1B45D, #E2A0A3, #9486BC');
 ui.angle('90');assert.equal(e['#gradient-angle-output'].textContent,'90°');ui.click({gradientCss:'saffron-draft'});await flush();assert.equal(ui.clipboard.at(-1),'background: linear-gradient(90deg, #F1B45D 0%, #E2A0A3 45%, #9486BC 100%);');
 ui.click({gradientPreview:'saffron-draft'});assert(e['#gradient-detail'].open);assert(e['#gradient-detail-body'].innerHTML.includes('Saffron Draft'));assert(e['#gradient-detail-body'].innerHTML.includes(ui.clipboard.at(-1)));assert(e['#gradient-detail-body'].innerHTML.includes('45%'));
 ui.language('zh-CN');assert(e['#gradient-detail'].open);assert(e['#gradient-detail-body'].innerHTML.includes('藏红花草稿'));assert.equal(ui.storage['colour-atlas-language-v1'],'zh-CN');
 ui.angle('360');assert(e['#gradient-detail-body'].innerHTML.includes('linear-gradient(360deg,'));ui.angle('-1');assert.equal(e['#gradient-angle-output'].textContent,'360°');ui.angle('361');assert.equal(e['#gradient-angle-output'].textContent,'360°');ui.angle('NaN');assert.equal(e['#gradient-angle-output'].textContent,'360°');
 e['#close-gradient'].onclick();assert(!e['#gradient-detail'].open);e['#reset-angle'].onclick();assert.equal(e['#gradient-angle'].value,'135');
 ui.click({gradientGroup:'soft'});assert.equal(count(ui),9);ui.language('en');assert.equal(count(ui),9);assert(e['#gradient-filters'].innerHTML.includes('Soft'));
 e['#gradient-reset'].onclick();ui.search('#9badd0');assert.equal(count(ui),1);assert(e['#gradient-grid'].innerHTML.includes('Morning Atlas'));
 ui.search('薄荷手稿');assert.equal(count(ui),1);assert(e['#gradient-grid'].innerHTML.includes('Mint Manuscript'));ui.language('zh-CN');assert.equal(count(ui),1);assert(e['#gradient-grid'].innerHTML.includes('薄荷手稿'));assert.equal(e['#gradient-angle-output'].textContent,'135°');
 ui.search('does-not-exist');assert.equal(count(ui),0);assert(!e['#gradient-empty'].hidden);e['#gradient-reset'].onclick();assert.equal(count(ui),36);
 assert.equal(ui.storage['colour-atlas-likes-v1'],'{"existing-paper":true}','Gradient actions must preserve existing paper likes');
 const persisted=await boot([data],ui.storage);assert.equal(persisted.context.document.documentElement.lang,'zh-CN');assert(persisted.elements['#gradient-grid'].innerHTML.includes('晨光图谱'));
 const fallback=await boot([data],{},false);fallback.click({gradientCss:'morning-atlas'});await flush();assert.equal(fallback.clipboard.at(-1),'background: linear-gradient(135deg, #9BADD0 0%, #E8A3B7 100%);');
 const retry=await boot([Error('offline'),data]);assert(!retry.elements['#gradient-error'].hidden);retry.language('zh-CN');assert.equal(retry.elements['#gradient-results'].textContent,'暂时无法加载渐变色卡');await retry.elements['#gradient-retry'].onclick();assert.equal(count(retry),36);assert(retry.elements['#gradient-error'].hidden);
 const wrongOrder=structuredClone(data);wrongOrder[0].stops[1].position=0;const invalid=await boot([wrongOrder]);assert(!invalid.elements['#gradient-error'].hidden);
 const badHex=structuredClone(data);badHex[0].stops[0].color='red';assert(!(await boot([badHex])).elements['#gradient-error'].hidden);
 for(const g of data){ui.click({gradientPreview:g.id});assert(e['#gradient-detail-body'].innerHTML.includes(g.name['zh-CN']));for(const stop of g.stops)assert(e['#gradient-detail-body'].innerHTML.includes(stop.color));e['#close-gradient'].onclick()}
 console.log('PASS: 36 gradients; exact HEX/CSS output and stop positions; angle changes; preview dialog; bilingual search/preferences; filter state; clipboard fallback; retry/invalid-data states; paper likes preserved.');
})().catch(error=>{console.error(error);process.exitCode=1});
