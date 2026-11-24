const GRADIENT_COPY={
 en:{gradients:'Gradients',eyebrow:'THE GRADIENT COLLECTION',heading:'Find your gradient.',intro:'Smooth colour blends for your next figure. Preview a gradient, see its colours, and take the one that fits.',collectionLabel:'Gradient collection',search:'Search gradients',placeholder:'Search by name or HEX, e.g. lilac / #9BADD0',direction:'Direction',resetAngle:'Reset direction to 135 degrees',filters:'Filter gradients',all:'All',soft:'Soft',cool:'Cool',warm:'Warm',vivid:'Vivid',deep:'Deep',loading:'Loading gradients…',empty:'No matching gradients',emptyHint:'Try a name, a HEX value, or another colour family.',viewAll:'View all gradients',loadError:'Gradients could not be loaded',retryHint:'Check your connection and try again.',retry:'Try again',inspiration:'Layout inspired by',curated:'. Palettes curated for Colour Atlas.',tip:'Select a colour to copy its HEX. Positions show where each colour sits in the gradient.',back:'Browse paper palettes',previewLabel:'Gradient preview',closePreview:'Close preview',preview:'Preview {name}',copyStop:'Copy {colour} at {position}%',copyCss:'Copy CSS',copyColours:'Copy colours',copied:'Copied {value}',copiedCss:'Gradient CSS copied',copiedColours:'Gradient colours copied',copyFailed:'Copy failed. Select the HEX values or CSS and copy them manually.',results:'{count} gradients',filtered:'{count} of {total} gradients',description:'Curated colour gradients with every HEX value, colour-stop position and ready-to-use CSS.'},
 'zh-CN':{gradients:'渐变色卡',eyebrow:'渐变配色集',heading:'找到你需要的渐变。',intro:'为下一张图挑选一组平滑过渡的配色。上方预览渐变，下方查看组成颜色，选中即可复制。',collectionLabel:'渐变色卡集合',search:'搜索渐变色卡',placeholder:'搜索名称或 HEX，例如：薄荷 / #9BADD0',direction:'渐变方向',resetAngle:'恢复为135度渐变方向',filters:'筛选渐变色卡',all:'全部',soft:'柔和',cool:'冷色',warm:'暖色',vivid:'鲜明',deep:'深色',loading:'正在加载渐变色卡…',empty:'没有找到匹配的渐变',emptyHint:'试试名称、HEX 色值，或切换其他色彩类别。',viewAll:'查看全部渐变',loadError:'暂时无法加载渐变色卡',retryHint:'请检查网络连接后重试。',retry:'重新加载',inspiration:'页面形式参考',curated:'，配色由 Colour Atlas 整理。',tip:'点击颜色复制 HEX，百分比表示该颜色在渐变中的位置。',back:'浏览论文配色',previewLabel:'渐变预览',closePreview:'关闭预览',preview:'预览{name}',copyStop:'复制{position}%位置的{colour}',copyCss:'复制 CSS',copyColours:'复制整组颜色',copied:'已复制 {value}',copiedCss:'渐变 CSS 已复制',copiedColours:'整组颜色已复制',copyFailed:'复制失败，请选中色值或 CSS 手动复制。',results:'共 {count} 组渐变',filtered:'找到 {count} / {total} 组渐变',description:'查看渐变预览、每个 HEX 色值与渐变位置，并复制可直接使用的 CSS。'}
};
const GRADIENT_GROUPS=['all','soft','cool','warm','vivid','deep'];
let gradientLanguage='en',gradients=[],gradientGroup='all',gradientQuery='',gradientAngle=135,gradientCurrent=null,gradientState='loading',gradientLoading=false;
try{const saved=localStorage.getItem('colour-atlas-language-v1');if(saved==='en'||saved==='zh-CN')gradientLanguage=saved}catch{}
const g$=selector=>document.querySelector(selector);
const gEsc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const gt=(key,values={})=>String(GRADIENT_COPY[gradientLanguage][key]??ATLAS_I18N[gradientLanguage][key]).replace(/\{(\w+)\}/g,(_,name)=>String(values[name]??''));
const gradientName=g=>g.name[gradientLanguage];
function gradientCss(g){return 'linear-gradient('+gradientAngle+'deg, '+g.stops.map(stop=>stop.color+' '+stop.position+'%').join(', ')+')'}
function gradientToast(message){g$('#toast').textContent=message;g$('#toast').classList.add('show');clearTimeout(window.gradientToastTimer);window.gradientToastTimer=setTimeout(()=>g$('#toast').classList.remove('show'),2200)}
async function gradientCopy(value,message){
 try{await navigator.clipboard.writeText(value);gradientToast(message)}
 catch{const field=document.createElement('textarea');field.value=value;document.body.append(field);field.select();const copied=document.execCommand('copy');field.remove();gradientToast(copied?message:gt('copyFailed'))}
}
function gradientStops(g){
 return '<div class="gradient-stops" style="--stops:'+g.stops.length+'">'+g.stops.map(stop=>'<button class="gradient-stop" type="button" data-gradient-colour="'+stop.color+'" aria-label="'+gEsc(gt('copyStop',{colour:stop.color,position:stop.position}))+'"><span class="stop-sample" style="background:'+stop.color+'" aria-hidden="true"></span><span class="stop-code">'+stop.color+'</span><span class="stop-position">'+stop.position+'%</span></button>').join('')+'</div>';
}
function gradientActions(g){return '<div class="gradient-card-actions"><button type="button" class="copy-gradient-css" data-gradient-css="'+g.id+'">'+gt('copyCss')+'</button><button type="button" class="copy-gradient-colours" data-gradient-colours="'+g.id+'">'+gt('copyColours')+'</button></div>'}
function gradientCard(g){
 return '<article class="gradient-card"><button type="button" class="gradient-preview" data-gradient-preview="'+g.id+'" aria-label="'+gEsc(gt('preview',{name:gradientName(g)}))+'"><span class="gradient-orb" style="background-image:'+gradientCss(g)+'"></span><span class="gradient-expand" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M2 6V2h4m4 0h4v4m0 4v4h-4m-4 0H2v-4"/></svg></span></button><div class="gradient-card-body"><div class="gradient-card-heading"><h2>'+gEsc(gradientName(g))+'</h2><span class="gradient-card-group">'+gt(g.group)+'</span></div>'+gradientStops(g)+gradientActions(g)+'</div></article>';
}
function renderGradients(){
 const search=gradientQuery.toLocaleLowerCase();
 const shown=gradients.filter(g=>(gradientGroup==='all'||g.group===gradientGroup)&&(!search||[g.name.en,g.name['zh-CN'],...g.stops.map(s=>s.color)].join(' ').toLocaleLowerCase().includes(search)));
 g$('#gradient-grid').innerHTML=shown.map(gradientCard).join('');
 g$('#gradient-empty').hidden=shown.length>0;g$('#gradient-error').hidden=true;g$('#gradient-loading').hidden=true;
 g$('#gradient-results').textContent=gt(gradientGroup==='all'&&!gradientQuery?'results':'filtered',{count:shown.length,total:gradients.length});
 g$('#gradient-filters').innerHTML=GRADIENT_GROUPS.map(group=>'<button class="filter '+(group===gradientGroup?'active':'')+'" type="button" data-gradient-group="'+group+'" aria-pressed="'+(group===gradientGroup)+'">'+gt(group)+'<em>'+(group==='all'?gradients.length:gradients.filter(g=>g.group===group).length)+'</em></button>').join('');
 g$('#gradient-angle-output').textContent=gradientAngle+'°';
 if(gradientCurrent&&g$('#gradient-detail').open)openGradient(gradientCurrent);
}
function applyGradientLanguage(){
 document.documentElement.lang=gradientLanguage;document.title=gt('title');
 const properties={gradientCopy:'textContent',gradientAria:'aria-label',gradientPlaceholder:'placeholder'};
 for(const [property,target] of Object.entries(properties)){
  const attr='data-'+property.replace(/[A-Z]/g,c=>'-'+c.toLowerCase());
  document.querySelectorAll('['+attr+']').forEach(node=>{const value=gt(node.dataset[property]);if(target==='textContent')node.textContent=value;else node.setAttribute(target,value)});
 }
 document.querySelector('meta[name="description"]').setAttribute('content',gt('description'));
 g$('#language-select').value=gradientLanguage;g$('#reset-angle').setAttribute('title',gt('resetAngle'));
 if(gradientState==='ready')renderGradients();else g$('#gradient-results').textContent=gt(gradientState==='error'?'loadError':'loading');
}
function openGradient(id){
 const g=gradients.find(item=>item.id===id);if(!g)return;gradientCurrent=id;
 const css='background: '+gradientCss(g)+';';
 g$('#gradient-detail-body').innerHTML='<div class="gradient-modal-preview" style="background-image:'+gradientCss(g)+'"></div><div class="gradient-modal-copy"><div class="gradient-modal-heading"><h2 id="gradient-detail-title">'+gEsc(gradientName(g))+'</h2><span>'+gt('direction')+' · '+gradientAngle+'°</span></div>'+gradientStops(g)+'<pre class="gradient-code"><code>'+gEsc(css)+'</code></pre>'+gradientActions(g)+'</div>';
 if(!g$('#gradient-detail').open)g$('#gradient-detail').showModal();
}
function resetGradients(){gradientGroup='all';gradientQuery='';g$('#gradient-search').value='';renderGradients()}
document.addEventListener('click',event=>{
 const button=event.target.closest('button');if(!button)return;const data=button.dataset;
 if(data.gradientColour)gradientCopy(data.gradientColour,gt('copied',{value:data.gradientColour}));
 if(data.gradientGroup){gradientGroup=data.gradientGroup;if(gradientState==='ready')renderGradients()}
 if(data.gradientPreview)openGradient(data.gradientPreview);
 if(data.gradientCss){const g=gradients.find(item=>item.id===data.gradientCss);if(g)gradientCopy('background: '+gradientCss(g)+';',gt('copiedCss'))}
 if(data.gradientColours){const g=gradients.find(item=>item.id===data.gradientColours);if(g)gradientCopy(g.stops.map(s=>s.color).join(', '),gt('copiedColours'))}
});
g$('#gradient-search').addEventListener('input',event=>{gradientQuery=event.target.value.trim();if(gradientState==='ready')renderGradients()});
g$('#gradient-angle').addEventListener('input',event=>{const value=Number(event.target.value);if(!Number.isFinite(value)||value<0||value>360)return;gradientAngle=value;g$('#gradient-angle-output').textContent=value+'°';if(gradientState==='ready')renderGradients()});
g$('#reset-angle').onclick=()=>{gradientAngle=135;g$('#gradient-angle').value='135';if(gradientState==='ready')renderGradients()};
g$('#language-select').addEventListener('change',event=>{if(!['en','zh-CN'].includes(event.target.value))return;gradientLanguage=event.target.value;try{localStorage.setItem('colour-atlas-language-v1',gradientLanguage)}catch{}applyGradientLanguage()});
g$('#about').onclick=()=>g$('#about-dialog').showModal();
g$('#close-about').onclick=()=>g$('#about-dialog').close();
g$('#about-dialog').addEventListener('click',event=>{if(event.target!==g$('#about-dialog'))return;const r=event.target.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)event.target.close()});
g$('#gradient-reset').onclick=resetGradients;g$('#gradient-retry').onclick=loadGradients;
g$('#close-gradient').onclick=()=>{g$('#gradient-detail').close();gradientCurrent=null};
g$('#gradient-detail').addEventListener('click',event=>{if(event.target!==g$('#gradient-detail'))return;const r=event.target.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom){event.target.close();gradientCurrent=null}});
document.addEventListener('keydown',event=>{if(event.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!g$('#gradient-detail').open&&!g$('#about-dialog').open){event.preventDefault();g$('#gradient-search').focus()}});
function validGradient(g){
 return g&&typeof g.id==='string'&&/^[a-z0-9-]+$/.test(g.id)&&g.name&&['en','zh-CN'].every(lang=>typeof g.name[lang]==='string'&&g.name[lang].trim())&&GRADIENT_GROUPS.slice(1).includes(g.group)&&Array.isArray(g.stops)&&g.stops.length>=2&&g.stops.length<=4&&g.stops.every((s,i)=>s&&/^#[0-9A-F]{6}$/.test(s.color)&&Number.isFinite(s.position)&&s.position>=0&&s.position<=100&&(i===0||s.position>g.stops[i-1].position))&&g.stops[0].position===0&&g.stops.at(-1).position===100&&new Set(g.stops.map(s=>s.color)).size>=2;
}
async function loadGradients(){
 if(gradientLoading)return;gradientLoading=true;gradientState='loading';g$('#gradient-grid').setAttribute('aria-busy','true');g$('#gradient-error').hidden=true;g$('#gradient-empty').hidden=true;g$('#gradient-loading').hidden=false;g$('#gradient-results').textContent=gt('loading');
 try{
  const response=await fetch('gradients.json?v=1');if(!response.ok)throw Error('Gradient data unavailable');const data=await response.json();
  if(!Array.isArray(data)||!data.length||!data.every(validGradient)||new Set(data.map(g=>g.id)).size!==data.length)throw Error('Invalid gradients');
  gradients=data;gradientState='ready';renderGradients();
 }catch{gradientState='error';g$('#gradient-grid').innerHTML='';g$('#gradient-loading').hidden=true;g$('#gradient-error').hidden=false;g$('#gradient-results').textContent=gt('loadError')}
 finally{gradientLoading=false;g$('#gradient-grid').setAttribute('aria-busy','false')}
}
applyGradientLanguage();loadGradients();

