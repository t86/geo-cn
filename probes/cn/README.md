# probes/cn — China AI engine probe contract

Part of **geo-cn**, a China-first fork of [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) (MIT).

## Goal

`query brand/keyword (+ optional URL) → structured visibility result` for domestic P0 engines:

| ID | Product |
|----|---------|
| `doubao` | 豆包 |
| `deepseek` | DeepSeek |
| `tongyi` | 通义 / Qwen |
| `kimi` | Kimi |
| `ernie` | 文心 |
| `yuanbao` | 元宝 |

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

## CLI (stub)

From the repo root (needs Python 3.10+ on `PYTHONPATH=.`):

```bash
cd /path/to/geo-cn
PYTHONPATH=. python -m probes.cn.cli list-engines
PYTHONPATH=. python -m probes.cn.cli probe --engine kimi --query "某工业软件 是什么" --brand "某工业软件" --json
```

Expected stub output includes `"status": "stub"` and empty `citations`.

## Plugging a real adapter

1. Implement `EngineProbe` (see `base.py`) for one engine — API, browser automation, or partner SoV feed.
2. Call `register_probe(YourProbe())` at process start (overrides the stub).
3. On success set `status=ProbeStatus.MEASURED` and fill citations from the real response only.
4. Keep robots / crawler analysis in the GEO agent (`agents/seo-geo.md`); probes answer **visibility**, not page scoring.

Suggested first live wire: **Kimi** (official SearchBot docs) or a vendor chat API you already have keys for. Browser automation against consumer chat UIs is fragile — treat as last resort and respect ToS.

## Related

- Agent: `agents/seo-geo.md`
- Skill: `skills/seo-geo/SKILL.md`
- Crawler notes: `skills/seo-geo/references/cn-engines-and-crawlers.md`
