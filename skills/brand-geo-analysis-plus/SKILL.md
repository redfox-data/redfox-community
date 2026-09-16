---
name: brand-geo-analysis-plus
description: 中国互联网品牌感知监测统一工具。聚合全网热榜追踪（hub）、小红书/抖音/公众号近30天深度讨论研究（cn30）、豆包/Kimi/DeepSeek AI 搜索品牌可见度分析（geo）三个互补模块，帮助品牌方/市场运营/内容创作者从「话题热度—真实口碑—AI 回答」三层视角全面感知品牌。当用户需要研究中国社交媒体热点、分析品牌舆情、对比竞品口碑、分析品牌在 AI 搜索中的表现、做 GEO 优化、追踪全网热点时使用。触发词：品牌感知、舆情监测、社媒研究、热榜聚合、AI 搜索可见度、GEO 分析、跨平台舆情、热点追踪、品牌口碑、品牌竞品对比、社媒热榜。
agent_created: true
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
metadata:
  emoji: "👁️"
  requires:
    env:
      - REDFOX_API_KEY
    bins:
      - python3
  primaryEnv: REDFOX_API_KEY
  tags:
    - brand
    - social-media
    - trends
    - ai-search
    - geo
    - xiaohongshu
    - douyin
    - wechat
    - weibo
    - bilibili
    - kuaishou
    - toutiao
    - baidu
    - zhihu
    - doubao
    - kimi
    - deepseek
---

# 品牌GEO分析Plus版

## 一句话定位

一个 Skill、三层视角：实时热榜聚合（hub）+ 近30天社媒深度研究（cn30）+ AI 搜索品牌可见度（geo），覆盖中国互联网品牌感知的全部关键场景。

## 何时使用

任意以下场景触发，立即使用本 skill：

- 想知道今天全网在聊什么、哪个热点值得追 → **hub 模块**
- 想研究某话题在过去30天的真实用户讨论、做品牌口碑/竞品对比 → **cn30 模块**
- 想看品牌在豆包/Kimi/DeepSeek AI 搜索里被如何介绍、品牌 AI 可见度如何 → **geo 模块**
- 想做完整的品牌感知诊断（热榜热度 → 真实口碑 → AI 回答） → **组合工作流**

## 三个模块速览

| 模块                     | 脚本入口                                                                     | 平台                                       | 时间维度                               | 输出                                                      |
| ------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------ | -------------------------------------- | --------------------------------------------------------- |
| **hub**（热榜）          | `scripts/hub_fetch.py`                                                       | 百度/知乎/微博/抖音/B站/快手/头条（7平台） | 实时（小时级）/ 昨日 / 本周 / 历史30天 | TOP10 表格 + 跨平台小结 + 趋势预测                        |
| **cn30**（社媒研究）     | `scripts/cn30_search.py`                                                     | 小红书/抖音/公众号（3平台）                | 近30天任意天数                         | 数据速览（TOP5×3平台）+ 综合洞察 + HTML 报告              |
| **geo**（AI 搜索可见度） | `scripts/geo_search.py` + `scripts/geo_analyze.py` + `scripts/geo_report.py` | 豆包/Kimi/DeepSeek（3 平台）               | 即时提问                               | GEO 得分 + 提及率 + 情绪 + 竞品 + 信源 + 交互式 HTML 报告 |

## 鉴权（共享）

三个模块共享同一个 `REDFOX_API_KEY`。从 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 获取，配置方式：

```bash
export REDFOX_API_KEY=ak_你的密钥
```

或写入 `~/.openclaw/openclaw.json` 的 `env.REDFOX_API_KEY`。优先级：命令行 `--api-key` > 环境变量 > 配置文件。

依赖安装（按模块）：

| 模块 | 依赖                                   |
| ---- | -------------------------------------- |
| hub  | 标准库（`urllib.request`，无三方依赖） |
| cn30 | 标准库（`urllib.request`，无三方依赖） |
| geo  | `pip install requests`                 |

---

## 路由决策树

根据用户意图选择模块。如果意图模糊，先用 AskUserQuestion 确认。

