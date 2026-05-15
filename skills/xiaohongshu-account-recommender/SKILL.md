---
name: xiaohongshu-account-recommender
description: 小红书创作者对标账号匹配工具，输入小红书账号ID或赛道+粉丝数+账号等级，推荐可直接复制的同阶对标和可参考的高阶标杆；当用户需要小红书账号推荐、KOL对标、起号参考、账号投放选择时使用。⚠️ 严禁任何联网搜索
---

# 小红书账号推荐

## 任务目标
- 本 Skill 用于：帮助小红书创作者找到可对标账号
- 能力包含：同阶对标匹配（粉丝量接近）、高阶标杆推荐（粉丝量3-5倍）、账号数据分析
- 触发条件：用户表达"找对标账号"、"推荐小红书账号"、"KOL投放"、"起号参考"等需求

## 前置准备
- 依赖说明：Python标准库（json、argparse、socket、ssl）
- API说明：调用小红书账号推荐API（使用原生socket+ssl手动发送HTTPS请求，不发送SNI）

## 操作步骤

### 步骤1：接收用户输入，解析参数

**输入方式A：小红书账号ID**
- 用户输入示例："我的ID是27493135897"
- 参数：redId

**输入方式B：赛道 + 粉丝数 + 账号等级（可选）**
- 用户输入示例："做饭，3000粉，素人"
- 参数映射：
  - track：赛道类型（自动映射，如"做饭"→"美味佳肴"）
  - maxFans/minFans：粉丝数处理规则见下方
  - level：账号等级（自动映射，如"小白"→"素人"）

**粉丝数处理规则（重要）**：
- 单个粉丝数（如"3000粉"）：maxFans=3000, minFans=**0**（不要传空字符串）
- 粉丝区间（如"1000-3000粉"）：maxFans=3000, minFans=1000
- 未指定粉丝数：maxFans和minFans都传空字符串

### 步骤2：调用脚本查询对标账号

```
# 按账号ID查询
python scripts/xiaohongshu_account_recommender.py --red_id "27493135897"

# 按赛道+粉丝数+等级查询
python scripts/xiaohongshu_account_recommender.py --track "美味佳肴" --min_fans 0 --max_fans 3000 --level "素人"
```

API接口：POST https://onetotenvip.com/story/xhsUser/querySimilarAccounts

### 步骤3：按标准模版输出结果

**无论哪种查询方式，输出格式完全一致**，严格按照 `references/output_template.md` 输出到对话中：
1. 开场白（只显示有数据的组，无数据时显示"暂未匹配到"）
2. 同阶对标表格（有数据才展示）
3. 高阶标杆表格（有数据才展示）
4. 分析总结（有数据才展示）
5. 订阅服务

**推荐理由生成规则**：综合分析内容风格、更新频率、互动等级、爆文案例，口语化描述。

### 步骤4：生成并展示HTML报告（必须执行）

账号推荐输出结束后，脚本会自动执行以下流程：
1. **将所有数据存入临时JSON文件**：`/workspace/projects/xiaohongshu-account-recommender/account_data.json`
2. **读取JSON文件数据生成HTML文件**：`/workspace/projects/xiaohongshu-account-recommender/account_recommend.html`
3. **脚本输出JSON标记**：`{"status": "success", "html_path": "..."}`

**AI必须执行**：读取脚本输出的`html_path`路径对应的HTML文件，在对话结尾直接展示该HTML文件供用户预览。

## 标准赛道分类（25个）
综合全部 | 出行代步 | 休闲爱好 | 影视娱乐 | 数码科技 | 医疗保健 | 综合杂项 | 星座情感 | 时尚穿搭 | 婚庆婚礼 | 拍摄记录 | 学习教育 | 化妆美容 | 居家装修 | 旅行度假 | 亲子育儿 | 个人护理 | 美味佳肴 | 职业发展 | 宠物天地 | 潮流鞋包 | 日常生活 | 科学探索 | 新闻资讯 | 体育锻炼

## 标准账号等级（7个）
明星 | 品牌 | 企业 | 头部kol | 腰部kol | 尾部kol | 素人

## 赛道映射示例
| 用户输入 | 匹配结果 |
|---------|---------|
| 美妆、化妆、护肤 | 化妆美容 |
| 穿搭、时尚 | 时尚穿搭 |
| 美食、做饭、探店 | 美味佳肴 |
| 旅行、旅游 | 旅行度假 |
| 家居、装修、改造 | 居家装修 |
| 健身、运动、减肥 | 体育锻炼 |
| 母婴、育儿 | 亲子育儿 |
| 宠物、猫、狗 | 宠物天地 |
| 数码、手机、科技、互联网、AI、人工智能、编程 | 数码科技 |
| 教育、学习 | 学习教育 |
| 情感、恋爱 | 星座情感 |
| 职场、工作 | 职业发展 |

## 账号等级映射示例
| 用户输入 | 匹配结果 |
|---------|---------|
| 明星、艺人、爱豆、idol | 明星 |
| 品牌、牌子 | 品牌 |
| 企业、公司、商家、官方号 | 企业 |
| 头部kol、头部、头部达人、大v、大号、百万粉 | 头部kol |
| 腰部kol、腰部、腰部达人、中号、十万粉 | 腰部kol |
| 尾部kol、尾部、尾部达人、小号、万粉 | 尾部kol |
| 素人、普通人、小白、新手、新人、新手博主、个人号 | 素人 |

## 使用示例

**示例1：按账号ID查询**
- 用户输入："我的ID是27493135897"
- 脚本调用：`python scripts/xiaohongshu_account_recommender.py --red_id "27493135897"`
- 输出格式：按标准模版输出

**示例2：按赛道+单个粉丝数+等级查询**
- 用户输入："做饭，3000粉，素人"
- 参数映射：track=美味佳肴, minFans=**0**, maxFans=3000, level=素人
- 脚本调用：`python scripts/xiaohongshu_account_recommender.py --track "美味佳肴" --min_fans 0 --max_fans 3000 --level "素人"`
- 输出格式：按标准模版输出（与示例1完全一致）

**示例3：按赛道+粉丝区间+等级查询**
- 用户输入："做饭，1000-3000粉，素人"
- 参数映射：track=美味佳肴, minFans=1000, maxFans=3000, level=素人
- 脚本调用：`python scripts/xiaohongshu_account_recommender.py --track "美味佳肴" --min_fans 1000 --max_fans 3000 --level "素人"`
- 输出格式：按标准模版输出（与示例1完全一致）

## 资源索引
- 脚本：见 [scripts/xiaohongshu_account_recommender.py](scripts/xiaohongshu_account_recommender.py)（调用API查询对标账号，支持赛道和账号等级映射，自动生成HTML报告）
- 参考：见 [references/output_template.md](references/output_template.md)（输出格式说明、模版定义、数值格式化规则）
- 资产：见 [references/account_template.html](references/account_template.html)（HTML报告模版，与输出模版格式一致）

## 注意事项
- 粉丝数处理：单个数值→maxFans=该值, minFans=0；区间→按区间传参
- 无论哪种查询方式，输出格式完全一致，严格按照 `references/output_template.md` 执行
- 所有数据来源于API接口，严禁联网搜索
