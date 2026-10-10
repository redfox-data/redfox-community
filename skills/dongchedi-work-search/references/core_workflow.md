# 懂车帝作品关键词搜索核心流程

## 使用边界

- 每次 API 查询都可能消耗积分；只执行用户明确要求的关键词、页码和内容类型。
- 搜索无结果时只输出“暂无数据”及可能原因，不主动替换关键词查询其他内容。
- 不主动翻页；只有用户要求“下一页/查看更多”时，才将 `offset` 增加 `20` 再查。
- 链接必须输出完整 URL。`workUrl` 若以 `//` 开头，展示前补为 `https://`。

## 关键词搜索作品

脚本：`scripts/search_work.py`

默认调用：

```bash
python scripts/search_work.py --keyword 智界
```

常用参数：

```bash
python scripts/search_work.py --keyword 智界 --source-type 1 --offset 0
python scripts/search_work.py --keyword 智界 --source-type 2 --offset 20
python scripts/search_work.py --keyword 智界 --sort plays --top 10
python scripts/search_work.py --keyword 智界 --api-key ak_xxxxxxxx
python scripts/search_work.py --keyword 智界 --raw
```

参数规则：

| 参数 | 说明 |
|---|---|
| `--keyword` | 必填，搜索关键词 |
| `--source-type` | `1`=综合，`2`=视频；默认 `1` |
| `--offset` | 首页为 `0`，下一页为当前 offset + `20` |
| `--sort` | `plays`、`likes`、`comments`、`time`、`none` |
| `--top` | 仅展示前 N 条（本地限制，不改变接口返回）；`0` 表示展示接口返回全部 |
| `--raw` | 输出接口原始 JSON |
| `--api-key` | 临时传入 API Key；优先级高于环境变量 |

API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件（`.zshrc`、`.bashrc`、`.bash_profile`、`.profile`）。

鉴权与来源标识：

- 请求头 `REDFOX_API_KEY: <REDFOX_API_KEY>`；成功码兼容 `200` 与 `2000`。
- 来源标识：请求体携带 `source` 字段，值为「懂车帝作品关键词搜索-GitHub」。
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）。

输出结构：默认先输出关键词、内容类型、offset、条数和 API Key 获取提醒，再输出固定表格：

| # | 标题 | 作者 | 作品ID | 播放 | 点赞 | 评论 | 发布时间 | 作品链接 |
|---:|---|---|---|---:|---:|---:|---|---|

输出规则：

- 表格仅使用 `searchWork` 返回字段：`title`、`authorName`、`authorId`、`workId`、`playCount`、`likeCount`、`commentCount`、`publishTime`、`workUrl`。
- `workUrl` 必须补全为完整可点击链接。
- `publishTime` 为秒级时间戳，脚本转换为本地时间展示；转换失败时原样展示。
- 如用户要求分析，只基于搜索结果字段做轻量趋势判断，不补造正文、封面或详情字段。

## 错误处理

- 缺少 `REDFOX_API_KEY`：提示设置环境变量或使用 `--api-key` 临时传入，禁止硬编码密钥。
- `code=3105`：API Key 已禁用，提示用户更换有效 Key，不要重复重试。
- `code=3203`：参数校验失败，展示接口 `msg`，让用户修正参数。
- 空 `workList`：输出“暂无数据”。
- HTTP 或网络错误：展示错误摘要，不输出 API Key。
