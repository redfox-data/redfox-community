---
name: douyin-top-account
description: 抖音每日最具影响力账号榜单追踪分析工具；日榜每日17:30更新/回溯7天，周榜每周一17:30更新/回溯3周，月榜每月2号9点更新/回溯3月；当用户需要查询抖音账号排名、抖音日榜/周榜/月榜、抖音赛道TOP账号或下载榜单报告时使用
dependency: {}
---

# 抖音热门账号推荐

## 1. 简介

抖音每日最具影响力账号榜单追踪分析工具 -- 基于红狐数据 API，提供抖音全品类 / 分品类账号每日 / 每周 / 每月的表现榜单查询，支持排名查询、赛道筛选、HTML 可视化报告下载与定时订阅推送。

**适用对象**：新手内容创作者、品牌方 / 商务投放人员、MCN 机构 / 内容团队、行业分析师 / 咨询从业者。

---

## 2. 功能特性

**核心功能**：

- 排名查询 -- 查日榜、周榜、月榜 TOP50，支持全品类和分品类
- 赛道筛选 -- 按品类筛选（美食、旅行、科技、游戏等 27 个赛道）
- 报告下载 -- 生成 HTML 可视化报告，支持导出 PDF / 截图
- 定时订阅 -- 设置自动化定时推送，支持日 / 周 / 月频率

**特色亮点**：

- 日榜每日 17:30 更新 / 回溯 7 天，周榜每周一 17:30 更新 / 回溯 3 周，月榜每月 2 号 9 点更新 / 回溯 3 月
- 综合评分算法：根据总粉丝数、新增粉丝增量、新增点赞 / 分享 / 评论加权计算，满分 100
- 赛道模糊匹配：支持自然语言输入（如 "美妆" 自动映射到 "化妆美容"）
- 数据一致性保障：对话展示的数据条数与 HTML 报告严格一致

---

## 3. 一键安装

### 鉴权

#### 获取 API Key

请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取API KEY

#### 配置 API Key

方案1: 以OpenClaw为例，将REDFOX_API_KEY添加到~/.openclaw/openclaw.json中

```bash
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }
```

方案2: 终端配置：export REDFOX_API_KEY="ak_xxxx..."

```bash
export REDFOX_API_KEY="ak_xxxx..."
```

### 依赖安装

无需安装第三方依赖，使用 Python 标准库即可运行。

---

## 4. 使用指南

### 基础使用

**查询榜单数据（默认展示 TOP 20）**：

```bash
python scripts/fetch_rank.py --query "用户原始问题" --limit 20 --output /path/to/data.json
```

脚本会自动解析：
- **时间**：从用户文本识别日 / 周 / 月，未明确则默认日榜
- **日期**：自动计算最新可用日期（日榜 17:30 更新，周榜周一 17:30 更新，月榜每月 2 号 9 点更新）
- **赛道**：支持模糊匹配（如 "美妆" 映射为 "化妆美容"）

**生成 HTML 报告**：

```bash
python scripts/generate_report.py --data /path/to/data.json --limit 20
```

> 重要：HTML 报告展示的数据条数必须与对话中展示的数量保持一致。使用 `deliver_attachments` 交付 HTML 文件。

**查看全部 50 条数据**：

```bash
python scripts/fetch_rank.py --query "用户原始问题" --limit 50 --output /path/to/data_full.json
python scripts/generate_report.py --data /path/to/data_full.json --limit 50
```

### 高级使用

**更新时间与回溯范围**：

| 榜单类型 | 更新时间    | 回溯范围 |
| -------- | ----------- | -------- |
| 日榜     | 每日17:30   | 过去7天  |
| 周榜     | 每周一17:30 | 过去3周  |
| 月榜     | 每月2号9点  | 过去3月  |

**时间边界处理（必须严格遵守）**：
- 查询当日及未来日期：回复「非常抱歉🙏，我们最新的是昨日/上周/上月的数据，将为您提供最接近您需求的昨日/上周/上月热榜。」
- 查询时间早于回溯日期：回复「非常抱歉🙏，目前榜单最多支持回溯「过去7天/过去3周/过去3月」，我将为您查询最接近您需求的时间范围~」

**订阅服务**：

用户确认订阅后，使用 `automation_update` 工具创建自动化任务：
- 日榜：`FREQ=DAILY;BYHOUR=19;BYMINUTE=30`
- 周榜：`FREQ=WEEKLY;BYDAY=MO;BYHOUR=19;BYMINUTE=30`
- 月榜：`FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=16;BYMINUTE=0`

automation prompt 示例：`查询抖音最新日榜（全品类），生成报告并推送给用户`

### 常用指令速查

| 用户意图 | 典型触发词 | 对应操作 |
| -------- | ---------- | -------- |
| 排名查询 | 抖音日榜、周榜、月榜、TOP50、最夯账号、排行榜、最新推荐 | 调用脚本查询并格式化输出 |
| 领域查询 | 美食类/旅行类/游戏类/科技类...抖音排名 | 调用脚本并按赛道筛选 |
| 报告下载 | 下载报告、导出榜单、生成报告 | 运行 generate_report.py 生成 HTML |

### 输出格式

**Markdown 表格模板**：

