# 引擎选择策略详解

## 一、决策树：如何选择引擎组合

```
用户输入调查需求
│
├── A股/股票/财经相关？
│   ├── 是 → 必选: Baidu + 东方财富 + 雪球 + 巨潮资讯
│   │   ├── 需要财报/公告 → 巨潮资讯 + 上交所/深交所 site:
│   │   ├── 需要资金/行情 → 东方财富 + 同花顺
│   │   ├── 需要舆情/讨论 → 雪球 + 新浪财经 + 证券时报
│   │   └── 需要研报/评级 → 东方财富研报中心 + 同花顺iFind
│   └── 否 → 继续判断
│
├── 包含中文关键词？
│   ├── 是 → 必选: Baidu + WeChat + Toutiao
│   └── 否 → 跳过国内引擎
│
├── 需要国际视角？
│   ├── 是 → 必选: Google + DuckDuckGo/Brave
│   └── 否 → 聚焦国内引擎
│
├── 信息敏感/需隐私？
│   ├── 是 → 优先: DuckDuckGo + Startpage + Qwant
│   └── 否 → 无特殊要求
│
├── 需要时间线/实时性？
│   ├── 小时级 → Google(tbs=qdr:h) + Brave
│   ├── 天级 → Google(tbs=qdr:d) + Baidu
│   └── 周级 → 全引擎均可
│
├── 需要数据验证？
│   ├── 是 → WolframAlpha + Google Scholar
│   └── 否 → 通用引擎
│
└── 需要技术深度？
    ├── 是 → DuckDuckGo(!gh !so !npm)
    └── 否 → 通用引擎
```

---

## 二、五类调查模式的引擎编排

### A股情报调查

| 轮次 | 目的 | 引擎 | 搜索策略 |
|------|------|------|---------|
| 第1轮 | 基本面扫描 | Baidu, 东方财富, 同花顺 | 公司概况+财务数据+行业地位 |
| 第2轮 | 深度挖掘 | 雪球, 巨潮资讯, 证券时报 | 公告研报+投资者讨论+机构观点 |
| 第3轮 | 交叉验证 | 新浪财经, 东方财富, Baidu | 财务数据多源比对+舆情核实 |

**关键词构建模板：**
- 第1轮：`{股票名称/代码} 基本面 财报 主营业务` / `{行业} 龙头 竞争格局`
- 第2轮：`site:xueqiu.com {股票名称}` / `site:cninfo.com.cn {股票代码}` / `{股票名称} 研报 评级 目标价`
- 第3轮：`{股票名称} 营收 净利润 增长率` / `{概念/行业} 政策 利好 利空`

### 竞品情报调查

| 轮次 | 目的 | 引擎 | 搜索策略 |
|------|------|------|---------|
| 第1轮 | 广域扫描 | Baidu, Google, Bing INT | 广泛关键词，建立全景 |
| 第2轮 | 深度挖掘 | WeChat, Toutiao, DuckDuckGo | 细分关键词，挖掘真实反馈 |
| 第3轮 | 交叉验证 | Baidu, Google, Brave | 关键数据多源验证 |

**关键词构建模板：**
- 第1轮：`{竞品名} 产品 功能 定价`
- 第2轮：`{竞品名} 使用体验 测评 评价` / `site:reddit.com {竞品名} review`
- 第3轮：`{竞品名} 融资 营收 市场份额`

### 舆情事件调查

| 轮次 | 目的 | 引擎 | 搜索策略 |
|------|------|------|---------|
| 第1轮 | 事件还原 | Baidu, Google(tbs=qdr:d), Toutiao | 时间过滤+热点词 |
| 第2轮 | 多视角 | WeChat, Sogou, DuckDuckGo | 评论区+论坛+自媒体 |
| 第3轮 | 时间线 | Google(tbs=qdr:w), Bing INT | 追溯事件发展脉络 |

**关键词构建模板：**
- 第1轮：`{事件关键词}` (加时间过滤)
- 第2轮：`{事件关键词} 评论 分析 观点` / `site:reddit.com {事件}`
- 第3轮：`{事件关键词} 时间线 经过 回顾`

### 人物背景调查

| 轮次 | 目的 | 引擎 | 搜索策略 |
|------|------|------|---------|
| 第1轮 | 基本信息 | Baidu, Google, Bing INT | 姓名+职务+公司 |
| 第2轮 | 专业验证 | DuckDuckGo(!gh), Google Scholar | 学术/技术成果 |
| 第3轮 | 信誉排查 | Baidu, Google, WeChat | 争议+诉讼+负面 |

**关键词构建模板：**
- 第1轮：`{人物名} 简介 背景 职务` / `{人物名} biography`
- 第2轮：`!gh {人物名}` / `author:"{人物名}"`
- 第3轮：`{人物名} 争议 诉讼 负面` / `{人物名} controversy`

### 信息交叉验证

| 轮次 | 目的 | 引擎 | 搜索策略 |
|------|------|------|---------|
| 第1轮 | 溯源 | Google(精确匹配), Baidu | 引号包裹+精确搜索 |
| 第2轮 | 比对 | DuckDuckGo, Brave, Startpage | 同一关键词不同引擎 |
| 第3轮 | 权威 | WolframAlpha, Google(site:权威站) | 官方信源确认 |

