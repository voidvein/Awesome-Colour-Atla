"""Explicit decisions following individual root-d image/palette inspection."""
import hashlib,json
from pathlib import Path
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from record_review import record_review

accepted={
1:('SPM参数/非参数模块、融合注意力与遗忘删除路径结构完整。','屏蔽两侧输入/输出实例照片；杏色非参数路径、蓝色参数路径、绿/灰注意力特征均来自实际图形模块。'),
2:('LLM并行验证、SLM自回归、阈值切换映射与候选token流完整。','蓝/橙分布柱和设备链路、灰色候选区、浅紫验证层等为算法语义编码，无照片取色。'),
3:('GHN、任务感知重排和PITH参数继承网络各子模型完整。','浅蓝网络、绿/黄预训练权重块和紫色编码器等均为有色模块填充。'),
4:('Prune2Drive层内剪枝、优化环路和token选择计算模块完整。','重新手采粉色剪枝节点、蓝色视觉token、深青边框和浅蓝优化区；不取矩阵数值热图或道路照片颜色。'),
5:('LLM故事推理、事件时间线/描述和多事件扩散生成网络流程完整。','屏蔽故事示例与输出音视频色谱；保留橙色LLM、蓝色阶段条、奶油扩散块、浅蓝时间线等设计色。'),
6:('质量感知patch权重、视觉编码器及两级聚合质量轴网络完整。','扩大照片/显著图排除区；浅蓝聚合、浅绿权重、奶油编码器、粉色轴特征与训练标记均可追踪。'),
7:('裁取Fig3完整中间PanoEnv-RL训练面板，含两阶段模型和GRPO策略更新循环；去左右基线/结果面板。','屏蔽训练回路内场景图片，排除表情图标黄；只保留训练面板底色、轨迹token分隔与阶段箭头灰。'),
8:('视觉编码器、随机mask与文本解码器形成实际预训练架构。','排除顶部猫照片；蓝色编码器/解码器、桃色文本条件与灰色mask tokens三种真实设计色。'),
9:('图像描述、角色判断、讽刺/荒诞对比和结果生成构成多阶段神经推理链。','输入插图完全屏蔽；绿/粉/紫/蓝推理节点及黄色理论分支背景为明确的阶段分色。'),
10:('粗到细自回归注意力mask和放大计算结构可见，非结果曲线。','淡紫图像token注意力、桃色放大区、蓝灰网格和粉色类别注意力均为掩码语义编码。'),
11:('图多模态编码、Mixer/Attention/MLP及结构感知提示和路由网络完整。','排除输入实景缩略图；绿/蓝FFN、黄AddNorm、粉色模态token及训练标志来自结构本身。'),
12:('地球系统编码器、策略/参考模型和GRPO优势计算路径完整。','屏蔽天气地图与输出数据图，进一步剔除残余地图蓝/灰；只留绿色模型节点、优势条及浅绿分区。'),
13:('UNet编码、SAFB注意力块和损失监督神经结构完整。','去掉所有组织/预测图紫色；手采黑色神经模块边框和红色损失箭头两色，明确保留其真实黑白加红强调设计。'),
15:('视觉动态压缩、dLDM和自回归Transformer训练/推理两阶段网络完整。','照片、潜变量可视化与生成实例不入色卡；仅保留浅紫分区、杏色dLDM/VDM模块与粉色离散latent tokens。'),
16:('低频Diffusion Transformer、高频pixel decoder和频率相关损失模块完整。','屏蔽噪声、输出图和DiT结果热图；保留杏色扩散、粉蓝解码器、黄色损失和绿色下采样模块。'),
17:('双DiT音视频路径、跨模态注意力、V2A/A2V对齐与动态mask模块完整。','屏蔽顶部频谱与视频帧；浅青/绿/蓝注意力模块、橙色与杏色条件/噪声token均来自结构编码。'),
18:('语义理解、密度估计、shape encoder与自回归Transformer骨架生成路径完整。','左右输入/输出几何可视化不取色；淡蓝Transformer、绿语义、黄色shape和不同token语义色保留。'),
19:('可供性/推理特征经实例匹配进入Match-to-match注意力与优化模块，结构完整。','屏蔽室内/人物视频与最终可供性热图；保留浅蓝注意力、粉色矩阵运算、浅绿匹配及奶油模块背景。'),
20:('双分支深度引导编码、depth decoder和mask/depth heads完整。','剔除输入照片与输出深度热图的紫黄红，仅保留真实浅绿编码器和浅青解码器两色。'),
21:('mask/image编码、残差量化code与两词重建的神经路径完整。','左侧树/街景图片排除；紫色量化器、蓝/灰编码器框及浅紫code tokens来自网络节点。'),
22:('多先验表征、OmR/fusion和融合block/component attention模块完整。','滤去低光照片、增强结果和特征热图颜色；只留FB灰紫、CWA杏色和两种黄色融合/调制区。'),
24:('CLIP语义/几何图构建、多层消息传递、FFN和异常评分网络完整。','输入和布局结果图排除，残余深蓝热图候选也剔除；保留绿语义、蓝几何、桃色评分等明确模块色。'),
25:('Expert模仿、Prior/Decoder预训练和Encoder后训练神经结构完整。','移除人体/椅子渲染色与边缘灰，只保留蓝色Prior/Decoder、洋红Expert、绿色Encoder三种真实节点色。'),
26:('SNN卷积、Transformer和tracking heads及下方细化模块完整。','输入事件/轨迹图不参与取色；黄主流程、绿卷积、蓝Transformer、桃色head及灰色组件底均为模块设计。'),
27:('深度/PE/vision/text编码、VLM、LoRA和PE decoder路径完整。','排除车辆照片；杏色文本、绿PE、蓝视觉、紫VLM、粉LoRA和灰色表示均为架构色。'),
29:('统一decoder-only多模态模型、双FFN和attention/QKV结构完整。','右侧生成猫与编辑实例全部排除；只保留模型主体蓝、桃和绿色FFN/输入token填色。'),
31:('Global/Scene/Segment/Entity层次记忆与推理LLM观察调用构成实际Agent架构。','视频截图排除；桃色LLM、绿场景、藕紫实体，以及显式实体/时间词语编码色来自结构标注。'),
32:('LLCC、HARM和视觉增强解码的Detect-Mitigate神经计算框架完整。','实景照片和注意力热图区域排除；淡紫模块、杏色目标识别、黄色检测强调和绿色最终输出等语义色保留。'),
33:('多头attention+MoE与CME-MoE扩展、元专家和自扩展原型分类器完整。','黄CME、紫SEPC、青色元优化、桃/粉专家及训练/阈值强调均为网络机制的实际色标。'),
35:('VLM自适应观察、工具token/answer token、bbox工具与多分辨率视觉输入路径完整。','排除低分辨率照片；绿VLM、紫工具、蓝tool/visual token、粉answer token和杏色question为模型语义色。'),
36:('从Fig4数据整理换为Fig1，其中(b)明确显示Vision Encoder→Projector→Language Model及视觉/语言token路径。','仅从(b)模型区采色，排除婴幼儿照片与右侧benchmark图；蓝视觉、桃投影、奶油LM、绿token与绿色背景均可追踪。'),
}
rejected={
14:('查看缓存原文所有方法候选：RKPM粒子、弹性特征分析与降阶数值模拟，不是神经网络/神经模块。','原色主要来自数值仿真物体渲染；不以其红蓝渲染色代替网络配色。'),
23:('查看原文方法/其他图：DCT、低通和阈值的传统感知哈希流程，无神经模块，其他为数据错误实例。','候选七色全来自卫星照片；拒绝，未以黑线或白纸凑色。'),
28:('本地PDF逐图候选核对：Fig2为数据规模/训练时长阶段概览和任务例子，其他为性能、数据组成与定性结果，无具体神经架构。','主要颜色来自医学照片/插图，不符合网络结构配色来源。'),
30:('补取并查看原始PDF：Fig1仅任务能力示例，Fig3为训练数据饼图，Fig4为RL优势公式比较，余图为案例/成绩，无可用网络结构图。','未以数据饼图或任务实例背景替代架构配色。'),
34:('查看原文所有候选：GeoCodeBench数据构建/单元测试/模型评测流程，没有所提出神经架构或明确神经计算模块。','候选色来自会议logo、代码示例与测试标记，不能用来凑网络架构色卡。'),
}
packet=json.loads((WORK/'contacts/root-d/packet.json').read_text(encoding='utf8'));counts={}
for i,item in enumerate(packet,1):
 r=json.loads((RECORDS/(item['id']+'.json')).read_text(encoding='utf8'));e=r['extraction']
 verdict='accepted' if i in accepted else 'rejected';reason,observation=(accepted if i in accepted else rejected)[i]
 if verdict=='accepted':
  for key in ['paper','sourceType','sourceTitle','imageSHA256']:assert e.get(key),(i,key)
  assert e.get('source_url') or e.get('image_url'),i
  im=Image.open(e['image']).convert('RGB');assert 2<=len(e['colors'])<=8
  assert e['imageSHA256']==hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
  for point in e['colorEvidence']:assert im.getpixel(tuple(point['sampleXY']))==tuple(point['rgb']),(i,point)
 review=record_review(item['id'],verdict,reason,reviewer='figure_extractor/root-d',palette_observation=observation,exclude_regions=e.get('excludedRegions'))
 counts[verdict]=counts.get(verdict,0)+1
 print(i,item['id'],verdict,flush=True)
atomic_json(WORK/'contacts/root-d/review-summary.json',counts)
print(counts)
