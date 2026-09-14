---
name: image-gen
description: AI 图片生成器 — 基于 gpt-image-2 模型，支持文生图与图生图，开箱即用。
---

# GPT-image2

调用 OpenAI 最新的 **gpt-image-2** 模型生成高质量图片。粘贴提示词就能用。

> **Skill 特色**
>
> - 支持命令行批量生成、参数化控制宽高比与分辨率档位
> - 文生图 + 图生图双模式，`--image` 一个参数启用编辑模式（最多 2 张参考图）

---

## 能力概述

- **文生图**：输入提示词，生成全新图片
- **图生图**：上传参考图（最多 2 张） + 提示词，基于原图编辑生成
- **模型**：gpt-image-2（OpenAI 最新图像模型）
- **接口**：红狐新版 `gptImage2Submit` / `gptImage2Result`
- **输出格式**：PNG（新接口固定输出）
- **宽高比**：`1:1` / `3:2` / `2:3` / `4:3` / `3:4` / `5:4` / `4:5` / `16:9`（默认） / `9:16` / `2:1` / `1:2` / `21:9` / `9:21`
- **分辨率档位**：`1k` / `2k`（默认） / `4k`
- **批量生成**：单次最多 4 张（新接口上限）
- **兼容旧像素格式**：仍接受 `1792x1024` 等旧写法，脚本内部自动映射到宽高比 + 档位

---

## 使用方式

### 文生图 — 输入文字生成图片

```bash
# 基本生成（默认 16:9 + 2k）
python3 "$SKILL_PATH/assets/imagegen.py" "一只橘色的猫咪坐在窗台上看着窗外的夕阳"

# 横版 4k 高清
python3 "$SKILL_PATH/assets/imagegen.py" "futuristic city skyline" --size 16:9 --resolution 4k

# 竖版小红书封面（3:4 + 2k）
python3 "$SKILL_PATH/assets/imagegen.py" "product cover, minimal style" --size 3:4 --resolution 2k

# 方形 1k 快速档
python3 "$SKILL_PATH/assets/imagegen.py" "minimalist cat logo, flat design" --size 1:1 --resolution 1k

# 批量生成 4 张（新接口上限）
python3 "$SKILL_PATH/assets/imagegen.py" "icon set, flat style" -n 4

# 兼容旧像素写法（自动映射为 16:9 + 1k）
python3 "$SKILL_PATH/assets/imagegen.py" "cyberpunk street" --size 1792x1024
```

### 图生图 — 上传参考图编辑生成

```bash
# 单张参考图（自动上传 OSS → 提交任务）
python3 "$SKILL_PATH/assets/imagegen.py" "把猫咪改成白色，背景换成星空" --image ~/Pictures/cat.png

# 两张参考图（新接口最多支持 2 张）
python3 "$SKILL_PATH/assets/imagegen.py" "融合两张图的风格" --image ref1.png --image ref2.jpg

# 直接使用 URL 参考图（跳过上传步骤）
python3 "$SKILL_PATH/assets/imagegen.py" "把海报主体换成手表" --image "https://example.com/poster.jpg"
```

### 其他操作

```bash
# 仅提交任务（返回 taskId，不等待）
python3 "$SKILL_PATH/assets/imagegen.py" "complex scene" --no-download

# 查询已有任务结果
python3 "$SKILL_PATH/assets/imagegen.py" "" --task-id 5f100fcb8f3c4e3087c6aba93e121f7e

# 指定输出目录和文件名前缀
python3 "$SKILL_PATH/assets/imagegen.py" "illustration" -o ~/Pictures/AI --prefix artwork
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 生成/编辑提示词（必填，最多 500 字） | - |
| `--size` | 宽高比（如 `16:9`）；也兼容旧像素格式（如 `1792x1024`） | `16:9` |
| `--resolution` | 分辨率档位：`1k` / `2k` / `4k` | 像素格式自动匹配；宽高比默认 `2k` |
| `-n, --count` | 生成数量（1-4，新接口上限 4） | `1` |
| `--image` | 参考图路径或 URL（可多次传入，最多 2 张） | - |
| `-o, --output-dir` | 输出目录 | `~/Downloads/QoderImages` |
| `--prefix` | 文件名前缀 | `image` |
| `--no-download` | 仅提交不等待 | - |
| `--task-id` | 查询已有任务 | - |
| `--api-key` | 指定 API Key | - |

**已弃用参数（新接口不再支持，传入会被忽略并给出提示）**

| 参数 | 说明 |
|------|------|
| `--quality` | 用 `--resolution` 代替 |
| `--format` | 新接口固定输出 PNG |
| `--bg` / `--background` | 新接口不再支持背景控制 |
| `--compression` | 新接口不再支持压缩比 |
| `--fidelity` | 新接口不再支持保真度控制 |

### 依赖安装

| 依赖 | 安装命令 |
|------|----------|
| `requests` | `pip3 install requests` |

---

## 首次使用

先配置 API Key，然后运行：

```bash
# 设置环境变量
export REDFOX_API_KEY=ak_你的密钥

