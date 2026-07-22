---
name: geo-analyzer
description: GEO（生成式引擎优化）品牌分析工具。自动向豆包、Kimi、DeepSeek 三个 AI 搜索引擎提问，分析品牌在 AI 回答中的出现率、情绪、信源引用、竞品对比，生成交互式 HTML 报告。当用户需要分析品牌在 AI 搜索引擎中的表现、GEO 优化、AI 搜索品牌监测、品牌 AI 可见度分析时使用。触发词：GEO分析、品牌AI搜索分析、AI搜索引擎优化、品牌可见度、GEO、geo analyzer。
---

# 品牌GEO分析

## 简介

帮助品牌了解自己在 AI 搜索引擎（豆包、Kimi、DeepSeek）中的表现。系统自动向三个 AI 平台提出相同问题，分析品牌出现率、情绪倾向、信源引用、竞品对比，生成可视化 HTML 报告。

## 鉴权

前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key，通过以下方式配置：

```bash
# 方式一：配置文件
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }

# 方式二：终端环境变量
export REDFOX_API_KEY="ak_xxxx..."
```

## 依赖

```bash
pip3 install requests
```

## 完整工作流

### Step 0: 输入收集

向用户收集以下信息（使用 AskUserQuestion 或直接从用户消息中提取）：

**必填信息：**
- **品牌名称**: 用户要分析的品牌名（如"元气森林"、"大疆"、"蔚来"）
- **品类/行业**: 品牌所属品类（如"无糖饮料"、"无人机"、"新能源汽车"）

**可选信息：**
- **品牌别名**: 品牌的其他常见称呼（如"小红书"的别名"RED"、"小红书App"）
- **竞品列表**: 用户已知竞品（如"可口可乐"、"百事可乐"）
- **自定义问题列表**: 如果用户已有问题列表，直接使用，跳过 Step 1

**关键规则：**
- 如果用户只提供了品牌名没有品类，必须追问品类
- 如果用户提供了问题列表，跳过 Step 1 直接进入 Step 2
- 竞品和别名可以为空

### Step 1: 问题生成（用户未提供问题时）

如果用户没有提供问题列表，需要生成 5 个热门问题。

**1.1 搜索品类热度**

调用任一 websearch skill 搜索品类相关信息：

```bash
python3 ~/.agents/skills/doubao-websearch/scripts/doubao_search.py "{品类} 消费者最关心的问题"
python3 ~/.agents/skills/kimi-websearch/scripts/kimi_search.py "{品类} 品牌推荐 常见问题"
```

**1.2 AI 生成 5 个问题**

结合搜索结果和品类知识，生成 5 个用户最可能在 AI 搜索引擎中提问的问题。

**问题类型必须覆盖以下四类（每类至少 2 个）：**

| 类型 | 示例 | 说明 |
|------|------|------|
| 推荐类 | "{品类}哪个品牌好？"、"推荐几款好用的{品类}" | 测试品牌是否进入推荐列表 |
| 对比类 | "{品牌A}和{品牌B}哪个好？"、"{品类}品牌对比" | 测试品牌在直接对比中的表现 |
| 评价类 | "{品牌}怎么样？"、"{品牌}值得买吗？" | 测试品牌单独评价的倾向 |
| 场景类 | "{场景}用什么{品类}好？"、"新手适合用哪个{品类}？" | 测试品牌在特定场景下的可见度 |

**问题生成规则：**
- 问题必须是用户真实可能搜索的自然语言
- 不要在问题中直接包含用户品牌名（推荐类和场景类），除非是评价类问题
- 评价类问题中可以包含品牌名
- 问题长度控制在 10-30 字
- 不要生成过于相似的问题

**1.3 确认问题列表（必须执行）**

将生成的 5 个问题展示给用户，使用 AskUserQuestion 询问确认。必须等待用户明确同意后，才能进入 Step 2 批量搜索。如果用户要求修改，重新调整问题列表并再次确认。

### Step 2: 批量搜索

