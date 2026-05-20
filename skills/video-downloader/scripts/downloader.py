#!/usr/bin/env python3
"""
Qoder Video Downloader - API 版本
使用 redfox.hk API 解析并下载无水印视频/图文
支持：抖音、小红书、快手、B站

Usage:
    python3 downloader.py <url> [--api-key <key>] [--output-dir <path>]
"""

import argparse
import json
import os
import re
import sys
import warnings
from pathlib import Path

import requests

# Suppress urllib3 OpenSSL warning on macOS
warnings.filterwarnings("ignore", category=Warning)
warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

API_URL = "https://redfox.hk/story/api/parseWork/parse"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"

ENV_KEY = "X_API_KEY"

# 内置公共 API Key（免费 10000 次，超出后需自行注册）
PUBLIC_API_KEY = "ak_783ee098b4934f539e0259d98d2a0f90"
PUBLIC_API_KEY_LIMIT = 10000

PLATFORM_MAP = {
    "dy": "抖音",
    "xhs": "小红书",
    "xhsw": "小红书",
    "ks": "快手",
    "bili": "B站",
}

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
    """Get API key with priority: CLI arg > env var > config file > public key."""
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

    return PUBLIC_API_KEY


def save_api_key(api_key):
    """Persist API key to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"api_key": api_key}, indent=2))
    os.chmod(CONFIG_FILE, 0o600)  # secure file permissions
    info(f"API Key saved to {CONFIG_FILE}")


def sanitize_filename(name):
    """Remove or replace characters unsafe for filenames."""
    if not name:
        return None
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().replace(" ", "_")
    name = name[:120]  # limit length
    return name or None


def download_file(session, url, filepath, desc="Downloading"):
    """Download a file with progress display."""
    try:
        resp = session.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        total = int(resp.headers.get("content-length", 0))
        downloaded = 0

        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = int(downloaded * 100 / total)
                        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                        print(f"\r  {bar} {pct}%", end="", flush=True)
        print()
        return True

    except requests.exceptions.RequestException as e:
        error(f"Download failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="短视频下载器 - 使用 redfox.hk API 下载无水印视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 downloader.py https://v.douyin.com/xxxxxx/
  python3 downloader.py https://b23.tv/xxxxxx --api-key ark_xxxxx
  python3 downloader.py https://xhslink.com/o/xxxxxx -o ~/Videos

也可通过环境变量 X_API_KEY 配置密钥：
  export X_API_KEY=ark_xxxxx
  python3 downloader.py <url>
        """,
    )
    parser.add_argument("url", help="视频/图文链接")
    parser.add_argument("--api-key", help="API Key（格式 ark_xxx，不传则读取环境变量或内置公共 Key）")
    parser.add_argument("-o", "--output-dir", help="输出目录（默认 ~/Downloads/QoderVideos）")
    parser.add_argument(
        "--save-key",
        action="store_true",
        help="将本次传入的 API Key 保存到配置文件",
    )

    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════╗
  ║     Qoder Video Downloader (API)     ║
  ║     视频下载去水印工具          ║
  ╚══════════════════════════════════════╝{RESET}
"""
    print(banner)

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)

    # 提示公共 Key 的免费额度限制
    if api_key == PUBLIC_API_KEY and not args.api_key and not os.environ.get(ENV_KEY) and not CONFIG_FILE.exists():
        print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║  使用内置公共 API Key（剩余约 10000 次）     ║{RESET}")
        print(f"{YELLOW}║  超出后请前往 www.redfox.hk 获取 Key：       ║{RESET}")
        print(f"{YELLOW}║  export X_API_KEY=ark_你的密钥                ║{RESET}")
        print(f"{YELLOW}║  或：--api-key ark_你的密钥                  ║{RESET}")
        print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}")
        print()

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
        resp = session.post(API_URL, json={"url": url, "source": "短视频下载器-GitHub"}, timeout=30)
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
            if api_key == PUBLIC_API_KEY:
                error("公共 API Key 已失效（可能超出 10000 次免费限额）")
                warn("请前往 www.redfox.hk 获取自己的 API Key")
                print("  配置方式：export X_API_KEY=ark_你的密钥")
            else:
                error("API Key 无效，请检查是否正确")
                print("  格式应为 ark_xxx，可通过 export X_API_KEY=ark_你的密钥 设置")
        elif code == 400:
            error(f"请求参数错误: {msg}")
        else:
            error(f"API error (code {code}): {msg}")
        sys.exit(1)

    data = result.get("data")
    if not data:
        error("API returned empty data")
        sys.exit(1)

    aweme_type = data.get("awemeType")
    platform = data.get("platform", "unknown")
    title = data.get("title", "untitled")

    print()
    info(f"Platform: {PLATFORM_MAP.get(platform, platform)}")
    info(f"Title: {title[:80]}")

    # ── Output directory ──
    output_dir = args.output_dir or str(Path.home() / "Downloads" / "QoderVideos")
    os.makedirs(output_dir, exist_ok=True)

    # ── Download ──
    downloaded_files = []

    if aweme_type == "video":
        video_url = data.get("videoUrl")
        if not video_url:
            error("API did not return video URL")
            sys.exit(1)

        safe_title = sanitize_filename(title) or f"video_{platform}"
        filename = f"{safe_title}.mp4"
        filepath = os.path.join(output_dir, filename)

        info(f"Type: Video")
        step("Downloading video...")

        if download_file(session, video_url, filepath):
            downloaded_files.append(filepath)

    elif aweme_type == "photo":
        image_urls = data.get("imageUrls") or []
        if not image_urls:
            error("API did not return image URLs")
            sys.exit(1)

        safe_title = sanitize_filename(title) or f"photo_{platform}"
        total = len(image_urls)
        info(f"Type: Photo (共 {total} 张)")

        for i, img_url in enumerate(image_urls, 1):
            ext = os.path.splitext(img_url.split("?")[0])[1] or ".jpg"
            filename = f"{safe_title}_{i}{ext}"
            filepath = os.path.join(output_dir, filename)

            step(f"Downloading image {i}/{total}...")
            if download_file(session, img_url, filepath):
                downloaded_files.append(filepath)

    else:
        error(f"Unknown awemeType: {aweme_type}")
        sys.exit(1)

    # ── Result ──
    if downloaded_files:
        print(f"\n{GREEN}{BOLD}✓ Download complete!{RESET}")
        for f in downloaded_files:
            size_mb = os.path.getsize(f) / (1024 * 1024)
            print(f"  {f} ({size_mb:.1f} MB)")
        sys.exit(0)
    else:
        print(f"\n{RED}{BOLD}✗ Download failed{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