```
用户想做什么？
│
├─ 想知道今天/最近哪个话题/事件在全网火
│   └─→ hub 模块（实时热榜）
│
├─ 想研究某话题在用户真实讨论里的口碑/反馈
│   └─→ cn30 模块（小红书+抖音+公众号）
│
├─ 想看品牌/产品在 AI 搜索里被如何介绍
│   └─→ geo 模块
│
├─ 想做品牌诊断：热度 + 口碑 + AI 可见度 全维度
│   └─→ 组合工作流（hub → cn30 → geo）
│
└─ 给了具体平台/时间/品牌名
    └─→ 根据字段路由到对应模块
```

---

## 模块一：hub（热榜聚合）

### 能力

实时抓取 7 大平台热搜数据，跨平台事件识别，TOP10 榜单，趋势预测，订阅推送。

### 平台代码

| 代码 | 平台 | 代码 | 平台 |
| ---- | ---- | ---- | ---- |
| `bd` | 百度 | `bz` | B站  |
| `zh` | 知乎 | `ks` | 快手 |
| `wb` | 微博 | `tt` | 头条 |
| `dy` | 抖音 |      |      |

### 快速调用

```bash
# 最新热榜（前一个完整小时）
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/hub_fetch.py \
  --source "全平台热点事件-GitHub"

# 今日热榜（今日0:00 到当前整点）
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/hub_fetch.py \
  --source "全平台热点事件-GitHub" \
  --start-date "T 00:00:00" --end-date "T HH:00:00"

# 昨日热榜 / 本周热榜 / 指定平台 / 关键词泛化
# 详见 references/hub-instructions.md
```

### 输出规范

按平台分类输出 TOP10，**平台展示顺序固定**为：百度 → 知乎 → 微博 → 抖音 → B站 → 快手 → 头条。

- 智能跳过空平台
- 数据≤10 条展示实际数量；>10 条显示「查看{平台名}完整榜单」引导
- 热度值**已由脚本格式化完毕**，直接使用 `hotCount` 字段原值即可，**不要做任何换算**
  - 脚本内 `format_hot_count()` 已处理：纯数字会折算为「数字+万」（`5980000` → `598万`）；返回值已含单位（`"598万"`、`"345 万热度"`）的原样透传
  - 禁止对 `hotCount` 做整除/乘法运算（它是字符串，会 `TypeError`），也禁止再拼接「万」（会得到「598万万」）
- 完整模板见 `references/hub-output-templates.md`
- 趋势预测逻辑见 `references/hub-prediction-logic.md`
- 全部指令清单见 `references/hub-instructions.md`

### 关键规则

- **小时级更新**：默认查询是「前一个完整小时」而非当前小时
- **关键词泛化**：大词（体育/娱乐/科技等）自动扩展为10个相关词；精确词直接用原词
- **默认 compact 模式**：stdout 输出极简（每平台仅预览 TOP3，表头会标注"（下表为 TOP3 预览）"）+ 末尾附带 `dataFile: {path}`，完整榜单必须从 `dataFile` 读 JSON，不要因为只看到 3 条就认为数据缺失
- **平台顺序已由脚本固定**为 百度 → 知乎 → 微博 → 抖音 → B站 → 快手 → 头条，无需自行重排

---

## 模块二：cn30（社媒深度研究）

### 能力

从小红书、抖音、公众号三大平台搜索近30天真实用户讨论数据，跨平台综合分析舆情趋势，输出研究报告和可视化 HTML 报告。

### 平台代码

| 代码  | 平台   | 关键指标                               |
| ----- | ------ | -------------------------------------- |
| `xhs` | 小红书 | 点赞/收藏/评论（收藏/点赞比=种草信号） |
| `dy`  | 抖音   | 点赞/评论/分享（分享数=传播力）        |
| `gzh` | 公众号 | 阅读/点赞/转发（阅读量=关注度）        |

### 快速调用

```bash
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/cn30_search.py \
  "AI视频工具,大模型" \
  --platforms xhs,dy,gzh \
  --count 50 \
  --days 30 \
  --output-format both \
  --output-dir ~/Documents/CnLast30Days
```

