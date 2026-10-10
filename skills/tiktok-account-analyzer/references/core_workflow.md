# Core Workflow

> 本文件为 tiktok-account-analyzer 技能的完整执行逻辑参考。SKILL.md 仅保留用户可见的功能描述，Agent 执行时必须遵循本文件中的所有规则。

---

## Step 0：鉴权配置（前置步骤）

> 用户使用本技能前需完成数据服务接入凭证配置。Agent 在首次交互时应主动检查并引导配置。

- 本技能依赖环境变量 `REDFOX_API_KEY`；未设置时脚本会尝试从 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 等 shell 配置文件中读取
- API Key 读取顺序：`--api-key` 参数 > `REDFOX_API_KEY` 环境变量 > shell 配置文件
- API Key 获取：访问 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册账号并获取（格式 `ak_xxxxxxxx`）
- 未获取到 Key 时脚本报错并以非零状态码退出，同时输出 API Key 获取提醒

---

## Step 1：数据来源与接口

本技能共对接 3 个数据接口，按分析需求组合调用：

| 接口 | 用途 | 路径 |
|---|---|---|
| 关键词用户搜索 | 按昵称 / 关键词定位账号 | `POST https://redfox.hk/story/api/tiktok/ability/searchUser` |
| 用户主页作品 | 获取账号主页作品列表 | `POST https://redfox.hk/story/api/tiktok/ability/userAwemeList` |
| 用户喜欢作品 | 获取账号喜欢（点赞）的作品 | `POST https://redfox.hk/story/api/tiktok/ability/userFavoriteAwemeList` |

通用规则：

- 认证方式：请求头 `X-API-KEY`（即环境变量 `REDFOX_API_KEY`）
- 来源标识：每个接口的请求体均携带 `source` 字段，值为 `TikTok账号深度分析-GitHub`
- 成功码：`code=2000`
- 传输说明：redfox.hk 接口在本地环境可能需要无 SNI 的 socket + SSL 连接；脚本已内置该传输方式（保留证书链校验，仅关闭主机名检查），Agent 无需额外处理

### 1.1 关键词用户搜索（searchUser）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| keyword | String | 是 | 搜索关键词（昵称 / handle） |
| offset | String | 是 | 偏移量，首次传 `"0"`，翻页传上一次响应中的 cursor |
| count | String | 是 | 单页条数（脚本默认 `"20"`） |

响应说明：

- `data.cursor`：下一页游标；`data.hasMore`：1-还有下一页，0-没有
- `data.userList`：用户列表，字段包括 `userName`、`userHandle`、`fansCount`、`followCount`、`likedTotal`、`workCount`、`avatarImage`、`secUserId`、`userId`（未返回主页链接，按 `https://www.tiktok.com/@<userHandle>` 拼接）

### 1.2 用户主页作品（userAwemeList）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| secUserId | String | 是 | 用户加密 ID（`MS4w` 开头的长串） |

响应说明：

- `data` 为**数组**（无翻页参数，一次返回账号近期全部作品），每个元素即一条作品
- 作品字段：`workId`、`content`、`shareLink`、`publishTime`（秒级时间戳）、`mediaType`、`area`
- `authorData`：作者信息（`userName`、`userHandle`、`fansCount`、`followCount`、`likedTotal`、`workCount`、`userSignature`、`userArea`、`avatarImage`、`verifyInfo`、`secUserId`、`userId` 等）——账号基础信息可由首条作品的 authorData 提取
- `statsData`：统计数据（`viewCount` 播放、`likeCount` 点赞、`commentTotal` 评论、`favoriteCount` 收藏、`shareTotal` 分享等）
- `videoData`：视频数据（`coverImage`、`playAddress`、`downloadNoMarkAddress` 等）
- 数据可能为 `null`（账号暂无作品），此时如实说明

### 1.3 用户喜欢作品（userFavoriteAwemeList）

请求参数：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| sec_user_id | String | 是 | 用户加密 ID（`MS4w` 开头的长串，注意下划线命名） |
| max_cursor | Integer | 是 | 翻页游标，第一页传 `0`，翻页传上一次响应中的 nextCursor |

响应说明：

- `data.hasMore`：1-还有下一页，0-没有；`data.nextCursor`：下一页游标
- `data.workList`：作品列表，单页约 20 条，作品结构与主页作品一致
- 喜欢列表为私密的账号返回空列表（`hasMore` 为 null），此时提示「该账号的喜欢列表可能已设为私密」

