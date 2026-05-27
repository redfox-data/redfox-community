---
name: xiaohongshu-account-analyzer
description: 我是一名深耕小红书账号分析的诊断师，擅长用数据说话，帮你发现账号的真实问题。从定位模糊到变现困难，从选题迷茫到更新瓶颈，我都能给你一份基于数据的诊断报告和可落地的行动建议。当你需要分析自己的账号数据、诊断账号健康度、评估商业价值、对比竞品账号或制定优化策略时，找我准没错。
---

# 小红书账号诊断

## 使用示例

| 场景 | 用户输入 | 预期产出 |
|------|---------|---------|
| 单账号诊断 | 分析小红书号 26112666886 | 输出七维度诊断报告（账号定位、粉丝画像、选题体系、封面风格、爆文能力、互动规模、更新产能），推荐相似账号，生成可导出图片的HTML报告 |
| 多账号对比 | 帮我对比分析 ID1 和 ID2 | 分别输出各账号诊断报告，生成横向对比总结（核心差异、共同问题、发展建议），生成对比HTML报告 |
| 分析相似账号 | 回复序号"1"选择相似账号 | 对选中的相似账号进行完整诊断分析，输出报告并生成HTML |
| 订阅更新 | 账号无作品数据时回复"订阅" | 30分钟后自动推送该账号的诊断报告 |

## 任务目标
- 本 Skill 用于：深度拆解小红书账号，输出专业的商业价值分析报告
- 能力包含：七维度评分（账号定位10分、粉丝画像与需求15分、选题体系15分、封面风格10分、爆文能力15分、互动规模20分、更新产能15分，满分100）、生命周期分析、行动处方生成、相似账号推荐、多账号对比分析
- 触发条件：用户提供小红书号（名称下方的小红书号，格式为纯数字或字母数字组合，非中文昵称），需要生成完整的账号诊断报告

## 前置准备
- 依赖说明：Python标准库（ssl、urllib.request、json），无需额外安装
- 数据接口：POST https://redfox.hk/story/api/xhsUser/query（见 references/api_guide.md）
- WebSearch：获取博主昵称后执行背景信息补全（搜索小红书+昵称、采访报道、跨平台布局）

### 鉴权

