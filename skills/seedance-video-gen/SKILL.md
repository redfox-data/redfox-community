---
name: seedance-video-gen
description: 基于 Seedance 2.0 模型的 AI 视频生成器，输入关键词/描述文案即可生成 MP4 视频。支持文生视频、分辨率/比例/时长控制、预置虚拟人像引用。使用 Seedance 视频生成、AI 视频、text-to-video 时调用此 Skill。
---

# Seedance2.0

## 简介

Seedance2.0是一款基于火山方舟 **Seedance 2.0** 模型的 AI 视频生成工具。通过 redfox.hk 平台封装了复杂的 ARK API 鉴权流程，**一行命令即可生成视频**。

> **Skill 特色**
>
> - 支持命令行参数化控制分辨率、比例、时长
> - 文生视频 + 虚拟人像引用双模式

### 为什么用这个 Skill？

- **对开发者**：无需去火山方舟申请白名单、配置 AK/SK、对接 ARK 鉴权，一行命令搞定
- **对创作者**：不用买会员、不用绑卡订阅，按次消费，用完即走
- **对所有人**：极低门槛，注册即用，无需自行搭建 API 链路

### 适用对象

社交媒体创作者、产品经理、内容运营人员、AI 爱好者，以及任何需要快速将文案转化为视频的用户。

---

## 功能特性

### 核心功能

- **文生视频**：输入一句中文或英文描述，Seedance 2.0 自动生成带有同步音频的 MP4 视频
- **参数控制**：支持分辨率（480p/720p/1080p）、画面比例（16:9/9:16 等 7 种）、视频时长（4-15 秒）
- **虚拟人像**：支持通过 `asset://` 格式引用预置虚拟人像，无需上传真实人脸素材
- **任务管理**：支持提交任务后获取 taskId，可随时查询任务进度和结果
- **自动轮询**：脚本自动轮询任务状态（排队中/生成中/已完成），无需手动等待

### 技术亮点

- 底层模型：`doubao-seedance-2-0-260128`
- 同步音频生成：视频画面与声音同步输出
- 尾帧提取：支持返回视频最后一帧，用于连续视频生成
- 随机种子：支持设置 seed 值，结果可复现
- HTTPS 安全传输：全链路 SSL 验证

### 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 视频提示词（必填，中英文均可） | — |
| `--resolution` | 分辨率：`480p` / `720p` / `1080p` | `720p` |
| `--ratio` | 画面比例：`16:9` / `4:3` / `1:1` / `3:4` / `9:16` / `21:9` / `adaptive` | `16:9` |
| `--duration` | 视频时长（秒）：4-15 或 -1（智能） | `5` |
| `--seed` | 随机种子：-1 到 2147483647 | `-1` |
| `--no-audio` | 不生成声音 | 默认生成 |
| `--watermark` | 添加水印 | 默认不添加 |
| `--return-last-frame` | 返回尾帧图片 URL | 默认不返回 |
| `--image-url` | 参考图 URL（`asset://` 格式） | — |
| `-o, --output-dir` | 输出目录 | `~/Downloads/QoderVideos` |
| `--prefix` | 文件名前缀 | `video` |
| `--no-download` | 仅提交不等待 | — |
| `--task-id` | 查询已有任务 | — |

---

## 使用场景

### 场景一：社交媒体内容创作

**角色**：短视频博主 / 小红书运营

**需求**：快速生成竖屏（9:16）视频素材，用于抖音/小红书/视频号发布

**使用方式**：

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "美妆产品展示，柔和的灯光，产品缓缓旋转" --ratio 9:16
```

**预期收益**：降低素材制作成本，从数小时缩短到几分钟

---

### 场景二：产品功能演示

**角色**：产品经理 / 创业者

**需求**：快速生成产品概念视频，用于提案、路演或展示

**使用方式**：

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "一款智能手表在桌面上展示，表盘切换不同功能界面" --resolution 1080p --duration 8
```

**预期收益**：无需专业视频制作能力，文案即视频

