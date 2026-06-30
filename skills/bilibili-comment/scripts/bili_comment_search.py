#!/usr/bin/env python3
"""
B站评论分析脚本
调用 Redfox API 获取B站视频一级评论数据，同步生成 HTML 报告
两步异步接口：commentSubmit 提交任务 → commentResult 轮询结果
用法: python3 bili_comment_search.py "<bvId>" [--page 1] [--no-html] [--output-dir ~/Downloads/QoderReports]
"""

import sys
import os
import re
import json
import time
import argparse
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

SUBMIT_API = "https://redfox.hk/story/api/bili/commentSubmit"
RESULT_API = "https://redfox.hk/story/api/bili/commentResult"
WORK_DETAIL_API = "https://redfox.hk/story/api/bili/workDetail"
PAGE_SIZE = 20  # 每页固定 20 条
MAX_POLL_ATTEMPTS = 30  # 最大轮询次数
POLL_INTERVAL = 2  # 轮询间隔（秒）

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


def extract_bv_id(input_str: str) -> str:
    """从用户输入中提取 BV号（支持直接 BV号或完整链接）"""
    input_str = input_str.strip()
    # 匹配 BV号（以 BV 开头，后跟字母数字）
    match = re.search(r"(BV[A-Za-z0-9]+)", input_str)
    if match:
        return match.group(1)
    return input_str


