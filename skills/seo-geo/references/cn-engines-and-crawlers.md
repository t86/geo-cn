# China engines and crawlers (geo-cn)

Last reviewed: 2026-10-26. Prefer primary-source URLs over community UA lists.
When evidence is thin, say **unknown / unverified** in audit output.

## P0 product engines

| ID | Product | Vendor | Index / crawl path (working model) | Evidence strength |
|----|---------|--------|------------------------------------|-------------------|
| `doubao` | 豆包 | ByteDance | ByteDance crawl/search ecosystem; check `Bytespider`, sometimes `ByteDanceBot` | Medium (ecosystem UA known; product-specific UA mixed) |
| `deepseek` | DeepSeek | DeepSeek | Often index-backed / partner search; `DeepSeekBot` appears in third-party lists | Low–Medium |
| `tongyi` | 通义 / Qwen | Alibaba | Partial overlap with 神马/夸克 (`YisouSpider`) in community guides | Medium for 神马; Low for “TongyiBot” claims |
| `kimi` | Kimi | Moonshot | Official: `Kimi-SearchBot`, `KimiBot`, `Kimi-User` | **High** — https://www.kimi.ai/policies/kimi-crawlers |
| `ernie` | 文心 | Baidu | Primarily `Baiduspider` + Baidu resource platform | High for Baiduspider path |
| `yuanbao` | 元宝 | Tencent | Sogou index + WeChat 公众号/视频号 | Medium |

## Official Kimi UAs (primary source)

From Moonshot's crawler policy page:

- `KimiBot` — foundation-model training crawl
- `Kimi-SearchBot` — search index / search features
- `Kimi-User` — user-triggered fetches; robots.txt may not fully apply

Always report training vs search separately (same spirit as OAI-SearchBot vs GPTBot upstream).

## Common ecosystem UAs to check

| UA token | Often associated with | Notes |
|----------|----------------------|-------|
| `Baiduspider` | 百度搜索 / 文心联网 | Primary Baidu path |
| `Bytespider` | 抖音/头条/豆包生态 | ByteDance spider family |
| `ByteDanceBot` | ByteDance | Seen on some publisher robots examples |
| `Sogou web spider` | 搜狗 / 元宝部分来源 | Keep exact spacing when matching |
| `YisouSpider` | 神马 / 夸克 / 通义部分来源 | Community GEO guides |
| `bingbot` | 必应 | Sometimes feeds partner AI answers |
| `Kimi-SearchBot` / `KimiBot` / `Kimi-User` | Kimi | Official |

## Unverified UA names (do not assert purpose)

`DeepSeekBot`, `DoubaoBot`, `YuanbaoBot`, `ERNIEBot`, `QwenBot`, `TongyiBot`, `MoonshotBot`, `Hunyuan` — may appear in third-party robots aggregators or site configs. Report presence if found in the site's robots.txt, but label purpose as **unverified** unless you attach an official doc URL.

## Brand / citation surfaces (China)

Prefer these over Wikipedia / Reddit / LinkedIn for CN scores:

1. 知乎
2. 微信公众号
3. 小红书
4. B站
5. 百度百科 / 垂直百科 / 权威行业站
6. CSDN / 掘金（偏研发与工业软件受众）

## Probe contract

Live visibility checks go through `probes/cn/` (stub by default). Never invent citations.
