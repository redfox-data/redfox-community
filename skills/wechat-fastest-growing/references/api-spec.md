# 公众号黑马账号推荐 API 接口规范

## 接口信息

**接口地址**: `https://redfox.hk/story/api/cozeSkill/getGzhCozeSkillDataRaise`

**请求方式**: GET

**请求头**:
- `Content-Type`: application/json
- `X-API-KEY`: 通过三级回退机制获取（环境变量 → shell 配置文件 → 提示用户配置）

## 认证方式

脚本按以下三级回退读取 API Key：
1. **环境变量** `REDFOX_API_KEY`（推荐）
2. **环境变量** `COZE_REDFOX_API_7633629455969337344`（兼容旧变量名）
3. **Shell 配置文件** 自动探测（~/.bashrc / ~/.zshrc / ~/.bash_profile / ~/.profile），提取其中 `REDFOX_API_KEY` 的值
4. **提示用户配置**：未找到时输出配置指引并退出

请求使用原生 `requests` 库，不依赖任何 Coze 工作负载身份模块。

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| rankDate | String | 是 | 榜单日期（YYYY-MM-DD格式，如"2026-04-15"；支持相对日期"yesterday"/"today"） |
| source | String | 是 | 数据源（"公众号阅读增长榜-GitHub"） |

**时间参数说明**：
- **yesterday**: 昨天（用于查询昨日榜单）
- **today**: 今天（用于查询今日榜单）
- **YYYY-MM-DD**: 具体日期（如 2026-04-15）
- **时间限制**: 最早支持前30天的数据，超过30天会返回错误

### 示例1：获取昨日增长榜
```
GET https://redfox.hk/story/api/cozeSkill/getGzhCozeSkillDataRaise?rankDate=2026-04-15&source=公众号阅读增长榜-GitHub
```

### 示例2：获取指定日期增长榜
```
GET https://redfox.hk/story/api/cozeSkill/getGzhCozeSkillDataRaise?rankDate=2026-04-01&source=公众号阅读增长榜-GitHub
```

## 返回数据

### 成功响应
```json
{
  "code": 2000,
  "message": "success",
  "data": [
    {
      "rankPosition": 1,
      "accountId": "账号ID",
      "uid": 123456,
      "userName": "公众号名称",
      "userHeadUrl": "头像URL",
      "growthRate": 125.50,
      "rankDate": "2026-04-15",
      "minWork": {
        "photoId": "作品标识",
        "title": "作品标题",
        "coverUrl": "封面URL",
        "clicksCount": "10000",
        "shareCount": "500",
        "likeCount": "300",
        "watchCount": "200",
        "commentCount": "100",
        "publicTime": "发布时间",
        "summary": "摘要",
        "content": "原文内容",
        "oriUrl": "原文链接"
      },
      "maxWork": {
        "photoId": "作品标识",
        "title": "作品标题",
        "coverUrl": "封面URL",
        "clicksCount": "50000",
        "shareCount": "2000",
        "likeCount": "1500",
        "watchCount": "800",
        "commentCount": "400",
        "publicTime": "发布时间",
        "summary": "摘要",
        "content": "原文内容",
        "oriUrl": "原文链接"
      }
    }
  ]
}
```

### 响应字段说明

#### WxGrowthRankVo（主对象）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| rankPosition | Integer | 排名位置 |
| accountId | String | 公众号账号ID |
| uid | Integer | 用户ID |
| userName | String | 公众号名称 |
| userHeadUrl | String | 公众号头像URL |
| growthRate | BigDecimal | 增长率百分比 |
| rankDate | String | 榜单日期 |
| minWork | WorkDetail | 最低阅读作品数据 |
| maxWork | WorkDetail | 最高阅读作品数据 |

#### WorkDetail（作品详情内部类）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| photoId | String | 作品标识 |
| title | String | 标题 |
| coverUrl | String | 封面URL |
| clicksCount | String | 阅读数 |
| shareCount | String | 分享数 |
| likeCount | String | 点赞数 |
| watchCount | String | 在看数 |
| commentCount | String | 评论数 |
| publicTime | String | 发布时间 |
| summary | String | 摘要 |
| content | String | 原文内容 |
| oriUrl | String | 原文链接 |

### 错误响应

```json
{
  "code": 4000,
  "message": "错误信息",
  "data": null
}
```

## 注意事项

1. 日期参数必须为YYYY-MM-DD格式，或使用相对日期"yesterday"/"today"
2. 仅支持查询最近30天内的数据
3. 数据按增长率降序排列，rankPosition从1开始
4. 每个账号包含最高阅读和最低阅读两个作品数据
5. growthRate字段为百分比数值，如125.50表示125.50%的增长率
