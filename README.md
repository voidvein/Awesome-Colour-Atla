# Colour Atlas

首批 10 张来自 Paper Notes CVPR 2026 索引的论文架构图配色色卡。静态网站位于 `dist/`。

## 在线访问与部署

网站：[Colour Atlas](https://voidvein.github.io/Awesome-Colour-Atla/)

使用 GitHub Pages 和 GitHub Actions 部署。`.github/workflows/pages.yml` 检查前端脚本、10 张色卡数据及其图片，然后仅发布 `dist/`。推送到 `main` 的页面更新自动触发部署，也可在 Actions 页面手动运行。GitHub 仓库的 Settings → Pages → Source 需选择 GitHub Actions。

点赞仍为当前浏览器保存的预览记录，不是跨用户统一榜单；GitHub Pages 提供静态页面托管。

## 本地预览

```sh
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:4173/ 。需要通过 HTTP 打开，以加载配色 JSON。

## 功能和范围

- 10 篇、10 个领域，原版架构图和每篇原论文/解读来源。
- 领域筛选、标签检索、全文关键词搜索、原图放大和配色观察。
- 单色或整组 HEX 复制、JSON 导出。
- 当前浏览器的点赞/取消点赞、刷新后保留、按点赞降序排序。同票按收录顺序排列。
- 此次是效果预览：没有全站点赞数据库，每张初始 0 赞；不展示虚构热度。

## 内容与溯源

`dist/palettes.json` 是完整前端数据。`research/assets-a.json` 记录五篇作者项目/arXiv 原图的下载和核验信息，其余来源写在每张色卡中。`build_palettes.py` 生成配色数据。

采色定位模块填色、边框和 token 色，统计原始像素中的代表颜色，再目视校对；排除白背景、无意义抗锯齿、示例照片和噪声。允许灰色等有意义中性色。色块等宽显示，不代表面积比例。TESSERA 的渐变色使用模块中部的代表取样。首批共 64 个色值。

医学图像论文属于 **CVPR 2026 Findings**。OmniGen2 使用作者项目页展示的早期架构版本，其图源标题与索引中的新版标题分别保留在溯源记录及卡片说明中。

原始图像归论文作者/权利人所有，使用或再分发请遵守来源的许可要求；此项目的配色分析属于编辑性解读，不是论文作者的设计声明。

## 检查

```sh
python validate.py
node --check dist/app.js
```

## 后续上线

若需要多用户统一点赞榜，需增加服务端数据库、身份或匿名访客标识、幂等点赞 API 与滥用限制；不要把浏览器点赞统计当成全站榜单。
