# 小红书达人涨粉榜查询 · XHS Follower Growth Chart

**[中文](./README.md) | [English](./README.en.md)**

> 想知道小红书哪些账号涨粉最猛？这款工具帮你追踪日榜 / 周榜 / 月榜涨粉数据，覆盖 25 个品类，还能一键生成好看的排名图、导出 Excel！

[![Version](https://img.shields.io/badge/version-1.1.3-blue.svg)](./SKILL.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Coze%20%7C%20Skillhub%20%7C%20Clawhub%20%7C%20GitHub-orange.svg)]()

---

## ✨ 功能特性

- **📊 数据追踪** —— 粉丝数、涨粉数、涨粉率等核心指标，另含点赞 / 评论 / 收藏 / 分享增长与新增笔记数
- **📈 排名统计** —— 日榜 / 周榜 / 月榜三种维度，25 个固定类目筛选
- **🎨 图片生成** —— 一键生成小红书风格表格排名图，可直接发布
- **📥 Excel 导出** —— 榜单数据完整字段导出，便于自行分析
- **🔔 定时推送** —— 支持订阅每日 / 每周 / 每月自动推送（见 `subscription_manager.py`）

**适合谁用**：品牌方（盯竞品、找达人）、MCN（管旗下账号）、博主（看同行、找灵感）、数据爱好者。

---

## 🔐 鉴权（使用前提）

本工具通过 [红狐Hub](https://redfox.hk/?source=github) 官方鉴权 API 获取数据，**API Key 为查询的必要条件**。

### 获取 API Key

1. 访问 [红狐Hub 官网](https://redfox.hk/?source=github) 了解服务详情
2. 前往 [注册页面](https://redfox.hk/login?source=github) 注册账号
3. **新注册用户将获赠免费积分**，可立即开始使用 API 服务
4. 注册登录后，在个人中心获取 API Key，格式为 `ak_xxxxxxxx`

### 配置 API Key

- **macOS / Linux**：将 `export REDFOX_API_KEY=<值>` 追加到 `~/.zshrc`（zsh）或 `~/.bashrc`（bash），然后 `source` 对应文件使其全局生效
- **Windows**：执行以下命令设置用户级永久环境变量（需重启终端生效）：

  ```powershell
  [Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")
  ```

- 配置完成后验证：`echo $REDFOX_API_KEY`（macOS/Linux）或 `echo %REDFOX_API_KEY%`（Windows），确保其他工具也能读取到

### 读取优先级与请求头

- **读取优先级**：`--api-key` 参数 > 环境变量 `REDFOX_API_KEY` > 自动扫描 shell 配置文件（`~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 及 PowerShell profile 中的 `export REDFOX_API_KEY=xxx` / `$env:REDFOX_API_KEY = "xxx"` 写法）
- **请求鉴权头**：脚本发起请求时自动携带 `X-API-KEY` 请求头（同时附带 `REDFOX_API_KEY` 兼容头）
- **请求体**：JSON 格式，附带来源标识 `source`（值固定为 `小红书达人涨粉榜查询-GitHub`），随请求上报供数据源统计渠道来源

  ```json
  {
    "dateType": 1,
    "rankDate": "2026-09-17",
    "type": "综合全部",
    "source": "小红书达人涨粉榜查询-GitHub"
  }
  ```

- 三处均未获取到 Key 时，脚本直接返回空数据并输出上述配置指引

**常见鉴权错误码**：

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 3106 | 缺少 API Key | 通过 `--api-key` 或环境变量提供 |
| 3201 | 积分不足 | 前往控制台充值 |
| 3202 | 积分账户不存在 | 登录控制台确认账户状态 |
| 4004 | 操作过于频繁 | 降低请求频率后重试 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 依赖安装（推荐固定版本号）：

```bash
pip install Pillow==10.0.0 requests==2.31.0 matplotlib==3.7.0 numpy==1.24.0 pandas==2.0.0 openpyxl==3.1.0
```

### 1. 查询榜单数据

```bash
# 配置 API Key（推荐环境变量方式；也可每次用 --api-key 参数传入）
export REDFOX_API_KEY="你的APIKey"

# 查询综合全部日榜 TOP20
python3 scripts/query_rankings.py --category 综合全部 --limit 20

# 指定类目 / 周期 / 日期
python3 scripts/query_rankings.py --category 化妆美容 --type weekly --date 2026-09-07 --limit 20
```

### 2. 生成榜单图片

```bash
# 一键生成（查询 + 生成图片），图片保存到当前目录
python3 scripts/generate_ranking_image.py --category 综合全部 --type daily --limit 20

# 自定义标题
python3 scripts/generate_ranking_image.py \
  --category 综合全部 \
  --title "小红书涨粉榜" \
  --subtitle "昨日涨粉最快的博主" \
  --api-key "你的APIKey"
```

### 3. 导出数据为 Excel

```bash
# 先查询数据保存为 JSON
python3 scripts/query_rankings.py --category 综合全部 --type daily --limit 20 --output /tmp/rankings.json

# 导出为 Excel
python3 scripts/export_to_excel.py --data /tmp/rankings.json --output ~/Desktop/涨粉榜.xlsx
```

### 4. 订阅定时推送

```bash
python3 scripts/subscription_manager.py create   # 创建订阅
python3 scripts/subscription_manager.py list     # 查看订阅列表
```

---

## 📅 数据规则

- **更新时间**：榜单每日晚上 8 点更新，日榜可查昨日数据；周榜每周一更新上周数据（`--date` 填周一日期）；月榜每月 1 号更新上月数据（`--date` 填每月 1 号）
- **数据延迟**：数据有 1 天延迟（例如：4 月 20 日可获取 4 月 18 日完整数据）；不指定日期时默认获取前天数据
- **查询范围限制**：

| 周期 | 参数 | 最多查询 |
|------|------|----------|
| 日榜 | `--type daily` | 前 30 天 |
| 周榜 | `--type weekly` | 前 8 周 |
| 月榜 | `--type monthly` | 前 3 个月 |

- 查询结果为空时不扣除积分

### 常用命令速查

| 命令 | 功能 |
|------|------|
| `query_rankings.py --category 综合全部` | 查询榜单数据 |
| `generate_ranking_image.py --category [类目]` | 生成榜单图片 |
| `export_to_excel.py --data [文件]` | 导出数据为 Excel |
| `generate_chart.py --type table` | 生成表格样式图片 |
| `subscription_manager.py create` | 创建订阅 |
| `subscription_manager.py list` | 查看订阅列表 |

---

## 🗂 支持的类目（25 个固定类目）

**默认推荐**：`综合全部`（包含所有类型账号）

**细分类型（24 种）**：

出行代步、医疗保健、休闲爱好、综合杂项、婚庆婚礼、居家装修、影视娱乐、星座情感、拍摄记录、学习教育、旅行度假、亲子育儿、日常生活、科学探索、数码科技、时尚穿搭、化妆美容、个人护理、美味佳肴、职业发展、宠物天地、新闻资讯、体育锻炼、潮流鞋包

> 仅支持上述 25 个类目，不支持自定义关键词订阅。单个榜单最多返回 100 条（`--limit` 控制，默认 20）。

---

## 📂 目录结构

```text
xhs-follower-growth-chart/
├── README.md                       # 本文档（GitHub 平台）
├── SKILL.md                        # 技能平台元数据文档
├── icon.png                        # 技能图标
├── scripts/                        # 核心脚本
│   ├── query_rankings.py           # 数据查询（入口脚本）
│   ├── generate_ranking_image.py   # 一键生成榜单图片
│   ├── export_to_excel.py          # 导出数据为 Excel
│   ├── generate_chart.py           # 图表生成（表格/柱状图）
│   ├── subscription_manager.py     # 订阅管理
│   └── delivery_service.py         # 推送服务
└── references/                     # 参考文档
    └── subscription_tiers.md       # 付费订阅方案
```

### 数据流转

```text
用户请求 → generate_ranking_image.py → query_rankings.py → 数据源（redfox.hk 官方鉴权 API）
                                              ↓
用户展示 ← 图片文件 ← generate_chart.py ← 原始数据
```

---

## 🛠 技术栈

- **运行环境**：Python 3.8+
- **核心依赖**：`Pillow`（图片生成）、`matplotlib`（图表绘制）、`pandas` + `openpyxl`（Excel 导出）、`requests`
- **网络访问**：原生 Socket + SSL（无 SNI）方式访问数据源
- **部署平台**：Coze / Skillhub / Clawhub / GitHub

---

## ❓ 常见问题

**Q: 查询返回空数据怎么办？**

A: 请检查：① 日期参数是否正确（日榜需在每晚 20:00 后查昨日数据，周榜输入周一日期，月榜输入每月 1 号日期）；② 类目名称是否在 25 个固定类目内；③ 网络环境是否可访问 redfox.hk。空结果不扣积分，放心重试。

**Q: 运行脚本时报鉴权错误（3106 / 3201 / 3202 / 4004）？**

A: 对照上文「常见鉴权错误码」表处理，最常见原因是未配置 `REDFOX_API_KEY` 环境变量。

**Q: 生成的图片中文字体显示异常怎么办？**

A: 指定中文字体路径：

```bash
python3 scripts/generate_chart.py --font /System/Library/Fonts/PingFang.ttc --type table --data data.json --output table.png
```

**Q: 图片生成成功但找不到文件？**

A: 图片默认保存到脚本执行目录，可通过 `--output` 参数指定路径：

```bash
python3 scripts/generate_ranking_image.py --output ~/Desktop/my_ranking.png
```

---

## 📝 更新日志

### v1.1.3
- 📌 接口调用新增 `source` 字段（值：`小红书达人涨粉榜查询-GitHub`），随请求上报，供数据源统计渠道来源

### v1.1.2
- 🧹 彻底移除已停摆的旧免费接口（GET `/story/api/hotSpot/getXhsRiseFansRank`）：未配置 API Key 时不再发出无意义请求，直接输出配置指引并返回空数据
- 🧹 同步清理旧接口专用代码：`--source` 参数、旧版响应解析器与 GET 请求方法

### v1.1.1
- 🔑 鉴权请求头统一为 `X-API-KEY`（同时附带 `REDFOX_API_KEY` 兼容头）
- 📂 API Key 读取链扩展：`--api-key` 参数 > 环境变量 `REDFOX_API_KEY` > 自动扫描 shell 配置文件（`~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile` 及 PowerShell profile）
- 📝 按标准模板重写鉴权章节：红狐Hub 注册流程（新注册用户赠送免费积分）、各平台环境变量配置指引与验证方法、Agent 代设指引

### v1.1.0
- 🔧 适配 redfox.hk 平台 API 升级：旧免费接口已停摆，切换至官方鉴权接口 `POST /story/api/xhsData/query`
- 🔑 新增 API Key 支持：`--api-key` 参数与 `REDFOX_API_KEY` 环境变量，未配置时自动兜底并给出明确提示
- 📊 新增字段解析：点赞/评论/收藏/分享增长、新增笔记数、账号主页链接等
- 🩹 修复旧接口路径缺失 `/api/` 层级导致的超时问题

### v1.0.0
- ✅ 基础数据查询功能
- ✅ 表格样式图片生成
- ✅ 一键生成脚本
- ✅ 订阅管理功能
- ✅ 定时推送支持
- ✅ 支持 25 个固定类目

---

## 📄 许可

本技能由 Agent创想工坊 提供。数据来源于 redfox.hk 平台，API 调用遵循红狐Hub 的积分计费规则（新注册用户赠送免费积分）。

如有问题：📖 查阅本文档与 `SKILL.md` ｜ 💬 联系管理员
