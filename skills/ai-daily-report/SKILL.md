---
name: ai-hot-articles
description: AI公众号热门爆款 — 每天帮你盯盘全网 AI 公众号，按阅读量找出最火的爆款内容，自动聚类生成精美 HTML 日报。
---

# AI公众号热门爆款

你的 AI 内容雷达。每天自动扫描全网 AI 公众号，把阅读量最高的爆款文章找出来，按话题智能聚类，一份精美的 HTML 日报送到你手里。

> **API Source**: `AI公众号热门爆款-SkillHub` — 所有 API 请求均携带此标识，用于区分不同 Skill 的调用来源。

---

## 首次使用

**开箱即用 — 粘贴命令就能跑**

内置公共 API Key，约 **10000 次免费额度**，零配置直接用：

```bash
python3 "$SKILL_PATH/assets/daily_report.py"
```

生成的 HTML 文件保存在 `~/Downloads/QoderReports/` 目录，自动在浏览器中打开。每篇文章带封面图、标题超链接、阅读/点赞/评论数据。

---

## 后续使用

免费额度用完后，前往 [redfox.hk/login](https://www.redfox.hk/login) 注册账号获取自己的 API Token：

| 配置方式 | 说明 | 命令 |
|----------|------|------|
| **环境变量**（推荐） | 设置一次，全局生效 | `export X_API_KEY=ak_你的密钥` |
| **命令行参数** | 临时使用 | `python3 "$SKILL_PATH/assets/daily_report.py" --api-key ak_你的密钥` |
| **配置文件** | 持久化存储 | `echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 功能特点

- **爆款发现**：从 200+ 篇 AI 公众号文章中，按阅读量筛选出最火的热门内容
- **智能聚类**：自动从当天内容中发现话题方向（Agent、大模型、AI绘画、提示词...），每天的分类由内容决定
- **可视化日报**：深色主题 + 橙色强调的精美 HTML 页面，带封面图、互动数据、文章直链
- **一键订阅**：`--subscribe` 即可开启每日自动产出，日报自动攒在本地文件夹
- **响应式设计**：手机、平板、桌面都能完美阅读

---

## 使用方式

### 生成今日爆款日报

```bash
python3 "$SKILL_PATH/assets/daily_report.py"
```

### 自定义关注方向

```bash
python3 "$SKILL_PATH/assets/daily_report.py" --keywords "AI Agent,RAG,LangChain,Prompt"
```

### 查看历史某天的热门

```bash
python3 "$SKILL_PATH/assets/daily_report.py" --date 2026-05-26
```

### 订阅每日爆款（每天 9:00 自动生成）

```bash
python3 "$SKILL_PATH/assets/daily_report.py" --subscribe
```

### 取消订阅

```bash
python3 "$SKILL_PATH/assets/daily_report.py" --unsubscribe
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--keywords` | 关注的话题方向，逗号分隔 | `AI,人工智能,大模型,GPT,Agent,AI绘画` |
| `--count` | 扫描文章数量 | `200` |
| `--date` | 指定日期 YYYY-MM-DD | 今天 |
| `--output-dir` | 输出目录 | `~/Downloads/QoderReports` |
| `--api-key` | 指定 API Key | - |
| `--subscribe` | 开启每日订阅 | - |
| `--unsubscribe` | 关闭每日订阅 | - |
| `--no-open` | 不自动打开浏览器 | - |

### 依赖安装

| 依赖 | 安装命令 |
|------|----------|
| `requests` | `pip3 install requests` |

---

## 常见问题

**Q：日报里的分类是怎么来的？**
A：完全由当天内容决定。系统从文章话题、分类标签和标题关键词中自动识别聚类，每天的热点方向不同，分类也会跟着变。

**Q：怎么看到更多文章？**
A：用 `--count 300` 扩大扫描范围，或通过 `--keywords` 添加更多关注方向。

**Q：订阅后日报存在哪？**
A：默认 `~/Downloads/QoderReports/`，文件名格式 `AI日报_2026-05-27.html`。

**Q：怎么自定义日报样式？**
A：修改 `$SKILL_PATH/assets/report_template.html` 中的 CSS 变量即可换色、换字体。

**Q：额度用完了怎么办？**
A：前往 [redfox.hk/login](https://www.redfox.hk/login) 注册获取免费 API Token。

---

## 获取方式

本 Skill 可在以下平台找到：

- [SkillHub](https://skillhub.cn)
- [ClawHub](https://clawhub.com)
- [GitHub](https://github.com)