`--output-format` 支持 `json` / `html` / `both`。

### 工作流

1. **环境检查**：确认 `REDFOX_API_KEY` 已配置
2. **关键词质量检查**：话题太模糊（"工具"、"方法"）时让用户具体化
3. **预研究**：并行 2-3 个 WebSearch 提取热词（小红书/抖音/通用）
4. **查询计划**：合并相关词为一次调用，每平台最多5个词，默认只调用1次引擎
5. **运行引擎**：前台运行（5分钟超时），读完整输出
6. **WebSearch 补充**：1-2 次 WebSearch 覆盖知乎/B站/36氪（排除 xhs/dy/gzh 域名）
7. **综合输出**：按 [输出规则](references/cn30-output-rules.md) 生成报告

### 输出规范（强制）

```
🇨🇳 cn-last30days v2.0.0 · {YYYY-MM-DD}

## 数据速览
（公众号 TOP5 → 小红书 TOP5 → 抖音 TOP5，标题作可点击 Markdown 链接）

我的发现：
**{话题}** - 1-2句描述，来源 [平台@作者](链接)
核心发现：
1. ...
2. ...

{引擎页脚逐字粘贴}

---
我是 {TOPIC} 的专家，我可以帮你：
- ...
HTML 报告已生成：[查看报告](HTML文件路径)
```

**LAW 规则**（任何一条违反都视为输出错误）：

- LAW 1：结尾不要 `Sources:` / `References:` 块
- LAW 2：通用查询以「我的发现：」开头，禁止 `##`/`###` 章节标题；对比查询例外
- LAW 3：不用破折号（`—`/`–`），用 `-`（空格连字符空格）
- LAW 4：引擎页脚逐字包含，位于核心发现之后、邀请之前
- LAW 5：每个引用用内联 Markdown 链接，不用裸 URL
- LAW 6：不要输出原始排名列表，转化为散文洞察
- LAW 7：徽章之后、「我的发现」之前必须有「数据速览」模块

完整模板见 `references/cn30-output-rules.md`。

### HTML 报告（自动生成）

数据查询完成后，**无需询问**直接生成 HTML：

```bash
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/cn30_search.py \
  --from-json "JSON文件路径" \
  --output-dir ~/Documents/CnLast30Days
open "HTML文件路径"
```

---

## 模块三：geo（AI 搜索品牌可见度）

### 能力

向豆包、Kimi、DeepSeek 三个 AI 搜索引擎批量提问，分析品牌出现率、情绪倾向、信源引用、竞品对比，生成交互式 HTML 报告。

### 平台代码

`doubao` / `kimi` / `deepseek`（默认全选，逗号分隔）

### 工作流

#### Step 0: 输入收集

必填：

- 品牌名（如「元气森林」、「大疆」、「蔚来」）
- 品类/行业（如「无糖饮料」、「无人机」、「新能源汽车」）

可选：

- 品牌别名（提高匹配精度）
- 竞品列表
- 自定义问题列表（有则跳过 Step 1）

**如果只有品牌名没有品类，必须追问品类。**

#### Step 1: 问题生成（用户未提供问题时）

通过 websearch 搜索品类相关问题，结合品类知识生成 **8 个**问题。

问题类型必须覆盖四类（**每类至少 2 个**，共 8 个，最多 12 个）：

- **推荐类**：「{品类}哪个品牌好？」（不直接含品牌名）
- **对比类**：「{品牌A}和{品牌B}哪个好？」
- **评价类**：「{品牌}怎么样？」（可含品牌名）
- **场景类**：「{场景}用什么{品类}好？」（不直接含品牌名）

生成后**必须用 AskUserQuestion 确认**，等用户明确同意才能进入 Step 2。

#### Step 2: 批量搜索

```bash
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/geo_search.py \
  --queries '["问题1","问题2","问题3","问题4","问题5","问题6","问题7","问题8"]' \
  --platforms doubao,kimi,deepseek
```

输出 `output/search_results.json`。脚本自动完成全部任务（3 平台 × N 问题）的并行提交与轮询，最长 15 分钟。

