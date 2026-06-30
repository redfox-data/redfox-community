---
name: video-prompt-expert
description: |
  AI 视频生成提示词专家 Skill。帮助用户编写专业级 AI 视频生成提示词，并提供一键生成视频能力（Seedance 2.0 API）。
  支持多场景模板、效果诊断、@多模态参考语法指导，写完提示词直接出 MP4 视频。

  触发词：视频提示词、视频生成提示词、AI视频创作、写视频提示词、导演指令、Seedance提示词、文生视频提示词、视频脚本、@语法、生成视频

---

# 视频生成提示词专家

> **核心定位**：用导演思维写 AI 视频提示词。AI 不是画家，是刚入行的摄影师——你给的是**可执行的摄影指令**，不是画面描述。
>
> **表达风格**：专业但不学术，直接给结论。每个词都必须可执行。

> 核心执行流程详见 `references/core_workflow.md`

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| 结构化提示词编写 | 按专业技术参数体系逐层构建提示词 |
| @多模态参考语法 | 首帧锁定/风格参考/运镜参考/音频同步/主体锁定 |
| 黄金公式校验 | 检查主体+动作+场景+风格+情绪五要素完整性 |
| 20+场景问题诊断 | 人物不一致、运镜混乱、画面质量差等常见问题修复 |
| 实战模板库 | 8个常见场景模板（自然风光、城市夜景、人物特写等） |
| 一键生成视频 | 写完提示词直接调用 API 出 MP4 视频 |

### 特色亮点

- **提示词即摄影指令**：将抽象描述转化为 AI 可精确执行的指令，避免"很科幻""有感觉"等模糊表述
- **写+拍一体化**：完成提示词后可直接生成 4-15 秒 1080p 视频，无需切换工具
- **内置诊断能力**：遇到人物换脸、运镜混乱等问题时，可直接给出修复方案

---

## 使用指南

### 基础使用

直接用自然语言描述你想要的视频画面，技能会自动将其转化为专业级提示词。

> 用户：帮我写一个日落海滩的视频提示词，要电影感
>
> 助手：会按技术参数、空间层次、光影设计、运动编排逐层构建提示词

### 常用说法速查

| 意图 | 示例话术 | 效果 |
|------|---------|------|
| 新写提示词 | 「帮我写一个赛博朋克城市夜景的视频提示词」 | 按专业体系逐层构建完整提示词 |
| 效果诊断 | 「生成的视频人物总是换脸，怎么办」 | 诊断问题并给出修复方案 |
| 调用模板 | 「给我一个产品展示的提示词模板」 | 直接输出对应场景的可用模板 |
| 生成视频 | 「用这个提示词生成视频，16:9，8秒」 | 调用 API 直接出片 |

---

## 视频生成（调用 API 出片）

写完提示词后可直接调用 Seedance 2.0 API 生成 MP4 视频。

### 前置条件

- 环境变量 `REDFOX_API_KEY` 已配置（前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 获取）
- 依赖：`pip3 install requests`

### 基础命令

```bash
python3 "$SKILL_PATH/scripts/videogen.py" "提示词内容" --ratio 16:9 --duration 8 --resolution 1080p
```

### 参数速查

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 提示词（必填，中英文均可） | — |
| `--resolution` | `480p` / `720p` / `1080p` | `720p` |
| `--ratio` | `16:9` / `4:3` / `1:1` / `9:16` / `21:9` / `adaptive` | `16:9` |
| `--duration` | 时长（秒）：4-15 或 -1（智能） | `5` |
| `--seed` | 随机种子：-1 到 2147483647 | `-1` |
| `--no-audio` | 不生成声音 | 默认生成 |
| `--watermark` | 添加水印 | 默认不添加 |
| `--image-url` | 参考图 URL（`asset://` 格式引用虚拟人像） | — |
| `-o, --output-dir` | 输出目录 | `~/Downloads/QoderVideos` |
| `--no-download` | 仅提交任务，不等待 | — |
| `--task-id` | 查询已有任务并下载 | — |

### 画幅选择建议

| 用途 | 推荐画幅 |
|------|--------|
| 短视频（抖音/小红书） | `9:16` |
| 横屏内容（B站/YouTube） | `16:9` |
| 电影感宽银幕 | `21:9` |
| 社交帖图/产品展示 | `1:1` 或 `4:3` |

### 工作流示例

```bash
# 1. 写完提示词
# 2. 直接调用生成
python3 "$SKILL_PATH/scripts/videogen.py" "提示词" --ratio 16:9 --duration 8 --resolution 1080p

# 竖屏短视频
python3 "$SKILL_PATH/scripts/videogen.py" "提示词" --ratio 9:16 --duration 5

# 多段连续视频：第一段获取尾帧
python3 "$SKILL_PATH/scripts/videogen.py" "第一段" --return-last-frame
# 将返回的 lastFrameUrl 作为第二段首帧
python3 "$SKILL_PATH/scripts/videogen.py" "第二段" --image-url "上一步的lastFrameUrl"
```

### 生成耗时与消耗

- 通常 3-15 分钟，脚本自动轮询等待
- 分辨率越高、时长越长，Token 消耗越大
- 中途网络超时脚本会自动重试，不影响最终结果

### API Key 配置

```bash
# 方式1：环境变量（推荐）
export REDFOX_API_KEY=ak_你的密钥

# 方式2：命令行参数
python3 "$SKILL_PATH/scripts/videogen.py" "prompt" --api-key ak_你的密钥

# 方式3：配置文件（持久化）
mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json
```

---

## 文件结构

```
video-prompt-expert/
├── SKILL.md                          # 主技能文件（本文档）
├── scripts/
│   └── videogen.py                  # 视频生成主程序（Seedance 2.0 API）
├── references/
│   └── core_workflow.md             # 核心执行流程
└── assets/
    └── templates/
        └── prompt_templates.json    # 结构化模板数据
```
