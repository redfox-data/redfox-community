---
name: bili-ai-feed
description: "B站AI信息源 — 每日扫描B站AI相关账号，按点赞量发现爆款视频，智能聚类话题后生成包含封面图、互动数据与订阅支持的HTML日报。同时基于热门话题执行AI情报调查，采用多引擎搜索与交叉验证，输出结构化调查报告。当用户需要AI-B站日报、B站爆款、AI-B站热点、B站AI内容、B站AI视频或B站情报时使用。"
---

# B站AI信息源

## 📝 简介

每日自动扫描B站AI创作内容，按点赞量筛选爆款视频，智能聚类后生成HTML日报。同步基于热门话题执行AI情报调查，使用多搜索引擎交叉验证，输出结构化调查报告。

> API 请求均携带 `B站AI信息源-GitHub` 标识。内置公共 API Key，约 10000 次免费额度。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|----------|
| 爆款发现 | 从B站AI相关视频中按点赞量筛选热门内容 | 精准定位高热度AI视频 |
| 智能聚类 | 自动识别话题方向（AI教程、大模型、AI绘画等） | 每天分类由内容动态决定 |
| AI情报调查 | 基于热门话题执行多引擎搜索+交叉验证 | 深度挖掘话题背后的情报 |
| 可视化日报 | 深色主题HTML，封面图+互动数据+视频直链 | 直观展示每日AI热点 |
| 一键订阅 | `--subscribe` 开启每日自动产出 | 日报自动攒在本地文件夹 |

## 🔑 鉴权

数据查询接口通过请求头 `X-API-KEY` 鉴权，Key 从环境变量 `REDFOX_API_KEY` 获取。

