# 语气 × 读者 × IP 三维配置矩阵

> 解决"风格与 IP 人设冲突"问题。
> 三个维度正交：用户调用时只需选 3 个标签，框架自动装配。

---

## 维度 1：语气（tone）

| 标签 | 适合场景 | 语言特征 |
|------|---------|---------|
| `direct`（直白坦率，默认） | 运营干货、工具测评、踩坑警示 | "别只看粉丝数""这个方法不适用于" |
| `professional`（专业严谨） | 方法论、行业分析、深度报告 | "从数据分布看""结合 X 指标判断" |
| `casual`（轻松对话） | 入门科普、个人故事、随笔 | "我有个朋友""说真的""其实没那么玄" |

## 维度 2：读者（audience）

| 标签 | 表达侧重 | 示例句 |
|------|---------|--------|
| `individual`（个体创作者，默认） | 个人可执行、周计划、案例驱动 | "你下周可以这样安排" |
| `team`（团队/企业） | 工具系统、协同流程、价值量化 | "建议团队每周同步一次" |

## 维度 3：视觉 IP（visualPersona）

| 标签 | 风格 | 适用场景 |
|------|------|---------|
| `redfox`（红狐讲解员，默认） | 红色狐狸 + 美式复古报刊 + 圆框眼镜 | 亲切科普、入门向 |
| `analyst`（严肃分析师） | 深色西装 + 商务报表 + 数据可视化 | 深度分析、行业研究 |
| `none`（无 IP） | 纯文字/纯图，无人物 | 资讯类、官方公告 |

---

## 18 种组合的完整配置

### direct × individual × redfox（默认组合）
- **语气**：直白坦率 + 经验分享感
- **读者**：个人可执行方法、周计划、中腰部账号案例
- **IP**：红狐讲解员，姿态随章节切换（封面=欢迎/分析=前倾/方法论=托腮/操作=打字）
- **典型文章**：找对标账号、运营工具推荐、入门指南

### direct × individual × analyst
- **语气**：直白坦率
- **读者**：个体创作者
- **IP**：无人物，改为数据仪表盘/流程图/对比表
- **典型文章**：硬核拆解、对比测评、行业揭秘

### direct × individual × none
- **语气**：直白坦率
- **读者**：个体创作者
- **IP**：无视觉 IP，纯文字+表格
- **典型文章**：纯干货清单、工具清单

### direct × team × redfox
- **语气**：直白坦率
- **读者**：团队/企业
- **IP**：红狐讲解员
- **典型文章**：团队协作指南、内部 SOP

### direct × team × analyst
- **语气**：直白坦率
- **读者**：团队/企业
- **IP**：数据仪表盘
- **典型文章**：竞品分析、ROI 评估

### direct × team × none
- **语气**：直白坦率
- **读者**：团队/企业
- **IP**：无
- **典型文章**：内部备忘录、流程文档

### professional × individual × redfox
- **语气**：专业严谨
- **读者**：个人创作者
- **IP**：红狐讲解员（亲和力缓和专业感）
- **典型文章**：深度方法论个人版、行业研究入门

### professional × individual × analyst
- **语气**：专业严谨
- **读者**：个人创作者
- **IP**：数据可视化
- **典型文章**：硬核研究、数据解读

### professional × individual × none
- **语气**：专业严谨
- **读者**：个人创作者
- **IP**：无
- **典型文章**：纯学术风干货

### professional × team × redfox
- **语气**：专业严谨
- **读者**：团队/企业
- **IP**：红狐讲解员
- **典型文章**：企业内训、团队白皮书

### professional × team × analyst
- **语气**：专业严谨
- **读者**：团队/企业
- **IP**：数据仪表盘
- **典型文章**：行业报告、商业分析（最常用）

### professional × team × none
- **语气**：专业严谨
- **读者**：团队/企业
- **IP**：无
- **典型文章**：白皮书、官方报告

### casual × individual × redfox
- **语气**：轻松对话
- **读者**：个人创作者
- **IP**：红狐讲解员
- **典型文章**：随笔、个人故事、入门科普

### casual × individual × analyst
- **语气**：轻松对话
- **读者**：个人创作者
- **IP**：数据仪表盘（轻松语言 + 严肃图表的张力）
- **典型文章**：趣味数据解读、轻松测评

### casual × individual × none
- **语气**：轻松对话
- **读者**：个人创作者
- **IP**：无
- **典型文章**：博客随笔、社交媒体长文

### casual × team × redfox
- **语气**：轻松对话
- **读者**：团队/企业
- **IP**：红狐讲解员
- **典型文章**：团队文化、内部沟通

### casual × team × analyst
- **语气**：轻松对话
- **读者**：团队/企业
- **IP**：数据仪表盘
- **典型文章**：轻松向行业分析

### casual × team × none
- **语气**：轻松对话
- **读者**：团队/企业
- **IP**：无
- **典型文章**：团队通讯、轻松公告

---

## 使用方式

### 显式指定（推荐）

```bash
# 链接仿写
python scripts/generate_image.py \
  --prompt "..." \
  --reference-image "https://xxx.com/img.jpg" \
  --style reference \
  --persona direct-individual-analyst \
  --api-key "ak_xxx"
```

### 隐式默认

未指定时使用 `direct-individual-redfox`（默认组合）。

### 切换 IP 风格时的注意事项

- `redfox → analyst`：去掉狐狸描述，改为"商务感/数据仪表盘/极简线条"
- `analyst → redfox`：追加红狐讲解员姿态描述
- `xxx → none`：去掉所有 IP 描述，prompt 保持原始

风格切换由 `generate_image.py` 的 `--style` 参数控制（已实现）：
- `--style redfox`：自动追加红狐风格
- `--style reference`：原 prompt 不变（参考图自带）
- `--style none`：原 prompt 不变（无风格）

---

## 与 tonePreference 参数的兼容性

旧的 `tonePreference` 参数保留作为简写：
- `tonePreference=直白坦率` → `direct`
- `tonePreference=专业严谨` → `professional`
- `tonePreference=轻松对话` → `casual`

旧的 `targetAudience` 参数保留作为简写：
- `targetAudience=个体创作者` → `individual`
- `targetAudience=团队企业` → `team`

新参数优先级：显式三标签组合 > 旧的 tonePreference/targetAudience > 默认值。
