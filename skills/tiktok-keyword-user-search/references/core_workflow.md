# TikTok关键词搜用户核心流程

> 本 Skill 包含两个能力：关注列表查询（userFollowing）与关键词搜索用户（searchUser），支持"搜索定位用户 → 查其关注列表"链式查询。

## 使用边界

- 每次 API 查询都可能消耗积分；只执行用户明确指定的用户ID、关键词与页码，不主动批量查询多个用户或关键词。
- `userId` 与 `secUserId` 必须二选一传入；两者都未提供或都提供时，脚本会直接报错，请引导用户明确其一。
- 关注列表接口不接受 @handle / 昵称查询。用户只给 handle 时，先用「关键词搜索用户」定位 userId（见下文链式查询），不猜测ID。
- 返回空 `followingList` 时只输出"暂无数据"及可能原因（关注数为 0、ID 有误、账号私密等），不主动改查其他用户。
- 不主动翻页；只有用户要求"下一页/查看更多"时，才携带上次返回的 `minTime` / `pageToken`（关注列表）或 `cursor`（用户搜索）续查。
- 链式查询（搜索→关注列表）涉及两次独立调用：搜索结果先向用户确认目标账号（handle 相同或相似的账号可能多个），确认后再查关注列表，不自动连查。

## 输出模板

Agent 最终回复按本模板包装呈现（脚本负责数据部分，本节负责呈现规范）：

**首次使用功能介绍**：会话内第一次触发本 Skill，或用户表示刚安装/第一次使用时，必须先输出功能介绍（可直接复用）：

> 📋 **功能介绍**：本技能支持两个能力——
> ① **关键词搜索用户**：给我昵称或 handle，搜出 TikTok 账号及其 userId；
> ② **关注列表查询**：给我 userId，查这个账号关注了谁；
> 也可以直接说「查 xxx 的关注列表」，我会先搜索定位再向你确认。
> 例：「搜一下 AI 相关的用户」「查 293977214893735936 的关注列表」

**每次查询回复结构**：

1. 查询说明行：本次查询目标与口径（关键词 / userId、页码、排序、筛选）。
2. 数据表格：脚本输出的固定表头整表照搬，禁止为可读性精简列数；仅含接口返回字段。
3. 结尾下一步引导（每轮必带，按场景选用，可直接复用）：
   - 关注列表 `hasMore=1`：`⚡ 回复「下一页」继续查看更早的关注（消耗 1 次调用）`
   - 用户搜索 `hasMore=1`：`⚡ 回复「下一页」查看更多结果；把目标账号的 userId 发给我，可直接查 TA 的关注列表（消耗 1 次调用）`
   - 链式搜索完成待确认：`⚡ 确认要查哪个账号的关注列表？回复序号或 userId 即可`
   - 查询无结果：`⚡ 可以换一个关键词或 userId 再试，直接发给我即可`
4. API Key 获取提醒（脚本输出已含，保留原位即可）。

同会话后续查询可省略首次功能介绍，但结尾引导不可省略。

## 关键词搜索用户（searchUser）

脚本：`scripts/search_user.py`

默认调用：

```bash
python scripts/search_user.py --keyword 南浔
```

常用参数：

```bash
python scripts/search_user.py --keyword 南浔 --count 20
python scripts/search_user.py --keyword 手冲咖啡 --fans 3 --verified
python scripts/search_user.py --keyword 南浔 --offset 20
python scripts/search_user.py --keyword 南浔 --sort none
python scripts/search_user.py --keyword 南浔 --api-key ak_xxxxxxxx
python scripts/search_user.py --keyword 南浔 --raw
```

参数规则：

| 参数 | 说明 |
|---|---|
| `--keyword` | 必填，搜索关键词（昵称 / handle） |
| `--offset` | 偏移量，首页为 `0`，翻页传上次返回的 `cursor` |
| `--count` | 单页条数，默认 10，范围 1~50 |
| `--fans` | 粉丝数筛选：`1`-0~1K / `2`-1K~10K / `3`-10K~100K / `4`-100K以上 |
| `--verified` | 仅看认证用户 |
| `--name-relevance` | 按用户名相关性（接口偏好参数，默认不启用） |
| `--sort` | `fans`（默认，粉丝数降序）/ `none`（接口原始相关度顺序） |
| `--top` | 仅展示前 N 条（本地限制）；`0` 表示展示全部 |
| `--raw` | 输出接口原始 JSON |
| `--api-key` | 临时传入 API Key；优先级高于环境变量 |

鉴权与传输：与关注列表接口一致，请求头 `REDFOX_API_KEY: <REDFOX_API_KEY>`，成功码兼容 `2000` 与 `200`，传输层同为无 SNI socket 写法。

输出结构：先输出关键词、offset、条数、hasMore/cursor 与 API Key 获取提醒，再输出固定表格：

| # | 昵称 | Handle | userId | 粉丝 | 关注 | 获赞 | 作品 |
|---:|---|---|---|---:|---:|---:|---:|

输出规则：

