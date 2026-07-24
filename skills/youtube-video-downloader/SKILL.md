---
name: youtube-video-downloader
description: YouTube视频下载 — 粘贴 YouTube 视频链接，一键解析返回无水印视频下载链接（支持多种清晰度）。当用户需要下载 YouTube 视频、保存油管视频、获取 YouTube 视频直链时使用。触发词：YouTube视频下载、油管视频下载、yt视频下载、YouTube视频解析、下载YouTube视频、youtube视频下载。
---

# YouTube视频下载

通过 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) API 解析 YouTube 视频链接，直接返回无水印视频下载链接（资源可能包含不同格式的视频和音频文件）。

---

## 能力概述

- **平台支持**：YouTube
- **内容类型**：视频/音频（mp4 / webm / m4a 等格式，资源可能包含视频和音频文件）
- **输入方式**：粘贴 YouTube 视频链接即可（每次仅限一个链接，不支持批量上传）
- **输出结果**：直接返回视频下载链接，复制到浏览器或下载工具即可保存
- **链接展示规则**：下载链接和封面链接必须完整展示原始 URL，严禁使用 `...` 或任何形式截断
- **字段展示规则**：返回结果必须完整展示以下字段：
  - 内容描述（desc）：完整原文逐行展示，不截断
  - 资源列表：对每个 resource 对象展示其类型（type）、时长（durationSeconds）、下载链接（downloadUrl）、封面链接（coverUrl）
  - 当接口未返回 resources 数组时，自动回退提取顶层同名字段保证兼容性

---

## 使用方式

### 示例命令

下载 YouTube 视频：

```bash
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.youtube.com/watch?v=xxxxx"
```

### 首次使用

先配置 API Key，然后运行：

```bash
# 设置环境变量
export REDFOX_API_KEY=ak_你的密钥

# 解析视频，获取下载链接
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.youtube.com/watch?v=xxxxx"
```

> 前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 API Key。

### 后续使用

配置方式（任选其一）：

| 方式 | 命令 |
|------|------|
| **环境变量**（推荐） | `export REDFOX_API_KEY=ark_你的密钥` |
| **命令行参数** | `python3 "$SKILL_PATH/scripts/downloader.py" "<链接>" --api-key ark_你的密钥` |
| **配置文件** | `echo '{"api_key":"ark_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 特色功能

| 功能 | 说明 |
|------|------|
| **无水印直链** | API 自动返回无水印视频下载链接，无需手动处理 |
| **多资源可选** | 返回多个资源（视频文件、音频文件等），依次列出所有下载链接，按类型选择需要的即可 |
| **即贴即解析** | 粘贴视频链接即可，无需额外操作 |
| **结果直出** | 解析完成直接返回下载链接，复制即可用 |

---

## 常见使用场景

| 场景 | 示例链接 | 说明 |
|------|----------|------|
| 保存 YouTube 上的视频 | `https://www.youtube.com/watch?v=xxxxx` | 获取无水印视频/音频下载链接 |
| YouTube Shorts 离线收藏 | `https://www.youtube.com/shorts/xxxxx` | 解析后复制链接下载保存 |
| 内容二次创作 | 任意 YouTube 视频链接 | 下载素材用于剪辑创作 |
| 素材备份 | 任意 YouTube 视频链接 | 备份喜欢的视频到本地 |

### 支持的作品链接格式

| 平台 | 链接格式 | 示例 |
|------|----------|------|
| YouTube 普通视频 | `https://www.youtube.com/watch?v=<videoId>` | 标准视频链接 |
| YouTube Shorts | `https://www.youtube.com/shorts/<videoId>` | Shorts 短视频 |
| YouTube 短链接 | `https://youtu.be/<videoId>` | 分享短链接 |

---

## 常见问题

**Q：如何获取自己的 API Key？**
A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册即可获取 Token。

**Q：下载的视频有水印吗？**
A：没有。API 返回的是无水印视频直链。

**Q：会返回多个资源吗？**
A：会。API 通常返回多个资源，可能包含不同格式的视频文件和音频文件（如 mp4、webm、m4a 等），每个资源的下载链接都会完整列出，按需选择即可。

**Q：可以批量上传多个链接吗？**
A：不支持。每次只能输入一个链接，批量上传会导致解析失败。

**Q：链接提示解析失败怎么办？**
A：确认链接是否完整、视频是否仍然存在、是否为地区限制内容。已删除或受限视频无法解析。

---

## 了解更多

本工具基于 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 的 `parseWork/videoDownload/youtube` 接口构建。前往官网查看更多 API 能力和使用文档。
