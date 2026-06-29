# Core Workflow

## 执行工作流程

1. **需求确认**：明确调查目标、范围、时间约束
2. **策略编排**：根据目标选择引擎组合与搜索轮次
3. **广域扫描**（第1轮）：广泛关键词搜索，建立全景认知
4. **深度挖掘**（第2轮）：细分关键词，挖掘真实反馈
5. **交叉验证**（第3轮）：多源比对，确认关键数据可信度
6. **报告生成**：输出结构化调查报告，保存至红狐平台

---

## 调查模式

| 模式 | 调查目标 |
|------|---------|
| A股情报调查 | A股公司基本面、行业赛道、概念热点、资金动态、公告事件 |
| 竞品情报调查 | 分析竞品产品、市场策略、用户口碑 |
| 舆情事件调查 | 热点事件追踪、舆论走向分析、危机监测 |
| 人物背景调查 | 商务合作前的背景调查、行业人物了解 |
| 信息交叉验证 | 验证信息真实性、对比不同来源说法 |

### A股情报调查 — 搜索策略编排

| 轮次 | 引擎 | 搜索策略 |
|------|------|---------|
| 第1轮 | Baidu, 东方财富, 同花顺 | 公司概况+财务数据+行业地位 |
| 第2轮 | 雪球, 巨潮资讯, 证券时报 | 公告研报+投资者讨论+机构观点 |
| 第3轮 | 新浪财经, 东方财富, Baidu | 财务数据多源比对+舆情核实 |

**关键词构建：**
- 第1轮：`{股票名称/代码} 基本面 财报 主营业务` / `{行业} 龙头 竞争格局`
- 第2轮：`site:xueqiu.com {股票名称}` / `site:cninfo.com.cn {股票代码}` / `{股票名称} 研报 评级 目标价`
- 第3轮：`{股票名称} 营收 净利润 增长率` / `{概念/行业} 政策 利好 利空`

**输出维度：** 公司概况、财务表现、行业赛道、概念热度、资金动态、舆论风向、机构观点、风险提示、综合评估、调查结论

### 竞品情报调查 — 搜索策略编排

| 轮次 | 引擎 | 搜索策略 |
|------|------|---------|
| 第1轮 | Baidu, Google, Bing INT | 广泛关键词，建立全景 |
| 第2轮 | WeChat, Toutiao, DuckDuckGo | 细分关键词，挖掘真实反馈 |
| 第3轮 | Baidu, Google, Brave | 关键数据多源验证 |

**关键词构建：**
- 第1轮：`{竞品名} 产品 功能 定价`
- 第2轮：`{竞品名} 使用体验 测评 评价` / `site:reddit.com {竞品名} review`
- 第3轮：`{竞品名} 融资 营收 市场份额`

**输出维度：** 产品定位、核心功能、用户口碑、市场表现、竞争优势、潜在风险

### 舆情事件调查 — 搜索策略编排

| 轮次 | 引擎 | 搜索策略 |
|------|------|---------|
| 第1轮 | Baidu, Google(tbs=qdr:d), Toutiao | 时间过滤+热点词 |
| 第2轮 | WeChat, Sogou, DuckDuckGo | 评论区+论坛+自媒体 |
| 第3轮 | Google(tbs=qdr:w), Bing INT | 追溯事件发展脉络 |

**关键词构建：**
- 第1轮：`{事件关键词}` (加时间过滤)
- 第2轮：`{事件关键词} 评论 分析 观点` / `site:reddit.com {事件}`
- 第3轮：`{事件关键词} 时间线 经过 回顾`

**输出结构：** 时间线、舆论分布（支持/反对/中立）、待验证信息、关键结论

### 人物背景调查 — 搜索策略编排

| 轮次 | 引擎 | 搜索策略 |
|------|------|---------|
| 第1轮 | Baidu, Google, Bing INT | 姓名+职务+公司 |
| 第2轮 | DuckDuckGo(!gh), Google Scholar | 学术/技术成果 |
| 第3轮 | Baidu, Google, WeChat | 争议+诉讼+负面 |

**关键词构建：**
- 第1轮：`{人物名} 简介 背景 职务` / `{人物名} biography`
- 第2轮：`!gh {人物名}` / `author:"{人物名}"`
- 第3轮：`{人物名} 争议 诉讼 负面` / `{人物名} controversy`

**输出维度：** 身份信息、职业履历、专业成就、行业口碑、风险信号、综合评估

### 信息交叉验证 — 搜索策略编排

| 轮次 | 引擎 | 搜索策略 |
|------|------|---------|
| 第1轮 | Google(精确匹配), Baidu | 引号包裹+精确搜索 |
| 第2轮 | DuckDuckGo, Brave, Startpage | 同一关键词不同引擎 |
| 第3轮 | WolframAlpha, Google(site:权威站) | 官方信源确认 |

**关键词构建：**
- 第1轮：`"{待验证信息}"`
- 第2轮：`{待验证信息核心关键词}` (不同引擎)
- 第3轮：`site:gov.cn {关键词}` / WolframAlpha计算

---

## 引擎选择策略

### 决策树

