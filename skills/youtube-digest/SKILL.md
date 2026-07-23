---
name: youtube-digest
description: YouTube 提文案 — 输入 YouTube 视频链接或 ID，一键提取视频文字稿（字幕/口播文案），默认输出不带时间戳的纯文案；字幕中文轨优先、无中文轨回退英文后自动翻译为中文，结果以表格（标题/时长/文案内容）呈现，支持导出 Excel、可选带时间戳版本。当用户需要提取 YouTube 视频文案、把视频转成文字稿、做视频笔记/总结/翻译/二次创作时使用。
---

# YouTube 提文案

输入 YouTube 视频链接，一键提取视频文字稿（口播文案），终端展示 + Markdown 存档 + 可导出 Excel。

**支持的链接格式（视频链接必须包含视频 ID）：**

- 完整URL：`https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- 短URL：`https://youtu.be/dQw4w9WgXcQ`
- 视频ID：`dQw4w9WgXcQ`

**默认行为（重要）：**

- 默认输出**不带时间戳**的纯文案；需要带时间戳版本时加 `--timestamp`
- 字幕按 `zh,en,asr` 优先级选轨：**视频有中文字幕轨时直接输出中文**；没有中文轨时回退英文，**脚本自动将非中文字幕翻译为中文**（基于 Google Translate，批量翻译提升效率）；加 `--no-translate` 可禁用自动翻译、保留原文
- 默认自动获取视频元数据（标题/频道），无需额外参数

> 需先配置 API Key，通过环境变量 REDFOX_API_KEY 或 --api-key 参数传入。
> 文字稿来源：视频字幕轨（手动字幕 + 自动生成字幕 asr），按语言优先级选轨、中文轨优先；非中文字幕由脚本端自动翻译为中文。

---

## 使用场景

当你需要执行以下任务时，应优先使用本技能：

| 场景 | 示例 |
|------|------|
| **视频转文字稿** | 丢一个 YouTube 链接，拿到完整口播文案 |
| **学习笔记整理** | 提取教程/演讲文案后让 AI 总结成章节笔记 |
| **内容二次创作** | 提取英文视频文案 → AI 翻译改写 → 公众号文章 |
| **播客/访谈存档** | 提取访谈全文，导出 Excel 归档 |
| **竞品内容分析** | 批量提取同行视频文案，分析话术与结构 |
| **视频选题调研** | 先提文案再快速判断视频是否值得深看 |

---

## 使用方法

```bash
# 基础提取（默认：不带时间戳 + 自动获取标题等元数据）
python3 "$SKILL_PATH/scripts/extract.py" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 支持短链和纯视频 ID
python3 "$SKILL_PATH/scripts/extract.py" "https://youtu.be/dQw4w9WgXcQ"
python3 "$SKILL_PATH/scripts/extract.py" "dQw4w9WgXcQ"

# 带时间戳版本（方便定位原片进度）
python3 "$SKILL_PATH/scripts/extract.py" "URL" --timestamp

# 同时导出 Excel（标题/时长/视频链接/文案内容 四列）
python3 "$SKILL_PATH/scripts/extract.py" "URL" --excel

# 带时间戳文案 + 导出 Excel（Excel 内容与当前模式一致）
python3 "$SKILL_PATH/scripts/extract.py" "URL" --timestamp --excel

# 指定语言优先级（如只要英文字幕）
python3 "$SKILL_PATH/scripts/extract.py" "URL" --language "en"

# 输出原始 JSON / 不保存文件 / 不获取元数据
python3 "$SKILL_PATH/scripts/extract.py" "URL" --json
python3 "$SKILL_PATH/scripts/extract.py" "URL" --no-save
python3 "$SKILL_PATH/scripts/extract.py" "URL" --no-metadata
```

终端输出：视频概要（标题/语言/片段数/总时长）+ 纯文案全文。

Markdown 存档默认保存在 `~/Downloads/QoderYoutubeDigest/`，文件名 `{视频ID}_{时间戳}.md`，含视频信息头表 + 全文；Excel（.xlsx）同目录。

---

## 工作流程（AI 必须遵循）

1. **提取**：运行脚本获取文案
2. **表格展示**：按「返回结果展示规范」用表格呈现（标题/时长/文案内容），文案内容列展示**中文译文全文**（无时间戳；非中文字幕已自动翻译）
3. **收尾询问**：展示结束后，**必须主动询问用户**：
   > 「需要带时间戳的文案版本吗（方便定位原片进度）？也可以为你导出 Excel。」
   - 用户要带时间戳 → 加 `--timestamp` 重跑并展示
   - 用户要 Excel → 加 `--excel` 重跑（如需时间戳一并加 `--timestamp`），给出文件路径

> 注意：脚本默认自动将非中文字幕翻译为中文。如用户明确要求保留原文，加 `--no-translate` 重跑。

---

## 返回结果展示规范

向用户展示提取结果时，**必须**使用以下表格，不得省略字段：

