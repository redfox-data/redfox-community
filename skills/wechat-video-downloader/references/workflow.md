# 解析视频号下载地址 - 执行工作流

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

**请求体**: `{"url": "{视频号链接}"}`

**成功响应** (code=2000):
```json
{"code": 2000, "msg": "成功", "data": {"title": "...", "cover": "...", "videoUrl": "..."}}
```

---

## Step 3: 输出结果

### 成功输出模板

```markdown
## 🎬 视频号解析结果

**📌 标题：** {data.title}

**🖼️ 封面图：**

[封面图]({data.cover})

**🔗 下载地址：**

[点击下载视频]({data.videoUrl})

> 💡 下载地址为临时链接，建议及时保存
```

### 失败输出模板

```markdown
## ❌ 解析失败

**原因：** {错误信息}
```

> ⛔ 当 API 返回异常时，直接向用户展示 API 原始错误信息，**不得**通过浏览器或其他方式访问链接内容作为回退方案。
