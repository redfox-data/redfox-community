#!/usr/bin/env python3
"""
Qoder Image Generator - 基于 gpt-image-2 的图片生成工具

对接红狐新版接口：
    SUBMIT: POST https://redfox.hk/story/api/parseWork/imageGen/gptImage2Submit
    RESULT: POST https://redfox.hk/story/api/parseWork/imageGen/gptImage2Result

新接口请求参数：
    prompt          (String, 必填)
    resolution      (String, 必填) 1k / 2k / 4k
    size            (String, 必填) 宽高比：1:1 / 3:2 / 2:3 / 4:3 / 3:4 / 5:4 / 4:5 /
                                    16:9 / 9:16 / 2:1 / 1:2 / 21:9 / 9:21
    n               (Integer, 必填) 生成数量，最大 4
    referenceImages (Array, 必填) 参考图 URL 列表，最多 2 张（文生图传空数组）

新接口响应字段（data）：
    taskId / status(completed|processing|failed) / progress(0-100) /
    imageUrls[] / failReason / model / resolution / size

Usage:
    python3 imagegen.py "提示词" [options]
    python3 imagegen.py "修改提示词" --image ~/path/to/ref.png
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

SUBMIT_URL = "https://redfox.hk/story/api/parseWork/imageGen/gptImage2Submit"
RESULT_URL = "https://redfox.hk/story/api/parseWork/imageGen/gptImage2Result"
UPLOAD_URL = "https://redfox.hk/story/api/parseWork/imageGen/uploadImage"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
POLL_INTERVAL = 3  # seconds
MAX_POLL_ATTEMPTS = 80  # max ~4 minutes

# 新接口 size 支持的宽高比
VALID_ASPECTS = {
    "1:1", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5",
    "16:9", "9:16", "2:1", "1:2", "21:9", "9:21",
}
VALID_RESOLUTIONS = {"1k", "2k", "4k"}

# 兼容旧像素格式：像素尺寸 → (新接口 size 宽高比, 推荐 resolution 档位)
LEGACY_SIZE_MAP = {
    "1024x1024": ("1:1", "1k"),
    "1024x1536": ("2:3", "1k"),
    "1536x1024": ("3:2", "1k"),
    "1792x1024": ("16:9", "1k"),
    "1024x1792": ("9:16", "1k"),
    "2048x2048": ("1:1", "2k"),
    "2048x1152": ("16:9", "2k"),
    "1152x2048": ("9:16", "2k"),
}

MAX_PROMPT_LENGTH = 500
MAX_REFERENCE_IMAGES = 2
MAX_COUNT = 4

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
    """Get API key: CLI arg > env var > config file."""
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
            headers = {"REDFOX_API_KEY": api_key, "X-API-KEY": api_key}
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

    data = result.get("data") or {}
    image_url = data.get("imageUrl")
    if not image_url:
        error("Upload succeeded but no imageUrl returned")
        return None

    info(f"Upload complete: {image_url}")
    return image_url


def confirm_retry():
    """询问用户是否需要重试。"""
    while True:
        answer = input(f"{YELLOW}[?]{RESET} 是否重试？(y/n): ").strip().lower()
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False


def normalize_size(size_arg, resolution_arg):
    """把 CLI 传入的 --size 归一化为新接口的 (aspect, resolution)。

    支持两种输入：
      1. 像素格式（旧）：1792x1024 → ("16:9", "1k")
      2. 宽高比格式（新）：16:9 → ("16:9", resolution_arg or "2k")
    """
    size_str = (size_arg or "").strip()

    if size_str in LEGACY_SIZE_MAP:
        aspect, default_res = LEGACY_SIZE_MAP[size_str]
        resolution = (resolution_arg or default_res).strip().lower()
        if resolution not in VALID_RESOLUTIONS:
            error(f"Unsupported --resolution: {resolution}")
            sys.exit(1)
        return aspect, resolution

    if size_str in VALID_ASPECTS:
        resolution = (resolution_arg or "2k").strip().lower()
        if resolution not in VALID_RESOLUTIONS:
            error(f"Unsupported --resolution: {resolution}")
            sys.exit(1)
        return size_str, resolution

    error(f"Unsupported --size: {size_str}")
    print(f"  宽高比可选: {', '.join(sorted(VALID_ASPECTS))}")
    print(f"  兼容旧像素格式: {', '.join(sorted(LEGACY_SIZE_MAP.keys()))}")
    sys.exit(1)


def submit_task(session, prompt, resolution, aspect, n, reference_images):
    """Submit image generation task via gptImage2Submit, return taskId."""
    payload = {
        "prompt": prompt,
        "resolution": resolution,
        "size": aspect,
        "n": n,
        "referenceImages": reference_images or [],
        "source": "imageGen-GitHub",
    }

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

    data = result.get("data") or {}
    task_id = data.get("taskId")
    if not task_id:
        error("API did not return taskId")
        return None

    return task_id


def poll_result(session, task_id):
    """Poll gptImage2Result until completed/failed/timeout, return imageUrls list."""
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        try:
            resp = session.post(RESULT_URL, json={"taskId": task_id}, timeout=15)
            result = resp.json()
        except requests.exceptions.RequestException as e:
            warn(f"Poll request failed (attempt {attempt}): {e}")
            time.sleep(POLL_INTERVAL)
            continue
        except json.JSONDecodeError:
            warn(f"Invalid JSON response (attempt {attempt})")
            time.sleep(POLL_INTERVAL)
            continue

        code = result.get("code")
        if not str(code).startswith("2"):
            error(f"Query failed (code {code}): {result.get('msg', '')}")
            return None

        data = result.get("data") or {}
        status = data.get("status")

        if status == "completed":
            urls = data.get("imageUrls") or []
            if isinstance(urls, str):
                urls = [urls]
            print()  # 结束进度行
            return urls
        elif status == "failed":
            reason = data.get("failReason") or "unknown"
            print()
            error(f"Generation failed: {reason}")
            return None
        else:
            # processing / pending
            progress = data.get("progress")
            elapsed = attempt * POLL_INTERVAL
            suffix = f" {progress}%" if isinstance(progress, int) else ""
            print(f"\r  {CYAN}⏳ Generating...{suffix} ({elapsed}s){RESET}", end="", flush=True)
            time.sleep(POLL_INTERVAL)

    print()
    error("Timeout: task did not complete within expected time")
    return None


def download_images(session, image_urls, output_dir, prefix="image"):
    """Download generated images to output directory."""
    downloaded = []
    total = len(image_urls)

    for i, url in enumerate(image_urls, 1):
        ext = ".png"
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
        description="AI 图片生成器 - 基于 gpt-image-2（对接 gptImage2Submit/gptImage2Result 新接口）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 文生图（默认 16:9 + 2k）
  python3 imagegen.py "一只橘色的猫咪坐在窗台上看着窗外的夕阳"

  # 竖版 4k
  python3 imagegen.py "cyberpunk city" --size 9:16 --resolution 4k

  # 批量 4 张
  python3 imagegen.py "icon set, flat style" -n 4

  # 图生图（最多 2 张参考图）
  python3 imagegen.py "把猫咪改成白色，背景换成星空" --image ~/Pictures/cat.png

  # 兼容旧像素格式（自动映射为宽高比 + 分辨率档位）
  python3 imagegen.py "logo design" --size 1792x1024
        """,
    )
    parser.add_argument("prompt", help="图片生成/编辑提示词 (最多 500 字)")
    parser.add_argument("--api-key", help="API Key (不传则读取环境变量或配置文件)")
    parser.add_argument("-o", "--output-dir", help="输出目录 (默认 ~/Downloads/QoderImages)")
    parser.add_argument("-n", "--count", type=int, default=1,
                        help=f"生成图片数量 (1-{MAX_COUNT}, 默认 1，新接口上限 4)")
    parser.add_argument("--size", default="16:9",
                        help="图片宽高比 (默认 16:9，可选: "
                             + ", ".join(sorted(VALID_ASPECTS))
                             + ")；也兼容旧像素格式如 1792x1024")
    parser.add_argument("--resolution", default=None, choices=sorted(VALID_RESOLUTIONS),
                        help="分辨率档位 1k/2k/4k（默认：像素格式跟随档位，宽高比格式默认 2k）")
    parser.add_argument("--image", action="append", default=None,
                        help=f"参考图路径或 URL（可多次传入，最多 {MAX_REFERENCE_IMAGES} 张；启用图生图模式）")
    parser.add_argument("--no-download", action="store_true",
                        help="仅提交任务并返回 taskId, 不等待结果")
    parser.add_argument("--task-id", help="直接查询已有任务的结果 (跳过提交)")
    parser.add_argument("--prefix", default="image", help="下载文件名前缀 (默认 image)")

    # 已弃用参数：新接口不再支持，仅为向后兼容 CLI 保留，接收后忽略
    parser.add_argument("--quality", help="[已弃用] 新接口用 --resolution 表达档位，此参数被忽略")
    parser.add_argument("--format", dest="fmt", help="[已弃用] 新接口固定输出 PNG，此参数被忽略")
    parser.add_argument("--bg", "--background", dest="bg",
                        help="[已弃用] 新接口不再支持 background，此参数被忽略")
    parser.add_argument("--compression", type=int,
                        help="[已弃用] 新接口不再支持 outputCompression，此参数被忽略")
    parser.add_argument("--fidelity",
                        help="[已弃用] 新接口不再支持 inputFidelity，此参数被忽略")

    args = parser.parse_args()

    # 弃用参数提示
    deprecated = []
    if args.quality:
        deprecated.append("--quality")
    if args.fmt:
        deprecated.append("--format")
    if args.bg:
        deprecated.append("--bg")
    if args.compression is not None:
        deprecated.append("--compression")
    if args.fidelity:
        deprecated.append("--fidelity")

    # 校验 count
    if args.count < 1 or args.count > MAX_COUNT:
        error(f"-n 取值范围 1-{MAX_COUNT}（新接口上限为 4）")
        sys.exit(1)

    # 校验 prompt 长度
    if len(args.prompt) > MAX_PROMPT_LENGTH:
        error(f"提示词过长 ({len(args.prompt)} 字)，请控制在 {MAX_PROMPT_LENGTH} 字以内")
        sys.exit(1)

    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════╗
  ║     Qoder Image Generator (API)      ║
  ║     AI 图片生成工具 · gpt-image-2    ║
  ╚══════════════════════════════════════╝{RESET}
