---
name: video-downloader
description: 短视频下载器 — 支持抖音、小红书、快手、B站无水印视频下载，开箱即用。
---

# 短视频下载器

---

## 1. 简介

**短视频下载器**是一款支持抖音、小红书、快手、B站四大主流短视频平台的无水印视频下载工具。通过 [redfox.hk](https://www.redfox.hk) API 解析作品链接，自动获取无水印直链并下载到本地，开箱即用。

**核心价值**：一个链接，一键下载，无水印直链，无需抓包、无需分析网页源码，真正零门槛使用。

**适用对象**：内容创作者（下载素材二次创作）、自媒体运营（收集竞品视频）、普通用户（离线保存喜欢的视频）、数据分析师（下载视频用于研究分析）。

---

## 2. 功能特性

| 功能 | 说明 |
|------|------|
| 🎬 **无水印下载** | API 自动返回无水印直链，无需手动处理，下载即用 |
| 📱 **跨平台支持** | 一个工具覆盖抖音、小红书、快手、B站四大主流平台 |
| 🖼️ **图文下载** | 支持图文类型作品，自动下载全部图片并按序号命名（暂不支持小红书图文） |
| 🔗 **链接自适应** | 支持短链、分享链接、网页链接等多种格式，智能识别 |
| 📊 **进度显示** | 下载过程实时显示进度条和百分比，大文件也不会焦虑 |
| 🔑 **开箱即用** | 内置公共 API Key（约 10000 次免费额度），无需任何配置即可使用 |

**特色亮点**：
- 支持手机端分享链接和 PC 端网页链接，多端兼容
- API Key 四种配置方式：内置公共 Key / 环境变量 / 命令行参数 / 配置文件，灵活适配各种场景
- 隐私安全：API Key 本地存储，不会泄露

---

## 3. 一键安装

### 鉴权配置（API Key）

视频下载器使用 `X_API_KEY` 进行 API 鉴权，提供四种配置方式，按优先级从高到低：

| 优先级 | 配置方式 | 适用场景 | 命令 / 操作 |
|--------|----------|----------|-------------|
| 1 | **内置公共 Key**（默认） | 开箱即用，免费约 10000 次 | 无需任何配置，直接使用 |
| 2 | **命令行参数** | 临时使用，单次生效 | `python3 downloader.py "<链接>" --api-key ark_你的密钥` |
| 3 | **环境变量** | 推荐方式，设置一次全局生效 | `export X_API_KEY=ark_你的密钥` |
| 4 | **配置文件** | 持久化存储，跨会话保留 | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ark_你的密钥"}' > ~/.qoder/apis/redfox.json` |

> **获取 API Key**：前往 [www.redfox.hk](https://www.redfox.hk) 注册即可获取，格式为 `ark_xxx`。Key 绑定用户身份（vid），需要用户身份的接口会自动注入，无需手动传 vid。
>
> **免费额度说明**：公共 Key 提供约 10000 次免费调用。超出后 API 返回 3107 错误，届时请配置自己的 Key。

### 依赖安装

| 依赖 | 说明 | 安装命令 |
|------|------|----------|
| `requests` | HTTP 请求库，用于调用 API 和下载文件 | `pip3 install requests` |

### 环境要求

- Python 3.7+
- 支持的操作系统：macOS / Linux / Windows

---

## 4. 使用指南

### 基础使用

**最简用法**（使用内置公共 Key）：

```bash
python3 "$SKILL_PATH/assets/downloader.py" "<分享链接>"
```

**示例**：

```bash
# 抖音视频
python3 downloader.py "https://v.douyin.com/xxxxxx/"

# 小红书视频
python3 downloader.py "http://xhslink.com/o/xxxxxx"

# 快手视频
python3 downloader.py "https://v.kuaishou.com/xxxxxx"

# B站视频
python3 downloader.py "https://b23.tv/xxxxxx"
```

### 支持的作品链接格式

| 平台 | 链接格式 | 示例 |
|------|----------|------|
| 抖音（Douyin） | `https://v.douyin.com/xxxxxx/` | 手机分享链接 / PC 网页链接 |
| 小红书（Xiaohongshu） | `http://xhslink.com/o/xxxxxx` | 短链分享链接 |
| 快手（Kuaishou） | `https://v.kuaishou.com/xxxxxx` | 手机分享链接 |
| B站（Bilibili） | `https://b23.tv/xxxxxx` | 短链分享链接 |

> **重要提示**：每次仅限输入一个链接，不支持批量上传。如需下载多个视频，请逐个粘贴链接。

### 高级使用

**指定 API Key**：

```bash
# 命令行参数方式（单次生效）
python3 downloader.py "<链接>" --api-key ark_你的密钥

# 环境变量方式（全局生效）
export X_API_KEY=ark_你的密钥
python3 downloader.py "<链接>"
```

**指定输出目录**：

```bash
python3 downloader.py "<链接>" -o ~/Videos
# 默认输出目录：~/Downloads/QoderVideos
```

**保存 API Key 到配置文件**（持久化）：

```bash
python3 downloader.py "<链接>" --api-key ark_你的密钥 --save-key
```

### 常用命令 / 指令速查表

| 场景 | 命令 |
|------|------|
| 下载抖音无水印视频 | `python3 downloader.py "https://v.douyin.com/xxxxxx/"` |
| 下载小红书视频 | `python3 downloader.py "http://xhslink.com/o/xxxxxx"` |
| 下载快手视频 | `python3 downloader.py "https://v.kuaishou.com/xxxxxx"` |
| 下载 B 站视频 | `python3 downloader.py "https://b23.tv/xxxxxx"` |
| 指定 API Key | 加 `--api-key ark_你的密钥` |
| 指定输出目录 | 加 `-o ~/Videos` 或 `--output-dir ~/Videos` |
| 持久化保存 Key | 加 `--save-key` |
| 环境变量配置 Key | `export X_API_KEY=ark_你的密钥` |
| 配置文件方式 | `echo '{"api_key":"ark_xxx"}' > ~/.qoder/apis/redfox.json` |

---

## 5. 使用场景

| 场景 | 角色 | 需求 | 使用方式 | 预期收益 |
|------|------|------|----------|----------|
| ✂️ **视频二次创作** | 短视频创作者 / 剪辑师 | 下载抖音、B站热门视频作为剪辑素材 | 复制目标视频分享链接 → 执行下载命令 → 获取无水印原视频 | 省去录屏和去水印步骤，直接获得高清素材，效率提升 80% |
| 💾 **离线收藏备份** | 普通用户 | 将喜欢的短视频保存到本地，防止链接失效 | 粘贴链接下载 → 分类保存到本地文件夹 | 永久保存喜爱的视频，不依赖平台链接是否有效 |
| 📊 **内容分析研究** | 数据分析师 / 市场调研 | 批量下载竞品或行业视频用于内容分析 | 逐个链接下载 → 本地分析视频内容特征 | 获取原始视频素材，支持深度内容分析和趋势研究 |
| 🏢 **自媒体内容运营** | 运营人员 / MCN | 收集同赛道热门作品，研究爆款规律 | 搜索爆款视频链接 → 批量下载 → 分析内容结构 | 建立本地爆款视频素材库，辅助选题和内容策略决策 |

---

## 6. 项目架构

### 目录结构

```
video-downloader/
├── SKILL.md                          # Skill 定义文件
├── scripts/
│   └── downloader.py                 # 视频下载核心脚本
├── assets/
│   ├── presentation.html             # 功能演示页面
│   └── 短视频下载器_Skill_审核演示.pdf   # 审核演示文档
```

### 技术栈

| 技术 | 用途 | 版本要求 |
|------|------|----------|
| Python | 脚本运行环境 | 3.7+ |
| requests | HTTP 请求库，调用 API 和下载文件 | 最新稳定版 |
| argparse | 命令行参数解析 | Python 内置 |
| json | JSON 数据序列化/反序列化 | Python 内置 |
| os / pathlib | 文件路径和目录操作 | Python 内置 |

### 核心模块说明

**`scripts/downloader.py`** — 视频下载核心脚本：

- **`get_api_key(cli_key)`** — API Key 获取函数，按优先级：命令行参数 > 环境变量 `X_API_KEY` > 配置文件 `~/.qoder/apis/redfox.json` > 内置公共 Key
- **`API_URL`** — 调用 `https://redfox.hk/story/api/parseWork/parse` 解析作品链接
- **`save_api_key(api_key)`** — 持久化保存 API Key 到配置文件
- **`sanitize_filename(name)`** — 文件名安全处理，移除非法字符并截断
- **`download_file(session, url, filepath)`** — 流式下载文件，实时显示进度条
- **平台支持**：通过 `PLATFORM_MAP` 映射平台代码到中文名称（dy→抖音、xhs→小红书、ks→快手、bili→B站）
- **内容类型**：支持 `video`（视频，下载为 `.mp4`）和 `photo`（图文，下载全部图片并序号命名）

### 资源索引

| 资源 | 路径 | 说明 |
|------|------|------|
| 核心脚本 | [scripts/downloader.py](scripts/downloader.py) | 视频下载核心脚本 |
| API 来源 | [redfox.hk](https://www.redfox.hk) | 基于 `parseWork/parse` 接口构建 |
| 演示页面 | [assets/presentation.html](assets/presentation.html) | 功能演示页面 |

---

## 7. 常见问答

### 安装 / 配置

**Q：公共 Key 有多少次免费额度？**
A：约 10000 次。超出后 API 会返回 3107 错误，届时请配置自己的 Key。

**Q：如何获取自己的 API Key？**
A：前往 [www.redfox.hk](https://www.redfox.hk) 注册即可获取，格式为 `ark_xxx`。

**Q：四种 API Key 配置方式有什么区别？**
A：内置公共 Key 开箱即用但不稳定；环境变量设置一次全局生效最方便；命令行参数适合临时切换 Key；配置文件方式支持跨会话持久化。四种方式按优先级叠加，无需担心冲突。

### 使用

**Q：下载的视频有水印吗？**
A：没有。API 返回的是无水印直链，下载的视频即为纯净版。

**Q：支持图文下载吗？**
A：支持图文类型下载（暂不支持小红书图文）。图文内容会自动下载所有图片，并按 `{标题}_{序号}.{扩展名}` 格式命名。

**Q：可以批量上传多个链接吗？**
A：不支持。每次只能输入一个链接，批量上传会导致解析失败。如需下载多个视频，请逐个粘贴链接。

**Q：下载的文件保存在哪里？**
A：默认保存在 `~/Downloads/QoderVideos/`。可通过 `-o` 或 `--output-dir` 参数自定义输出目录。

**Q：支持哪些平台？**
A：抖音、小红书、快手、B站。覆盖手机端分享链接和 PC 端网页链接。

### 故障排除

**Q：链接提示解析失败怎么办？**
A：确认链接是否完整、是否已过期。短链有时效性，建议重新复制分享链接后再试。

**Q：API 返回 3107 错误？**
A：表示 API Key 无效或免费额度已用完。如果使用的是公共 Key，请前往 [www.redfox.hk](https://www.redfox.hk) 注册获取自己的 Key 并配置。

**Q：API 返回 3106 错误？**
A：缺少 API Key。请通过命令行 `--api-key`、环境变量 `X_API_KEY` 或配置文件方式提供有效的 Key。

**Q：下载速度慢怎么办？**
A：大文件下载需要稳定的网络连接。可尝试更换网络环境，或检查网络代理设置。脚本已设置 120 秒超时，大文件会自动等待。

**Q：installing requests 报错？**
A：确保 pip 版本为最新：`pip3 install --upgrade pip`。如仍有问题，尝试使用 `python3 -m pip install requests`。
