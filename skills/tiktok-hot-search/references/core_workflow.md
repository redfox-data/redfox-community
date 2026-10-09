# Core Workflow

> 本文件为 tiktok-hot-search 技能的完整执行逻辑参考。SKILL.md 仅保留用户可见的功能描述，Agent 执行时必须遵循本文件中的所有规则。

---

## Step 0：鉴权配置（前置步骤）

> 用户使用本技能前需完成数据服务接入凭证配置。Agent 在首次交互时应主动检查并引导配置。

- 本技能依赖环境变量 `REDFOX_API_KEY`；未设置时脚本会尝试从 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 等 shell 配置文件中读取
- API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）
- 未获取到 Key 时脚本报错并以非零状态码退出，同时输出 API Key 获取提醒

---

## Step 1：数据来源与接口

本技能共对接 3 个数据接口，按用户需求选择其中 1~3 个调用：

| 接口 | 用途 | 路径 |
|---|---|---|
| 关键词视频搜索 | 按关键词查热门视频 | `POST https://redfox.hk/story/api/tiktok/ability/searchVideo` |
| 关键词用户搜索 | 按关键词查账号 / 达人 | `POST https://redfox.hk/story/api/tiktok/ability/searchUser` |
| 关键词话题搜索 | 按关键词查话题 / hashtag | `POST https://redfox.hk/story/api/tiktok/ability/searchTopic` |

通用规则：

- 认证方式：请求头 `X-API-KEY`（即环境变量 `REDFOX_API_KEY`）
- 来源标识：每个接口的请求体均携带 `source` 字段，值为 `TikTok热门搜索-GitHub`
- 成功码：`code=2000`
- 传输说明：redfox.hk 接口在本地环境可能需要无 SNI 的 socket + SSL 连接；脚本已内置该传输方式（保留证书链校验，仅关闭主机名检查），Agent 无需额外处理

### 1.1 关键词视频搜索（searchVideo）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | String | 是 | 搜索关键词 |
| offset | String | 否 | 偏移量，首次传 `"0"` |
| count | String | 否 | 单页条数 |
| sortType | String | 否 | 0-相关度（默认），1-最多点赞 |
| publishTime | String | 否 | 0-不限制（默认），1-最近一天，7-最近一周，30-最近一个月，90-最近三个月，180-最近半年 |
| region | String | 否 | 地区，默认 US-美国 |

响应说明：

- `data` 为**数组**，每个元素即一条视频，字段包括 `workId`、`content`、`shareLink`、`publishTime`（秒级时间戳）、`mediaType`、`area`
- `authorData`：作者信息（`userName`、`userHandle`、`fansCount`、`secUserId`、`userId` 等）
- `statsData`：统计数据（`viewCount` 播放、`likeCount` 点赞、`commentTotal` 评论、`shareTotal` 分享等）
- `videoData`：视频数据（`playAddress`、`downloadNoMarkAddress`、`coverImage` 等）
- 该接口**不返回翻页标识**，下一页 offset = 当前 offset + count

### 1.2 关键词用户搜索（searchUser）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | String | 是 | 搜索关键词 |
| offset | String | 是 | 偏移量，首次传 `"0"`，翻页传上一次响应中的 cursor |
| count | String | 是 | 单页条数 |
| followerCountFilter | Integer | 否 | 粉丝数筛选：空-不限制，1-0~1K，2-1K~10K，3-10K~100K，4-100K 以上 |
| profileTypeFilter | Integer | 否 | 账号类型筛选：空-不限制，1-认证用户 |
| otherPrefFilter | Integer | 否 | 其他偏好：空-不限制，1-按用户名相关性（技能默认不启用） |

响应说明：

- `data.cursor`：下一页游标（作为下一次请求的 `offset`）
- `data.hasMore`：1-还有下一页，0-没有
- `data.userList`：用户列表，字段包括 `userName`、`userHandle`、`fansCount`、`followCount`、`likedTotal`、`workCount`、`avatarImage`、`secUserId`、`userId`（未返回用户主页链接）

### 1.3 关键词话题搜索（searchTopic）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | String | 是 | 搜索关键词 |
| offset | Integer | 是 | 偏移量，首次传 `0`，翻页传上一次响应中的 nextCursor |

响应说明：

- 该接口无 `count` 参数，单页条数由服务端固定
- `data.hasMore`：1-还有下一页，0-没有
- `data.nextCursor`：下一页游标（作为下一次请求的 `offset`）
- `data.topicList`：话题列表，字段包括 `topicId`、`topicName`、`viewCount`（浏览量）、`usageCount`（使用次数）、`participantCount`（参与人数）、`shareLink`（话题链接）、`description`、`challengeFlag`、`commerceFlag`、`liveFlag`

---

## Step 2：理解用户意图

