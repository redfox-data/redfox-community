---
name: geo-analyzer
description: GEO（生成式引擎优化）品牌分析工具。自动向豆包、Kimi、DeepSeek、元宝、千问、百度 六个 AI 搜索引擎提问，分析品牌在 AI 回答中的出现率、情绪、信源引用、竞品对比，生成交互式 HTML 报告。当用户需要分析品牌在 AI 搜索引擎中的表现、GEO 优化、AI 搜索品牌监测、品牌 AI 可见度分析时使用。触发词：GEO分析、品牌AI搜索分析、AI搜索引擎优化、品牌可见度、GEO、geo analyzer。
---

# 品牌GEO分析

## 简介

帮助品牌了解自己在 AI 搜索引擎（豆包、Kimi、DeepSeek、元宝、千问、百度）中的表现。系统自动向六个 AI 平台提出相同问题，分析品牌出现率、情绪倾向、信源引用、竞品对比，生成可视化 HTML 报告。

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
- **品牌别名**: 品牌的其他常见称呼（如"小红书"的别名"RED"）
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

**问题类型必须覆盖以下三类（推荐类至少 1 个，多场景类与功能类合计至少 4 个）：**

| 类型 | 示例 | 说明 |
|------|------|------|
| 推荐类 | "{品类}哪个品牌好？"、"推荐几款好用的{品类}" | 测试品牌是否进入通用推荐列表 |
| 多场景类 | "{人群/场景}用什么{品类}好？"，如"经常熬夜看手机用什么缓解视疲劳眼药水好"、"学生党上课用眼多适合用的缓解视疲劳眼药水有哪些"、"长期对着电脑办公选什么缓解视疲劳眼药水合适" | 测试品牌在真实使用场景下的可见度 |
| 功能类 | "{功能诉求}的{品类}推荐"，如"温和不刺激的缓解视疲劳眼药水推荐"、"缓解视疲劳眼药水哪些好用不贵" | 测试品牌在功能诉求下的匹配度 |

**问题生成铁律：**
- 所有问题一律不带目标品牌名（含别名）——AI 不知道在测谁，结果才客观
- 不生成明确的品牌对比类问题（如"{品牌A}和{品牌B}哪个好"）；与竞品的对比表现可从回答中的竞品提及自然观察
- 多场景类须贴合品牌的真实使用人群与场景（结合品类知识构造互不重复的场景，如不同人群、使用场合、使用强度）
- 功能类围绕该品类用户最关心的功能点或顾虑（如温和不刺激、性价比、便携性）
- 问题必须是用户真实可能搜索的自然语言，长度控制在 10-30 字，不要生成过于相似的问题

**1.3 确认问题列表（必须执行）**

将生成的 5 个问题展示给用户，使用 AskUserQuestion 询问确认。必须等待用户明确同意后，才能进入 Step 2 批量搜索。如果用户要求修改，重新调整问题列表并再次确认。

### Step 2: 批量搜索

将 5 个问题同时提交到 6 个 AI 平台进行联网搜索。

```bash
python3 scripts/geo_search.py --queries '["问题1","问题2",...,"问题5"]' --platforms doubao,kimi,deepseek,yuanbao,qianwen,baidu
```

**脚本自动完成：**
1. 批量提交 30 个搜索任务（6平台 x 5问题）
2. 并行轮询所有任务，每 30 秒检查一次
3. 最长等待 5 分钟
4. 输出 `output/search_results.json`

