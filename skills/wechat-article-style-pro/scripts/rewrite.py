#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wechat-article-style/scripts/rewrite.py

公众号文案改写辅助脚本

用途：
  - prompt：导出规则（无网络）
  - report：HTTPS POST 至记录接口，JSON 仅含固定字段 source

记录接口（report）：https://onetotenvip.com/story/content/rewriting
网络实现：http.client + 系统默认 TLS（校验证书与主机名）

用法：
  python rewrite.py prompt    # 输出公众号改写规则 prompt
  python rewrite.py report    # HTTPS POST，JSON 仅 {"source": "..."}
"""

import sys
import os
import re
import http.client
import ssl
import json
from typing import Dict, Any

# ── 路径 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(SCRIPT_DIR, '..', 'assets', 'platform-rules.md')

# ── 平台 ──────────────────────────────────────────────────────────────────────
PLATFORM = '公众号'

# ── 记录接口配置 ───────────────────────────────────────────────────────────────
RECORD_HOST = 'onetotenvip.com'
RECORD_PORT = 443
RECORD_PATH = '/story/content/rewriting'


# ─────────────────────────────────────────────────────────────────────────────
# 规则提取
# ─────────────────────────────────────────────────────────────────────────────

def extract_platform_rules() -> str:
    """读取规则文件，提取公众号规则块。"""
    rules_path = os.path.normpath(RULES_FILE)
    if not os.path.exists(rules_path):
        print(f'❌ 规则文件不存在：{rules_path}', file=sys.stderr)
        sys.exit(1)

    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取公众号部分（从 ## 公众号 到文件末尾）
    match = re.search(r'^## 公众号\n(.*)', content, re.DOTALL | re.MULTILINE)
    if match:
        return '## 公众号\n' + match.group(1).strip()
    return ''


# ─────────────────────────────────────────────────────────────────────────────
# 记录接口：标准 HTTPS（校验服务端证书，禁止 CERT_NONE）
# ─────────────────────────────────────────────────────────────────────────────

RECORD_SOURCE = '公众号文案改写-GitHub'


def report_rewrite() -> Dict[str, Any]:
    """
    向记录接口发送 HTTPS POST。

    负载仅包含 source；使用 ssl.create_default_context() 启用证书与主机名校验。
    """
    payload = json.dumps(
        {'source': RECORD_SOURCE},
        ensure_ascii=False
    ).encode('utf-8')

    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection(
        RECORD_HOST,
        RECORD_PORT,
        context=ctx,
        timeout=10,
    )
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Connection': 'close',
        'User-Agent': 'wechat-article-style/1.0',
    }

    try:
        conn.request('POST', RECORD_PATH, body=payload, headers=headers)
        resp = conn.getresponse()
        status_code = resp.status
        reason = resp.reason or ''
        status_line = f'HTTP/1.1 {status_code} {reason}'
        resp.read()
    except ssl.SSLError as e:
        return {'ok': False, 'error': f'SSL error: {e}'}
    except OSError as e:
        return {'ok': False, 'error': f'Network error: {e}'}
    except http.client.HTTPException as e:
        return {'ok': False, 'error': f'HTTP error: {e}'}
    finally:
        conn.close()

    return {
        'ok':          200 <= status_code < 300,
        'status_code': status_code,
        'status_line': status_line,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI 命令
# ─────────────────────────────────────────────────────────────────────────────

def cmd_prompt() -> None:
    """输出公众号改写规则 prompt。"""
    rules = extract_platform_rules()
    if not rules:
        print(f'\n❌ 规则文件中未找到公众号规则\n', file=sys.stderr)
        sys.exit(1)

    print(f'\n✅ 平台：{PLATFORM}\n')
    print('─' * 60)
    print('\n【System Prompt（供 AI 使用）】\n')
    print(rules)


def cmd_report() -> None:
    """调用记录接口（仅 source）。"""
    print(f'\n📡 调用记录接口（HTTPS，校验证书）…')
    result = report_rewrite()
    if result.get('ok'):
        print(f'✅ 成功（HTTP {result.get("status_code")}）')
    else:
        print(
            f'⚠️  失败：{result.get("error") or result.get("status_line")}',
            file=sys.stderr
        )


def print_help() -> None:
    print(f"""
📝 公众号文案改写辅助脚本

用法：
  python rewrite.py prompt                    # 输出公众号改写规则 prompt
  python rewrite.py report                    # POST 记录接口（JSON 仅 source）

注意：
  HTTPS；TLS 校验服务端证书。详见 SKILL.md「六、脚本步骤」。
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

    # ── report：记录接口 ─────────────────────────────────────────────────────
    if first == 'report':
        cmd_report()
        return

    print(
        '❌ 未知参数。请使用：python rewrite.py prompt | python rewrite.py report',
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == '__main__':
    main()
