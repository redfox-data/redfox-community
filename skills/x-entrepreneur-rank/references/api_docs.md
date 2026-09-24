# 红狐数据接口文档（实测）

鉴权：所有请求 Header 携带 `X-API-KEY: <REDFOX_API_KEY>`；`Content-Type: application/json`。
成功响应：`{"code": 2000, "msg": "成功", "data": {...}}`；`code=3105` 表示 API Key 已禁用。

所有请求 payload 必须携带固定 `source` 参数（具体值由脚本 `SOURCE` 常量声明，不在文档中重复写入，便于平台副本工具统一替换）。

## 1. 企业家/热门账号榜

`POST https://redfox.hk/story/api/x/hotAccount/rankList`

请求：

```json
{
  "pageNum": 1,
  "rankDate": "2026-09-22",
  "gender": "all",
  "category": "Business & Entrepreneurship",
  "source": <SOURCE>   // 固定来源标识，每次请求必传；具体值由脚本 SOURCE 常量注入
}
```

- `category` 为接口固定请求参数（已内置于脚本），不对用户展示
- `source` 为固定来源标识（已内置于脚本 `SOURCE` 常量），不对用户展示
- 每页 20 条，共 10 页；`rankDate` 每日 9:00 更新前一日数据，最多回溯 7 天

响应 `data`：`pageNum / pageSize / pages / total / list[]`。`list[]` 关键字段：

| 接口字段 | 含义 | 脚本归一化 |
|---|---|---|
| `rankNo` | 排名 | `rank` |
| `fullName` / `profileUrl` / `pictureUrl` | 账号名 / 主页 / 头像 | 同名；handle 由 profileUrl 末段解析 |
| `title` | 头衔（关联公司/职位） | `title` |
| `biography` | 账号简介 | `biography` |
| `countryName` / `countryCode` | 国家/地区 | `country` / `countryCode` |
| `xScore` | 综合影响力（满分 100） | `score` |
| `growthPercentage` | 日涨幅（如 `+0.13%`） | `growthPercentage` |
| `growthAbsolute` | 单日新增粉丝（如 `+313.2K`） | `growthAbsolute` / `growthAbsoluteNum` |
| `xFollowerCount` | X 粉丝数原始值 | `xFollowers` / `xFollowersFmt` |
| `categoriesJson` | 行业标签（primary=true 的 root_name） | `industries` |
| `badgesJson` | 专题/公益标签 | `topics` / `cause` |

## 2. 账号推文时间线

`POST https://redfox.hk/story/api/x/userTimeline`

请求：

```json
{
  "screenName": "elonmusk",
  "pageNum": 1,
  "source": <SOURCE>   // 固定来源标识，每次请求必传；具体值由脚本 SOURCE 常量注入
}
```

- `screenName` 与 `restId` 至少传一个（缺参返回 `code=3203`，msg 含「userName 和 restId 至少传一个」）
- `source` 为固定来源标识（已内置于脚本 `SOURCE` 常量），不对用户展示
- GET 方式不可用（返回 `code=500` 参数校验错误）

响应 `data`：

| 字段 | 含义 |
|---|---|
| `timeline[]` | 推文列表（第一页约 20 条） |
| `timeline[].tweetId` | 推文 ID → 原文链接 `https://x.com/<handle>/status/<tweetId>` |
| `timeline[].text` | 推文正文（`RT @` 开头为转载） |
| `timeline[].createdAt` | 格式 `Wed Sep 23 06:52:20 +0000 2026`（`%a %b %d %H:%M:%S %z %Y`） |
| `timeline[].likeCount / retweetCount / replyCount / viewCount` | 互动数据 |
| `nextCursor / prevCursor` | 翻页游标（本 skill 只取第一页，不使用） |
| `pinned` | 置顶推文（结构同 timeline 元素） |

注意：`timeline[].author.username` 可能为 `null`，账号归属以请求时的 `screenName` 为准。