```
用户输入调查需求
├── A股/股票/财经相关？
│   └── 是 → 必选: Baidu + 东方财富 + 雪球 + 巨潮资讯
├── 包含中文关键词？
│   └── 是 → 必选: Baidu + WeChat + Toutiao
├── 需要国际视角？
│   └── 是 → 必选: Google + DuckDuckGo/Brave
├── 信息敏感/需隐私？
│   └── 是 → 优先: DuckDuckGo + Startpage + Qwant
├── 需要时间线/实时性？
│   ├── 小时级 → Google(tbs=qdr:h) + Brave
│   └── 天级 → Google(tbs=qdr:d) + Baidu
├── 需要数据验证？
│   └── 是 → WolframAlpha + Google Scholar
└── 需要技术深度？
    └── 是 → DuckDuckGo(!gh !so !npm)
```

### 按调查目标选引擎

| 调查目标 | 首选引擎 | 备选引擎 |
|---------|---------|---------|
| A股情报 | Baidu + 东方财富/同花顺 + 雪球 + 巨潮资讯 | 新浪财经、证券时报 |
| 中文舆情 | Baidu + WeChat + Toutiao | Sogou, 360 |
| 国际视野 | Google + Brave + Yahoo | Bing INT, Ecosia |
| 隐私敏感 | DuckDuckGo + Startpage | Brave, Qwant |
| 学术验证 | Google Scholar + WolframAlpha | Google |
| 技术调查 | DuckDuckGo(!gh !so) + Google | Brave |
| 交叉验证 | 多引擎同时搜索 | 全引擎 |

### 按地区选引擎

| 地区视角 | 引擎 |
|---------|------|
| 中国大陆 | Baidu, Sogou, 360, WeChat, Toutiao |
| 国际视角 | Google, Bing INT, Yahoo, Brave |
| 隐私保护 | DuckDuckGo, Startpage, Qwant |
| 知识计算 | WolframAlpha |

### 引擎独有能力

| 引擎 | 独有能力 | 最佳场景 |
|------|---------|---------|
| Google | 最全索引+高级操作符+时间过滤+语言筛选 | 所有调查的基础引擎 |
| Baidu | 中文内容最全+知道/贴吧/百科 | 国内舆情+竞品口碑 |
| DuckDuckGo | Bangs直达(!gh !so !w !a)+无追踪 | 技术调查+隐私调查 |
| WeChat搜狗 | 微信公众号文章搜索 | 深度分析文章+行业观察 |
| Toutiao | 自媒体+热点追踪+实时性 | 热点事件+舆论走向 |
| Brave | 独立索引+无偏见+Discussions | 无过滤信息+论坛观点 |
| Startpage | Google结果+隐私保护 | 需Google结果但保护隐私 |
| WolframAlpha | 结构化数据+知识计算 | 数据验证+数值型信息 |
| Bing INT | 中文界面+国际搜索结果 | 跨国调查+国际对比 |
| Sogou | 微信+知乎内容 | 中文社区深度内容 |
| 东方财富 | 实时行情+财务数据+股吧社区+F10资料 | A股基本面+资金流向+散户舆情 |
| 同花顺 | 行情数据+题材概念+问财AI+机构研报 | A股概念热度+技术面分析 |
| 雪球 | 投资者社区+大V观点+组合追踪 | A股深度讨论+机构/牛散观点 |
| 巨潮资讯 | 证监会指定披露平台+公告原文 | A股官方公告+年报/季报原文 |
| 新浪财经 | 财经新闻+实时行情+机构评级汇总 | A股事件驱动+市场情绪监测 |
| 证券时报 | 证监会指定披露媒体+深度财经报道 | A股政策解读+上市公司调查报道 |

---

## 高级搜索策略

### 反向搜索法

通过已知信息反推更多细节：

```
已知：公司名 → 反向搜索
├── Google: "site:linkedin.com {公司名}"
├── DuckDuckGo: "!gh {公司名}"
├── Baidu: "{公司名} 团队 创始人"
└── Google: "{公司名} filetype:pdf"
```

### 时间轴搜索法

追踪事件/信息随时间的变化：

```
├── Google: "{关键词}&tbs=qdr:h" (1小时内)
├── Google: "{关键词}&tbs=qdr:d" (24小时内)
├── Google: "{关键词}&tbs=qdr:w" (1周内)
└── Google: "{关键词}&tbs=qdr:m" (1月内)
```

### 地域对比法

对比不同地区的信息差异：

```
├── Baidu: "{关键词}" (中国视角)
├── Google: "{关键词}&gl=us" (美国视角)
├── Google HK: "{关键词}" (香港视角)
└── Ecosia: "{关键词}" (欧洲视角)
```

### 垂直深耕法

在特定平台深入挖掘：

```
├── Google: "site:reddit.com {关键词}" (Reddit社区)
├── Google: "site:zhihu.com {关键词}" (知乎)
├── Google: "site:github.com {关键词}" (开源项目)
├── Google: "site:crunchbase.com {关键词}" (融资数据)
├── WeChat: "{关键词}" (公众号深度文章)
├── Baidu: "site:xueqiu.com {股票名}" (雪球投资者社区)
├── Baidu: "site:cninfo.com.cn {股票代码}" (巨潮公告原文)
├── Baidu: "site:eastmoney.com {股票名} 研报" (东方财富研报)
├── Baidu: "site:10jqka.com.cn {股票名} 概念" (同花顺概念板块)
└── Baidu: "site:stcn.com {行业/政策}" (证券时报深度报道)
```