**关键词构建模板：**
- 第1轮：`"{待验证信息}"`
- 第2轮：`{待验证信息核心关键词}` (不同引擎)
- 第3轮：`site:gov.cn {关键词}` / WolframAlpha计算

---

## 三、引擎独有能力与场景匹配

| 引擎 | 独有能力 | 最佳调查场景 |
|------|---------|------------|
| **Google** | 最全索引+高级操作符+时间过滤+语言筛选 | 所有调查的基础引擎 |
| **Baidu** | 中文内容最全+知道/贴吧/百科 | 国内舆情+竞品口碑 |
| **DuckDuckGo** | Bangs直达(!gh !so !w !a)+无追踪 | 技术调查+隐私调查 |
| **WeChat搜狗** | 微信公众号文章搜索 | 深度分析文章+行业观察 |
| **Toutiao** | 自媒体+热点追踪+实时性 | 热点事件+舆论走向 |
| **Brave** | 独立索引+无偏见+Discussions | 无过滤信息+论坛观点 |
| **Startpage** | Google结果+隐私保护 | 需Google结果但保护隐私 |
| **WolframAlpha** | 结构化数据+知识计算 | 数据验证+数值型信息 |
| **Bing INT** | 中文界面+国际搜索结果 | 跨国调查+国际对比 |
| **Sogou** | 微信+知乎内容 | 中文社区深度内容 |
| **东方财富** | 实时行情+财务数据+股吧社区+F10资料 | A股公司基本面+资金流向+散户舆情 |
| **同花顺** | 行情数据+题材概念+问财AI+机构研报 | A股概念热度+技术面分析+智能选股 |
| **雪球** | 投资者社区+大V观点+组合追踪 | A股深度讨论+机构/牛散观点挖掘 |
| **巨潮资讯** | 证监会指定披露平台+公告原文 | A股官方公告+年报/季报原始文件 |
| **新浪财经** | 财经新闻+实时行情+机构评级汇总 | A股事件驱动+市场情绪监测 |
| **证券时报** | 证监会指定披露媒体+深度财经报道 | A股政策解读+上市公司调查报道 |

---

## 四、高级搜索策略

### 4.1 反向搜索法

目的：通过已知信息反推更多细节

```
已知：公司名 → 反向搜索
├── Google: "site:linkedin.com {公司名}"
├── DuckDuckGo: "!gh {公司名}"
├── Baidu: "{公司名} 团队 创始人"
└── Google: "{公司名} filetype:pdf" (查找公开文档)
```

### 4.2 时间轴搜索法

目的：追踪事件/信息随时间的变化

```
├── Google: "{关键词}&tbs=qdr:h" (1小时内)
├── Google: "{关键词}&tbs=qdr:d" (24小时内)
├── Google: "{关键词}&tbs=qdr:w" (1周内)
├── Google: "{关键词}&tbs=qdr:m" (1月内)
└── 对比不同时间段结果变化
```

### 4.3 地域对比法

目的：对比不同地区的信息差异

```
├── Baidu: "{关键词}" (中国视角)
├── Google: "{关键词}&gl=us" (美国视角)
├── Google HK: "{关键词}" (香港视角)
├── Ecosia: "{关键词}" (欧洲视角)
└── 对比结果差异，识别信息偏差
```

### 4.4 垂直深耕法

目的：在特定平台深入挖掘

```
├── Google: "site:reddit.com {关键词}" (Reddit社区)
├── Google: "site:zhihu.com {关键词}" (知乎)
├── Google: "site:github.com {关键词}" (开源项目)
├── Google: "site:crunchbase.com {关键词}" (融资数据)
├── WeChat: "{关键词}" (公众号深度文章)
├── Google: "site:bloomberg.com {关键词}" (财经数据)
├── Baidu: "site:xueqiu.com {股票名}" (雪球投资者社区)
├── Baidu: "site:cninfo.com.cn {股票代码}" (巨潮公告原文)
├── Baidu: "site:eastmoney.com {股票名} 研报" (东方财富研报)
├── Baidu: "site:10jqka.com.cn {股票名} 概念" (同花顺概念板块)
└── Baidu: "site:stcn.com {行业/政策}" (证券时报深度报道)
```

### 4.5 证据链构建法

目的：构建完整证据链确认信息

```
信息A（待验证）
├── 寻找首发源 → 源头是官方还是转载？
├── 确认传播路径 → 哪些媒体引用了？
├── 检查是否有反驳 → 搜索"辟谣"+"信息关键词"
├── 权威信源验证 → site:gov.cn / site:reuters.com
└── 数据验证 → WolframAlpha（如适用）
```

---

## 五、常见调查场景引擎组合速查

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
| 融资数据验证 | Google+Baidu+WolframAlpha+Jisilu | 近1年 | `site:crunchbase.com` |
| 用户口碑收集 | WeChat+Toutiao+DuckDuckGo+Brave | 近1月 | `site:reddit.com` |
| 技术栈调查 | DuckDuckGo(!gh !so)+Google | 无限制 | `!gh` `!so` `site:` |
| 价格/销量调查 | Baidu+Google+DuckDuckGo(!a) | 近1月 | `filetype:pdf` |
| 学术论文验证 | Google Scholar+Google+DuckDuckGo | 近2年 | `site:arxiv.org` |
| 法律诉讼排查 | Baidu+Google+Bing INT | 无限制 | `site:court.gov.cn` |
