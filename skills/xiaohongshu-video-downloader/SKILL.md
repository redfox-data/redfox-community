---
name: xiaohongshu-video-downloader
description: 小红书视频下载 — 粘贴带 xsec_token 参数的小红书视频链接，一键解析返回无水印视频下载链接。当用户需要下载小红书视频、保存红书视频、获取小红书视频直链时使用。触发词：小红书视频下载、红书视频下载、小红书视频解析、下载小红书视频、RED视频下载。
---

# 小红书视频下载

粘贴带 `xsec_token` 参数的小红书视频链接，一键获取无水印视频下载直链。通过 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 服务解析，支持单个或批量链接处理，自动识别并校验小红书视频链接。

> ⚠️ **链接必须携带 `xsec_token` 参数**，否则小红书接口会返回链接格式错误。官方示例链接：
> `https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed`

---

## 简介

**适用对象**：需要下载小红书视频的用户，包括内容创作者、视频收藏者、运营分析人员。

**核心能力**：
- 📹 粘贴带 `xsec_token` 参数的小红书链接即可获取无水印 mp4 下载直链
- 📦 支持批量链接解析（空格分隔多个链接）
- 🔍 自动校验域名与 `xsec_token` 参数，不合规链接会提示重新输入并附上官方示例
- 🎬 返回视频下载链接、封面链接，复制到浏览器或下载工具即可保存

---

## 功能特性

| 功能 | 说明 |
|------|------|
| **无水印直链** | 自动返回无水印视频下载链接，无需手动处理 |
| **即贴即解析** | 粘贴带 `xsec_token` 的视频链接即可，无需额外操作 |
| **批量解析** | 支持一次粘贴多个链接，逐个解析并在最后汇总成功和失败数量 |
| **智能校验** | 自动识别小红书视频链接并校验 `xsec_token` 参数，不合规链接提示重新输入 |
| **链接自适应** | 支持 www.xiaohongshu.com 网页链接与 xhslink.com 短链两种格式 |
| **接口错误兜底** | 接口返回链接格式错误时自动附上官方示例链接，引导用户重新传入 |
| **结果直出** | 解析完成直接返回下载链接，复制即可用 |

---

## 一键安装

1. 前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 API Key
2. 配置环境变量：`export REDFOX_API_KEY=ark_你的密钥`
3. 粘贴带 `xsec_token` 参数的小红书视频链接即可使用

---

## 使用指南

> 核心执行流程详见 `references/core_workflow.md`

直接用自然语言描述需求，无需记忆命令。提供正确的小红书视频链接时，直接执行解析并返回结果。

### 常用说法速查

| 意图 | 示例话术 | 效果 |
|------|----------|------|
| 下载单个视频 | 「下载这个视频 https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed」 | 解析链接并返回无水印下载直链 |
| 批量下载 | 「下载这几个视频 链接1 链接2 链接3」（每个链接均需携带 `xsec_token`） | 逐个解析每个链接，最后汇总结果 |
| 保存视频 | 「帮我把这条小红书视频存下来」 | 引导贴上带 `xsec_token` 的链接，解析后返回下载链接 |

### 支持的作品链接格式

| 平台 | 链接格式 | 示例 |
|------|----------|------|
| 小红书 | `https://www.xiaohongshu.com/explore/<笔记ID>?xsec_token=<token>&xsec_source=<source>` | `https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed` |
| 小红书 | `http://xhslink.com/a/<短码>?xsec_token=<token>` | 手机分享短链，同样需携带 `xsec_token` |

> 🔑 **如何获取带 `xsec_token` 的链接**：在小红书 PC 网页打开笔记后，直接复制浏览器地址栏 URL；或在 App 内点“分享 → 复制链接”，得到的链接默认已携带 `xsec_token`。

---

## 使用场景

| 场景 | 角色 | 示例问法 | 收益 |
|------|------|----------|------|
| 素材收集 | 剪辑师 | 「下载这条小红书视频」 | 快速拿到无水印素材，直接进剪辑流程 |
| 内容备份 | 收藏者 | 「保存这个小红书视频」 | 原笔记删除也不怕，本地永久留存 |
| 热点分析 | 运营 | 「把这个爆款视频下下来」 | 离线反复观看，拆解爆款逻辑 |

---

## 常见问答

**Q：如何获取自己的 API Key？**
A：前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册即可获取 Token。

**Q：下载的视频有水印吗？**
A：没有。返回的是无水印视频直链。

**Q：可以批量解析多个链接吗？**
A：可以。多个链接用空格分隔即可，会逐个解析并在最后汇总成功和失败数量（每个链接均需携带 `xsec_token`）。

**Q：为什么我的链接提示“缺少 xsec_token 参数”？**
A：小红书接口要求链接必须携带 `xsec_token` 参数，否则无法解析。请在 PC 网页地址栏或 App 分享面板重新复制完整链接，例如：
`https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed`

**Q：输入了非小红书链接会怎样？**
A：会提示「该链接不是小红书视频链接」，附上官方示例链接并终止解析。请重新输入正确的小红书视频链接（支持 www.xiaohongshu.com 网页链接或 xhslink.com 短链，均需携带 `xsec_token`）。

**Q：链接提示解析失败怎么办？**
A：依次排查：① 链接是否携带 `xsec_token`；② 链接是否完整；③ 视频是否仍然存在、笔记内容是否公开。私密笔记或已删除笔记无法解析。

---

## 了解更多

本工具基于 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 的视频解析服务构建。前往官网查看更多功能和使用文档。
