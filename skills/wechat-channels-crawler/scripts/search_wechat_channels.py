#!/usr/bin/env python3
"""
视频号作品搜索脚本
调用 Redfox API 搜索视频号热门作品数据
用法: python3 search_wechat_channels.py "<关键词>" [--sort 综合|最新|最多点赞|最多收藏] [--page 1] [--size 20]
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/sphAllData/searchWork"

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
    """从环境变量获取 API Key"""
    val = os.environ.get("REDFOX_API_KEY")
    if val:
        return val
    print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
    sys.exit(1)


def search(keyword: str, sort: str = "综合", page: int = 1, size: int = 20) -> dict:
    """调用搜索接口，返回 {total, list}"""
    api_key = get_api_key()
    payload = json.dumps({
        "keyword": keyword,
        "sort": sort,
        "page": page,
        "size": size,
        "source": "视频号作品爬虫-GitHub",
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
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
    raw_list = data.get("list") or []
    total = data.get("total", 0) or 0

    # 提取需要的字段并统一格式
    items = []
    for work in raw_list:
        # 解析 topic 字段（API 返回 JSON 字符串）
        topics = []
        topic_raw = work.get("topic", "")
        if topic_raw:
            try:
                topics = json.loads(topic_raw) if isinstance(topic_raw, str) else topic_raw
            except (json.JSONDecodeError, TypeError):
                topics = []

        items.append({
            "title": work.get("description", "").strip(),
            "author": work.get("nickname", "").strip(),
            "author_avatar": work.get("headUrl", ""),
            "like_count": work.get("likeCount", 0) or 0,
            "comment_count": work.get("commentCount", 0) or 0,
            "share_count": work.get("forwardCount", 0) or 0,
            "collect_count": work.get("favCount", 0) or 0,
            "work_url": work.get("videoUrl", ""),
            "publish_time": work.get("publishTime", ""),
            "topics": topics,
            "duration": int(work.get("videoDuration", 0) or 0),
            "cover_url": work.get("coverUrl", ""),
        })

    return {"total": total, "list": items}


def main():
    # 强制 stdout 使用 UTF-8 编码，避免 Windows GBK 环境下 emoji 等字符报错
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="视频号作品搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--sort", choices=["综合", "最新", "最多点赞", "最多收藏"],
                        default="综合", help="排序方式（默认：综合）")
    parser.add_argument("--page", type=int, default=1, help="页码，从1开始（默认：1）")
    parser.add_argument("--size", type=int, default=20, help="每页条数，最大50（默认：20）")
    parser.add_argument("--output", "-o", help="输出到 JSON 文件（UTF-8 编码），避免 shell 重定向乱码")

    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)

    # 限制 size 最大 50
    size = min(args.size, 50)

    result = search(keyword, sort=args.sort, page=args.page, size=size)
    json_str = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"结果已写入: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
