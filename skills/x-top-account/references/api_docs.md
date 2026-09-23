# X 热门账号榜 API 接口文档

## 接口基础信息

| 字段 | 值 |
|------|-----|
| 接口地址 | `https://redfox.hk/story/api/x/hotAccount/rankList` |
| 请求方式 | POST |
| Content-Type | `application/json` |
| 认证方式 | `X-API-KEY`（从环境变量 `REDFOX_API_KEY` 获取，格式 `ak_xxxxxxxx`） |

---

## 请求参数

```json
{
  "pageNum": 1,                  // 页码，从 1 开始（每页固定 20 条）
  "rankDate": "2026-09-20",     // 榜单日期 YYYY-MM-DD
  "gender": "all",              // 性别：all / male / female
  "category": "all",            // 行业分类：all 或行业中文名（如 "萌宠动物"）
  "source": "X账号榜-GitHub"     // 固定来源标识，每次请求必传
}
```

> ⚠️ **重要**：`category` 传**行业中文名**（如用户问宠物 → 传 `"萌宠动物"`），全部行业传 `"all"`；skill 内部不暴露英文分类值。

---

## 响应结构

```json
{
  "code": 2000,
  "msg": null,
  "data": {
    "pageNum": 1,
    "pageSize": 20,
    "pages": 10,
    "total": 200,
    "list": [
      {
        "rankNo": 1,
        "fullName": "Donald J. Trump",
        "profileUrl": "https://www.twitter.com/realdonaldtrump/",
        "pictureUrl": "https://favikon-medias.s3.../25073877.jpg",
        "title": "Former U.S. President and Political Leader",
        "biography": "Donald J. Trump is the 45th and 47th President...",
        "countryCode": "us",
        "countryName": "United States",
        "gender": "male",
        "xScore": 98.6,
        "growthPercentage": "+0.11 %",
        "growthAbsolute": "+186.1K",
        "xFollowerCount": 111800000,
        "statDate": "2026-09-20",
        "typologie": null,
        "categoriesJson": "[{\"root_name\":\"⚖️ Law, Medias & Politics\",\"name\":\"Politicians\",\"primary\":true,...}]",
        "networksJson": "{\"youtube\":{\"follower_count\":\"4M\",\"profile_url\":\"...\"},\"twitter\":{...},\"tiktok\":{...}}",
        "badgesJson": "{\"hasTopics\":\"US Elections 2024, Trump Government\",\"hasCause\":\"Conservatives,...\",\"verifiedCreator\":false,...}"
      }
    ]
  }
}
```

---

## 错误码

| code | 含义 |
|------|------|
| 2000 | **成功**（注意：成功码是 2000 不是 0！） |
| 其他 | 错误；目标日期/筛选无数据时 `data.list` 为空数组、`total=0` |

---

## 字段映射（fetch_rank.py normalized JSON）

| 接口原始字段 | normalized 字段 | 含义 |
|------------|----------------|------|
| `rankNo` | `rank` | 排名 |
| `fullName` | `fullName` | 账号名 |
| `profileUrl` | `profileUrl` | X 主页链接 |
| `pictureUrl` | `pictureUrl` | 头像 |
| `title` | `title` | 头街（一句话介绍） |
| `biography` | `biography` | 账号简介 |
| `countryName` / `countryCode` | `country` / `countryCode` | 国家/地区 |
| `categoriesJson`（primary=true 的 root_name，去 emoji） | `industries` | 主行业 |
| `xScore` | `score` | 影响力评分（满分 100） |
| `growthPercentage` | `growthPercentage` | 日涨幅（去空格，如 `+0.11%`） |
| `growthAbsolute` | `growthAbsolute` | 日涨粉绝对值 |
| `xFollowerCount` | `xFollowers` / `xFollowersFmt` | X 粉丝数（原始值 / 格式化） |
| `networksJson`（除 twitter 外） | `otherNetworks` | 其他平台粉丝数列表 |
| `badgesJson.hasTopics` / `hasCause` | `topics` / `cause` | 专题标签 / 公益标签 |

**JSON 字符串字段**：`categoriesJson`、`networksJson`、`badgesJson` 均为 JSON 字符串，需二次 `json.loads` 解析；解析失败时按空值容错处理。

**头像时效**：`pictureUrl` 为 S3 签名 URL（有效期约 15 分钟），HTML 报告内置 `onerror` 容错，头像失效时自动隐藏、不影响排版。

---

## 更新规则与日期计算

| 规则 | 值 |
|------|-----|
| 更新时间 | 每日早上 9:00 更新前一天榜单 |
| 最新可用日期 | 当前时间 ≥ 9:00 → 昨日；< 9:00 → 前日 |
| 回溯范围 | 过去 7 天 |
| 空数据回退 | 目标日期 `total=0` 时，自最新可用日期向前逐日扫描（最多 7 天） |

---

## 分页规则

| 字段 | 值 |
|------|-----|
| pageSize | 固定 20 |
| pages | 10（全量 200 条） |
| 翻页方式 | 请求参数 `pageNum` 递增；对话中逐页展示并询问是否继续 |
