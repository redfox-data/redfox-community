# Core Workflow

> 本文件为 Agent 内部执行手册，包含完整的技术执行逻辑。SKILL.md 仅保留用户向描述，Agent 执行时以本文件为唯一逻辑来源，保证功能完整。

## 1. 数据获取机制

- **数据源**：redfox.hk 官方鉴权接口 `POST https://redfox.hk/story/api/xhsData/query`（按次计费）
- **传输方式**：原生 Socket + SSL，**不发送 SNI**（`check_hostname=False`、`verify_mode=CERT_NONE`、`wrap_socket(server_hostname=None)`），这是数据源接口的硬性要求，改用 requests 等常规方式会连接失败
- **请求头**：
  - `X-API-KEY`：主鉴权头
  - `REDFOX_API_KEY`：同时附带，兼容官方文档示例（双发兼容）
  - `Content-Type: application/json`
- **请求体**：
  ```json
  {
    "dateType": 1,
    "rankDate": "2026-04-18",
    "type": "综合全部",
    "source": "小红书达人涨粉榜查询-GitHub"
  }
  ```
  - `dateType` 映射：`daily`→1、`weekly`→2、`monthly`→3
  - `source` 为调用来源标识，随请求上报供数据源统计渠道；源目录固定为 `-GitHub`，发布到其他平台时由 duplicate.py 自动替换为对应平台后缀（如 `-SkillHub`）
- **响应判断**：`code == 2000` 且含 `data` 字段为成功；否则输出 `msg` 错误信息
- 接口同时支持分块传输编码（Transfer-Encoding: chunked）响应解析

## 2. API Key 读取链

- **优先级**：`--api-key` 参数 > 环境变量 `REDFOX_API_KEY` > shell 配置文件自动扫描
- **shell 配置扫描路径**：
  - `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile`
  - Windows PowerShell profile：`~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1`、`~/Documents/PowerShell/Microsoft.PowerShell_profile.ps1`
- **匹配写法**：
  - bash/zsh：`export REDFOX_API_KEY=ak_xxx`（export 可选，引号可选）
  - PowerShell：`$env:REDFOX_API_KEY = "ak_xxx"`（引号可选）
- **无 Key 时**：直接输出配置指引并返回空数据（API Key 为查询的必要条件），指引文案：
  - macOS/Linux：`export REDFOX_API_KEY=<值>` 追加到 `~/.zshrc` 或 `~/.bashrc`，然后 `source` 对应文件
  - Windows：`[Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")`（需重启终端）
  - 验证：`echo $REDFOX_API_KEY`（macOS/Linux）或 `echo %REDFOX_API_KEY%`（Windows）

## 3. 鉴权错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 3106 | 缺少 API Key | 通过 --api-key 或环境变量提供 |
| 3201 | 积分不足 | 前往控制台充值 |
| 3202 | 积分账户不存在 | 登录控制台确认账户状态 |
| 4004 | 操作过于频繁 | 降低请求频率后重试 |

## 4. 数据解析与指标计算

接口原始字段 → 标准字段映射：

| 原始字段 | 标准字段 | 说明 |
|----------|----------|------|
| accountRanking | ranking | 排名 |
| accountName | account_name | 账号名称 |
| accountLink | account_id / account_link | 账号主页链接 |
| category | category | 类目 |
| fansCount | followers_count | 粉丝数（如 "375.00w"） |
| fansGrowth | growth_count | 涨粉数（如 "1.11w"） |
| likedGrowth | liked_growth | 点赞增长 |
| commentsGrowth | comments_growth | 评论增长 |
| collectedGrowth | collected_growth | 收藏增长 |
| sharedGrowth | shared_growth | 分享增长 |
| newNoteCount | new_note_count | 新增笔记数 |
| avatar | avatar_url | 头像 URL |
| rankDate | stat_date | 统计日期 |
| rankPeriod | stat_type | 排名周期（日/周/月） |

- **涨粉率**：官方接口无该字段，按 `涨粉数 / (粉丝数 - 涨粉数) × 100` 计算，保留 4 位小数；分母 ≤0 时记为 0
- **数字解析**：支持 `w`/`万` 后缀（如 `"375.00w"` → 3750000）、千分位逗号、浮点/整型混合

## 5. 脚本命令参考

### query_rankings.py（数据查询入口）

```bash
python3 scripts/query_rankings.py --category 综合全部 --type daily --limit 20
python3 scripts/query_rankings.py --category 综合全部 --type daily --limit 20 --output /tmp/rankings.json
python3 scripts/query_rankings.py --category 化妆美容 --type weekly --limit 20
```

