# 全网内容出海信息源 - 核心工作流程

## 📋 执行流程概览

```
第零步:日期有效性预检(必须)
  ↓
第一步:生成爆款日报(调用API)
  ↓
第二步:执行深度分析(自动)
  ↓
输出:HTML日报 + 终端摘要
```

## ⛔ 第零步:日期预检规则(核心)

### 数据更新机制

- **更新时间**:每日15:00更新前一天的数据
- **15:00前**:最新可用日期 = T-2(前天)
- **15:00后**:最新可用日期 = T-1(昨天)

### 强制拦截逻辑

```python
DATA_UPDATE_HOUR = 15  # 每日15:00更新前一天数据

def calculate_latest_date():
    now = datetime.now()
    if now.hour < DATA_UPDATE_HOUR:
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
```

### Agent行为约束

1. **未经用户确认,禁止调用任何数据接口**
2. **禁止自动执行 `--latest` 参数**
3. 目标日期无数据时,必须输出提示并等待用户明确确认

### 标准提示模板

```
**⚠️{查询日期}数据尚未更新**
数据更新规则:每日15:00更新前一天的数据
当前可查询的最新日期:{最新可查询到数据的日期}

是否需要查询{最新可查询到数据的日期}的数据?
```

### 示例对话

```
用户:查询今天的内容出海日报
Agent:⚠️2026-06-16数据尚未更新
      数据更新规则:每日15:00更新前一天的数据
      当前可查询的最新日期:2026-06-14

      是否需要查询2026-06-14的数据?
用户:好的
Agent:(执行 python3 daily_report.py --latest)
```

## 📊 第一步:爆款日报生成

### 默认查询策略

```bash
# 生成最新一期日报(用户确认后,自动跳过无数据日期)
python3 assets/daily_report.py --latest

# 生成指定日期日报(历史日期已有数据,无需确认)
python3 assets/daily_report.py --date 2026-06-10

# 按关键词查询
python3 assets/daily_report.py --keyword "品牌出海" --latest

# 查询指定平台(逗号分隔:0=公众号,1=抖音,2=视频号,3=小红书,4=快手,6=B站)
python3 assets/daily_report.py --platforms "3,1" --latest

# 订阅 / 取消订阅
python3 assets/daily_report.py --subscribe
python3 assets/daily_report.py --unsubscribe
```

### 智能扩展逻辑

1. 默认查询全平台(公众号/抖音/视频号/小红书/快手/B站),每个平台Top50
2. 可通过 `--platforms` 参数指定平台
3. 可通过 `--keyword` 关键词搜索
4. **题材聚类基于API返回的`topic`字段自动完成**,无需预定义关键词,题材分类完全由数据内容决定

### API调用参数

**接口**:`POST https://redfox.hk/story/api/parseWork/queryContentExportTop`

**请求头**:
| 参数名 | 类型 | 说明 |
|--------|------|------|
| `X-API-KEY` | String | API Key |
| `Content-Type` | String | `application/json` |

**请求体**:
```json
{
  "source": "全网内容出海信息源-GitHub",
  "platforms": [0, 1, 2, 3, 4, 6],
  "startTime": "2026-06-15 00:00:00",
  "endTime": "2026-06-15 23:59:59",
  "keyword": "品牌出海"
}
```

**请求参数说明**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `source` | String | 是 | 调用来源标识，固定值 `"全网内容出海信息源-GitHub"` |
| `platforms` | List\<Integer\> | 是 | 平台列表(0=公众号,1=抖音,2=视频号,3=小红书,4=快手,6=B站) |
| `keyword` | String | 否 | 搜索关键词(模糊匹配标题或用户名称) |
| `startTime` | String | 否 | 开始时间 yyyy-MM-dd HH:mm:ss |
| `endTime` | String | 否 | 结束时间 yyyy-MM-dd HH:mm:ss |

**成功响应码**:`2000`

**响应结构**:
```json
{
  "code": 2000,
  "msg": "成功",
  "data": {
    "platformGroups": [
      {
        "platform": 0,
        "platformName": "公众号",
        "list": [ ... ]
      }
    ]
  }
}
```

> **注意**: 公众号按阅读数(readCount)倒序,其余平台按点赞数(likeCount)倒序,每个平台返回前50条。`platforms` 为必填,至少传入一个平台。

### 全平台字段映射

| 字段 | 说明 | 示例 |
|------|------|------|
| photoId | 作品唯一标识 | `"gzh_20260620001"` |
| authorId | 作者ID | `"rmrbwx"` |
| msgType | 内容类型 | `"内容出海"` |
| coverUrl | 封面图 | `"https://oss.example.com/cover.jpg"` |
| userName | 作者昵称 | `"出海观察君"` |
| userHeadUrl | 作者头像URL | `"https://oss.example.com/avatar.jpg"` |
| title | 标题 | `"中国品牌出海:从制造到智造"` |
| platform | 平台标识 | `0`(公众号)/`1`(抖音)/`3`(小红书)等 |
| url | 作品链接 | `"https://mp.weixin.qq.com/s/xxx"` |
| likeCount | 点赞数 | `8000` |
| commentCount | 评论数 | `1200` |
| shareCount | 分享/转发数 | `3500` |
| readCount | 阅读数 | `150000` |
| type | 分类 | `"品牌出海"` |
| topic | 话题 | `"出海动态"` |
| gmtCreate | 发布时间 | `"2026-06-20 10:30:00"` |
| gmtModified | 修改时间 | `"2026-06-21 08:20:00"` |

