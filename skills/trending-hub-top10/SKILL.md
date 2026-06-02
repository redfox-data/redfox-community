---
name: trending-hub-top10
description: 基于每小时收录的抖音、微博、B站、快手、知乎、头条、百度等7大平台热点数据，聚合全网最热TOP10热点。支持回溯近7天热点。不支持具体热点的查询。
dependency:
  python:
    - python-dateutil==2.8.2
  system:
    - mkdir -p output
---

# 全网聚合热点榜

## 1. 简介

**一句话定位**：全网聚合热点TOP10榜，基于每小时收录的7大平台热点数据，通过智能事件识别和跨平台归并，输出综合热度最高的TOP10热点事件。

**核心价值**：解决内容创作者、市场运营者在热点追踪中的三大痛点：
- **热点分散难整合**：无需逐个平台查看，一次聚合7大平台热榜
- **跨平台对比困难**：自动识别同一事件在不同平台的讨论差异和热度表现
- **趋势判断模糊**：基于热度值、上榜时长、平台覆盖等维度智能预测热点走势

**适用对象**：内容创作者、市场运营人员、媒体编辑、品牌策划、数据分析师。

**不支持**：该技能不支持查询特定热词详情，仅提供全网热点榜聚合查询。

## 2. 功能特性

### 核心功能

| 功能模块 | 能力描述 | 核心价值 |
|----------|----------|----------|
| 🔍 全网热榜聚合 | 实时抓取7大平台热搜数据 | 一键获取全网热点，告别逐平台查看 |
| 🔗 跨平台事件识别 | 智能识别同一事件在不同平台的表述 | 自动归并相似话题，避免重复统计 |
| 📊 热度趋势预测 | 基于热度值、时长、平台覆盖预测走势 | 提前判断热点生命周期，把握创作窗口 |
| 📈 TOP10榜单提供 | 按综合热度排序输出TOP10热点 | 快速定位高价值选题 |
| 💬 跨平台讨论分析 | 展示不同平台的讨论焦点和差异 | 深度洞察舆论生态，精准定位受众 |
| 📄 HTML报告导出 | 生成美观的可视化报告 | 支持图片导出，便于分享存档 |
| ⏰ 订阅推送服务 | 定时推送最新热榜/昨日热榜 | 持续追踪热点动态，不错过关键机会 |

### 特色亮点

- **智能事件识别**：从所有标题中独立识别和归纳具体热点事件，不直接使用原标题
- **可视化HTML报告**：自动生成精美HTML报告，支持PDF/图片导出
- **跨平台讨论对比**：展示同一事件在不同平台的讨论焦点和差异
- **热度趋势预测**：综合分析热度值、上榜时长、排名变化，输出趋势预测

## 3. 一键安装

### 鉴权

#### 获取 API Key

请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取API KEY

#### 配置 API Key

方案1: 以OpenClaw为例，将REDFOX_API_KEY添加到~/.openclaw/openclaw.json中，部分内容如下：

```bash
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }
```

方案2: 终端配置：

```bash
export REDFOX_API_KEY="ak_xxxx..."
```

### 依赖安装

```bash
pip install python-dateutil==2.8.2
mkdir -p output
```

### 环境变量配置

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `REDFOX_API_KEY` | 红狐 API Key | 是 |

## 4. 使用指南

### 基础使用

#### 查询最新热榜（默认）

```bash
python scripts/fetch_hotspot.py --output json
```

自动计算当前时间的前一个小时作为查询范围。例如：当前时间为 `2026-04-16 08:30:00`，则查询 `2026-04-16 07:00:00` 到 `2026-04-16 08:00:00` 的数据。

#### 查询历史热榜

```bash
# 查询昨日热榜（假设今天是2026-04-16）
python scripts/fetch_hotspot.py --start-date "2026-04-15 00:00:00" --end-date "2026-04-16 00:00:00"
```