参数：`--category`（默认综合全部）、`--type`（daily/weekly/monthly，默认 daily）、`--date`（YYYY-MM-DD，默认前天）、`--limit`（默认 20，上限 100）、`--output`（JSON 输出路径）、`--action`（rankings/categories/dates）、`--api-key`

### generate_ranking_image.py（一键查询+生成图片）

```bash
python3 scripts/generate_ranking_image.py --category 综合全部 --limit 20
python3 scripts/generate_ranking_image.py --category 化妆美容 --limit 20
python3 scripts/generate_ranking_image.py --category 综合全部 --type weekly --limit 20
python3 scripts/generate_ranking_image.py --category 综合全部 --type monthly --limit 20
python3 scripts/generate_ranking_image.py --category 综合全部 \
  --title "小红书涨粉榜" --subtitle "昨日涨粉最快的博主" --api-key "你的APIKey"
python3 scripts/generate_ranking_image.py --category 综合全部 --date 2026-04-10 --limit 20
python3 scripts/generate_ranking_image.py --output ~/Desktop/my_ranking.png
```

流程：校验类目 → 查询数据 → 自动生成标题/副标题（默认"小红书涨粉榜"+类目+榜型+TOP N）→ 生成 PNG → 复制到桌面。默认文件名：`小红书涨粉榜_{类目}_{类型}_{时间戳}.png`

### export_to_excel.py（导出 Excel）

```bash
python3 scripts/query_rankings.py --category 综合全部 --type daily --limit 20 --output /tmp/rankings.json
python3 scripts/export_to_excel.py --data /tmp/rankings.json --output ~/Desktop/涨粉榜.xlsx
```

依赖：`pandas==2.0.0 openpyxl==3.1.0`

### generate_chart.py（图表生成）

```bash
python3 scripts/generate_chart.py --type table --data data.json --output table.png
python3 scripts/generate_chart.py --font /System/Library/Fonts/PingFang.ttc ...
```

支持表格样式图片（table）等；中文字体异常时用 `--font` 指定中文字体路径。

### subscription_manager.py（订阅管理）

```bash
python3 scripts/subscription_manager.py create --user-id xxx --categories 综合全部 --frequency daily --tier free
python3 scripts/subscription_manager.py list [--user-id xxx] [--due]
python3 scripts/subscription_manager.py update --id xxx --frequency weekly
python3 scripts/subscription_manager.py cancel --id xxx
python3 scripts/subscription_manager.py tiers [--tier basic]
python3 scripts/subscription_manager.py mark-sent --id xxx
```

### delivery_service.py（推送服务）

- 邮件推送：SMTP 配置（smtp_server、smtp_port、username、password、from_name），支持 HTML 内容与附件
- 微信推送：模板消息（appid、appsecret、template_id）

## 6. 订阅体系

三级订阅（详见 `references/subscription_tiers.md`）：

| 等级 | 价格 | 类目数 | 频率 | 图表 | 历史数据 |
|------|------|--------|------|------|----------|
| 免费版 Free | ¥0 | 1 | 仅周榜 | 基础柱状图 | 7 天 |
| 基础版 Basic | ¥29/月 或 ¥299/年 | 3 | 日+周 | 柱状/折线/对比 | 30 天 |
| 高级版 Premium | ¥99/月 或 ¥999/年 | 不限 | 日+周+月 | 全部+自定义 | 无限 |

- 订阅数据存储于 `subscriptions.json`（id、user_id、categories、frequency、tier、status、next_send_at 等）
- 推送时间：日榜次日上午 9:00、周榜每周一 9:00、月榜每月 1 号 9:00
- 权限校验：创建/更新订阅时校验等级对应的类目数与频率上限

## 7. 数据规则硬约束

- **类目**：仅支持 25 个固定类目（综合全部 + 24 个细分），**不支持自定义关键词订阅**
- **条数上限**：单个类目榜单最多 100 条（MAX_LIMIT=100，超出自动截断并提示）
- **查询范围**：日榜最多查前 30 天、周榜最多查前 8 周、月榜最多查前 3 个月
- **更新节奏**：榜单每日下午 7:00 发布；数据有 1 天延迟（如 4 月 20 日可获取 4 月 18 日数据）；周榜周一更新上周、月榜每月 1 号更新上月
- **默认日期**：未指定 `--date` 时默认取前天（确保数据已发布）
- **周榜日期**：rankDate 需为周一；**月榜日期**：rankDate 需为每月 1 号

## 8. 交付物与输出路径

- **榜单图片**：默认保存到脚本执行目录，并自动复制到桌面；`--output` 可自定义
- **Excel**：默认保存到桌面
- **JSON 数据**：`--output` 指定路径，否则打印到 stdout

## 9. 故障排除

