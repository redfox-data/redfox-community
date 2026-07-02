# 小红书作品分析助手 - 核心工作流程

## Step 0: 鉴权前置检查

执行任何数据采集前，必须先确认 API KEY 已配置：

1. 检查环境变量 `REDFOX_API_KEY` 是否存在
2. 如未配置，引导用户完成鉴权：

> 前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API KEY
>
> 配置方式：
> 1. 在 `~/.openclaw/openclaw.json` 中配置
> 2. 设置环境变量 `REDFOX_API_KEY`
> 3. 使用命令行参数 `--api-key`

3. 鉴权通过后，继续执行后续步骤

## Step 1: 解析用户输入

从用户消息中提取笔记ID，支持以下输入形式：

| 输入形式 | 示例 | 提取方式 |
|----------|------|----------|
| 直接提供ID | `6a23eddb000000003502a39d` | 直接使用（24位十六进制字符串） |
| 标准笔记链接 | `https://www.xiaohongshu.com/explore/{noteId}?...` | 从URL路径中提取24位hex |
| discovery链接 | `https://www.xiaohongshu.com/discovery/item/{noteId}` | 从URL路径中提取24位hex |

**不支持的格式**：短链接（`xhslink.com/...`）——提示用户改用完整链接。

**批量输入**：用户可提供多个笔记ID或链接（逗号分隔），使用 `--batch` 参数逐一查询，结果以 JSON 数组返回，单个失败不影响其余。

若无法提取有效ID，提示用户检查输入格式。

## Step 2: 执行数据采集

### 单篇查询

```bash
python3 "$SKILL_PATH/scripts/fetch_note_detail.py" --note-id {noteId或笔记链接}
```

脚本会自动识别输入格式（链接/ID），读取环境变量 `REDFOX_API_KEY` 完成鉴权，并返回结构化数据。

### 批量查询

```bash
python3 "$SKILL_PATH/scripts/fetch_note_detail.py" --note-id "{id1},{id2},{id3}" --batch
```

每个笔记独立调用接口，结果以 JSON 数组输出；单个失败在数组中标记 `{"noteId": "...", "success": false, "error": "..."}`，不影响其余笔记。

## Step 3: 数据结构化

### 字段映射表

| 字段 | 含义 | 格式化规则 |
|------|------|-----------|
| noteId | 作品ID | 原样展示 |
| noteTitle | 标题 | 原样展示 |
| contentDesc | 正文描述 | 原样展示 |
| coverImage | 封面图 | 作为链接展示 |
| noteType | 作品类型 | `normal`→"图文", `video`→"视频" |
| noteUrl | 作品链接 | 作为链接展示：`[{noteUrl}]({noteUrl})` |
| videoUrl | 视频地址 | 仅视频类型展示 |
| duration | 视频时长 | 原样展示，仅视频类型 |
| thumbCount | 点赞数 | 数字格式化 |
| favoriteCount | 收藏数 | 数字格式化 |
| replyCount | 评论数 | 数字格式化 |
| forwardCount | 分享数 | 数字格式化 |
| releaseTimestamp | 发布时间 | 转换为可读日期格式 |
| authorUid | 作者ID | 原样展示 |
| authorName | 作者昵称 | 作为链接展示：`[{authorName}](https://www.xiaohongshu.com/user/profile/{authorUid})` |
| authorAvatar | 作者头像 | 作为链接展示 |
| ipRegion | IP属地 | 原样展示 |
| lastEditTime | 最后编辑时间 | 转换为可读日期格式 |
| picList | 图片列表 | 展示每张图的 defaultUrl |
| tags | 标签列表 | 空格连接展示 |
| hashTags | 话题标签 | 以 `#标签` 形式展示 |
| interactionEstimated | 互动数据是否为估算值 | `true` 时必须在互动数据区域醒目提示 |

### 脚本自动计算的增强字段

| 字段 | 含义 | 计算/格式化规则 |
|------|------|----------------|
| totalInteraction | 总互动数 | `thumbCount + favoriteCount + replyCount + forwardCount` |
| releaseTimeFormatted | 发布时间（格式化） | Unix时间戳 → `YYYY-MM-DD HH:mm`（CST） |
| lastEditTimeFormatted | 最后编辑时间（格式化） | Unix时间戳 → `YYYY-MM-DD HH:mm`（CST，如有） |
| thumbCountFormatted | 点赞数（格式化） | 数字格式化 |
| favoriteCountFormatted | 收藏数（格式化） | 数字格式化 |
| replyCountFormatted | 评论数（格式化） | 数字格式化 |
| forwardCountFormatted | 分享数（格式化） | 数字格式化 |
| totalInteractionFormatted | 总互动数（格式化） | 数字格式化 |
| noteTypeFormatted | 作品类型（格式化） | `normal`→"图文", `video`→"视频" |

