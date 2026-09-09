---
name: pdf-image-text-extractor
slug: pdf-image-text-extractor
version: 2.1.0
displayName: PDF和图片文字提取
description: 从图片或 PDF 文档中识别并提取文字内容，支持多种图片格式和 PDF 文件，自动判断是否包含文字并保留原始格式输出结构化结果；v2.1 采用零额外依赖方案：扫描版 PDF 自动渲染为图片交由 AI 视觉识别（无需 tesseract/rapidocr）、表格用 pymupdf 内置 find_tables 结构化提取（无需 pdfplumber）、批量处理目录（PDF+图片一次性提取）；当用户需要从图片或 PDF 提取文字、进行 OCR 识别、处理含文字的文档、提取 PDF 表格、批量处理文件夹或转换为可编辑文本时使用。该skill能力来自RedFoxHub，官网：https://redfox.hk/skills。
dependency:
  python:
    - pymupdf>=1.23.0
    - requests>=2.28.0
---

# PDF和图片文字提取

## 任务目标

- 本 Skill 用于：从用户上传的图片或 PDF 文档中识别并提取文字内容
- 能力包含：图片文字检测、PDF 文字提取、**扫描版 OCR 识别**、**表格结构化提取**、**批量目录处理**、格式保留、Markdown 文件生成
- 触发条件：用户上传图片或 PDF 并要求提取文字，或询问文档中的文字内容；用户需要批量处理文件夹；用户需要提取 PDF 中的表格数据

## 🔑 鉴权

本 Skill **完全免费**，但需配置红狐 API Key 请求使用权限，Key 本身不扣积分。

前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 注册获取个人 API Key，通过以下任一方式配置：

```bash
# 方式一：配置文件（如 OpenClaw 的 ~/.openclaw/openclaw.json）
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }

# 方式二：终端环境变量
export REDFOX_API_KEY="ak_xxxx..."
```

> ⚠️ **每次执行任何操作前，必须先运行 `python3 scripts/record.py`**。
> 若脚本以非零退出码终止（未配置 Key 或接口返回失败），则**立即停止执行**，并向用户提示：
> 「需要配置红狐 API Key 才能使用本 Skill。请前往 https://redfox.hk/settings/api-keys?source=github **免费**注册获取，然后配置环境变量：`export REDFOX_API_KEY="ak_xxxx..."`」

## 前置准备

### 必要依赖

```
pymupdf>=1.23.0
requests>=2.28.0
```

```bash
pip install pymupdf>=1.23.0 requests>=2.28.0
```

### 零额外依赖说明

本 Skill **无需安装任何 OCR 引擎或表格库**：
- 扫描版 PDF：自动渲染为高清 PNG，交由 Agent 的 `read_image`（AI 视觉）识别
- 表格提取：使用 pymupdf 内置 `find_tables()`，无需 pdfplumber
- 仅需 `pymupdf` + `requests` 两个包即可启用全部功能

### 支持的文件格式

- 图片格式：PNG、JPG、JPEG、GIF、WebP、BMP、TIFF
- 文档格式：PDF（文字版 + 扫描版，扫描版自动渲染为图片由 AI 识别）

## 操作步骤

### 标准流程

#### Step 0：鉴权检查（必须首先执行）

```bash
python3 scripts/record.py
```

- 输出 `✅ 鉴权通过，已获得使用权限` → 继续后续流程
- 脚本以非零退出码终止 → **立即停止**，向用户展示脚本输出的错误提示，告知需前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 免费获取 API Key

#### Step 0.5：版本更新提示（每次执行）

```bash
python3 scripts/changelog.py
```

- 若有输出（首次使用或版本升级）→ 将输出内容**完整展示给用户**，然后继续
- 若无输出（版本已是最新）→ 直接继续

#### 图片文字提取流程

1. **接收图片**
   - 确认用户已上传图片文件
   - 获取图片的访问 URL