#### 获取 API Key
1. 访问 [RedFox 官网](https://redfox.hk/) 了解服务详情
2. 前往 [注册页面](https://redfox.hk/login) 注册账号
3. **新注册用户将获赠免费积分**，可立即开始使用 API 服务
4. 注册登录后，在个人中心获取 API Key，格式为 `ak_xxxxxxxx`

#### 配置 API Key
- `REDFOX_API_KEY` 从环境变量获取，格式 `ak_xxxxxxxx`
- 若未设置，提示用户自行配置：`export REDFOX_API_KEY=<你的apikey>`；若用户不会配置，Agent应主动帮用户设置：
  - **macOS/Linux**：将 `export REDFOX_API_KEY=<值>` 追加到 `~/.zshrc`（zsh）或 `~/.bashrc`（bash），然后 `source` 对应文件使其全局生效
  - **Windows**：使用 `[Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")` 设置用户级永久环境变量（需重启终端生效）
  - 配置完成后应验证：`echo $REDFOX_API_KEY`（macOS/Linux）或 `echo %REDFOX_API_KEY%`（Windows），确保换一个skill也能读取到

## 操作步骤
- 标准流程（必须严格按顺序执行，不得跳过任何步骤）：
  1. **开场白引导** — 输出欢迎语，引导用户输入小红书号
     - 输出 `references/workflow_guide.md` 中的标准开场白
     - 明确说明：请输入小红书号（纯数字或字母数字组合，非中文昵称）
  2. **输入识别与数据获取** — 识别用户输入并调用接口查询
     - **识别规则**：用户输入为纯数字或字母数字组合时，识别为小红书号，直接调用接口
     - **示例**：`Esther1218`、`26112666886`、`abc123` 都是有效的小红书号格式
     - 按ID查询：`python scripts/xiaohongshu_analyzer.py query --user_ids "id1,id2"`
     - 若用户输入中文昵称，提示用户提供小红书号而非昵称
     - 脚本自动将接口原始数据保存至 `output/raw_data.json`，供后续步骤参考
  3. **WebSearch背景信息补全** — 获取博主昵称后执行：
     - WebSearch 搜索「小红书 + 昵称」补全背景信息
     - WebSearch 搜索「昵称 + 采访/报道」寻找媒体报道
     - WebSearch 搜索抖音/B站/公众号等跨平台布局
  4. **查询结果处理** — 根据查询类型输出对应响应
     - 参考 `references/workflow_guide.md` 处理场景：
       * **未查询到账号（账号数据为空）** → 执行以下处理：
         - 调用数据同步接口：`python scripts/xiaohongshu_analyzer.py sync_notes --red_ids "用户输入的账号ID"`
         - 输出提示：
           ```
           非常抱歉，未查询到该账号。请检查账号id是否有误，若输入准确，可能当前账号粉丝低于1000或者近期发文数据未达到收录标准。
           我们将为你实时去采集数据，30min后向您推送新的诊断报告，请问是否接收？
           1. 接收推送
           2. 暂不接收
           ```
         - 用户输入编号"1"或回复"接收"后，执行以下操作：
           1. **【必须】创建日程任务**（使用calendar_create工具）：
              - summary: 推送xxx账号诊断报告
              - dtstart: 当前时间+30分钟（格式YYYYMMDDHHMM）
              - description: 重新查询账号数据并推送诊断报告（python scripts/xiaohongshu_analyzer.py query --user_ids <用户输入的账号ID>）
           2. 创建日程成功后提示：「订阅成功！系统将在30分钟后自动向您推送该账号的诊断报告，请耐心等待」
         - 用户输入编号"2"或回复"暂不接收"，结束本次分析
       * 查询到唯一账号 → 继续生成单账号报告（步骤5-7）
       * 查询到多个账号数据 → 进入多账号对比流程（步骤5M-7M）
       * 查询到账号但无作品（works为空数组）→ **直接进入订阅流程**：
         - 立即停止后续步骤，输出提示（xxx为账号昵称）：
           ```
           为您获取作品中，30分钟后会更新数据后可向您推荐，请问是否订阅"xxx"账号？
           1. 订阅账号xxx
           2. 仍然执行分析
           3. 暂不订阅
           ```
         - 用户输入编号"1"或回复"订阅"后，执行以下操作：
           1. **【必须】创建日程任务**（使用calendar_create工具）：
              - summary: 推送xxx账号诊断报告
              - dtstart: 当前时间+30分钟（格式YYYYMMDDHHMM）
              - description: 重新查询账号数据并推送诊断报告（python scripts/xiaohongshu_analyzer.py query --user_ids <redId>）
           2. 创建日程成功后，调用脚本同步作品数据：
              ```bash
              python scripts/xiaohongshu_analyzer.py sync_notes --red_ids <redId>
              ```
           3. 同步成功后提示：「订阅成功！系统将在30分钟后自动向您推送"xxx"账号的诊断报告，请耐心等待」
         - 用户输入编号"2"或回复"仍然执行分析"后，继续执行分析流程，在报告开头提示：「该账号暂未获取到近7天作品」，然后输出完整的分析报告
         - 用户输入编号"3"或回复"暂不订阅"，结束本次分析

      **订阅推送机制**：
      - 订阅成功后，系统创建一个30分钟后的定时任务
      - 定时任务到达时，**无论是否有作品数据都执行分析流程**：
        1. 重新查询账号数据（`python scripts/xiaohongshu_analyzer.py query --user_ids <redId>`）
        2. **如果works为空**：
           - 在报告开头提示：「该账号已重新同步，但暂未获取到近7天作品数据」
           - 继续执行完整的分析流程，输出诊断报告
        3. **如果works有数据**：
           - 正常输出完整的诊断报告
  5. **诊断报告生成** — 智能体严格按照模板格式在对话中输出诊断报告
     **重要**：报告必须在对话中直接输出，不得生成md文件。必须完全按照 `references/report_template.md` 的格式逐字输出，包括所有边框符号、标题格式、分隔线等，不得改变任何格式。
     - **步骤5.1**：先读取 `references/report_template.md` 获取完整格式
     - **步骤5.2**：将脚本数据填入模板对应位置，保持格式完全一致；**当数据字段为空或无值时，直接留空或省略该字段所在行，不展示"暂无"**
     - **步骤5.3**：动态生成内容（账号定位、粉丝画像、选题体系、封面风格、行动处方等），所有内容必须严格基于接口返回数据和WebSearch结果
     - **步骤5.4**：根据数据条件隐藏空数据模块：
       * 爆文数为0 → 省略爆文能力整段
       * 无近期作品数据 → 省略近期作品整段
       * 赛道痛点或你的优势为空 → 省略差异化优势
     - **综合评分结论规则**：
       * 综合评分>=60：必须列>=2个已验证可复用的具体动作
       * 综合评分<60：必须先点明薄弱项对应的具体数据问题，再给对应建议
     - 报告结构按7个评分维度展开：
       * 账号定位（10分）：TA是谁、心智占位、核心身份、价值观锚点、吸引力类型、差异化优势
       * 粉丝画像与需求（10分）：粉丝构成、核心需求反推、付费意愿评估
       * 选题体系（15分）：选题方向、表达风格、叙事手法、人格一致性
       * 封面风格（10分）：视觉特征、信息层级、一致性
       * 爆文能力（15分）：爆文率、爆文特征分析、爆文列表、放大倍数
       * 互动规模（20分）：互动量、互动率、收藏率、互动结构、水平衡量
       * 更新产能（15分）：周更频率、间隔标准差、发布时间分析、水平衡量
  6. **展示相似账号** — 诊断报告输出完毕后直接展示相似账号
     - 从脚本返回数据的 `similar_accounts` 字段提取2-5个相似账号数据
     - 按以下格式直接展示（无需询问）：
       ```
       1. [账号名](https://www.xiaohongshu.com/user/profile/[accountId])
       | 粉丝：[followerCount] | 总互动：[总点赞+总收藏] | 活跃评分：[评分]
       推荐理由：[基于数据总结值得学习的点]
       发文特点：[总结内容特征和策略]
       可学之处：[具体可复制的策略]
       
       2. ...
       
       回复序号可继续分析！
       ```
     - 相似账号展示完成后直接进入步骤7
  7. **生成HTML报告并展示** — 在相似账号推荐输出"回复序号可继续分析！"后执行，所有HTML相关操作统一在本步骤执行，不得提前
     - **核心原则**：HTML只是将对话中的分析报告进行更美观的输出，**必须与对话输出的内容完全一致**，不能有任何差异
     - **步骤7.1**：基于模板生成report_data.json
       * 调用脚本：`python scripts/xiaohongshu_analyzer.py build_report_data --account_name "账号名"`
       * 脚本会基于 `assets/report_data_template.json` 生成 `output/report_data.json`
     - **步骤7.2**：填充AI分析内容到report_data.json
       * 读取 `output/report_data.json`，在模板基础上填充以下AI分析字段（与对话输出一致）：
         - `positioning`：TA是谁、心智占位、价值观锚点、吸引力类型、赛道痛点、你的优势、可强化
         - `fans_profile`：核心需求反推、付费意愿评估内容
         - `topic_system`：选题方向、表达风格、叙事手法、人格一致性、选题分析
         - `cover_style`：视觉特征、信息层级、一致性、封面分析
         - `viral_ability`：爆文特征分析、爆文标题分析
         - `interactive_scale`：类型判断
         - `update_rhythm`：频率分析
         - `similar_accounts`：步骤6展示的相似账号数据（最多3个）
         - `综合诊断结论内容`：完整诊断结论
         - `action_prescription`：行动处方内容
       * **数值字段格式**：`收藏率`、`爆文率`、`互动率` 填纯数字，不带 `%` 符号
       * **数量字段格式**：`近7天发作品数`、`爆文数`、`周更频率` 填纯数字，不带单位
       * **空值处理**：空值字段留空字符串""，不填写"暂无"
       * 填充完成后保存文件
     - **步骤7.3**：调用脚本生成HTML：`python scripts/xiaohongshu_analyzer.py generate_html`
     - **步骤7.4**：**直接在对话中展示HTML文件内容**，让用户可以看到完整的报告

  **多账号对比流程**（当步骤4返回 `query_type: multi` 时执行）：
  5M. **多账号对比报告生成** — 智能体为每个账号生成诊断报告并在对话中输出，最后输出对比总结
     - 依次为每个账号输出诊断报告，格式同步骤5
     - 对比总结按三个模块输出：
       * 核心差异：每个账号的核心差异，按账号分别展示
       * 共同问题：所有账号的共性问题列表
       * 发展建议：每个账号的发展建议，按账号分别展示
  6M. **展示相似账号** — 同步骤6，直接展示相似账号
  7M. **生成多账号HTML报告并展示** — 同步骤7逻辑，但使用多账号模板
     - **步骤7M.1**：基于模板生成multi_report_data.json
       * 调用脚本：`python scripts/xiaohongshu_analyzer.py build_multi_report_data --account_names "账号1,账号2"`
       * 脚本会基于 `assets/multi_report_data_template.json` 生成 `output/multi_report_data.json`
     - **步骤7M.2**：填充各账号分析内容到multi_report_data.json的accounts数组
     - **步骤7M.3**：调用脚本生成多账号HTML：`python scripts/xiaohongshu_analyzer.py generate_multi_html`
     - **步骤7M.3**：**直接在对话中展示HTML文件内容**，让用户可以看到完整的报告

- 可选分支:
  - 当用户提供后台数据：直接使用数据生成报告，无需调用查询接口
  - **用户回复序号继续分析相似账号**：
     * 从similar_accounts数据中获取该账号的userId
     * 调用脚本查询该账号详情：`python scripts/xiaohongshu_analyzer.py query --user_ids "userId"`
     * **执行完整分析流程**（同步骤3-7）：
       - 步骤3：WebSearch补全背景信息
       - 步骤4：在对话中输出完整诊断报告
       - 步骤5：直接展示相似账号
       - 步骤6：生成HTML报告并展示
     * **注意**：必须在对话中输出完整诊断报告，不能只输出HTML

## 资源索引
- 脚本:见 [scripts/xiaohongshu_analyzer.py](scripts/xiaohongshu_analyzer.py)(用途与参数:query查询数据保存raw_data.json，build_report_data生成report_data.json模板，generate_html生成HTML报告)
- 脚本:见 [scripts/html_generator.py](scripts/html_generator.py)(用途:HTML报告生成逻辑，包含模板替换、字段填充、条件移除等)
- 脚本:见 [scripts/html_checker.py](scripts/html_checker.py)(用途:HTML数据完整性检查与修复，检测缺失字段并填充默认值)
- 参考:见 [references/report_template.md](references/report_template.md)(何时读取:生成报告前必须先读取此模板，输出时必须严格按照此格式)
- 参考:见 [references/api_guide.md](references/api_guide.md)(何时读取:理解接口字段和评分逻辑时)
- 参考:见 [references/workflow_guide.md](references/workflow_guide.md)(何时读取:处理开场白、查询结果、相似账号展示、评分体系和数据填写时)
- 资产:见 [assets/report_template.html](assets/report_template.html)(用途:单账号HTML格式报告模板)
- 资产:见 [assets/report_data_template.json](assets/report_data_template.json)(用途:单账号报告数据模板，build_report_data命令基于此生成report_data.json)
- 资产:见 [assets/multi_report_template.html](assets/multi_report_template.html)(用途:多账号对比HTML格式报告模板)
- 资产:见 [assets/multi_report_data_template.json](assets/multi_report_data_template.json)(用途:多账号报告数据模板)

## 注意事项
- 分析基于近30天数据，确保数据时效性
- 脚本输出 JSON 格式，智能体负责内容解析与报告呈现
- **格式要求**：诊断报告必须在对话中直接输出，不得生成md文件；必须严格按照 `references/report_template.md` 格式输出
- 无作品数据时需提示用户等待更新并引导订阅提醒
- 所有动态生成内容必须基于接口返回数据+WebSearch结果，禁止虚构
- **输出顺序**：对话输出诊断报告 → 直接展示相似账号 → 生成HTML并展示
- **空值处理**：数据字段为空时直接隐藏对应模块，不展示"暂无"
- **数据模板一致性**：步骤7填充report_data.json时，AI分析内容必须与对话中输出的诊断报告完全一致
- HTML报告生成必须在步骤7执行，不得省略
- 用户回复序号选择相似账号时，获取该账号userId并走完整诊断流程
- **多账号对比总结**：核心差异和发展建议按账号分别展示
- **反空话规则**：禁止出现无具体动作、无数据支撑的表述，所有结论必须满足数据支撑+落地动作