### 数字格式化规则

- < 10000：原数显示（如 `8621`）
- ≥ 10000：以万为单位，保留一位小数（如 `1.2w`）
- ≥ 1亿：以亿为单位，保留一位小数（如 `1.5亿`）

## Step 4: 输出结果

按以下 Markdown 模板展示查询结果：

```markdown
## 📝 笔记详情

**{noteTitle}**

| 属性 | 内容 |
|------|------|
| 类型 | {noteTypeFormatted} |
| 发布时间 | {releaseTimeFormatted} |
| 作者 | [{authorName}](https://www.xiaohongshu.com/user/profile/{authorUid}) |
| 笔记链接 | [{noteUrl}]({noteUrl}) |
| IP属地 | {ipRegion}（如有） |
| 最后编辑 | {lastEditTimeFormatted}（如有） |

### 📊 互动数据

| 👍 点赞 | ⭐ 收藏 | 💬 评论 | 🔄 分享 | 📈 总互动 |
|--------|--------|--------|--------|----------|
| {thumbCountFormatted} | {favoriteCountFormatted} | {replyCountFormatted} | {forwardCountFormatted} | {totalInteractionFormatted} |

> ⚠️ **数据准确性提示**：以上互动数据为平台估算值（`interactionEstimated: true`），实际数据可能存在偏差，仅供趋势参考，不作为精确决策依据。
（仅当 interactionEstimated 为 true 时展示此提示）

### 📄 正文内容

{contentDesc}

### 🏷️ 话题标签

{hashTags以 #标签 形式用空格连接}

### 🏷️ 标签

{tags空格连接展示}（如有）

### 🖼️ 封面图

[![封面图]({coverImage})]({noteUrl})

> 点击上方图片跳转至笔记原文

### 🖼️ 图片列表

{遍历picList，每张图展示defaultUrl作为链接}（如有）

### 🔗 相关链接

- 作者主页：[https://www.xiaohongshu.com/user/profile/{authorUid}](https://www.xiaohongshu.com/user/profile/{authorUid})
- 笔记链接：[{noteUrl}]({noteUrl})
- 封面图：[{coverImage}]({coverImage})
- 作者头像：{authorAvatar}（如有）
- 视频地址：{videoUrl}（仅视频类型时展示此行）
- 视频时长：{duration}（仅视频类型时展示此行）
```

### 作者主页链接拼接规则

使用格式：`https://www.xiaohongshu.com/user/profile/{authorUid}`

## Step 4.5: 封面图下载与视觉分析

在进入内容分析前，需先下载封面图到本地，然后通过 Agent 进行视觉分析。

### 下载封面图

使用 `curl` 或 `wget` 将 `coverImage` 字段的图片下载到本地临时目录：

```bash
curl -o "$SKILL_PATH/scripts/cover_temp.jpg" "{coverImage}"
```

### Agent 视觉分析

使用 GeneralPurpose Agent 读取下载的封面图，按以下维度进行分析：

- **视觉冲击力**：封面图是否在信息流中具有吸引力、能否让用户停下滑动
- **文字叠加**：是否使用了文字标题叠加，文字内容是否清晰、排版是否合理
- **构图与色调**：构图方式（居中/三分法/对角线等）、色调风格是否符合目标受众审美偏好
- **信息传达**：封面图是否能在 1 秒内传达笔记核心主题
- **与标题/正文的关联性**：封面图内容是否与标题和正文主题一致

将 Agent 分析结果作为「🖼️ 封面与视觉吸引力」维度的输入，整合到 Step 5 的作品分析中。

> **降级处理**：若封面图下载失败或 Agent 分析异常，在封面分析维度注明「封面图无法获取，跳过视觉分析」，不影响其余维度。

## Step 5: 作品内容分析

在展示完基础数据后，以**专业资深小红书内容创作者**的视角对作品进行多维度深度分析。

### 分析角色设定

> 你是一个专业资深的小红书内容创作者，你知道怎么将小红书内容做得更高质量、提高作品吸引力与转化力。

### 分析维度

针对获取到的笔记数据，从以下 7 个维度逐一分析：

