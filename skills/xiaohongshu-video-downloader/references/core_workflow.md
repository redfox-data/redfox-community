# Core Workflow

## 官方示例链接

所有文档、错误提示、示例代码统一使用以下链接：

```
https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed
```

## 执行规则

- **用户提供带 `xsec_token` 参数的正确小红书链接时**：直接执行解析流程，无需额外确认或追问
- **用户未提供链接时**：提示用户输入小红书视频链接，并附上上方示例
- **用户提供的链接不是小红书链接时**：提示「该链接不是小红书视频链接」，附上示例链接，终止解析
- **用户提供的链接缺少 `xsec_token` 参数时**：提示「链接缺少 xsec_token 参数，无法解析」，附上示例链接，终止解析
- **接口返回链接格式错误（code=400 或 msg 含「链接格式/链接错误/xsec_token/link format」）时**：主动附上示例链接，引导用户重新传入带 `xsec_token` 的完整链接

## 脚本调用

### 单链接

```bash
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed"
```

### 批量链接（空格分隔，每个链接均需携带 `xsec_token`）

```bash
python3 "$SKILL_PATH/scripts/downloader.py" \
  "https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed" \
  "https://www.xiaohongshu.com/explore/<笔记ID2>?xsec_token=<token2>&xsec_source=pc_feed"
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `urls`（位置参数，必填） | 小红书视频链接（支持多个，空格分隔），**必须携带 `xsec_token` 参数** |
| `--api-key` | API Key（格式 ark_xxx，不传则读取环境变量或配置文件） |
| `--save-key` | 将本次传入的 API Key 保存到配置文件 |
| `--json` | 以 JSON 格式输出完整返回结果 |

## API Key 配置

优先级：CLI 参数 > 环境变量 > 配置文件

| 方式 | 命令 |
|------|------|
| **环境变量**（推荐） | `export REDFOX_API_KEY=ark_你的密钥` |
| **命令行参数** | `python3 "$SKILL_PATH/scripts/downloader.py" "<链接>" --api-key ark_你的密钥` |
| **配置文件** | `echo '{"api_key":"ark_你的密钥"}' > ~/.qoder/apis/redfox.json` |

### 首次使用

```bash
# 设置环境变量
export REDFOX_API_KEY=ark_你的密钥

# 解析视频，获取下载链接（链接必须携带 xsec_token）
python3 "$SKILL_PATH/scripts/downloader.py" "https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed"
```

> 前往 [redfox.hk](https://redfox.hk/settings/api-keys?source=github) 注册获取 API Key。

## API 调用细节

- **API 端点**：`https://redfox.hk/story/api/parseWork/videoDownload/xhs`
- **请求方法**：POST，Content-Type: application/json，Header: X-API-KEY
- **请求体**：`{"url": "<链接>", "source": "xhs/小红书视频下载-GitHub"}`
- **成功判断**：响应 code 以 2 开头（如 200、2000）
- **错误码**：3106=缺少 Key，3107=Key 无效，400=参数错误（通常是链接缺少 `xsec_token`）

## 输出格式

成功时依次输出：
1. 内容描述（完整原文）
2. 资源列表（类型/时长/下载链接/封面链接）
3. 有效期提醒

批量模式下最后汇总成功/失败数量。

## 链接校验

脚本对传入链接执行两级校验，任一失败即终止解析并附上示例链接：

1. **域名校验**：仅接受 `xiaohongshu.com`、`xhslink.com`（支持自动去除 `www.` 前缀）
2. **`xsec_token` 参数校验**：查询串中必须包含非空 `xsec_token` 参数

### 为什么必须携带 `xsec_token`

小红书接口对未携带 `xsec_token` 的链接会返回链接格式错误，无法完成解析。用户需要从 PC 网页或 App 分享入口复制完整链接（浏览器地址栏或分享面板复制出的链接默认已携带 `xsec_token`）。

### 校验失败提示模板

```
[✗] 链接缺少 xsec_token 参数，无法解析：<用户输入的链接>
  请传入带 xsec_token 参数的完整小红书链接，示例：
  https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed
  获取方式：在小红书 PC 网页或 App 中打开笔记 → 复制分享链接（链接需包含 xsec_token 参数）
```