### 证据链构建法

构建完整证据链确认信息：

```
信息A（待验证）
├── 寻找首发源 → 源头是官方还是转载？
├── 确认传播路径 → 哪些媒体引用了？
├── 检查是否有反驳 → 搜索"辟谣"+"信息关键词"
├── 权威信源验证 → site:gov.cn / site:reuters.com
└── 数据验证 → WolframAlpha（如适用）
```

---

## 可信度标注规范

| 标识 | 含义 | 判定标准 |
|------|------|---------|
| ✅ 已确认 | 信息可靠 | 2+个独立来源一致 |
| ⚠️ 待确认 | 有争议 | 来源说法矛盾 |
| ❌ 已否定 | 信息不实 | 权威信源反驳 |
| 🔍 单一来源 | 仅1个来源 | 需进一步验证 |

### 信息源分级（ABCD）

| 级别 | 类型 | 示例 |
|------|------|------|
| A级 | 官方/政府/权威媒体 | gov.cn, reuters.com, xinhua.net, cninfo.com.cn(巨潮), sse.com.cn(上交所), szse.cn(深交所) |
| B级 | 行业媒体/专业平台 | 36kr, techcrunch.com, eastmoney.com(东方财富), 10jqka.com.cn(同花顺), stcn.com(证券时报), cnstock.com(上海证券报) |
| C级 | 社交媒体/自媒体 | weibo, zhihu, reddit, xueqiu.com(雪球) |
| D级 | 匿名/未验证来源 | 贴吧, 4chan, 股吧匿名帖 |

---

## 常见调查场景引擎组合速查

| 调查场景 | 推荐引擎组合 | 时间过滤 | 关键操作符 |
|---------|------------|---------|-----------|
| A股公司基本面 | Baidu+东方财富+同花顺+巨潮资讯+雪球 | 近1季/1年 | `site:cninfo.com.cn` `site:xueqiu.com` |
| A股行业/概念分析 | Baidu+东方财富+同花顺+证券时报+新浪财经 | 近1月 | `site:10jqka.com.cn` `filetype:pdf` |
| A股公告/事件追踪 | Baidu+巨潮资讯+东方财富+新浪财经+雪球 | 近1天/1周 | `site:cninfo.com.cn` `tbs=qdr:d` |
| A股资金/舆情监控 | 东方财富+雪球+同花顺+新浪财经 | 近1天 | `site:guba.eastmoney.com` `site:xueqiu.com` |
| 产品竞品分析 | Baidu+Google+WeChat+DuckDuckGo | 近1月 | `site:` `""` |
| 公司背景调查 | Baidu+Google+Bing INT+WeChat | 无限制 | `site:linkedin.com` |
| 热点事件追踪 | Baidu+Toutiao+Google+WeChat | 近1天/1周 | `tbs=qdr:d` |
| 人物背景验证 | Baidu+Google+DuckDuckGo(!gh) | 无限制 | `""` `site:` |
| 融资数据验证 | Google+Baidu+WolframAlpha | 近1年 | `site:crunchbase.com` |
| 用户口碑收集 | WeChat+Toutiao+DuckDuckGo+Brave | 近1月 | `site:reddit.com` |
| 技术栈调查 | DuckDuckGo(!gh !so)+Google | 无限制 | `!gh` `!so` `site:` |
| 学术论文验证 | Google Scholar+Google+DuckDuckGo | 近2年 | `site:arxiv.org` |
| 法律诉讼排查 | Baidu+Google+Bing INT | 无限制 | `site:court.gov.cn` |

---

## 使用示例

### A股情报调查

```text
用户：帮我调查一下宁德时代这家公司

执行：
1. 广域扫描 → Baidu/东方财富/同花顺 搜索公司基本面与行业地位
2. 深度挖掘 → 雪球/巨潮资讯/证券时报 搜索公告研报与投资者讨论
3. 交叉验证 → 新浪财经/Google 验证财务数据与机构评级
输出：结构化A股情报调查报告
```

### 竞品产品调查

```text
用户：帮我调查一下 Notion 这个产品

执行：
1. 广域扫描 → Baidu/Google/Bing INT 搜索产品功能与对比
2. 深度挖掘 → WeChat/Toutiao/DuckDuckGo 搜索测评与用户反馈
3. 交叉验证 → Google/Brave 验证融资数据与市场份额
输出：结构化竞品调查报告
```

### 信息验证

```text
用户：验证"XX公司获得10亿融资"是否属实

执行：
1. 信息溯源 → Google/Baidu 精确匹配搜索
2. 多源比对 → DuckDuckGo/Brave/Startpage 跨引擎比对
3. 权威验证 → site:crunchbase.com / site:bloomberg.com
输出：信息验证报告（确认/否定/待确认）
```
