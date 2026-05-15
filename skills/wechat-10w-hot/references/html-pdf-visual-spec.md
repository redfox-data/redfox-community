# HTML / PDF 视觉与生成规范

## 视觉规范（生成 HTML 时必须遵守）

**主题色调**

- 主色：`rgb(0, 179, 84)`（微信绿）
- 辅助色：`#0088ff`（阅读数、用户名称）
- 背景：`#fff`

**布局**

- 序号：前 3 条用 🥇🥈🥉，其余用数字；序号在标题左侧。
- 用户、类型、阅读数、发布时间之间用 **浅灰竖线** `|` 分隔；竖线高度缩短一半并垂直居中。
- **阅读量排序标签** 与 **导出 PDF** 按钮放在标题右侧。
- **头部不出现**「爆款研究院」等品牌块，保持简洁。

**图标**

- 用户：`👤`（无背景）
- 阅读：`📖`
- 时间：`📅`

**元素**

- 用户名：`#0088ff`，可点击跳转公众号名片：  
  `https://open.weixin.qq.com/qr/code?username={accountId}`
- 阅读数：`#0088ff`
- 「爆款规律分析」区块：无左边框，白底 + 浅绿衬底。

## PDF（html2pdf.js）

- 按钮在标题右侧，紧邻阅读量排序标签；**蓝色渐变底、白字、12px**。
- **单页自适应**：按内容宽高估算纸张，**整页不分页**。
- 配置要点：`pagebreak: { mode: 'none' }`、`margin: 0`；对 `article-item`、`article-list`、`content` 等加 `page-break-inside: avoid` 与 `break-inside: avoid`。

## 生成 HTML 脚本

- 脚本：`scripts/generate_hot_html.py`
- 默认读 `temp_articles.json`（由 `fetch_hot_articles.py` 写出）。

**关键参数**

| 参数 | 含义 |
|------|------|
| `--temp_file` | 临时 JSON，默认 `temp_articles.json` |
| `--output` | 输出 HTML 路径，建议 `{关键词}_热门榜单.html` |
| `--display_count` | **必须与对话中展示的条数一致**（preview 常填 10；full 常填 50；不足 10 条则填实际 N） |

**命令示例**

```bash
python scripts/generate_hot_html.py --temp_file temp_articles.json --output "热门文章_榜单.html" --display_count 10
python scripts/generate_hot_html.py --temp_file temp_articles.json --output "热门文章_榜单.html" --display_count 50
```

**生成前检查**

- 对话展示几条，HTML 就几条；标题 / 作者 / 阅读 / 时间 / 链接与对话一致。
- 临时文件即使有 50 条，若对话只展示 10 条，仍用 `--display_count 10`。

**生成后**

1. 使用 `preview_url` 预览 HTML（若环境提供该工具）。
2. 告知用户文件路径。
3. 询问是否需要微调样式。

**页脚文案（HTML）**

- 「公众号10w+阅读文章，每日更新最新爆文内容」
- 「备注：互动数据为入库快照，实时数据可能持续增长」
