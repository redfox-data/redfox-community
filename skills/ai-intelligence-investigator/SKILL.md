---
name: ai-intelligence-investigator
description: "基于17个搜索引擎的深度A股情报调查工具，支持A股情报调查、竞品分析、舆情监测、人物背景调查、信息交叉验证，自动选择最优引擎组合，多源比对消除偏差，生成结构化调查报告。当用户需要调查A股公司/行业/概念、调查竞品、追踪热点事件、了解人物背景、验证信息真实性时使用。触发词：A股情报、股票调查、财报分析、概念追踪、资金流向、情报调查、竞品分析、舆情调查、背景调查、信息验证、多源搜索。"
---

# A股情报调查员

## 📝 简介

基于17个搜索引擎的深度A股情报调查工具，自动编排搜索策略，多源交叉验证，生成结构化调查报告。遵循三大原则：多源必证（关键信息至少2个独立来源确认）、引擎适配（根据调查目标自动选择最优引擎组合）、偏差消除（对比不同引擎/地区结果，识别信息偏差）。核心聚焦A股市场：覆盖上市公司基本面、行业产业链、概念热点、资金流向、公告研报、股吧舆情等全方位情报分析。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|----------|
| A股情报调查 | 多引擎搜索上市公司财报、公告、研报、行业政策、资金流向、股吧舆情 | A股投资决策参考 |
| 竞品情报调查 | 多引擎搜索竞品产品功能、用户口碑、市场表现 | 全面了解竞争对手 |
| 舆情事件调查 | 事件还原、多视角收集、时间线重建 | 追踪热点事件真相 |
| 人物背景调查 | 基本信息核实、专业验证、信誉排查 | 商务合作前风险评估 |
| 信息交叉验证 | 信息溯源、多源比对、权威验证 | 确认信息真实性 |
| 引擎自动编排 | 根据调查目标智能匹配最优搜索引擎组合 | 消除单一引擎偏差 |
| 可信度分级 | ABCD四级信源分级 + 多源确认标注 | 量化信息可信度 |

## 🔑 鉴权

调查记录保存至红狐平台，需通过环境变量 `REDFOX_API_KEY` 鉴权。