# 运行
python3 "$SKILL_PATH/assets/imagegen.py" "一只橘色的猫咪"
```

> 前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 API Key。
>
> ⚠️ 新接口仅支持**付费调用**，账户免费积分无法抵扣本接口。若返回错误码 `3203`，请前往 [充值页面](https://redfox.hk/dashboard/recharge) 补充付费积分。

---

## 后续使用

前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册账号获取自己的 API Token，三种配置方式任选其一：

| 配置方式 | 说明 | 命令 |
|----------|------|------|
| **环境变量**（推荐） | 设置一次，全局生效 | `export REDFOX_API_KEY=ak_你的密钥` |
| **命令行参数** | 临时使用，单次生效 | `python3 "$SKILL_PATH/assets/imagegen.py" "prompt" --api-key ak_你的密钥` |
| **配置文件** | 持久化存储，跨会话保留 | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 接口规格（新）

### 提交任务

`POST https://redfox.hk/story/api/parseWork/imageGen/gptImage2Submit`

请求头：`REDFOX_API_KEY: ak_xxx` + `Content-Type: application/json`

请求体：

```json
{
  "prompt": "把这个海报的主体变为手表 并把文字都用中文",
  "resolution": "2k",
  "size": "16:9",
  "n": 2,
  "referenceImages": ["https://example.com/poster.jpg"]
}
```

响应：`data.taskId` 用于后续轮询。

### 查询结果

`POST https://redfox.hk/story/api/parseWork/imageGen/gptImage2Result`

请求体：`{"taskId": "..."}`

响应关键字段：

| 字段 | 说明 |
|------|------|
| `data.status` | `completed` / `processing` / `queued` / `failed` |
| `data.progress` | 生成进度 0-100 |
| `data.imageUrls` | 生成结果 URL 数组（数量与 `n` 一致） |
| `data.failReason` | 失败原因（成功时为 null） |
| `data.model` | 使用的模型（`gpt-image-2`） |
| `data.resolution` / `data.size` | 实际使用的档位与宽高比 |

---

## 常见问题

**Q：本 Skill 的特点是什么？**
A：命令行直接调用 gpt-image-2 模型，支持批量生成、宽高比与分辨率档位控制、图生图（最多 2 张参考图）。

**Q：生成一张图片需要多久？**
A：通常 10-60 秒，`4k` 档位或复杂场景可能更久。脚本会自动轮询等待并展示 progress。

**Q：新的 `resolution` 与旧的 `quality` 有什么区别？**
A：`resolution` 是分辨率档位（`1k`/`2k`/`4k`），直接决定输出图像的清晰度与生成耗时；旧的 `quality` 参数已弃用，传入会被忽略。

**Q：为什么 `--size` 从像素改成了宽高比？**
A：新接口 `gptImage2Submit` 的 `size` 字段就是宽高比（如 `16:9`）。为兼容旧调用，脚本仍接受 `1792x1024` 等像素写法，内部自动映射到宽高比 + 推荐档位。

**Q：图生图能传几张参考图？**
A：新接口最多 2 张。多次传入 `--image` 即可，超出部分会被截断并提示。

**Q：为什么调用返回错误码 3203？**
A：新接口仅支持付费调用，账户免费积分不可抵扣。请前往 [redfox.hk/dashboard/recharge](https://redfox.hk/dashboard/recharge) 充值付费积分。

**Q：如何获取 API Key？**
A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取自己的 API Token。

**Q：支持哪些图片格式作为参考图？**
A：支持 PNG、JPEG、WebP 格式的本地文件或 HTTP(S) URL。

**Q：提示词有长度限制吗？**
A：提示词最多支持 500 字，超过会被阻断并提示精简。
