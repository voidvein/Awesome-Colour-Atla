import json
from pathlib import Path
R=Path(__file__).parent
if (R/'dist/collection.json').exists():
 raise SystemExit('Legacy 10-card builder disabled after batch publication. Use pipeline/publish_dataset.py.')
papers=json.loads((R/'research/papers.json').read_text(encoding='utf8'))
assets={p['id']:p for p in json.loads((R/'research/assets-a.json').read_text(encoding='utf8'))}
# Representative flat module fills and outlines, verified against original pixels.
spec={
'image_generation':('OmniGen2','图像生成',['图像生成','多模态','Transformer'],'青蓝 × 珊瑚','#97CBD9 #B3D9E4 #B4C7E7 #D0CDCD #EF8E77','青蓝色的自回归路径与珊瑚色的扩散路径形成清晰的冷暖分工；浅蓝 tokenizer 与灰色隐藏状态弱化辅助环节。','适合理解与生成双分支架构。主模块用两种对比色，同一分支的子模块使用浅色。'),
'3d_reconstruction':('ARCA-GS','三维重建',['三维重建','3D Gaussian','FiLM'],'蓝绿 × 杏桃','#DDF0D2 #ACC8E8 #DEE8F5 #F6E3D7 #6092D3 #264F22 #F4C142','浅绿分辨率感知模块、浅蓝两阶段特征与深绿像素覆盖门形成层级，杏桃色区分残差预测。蓝色渲染块统一两条输出路径。','适合多阶段重建与编码解码网络。浅色用于模块背景，深色用于少量关键门控节点。'),
'object_detection':('Rex-Omni','目标检测',['目标检测','VLM','点预测'],'雾蓝 × 浅桃','#DDE4E9 #FBE3D6 #F3F3E0 #A6A6A6 #0E2841','蓝灰色统一视觉主干与视觉 token，浅桃色标识文本输入，奶油色标识坐标 token；深海军蓝文字建立可读性。','适合视觉语言模型与 token 流程。大面积低饱和填色搭配深色文字，让模块区别保持克制。'),
'segmentation':('Earth2Ocean','语义分割',['语义分割','开放词汇','CLIP'],'金黄 × 草绿','#FDF6E0 #FDE694 #F1B902 #E2F1D9 #75BC42 #91ACDF #323296 #EE939E','暖黄色组织语言推理与文本模块，绿色区分类别语义，蓝色区分视觉与融合特征；少量深蓝让几何注意力更醒目。','适合视觉与语言两条路径的分割网络。大区域用浅色，箭头、类别条形图与关键特征用同色系高饱和色。'),
'image_restoration':('DiffDecompose','图像恢复',['图像恢复','扩散模型','DiT'],'粉蓝 × 鼠尾草','#BCD6ED #B8D7A0 #E7DCD0 #CDA99B #F4B083 #2D75B6','粉蓝编码条件 token，浅绿编码噪声 token，米灰色承载 DiT 模块；暖橙用于层次位置编码，蓝色轮廓强化 token 类型。','适合扩散模型、条件生成和多输入恢复网络。按 token 类型统一配色，让颜色贯穿输入、注意力与输出。'),
'remote_sensing':('TESSERA','遥感',['遥感','时序建模','自监督'],'青绿 × 淡紫','#F9DEC8 #AACFC8 #D3CAE6 #B6D2C7 #497589 #042433','光学分支使用浅桃色，雷达时序编码路径使用青绿与蓝色渐变，投影特征使用浅紫色；深蓝描边统一密集的模块与连线。','适合多源遥感、时序融合与对比学习架构。不同模态保持不同色系，融合特征统一使用紫色。'),
'video_understanding':('WorldMM','视频理解',['视频理解','多模态记忆','Agent'],'冰蓝 × 蜜桃','#DCEAF7 #FAE2D5 #D9F1D0 #A6C9EB #F6C5AC #186B23 #37474F','情景、语义与视觉记忆分别使用蓝、桃、绿三组颜色，检索阶段沿用同一映射，便于跨区域追踪信息流。','适合多记忆、多工具或多分支 Agent 框架。同一类型从构建到检索复用一种颜色，深色只强调数据结构与输出。'),
'autonomous_driving':('DriveMoE','自动驾驶',['自动驾驶','MoE','VLA'],'杏桃 × 奶油黄','#FADDCB #FFEFBE #BDD7ED #FFD966 #9DC3E6 #A9D18E #7D88CD','杏桃色划分视觉选择区，奶油黄色划分驾驶技能区。中央蓝色语言模型与黄色动作 MoE 构成主干，绿色与紫色区分动作及状态 token。','适合感知、决策、动作多阶段网络。先用大面积浅色分区，再用饱和色给核心模块和 token 编码。'),
'robotics':('Motus','机器人',['机器人','世界模型','多专家'],'酒红 × 赭橙 × 紫','#851321 #FFF0FF #843F0B #FFF3E6 #7030A0 #F0E9FF','酒红、赭橙与紫色区分视频生成、动作和理解三个专家，各配相应浅色底；联合注意力的渐变表达三条路径的融合。','适合三专家架构与具身世界模型。描边、模块标题和 token 使用同组深色，背景采用同色系浅色。'),
'medical_imaging':('GVL-MIL','医学图像',['医学图像','多实例学习','VLM'],'浅绿 × 藕粉','#E7F2E0 #B0D4C8 #EED0E3 #BDD3E7 #A83766 #F7C6B3 #CDCAAB','浅绿色组织 VLM 分层结构，藕粉色强调特征聚合与双分支 MIL；蓝色对应视觉编码，粉色 token 与杏色 LoRA 模块提供局部区分。','适合医学多模态、弱监督与特征聚合网络。骨干用低饱和浅色，选择或聚合模块用粉色形成视觉焦点。')}
extras={
'3d_reconstruction':dict(paperUrl='https://openaccess.thecvf.com/content/CVPR2026/html/Jeong_3D_Gaussian_Splatting_at_Arbitrary_Resolutions_with_Compact_Proxy_Anchors_CVPR_2026_paper.html',figure='Figure 2',sourceUrl='CVF 开放论文，PDF 第 3 页，图 2；仅裁去正文与页边空白'),
'image_restoration':dict(paperUrl='https://arxiv.org/abs/2505.21541',figure='Figure 3',sourceUrl='arXiv 2505.21541 v3，图 3',imageUrl='https://arxiv.org/html/2505.21541v3/Fig3.png'),
'video_understanding':dict(paperUrl='https://arxiv.org/abs/2512.02425',figure='Figure 2',sourceUrl='arXiv 2512.02425 v2，图 2',imageUrl='https://arxiv.org/html/2512.02425v2/fig_method.png'),
'autonomous_driving':dict(paperUrl='https://arxiv.org/abs/2505.16278',figure='Figure 2',sourceUrl='arXiv 2505.16278 v2，图 2',imageUrl='https://arxiv.org/html/2505.16278v2/drivemoe.png'),
'medical_imaging':dict(paperUrl='https://openaccess.thecvf.com/content/CVPR2026F/html/Zhang_Generative_Vision-Language_Multiple_Instance_Learning_for_Weakly_Supervised_Neonatal_Fundus_CVPRF_2026_paper.html',figure='Figure 2',sourceUrl='作者 CVIU-CSU/GVL-MIL 仓库 Framework 图',imageUrl='https://raw.githubusercontent.com/CVIU-CSU/GVL-MIL/main/assets/main_framework_01.png')}
out=[]
for order,p in enumerate(papers):
 id=p['id'];name,domain,tags,mood,colors,analysis,usage=spec[id];a=assets.get(id,extras.get(id))
 if id=='3d_reconstruction':p['title']='3D Gaussian Splatting for Arbitrary Resolutions with Compact Proxy Anchors'
 out.append(dict(id=id,order=order,name=name,title=p['title'],domain=domain,tags=tags,mood=mood,colors=colors.split(),analysis=analysis,usage=usage,image=f'assets/{id}.png',figure=a['figure'].split(' (')[0],venue='CVPR 2026 FINDINGS' if id=='medical_imaging' else 'CVPR 2026',paper=a['paperUrl'],sourceLabel='CVF · 原论文' if 'thecvf' in a['paperUrl'] else a['paperUrl'].split('/abs/')[-1],noteUrl=p['note'],provenance=a['sourceUrl'],imageSource=a.get('imageUrl',a['paperUrl']),note='图中示例照片与纹理未用作代表色。'+('此图来自作者项目展示版本，标题为 Exploration to Advanced Multimodal Generation。' if id=='image_generation' else '')))
(R/'dist/palettes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(f'Built {len(out)} palettes with {sum(len(x["colors"]) for x in out)} sampled colours.')