**输出文件结构：**
```json
{
  "queries": ["问题1", "问题2", ...],
  "platforms": ["doubao", "kimi", "deepseek", "yuanbao", "qianwen", "baidu"],
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

**等待提示：** 搜索过程约需 3-5 分钟，告知用户耐心等待。部分平台任务超时属常见现象，直接用已完成的回答继续分析。

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

读取 `output/search_results.json`，获取所有 30 份 AI 回答。

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
- 同一回答内排名不得重复：brand_rank 与各竞品的 rank 必须互不相同；回答中并列呈现时，按先呈现/更被推荐的一方排前，依次递增（不得出现两个并列第1）

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

输出 `output/geo_report.html`（单页交互式，顶部锚点导航，滚动高亮当前板块）。报告结构：

| 板块 | 内容 |
|------|------|
| 顶部摘要 | 品牌名、GEO 综合得分、提及率、覆盖平台、生成时间 + AI 文字总结（综合评估 / 各平台表现 / 发力方向） |
| 品牌指纹 | GEO 综合、提及率、平均排名、正面率四大指标卡 + 分平台得分卡（得分 / 等级徽章 / 提及率 / 条数）+ 行业位置（#排名 · 参与品牌数） |
| 提及矩阵 | 问题 × 平台热力表：已提及 = 出现次数，未提及 = —，查询失败 = ✕ |
| 情感分析 | 整体分布（正 / 中 / 负）+ 各平台情感对比条 + 正面/负面信号标签 + 非中性回答详情卡（含判断依据） |
| 信源分析 | 引用域名 TOP10（带分类标签，品牌域名高亮 *）+ 引用文章 TOP10（可点击）+ 域名分类占比 + 官网是否进入 TOP10 提示 |
| 竞品对比 | 本品牌行（高亮"本品牌"徽章）+ 竞品按提及率降序（最多 10 个），列为提及率 / 平均排名 / 正面率，点击行展开各平台明细 |
| 原始存档 | 按问题分组展示全部 AI 回答原文（品牌词高亮），每条带平台徽章 + 情绪徽章，失败任务标注 [status] |

**依赖说明：** 情感分析板块依赖 Step 4 写入的 `ai_analysis.json`，缺失时显示"暂无 AI 情感分析数据"占位，报告其余板块照常生成。

### Step 6: 交付

1. **交付 HTML 报告文件**: `output/geo_report.html`
2. **输出关键发现摘要**（3-5 条核心结论），格式参考：

```
GEO 分析完成 — {品牌名} 在六大 AI 搜索引擎中的表现：

1. 跨平台提及率: {X}%（{被提及数}/{总问题数}）
   - 豆包: {X}% | Kimi: {X}% | DeepSeek: {X}% | 元宝: {X}% | 千问: {X}% | 百度: {X}%

2. GEO 综合得分: {X}/100
   - {最佳平台} 表现最佳（{X}分），{最差平台} 表现最弱（{X}分）

3. 情绪分布: 正面 {X}% | 中性 {X}% | 负面 {X}%
   - 正面率 = 1 − 负面率（中性计入正面）
   - {如果有负面，指出主要负面原因}

4. 竞品对比: 共发现 {N} 个竞品
   - 提及率最高的竞品: {竞品名}（{X}%）
   - 您的品牌提及率排名: 第 {N} 位

5. 信源引用: TOP3 引用域名为 {域名1}、{域名2}、{域名3}
   - 品牌官网是否被引用: {是/否}（若某平台整体无信源数据，须说明该平台信源不可用，不要当作"官网未被引用"）

完整报告: output/geo_report.html
```

## 核心指标

详细定义见 `references/geo-metrics.md`。核心公式：

```
GEO 得分 = 提及率得分 × 40% + 排名得分 × 30% + 情绪得分 × 30%
        = 提及率×100 × 40% + max(0, 100 - (均排名-1)×10) × 30%
          + 正面率×100 × 30%（正面率 = 1 − 负面率，中性计入正面）
```

解读：70+ 优秀 / 50-69 良好 / 30-49 一般 / <30 不足。

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 未配置 REDFOX_API_KEY | 提示用户前往红狐hub获取 API Key |
| 搜索任务部分失败/超时 | 属常见现象（DeepSeek/Kimi 可能长时间排队），最长等待5min，超时直接用已完成的回答继续分析，在报告中标注失败项，不要反复重试 |
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
│       ├── platforms.py            # 6平台适配器
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