---

## Step 2：理解用户意图与账号定位

### 2.1 账号输入解析

| 用户输入 | 解析结果 | 定位方式 |
|---|---|---|
| secUserId（`MS4w` 开头长串） | secUserId | 直接定位，无需搜索 |
| 带 `sec_uid=MS4w...` 参数的分享链接 | secUserId | 直接定位，无需搜索 |
| 主页链接（`tiktok.com/@xxx`） | handle | searchUser 搜索精确匹配 |
| @handle / 裸 handle | handle | searchUser 搜索精确匹配 |
| 昵称 / 关键词 | 关键词 | searchUser 搜索候选，用户确认后继续 |

账号输入规则：

- 若用户提供的 secUserId 不正确（不以 `MS4w` 开头、长度过短或格式错误），将下方「secUserId 获取方式」指引返回给用户，引导重新获取后再查询
- 若用户只输入昵称 / 关键词（非 handle），必须先用 `--resolve` 展示候选账号，由用户确认后再继续分析，不要直接分析第 1 个候选
- 若 handle 搜索未精确匹配，脚本会展示候选列表并默认选定第 1 个；Agent 必须提示用户核对，可用 `--pick N` 重新指定

secUserId 获取方式（secUserId 为 MS4w 开头的完整长串）：

1. 手机 TikTok App 进入目标账号主页 → 点右上角「分享」→「复制链接」，分享链接中带有 `sec_uid=MS4w...` 参数，把完整分享链接提供给本技能即可
2. 或按 F12 打开浏览器开发者工具 → Console 粘贴执行：`JSON.parse(document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').textContent).__DEFAULT_SCOPE__['webapp.user-detail'].userInfo.user.secUid`
3. 复制时请确认以 `MS4w` 开头且整串完整，中途截断会查询失败

### 2.2 查询类型

| 用户意图 | 执行动作 |
|---|---|
| 只问账号数据（粉丝、获赞、作品数等） | `--types profile`（仅搜索定位，1 次调用） |
| 只看主页作品 | `--types works` |
| 只看喜欢作品 | `--types favorites` |
| 全面分析 / 背调 / 泛指 | `--types all`（默认） |
| 昵称 / 关键词定位 | 先 `--resolve` 展示候选，用户确认后再执行分析 |
| 喜欢作品翻页 | `--cursor <上一次输出的 nextCursor>` |
| 查看原始返回 | `--raw` |

用户只提到某一类时，只查询该类型，不默认追加其他类型；只有泛指分析或明确要求「都看看」时才用 `--types all`。

### 2.3 积分口径

- `--types all` + 昵称 / handle 定位：3 次调用（搜索定位 + 主页作品 + 喜欢作品）
- `--types all` + secUserId 直接定位：2 次调用（主页作品 + 喜欢作品）
- `--resolve`：仅 1 次调用；喜欢作品翻页每次 1 次调用
- 主页作品接口一次返回全部作品，作品翻页为本地切片展示，不产生额外调用

---

## Step 3：调用脚本

```bash
# 完整分析（handle 精确定位）：3 次接口调用，结果落盘供 HTML 报告使用
python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types all --save-json

# 昵称 / 关键词先定位（仅 1 次调用，展示候选账号）
python scripts/tiktok_account_analyzer.py --account "Tom Curtain" --resolve
# 用户确认后选定候选并完整分析（3 次调用）
python scripts/tiktok_account_analyzer.py --account "Tom Curtain" --pick 11 --types all --save-json

# 直接提供 secUserId：2 次调用
python scripts/tiktok_account_analyzer.py --account "MS4wLjAB..." --types all --save-json

# 只看主页作品
python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types works

# 喜欢作品翻页：按上次输出提示的 cursor 继续
python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types favorites --cursor 1791462081000000

# 生成 HTML 报告（基于已保存的查询结果与本地分析 JSON，不调用接口、不消耗积分）
python scripts/generate_report.py --data output/tiktok_account_latest.json --analysis output/tiktok_account_analysis.json

# 六维量化诊断（离线评分，读已保存 JSON，不调用接口、不消耗积分；可选 --update-analysis 写入分析 JSON）
python scripts/tiktok_diagnosis.py --data output/tiktok_account_latest.json
python scripts/tiktok_diagnosis.py --data output/tiktok_account_latest.json --update-analysis output/tiktok_account_analysis.json
```