**链接处理规则**:直接使用API返回的`url`字段;小红书`url`为空时,fallback拼接`https://www.xiaohongshu.com/explore/{photoId}`。

**字段使用逻辑**:
- **去重**:基于 `photoId`
- **排序**:基于 `likeCount`(降序),公众号API端已按readCount预排序
- **数据为0时**:HTML日报中该指标不展示

## 📈 第二步:深度分析(漏斗结构,零重复)

日报生成后,**必须**基于数据自动执行深度分析,按漏斗结构逐层深入,每层都有新信息:

### 分析维度

1. **数据全景**:6平台核心指标一张表(作品/总互动/均互动/头部天花板/第一题材/分享率特征),不加分析
2. **跨平台差异洞察**:题材矩阵 + 核心数据洞察
3. **趋势判断**:每条带可验证条件和行动建议

## 🎨 HTML日报格式规范

### 主题配色

- **背景色**:`#f5f5f5`(浅灰)
- **卡片背景**:`#fff`(白色,带阴影)
- **主色调**:`#FF2442`
- **文字色**:`#333`(深色)
- **平台标签色**:公众号`#07C160` / 抖音`#1A1A1A` / 视频号`#FA9D3B` / 小红书`#FF2442` / 快手`#FF4906` / B站`#00A1D6`

### 布局结构

```
Header(标题🌏+日期)
  ↓
Overview(总作品/平台数/题材数/总互动/均互动)
  ↓
Compare Table(平台对比表:平台/作品数/总点赞/均点赞/热门题材/Top作品)
  ↓
Platform Sections(各平台详细板块)
  - 平台Header(名称+统计)
  - 题材标签云
  - Top8热门作品列表
  ↓
Footer(生成时间+数据说明)
```

### 平台板块内容

每个平台板块包含:
- 平台名称+图标+彩色标签
- 统计摘要(作品数/总互动/均互动/最高互动)
- 题材标签云(最多8个,含数量和占比)
- Top8作品(封面+题材标签+标题+作者+互动数据)
- **互动数据为0的字段不展示**

## 📝 终端输出格式(强制执行)

> ⛔ **严格执行规则**:
> - 输出**必须包含全部3个版块**:一、数据全景 + 二、跨平台差异洞察 + 三、趋势判断及验证
> - 以下模板是**唯一合法输出格式**,禁止任何自由发挥、省略、简化或重新组织
> - 禁止输出模板中未定义的额外内容(如"我来帮你…""以下是…"等口语化文字)
> - **每次获取日报后,对话回复必须严格按此模板输出 md 内容,不得包含模板以外的任何文字**

每次运行日报后,对话输出**必须严格**按以下模板原样输出(仅替换 `{...}` 占位符):

```
## 全网内容出海信息源 · {日期} 日报

**扫描 {N} 部作品 · {P} 个平台 · {T} 个题材**

---

### 一、📊 数据全景

| 平台 | 作品 | 总点赞 | 均点赞 | 头部天花板 | 第一题材 | 分享率特征 |
|------|------|--------|--------|------------|----------|------------|
| {平台名} | {N} | {X}w | {X} | {X}w | #{题材} {X}% | {分享特征描述} |
| ... | ... | ... | ... | ... | ... | ... |

**一句话读懂格局**:{基于数据的核心格局判断}

---

### 二、🔍 跨平台差异洞察

**题材矩阵**:

| 题材 | 抖音 | 快手 | 小红书 | 视频号 | 公众号 | B站 | 总 | 特征 |
|------|------|------|--------|--------|--------|-----|-----|------|
| #{题材} | {N} | {N} | {N} | {N} | {N} | {N} | {N} | {一句话特征} |

**{N}条核心数据洞察**:

**洞察1**: {数据驱动的洞察,带数据支撑}
**洞察2**: {数据驱动的洞察,带数据支撑}
**洞察3**: {数据驱动的洞察,带数据支撑}

---

### 三、🔮 趋势判断及验证

| # | 判断 | 依据 | 验证条件 | 行动建议 |
|---|------|------|----------|----------|
| 1 | {趋势判断} | {数据依据} | {可验证条件} | {具体行动} |
| 2 | {趋势判断} | {数据依据} | {可验证条件} | {具体行动} |
| 3 | {趋势判断} | {数据依据} | {可验证条件} | {具体行动} |

---

**日报地址**:{HTML文件绝对路径}

> 数据说明:每日15:00更新昨天的数据
```