将 5 个问题同时提交到 3 个 AI 平台进行联网搜索。

```bash
python3 scripts/geo_search.py --queries '["问题1","问题2",...,"问题10"]' --platforms doubao,kimi,deepseek
```

**脚本自动完成：**
1. 批量提交 15 个搜索任务（3平台 x 5问题）
2. 并行轮询所有任务，每 5 秒检查一次
3. 最长等待 8 分钟
4. 输出 `output/search_results.json`

**输出文件结构：**
```json
{
  "queries": ["问题1", "问题2", ...],
  "platforms": ["doubao", "kimi", "deepseek"],
  "total_tasks": 30,
  "completed": 28,
  "failed": 2,
  "results": [
    {
      "question": "问题1",
      "query_index": 0,
      "platform": "doubao",
      "content": "AI回答全文...",
      "sources": [{"title": "...", "url": "...", "domain": "..."}],
      "status": "completed"
    }
  ]
}
```

**等待提示：** 搜索过程约需 3-5 分钟，告知用户耐心等待。

### Step 3: 确定性分析

运行分析脚本执行确定性分析（品牌提及检测、域名提取、频次统计）：

```bash
python3 scripts/geo_analyze.py \
  --brand "品牌名" \
  --aliases '["别名1","别名2"]' \
  --competitors '["竞品A","竞品B"]' \
  --search-results output/search_results.json
```

**输出两个文件：**
- `output/deterministic.json` — 确定性分析结果（提及率、域名统计等）
- `output/ai_analysis_template.json` — AI 分析模板（待填充）

### Step 4: AI 分析（Agent 执行）

这是核心步骤。Agent 需要读取搜索结果，对每份 AI 回答执行深度分析。

**4.1 读取搜索结果**

读取 `output/search_results.json`，获取所有 15 份 AI 回答。

**4.2 逐份分析**

对每份状态为 `completed` 的回答，分析以下字段：

1. **brand_rank** (int | null): 品牌在回答的推荐列表或排名中的位置。如果回答列举了"推荐5个品牌"，品牌排第几？未提及则为 null。
2. **brand_context** (str): 品牌被提及时的一句话上下文摘要。未提及则为空字符串。
3. **sentiment** (str): 回答对该品牌的整体情绪倾向。
   - `"positive"`: 正面/推荐/强调优势
   - `"neutral"`: 中性/客观描述
   - `"negative"`: 负面/强调劣势/不推荐
   - 未提及则为 `"neutral"`
4. **sentiment_reason** (str): 情绪判断的依据，引用回答中的原文或概括原因。
5. **competitors_mentioned** (list[str]): 回答中提及的所有竞品品牌名称。不限于已知竞品，发现新竞品也列出。
6. **competitor_details** (list[dict]): 对每个被提及的竞品，提供其排名和情绪信息。格式为列表，每项含:
   - `name` (str): 竞品品牌名
   - `rank` (int | null): 竞品在推荐列表中的排名，无排名则为 null
   - `sentiment` (str): 竞品的情绪倾向 (positive/neutral/negative)
7. **key_claims** (list[str]): 关于该品牌的关键描述或评价（2-3条简短摘要）。

**分析规则：**
- 情绪判断基于回答中对品牌的整体描述，不是单句话
- 如果回答只是列举品牌名没有评价，sentiment 为 "neutral"
- 如果回答明确推荐该品牌或强调其优势，sentiment 为 "positive"
- 如果回答指出该品牌的缺点或不推荐，sentiment 为 "negative"
- competitors_mentioned 应包含回答中出现的所有同品类品牌，即使用户没有列为竞品
- competitor_details 中每个竞品的 rank 和 sentiment 基于回答中对竞品的描述判断
- brand_rank 只在回答有明确的品牌排序时填写（如"第一名是XX，第二名是YY"），无排序则为 null

**4.3 写入 AI 分析结果**

将所有分析结果写入 `output/ai_analysis.json`，格式如下：