| 序号 | 字段 | 说明 |
|------|------|------|
| 1 | 标题 | 视频标题（来自元数据） |
| 2 | 时长 | 格式 `MM:SS` 或 `HH:MM:SS` |
| 3 | 文案内容 | **不带时间戳**的文案全文，非中文字幕已自动翻译为中文 |

**展示示例：**

```
| 标题 | 时长 | 文案内容 |
|------|------|----------|
| Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster) | 03:31 | 我们对爱情并不陌生 / 你知道规则，我也一样 / ……（中文译文全文） |
```

- 文案内容列：多段落文案在单元格内用「/」或换行衔接，保持完整不截断；非中文字幕已自动翻译为中文展示
- 表格后附一行存档信息：`已存档：~/Downloads/QoderYoutubeDigest/dQw4w9WgXcQ_xxx.md`

---

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `video_url` | YouTube 视频链接（完整URL/短URL/视频ID，必须含视频 ID，必填位置参数） | — |
| `--language` | 字幕语言优先级，逗号分隔（中文轨优先，`asr` 为自动生成字幕兜底；仅选轨不翻译） | `zh,en,asr` |
| `--timestamp` | 输出带 `[MM:SS]` 时间戳的文案 | 默认**不带**时间戳 |
| `--excel` | 同时导出 Excel（.xlsx，四列：标题/时长/视频链接/文案内容） | 不导出 |
| `--no-metadata` | 不获取视频元数据 | 默认获取（标题/频道） |
| `--json` | 终端输出原始 JSON 响应 | — |
| `--no-save` | 不保存 Markdown 文件 | 自动保存 |
| `--output-dir` | 输出目录 | `~/Downloads/QoderYoutubeDigest` |
| `--no-translate` | 禁用自动翻译，保留字幕原文输出 | 默认**自动翻译**非中文字幕为中文 |
| `--api-key` | 指定 RedFox API Key | — |

---

## API Key 配置

任选一种方式配置个人 Key：

| 方式 | 命令 |
|------|------|
| 环境变量（推荐） | `export REDFOX_API_KEY=ak_你的密钥` |
| 命令行参数 | `--api-key ak_你的密钥` |
| 配置文件 | `echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

注册地址：[redfox.hk](https://redfox.hk/settings/api-keys?source=github)

---

## 功能特点

- **三种输入格式**：完整 URL、`youtu.be` 短链、纯视频 ID，自动识别
- **默认纯文案**：不带时间戳，直接可读、可直接喂给 AI 二次加工；`--timestamp` 随时切换
- **自动翻译**：非中文字幕自动翻译为中文（基于 Google Translate），加 `--no-translate` 可保留原文
- **表格化交付**：标题/时长/文案内容三字段表格呈现，信息一目了然
- **Excel 导出**：`--excel` 一键导出 xlsx（自动换行、列宽适配），适合归档与分享
- **中文轨优先**：按 `zh,en,asr` 优先级选轨，有中文字幕直接输出中文；没有则回退英文轨并自动翻译为中文
- **稳健重试**：网络异常/状态码错误/数据为空自动递增延迟重试（0.5s→1.0s），限频（3108）自动等待 5 秒重试
- **AI 友好**：可衔接总结、翻译、改写、公众号排版发布等后续技能

---

## 依赖

```bash
pip3 install requests openpyxl deep-translator
```

（`openpyxl` 仅 Excel 导出需要；`deep-translator` 仅自动翻译需要；未安装时对应功能自动降级，其余功能不受影响）

---

## 常见问题

**Q：默认文案带时间戳吗？**
A：不带。默认输出纯文案；加 `--timestamp` 才输出 `[MM:SS]` 时间戳版本，提取结束后 AI 也会主动询问是否需要。

**Q：英文视频能直接给我中文文案吗？**
A：可以。脚本检测到非中文字幕时会自动翻译为中文（基于 Google Translate）。视频有中文轨时直接输出中文，没有中文轨时回退英文后自动翻译。如需保留原文，加 `--no-translate`。

**Q：Excel 里是什么内容？**
A：四列——标题、时长、视频链接、文案内容。文案内容与当前模式一致：加 `--timestamp` 时 Excel 内含时间戳，否则为纯文案。

**Q：为什么提取失败提示"视频可能无字幕"？**
A：文字稿来自视频字幕轨。完全无字幕（含自动生成字幕）的视频无法提取；部分受限/私享视频也不支持。

**Q：链接报错了怎么办？**
A：链接无效返回 `Invalid YouTube URL or video ID`（积分不扣除），请检查链接是否包含正确的视频 ID；Key 无效（3106/3107）请检查 API Key 配置；限频（3108）会自动等待重试。

**Q：拿到文案后能做什么？**
A：可以让 AI 直接总结成笔记、翻译成中文、改写成公众号文章（配合 gzh-design 排版、md-to-wechat 一键推送草稿）。

**Q：额度用完怎么办？**
A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 Token。
