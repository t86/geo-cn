# geo-cn — Claude SEO 国内优先 GEO 分支

本地工作区路径：`/workspace/geo-cn`  
上游：[`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo)（MIT，Agrici Daniel）  
远程 fork：[`t86/geo-cn`](https://github.com/t86/geo-cn)

本仓库是 **在上游 Claude SEO 插件之上的 China-first 适配**，产品方向对齐国内 B2B：**监测 + 诊断 + 可执行工单**。  
**不是**重写全部 19 个传统 SEO Agent，也 **不是**又一个泛提及率大盘。

## 相对上游改了什么

| 项 | 上游 Claude SEO | geo-cn |
|----|-----------------|--------|
| GEO 主引擎 | Google AIO / ChatGPT / Perplexity / Gemini / Copilot | **豆包 / DeepSeek / 通义 / Kimi / 文心 / 元宝** + **智谱（优先真探针）** |
| 品牌与引用信号 | Wikipedia、Reddit、YouTube、LinkedIn | **知乎、小红书、B站、微信公众号、百度百科/行业站** |
| 爬虫说明 | OAI-SearchBot、Claude-SearchBot 等 | 增加国内 UA 说明；**未知即标注未知** |
| 可见度探针 | 可选 DataForSEO 等（偏海外） | `probes/cn/`：**DeepSeek + 智谱可 live**；其余默认 stub |
| 传统 SEO 大包 | 完整保留 | 基本保留；本阶段重点只改编 GEO |

## Live 探针（DeepSeek / 智谱）

环境变量（**不要**把 key 写入仓库）：

| 变量 | 引擎 |
|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek（`deepseek-flash` → `api.deepseek.com/chat/completions`） |
| `DEEPSEEK_WEB_SEARCH=1` | 可选：Anthropic 兼容 `web_search_20250305` 路径 |
| `ZHIPU_API_KEY` 或 `BIGMODEL_API_KEY` | 智谱（优先 `glm-4-flash` + `web_search` / `search_pro`） |

```bash
cd /workspace/geo-cn   # 或本机 clone 路径
export DEEPSEEK_API_KEY=...
export ZHIPU_API_KEY=...   # 或 BIGMODEL_API_KEY

PYTHONPATH=. python3 -m probes.cn.cli list-engines --live-status

# 必须加 --live 才会真正打 API（否则 dry_run stub）
PYTHONPATH=. python3 -m probes.cn.cli probe \
  --engine deepseek --query "某工业软件 是什么" --brand "某工业软件" --live --json

PYTHONPATH=. python3 -m probes.cn.cli probe \
  --engine zhipu --query "某工业软件 是什么" --brand "某工业软件" --live --json
```

- 无 key → `status=stub`，并提示需要哪个 env。
- 有假 key / 网络失败 → `status=error`，**不会**捏造 citations。
- `doubao` / `tongyi` / `kimi` / `ernie` / `yuanbao` 仍为 stub。

## 怎么概念上跑 `/seo geo`（国内引擎）

1. 在 Claude Code 中仍可按上游方式安装本插件目录。
2. 对目标站执行：`/seo geo <url>`。
3. Agent 会按五维打分，并输出国内引擎平台分与工单；有 key 时优先用 DeepSeek/智谱实测。

## 已就绪 vs 仍是 stub

**已就绪**

- DeepSeek / 智谱 live 适配器（`probes/cn/engines/`）
- `agents/seo-geo.md`、`skills/seo-geo/`、探针契约与 CLI

**仍是 stub / 未接真机**

- 豆包 / 通义 / Kimi / 文心 / 元宝 live 抓取
- 付费 SoV 大盘、工单系统自动同步

## 许可与致谢

- 许可证：MIT（见 `LICENSE`）
- 上游版权：Agrici Daniel 及贡献者
- 本分支仅声明 **国内 GEO 适配** 的增量工作

更多变更见 [`CHANGELOG-CN.md`](./CHANGELOG-CN.md)。