- 表格仅使用 `userList` 返回字段：`userName`、`userHandle`、`userId`、`fansCount`、`followCount`、`likedTotal`、`workCount`。
- **userId 列固定输出**（供链式查询关注列表直接使用）；`followCount` 为该用户关注数，接口实测返回，如实展示。
- 接口未返回主页地址字段，不构造输出主页链接；该接口无认证信息字段，不输出认证列。
- 默认按粉丝数降序输出；`--sort none` 保留接口原始相关度顺序（同名/相似账号场景下更贴近搜索意图，可提示用户切换）。
- 空 `userList`：输出"暂无数据"，不改查其他关键词。
- `hasMore=1` 时输出下一页命令提示（含 `--offset <cursor>`）。

## 链式查询：搜索定位 → 查关注列表

用户只提供昵称 / handle 想查关注列表时，按以下顺序执行：

1. 用 `search_user.py --keyword <昵称或handle>` 搜索（handle 优先用完整 handle 作为关键词，精确度最高）。
2. 将搜索结果（含 userId、粉丝数）展示给用户，若精确匹配唯一可直接确认；多个相似账号时请用户选择。
3. 用户确认后，用 `fetch_user_following.py --user-id <userId>` 查询关注列表。

边界：searchUser 响应包含 `userId` 与 `secUserId`，链路字段完整可用；反向路径（直接按 handle 查关注列表）不存在，不要尝试。

## 脚本调用

脚本：`scripts/fetch_user_following.py`

默认调用（首页）：

```bash
python scripts/fetch_user_following.py --user-id 6748953635118187521
```

常用参数：

```bash
python scripts/fetch_user_following.py --sec-user-id MS4wLjABAAAA...
python scripts/fetch_user_following.py --user-id 6748953635118187521 --sort fans --top 20
python scripts/fetch_user_following.py --user-id 6748953635118187521 --min-time 1760525119 --page-token xxx
python scripts/fetch_user_following.py --user-id 6748953635118187521 --api-key ak_xxxxxxxx
python scripts/fetch_user_following.py --user-id 6748953635118187521 --raw
```

参数规则：

| 参数 | 说明 |
|---|---|
| `--user-id` | 纯数字用户ID，与 `--sec-user-id` 二选一（互斥必选） |
| `--sec-user-id` | 字母数字混合ID（`MS4wLjAB` 开头），与 `--user-id` 二选一 |
| `--min-time` | 翻页游标，首页为 `0`，翻页传上次返回的 `minTime` |
| `--page-token` | 翻页token，首页留空，翻页传上次返回的 `pageToken`；为 null 时省略 |
| `--sort` | `none`（默认，接口原始顺序=关注时间倒序）、`fans`、`works`、`likes` |
| `--top` | 仅展示前 N 条（本地限制，不改变接口返回）；`0` 表示展示全部 |
| `--raw` | 输出接口原始 JSON |
| `--api-key` | 临时传入 API Key；优先级高于环境变量 |

API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件（`.zshrc`、`.bashrc`、`.bash_profile`、`.profile`）。

鉴权与传输：

- 请求头 `REDFOX_API_KEY: <REDFOX_API_KEY>`（注意：本接口头名不是 `X-API-KEY`）；成功码兼容 `2000` 与 `200`。
- redfox.hk 本地链路实测要求无 SNI 的 socket + SSL 连接，脚本已内置该传输方式（详见 `api-spec.md` 传输层说明）。
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）。

## 输出结构

默认先输出目标用户、minTime、条数、hasMore 与 API Key 获取提醒，再输出固定表格：

| # | 昵称 | Handle | 粉丝 | 作品 | 获赞 | 地区 | 认证 |
|---:|---|---|---:|---:|---:|---|---|

输出规则：

- 表格仅使用 `followingList` 返回字段：`userName`、`userHandle`、`fansCount`、`workCount`、`likedTotal`、`region`、`customVerify`、`enterpriseVerifyReason`、`isSecret`。
- 接口未返回主页地址字段，不构造输出主页链接。
- `isSecret=1` 的关注对象在昵称后追加"（私密）"。
- "认证"列优先展示 `customVerify`，为空时展示 `enterpriseVerifyReason`（加 `[企业]` 前缀），均为空显示 `-`。
- `signature`、`createTime`（注册时间）、`followCount`、`favoritingCount`、`avatarImage` 不进主表；用户要求深度分析时用 `--raw` 读取或按需补充输出，不编造。
- `hasMore=1` 时脚本会输出下一页命令提示（含 `--min-time`，必要时含 `--page-token`），翻页时原样透传给脚本。
- 如用户要求分析关注画像，只基于返回字段做轻量判断（如大号占比、地区分布），不补造数据。

## 错误处理

- 缺少 `REDFOX_API_KEY`：提示设置环境变量或使用 `--api-key` 临时传入，禁止硬编码密钥。
- `code=3105`：API Key 已禁用，提示用户更换有效 Key，不要重复重试。
- `code=3203`：参数校验失败，展示接口 `msg`（通常标注"积分未扣除"），让用户修正参数。
- 空 `followingList`：输出"暂无数据"及可能原因，不改查其他用户。
- 空 `userList`：输出"暂无数据"，不改查其他关键词。
- HTTP 或网络错误（含读超时）：展示错误摘要，不输出 API Key，不自动重试；确认参数无误后由用户决定是否重查。
