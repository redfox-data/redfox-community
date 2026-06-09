---
name: seedream-5.0-lite
description: 基于火山方舟 seedream 5.0 lite 模型的 AI 图片生成器，支持文生图、图生图、组图生成与提示词优化。输入关键词即可生成高分辨率图片，使用 seedream 图片生成、AI 绘图、文生图、图生图时调用此 Skill。
---

# seedream5.0 lite

## 简介

基于火山方舟 **seedream 5.0 lite** 模型的 AI 图片生成工具。通过 redfox.hk 平台封装了复杂的 ARK API 鉴权流程，**一行命令即可生成高质量图片**。内置免费额度，开箱即用。

### 为什么用这个 Skill？

- **对开发者**：无需去火山方舟申请白名单、配置 AK/SK、对接 ARK 鉴权，一行命令搞定
- **对创作者**：不用买会员、不用绑卡订阅，按次消费，用完即走
- **对所有人**：内置公共 API Key，约 **10000 次免费额度**，零配置零成本快速上手

### 适用对象

设计师、社交媒体创作者、内容运营人员、AI 爱好者，以及任何需要快速将创意转化为图片的用户。

---

## 功能特性

### 核心功能

- **文生图**：输入一句中文或英文描述，seedream 5.0 lite 自动生成高清图片
- **图生图**：上传参考图 + 提示词，基于原图进行编辑和风格转换
- **组图生成**：支持 `auto` 模式自动生成多张关联图片（最多 15 张）
- **提示词优化**：内置 `standard`（高质量）和 `fast`（快速）两种优化模式
- **高分辨率输出**：支持 `2K`/`3K`/`4K` 或自定义像素尺寸，默认 `2048x2048`
- **任务管理**：支持提交任务后获取 taskId，可随时查询任务进度和结果
- **自动轮询**：脚本自动轮询任务状态（排队中/生成中/已完成），无需手动等待

### 技术亮点

- 底层模型：`doubao-seedream-5-0-260128`
- 输出格式：PNG、JPEG
- 水印控制：可选择是否添加 "AI生成" 水印
- 图片 URL 自动转存 OSS，长期有效
- HTTPS 安全传输：全链路 SSL 验证

### 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 图片生成提示词（必填，中英文均可） | — |
| `--image` | 参考图路径或 URL（启用图生图模式） | — |
| `--size` | 图片尺寸：`2K`/`3K`/`4K` 或具体像素如 `2048x2048` | `2048x2048` |
| `--format` | 输出格式：`png` / `jpeg` | `jpeg` |
| `--watermark` | 添加 "AI生成" 水印 | 默认不添加 |
| `--sequential` | 组图模式：`auto` / `disabled` | `disabled` |
| `--max-images` | 组图最多生成数量（1-15） | `4` |
| `--optimize` | 提示词优化：`standard` / `fast` | — |
| `-o, --output-dir` | 输出目录 | `~/Downloads/QoderImages` |
| `--prefix` | 文件名前缀 | `image` |
| `--no-download` | 仅提交不等待 | — |
| `--task-id` | 查询已有任务 | — |

---

## 使用场景

### 场景一：社交媒体内容创作

**角色**：小红书博主 / 自媒体运营

**需求**：快速生成高质量配图、封面图、产品展示图

**使用方式**：

```bash
python3 "$SKILL_PATH/assets/seedream.py" "一杯拿铁咖啡放在木质桌面上，柔和的自然光，ins风" --size 2048x2048
```

**预期收益**：从找图/拍图到出图只需几秒，支持批量组图生成

---

### 场景二：电商产品展示

**角色**：电商运营 / 独立站卖家

**需求**：为商品生成统一风格的产品场景图

**使用方式**：

```bash
python3 "$SKILL_PATH/assets/seedream.py" "白色无线耳机悬浮在浅灰色背景上，专业产品摄影，柔和阴影" --format png --size 3K
```

**预期收益**：零摄影成本，快速产出高质量商品图

---

### 场景三：设计灵感快速验证

**角色**：UI 设计师 / 插画师

**需求**：将脑中的画面用自然语言快速变成可视化图片，验证创意方向

**使用方式**：

```bash
python3 "$SKILL_PATH/assets/seedream.py" "赛博朋克风格的未来城市，霓虹灯倒映在雨后的街道上，电影级构图" --size 4K
```