def fetch_work_detail(bv_id: str, api_key: str) -> dict:
    """获取作品详情（同步接口，POST JSON）"""
    payload = {
        "bvid": bv_id,
        "source": "B站评论分析-GitHub",
    }
    result = api_request(WORK_DETAIL_API, payload, api_key)

    code = result.get("code")
    if code != 2000:
        print(f"[warn] 获取作品详情失败: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        return {}

    data = result.get("data") or {}
    if not data:
        return {}

    # 发布时间（时间戳转字符串）
    publish_time = data.get("publishTime") or ""
    if isinstance(publish_time, (int, float, str)):
        try:
            ts = int(publish_time)
            if ts > 1000000000:
                publish_time = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            publish_time = str(publish_time)

    # 时长（秒转 MM:SS）
    duration = data.get("duration") or 0
    if isinstance(duration, (int, float)):
        mins = int(duration) // 60
        secs = int(duration) % 60
        duration_str = f"{mins}:{secs:02d}"
    else:
        duration_str = str(duration)

    owner = data.get("owner") or {}
    stats = data.get("stats") or {}

    return {
        "title": data.get("title") or "",
        "author_name": owner.get("nickname") or "",
        "author_uid": str(owner.get("uid") or ""),
        "author_avatar": owner.get("avatar") or "",
        "cover": data.get("cover") or "",
        "publish_time": publish_time,
        "duration": duration_str,
        "view_count": stats.get("viewCount") or 0,
        "like_count": stats.get("likeCount") or 0,
        "coin_count": stats.get("coinCount") or 0,
        "favorite_count": stats.get("favoriteCount") or 0,
        "share_count": stats.get("shareCount") or 0,
        "reply_count": stats.get("replyCount") or 0,
        "danmaku_count": stats.get("danmakuCount") or 0,
    }


def api_request(url: str, payload: dict, api_key: str) -> dict:
    """通用 API 请求函数"""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": "QoderWork/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
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

    return result


def submit_comment_task(bv_id: str, offset: int, api_key: str, sort_type: str = "1", data_num: int = PAGE_SIZE) -> str:
    """提交评论查询任务，返回 taskId
    
    API 必填参数：opusId（视频标识）、sortType（排序方式）、dataNum（每页条数）
    """
    payload = {
        "opusId": bv_id,
        "sortType": sort_type,
        "dataNum": str(data_num),
        "offset": str(offset),
        "source": "B站评论分析-GitHub",
    }

    result = api_request(SUBMIT_API, payload, api_key)

    code = result.get("code")
    if code != 2000:
        print(f"[error] 提交任务失败: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data") or {}
    task_id = data.get("taskId") or data.get("task_id") or ""
    if not task_id:
        # 某些接口可能直接在 data 中返回结果（非异步），将完整 data 作为结果返回
        return "__direct__"
    return task_id


def poll_comment_result(task_id: str, api_key: str) -> dict:
    """轮询评论结果（POST + form-urlencoded），直到数据就绪或超时。
    
    commentResult 接口要求 POST + application/x-www-form-urlencoded 格式。
    """
    for attempt in range(MAX_POLL_ATTEMPTS):
        form_data = urllib.parse.urlencode({
            "taskId": task_id,
            "source": "B站评论分析-GitHub",
        }).encode("utf-8")
        req = urllib.request.Request(
            RESULT_API,
            data=form_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-API-Key": api_key,
                "User-Agent": "QoderWork/1.0",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
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
            print(f"[error] 查询结果失败: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
            sys.exit(1)

        data = result.get("data") or {}

        # 检查任务状态
        status = data.get("status") or data.get("state") or ""
        if status in ("pending", "processing", "running"):
            print(f"[poll] 第 {attempt + 1} 次轮询，任务状态: {status}，等待 {POLL_INTERVAL}s...", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        # 任务完成或数据已就绪
        return result

    print(f"[error] 评论数据获取超时（已轮询 {MAX_POLL_ATTEMPTS} 次），请稍后重试", file=sys.stderr)
    sys.exit(1)


def format_comment(raw: dict) -> dict:
    """将 API 返回的原始评论格式化为统一结构

    commentResult 实际返回字段：
    commentId, content, likeNum, createTime, ipLocation,
    nickname, commenterUid, avatar, avId, isPinned, pictures
    
    输出字段：用户昵称、用户ID、评论内容、点赞数、评论时间、IP属地
    """
    user_name = (raw.get("nickname") or raw.get("authorName") or "").strip()
    user_id = str(raw.get("commenterUid") or raw.get("authorUid") or "")

    content = raw.get("content") or raw.get("message") or raw.get("text") or ""
    if isinstance(content, dict):
        content = content.get("message", "") or content.get("content", "")

    like_count = raw.get("likeNum") or raw.get("like") or raw.get("likeCount") or 0

    create_time = raw.get("createTime") or raw.get("ctime") or raw.get("publishTime") or ""
    if isinstance(create_time, (int, float)) and create_time > 1000000000:
        try:
            create_time = datetime.fromtimestamp(int(create_time)).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            create_time = str(create_time)

    ip_raw = raw.get("ipLocation") or ""
    ip_location = ip_raw.replace("IP属地：", "").replace("IP属地:", "").strip()

    return {
        "user_name": user_name,
        "user_id": user_id,
        "content": str(content).strip(),
        "like_count": int(like_count) if like_count else 0,
        "create_time": str(create_time),
        "ip_location": ip_location,
    }


def fetch_comments(bv_id: str, page: int, api_key: str, sort_type: str = "1") -> tuple:
    """
    两步获取评论：提交任务 → 轮询结果。
    返回 (comments_list, has_next, total_count)
    """
    offset = (page - 1) * PAGE_SIZE

    # Step 1: 提交任务
    task_id = submit_comment_task(bv_id, offset, api_key, sort_type=sort_type)

    # Step 2: 获取结果
    if task_id == "__direct__":
        payload = {
            "opusId": bv_id,
            "sortType": sort_type,
            "dataNum": str(PAGE_SIZE),
            "offset": str(offset),
            "source": "B站评论分析-GitHub",
        }
        result = api_request(SUBMIT_API, payload, api_key)
    else:
        result = poll_comment_result(task_id, api_key)

    data = result.get("data") or {}

    # 评论列表
    comment_list = data.get("commentList") or data.get("comments") or []
    if not isinstance(comment_list, list):
        comment_list = []

    all_comments = [format_comment(c) for c in comment_list]

    # 分页判断：基于 total/received 字段
    total_count = data.get("total", 0) or 0
    received = data.get("received", 0) or 0
    has_next = bool(data.get("hasMore") or data.get("has_next") or False)
    if not has_next:
        # 如果 offset + 本页数量 < 总评论数，说明还有下一页
        has_next = (offset + len(all_comments)) < total_count

    return all_comments, has_next, total_count


def escape_html(text: str) -> str:
    """HTML 实体转义"""
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_comment_rows(comments: list) -> str:
    """根据评论列表生成 HTML 表格行"""
    rows = []
    for c in comments:
        name = escape_html(c.get("user_name", ""))
        uid = escape_html(c.get("user_id", ""))
        content = escape_html(c.get("content", ""))
        like = c.get("like_count", 0) or 0
        time_str = (c.get("create_time", "") or "")[5:16]  # MM-DD HH:MM
        ip = escape_html(c.get("ip_location", ""))

        user_url = f"https://space.bilibili.com/{uid}" if uid and uid != "0" else "#"

        row = (
            f'<tr>'
            f'<td><a href="{user_url}" target="_blank" class="user-name">{name}</a></td>'
            f'<td class="uid-cell">{uid}</td>'
            f'<td class="content-cell">{content}</td>'
            f'<td class="num-cell">{like}</td>'
            f'<td class="time-cell">{time_str}</td>'
            f'<td class="ip-cell">{ip}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def generate_html_report(bv_id: str, current_page: int, comments: list, work_detail: dict = None, output_dir: str = None) -> str:
    """读取 HTML 模板，填充评论数据，生成报告文件。返回生成的 HTML 文件绝对路径。"""
    template_path = os.path.normpath(TEMPLATE_PATH)
    if not os.path.exists(template_path):
        print(f"[warn] 模板文件不存在: {template_path}，跳过 HTML 生成", file=sys.stderr)
        return ""

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    total = len(comments)
    now = datetime.now()
    total_likes = sum(c.get("like_count", 0) or 0 for c in comments)

    wd = work_detail or {}
    replacements = {
        "{{VIDEO_ID}}": escape_html(bv_id),
        "{{DATE}}": now.strftime("%Y-%m-%d"),
        "{{TOTAL_COMMENTS}}": str(total),
        "{{COMMENT_ROWS}}": build_comment_rows(comments),
        "{{TIMESTAMP}}": now.strftime("%Y-%m-%d %H:%M:%S"),
        "{{TOTAL_LIKES}}": str(total_likes),
        "{{PAGE}}": str(current_page),
        "{{TITLE}}": escape_html(wd.get("title") or ""),
        "{{AUTHOR_NAME}}": escape_html(wd.get("author_name") or ""),
        "{{AUTHOR_UID}}": escape_html(wd.get("author_uid") or ""),
        "{{AUTHOR_AVATAR}}": wd.get("author_avatar") or "",
        "{{COVER}}": wd.get("cover") or "",
        "{{PUBLISH_TIME}}": escape_html(wd.get("publish_time") or ""),
        "{{DURATION}}": escape_html(wd.get("duration") or ""),
        "{{VIEW_COUNT}}": str(wd.get("view_count") or 0),
        "{{LIKE_COUNT}}": str(wd.get("like_count") or 0),
        "{{COIN_COUNT}}": str(wd.get("coin_count") or 0),
        "{{FAVORITE_COUNT}}": str(wd.get("favorite_count") or 0),
        "{{SHARE_COUNT}}": str(wd.get("share_count") or 0),
        "{{REPLY_COUNT}}": str(wd.get("reply_count") or 0),
        "{{DANMAKU_COUNT}}": str(wd.get("danmaku_count") or 0),
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    # 确定输出目录
    if output_dir:
        out_dir = os.path.expanduser(output_dir)
    else:
        out_dir = os.path.expanduser("~/Downloads/QoderReports")
    os.makedirs(out_dir, exist_ok=True)

    filename = f"B站评论分析_{bv_id}_p{current_page}.html"
    file_path = os.path.join(out_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[html] HTML 报告已生成: {file_path}", file=sys.stderr)
    return file_path


def main():
    parser = argparse.ArgumentParser(description="B站视频评论查询")
    parser.add_argument("bv_id", help="B站视频 BV号、AV号或完整链接")
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从1开始（默认1，每页20条）",
    )
    parser.add_argument(
        "--sort", dest="sort_type", default="1", choices=["1", "2", "3"],
        help="排序方式：1-按时间 2-按热度 3-按回复数（默认1）",
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

    bv_id = extract_bv_id(args.bv_id)
    if not bv_id:
        print("[error] 视频ID不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()

    # 获取作品详情（同步接口，与评论获取并行逻辑但顺序执行）
    work_detail = fetch_work_detail(bv_id, api_key)

    comments, has_next, total_count = fetch_comments(bv_id, args.page, api_key, sort_type=args.sort_type)

    total = len(comments)

    output = {
        "work_detail": work_detail,
        "total_count": total_count,
        "total_fetched": total,
        "has_next": has_next,
        "comments": comments,
    }

    # HTML 报告生成
    if not args.no_html:
        html_path = generate_html_report(
            bv_id=bv_id,
            current_page=args.page,
            comments=comments,
            work_detail=work_detail,
            output_dir=args.output_dir,
        )
        output["html_path"] = html_path

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
