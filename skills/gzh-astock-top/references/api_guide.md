# A股公众号大V API 接口说明

## 概览

本脚本使用单接口策略：**1次调用** `dailyPublish` 接口，批量获取49个固定账号在指定日期发布的文章数据。服务端直接完成日期筛选并返回 workUrl，无需二次查询。

---

## 核心接口：每日发布文章查询

**请求地址**：`POST https://redfox.hk/story/api/gzh/search/dailyPublish`

**请求头**：
```
Content-Type: application/json
X-API-Key: <REDFOX_API_KEY>
```

### 请求参数

```json
{
  "date": "2026-06-15",
  "accountNames": ["央视财经", "招商策略", "laoduo"],
  "source": "A股公众号大V-GitHub"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `date` | string | 是 | 查询日期 yyyy-MM-dd |
| `accountNames` | array | 是 | 公众号名称列表（最多49个） |
| `source` | string | 否 | 来源标识 |

### 返回格式

```json
{
  "code": 2000,
  "msg": "成功",
  "data": {
    "accounts": [
      {
        "accountName": "招商策略",
        "accountId": "xxx",
        "avgReadCount": 85000,
        "redfoxIndex": 72.3,
        "description": "招商证券策略研究",
        "verifyName": "招商证券股份有限公司",
        "works": [
          {
            "title": "A股反弹信号确认",
            "publishTime": "2026-06-15 08:00:00",
            "clicksCount": 100000,
            "likeCount": 3200,
            "commentCount": 156,
            "workUrl": "https://mp.weixin.qq.com/..."
          }
        ]
      }
    ],
    "totalAccounts": 32,
    "totalArticles": 38
  }
}
```

### 返回字段说明

**data 顶层字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `accounts` | array | 当日有文章的账号列表（服务端已按日期筛选） |
| `totalAccounts` | int | 有文章的账号数 |
| `totalArticles` | int | 文章总数 |

**accounts 元素字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `accountName` | string | 公众号名称 |
| `accountId` | string | 公众号ID |
| `avgReadCount` | int | 平均阅读数 |
| `redfoxIndex` | float | 红狐指数 |
| `description` | string | 账号描述 |
| `verifyName` | string | 认证主体名称 |
| `works` | array | 当日文章列表（已按日期筛选） |

**works 元素字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `title` | string | 文章标题 |
| `publishTime` | string | 发布时间 |
| `clicksCount` | int | 阅读数 |
| `likeCount` | int | 点赞数 |
| `commentCount` | int | 评论数 |
| `workUrl` | string | 文章链接（服务端直接返回，无需二次补全） |

---

## 调用流程

```
1次调用 dailyPublish（传入49个固定账号名 + 日期）
    ↓
服务端按日期筛选 → 返回当日有文章的账号列表（含workUrl）
    ↓
脚本按 FIXED_PERSONAL_ACCOUNTS / FIXED_OFFICIAL_ACCOUNTS 分类
    ↓
按 avgReadCount 降序排序输出
```

**优势（相比旧版）**：
- 旧版：hotArticle × 15次 + gzhUser/query × 10批 + hotArticle × N次补链 ≈ 40+ 次调用
- 新版：**1次调用**，速度更快，API消耗大幅减少

---

## 常见错误码

| code | 说明 |
|------|------|
| 2000 | 成功 |
| 3106 | API Key 无效 |
| 3107 | API Key 过期 |
| 3108 | 限频 |
# A股公众号大V API 接口说明

## 概览

本脚本采用两步获取策略：
1. **Step 1**: 通过爆款文章搜索接口获取A股相关文章，提取公众号作者名
2. **Step 2**: 通过账号查询接口批量获取账号详情与最新文章

---

## Step 1: 爆款文章搜索接口

**请求地址**：`POST https://redfox.hk/story/api/gzh/search/hotArticle`

**请求头**：
```
Content-Type: application/json
X-API-Key: <REDFOX_API_KEY>
```

### 请求参数