**预期收益**：降低创意门槛，想法到视觉稿只需一行命令

---

### 场景四：组图内容运营

**角色**：内容运营 / 市场人员

**需求**：一次性生成多张风格统一的配图，用于文章/推文/活动页

**使用方式**：

```bash
python3 "$SKILL_PATH/assets/seedream.py" "一组清新风格的早餐摄影，包含面包、水果、咖啡" --sequential auto --max-images 6
```

**预期收益**：批量生成风格一致的视觉素材，提升内容产出效率

---

### 场景五：图生图风格迁移

**角色**：摄影师 / 艺术创作者

**需求**：基于现有图片进行风格转换或元素修改

**使用方式**：

```bash
python3 "$SKILL_PATH/assets/seedream.py" "将画面转换成宫崎骏动画风格，色彩明亮温暖" --image ~/Pictures/photo.jpg
```

**预期收益**：无需掌握复杂修图软件，自然语言即可驱动风格转换

---

### 依赖安装

| 依赖 | 安装命令 |
|------|----------|
| `requests` | `pip3 install requests` |

---

## 首次使用

**开箱即用 — 无需任何配置**

脚本内置公共 API Key，提供约 **10000 次免费额度**。直接运行示例命令即可，零配置零成本。

```bash
python3 "$SKILL_PATH/assets/seedream.py" "一只橘色的猫咪坐在窗台上看着窗外的夕阳"
```

---

## 后续使用

公共 Key 额度用完后，前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册账号获取自己的 API Token，三种配置方式任选其一：

| 配置方式 | 说明 | 命令 |
|----------|------|------|
| **环境变量**（推荐） | 设置一次，全局生效 | `export REDFOX_API_KEY=ak_你的密钥` |
| **命令行参数** | 临时使用，单次生效 | `python3 "$SKILL_PATH/assets/seedream.py" "prompt" --api-key ak_你的密钥` |
| **配置文件** | 持久化存储，跨会话保留 | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 使用指南

### 基础使用

#### 1. 输入提示词生成图片

```bash
python3 "$SKILL_PATH/assets/seedream.py" "一只橘猫在窗台上打哈欠，阳光温暖地照在它的毛上"
```

脚本会自动提交任务、轮询等待（约 10-60 秒），完成后下载到 `~/Downloads/QoderImages/`。

#### 3. 查看结果

生成成功后会显示图片信息和文件路径：

```
[✓] Model: doubao-seedream-5-0-260128, Size: 2048x2048
[✓] Generated images: 1, Tokens: 1024
[→] Downloading 1/1: image.jpeg
[████████████████████] 100%

✓ Done!
  /Users/you/Downloads/QoderImages/image.jpeg (312.5 KB)
```

### 高级使用

#### 高分辨率输出

```bash
# 4K 超高清
python3 "$SKILL_PATH/assets/seedream.py" "雪山日出，金色阳光洒在雪顶" --size 4K

# 指定具体像素
python3 "$SKILL_PATH/assets/seedream.py" "城市夜景" --size 2048x1152
```

#### 组图生成（批量出图）

```bash
# 自动生成最多 6 张关联图片
python3 "$SKILL_PATH/assets/seedream.py" "一组极简风办公桌面静物" --sequential auto --max-images 6
```

#### 图生图编辑

```bash
# 基于参考图修改
python3 "$SKILL_PATH/assets/seedream.py" "把背景换成海边日落" --image ~/Pictures/portrait.jpg

# 使用网络图片作为参考
python3 "$SKILL_PATH/assets/seedream.py" "转换成油画风格" --image "https://example.com/photo.jpg"
```

#### 提示词优化

```bash
# 标准模式（质量更高，耗时较长）
python3 "$SKILL_PATH/assets/seedream.py" "未来太空站内部" --optimize standard

# 快速模式（快速出图，质量一般）
python3 "$SKILL_PATH/assets/seedream.py" "快速草图概念" --optimize fast
```

#### 任务管理

```bash
# 仅提交任务，返回 taskId 后立即退出
python3 "$SKILL_PATH/assets/seedream.py" "复杂场景" --no-download

# 稍后用 taskId 查询结果
python3 "$SKILL_PATH/assets/seedream.py" "ignored" --task-id ark_abc123def456
```

### 命令速查

