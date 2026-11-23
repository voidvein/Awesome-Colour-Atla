"""Explicit audit-m per-paper architecture and actual-pixel review decisions."""
import hashlib,json
from pathlib import Path
from PIL import Image
from collect_batch import WORK,RECORDS,atomic_json
from record_review import record_review
accepted={
1:('将应用概念Fig1改为Fig2，含ID encoder/MLP、VID sampler、Stable Diffusion、VAE及水印编码/解码网络。','人脸、normal map、噪声和人体头模不入色卡；浅蓝神经encoder/SD、桃sampler、紫3D modeling、黄watermark decoder、绿signature encoder与蓝特征token来自模块。'),
2:('视觉编码、learned Compressor、LLM与演化标签训练/推理结构完整。','顶部输入照片和小型输出曲线区域排除；粉色LLM/encoder、绿色compressor、蓝红保留/丢弃标签及紫system token均为真实神经/语义编码。'),
3:('TAPE的音频encoder、Task Adapter、prototype更新和few-shot分类神经机制完整。','原始音频波形展示不采色；桃task adapter、蓝特征/预测token、黄prototype、红相关点和橙演化箭头为实际语义配色。'),
4:('TALON encoder blocks、projector与prototype在线更新/类别发现结构完整。','鸟照片底部曾残留一像素行，已扩大遮罩并删除棕色照片候选；仅保留桃encoder、蓝prototype/embedding、绿类别token和蓝灰分隔的真实模块色。'),
5:('图中明确包含SVTRv2 Encoder→AR Decoder以及迭代伪标签/重采样的神经识别模型结构。','文字/街景/合成样例照片不入色卡；蓝encoder、桃AR decoder、浅蓝框架背景和蓝框线四色来自实际模型/阶段区域。'),
7:('VIVA含LLaVA tokenizer/vision encoder、VAE、projector与DiT的指令视频编辑神经架构。','输入/参考/编辑后照片全部排除；仅浅绿projector/DiT、浅蓝VLM与桃VAE三种神经模块色。'),
8:('FlashMesh的Hourglass Transformer、cache和draft/verify structured speculation模块完整。','图无自然照片或性能曲线；奶油采样/并行区、淡紫Transformer、黄上/下采样、粉LH和不同token类型色均有实际模块/图例对应。'),
9:('Point Feature Encoder与edge regression主网络及GREO cost/advantage/loss计算模块完整。','上方点云/重建几何和下方线框示例不采色；只留浅紫geometry参数区、蓝GREO损失与浅绿confidence编码，未取pairwise cost数值色块。'),
10:('EfficientVPR的prompt骨干、MsLA、OLE与SGFS多头注意力/正交融合网络结构完整。','街景输入完全排除；蓝骨干/注意力、黄orthogonal fusion、灰conv/reshape与绿色LayerNorm/FC均为模块色。'),
11:('3M-TI双encoder、latent-prompt diffusion、CSM跨模态自注意力及QKV结构完整。','全部RGB/thermal输入输出及增强示例屏蔽；浅蓝ZeroConv、紫CSM、绿encoder/decoder、黄LoRA、灰latent、桃token和粉augmentation阶段来自结构。'),
12:('GDPO-SR包含Policy/Reference ISR、归因奖励、group advantage和GDPO loss的神经训练架构。','花照片、SR样本和噪声全部排除，训练火焰/雪花图标色不采；只留蓝冻结model、桃可训练model和奶油loss/advantage计算区三色。'),
13:('Fig5含双encoder、CVMF跨视角多特征融合及训练目标完整模型架构。','道路/卫星/定位照片全部排除；浅绿训练区、桃backbone、蓝CVMF和蓝one-hot encoding为实际模块/语义填色。'),
14:('Interact2Ar展示motion encoder、自/交叉注意力、specific heads与扩散迭代神经结构。','全部人体渲染屏蔽；手采灰色cross-attention/head模块，以及模型内部两种运动流的橙/青交叉注意力连接线，未取人体皮肤/衣物色。'),
16:('ColaVLA含Driving Scene Perceiver、Ego-Adaptive Router、Latent Rethinker、Strategy Classifier及并行Planner。','图无自然照片；蓝场景/query、绿认知模块、桃meta/ego query、紫time/meta bank和深青边框均来自实际神经模块/类别token。'),
17:('SocialNav Brain、text/vision/waypoint encoder、AR head与Action Expert/SAFE-GRPO路径完整。','导航截图与advantage表的数值色不采；手补浅紫SocialNav Brain模块主体，保留桃waypoint encoder、蓝action token/专家和绿合规奖励字段。'),
18:('OralGPT-Plus的instruction tuning、工具调用、RL模型和hybrid reward→scores/advantages神经训练系统完整。','X-ray和zoom/mirror结果全部排除，红色品牌logo/装饰蓝紫也剔除；仅粉色训练/奖励区域与淡紫reward-score token两种真实结构色。'),
19:('Geoint-R1包含LLM采样分类、辅助构造SFT和verifier/GRPO强化学习的神经训练机制。','几何问题缩略图不作配色；浅蓝SFT、浅绿RL/训练阶段与红/绿/蓝难度课程块均为结构语义色，去冗余箭头和图标黄绿。'),
20:('iSHIFT含多模态LLM慢/快路径、自适应感知DINO+cross attention以及隐状态/工具token结构。','两端GUI手机截图完全排除；青感知模块、灰LLM、橙感知图像token与蓝/紫工具和latent状态均来自真实架构。'),
21:('动态重加权OOD网络显示共享feature encoder、closed-set分类head与OOD detection head连接完整。','输入照片、transport cost热图及结果散点图不采；仅棕/蓝两个特征encoder分支和浅蓝OOD head三种神经模块色。'),
22:('MAD的音视频语言模型、模态query logits/权重提取、自适应解码与softmax响应路径完整。','视频帧不采色；奶油AVLM、浅蓝generation、青logit和蓝/粉步骤箭头、浅绿response是实际神经计算模块的语义色。'),
23:('Visual encoder、Policy decoder、Cross-Attention和两个持续Critic的神经结构及加权TD损失完整。','两张驾驶截图全部排除并去灰色图片/抗锯齿候选；蓝视觉encoder、绿policy、紫attention、橙Critic、红TD loss和浅蓝latent区来自模块框线/填色。'),
24:('将照片teaser Fig1换成Fig2，明确显示冻结feature extractor、可训练translator、CLIP/UnCLIP和等价特征投影神经机制。','鱼、海星、汽车照片全部屏蔽；深青feature/translator、绿CLIP、粉推理区、深蓝projector、蓝灰网络主体及紫/桃语义特征token均为模块色。'),
25:('4D-RGPT的teacher 4D encoder/decoder、学生视觉/时间encoder、LLM及latent/explicit distillation架构完整。','视频帧和depth/flow输出色图全部排除；粉紫蒸馏区、绿embedding、蓝encoder、紫latent tokens、粉LLM及红trainable状态标记来自原神经结构。'),
26:('VFM-VAE含冻结ViT、projection、多尺度空间latent、disentangler及modulated ConvNeXt decoder结构完整。','猫输入照片排除；蓝VFM、绿/黄/桃多尺度decoder blocks、浅蓝网络底和蓝灰ConvNeXt/Disentangler等真实模块色保留。'),
27:('Complet4R包含frame/global attention、聚合/图像token以及camera/depth/aggregation heads完整网络。','左视频与右重建结果全部排除；只留绿/橙/紫不同时间图像token和粉agg token四种真实语义色，不使用重建场景棕色。'),
}
rejected={
6:('检查缓存PDF全部图候选：CompBench只展示数据收集/掩码预处理、任务分类和benchmark结果，没有明确神经架构。','候选色来自样例图/标志/数据处理区，不以benchmark数据生产流程替代网络架构。'),
15:('检查缓存PDF全部图：GIFT为query relevance×directed diversity及预算迭代选帧，之后仅接通用VLM应用框，无明确神经架构或神经计算模块。','候选绿/蓝来自传统选帧阶段、红色散点和视频示例；不以普通预处理/性能图凑网络架构色卡。'),
}
items=json.loads((WORK/'contacts/audit-m/packet.json').read_text(encoding='utf8'));assert set(accepted)|set(rejected)==set(range(1,28));counts={};details=[]
for i,item in enumerate(items,1):
 r=json.loads((RECORDS/(item['id']+'.json')).read_text(encoding='utf8'));e=r['extraction'];verdict='accepted' if i in accepted else 'rejected';reason,observation=(accepted if i in accepted else rejected)[i]
 if verdict=='accepted':
  for key in ['paper','sourceType','sourceTitle','imageSHA256']:assert e.get(key),(i,key)
  assert e.get('source_url') or e.get('image_url'),i;assert 2<=len(e['colors'])<=8
  assert e['imageSHA256']==hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 review=record_review(item['id'],verdict,reason,reviewer='figure_extractor/audit-m',palette_observation=observation,exclude_regions=e.get('excludedRegions'))
 counts[verdict]=counts.get(verdict,0)+1;details.append({'index':i,'id':item['id'],'verdict':verdict,'figure':e.get('figure'),'colors':e['colors']});print(i,item['id'],verdict,flush=True)
atomic_json(WORK/'contacts/audit-m/review-summary.json',{'counts':counts,'decisions':details});print(counts)