---

### 场景三：品牌内容运营

**角色**：内容运营 / 市场人员

**需求**：批量生成品牌配景视频，搭配文案制作品牌宣传短片

**使用方式**：

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "品牌主题色背景，文字渐变浮现，专业大气" --ratio 16:9 --no-audio
```

**预期收益**：提升内容产出效率，统一品牌视觉风格

---

### 场景四：创意灵感快速验证

**角色**：设计师 / 创意人员

**需求**：将脑中的画面用自然语言快速变成可视化视频，验证创意方向

**使用方式**：

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "赛博朋克风格的城市夜景，霓虹灯闪烁，雨滴落在镜头上的效果" --duration 6
```

**预期收益**：降低创意门槛，想法到视频只需一行命令

---

### 场景五：教育培训可视化

**角色**：教师 / 培训师

**需求**：将抽象知识点转化为可视化短片，提升教学效果

**使用方式**：

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "太阳系行星围绕太阳旋转的动画，标注每颗行星的名称" --duration 10
```

**预期收益**：无需动画制作技能，知识可视化零门槛

---

## 首次使用

配置 API Key 后即可使用：

```bash
# 设置环境变量
export REDFOX_API_KEY=ak_你的密钥

# 运行
python3 "$SKILL_PATH/scripts/videogen.py" "一只橘猫在窗台上打哈欠，阳光温暖地照在它的毛上"
```

> 前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 API Key。

---

## 后续使用

可前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册账号获取自己的 API Key，三种配置方式任选其一：

| 配置方式 | 说明 | 命令 |
|----------|------|------|
| **环境变量**（推荐） | 设置一次，全局生效 | `export REDFOX_API_KEY=ak_你的密钥` |
| **命令行参数** | 临时使用，单次生效 | `python3 "$SKILL_PATH/scripts/videogen.py" "prompt" --api-key ak_你的密钥` |
| **配置文件** | 持久化存储，跨会话保留 | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 一键安装

### 依赖安装

```bash
pip3 install requests
```

### 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `REDFOX_API_KEY` | — | redfox.hk 平台的 API 访问密钥 |

---

## 使用指南

### 基础使用

#### 1. 输入提示词生成视频

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "一只橘猫在窗台上打哈欠，阳光温暖地照在它的毛上"
```

脚本会自动提交任务、轮询等待（约 3-15 分钟），完成后下载到 `~/Downloads/QoderVideos/`。

#### 2. 查看结果

生成成功后会显示视频信息和文件路径：

```
[✓] Video ready: 5s, 720p, 16:9
[✓] Token usage: 108900
[→] Downloading video: video.mp4
[✓] Done!
  /Users/you/Downloads/QoderVideos/video.mp4 (2.5 MB)
```

### 高级使用

#### 竖屏短视频（适配抖音/小红书）

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "时尚都市夜景，霓虹灯闪烁" --ratio 9:16
```

#### 高清长视频

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "海浪拍打岩石的慢动作" --resolution 1080p --duration 10
```

#### 使用预置虚拟人像

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "一位年轻女性在图书馆安静阅读" --image-url "asset://female_student_01"
```

更多预置虚拟人像 ID 请参考火山方舟「素材&虚拟人像库」文档。

#### 任务管理

```bash
# 仅提交任务，返回 taskId 后立即退出
python3 "$SKILL_PATH/scripts/videogen.py" "复杂场景" --no-download

# 稍后用 taskId 查询结果
python3 "$SKILL_PATH/scripts/videogen.py" "ignored" --task-id vg_abc123def456
```

#### 多段连续视频生成

```bash
# 1. 生成第一段，获取尾帧
python3 "$SKILL_PATH/scripts/videogen.py" "开场画面" --return-last-frame

