# Facebook 主页帖子接口文档

## 接口基础信息

| 字段 | 值 |
|------|-----|
| 接口地址 | `https://redfox.hk/story/api/fb/userPosts` |
| 请求方式 | POST |
| Content-Type | `application/json` |
| 认证方式 | 请求头 `REDFOX_API_KEY`（值取自环境变量 `REDFOX_API_KEY`，格式 `ak_xxxx`） |

> 注意：本接口的鉴权头名为 `REDFOX_API_KEY`，与其他红狐接口（如 X 榜单使用 `X-API-KEY`）不同。

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| url | string | 否 | 主页 URL（与 pageId 至少传一个），格式 `facebook.com/用户名`，如 `https://www.facebook.com/Meta` |
| pageId | string | 否 | 主页 ID（与 url 至少传一个），传 pageId 查询更快 |
| cursor | string | 否 | 分页游标，取上一次响应 `data.paginationToken`；为空表示无更多数据 |
| source | string | 是 | 固定来源标识，每次请求必传 |

## 响应结构

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| code | integer | 2000 表示成功 |
| msg | string | 响应消息 |
| data.count | integer | 本次返回帖子数量 |
| data.items | array | 帖子列表，按发布时间倒序 |
| data.paginationToken | string | 分页令牌（Base64），作为下次请求 cursor 传入；为空表示无更多数据 |

### items 元素字段

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| postId | string | 帖子唯一 ID |
| permalink | string | 帖子永久链接 |
| caption | string | 帖子正文文本 |
| likeCount | integer | 点赞数量 |
| commentCount | integer | 评论数量 |
| mediaType | string / null | 媒体类型（图片帖可能为 null） |
| imageUrl | string | 帖子首图 URL |
| mediaUrls | array | 全部媒体资源 URL 列表 |
| videoUrl | string / null | 视频播放地址（图片帖为 null） |
| videoDuration | string / null | 视频时长（图片帖为 null） |
| publishedAt | string | 发布时间（ISO 8601 UTC，如 `2026-10-18T04:07:25.000Z`） |
| feedbackId | string | 帖子互动反馈 ID（Base64） |
| author.displayName | string | 作者显示名称 |
| author.id | string | 作者主页 ID |

## 响应示例

```json
{
  "code": 2000,
  "data": {
    "count": 3,
    "items": [
      {
        "author": { "displayName": "奔跑吧肥祥", "id": "100044377571572" },
        "caption": "男友說，我們的小豆樹越長越大，要換盆子了。…",
        "commentCount": 77,
        "feedbackId": "ZmVlZGJhY2s6MTY1OTU0MTE1MjIwMTc4OA==",
        "imageUrl": "https://scontent-phl2-1.xx.fbcdn.net/v/t39.30808-6/857045839_..._n.jpg?oh=...&oe=6ADE19A2",
        "likeCount": 3564,
        "mediaType": null,
        "mediaUrls": ["https://scontent-phl2-1.xx.fbcdn.net/v/t39.30808-6/857045839_..._n.jpg?oh=...&oe=6ADE19A2"],
        "permalink": "https://www.facebook.com/permalink.php?story_fbid=pfbid0S9GPM3mYXEq...&id=100044377571572",
        "postId": "1659541152201788",
        "publishedAt": "2026-10-18T04:07:25.000Z",
        "videoDuration": null,
        "videoUrl": null
      }
    ],
    "paginationToken": "sc2.eyJzIjoiYiIsImMiOiJDZzhPYjNKbllXNXBZMTlqZFhKemIzSUpBQUFDUkVG..."
  },
  "msg": "成功"
}
```

## 错误码

| code | 含义 |
| ---- | ---- |
| 2000 | 成功 |
| 3105 | API Key 已禁用 / 无效，需重新生成 |
| 其他 | 错误，以 msg 为准 |

## 安全说明

- 密钥仅用于请求头，禁止硬编码到代码、提示词、日志或输出文件
- 临时密钥只通过环境变量传递，不落盘
