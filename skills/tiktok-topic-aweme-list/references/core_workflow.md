# Core Workflow

> 本文件为 tiktok-topic-aweme-list 技能的完整执行逻辑参考。SKILL.md 仅保留用户可见的功能描述，Agent 执行时必须遵循本文件中的所有规则。

---

## Step 0：鉴权配置（前置步骤）

> 用户使用本技能前需完成数据服务接入凭证配置。Agent 在首次交互时应主动检查并引导配置。

- 本技能依赖环境变量 `REDFOX_API_KEY`；未设置时脚本会尝试从 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 等 shell 配置文件中读取
- API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）
- 未获取到 Key 时脚本报错并以非零状态码退出，同时输出 API Key 获取提醒

---

## Step 1：数据来源与接口

- 唯一数据源：红狐 API `POST https://redfox.hk/story/api/tiktok/ability/topicAwemeList`
- 认证方式：请求头 `X-API-KEY`（即环境变量 `REDFOX_API_KEY`）
- 来源标识：请求体携带 `source` 字段，值为「获取TikTok指定话题作品数据-GitHub」
- 成功码：`code=2000`
- 必填参数：

```json
{
  "ch_id": 2525872,
  "cursor": 0,
  "count": 10,
  "source": "获取TikTok指定话题作品数据-GitHub"
}
```

字段说明：

- `ch_id`：TikTok 话题 ID / challengeId / hashtagId，必须为大于 0 的数字
- `cursor`：分页游标，首页传 `0`
- `count`：单页条数
- 响应 `data.nextCursor` 可作为下一页 `cursor`
- 响应 `data.hasMore=1` 表示还有下一页

传输说明：redfox.hk 接口在本地环境可能需要无 SNI 的 socket + SSL 连接；脚本已内置该传输方式（保留证书链校验，仅关闭主机名检查），Agent 无需额外处理。

---

## Step 2：理解用户意图

| 用户意图 | 执行动作 |
|---|---|
| 查询话题作品（给出话题 ID） | 运行脚本并传入 `--ch-id`；可附 `--topic` 话题名用于表格展示 |
| 只给出 TikTok 作品链接 | 先从作品页提取话题 ID 再查询；若作品没有 `challenges` / `textExtra` 话题，直接说明"暂无话题 ID"，不要改查其他话题 |
| 用户以接口名 / `ch_id` 指代 | 按话题作品查询处理（等价于"查询 TikTok 话题作品数据"） |
| 指定排序 | 加 `--sort likes` / `comments` / `shares` / `none`（默认 `views`，按播放数降序） |
| 翻页 | 使用上一页响应的 `data.nextCursor` 作为 `--cursor` 再查一次 |
| 查看原始返回 | 加 `--raw` 输出接口原始 JSON |

用户要求排序时，优先建议按作品指标排序：播放、点赞、评论、分享。

---

## Step 3：调用脚本

```bash
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --count 10
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --cursor 10 --count 10
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --sort likes
python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --api-key ak_xxxxxxxx
```

参数校验（脚本内置）：

- `--ch-id` 必须大于 0；`--cursor` 不能小于 0；`--count` 必须大于 0
- `--sort` 可选值：`views`（默认，播放数降序）、`likes`、`comments`、`shares`、`none`（接口原始顺序）

---

## Step 4：渲染输出

输出顺序固定：先输出话题与分页信息、API Key 获取提醒，再输出作品表格。

信息行格式：

```text
话题：`<topic>` | ch_id：`<ch_id>` | cursor：<cursor> | count：<本页条数> | hasMore：<hasMore> | nextCursor：<nextCursor>
```

表格表头固定为：

| # | 作者 | 作品 ID | 播放 | 点赞 | 评论 | 分享 | 作品链接 | 内容摘要 | 话题 |
|---:|---|---|---:|---:|---:|---:|---|---|---|

渲染规则：

- 话题名自动加 `#` 前缀；未提供话题名时显示 `ch_id:<id>`
- "作品链接"必须使用接口返回的完整 `workList[].shareLink`，格式为 `[打开作品](完整shareLink)`
- 不要自行用 `userHandle + workId` 拼接链接，除非 `shareLink` 为空且用户明确要求兜底
- 默认不输出 `fansCount`、`followCount`、`workCount`、`likedTotal`；这些作者级字段在该接口实测常为 `0`，不适合排序或判断账号规模
- 列表默认按作品播放数（`statsData.viewCount`）降序排序；如用户指定排序，可通过 `--sort` 改为点赞、评论、分享或接口原始顺序
- 返回空 `workList` 时输出"暂无数据"

---

## Step 5：错误处理

- `code=3105`：API Key 已禁用，提示用户更换有效 Key，并输出获取 API Key 提醒，不要重复重试
- `code=3203`：参数校验失败，按 `msg` 中提示修正参数；该错误通常提示"积分未扣除"
- 其他非 `2000` 返回：输出 `接口返回异常：code=<code>, msg=<msg>`
- 返回空 `workList`：输出"暂无数据"，不要主动改查其他话题
- TikTok 页面无法直接抓取时，可通过浏览器页面内嵌 JSON 中的 `textExtra` / `challenges` 提取话题 ID
- 脚本异常：错误信息输出到 stderr 并以 exit 1 退出；与 Key 相关时同时输出 API Key 获取提醒

---

## Step 6：注意事项

1. **积分保护**：每次成功查询可能消耗积分；未经用户明确指定，不要主动翻页或批量查询多个话题
2. **链接完整性**：输出中的链接必须保持完整，不要使用被终端截断的 URL
3. **无结果不替换**：空结果 / 暂无话题 ID 时如实说明，不自动改查其他话题
4. **鉴权提示**：依赖环境变量 `REDFOX_API_KEY`（三级读取），API Key 获取：https://redfox.hk/settings/api-keys?source=github

---

## Step 7：版本信息

- **版本号**：v1.0.0
- **核心功能**：按话题 ID 查询 TikTok 作品列表，默认按播放数降序输出播放/点赞/评论/分享数据与完整作品链接，支持排序切换与游标翻页
- **数据来源**：红狐 API `/story/api/tiktok/ability/topicAwemeList`