> 以上格式为**强制规范**。3个版块必须全部包含,不得省略任何版块。

## 💾 缓存机制

### 缓存路径

```
~/.workbuddy/cache/content_export_top_data.json
```

### 缓存策略

- **有效期**:1小时(3600秒)
- **去重字段**:`photoId`
- **排序字段**:`likeCount`(降序)

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keyword` | 搜索关键词(模糊匹配标题或用户名称) | — |
| `--platforms` | 平台列表,逗号分隔(0=公众号,1=抖音,2=视频号,3=小红书,4=快手,6=B站) | 全平台 |
| `--date` | 指定日期 YYYY-MM-DD(若无数据会提示并询问切换) | 今天 |
| `--start-time` | 自定义开始时间 YYYY-MM-DD HH:MM:SS(覆盖 --date 推算) | — |
| `--end-time` | 自定义结束时间 YYYY-MM-DD HH:MM:SS(覆盖 --date 推算) | — |
| `--latest` | 自动使用最新有数据的日期,跳过无数据区间 | — |
| `--output-dir` | 输出目录 | `~/Downloads/QoderReports` |
| `--api-key` | 指定 API Key | — |
| `--subscribe` | 开启每日订阅 | — |
| `--unsubscribe` | 关闭每日订阅 | — |
| `--from-cache` | 使用缓存数据 | — |

## 💬 自定义查询场景

除默认全平台日报外,用户可按关键词或平台进行定向查询:

```bash
# 按关键词查询
python3 "$SKILL_PATH/assets/daily_report.py" --keyword "品牌出海" --latest

# 查询指定平台
python3 "$SKILL_PATH/assets/daily_report.py" --platforms "3,1" --latest

# 关键词+平台组合
python3 "$SKILL_PATH/assets/daily_report.py" --keyword "AI" --platforms "0,3" --latest
```

**自定义查询逻辑**:
- 所有符合条件的数据一次性查询,无需逐个调用
- 查询结果自动去重,题材聚类、趋势分析均基于查询结果生成

## 🔒 安全约束

1. **API Key**从环境变量`REDFOX_API_KEY`获取
2. **禁止硬编码**密钥
3. **数据来源唯一性**:仅使用红狐API

## 📋 平台适配说明

### 平台编号对照表

| 编号 | 平台 | 排序规则 | 标签颜色 |
|------|------|----------|----------|
| 0 | 公众号 | readCount(阅读数)倒序 | `#07C160`(绿) |
| 1 | 抖音 | likeCount(点赞数)倒序 | `#1A1A1A`(黑) |
| 2 | 视频号 | likeCount(点赞数)倒序 | `#FA9D3B`(橙) |
| 3 | 小红书 | likeCount(点赞数)倒序 | `#FF2442`(红) |
| 4 | 快手 | likeCount(点赞数)倒序 | `#FF4906`(橙) |
| 6 | B站 | likeCount(点赞数)倒序 | `#00A1D6`(蓝) |

### 作品链接适配

```python
# 直接使用API返回的url字段
url = item.get("url") or ""

# 小红书url为空时fallback
if not url and platform == 3 and photo_id:
    url = f"https://www.xiaohongshu.com/explore/{photo_id}"
```

### 核心配置

| 维度 | 值 |
|------|------|
| API端点 | `https://redfox.hk/story/api/parseWork/queryContentExportTop` |
| 成功响应码 | `2000` |
| 请求参数 | `platforms`(列表)+`keyword`+`startTime`+`endTime` |
| 响应结构 | `data.platformGroups[].list[]` |
| 主色调 | `#FF2442` |
| 图标 | 🌏 |
| 缓存文件 | `content_export_top_data.json` |
| HTML文件名 | `内容出海日报_YYYY-MM-DD.html` |
| 脚本文件名 | `playlet_xhs_daily.py` |

## ✅ 验证清单

- [x] API接口地址正确(`queryContentExportTop`)
- [x] 支持全平台(0=公众号,1=抖音,2=视频号,3=小红书,4=快手,6=B站)
- [x] 请求参数使用 `platforms` 列表
- [x] 成功响应码为 `2000`
- [x] 响应结构为 `data.platformGroups[].list[]`
- [x] 字段映射确认(photoId、likeCount等)
- [x] 去重逻辑使用photoId
- [x] 排序逻辑使用likeCount(降序)
- [x] 链接直接使用API返回的url字段,小红书fallback
- [x] HTML主题色 `#FF2442`
- [x] 平台彩色标签
- [x] 图标 🌏
- [x] 文件命名统一
- [x] 数字格式化逻辑(万→w)
- [x] 互动数据为0时隐藏该字段
- [x] 封面图HEIF→JPG格式兼容转换
- [x] SKILL.md文档更新
- [x] 参考文档同步更新
- [x] 输出必须包含全部3个版块
- [x] 题材聚类基于topic字段自动完成
- [x] get()方法使用 `or 0` 处理None值