**API Key 获取**：前往 [红狐Hub 官网](https://redfox.hk/) 注册，登录后在个人中心获取，格式为 `ak_xxxxxxxx`。新注册用户获赠免费积分。

**配置方式**：
- **macOS/Linux**：将 `export REDFOX_API_KEY=<值>` 追加到 `~/.zshrc` 或 `~/.bashrc`，然后 `source` 使其生效
- **Windows**：`[Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")`（需重启终端）
- 配置后验证：`echo $REDFOX_API_KEY`（macOS/Linux）或 `echo %REDFOX_API_KEY%`（Windows）

查询接口调用时通过 `source` 字段同步记录，无需额外请求保存接口。

## 🔄 工作流程

### 第一步：生成爆款日报

```bash
# 生成今日爆款日报
python3 "$SKILL_PATH/assets/daily_report.py"

# 自定义关注方向
python3 "$SKILL_PATH/assets/daily_report.py" --keywords "AI教程,AI绘画,ChatGPT,AI工具"

# 查看历史某天
python3 "$SKILL_PATH/assets/daily_report.py" --date 2026-06-10

# 订阅 / 取消订阅
python3 "$SKILL_PATH/assets/daily_report.py" --subscribe
python3 "$SKILL_PATH/assets/daily_report.py" --unsubscribe
```

### 第二步：执行AI情报调查

日报生成后，**必须**基于聚类结果中的TOP话题自动执行AI情报调查：

1. 读取聚类结果，选取TOP 3热门话题
2. 为每个话题自动匹配调查模式（竞品/舆情/人物/验证）
3. 按三轮搜索策略执行调查（广域扫描→深度挖掘→交叉验证）
4. 输出结构化调查报告（参照 [investigation-templates.md](references/investigation-templates.md)）

生成的HTML日报保存在 `~/Downloads/QoderReports/`，自动浏览器打开。终端同步输出分类视频表格 + AI情报调查报告。

## 🔍 调查模式

| 模式 | 调查目标 | 推荐引擎 | 适用话题 |
|------|---------|---------|---------|
| 竞品情报调查 | 分析竞品产品、市场策略、用户口碑 | Baidu + Google + WeChat + DuckDuckGo | AI产品、AI工具类话题 |
| 舆情事件调查 | 热点事件追踪、舆论走向分析、危机监测 | Baidu + Toutiao + Google + WeChat | AI热点事件、争议话题 |
| 人物背景调查 | 商务合作前的背景调查、行业人物了解 | Baidu + Google + DuckDuckGo | 核心达人、关键人物 |
| 信息交叉验证 | 验证信息真实性、对比不同来源说法 | Google + DuckDuckGo + Brave + Startpage | 待验证的AI技术/数据 |

## 🌐 引擎选择策略

### 按调查目标选引擎

| 调查目标 | 首选引擎 | 备选引擎 |
|---------|---------|---------|
| 中文舆情 | Baidu + WeChat + Toutiao | Sogou, 360 |
| 国际视野 | Google + Brave + Yahoo | Bing INT, Ecosia |
| 隐私敏感 | DuckDuckGo + Startpage | Brave, Qwant |
| 学术验证 | Google Scholar + WolframAlpha | Google |
| 技术调查 | DuckDuckGo(!gh !so) + Google | Brave |
| 交叉验证 | 多引擎同时搜索 | 全引擎 |

详细引擎能力与高级搜索策略详见 [engine-strategy.md](references/engine-strategy.md)。

## ⚠️ 可信度标注规范

| 标识 | 含义 | 判定标准 |
|------|------|---------|
| ✅ 已确认 | 信息可靠 | 2+个独立来源一致 |
| ⚠️ 待确认 | 有争议 | 来源说法矛盾 |
| ❌ 已否定 | 信息不实 | 权威信源反驳 |
| 🔍 单一来源 | 仅1个来源 | 需进一步验证 |

**信息源分级**：

| 级别 | 类型 | 示例 |
|------|------|------|
| A级 | 官方/政府/权威媒体 | gov.cn, reuters.com, xinhua.net |
| B级 | 行业媒体/专业平台 | 36kr, techcrunch.com |
| C级 | 社交媒体/自媒体 | weibo, zhihu, reddit |
| D级 | 匿名/未验证来源 | 贴吧, 4chan |

## 📊 输出格式

每次运行日报后，终端与对话输出**必须**遵循以下结构化格式：

```
## B站AI信息源 · {日期} 日报

**扫描 {N} 条热门视频，聚类 {M} 个分类**

---

### 分类概览

| 分类 | 数量 | 占比 | 亮点 |
|------|------|------|------|
| #{分类名} | {N}条 | {X}% | 头部视频亮点描述 |
| ... | ... | ... | ... |

---

### AI情报调查报告

**一、新兴起量信号**

- 🔥 **#{话题}** — 仅{N}条但均互动{X}+，描述

**二、核心达人**

| 达人 | 作品数 | 总赞 | 亮点 |
|------|--------|------|------|
| @{作者} | {N}条 | {X}w | 描述 |
| ... | ... | ... | ... |

**三、{话题1} 调查报告**

**调查模式**：{竞品情报调查/舆情事件调查/人物背景调查/信息交叉验证}
**引擎组合**：{引擎1} + {引擎2} + {引擎3}

| 维度 | 发现 | 来源 | 可信度 |
|------|------|------|--------|
| {维度1} | {内容} | {来源} | {A/B/C/D级} |
| ... | ... | ... | ... |

**关键结论**：{已确认/待确认/已否定的信息汇总}

**四、{话题2} 调查报告**

（同上格式）

**五、{话题3} 调查报告**

（同上格式）

**六、跨平台对比建议**

- **{话题}** — 建议同步关注抖音、小红书、公众号同话题热度，用 引擎组合 追踪国内全平台动态

---

**日报地址**：{HTML文件绝对路径}
```

> 以上格式为**强制规范**，所有字段不可省略。若某模块无数据则标注"暂无"。

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 关注的话题方向，逗号分隔 | `AI,人工智能,大模型,GPT,Agent,AI绘画,AI教程` |
| `--count` | 扫描视频数量 | `200` |
| `--date` | 指定日期 YYYY-MM-DD | 今天 |
| `--start-time` | 自定义开始时间 YYYY-MM-DD HH:MM:SS（覆盖 --date 推算） | — |
| `--end-time` | 自定义结束时间 YYYY-MM-DD HH:MM:SS（覆盖 --date 推算） | — |
| `--output-dir` | 输出目录 | `~/Downloads/QoderReports` |
| `--api-key` | 指定 API Key | — |
| `--subscribe` | 开启每日订阅 | — |
| `--unsubscribe` | 关闭每日订阅 | — |
| `--no-open` | ~~已移除~~ 生成后始终自动预览 | — |

## 📚 参考文档

- [engine-strategy.md](references/engine-strategy.md) — 引擎选择策略、独有能力与高级搜索方法
- [investigation-modes.md](references/investigation-modes.md) — 四种调查模式的搜索策略编排与输出模板
- [investigation-templates.md](references/investigation-templates.md) — 调查报告完整模板集
