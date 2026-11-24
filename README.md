# Colour Atlas

来自 Paper Notes [CVPR 2026](https://papernotes.org/CVPR2026/) 与 [NeurIPS 2026](https://papernotes.org/NeurIPS2026/) 的论文架构图配色色卡。静态网站位于 `dist/`。

## 在线访问与部署

网站：[Colour Atlas](https://voidvein.github.io/Awesome-Colour-Atla/)

使用 GitHub Pages 和 GitHub Actions 部署。`.github/workflows/pages.yml` 恢复图片与审核记录，根据发布清单检查完整的已审核色卡、全部大图与缩略图、来源及审核哈希，并验证前端检索、分页、点赞和导出，然后发布 `dist/`。推送到 `main` 的页面更新自动触发部署，也可在 Actions 页面手动运行。GitHub 仓库的 Settings → Pages → Source 需选择 GitHub Actions。

点赞仍为当前浏览器保存的预览记录，不是跨用户统一榜单；GitHub Pages 提供静态页面托管。

## 本地预览

```sh
python -m pip install Pillow requests
python pipeline/restore_assets.py
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:4173/ 。需要通过 HTTP 打开，以加载配色 JSON。

## 功能和范围

- 页头提供 English / 简体中文选择，首次访问默认英文，并在当前浏览器记住选择。
- 界面、领域标签和色卡说明随语言切换；切换时保留检索、筛选、展开数量与点赞。英文、中文文案保存在静态语言文件中，访客无需访问翻译服务。
- 收录论文的原版架构图和每篇原论文/解读来源。逐图复核网络及神经模块，替换误选的 teaser、数据示例和性能图。
- 每次加载 24 张；搜索、领域与标签筛选覆盖全部收录论文。
- 领域筛选、标签检索、全文关键词搜索、原图放大和配色观察。
- 单色或整组 HEX 复制、JSON 导出。
- 当前浏览器的点赞/取消点赞、刷新后保留、按点赞降序排序。同票按收录顺序排列。
- 此次是效果预览：没有全站点赞数据库，每张初始 0 赞；不展示虚构热度。

## 内容与溯源

`dist/palettes.json` 是完整前端数据，`dist/collection.json` 记录数量。初始 10 篇之外的逐图审核证据保存在部署后的 `dist/collection-audit.json`，包含原图 SHA256、图号、来源、取色像素坐标、确切 RGB、排除区域与具体配色观察。发布前逐个核验取色点及审核绑定。

首批十篇记录在 `research/seed-palettes.json` 和 `research/assets-a.json` 中。`build_palettes.py` 是历史十张构建脚本，完整发布后禁止覆盖新数据。500 篇的采集与发布流程见 `research/batch500/README.md`。

采色定位模块填色、边框和 token 色，统计原始像素中的代表颜色，再目视校对；排除白背景、无意义抗锯齿、示例照片和输出热图。每组保留 2–8 个真实代表色，允许灰色等有意义中性色。色块等宽显示，不代表面积比例。TESSERA 的渐变色使用模块中部的代表取样。

图片与完整审核数据通过 `data/figure-assets/` 的分片包保存。恢复程序验证每片与完整包的 SHA256，只允许写入指定图片目录和审核文件。原始论文 PDF、网页抓取及工作缓存不上传到仓库。

医学图像论文属于 **CVPR 2026 Findings**。OmniGen2 使用作者项目页展示的早期架构版本，其图源标题与索引中的新版标题分别保留在溯源记录及卡片说明中。

原始图像归论文作者/权利人所有，使用或再分发请遵守来源的许可要求；此项目的配色分析属于编辑性解读，不是论文作者的设计声明。

## NeurIPS 2026 增量维护

每批 7 篇，以当前上线集合为基线。先恢复现有图片包，再以版本化论文、授权证据、目视审核稿与原图像素注入新批次。历史 500 篇导出脚本不能用于增量更新。

```sh
python pipeline/restore_assets.py
BASELINE=$(sha256sum dist/palettes.json | cut -d ' ' -f1)
python pipeline/append_reviewed.py /path/to/review-packet.json --baseline-sha256 "$BASELINE"
python pipeline/bundle_assets.py
python pipeline/restore_assets.py
```

新增色卡需要补齐 `dist/content-en.json` 和 `dist/content-zh.json` 的静态本地化映射；发布时同步更新 HTML 中脚本和加载的数据版本，避免旧缓存与新数据混用。

逐张审核稿需要绑定原图 SHA256、至少 2 个且最多 8 个确切原图 RGB、坐标、确认人、配色观察及适用许可。公开审图记录保留原图、出处与衍生大图和缩略图校验，不包括完整论文 PDF 或暂存候选。

## 检查

```sh
python pipeline/validate_release.py
node --check dist/app.js
node --check dist/i18n.js
node tests/frontend-scale.cjs --require-release
python tests/asset_bundle.py
```

上线后运行 `python pipeline/verify_pages.py`，逐文件核对全部线上大图、缩略图和站点数据与已审核发布版本一致。

## 后续上线

若需要多用户统一点赞榜，需增加服务端数据库、身份或匿名访客标识、幂等点赞 API 与滥用限制；不要把浏览器点赞统计当成全站榜单。
