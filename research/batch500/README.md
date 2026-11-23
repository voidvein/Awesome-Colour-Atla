# 500篇色卡审计

目标是500篇去重、逐图审查通过的论文色卡，包含原有10篇。候选数量与下载成功数不代表完成数量。

## 数据流

1. `pipeline/collect_batch.py catalog` 读取用户指定的 CVPR 2026 目录，按领域轮流建立候选列表。
2. `pipeline/collect_batch.py notes --limit 1400` 保存候选的标题、领域、标签、原文链接。读取较多候选是为了替换没有架构图或无法核验的文章。
3. `pipeline/process_sources.py --limit 1200 --workers 4` 仅取得公开论文正文或原版图，不下载补充材料。所有自动结果都保持待审。
4. `pipeline/review_batch.py <packet-name>` 生成分配明确的审图包。审查原图、裁剪边界、配色取样点；照片与结果图不作为架构模块配色。原文含多种任务图时，选择明确网络或计算模块。
5. `pipeline/record_review.py` 记录逐图决定，绑定原图 SHA256、确认的色卡和具体配色观察；必要时先用 `repair_palette.py` 显式排除照片区域。
6. `pipeline/publish_dataset.py --target 500` 仅合并已批准且哈希/色卡未变更的条目，去除标题与论文来源重复。少于500时拒绝生成正式数据。
7. `pipeline/bundle_assets.py` 把网页图片分块打包；GitHub Actions 用 `pipeline/restore_assets.py` 校验并恢复，再逐卡验证、部署。

## 审计证据

- `catalog.json`：候选来源与领域。
- `records/`：每篇正文来源、具体图号与图注、PDF页码/裁剪位置、原图哈希、逐色实际像素位置和排除区域。
- `reviews/`：逐张审查结论。仅 `accepted` 可计入；`needs_recrop`、`needs_palette_mask`、`rejected` 均不计入。
- `published-audit.json`：最终发布的新条目审计与适屏图、缩略图哈希；随分块资源包一起恢复到 `dist/collection-audit.json` 并发布。原有10篇保留在 `../seed-palettes.json`。

`cache/` 中的完整PDF/HTML、`contacts/` 工作图和包含未入选候选的 `records/` 不提交到GitHub；对外保留论文/图源链接、逐篇review及最终入选审计证据。前端仅展示确切存在的2–8个代表色，不为统一色数引入照片或伪造颜色。

## 完成判据

正式数据须恰好包含500篇唯一论文，每篇具有原版架构或明确计算模块图、可追溯来源、真实色卡、领域标签、逐图批准记录。GitHub Actions需通过全部图片与审计校验、前端500条交互测试、Pages部署，并检查正式网站的完整资源清单。