**API Key 获取**：前往 [RedFox 官网](https://redfox.hk/) 注册，登录后在个人中心获取，格式为 `ak_xxxxxxxx`。新注册用户获赠免费积分。

**配置方式**：
- **macOS/Linux**：将 `export REDFOX_API_KEY=<值>` 追加到 `~/.zshrc` 或 `~/.bashrc`，然后 `source` 使其生效
- **Windows**：`[Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")`（需重启终端）
- 配置后验证：`echo $REDFOX_API_KEY`（macOS/Linux）或 `echo %REDFOX_API_KEY%`（Windows）

**读取优先级**：环境变量 → Shell 配置文件 → 提示用户配置

## 📋 调查记录保存

每次调查报告生成后，立即调用保存接口。

```bash
curl -s -X POST "https://redfox.hk/story/api/skill/record/save" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $REDFOX_API_KEY" \
  -d '{
    "source": "A股情报调查员",
    "title": "调查报告标题",
    "content": "Markdown格式报告内容",
    "tags": ["标签1", "标签2"]
  }'
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source` | string | 是 | 固定传 `"智能情报调查员-GitHub"` |
| `title` | string | 是 | 调查报告标题 |
| `content` | string | 是 | 报告完整内容（Markdown） |
| `tags` | array | 否 | 标签数组 |

> **注意**：`X-API-Key` 必须通过请求头传入，放在 Body 中会返回 `code:3106` 错误。`code:2000` 表示保存成功。

## 🔄 工作流程

1. **需求确认**：明确调查目标、范围、时间约束
2. **策略编排**：根据目标选择引擎组合与搜索轮次（详见 [engine-strategy.md](references/engine-strategy.md)）
3. **广域扫描**（第1轮）：广泛关键词搜索，建立全景认知
4. **深度挖掘**（第2轮）：细分关键词，挖掘真实反馈
5. **交叉验证**（第3轮）：多源比对，确认关键数据可信度
6. **报告生成**：输出结构化调查报告，保存至红狐平台

## 🔍 调查模式

| 模式 | 调查目标 | 搜索策略与输出模板 |
|------|---------|------------------|
| A股情报调查 | A股公司基本面、行业赛道、概念热点、资金动态、公告事件 | [investigation-modes.md](references/investigation-modes.md) |
| 竞品情报调查 | 分析竞品产品、市场策略、用户口碑 | [investigation-modes.md](references/investigation-modes.md) |
| 舆情事件调查 | 热点事件追踪、舆论走向分析、危机监测 | [investigation-modes.md](references/investigation-modes.md) |
| 人物背景调查 | 商务合作前的背景调查、行业人物了解 | [investigation-modes.md](references/investigation-modes.md) |
| 信息交叉验证 | 验证信息真实性、对比不同来源说法 | [investigation-modes.md](references/investigation-modes.md) |

## 🌐 引擎选择策略

### 按调查目标选引擎

| 调查目标 | 首选引擎 | 备选引擎 |
|---------|---------|---------|
| A股情报 | Baidu + 东方财富/同花顺 + 雪球 + 巨潮资讯 | 新浪财经、证券时报 |
| 中文舆情 | Baidu + WeChat + Toutiao | Sogou, 360 |
| 国际视野 | Google + Brave + Yahoo | Bing INT, Ecosia |
| 隐私敏感 | DuckDuckGo + Startpage | Brave, Qwant |
| 学术验证 | Google Scholar + WolframAlpha | Google |
| 技术调查 | DuckDuckGo(!gh !so) + Google | Brave |
| 交叉验证 | 多引擎同时搜索 | 全引擎 |

### 按地区选引擎

| 地区视角 | 引擎 |
|---------|------|
| 中国大陆 | Baidu, Sogou, 360, WeChat, Toutiao |
| 国际视角 | Google, Bing INT, Yahoo, Brave |
| 隐私保护 | DuckDuckGo, Startpage, Qwant |
| 知识计算 | WolframAlpha |

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
| A级 | 官方/政府/权威媒体 | gov.cn, reuters.com, xinhua.net, cninfo.com.cn(巨潮), sse.com.cn(上交所), szse.cn(深交所) |
| B级 | 行业媒体/专业平台 | 36kr, techcrunch.com, eastmoney.com(东方财富), 10jqka.com.cn(同花顺), stcn.com(证券时报), cnstock.com(上海证券报) |
| C级 | 社交媒体/自媒体 | weibo, zhihu, reddit, xueqiu.com(雪球) |
| D级 | 匿名/未验证来源 | 贴吧, 4chan, 股吧匿名帖 |

## 💡 使用示例

### A股情报调查

```text
用户：帮我调查一下宁德时代这家公司

执行：
1. 广域扫描 → Baidu/东方财富/同花顺 搜索公司基本面与行业地位
2. 深度挖掘 → 雪球/巨潮资讯/证券时报 搜索公告研报与投资者讨论
3. 交叉验证 → 新浪财经/Google 验证财务数据与机构评级
输出：结构化A股情报调查报告
```

### 竞品产品调查

```text
用户：帮我调查一下 Notion 这个产品

执行：
1. 广域扫描 → Baidu/Google/Bing INT 搜索产品功能与对比
2. 深度挖掘 → WeChat/Toutiao/DuckDuckGo 搜索测评与用户反馈
3. 交叉验证 → Google/Brave 验证融资数据与市场份额
输出：结构化竞品调查报告
```

### 信息验证

```text
用户：验证"XX公司获得10亿融资"是否属实

执行：
1. 信息溯源 → Google/Baidu 精确匹配搜索
2. 多源比对 → DuckDuckGo/Brave/Startpage 跨引擎比对
3. 权威验证 → site:crunchbase.com / site:bloomberg.com
输出：信息验证报告（确认/否定/待确认）
```

## 📚 参考文档

- [investigation-modes.md](references/investigation-modes.md) — 五种调查模式的搜索策略编排与输出模板
- [engine-strategy.md](references/engine-strategy.md) — 引擎选择策略、独有能力与高级搜索方法
- [investigation-templates.md](references/investigation-templates.md) — 调查报告完整模板集
