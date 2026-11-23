const PAGE_SIZE=24;
const LANGUAGE_KEY='colour-atlas-language-v1';
let language='en',englishText={},chineseText={},papers=[],selected='全部',onlyLiked=false,query='',visibleLimit=PAGE_SIZE,loading=false,loadState='initial',currentDetail=null;
try{const saved=localStorage.getItem(LANGUAGE_KEY);if(saved==='en'||saved==='zh-CN')language=saved}catch{}
let likes={};
try{likes=JSON.parse(localStorage.getItem('colour-atlas-likes-v1')||'{}');if(!likes||typeof likes!=='object'||Array.isArray(likes))likes={}}catch{}
const $=s=>document.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const t=(key,values={})=>ATLAS_I18N[language][key].replace(/\{(\w+)\}/g,(_,name)=>String(values[name]??''));
const text=value=>language==='en'?(englishText[value]||value):(chineseText[value]||value);
const number=value=>value.toLocaleString(language==='en'?'en-US':'zh-CN');
const heart='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/></svg>';
const external='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3H3v10h10v-3M9 2h5v5M14 2 7 9"/></svg>';
const swatches=p=>'<div class="swatches">'+p.colors.map(c=>'<button class="swatch" style="background:'+c+'" data-color="'+c+'" title="'+esc(t('copy',{value:c}))+'" aria-label="'+esc(t('copyColour',{value:c}))+'"><span class="hex">'+c+'</span></button>').join('')+'</div>';
function notify(value){$('#toast').textContent=value;$('#toast').classList.add('show');clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),2000)}
async function copy(value){
 try{await navigator.clipboard.writeText(value);notify(t('copied',{value}))}
 catch{const a=document.createElement('textarea');a.value=value;document.body.append(a);a.select();const ok=document.execCommand('copy');a.remove();notify(ok?t('copied',{value}):t('copyFailed'))}
}
function applyLanguage(){
 document.documentElement.lang=language;document.title=t('title');
 const attributes={i18n:'textContent',i18nHtml:'innerHTML',i18nAria:'aria-label',i18nPlaceholder:'placeholder'};
 for(const [property,target] of Object.entries(attributes)){
  const attr='data-'+property.replace(/[A-Z]/g,c=>'-'+c.toLowerCase());
  document.querySelectorAll('['+attr+']').forEach(node=>{
   const value=t(node.dataset[property]);if(target==='textContent'||target==='innerHTML')node[target]=value;else node.setAttribute(target,value);
  });
 }
 $('#language-select').value=language;
 if(loadState==='ready'){updateCounts();render()}
 else $('#results').textContent=t(loadState==='error'?'loadError':'loading');
 if(currentDetail&&$('#detail').open)detail(currentDetail);
}
function setLanguage(value){
 if(value!=='en'&&value!=='zh-CN')return;
 language=value;try{localStorage.setItem(LANGUAGE_KEY,language)}catch{}
 applyLanguage();
}
function updateCounts(){
 const domains=new Set(papers.map(p=>p.domain)).size,colours=papers.reduce((n,p)=>n+p.colors.length,0);
 $('#paper-count').textContent=number(papers.length);$('#domain-count').textContent=number(domains);$('#colour-count').textContent=number(colours);$('#total').textContent=number(papers.length);
 $('#footer-count').textContent='CVPR 2026 · '+number(papers.length)+(language==='en'?' PALETTES':' 张色卡');
 $('#about-count').textContent=t('aboutCount',{papers:number(papers.length),domains:number(domains)});
 document.querySelector('meta[name="description"]').setAttribute('content',t('description',{papers:number(papers.length),domains:number(domains)}));
}
function filters(){
 const counts=new Map();for(const p of papers)counts.set(p.domain,(counts.get(p.domain)||0)+1);
 $('#filters').innerHTML=['全部',...counts.keys()].map(d=>'<button class="filter '+(selected===d?'active':'')+'" data-filter="'+esc(d)+'" aria-pressed="'+(selected===d)+'">'+esc(d==='全部'?t('all'):text(d))+'<em>'+(d==='全部'?papers.length:counts.get(d))+'</em></button>').join('');
}
function matchingPapers(){
 const search=query.toLocaleLowerCase();
 return papers.filter(p=>(selected==='全部'||p.domain===selected||p.tags.includes(selected))&&(!onlyLiked||likes[p.id]===true)&&(!search||p.searchText.includes(search)))
  .sort((a,b)=>Number(likes[b.id]===true)-Number(likes[a.id]===true)||a.order-b.order||a.sourceOrder-b.sourceOrder);
}
function card(p){
 const name=esc(p.name);
 return '<article class="card"><button class="image-button" data-detail="'+esc(p.id)+'" aria-label="'+esc(t('viewDetail',{name:p.name}))+'"><img src="'+esc(p.thumbnail||p.image)+'" alt="'+esc(t('imageAlt',{name:p.name,figure:p.figure}))+'" loading="lazy" decoding="async"><span class="image-label">'+esc(p.figure)+' · '+t('originalFigure')+'</span><span class="zoom-hint"><span>'+t('zoom')+'</span></span></button><div class="card-content"><div class="card-meta"><span class="venue">'+esc(p.venue)+'</span><span class="palette-name">'+esc(text(p.mood))+'</span></div><h3>'+name+'</h3>'+swatches(p)+'<p class="paper-title" title="'+esc(text(p.title))+'">'+esc(text(p.title))+'</p><div class="tags">'+p.tags.slice(0,3).map(tag=>'<button class="tag" data-tag="'+esc(tag)+'">'+esc(text(tag))+'</button>').join('')+'</div><div class="card-footer"><a class="source-link" href="'+esc(p.paper)+'" target="_blank" rel="noopener">'+esc(text(p.sourceLabel))+' '+external+'</a><button class="like" data-like="'+esc(p.id)+'" aria-label="'+esc(t(likes[p.id]===true?'unlike':'like',{name:p.name}))+'" aria-pressed="'+(likes[p.id]===true)+'">'+heart+'<span>'+(likes[p.id]===true?1:0)+'</span></button></div></div></article>';
}
function render(){
 const shown=matchingPapers(),visible=shown.slice(0,visibleLimit);
 $('#cards').innerHTML=visible.map(card).join('');$('#empty').hidden=shown.length>0;$('#load-error').hidden=true;
 $('#results').textContent=t(selected==='全部'&&!query&&!onlyLiked?'total':'found',{count:number(shown.length)})+(shown.length>visible.length?t('shown',{count:number(visible.length)}):'');
 $('#reset').hidden=selected==='全部'&&!query&&!onlyLiked;$('#liked-filter').setAttribute('aria-pressed',String(onlyLiked));
 $('#pagination').hidden=shown.length<=visible.length;$('#load-more').textContent=t('moreCount',{count:Math.min(PAGE_SIZE,shown.length-visible.length)});
 $('#page-progress').textContent=t('progress',{visible:number(visible.length),total:number(shown.length)});filters();
}
function detail(id){
 const p=papers.find(x=>x.id===id);if(!p)return;currentDetail=id;
 $('#detail-body').innerHTML='<div class="detail-image"><a href="'+esc(p.image)+'" target="_blank" rel="noopener" title="'+t('fullSize')+'"><img src="'+esc(p.image)+'" alt="'+esc(t('fullAlt',{name:p.name}))+'"></a></div><div class="detail-copy"><p class="venue">'+esc(p.venue)+' · '+esc(p.figure)+'</p><h2>'+esc(p.name)+'<span>'+t('colourCount',{count:p.colors.length})+'</span></h2><p class="full-title">'+esc(text(p.title))+'</p>'+swatches(p)+'<div class="hex-list">'+p.colors.map(c=>'<span>'+c+'</span>').join(' · ')+'</div><h4>'+t('notes')+'</h4><p class="analysis">'+esc(text(p.analysis))+'</p><h4>'+t('usage')+'</h4><p class="analysis">'+esc(text(p.usage))+'</p><div class="tags">'+p.tags.map(tag=>'<span class="tag">'+esc(text(tag))+'</span>').join('')+'</div><p class="detail-caption">'+t('source')+esc(text(p.provenance))+'. '+esc(text(p.note))+' '+t('caption')+'</p><div class="detail-links"><a href="'+esc(p.paper)+'" target="_blank" rel="noopener">'+t('paper')+'</a><a href="'+esc(p.noteUrl)+'" target="_blank" rel="noopener">'+t('paperNotes')+'</a><button class="tag" data-copy-all="'+esc(p.id)+'">'+t('copyAll')+'</button></div></div>';
 if(!$('#detail').open)$('#detail').showModal();
}
function reset(){selected='全部';query='';onlyLiked=false;visibleLimit=PAGE_SIZE;$('#search').value='';render()}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.color)copy(b.dataset.color);
 if(b.dataset.detail)detail(b.dataset.detail);
 if(b.dataset.filter){selected=b.dataset.filter;visibleLimit=PAGE_SIZE;render()}
 if(b.dataset.tag){selected=b.dataset.tag;if(!papers.some(p=>p.domain===selected)){selected='全部';query=text(b.dataset.tag);$('#search').value=query}visibleLimit=PAGE_SIZE;render();$('#collection').scrollIntoView({behavior:'smooth'})}
 if(b.dataset.like){const id=b.dataset.like;if(!papers.some(p=>p.id===id))return;likes[id]=likes[id]!==true;try{localStorage.setItem('colour-atlas-likes-v1',JSON.stringify(likes))}catch{notify(t('storageFailed'))}render();document.querySelector('[data-like="'+CSS.escape(id)+'"]')?.focus({preventScroll:true})}
 if(b.dataset.copyAll){const p=papers.find(p=>p.id===b.dataset.copyAll);if(p)copy(p.colors.join(', '))}
});
$('#language-select').addEventListener('change',e=>setLanguage(e.target.value));
$('#search').addEventListener('input',e=>{query=e.target.value.trim();visibleLimit=PAGE_SIZE;render()});
$('#liked-filter').onclick=()=>{onlyLiked=!onlyLiked;visibleLimit=PAGE_SIZE;render()};
$('#load-more').onclick=()=>{visibleLimit+=PAGE_SIZE;render()};
$('#reset').onclick=reset;$('#empty-reset').onclick=reset;$('#retry-load').onclick=loadPapers;
$('#close-detail').onclick=()=>{$('#detail').close();currentDetail=null};$('#about').onclick=()=>$('#about-dialog').showModal();$('#close-about').onclick=()=>$('#about-dialog').close();
document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();$('#search').focus()}});
$('#download-all').onclick=()=>{
 if(!papers.length)return;const data=papers.map(({sourceOrder,searchText,...p})=>p),a=document.createElement('a');
 a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='colour-atlas-cvpr2026.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);notify(t('exported',{count:number(papers.length)}));
};
async function loadPapers(){
 if(loading)return;loading=true;loadState='loading';$('#cards').setAttribute('aria-busy','true');$('#load-error').hidden=true;$('#results').textContent=t('loading');$('#download-all').disabled=true;
 try{
  const responses=await Promise.all([fetch('palettes.json'),fetch('content-en.json?v=20261124-languages'),fetch('content-zh.json?v=20261124-languages')]);if(responses.some(r=>!r.ok))throw Error('Data could not be loaded');
  const [data,english,chinese]=await Promise.all(responses.map(r=>r.json()));
  if(!english||english.version!==1||!english.strings||typeof english.strings!=='object')throw Error('Invalid English dictionary');
  if(!chinese||chinese.version!==1||!chinese.strings||typeof chinese.strings!=='object')throw Error('Invalid Chinese dictionary');
  if(!Array.isArray(data)||!data.every(p=>p&&typeof p.id==='string'&&typeof p.domain==='string'&&typeof p.image==='string'&&typeof p.title==='string'&&Array.isArray(p.tags)&&Array.isArray(p.colors)&&p.colors.length>=2&&p.colors.length<=8&&p.colors.every(c=>/^#[0-9a-f]{6}$/i.test(c)))||new Set(data.map(p=>p.id)).size!==data.length)throw Error('Invalid palette data');
  englishText=english.strings;chineseText=chinese.strings;
  papers=data.map((p,i)=>({...p,sourceOrder:i,order:Number.isFinite(p.order)?p.order:i,searchText:[p.name,p.title,p.domain,...p.tags,p.mood,...[p.title,p.domain,...p.tags,p.mood].map(x=>englishText[x]||x)].join(' ').toLocaleLowerCase()}));
  visibleLimit=PAGE_SIZE;loadState='ready';updateCounts();render();$('#download-all').disabled=!papers.length;
 }catch{
  loadState='error';$('#results').textContent=t('loadError');$('#cards').innerHTML='';$('#empty').hidden=true;$('#pagination').hidden=true;$('#load-error').hidden=false;
 }finally{loading=false;$('#cards').setAttribute('aria-busy','false')}
}
applyLanguage();loadPapers();

