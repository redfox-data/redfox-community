# 小红书热门数据格式说明

## 概览

本文档定义了小红书热门数据查询脚本 `fetch_xhs_trends.py` 的输入输出格式规范。

## 输入格式

### 脚本参数

```bash
python scripts/fetch_xhs_trends.py --keyword <关键词> [选项]
```

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--keyword` | 是 | 搜索关键词（支持多个关键词，逗号分隔，最多5个，总长度不超过200字符） | - |
| `--start-date` | 否 | 开始日期，格式 yyyy-MM-dd | 最近30天 |
| `--max-items` | 否 | 每类内容最多展示数量 | 50 |
| `--output-format` | 否 | 输出格式：text、json 或 markdown | markdown |
| `--debug` | 否 | 调试模式，打印原始API响应 | False |

## 输出格式

### 四类爆款内容

脚本返回**近30天**的小红书热门数据，包含以下四类爆款内容：

| 内容类型 | 适用场景 |
|---------|---------|
| **新手友好爆款** | 适合模仿学习，发现低成本爆款 |
| **当日点赞爆款** | 了解当前最热门内容 |
| **爆发增长内容** | 发现快速增长的内容 |
| **持续增长内容** | 发现持续增长的内容 |

### 作品数据字段（完整）

每个作品包含以下字段：

#### 作品基本信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `photoId` | string | 作品ID（唯一标识） |
| `title` | string | 作品标题 |
| `desc` | string | 作品描述/正文 |
| `publicTime` | string | 发布时间（格式：YYYY-MM-DD HH:MM:SS） |

#### 作者信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `userId` | string | 作者ID |
| `userName` | string | 作者名称 |
| `userHeadUrl` | string | 作者头像URL |
| `fans` | int | 粉丝数 |

**作者主页链接拼接规则**：
```
https://www.xiaohongshu.com/user/profile/{userId}
```

**作品链接拼接规则**：
```
https://www.xiaohongshu.com/explore/{photoId}
```

#### 互动数据（非增量类）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `useLikeCount` | int | 点赞数 |
| `collectedCount` | int | 收藏数 |
| `useCommentCount` | int | 评论数 |
| `useShareCount` | int | 分享数 |
| `interactiveCount` | int | 互动总数 |

#### 互动数据（增量类）

增量类（单日增量、七日增量）的数据在 `anaAdd` 对象中：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `anaAdd.addLikeCount` | int | 新增点赞数 |
| `anaAdd.addCollectedCunt` | int | 新增收藏数（注意：API字段名有拼写错误） |
| `anaAdd.addCommentCount` | int | 新增评论数 |
| `anaAdd.addShareCount` | int | 新增分享数 |
| `anaAdd.addInteractiveount` | int | 新增互动总数（注意：API字段名有拼写错误） |
| `anaAdd.useLikeCount` | int | 总点赞数 |
| `anaAdd.collectedCount` | int | 总收藏数 |
| `anaAdd.useCommentCount` | int | 总评论数 |
| `anaAdd.useShareCount` | int | 总分享数 |
| `anaAdd.interactiveCount` | int | 总互动数 |
| `anaAdd.pred_readnum` | int | 预测阅读数 |

#### 图片链接

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `coverUrl` | string | 封面图URL |
| `thumbnail` | string | 缩略图URL |

---

## 评分维度定义

基于爆款数据分析，提炼以下4个评分维度：

**评分总原则**：客观公正，不压分，好与坏差距拉开，优秀的能上90就上90。

### 1. 关键词覆盖（满分100分）

**评分要点**：是否包含领域高频热词

| 覆盖率 | 得分区间 | 说明 |
|--------|---------|------|
| 50%以上 | 80-100分 | 覆盖大部分爆款高频词 |
| 30%-50% | 60-80分 | 覆盖部分高频词 |
| 10%-30% | 40-60分 | 覆盖少量高频词 |
| 10%以下 | 40分以下 | 几乎未覆盖高频词 |

**高频词来源**：从爆款数据的 `title` 和 `desc` 字段中提取

### 2. 结构完整度（满分100分）

**评分要点**：内容结构是否符合爆款模式

| 结构要素 | 分值 | 说明 |
|---------|------|------|
| 开头钩子 | +25分 | 前3行能吸引注意力（痛点共鸣/惊人数据/反差对比） |
| 分点结构 | +25分 | 内容分点清晰，易于阅读 |
| 干货内容 | +25分 | 提供有价值的信息或方法 |
| 互动引导 | +25分 | 结尾引导用户互动（评论/收藏/分享） |

### 3. 时效性（满分100分）

**评分要点**：是否结合当前热点

| 时效性等级 | 得分区间 | 说明 |
|-----------|---------|------|
| 热点内容 | 90-100分 | 结合当前热门事件/话题 |
| 季节内容 | 80-90分 | 结合季节/节日/特定时段 |
| 常青内容 | 70-85分 | 长期有效的内容，无时效性 |
| 过时内容 | 60分以下 | 内容已过时或不再适用 |

**评分原则**：不压分，常青内容也给到70-85分的基础分，热点内容可达满分。

### 4. 内容质量（满分100分）

**评分要点**：内容的整体质量

| 质量要素 | 分值 | 说明 |
|---------|------|------|
| 干货密度 | +25分 | 信息量充足，有实用价值 |
| 排版清晰 | +25分 | 分段合理，易于阅读 |
| Emoji使用 | +25分 | 适量使用（每段1-2个），不过度 |
| 标签合理 | +25分 | 标签与内容相关，数量适中 |

**评分原则**：优秀内容不压分，四项都达标即可达到90分以上；差距拉开，差的文案果断给低分。

---

## JSON 输出示例

```json
{
  "keyword": "高考",
  "low_fan_explosive": [
    {
      "photoId": "69aa603c0000000015021b18",
      "title": "对于26高考女宝们的选大学建议",
      "desc": "一定要选人文关怀好以及男女平等的大学...",
      "publicTime": "2026-03-06 13:03:56",
      "userId": "68ebaae60000000037006191",
      "userName": "Alley",
      "fans": 2,
      "useLikeCount": 23439,
      "collectedCount": 15610,
      "useCommentCount": 846,
      "useShareCount": 697,
      "interactiveCount": 39895,
      "coverUrl": "http://sns-img-hw.xhscdn.com/..."
    }
  ],
  "daily_like_top": [...],
  "daily_increment": [...],
  "weekly_increment": [...]
}
```
