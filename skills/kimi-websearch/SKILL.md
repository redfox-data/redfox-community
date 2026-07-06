---
name: kimi-websearch
description: Kimi WebSearch 搜索工具。基于红狐 API 调用 Kimi 联网搜索能力，提交查询后自动轮询等待结果返回。当用户需要使用 Kimi 搜索、联网搜索、AI 搜索获取实时信息时使用。触发词：kimi搜索、kimi websearch、联网搜索、AI搜索、kimi搜索。
---

# Kimi WebSearch

## 📝 简介

调用 Kimi 联网搜索能力，和kimi直接对话。适用于需要联网实时搜索、AI 辅助信息检索的场景。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|---------|
| 异步提交 | 提交搜索关键词到 Kimi WebSearch，返回 taskId | 无需等待，立即获取任务标识 |
| 自动轮询 | 每 5 秒查询任务状态，最多等待 5 分钟 | 自动等待结果，无需手动查询 |
| 进度反馈 | 轮询期间通过 stderr 实时输出等待状态 | 用户可知搜索进度 |
| 结果输出 | 状态变为 completed 后输出完整 JSON | 结构化数据便于 Agent 解析展示 |
| 异常处理 | 覆盖 API Key 缺失、提交失败、超时、任务失败四种场景 | 每种异常有明确提示和处理 |

## 🔑 鉴权

前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key，通过以下方式配置：

```bash
# 方式一：配置文件（如 OpenClaw 的 ~/.openclaw/openclaw.json）
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }

# 方式二：终端环境变量
export REDFOX_API_KEY="ak_xxxx..."
```

## 🔄 工作流程

### Step 1：提取搜索关键词

从用户自然语言描述中提取搜索意图和关键词，作为 `inquiry_text` 传入。

### Step 2：调用搜索脚本

```bash
python3 ~/.agents/skills/kimi-websearch/scripts/kimi_search.py "<搜索关键词>"
```

脚本自动完成：
1. **提交搜索**：`POST /story/api/kimi/submit`，传入 `{"inquiry_text": "...", "source": "kimi websearch-GitHub"}`
2. **轮询结果**：每 5 秒 `POST /story/api/kimi/result` 查询一次，直到状态为 `completed`
3. **实时反馈**：轮询期间通过 stderr 输出等待提示
4. **最终输出**：状态 `completed` 后输出完整 JSON 结果到 stdout

### Step 3：展示结果

脚本返回 JSON 后，提取 `data.content` 中的 Kimi 回答文本和 `data.result` 中的引用来源，结构化整理后向用户展示。

## 📦 依赖

```bash
pip3 install requests
```

## ⚠️ 错误处理

| 情况 | 处理方式 |
|------|---------|
| 未配置 `REDFOX_API_KEY` | 提示用户前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key |
| 提交失败 | 输出错误信息，建议用户重试 |
| 轮询超时（5 分钟） | 提示超时，建议稍后重试 |
| 任务失败（status=failed） | 输出失败详情 |
