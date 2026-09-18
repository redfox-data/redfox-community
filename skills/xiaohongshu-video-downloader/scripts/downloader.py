#!/usr/bin/env python3
"""
小红书视频下载 - API 版本
使用 redfox.hk API 解析小红书视频链接，直接返回无水印视频下载链接
支持单链接和批量链接解析，自动校验小红书视频链接

Usage:
    python3 downloader.py <url> [<url> ...] [--api-key <key>]
"""

import argparse
import json
import os
import sys
import warnings
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

# Suppress urllib3 OpenSSL warning on macOS
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

# Ensure UTF-8 output (especially on Windows where default encoding may be GBK)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

API_URL = "https://redfox.hk/story/api/parseWork/videoDownload/xhs"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"

ENV_KEY = "REDFOX_API_KEY"

# 官方示例链接：所有对外提示与文档统一使用此链接，必须携带 xsec_token 参数
EXAMPLE_URL = (
    "https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071"
    "?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M="
    "&xsec_source=pc_feed"
)

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def info(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def error(msg):
    print(f"{RED}[✗]{RESET} {msg}")


def step(msg):
    print(f"{CYAN}[→]{RESET} {msg}")


def get_api_key(cli_key=None):
    """Get API key with priority: CLI arg > env var > config file."""
    if cli_key:
        return cli_key

    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key

    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            key = data.get("api_key")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass

    return None


def save_api_key(api_key):
    """Persist API key to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"api_key": api_key}, indent=2))
    os.chmod(CONFIG_FILE, 0o600)  # secure file permissions
    info(f"API Key saved to {CONFIG_FILE}")


def is_xhs_video_url(url):
    """Check if the URL is a valid Xiaohongshu (RED) video link.

    Accepts:
      - www.xiaohongshu.com  (PC web links / mobile share links)
      - xhslink.com           (mobile short links)
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain in ("xiaohongshu.com", "xhslink.com")


def has_xsec_token(url):
    """Check if the URL contains a non-empty xsec_token query parameter.

    小红书接口要求链接必须携带 xsec_token，缺失时接口会返回链接格式错误。
    """
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
    except Exception:
        return False
    token = qs.get("xsec_token", [""])[0]
    return bool(token and token.strip())


def print_xsec_token_hint():
    """统一输出 xsec_token 缺失/链接格式错误的用户提示。"""
    print(f"  请传入带 xsec_token 参数的完整小红书链接，示例：")
    print(f"  {EXAMPLE_URL}")
    print(f"  获取方式：在小红书 PC 网页或 App 中打开笔记 → 复制分享链接（链接需包含 xsec_token 参数）")


def extract_download_url(data):
    """Extract video download URL from API response data (tolerant of field naming)."""
    if isinstance(data, str):
        return data
    if not isinstance(data, dict):
        return None

    # Common field names that may carry the downloadable video link
    candidate_keys = [
        "videoUrl", "video_url", "downloadUrl", "download_url",
        "videoDownloadUrl", "video_download_url", "playUrl", "play_url",
        "url", "link",
    ]
    for key in candidate_keys:
        value = data.get(key)
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value

    # Nested structures: data.video.url / data.media[0].url etc.
    for nested_key in ("video", "media", "result", "detail"):
        nested = data.get(nested_key)
        found = extract_download_url(nested) if isinstance(nested, (dict, list)) else None
        if found:
            return found

    if isinstance(data.get("videos"), list):
        for item in data["videos"]:
            found = extract_download_url(item)
            if found:
                return found

    return None


def process_single_url(url, session, output_json):
    """Process a single XHS video URL.

    Returns:
        "success" — parsed successfully
        "error"   — non-fatal error, can continue with next URL
        "fatal"   — invalid URL or API Key issue, stop all processing
    """
    # ── Validate URL first ──
    if not is_xhs_video_url(url):
        error(f"该链接不是小红书视频链接：{url}")
        print(f"  支持域名：www.xiaohongshu.com 网页链接 或 xhslink.com 短链")
        print_xsec_token_hint()
        return "fatal"

    # ── 小红书接口必须携带 xsec_token，缺失时提前拦截，避免无效请求 ──
    if not has_xsec_token(url):
        error(f"链接缺少 xsec_token 参数，无法解析：{url}")
        print_xsec_token_hint()
        return "fatal"

    step(f"URL: {url}")
    step("Calling redfox.hk API...")

    try:
        resp = session.post(API_URL, json={"url": url, "source": "xhs/小红书视频下载-GitHub"}, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        error(f"API request failed: {e}")
        return "error"
    except json.JSONDecodeError:
        error(f"API returned invalid JSON: {resp.text[:200]}")
        return "error"

    code = result.get("code")
    msg = result.get("msg", "")

    # 成功 code 以 2 开头（如 200、2000），其余为错误
    if not str(code).startswith("2"):
        if code == 3106:
            error("缺少 API Key")
            return "fatal"
        elif code == 3107:
            error("API Key 无效或已失效，请检查是否正确")
            print("  配置方式：export REDFOX_API_KEY=ark_你的密钥")
            return "fatal"
        elif code == 400:
            error(f"请求参数错误: {msg}")
            # 400 通常是链接格式错误，主动提示用户传入带 xsec_token 的完整链接
            print_xsec_token_hint()
        else:
            error(f"API error (code {code}): {msg}")
            # 其他错误如果提示中包含“链接格式”“xsec_token”等关键字，同样提示用户重新传入
            msg_lower = str(msg).lower()
            if any(kw in str(msg) for kw in ("链接格式", "链接错误", "链接无效", "xsec_token")) or \
               any(kw in msg_lower for kw in ("link format", "invalid link", "invalid url", "xsec_token")):
                print_xsec_token_hint()
        return "error"

    data = result.get("data")
    if not data:
        error("API returned empty data")
        return "error"

    # ── Parse result ──
    if output_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    desc = data.get("desc") if isinstance(data, dict) else None
    cover = data.get("cover") if isinstance(data, dict) else None
    resources = data.get("resources") if isinstance(data, dict) else None

    print(f"\n{GREEN}{BOLD}✓ 解析成功！{RESET}")

    # 内容描述（完整原文，不截断）
    if desc:
        print(f"\n{CYAN}{BOLD}📝 内容描述：{RESET}")
        for line in str(desc).splitlines():
            print(f"  {line}")

    # 资源列表：类型 / 时长 / 下载链接 / 封面链接
    if isinstance(resources, list) and resources:
        print(f"\n{CYAN}{BOLD}🎬 资源列表（共 {len(resources)} 个）：{RESET}")
        for i, res in enumerate(resources, 1):
            if not isinstance(res, dict):
                continue
            rtype = res.get("type") or "未知"
            dl = res.get("downloadUrl") or "-"
            cu = res.get("coverUrl") or cover or "-"
            dur = res.get("durationSeconds")
            dur_str = f"{dur} 秒" if isinstance(dur, (int, float)) and dur else "未知"
            print(f"\n  {BOLD}【资源 {i}】{RESET}")
            print(f"    资源类型：{rtype}")
            print(f"    时长：{dur_str}")
            print(f"    下载链接：{dl}")
            print(f"    封面链接：{cu}")
    else:
        # 回退：无 resources 字段时从顶层提取
        download_url = extract_download_url(data)
        if not download_url:
            error("未能从 API 返回结果中提取下载链接，原始返回如下：")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return "error"
        print(f"\n{CYAN}{BOLD}🎬 资源：{RESET}")
        print(f"    下载链接：{download_url}")
        if cover:
            print(f"    封面链接：{cover}")

    print(f"{YELLOW}⚠️ 视频号下载链接有效期约 5 分钟，请立即复制到浏览器打开或下载！{RESET}")
    return "success"


def main():
    parser = argparse.ArgumentParser(
        description="小红书视频下载 - 使用 redfox.hk API 解析视频并返回下载链接（支持批量）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python3 downloader.py "{EXAMPLE_URL}"
  python3 downloader.py "{EXAMPLE_URL}" --api-key ark_xxxxx
  python3 downloader.py "<链接1>" "<链接2>"   # 批量解析，每个链接均需携带 xsec_token

❗ 链接必须携带 xsec_token 参数，否则接口会返回链接格式错误。

也可通过环境变量 REDFOX_API_KEY 配置密钥：
  export REDFOX_API_KEY=ark_xxxxx
  python3 downloader.py <url> [<url> ...]
        """,
    )
    parser.add_argument(
        "urls",
        nargs="+",
        help=f"小红书视频链接（支持多个，空格分隔），必须携带 xsec_token 参数，如：{EXAMPLE_URL}",
    )
    parser.add_argument("--api-key", help="API Key（格式 ark_xxx，不传则读取环境变量或配置文件）")
    parser.add_argument(
        "--save-key",
        action="store_true",
        help="将本次传入的 API Key 保存到配置文件",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出完整返回结果",
    )

    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════╗
  ║   Xiaohongshu Video Downloader       ║
  ║   小红书视频下载                     ║
  ╚══════════════════════════════════════╝{RESET}
"""
    print(banner)

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        error("未找到 API Key，请设置环境变量 REDFOX_API_KEY 或使用 --api-key 参数")
        print(f"  获取 Key: https://redfox.hk/settings/api-keys?source=github")
        sys.exit(1)

    # Save key if requested
    if args.save_key:
        save_api_key(api_key)

    # ── Normalize URLs ──
    urls = []
    for raw_url in args.urls:
        url = raw_url.strip().strip('"').strip("'")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        urls.append(url)

    total = len(urls)

    # ── Session ──
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    })

    # ── Process URLs ──
    success_count = 0

    for i, url in enumerate(urls, 1):
        if total > 1:
            print(f"\n{CYAN}{BOLD}{'═' * 40}{RESET}")
            print(f"{CYAN}{BOLD}  处理第 {i}/{total} 个链接{RESET}")
            print(f"{CYAN}{BOLD}{'═' * 40}{RESET}")

        status = process_single_url(url, session, args.json)

        if status == "fatal":
            # Invalid URL or API Key issue — stop all processing
            sys.exit(1)
        elif status == "success":
            success_count += 1

    # ── Summary (batch mode) ──
    if total > 1:
        print(f"\n{CYAN}{BOLD}{'═' * 40}{RESET}")
        fail_count = total - success_count
        if fail_count == 0:
            print(f"{GREEN}{BOLD}✓ 批量解析完成：共 {total} 个链接，全部成功{RESET}")
        else:
            print(f"{GREEN}{BOLD}✓ 批量解析完成：共 {total} 个链接，成功 {success_count} 个，失败 {fail_count} 个{RESET}")

    # ── Enterprise procurement guidance ──
    print(f"\n💼 另外红狐配套全量数据库可提供完整详实数据，如需了解采购方案，可前往红狐hub 企业服务(https://redfox.hk/dashboard/enterprise) 对接咨询")

    sys.exit(0 if success_count > 0 else 1)


if __name__ == "__main__":
    main()