| 用户意图 | 执行动作 |
|---|---|
| 搜视频 / 找内容 / 看播放量 | `--type video` |
| 找账号 / 找达人 / 哪个博主在做 | `--type user` |
| 话题 / 挑战 / hashtag / `#xx` | `--type topic` |
| 泛指"搜一下 / 都看看 / 全站搜索" | `--type all`（默认） |
| 指定排序 | `--sort`：`views`（默认，播放数降序）、`likes`、`comments`、`shares`、`none`（原始相关度顺序） |
| 发布时间筛选 | `--publish`：`0`（默认，不限制）、`1`、`7`、`30`、`90`、`180` |
| 指定地区 | `--region`：默认 `US`，其余按 TikTok 地区代码传入 |
| 粉丝数筛选 | `--fans`：1-0~1K，2-1K~10K，3-10K~100K，4-100K 以上 |
| 只看认证账号 | `--verified` |
| 翻页 | 使用上一页输出提示的 offset / 游标作为 `--offset` |
| 查看原始返回 | `--raw` |

用户只提到某一类时，只查询该类型，不默认追加其他类型；只有泛指搜索或明确要求"全都看"时才用 `--type all`。

---

## Step 3：调用脚本

```bash
# 全站搜索：视频 + 用户 + 话题（结果同时落盘，供 HTML 报告使用）
python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type all --count 10 --save-json

# 只搜视频：按点赞排序，只看最近一周
python scripts/tiktok_hot_search.py --keyword "camping gear" --type video --sort likes --publish 7

# 只搜账号：10K~100K 粉的认证账号
python scripts/tiktok_hot_search.py --keyword "手冲咖啡" --type user --fans 3 --verified

# 只搜话题
python scripts/tiktok_hot_search.py --keyword "cat" --type topic

# 翻页：按上次输出提示的 offset 继续
python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type video --offset 10 --count 10

# 生成 HTML 报告（基于已保存的查询结果，不调用接口、不消耗积分）
python scripts/generate_report.py --data output/tiktok_search_latest.json
```

执行规则：

- Agent 执行查询时统一附带 `--save-json`，结果落盘到 `output/tiktok_search_latest.json`（本地文件，不产生额外接口调用）
- 查询完成后用该 JSON 运行 `generate_report.py --no-open` 生成 HTML 报告（本地文件生成，不调用接口、不消耗积分）；用户要求「导出报告」时直接复用已生成的报告，JSON 缺失时才重新查询一次
- `--save-json` 不带路径时使用默认路径；翻页查询同样覆盖保存为最新结果

参数校验（脚本内置）：

- `--keyword` 不能为空
- `--count` 必须在 1~50 之间（默认 10；话题查询忽略该参数）
- `--offset` 不能小于 0
- `--type` 可选值：`video` / `user` / `topic` / `all`（默认 `all`）
- `--sort` 可选值：`views`（默认）/ `likes` / `comments` / `shares` / `none`
- `--publish` 可选值：`0`（默认）/ `1` / `7` / `30` / `90` / `180`
- `--fans` 可选值：`1` / `2` / `3` / `4`

---

## Step 4：渲染输出

输出参考「X(Twitter) 企业家影响力榜」技能的结构：数据表格在前，AI 分析块在后，结尾统一附免责声明与「更多操作」。输出顺序固定：

1. 💡 搜索说明
2. 各类型板块：📊 表格 + 分析块（只输出本次查询的类型）
3. 免责声明
4. ⚡ 更多操作

整体模板如下（`{}` 为占位内容，Agent 依据脚本输出如实填写）：

```text
💡 搜索说明：关键词「{keyword}」的 TikTok 热门数据，{筛选口径说明}；数据来自红狐数据服务，与实时数据可能存在差异。
🔑 API Key 获取：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)

📊 {视频板块标题}
{视频信息行}

{视频表格}

🎯 爆款视频 TOP3 拆解（按播放数排序，统计范围：本页视频）
1. **{作者}**（@{TikTok号}）发布于 {日期} ｜ 播放 {x} ｜ 点赞 {y}
   内容摘要：{摘要}
   爆款原因推测：{1~2 句，结合内容与数据表现，明确为推测} ｜ [打开作品]({作品链接})

🚀 值得关注的达人 TOP3（按粉丝数排序，统计范围：本页账号）
1. **{昵称}**（@{TikTok号}）粉丝 {x} ｜ 获赞 {y} ｜ 作品 {z}
   关注理由：{1~2 句，结合账号定位与关键词相关性，明确为推测} ｜ [打开主页]({主页链接})

💡 话题趋势解读（按浏览量排序，统计范围：本页话题）
1. **#{话题名}**
   {100~200 字分析：热度规模、使用趋势、与关键词的关系、商业化信号；关键数据附话题链接}

（以上为基于公开数据的 AI 分析与推测，仅供参考。）

⚡ 更多操作
• [打开 HTML 报告]({报告文件绝对路径})，支持导出 PDF / 高清图片
• 是否继续查看第 {下一页} 页？
```

各板块规则：

