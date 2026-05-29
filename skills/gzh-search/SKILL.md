---
name: gzh-search
description: 公众号文章搜索 — 通过关键字搜索微信公众号文章，终端表格展示，一键导出 Excel 并生成可交互 HTML 报告。
---

# 公众号文章搜索

你的公众号内容搜索引擎。输入任意关键词，实时搜索微信公众号文章，终端表格清晰展示：标题、作者、阅读数、点赞数、分享数、收藏数、发布时间，数据一键导出 Excel，并生成带搜索框的交互式 HTML 报告。

> **API Source**: `公众号搜索SkillHub` — 所有 API 请求均携带此标识，用于区分不同 Skill 的调用来源。

---

## 首次使用

**开箱即用 — 粘贴命令就能跑**

内置公共 API Key，约 **10000 次免费额度**，零配置直接用：

```bash
# 搜索公众号文章
python3 "$SKILL_PATH/assets/search.py" "人工智能"

# 指定排序方式和每页数量
python3 "$SKILL_PATH/assets/search.py" "AI Agent" --sort-type default --page-size 20

# 生成并打开交互式 HTML 报告
python3 "$SKILL_PATH/assets/search.py" "大模型" --open
```

HTML 报告页面内置搜索框，支持实时调接口查询任意关键词的公众号文章，结果以卡片形式展示（标题、作者、阅读/点赞/分享/收藏数据），点击卡片直跳原文阅读。

CSV 数据文件保存在 `~/Downloads/QoderGzhSearch/` 目录。

---

## 后续使用

免费额度用完后，前往 [redfox.hk/login](https://www.redfox.hk/login) 注册账号获取自己的 API Token：

| 配置方式 | 说明 | 命令 |
|----------|------|------|
| **环境变量**（推荐） | 设置一次，全局生效 | `export X_API_KEY=ak_你的密钥` |
| **命令行参数** | 临时使用 | `python3 "$SKILL_PATH/assets/search.py" "关键词" --api-key ak_你的密钥` |
| **配置文件** | 持久化存储 | `echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 功能特点

- **关键词搜索**：输入任意关键词，实时查询微信公众号文章
- **终端表格展示**：标题、作者、阅读数、点赞数、分享数、收藏数、发布时间一览无余
- **数据导出**：搜索完成后自动生成 CSV 文件，方便数据分析
- **HTML 交互报告**：生成自包含 HTML 页面，内置搜索框支持实时调接口查询
- **原文直达**：在 HTML 报告中点击任意文章卡片，直接跳转到公众号文章阅读链接
- **本地服务模式**：内置 HTTP 服务代理 API 请求，避免浏览器跨域限制

---

## 使用方式

### 基础搜索

```bash
# 搜索指定关键词的公众号文章
python3 "$SKILL_PATH/assets/search.py" "人工智能"

# 一次搜索多个关键词（分别执行，可手动多次调用）
python3 "$SKILL_PATH/assets/search.py" "AI Agent"
python3 "$SKILL_PATH/assets/search.py" "大模型"
python3 "$SKILL_PATH/assets/search.py" "ChatGPT"
```

### 高级参数

```bash
# 指定获取数量（API 每页固定约 20 条，多页自动翻页）
python3 "$SKILL_PATH/assets/search.py" "AI" --count 50

# 不自动打开浏览器
python3 "$SKILL_PATH/assets/search.py" "AI" --no-open

# 指定输出目录
python3 "$SKILL_PATH/assets/search.py" "AI" --output-dir ~/Desktop

# 只生成 CSV 不生成 HTML
python3 "$SKILL_PATH/assets/search.py" "AI" --csv-only
```

### 交互式 HTML 报告

运行搜索后自动生成 HTML 报告并打开浏览器。在 HTML 页面的搜索框中输入关键词，可实时调接口搜索更多公众号文章，无需重新运行脚本。

报告特性：
- 深色主题，响应式布局
- 搜索框支持防抖输入（300ms 延迟）
- 每篇文章展示：标题、作者、阅读数、点赞数、分享数、收藏数、发布时间
- 点击文章卡片直接跳转到公众号原文
- 支持分页加载更多

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `keyword` | 搜索关键词（必填，位置参数） | — |
| `--count` | 获取文章数量，多页自动翻页 | `20` |
| `--sort-type` | 排序方式：default / time | `default` |
| `--output-dir` | 输出目录 | `~/Downloads/QoderGzhSearch` |
| `--api-key` | 指定 API Key | — |
| `--open` | 自动打开浏览器查看 HTML 报告 | 默认开启 |
| `--no-open` | 不自动打开浏览器 | — |
| `--csv-only` | 仅生成 CSV 文件，不生成 HTML | — |
| `--port` | HTML 报告本地服务端口 | `8766` |

### 依赖安装

| 依赖 | 安装命令 |
|------|----------|
| `requests` | `pip3 install requests` |

---

## 常见问题

**Q：搜索范围是什么？**
A：搜索全量微信公众号文章，不限定特定领域或账号。

**Q：最多一次性返回多少条数据？**
A：单次请求默认返回 20 条，可通过 `--page-size` 调整。HTML 报告页面支持分页加载更多结果。

**Q：数据保存在哪？**
A：CSV 文件默认保存在 `~/Downloads/QoderGzhSearch/`，文件名格式 `公众号搜索_[关键词]_2026-05-27.csv`。

**Q：为什么 HTML 报告需要本地服务？**
A：浏览器直接打开 HTML 文件时可能存在跨域限制，无法直接调用 redfox.hk API。内置本地 HTTP 服务作为代理中转，确保搜索功能正常。

**Q：搜索有文章封面图吗？**
A：搜索接口暂不返回封面图，HTML 报告中使用文章标题首字作为卡片视觉标识。

**Q：额度用完了怎么办？**
A：前往 [redfox.hk/login](https://www.redfox.hk/login) 注册获取免费 API Token。

---

## 获取方式

本 Skill 可在以下平台找到：

- [SkillHub](https://skillhub.cn)
- [ClawHub](https://clawhub.com)
- [GitHub](https://github.com)
