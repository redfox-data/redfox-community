#!/usr/bin/env python3
"""
公众号账号搜索脚本
调用 Redfox API 搜索公众号账号数据
用法: python3 search_gzh_account.py "<关键词>" [--page 1]
"""

import sys
import os
import json
import argparse
import ssl
import urllib.request
import urllib.error
import urllib.parse

API_URL = "https://redfox.hk/story/api/gzh/ability/searchAccount"

PAGE_SIZE = 10


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def _ssl_context():
    """创建兼容多环境的 SSL 上下文"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    except Exception:
        ctx = None
    return ctx


def format_accounts(account_list: list) -> list:
    """
    格式化账号列表。
    API 返回字段：nickname, account, introduction
    """
    items = []
    for acc in account_list:
        if not isinstance(acc, dict):
            continue

        nickname = (acc.get("nickname") or "").strip()
        # Markdown 转义：防止 _、`、*、| 等字符破坏表格渲染
        for ch in ["_", "`", "*", "|", "[", "]"]:
            nickname = nickname.replace(ch, "\\" + ch)
        account_id = (acc.get("account") or "").strip()
        introduction = (acc.get("introduction") or "").strip()

        # 清理简介中的换行
        introduction = introduction.replace("\n", " ").replace("\r", "")

        # 构建跳转链接，对 account_id 中的特殊字符做 URL 编码，避免 Markdown 渲染时被转义
        profile_url = ""
        if account_id:
            # quote 不会编码 _ - . ~，手动将 _ 替换为 %5F 防止 Markdown 转义
            encoded = urllib.parse.quote(account_id, safe='')
            encoded = encoded.replace('_', '%5F')
            profile_url = f"https://open.weixin.qq.com/qr/code?username={encoded}"

        items.append({
            "nickname":     nickname,
            "account_id":   account_id,
            "introduction": introduction,
            "profile_url":  profile_url,
        })
    return items


def search(keyword: str, page: int = 1, cursor: int = 0) -> dict:
    api_key = get_api_key()

    payload_dict = {
        "keyword": keyword,
        "cursor":  cursor,
        "source":  "公众号账号搜索-GitHub",
    }

    payload = json.dumps(payload_dict).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key":    api_key,
            "User-Agent":   "QoderWork/1.0",
        },
        method="POST",
    )

    ctx = _ssl_context()

    try:
        kwargs = {"timeout": 30}
        if ctx:
            kwargs["context"] = ctx
        with urllib.request.urlopen(req, **kwargs) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[error] HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[error] 网络请求失败: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[error] 数据解析异常: {e}", file=sys.stderr)
        sys.exit(1)

    code = result.get("code")
    if code != 2000:
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data_list = result.get("data") or []
    data = data_list[0] if isinstance(data_list, list) and len(data_list) > 0 else {}

    account_list = data.get("accountList") or data.get("accounts") or []
    accounts_count = len(account_list)
    next_cursor = data.get("cursor") or 0

    has_next = accounts_count >= PAGE_SIZE

    return {
        "accounts":   format_accounts(account_list),
        "page":       page,
        "has_next":   has_next,
        "total":      accounts_count,
        "cursor":     next_cursor,
    }


def main():
    parser = argparse.ArgumentParser(description="公众号账号搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从1开始（默认1）",
    )
    parser.add_argument(
        "--cursor", dest="cursor", type=int, default=0,
        help="翻页游标，第一页传0（内部使用）",
    )
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, args.page, args.cursor)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
