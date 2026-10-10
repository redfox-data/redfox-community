# 懂车帝关键词搜索红狐 API 规范

## 通用约定

- Host：`https://redfox.hk`
- Method：`POST`
- 鉴权请求头：`REDFOX_API_KEY: <REDFOX_API_KEY>`
- Content-Type：`application/json`
- 成功码兼容：接口文档示例为 `code=200`；红狐平台常见成功码为 `code=2000`。脚本兼容 `200` 与 `2000`。
- API Key 获取：[红狐hub](https://redfox.hk/settings/api-keys?source=github)
- 禁止在代码、提示词、日志或输出文件中硬编码/明文暴露 API Key。

## 关键词搜索作品

Endpoint：`/story/api/dongchedi/searchWork`

请求参数：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `keyword` | String | 是 | 搜索关键词 | `智界` |
| `offset` | String | 是 | 翻页偏移量，从 `0` 开始，翻页 `+20` | `0` |
| `sourceType` | String | 是 | 内容类型：`1`=综合，`2`=视频 | `1` |
| `source` | String | 是 | 来源标识，固定值「懂车帝作品关键词搜索-GitHub」 | `懂车帝作品关键词搜索-GitHub` |

请求示例：

```json
{
  "keyword": "智界",
  "offset": "0",
  "sourceType": "1",
  "source": "懂车帝作品关键词搜索-GitHub"
}
```

响应字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `data.hasMore` | String | 是否有更多数据：`1`=有，`0`=无 |
| `data.workList[]` | Array | 作品列表 |
| `workId` | String | 作品 ID |
| `workUrl` | String | 作品链接，可能以 `//` 开头 |
| `title` | String | 作品标题 |
| `authorId` | String | 作者 ID |
| `authorName` | String | 作者昵称 |
| `likeCount` | Integer | 点赞数 |
| `playCount` | Integer | 播放数 |
| `commentCount` | Integer | 评论数 |
| `publishTime` | String | 秒级时间戳 |