**日期范围规则**：
- 时间格式为 `YYYY-MM-DD HH:MM:SS`，也可简写为 `YYYY-MM-DD`（自动补全为 00:00:00）
- 日期范围是 `[start_date, end_date)` 左闭右开区间
- 最长查询范围：**7天**

### 高级使用

#### 标准执行流程

**重要原则：智能体完成数据分析并保存JSON后，直接生成HTML报告，不在对话中输出详细榜单。**

1. **获取热点数据**：调用脚本获取原始JSON数据
2. **智能体分析并保存JSON**：执行热点事件识别，按热度值降序排列取TOP10，保存为 `structured_report.json`
3. **自动生成HTML报告**：`python scripts/generate_html_report.py --input structured_report.json --output 热点榜报告.html`
4. **对话中输出简要信息**：标题 > 统计时间 > HTML报告 > 订阅推送服务询问

#### 智能体时间判断逻辑

| 用户意图 | 查询方式 |
|----------|----------|
| "今日热榜" / "今日热点" | 查询今日0:00到当前整点：`--start-date "T 00:00:00" --end-date "T {当前小时}:00:00"` |
| "最新热榜" / "热点榜" | 查询当前时间前一小时：`--start-date "T {当前小时-1}:00:00" --end-date "T {当前小时}:00:00"` |
| "昨日热榜" / "昨天热榜" | `--start-date "T-1 00:00:00" --end-date "T 00:00:00"` |
| "近7天热榜" / "一周热榜" | `--start-date "T-7 00:00:00" --end-date "T 00:00:00"` |
| "X月X日热榜" | `--start-date "X月X日 00:00:00" --end-date "X月X日+1天 00:00:00"` |

**对比查询**：需分别查询多天数据，不能合并查询：

```bash
# 对比昨天和今天的热榜（假设今天是2026-04-16）
python scripts/fetch_hotspot.py --start-date "2026-04-15 00:00:00" --end-date "2026-04-16 00:00:00"  # 昨日
python scripts/fetch_hotspot.py --start-date "2026-04-16 00:00:00" --end-date "2026-04-17 00:00:00"  # 今日实时
```

#### 热点事件识别规则

**核心原则：完全忽略接口返回的keyword和分类，独立从所有标题中识别并归纳具体热点事件。**

识别流程（必须按顺序执行）：
1. **收集所有标题**：遍历 `hotspots` 数组，提取 `title` 和 `platName`
2. **识别具体事件**：判断标题是否描述同一事件（相同主体、相同事件核心、时间连续性）
3. **归纳事件热词**：为每个事件提炼简洁热词（5-15个字）
   - ✅ 正确：U20女足中日对决、2026大学排名发布
   - ❌ 错误：中国相关热点、体育新闻
4. **按热度值排序**：取TOP10

#### 热度值处理与输出规范

- **热度换算**：`maxHotScore // 10000`（整数除法），拼接"万"。例如：9384468 → 938万
- **热度值格式**：必须是"数字+万"，禁止包含其他字符
- **持续时长**：`topOfTheDayTime` 为 0 时显示"刚上热搜"，否则显示"{N}h"
- **URL链接**：有 `url` 时显示为超链接，无URL时仅显示文本
- **平台图标**：使用emoji区分（微博🌐、抖音🎵、知乎📚、B站📺、快手🎬、头条📰、百度🔍）

#### 综合预测规则

| 热度范围 | 预测emoji | 说明 |
|----------|-----------|------|
| ≥ 1000万 | 🔥🔥🔥 | 爆款 |
| 500-999万 | 🔥🔥 | 高热 |
| 100-499万 | 🔥 | 中等 |
| < 100万 | 📉 | 低热 |

预测内容不少于30字，需根据话题类型（突发事件/娱乐八卦/社会民生/行业动态）、热度值、上榜时长、平台覆盖表现综合分析。

#### 结构化报告JSON格式

智能体完成分析后保存为 `structured_report.json`：

