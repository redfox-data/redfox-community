# 短剧-抖音信息源 - 使用示例

## 示例 1:查询今日短剧爆款日报

```bash
python3 scripts/playlet_douyin_daily.py --latest
```

**预期输出**:
```
## 短剧-抖音信息源 · 2026-06-17 日报

**扫描 186 部热门短剧,聚类 8 个题材方向**

---

### 题材概览

| 题材 | 数量 | 占比 | 爆款亮点 |
|------|------|------|---------|
| #穿越 | 45部 | 24.2% | 《重生之穿越大明》点赞52.3w |
| #霸总 | 38部 | 20.4% | 《霸总的替身娇妻》点赞48.1w |
| ... | ... | ... | ... |
```

---

## 示例 2:查询穿越题材短剧

```bash
python3 scripts/playlet_douyin_daily.py --topics "穿越"
```

**说明**:专注查询穿越题材的短剧内容

---

## 示例 3:查询多个题材组合

```bash
python3 scripts/playlet_douyin_daily.py --topics "穿越,霸总,重生"
```

**说明**:同时查询三个热门题材的短剧,自动去重

---

## 示例 4:查询6月份的短剧内容

```bash
python3 scripts/playlet_douyin_daily.py \
  --start-time "2026-06-01 00:00:00" \
  --end-time "2026-06-30 23:59:59"
```

---

## 示例 5:组合查询(穿越题材+6月)

```bash
python3 scripts/playlet_douyin_daily.py \
  --topics "穿越" \
  --start-time "2026-06-01 00:00:00" \
  --end-time "2026-06-17 23:59:59" \
  --count 100
```

**说明**:
- 同时使用题材、时间范围筛选
- `count=100` 表示扫描100部作品

---

## 示例 6:使用缓存数据

```bash
python3 scripts/playlet_douyin_daily.py --from-cache
```

**说明**:如果1小时内有缓存,直接使用缓存数据,节省API积分

---

## 示例 7:查询指定日期

```bash
python3 scripts/playlet_douyin_daily.py --date 2026-06-10
```

**说明**:查询历史日期数据,无需用户确认

---

## 示例 8:开启每日订阅

```bash
python3 scripts/playlet_douyin_daily.py --subscribe
```

**说明**:开启后每日自动生成日报,保存在 `~/Downloads/QoderReports/`

---

## 示例 9:查询悬疑题材短剧

```bash
python3 scripts/playlet_douyin_daily.py --topics "悬疑,推理,反转"
```

**说明**:查询悬疑类短剧,包含相关关键词

---

## 示例 10:查询甜宠题材短剧

```bash
python3 scripts/playlet_douyin_daily.py --topics "甜宠,恋爱,撒糖"
```

**说明**:查询甜宠类短剧

---

## 题材参数速查

| 题材类型 | 典型关键词 | 示例命令 |
|---------|-----------|---------|
| 穿越 | 穿越、时空、古代、现代 | `--topics "穿越"` |
| 霸总 | 霸总、总裁、豪门 | `--topics "霸总"` |
| 重生 | 重生、回到、逆袭 | `--topics "重生"` |
| 悬疑 | 悬疑、推理、反转、惊悚 | `--topics "悬疑"` |
| 甜宠 | 甜宠、恋爱、撒糖 | `--topics "甜宠"` |
| 逆袭 | 逆袭、翻身、打脸 | `--topics "逆袭"` |

---

## 常见用法组合

### 创作者日常使用
```bash
# 查看今日短剧爆款
python3 scripts/playlet_douyin_daily.py --latest
```

### 创作者选题参考
```bash
# 查看特定题材的热门作品
python3 scripts/playlet_douyin_daily.py --topics "穿越,重生" --count 100
```

### 运营人员趋势分析
```bash
# 查看本月短剧趋势
python3 scripts/playlet_douyin_daily.py \
  --start-time "2026-06-01 00:00:00" \
  --end-time "2026-06-30 23:59:59" \
  --count 200
```

### 题材对比分析
```bash
# 对比穿越和霸总题材
python3 scripts/playlet_douyin_daily.py --topics "穿越,霸总" --count 150
```

---

## 数据说明

- **数据更新**:每日15:00更新前一天的数据
- **数据来源**:红狐Hub 抖音短剧创作数据API
- **平台**:固定为抖音(platform=1)
- **内容类型**:固定为短剧(msgType="短剧")
- **缓存策略**:1小时内可复用缓存
