# API 配置说明

## 环境变量配置

在使用本 skill 前，需配置以下环境变量（或在 Qoder 设置中配置 API Key）：

```bash
REDFOX_API_KEY=your_api_key_here
```

## 接口说明

### 查询点赞排行榜

```
POST https://redfox.hk/story/api/dy/search/likesRank
Content-Type: application/json
```

**请求头：**

| Header    | 说明                                         |
| --------- | -------------------------------------------- |
| X-API-KEY | API 密钥，从环境变量 `REDFOX_API_KEY` 中获取 |

**请求体（JSON）：**

| 参数      | 类型   | 必填 | 说明                                 |
| --------- | ------ | ---- | ------------------------------------ |
| type      | string | 否   | 赛道分类，默认"全部"，见下方分类列表 |
| startTime | string | 否   | 查询起始时间，格式 YYYY-MM-DD        |
| endTime   | string | 否   | 查询结束时间，格式 YYYY-MM-DD        |
| source    | string | 是   | 固定参数                             |

**响应示例：**

```json
{
  "code": 2000,
  "data": [
    {
      "accountId": "1234567890",
      "accountName": "账号名",
      "avatarUrl": "https://p3.douyinpic.com/aweme-avatar/xxx.jpeg",
      "category": "美食",
      "followerCount": 1000000,
      "collectCount": 100000,
      "commentCount": 50000,
      "shareCount": 30000,
      "likeCount": 500000,
      "title": "作品标题",
      "content": "作品正文",
      "publishTime": "2026-05-28 12:00:00",
      "workId": "7644570847852254031",
      "workUrl": "https://www.iesdouyin.com/share/video/7644570847852254031"
    }
  ]
}
```

## 状态码说明

| 状态码 | 说明     |
| ------ | -------- |
| 2000   | 请求成功 |

## 错误处理

| 错误码 | 说明                 | 处理方式                  |
| ------ | -------------------- | ------------------------- |
| 401    | API Key 无效或未配置 | 提示用户检查 API Key 配置 |
| 404    | 该日期数据不存在     | 提示用户该日期暂无数据    |
| 429    | 请求频率超限         | 提示稍后重试              |
| 500    | 服务端错误           | 提示稍后重试              |

## 支持的赛道分类

```
全部、个人才艺、生活vlog、财富理财、二次元、居家装修、学习教育、小剧场、
数码科技、旅行、美食、化妆美容、动物、亲子、汽车、情感、三农、健康医学、
潮流风尚、舞蹈才艺、颜值造型、人文、音乐、影视、身体锻炼、体育、明星娱乐、游戏
```

## 数据更新时间

- 每日 15:00 更新昨日全天数据
- 可回溯范围：最近 30 天
