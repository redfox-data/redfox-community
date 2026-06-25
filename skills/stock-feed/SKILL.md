---
name: stock-feed
version: "1.0.0"
description: "A股每日新闻。从小红书、抖音、公众号三大平台搜索A股相关短讯，内置17个A股核心关键词一次性查询，默认近7天数据，自动过滤非股票内容，跨平台对比分析股市舆情。当用户需要研究A股舆情、股市讨论、大盘分析、选股策略、涨跌复盘时使用。触发词：A股、A股舆情、股市新闻、大盘分析、涨停、选股、A股复盘、股票讨论、股市热点。"
argument-hint: 'stock-feed | stock-feed --days 30'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
homepage: https://github.com/redfox-data/redfox-community/stock-feed-skill
repository: https://github.com/redfox-data/redfox-community
author: redfox-community
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "📈"
    requires:
      env: []
      optionalEnv:
        - REDFOX_API_KEY
      bins:
        - python3
    primaryEnv: REDFOX_API_KEY
    files:
      - "scripts/*"
    tags:
      - research
      - a-stock
      - stock-market
      - xiaohongshu
      - douyin
      - wechat
      - gzh
      - trends
      - social-media
      - analysis
---

# A股每日新闻

## 📝 简介

A股每日新闻是中国股市舆情研究工具，从小红书、抖音、公众号三大平台一次性搜索17个A股核心关键词（A股、A股市场、A股大盘、涨停、涨跌、潜力股、选股、加仓等），默认拉取近7天真实讨论数据，自动过滤非股票/投资相关内容，跨平台对比分析股市舆情趋势，输出结构化研究报告和可视化 HTML。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|---------|
| 17词一键查询 | 内置A股核心关键词，一次覆盖全话题 | 零配置即用 |
| 三平台数据源 | 小红书、抖音、公众号真实数据 | 多维度舆情视角 |
| 跨平台对比 | 自动综合三平台数据生成洞察 | 发现差异化趋势 |
| 灵活时间范围 | 默认7天，支持自定义1~30天 | 追踪盘中/周度变化 |
| HTML 报告 | 交互式可视化报告生成 | 便于分享传播 |
| 历史回溯 | 支持近30天任意日期数据 | 追踪趋势演变 |

## 🔑 鉴权

脚本需配置 API Key 使用。从 [红狐数据](https://www.redfox.hk/settings/api-keys?source=github) 获取个人 Key 并配置环境变量：

```bash
export REDFOX_API_KEY=ak_你的密钥
```

优先级：命令行 `--api-key` > `REDFOX_API_KEY` / `X_API_KEY` 环境变量 > 配置文件。

---

## 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（可选，不传则使用内置17个A股关键词） | A股,A股市场,A股大盘,... 共17词 |
| `--platforms` | 平台列表（不建议缩减） | `xhs,dy,gzh` |
| `--count` | 每平台条数 | `50` |
| `--days` | 时间范围（默认7天，用户指定时按需传入） | `7` |
| `--output-format` | `json` / `html` / `both` | `json` |
| `--output-dir` | 输出目录 | `~/Downloads/StockFeed` |

**平台信号解读：**

| 平台 | 内容特征 | 关键指标 |
|------|---------|---------|
| 小红书 (xhs) | 散户分享、炒股心得、入门教程 | 收藏/点赞比高=实用信号 |
| 抖音 (dy) | 盘中速评、涨停解读、情绪传播 | 分享数=传播力 |
| 公众号 (gzh) | 深度复盘、策略分析、行业研报 | 阅读量=关注度，分享=认同 |

---

## 工作流程

### 1. 环境检查

运行前需确保已配置 API Key（环境变量 `REDFOX_API_KEY` 或 `--api-key` 参数）。如未配置，提示用户：
> 请配置 API Key：`export REDFOX_API_KEY=ak_你的密钥`，注册地址 https://www.redfox.hk/login

### 2. 关键词处理

- **默认行为**：不传 keyword 参数，脚本自动使用内置17个A股核心关键词
- **用户自定义**：用户明确指定关键词时，传入 `--keyword` 参数覆盖默认值
- 检查关键词是否过于模糊，若是则请用户具体化

### 3. 预研究

调用引擎前，并行运行 2-3 个 WebSearch 提取热词和背景：

- `A股 {TOPIC} 小红书 热门讨论` → 提取小红书热词
- `A股 {TOPIC} 抖音 热门话题` → 提取抖音标签
- `A股 {TOPIC} 最新动态` → 补充时效背景

### 4. 运行引擎

```bash
python3 scripts/stock_feed.py \
  --platforms xhs,dy,gzh \
  --count 50 \
  --days 7 \
  --output-format json \
  --output-dir="${STOCK_FEED_MEMORY_DIR:-$HOME/Downloads/StockFeed}"
```

用户指定关键词时：
```bash
python3 scripts/stock_feed.py "半导体,芯片" \
  --platforms xhs,dy,gzh \
  --count 50 \
  --days 7 \
  --output-format json \
  --output-dir="${STOCK_FEED_MEMORY_DIR:-$HOME/Downloads/StockFeed}"
```

**前台运行，5分钟超时，不要后台。** 读取完整输出，包含三平台的标题、作者、互动数据和链接。

### 5. WebSearch 补充

引擎完成后补充 1-2 个 WebSearch，覆盖雪球、东方财富、同花顺等引擎未覆盖的来源。排除 xiaohongshu.com / douyin.com / mp.weixin.qq.com（已被引擎覆盖）。

### 6. 综合输出

按 [输出规则](references/output-rules.md) 生成研究报告。核心原则：
- **徽章之后、标题之前**，必须输出「数据速览」模块：按公众号→小红书→抖音顺序，每平台展示 TOP5 作品表格（标题作为可点击超链接、作者、平台专属互动指标分列展示（公众号阅读/点赞/转发，小红书点赞/收藏/评论，抖音点赞/评论/分享）），模块末尾展示数据总量和 HTML 报告提示
- 报告以一级标题 `# A股每日新闻` 开头
- 按话题/故事综合，非按平台罗列
- 多平台交叉验证的结论置信度最高
- 高互动内容权重最高（含真实用户信号）
- 每个叙事段落以粗体标题开头，后跟 ` - ` 和正文
- **每条发现必须引用至少2个不同平台的来源**（如：小红书+抖音、公众号+小红书）
- 引用必须为可点击的 Markdown 链接
- 核心发现之后必须附「操作要点预判」和「风险说明」两个固定区块

综合报告完成后，**自动执行**以下步骤生成 HTML 报告（无需询问用户）：

```bash
# 直接从 JSON 生成 HTML（不调 API，不写入 Markdown）
python3 scripts/stock_feed.py --from-json "JSON文件路径" \
  --output-dir="${STOCK_FEED_MEMORY_DIR:-$HOME/Downloads/StockFeed}"

# 自动打开 HTML 报告
open "HTML文件路径"
```

脚本会输出 HTML 文件路径，自动打开后将路径告知用户即可。

---

## 其他资源

- [输出规则与模板](references/output-rules.md) - 输出规则（LAW）、通用/对比查询输出格式模板
- [脚本文件](scripts/stock_feed.py) - Python 引擎（Python 3.8+，仅标准库）
