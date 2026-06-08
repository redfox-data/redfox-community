#!/usr/bin/env python3
"""
Qoder Seedream 5.0 Lite Image Generator
基于火山方舟 seedream 5.0 lite 模型的图片生成工具

Usage:
    python3 seedream.py "提示词" [options]
    python3 seedream.py "修改提示词" --image ~/path/to/ref.png
    python3 seedream.py "ignored" --task-id ark_xxx
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

SUBMIT_URL = "https://redfox.hk/story/api/parseWork/imageGen/arkSubmit"
RESULT_URL = "https://redfox.hk/story/api/parseWork/imageGen/arkResult"
UPLOAD_URL = "https://redfox.hk/story/api/parseWork/imageGen/uploadImage"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
PUBLIC_API_KEY = "ak_783ee098b4934f539e0259d98d2a0f90"
SOURCE = "seedream 5.0 lite-GitHub"
DEFAULT_MODEL = "doubao-seedream-5-0-260128"

POLL_INTERVAL = 3  # seconds
MAX_POLL_ATTEMPTS = 120  # max ~6 minutes

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
    """Get API key: CLI arg > env var > config file > public key."""
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


def upload_image(api_key, image_path):
    """Upload a local image file to OSS, return the image URL."""
    image_path = os.path.expanduser(image_path)
    if not os.path.isfile(image_path):
        error(f"Image file not found: {image_path}")
        return None

    ext = os.path.splitext(image_path)[1].lower()
    fmt_map = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
    fmt = fmt_map.get(ext, "png")

    step(f"Uploading image: {image_path}")

    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f)}
            data = {"format": fmt}
            headers = {"X-API-KEY": api_key}
            resp = requests.post(UPLOAD_URL, files=files, data=data, headers=headers, timeout=60, verify=True)
            result = resp.json()
    except requests.exceptions.RequestException as e:
        error(f"Upload request failed: {e}")
        return None
    except json.JSONDecodeError:
        error(f"Upload returned invalid JSON: {resp.text[:200]}")
        return None

    code = result.get("code")
    if not str(code).startswith("2"):
        error(f"Upload failed (code {code}): {result.get('msg', '')}")
        return None

    data = result.get("data", {})
    image_url = data.get("imageUrl")
    if not image_url:
        error("Upload succeeded but no imageUrl returned")
        return None

    info(f"Upload complete")
    return image_url


def submit_task(session, prompt, params):
    """Submit image generation task, return taskId."""
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "source": SOURCE,
    }

    # Add optional params
    if params.get("size"):
        payload["size"] = params["size"]
    if params.get("image"):
        payload["image"] = params["image"]
    if params.get("outputFormat"):
        payload["outputFormat"] = params["outputFormat"]
    if params.get("responseFormat"):
        payload["responseFormat"] = params["responseFormat"]
    if params.get("watermark") is not None:
        payload["watermark"] = params["watermark"]
    if params.get("sequentialImageGeneration"):
        payload["sequentialImageGeneration"] = params["sequentialImageGeneration"]
        if params.get("sequentialImageGenerationOptions"):
            payload["sequentialImageGenerationOptions"] = params["sequentialImageGenerationOptions"]
    if params.get("optimizePromptOptions"):
        payload["optimizePromptOptions"] = params["optimizePromptOptions"]

    try:
        resp = session.post(SUBMIT_URL, json=payload, timeout=30)
        result = resp.json()
    except requests.exceptions.RequestException as e:
        error(f"API request failed: {e}")
        return None
    except json.JSONDecodeError:
        error(f"API returned invalid JSON: {resp.text[:200]}")
        return None

    code = result.get("code")
    msg = result.get("msg", "")

    if not str(code).startswith("2"):
        error(f"Submit failed (code {code}): {msg}")
        return None

    data = result.get("data")
    if not data or not data.get("taskId"):
        error("API did not return taskId")
        return None

    return data["taskId"]


def poll_result(session, task_id):
    """Poll for task result until succeeded/failed/timeout."""
    consecutive_errors = 0

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        try:
            resp = session.post(RESULT_URL, json={"taskId": task_id}, timeout=15)
            result = resp.json()
        except requests.exceptions.RequestException as e:
            consecutive_errors += 1
            warn(f"Poll request failed (attempt {attempt}): {e}")
            if consecutive_errors >= 5:
                error("Too many consecutive network errors, giving up")
                return None
            time.sleep(POLL_INTERVAL)
            continue
        except json.JSONDecodeError:
            consecutive_errors += 1
            warn(f"Invalid JSON response (attempt {attempt})")
            if consecutive_errors >= 5:
                error("Too many consecutive decode errors, giving up")
                return None
            time.sleep(POLL_INTERVAL)
            continue

        consecutive_errors = 0

        code = result.get("code")
        if not str(code).startswith("2"):
            error(f"Query failed (code {code}): {result.get('msg', '')}")
            return None

        data = result.get("data", {})
        status = data.get("status")

        if status == "succeeded":
            return data
        elif status == "failed":
            reason = data.get("failReason", "unknown")
            error(f"Generation failed: {reason}")
            return None
        else:
            elapsed = attempt * POLL_INTERVAL
            status_cn = {"queued": "排队中", "running": "生成中"}.get(status, status)
            print(f"\r  {CYAN}⏳ Generating... ({elapsed}s) [{status_cn}]{RESET}", end="", flush=True)
            time.sleep(POLL_INTERVAL)

    print()
    error(f"Timeout: task did not complete within {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")
    print(f"  You can query later with: --task-id {task_id}")
    return None


def download_images(session, image_urls, output_dir, prefix="image"):
    """Download generated images to output directory."""
    downloaded = []
    total = len(image_urls)

    for i, url in enumerate(image_urls, 1):
        ext = ".jpeg"
        url_path = url.split("?")[0]
        for fmt in [".png", ".jpg", ".jpeg", ".webp"]:
            if url_path.lower().endswith(fmt):
                ext = fmt
                break

        filename = f"{prefix}_{i}{ext}" if total > 1 else f"{prefix}{ext}"
        filepath = os.path.join(output_dir, filename)

        step(f"Downloading {i}/{total}: {filename}")
        try:
            resp = session.get(url, stream=True, timeout=120)
            resp.raise_for_status()
            total_size = int(resp.headers.get("content-length", 0))
            dl = 0
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        if total_size > 0:
                            pct = int(dl * 100 / total_size)
                            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                            print(f"\r  {bar} {pct}%", end="", flush=True)
            print()
            downloaded.append(filepath)
        except requests.exceptions.RequestException as e:
            error(f"Download failed: {e}")

    return downloaded


def main():
    parser = argparse.ArgumentParser(
        description="AI 图片生成器 - 基于 seedream 5.0 lite 模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 文生图
  python3 seedream.py "一只橘色的猫咪坐在窗台上看着窗外的夕阳"

  # 指定尺寸和格式
  python3 seedream.py "赛博朋克城市夜景" --size 2048x2048 --format png

  # 组图模式（自动生成多张）
  python3 seedream.py "一组美食摄影" --sequential auto --max-images 4

  # 图生图
  python3 seedream.py "把猫咪改成白色，背景换成星空" --image ~/Pictures/cat.png

  # 仅提交任务
  python3 seedream.py "complex scene" --no-download

  # 查询已有任务
  python3 seedream.py "ignored" --task-id ark_abc123def456
        """,
    )
    parser.add_argument("prompt", help="图片生成提示词（中英文均可）")
    parser.add_argument("--image", help="参考图片路径或 URL（启用图生图模式）")
    parser.add_argument("--size", default="2048x2048",
                        help="图片尺寸 (默认 2048x2048, 支持 2K/3K/4K 或具体像素如 1024x1024)")
    parser.add_argument("--format", default="jpeg", choices=["png", "jpeg"],
                        help="输出格式 (默认 jpeg)")
    parser.add_argument("--watermark", action="store_true",
                        help="添加水印 (默认不添加)")
    parser.add_argument("--sequential", choices=["auto", "disabled"], default="disabled",
                        help="组图模式: auto=自动判断/disabled=单张 (默认 disabled)")
    parser.add_argument("--max-images", type=int, default=4,
                        help="组图最多生成数量 1-15 (默认 4, 仅 sequential=auto 时生效)")
    parser.add_argument("--optimize", choices=["standard", "fast"],
                        help="提示词优化模式: standard=高质量/fast=快速")
    parser.add_argument("--no-download", action="store_true",
                        help="仅提交任务并返回 taskId，不等待结果")
    parser.add_argument("--task-id", help="直接查询已有任务的结果 (跳过提交)")
    parser.add_argument("--api-key", help="API Key (前往 https://redfox.hk/settings/api-keys?source=github 注册获取)")
    parser.add_argument("-o", "--output-dir", help="输出目录 (默认 ~/Downloads/QoderImages)")
    parser.add_argument("--prefix", default="image", help="下载文件名前缀 (默认 image)")

    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════════╗
  ║     Qoder Image Generator (API)          ║
  ║   AI 图片生成工具 · seedream 5.0 lite    ║
  ╚══════════════════════════════════════════╝{RESET}
