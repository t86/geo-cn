# Changelog (geo-cn)

## 2026-10-26 — DeepSeek + 智谱 live probes

### Added

- `EngineId.ZHIPU = "zhipu"`（七引擎：原六引擎 + 智谱优先）
- `probes/cn/engines/common.py` — env key、品牌提及/引用判定、urllib JSON HTTP
- `probes/cn/engines/deepseek_probe.py` — `DEEPSEEK_API_KEY`；`deepseek-flash` chat；可选 Anthropic `web_search_20250305`
- `probes/cn/engines/zhipu_probe.py` — `ZHIPU_API_KEY` / `BIGMODEL_API_KEY`；`glm-4-flash`（失败再试 `glm-4-air`）+ `web_search`/`search_pro`；失败回退 `/paas/v4/web_search`
- `registry.refresh_registry()` — 按 env 注册 live 适配器，否则 stub
- CLI `--live`、`--web-search`、`list-engines --live-status`

### Changed

- `README-CN.md` / `agents/seo-geo.md` / `probes/cn/README.md` — 文档对齐 live 路径
- 无 key 或 dry_run 时诚实返回 `stub`；假 key 返回 `error`，不伪造 citations

### Still stub

- doubao / tongyi / kimi / ernie / yuanbao

---

## 2026-10-26 — China-first GEO fork

基于上游 `AgriciDaniel/claude-seo` 适配并推送到 [`t86/geo-cn`](https://github.com/t86/geo-cn)。

### Added

- `README-CN.md`、`CHANGELOG-CN.md`
- `probes/cn/` 契约（models / base / stub / registry / cli）
- `skills/seo-geo/references/cn-engines-and-crawlers.md`

### Changed

- `agents/seo-geo.md`、`skills/seo-geo/SKILL.md` — 国内六引擎 + 品牌信号
- Git：`upstream` → AgriciDaniel/claude-seo；`origin` → t86/geo-cn
