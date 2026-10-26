# Changelog (geo-cn)

## 2026-10-26 — China-first GEO fork (local)

基于上游 `AgriciDaniel/claude-seo` 浅克隆本地适配，**未推送到 GitHub**。

### Added

- `README-CN.md` — 中文说明：分支定位、相对上游差异、探针用法、stub 边界、MIT 致谢
- `CHANGELOG-CN.md` — 本文件
- `probes/cn/` — 国内引擎探针契约
  - `models.py` / `base.py` / `stub_probe.py` / `registry.py` / `cli.py`
  - `README.md` — 输入输出约定与接入 live adapter 指引
  - P0 engine IDs: `doubao`, `deepseek`, `tongyi`, `kimi`, `ernie`, `yuanbao`
- `skills/seo-geo/references/cn-engines-and-crawlers.md` — 国内引擎与 crawler UA 诚实对照

### Changed

- `agents/seo-geo.md` — 改为国内 GEO 专家：六引擎、国内品牌信号、工单输出、探针契约
- `skills/seo-geo/SKILL.md` — China-first 评分与平台说明；上游 Google/海外材料降为参考
- `README.md` — 顶部增加 geo-cn / Claude SEO CN fork 标识（保留英文安装与命令）
- `.claude-plugin/plugin.json` — description 注明 CN GEO fork；保留可安装的插件名兼容
- Git remote：`origin` 重命名为 `upstream`（指向 AgriciDaniel/claude-seo），便于后续添加自有 fork 为 `origin`

### Not done (intentional)

- 未登录 `gh`、未创建远程 fork、未 push
- 未接付费 API / 未宣称 live 引擎实测
- 未重写其余传统 SEO Agent（technical/content/schema 等仍为上游原文）