```
📊 抖音{period_label} · {category_label}
数据日期：{date}
共 {total} 个账号上榜（展示 TOP {displayed} 条）

💡 榜单说明：{warning}{period_update_time}，与实时数据存在差异

📐 综合评分：根据总粉丝数、新增粉丝增量、新增点赞/分享/评论加权计算，满分100

| 排名 | 账号名 | 综合评分 | 总粉丝数 | 新增粉丝 | 新增点赞 | 新增评论 | 新增分享 |
|:---:|--------|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| 🥇 1 | [账号A](https://www.douyin.com/user/xxx) | 96 | 254.06w | 6919 | 24.64w | 6.68w | 13.39w |
| 🥈 2 | [账号B](https://www.douyin.com/user/xxx) | 89 | 113.55w | 1.91w | 7.90w | 4787 | 3.12w |
| 🥉 3 | [账号C](https://www.douyin.com/user/xxx) | 87 | 439.14w | 5859 | 16.51w | 993 | 687 |
```

输出完榜单后追加：

```
⚡ 更多操作
⏺️ 本次榜单完整共 50 条数据，是否需要查看剩余 30 条？

📬 订阅服务
1️⃣ 是否需要订阅每日/周/月的抖音账号最新排名？
2️⃣ 是否需要订阅具体赛道的账号表现？我们支持：个人才艺、生活vlog、财富理财、二次元、居家装修、学习教育、小剧场、数码科技、旅行、美食、化妆美容、动物、亲子、汽车、情感、三农、健康医学、潮流风尚、舞蹈才艺、颜值造型、人文、音乐、影视、身体锻炼、体育、明星娱乐、游戏
```

---

## 5. 使用场景

| 用户分层 | 核心痛点 | 使用方式 |
| -------- | -------- | -------- |
| 新手内容创作者 / 个体运营 | 不知道哪些账号做得好、无从借鉴、不知道自己水平在赛道内所处位置 | 查询 "美食类账号 TOP50"，获取对标参考 |
| 品牌方 / 商务投放人员 | 找达人效率低、数据维度单一、不了解账号历史表现 | 查询 "上周抖音美妆 TOP50"，获取投放候选 |
| MCN 机构 / 内容团队 | 竞品账号情报获取难、无法快速掌握市场动态 | 查询 "最近一周游戏账号涨粉最快"，监控市场 |
| 行业分析师 / 咨询从业者 | 数据获取门槛高、缺乏可视化报告工具 | 生成 "3 月份抖音游戏类榜单分析报告" |

**预期收益**：快速获取赛道动态、识别优质账号、降低投放决策成本、提升内容运营效率。

---

## 6. 项目架构

### 目录结构

```
douyin-top-account/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── fetch_rank.py                 # 查询抖音榜单数据
│   └── generate_report.py            # 生成 HTML 可视化报告
└── references/
    ├── category_map.md               # 赛道映射表与匹配规则
    ├── update_rules.md               # 更新规则与日期计算逻辑
    ├── score_rules.md                # 评分算法说明
    └── api_docs.md                   # API 接口详细文档（技术参考）
```

### 技术栈

| 技术 | 用途 |
| ---- | ---- |
| Python 标准库 | 数据查询与报告生成 |
| 红狐 API | 抖音榜单数据来源 |
| HTML / CSS | 可视化报告渲染 |

### 核心模块说明

- **fetch_rank.py**：接收用户查询参数，调用红狐 API 获取榜单数据，自动解析时间、日期和赛道，输出 JSON 数据文件。
- **generate_report.py**：读取 fetch_rank 输出的 JSON 数据，生成带排名表格、统计卡片、排名算法的 HTML 可视化报告；账号名均可点击跳转抖音主页。

### 资源索引

| 文件 | 用途 |
| ---- | ---- |
| [scripts/fetch_rank.py](scripts/fetch_rank.py) | 查询抖音榜单数据 |
| [scripts/generate_report.py](scripts/generate_report.py) | 生成 HTML 可视化报告 |
| [references/category_map.md](references/category_map.md) | 赛道映射表与匹配规则 |
| [references/update_rules.md](references/update_rules.md) | 更新规则与日期计算逻辑 |
| [references/score_rules.md](references/score_rules.md) | 评分算法说明 |
| [references/api_docs.md](references/api_docs.md) | API 接口详细文档（技术参考） |

---

## 7. 常见问答

### 安装

**Q: 需要安装什么依赖？**
A: 无需安装第三方依赖，使用 Python 标准库即可运行。

**Q: 如何配置 API Key？**
A: 请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API KEY，然后通过环境变量 `REDFOX_API_KEY` 配置。

### 使用

**Q: 日榜数据什么时候更新？**
A: 每日 17:30 更新昨日数据。当前时间未到 17:30 时，脚本会自动取前天数据。

**Q: 支持哪些赛道？**
A: 支持 27 个赛道，完整列表见 [references/category_map.md](references/category_map.md)。

**Q: 数据回溯范围？**
A: 日榜可查过去 7 天，周榜可查过去 3 周，月榜可查过去 3 个月。

**Q: 赛道识别失败怎么办？**
A: 无法识别时，请列出完整赛道列表供用户选择。

**Q: 默认展示多少条数据？**
A: 日榜默认展示 TOP 20，完整 50 条通过报告或追问查看。

### 故障排除

**Q: HTML 报告生成失败？**
A: 确保 workspace 有写权限，且 JSON 数据文件路径正确。

**Q: 数据不一致？**
A: 对话展示多少条，HTML 报告就展示多少条，两者必须一致。如果用户要求查看全部 50 条，需要重新生成完整报告。

---