- **搜索说明**：`{筛选口径说明}` 只写本次生效的非默认条件，如"按点赞数降序 · 仅最近一周 · 地区 JP"；全部为默认值时写"按播放数降序、发布时间不限制、地区 US"即可
- **板块顺序**：`--type all` 时按「视频」→「相关用户」→「相关话题」输出；只查某一类型时仅输出该类型板块
- **信息行**（紧跟板块标题之后）：
  ```text
  视频：offset：<offset> | count：<count> | 本页：<n> 条 | 下一页 offset：<offset+count>
  相关用户：offset：<offset> | count：<count> | 本页：<n> 条 | hasMore：<hasMore> | 下一页 offset：<cursor>
  相关话题：offset：<offset> | 本页：<n> 条 | hasMore：<hasMore> | 下一页 offset：<nextCursor>
  ```
- **表格表头固定**为：
  ```text
  ### 视频（按播放数降序）
  | # | 作者 | 作品 ID | 播放 | 点赞 | 评论 | 分享 | 发布时间 | 作品链接 | 内容摘要 |
  |---:|---|---|---:|---:|---:|---:|---|---|---|

  ### 相关用户（按粉丝数降序）
  | # | 昵称 | TikTok号 | 粉丝数 | 获赞总数 | 作品数 | 主页链接 |
  |---:|---|---|---:|---:|---:|---|

  ### 相关话题（按浏览量降序）
  | # | 话题 | 话题 ID | 浏览量 | 使用次数 | 话题链接 |
  |---:|---|---|---:|---:|---|
  ```
- **表格渲染规则**（与脚本输出一致）：
  - 视频链接必须使用接口返回的完整 `shareLink`，格式为 `[打开作品](完整shareLink)`
  - 用户主页链接按 `https://www.tiktok.com/@<userHandle>` 拼接，格式为 `[打开主页](完整URL)`；`userHandle` 为空时显示"暂无链接"
  - 话题链接使用接口返回的完整 `shareLink`，格式为 `[打开话题](完整shareLink)`；话题名自动加 `#` 前缀
  - 所有数字加千分位（如 `1,234,567`）；发布时间为秒级时间戳，按北京时间渲染为 `YYYY-MM-DD` 日期
  - 视频默认按播放数（`statsData.viewCount`）降序；用户固定按粉丝数降序；话题固定按浏览量降序
  - 用户"粉丝数 / 获赞总数 / 作品数"为搜索结果快照，如个别账号返回 0，如实展示、不推断账号规模
  - 内容摘要超过 60 字符截断加 `...`，表格内文本转义换行与 `|`
  - 某类型返回空列表时输出"暂无数据"，不自动替换关键词
  - 多类型查询时某一类型失败，输出该类型错误说明，其余类型正常输出
- **分析块规则**：
  - 只对本次查询且非空的类型输出分析块；每类只分析 TOP3，本页不足 3 条时按实际条数分析并注明
  - 爆款原因推测、关注理由、话题趋势解读必须基于本页表格可见数据撰写，1~2 句或 100~200 字，不得编造数据之外的细节
  - 所有分析内容须以"推测 / 解读"口吻表述，结尾统一附免责声明；分析中引用的作品 / 主页 / 话题链接保持完整可点击
  - 话题不足 3 个或某类无数据时如实说明，不虚构
- **报告入口**：每次查询完成后，用已落盘的 `output/tiktok_search_latest.json` 运行 `generate_report.py --no-open` 生成 HTML 报告（本地文件生成，不产生接口调用、不消耗积分），入口用 `[打开 HTML 报告](文件绝对路径)` 形式给出可点击链接，并注明支持导出 PDF / 高清图片；报告生成失败（如 JSON 缺失）时如实说明，不重复查询
- **翻页提示**：基于各类型信息行中的「下一页 offset / 游标」提示用户是否继续查看下一页，不主动翻页

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
| 某类型空列表 | 输出"暂无数据"，不要主动改查其他关键词 |
| 脚本异常 | 错误信息输出到 stderr 并以 exit 1 退出；与 Key 相关时同时输出 API Key 获取提醒 |

---

## Step 6：注意事项

1. **积分保护**：每次成功查询可能消耗积分；一次 `--type all` 包含 3 次数据查询；未经用户明确指定，不要主动翻页或批量查询多个关键词
2. **链接完整性**：输出中的链接必须保持完整，不要使用被终端截断的 URL
3. **无结果不替换**：空结果时如实说明，不自动改查其他关键词
4. **鉴权提示**：依赖环境变量 `REDFOX_API_KEY`（三级读取），API Key 获取：https://redfox.hk/settings/api-keys?source=github
5. **分析为推测**：爆款原因推测、关注理由与话题趋势解读均基于公开数据撰写，必须标注为推测，不得编造数据之外的细节
6. **报告零成本**：HTML 报告仅读取本地 JSON 生成，不发起接口调用、不消耗积分

---

## Step 7：版本信息

- **版本号**：v1.1.1
- **核心功能**：一次输入关键词，按需获取 TikTok 热门视频、相关用户与相关话题数据，支持排序、发布时间 / 地区 / 粉丝数筛选与游标翻页；输出榜单表格、爆款视频 TOP3 拆解、达人推荐与话题趋势解读，并生成 HTML 报告（含「关键词热门概览」与三类榜单，支持导出 PDF / 高清图片）
- **数据来源**：红狐 API `/story/api/tiktok/ability/searchVideo`、`/searchUser`、`/searchTopic`
