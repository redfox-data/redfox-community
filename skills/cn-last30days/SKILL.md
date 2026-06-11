---
name: cn-last30days
version: "2.0.0"
description: "中国社媒平台话题研究工具。从小红书、抖音、公众号三大平台搜索近30天真实讨论，跨平台对比分析舆情趋势。当用户需要研究中国社交媒体热点话题、分析舆情趋势、对比品牌口碑时使用。触发词：小红书热点、抖音趋势、公众号舆情、跨平台分析、社媒研究、话题分析、舆情监测。"
argument-hint: 'cn-last30days AI视频工具 | cn-last30days 大模型 | cn-last30days 小红书运营'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
homepage: https://github.com/redfox-data/redfox-community/cn-last30days-skill
repository: https://github.com/redfox-data/redfox-community
author: redfox-community
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "🇨🇳"
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
      - xiaohongshu
      - douyin
      - wechat
      - gzh
      - trends
      - social-media
      - analysis
---

# Last 30 Days—CN版

## 📝 简介

Last 30 Days—CN版 是中国社交媒体话题研究工具，从小红书、抖音、公众号三大平台搜索近30天真实讨论数据，通过跨平台对比分析舆情趋势。支持通用话题研究和实体对比两种模式，输出结构化研究报告和可视化 HTML。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|---------|
| 三平台数据源 | 小红书、抖音、公众号真实数据 | 多维度舆情视角 |
| 关键词研究 | 支持多词组合查询（英文逗号分隔） | 灵活话题覆盖 |
| 跨平台对比 | 自动综合三平台数据生成洞察 | 发现差异化趋势 |
| 对比 | A vs B 结构化对比分析 | 辅助决策判断 |
| HTML 报告 | 交互式可视化报告生成 | 便于分享传播 |
| 历史回溯 | 支持近30天任意日期数据 | 追踪趋势演变 |

## 🔑 鉴权

脚本内置免费公共 Key，开箱即用。如需更高额度，从 [红狐数据](https://www.redfox.hk/settings/api-keys?source=github) 获取个人 Key 并配置环境变量：

```bash
export REDFOX_API_KEY=ak_你的密钥
```

优先级：命令行 `--api-key` > 内置公共 Key > `REDFOX_API_KEY` / `X_API_KEY` 环境变量。

---

## 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必填，多词用英文逗号分隔） | - |
| `--platforms` | 平台列表（不建议缩减） | `xhs,dy,gzh` |
| `--count` | 每平台条数 | `50` |
| `--days` | 时间范围，看近期趋势可设7 | `30` |
| `--output-format` | `json` / `html` / `both` | `json` |
| `--output-dir` | 输出目录 | `~/Documents/CnLast30Days` |

**平台信号解读：**

| 平台 | 内容特征 | 关键指标 |
|------|---------|---------|
| 小红书 (xhs) | 种草体验、教程攻略、用户反馈 | 收藏/点赞比高=种草信号 |
| 抖音 (dy) | 热点追评、知识碎片、情绪传播 | 分享数=传播力 |
| 公众号 (gzh) | 行业深度分析、观点输出、数据报告 | 阅读量=关注度，分享=认同 |

---

## 工作流程

### 1. 环境检查

脚本内置公共 Key 有免费额度，直接使用即可。如内置 Key 不可用且无 `REDFOX_API_KEY` / `X_API_KEY` 环境变量，提示用户：
> 请配置 API Key：`export REDFOX_API_KEY=ak_你的密钥`，注册地址 https://www.redfox.hk/login

### 2. 关键词质量检查

运行引擎前检查话题是否过于模糊（如"工具"、"方法"），若是则请用户具体化。

### 3. 预研究

调用引擎前，并行运行 2-3 个 WebSearch 提取热词和背景：

- `小红书 {TOPIC} 热门讨论` → 提取小红书热词
- `抖音 {TOPIC} 热门话题` → 提取抖音标签
- `{TOPIC} 最新动态` → 补充时效背景

### 4. 查询计划

根据预研究决定查询策略：
- 优先将相关关键词合并为一次调用（如 `"产品经理,AI产品经理"`）
- 每平台最多5个词，只在话题维度差异极大时才分开调用
- 默认只调用 1 次引擎

### 5. 运行引擎

```bash
python3 scripts/cn_last30days.py "{TOPIC},{SUBTOPIC}" \
  --platforms xhs,dy,gzh \
  --count 50 \
  --days 30 \
  --output-format json \
  --output-dir="${CN_LAST30DAYS_MEMORY_DIR:-$HOME/Documents/CnLast30Days}"
```

**前台运行，5分钟超时，不要后台。** 读取完整输出，包含三平台的标题、作者、互动数据和链接。

### 6. WebSearch 补充

引擎完成后补充 1-2 个 WebSearch，覆盖知乎、B站、36氪等引擎未覆盖的来源。排除 xiaohongshu.com / douyin.com / mp.weixin.qq.com（已被引擎覆盖）。

### 7. 综合输出

按 [输出规则](references/output-rules.md) 生成研究报告。核心原则：
- 按话题/故事综合，非按平台罗列
- 多平台交叉验证的结论置信度最高
- 高互动内容权重最高（含真实用户信号）
- 每个叙事段落以粗体标题开头，后跟 ` - ` 和正文
- 引用必须为可点击的 Markdown 链接

综合报告完成后，询问用户是否需要 HTML。如需要：

```bash
# 1. 写入 Markdown 报告
cat > "${CN_LAST30DAYS_MEMORY_DIR:-$HOME/Documents/CnLast30Days}/cn30days_{TOPIC}_report.md" << 'REPORT_EOF'
{综合报告全文}
REPORT_EOF

# 2. 从 JSON + 报告生成 HTML（不调 API）
python3 scripts/cn_last30days.py --from-json "JSON文件路径" --report-file "报告Markdown路径" \
  --output-dir="${CN_LAST30DAYS_MEMORY_DIR:-$HOME/Documents/CnLast30Days}"
```

---

## 其他资源

- [输出规则与模板](references/output-rules.md) - 输出规则（LAW）、通用/对比查询输出格式模板
- [脚本文件](scripts/cn_last30days.py) - Python 引擎（Python 3.8+，仅标准库）