- 8 个问题 → 24 个任务，等待提示：「约需 5-8 分钟」
- 平台返回限流/故障话术（如豆包「高峰期算力紧张…请稍后再试」）时，脚本会自动重试 1 次；仍无效则记为 `status: "invalid"` 并**排除出统计**（不计入提及率分母），不再当作「品牌未被提及」

#### Step 3: 确定性分析

```bash
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/geo_analyze.py \
  --brand "品牌名" \
  --aliases '["别名1","别名2"]' \
  --competitors '["竞品A","竞品B"]' \
  --search-results output/search_results.json
```

输出 `output/deterministic.json` + `output/ai_analysis_template.json`。

#### Step 4: AI 分析（Agent 执行）

读取 `output/search_results.json`，**只对 `status == "completed"` 的回答**分析以下字段（`invalid` / `failed` / `timeout` 一律跳过，它们已被排除出统计）：

- `brand_rank` (int|null)：推荐列表中的排名位置
- `brand_context` (str)：上下文摘要
- `sentiment` (str)：`positive` / `neutral` / `negative`
- `sentiment_reason` (str)：判断依据
- `competitors_mentioned` (list[str])：所有提及的竞品
- `competitor_details` (list[dict])：每竞品的 rank + sentiment
- `key_claims` (list[str])：2-3 条关键描述

写入 `output/ai_analysis.json`。

**注意**：正文中的内联引用标记（Kimi `<REF>…</REF>`、DeepSeek `[citation:N]`）已由脚本在 Step 2 剥离，无需自行处理。

**信源可用性**：`sources` 为空是**正常现象**，常见于 Kimi（该平台只返回正文内联引用标记，不含可解析外链）。此时结果里会带 `sources_note` 字段，报告「信源分析」章节会自动展示数据完整性提示，**不要把空信源当作「品牌官网未被引用」的结论**。

**情绪判断规则：**

- 回答明确推荐/强调优势 → `positive`
- 客观描述/仅列举 → `neutral`
- 指出缺点/不推荐 → `negative`

#### Step 5: 合并 + 报告生成

```bash
# 合并分析（Step 4 完成后）
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/geo_analyze.py \
  --brand "品牌名" --aliases '["别名"]' --competitors '["竞品"]' \
  --search-results output/search_results.json \
  --ai-analysis output/ai_analysis.json

# 生成 HTML
python3 ~/.workbuddy/skills/brand-geo-analysis-plus/scripts/geo_report.py \
  --analysis output/analysis_result.json \
  --search-results output/search_results.json
```

#### Step 6: 交付

1. 交付 `output/geo_report.html`
2. 输出关键发现摘要（5 条核心结论）：
   - 跨平台提及率 + 分平台拆分
   - GEO 综合得分 + 最佳/最差平台
   - 情绪分布（正面率 = 正面数/有效回答数，中性不计入正面）
   - 竞品对比 + 品牌排名
   - TOP3 信源域名 + 官网是否被引用（若某平台无信源，须说明而非当作"未被引用"）

### 核心指标

详细定义见 `references/geo-metrics.md`。核心公式：

```
GEO 得分 = 提及率得分 × 40% + 排名得分 × 30% + 情绪得分 × 30%
        = 提及率×100 × 40% + max(0, 100 - (均排名-1)×10) × 30%
          + (正面占比×100 - 负面占比×50) × 30%
```

解读：70+优秀 / 50-69良好 / 30-49一般 / <30不足。

---

## 组合工作流：完整品牌感知诊断

当用户需要做全维度品牌诊断（典型问法：「帮我做一份{X}品牌的完整感知报告」），依次执行：

### 阶段 1：hub 摸热度（5分钟）

```bash
python3 scripts/hub_fetch.py --source "全平台热点事件-GitHub" --keywords "{品牌}" --expand-keywords
```

产出：品牌是否在近期热点中、覆盖哪些平台、平均热度、上榜时长。

### 阶段 2：cn30 挖口碑（5-10分钟）

```bash
python3 scripts/cn30_search.py "{品牌},{品类}" --days 30 --output-format both
```

