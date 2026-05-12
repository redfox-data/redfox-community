#!/usr/bin/env python3
"""
小红书热门数据查询脚本（最终版 - 禁用 SNI + 支持 chunked + gzip）
"""

import sys
import argparse
import json
import socket
import ssl
import gzip


def decode_chunked(data):
    """解码 chunked 传输编码"""
    chunks = []
    idx = 0

    while idx < len(data):
        # 读取 chunk 大小
        line_end = data.find(b'\r\n', idx)
        if line_end == -1:
            break

        chunk_size_line = data[idx:line_end]
        try:
            chunk_size = int(chunk_size_line, 16)
        except:
            break

        if chunk_size == 0:
            break

        # 读取 chunk 数据
        chunk_start = line_end + 2
        chunk_end = chunk_start + chunk_size

        if chunk_end > len(data):
            break

        chunk = data[chunk_start:chunk_end]
        chunks.append(chunk)

        # 移动到下一个 chunk
        idx = chunk_end + 2  # 跳过 \r\n

    return b''.join(chunks)


def fetch_via_no_sni(base_url: str, params: dict, headers: dict, timeout: int = 60):
    """
    使用原生 socket 实现 HTTPS 请求（不发送 SNI）

    关键：服务器在 SNI 扩展中检测到域名后主动断开连接
    解决：不发送 SNI 扩展
    """
    # 解析 URL
    if "://" in base_url:
        base_url = base_url.split("://", 1)[1]
    host, path = base_url.split("/", 1)

    # 构建 query string
    if params:
        from urllib.parse import quote
        query = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items())
        path = f"{path}?{query}"

    # 创建 TCP 连接
    sock = socket.create_connection((host, 443), timeout=timeout)

    # 创建 SSL 上下文（不使用 SNI）
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # 包装 socket（不传递 server_hostname，避免发送 SNI）
    ssl_sock = context.wrap_socket(sock)

    # 构建 HTTP 请求
    request_lines = [
        f"GET /{path} HTTP/1.1",
        f"Host: {host}",
    ]
    for k, v in headers.items():
        request_lines.append(f"{k}: {v}")
    request_lines.append("")
    request_lines.append("")

    request = "\r\n".join(request_lines)

    # 发送请求
    ssl_sock.send(request.encode())

    # 接收响应
    response_data = b""
    while True:
        try:
            chunk = ssl_sock.recv(8192)
            if not chunk:
                break
            response_data += chunk
        except:
            break

    ssl_sock.close()

    # 解析响应头
    response_str = response_data.decode('utf-8', errors='ignore')
    lines = response_str.split('\r\n')

    # 提取状态码
    status_code = int(lines[0].split()[1])

    # 提取响应头
    headers_dict = {}
    for i, line in enumerate(lines[1:]):
        if line == '':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers_dict[key.strip().lower()] = value.strip()

    # 分离头部和正文
    header_end = response_data.find(b'\r\n\r\n')
    if header_end != -1:
        body_bytes = response_data[header_end + 4:]
    else:
        body_bytes = b""

    # 处理 chunked 编码
    if headers_dict.get('transfer-encoding', '').lower() == 'chunked':
        body_bytes = decode_chunked(body_bytes)

    # 处理 gzip 压缩
    if headers_dict.get('content-encoding', '').lower() == 'gzip':
        try:
            body_bytes = gzip.decompress(body_bytes)
        except:
            pass

    response_body = body_bytes.decode('utf-8', errors='ignore')

    return status_code, response_body


