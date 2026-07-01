<p align="center">
  <a href="https://redfox.hk/?source=github">
    <img src="https://lyy.redfox.hk/page/logo-redfox-name.png" alt="RedFox Logo" width="200">
  </a>
</p>

<p align="right">
  中文
  <a href="https://github.com/redfox-data/redfox-community/blob/main/README.en.md">English</a>
</p>

# redfoxdata · Agent Skills

本仓库收录 **redfoxdata** 社区维护的多枚 Agent 技能（Skill），面向灵感、选题、文案创作、数据复盘等场景。技能以 `SKILL.md` 为核心，可与 Cursor、Claude Code 等支持 Agent Skills 的工具配合使用。

## 仓库结构

```text
.
├── README.md          # 本说明（中文）
├── README.en.md       # English README
├── skills/            # 技能（每个子目录一枚技能）
│   └── <skill-name>/
│       ├── SKILL.md
│       └── …          # 脚本、参考文档等（可选）
```

## 技能目录约定

每个技能是一个**独立子文件夹**，且至少包含：

| 文件       | 说明                                                              |
| ---------- | ----------------------------------------------------------------- |
| `SKILL.md` | 技能入口：YAML frontmatter + 正文（触发条件、步骤、约束、示例等） |

建议在 `SKILL.md` 的 frontmatter 中提供清晰元信息，便于检索与导入平台识别，例如：

```yaml
---
name: Example Skill
description: 一句话说明技能适用场景与能力边界（建议具体，避免空泛）。
---
```

可选：`references/`、`scripts/`、`assets/` 等，与 `SKILL.md` 同目录存放，保持单技能自包含、路径相对引用即可。

## RedFoxHub首页

<p align="center">
  <a href="https://redfox.hk/?source=github">
    <img src="https://lyy.redfox.hk/page/redfox-page-3.png" alt="RedFox Logo" width="100%">
  </a>
</p>

## 丰富多样的Skill

<p align="center">
  <a href="https://redfox.hk/skills?source=github">
    <img src="https://lyy.redfox.hk/page/redfox-page-2.png" alt="RedFox Logo" width="100%">
  </a>
</p>

## 身份认证

所有 API 请求都需要有效的 API KEY。

### 获取链接：

请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取API KEY

### Skill如何使用

#### 本地 / Cursor

将需要的技能目录复制到你所用工具的 skills 目录（例如 Cursor 的 user skills 或项目内 `.cursor/skills/` 等，以你当前客户端文档为准），或通过客户端提供的「添加技能」入口指向该子文件夹。

#### For Agent

直接告诉智能体Agent（openclaw/workbuddy/qoder）：

```bash
帮我安装这个skill：https://github.com/redfox-data/redfox-community/tree/main/skills/seedance-video-gen
```

#### skills cli

在交互终端执行以下命令，可直接复制

```bash
npx skills init //安装skills cli

npx skills add redfox-data/redfox-community //检索redfox仓库选择安装skill

npx skills add https://github.com/redfox-data/redfox-community/tree/main/skills/seedance-video-gen //安装具体skill
```

根据提示将skill安装在指定的agent文件夹中或者安装在全局

#### SkillHub

访问SkillHub搜索skills目录中对应技能的中文名安装：https://skillhub.cn/skills

搜索示例：公众号爆款文章查询 或 抖音每日最具影响力账号

#### ClawHub（`clawhub`）

访问clawhub红狐数据官方主页搜索安装skill：https://clawhub.ai/user/redfox-data

## 多平台API文档

<p align="center">
  <a href="https://redfox.hk/apis?source=github">
    <img src="https://lyy.redfox.hk/page/redfox-page-1.png" alt="RedFox Logo" width="100%">
  </a>
</p>

### 文档中包含：

请求参数说明
返回字段说明
错误码说明
调用示例

### API明细：

#### 抖音：

