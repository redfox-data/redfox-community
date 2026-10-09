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
# 全站搜索：视频 + 用户 + 话题
python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type all --count 10

# 只搜视频：按点赞排序，只看最近一周
python scripts/tiktok_hot_search.py --keyword "camping gear" --type video --sort likes --publish 7

# 只搜账号：10K~100K 粉的认证账号
python scripts/tiktok_hot_search.py --keyword "手冲咖啡" --type user --fans 3 --verified

# 只搜话题
python scripts/tiktok_hot_search.py --keyword "cat" --type topic

# 翻页：按上次输出提示的 offset 继续
python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type video --offset 10 --count 10
```

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

输出顺序固定：先输出关键词与 API Key 获取提醒，再按「视频」→「相关用户」→「相关话题」顺序输出已查询类型的板块（每个板块 = 信息行 + 表格）。

信息行格式（仅输出本次查询的类型）：

```text
视频：offset：<offset> | count：<count> | 本页：<n> 条 | 下一页 offset：<offset+count>
相关用户：offset：<offset> | count：<count> | 本页：<n> 条 | hasMore：<hasMore> | 下一页 offset：<cursor>
相关话题：offset：<offset> | 本页：<n> 条 | hasMore：<hasMore> | 下一页 offset：<nextCursor>
```

表格表头固定为：

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

渲染规则：

- 视频链接必须使用接口返回的完整 `shareLink`，格式为 `[打开作品](完整shareLink)`
- 用户主页链接按 `https://www.tiktok.com/@<userHandle>` 拼接，格式为 `[打开主页](完整URL)`；`userHandle` 为空时显示"暂无链接"
- 话题链接使用接口返回的完整 `shareLink`，格式为 `[打开话题](完整shareLink)`；话题名自动加 `#` 前缀
- 所有数字加千分位（如 `1,234,567`）
- 发布时间为秒级时间戳，按北京时间渲染为 `YYYY-MM-DD` 日期
- 视频默认按播放数（`statsData.viewCount`）降序；用户固定按粉丝数降序；话题固定按浏览量降序
- 用户"粉丝数 / 获赞总数 / 作品数"为搜索结果快照，如个别账号返回 0，如实展示、不推断账号规模
- 内容摘要超过 60 字符截断加 `...`，表格内文本转义换行与 `|`
- 某类型返回空列表时输出"暂无数据"，不自动替换关键词
- 多类型查询时某一类型失败，输出该类型错误说明，其余类型正常输出

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

---

## Step 7：版本信息

- **版本号**：v1.0.0
- **核心功能**：一次输入关键词，按需获取 TikTok 热门视频、相关用户与相关话题数据，支持排序、发布时间 / 地区 / 粉丝数筛选与游标翻页
- **数据来源**：红狐 API `/story/api/tiktok/ability/searchVideo`、`/searchUser`、`/searchTopic`
