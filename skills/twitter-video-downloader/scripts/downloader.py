#!/usr/bin/env python3
"""
X(Twitter)视频下载 - API 版本
使用 redfox.hk API 解析 X(Twitter) 视频链接，直接返回无水印视频下载链接

Usage:
    python3 downloader.py <url> [--api-key <key>]
"""

import argparse
import json
import os
import sys
import warnings
from pathlib import Path

import requests

# Suppress urllib3 OpenSSL warning on macOS
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

API_URL = "https://redfox.hk/story/api/parseWork/videoDownload/x"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"

ENV_KEY = "REDFOX_API_KEY"

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


def main():
    parser = argparse.ArgumentParser(
        description="X(Twitter)视频下载 - 使用 redfox.hk API 解析视频并返回下载链接",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 downloader.py https://x.com/user/status/xxxxx
  python3 downloader.py https://x.com/user/status/xxxxx --api-key ark_xxxxx

也可通过环境变量 REDFOX_API_KEY 配置密钥：
  export REDFOX_API_KEY=ark_xxxxx
  python3 downloader.py <url>
        """,
    )
    parser.add_argument("url", help="X(Twitter) 视频链接，如 https://x.com/user/status/xxxxx")
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
  ║   X(Twitter) Video Downloader        ║
  ║   X(Twitter)视频下载                 ║
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

    # ── URL ──
    url = args.url.strip().strip('"').strip("'")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    step(f"URL: {url}")

    # ── Call API ──
    step("Calling redfox.hk API...")

    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    })

    try:
        resp = session.post(API_URL, json={"url": url, "source": "twitter/X视频下载-GitHub"}, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        error(f"API request failed: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        error(f"API returned invalid JSON: {resp.text[:200]}")
        sys.exit(1)

    code = result.get("code")
    msg = result.get("msg", "")

    # 成功 code 以 2 开头（如 200、2000），其余为错误
    if not str(code).startswith("2"):
        if code == 3106:
            error("缺少 API Key")
        elif code == 3107:
            error("API Key 无效或已失效，请检查是否正确")
            print("  配置方式：export REDFOX_API_KEY=ark_你的密钥")
        elif code == 400:
            error(f"请求参数错误: {msg}")
        else:
            error(f"API error (code {code}): {msg}")
        sys.exit(1)

    data = result.get("data")
    if not data:
        error("API returned empty data")
        sys.exit(1)

    # ── Parse result ──
    if args.json:
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
            sys.exit(1)
        print(f"\n{CYAN}{BOLD}🎬 资源：{RESET}")
        print(f"    下载链接：{download_url}")
        if cover:
            print(f"    封面链接：{cover}")

    print(f"\n{CYAN}复制链接到浏览器或下载工具即可下载。{RESET}")
    sys.exit(0)


if __name__ == "__main__":
    main()