# 2. 将返回的 lastFrameUrl 作为下一段的首帧
python3 "$SKILL_PATH/scripts/videogen.py" "转场到第二个场景" --image-url "上一步的lastFrameUrl"
```

### 命令速查

| 命令 | 功能 |
|------|------|
| `python3 videogen.py "提示词"` | 基础文生视频 |
| `--ratio 9:16` | 竖屏比例 |
| `--resolution 1080p` | 高清分辨率 |
| `--duration 10` | 指定时长 |
| `--no-audio` | 静音视频 |
| `--watermark` | 添加水印 |
| `--seed 42` | 固定种子可复现 |
| `--image-url "asset://..."` | 引用虚拟人像 |
| `--no-download` | 仅提交任务 |
| `--task-id <id>` | 查询已有任务 |
| `--api-key <key>` | 指定 API Key |
| `-o ~/Desktop` | 指定输出目录 |

---

## 项目架构

### 目录结构

```
seedance-video-gen/
├── SKILL.md              # Skill 定义与文档
└── scripts/              # 工具脚本
    └── videogen.py       # 视频生成主程序
```

### 技术栈

| 组件 | 技术 |
|------|------|
| 运行环境 | Python 3.6+ |
| HTTP 库 | requests |
| API 平台 | redfox.hk |
| 底层模型 | 火山方舟 Seedance 2.0 (doubao-seedance-2-0-260128) |
| 输出格式 | MP4 |

### 核心模块

| 模块 | 职责 |
|------|------|
| `get_api_key()` | 三级优先级获取 API Key：CLI > 环境变量 > 配置文件 |
| `submit_video_task()` | 构建 content 数组，提交视频生成任务 |
| `poll_video_result()` | 轮询任务状态（queued/running/succeeded/failed/expired），最多 20 分钟 |
| `download_video()` | 流式下载 MP4 视频，带进度条显示 |
| `main()` | CLI 入口：参数解析、API Key 校验、双分支（提交/查询）流程 |

### 数据流转

```
用户输入提示词 → submit_video_task() → redfox.hk API → 火山方舟 Seedance 2.0
                                                                      ↓
用户获得 MP4 ← download_video() ← poll_video_result() ← 任务完成回调
```

---

## 常见问答

### 安装相关问题

**Q1：需要 API Key 吗？**

A：需要。前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取自己的 API Key，通过环境变量 `REDFOX_API_KEY` 或 `--api-key` 参数配置。


**Q2：配置文件放在哪里？**

A：放在 `~/.qoder/apis/redfox.json`，内容格式为：`{"api_key": "ak_你的密钥"}`。

**Q3：如何验证 API Key 是否配置成功？**

A：运行 `python3 videogen.py "测试" --no-download`，如果能返回 taskId 则配置成功。

---

### 使用相关问题

**Q4：生成一个视频需要多久？**

A：通常 3-15 分钟，复杂场景可能更长。脚本会自动轮询等待，最多等待 20 分钟。

**Q5：支持上传自己的参考图吗？**

A：Seedance 2.0 不支持直接上传含真人人脸的参考图/视频。如需指定人物外观，可在提示词中描述（如"一位戴眼镜的亚洲女性"），或使用预置虚拟人像库的 `asset://` URL。更多信息请参考火山方舟「素材&虚拟人像库」文档。

**Q6：支持哪些提示词语言？**

A：中英文均可，API 内部会自动处理。

**Q7：输出文件保存在哪里？**

A：默认保存到 `~/Downloads/QoderVideos/video.mp4`，可通过 `-o` 参数指定目录。

---

### 故障排除

**Q8：任务超时了怎么办？**

A：脚本最多等待 20 分钟。超时后会打印 taskId，你可以稍后通过 `--task-id` 参数重新查询并下载结果。

**Q9：提示"API request failed"？**

A：检查网络连接是否正常，确认 redfox.hk 服务可访问。如果持续失败，可能是 API Key 已过期或余额不足。

**Q10：视频下载失败？**

A：确认输出目录有写入权限，磁盘空间充足。如果 OSS 链接过期，可以用 `--task-id` 重新查询获取新的下载链接。

---

### 获取帮助

如有其他问题，可前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 查看平台文档或联系客服。
