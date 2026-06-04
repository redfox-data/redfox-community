---
name: image-gen
description: AI 图片生成器 — 基于 gpt-image-2 模型，支持文生图与图生图，内置免费额度，开箱即用。
---

# GPT - image2

调用 OpenAI 最新的 **gpt-image-2** 模型生成高质量图片。内置免费额度，粘贴提示词就能用。

> **Skill 特色**
>
> - 内置公共 API Key，开箱即用，约 **10000 次免费额度**
> - 无需额外订阅或绑定信用卡
> - 支持命令行批量生成、参数化控制尺寸/格式/背景
> - 文生图 + 图生图双模式，`--image` 一个参数启用编辑模式
> - 用完额度后可前往 [redfox.hk/login](https://www.redfox.hk/login) 注册获取免费 Token 继续使用

---

## 能力概述

- **文生图**：输入提示词，生成全新图片
- **图生图**：上传参考图 + 提示词，基于原图编辑生成
- **模型**：gpt-image-2（OpenAI 最新图像模型）
- **输出格式**：PNG、JPEG、WebP
- **尺寸支持**：1024x1024、1024x1792、1792x1024 及 `auto`
- **批量生成**：单次最多 10 张
- **透明背景**：支持 PNG/WebP 透明背景输出
- **保真控制**：图生图支持 high/low 保真度

---

## 使用方式

### 文生图 — 输入文字生成图片

```bash
# 基本生成
python3 "$SKILL_PATH/assets/imagegen.py" "一只橘色的猫咪坐在窗台上看着窗外的夕阳"

# 横版高清
python3 "$SKILL_PATH/assets/imagegen.py" "futuristic city skyline" --size 1792x1024

# 透明背景 logo
python3 "$SKILL_PATH/assets/imagegen.py" "minimalist cat logo, flat design" --bg transparent --format png

# 批量生成 4 张
python3 "$SKILL_PATH/assets/imagegen.py" "icon set, flat style" -n 4 --bg transparent

# WebP + 压缩
python3 "$SKILL_PATH/assets/imagegen.py" "product photo on white background" --format webp --compression 50
```

### 图生图 — 上传参考图编辑生成

```bash
# 基于参考图修改（自动上传图片 → 编辑生成）
python3 "$SKILL_PATH/assets/imagegen.py" "把猫咪改成白色，背景换成星空" --image ~/Pictures/cat.png

# 风格迁移，高保真
python3 "$SKILL_PATH/assets/imagegen.py" "改成赛博朋克风格" --image ref.jpg --fidelity high

# 低保真，大幅改动
python3 "$SKILL_PATH/assets/imagegen.py" "变成水彩画风格，加入樱花元素" --image photo.png --fidelity low
```

### 其他操作

```bash
# 仅提交任务（返回 taskId，不等待）
python3 "$SKILL_PATH/assets/imagegen.py" "complex scene" --no-download

# 查询已有任务结果
python3 "$SKILL_PATH/assets/imagegen.py" "" --task-id sfwmpic7xxxxxxxx

# 指定输出目录和文件名前缀
python3 "$SKILL_PATH/assets/imagegen.py" "illustration" -o ~/Pictures/AI --prefix artwork
```

### 参数说明

| 参数               | 说明                                     | 默认值                    |
| ------------------ | ---------------------------------------- | ------------------------- |
| `prompt`           | 生成/编辑提示词（必填）                  | -                         |
| `--image`          | 参考图路径（启用图生图模式）             | -                         |
| `--fidelity`       | 图生图保真度：`high` / `low`             | -                         |
| `--size`           | 尺寸                                     | `1024x1024`               |
| `-n, --count`      | 生成数量（1-10）                         | `1`                       |
| `--quality`        | 质量：`low` / `medium` / `high` / `auto` | `medium`                  |
| `--format`         | 格式：`png` / `jpeg` / `webp`            | `png`                     |
| `--bg`             | 背景：`transparent` / `opaque` / `auto`  | `auto`                    |
| `--compression`    | 压缩比（0-100）                          | `0`                       |
| `-o, --output-dir` | 输出目录                                 | `~/Downloads/QoderImages` |
| `--prefix`         | 文件名前缀                               | `image`                   |
| `--no-download`    | 仅提交不等待                             | -                         |
| `--task-id`        | 查询已有任务                             | -                         |
| `--api-key`        | 指定 API Key                             | -                         |

### 依赖安装

| 依赖       | 安装命令                |
| ---------- | ----------------------- |
| `requests` | `pip3 install requests` |

---

## 首次使用

**开箱即用 — 无需任何配置**

脚本内置公共 API Key，提供约 **10000 次免费额度**。直接运行示例命令即可，零配置零成本。

```bash
python3 "$SKILL_PATH/assets/imagegen.py" "一只橘色的猫咪"
```

---

## 后续使用

公共 Key 额度用完后，前往 [redfox.hk/login](https://www.redfox.hk/login) 注册账号获取自己的 API Token，三种配置方式任选其一：

| 配置方式             | 说明                   | 命令                                                                                     |
| -------------------- | ---------------------- | ---------------------------------------------------------------------------------------- |
| **环境变量**（推荐） | 设置一次，全局生效     | `export REDFOX_API_KEY=ak_你的密钥`                                                      |
| **命令行参数**       | 临时使用，单次生效     | `python3 "$SKILL_PATH/assets/imagegen.py" "prompt" --api-key ak_你的密钥`                |
| **配置文件**         | 持久化存储，跨会话保留 | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 常见问题

**Q：本 Skill 的特点是什么？**
A：命令行直接调用 gpt-image-2 模型，支持批量生成、参数化控制、图生图编辑，内置免费额度开箱即用。

**Q：生成一张图片需要多久？**
A：通常 10-30 秒，复杂场景可能更久。脚本会自动轮询等待。

**Q：图生图的保真度怎么选？**
A：`--fidelity high` 尽量保留原图细节（微调），`--fidelity low` 允许大幅改动（风格迁移）。不传则由模型自行判断。

**Q：如何生成透明背景图？**
A：使用 `--bg transparent`，搭配 PNG 或 WebP 格式（JPEG 不支持透明）。

**Q：额度用完了怎么办？**
A：前往 [redfox.hk/login](https://www.redfox.hk/login) 注册获取自己的 API Token。

**Q：支持哪些图片格式作为参考图？**
A：支持 PNG、JPEG、WebP 格式的本地图片文件。