2. **识别图片内容（第一轮：全局识别）**
   - 使用 `read_image` 工具识别图片内容
   - 在 prompt 中明确要求识别所有文字内容，包括标题、正文、注释、水印等
   - 对数字字符需特别注意视觉形状特征（封闭圆圈数、开口方向、弧线走向），确保 6/8/9/0/3 等易混淆数字准确识别

3. **判断文字存在性**
   - 如果检测到文字：进入步骤 4
   - 如果未检测到文字：告知用户"图片中未包含可提取的文字"，任务结束

4. **提取并整理文字**
   - 提取图片中的所有文字内容
   - 保持原有的结构和排版
   - 整理为易读的格式

5. **数字二次聚焦校验（静默执行，不展示给用户）**
   - ⚠️ **重要**：整个校验过程（包括形状描述、对比表格、校验轮次等）必须静默执行，禁止在对话输出中展示任何校验过程，只向用户展示最终确认的提取结果
   - 对第一轮提取结果中的所有数字串（手机号、订单号、金额、日期等），执行二次聚焦识别：
   - **策略 A：局部放大验证**
     - 再次使用 `read_image`，但这次在 prompt 中只要求识别特定数字串区域
     - prompt 模板：「请只关注图片中的数字串 [上下文描述]，逐位描述每个数字字符的视觉形状（有几个封闭圆圈、开口方向、弧线走向），然后给出最终判断结果」
   - **策略 B：交叉验证**
     - 将第一轮的形状描述与第二轮的独立判断进行对比
     - 如果两轮结果一致 → 确认为最终结果
     - 如果两轮结果不一致 → 标注 `[待确认：第一轮识别为X，第二轮识别为Y]`
   - **易混淆数字对速查表**：
     | 数字 | 关键视觉特征 |
     |------|-------------|
     | **8** | 上下两个封闭圆圈，像雪人/沙漏 |
     | **6** | 仅下方一个封闭圆圈，顶部向左弯弧 |
     | **9** | 仅上方一个封闭圆圈，底部向下竖线 |
     | **0** | 完整封闭椭圆，无开口 |
     | **3** | 右侧开口，两个弧形朝右 |
     | **5** | 顶部横线+左侧竖线+下方圆弧 |
     | **S** | 类似5但上下对称，无横线 |
     | **O** | 比0更圆的封闭图形 |

#### PDF 文字提取流程

1. **接收 PDF 文件**
   - 确认用户已上传 PDF 文件
   - 获取 PDF 文件的本地路径

2. **调用脚本提取文字**

   ```bash
   # 标准模式（自动检测扫描页渲染为图片 + 提取表格）
   python3 scripts/pdf_text_extractor.py <pdf_file_path>

   # 仅提取文字，跳过表格（速度更快）
   python3 scripts/pdf_text_extractor.py <pdf_file_path> --no-tables

   # 不渲染扫描页（仅提示哪些页是扫描页）
   python3 scripts/pdf_text_extractor.py <pdf_file_path> --no-render

   # 自定义扫描页图片输出目录 / 渲染分辨率
   python3 scripts/pdf_text_extractor.py <pdf_file_path> --scan-dir ./ocr_pages --dpi 300
   ```

3. **处理提取结果**

   脚本返回 JSON，关键字段说明：

   | 字段 | 说明 |
   |------|------|
   | `success` | 是否提取成功 |
   | `text` | Markdown 格式正文（文字层） |
   | `page_count` | 总页数 |
   | `tables_markdown` | 所有表格的 Markdown 汇总 |
   | `ocr_images` | 需 Agent `read_image` 识别的图片清单 `[{'page','image'}]` |
   | `warnings` | 非致命警告（如扫描页提示等） |

   - 如果 `success=true`：进入步骤 4
   - 如果 `success=false`：告知用户 `error` 字段内容，任务结束

4. **格式化输出**
   - 展示 `text` 字段内容
   - 若 `tables_markdown` 非空，单独展示表格内容
   - 若 `ocr_images` 非空：逐张用 `read_image` 识别这些图片，把识别结果并入正文，并告知用户哪些页是扫描页
   - 若 `warnings` 非空，向用户展示警告信息

