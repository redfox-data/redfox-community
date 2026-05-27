#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
违禁词检测脚本（Skill：multi-wordcheck）

默认将待检测文案通过 HTTPS POST（TLS 校验开启）发往 Skill 对接的第三方检测后端，不在本地持有词库。
- 默认接口：https://redfox.hk/story/api/cozeSkill/sensitiveWordSearch
  域名 redfox.hk 为本 Skill 声明的检测服务端（见 SKILL.md「第三方服务与数据去向」）。
- 认证方式：请求头 X-API-KEY，通过 REDFOX_API_KEY 三级回退获取。
- 请求 JSON 字段：content、platform、source（来源标识）。
- 自建/合规网关：设置环境变量 PROHIBITED_WORD_API_URL 为 https 完整 URL（优先级最高）。
"""

import argparse
import json
import os
import re

import requests


def _get_api_key():
    """
    三级回退获取 REDFOX_API_KEY：
    1. 从当前设备环境变量 REDFOX_API_KEY 获取
    2. 从 shell 配置文件（.bashrc / .zshrc / .bash_profile 等）中读取
    3. 仍未获取到则提示用户配置
    """
    # 第一级：环境变量
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if api_key:
        return api_key

    # 第二级：从 shell 配置文件中读取
    home = os.path.expanduser("~")
    shell_rc_files = [".bashrc", ".zshrc", ".bash_profile", ".profile", ".zprofile"]

    for rc_file in shell_rc_files:
        rc_path = os.path.join(home, rc_file)
        if not os.path.isfile(rc_path):
            continue
        try:
            with open(rc_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if "REDFOX_API_KEY" in stripped and "=" in stripped:
                        assignment = stripped
                        if assignment.startswith("export "):
                            assignment = assignment[len("export "):]
                        _, _, value = assignment.partition("=")
                        value = value.strip().strip('"').strip("'").strip()
                        if value:
                            return value
        except Exception:
            continue

    # 第三级：仍未获取到，提示用户配置
    raise SystemExit(
        "未找到 REDFOX_API_KEY，请通过以下方式配置：\n"
        "  方式一：设置环境变量 export REDFOX_API_KEY=<你的apikey>\n"
        "  方式二：在 shell 配置文件（~/.bashrc 或 ~/.zshrc）中添加 export REDFOX_API_KEY=<你的apikey>\n"
        "  配置后请重新打开终端或执行 source ~/.bashrc 使其生效"
    )


def check_sensitive_words(content, platform="公众号"):
    """
    调用违禁词检测 API（HTTPS POST，TLS 默认校验）。

    API 地址优先级：
    1. 环境变量 PROHIBITED_WORD_API_URL（自建/合规网关）
    2. 默认地址 https://redfox.hk/story/api/cozeSkill/sensitiveWordSearch

    Args:
        content: 待检测的文案内容
        platform: 平台名称，默认为"公众号"

    Returns:
        dict: 包含检测结果和格式化HTML的字典
    """
    DEFAULT_API_URL = "https://redfox.hk/story/api/cozeSkill/sensitiveWordSearch"

    # 优先使用 PROHIBITED_WORD_API_URL 环境变量（向后兼容）
    api_url = os.environ.get("PROHIBITED_WORD_API_URL", "").strip()
    if not api_url:
        api_url = DEFAULT_API_URL

    if not api_url.lower().startswith("https://"):
        return {
            "status": "error",
            "platform": platform,
            "original_content": content,
            "error": "PROHIBITED_WORD_API_URL 必须为 https:// 地址",
        }

    # 获取 API Key（三级回退）
    api_key = _get_api_key()

    # 构建请求头
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-API-KEY": api_key,
    }

    # 构建请求参数
    params = {
        "content": content,
        "platform": platform,
        "source": "多平台违禁词查询-GitHub",
    }

    try:
        # 发起 HTTPS POST 请求
        response = requests.post(api_url, headers=headers, json=params, timeout=30)

        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: {response.status_code}, {response.text[:500]}")

        # 解析响应
        resp = response.json()

        # API返回格式: {"code": 2000, "data": {...}, "msg": "成功"}
        api_code = resp.get("code", 0)
        if api_code != 2000:
            raise Exception(f"API业务错误: code={api_code}, msg={resp.get('msg', '未知')}")

        api_data = resp.get("data", {})

        # 从API返回的content中提取违禁词列表
        # API格式: content中用<span class="banned-word">或<span class="sensitive-word">标记违禁词
        api_content = api_data.get("content", "")
        original_content = api_data.get("originalContent", content)
        prohibited_words_type = api_data.get("prohibitedWordsType", [])

        # 兼容处理：API返回content为空或None时（可能内容过长API未返回标记）
        if not api_content:
            api_content = original_content if original_content else content

        # 提取违禁词文本（兼容banned-word和sensitive-word两种类名，去重）
        sensitive_words = list(dict.fromkeys(
            re.findall(r'<span class="(?:banned-word|sensitive-word)">(.*?)</span>', api_content)
        ))

        # 将banned-word和sensitive-word样式统一替换为color:red样式
        html_content = re.sub(
            r'<span class="(?:banned-word|sensitive-word)">',
            '<span style="color:red">',
            api_content,
        )

        result = {
            "status": "success",
            "platform": platform,
            "original_content": original_content,
            "sensitive_words": sensitive_words,
            "prohibited_words_type": prohibited_words_type,
            "word_count": len(sensitive_words),
            "html_content": html_content,
        }

        return result

    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "platform": platform,
            "original_content": content,
            "error": f"响应解析失败: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "error",
            "platform": platform,
            "original_content": content,
            "error": f"处理失败: {str(e)}",
        }


def main():
    parser = argparse.ArgumentParser(description="违禁词检测工具")
    parser.add_argument("--content", required=True, help="待检测的文案内容")
    parser.add_argument("--platform", default="公众号", help="平台名称（公众号/小红书/抖音），默认为公众号")

    args = parser.parse_args()

    result = check_sensitive_words(args.content, args.platform)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
