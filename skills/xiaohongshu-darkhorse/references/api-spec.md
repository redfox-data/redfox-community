# 小红书黑马爆文榜API接口规范

## 接口信息

**接口地址**: `https://redfox.hk/story/api/cozeSkill/getLowPowderExplosiveArticle`

**请求方式**: POST

**认证方式**: API Key，通过请求头 `REDFOX_API_KEY` 传递

**内容类型**: application/json

## 请求头

| 名称 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| REDFOX_API_KEY | string | 是 | 平台鉴权令牌，每次请求必填 | ak_xxxxxx |
| Content-Type | string | 是 | 请求体数据类型 | application/json |

## 请求参数

请求体为 JSON：

| 参数 | 类型 | 必填 | 说明 | 示例 |
| --- | --- | --- | --- | --- |
| category | String | 是 | 内容分类（见下方分类列表） | 潮流鞋包 |
| rankDate | String | 是 | 统计窗口开始日期，格式 yyyy-MM-dd，可查询近30天内任意一天（接口文档口径最长回溯30天）；实际按单日出榜 | 2026-09-08 |
| source | String | 是 | 来源标识，固定值「小红书黑马爆文榜-GitHub」 | 小红书黑马爆文榜-GitHub |

## 分类列表

| 分类名称 | 说明                 |
| -------- | -------------------- |
| 综合全部 | 所有分类合集，默认值 |
| 出行代步 | 交通出行相关         |
| 休闲爱好 | 休闲娱乐相关         |
| 影视娱乐 | 影视综艺相关         |
| 数码科技 | 数码产品、科技相关   |
| 医疗保健 | 医疗健康相关         |
| 综合杂项 | 其他杂项             |
| 星座情感 | 情感、星座相关       |
| 时尚穿搭 | 时尚搭配相关         |
| 婚庆婚礼 | 婚庆相关             |
| 拍摄记录 | 摄影、Vlog相关       |
| 学习教育 | 学习、考试相关       |
| 化妆美容 | 美妆护肤相关         |
| 居家装修 | 家居装修相关         |
| 旅行度假 | 旅游出行相关         |
| 亲子育儿 | 亲子、母婴相关       |
| 个人护理 | 个人洗护相关         |
| 美味佳肴 | 美食烹饪相关         |
| 职业发展 | 职场、求职相关       |
| 宠物天地 | 宠物相关             |
| 潮流鞋包 | 潮流鞋包相关         |
| 日常生活 | 日常技巧相关         |
| 科学探索 | 科学科普相关         |
| 新闻资讯 | 新闻时事相关         |
| 体育锻炼 | 运动健身相关         |

## 请求示例

```bash
curl -X POST "https://redfox.hk/story/api/cozeSkill/getLowPowderExplosiveArticle" \
  -H "REDFOX_API_KEY: $REDFOX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"category": "潮流鞋包", "rankDate": "2026-09-08", "source": "小红书黑马爆文榜-GitHub"}'
```

## 响应示例

```json
{
  "code": 2000,
  "data": [
    {
      "collectedCount": "5267",
      "coverUrl": "https://sns-img-hw.xhscdn.net/spectrum/1040g34o3246nb5os0m0g5othldk9i03rdtftq9g?imageView2/2/w/1080/format/webp",
      "desc": "为什么姐姐能吃！#美妆 #美妆AI #抽象 #情感",
      "fans": "4w+",
      "interactiveCount": null,
      "photoId": "6a8a472f000000001801be25",
      "pred_readnum": null,
      "publicTime": "2026-08-23 09:04:47",
      "thumbnail": "http://sns-img-hw.xhscdn.net/spectrum/1040g34o3246nb5os0m0g5othldk9i03rdtftq9g?imageView2/2/w/375/format/webp",
      "title": "爆款口红（三）",
      "useCommentCount": "979",
      "useLikeCount": "2w+",
      "useShareCount": "1115",
      "userHeadUrl": "https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31vvol28q566g5othldk9i03raiarmig?imageView2%2F2%2Fw%2F540%2Fformat%2Fwebp&sign=0da19cd0d3bec831d89512b1c8478bd6&t=6a8a240c",
      "userId": "63b1ab68000000002601007b",
      "userName": "再来一份耋米花"
    }
  ],
  "msg": "成功"
}
```

## 返回值与结构