def fetch_xhs_trends(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """
    调用新接口获取小红书热门数据

    Args:
        keyword: 搜索关键词（多个关键词用逗号分隔，最多5个，总长度不超过200）
        debug: 是否打印调试信息
        max_retries: 最大重试次数
        start_date: 开始日期，格式 yyyy-MM-dd，最长为最近30天

    Returns:
        dict: 包含4类爆款数据

    Raises:
        Exception: 当API调用失败时抛出异常
    """
    base_url = "https://onetotenvip.com/skill/cozeSkill/getXhsCozeSkillData"
    params = {
        "keyword": keyword,
        "source": "小红书笔记创作-GitHub"
    }

    # 添加开始日期参数
    if start_date:
        params["startDate"] = start_date
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)

            status_code, body = fetch_via_no_sni(base_url, params, headers)

            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(body)} 字节", file=sys.stderr)

            if status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {status_code}")

            data = json.loads(body)

            if "data" not in data:
                error_msg = data.get("msg", "未知错误")
                raise Exception(f"API 错误: {error_msg}")

            result_data = data.get("data", {})

            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)

            return {
                "keyword": keyword,
                "low_fan_explosive": result_data.get("lowPowderExplosiveArticle", []),
                "daily_like_top500": result_data.get("likeTheTop500", []),
                "daily_increment": result_data.get("singleDayIncrements", []),
                "weekly_increment": result_data.get("sevenDaysOfIncrements", [])
            }

        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def format_output(data: dict, max_items: int = None):
    """
    格式化输出热门数据（表格形式）

    Args:
        data: 原始数据
        max_items: 每类爆款数据最多展示数量，None 表示展示所有数据
    """

    def process_title(item):
        """处理标题：转义特殊字符，空标题使用desc替代，并添加作品链接"""
        title = item.get('title', '')
        # 如果标题为空，尝试使用 desc 字段
        if not title or title.strip() == '':
            desc = item.get('desc', '')
            if desc:
                # 移除 desc 中的换行符并截取前30个字符
                title = desc.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(desc) > 30:
                    title = title + '...'

        if not title or title.strip() == '':
            title = '无标题'

        # 转义 Markdown 表格特殊字符（|）
        title = title.replace('|', '\\|')
        # 移除换行符
        title = title.replace('\n', ' ').replace('\r', ' ')
        # 移除多余空格
        title = ' '.join(title.split())

        # 截断过长标题
        if len(title) > 30:
            title = title[:30] + "..."

        # 添加作品链接
        photo_id = item.get('photoId', '')
        if photo_id:
            work_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
            title = f"[{title}]({work_link})"

        return title

    output = []

    # 按 photoId 去重（API 返回数据可能有重复）
    def dedup_items(items):
        seen = set()
        result = []
        for item in items:
            photo_id = item.get('photoId', '')
            if photo_id and photo_id not in seen:
                seen.add(photo_id)
                result.append(item)
        return result

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    daily_like_items = dedup_items(data.get("daily_like_top500", []))
    daily_increment_items = dedup_items(data.get("daily_increment", []))
    weekly_increment_items = dedup_items(data.get("weekly_increment", []))

    total_count = len(low_fan_items) + len(daily_like_items) + len(daily_increment_items) + len(weekly_increment_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"# 小红书爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{total_count} 条\n\n")
        output.append("---\n\n")
        output.append("## 暂无相关爆款数据\n\n")
        output.append(f"很抱歉，当前关键词 **「{keyword}」** 尚未有足够的爆款笔记数据。\n\n")
        output.append("### 可能原因\n\n")
        output.append("- 该关键词相对小众或新兴，爆款内容积累较少\n")
        output.append("- 近期该赛道热度较低，暂无突出爆款笔记\n")
        output.append("- 关键词表述方式可以更加具体或热门\n\n")
        output.append("### 建议操作\n\n")
        output.append("- 更换为更热门的关键词，如：**\"早八穿搭\"**、**\"减脂餐\"**、**\"职场干货\"** 等\n")
        output.append("- 尝试更细分的长尾关键词，如：**\"小个子穿搭\"**、**\"学生党便当\"** 等\n")
        output.append("- 输入其他感兴趣的领域或赛道进行追踪\n\n")
        output.append("---\n\n")
        output.append("*数据来源：小红书爆款雷达，每日更新最新热门内容*\n")
        return "\n".join(output)

    # 1. 新手友好爆款
    items = low_fan_items
    if max_items is not None:
        items = items[:max_items]

    # 计算实际展示的总数
    display_low_fan = items
    display_daily_like = daily_like_items[:max_items] if max_items is not None else daily_like_items
    display_daily_increment = daily_increment_items[:max_items] if max_items is not None else daily_increment_items
    display_weekly_increment = weekly_increment_items[:max_items] if max_items is not None else weekly_increment_items
    display_total = len(display_low_fan) + len(display_daily_like) + len(display_daily_increment) + len(display_weekly_increment)

    # 输出标题和总数量
    keyword = data.get("keyword", "")
    output.append(f"# 小红书爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{display_total} 条\n\n---\n")

    output.append(f"\n## 爆款笔记（共 {len(items)} 条）")
    output.append(f"### - **新手友好爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **互动总数** | 收藏 | 分享 | 评论 | 点赞 |")
        output.append("|------|------|------|------------|------|------|------|------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('interactiveCount', 0)}** | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} | {item.get('useLikeCount', 0)} |")

    # 2. 当日点赞爆款
    items = data.get("daily_like_top500", [])
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **当日点赞爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **点赞** | 收藏 | 分享 | 评论 |")
        output.append("|------|------|------|-------|------|------|------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('useLikeCount', 0)}** | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} |")

    # 3. 当日增长爆款
    items = data.get("daily_increment", [])
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **当日增长爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | **新增互动总量** |")
        output.append("|------|------|------|------|------|------|------|---------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            # 从 anaAdd 对象获取新增互动数据
            ana_add = item.get('anaAdd', {})
            if ana_add:
                total = ana_add.get('addInteractiveount', 0)
                collected = ana_add.get('addCollectedCunt', 0)
                share = ana_add.get('addShareCount', 0)
                comment = ana_add.get('addCommentCount', 0)
                like = ana_add.get('addLikeCount', 0)
            else:
                total = 0
                collected = 0
                share = 0
                comment = 0
                like = 0

            output.append(f"| {idx} | {title} | {author_str} | {collected} | {share} | {comment} | {like} | **{total}** |")

    # 4. 持续增长爆款
    items = data.get("weekly_increment", [])
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **持续增长爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | **新增互动总量** |")
        output.append("|------|------|------|------|------|------|------|---------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            # 从 anaAdd 对象获取新增互动数据
            ana_add = item.get('anaAdd', {})
            if ana_add:
                total = ana_add.get('addInteractiveount', 0)
                collected = ana_add.get('addCollectedCunt', 0)
                share = ana_add.get('addShareCount', 0)
                comment = ana_add.get('addCommentCount', 0)
                like = ana_add.get('addLikeCount', 0)
            else:
                total = 0
                collected = 0
                share = 0
                comment = 0
                like = 0

            output.append(f"| {idx} | {title} | {author_str} | {collected} | {share} | {comment} | {like} | **{total}** |")

    return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小红书热门数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10,
                       help='每类爆款内容最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'markdown'],
                       default='markdown', help='输出格式：text（文本表格）、json（JSON格式）或 markdown（Markdown格式，默认）')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd（默认最近30天）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数（默认3次）')

    args = parser.parse_args()

    try:
        data = fetch_xhs_trends(args.keyword, debug=args.debug, max_retries=args.max_retries, start_date=args.start_date)

        # 生成输出内容
        if args.output_format == 'json':
            output_content = json.dumps(data, ensure_ascii=False, indent=2)
        else:
            output_content = format_output(data, max_items=args.max_items)

        # 直接输出到控制台
        print(output_content)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
