# 爆款内容API接口规范

## 接口信息

**接口地址**: `https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData`

**请求方式**: GET

**请求头**:
- `Content-Type`: application/json
- `N-Token`: 2f9f88dbb743423dbf0a8db2977c49eb

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | String | 是 | 关键词（从用户输入中提取，空字符串表示获取全部爆文） |
| source | String | 是 | 数据源（固定值："公众号10w+阅读文章推荐"） |
| startDate | String | 否 | 开始日期（YYYY-MM-DD格式，如"2024-03-15"；空字符串表示不限时间，获取最近30天数据） |

**时间参数说明**：
- **daybeforeyesterday**: 特殊值，表示前天（用于获取最新推荐，如今天是2026-04-17，传入2026-04-15）
- **yesterday**: 特殊值，表示昨天（用于查询昨日数据）
- **YYYY-MM-DD**: 具体日期（如 2024-03-15）
- **空字符串**: 不限时间，获取最近30天数据
- **时间限制**: 最早支持前30天的数据，超过30天会返回错误
- **数据同步时间**: 每日下午6:30同步前一日数据

### 示例1：获取最新推荐（总榜）
```
GET https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData?keyword=&source=公众号10w+热门文章推荐&startDate=2026-04-15
```
注：如果今天是2026-04-17，获取最新推荐时传入2026-04-15（前天的日期）

### 示例2：战争领域爆文（不限时间）
```
GET https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData?keyword=战争&source=公众号10w+阅读文章推荐
```

### 示例3：指定日期查询
```
GET https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData?keyword=AI&source=公众号10w+阅读文章推荐&startDate=2024-03-15
```

## 返回数据

### 成功响应
```json
{
  "code": 2000,
  "message": "success",
  "tenWReadingRank": [
    {
      "title": "文章标题",
      "userName": "公众号名称",
      "accountId": "公众号ID",
      "type": "分类",
      "clicksCount": "5w+",
      "likeCount": 500,
      "interactiveCount": 50000,
      "publicTime": "2024-01-01 08:00:00",
      "oriUrl": "https://mp.weixin.qq.com/...",
      "summary": "文章摘要",
      "content": "文章内容"
    }
  ]
}
```

### 字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| tenWReadingRank | Array[Object] | 10w+阅读文章列表 |
| title | String | 文章标题 |
| userName | String | 公众号名称 |
| accountId | String | 公众号ID（用于生成名片链接） |
| type | String | 文章分类 |
| clicksCount | String | 阅读量（格式如"5w+"） |
| likeCount | Integer | 点赞数 |
| interactiveCount | Integer | 互动数（用于排序） |
| publicTime | String | 发布时间 |
| oriUrl | String | 文章链接 |
| summary | String | 文章摘要 |
| content | String | 文章内容 |

## 注意事项

1. **关键词提取规则**：
   - 用户输入"今日爆文"、"10w+文章"、"最新推荐"等 → keyword为空字符串""，startDate为"daybeforeyesterday"（前天）
   - 用户输入"推荐一下战争10w+阅读数文章" → 提取关键词"战争"，startDate为空字符串
   - 用户输入"昨天有哪些AI相关的爆文" → 提取关键词"AI"，startDate计算为昨天的日期

2. **source参数**：
   - 始终使用固定值："公众号10w+热门文章推荐"

3. **startDate参数**：
   - **最新推荐**: 传"daybeforeyesterday"（如今天是2026-04-17，传入2026-04-15）
   - **具体时间**: 根据用户描述转换为YYYY-MM-DD格式
   - **不限时间**: 传空字符串""，获取最近30天数据
   - **时间限制**: 最早支持前30天的数据
   - **数据同步**: 每日下午6:30同步前一日数据

4. **排序规则**：
   - 默认按互动数（interactiveCount）降序排序
   - 如果interactiveCount为0或不存在，则按clicksCount + likeCount*10计算

5. **错误处理**：
   - 网络超时：30秒
   - HTTP错误：显示状态码和响应内容
   - API错误：显示错误信息（成功码为2000）

## 使用建议

1. 最新推荐使用空字符串keyword和"daybeforeyesterday"startDate获取（如今天是2026-04-17，传入2026-04-15）
2. 领域查询需要从用户输入中智能提取关键词
3. 用户提到具体时间时，将时间描述转换为YYYY-MM-DD格式
4. 用户未提到时间时，startDate传空字符串获取最近30天数据
5. 日期不能早于30天前，晚于今天
6. 数据同步时间：每日下午6:30同步前一日数据