统一包装为 `code`、`msg`、`data`。`code=2000` 表示成功。

## 响应字段说明

| 字段名           | 类型    | 说明                              |
| ---------------- | ------- | --------------------------------- |
| title            | String  | 笔记标题                          |
| userName         | String  | 作者昵称                          |
| userId           | String  | 用户标识（24位十六进制）          |
| userHeadUrl      | String  | 作者头像                          |
| fans             | String  | 作者粉丝数（可能为"4w+"格式）     |
| publicTime       | String  | 发布时间（yyyy-MM-dd HH:mm:ss）   |
| photoId          | String  | 笔记标识                          |
| coverUrl         | String  | 笔记封面图片                      |
| thumbnail        | String  | 笔记缩略图                        |
| desc             | String  | 笔记描述/标签                     |
| collectedCount   | String  | 收藏数                            |
| interactiveCount | String  | 互动数（**可能为null**）          |
| useCommentCount  | String  | 评论数                            |
| useLikeCount     | String  | 点赞数（可能为"2w+"格式）         |
| useShareCount    | String  | 分享数                            |
| pred_readnum     | String  | 预估阅读数（可能为null）          |

## 脚本实现层面的字段适配

本技能脚本在接口原始字段之上做了以下适配（见 `fetch_darkhorse_articles.py` 的 `normalize_article()`）：

1. **链接拼接**：接口不直接返回笔记与作者主页链接，脚本按小红书标准 URL 规则拼接：
   - 笔记链接 = `https://www.xiaohongshu.com/explore/{photoId}`
   - 作者主页 = `https://www.xiaohongshu.com/user/profile/{userId}`

2. **互动总数兜底**：`interactiveCount` 可能为 null，此时按 `点赞 + 收藏 + 评论 + 分享` 四项求和（"2w+"等格式按 1w=10000 换算），作为排序与展示依据。

3. **数值格式解析**：`useLikeCount`、`fans` 等字段可能为 `"2w+"`、`"4w+"` 格式，解析时统一换算为整数。

## 注意事项

1. **日期格式**：
   - 必须使用 yyyy-MM-dd 格式
   - 示例：2026-09-08（正确） vs 2026/09/08（错误）

2. **rankDate 语义**：
   - rankDate 是统计窗口的**开始日期**
   - 接口文档标注窗口最长回溯 30 天；实测 29 天前窗口可用（返回 50 条），但个别近期历史日期（如 2026-09-15）会返回「接口执行异常，积分未扣除: 日期格式错误」——格式本身正确，疑似当日数据断档或服务端窗口计算差异，遇此报错不要检查字符串格式
   - 脚本默认取 7 天前（稳定可用）；用户指定的日期报日期类错误或无数据时，脚本自动回退用默认窗口重查一次

3. **category参数**：
   - 必传参数
   - 必须使用上方分类列表中的名称
   - 默认传"综合全部"

4. **数据更新时间**：
   - 每天 17:30 开始更新昨日数据（17:30 前查询昨日窗口会返回成功但 0 条数据，属正常现象）
   - 实测按单日出榜：返回笔记的发布日期集中在 rankDate 当天或前一天（T-1），具体取决于该期榜单快照的生成时点（如 2026-10-11 榜单收录 10-10 发布的笔记，2026-10-13 榜单收录 10-13 发布的笔记）

5. **积分消耗**：
   - 每次调用会扣除积分（包括返回空数据的请求）
   - 脚本内置策略：业务响应已到达时不再重试，仅连接层异常最多重试 3 次，避免重复扣积分
   - 主查询流程最多 2 次 API 请求（首次查询 + 空数据自动回退）

6. **错误处理**：
   - 网络超时：45秒
   - HTTP 非200：有限重试后报错（限流时接口可能返回 HTML 错误页而非 JSON）
   - 业务错误：优先展示接口返回的 msg

## 密钥获取与安全说明

- 本API需要使用API密钥 `REDFOX_API_KEY`。
- API密钥由 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`)提供。
- 请前往 [红狐 hub](https://redfox.hk?source=github) 注册并登录账号，在密钥管理模块创建 API密钥。
- 复制并仅在请求头中使用API密钥。
- 在提供密钥前，请先确认密钥来源、可用范围、有效期及是否支持重置/撤销。
- 禁止在代码、提示词、日志或输出文件中硬编码/明文暴露密钥。
