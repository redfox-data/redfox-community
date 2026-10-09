# Core Workflow

> 本文件为 tiktok-keyword-topic-search 技能的完整执行逻辑参考。SKILL.md 仅保留用户可见的功能描述，Agent 执行时必须遵循本文件中的所有规则。

---

## Step 0：鉴权配置（前置步骤）

> 用户使用本技能前需完成数据服务接入凭证配置。Agent 在首次交互时应主动检查并引导配置。

- 本技能依赖环境变量 `REDFOX_API_KEY`；未设置时脚本会尝试从 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 等 shell 配置文件中读取
- API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）
- 未获取到 Key 时脚本报错并以非零状态码退出，同时输出 API Key 获取提醒
- 禁止硬编码密钥

---

## Step 1：数据来源与接口

- 唯一数据源：红狐 API
- 接口一（关键词搜话题）：`POST https://redfox.hk/story/api/tiktok/ability/searchTopic`
  - 认证方式：请求头 `REDFOX_API_KEY`（即环境变量 `REDFOX_API_KEY`）
- 接口二（话题作品获取）：`POST https://redfox.hk/story/api/tiktok/ability/topicAwemeList`
  - 认证方式：请求头 `X-API-KEY`（即环境变量 `REDFOX_API_KEY`）
- 来源标识：两个接口请求体均携带 `source` 字段，值为「tiktok关键词搜话题-GitHub」
- 成功码：`code=2000`

### 关键词搜话题请求参数

```json
{
  "keyword": "cat",
  "offset": 0,
  "source": "tiktok关键词搜话题-GitHub"
}
```

字段说明：

- `keyword`：搜索关键词，必填，不能为空
- `offset`：分页偏移量，首页传 `0`
- 响应 `data.nextCursor` 可作为下一页 `offset`
- 响应 `data.hasMore=1` 表示还有下一页
- 响应 `data.topicList` 为话题列表

### 话题作品获取请求参数

```json
{
  "ch_id": 2525872,
  "cursor": 0,
  "count": 10,
  "source": "tiktok关键词搜话题-GitHub"
}
```

字段说明：

- `ch_id`：TikTok 话题 ID / challengeId / hashtagId，必须为大于 0 的数字
- `cursor`：分页游标，首页传 `0`
- `count`：单页条数
- 响应 `data.nextCursor` 可作为下一页 `cursor`
- 响应 `data.hasMore=1` 表示还有下一页

传输说明：redfox.hk 接口在本地环境可能需要无 SNI 的 socket + SSL 连接；脚本已内置该传输方式（保留证书链校验，仅关闭主机名检查），Agent 无需额外处理。

---

## Step 2：理解用户意图

| 用户意图 | 执行动作 |
|---|---|
| 关键词搜话题（给出关键词） | 运行 `search_tiktok_topics.py` 并传入 `--keyword` |
| 查询话题作品（给出话题 ID） | 运行 `fetch_topic_aweme_list.py` 并传入 `--ch-id`；可附 `--topic` 话题名用于表格展示 |
| 用户以接口名 / `ch_id` 指代 | 按话题作品查询处理 |
| 指定排序 | 搜话题：加 `--sort views` / `usage` / `participants` / `none`（默认 `usage`，按使用次数降序）；查作品：加 `--sort likes` / `comments` / `shares` / `none`（默认 `views`，按播放数降序） |
| 翻页 | 使用上一页响应的 `data.nextCursor` 再查一次 |
| 查看原始返回 | 加 `--raw` 输出接口原始 JSON |

话题列表输出完成后，必须主动询问用户是否需要查看某个话题下的作品数据（提示格式见 Step 4）。

---

## Step 3：调用脚本

### 1. 关键词搜话题

```bash
python scripts/search_tiktok_topics.py --keyword cat
```

可选参数：

```bash
python scripts/search_tiktok_topics.py --keyword cat --offset 20
python scripts/search_tiktok_topics.py --keyword cat --sort views
python scripts/search_tiktok_topics.py --keyword cat --sort usage
python scripts/search_tiktok_topics.py --keyword cat --api-key ak_xxxxxxxx
python scripts/search_tiktok_topics.py --keyword cat --raw
```

参数校验（脚本内置）：

- `--keyword` 必填且不能为空
- `--offset` 不能小于 0
- `--sort` 可选值：`usage`（默认，使用次数降序）、`views`、`participants`、`none`（接口原始顺序）

### 2. 话题作品获取

```bash
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --count 10
```

可选参数：

```bash
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --cursor 10 --count 10
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --sort likes
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --api-key ak_xxxxxxxx
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --raw
```

参数校验（脚本内置）：

