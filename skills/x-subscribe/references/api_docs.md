# X(Twitter) 订阅账号推文 · API 接口文档（技术参考）

本 Skill 依赖红狐数据 3 个接口，统一使用请求头 `X-API-KEY` 鉴权（值取自环境变量 `REDFOX_API_KEY`）。

---

## 1. 获取用户发帖（时间线）

**`POST`** `https://redfox.hk/story/api/x/userTimeline`

根据用户名获取用户时间线，支持游标分页。**用于拉取订阅账号推文。**

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| screenName | string | 否 | 用户名，如 `elonmusk`（从主页链接 `x.com/elonmusk` 解析） |
| restId | string | 否 | 用户ID（如 `44196397`），传入后忽略 screenName |
| cursor | string | 否 | 游标，首页传空，后续用上次返回的 `nextCursor` |

> 本 Skill 额外携带 `source` 字段（`X账号订阅-GitHub`）用于来源标识。

### 关键响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 2000 表示成功 |
| data.user | object | 查询目标用户信息：`displayName`/`username`/`verified`/`avatar`/`followers`(可能为 null)/`description`/`location` |
| data.pinned | object | 置顶推文（本 Skill 不参与日期过滤，避免与 timeline 重复） |
| data.timeline | array | 时间线推文列表，按时间倒序 |
| data.nextCursor | string | 下一页游标 |
| data.prevCursor | string | 上一页游标 |

单条推文（timeline 元素）字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| tweetId | string | 推文ID，用于拼接 `https://x.com/{screenName}/status/{tweetId}` |
| text | string | 推文正文 |
| createdAt | string | 发布时间，格式 `Tue Sep 22 01:23:58 +0000 2026`（UTC） |
| viewCount | string | 浏览量（字符串类型，需转 int） |
| likeCount / retweetCount / replyCount / quoteCount / bookmarkCount | integer | 点赞/转发/回复/引用/收藏数 |
| language | string | 语言代码 |
| medias.photos[].url | string | 图片URL |
| isSensitive | boolean | 是否敏感内容 |
| retweetedTweet | object/null | 被转发推文（非空表示这是转推） |
| quoted | object/null | 被引用推文（非空表示这是引用推文） |

### 翻页与日期过滤规则（核心）

接口**不支持按时间排序/筛选**，时间线按倒序返回。每日更新拉取「昨日」推文时，Skill 内部按以下规则处理：

1. 拉第 1 页（cursor 为空）
2. 将每条推文 `createdAt`（UTC）转换为**本地时区**后取日期
3. 逐页判断：
   - 本页存在命中（日期 == 目标日期）推文 **且** 本页没有更早日期 → 记录本页命中推文，用 `nextCursor` 继续翻页
   - 本页已包含比目标日期更早的推文 → **结束翻页**，只保留命中推文
   - 本页全部晚于目标日期（无命中、无更早）→ 继续翻页
4. 安全上限：每账号最多翻 `--max-pages` 页（默认 5），或 `nextCursor` 为空时停止

> cursor 是服务端状态标识，不可自行构造，必须严格使用上一页返回的 `nextCursor`。

---

## 2. 获取用户关注列表

**`POST`** `https://redfox.hk/story/api/x/userFollowing`

根据用户名获取该用户的关注列表，支持游标分页。**用于订阅前的账号探索（入口三）。**

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| screenName | string | 是 | 用户名，如 `elonmusk` |
| cursor | string | 否 | 游标，首页传空，后续用 `nextCursor` |

### 关键响应字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | integer | 2000 表示成功 |
| data.following | array | 关注用户列表 |
| data.moreUsers | boolean | 是否还有更多：true 有 / false 无 |
| data.nextCursor | string | 下一页游标 |

following 元素字段：`avatar`/`createdAt`/`description`/`displayName`/`followers`(int)/`following`(int)/`mediaCount`/`tweetCount`/`userId`/`username`/`website`。

> 默认只拉 1 页（每页约 20 个账号）、首次最多展示 20 个，展示名称/粉丝数/简介供用户挑选；用户想查看更多时加 `--all` 展示本页全部，`moreUsers=true` 时可用 `--cursor` 继续翻页。

---

## 3. 热门账号榜（批量订阅推荐来源）

**`POST`** `https://redfox.hk/story/api/x/hotAccount/rankList`

X 热门账号榜接口。**本 Skill 用其作为「榜单批量订阅」的推荐来源，固定查询昨日数据**，支持性别（全部/男/女）与 32 个行业分类筛选。

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| pageNum | integer | 是 | 页码，每页 20 条 |
| rankDate | string | 是 | 榜单日期 `YYYY-MM-DD`（本 Skill 固定取昨日） |
| gender | string | 是 | `all`/`male`/`female` |
| category | string | 是 | 行业中文名（如 `科技软件`）或 `all` |

### 关键响应字段

| 字段 | 说明 |
| --- | --- |
| data.list[].rankNo | 排名 |
| data.list[].fullName | 账号名 |
| data.list[].profileUrl | 主页链接，**从中解析 screen_name**（`x.com/<handle>`） |
| data.list[].xFollowerCount | X 粉丝数 |
| data.list[].xScore | 影响力评分（满分 100） |
| data.list[].title / biography / countryName | 头衔 / 简介 / 国家地区 |

### 更新时间与回溯

- 榜单每日早上 **9:00** 更新**前一天**数据；9 点后最新为昨日，9 点前为前日
- 最多回溯过去 7 天

> 完整 32 个行业分类与关键词映射见 [../assets/category_config.json](../assets/category_config.json)。

---

## 鉴权与安全

- 三个接口均需 API 密钥 `REDFOX_API_KEY`，由 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 提供
- 密钥仅通过环境变量或请求头传入，**禁止在代码、提示词、日志或输出文件中硬编码/明文暴露**
