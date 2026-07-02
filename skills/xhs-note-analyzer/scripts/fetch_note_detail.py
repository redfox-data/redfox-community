"""
小红书作品分析助手
功能：根据小红书笔记ID查询笔记完整详情信息（标题、正文、互动数据、作者信息等）
接口：POST https://redfox.hk/story/api/xhs/ability/noteDetail
鉴权：通过环境变量 REDFOX_API_KEY 读取密钥
说明：接口返回 {code, data, msg} 结构，脚本自动解包并增强字段
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from urllib import request, error


# ─────────────────────────────────────────────
# 输入解析：从多种格式中提取 noteId
# ─────────────────────────────────────────────

_EXPLORE_RE = re.compile(r"xiaohongshu\.com/explore/([0-9a-fA-F]{24})")
_DISCOVERY_RE = re.compile(r"xiaohongshu\.com/discovery/item/([0-9a-fA-F]{24})")
_RAW_ID_RE = re.compile(r"^[0-9a-fA-F]{24}$")
_SHORT_LINK_RE = re.compile(r"^https?://xhslink\.com/", re.IGNORECASE)


def extract_note_id(raw_input: str) -> tuple:
    """
    从用户输入中提取 noteId。
    返回 (note_id: str | None, error_msg: str | None)
    """
    raw_input = raw_input.strip()

    if _SHORT_LINK_RE.match(raw_input):
        return None, "不支持短链接（xhslink.com），请提供完整的小红书笔记链接。"

    m = _EXPLORE_RE.search(raw_input)
    if m:
        return m.group(1), None

    m = _DISCOVERY_RE.search(raw_input)
    if m:
        return m.group(1), None

    if _RAW_ID_RE.match(raw_input):
        return raw_input, None

    return None, (
        "无法从输入中识别笔记ID，请提供以下任意一种格式：\n"
        "  · 笔记链接：https://www.xiaohongshu.com/explore/{noteId}\n"
        "  · discovery链接：https://www.xiaohongshu.com/discovery/item/{noteId}\n"
        "  · 24位笔记ID：6a23eddb000000003502a39d"
    )


# ─────────────────────────────────────────────
# 数字与时间格式化
# ─────────────────────────────────────────────

def format_number(n) -> str:
    """将数字格式化为易读字符串"""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return str(n)

    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}亿"
    if n >= 10_000:
        return f"{n / 10_000:.1f}w"
    return str(n)


_CST = timezone(timedelta(hours=8))


def format_timestamp(ts) -> str:
    """将 Unix 秒级时间戳转为 YYYY-MM-DD HH:mm（CST）"""
    try:
        ts = int(ts)
        return datetime.fromtimestamp(ts, tz=_CST).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError, OSError):
        return ""


# ─────────────────────────────────────────────
# 字段增强
# ─────────────────────────────────────────────

_NOTE_TYPE_MAP = {"normal": "图文", "video": "视频"}


def enrich_note(note: dict) -> dict:
    """在原始笔记对象上追加增强字段并返回"""
    # 互动数（取不到则视为 0）
    thumb = int(note.get("thumbCount") or 0)
    fav = int(note.get("favoriteCount") or 0)
    reply = int(note.get("replyCount") or 0)
    fwd = int(note.get("forwardCount") or 0)
    total = thumb + fav + reply + fwd

    note["totalInteraction"] = total

    # 时间格式化
    if note.get("releaseTimestamp"):
        note["releaseTimeFormatted"] = format_timestamp(note["releaseTimestamp"])
    if note.get("lastEditTime"):
        note["lastEditTimeFormatted"] = format_timestamp(note["lastEditTime"])

    # 数字格式化
    note["thumbCountFormatted"] = format_number(thumb)
    note["favoriteCountFormatted"] = format_number(fav)
    note["replyCountFormatted"] = format_number(reply)
    note["forwardCountFormatted"] = format_number(fwd)
    note["totalInteractionFormatted"] = format_number(total)

    # 作品类型格式化
    raw_type = note.get("noteType")
    if raw_type in _NOTE_TYPE_MAP:
        note["noteTypeFormatted"] = _NOTE_TYPE_MAP[raw_type]

    return note


# ─────────────────────────────────────────────
# 接口调用
# ─────────────────────────────────────────────

def _get_api_key() -> str:
    api_key = os.environ.get("REDFOX_API_KEY")
    if not api_key:
        print(
            json.dumps(
                {"success": False, "error": "未配置 REDFOX_API_KEY 环境变量，请先完成鉴权配置。"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)
    return api_key


def fetch_note_detail(note_id: str) -> dict:
    """
    查询单篇笔记详情，返回增强后的笔记对象。
    失败时返回 {"success": False, "error": "...", "noteId": "..."} 形式。
    """
    api_key = _get_api_key()
    url = "https://redfox.hk/story/api/xhs/ability/noteDetail"
    payload = json.dumps({"noteId": note_id, "source": "小红书作品分析助手-GitHub"}).encode("utf-8")
    headers = {
        "REDFOX_API_KEY": api_key,
        "Content-Type": "application/json",
    }
    req = request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=30) as resp:
            status_code = resp.status
            body = resp.read().decode("utf-8")

            if status_code != 200:
                return {"success": False, "error": f"请求失败，状态码：{status_code}", "noteId": note_id}

            try:
                result = json.loads(body)
            except json.JSONDecodeError:
                return {"success": False, "error": "响应内容无法解析", "noteId": note_id}

            # ── 解包响应结构 ──
            code = result.get("code")
            msg = result.get("msg", "")
            data = result.get("data", [])

            if code != 2000:
                return {"success": False, "error": msg or f"接口返回异常，code={code}", "noteId": note_id}

            if not data:
                return {
                    "success": False,
                    "error": "该笔记可能已被删除或设为私密，无法获取详情。",
                    "noteId": note_id,
                }

            note = data[0]

            # ── 关键字段校验（缺失时不报错，保持正常输出）──
            for field in ("noteId", "noteTitle", "contentDesc"):
                if field not in note:
                    pass  # 静默处理，不阻断流程

            # ── 增强字段 ──
            note = enrich_note(note)
            note["success"] = True
            return note

    except error.HTTPError as e:
        return {"success": False, "error": f"请求失败，HTTP错误码：{e.code}", "noteId": note_id}

    except error.URLError as e:
        return {"success": False, "error": "网络请求失败，请检查网络连接", "noteId": note_id}

    except Exception as e:
        return {"success": False, "error": "未知错误", "detail": str(e), "noteId": note_id}


# ─────────────────────────────────────────────
# 批量查询
# ─────────────────────────────────────────────

def fetch_batch(raw_inputs: list) -> list:
    """批量查询，每个输入独立调用，失败不影响其他。"""
    results = []
    for raw in raw_inputs:
        note_id, err = extract_note_id(raw)
        if err:
            results.append({"success": False, "error": err, "noteId": raw.strip()})
            continue
        result = fetch_note_detail(note_id)
        results.append(result)
    return results


# ─────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="小红书作品分析助手")
    parser.add_argument(
        "--note-id",
        required=True,
        help="小红书笔记ID或笔记链接，多个用逗号分隔（自动判断格式）",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量查询模式：将 --note-id 的值按逗号拆分，逐一查询",
    )
    args = parser.parse_args()

    raw_value = args.note_id.strip()

    if not raw_value:
        print(
            json.dumps({"success": False, "error": "笔记ID不能为空"}, ensure_ascii=False)
        )
        sys.exit(1)

    if args.batch:
        raw_inputs = [item.strip() for item in raw_value.split(",") if item.strip()]
        if not raw_inputs:
            print(
                json.dumps({"success": False, "error": "未提供有效的笔记ID或链接"}, ensure_ascii=False)
            )
            sys.exit(1)
        results = fetch_batch(raw_inputs)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        note_id, err = extract_note_id(raw_value)
        if err:
            print(json.dumps({"success": False, "error": err}, ensure_ascii=False))
            sys.exit(1)
        result = fetch_note_detail(note_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result.get("success"):
            sys.exit(1)


if __name__ == "__main__":
    main()
