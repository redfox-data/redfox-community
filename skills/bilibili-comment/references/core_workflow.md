# Core Workflow

## Step 1：理解用户意图，提取 bvId

- 从用户输入中提取 bvId（BV号）；若提供视频链接则从链接中提取
- 若用户未提供，主动询问：「请提供B站视频链接或BV号」
- 若上一轮已查询某视频且本轮输入模糊（如「下一页」「评论分析」），沿用上一轮 bvId

## Step 2：调用评论获取脚本

每次调用仅请求一页数据（一次 API 请求），不可擅自发起多次调用拉取多页。

```bash
python3 "$SKILL_PATH/scripts/bili_comment_search.py" "<bvId>" [--page <page>]
```

参数：`bvId`（必填）、`--page`（默认1）、`--output-dir`（默认 ~/Downloads/QoderReports）

脚本自动生成含 `{{PLACEHOLDER}}` 占位符的 HTML 报告（未回填分析数据）。

脚本返回 JSON 字段：`work_detail`、`total_count`、`total_fetched`、`has_next`、`comments`、`html_path`

## Step 3：对话中展示评论数据 + AI 总结

**A0（每次查询必须输出）** 作品详情（标题、UP主链接、发布时间、时长、播放/点赞/投币/收藏/分享/评论/弹幕数）；数字 ≥ 10000 使用 x.xw 格式。

**A1** 告知查询范围（获取条数）

**A2** 渲染评论表格：用户昵称带 Bilibili 主页链接、评论超40字截断加 `...`、时间格式 MM-DD HH:MM、点赞数 ≥ 10000 用 x.xw 格式；每页最多20条全部展示，不得截断。

**A3（每次查询必须输出）** 四维情感分析（积极/负面/需求/竞品）：
- 基于B站梗文化理解（awsl / 爷青回 / xswl / yyds / 绝绝子 等）
- 每条要点引用代表评论关键词/短语
- 百分比为各类评论占总评论数比例，四类总和可超100%
- 若 `total_fetched` < `work_detail.reply_count`，追加提示引导用户前往红狐平台

A0~A3 在同一轮输出中连续完成，不可省略任何一步。

A3 完毕后询问用户：「📊 是否需要生成 HTML 可视化报告？」

**用户确认后（无需重新调用脚本，HTML 已在 Step 2 生成）：**

**① 写入分析 JSON 文件（用 Python，确保 UTF-8）**

⚠️ 不可用 Write 工具写 JSON 文件（Windows 上默认 GBK 会损坏中文）。
必须用 Python 写：

```bash
python -c "import json; json.dump({分析数据}, open('temp.json','w',encoding='utf-8'), ensure_ascii=False)"
```

若 Python 字符串中含中文标点/引号导致 PowerShell 转义错误，改用 unicode 转义：
```bash
$env:PYTHONIOENCODING='utf-8'; python -c "import json; d={...}; open('temp.json','w',encoding='utf-8').write(json.dumps(d,ensure_ascii=False))"
```

**② 回填 AI 分析到 HTML（--json-file 绕过管道）**

```bash
python "$SKILL_PATH/scripts/backfill_html.py" "<html_path>" --json-file "<temp_json_file>"
```

JSON 字段：`positive_ratio`、`negative_ratio`、`demand_ratio`、`competitor_ratio`（纯整数）；
`positive_summary`、`negative_summary`、`demand_summary`、`competitor_summary`（HTML `<ul><li>` 格式）

**③ 打开 HTML 报告**
- Windows: `Start-Process "<html_path>"`
- macOS/Linux: `open "<html_path>"`

## Step 4：翻页处理

当用户回复「下一页」「上一页」「第N页」时：
1. 沿用已有 bvId，计算新 page 值（`offset = (page - 1) × 20`）
2. 重新调用脚本（`--page <page>`），脚本自动生成当页 HTML
3. 完整执行 Step 3（A1~A3），A3 后询问是否生成当前页 HTML
4. 翻页规则：`has_next=true` 有下一页；`has_next=false` 已是最后一页

## Step 5：错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 无 API Key | 提示配置 REDFOX_API_KEY，给出配置指引 |
| 视频链接无效 | 提示「未找到该视频的评论，请检查视频链接是否正确」 |
| 接口返回 502 错误 | 服务返回 502 错误，可能存在网络不稳定问题，请稍后重试 |
| 获取 0 条评论 | 提示「该视频暂无评论」并建议检查视频是否存在或已删除 |
| 网络请求超时 | 提示「网络请求超时，请稍后重试」 |
| 评论任务超时 | 提示「评论数据获取超时，请稍后重试」 |
| HTML 中文乱码 | 根本原因：Write 工具写 JSON 为 GBK 或 PowerShell 管道二次编码损坏。解决方案：用 Python `json.dump(ensure_ascii=False)` + `open(f,'w',encoding='utf-8')` 写 JSON，再用 `backfill_html.py --json-file` 直接读文件回填，全程不经过 Write 工具和管道 |