```json
{
  "query_range": { "start_date": "...", "end_date": "..." },
  "hotspots": [
    {
      "rank": 1,
      "title": "归纳的事件热词",
      "hot_score": "938万",
      "platform_count": 4,
      "duration": "14h",
      "max_position": 3,
      "platforms": ["微博", "抖音", "头条", "快手"],
      "discussions": [
        {
          "platform": "微博",
          "focus": "讨论焦点描述，不少于10个字",
          "topics": [{"title": "原始标题1", "url": "https://..."}]
        }
      ],
      "prediction": "预测内容文字",
      "prediction_emoji": "🔥🔥🔥"
    }
  ]
}
```

**关键规则**：
- `discussions` 必须覆盖 `platforms` 中所有在榜平台
- `hot_score` 必须为"数字+万"格式
- 每个平台的讨论焦点不少于10个字
- 每个平台展示2-3个具体话题标题

### 命令速查表

| 场景 | 命令 |
|------|------|
| 最新热榜 | `python scripts/fetch_hotspot.py --output json` |
| 今日热榜 | `python scripts/fetch_hotspot.py --start-date "T 00:00:00" --end-date "T HH:00:00" --output json` |
| 昨日热榜 | `python scripts/fetch_hotspot.py --start-date "T-1 00:00:00" --end-date "T 00:00:00" --output json` |
| 生成HTML报告 | `python scripts/generate_html_report.py --input structured_report.json --output 热点榜报告.html` |

### 数据结构说明

```json
{
  "status": "success",
  "stat_time": "2026-04-16 08:30:00",
  "query_range": { "type": "realtime", "start_date": "...", "end_date": "..." },
  "total_count": 50,
  "hotspots": [
    {
      "hotId": "0DFEC...",
      "title": "匈牙利总理用三个最描述中国",
      "platName": "头条",
      "plat": 11,
      "url": "https://www.toutiao.com/trending/...",
      "firstRankTime": "2026-04-15 21:00:00",
      "latestRankDate": "2026-04-16 00:00:00",
      "maxHotScore": 4427099,
      "maxPosition": 15,
      "topOfTheDayTime": "3",
      "source_keyword": "中国"
    }
  ]
}
```

| 字段 | 含义 | 可分析维度 |
|------|------|-----------|
| hotId | 热点唯一ID | - |
| title | 热点标题 | 事件识别、跨平台归并 |
| platName | 平台名称 | 平台覆盖分析 |
| plat | 平台代码 | - |
| url | 跳转链接 | 查看详情、跳转访问 |
| firstRankTime | 首次上榜时间 | 热点发酵起点、时效性 |
| latestRankDate | 最新上榜日期 | 热点是否仍在榜 |
| maxHotScore | 最高热度值 | 热度排行、热度对比 |
| maxPosition | 最高排名位置 | 热度峰值、排名变化 |
| topOfTheDayTime | 榜单停留时长(小时) | 热度持续性、生命周期预测 |
| source_keyword | 接口分组关键词 | 仅供参考，不用于输出 |

**可分析维度**：
- 停留<3小时：短期热点，快速衰减
- 停留3-10小时：中等持续
- 停留>10小时：长期热点，持续发酵

## 5. 使用场景

### 场景一：内容创作者选题决策

**角色**：短视频/自媒体创作者
**需求**：每天早晨快速了解全网最热的10个话题，判断哪个值得创作
**使用方式**：输入"今日热点"，获取TOP10聚合热点 + HTML可视化报告
**预期收益**：5分钟内定位高价值选题，提升内容曝光率

### 场景二：品牌舆情监测

**角色**：品牌公关经理
**需求**：快速了解当前最热事件中是否涉及自家品牌或竞品
**使用方式**：查看全网聚合TOP10，关注跨平台讨论差异
**预期收益**：第一时间发现潜在舆情信号，及时制定应对策略

### 场景三：热点趋势研究

**角色**：数据分析师/研究员
**需求**：分析近期热点演变趋势，输出热点研究报告
**使用方式**：查询近7天热榜数据，生成HTML报告用于分享汇报
**预期收益**：基于数据的热点趋势分析，支持决策和报告撰写

