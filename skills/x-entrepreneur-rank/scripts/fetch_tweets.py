#!/usr/bin/env python3
"""
拉取企业家榜 Top N 账号的第一页推文，供「大佬们在关注什么」话题总结使用。
用法：
    python fetch_tweets.py --data entrepreneur_rank_data.json
    python fetch_tweets.py --data rank.json --days 30 --max 20 --output tweets.json
接口：POST https://redfox.hk/story/api/x/userTimeline  {"screenName": handle, "pageNum": 1, "source": <SOURCE>}
失败/无推文的账号自动跳过并在 skipped 中记录。
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/x/userTimeline"
SOURCE = "X企业家榜单-GitHub"  # 接口固定 source 参数
TWITTER_TIME_FMT = "%a %b %d %H:%M:%S %z %Y"


def _get_api_key():
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if not api_key:
        print("[ERROR] 未设置 REDFOX_API_KEY 环境变量", file=sys.stderr)
        print("[HINT] 请运行: export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
        print("[HINT] 访问 https://redfox.hk/settings/api-keys?source=github 获取 API Key", file=sys.stderr)
        sys.exit(4)
    return api_key


def fetch_timeline(handle, timeout=25):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"screenName": handle, "pageNum": 1,
                         "source": SOURCE}).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-KEY": _get_api_key()},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_created_at(s):
    try:
        return datetime.strptime(s, TWITTER_TIME_FMT)
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description="拉取榜内账号第一页推文")
    parser.add_argument("--data", required=True, help="fetch_rank.py 输出的榜单 JSON")
    parser.add_argument("--days", type=int, default=30, help="只保留近 N 天推文（默认 30）")
    parser.add_argument("--max", type=int, default=20, help="最多拉取前 N 个账号（默认 20）")
    parser.add_argument("--output", default=None, help="推文 JSON 输出路径")
    parser.add_argument("--sleep", type=float, default=0.4, help="账号间隔秒数，防限流")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        payload = json.load(f)
    items = payload.get("items", [])[:args.max]
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    accounts, skipped = [], []
    for it in items:
        handle = it.get("handle") or ""
        if not handle:
            skipped.append({"handle": "", "fullName": it.get("fullName"), "reason": "无 handle"})
            continue
        try:
            resp = fetch_timeline(handle)
        except urllib.error.HTTPError as e:
            skipped.append({"handle": handle, "fullName": it.get("fullName"), "reason": f"HTTP {e.code}"})
            continue
        except Exception as e:  # 网络超时等：跳过该账号，不中断整批
            skipped.append({"handle": handle, "fullName": it.get("fullName"), "reason": str(e)[:80]})
            continue
        if resp.get("code") != 2000:
            skipped.append({"handle": handle, "fullName": it.get("fullName"),
                            "reason": f"code={resp.get('code')} {resp.get('msg')}"})
            continue

        tweets = []
        for t in (resp.get("data") or {}).get("timeline") or []:
            created = parse_created_at(t.get("createdAt"))
            if created and created < cutoff:
                continue
            tid = str(t.get("tweetId") or "")
            tweets.append({
                "tweetId": tid,
                "url": f"https://x.com/{handle}/status/{tid}" if tid else "",
                "text": (t.get("text") or "").strip(),
                "createdAt": t.get("createdAt") or "",
                "createdAtIso": created.strftime("%Y-%m-%d") if created else "",
                "likeCount": t.get("likeCount"),
                "retweetCount": t.get("retweetCount"),
                "viewCount": t.get("viewCount"),
                "isRetweet": (t.get("text") or "").startswith("RT @"),
            })
        if not tweets:
            skipped.append({"handle": handle, "fullName": it.get("fullName"), "reason": "近30天无推文"})
            continue
        accounts.append({
            "rank": it.get("rank"), "fullName": it.get("fullName"), "handle": handle,
            "title": it.get("title"), "tweetCount": len(tweets), "tweets": tweets,
        })
        time.sleep(args.sleep)

    result = {
        "meta": {
            "rankDate": (payload.get("meta") or {}).get("rankDate"),
            "days": args.days,
            "accountCount": len(accounts),
            "tweetCount": sum(a["tweetCount"] for a in accounts),
            "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "accounts": accounts,
        "skipped": skipped,
    }
    out_path = args.output or os.path.join(os.getcwd(), "entrepreneur_tweets.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[INFO] 推文拉取完成：成功 {len(accounts)} 个账号 / 跳过 {len(skipped)} 个 / "
          f"近{args.days}天推文 {result['meta']['tweetCount']} 条")
    for s in skipped:
        print(f"[WARN] 跳过 {s.get('fullName') or s.get('handle')}：{s['reason']}")
    print(f"[INFO] 推文文件：{out_path}")


if __name__ == "__main__":
    main()