- `--ch-id` 必须大于 0
- `--cursor` 不能小于 0；`--count` 必须大于 0
- `--sort` 可选值：`views`（默认，播放数降序）、`likes`、`comments`、`shares`、`none`（接口原始顺序）

---

## Step 4：渲染输出

### 1. 关键词搜话题

输出顺序固定：先输出关键词与分页信息、API Key 获取提醒，再输出话题表格。

信息行格式：

```text
关键词：`<keyword>` | offset：<offset> | count：<本页条数> | hasMore：<hasMore> | nextCursor：<nextCursor>
```

表格表头固定为：

| # | 话题名称 | 话题ID | 使用次数 | 浏览量 | 参与人数 | 挑战标记 |
|---:|---|---|---:|---:|---:|---:|

渲染规则：

- 表格输出 `topicList[]` 中已知有效字段：`topicName`、`topicId`、`usageCount`、`viewCount`、`participantCount`、`challengeFlag`
- 默认按使用次数（`usageCount`）降序排序；如用户指定排序，可通过 `--sort views/usage/participants/none` 改为浏览量、使用次数、参与人数或接口原始顺序
- 可将输出的 `topicId` 作为 `--ch-id` 参数传入 `fetch_topic_aweme_list.py` 查询话题作品
- **搜完话题后必须主动提示用户**：话题列表输出完成后，须紧接着询问用户是否需要查看其中某个话题下的作品数据。提示格式示例：

  > 以上是搜索到的话题列表。需要查看哪个话题下的作品吗？例如：
  > 1. #cat（话题ID：7551）
  > 2. #cats（话题ID：5216）
  > 3. #catch（话题ID：35179）
  >
  > 告诉我话题名称或话题ID即可查询。

- 返回空 `topicList` 时输出"暂无数据"

### 2. 话题作品获取

输出顺序固定：先输出话题与分页信息、API Key 获取提醒，再输出作品表格。

信息行格式：

```text
话题：`<topic>` | ch_id：`<ch_id>` | cursor：<cursor> | count：<本页条数> | hasMore：<hasMore> | nextCursor：<nextCursor>
```

表格表头固定为：

| # | 作者 | 作品 ID | 播放 | 点赞 | 评论 | 分享 | 作品链接 | 内容摘要 | 话题 |
|---:|---|---|---:|---:|---:|---:|---|---|---|

渲染规则：

- 话题名自动加 `#` 前缀；未提供话题名时显示 `ch_id:<id>`
- "作品链接"必须使用接口返回的完整 `workList[].shareLink`，格式为 `[打开作品](完整shareLink)`
- 不要自行用 `userHandle + workId` 拼接链接，除非 `shareLink` 为空且用户明确要求兜底
- 默认不输出 `fansCount`、`followCount`、`workCount`、`likedTotal`，这些作者级字段在该接口实测常为 `0`，不适合排序或判断账号规模
- 列表默认按作品播放数（`statsData.viewCount`）降序排序；如用户指定排序，可通过 `--sort likes/comments/shares/none` 改为点赞、评论、分享或接口原始顺序
- 返回空 `workList` 时输出"暂无数据"

---

## Step 5：错误处理

- `code=3105`：API Key 已禁用，提示用户更换有效 Key，并输出获取 API Key 提醒，不要重复重试
- `code=3203`：参数校验失败，按 `msg` 中提示修正参数；该错误通常提示"积分未扣除"
- 其他非 `2000` 返回：输出 `接口返回异常：code=<code>, msg=<msg>`
- 返回空 `topicList` / `workList`：输出"暂无数据"，不要主动改查其他关键词或话题
- 缺少 `REDFOX_API_KEY`：提示设置环境变量或使用 `--api-key` 临时传入，禁止硬编码密钥
- 脚本异常：错误信息输出到 stderr 并以 exit 1 退出；与 Key 相关时同时输出 API Key 获取提醒

---

## Step 6：注意事项

1. **积分保护**：每次成功查询可能消耗积分；未经用户明确指定，不要主动翻页或批量查询多个关键词
2. **链接完整性**：输出中的链接必须保持完整，不要使用被终端截断的 URL
3. **无结果不替换**：空结果时如实说明并给出可选调整方向，不自动改查其他关键词或话题
4. **鉴权提示**：依赖环境变量 `REDFOX_API_KEY`（三级读取），API Key 获取：https://redfox.hk/settings/api-keys?source=github

---

## Step 7：版本信息

- **版本号**：v1.0.0
- **核心功能**：按关键词搜索 TikTok 话题（默认按使用次数降序），并按话题 ID 查询话题作品列表（默认按播放数降序），支持排序切换与游标翻页
- **数据来源**：红狐 API `/story/api/tiktok/ability/searchTopic` 与 `/story/api/tiktok/ability/topicAwemeList`