"""
    print(banner)

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)

    if api_key == PUBLIC_API_KEY and not args.api_key and not os.environ.get(ENV_KEY):
        print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║  使用内置公共 API Key                         ║{RESET}")
        print(f"{YELLOW}║  超出额度后请前往以下链接获取 Key：          ║{RESET}")
        print(f"{YELLOW}║  https://redfox.hk/settings/api-keys         ║{RESET}")
        print(f"{YELLOW}║  export REDFOX_API_KEY=ak_你的密钥                 ║{RESET}")
        print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}")
        print()

    # ── Session ──
    session = requests.Session()
    session.verify = True
    session.headers.update({
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    })

    # ── Mode: Query existing task ──
    if args.task_id:
        step(f"Querying task: {args.task_id}")
        result = poll_result(session, args.task_id)
        if not result:
            sys.exit(1)

        print()
        image_urls = result.get("imageUrls", [])
        model = result.get("model", "?")
        size = result.get("size", "?")
        usage = result.get("usage", {})

        info(f"Model: {model}, Size: {size}")
        if usage:
            info(f"Generated images: {usage.get('generatedImages', '?')}, Tokens: {usage.get('totalTokens', '?')}")

        if image_urls:
            output_dir = os.path.expanduser(args.output_dir) if args.output_dir else str(Path.home() / "Downloads" / "QoderImages")
            os.makedirs(output_dir, exist_ok=True)
            downloaded = download_images(session, image_urls, output_dir, args.prefix)
            if downloaded:
                print(f"\n{GREEN}{BOLD}✓ Done!{RESET}")
                for f in downloaded:
                    size_kb = os.path.getsize(f) / 1024
                    print(f"  {f} ({size_kb:.1f} KB)")
            else:
                print(f"\n{RED}{BOLD}✗ Download failed{RESET}")
                sys.exit(1)
        else:
            warn("Task succeeded but no imageUrls returned")
        sys.exit(0)

    # ── Mode: Submit new task ──
    prompt = args.prompt.strip()
    if not prompt:
        error("提示词不能为空")
        sys.exit(1)

    # Validate max-images
    if args.max_images < 1 or args.max_images > 15:
        error(f"max-images 取值范围: 1-15，当前值: {args.max_images}")
        sys.exit(1)

    # Handle image parameter
    image_value = None
    if args.image:
        if args.image.startswith(("http://", "https://")):
            image_value = args.image
            step(f"Using image URL: {image_value}")
        else:
            image_url = upload_image(api_key, args.image)
            if not image_url:
                sys.exit(1)
            image_value = image_url

    # Display mode and settings
    if image_value:
        step(f"Mode: 图生图 (image-to-image)")
    else:
        step(f"Mode: 文生图 (text-to-image)")
    step(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    step(f"Settings: size={args.size}, format={args.format}, sequential={args.sequential}, watermark={'on' if args.watermark else 'off'}")

    # Build params
    params = {
        "size": args.size,
        "outputFormat": args.format,
        "responseFormat": "url",
        "watermark": args.watermark,
    }
    if image_value:
        params["image"] = image_value
    if args.sequential == "auto":
        params["sequentialImageGeneration"] = "auto"
        params["sequentialImageGenerationOptions"] = {"maxImages": args.max_images}
    if args.optimize:
        params["optimizePromptOptions"] = {"mode": args.optimize}

    # Submit
    step("Submitting image generation task...")
    task_id = submit_task(session, prompt, params)
    if not task_id:
        sys.exit(1)

    info(f"Task submitted: {task_id}")

    if args.no_download:
        print(f"\n{GREEN}{BOLD}✓ Task submitted successfully{RESET}")
        print(f"  taskId: {task_id}")
        print(f"  查询命令: python3 seedream.py \"ignored\" --task-id {task_id}")
        sys.exit(0)

    # Poll
    step("Waiting for image generation...")
    result = poll_result(session, task_id)
    if not result:
        sys.exit(1)

    print()
    image_urls = result.get("imageUrls", [])
    model = result.get("model", "?")
    size = result.get("size", "?")
    usage = result.get("usage", {})

    info(f"Model: {model}, Size: {size}")
    if usage:
        info(f"Generated images: {usage.get('generatedImages', '?')}, Tokens: {usage.get('totalTokens', '?')}")

    if image_urls:
        output_dir = os.path.expanduser(args.output_dir) if args.output_dir else str(Path.home() / "Downloads" / "QoderImages")
        os.makedirs(output_dir, exist_ok=True)
        downloaded = download_images(session, image_urls, output_dir, args.prefix)
        if downloaded:
            print(f"\n{GREEN}{BOLD}✓ Done!{RESET}")
            for f in downloaded:
                size_kb = os.path.getsize(f) / 1024
                print(f"  {f} ({size_kb:.1f} KB)")
            sys.exit(0)
        else:
            print(f"\n{RED}{BOLD}✗ Download failed{RESET}")
            sys.exit(1)
    else:
        error("Task succeeded but no imageUrls returned")
        sys.exit(1)


if __name__ == "__main__":
    main()
