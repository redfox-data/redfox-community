# 核心工作流（Agent 执行参考）

本文档为 Agent 执行层的详细工作流指令，包含数据获取、展示、分析、订阅、HTML 生成等完整步骤。

## 任务目标

- 获取抖音平台热榜数据，并提供创作者视角的深度洞察
- 触发条件：用户询问抖音热榜、热门话题、热搜榜单、历史热榜、订阅热榜推送等

## 操作步骤

### 1. 获取热榜数据

**Python 执行说明**：

- 优先使用系统默认 `python` 命令
- 若 `python` 不可用（Windows Git Bash 常见），使用 WorkBuddy 管理的 Python 全路径：`"C:/Users/马祯/.workbuddy/binaries/python/versions/3.13.12/python.exe"`
- 始终先 `cd` 到技能根目录再执行

#### 1.1 实时热榜（默认）

```bash
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py
```

#### 1.2 历史热榜查询

支持查询近7天、近30天的历史热榜数据：

```bash
# 查询昨日热榜（假设今天是2026-04-16）
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py --start-date 2026-04-15 --end-date 2026-04-16

# 查询近7天热榜（假设今天是2026-04-16）
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py --start-date 2026-04-09 --end-date 2026-04-16

# 查询近30天热榜（假设今天是2026-04-16）
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py --start-date 2026-03-17 --end-date 2026-04-16

# 查询4月1日热榜
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py --start-date 2026-04-01 --end-date 2026-04-02
```

**日期范围规则**：
- 日期范围是 **[start_date, end_date)** 左闭右开区间
- 例如：`start-date 2026-04-01 --end-date 2026-04-02` 查询的是4月1日当天的数据
- 例如：`start-date 2026-04-09 --end-date 2026-04-16` 查询的是4月9日至4月15日共7天的数据

**参数说明**：
- `--start-date`：开始日期（包含），格式 YYYY-MM-DD
- `--end-date`：结束日期（不包含），格式 YYYY-MM-DD
- `--days`：查询天数，自动计算日期范围（end_date为今天）
- **最长查询范围：30天**

#### 1.3 意图判断逻辑

根据用户意图自动选择查询方式（假设今天日期为T）：

| 用户表达 | start_date | end_date | 查询范围 |
|---------|-----------|----------|---------|
| "今日热榜" / "最新热榜" / "热榜" | 无（实时） | 无（实时） | 实时 |
| "昨日热榜" / "昨天热榜" | T-1 | T | 昨日当天 |
| "近7天热榜" / "一周热榜" | T-7 | T | 近7天 |
| "近30天热榜" / "本月热榜" | T-30 | T | 近30天 |
| "X月X日热榜" | X月X日 | X月X日+1 | 指定日期当天 |

### 2. 展示热榜数据表格

将脚本返回的JSON数据转换为表格形式展示。

**标题格式**：

实时热榜：`抖音实时热榜（2026-04-14 16:00 每小时更新）`

历史热榜：`抖音历史热榜（2026-04-14 至 2026-04-15）`

**表格格式**（默认展示TOP20数据）：

| 排名 | 热度值 | 话题 | 核心内容 |
|-----|-------|------|---------|

**表格绘制规则**：
1. 排名：默认 `TOP01` 到 `TOP20`（双数字符）；加载更多 `TOP21` 到 `TOP50`
2. 热度值：保留一位小数，单位统一为 `w`（小写），示例 `1109.6w`
3. 话题：使用 Markdown 链接格式 `[标题](URL)`
4. 核心内容：30-80字，概括话题主要内容

**加载更多**：

表格下方展示：
> 抖音实时热榜为你提供TOP50的数据，是否继续加载剩余30条？

- 确认后仅输出 TOP21-TOP50，不重复 TOP1-20
- 确认后必须生成新的 HTML 文件，包含完整 TOP50 数据

### 3. 创作者洞察报告

展示数据后自动输出创作者视角的深度洞察：

#### 3.1 爆款选题机会

分析热榜内容的共同规律，提供可迁移的选题建议。

输出格式：

