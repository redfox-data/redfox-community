# Core Workflow

## Step 1：提取搜索关键词

从用户自然语言描述中提取搜索意图和关键词，作为 `inquiryText` 传入。

## Step 2：调用搜索脚本

```bash
python3 ~/.agents/skills/deepseek-websearch/scripts/deepseek_search.py "<搜索关键词>"
```

脚本自动完成以下流程：
1. **提交搜索**：`POST /story/api/deepSearch/dsSubmit`，传入 `{"inquiryText": "..."}`
2. **轮询结果**：每 5 秒 `POST /story/api/deepSearch/dsResult` 查询一次，直到状态为 `succeeded`
3. **实时反馈**：轮询期间通过 stderr 输出等待提示（状态：queued → running → succeeded）
4. **最终输出**：状态 `succeeded` 后输出完整 JSON 结果到 stdout

## Step 3：展示结果

脚本返回 JSON 后，提取 `data.result.content` 中的 Deepseek 回答文本和 `data.result.search_result` 中的引用来源，结构化整理后向用户展示。