### 场景四：运营活动策划

**角色**：活动运营策划
**需求**：借势当前最热话题策划营销活动
**使用方式**：查看TOP10热点 + 热度趋势预测，选择处于上升期的热点借力
**预期收益**：精准借势热点，提升活动参与度和传播效果

## 6. 项目架构

### 目录结构

```
trending-hub-top10/
├── SKILL.md                        # 技能描述文件
├── scripts/
│   ├── fetch_hotspot.py            # 热点数据获取脚本
│   └── generate_html_report.py     # HTML报告生成脚本
├── references/
│   ├── output-templates.md         # 输出格式模板参考
│   └── prediction-logic.md         # 热度趋势预测规则
└── assets/
    └── report-template.html        # HTML报告模板
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 脚本语言 | Python 3 | 数据获取与报告生成 |
| 外部依赖 | python-dateutil | 日期处理 |
| 数据接口 | Redfox API | 多平台热点数据聚合 |
| 报告模板 | HTML/CSS/JS | 可视化HTML报告 |
| 输出格式 | JSON / HTML | 结构化数据和可视化报告 |

### 核心模块说明

| 模块 | 功能 |
|------|------|
| `fetch_hotspot.py` | 从API获取多平台热点数据，支持时间范围查询 |
| `generate_html_report.py` | 读取 structured_report.json 生成HTML报告（参数：--input JSON路径 --output输出路径） |
| `output-templates.md` | HTML报告格式参考模板 |
| `prediction-logic.md` | 热度趋势预测规则参考 |
| `report-template.html` | HTML报告模板，用于渲染最终报告 |

### 资源索引

- 脚本: 见 [scripts/fetch_hotspot.py](scripts/fetch_hotspot.py)（用途与参数：从API获取热点数据）
- 脚本: 见 [scripts/generate_html_report.py](scripts/generate_html_report.py)（用途与参数：读取structured_report.json生成HTML报告，参数--input JSON路径 --output输出路径）
- 参考: 见 [references/output-templates.md](references/output-templates.md)（何时读取：HTML报告格式参考）
- 参考: 见 [references/prediction-logic.md](references/prediction-logic.md)（何时读取：生成热度趋势预测时参考预测规则）
- 资产: 见 [assets/report-template.html](assets/report-template.html)（直接用于生成：HTML报告模板）

## 7. 常见问答

### 安装相关

**Q: 脚本运行报错 "ModuleNotFoundError: No module named 'dateutil'"**
A: 请安装依赖：`pip install python-dateutil==2.8.2`

**Q: 提示 "REDFOX_API_KEY not found"**
A: 请确保已配置环境变量 `REDFOX_API_KEY`，可参考上方鉴权章节配置。

### 使用相关

**Q: TOP10的排序依据是什么？**
A: 按热度值（maxHotScore）降序排列，热度最高的排第1位。排序前必须逐一核对热度值是否递减。

**Q: 为什么有些热点只在一个平台出现？**
A: 这是正常现象。不同平台有不同用户群体和内容偏好，一些热点可能只在特定平台发酵。

**Q: 对话中为什么看不到详细榜单？**
A: 本技能设计为对话中仅输出简要信息（标题、统计时间、订阅提示），详细内容在HTML报告中展示，方便分享和导出。

**Q: 支持查询多久之前的数据？**
A: 最长查询范围为7天。

### 故障排除

**Q: HTML报告生成失败？**
A: 请检查：1) `structured_report.json` 是否存在且格式正确；2) `discussions` 是否覆盖了所有platforms中的平台；3) 热度值格式是否正确（"数字+万"）。

**Q: 报告中的热度值与对话不一致？**
A: 请确保 `structured_report.json` 中的数据与对话输出完全一致。HTML报告脚本只负责模板渲染，不进行数据分析。

**Q: 事件识别不准确？**
A: 热点事件识别由AI完成。如果识别不准确，请尝试使用更具体的时间范围查询，或使用 trending-hub 技能查看按平台分类的榜单。