**查询返回空数据**：
1. 确认网络可访问 redfox.hk
2. 确认日期参数正确（日榜需在每晚 20:00 后查昨日数据；周榜输入周一日期；月榜输入每月 1 号）
3. 确认类目名称正确（仅 25 个固定类目）

**Connection reset by peer / read operation timed out**：
1. 确认已配置 API Key（缺失时脚本直接返回空数据并输出配置指引）
2. 确认网络环境可访问 redfox.hk
3. 联系管理员确认访问权限

**ModuleNotFoundError**（Pillow / requests / matplotlib 等）：
```bash
pip install Pillow==10.0.0 requests==2.31.0 matplotlib==3.7.0 numpy==1.24.0 pandas==2.0.0 openpyxl==3.1.0
```

**中文字体显示异常**：用 `generate_chart.py --font /System/Library/Fonts/PingFang.ttc` 指定中文字体路径。

**图片生成成功但找不到文件**：检查当前目录与桌面；或用 `--output` 指定路径。

## 10. 项目架构

### 目录结构

```
xhs-follower-growth-chart/
├── SKILL.md                          # 技能文档（用户向）
├── scripts/                          # 核心脚本
│   ├── query_rankings.py             # 数据查询（入口脚本）
│   ├── generate_ranking_image.py     # 一键生成榜单图片
│   ├── export_to_excel.py            # 导出数据为 Excel
│   ├── generate_chart.py             # 图表生成（表格/柱状图）
│   ├── subscription_manager.py       # 订阅管理
│   └── delivery_service.py           # 推送服务
└── references/                       # 参考文档
    ├── core_workflow.md              # 本文件（核心执行流程）
    └── subscription_tiers.md         # 付费订阅方案
```

### 技术栈

- **运行环境**：Python 3.8+
- **核心依赖**：Pillow（图片生成）、matplotlib（图表绘制）、requests（HTTP 请求）、pandas/openpyxl（Excel 导出）、numpy
- **网络层**：原生 socket + ssl（无 SNI），不依赖 requests 做数据查询
- **部署平台**：Coze / Skillhub / Clawhub / GitHub

### 数据流转

```
用户请求 → generate_ranking_image.py → query_rankings.py → redfox.hk 鉴权接口
                                              ↓
用户展示 ← 图片文件 ← generate_chart.py ← 原始数据
```

### 核心模块

| 模块 | 职责 |
|------|------|
| `query_rankings.py` | 主入口脚本，查询数据并引导用户后续操作；含 HTTPSClient（无 SNI）与 RankingAPIClient |
| `generate_ranking_image.py` | 一键生成榜单图片（校验→查询→生成→复制桌面） |
| `export_to_excel.py` | 将榜单数据导出为 Excel 文件 |
| `generate_chart.py` | 使用 PIL 生成表格样式图片 |
| `subscription_manager.py` | 订阅的增删改查，支持三级订阅体系 |
| `delivery_service.py` | 邮件、微信模板消息推送 |

## 11. 更新日志

### v1.1.3
- 接口调用新增 `source` 字段（源目录值：`小红书达人涨粉榜查询-GitHub`，平台变体由 duplicate.py 自动替换），随请求上报，供数据源统计渠道来源

### v1.1.2
- 彻底移除已停摆的旧免费接口（GET /story/api/hotSpot/getXhsRiseFansRank）：未配置 API Key 时不再发出无意义请求，直接输出配置指引并返回空数据
- 同步清理旧接口专用代码：`--source` 参数、旧版响应解析器与 GET 请求方法

### v1.1.1
- 鉴权请求头统一为 `X-API-KEY`（同时附带 `REDFOX_API_KEY` 兼容头）
- API Key 读取链扩展：`--api-key` 参数 > 环境变量 `REDFOX_API_KEY` > 自动扫描 shell 配置文件（`~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 及 PowerShell profile）
- 按标准模板重写鉴权章节：红狐Hub 注册流程（新注册用户赠送免费积分）、各平台环境变量配置指引与验证方法、Agent 代设指引

### v1.1.0
- 适配 redfox.hk 平台 API 升级：旧免费接口已停摆，切换至官方鉴权接口 `POST /story/api/xhsData/query`
- 新增 API Key 支持：`--api-key` 参数与 `REDFOX_API_KEY` 环境变量，未配置时自动兜底并给出明确提示
- 新增字段解析：点赞/评论/收藏/分享增长、新增笔记数、账号主页链接等
- 修复旧接口路径缺失 `/api/` 层级导致的超时问题

### v1.0.0
- 基础数据查询功能
- 表格样式图片生成
- 一键生成脚本
- 订阅管理功能
- 定时推送支持
- 支持 25 个固定类目
