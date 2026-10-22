#!/usr/bin/env python3
"""
抖音爆款作品搜索脚本
调用 Redfox API 搜索抖音热门作品数据
用法: python3 search_douyin.py "<关键词>" [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
"""

import sys
import os
import json
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/dy/data/searchWork"

PAYMENT_EXIT_CODE = 3
INSUFFICIENT_CODES = {3210, 3201}


def emit_payment_required(resp):
    data = resp.get("data")
    data = data if isinstance(data, dict) else {}
    cashier_url = data.get("cashierUrl")
    amount = data.get("amount")
    goods_name = data.get("goodsName")
    out = sys.stdout.write
    out(f"\n💳 积分不足，需要充值（API code={resp.get('code')}）\n")
    out(f"消息：{resp.get('msg', '积分不足')}\n")
    out(f"商品名称：{goods_name or '-'}\n")
    out(f"订单金额：{amount if amount is not None else '-'} 元\n")
    out(f"订单号：{data.get('outTradeNo') or '-'}\n")
    if data.get("expireTime"):
        out(f"支付截止：{data.get('expireTime')}\n")
    out("\n请严格按 references/alipay-recharge.md「支付宝充值接管流程（通用）」处理：\n")
    out("  1) 将下方 cashierUrl 原文作为支付链接（--payment-link）\n")
    out("  2) amount=订单金额、goodsName=商品名称，直接用于 --amount / --merchant-info\n")
    out("  3) alipay-bot trigger-payment-signal 压缩得到支付短链 paymentLink\n")
    out("  4) alipay-bot submit-payment 用支付短链唤起支付宝，解析查询单号 out-shake-no\n")
    out("  5) alipay-bot poll-payment-status --out-shake-no 自动监听到账\n")
    out("  6) 到账（outcome=success）后，用原始查询参数重新运行本脚本\n\n")
    payload = {
        "need_payment": True,
        "code": resp.get("code"),
        "msg": resp.get("msg", "积分不足"),
        "cashierUrl": cashier_url,
        "amount": amount,
        "goodsName": goods_name,
        "outTradeNo": data.get("outTradeNo"),
        "expireTime": data.get("expireTime"),
        "points": data.get("points"),
    }
    out("===PAYMENT_REQUIRED_JSON_START===\n")
    out(json.dumps(payload, ensure_ascii=False))
    out("\n===PAYMENT_REQUIRED_JSON_END===\n")
    sys.stdout.flush()


def get_api_key() -> str:
    """从环境变量获取 API Key，"""
    for key_name in ["REDFOX_API_KEY"]:
        val = os.environ.get(key_name)
        if val:
            return val
    print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
    sys.exit(1)


def format_articles(articles: list) -> list:
    """将原始 articles 数据转换为统一格式"""
    items = []
    for art in articles:
        items.append({
            "title": art.get("content", "").strip(),
            "author": art.get("authorName", "").strip(),
            "like_count": art.get("likeCount", 0) or 0,
            "comment_count": art.get("commentCount", 0) or 0,
            "share_count": art.get("shareCount", 0) or 0,
            "collect_count": art.get("collectCount", 0) or 0,
            "work_url": art.get("opusUrl", ""),
            "publish_time": art.get("publishTime", ""),
        })
    # 按点赞数降序排列
    items.sort(key=lambda x: x["like_count"], reverse=True)
    return items


def search(keyword: str, start_date: str = "", end_date: str = "", page_num: int = 1, page_size: int = 50) -> dict:
    """调用搜索接口，返回完整数据（articles, total, pageNum, pageSize）"""
    api_key = get_api_key()
    payload_dict = {
        "keyword": keyword,
        "source": "抖音作品查询-GitHub",
        "pageNum": page_num,
        "pageSize": page_size,
    }
    if start_date:
        payload_dict["startDate"] = start_date
    if end_date:
        payload_dict["endDate"] = end_date
    payload = json.dumps(payload_dict).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "REDFOX_API_KEY": api_key,
            "User-Agent": "QoderWork/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
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
    if code in INSUFFICIENT_CODES:
        emit_payment_required(result)
        sys.exit(PAYMENT_EXIT_CODE)
    if code != 2000:
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data") or {}

    return {
        "articles": format_articles(data.get("list") or []),
        "total": data.get("total", 0),
        "pageNum": data.get("pageNum", 1),
        "pageSize": data.get("pageSize", page_size),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="抖音爆款作品搜索脚本")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--start-date", "-s", default="", help="起始日期，格式 YYYY-MM-DD（默认：空字符串）")
    parser.add_argument("--end-date", "-e", default="", help="结束日期，格式 YYYY-MM-DD（默认：空字符串）")
    parser.add_argument("--page-num", "-p", type=int, default=1, help="页码，从1开始（默认：1）")
    parser.add_argument("--page-size", type=int, default=50, help="每页大小（默认：50，最大50）")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, start_date=args.start_date, end_date=args.end_date,
                     page_num=args.page_num, page_size=args.page_size)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