产出：真实用户讨论、情感倾向、TOP 反馈、HTML 报告。

### 阶段 3：geo 看 AI 回答（10-15分钟）

```bash
python3 scripts/geo_search.py --queries '[5 个问题]' --platforms doubao,kimi,deepseek
python3 scripts/geo_analyze.py --brand "{品牌}" --competitors '["{竞品}"]' --search-results output/search_results.json
# 步骤 4-5 见 geo 模块工作流
```

产出：品牌在 AI 搜索里的提及率、情绪、排名、信源、HTML 报告。

### 阶段 4：综合报告

把 hub/cn30/geo 三阶段发现合并成一份叙事文档，结构：

```
# {品牌} 品牌感知诊断报告

## 一句话结论
（综合三阶段结果的一句话判断）

## 1. 热度层（全网热榜）
- 是否在热点中 / 平台覆盖 / 趋势方向

## 2. 口碑层（社媒讨论）
- 真实用户反馈 / 正负面信号 / 关键讨论主题

## 3. AI 层（生成式搜索）
- GEO 得分 / 提及率 / 情绪分布 / 竞品对比 / 信源

## 4. 行动建议
- 热度层：{是否需要借势}
- 口碑层：{具体需改进的负面反馈}
- AI 层：{GEO 优化方向}
```

---

## 错误处理（通用）

| 情况                         | 处理方式                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------- |
| 未配置 `REDFOX_API_KEY`      | 提示用户前往 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 获取 |
| 关键词模糊（"工具"、"方法"） | 用 AskUserQuestion 让用户具体化                                                 |
| cn30 引擎部分失败            | 继续分析已完成的数据，HTML 报告中标注失败项                                     |
| geo 任务全部超时             | 提示用户稍后重试，可能是 API 负载过高                                           |
| geo AI 分析结果缺失          | 仅生成确定性分析（提及率、域名），情绪模块标注"待分析"                          |
| 品牌名太短（≤2字）           | 提示用户提供品牌别名以提高匹配精度                                              |

---

## 资源索引

### 脚本

| 文件                             | 用途                                             |
| -------------------------------- | ------------------------------------------------ |
| `scripts/hub_fetch.py`           | 7平台热榜聚合                                    |
| `scripts/cn30_search.py`         | 小红书/抖音/公众号近30天讨论搜索 + HTML 报告生成 |
| `scripts/geo_search.py`          | AI 搜索批量调度器                                |
| `scripts/geo_analyze.py`         | GEO 确定性分析 + 合并分析                        |
| `scripts/geo_report.py`          | GEO HTML 报告生成                                |
| `scripts/lib/platforms.py`       | AI 平台适配器                                    |
| `scripts/lib/analyzer.py`        | GEO 分析逻辑库                                   |
| `scripts/lib/report_template.py` | GEO HTML 模板库                                  |

### 参考资料

| 文件                                 | 何时加载            |
| ------------------------------------ | ------------------- |
| `references/cn30-output-rules.md`    | 生成 cn30 报告时    |
| `references/hub-instructions.md`     | 处理 hub 用户指令时 |
| `references/hub-output-templates.md` | 输出 hub 报告时     |
| `references/hub-prediction-logic.md` | 做趋势预测时        |
| `references/geo-metrics.md`          | 计算 GEO 指标时     |

---

## 常见问答

**Q: 三个模块必须都用吗？**
A: 不必。根据路由决策树按需调用。简单场景用一个模块即可，复杂诊断才用组合工作流。

**Q: 为什么不把三个模块的脚本合并成一个 CLI？**
A: 三个数据源、调用逻辑、输出格式差异较大。脚本独立性更高，便于单独维护和升级。当一个数据源失败时不影响其他模块。

**Q: 升级某个模块怎么办？**
A: 单模块独立升级只需替换 `scripts/` 下对应文件 + 更新对应 `references/` 文档。统一 SKILL.md 不需要改动。

**Q: 这三个模块能直接拿到本工作区使用吗？**
A: 是的。skill 安装在 `~/.workbuddy/skills/brand-geo-analysis-plus/`，所有 WorkBuddy 会话和 workspace 都可使用。