#### 批量处理流程

当用户提供目录路径，或要求批量处理多个文件时：

1. **确认目录路径**
   - 获取用户指定的目录路径

2. **调用批量提取脚本**

   ```bash
   # 输出合并 Markdown 到终端
   python3 scripts/batch_extractor.py <目录路径>

   # 保存到文件
   python3 scripts/batch_extractor.py <目录路径> -o result.md

   # 输出 JSON 结构化数据
   python3 scripts/batch_extractor.py <目录路径> --json

   # 不渲染扫描页 / 自定义扫描页输出目录
   python3 scripts/batch_extractor.py <目录路径> --no-render --scan-dir ./ocr_pages
   ```

3. **处理结果**
   - 脚本在 stderr 输出进度信息，在 stdout 输出结果
   - 若指定了 `-o`，告知用户文件保存位置
   - 展示汇总统计（总文件数 / 成功数 / 失败数）
   - 若用户要求查看内容，展示 `combined_markdown` 或各文件提取结果

### 统一输出步骤

5. **生成输出结果**
   - 根据用户需求生成 Markdown 文件
   - 包含文件来源、提取状态、文字内容等信息
   - 使用清晰的标题和结构组织内容

### 可选分支

- 当用户仅需查看文字内容：直接输出文字，不生成文件
- 当用户要求保存结果：生成 `.md` 文件
- 当图片/PDF 文字模糊或难以识别：说明情况并提供最佳识别结果
- 当 PDF 为扫描版：脚本已自动渲染为图片，Agent 用 `read_image` 逐张识别即可，无需任何 OCR 依赖
- 当用户要求提取表格：使用标准模式（默认已包含表格提取），展示 `tables_markdown` 字段
- 当用户要求批量处理：使用 `batch_extractor.py`，支持 PDF + 图片混合目录

## 资源索引

- **鉴权脚本**：[scripts/record.py](scripts/record.py)
  - 用途：调用 `https://redfox.hk/story/api/skill/record/save` 请求使用权限，同时完成鉴权校验
  - 失败行为：未配置 Key 或接口返回 3106/3107 时以退出码 1 终止
- **版本提示脚本**：[scripts/changelog.py](scripts/changelog.py)
  - 用途：首次使用或版本升级时展示新功能介绍，版本一致时静默退出
  - 版本记录文件：`~/.pdf_image_extractor_version`
- **PDF 提取脚本**：[scripts/pdf_text_extractor.py](scripts/pdf_text_extractor.py)
  - 用途：从 PDF 提取文字 + 表格结构化提取 + 扫描页渲染为图片（供 read_image）
  - 参数：`<pdf_path> [--no-tables] [--no-render] [--scan-dir DIR] [--threshold N] [--dpi N]`
  - 输出：JSON，含 `text` / `tables_markdown` / `ocr_images` / `warnings` 等字段
- **批量提取脚本**：[scripts/batch_extractor.py](scripts/batch_extractor.py)
  - 用途：批量处理目录下所有 PDF + 图片文件
  - 参数：`<目录路径> [--no-tables] [--no-render] [--scan-dir DIR] [-o FILE] [--json]`
  - 输出：合并 Markdown 报告或 JSON 结构化数据

## 注意事项

### 图片文字提取
- **识别准确性**：文字识别结果受图片清晰度、字体、背景等因素影响，可能存在误差
- **「先看形状再判数字」原则**：识别数字时必须先描述字符的视觉形状特征（封闭圆圈数、开口方向、弧线走向），再根据特征判断数字，禁止跳过形状描述直接输出数字
- **关键数字串双重识别**：手机号、身份证号、银行卡号、订单号等关键数字串，必须执行两轮识别（全局识别 + 聚焦校验），两轮不一致时标注待确认
- **校验过程静默执行**：数字二次校验的形状描述、对比表格、轮次记录等过程信息严禁展示给用户，只在后台静默执行，最终仅输出确认后的提取结果
- **存疑标注**：对无法100%确认的字符，使用 `[?]` 标注并给出 2 个备选，如 `158****8[?可能为6]624`
- **文字排版**：提取时尽量保持原图的文字结构和顺序
- **多语言支持**：支持识别中文、英文等多种语言文字