| 命令 | 功能 |
|------|------|
| `python3 seedream.py "提示词"` | 基础文生图 |
| `--size 4K` | 4K 高分辨率 |
| `--format png` | PNG 格式输出 |
| `--sequential auto --max-images 6` | 组图模式生成 6 张 |
| `--image ~/pic.jpg` | 图生图模式 |
| `--optimize standard` | 提示词标准优化 |
| `--watermark` | 添加水印 |
| `--no-download` | 仅提交任务 |
| `--task-id <id>` | 查询已有任务 |
| `--api-key <key>` | 指定 API Key |
| `-o ~/Desktop` | 指定输出目录 |

---

## 项目架构

### 目录结构

```
seedream-5-lite/
├── SKILL.md              # Skill 定义与文档
└── assets/               # 工具脚本
    └── seedream.py       # 图片生成主程序
```

### 技术栈

| 组件 | 技术 |
|------|------|
| 运行环境 | Python 3.6+ |
| HTTP 库 | requests |
| API 平台 | redfox.hk |
| 底层模型 | 火山方舟 seedream 5.0 lite (`doubao-seedream-5-0-260128`) |
| 输出格式 | PNG、JPEG |

### 核心模块

| 模块 | 职责 |
|------|------|
| `get_api_key()` | 三级优先级获取 API Key：CLI > 环境变量 > 配置文件 |
| `upload_image()` | 将本地参考图上传至 OSS，获取可访问的 URL |
| `submit_task()` | 构建请求体，提交 ARK 图片生成任务 |
| `poll_result()` | 轮询任务状态（queued/running/succeeded/failed），最多 6 分钟 |
| `download_images()` | 流式下载生成图片，带进度条显示 |
| `main()` | CLI 入口：参数解析、API Key 校验、双分支（提交/查询）流程 |

### 数据流转

```
用户输入提示词 → submit_task() → redfox.hk API → 火山方舟 seedream 5.0 lite
                                                                      ↓
用户获得图片 ← download_images() ← poll_result() ← 任务完成回调
```

---

## 常见问答

### 安装相关问题

**Q1：本 Skill 的特点是什么？**

A：命令行直接调用 seedream 5.0 lite 模型，支持文生图、图生图、组图生成、提示词优化与高分辨率输出，内置免费额度开箱即用。

**Q2：额度用完了怎么办？**

A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取自己的 API Token。

**Q3：配置文件放在哪里？**

A：放在 `~/.qoder/apis/redfox.json`，内容格式为：`{"api_key": "ak_你的密钥"}`。

**Q4：如何验证 API Key 是否配置成功？**

A：运行 `python3 seedream.py "测试" --no-download`，如果能返回 taskId 则配置成功。

---

### 使用相关问题

**Q5：生成一张图片需要多久？**

A：通常 10-60 秒，复杂场景或高分辨率可能更久。脚本会自动轮询等待，最多等待 6 分钟。

**Q6：支持上传自己的参考图吗？**

A：支持。通过 `--image` 参数传入本地图片路径（如 `--image ~/Pictures/photo.jpg`），脚本会自动上传至 OSS 后提交图生图任务。也支持直接传入网络图片 URL。

**Q7：支持哪些提示词语言？**

A：中英文均可，API 内部会自动处理。

**Q8：输出文件保存在哪里？**

A：默认保存到 `~/Downloads/QoderImages/image.jpeg`，可通过 `-o` 参数指定目录。

**Q9：组图模式和单张模式有什么区别？**

A：`--sequential disabled`（默认）只生成单张图片；`--sequential auto` 会根据提示词自动判断并生成多张关联图片，最多 `--max-images` 张。

---

### 故障排除

**Q10：任务超时了怎么办？**

A：脚本最多等待 6 分钟。超时后会打印 taskId，你可以稍后通过 `--task-id` 参数重新查询并下载结果。

**Q11：提示"API request failed"？**

A：检查网络连接是否正常，确认 redfox.hk 服务可访问。如果持续失败，可能是 API Key 已过期或余额不足。

**Q12：图片下载失败？**

A：确认输出目录有写入权限，磁盘空间充足。如果 OSS 链接过期，可以用 `--task-id` 重新查询获取新的下载链接。

---

### 获取帮助

如有其他问题，可前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 查看平台文档或联系客服。