"""
    print(banner)

    if deprecated:
        warn(f"以下参数在新接口已弃用，将被忽略: {', '.join(deprecated)}")

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        error("未找到 API Key，请设置环境变量 REDFOX_API_KEY 或使用 --api-key 参数")
        print(f"  获取 Key: https://redfox.hk/settings/api-keys?source=github")
        sys.exit(1)

    # ── Session（新接口鉴权头：REDFOX_API_KEY；同时兼容 X-API-KEY） ──
    session = requests.Session()
    session.verify = True
    session.headers.update({
        "Content-Type": "application/json",
        "REDFOX_API_KEY": api_key,
        "X-API-KEY": api_key,
    })

    # ── Mode: Query existing task ──
    if args.task_id:
        step(f"Querying task: {args.task_id}")
        image_urls = poll_result(session, args.task_id)
        if not image_urls:
            sys.exit(1)
        info(f"Generated {len(image_urls)} image(s)")
        output_dir = args.output_dir or str(Path.home() / "Downloads" / "QoderImages")
        os.makedirs(output_dir, exist_ok=True)
        downloaded = download_images(session, image_urls, output_dir, args.prefix)
        if downloaded:
            print(f"\n{GREEN}{BOLD}✓ Done!{RESET}")
            for f in downloaded:
                size_kb = os.path.getsize(f) / 1024
                print(f"  {f} ({size_kb:.1f} KB)")
        sys.exit(0)

    # ── Mode: Submit new task ──
    prompt = args.prompt.strip()
    if not prompt:
        error("提示词不能为空")
        sys.exit(1)

    # 归一化 size / resolution 到新接口格式
    aspect, resolution = normalize_size(args.size, args.resolution)

    # 处理参考图
    reference_images = []
    if args.image:
        if len(args.image) > MAX_REFERENCE_IMAGES:
            warn(f"参考图数量超过上限，仅保留前 {MAX_REFERENCE_IMAGES} 张")
        for img in args.image[:MAX_REFERENCE_IMAGES]:
            if img.startswith("http://") or img.startswith("https://"):
                reference_images.append(img)
            else:
                url = upload_image(api_key, img)
                if not url:
                    sys.exit(1)
                reference_images.append(url)
        step(f"Mode: 图生图 (referenceImages={len(reference_images)})")
    else:
        step("Mode: 文生图")

    step(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    step(f"Parameters: size={aspect}, resolution={resolution}, n={args.count}")

    while True:
        step("Submitting task...")
        task_id = submit_task(session, prompt, resolution, aspect, args.count, reference_images)
        if task_id:
            break
        if not confirm_retry():
            sys.exit(1)

    info(f"Task submitted: {task_id}")

    if args.no_download:
        print(f"\n{GREEN}{BOLD}✓ Task submitted successfully{RESET}")
        print(f"  taskId: {task_id}")
        print(f"  查询命令: python3 imagegen.py \"\" --task-id {task_id}")
        sys.exit(0)

    step("Waiting for generation...")
    image_urls = poll_result(session, task_id)
    if not image_urls:
        sys.exit(1)

    info(f"Generated {len(image_urls)} image(s)")

    output_dir = args.output_dir or str(Path.home() / "Downloads" / "QoderImages")
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


if __name__ == "__main__":
    main()
