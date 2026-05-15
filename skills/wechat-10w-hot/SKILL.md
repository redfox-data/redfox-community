---
name: wechat-10w-hot
description: 全网持续收录每日超过1000+公众号10w+文章内容，向用户推送公众号达到10w+阅读的热门文章；当用户需要获取全领域的公众号热门文章、或订阅每日10w+文章推送、特定领域爆款文章时使用
dependency:
  python: []
  system: []
---

# 公众号 10w+ 热门文章推荐

---

## 简介

面向「公众号 10w+ 阅读爆文」场景的交付型 Skill：按分类与时间窗口拉取榜单，**对话内给出完整 Markdown 榜单**，并生成 **可导出 PDF 的 HTML**；支持按赛道订阅推送（产品侧若已开通）。

**能做什么？**

- **总榜 / 分赛道榜单**：标准 23 分类 + 总排名；默认 TOP50 候选，首轮对话可 preview 10 条。
- **数据诚实**：强依赖脚本 stdout，**禁止** Agent 编造文章或阅读数。
- **HTML + PDF**：榜单页遵循微信绿视觉规范，单页 PDF 导出（html2pdf.js）。
- **规律复盘**：在榜单后输出基于真实条目的「爆款规律分析」，并询问是否订阅赛道。

**适合谁用？**

- 公众号编辑 / 运营 —— 追热点、看标题与账号分布
- 内容负责人 —— 要「可分享、可打印」的榜单页
- 增长 / 商务 —— 按赛道盯 10w+ 供给

**运行依赖**：Python 3；数据脚本以仓库内 `scripts/fetch_hot_articles.py` 声明为准（标准库为主）。

---

## 功能特性

### 核心功能

- **榜单拉取**：`scripts/fetch_hot_articles.py` → 写 `temp_articles.json` → 对话原样输出。
- **时间口径**：每日 **18:30** 同步前一日数据；Agent 必须按当前钟点计算查询区间（详见参考文档）。
- **HTML 生成**：`scripts/generate_hot_html.py`，**`--display_count` 必须与当前对话展示条数一致**。
- **订阅引导**：规律分析后询问是否订阅；**同一轮不执行订阅**，待用户下一条再分支。

### 特色亮点

- **脚本输出即正文**：表格 + 详情 + 统计区均不可删改重排。
- **18:30 分水岭**：早于 18:30 与晚于 18:30，「最新可用日期」不同，需配合固定致歉话术。
- **禁止凑数**：少于 10 条如实展示；无数据按参考文档提示改查总榜或其它分类。

---

## 使用场景

当用户出现下列诉求时，应加载并严格按参考文档执行：

| 用户可能会问                          | Agent 行为概要                                                   |
| ------------------------------------- | ---------------------------------------------------------------- |
| 「今日爆文」「10w+ 文章」「最新爆文」 | 总榜意图 + 计算日期 + `fetch_hot_articles.py`（通常 preview 10） |
| 「科技 / 财经 / 健康…类 10w+」        | 映射到标准 `--type` + 时间区间 + 脚本                            |
| 「最近 / 最新有什么热门」             | 默认 **近 7 天** 区间（见时间规则文档）                          |
| 「展开全部 / 看 50 条」               | 在同区间下改 `--mode full`，HTML `display_count` 同步            |

### 典型对话节奏

1. 识别意图 → 2. 跑脚本原样展示 → 3. 爆款规律分析 → 4. 订阅询问 → 5. **立即**生成 HTML（不等订阅答复）→ 6. 用户若回订阅再走订阅分支。

---

## 重要数据说明

- **更新节奏**：榜单库 **每日 18:30** 对齐前一日；对外推送话术可用 **19:30**。
- **时间不一致**：凡用户说的「今天 / 昨天」与真实可查区间不一致，必须使用 **`references/time-and-date-rules.md`** 中的原文致歉话术。

---

## 核心执行规则（必须遵守）

1. **必须先跑脚本**：任何榜单正文均来自 `fetch_hot_articles.py` 的 stdout，不得手写替代。
2. **stdout 原样展示**：含「数据说明、概览表、详情、统计」整块粘贴。
3. **固定六步顺序**：不得跳过「规律分析 → 订阅询问 → HTML」；细则见 **`references/agent-workflow.md`**。
4. **HTML 条数一致**：对话展示 N 条，则 `generate_hot_html.py --display_count N`。
5. **细节下钻**：日期区间、参数表、输出模板、API 字段等一律以 references 为单一事实来源（见下节资源索引）。

---

## 项目架构

### 目录（参考）

```text
wechat-10w-hot/
├── SKILL.md                              # 本入口（精简版）
├── scripts/
│   ├── fetch_hot_articles.py             # 拉取 + 对话 Markdown 输出 + temp JSON
│   └── generate_hot_html.py             # 读 temp JSON → HTML
└── references/
    ├── agent-workflow.md                 # 六步流程、订阅、自检
    ├── time-and-date-rules.md            # 18:30 与区间、固定话术
    ├── script-parameters-and-output.md   # CLI、输出格式、四维分析
    ├── html-pdf-visual-spec.md           # 视觉、PDF、HTML 参数
    ├── usage-examples.md                 # 场景化命令示例
    ├── api-spec.md                       # 接口字段说明
    └── category-mapping.md               # 分类映射
```

### 数据流（概念）

```text
用户请求 → 意图 + 日期区间 → fetch_hot_articles.py → stdout（对话）+ temp_articles.json
                                              ↓
                     generate_hot_html.py（display_count 对齐）→ HTML（可 PDF）
```

---

## 资源索引（何时读哪份）

| 文件                                                                                     | 何时读取                                   |
| ---------------------------------------------------------------------------------------- | ------------------------------------------ |
| [references/agent-workflow.md](references/agent-workflow.md)                             | 执行任意一步前：核对顺序、订阅、自检       |
| [references/time-and-date-rules.md](references/time-and-date-rules.md)                   | 计算 `start_date` / `end_date`、写致歉话术 |
| [references/script-parameters-and-output.md](references/script-parameters-and-output.md) | 拼 CLI、理解 stdout 结构、内容分析四维     |
| [references/html-pdf-visual-spec.md](references/html-pdf-visual-spec.md)                 | 生成 HTML / PDF 样式与命令                 |
| [references/usage-examples.md](references/usage-examples.md)                             | 对照总榜 / 领域 / 全量 / 冷门 / 空数据     |
| [references/api-spec.md](references/api-spec.md)                                         | 查 URL、请求参数、`tenWReadingRank` 结构   |
| [references/category-mapping.md](references/category-mapping.md)                         | 用户口语 → 标准 `--type`                   |

---

## 常见问答

**Q1：能否不跑脚本直接给 10 篇例文？**
A：**不能**。无脚本输出即视为未执行本 Skill。

**Q2：用户只要 HTML、不要长文？**
A：仍必须先完整展示脚本 stdout（规范要求），再生成 HTML。

**Q3：`temp_articles.json` 有 50 条但对话只聊了 10 条，HTML 几条？**
A：**10 条**；`--display_count 10`。

**Q4：接口 URL 以哪里为准？**
A：以 **`references/api-spec.md`** 与 `fetch_hot_articles.py` 内常量为准，二者若有差异以脚本为准并应同步修正文档。

---