- [获取抖音作品内容详情 (优质库)](https://redfox.hk/apis/douyin/0OT1E306)
- [获取抖音账号信息 (优质库)](https://redfox.hk/apis/douyin/XUT4CECZ)
- [搜索关键词获取抖音账号 (优质库)](https://redfox.hk/apis/douyin/P5CHB3BZ)
- [搜索关键词获取抖音作品 (优质库)](https://redfox.hk/apis/douyin/774OBKK0)
- [获取抖音账号作品列表 (优质库)](https://redfox.hk/apis/douyin/QEQLCKD6)
- [搜索关键词获取抖音 AI 作品(优质库)](https://redfox.hk/apis/douyin/I8P3HTVH)

#### 小红书：

- [获取小红书账号信息 (优质库)](https://redfox.hk/apis/xiaohongshu/4IVIDHEN)
- [获取小红书作品内容详情 (优质库)](https://redfox.hk/apis/xiaohongshu/KR1LPTBF)
- [搜索关键词获取小红书账号 (优质库)](https://redfox.hk/apis/xiaohongshu/439NFLBD)
- [搜索关键词获取小红书作品 (优质库)](https://redfox.hk/apis/xiaohongshu/384C6W6B)
- [搜索关键词获取小红书 AI 作品(优质库)](https://redfox.hk/apis/xiaohongshu/047JJ3UA)

#### 公众号：

- [获取公众号账号信息 (优质库)](https://redfox.hk/apis/gongzhonghao/6C4A77XR)
- [根据作品uuid获取公众号作品 (优质库)](https://redfox.hk/apis/gongzhonghao/XEO0QQNF)
- [搜索关键词获取公众号账号 (优质库)](https://redfox.hk/apis/gongzhonghao/DNVPQZEZ)
- [搜索关键词获取公众号作品 (优质库)](https://redfox.hk/apis/gongzhonghao/PW97QFBS)
- [获取公众号账号作品列表 (优质库)](https://redfox.hk/apis/gongzhonghao/XNV30XZ3)
- [根据作品地址获取公众号作品 (优质库)](https://redfox.hk/apis/gongzhonghao/VUTTKTP6)
- [搜索关键词获取公众号 AI 创作作品 (优质库)](https://redfox.hk/apis/gongzhonghao/IE0887SO)

#### 哔哩哔哩：

- [获取哔哩哔哩作品内容详情 (优质库)](https://redfox.hk/apis/bilibili/TIN1NMTZ)
- [获取哔哩哔哩账号信息 (优质库)](https://redfox.hk/apis/bilibili/EH53TOT7)
- [搜索关键词获取哔哩哔哩账号 (优质库)](https://redfox.hk/apis/bilibili/ZXJLJQ21)
- [搜索关键词获取哔哩哔哩作品 (优质库)](https://redfox.hk/apis/bilibili/LEN9QXR3)
- [获取哔哩哔哩账号作品列表 (优质库)](https://redfox.hk/apis/bilibili/VPA67I98)

#### Tiktok：

- [Tiktok关键词搜索账号](https://redfox.hk/apis/tool-tiktok/20070019)

#### AI搜索：

- [豆包纯文字搜索](https://redfox.hk/apis/tool-ai-search/I9R9LIDL)
- [Deepseek纯文字搜索](https://redfox.hk/apis/tool-ai-search/KGX4SDXQ)

#### AI工具：

- [GPT图片生成](https://redfox.hk/apis/tool/HUV4KRFQ)
- [豆包图片生成](https://redfox.hk/apis/tool/7OM96HCF)
- [豆包视频生成](https://redfox.hk/apis/tool/ER2ATHKI)
- [上传图片](https://redfox.hk/apis/tool/FXDGJO1V)
- [上传视频/图片/音频](https://redfox.hk/apis/tool/6L178PZD)
- [短视频下载器](https://redfox.hk/apis/tool/AWUTFI4V)

#### 更多平台API：

- [敬请期待！！](https://redfox.hk/apis)

## 参与贡献

欢迎通过 Issue / Pull Request 贡献新技能或修正现有技能。

1. Fork 本仓库
2. 在 `skills/` 下新增或修改对应子目录
3. 确保 `SKILL.md` 可独立理解、步骤可执行、依赖与风险有说明
4. 发起 Pull Request，并在描述中简要说明变更动机与适用场景

## 许可证

如无特殊说明，默认采用 **[MIT](LICENSE)**（或在此处写明你实际选择的许可证）。若某技能含第三方素材或不同许可证，请在该技能目录内单独注明。

---

**redfoxdata** — 将可重复的新媒体工作流沉淀为可分享、可演进的 Agent 技能。