```json
{
  "keyword": "A股",
  "startDate": "2026-06-08",
  "endDate": "2026-06-15",
  "source": "A股公众号大V-GitHub"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 搜索关键词 |
| `startDate` | string | 是 | 开始日期 yyyy-MM-dd |
| `endDate` | string | 是 | 结束日期 yyyy-MM-dd |
| `source` | string | 否 | 来源标识 |

### 返回格式

```json
{
  "code": 2000,
  "msg": "成功",
  "data": {
    "articles": [
      {
        "id": "xxx",
        "title": "A股反弹...",
        "author": "招商策略",
        "clicksCount": 100000,
        "likeCount": 3200,
        "commentCount": 156,
        ...
      }
    ],
    "latestHotArticles": [],
    "hotTopics": [],
    "total": 50
  }
}
```

### 文章字段（用于提取作者名）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 文章ID |
| `title` | string | 文章标题 |
| `author` | string | **公众号名称（关键字段）** |
| `clicksCount` | int | 阅读数 |
| `likeCount` | int | 点赞数 |
| `commentCount` | int | 评论数 |

### 搜索关键词列表

脚本使用以下A股相关关键词进行搜索：

- A股
- 股票
- 股市
- 炒股
- 券商
- 牛市
- 基金投资
- 股市分析

每个关键词单独请求，结果合并去重。

---

## Step 2: 账号详情查询接口

**请求地址**：`POST https://redfox.hk/story/api/gzhUser/query`

**请求头**：
```
Content-Type: application/json
X-API-Key: <REDFOX_API_KEY>
```

### 请求参数

```json
{
  "accountNames": "招商策略,雪球,中国基金报",
  "source": "A股公众号大V-GitHub"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `accountNames` | string | 是 | 公众号名称列表，逗号分隔 |
| `accountIds` | string | 否 | 公众号ID列表，逗号分隔 |
| `source` | string | 否 | 来源标识 |

### 返回格式

```json
{
  "code": 2000,
  "msg": "成功",
  "data": [
    {
      "accountName": "招商策略",
      "accountId": "xxx",
      "avgReadCount": 85000,
      "redfoxIndex": 72.3,
      "description": "招商证券策略研究",
      "avatar": "https://...",
      "works": [
        {
          "id": "xxx",
          "title": "A股反弹信号确认",
          "summary": "...",
          "publishTime": "2026-06-15 08:00:00",
          "clicksCount": 100000,
          "likeCount": 3200,
          "commentCount": 156,
          "watchCount": 890,
          "shareCount": 450,
          "coverUrl": "https://...",
          "workUrl": "https://mp.weixin.qq.com/..."
        }
      ]
    }
  ]
}
```

### 账号字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `accountName` | string | 公众号名称 |
| `accountId` | string | 公众号ID |
| `avgReadCount` | int | **平均阅读数** |
| `redfoxIndex` | float | **红狐指数** |
| `description` | string | 账号描述 |
| `avatar` | string | 头像URL |
| `verifyName` | string | 认证名称 |
| `accountType` | string | 账号类型 |
| `works` | array | 近7天文章列表 |

### 作品字段（works数组元素）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 文章ID |
| `title` | string | 文章标题 |
| `summary` | string | 文章摘要 |
| `publishTime` | string | 发布时间 |
| `clicksCount` | int | 阅读数 |
| `likeCount` | int | 点赞数 |
| `commentCount` | int | 评论数 |
| `watchCount` | int | 在看数 |
| `shareCount` | int | 分享数 |
| `coverUrl` | string | 封面图URL |
| `workUrl` | string | 文章链接 |

### 批量查询策略

- 每次最多查询5个账号（避免接口限制）
- 超过5个时分批查询
- 批次间间隔0.3秒（限流保护）

---

## 脚本输出格式

脚本将两个接口的数据合并后输出为 JSON：

```json
{
  "date": "2026-06-15",
  "total": 25,
  "totalAuthorsFound": 30,
  "accounts": [
    {
      "accountName": "招商策略",
      "accountId": "xxx",
      "avgReadCount": 85000,
      "redfoxIndex": 72.3,
      "description": "招商证券策略研究",
      "latestArticle": {
        "title": "A股反弹信号确认",
        "clicksCount": 100000,
        "likeCount": 3200,
        "commentCount": 156,
        "publishTime": "2026-06-15 08:00:00"
      }
    }
  ]
}
```

### 输出字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `date` | string | 查询日期 |
| `total` | int | 成功获取详情的账号数量 |
| `totalAuthorsFound` | int | Step1发现的总作者数 |
| `accounts` | array | 账号列表（按avgReadCount降序） |
| `accounts[].latestArticle` | object/null | 最新文章数据，无文章时为null |

---

## 常见错误码

| code | 说明 |
|------|------|
| 2000 | 成功 |
| 3106 | API Key 无效 |
| 3107 | API Key 过期 |
| 3108 | 限频 |
