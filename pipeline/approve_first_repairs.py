"""Record the explicitly inspected first-packet decisions, bound to current image hashes."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from collect_batch import ROOT,WORK,RECORDS,atomic_json
from record_review import record_review
from extract_figures import make_contact_sheet

observations={
'cvpr26-8ea2ffc84c58':('完整的RoPE/KV-cache神经计算机制图，两组缓存结构和时间坐标均保留；不是用户研究界面。','四种实际token填色：浅绿、亮绿、中绿、浅青；未添加虚构第五色。'),
'cvpr26-012c5a980a26':('完整的3D-Fixer编码器/补全器/解码器及粗到细纹理路径，保留原版数据区但采色排除。','蓝色补全模块、浅紫/紫色编解码器、浅蓝底色和绿色几何表示；排除上方示例照片、右侧数据集面板与残留背景边。'),
'cvpr26-39c79b6b46e1':('更换为完整SMS-Net模型Fig3，图例与两端输入输出完整，无前一段正文。','模块浅绿、橄榄、棕色、蓝灰与灰色立方体；排除右侧彩色视差/深度输出图，不取紫黄热图颜色。'),
'cvpr26-cc3d6f737359':('跨栏Fig5完整保留检测、物体生成、迭代细化，以及score/segmentation/pose输出。','青绿分区、藕粉功能节点、蓝色细化路径和渐变分区；每色来自实际图中模块像素。'),
'cvpr26-c6b54c86d8be':('完整SAM3D编码器、跨注意力手/身解码器、特征/姿态token图，保留输入与网格输出。','扩大左侧照片排除区，去掉照片蓝边；保留浅绿解码器、奶油编码器、灰/绿token和粉/蓝prompt token。'),
'cvpr26-c58926db1673':('真正的VLM-3R Fig3，第5页；LLM、视觉/空间编码器、融合路径及底部标签完整。','浅绿LLM、棕色视觉编码器、橄榄空间编码器、深蓝边框和中性色；排除单目视频实景条。'),
'cvpr26-1cf488782e68':('改选Fig2完整推理与训练流程，比带奖励柱图的Fig3更贴合主流程检索；无裁断。','直接依图例取六色：灰色思考上下文、蓝色工具、杏色编辑图像、粉色自评、淡紫反思与深青框线；逐个精确像素核对。'),
'cvpr26-41ffb66d6727':('VISTA图包含工具集合、VISTA-Gym与VLM Agent交互回路及动作/观察/奖励策略更新，属于Agent训练架构。','排除左侧问答示例区；蓝色工具区与token、黄色问题标记、红绿反馈和浅绿成功反馈均为图中语义编码。'),
'cvpr26-f6fefeca849e':('换为SafeGRPO Fig2实际训练/奖励构造流程，而非Fig3数据集统计饼图。','仅取训练侧策略输出节点：浅蓝文档token填色、深灰蓝框线、橙色Policy Outputs标签；排除左侧饼图、照片、人物插画及背景纹理。'),
'cvpr26-bf8daf9a666b':('完整Watch-and-Learn Fig2包含IDM模型和多阶段训练/推理流程，原始流程图保留。','只取神经模型块棕色Transformer/动作头和灰色SigLIP2编码器；手工核对灰色模块104812精确像素，排除界面截图与prompt薄边。'),
'cvpr26-7b3f387a7ee9':('STC整体模型图保留LLM、STC-Pruner、STC-Cacher与各层token路径和视频输入。','排除底部泳池视频照片；奶油、蓝灰、杏粉、薄荷、浅绿等来自模型模块及真实token填色。'),
'cvpr26-4576aaa90a87':('Franca图左侧包含嵌套投影、聚类头和多尺度聚类损失，方法结构完整保留。','采色仅左侧方法区，排除右侧数据气泡与结果散点；保留浅蓝聚类头、粉紫编码器和不同簇点颜色。'),
}

def manual_palette(e, specifications, method):
 a=np.asarray(Image.open(e['image']).convert('RGB'));evidence=[]
 for rgb,role,roi in specifications:
  x0,y0,x1,y1=roi;patch=a[y0:y1,x0:x1];ys,xs=np.where(np.all(patch==rgb,axis=2));assert len(ys),role
  color='#%02X%02X%02X'%tuple(rgb)
  evidence.append({'hex':color,'rgb':rgb,'sampleXY':[int(xs[0]+x0),int(ys[0]+y0)],'exactSamples':len(ys),'sampleRegion':roi,'manualRole':role,'neutral':max(rgb)-min(rgb)<12})
 e['colors']=[x['hex'] for x in evidence];e['colorEvidence']=evidence;e['method']=method;e['paletteStatus']='needs_visual_review'

reviewed=[]
for id,(reason,observation) in observations.items():
 p=RECORDS/f'{id}.json';r=json.loads(p.read_text(encoding='utf8'));e=r['extraction']
 if id=='cvpr26-012c5a980a26':
  e['colors']=[c for c in e['colors'] if c!='#FDF0E6'];e['colorEvidence']=[c for c in e['colorEvidence'] if c['hex']!='#FDF0E6']
 if id=='cvpr26-1cf488782e68':
  manual_palette(e,[([126,126,126],'Think context',[50,120,90,140]),([220,234,247],'Editing tools',[50,145,90,165]),([251,227,214],'Edited image',[50,178,90,193]),([243,202,199],'Self-evaluation',[50,208,90,222]),([228,231,250],'Self-reflection',[50,235,90,249]),([21,96,130],'Module frame',[0,0,834,528])],'Manual semantic legend/frame samples, each traced to exact source RGB pixels.')
 if id=='cvpr26-f6fefeca849e':
  manual_palette(e,[([234,242,255],'Policy rollout document token fill',[1050,190,1500,345]),([80,88,104],'Policy output module outline',[1050,190,1500,345]),([228,108,11],'Policy Outputs Rollouts label',[1050,190,1500,345])],'Manual policy-output-node samples; photos, pie chart, illustrations and background excluded.')
 a=Image.open(e['image']).convert('RGB')
 assert 2<=len(e['colors'])<=8
 for ev in e['colorEvidence']:assert a.getpixel(tuple(ev['sampleXY']))==tuple(ev['rgb'])
 assert e['imageSHA256']==hashlib.sha256(Path(e['image']).read_bytes()).hexdigest()
 r['extraction']=e;atomic_json(p,r)
 review=record_review(id,'accepted',reason,reviewer='figure_extractor',palette_observation=observation,exclude_regions=e.get('excludedRegions'))
 reviewed.append(dict(e,id=id,title=r['title']))
out=WORK/'contacts/first-approved';out.mkdir(exist_ok=True)
atomic_json(out/'packet.json',reviewed)
for i in range(0,len(reviewed),4):make_contact_sheet(reviewed[i:i+4],out/f'contact-{i//4+1:02d}.png',columns=2,thumb_size=(1000,500))
print('Accepted',len(reviewed),'individually inspected first-packet figures with exact-pixel palette evidence; existing accepted/rejected records untouched.')