| 维度 | 分析要点 |
|------|----------|
| 🎯 主题与痛点匹配度 | 内容是否精准命中目标受众的核心痛点；选题是否有明确的用户价值主张；与当前平台热门话题的契合程度 |
| 🔥 爆款成因拆解 | **核心爆点深挖**：拆解笔记的爆款核心机制（如标题反差感、情绪钩子、自我调侃+夸张手法等），分析"内容形式极简但互动极高"背后的真正原因；对比同类赛道内容，说明该笔记凭什么脱颖而出；结论必须锚定具体数据（标题文案、视频时长、正文字数等），禁止泛泛而谈 |
| 🏗️ 信息结构与诱导力 | 正文的逻辑层次是否清晰（是否有钩子开头、干货主体、行动号召）；信息密度是否合理；是否有效制造停留与阅读欲；对于极简内容（如短视频+短文案），分析其"少即是多"的结构策略 |
| 🔍 标题SEO与场景化 | 标题是否包含核心搜索关键词；是否具有场景代入感或情绪钩子；字数与结构是否符合平台推荐算法偏好；**标题反差感/冲突感分析**：拆解标题中的对比、夸张、悬念等手法及其对点击率的贡献 |
| #️⃣ 话题与标签质量 | 话题标签是否覆盖目标流量池（大词+长尾词组合）；标签数量是否合理；是否遗漏重要垂类标签 |
| 📈 互动数据解读 | 点赞/收藏/评论比例是否健康（收藏>点赞说明干货价值高）；评论数相对偏低是否有互动引导缺失；总互动量在同类内容中的竞争力；**时间归一化**：结合发布时间计算日均互动速率，评估内容持续吸引力；**数据可信度**：若 `interactionEstimated: true`，必须在分析开头醒目提示数据为估算值，分析结论需加"趋势性判断"的限定语 |
| 🖼️ 封面与视觉吸引力 | 基于 Step 4.5 的 Agent 视觉分析结果：封面图视觉冲击力评估、文字叠加效果、构图色调与受众审美匹配度、封面与标题/正文的关联性；若封面图无法获取则跳过并注明 |
| 💰 转化潜力推断 | **针对本条内容的特殊性**分析转化路径，禁止给出"可以接XX广告"等泛化结论；必须结合笔记的具体内容形式、受众画像、互动特征，给出该笔记独有的变现切入点或引流路径；评估转化可行性时说明理由 |

### 账号定位背景判断

在正式分析前，需先简要判断该笔记与账号整体定位的关系：

- 基于作者昵称（`authorName`）和笔记内容，推断账号的大致定位方向
- 评估本条笔记是否符合该账号的一贯内容调性，还是属于"破圈尝试"或"偶发爆款"
- 若判断为偶发爆款，需在综合建议中提示创作者：**不要盲目复制此模式**，应结合自身账号定位选择性借鉴

> **注意**：仅凭单条笔记无法完整判断账号定位，此部分为推断性分析，需明确标注判断依据和不确定性。

### 输出格式

```markdown
## 🔍 作品内容分析

> 📌 **账号定位参考**：{账号定位推断与本篇内容关系判断}

### 🎯 主题与痛点匹配度
{分析内容}

### 🔥 爆款成因拆解
{分析内容}

### 🏗️ 信息结构与诱导力
{分析内容}

### 🔍 标题SEO与场景化
{分析内容}

### #️⃣ 话题与标签质量
{分析内容}

### 📈 互动数据解读
{分析内容}

### 🖼️ 封面与视觉吸引力
{分析内容}

### 💰 转化潜力推断
{分析内容}

### ✨ 综合建议
{基于以上分析，给出 2-3 条可操作的优化建议，按影响大→小排序，并标注预期效果}
```

> **注意**：
> - 分析必须基于实际返回的数据字段（contentDesc、hashTags、thumbCount、favoriteCount、replyCount、duration、noteType 等），不做无依据的推测；对于缺失字段，明确指出数据缺失并跳过相关分析
> - 爆款成因拆解必须锚定笔记的具体数据特征（标题文案、视频时长、正文字数、互动量级等），禁止泛泛而谈
> - 转化潜力推断必须针对本条内容的特殊性展开，禁止给出适用于整个赛道的泛化结论
> - 若 `interactionEstimated: true`，互动数据解读维度必须以数据准确性提示开头

## 降级处理逻辑

| 场景 | 错误判断 | 用户提示 |
|------|----------|----------|
| noteId无效 | 提取出的ID不符合24位hex格式 | "笔记ID格式不正确，请检查后重新输入。示例格式：`6a23eddb000000003502a39d`" |
| 笔记不存在 | 接口返回data为空数组 | "该笔记可能已被删除或设为私密，无法获取详情。" |
| 接口异常 | code非2000 | 透传接口返回的msg字段 |
| 短链接不支持 | 输入为xhslink.com短链 | "不支持短链接，请提供完整的小红书笔记链接。" |
| 接口调用失败 | 网络超时、非200响应等 | "网络不稳定，请稍后重试。" |
| 未配置API KEY | 环境变量 `REDFOX_API_KEY` 为空 | 引导用户完成鉴权配置（同Step 0） |
