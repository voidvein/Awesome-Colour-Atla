"""Per-paper decisions after actual audit-g original/contact pixel inspection."""
import hashlib,json
from pathlib import Path
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from record_review import record_review
accepted={
1:('Backbone/Adapter、带吸引排斥约束的表征空间与密度检测路径完整。','唇部照片和高斯密度伪彩图不采色；灰色Backbone、红色损失/聚类与绿蓝语义簇线条来自架构编码。'),
2:('多帧scene-flow网络φG及运动候选、投票聚合计算结构完整。','屏蔽/剔除点云、输出场景流与训练火焰；保留候选生成浅蓝底、灰色候选运动几何和粉色投票矩阵。'),
3:('基因/蛋白/病理特征、图卷积、超图学习和生存预测神经结构完整。','组织照片不采色；青色基因/GCN、浅蓝蛋白、紫色超图、奶油预测和粉色特征为真实模块填色。'),
5:('DINOv2骨干、非对称几何聚合和归一化特征模块完整。','街景/特征相似度图不入色卡；灰色特征token、粉色全局投影、桃色projection、青色加权与黄色归一化向量保留。'),
6:('Fig11展示真实实时推理模块：独立解码、条件更新、主去噪自/交叉注意力与线程队列。','观察照片排除；奶油线程/去噪区、灰色conditioner及蓝色队列/特征token均来自模块本身。'),
8:('Anchor Predictor、CNN、Gaussian Decoder MLP与Gaussian Refiner注意力结构完整。','输入/几何渲染不采色；奶油refiner区、黄色全局/串行注意力、绿色CNN/MLP及浅绿decoder背景来自架构。'),
9:('Holistic token embedding、自回归Transformer、交叉注意力和detokenize路径完整。','两侧B-rep实体渲染排除，进一步去残余灰色渲染；粉蓝层、粉色范数、黄色前馈及绿/桃/蓝类型token为语义配色。'),
11:('Point Encoder、Mask Transformer、姿态与形状双Decoder架构完整。','两端碎片/恢复物体和灰色结果箭头不入色卡；黄姿态、绿形状、蓝mask transformer、桃encoder及红色token保留。'),
12:('GS-CLIP几何prompt、几何蒸馏和协同视图细化双阶段结构完整。','点云、渲染图、深度图和分割结果不采色；蓝image encoder、青PointNet、紫蒸馏、金色细化和粉色特征均为模块色。'),
13:('ViT编码块、位置/patch嵌入、query fusion和track queries路径完整。','上下鸟类帧照片不采色；浅桃Transformer区域、橙色神经层边框、浅蓝query token和桃色编码块来自原结构。'),
14:('Flickerformer中AFFN、频率PFM和方向WDAM三模块及卷积/采样路径完整。','两张输入/输出照片排除；奶油PFM、蓝AFFN、粉WDAM、青PSF及灰色卷积/下采样均为结构模块。'),
15:('APEX中MLLM/Grounded SAM、地图更新与异步三阶段模块完整，裁掉下方正文解释。','场景照片和体积热图不取色；只留地图更新浅蓝、目标grounding浅绿、行动决策粉色三个阶段色。'),
16:('UniLS自回归Self/Cross Attention、FFN及LoRA的两阶段音频驱动网络完整。','人脸照片、输出头模渲染排除；桃色cross attention、浅蓝style embedding、灰色self attention和浅黄绿FFN是真实模块。'),
17:('SoccerMaster左侧Spatial/Temporal Transformer与MAP Head神经结构完整。','全幅右侧任务截图和输入球场图片全部屏蔽；粉/紫语义token、Transformer块和蓝灰阶段填色来自左侧实际架构。'),
18:('附录Fig35含Qwen-VL decoder、视觉投影/编码器、文本嵌入与LoRA的明确神经架构。','视频与评分卡不采色；仅红色Qwen decoder、青色视觉模块、黄色文本嵌入三色。'),
19:('保留Fig4三阶段SFT、Policy/Reference模型和GRPO训练结构，去掉上方误含的性能表。','取色来自任务/阶段分区：浅蓝SFT任务、奶油QA、桃色Grounding/Counting和浅粉全任务RL；火焰/雪花装饰未采。'),
20:('Refer-Agent含帧选择、意图分析、目标grounding、mask生成与双阶段反思Agent系统。','视频截图及示例帧排除；桃色reflection、绿/蓝反思节点与黄色意图区域为实际阶段色。'),
21:('EagleVision多模态LLM、SPF-DPP采样、BEV描述和零样本RL架构完整。','摄影视图、场景地图和拼接图不采色；桃色MLLM、浅蓝SPF-DPP、蓝/桃/绿视觉token及紫色answer区来自结构编码。'),
22:('自动构造锚点提示并输入MLRM的神经推理攻击机制框架完整，图内文字仅作为论文证据。','蓝色意图分类、绿安全锚、粉色有害意图及黄/青阶段连接均为结构语义编码，没有照片色。'),
23:('Fig6展示MCoT模型→视觉熵识别→推理干预的明确神经推理机制。','照片和紫黄色熵热图全部剔除；只留橙/蓝候选答案语义节点及深蓝模型框线。'),
24:('可训练latent经映射MLP更新大网络权重的计算图完整。','图无照片/性能图；浅蓝大网络、浅绿mapping和蓝灰立体侧面为三种真实模块色。'),
25:('UniComp的ViT/MLP、帧组融合、token allocation和动态压缩到LLM路径完整。','底部原始帧与右侧照片token示例不入色卡；蓝神经层、粉/绿/桃语义token与融合分支保留。'),
26:('病理特征encoder、MLP、cell-type加权prototype与模态校正神经结构完整。','组织和基因结果柱图不取色；手采灰色神经特征块、青色prototype矩阵线、橙红学习权重矩阵线，未把浅色抗锯齿当独立色。'),
27:('UniPixie网格编码、交叉/查询/自注意力和Flow Matching Decoder以及共享编码器完整。','输入物体和右侧物理仿真不采色；浅蓝decoder、蓝注意力、深蓝投影/模型线、棕色共享encoder与米色CLIP特征模块保留。'),
28:('原Fig9明确含VFN、FEB残差、FRB池化/门控/卷积融合网络，结构完整。','两端照片排除；青模块、紫卷积、黄激活、桃linear、浅紫池化、深青门控和浅黄绿归一化均有原图图例对应。'),
29:('改选Fig3，明确显示policy/reference neural models、verifiable reward、GRPO和策略更新回路。','所有上方数据构建照片/深度图排除；手采桃色policy、淡紫reference/GRPO、浅蓝奖励模块及棕色策略反馈线。'),
30:('由能力示例Fig1改为Fig2，Chorus 3D encoder经projector对齐PE/DINO/SigLIP教师并计算多教师loss。','场景渲染、embedding点云和右侧下游结果全排除；仅米色教师、蓝/绿教师token、桃色Chorus编码器及青色loss/projector色。'),
31:('真实DINO特征、frame/global聚合器、稀疏注意力token和MLP/DPT输出头架构完整。','左侧多视图照片完全屏蔽；浅蓝全局、奶油frame、绿/粉视图token、暗红register token和灰色head来自结构。'),
32:('图文编码器、数量嵌入、SPS/CAD与projection/upsampling神经计算结构完整。','水果输入、相似度/密度热图及空间聚合结果不采色；浅蓝编码器、粉色文本/聚合、浅绿语义token及蓝灰投影为实际色。'),
33:('PCA-Seg双编码器、并行聚合、ME parser专家与decoder结构完整。','输入照片/分割预测紫绿颜色排除；奶油聚合、蓝灰encoder、绿空间/频率操作、桃/紫专家与浅蓝parser色来自模块。'),
34:('UniLDiff双流特征融合、去噪UNet、退化专家路由与VAE decoder神经结构完整。','鹦鹉照片、噪声/latent小图和恢复结果不采色；紫色融合/专家、蓝文本encoder、粉linear与桃退化prompt保留。'),
35:('保留GeoMMAgent工具库、计划/多Agent执行和反思的实际神经Agent系统，而非benchmark统计图。','遥感示例/查询图屏蔽；奶油规划、蓝执行、桃工具、粉工具库和浅米角色区为真实结构阶段色。'),
36:('DoorMan包含Teacher Policy PPO→Student DAgger→Student GRPO的神经策略迁移与观测连接。','两张视觉观测/门场景及环境图标不取色；只保留灰色teacher/student策略模块和浅绿色最终student阶段两色。'),
37:('由数据集/性能概览改为Fig2(a)中LLM Judge→奖励归一化→MedGRPO训练的神经训练机制。','医学帧、分数矩阵和归一化性能曲线均不采色；只手采浅蓝任务区、桃色训练模块与深青Judge/训练模块框线。'),
38:('VOLD教师/学生SFT、GRPO、on-policy distillation和图像推理模型架构完整。','图中无自然图像取色；奶油推理阶段、紫GRPO/蒸馏、棕学生、绿色teacher/student与浅绿对齐阶段为真实模块填色。'),
39:('Symphony含planning/grounding/reflection多个神经Agent及阶段信息交互。','顶端视频和局部帧缩略图全部排除；浅蓝reflection、奶油plan、浅绿grounding与浅青任务区为Agent背景色，去logo蓝/图标深灰。'),
40:('当前/参考policy、采样/奖励/advantage、KL约束和RL优化计算结构完整。','手写样例只作任务示例不采色；灰旧policy、绿候选、蓝surrogate、黄logits、青KL/ratio、粉advantage和绿正则色均可追溯。'),
41:('长度泛化V2A模型的chunk/dechunk、多模态/单模态块和时序/多模态路由结构完整。','图无自然图片或性能图；粉网络区、蓝多模态块、桃单模态块、黄输出、橙频率/时序token与绿色路由语义色保留。'),
42:('VLM推理轨迹、证据池、supervisor和visual decider的推理反馈结构完整。','照片未参与；绿正确推理块、粉错误推理块、蓝框/兴趣区、灰原图节点与黄监督/步骤标志均为语义编码。'),
45:('Pixel2Phys中Plan/Variable/Equation/Experiment四类神经Agent交互与内部工具计算架构完整。','示例动力图和灰工具图标不入色卡；黄变量Agent、蓝实验Agent、绿方程Agent、桃规划Agent与浅绿节点背景来自结构。'),
46:('Fig8详细显示compact NN内FFN、AdaLN、自注意力、QKV及latent/token输入输出。','此图没有照片/数值热图；粉模块区、灰mask以及黄/蓝/紫/绿离散类别token均为设计的符号配色。'),
47:('多模态图、GraphSAGE、CNDA跨节点双注意力和CNAP pooling神经结构完整。','组织图、下游表达结果和矩阵数值蓝不入色卡；桃CNDA、青CNAP、黄graph、紫共享/私有网络分区与粉target行色保留。'),
48:('NAF编码器、2D-RoPE、pool和cross-scale neighborhood attention结构完整。','水果和右侧/底部特征热图全排除；仅青色无参数模块、桃色可训练encoder和浅绿注意力外框三种真实架构色。'),
49:('由图像概览改为Fig3，ControlNet与四个FFN/cross/self-attention主块、projector/LoRA结构完整。','此图无照片；紫preceding tokens/框、绿reference、黄text token、蓝noisy target及红/橙训练状态符号均来自原图语义图例。'),
50:('ART Transformer、hexaplane/property decoder和part slot/geometry输出连接完整。','木制实体渲染与左下原始多视图不取色；蓝Transformer、紫hexaplane、黄patchify、桃part tokens、奶油properties decoder与浅粉slot tokens保留。'),
51:('由teaser改选Fig2，真实VAE Encoder、Video Model、SDS梯度与4D表示正则化训练架构完整。','人物/桌子渲染、noise示例不取色；只留黄色VAE/VideoModel、粉色时空平滑正则和浅米输入节点三色。'),
52:('CLIPoint3D含prompt、text/image encoder、源/目标点云编码和prototype迁移的网络架构完整。','椅子/实体渲染及源prototype照片不采色；奶油模块、桃prompt/token、紫image encoder、黄损失、红text encoder与蓝point encoder来自结构。'),
53:('Fig3右侧明确画出冻结预训练stereo神经模型和带可训练适配器的目标网络，属神经模块迁移架构。','仅两种实色：红色为预训练/适配后的stereo网络主体，橙色为可训练适配器；左侧数据工厂照片、事件图、全部深度输出色带均未采色。'),
54:('MissingPointViT含Point Encoder、Linear Projection、Transformer Encoder和MLP Head网络结构完整。','滑雪照片和底部图像patch排除；蓝Transformer、浅绿MLP、青Point Encoder和蓝灰Linear Projection四种真实节点色。'),
}
rejected={
4:('逐图查看本地原文：可微光线追踪、透镜删除、光学成像和传统ISP流程，没有神经网络或明确神经模块。','候选颜色来自射线/PSF与光学参数，不作为网络架构配色。'),
7:('逐图查看本地PDF：主方法图是RoPE相位曲线、注意力经验热图和延长视频结果，没有可用神经模块结构图。','候选色来自注意力数值热图与性能/相位图，拒绝以其代替架构配色。'),
10:('查看原图/图注：差分渲染、概率物理形状/法向/纹理估计与结构光采样优化，未显示神经网络模块。','主要是结构光掩码和物理估计结果；即使有彩色优化框也不计作神经架构。'),
43:('查看原文图候选：训练视觉饮食的饱和度/模糊/连续性数据增广，仅列off-the-shelf模型，未画神经架构。','颜色来自样例照片和数据增广标志，不能拿来凑网络色卡。'),
44:('检查原文方法候选：非一致性得分近邻匹配、分位数和统计校准流程，当前候选还是性能散点图；无神经结构。','当前橙蓝来自性能曲线，不是网络模块色。'),
}
items=json.loads((WORK/'contacts/audit-g/packet.json').read_text(encoding='utf8'));counts={};details=[]
assert set(accepted)|set(rejected)==set(range(1,55))
for i,item in enumerate(items,1):
 r=json.loads((RECORDS/(item['id']+'.json')).read_text(encoding='utf8'));e=r['extraction'];verdict='accepted' if i in accepted else 'rejected';reason,observation=(accepted if i in accepted else rejected)[i]
 if verdict=='accepted':
  for key in ['paper','sourceType','sourceTitle','imageSHA256']:assert e.get(key),(i,key)
  assert e.get('source_url') or e.get('image_url'),i
  im=Image.open(e['image']).convert('RGB');assert 2<=len(e['colors'])<=8
  assert [x['hex'] for x in e['colorEvidence']]==e['colors'],i
  assert e['imageSHA256']==hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
  for x in e['colorEvidence']:assert im.getpixel(tuple(x['sampleXY']))==tuple(x['rgb']),(i,x)
 review=record_review(item['id'],verdict,reason,reviewer='figure_extractor/audit-g',palette_observation=observation,exclude_regions=e.get('excludedRegions'))
 counts[verdict]=counts.get(verdict,0)+1;details.append({'index':i,'id':item['id'],'verdict':verdict,'figure':e.get('figure'),'colors':e['colors']});print(i,item['id'],verdict,flush=True)
atomic_json(WORK/'contacts/audit-g/review-summary.json',{'counts':counts,'decisions':details});print(counts)