执行规则：

- Agent 执行查询时统一附带 `--save-json`，结果落盘到 `output/tiktok_account_latest.json`（本地文件，不产生额外接口调用）
- Agent 将对话中写好的「爆款作品 TOP3 拆解」与「账号诊断总结」写入本地 `output/tiktok_account_analysis.json`（结构：`viralTop3` 数组 + `diagnosis` 字符串，示例见下），与对话输出保持完全一致
- 查询完成后运行 `tiktok_diagnosis.py --data output/tiktok_account_latest.json --update-analysis output/tiktok_account_analysis.json`：脚本按规则离线计算六维量化诊断（不调用接口、不消耗积分），将结果以 `scoring` 键注入分析 JSON，并把评论文本输出到 stdout（直接用作对话中的「📐 六维量化诊断」板块）
- 再用上述两个 JSON 运行 `generate_report.py --no-open` 生成 HTML 报告（本地文件生成，不调用接口、不消耗积分），报告含「🎯 爆款作品 TOP3 拆解」「📐 六维量化诊断」与「🔍 账号诊断总结」板块；用户要求「导出报告」时直接复用已生成的报告，JSON 缺失时才重新查询一次
- `--save-json` 不带路径时使用默认路径；翻页查询同样覆盖保存为最新结果
- 脚本用 `python` 命令路径按运行环境而定（Windows 下需保证控制台为 UTF-8 编码）
- 改动评分规则或 `tiktok_diagnosis.py` 后必须运行 `python scripts/regression_test.py` 回归测试（离线，不消耗积分）

分析 JSON 结构（`viralTop3` 与 `diagnosis` 由 Agent 依据对话中的分析块如实填写；`scoring` 由 `tiktok_diagnosis.py --update-analysis` 自动注入，Agent 不手写）：

```json
{
  "viralTop3": [
    {
      "rank": 1,
      "title": "作品内容摘要",
      "date": "2025-12-16",
      "plays": 335563,
      "likes": 25986,
      "reason": "爆款原因推测（1~2 句，明确为推测）",
      "link": "完整作品链接"
    }
  ],
  "diagnosis": "100~200 字账号诊断总结",
  "scoring": {}
}
```

参数校验（脚本内置）：

- `--account` 不能为空
- `--count` 必须在 1~50 之间（默认 10）
- `--works-offset` 不能小于 0；`--pick` 不能小于 1
- `--cursor` 必须为整数游标
- `--types` 可选值：`profile` / `works` / `favorites` / `all`（默认 `all`）

---

## Step 4：渲染输出

输出参考「X(Twitter) 企业家影响力榜」技能的结构：数据表格在前，AI 分析块在后，结尾统一附免责声明与「更多操作」。输出顺序固定：

1. 💡 分析说明
2. 👤 账号基础信息
3. 📊 主页作品榜 + 🎯 爆款作品 TOP3 拆解
4. 🧭 喜欢作品透视 + 💡 喜欢偏好解读
5. 📐 六维量化诊断
6. 🔍 账号诊断总结
7. 免责声明
8. ⚡ 更多操作

整体模板如下（`{}` 为占位内容，Agent 依据脚本输出如实填写；未查询的类型不输出对应板块）：

```text
💡 分析说明：账号「{昵称}」（@{TikTok号}）的 TikTok 深度分析，{口径说明}；数据来自红狐数据服务，与实时数据可能存在差异。
🔑 API Key 获取：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)

👤 账号基础信息
{基础信息表格}

📊 主页作品榜（按发布时间倒序，统计范围：本页作品）
{主页作品信息行}

{主页作品表格}

🎯 爆款作品 TOP3 拆解（按播放数排序，统计范围：本页主页作品）
1. **{作品摘要}** 发布于 {日期} ｜ 播放 {x} ｜ 点赞 {y}
   爆款原因推测：{1~2 句，结合内容与数据表现，明确为推测} ｜ [打开作品]({作品链接})

🧭 喜欢作品透视（该账号喜欢的内容，按发布时间倒序，统计范围：本页喜欢作品）
{喜欢作品信息行}

{喜欢作品表格}

💡 喜欢偏好解读（统计范围：本页喜欢作品）
1. {内容类型偏好，1~2 句，明确为推测}
2. {关注的作者圈层，1~2 句，明确为推测}
3. {与自身内容定位的关联，1~2 句，明确为推测}

📐 六维量化诊断
{直接粘贴 `tiktok_diagnosis.py` 的 stdout 输出：综合评分行 + 维度表格 + 风险预警 + 提示行，原样呈现，不改写}

🔍 账号诊断总结
{100~200 字分析：账号定位、内容策略、数据表现与商业化信号，关键数据附主页链接}

（以上为基于公开数据的 AI 分析与推测，仅供参考。）

⚡ 更多操作
• [打开 HTML 报告]({报告文件绝对路径})，支持导出 PDF / 高清图片
• 是否继续查看下一页（主页作品 / 喜欢作品）？
```

