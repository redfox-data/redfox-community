# Core Workflow

> 本文件为 tiktok-subscribe 技能的完整执行逻辑参考。SKILL.md 仅保留用户可见的功能描述，Agent 执行时必须遵循本文件中的所有规则。

---

## Step 0：鉴权配置（前置步骤）

> 用户使用本技能前需完成数据服务接入凭证配置。Agent 在首次交互时应主动检查并引导配置。

- 本技能依赖环境变量 `REDFOX_API_KEY`；未设置时脚本会尝试从 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 等 shell 配置文件中读取
- API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）
- 未获取到 Key 时脚本报错并以非零状态码退出，同时输出 API Key 获取提醒

---

## Step 1：数据来源与接口

本技能共对接 3 个数据接口，对应三类订阅项：

| 接口 | 用途 | 路径 |
|---|---|---|
| 关键词视频搜索 | 关键词新增爆款视频（最近一天，按点赞排序） | `POST https://redfox.hk/story/api/tiktok/ability/searchVideo` |
| 用户主页作品 | 账号近期全部作品（无翻页，一次返回） | `POST https://redfox.hk/story/api/tiktok/ability/userAwemeList` |
| 话题作品列表 | 话题新作品（cursor 游标翻页） | `POST https://redfox.hk/story/api/tiktok/ability/topicAwemeList` |

通用规则：

- 认证方式：请求头 `X-API-KEY`（即环境变量 `REDFOX_API_KEY`）
- 来源标识：每个接口的请求体均携带 `source` 字段，值为 `TikTok监控订阅推送-GitHub`
- 成功码：`code=2000`
- 传输说明：redfox.hk 接口在本地环境可能需要无 SNI 的 socket + SSL 连接；脚本已内置该传输方式（保留证书链校验，仅关闭主机名检查），Agent 无需额外处理

### 1.1 关键词视频搜索（searchVideo）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | String | 是 | 订阅关键词 |
| offset | String | 否 | 偏移量，首次传 `"0"` |
| count | String | 否 | 单页条数 |
| sortType | String | 否 | 0-相关度，1-最多点赞（本技能固定 `"1"`） |
| publishTime | String | 否 | 每日模式固定 `"1"`（最近一天），首次模式 `"0"`（不限制） |
| region | String | 否 | 地区，默认 US-美国 |

响应说明：

- `data` 为**数组**，每个元素即一条作品，字段包括 `workId`、`content`、`shareLink`、`publishTime`（秒级时间戳）、`mediaType`、`area`
- `authorData`：作者信息（`userName`、`userHandle`、`fansCount`、`secUserId`、`userId` 等）
- `statsData`：统计数据（`viewCount` 播放、`likeCount` 点赞、`commentTotal` 评论、`shareTotal` 分享等）
- 该接口**不返回翻页标识**，下一页 offset = 当前 offset + count

### 1.2 用户主页作品（userAwemeList）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| secUserId | String | 是 | 用户加密 ID（`MS4w` 开头的长串，注意 camelCase 命名） |

响应说明：

- `data` 为**数组**（无翻页参数，一次返回账号近期全部作品，约 20+ 条），每个元素即一条作品
- 作品字段：`workId`、`content`、`shareLink`、`publishTime`（秒级时间戳）、`mediaType`、`area`
- `authorData`：作者信息（`userName`、`userHandle`、`fansCount` 等）——账号展示名称由首条作品的 authorData 提取
- `statsData`：统计数据（`viewCount`、`likeCount`、`commentTotal`、`shareTotal` 等）
- 数据可能为 `null`（账号暂无作品），此时如实说明

### 1.3 话题作品列表（topicAwemeList）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| ch_id | Integer | 是 | TikTok 话题 ID / challengeId，必须为大于 0 的数字 |
| cursor | Integer | 是 | 分页游标，首页传 `0`，翻页传上一次响应中的 nextCursor |
| count | Integer | 是 | 单页条数 |

响应说明：

- `data.hasMore`：1-还有下一页，0-没有；`data.nextCursor`：下一页游标
- `data.workList`：作品列表，单页约 20 条，作品结构与 1.1 一致
- `data.nextCursor` 可能为 null，此时若 hasMore=1 则按 cursor+count 兜底翻页

---

## Step 2：理解用户意图与订阅项解析

### 2.1 订阅项输入解析