```
📌 爆款选题机会

发现：[核心发现]
- 数据支撑：[具体数据]
- 核心公式：[拆解出的公式]

🔄 可迁移选题：
· 美妆赛道：[具体选题建议]
· 穿搭赛道：[具体选题建议]
· 其他赛道：[具体选题建议]
```

#### 3.2 标题套路破解

提炼爆款标题模式和情绪触发词。

输出格式：

```
✏️ 标题套路破解

爆款标题模式TOP3：
1. [类型名称]：[示例]
2. [类型名称]：[示例]
3. [类型名称]：[示例]

立即可用的标题公式：
· "用[方法]，[效果]" → 例：用万能旅行拍照姿势美美出片
· "耗时[时间]，拍下[成果]" → 例：耗时三年拍下古诗词里的中国
· "原来[认知]，真的存在" → 例：原来古诗词里的河南真的存在

情绪触发词：
[高频词列表]
```

#### 3.3 趋势预判与行动建议

基于热榜数据给出前瞻性判断。

输出格式：

```
📈 趋势预判

一、[预判点1]
   [具体分析内容和依据]
   行动建议：[具体建议]

二、[预判点2]
   [具体分析内容和依据]
   行动建议：[具体建议]

三、[预判点3]
   [具体分析内容和依据]
   行动建议：[具体建议]
```

#### 3.4 分析原则

- 基于实际数据，不编造
- 给出可执行的行动建议，不泛泛而谈
- 从创作者视角出发，每条洞察都要回答"怎么用"
- 保持专业但易懂，避免术语堆砌

### 4. 询问订阅

分析完成后必须主动询问是否需要订阅。

```
🔔 订阅服务

是否需要订阅每日/每小时热榜推送？

1. 每小时推送 - 实时追踪热点变化（默认推送TOP50完整数据）
2. 每日推送 - 每天早/晚获取一次热榜汇总（默认推送TOP50完整数据）
3. 暂不需要 - 仅本次查询

请回复数字或"取消"，如有其他推送时间偏好请说明。
```

**订阅处理流程**：
- 用户选择1（每小时推送）：记录偏好，后续每小时自动推送TOP50数据
- 用户选择2（每日推送）：询问具体推送时间（早/晚），记录偏好，推送TOP50数据
- 用户选择3或"取消"：结束本次交互，不记录
- 用户有其他偏好：灵活记录并确认

订阅数据默认推送TOP50完整数据；如用户特别要求TOP20，按用户要求执行。

### 5. 生成热榜HTML页面（强制执行）

HTML文件生成是必须执行的强制步骤，不等待用户回复，立即执行。

**执行顺序**：获取数据（保存JSON） → 展示表格 → 创作者洞察 → 询问订阅 → 立即执行HTML生成（从JSON读取）

**关键优化**：HTML生成器通过 `--json-file` 参数直接读取第一步保存的JSON文件，不再重复调用API。确保 API 调用次数始终为 1 次。

**触发场景**：

| 场景 | HTML数据范围 | 文件命名 |
|-----|------------|---------|
| 查询实时热榜 | TOP20（严格20条） | `douyin_hot_YYYYMMDD_HHMM.html` |
| 查询历史热榜 | TOP20（严格20条） | `douyin_hot_YYYYMMDD_YYYYMMDD.html` |
| 用户加载更多 | TOP50（严格50条） | `douyin_hot_top50_YYYYMMDD_HHMM.html` |

**HTML数据展示规则**：
- 默认展示TOP20，仅用户明确要求时展示TOP50
- 数据条数严格控制：TOP20模式20条，TOP50模式50条
- 禁止自动扩展数据范围

**执行流程**（两步，共1次API调用）：

```bash
# 步骤1：获取数据并保存为JSON文件
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/hotspot_fetcher.py > scripts/temp_hot_data.json

# 步骤2：从JSON文件生成HTML（不再调用API）
# 实时热榜（TOP20）
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/gen_douyin_hot_html.py --json-file scripts/temp_hot_data.json --output scripts/douyin_hot_20260529_1000.html

# 加载更多（TOP50）
cd "C:/Users/马祯/.workbuddy/skills/douyin-hot-trend" && python scripts/gen_douyin_hot_html.py --json-file scripts/temp_hot_data.json --top 50 --output scripts/douyin_hot_top50_20260529_1000.html
```

