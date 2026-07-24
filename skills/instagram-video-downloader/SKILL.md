---
name: instagram-video-downloader
description: Instagram视频下载 — 粘贴 Instagram 视频链接，一键解析返回无水印视频下载链接。当用户需要下载 Instagram 视频、保存 IG 视频、获取 Instagram 视频直链时使用。触发词：Instagram视频下载、IG视频下载、Ins视频下载、Instagram视频解析、下载Instagram视频、reel下载。
---

# Instagram视频下载

通过 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) API 解析 Instagram 视频链接，直接返回无水印视频下载链接。

---

## 能力概述

- **平台支持**：Instagram
- **内容类型**：视频（mp4 下载直链）
- **输入方式**：粘贴 Instagram 视频链接即可（每次仅限一个链接，不支持批量上传）
- **输出结果**：直接返回视频下载链接，复制到浏览器或下载工具即可保存
- **链接展示规则**：下载链接和封面链接必须完整展示原始 URL，严禁使用 `...` 或任何形式截断

---

## 使用方式

### 示例命令

下载 Instagram 视频：

```bash
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.instagram.com/reel/xxxxx/"
```

### 首次使用

先配置 API Key，然后运行：

```bash
# 设置环境变量
export REDFOX_API_KEY=ak_你的密钥

# 解析视频，获取下载链接
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.instagram.com/reel/xxxxx/"
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
| **即贴即解析** | 粘贴帖子链接即可，无需额外操作 |
| **链接自适应** | 支持 instagram.com 的 Reel 和普通帖子链接 |
| **结果直出** | 解析完成直接返回下载链接，复制即可用 |

---

## 常见使用场景

| 场景 | 示例链接 | 说明 |
|------|----------|------|
| 保存 IG 上的视频 | `https://www.instagram.com/reel/xxxxx/` | 获取无水印视频下载链接 |
| Reel 视频离线收藏 | `https://www.instagram.com/reel/xxxxx/` | 解析后复制链接下载保存 |
| 内容二次创作 | 任意 Instagram 视频链接 | 下载素材用于剪辑创作 |
| 素材备份 | 任意 Instagram 视频链接 | 备份喜欢的视频到本地 |

### 支持的作品链接格式

| 平台 | 链接格式 | 示例 |
|------|----------|------|
| Instagram Reel | `https://www.instagram.com/reel/<shortcode>/` | Reel 短视频 |
| Instagram Post | `https://www.instagram.com/p/<shortcode>/` | 普通帖子视频 |

---

## 常见问题

**Q：如何获取自己的 API Key？**
A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册即可获取 Token。

**Q：下载的视频有水印吗？**
A：没有。API 返回的是无水印视频直链。

**Q：可以批量上传多个链接吗？**
A：不支持。每次只能输入一个链接，批量上传会导致解析失败。

**Q：链接提示解析失败怎么办？**
A：确认链接是否完整、帖子是否仍然存在、账号内容是否公开。私密账号或已删除帖子无法解析。

---

## 了解更多

本工具基于 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 的 `parseWork/videoDownload/instagram` 接口构建。前往官网查看更多 API 能力和使用文档。
