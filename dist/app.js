const PAGE_SIZE=24;
let papers=[],selected='全部',onlyLiked=false,query='',visibleLimit=PAGE_SIZE,loading=false;
let likes={};
try{likes=JSON.parse(localStorage.getItem('colour-atlas-likes-v1')||'{}');if(!likes||typeof likes!=='object'||Array.isArray(likes))likes={}}catch{}
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const heart='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/></svg>';
const external='<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3H3v10h10v-3M9 2h5v5M14 2 7 9"/></svg>';
const swatches=p=>'<div class="swatches">'+p.colors.map(c=>`<button class="swatch" style="background:${c}" data-color="${c}" title="复制 ${c}" aria-label="复制色值 ${c}"><span class="hex">${c}</span></button>`).join('')+'</div>';
function notify(t){$('#toast').textContent=t;$('#toast').classList.add('show');clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),2000)}
async function copy(t){try{await navigator.clipboard.writeText(t);notify('已复制 '+t)}catch{const a=document.createElement('textarea');a.value=t;document.body.append(a);a.select();const ok=document.execCommand('copy');a.remove();notify(ok?'已复制 '+t:'复制失败，请从色值列表中手动复制')}}
function updateCounts(){
 const domains=new Set(papers.map(p=>p.domain)).size,colours=papers.reduce((n,p)=>n+p.colors.length,0);
 $('#paper-count').textContent=papers.length.toLocaleString();$('#domain-count').textContent=domains.toLocaleString();$('#colour-count').textContent=colours.toLocaleString();$('#total').textContent=papers.length.toLocaleString();
 $('#footer-count').textContent=`CVPR 2026 · ${papers.length.toLocaleString()} PALETTES`;
 $('#about-count').textContent=`目前收录 ${papers.length.toLocaleString()} 篇论文，覆盖 ${domains.toLocaleString()} 个研究方向。`;
 document.querySelector('meta[name="description"]').setAttribute('content',`从论文原版网络架构图中发现科研配色。${papers.length} 篇论文、${domains} 个研究方向，原图、领域标签和可复制色卡。`);
}
function filters(){
 const counts=new Map();for(const p of papers)counts.set(p.domain,(counts.get(p.domain)||0)+1);
 $('#filters').innerHTML=['全部',...counts.keys()].map(d=>`<button class="filter ${selected===d?'active':''}" data-filter="${esc(d)}" aria-pressed="${selected===d}">${esc(d)}<em>${d==='全部'?papers.length:counts.get(d)}</em></button>`).join('');
}
function matchingPapers(){
 const search=query.toLocaleLowerCase();
 return papers.filter(p=>(selected==='全部'||p.domain===selected||p.tags.includes(selected))&&(!onlyLiked||likes[p.id]===true)&&(!search||p.searchText.includes(search)))
  .sort((a,b)=>Number(likes[b.id]===true)-Number(likes[a.id]===true)||a.order-b.order||a.sourceOrder-b.sourceOrder);
}
function card(p){return `<article class="card"><button class="image-button" data-detail="${esc(p.id)}" aria-label="查看 ${esc(p.name)} 架构图及配色分析"><img src="${esc(p.thumbnail||p.image)}" alt="${esc(p.name)} 原版网络架构图，${esc(p.figure)}" loading="lazy" decoding="async"><span class="image-label">${esc(p.figure)} · 原版架构图</span><span class="zoom-hint"><span>查看大图与配色</span></span></button><div class="card-content"><div class="card-meta"><span class="venue">${esc(p.venue)}</span><span class="palette-name">${esc(p.mood)}</span></div><h3>${esc(p.name)}</h3>${swatches(p)}<p class="paper-title" title="${esc(p.title)}">${esc(p.title)}</p><div class="tags">${p.tags.slice(0,3).map(t=>`<button class="tag" data-tag="${esc(t)}">${esc(t)}</button>`).join('')}</div><div class="card-footer"><a class="source-link" href="${esc(p.paper)}" target="_blank" rel="noopener">${esc(p.sourceLabel)} ${external}</a><button class="like" data-like="${esc(p.id)}" aria-label="${likes[p.id]===true?'取消点赞':'点赞'} ${esc(p.name)}" aria-pressed="${likes[p.id]===true}">${heart}<span>${likes[p.id]===true?1:0}</span></button></div></div></article>`}
function render(){
 const shown=matchingPapers(),visible=shown.slice(0,visibleLimit);
 $('#cards').innerHTML=visible.map(card).join('');$('#empty').hidden=shown.length>0;$('#load-error').hidden=true;
 $('#results').textContent=`${selected==='全部'&&!query&&!onlyLiked?'共':'找到'} ${shown.length.toLocaleString()} 张色卡${shown.length>visible.length?` · 已展示 ${visible.length}`:''}`;
 $('#reset').hidden=selected==='全部'&&!query&&!onlyLiked;$('#liked-filter').setAttribute('aria-pressed',String(onlyLiked));
 $('#pagination').hidden=shown.length<=visible.length;$('#load-more').textContent=`再看 ${Math.min(PAGE_SIZE,shown.length-visible.length)} 张色卡`;
 $('#page-progress').textContent=`已展示 ${visible.length} / ${shown.length} 张`;
 filters();
}
function detail(id){
 const p=papers.find(x=>x.id===id);if(!p)return;
 $('#detail-body').innerHTML=`<div class="detail-image"><a href="${esc(p.image)}" target="_blank" rel="noopener" title="打开原尺寸图片"><img src="${esc(p.image)}" alt="${esc(p.name)} 完整架构图"></a></div><div class="detail-copy"><p class="venue">${esc(p.venue)} · ${esc(p.figure)}</p><h2>${esc(p.name)}<span>${p.colors.length} 色</span></h2><p class="full-title">${esc(p.title)}</p>${swatches(p)}<div class="hex-list">${p.colors.map(c=>`<span>${c}</span>`).join(' · ')}</div><h4>配色观察</h4><p class="analysis">${esc(p.analysis)}</p><h4>适合怎样的图？</h4><p class="analysis">${esc(p.usage)}</p><div class="tags">${p.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><p class="detail-caption">图像出处：${esc(p.provenance)}。${esc(p.note)} 色块为等宽展示，不表示颜色占比。点击色块复制色值。</p><div class="detail-links"><a href="${esc(p.paper)}" target="_blank" rel="noopener">查看原论文</a><a href="${esc(p.noteUrl)}" target="_blank" rel="noopener">Paper Notes 解读</a><button class="tag" data-copy-all="${esc(p.id)}">复制整组 HEX</button></div></div>`;
 $('#detail').showModal();
}
function reset(){selected='全部';query='';onlyLiked=false;visibleLimit=PAGE_SIZE;$('#search').value='';render()}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b)return;
 if(b.dataset.color)copy(b.dataset.color);
 if(b.dataset.detail)detail(b.dataset.detail);
 if(b.dataset.filter){selected=b.dataset.filter;visibleLimit=PAGE_SIZE;render()}
 if(b.dataset.tag){selected=b.dataset.tag;if(!papers.some(p=>p.domain===selected)){selected='全部';query=b.dataset.tag;$('#search').value=query}visibleLimit=PAGE_SIZE;render();$('#collection').scrollIntoView({behavior:'smooth'})}
 if(b.dataset.like){const id=b.dataset.like;if(!papers.some(p=>p.id===id))return;likes[id]=likes[id]!==true;try{localStorage.setItem('colour-atlas-likes-v1',JSON.stringify(likes))}catch{notify('浏览器未允许保存，点赞仅在本次页面中有效')}render();const next=document.querySelector(`[data-like="${CSS.escape(id)}"]`);next?.focus({preventScroll:true})}
 if(b.dataset.copyAll){const p=papers.find(p=>p.id===b.dataset.copyAll);if(p)copy(p.colors.join(', '))}
});
$('#search').addEventListener('input',e=>{query=e.target.value.trim();visibleLimit=PAGE_SIZE;render()});
$('#liked-filter').onclick=()=>{onlyLiked=!onlyLiked;visibleLimit=PAGE_SIZE;render()};
$('#load-more').onclick=()=>{visibleLimit+=PAGE_SIZE;render()};
$('#reset').onclick=reset;$('#empty-reset').onclick=reset;$('#retry-load').onclick=loadPapers;
$('#close-detail').onclick=()=>$('#detail').close();$('#about').onclick=()=>$('#about-dialog').showModal();$('#close-about').onclick=()=>$('#about-dialog').close();
document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!['INPUT','TEXTAREA'].includes(document.activeElement.tagName)&&!document.querySelector('dialog[open]')){e.preventDefault();$('#search').focus()}});
$('#download-all').onclick=()=>{
 if(!papers.length)return;
 const data=papers.map(({sourceOrder,searchText,...p})=>p),a=document.createElement('a');
 a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='colour-atlas-cvpr2026.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);notify(`已导出 ${papers.length.toLocaleString()} 组配色与论文来源`);
};
async function loadPapers(){
 if(loading)return;loading=true;$('#cards').setAttribute('aria-busy','true');$('#load-error').hidden=true;$('#results').textContent='正在加载论文色卡…';$('#download-all').disabled=true;
 try{
  const r=await fetch('palettes.json');if(!r.ok)throw Error('数据加载失败');const data=await r.json();
  if(!Array.isArray(data)||!data.every(p=>p&&typeof p.id==='string'&&typeof p.domain==='string'&&typeof p.image==='string'&&typeof p.title==='string'&&Array.isArray(p.tags)&&Array.isArray(p.colors)&&p.colors.length>=2&&p.colors.length<=8&&p.colors.every(c=>/^#[0-9a-f]{6}$/i.test(c)))||new Set(data.map(p=>p.id)).size!==data.length)throw Error('色卡数据格式异常');
  papers=data.map((p,i)=>({...p,sourceOrder:i,order:Number.isFinite(p.order)?p.order:i,searchText:[p.name,p.title,p.domain,...p.tags,p.mood].join(' ').toLocaleLowerCase()}));
  visibleLimit=PAGE_SIZE;updateCounts();render();$('#download-all').disabled=!papers.length;
 }catch{
  $('#results').textContent='暂时无法加载色卡';$('#cards').innerHTML='';$('#empty').hidden=true;$('#pagination').hidden=true;$('#load-error').hidden=false;
 }finally{loading=false;$('#cards').setAttribute('aria-busy','false')}
}
loadPapers();
