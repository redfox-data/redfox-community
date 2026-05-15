# 使用示例（场景 walkthrough）

## 示例 1：总榜（首次 preview）

**用户**：今日爆文  

**Agent**

- 识别：总榜；按当天时刻与 18:30 规则选 `start_date` / `end_date`（见 `time-and-date-rules.md`）。
- 执行示例（日期请替换为真实计算结果）：

```bash
python scripts/fetch_hot_articles.py \
  --type "总排名" \
  --start_date 2026-05-12 \
  --end_date 2026-05-13 \
  --mode preview \
  --limit 10
```

- 原样展示脚本输出 → 爆款规律分析 → 订阅询问 → 生成 HTML：`--display_count 10`。  
- 若总数 > 10：保留脚本自带「还有 X 条未展示」提示。

## 示例 2：领域（preview）

**用户**：推荐科技类的文章  

**Agent**

- 映射：`科技` → `科技数码`（详见 `category-mapping.md`）。
- 执行（日期替换为真实区间）：

```bash
python scripts/fetch_hot_articles.py \
  --type "科技数码" \
  --start_date 2026-05-13 \
  --end_date 2026-05-14 \
  --mode preview \
  --limit 10
```

- 后续同示例 1：`display_count=10`。

## 示例 3：用户要求看全量

承接示例 1，用户回复「是 / 全部展示」：

```bash
python scripts/fetch_hot_articles.py \
  --type "总排名" \
  --start_date 2026-05-12 \
  --end_date 2026-05-13 \
  --mode full
```

- 原样展示 → 规律分析 → 订阅询问 → HTML：`--display_count 50`（或与脚本实际最大条数一致）。

## 示例 4：结果 ≤ 10 条

冷门领域仅 5 条时：

```bash
python scripts/fetch_hot_articles.py \
  --type "学术研究" \
  --start_date 2026-05-13 \
  --end_date 2026-05-14 \
  --mode preview
```

- 无需追问是否展开；HTML 使用 `--display_count 5`。

## 示例 5：无数据

**用户**：极冷门胡编词  

**Agent**：脚本空结果 → 提示「未查询到相关10w+阅读文章数据」→ 建议改查「总排名」或列举其它标准分类供选。

示例话术：

```text
该领域在该时间段太冷门，暂无10w+文章，您可尝试查看综合10w+文章或者查看其他分类，如人文资讯、知识百科、健康养生、时尚潮流、美食餐饮、乐活生活、旅游出行、搞笑幽默、情感心理、体育娱乐、美容美体、文摘精选、民生资讯、财富理财、科技数码、创投商业、汽车交通、房产楼市、职场发展、教育考试、学术研究
```
