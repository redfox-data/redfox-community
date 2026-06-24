---
name: cultural-tourism-bilibili-feed
description: 文旅B站信息源 — 搜索文旅相关B站热门视频，按点赞量筛选最火内容，生成精美 HTML 报告。当用户需要文旅B站、旅游攻略、景区热度、文旅资讯、文旅爆款内容时使用。触发词：文旅B站、文旅信息源、文旅资讯、旅游B站、景区视频、文旅爆款。
---

# 文旅B站信息源

## 📝 简介

搜索全网文旅B站热门视频，按点赞量排名筛选最火内容，单次获取 200 条数据，自动按主题聚类，生成深色主题 HTML 可视化报告。支持时间范围筛选与每日自动订阅。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|----------|
| 关键词搜索 | 根据景区/城市/主题搜索文旅B站视频 | 精准匹配目标内容 |
| 时间筛选 | 按日期范围过滤（startTime / endTime） | 灵活控制数据窗口 |
| 自动聚类 | 200 条数据按 type/topic 标签自动分类 | 降低信息熵，聚焦主题 |
| 终端表格 | 按分类输出标题+作者+点赞+评论+分享 | 快速概览，无需打开报告 |
| 可视化报告 | 深色主题 HTML，分区卡片网格+封面图 | 精美呈现，支持全文搜索 |
| 每日订阅 | `--subscribe` 开启定时自动产出 | 无需手动重复操作 |

## 🔑 鉴权

前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key，通过以下方式配置：

```bash
# 方式一：环境变量（推荐）
export REDFOX_API_KEY=ak_xxxx

# 方式二：配置文件
mkdir -p ~/.qoder/apis
echo '{"api_key":"ak_xxxx"}' > ~/.qoder/apis/redfox.json
```

## ⚙️ 参数提取

从用户 query 中提取以下参数：

| 参数 | 提取方式 | 命令行示例 |
|------|----------|-----------|
| `keyword` | 用户提到的**具体景区/城市/主题**；若仅说"文旅爆款"未指定具体词，**必须传空字符串 `""`** | `--keyword "九寨沟"` / `--keyword ""` |
| `start-time` | 用户提到的起始日期，格式 YYYY-MM-DD | `--start-time "2026-06-20"` |
| `end-time` | 用户提到的结束日期，格式 YYYY-MM-DD | `--end-time "2026-06-21"` |

> ⚠️ **关键规则**：用户说"文旅爆款"/"文旅B站"时，"文旅"是 Skill 触发信号而非搜索词，keyword **必须传空字符串 `""`**（即 `--keyword ""`），让接口返回全量文旅内容。只有当用户明确指定了具体景区/城市/主题时，才将对应词作为 keyword 传入。

若用户未提及时间，不传 `--start-time` 和 `--end-time`（接口返回默认数据）。

完整参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keyword` | 搜索关键词（可选） | `""` |
| `--start-time` | 起始日期 YYYY-MM-DD | 空 |
| `--end-time` | 结束日期 YYYY-MM-DD | 空 |
| `--output-dir` | HTML 输出目录 | `~/Downloads/QoderReports` |
| `--api-key` | 指定 API Key | 环境变量 |
| `--subscribe` / `--unsubscribe` | 订阅/取消每日推送 | — |
| `--no-open` | 不自动打开浏览器 | — |

## 🚀 执行流程

1. 提取用户 query 中的 keyword、start-time、end-time
2. 拼接命令并执行：
   ```bash
   python3 "$SKILL_PATH/scripts/cultural_tourism_bilibili_report.py" \
       --keyword "" --start-time "2026-06-20" --end-time "2026-06-21" \
       --output-dir /path/to/tmp
   ```
3. 脚本自动：获取数据 → 聚类分类 → 生成 HTML → 终端表格输出 → 浏览器打开报告

> 沙箱环境下 `~/Downloads/` 不可写时，使用 `--output-dir /path/to/workspace/tmp`。每次执行必须自动打开 HTML 报告，禁止使用 `--no-open`。

## 📊 输出格式

脚本执行完毕后，Agent **必须**在对话中按以下结构向用户展示结果，每次缺一不可：

```
📌 数据说明：每日17点更新前一天数据

| 分类 | 数量 |
|------|------|
| xxx  | N    |
| ...  | ...  |

共 N 个视频，N 个分类。完整数据查看 [HTML 报告](file:///path/to/report.html)。

💡 需要每日17点自动推送最新文旅数据吗？
```

> ⚠️ **严格规则**：对话中**仅展示分类统计表格**，不展示完整数据表格（标题/作者/互动数据等）。完整数据和可点击链接通过 HTML 报告提供。

终端原始输出包含完整数据表格，Agent 从中提取分类统计信息用于对话展示。

HTML 报告文件命名：`文旅B站日报_{keyword}_{date}.html`，自动浏览器打开。

## 📦 依赖

```bash
pip3 install requests
```