各板块规则：

- **分析说明**：`{口径说明}` 写本次查询类型（如"含主页作品与喜欢作品"）；如为候选选定，注明"按第 N 个候选分析"
- **信息行**（紧跟板块标题之后）：
  ```text
  主页作品：本页 <n> 条 | 已拉取共 <N> 条 | 显示偏移：<offset>
  喜欢作品：本页 <n> 条 | hasMore：<hasMore> | 下一页 cursor：<nextCursor>
  ```
- **表格表头固定**为：
  ```text
  ### 👤 账号基础信息
  | 项目 | 数据 |
  |---|---|
  | 昵称 | ... |
  | TikTok号 | ... |
  | 粉丝数 | ... |
  | 关注数 | ... |
  | 获赞总数 | ... |
  | 作品数 | ... |
  | 地区 | ... |
  | 认证 | ... |
  | 签名 | ... |
  | 主页链接 | [打开主页](https://www.tiktok.com/@<handle>) |

  ### 📊 主页作品（按发布时间倒序）
  | # | 发布时间 | 作品 | 播放 | 点赞 | 评论 | 收藏 | 分享 | 作品链接 |
  |---:|---|---|---:|---:|---:|---:|---:|---|

  ### 🧡 喜欢作品（按发布时间倒序）
  | # | 发布时间 | 作品 | 作者 | 播放 | 点赞 | 作品链接 |
  |---:|---|---|---|---:|---:|---|
  ```
- **表格渲染规则**（与脚本输出一致）：
  - 作品链接必须使用接口返回的完整 `shareLink`，格式为 `[打开作品](完整shareLink)`
  - 主页链接按 `https://www.tiktok.com/@<userHandle>` 拼接，格式为 `[打开主页](完整URL)`；`userHandle` 为空时显示"暂无链接"
  - 喜欢作品「作者」列展示该作者昵称，`userHandle` 不包含在昵称中时追加 `(@handle)`
  - 所有数字加千分位（如 `1,234,567`）；发布时间为秒级时间戳，按北京时间渲染为 `YYYY-MM-DD` 日期
  - 作品默认按发布时间倒序；内容摘要超过 60 字符截断加 `...`，表格内文本转义换行与 `|`
  - 喜欢作品为空时输出"暂无数据（该账号的喜欢列表可能已设为私密）"
  - 某类型失败时输出该类型错误说明，其余类型正常输出
- **分析块规则**：
  - 只对本次查询且非空的类型输出分析块；爆款拆解只分析 TOP3，本页不足 3 条时按实际条数分析并注明
  - 喜欢偏好解读逐条 1~2 句；账号诊断总结 100~200 字
  - 爆款原因、喜欢偏好与账号诊断必须基于本页表格可见数据撰写，不得编造数据之外的细节
  - 所有分析内容须以"推测 / 解读"口吻表述，结尾统一附免责声明；分析中引用的作品 / 主页链接保持完整可点击
  - 喜欢作品为空时跳过喜欢偏好解读，如实说明；基础信息不完整（如 secUserId 直接定位但无作品）时如实说明缺失项
- **六维量化诊断板块**：
  - 只要执行过 `--save-json` 查询，就运行 `tiktok_diagnosis.py --data output/tiktok_account_latest.json` 并原样输出其 stdout（离线计算，不消耗积分）
  - 板块位于「喜欢作品透视」与「账号诊断总结」之间；未查询喜欢作品时紧随「爆款作品 TOP3 拆解」之后
  - 文本中不添加任何内部步骤标签（如"运行脚本""离线计算"等），只呈现脚本输出的评分表、风险预警与提示行
  - 评分规则详见 `references/diagnosis_rules.md`；输出中已含"初始校准值"提示，Agent 不再额外解释评分基准