### PDF 文字提取
- **格式保留**：脚本会尽量保留原文的段落结构和标题层级
- **扫描版 PDF**：自动检测文字层稀少的页面（< 20 字符）并渲染为高清 PNG，交由 `read_image`（AI 视觉）识别，无需任何 OCR 引擎；识别准确性取决于 AI 视觉能力
- **表格提取**：默认开启，用 pymupdf `find_tables()` 识别表格并输出 Markdown 格式；复杂表格（合并单元格、嵌套表格）识别效果可能不佳
- **加密 PDF**：不支持加密或受密码保护的 PDF 文件

### 批量处理
- **文件排序**：按文件名字母序处理
- **图片识别**：批量模式下图片不做本地 OCR，统一汇入 `ocr_images` 清单，由 Agent 逐张调用 `read_image` 识别
- **大目录**：建议每次处理不超过 100 个文件，过多文件可能导致处理时间较长
- **输出方式**：默认输出到终端，建议指定 `-o result.md` 保存为文件

### 通用注意事项
- **隐私保护**：处理的文件不会被存储，仅在当前会话中使用
- **文件大小**：建议处理小于 50MB 的文件，过大文件可能导致处理缓慢

## 使用示例

### 示例 1：图片文字提取

**用户操作**：上传一张包含文字的图片

**智能体处理**：
1. 执行 `python3 scripts/record.py` → `✅ 鉴权通过`
2. 执行 `python3 scripts/changelog.py` → 若有输出展示给用户
3. 使用 `read_image` 工具识别图片
4. 提取文字内容："所有经历的纠缠 / 还有难过的遗憾 / 都不可能没有意义"
5. 直接输出提取结果

### 示例 2：PDF 文字提取 + 表格

**用户操作**：上传 PDF 并要求"提取这个 PDF 的文字"

**智能体处理**：
1. 执行 `python3 scripts/record.py` → 鉴权通过
2. 执行 `python3 scripts/changelog.py` → 静默
3. 执行：`python3 scripts/pdf_text_extractor.py ./document.pdf`
4. 获取 JSON 结果：`text`（正文）+ `tables_markdown`（表格）
5. 分别展示正文和表格内容，生成 `./extracted_from_pdf.md`

### 示例 3：扫描版 PDF（渲染 + AI 识别）

**用户操作**：上传扫描版 PDF

**智能体处理**：
1. 鉴权 + 版本检查
2. 执行：`python3 scripts/pdf_text_extractor.py ./scan.pdf`
3. 脚本检测文字层为空的页面，渲染为高清 PNG，`ocr_images` 给出图片路径
4. Agent 逐张用 `read_image` 识别这些 PNG，提取文字
5. 告知用户："第 1/2/3 页为扫描页，已通过 AI 视觉识别"，展示提取结果

### 示例 4：批量处理目录

**用户操作**："帮我提取 ./documents/ 文件夹里所有文件的文字"

**智能体处理**：
1. 鉴权 + 版本检查
2. 执行：`python3 scripts/batch_extractor.py ./documents/ -o batch_result.md`
3. 脚本处理目录下所有 PDF + 图片，stderr 输出进度
4. 告知用户："已处理 8 个文件（7 个成功 / 1 个失败），结果已保存至 batch_result.md"
5. 展示汇总统计

### 示例 5：未配置 API Key 时的处理

**用户操作**：上传图片要求提取文字，但未配置 `REDFOX_API_KEY`

**智能体处理**：
1. 执行 `python3 scripts/record.py` → 脚本报错退出
2. **立即停止**，向用户输出：「需要配置红狐 API Key 才能使用本 Skill。请前往 https://redfox.hk/settings/api-keys?source=github **免费**注册获取，然后执行：`export REDFOX_API_KEY="ak_xxxx..."`」