**Agent执行注意事项**：
- 第一步获取数据时，将 `hotspot_fetcher.py` 的 stdout 输出重定向保存到临时JSON文件
- 第二步 HTML 生成时，必须使用 `--json-file` 参数指向临时JSON文件，禁止省略该参数
- 临时 JSON 文件可在 HTML 生成后保留或清理，不影响功能

**文件命名规则**：
- 实时热榜：`douyin_hot_YYYYMMDD_HHMM.html`
- 历史热榜：`douyin_hot_起始日期_结束日期.html`
- 加载更多：`douyin_hot_top50_YYYYMMDD_HHMM.html`

**加载更多场景**：仅输出TOP21-TOP50表格，立即生成新HTML文件（含完整TOP50）。

**HTML输出要求**：
- 必须直接输出完整HTML文件内容（使用代码块展示HTML源码）
- 同时告知文件路径
- 无论实时还是历史查询，都必须输出完整HTML

**HTML 交付与预览流程**（强制执行）：

1. **生成 HTML**：执行 `gen_douyin_hot_html.py` 脚本，确认 stderr 输出 `✅ 已生成` 和 `📊 共 X 条`
2. **尝试预览**：调用 `preview_url` 工具，传入 `file:///C:/Users/马祯/.workbuddy/skills/douyin-hot-trend/scripts/文件名.html`
3. **交付文件**：调用 `deliver_attachments` 工具，将 HTML 文件作为附件交付给用户
4. **预览失败备用方案**：若 `preview_url` 因中文路径或 `file://` 协议限制未能正常渲染，提示用户直接双击打开交付的 HTML 文件。不要反复重试 `preview_url`

**预览注意事项**：
- Windows 中文用户名路径（如 `马祯`）可能导致 `file://` 协议预览失败，这是已知限制
- `deliver_attachments` 交付的文件用户可直接下载并在浏览器中打开，不受路径编码影响
- 优先确保文件交付成功，预览仅作为辅助手段

**PDF输出要求**：
- 必须输出PDF文件
- 生成方式：先生成HTML，再转换为PDF
- PDF内容支持点击跳转到对应话题页面

**数据一致性要求**：
- HTML数据必须完全来自脚本执行的API返回数据
- 禁止修改排名、热度值、话题标题、跳转链接
- 禁止重新排序、美化或编造数据
- HTML中每条数据必须与表格输出完全一致

**HTML统计数据**：
- 话题总数 = 实际展示数据条数（TOP20或TOP50）
- 最高热度 = 所有展示热度值的最大值
- 平均热度 = 所有展示热度值的平均值
- 禁止编造统计数据

### 6. 可选操作

- 用户可点击标题直接跳转到对应热点页面
- 可根据热度值排序或筛选特定话题
- 可随时发送"取消订阅"停止推送

## 资源索引

- 数据获取脚本：`scripts/hotspot_fetcher.py` — 获取抖音热榜JSON数据
- HTML生成脚本：`scripts/gen_douyin_hot_html.py` — 生成热榜可视化HTML页面
- HTML模板文件：`assets/douyin_hot_trend_template.html` — HTML页面模板，支持占位符快速生成

## 模板使用说明

`douyin_hot_trend_template.html` 支持以下占位符：

| 占位符 | 说明 | 示例值 |
|-------|------|-------|
| `{{PAGE_TITLE}}` | 页面标题 | 抖音实时热榜 |
| `{{FETCH_TIME}}` | 获取时间 | 2026-04-17 10:00:00 |
| `{{HOT_LIST_DATA}}` | 热榜数据JSON | `[{...}, {...}]` |

将占位符替换为实际数据即可生成完整HTML页面。

## 注意事项

- API调用需要网络连接
- 热榜数据实时更新，每次调用获取最新数据
- 历史热榜最长查询范围为30天
- 如遇API调用失败，提示用户稍后重试
- 订阅偏好需要用户明确确认后记录
- 分析必须基于实际数据，给出可执行的行动建议