```json
[
  {
    "question": "问题1",
    "query_index": 0,
    "platform": "doubao",
    "brand": "品牌名",
    "competitors": ["竞品A", "竞品B"],
    "brand_rank": 3,
    "brand_context": "品牌被提及时的上下文摘要",
    "sentiment": "positive",
    "sentiment_reason": "回答中明确推荐该品牌",
    "competitors_mentioned": ["竞品A", "竞品C"],
    "competitor_details": [
      {"name": "竞品A", "rank": 1, "sentiment": "positive"},
      {"name": "竞品C", "rank": null, "sentiment": "neutral"}
    ],
    "key_claims": ["关键描述1", "关键描述2"]
  }
]
```

**关键规则：**
- 只包含 status 为 completed 的回答
- 每份回答一个 JSON 对象
- query_index 和 platform 必须与 search_results.json 中的对应
- 必须输出合法 JSON

### Step 5: 合并分析与报告生成

**5.1 合并分析**

将确定性分析与 AI 分析合并，计算完整指标（GEO 得分、情绪分布、平均排名等）：

```bash
python3 scripts/geo_analyze.py \
  --brand "品牌名" \
  --aliases '["别名1"]' \
  --competitors '["竞品A","竞品B"]' \
  --search-results output/search_results.json \
  --ai-analysis output/ai_analysis.json
```

输出 `output/analysis_result.json`（包含所有指标数据）。

**5.2 生成 HTML 报告**

```bash
python3 scripts/geo_report.py \
  --analysis output/analysis_result.json \
  --search-results output/search_results.json
```

输出 `output/geo_report.html`。

### Step 6: 交付

1. **交付 HTML 报告文件**: `output/geo_report.html`
2. **输出关键发现摘要**（3-5 条核心结论），格式参考：

```
GEO 分析完成 — {品牌名} 在三大 AI 搜索引擎中的表现：

1. 跨平台提及率: {X}%（{被提及数}/{总问题数}）
   - 豆包: {X}% | Kimi: {X}% | DeepSeek: {X}%

2. GEO 综合得分: {X}/100
   - {最佳平台} 表现最佳（{X}分），{最差平台} 表现最弱（{X}分）

3. 情绪分布: 正面 {X}% | 中性 {X}% | 负面 {X}%
   - {如果有负面，指出主要负面原因}

4. 竞品对比: 共发现 {N} 个竞品
   - 提及率最高的竞品: {竞品名}（{X}%）
   - 您的品牌提及率排名: 第 {N} 位

5. 信源引用: TOP3 引用域名为 {域名1}、{域名2}、{域名3}
   - 品牌官网是否被引用: {是/否}

完整报告: output/geo_report.html
```

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 未配置 REDFOX_API_KEY | 提示用户前往红狐hub获取 API Key |
| 搜索任务部分失败 | 继续分析已完成的回答，在报告中标注失败项 |
| 搜索全部超时 | 提示用户稍后重试，可能是 API 负载过高 |
| AI 分析结果缺失 | 仅生成确定性分析报告（提及率、域名统计），情绪等模块标注"待分析" |
| 品牌名太短导致误匹配 | 提示用户提供品牌别名以提高匹配精度 |

## 文件结构

```
geo-analyzer/
├── SKILL.md                        # 本文件
├── scripts/
│   ├── geo_search.py               # 批量搜索调度器
│   ├── geo_analyze.py              # 分析编排器
│   ├── geo_report.py               # 报告生成器
│   └── lib/
│       ├── platforms.py            # 3平台适配器
│       ├── analyzer.py             # 分析逻辑库
│       └── report_template.py      # HTML 模板库
├── output/                         # 输出目录
│   ├── search_results.json         # 搜索结果
│   ├── deterministic.json          # 确定性分析
│   ├── ai_analysis_template.json   # AI 分析模板
│   ├── ai_analysis.json            # AI 分析结果（Agent 写入）
│   ├── analysis_result.json        # 完整分析结果
│   └── geo_report.html             # 最终报告
└── references/
    └── geo-metrics.md              # GEO 指标定义说明
```
