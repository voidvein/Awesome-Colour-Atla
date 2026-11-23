/* Interface copy. Research text is translated once in content-en.json, never at runtime. */
const ATLAS_I18N={
 en:{
  title:'Colour Atlas — colour from research',home:'Colour Atlas home',navigation:'Main navigation',edition:'Research colour archive',explore:'Explore palettes',about:'About the colours',language:'Language',
  hero:'Great colours from papers.<br>For your <span class="accent">next figure.</span>',intro:'Find colour inspiration in network architectures.<br class="desktop"> Original figures, considered palettes, clearer research.',papers:'papers collected',domains:'research areas',colours:'representative colours',collection:'Find your next palette',sort:'Sorted by likes',
  search:'Search papers or tags',placeholder:'Search papers, fields or models, e.g. segmentation / MoE',liked:'My likes',filters:'Filter by research area',all:'All',reset:'Clear filters',preview:'Preview · likes saved in this browser',loading:'Loading research palettes…',
  more:'Load more palettes',loadError:'Palettes could not be loaded',retryHint:'Check your connection or try again later.',retry:'Try again',noScript:'Enable JavaScript to browse palettes, search research areas and copy colours.',empty:'No matching palettes',emptyHint:'Try another keyword or clear your filters.',viewAll:'View all palettes',
  closing:'Inspiration with a source.',closingCopy:'Every palette links to its paper. Open a figure for the full image and colour notes; select a swatch to copy its HEX.',export:'Export all palettes (JSON)',footer:'Collected for your next clearer research figure.',closeDetail:'Close details',closeAbout:'Close about',
  aboutHeading:'From architecture to palette.',aboutSource:'Papers come from the Paper Notes CVPR 2026 index. Figures come from original papers or public author projects; each card identifies its source and figure number.',
  aboutMethod:'We sample module fills, outlines and tokens, then visually check the original pixels. Backgrounds, example photos and noise are excluded; meaningful neutral colours are retained. Each palette has 2–8 exact representative colours. Swatches have equal widths, not proportional areas. Gradients use a representative sample.',
  aboutCredit:'Tags describe the paper’s task and model. Colour notes are editorial analysis; English descriptions are machine-assisted translations. Original figure labels stay as published. Figure rights belong to their authors; follow the source licence when reusing them.',
  aboutLikes:'Likes start at zero, can be undone and are saved in this browser. The ranking reflects your local likes, not a shared site-wide count. Ties follow collection order.',index:'Browse the paper index',aboutCount:'{papers} papers across {domains} research areas. ',
  description:'Discover colour palettes from original research architecture diagrams. {papers} papers, {domains} research areas, source figures, tags and copyable colours.',
  copy:'Copy {value}',copyColour:'Copy colour {value}',copied:'Copied {value}',copyFailed:'Copy failed. Copy the HEX values from the list instead.',storageFailed:'This browser could not save your likes; they will last for this visit only.',
  viewDetail:'View {name} architecture and palette',imageAlt:'{name} original architecture diagram, {figure}',originalFigure:'Original architecture',zoom:'View figure and palette',like:'Like {name}',unlike:'Unlike {name}',
  total:'{count} palettes',found:'{count} matching palettes',shown:' · showing {count}',moreCount:'Load {count} more palettes',progress:'Showing {visible} / {total} palettes',
  fullSize:'Open full-size image',fullAlt:'{name} full architecture diagram',colourCount:'{count} colours',notes:'Colour notes',usage:'Where this palette works',source:'Figure source: ',caption:'Swatches have equal widths, not proportional areas. Select a swatch to copy its HEX.',paper:'Read the paper',paperNotes:'Paper Notes',copyAll:'Copy all HEX values',exported:'Exported {count} palettes and paper sources'
 },
 'zh-CN':{
  title:'Colour Atlas — 论文里的好配色',home:'Colour Atlas 首页',navigation:'主导航',edition:'研究配色档案',explore:'探索色卡',about:'关于采色',language:'语言',
  hero:'论文里的好配色，<br>成为你的<span class="accent">下一张图。</span>',intro:'从网络架构图里发现色彩灵感。保留原图、提取主色，<br class="desktop">让科研绘图少一点试错，多一点好看。',papers:'篇收录论文',domains:'个研究方向',colours:'个代表色',collection:'发现一组好配色',sort:'按点赞数排序',
  search:'搜索论文或标签',placeholder:'搜索论文、领域或模型，例如：分割 / MoE',liked:'我赞过的',filters:'按研究领域筛选',all:'全部',reset:'清除筛选',preview:'预览版 · 点赞保存在当前浏览器',loading:'正在加载论文色卡…',
  more:'查看更多色卡',loadError:'暂时无法加载色卡',retryHint:'请检查网络连接，或稍后重试。',retry:'重新加载',noScript:'请启用 JavaScript，以加载色卡、搜索领域和复制配色。',empty:'还没有找到这组配色',emptyHint:'换一个关键词，或清除筛选试试。',viewAll:'查看全部色卡',
  closing:'灵感有出处，配色有依据。',closingCopy:'每张卡片都链接原始论文。点击架构图查看大图与配色分析，点击色块复制 HEX。',export:'导出全部配色 JSON',footer:'为下一张更清晰的科研图而收集。',closeDetail:'关闭详情',closeAbout:'关闭说明',
  aboutHeading:'从架构图，到你的调色板。',aboutSource:'论文来自 Paper Notes 的 CVPR 2026 索引。图片来自论文原文或作者公开项目，来源和图号在详情中逐一注明。',
  aboutMethod:'采色先定位模块填色、边框和 token，再统计原始像素中的代表颜色并目视校对。排除白背景、示例照片和噪声，保留有意义的中性色。每组保留 2–8 个确切的模块代表色；色块等宽展示，不表示像素占比。渐变使用模块中部的代表取样。',
  aboutCredit:'标签依据论文任务与模型类型整理；配色解读是本项目的设计分析，英文说明经过机器辅助翻译。原图中的文字保持论文原样。图像版权归原作者所有，引用原图时请遵守其许可并注明来源。',
  aboutLikes:'点赞从 0 开始，保存在当前浏览器，可取消。当前排序仅反映本浏览器的点赞，不是全站统计。同票时按收录顺序排列。',index:'查看论文索引',aboutCount:'目前收录 {papers} 篇论文，覆盖 {domains} 个研究方向。',
  description:'从论文原版网络架构图中发现科研配色。{papers} 篇论文、{domains} 个研究方向，原图、领域标签和可复制色卡。',
  copy:'复制 {value}',copyColour:'复制色值 {value}',copied:'已复制 {value}',copyFailed:'复制失败，请从色值列表中手动复制',storageFailed:'浏览器未允许保存，点赞仅在本次页面中有效',
  viewDetail:'查看 {name} 架构图及配色分析',imageAlt:'{name} 原版网络架构图，{figure}',originalFigure:'原版架构图',zoom:'查看大图与配色',like:'点赞 {name}',unlike:'取消点赞 {name}',
  total:'共 {count} 张色卡',found:'找到 {count} 张色卡',shown:' · 已展示 {count}',moreCount:'再看 {count} 张色卡',progress:'已展示 {visible} / {total} 张',
  fullSize:'打开原尺寸图片',fullAlt:'{name} 完整架构图',colourCount:'{count} 色',notes:'配色观察',usage:'适合怎样的图？',source:'图像出处：',caption:'色块等宽展示，不表示颜色占比。点击色块复制色值。',paper:'查看原论文',paperNotes:'Paper Notes 解读',copyAll:'复制整组 HEX',exported:'已导出 {count} 组配色与论文来源'
 }
};
