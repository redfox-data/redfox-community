# 抖音涨粉榜接口文档

## 基本信息

| 项目 | 说明 |
|------|------|
| 接口路径 | `POST https://redfox.hk/story/api/dyData/getDyRiseFansRank` |
| Content-Type | `application/json` |
| 认证方式 | API Key 认证（请求头 `X-API-KEY`，值以 `ak_` 开头） |

## 请求参数（Body - JSON）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `dateType` | Integer | 否 | 榜单日期类型：`1`-日榜 `2`-周榜 `3`-月榜，默认 `1`（日榜） |
| `rankDate` | String | 否 | 榜单日期，格式：`yyyy-MM-dd`，默认查询最近日榜日期 |
| `category` | String | 否 | 分类展示名称（如"个人才艺"、"生活vlog"等），默认全部 |
| `source` | String | 否 | 来源标识，用于调用次数限制 |

### 请求示例

```json
{
  "dateType": 1,
  "rankDate": "2026-05-28",
  "category": "个人才艺",
  "source": "test"
}
```

## 响应参数

返回类型：`List<DyRiseFansRankVO>`

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `ranking` | Integer | 排名 |
| `category` | String | 分类（展示名称） |
| `listType` | Integer | 榜单类型：`1`-日榜 `2`-周榜 `3`-月榜 |
| `date` | String | 榜单日期 |
| `secUid` | String | 安全用户ID |
| `nickname` | String | 账号名称 |
| `avatar` | String | 头像URL |
| `accountLink` | String | 账号链接 |
| `followerCount` | Long | 总粉丝数 |
| `fansIncrRate` | BigDecimal | 涨粉率 |
| `addFollowerCount` | Integer | 粉丝增量 |

## 响应示例

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "ranking": 1,
      "category": "个人才艺",
      "listType": 1,
      "date": "2026-05-28",
      "secUid": "MS4wLjABAAAAxxxxxxxxxxxx",
      "nickname": "示例账号",
      "avatar": "https://example.com/avatar.jpg",
      "accountLink": "https://www.douyin.com/user/MS4wLjABAAAAxxxxxxxxxxxx",
      "followerCount": 12345678,
      "fansIncrRate": 0.15,
      "addFollowerCount": 50000
    }
  ]
}
```

## 错误码

| code | 说明 |
|------|------|
| 200 | 成功 |
| 500 | 业务异常，具体原因见 msg 字段 |

### 常见业务错误

| msg | 场景 |
|-----|------|
| 今日调用次数已达上限，请明日再试 | source 标识对应的每日调用次数已达上限 |

## 错误响应示例

```json
{
  "code": 500,
  "msg": "今日调用次数已达上限，请明日再试",
  "data": null
}
```

## 支持的分类列表（27个）

全部、个人才艺、生活vlog、财富理财、二次元、居家装修、学习教育、小剧场、数码科技、旅行、美食、化妆美容、动物、亲子、汽车、情感、三农、健康医学、潮流风尚、舞蹈才艺、颜值造型、人文、音乐、影视、身体锻炼、体育、明星娱乐、游戏
