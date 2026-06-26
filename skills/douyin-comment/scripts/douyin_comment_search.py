#!/usr/bin/env python3
"""
抖音评论分析脚本
调用 Redfox API 获取抖音作品一级评论数据，同步生成 HTML 报告
用法: python3 douyin_comment_search.py "<videoId>" [--offset 0] [--no-html] [--output-dir ~/Downloads/QoderReports]
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime

API_URL = "https://redfox.hk/story/api/dy/work/comment"
PAGE_SIZE = 20  # 每页固定 20 条

# 脚本所在目录，用于定位模板
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "report_template.html")


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        print("[hint] 获取 API Key: https://redfox.hk/settings/api-keys?source=github", file=sys.stderr)
        print("[hint] 配置: export REDFOX_API_KEY=ak_xxxx...", file=sys.stderr)
        sys.exit(1)
    return val


def call_api(video_id: str, offset: int, api_key: str) -> dict:
    """单次调用评论接口，返回原始 JSON 数据"""
    payload = json.dumps({
        "videoId": video_id,
        "offset": str(offset),
        "source": "抖音作品评论-GitHub",
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
    if code != 2000:
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    return result


def format_comment(raw: dict) -> dict:
    """将 API 返回的原始评论格式化为统一结构
    
    API 实际返回字段（data.commentList[]）：
    authorAccount, authorAvatarUrls(list), authorName, authorSecUid, authorUid,
    commentId, ipLocation, isTop, likeCount, publishTime, replyCount, text
    """
    author_uid = raw.get("authorUid", "") or ""
    sec_uid = raw.get("authorSecUid", "") or ""
    user_url = f"https://www.douyin.com/user/{sec_uid}" if sec_uid else (
        f"https://www.douyin.com/user/{author_uid}" if author_uid else ""
    )

    # authorAvatarUrls 是数组，取第一个（100x100）
    avatars = raw.get("authorAvatarUrls") or []
    avatar = avatars[0] if isinstance(avatars, list) and avatars else ""

    return {
        "comment_id": raw.get("commentId", ""),
        "content": (raw.get("text", "") or "").strip(),
        "like_count": raw.get("likeCount", 0) or 0,
        "reply_count": raw.get("replyCount", 0) or 0,
        "create_time": raw.get("publishTime", "") or "",
        "ip_location": raw.get("ipLocation", "") or "",
        "user_name": (raw.get("authorName", "") or "").strip(),
        "user_avatar": avatar,
        "user_id": author_uid,
        "user_url": user_url,
        "is_top": bool(raw.get("isTop", False)),
    }


def fetch_comments(video_id: str, offset: int, api_key: str) -> tuple:
    """
    单次调用接口获取当前页评论数据（每次仅调用一次 API）。
    返回 (comments_list, has_next)
    """
    result = call_api(video_id, offset, api_key)
    data = result.get("data") or {}
    page_comments = data.get("commentList") or []
    if not isinstance(page_comments, list):
        page_comments = []
    all_comments = [format_comment(c) for c in page_comments]

    # 判断是否有下一页：基于 API 返回的 hasMore 字段
    has_next = bool(data.get("hasMore"))

    return all_comments, has_next


def main():
    parser = argparse.ArgumentParser(description="抖音作品评论查询")
    parser.add_argument("video_id", help="抖音作品 videoId")
    parser.add_argument(
        "--offset", dest="offset", type=int, default=0,
        help="偏移量（默认0，每页20条）",
    )
    parser.add_argument(
        "--no-html", dest="no_html", action="store_true",
        help="跳过 HTML 报告生成",
    )
    parser.add_argument(
        "--output-dir", dest="output_dir", type=str, default=None,
        help="HTML 输出目录（默认 ~/Downloads/QoderReports）",
    )

    args = parser.parse_args()

    video_id = args.video_id.strip()
    if not video_id:
        print("[error] videoId 不能为空", file=sys.stderr)
        sys.exit(1)
    if args.offset < 0:
        print("[error] offset 必须为非负整数", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()

    comments, has_next = fetch_comments(video_id, args.offset, api_key)

    total = len(comments)
    current_page = (args.offset // PAGE_SIZE) + 1

    output = {
        "video_id": video_id,
        "current_page": current_page,
        "offset": args.offset,
        "total_fetched": total,
        "has_next": has_next,
        "comments": comments,
        "total_count": total,
    }

    # HTML 报告生成
    if not args.no_html:
        html_path = generate_html_report(
            video_id=video_id,
            current_page=current_page,
            comments=comments,
            output_dir=args.output_dir,
        )
        output["html_path"] = html_path

    print(json.dumps(output, ensure_ascii=False, indent=2))


def escape_html(text: str) -> str:
    """HTML 实体转义"""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_comment_rows(comments: list) -> str:
    """根据评论列表生成 HTML 表格行"""
    rows = []
    for c in comments:
        is_top = c.get("is_top", False)
        row_class = ' class="top-comment"' if is_top else ""
        pin_badge = '<span class="top-badge">📌 置顶</span>' if is_top else ""

        avatar = c.get("user_avatar", "") or ""
        name = escape_html(c.get("user_name", ""))
        url = c.get("user_url", "") or "#"
        content = escape_html(c.get("content", ""))
        like = c.get("like_count", 0) or 0
        reply = c.get("reply_count", 0) or 0
        time_str = (c.get("create_time", "") or "")[5:16]  # YYYY-MM-DD HH:MM:SS → MM-DD HH:MM
        ip = escape_html(c.get("ip_location", ""))

        row = (
            f'<tr{row_class}>'
            f'<td>'
            f'<div class="user-cell">'
            f'<img src="{avatar}" class="user-avatar" alt="" onerror="this.style.display=\'none\'" referrerpolicy="no-referrer">'
            f'<a href="{url}" target="_blank" class="user-name">{name}{pin_badge}</a>'
            f'</div>'
            f'</td>'
            f'<td class="content-cell">{content}</td>'
            f'<td class="num-cell">{like}</td>'
            f'<td class="num-cell">{reply}</td>'
            f'<td class="time-cell">{time_str}</td>'
            f'<td class="ip-cell">{ip}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def generate_html_report(video_id: str, current_page: int, comments: list, output_dir: str = None) -> str:
    """
    读取 HTML 模板，填充评论数据，生成报告文件。
    返回生成的 HTML 文件绝对路径。
    """
    # 读取模板
    template_path = os.path.normpath(TEMPLATE_PATH)
    if not os.path.exists(template_path):
        print(f"[warn] 模板文件不存在: {template_path}，跳过 HTML 生成", file=sys.stderr)
        return ""

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    total = len(comments)
    now = datetime.now()

    # 计算基本统计
    total_likes = sum(c.get("like_count", 0) or 0 for c in comments)

    # 占位符替换
    # 数据占位 — 脚本直接填充
    # 分析占位 — 保留 {{PLACEHOLDER}}，后续由 backfill_html.py 回填
    replacements = {
        "{{VIDEO_ID}}": escape_html(video_id),
        "{{DATE}}": now.strftime("%Y-%m-%d"),
        "{{TOTAL_COMMENTS}}": str(total),
        "{{COMMENT_ROWS}}": build_comment_rows(comments),
        "{{TIMESTAMP}}": now.strftime("%Y-%m-%d %H:%M:%S"),
        "{{TOTAL_LIKES}}": str(total_likes),
        "{{PAGE}}": str(current_page),
        # {{POSITIVE_RATIO}} / {{NEGATIVE_RATIO}} / {{DEMAND_RATIO}} / {{COMPETITOR_RATIO}}
        # {{SUMMARY_POSITIVE}} / {{SUMMARY_NEGATIVE}} / {{SUMMARY_DEMAND}} / {{SUMMARY_COMPETITOR}}
        # 以上分析占位符不在脚本中替换，保留原样，由 backfill_html.py 统一回填
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    # 确定输出目录
    if output_dir:
        out_dir = os.path.expanduser(output_dir)
    else:
        out_dir = os.path.expanduser("~/Downloads/QoderReports")
    os.makedirs(out_dir, exist_ok=True)

    filename = f"抖音评论分析_{video_id}_p{current_page}.html"
    file_path = os.path.join(out_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[html] HTML 报告已生成: {file_path}", file=sys.stderr)
    return file_path


if __name__ == "__main__":
    main()
