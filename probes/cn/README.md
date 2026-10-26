# probes/cn — China AI engine probe contract

Part of **geo-cn**, a China-first fork of [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT).

## Goal

`query brand/keyword (+ optional URL) → structured visibility result` for domestic engines:

| ID | Product | Live? |
|----|---------|-------|
| `doubao` | 豆包 | stub |
| `deepseek` | DeepSeek | **live** if `DEEPSEEK_API_KEY` |
| `tongyi` | 通义 / Qwen | stub |
| `kimi` | Kimi | stub |
| `ernie` | 文心 | stub |
| `yuanbao` | 元宝 | stub |
| `zhipu` | 智谱 GLM | **live** if `ZHIPU_API_KEY` or `BIGMODEL_API_KEY` |

## Contract

- **Interface:** `EngineProbe.probe(query, *, brand=None, url=None, context=None) -> VisibilityResult`
- **Status values:** `stub` | `measured` | `error` | `unsupported`
- **Rule:** never invent live citations. Stub returns `status=stub` with null measurement fields and explanatory `notes`.

### `VisibilityResult` fields

| Field | Meaning |
|-------|---------|
| `engine` | One of the IDs above |
| `query` | Prompt / search query used |
| `brand` | Brand string being monitored |
| `status` | How the result was produced |
| `answer_excerpt` | Short engine answer text when measured |
| `brand_mentioned` | Brand name appears in answer |
| `brand_cited` | Brand URL / owned domain cited |
| `citations` | List of `{title,url,snippet,position,is_brand_domain}` |
| `competitor_mentions` | Other brands named |
| `notes` | Human-readable caveats |
| `error` | Set when `status=error` |

## CLI

```bash
cd /path/to/geo-cn
PYTHONPATH=. python3 -m probes.cn.cli list-engines --live-status
PYTHONPATH=. python3 -m probes.cn.cli probe --engine deepseek --query "某工业软件 是什么" --brand "某工业软件" --json
# measured call:
PYTHONPATH=. python3 -m probes.cn.cli probe --engine zhipu --query "某工业软件 是什么" --brand "某工业软件" --live --json
```

Without `--live`, `dry_run=True` and live adapters still return stub notes.

### Env

- `DEEPSEEK_API_KEY` — DeepSeek chat (`deepseek-flash`); optional `DEEPSEEK_WEB_SEARCH=1` or `--web-search`
- `ZHIPU_API_KEY` or `BIGMODEL_API_KEY` — 智谱 `glm-4-flash` (+ `glm-4-air` fallback) with `web_search` / `search_pro`

## Adapters

- `engines/deepseek_probe.py` — OpenAI-compatible chat; optional Anthropic `web_search_20250305`
- `engines/zhipu_probe.py` — chat+web_search; fallback `/paas/v4/web_search`
- `registry.refresh_registry()` — re-bind stubs vs live from current env

## Related

- Agent: `agents/seo-geo.md`
- Skill: `skills/seo-geo/SKILL.md`
- Crawler notes: `skills/seo-geo/references/cn-engines-and-crawlers.md`