| 订阅项 | 有效输入 | 解析结果 |
|--------|---------|---------|
| 关键词 | 任意非空字符串（逗号分隔） | 关键词列表，去重 |
| 账号 | secUserId（`MS4w` 开头的长串） | 直接使用 |
| 账号 | 带 `sec_uid=` 参数的分享链接 | 提取 `sec_uid` 参数值 |
| 话题 | 话题 ID（大于 0 的数字，逗号分隔） | 话题 ID 列表，去重 |

输入规则：

- 账号输入含无法解析项（非 MS4w 开头、无 `sec_uid` 参数）时，脚本报错并列出无效项，提示按 SKILL.md「secUserId 获取方式」重新获取，不要猜测替换
- 话题输入含非数字项时，脚本报错并列出无效项，提示用「TikTok热门搜索」技能搜索话题获取话题 ID
- 三类订阅项均未提供时，脚本报错提示至少提供一类
- 用户只给话题名 / 话题链接但无话题 ID 时：先用「TikTok热门搜索」技能（topic 查询）解析出 `topicId`，或从话题链接的 `ch_id` 参数提取，再走入口三订阅

### 2.2 拉取模式

| 用户意图 | 执行动作 |
|---|---|
| 首次订阅验证 / 查看最新动态 | `fetch ... --first`（拉第一页，不按时间窗过滤） |
| 每日更新 / 自动化任务 | `fetch ...`（默认每日模式，按昨日时间窗过滤 + 翻页） |
| 指定历史日期 | `fetch ... --date YYYY-MM-DD` |
| 查看原始返回 | `--raw` |

### 2.3 积分口径

- 关键词：每翻 1 页消耗 1 次调用（每日模式默认最多 3 页，`--max-pages` 可调）
- 话题：每翻 1 页消耗 1 次调用（每日模式默认最多 3 页）
- 账号：1 次调用返回近期全部作品，无额外翻页
- `--first` 模式每订阅项固定 1 次调用
- HTML 日报与 AI 总结为本地离线生成，不消耗积分

### 2.4 静默执行原则

所有中间步骤（fetch 验证、automation_update 查询/更新/创建）均不得向用户输出过程性提示（如「正在验证订阅项」「验证通过」等）。仅向用户展示最终结果（订阅结果总览 + 作品表格 + AI 总结 + 报告入口）。

---

## Step 3：调用脚本

```bash
# 每日更新（三类混合，生成 HTML 日报）
python scripts/subscribe.py fetch --keywords "nvidia,iphone" --accounts "MS4wLjAB..." --topics "2525872" --html

# 首次订阅验证（拉第一页最新动态，不按时间窗过滤）
python scripts/subscribe.py fetch --keywords "nvidia" --first --html

# 指定历史日期
python scripts/subscribe.py fetch --topics "2525872" --date 2026-10-12 --html

# Markdown 输出（供 Agent 转述）
python scripts/subscribe.py fetch --keywords "nvidia" --markdown

# 生成 HTML 日报（基于已保存的查询结果与本地 AI 总结 JSON，不调用接口、不消耗积分）
python scripts/generate_report.py --data output/tiktok_subscribe_latest.json --analysis output/tiktok_subscribe_ai_summary.json
```

执行规则：

- Agent 执行查询时统一附带 `--save-json`，结果落盘到 `output/tiktok_subscribe_latest.json`（本地文件，不产生额外接口调用）
- Agent 将对话中写好的「AI 语义总结」写入本地 `output/tiktok_subscribe_ai_summary.json`（结构见 Step 4.4），与对话输出保持完全一致
- `--html` 时脚本自动落盘并调用 `generate_report.py`（自动合并同目录 AI 总结 JSON），生成后自动打开浏览器
- 用户要求「导出报告」时直接复用已生成的报告；JSON 缺失时才重新查询一次
- 脚本用 `python` 命令路径按运行环境而定（Windows 下需保证控制台为 UTF-8 编码）

参数校验（脚本内置）：

- `--count` 必须在 1~50 之间（默认 20）
- `--max-pages` 必须在 1~10 之间（默认 3）
- `--date` 必须为 `YYYY-MM-DD` 格式
- `--accounts` / `--topics` 中的无效项按 Step 2.1 规则处理，脚本报错退出（在发起任何 API 调用之前）

---

## Step 4：渲染输出

输出参考「X(Twitter) 企业家影响力榜」技能的结构：数据表格在前，AI 分析块在后，结尾统一附免责声明与「更多操作」。输出顺序固定：

