---
name: ai-intelligence-investigator
description: "深度A股情报调查与分析工具，支持A股情报调查、竞品分析、舆情监测、人物背景调查、信息交叉验证，生成结构化调查报告。当用户需要调查A股公司/行业/概念、调查竞品、追踪热点事件、了解人物背景、验证信息真实性时使用。触发词：A股情报、股票调查、财报分析、概念追踪、资金流向、情报调查、竞品分析、舆情调查、背景调查、信息验证、多源搜索。"
---

# A股情报调查员

## 📝 简介

深度A股情报调查与分析工具，帮你快速完成公司研究、竞品对比、事件追踪、背景核实和信息验证，输出结构化调查报告。核心聚焦A股市场：覆盖上市公司基本面、行业产业链、概念热点、资金流向、公告研报、股吧舆情等全方位情报分析。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|----------|
| A股情报调查 | 获取上市公司财报、公告、研报、行业政策、资金流向、股吧舆情等全面信息 | A股投资决策参考 |
| 竞品情报调查 | 调查竞品产品功能、用户口碑、市场表现 | 全面了解竞争对手 |
| 舆情事件调查 | 事件还原、多视角收集、时间线重建 | 追踪热点事件真相 |
| 人物背景调查 | 基本信息核实、专业验证、信誉排查 | 商务合作前风险评估 |
| 信息交叉验证 | 信息溯源、多方比对、权威验证 | 确认信息真实性 |
| 可信度标注 | 为调查结果标注可信度等级，区分已确认/待确认/已否定/单一来源 | 量化信息可靠程度 |

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
2. **调查规划**：制定调查方案与信息获取计划
3. **信息采集**：广泛收集相关信息与数据
4. **深入调查**：针对关键维度深入挖掘细节
5. **信息核实**：核实关键数据的准确性与可信度
6. **报告生成**：输出结构化调查报告，保存至红狐平台

> 完整执行流程详见 `references/core_workflow.md`

## 🔍 调查模式

| 模式 | 调查目标 | 搜索策略与输出模板 |
|------|---------|------------------|
| A股情报调查 | A股公司基本面、行业赛道、概念热点、资金动态、公告事件 | [investigation-modes.md](references/investigation-modes.md) |
| 竞品情报调查 | 分析竞品产品、市场策略、用户口碑 | [investigation-modes.md](references/investigation-modes.md) |
| 舆情事件调查 | 热点事件追踪、舆论走向分析、危机监测 | [investigation-modes.md](references/investigation-modes.md) |
| 人物背景调查 | 商务合作前的背景调查、行业人物了解 | [investigation-modes.md](references/investigation-modes.md) |
| 信息交叉验证 | 验证信息真实性、对比不同来源说法 | [investigation-modes.md](references/investigation-modes.md) |

> 每种模式的详细调查策略与报告模板详见 `references/core_workflow.md`

## ⚠️ 可信度标注

| 标识 | 含义 |
|------|------|
| ✅ 已确认 | 信息可靠 |
| ⚠️ 待确认 | 有争议 |
| ❌ 已否定 | 信息不实 |
| 🔍 单一来源 | 需进一步验证 |

> 详细判定标准与信息源分级说明见 `references/core_workflow.md`

## 💡 使用场景

| 场景 | 角色 | 示例问法 | 收益 |
|------|------|---------|------|
| A股投资决策 | 个人投资者 | 「帮我调查一下宁德时代这家公司」 | 获取公司基本面、财务、行业地位全景分析 |
| 竞品分析 | 产品经理 | 「帮我调查一下 Notion 这个产品」 | 了解竞品功能、用户口碑与市场表现 |
| 热点追踪 | 内容运营/媒体人 | 「追踪最近的XX事件舆论走向」 | 还原事件时间线，掌握舆论分布 |
| 商务合作 | 企业BD/投资人 | 「调查一下XX公司创始人的背景」 | 评估合作风险，核实专业背景 |
| 信息验证 | 所有人 | 「验证"XX公司获得10亿融资"是否属实」 | 多方核实，确认信息真实性 |

## 📚 参考文档

- [core_workflow.md](references/core_workflow.md) — 完整执行流程与调查方法
- [investigation-modes.md](references/investigation-modes.md) — 五种调查模式的详细策略与输出模板
- [engine-strategy.md](references/engine-strategy.md) — 调查策略详解
- [investigation-templates.md](references/investigation-templates.md) — 调查报告完整模板集