- **报告入口**：每次查询完成后，按 Step 3 先运行 `tiktok_diagnosis.py --update-analysis` 注入评分，再用已落盘的两个 JSON 运行 `generate_report.py --no-open` 生成 HTML 报告（本地文件生成，不产生接口调用、不消耗积分），报告含客观数据 + 「🎯 爆款作品 TOP3 拆解」「📐 六维量化诊断」与「🔍 账号诊断总结」板块，分析内容与对话输出一致；入口用 `[打开 HTML 报告](文件绝对路径)` 形式给出可点击链接，并注明支持导出 PDF / 高清图片；报告生成失败（如 JSON 缺失）时如实说明，不重复查询
- **翻页提示**：主页作品翻页为本地切片（`--works-offset`，无额外调用）；喜欢作品按信息行中的「下一页 cursor」提示用户是否继续翻页，不主动翻页

---

## Step 5：错误处理

| 场景 | 处理方式 |
|---|---|
| `code=3103` / `code=3105` | API Key 不存在或已禁用：提示更换有效 Key 并输出获取提醒，不要重复重试 |
| `code=3201` | 积分不足：提示前往红狐控制台充值后重试 |
| `code=1001` / `1002` / `1003` | 参数问题：按 `msg` 提示修正参数后重试 |
| `code=4004` | 操作过于频繁：稍后重试，不要连续重试 |
| `502` | 服务返回 502 错误，可能存在网络不稳定问题，请稍后重试 |
| 其他非 `2000` 返回 | 输出 `接口返回异常：code=<code>, msg=<msg>` |
| 搜索无候选 | 提示提供准确的 TikTok 主页链接或带 `sec_uid` 参数的分享链接，附 secUserId 获取方式 |
| 主页作品为空 | 输出"暂无数据"，如为基础信息缺失则如实说明 |
| 喜欢作品为空 | 输出"暂无数据（该账号的喜欢列表可能已设为私密）" |
| 脚本异常 | 错误信息输出到 stderr 并以 exit 1 退出；与 Key 相关时同时输出 API Key 获取提醒 |

---

## Step 6：注意事项

1. **积分保护**：每次成功查询可能消耗积分；一次 `--types all` 最多包含 3 次数据查询；未经用户明确指定，不要主动翻页或批量查询多个账号
2. **定位确认**：昵称 / 关键词搜索必须先展示候选账号由用户确认（或 `--pick` 指定），不得静默分析第 1 个候选
3. **链接完整性**：输出中的链接必须保持完整，不要使用被终端截断的 URL
4. **无结果不替换**：空结果时如实说明，不自动改查其他账号
5. **鉴权提示**：依赖环境变量 `REDFOX_API_KEY`（三级读取），API Key 获取：https://redfox.hk/settings/api-keys?source=github
6. **分析为推测**：爆款原因、喜欢偏好与账号诊断均基于公开数据撰写，必须标注为推测，不得编造数据之外的细节
7. **报告零成本**：HTML 报告与六维量化诊断仅读取本地 JSON 生成/计算，不发起接口调用、不消耗积分；报告中的爆款拆解与诊断总结由 Agent 写入本地分析 JSON 后注入，评分由 `tiktok_diagnosis.py` 注入，与对话输出一致
8. **改动评分规则须回归**：修改 `tiktok_diagnosis.py` 或 `references/diagnosis_rules.md` 中的规则后，必须运行 `python scripts/regression_test.py`（离线，不消耗积分）验证评分模型

---

## Step 7：版本信息

- **版本号**：v1.1.0
- **核心功能**：输入 TikTok 主页链接、handle、secUserId 或昵称定位账号，输出账号基础信息、主页作品榜与喜欢作品透视；附六维量化诊断（100 分制评分 + 量级自适应基准 + 六类风险预警，规则化离线计算）、爆款作品 TOP3 拆解、喜欢偏好解读与账号诊断总结；支持喜欢作品游标翻页与 HTML 报告（含六维量化诊断 / 爆款拆解 / 诊断总结板块，导出 PDF / 高清图片）
- **数据来源**：红狐 API `/story/api/tiktok/ability/searchUser`、`/userAwemeList`、`/userFavoriteAwemeList`