1. 📊 订阅结果总览
2. 各订阅项作品表格（关键词 → 账号 → 话题，按传入顺序）
3. 无更新订阅项折叠提示（如有）
4. 📈 AI 语义总结
5. 免责声明
6. ⚡ 更多操作

整体模板如下（`{}` 为占位内容，Agent 依据脚本输出如实填写）：

```text
📊 订阅结果
| 项目 | 值 |
|------|-----|
| 本次订阅 | {本次新增订阅项说明} |
| 当前总订阅 | {总数} / 100 项 |
| 自动化任务 | 已更新 ✅ 每日 9:00 自动执行 |
| 拉取时间窗 | {MM-DD HH:mm} ~ {MM-DD HH:mm}（本地时区，首次模式则写「首次拉取最新动态」） |

### ▸ 关键词「{关键词}」 {昨日新内容/最新动态}（{n} 条）

| # | 作者 | 作品摘要 | 播放 | 点赞 | 评论 | 分享 | 发布时间 |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | {昵称} / `{handle}` | [{摘要}]({作品链接}) | {x} | {y} | {z} | {w} | {MM-DD HH:mm} |

### ▸ 账号 {昵称}（@{handle}） {昨日新内容/最新动态}（{n} 条）

| # | 作品摘要 | 播放 | 点赞 | 评论 | 分享 | 发布时间 |
|---:|---|---:|---:|---:|---:|---|

### ▸ 话题 ID {ch_id} {昨日新内容/最新动态}（{n} 条）

| # | 作者 | 作品摘要 | 播放 | 点赞 | 评论 | 分享 | 发布时间 |
|---:|---|---|---:|---:|---:|---:|---|

{无更新折叠提示：如「以下 1 个订阅项昨日无更新，已折叠」}

📈 AI 语义总结
**今日主题总结**
1. **{主题名}**：{这段在讲什么，1~2 句}（涉及 {订阅项}，相关作品 {n} 条）
**单订阅项解读**
1. 关键词「{nvidia}」：主题 {1~2 句} ｜ 观点 {1~2 句}

（以上为基于公开数据的 AI 分析与推测，仅供参考。）

⚡ 更多操作
• [打开 HTML 日报]({报告文件绝对路径})，支持导出 PDF / 高清图片
```

### 4.1 各板块规则

- **订阅结果总览**：订阅时填写「本次订阅 + 当前总订阅 + 自动化任务 + 首次拉取」四行（见 SKILL.md 第 9 节表格）；日常拉取（含自动化推送转述）时填写「拉取时间窗 + 更新统计（更新 X 项 / 无更新 X 项 / 失败 X 项）+ 自动化任务（已更新 ✅ 每日 9:00 自动执行）」三行
- **信息行**（紧跟订阅项标题之后，脚本已输出）：
  ```text
  本页：{n} 条 ｜ 按播放数降序[ ｜ 时间窗：{MM-DD HH:mm} ~ {MM-DD HH:mm}]
  ```
- **表格渲染规则**（与脚本输出一致）：
  - 作品摘要使用 `content` 原文（过长截取前 60 字加 `...`），渲染为可点击超链接 `[摘要](完整shareLink)`；无链接时输出纯文本
  - 关键词 / 话题订阅项表格含「作者」列（昵称 + `handle`）；账号订阅项表格无「作者」列
  - 所有数字加千分位（如 `85,207`）；发布时间按本地时区渲染为 `MM-DD HH:mm`
  - 所有订阅项按播放数（`statsData.viewCount`）降序排列
  - 表格内文本转义换行与 `|`
  - 某订阅项返回空时按状态输出折叠提示（见下），不自动替换订阅项
- **无更新折叠**：
  - `no_update_yesterday`：折叠提示「昨日无更新（该订阅项昨日时间窗内无新内容）」
  - `no_update_7d`：折叠提示「近 7 天无更新（该订阅项最近 7 天没有新内容）」
  - `error`：折叠提示「拉取失败：{原因}」，并如实转述失败原因
- **AI 语义总结**：
  - 由 Agent 读取本页作品内容撰写，不接 LLM 端点、不做词频统计
  - `overall`（今日主题总结）：分析作品在说什么（事件/主题），有几条归纳几条，不强制凑数，禁止虚构；每条含 title / summary（1~2 句）/ items（涉及的订阅项 key）/ workCount（相关作品条数）
  - `items`（单订阅项解读）：每个有更新订阅项一条，含 key / kind（keyword|account|topic）/ theme（主要主题）/ viewpoint（观点立场）
  - 无更新或失败订阅项不写入 `items`，如实说明
