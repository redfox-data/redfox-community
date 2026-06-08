---
name: wechat-similar-account
description: 公众号创作者对标账号匹配工具，基于3层加权匹配体系（核心基础40%+运营变现35%+数据特征25%）推荐对标账号和头部账号。当用户需要公众号账号推荐、公众号对标、起号参考、账号投放选择时使用。触发词：公众号对标、相似账号、对标推荐、起号参考、账号匹配。
---

# 公众号相似账号推荐

## 📋 概述

基于 [红狐Hub](https://redfox.hk/) 数据平台，为公众号创作者提供智能对标匹配：推荐同阶对标账号（可直接复制玩法）和高阶标杆账号（模式成熟可追赶），通过3层加权体系生成7维度个性化推荐理由。未收录账号支持提交微信号进行数据同步。

## 🔑 鉴权

`REDFOX_API_KEY` 从环境变量获取。若未设置，Agent 应主动帮用户配置：

| 系统 | 配置方式 | 验证命令 |
| --- | --- | --- |
| Windows | `[Environment]::SetEnvironmentVariable("REDFOX_API_KEY", "<值>", "User")` | `echo %REDFOX_API_KEY%` |
| macOS/Linux | `echo 'export REDFOX_API_KEY=<值>' >> ~/.zshrc && source ~/.zshrc` | `echo $REDFOX_API_KEY` |

> 配置后需重启终端生效，确保换一个 skill 也能读取到。

## 📊 命令速查

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `--account_name "名称"` | 按公众号名称查询 | `python scripts/wechat_similar_accountr.py --account_name "科技前沿"` |
| `--account_id "ID"` | 按公众号ID查询 | `python scripts/wechat_similar_accountr.py --account_id "gh_xxx"` |
| `--account_type "分类"` | 按账号分类查询 | `python scripts/wechat_similar_accountr.py --account_type "科技数码"` |
| `--sync_wechat_id "微信号" --account_name "名称"` | 提交数据同步请求 | `python scripts/wechat_similar_accountr.py --sync_wechat_id "kejiqianyan" --account_name "科技前沿"` |

> 支持组合查询：`--account_name "科技前沿" --account_type "科技数码"`
>
> ⚠️ `--account_type` 查询成功率较低，建议优先用代表性账号名称查询，详见 [core_workflow.md](references/core_workflow.md)「按分类查询注意事项」。

## 🔄 核心流程

完整工作流程（输入解析、脚本调用、输出模板、无数据处理、对标匹配规则、推荐理由生成规则、输出格式规范）详见 [core_workflow.md](references/core_workflow.md)。

**输出顺序**：
1. 查询账号基本信息 + 近5篇文章
2. 开场白（只显示有数据的组）
3. 同阶对标表格（有数据才展示）
4. 高阶标杆表格（有数据才展示）
5. 分析总结（有数据才展示）
6. **订阅服务（必须输出，无论有无数据）**

## 📎 其他资源

- [core_workflow.md](references/core_workflow.md) — 核心工作流程、对标匹配规则、推荐理由生成规则、输出格式规范
