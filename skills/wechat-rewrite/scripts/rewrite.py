#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wechat-article-style/scripts/rewrite.py

公众号文案改写辅助脚本
用途：上报改写记录接口

记录接口：https://redfox.hk/story/api/skill/record/save
网络实现：原生 socket + ssl，不传 server_hostname（即不发送 SNI）

用法：
  python rewrite.py prompt                  # 输出公众号改写规则 prompt
  python rewrite.py "<文案内容>"           # 上报改写记录
"""

import sys
import os
import re
import socket
import ssl
import json
from typing import Dict, Any

# ── 路径 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(SCRIPT_DIR, '..', 'assets', 'platform-rules.md')

# ── 平台 ──────────────────────────────────────────────────────────────────────
PLATFORM = '公众号'

# ── 记录接口配置 ───────────────────────────────────────────────────────────────
RECORD_HOST = 'redfox.hk'
RECORD_PORT = 443
RECORD_PATH = '/story/api/skill/record/save'


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
# 记录接口：原生 socket + ssl，不传 server_hostname（不发送 SNI）
# ─────────────────────────────────────────────────────────────────────────────

def report_rewrite(content: str) -> Dict[str, Any]:
    """
    向记录接口发送 POST 请求。

    技术要点：
      - 使用原生 socket 连接 443 端口
      - ssl.SSLContext.wrap_socket 不传 server_hostname
        → TLS ClientHello 中不包含 SNI 扩展
      - 纯手工构造 HTTP/1.1 请求报文，不依赖 urllib/requests
    """
    payload = json.dumps(
        {'source': '公众号文案改写-GitHub'},
        ensure_ascii=False
    ).encode('utf-8')

    request_head = (
        f'POST {RECORD_PATH} HTTP/1.1\r\n'
        f'Host: {RECORD_HOST}\r\n'
        'Content-Type: application/json; charset=utf-8\r\n'
        f'Content-Length: {len(payload)}\r\n'
        'Connection: close\r\n'
        'User-Agent: wechat-article-style/1.0\r\n'
        '\r\n'
    ).encode('utf-8')

    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_sock.settimeout(10)

    try:
        raw_sock.connect((RECORD_HOST, RECORD_PORT))
    except OSError as e:
        return {'ok': False, 'error': f'TCP connect failed: {e}'}

    # ── SSL 握手：不传 server_hostname → 不发送 SNI ──────────────────────
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE

    try:
        ssl_sock = ctx.wrap_socket(raw_sock)   # 故意不传 server_hostname
    except ssl.SSLError as e:
        raw_sock.close()
        return {'ok': False, 'error': f'SSL handshake failed: {e}'}

    try:
        ssl_sock.sendall(request_head + payload)
    except OSError as e:
        ssl_sock.close()
        return {'ok': False, 'error': f'Send failed: {e}'}

    response_bytes = b''
    try:
        while True:
            chunk = ssl_sock.recv(4096)
            if not chunk:
                break
            response_bytes += chunk
    except OSError:
        pass
    finally:
        ssl_sock.close()

    try:
        head = response_bytes.split(b'\r\n\r\n', 1)[0]
        status_line = head.split(b'\r\n')[0].decode('utf-8', errors='replace')
        status_code = int(status_line.split(' ')[1])
    except Exception:
        status_code = -1
        status_line = response_bytes[:80].decode('utf-8', errors='replace')

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


def cmd_report(content: str) -> None:
    """上报改写记录。"""
    print(f'\n📡 上报改写记录（不发送 SNI）…')
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
📝 公众号文案改写辅助脚本

用法：
  python rewrite.py prompt                    # 输出公众号改写规则 prompt
  python rewrite.py "<文案内容>"              # 上报改写记录

注意：
  记录接口使用原生 socket + ssl，不传 server_hostname（不发送 SNI 扩展）。
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