- **报告入口**：每次查询完成后，用已落盘的 `output/tiktok_subscribe_latest.json` 与 `output/tiktok_subscribe_ai_summary.json` 运行 `generate_report.py --no-open` 生成 HTML 日报（本地文件生成，不产生接口调用、不消耗积分），入口用 `[打开 HTML 日报](文件绝对路径)` 形式给出可点击链接，并注明支持导出 PDF / 高清图片；报告生成失败（如 JSON 缺失）时如实说明，不重复查询

### 4.2 AI 总结 JSON 结构（Agent 依据对话中的总结块如实填写）

```json
{
  "overall": [
    {"title": "主题/事件名", "summary": "这段在讲什么（1-2 句）", "items": ["nvidia"], "workCount": 8}
  ],
  "items": [
    {"key": "nvidia", "kind": "keyword", "theme": "该订阅项今日主要聊了什么主题", "viewpoint": "该订阅项内容表达的观点/立场"}
  ]
}
```

### 4.3 订阅结果总览规则（订阅时）

- 「本次订阅」按类型分列：`关键词 {n} 个、账号 {n} 个、话题 {n} 个`；已存在订阅项跳过并注明「（{n} 个已订阅跳过）」
- 「当前总订阅」= 现有订阅项数 + 新增数，上限 100
- 首次拉取展示各订阅项最新动态（`--first` 模式结果）

---

## Step 5：错误处理

| 场景 | 处理方式 |
|---|---|
| `code=3103` / `code=3105` | API Key 不存在或已禁用：提示更换有效 Key 并输出获取提醒，不要重复重试 |
| `code=3201` | 积分不足：提示前往红狐控制台充值后重试 |
| `code=1001` / `1002` / `1003` | 参数问题：按 `msg` 提示修正参数后重试 |
| `code=4004` | 操作过于频繁：稍后重试，不要连续重试 |
| `502` | 服务返回 502 错误，可能存在网络不稳定问题，请稍后重试 |
| 其他非 `2000` 返回 | 输出 `接口返回异常：code=<code>, msg=<msg>` |
| 账号输入无效 | 提示 secUserId 获取方式（SKILL.md 入口二），不要猜测替换 |
| 话题输入无效 | 提示用「TikTok热门搜索」技能搜索话题获取话题 ID |
| 某订阅项拉取失败 | 该项标记 `error` 并折叠提示原因，其余订阅项正常输出 |
| 脚本异常 | 错误信息输出到 stderr 并以 exit 1 退出；与 Key 相关时同时输出 API Key 获取提醒 |

---

## Step 6：注意事项

1. **积分保护**：每次成功查询可能消耗积分；关键词 / 话题翻页每页 1 次调用，未经用户明确指定，不要主动增加翻页数或批量查询
2. **订阅状态来源**：所有订阅状态 = 自动化命令中的 `--keywords` / `--accounts` / `--topics` 参数，无本地文件存储；不得另建订阅记录文件
3. **链接完整性**：输出中的链接必须保持完整，不要使用被终端截断的 URL
4. **无结果不替换**：某订阅项空结果时如实说明，不自动改查其他订阅项
5. **鉴权提示**：依赖环境变量 `REDFOX_API_KEY`（三级读取），API Key 获取：https://redfox.hk/settings/api-keys?source=github
6. **分析为推测**：AI 语义总结基于公开数据撰写，必须标注为推测，不得编造数据之外的细节
7. **报告零成本**：HTML 日报仅读取本地 JSON 生成，不发起接口调用、不消耗积分
8. **静默执行**：fetch 验证、automation_update 等中间步骤不向用户输出过程提示，仅展示最终结果

---

## Step 7：版本信息

- **版本号**：v1.0.0
- **核心功能**：订阅关键词 / 账号 / 话题三类订阅项，每日 9:00 自动拉取「昨日 9:00 ~ 今日 9:00」时间窗内新内容，按订阅项分组输出作品表格（播放 / 点赞 / 评论 / 分享），支持首次模式、指定日期、翻页与 HTML 日报（无更新折叠 + AI 语义总结合并，导出 PDF / 高清图片）
- **数据来源**：红狐 API `/story/api/tiktok/ability/searchVideo`、`/userAwemeList`、`/topicAwemeList`
