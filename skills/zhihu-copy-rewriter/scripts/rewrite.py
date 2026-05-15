#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wechat-article-style/scripts/rewrite.py

知乎文案改写辅助脚本
用途：上报改写记录接口

记录接口：https://onetotenvip.com/story/content/rewriting
网络实现：标准 HTTPS（urllib，校验证书、默认 TLS 行为）

用法：
  python rewrite.py prompt                  # 输出知乎改写规则 prompt
  python rewrite.py "<文案内容>"           # 上报改写记录
"""

import sys
import os
import re
import json
import urllib.error
import urllib.request
from typing import Dict, Any

# ── 路径 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(SCRIPT_DIR, '..', 'assets', 'platform-rules.md')

# ── 平台 ──────────────────────────────────────────────────────────────────────
PLATFORM = '知乎'

# ── 记录接口配置 ───────────────────────────────────────────────────────────────
RECORD_HOST = 'onetotenvip.com'
RECORD_PATH = '/story/content/rewriting'


# ─────────────────────────────────────────────────────────────────────────────
# 规则提取
# ─────────────────────────────────────────────────────────────────────────────

def extract_platform_rules() -> str:
    """读取规则文件，提取知乎规则块。"""
    rules_path = os.path.normpath(RULES_FILE)
    if not os.path.exists(rules_path):
        print(f'❌ 规则文件不存在：{rules_path}', file=sys.stderr)
        sys.exit(1)

    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取知乎部分（从 ## 知乎 到文件末尾）
    match = re.search(r'^## 知乎\n(.*)', content, re.DOTALL | re.MULTILINE)
    if match:
        return '## 知乎\n' + match.group(1).strip()
    return ''


# ─────────────────────────────────────────────────────────────────────────────
# 记录接口：标准 HTTPS（校验服务端证书，遵循平台默认 TLS/SNI 行为）
# ─────────────────────────────────────────────────────────────────────────────

def report_rewrite(content: str) -> Dict[str, Any]:
    """向记录接口发送 POST 请求（HTTPS，证书校验开启）。"""
    payload = json.dumps(
        {'source': '知乎文案改写-GitHub'},
        ensure_ascii=False
    ).encode('utf-8')

    url = f'https://{RECORD_HOST}{RECORD_PATH}'
    req = urllib.request.Request(
        url,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'wechat-article-style/1.0',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.getcode()
            reason = getattr(resp, 'reason', '') or ''
            status_line = f'HTTP/1.1 {status_code} {reason}'.strip()
            return {
                'ok':          200 <= status_code < 300,
                'status_code': status_code,
                'status_line': status_line,
            }
    except urllib.error.HTTPError as e:
        return {
            'ok': False,
            'status_code': e.code,
            'status_line': str(e),
            'error':       f'HTTP {e.code}: {e.reason}',
        }
    except urllib.error.URLError as e:
        err = e.reason if getattr(e, 'reason', None) is not None else str(e)
        return {'ok': False, 'error': str(err)}


# ─────────────────────────────────────────────────────────────────────────────
# CLI 命令
# ─────────────────────────────────────────────────────────────────────────────

def cmd_prompt() -> None:
    """输出知乎改写规则 prompt。"""
    rules = extract_platform_rules()
    if not rules:
        print(f'\n❌ 规则文件中未找到知乎规则\n', file=sys.stderr)
        sys.exit(1)

    print(f'\n✅ 平台：{PLATFORM}\n')
    print('─' * 60)
    print('\n【System Prompt（供 AI 使用）】\n')
    print(rules)


def cmd_report(content: str) -> None:
    """上报改写记录。"""
    print(f'\n📡 上报改写记录（HTTPS）…')
    result = report_rewrite(content)
    if result.get('ok'):
        print(f'✅ 上报成功（HTTP {result.get("status_code")}）')
    else:
        print(
            f'⚠️  上报失败：{result.get("error") or result.get("status_line")}',
            file=sys.stderr
        )


def print_help() -> None:
    print(f"""
📝 知乎文案改写辅助脚本

用法：
  python rewrite.py prompt                    # 输出知乎改写规则 prompt
  python rewrite.py "<文案内容>"              # 上报改写记录

注意：
  记录接口使用标准 HTTPS，启用证书校验。
""")


# ─────────────────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print_help()
        sys.exit(0)

    first = args[0].lower()

    # ── prompt ──────────────────────────────────────────────────────────────
    if first == 'prompt':
        cmd_prompt()
        return

    # ── 上报记录 ────────────────────────────────────────────────────────────
    content = ' '.join(args)
    cmd_report(content)


if __name__ == '__main__':
    main()
