# Core Workflow — 视频号视频下载

> 本文档为 Agent 内部执行参考，包含完整工作流、接口规范、输出格式及降级策略。

---

## Step 0: 鉴权前置检查

1. 检查环境变量 `REDFOX_API_KEY` 是否已配置
2. 未配置 → 引导用户前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取并配置
3. 已配置 → 进入 Step 1

---

## Step 1: 解析用户输入

从用户消息中提取视频号链接。如果用户未提供链接，引导用户：

1. 打开微信 → 视频号 → 找到目标视频
2. 点击视频右下角「分享」按钮
3. 选择「复制链接」

支持的链接格式：`https://weixin.qq.com/sph/xxxxxx`

---

## Step 2: 执行数据采集

**接口**: `POST https://redfox.hk/story/api/parseWork/videoDownload/sph`

**请求头**: `Content-Type: application/json` + `X-API-KEY: {API Key}`

**请求体**: `{"url": "{视频号链接}", "source": "视频号视频下载-GitHub"}`

**成功响应** (code=2000):
```json
{
  "code": 2000,
  "msg": "成功",
  "data": {
    "title": "",
    "desc": "视频描述",
    "cover": "封面图 URL",
    "videoUrl": "视频下载地址",
    "resources": [
      {
        "type": "video",
        "downloadUrl": "下载链接",
        "coverUrl": "封面链接",
        "durationSeconds": null
      }
    ]
  }
}
```

**响应字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| title | string | 视频标题（可能为空） |
| desc | string | 视频描述内容 |
| cover | string | 封面图 URL |
| videoUrl | string | 视频下载地址（可能为空，此时从 resources 取） |
| resources | array | 全部媒体资源列表 |
| resources[].type | string | 资源类型：video/audio/image |
| resources[].downloadUrl | string | 下载链接 |
| resources[].coverUrl | string | 封面链接 |
| resources[].durationSeconds | integer | 时长（秒） |

**fallback 逻辑**: 若 `videoUrl` 为空，从 `resources[0].downloadUrl` 取值。

---

## Step 3: 输出结果

脚本调用 `scripts/parse_video_download.py`，输出 JSON 数组，Agent 须按以下格式展示。

### 成功输出模板

**单视频时**使用以下 emoji 格式：

```markdown
## 🎬 视频号解析结果

**📌 标题：** {data.title}

**🖼️ 封面图：**

[封面图]({data.cover})

**🔗 下载地址：**

[{data.videoUrl}]({data.videoUrl})

> 💡 下载地址为临时链接，建议及时保存
```

**批量视频时**使用以下编号格式，每个视频一行，包含：
- **序号**：全局递增编号
- **标题**：视频标题（无标题时显示"无标题"）
- **封面图**：以 Markdown 链接展示，可点击跳转
- **视频下载地址**：以 Markdown 链接展示，可点击访问
- **操作**：提供可点击链接 `查看视频`（链接为视频下载地址）

失败视频在列表末尾单独列出，标注失败原因。

```
1. **标题**：xxx
   **封面图**：[封面图](cover_url)
   **下载地址**：[video_url](video_url)
   **操作**：[查看视频](video_url)

2. **标题**：xxx
   ...

---
❌ 解析失败：
- 链接：xxx | 原因：xxx

> ⚠️ 视频号下载链接有效期约 **5 分钟**，请立即复制到浏览器打开或下载！
```

### 失败输出模板

```markdown
## ❌ 解析失败

**原因：** {错误信息}
```

---

## Step 4: 降级处理

当接口返回异常时：

| 场景 | 处理方式 |
|------|----------|
| 链接无效 | 提示用户检查链接是否有效 |
| 系统繁忙 | 提示稍后重试 |
| 积分不足 | 提示前往红狐hub充值 |

> ⛔ **重要：** 当 API 返回异常时，直接向用户展示 API 原始错误信息，**不得**通过浏览器或其他方式访问链接内容作为回退方案。

---

## 脚本参考

- API 调用脚本：`scripts/parse_video_download.py`
- 超时设置：30 秒
- 错误码映射: 非 200/2000 返回码直接透传 API `msg` 字段；内置友好映射兜底
