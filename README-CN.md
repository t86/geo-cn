# geo-cn — Claude SEO 国内优先 GEO 分支

本地工作区路径：`/workspace/geo-cn`  
上游：[`AgriciDaniel/claude-seo`](https://github.com/AgriciDaniel/claude-seo)（MIT，Agrici Daniel）

本仓库是 **在上游 Claude SEO 插件之上的 China-first 适配**，产品方向对齐国内 B2B：**监测 + 诊断 + 可执行工单**。  
**不是**重写全部 19 个传统 SEO Agent，也 **不是**又一个泛提及率大盘。

> 当前为本地浅克隆适配；远程 fork / push 由维护者另做（本环境未登录 `gh`）。  
> Git remote 已命名为 `upstream` → 上游原仓库。

## 相对上游改了什么

| 项 | 上游 Claude SEO | geo-cn |
|----|-----------------|--------|
| GEO 主引擎 | Google AIO / ChatGPT / Perplexity / Gemini / Copilot | **豆包 / DeepSeek / 通义 / Kimi / 文心 / 元宝** |
| 品牌与引用信号 | Wikipedia、Reddit、YouTube、LinkedIn | **知乎、小红书、B站、微信公众号、百度百科/行业站** |
| 爬虫说明 | OAI-SearchBot、Claude-SearchBot 等 | 增加国内 UA 说明；**未知即标注未知**（见 `skills/seo-geo/references/cn-engines-and-crawlers.md`） |
| 可见度探针 | 可选 DataForSEO 等（偏海外） | 新增 `probes/cn/` 契约 + **默认 stub** |
| 传统 SEO 大包 | 完整保留 | 基本保留；本阶段重点只改编 GEO |

## 怎么概念上跑 `/seo geo`（国内引擎）

1. 在 Claude Code 中仍可按上游方式安装本插件目录（插件名暂保持兼容；见英文 README 安装段）。
2. 对目标站执行：`/seo geo <url>`（或把本 Agent/Skill 说明喂给编排器）。
3. Agent 会按五维打分（可引用性 / 结构 / 多模态 / 权威品牌信号 / 技术可达），并输出国内六引擎平台分与工单。
4. 可见度实测走探针契约：

```bash
cd /workspace/geo-cn
PYTHONPATH=. python -m probes.cn.cli list-engines
PYTHONPATH=. python -m probes.cn.cli probe --engine kimi --query "你的品牌 是什么" --brand "你的品牌" --json
```

默认返回 `"status": "stub"`——**表示未做真机调用，不要当成真实引用数据**。

## 已就绪 vs 仍是 stub

**已就绪（文档 / 契约 / 诊断逻辑）**

- `agents/seo-geo.md` — 国内 GEO 专家 Agent
- `skills/seo-geo/SKILL.md` — 国内 GEO Skill
- `skills/seo-geo/references/cn-engines-and-crawlers.md` — 引擎与爬虫诚实说明
- `probes/cn/` — 探针接口、模型、注册表、CLI、README

**仍是 stub / 未接真机**

- 六引擎 live 回答抓取与引用解析
- 付费 SoV / 监测后台
- 与客户工单系统（Linear/Notion 等）的自动同步
- 完整 `/seo setup` 运行时验证（本阶段未强制跑通）

## 许可与致谢

- 许可证：MIT（见 `LICENSE`）
- 上游版权：Agrici Daniel 及贡献者
- 本分支仅声明 **国内 GEO 适配** 的增量工作，**不声称**独立创作了整套 SEO 插件

更多变更见 [`CHANGELOG-CN.md`](./CHANGELOG-CN.md)。英文总览仍见 [`README.md`](./README.md)。
