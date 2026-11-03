#!/usr/bin/env python3
"""
Qoder Video Generator - 基于 Seedance 2.0 的视频生成工具
使用 redfox.hk API 提交视频生成任务并下载结果

Usage:
    python3 videogen.py "提示词" [options]
    python3 videogen.py "ignored" --task-id vg_xxx
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

SUBMIT_URL = "https://redfox.hk/story/api/parseWork/videoGen/seedanceSubmit"
RESULT_URL = "https://redfox.hk/story/api/parseWork/videoGen/result"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"

POLL_INTERVAL = 10  # seconds
MAX_POLL_ATTEMPTS = 120  # max ~20 minutes

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


def confirm_retry():
    """询问用户是否需要重试。"""
    while True:
        try:
            answer = input(f"{YELLOW}[?]{RESET} 是否重试？(y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        if answer in ('y', 'yes'):
            return True
        if answer in ('n', 'no'):
            return False


def submit_video_task(session, prompt, params, images=None):
    """Submit video generation task, return taskId."""
    payload = {
        "prompt": prompt,
        "aspectRatio": params["ratio"],
        "duration": params["duration"],
        "resolution": params["resolution"],
        "generateAudio": params["generateAudio"],
        "returnLastFrame": params["returnLastFrame"],
        "imageWithRoles": images or [],
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

    if code != 2000:
        error(f"Submit failed (code {code}): {msg}")
        return None

    data = result.get("data")
    if not data or not data.get("taskId"):
        error("API did not return taskId")
        return None

    return data["taskId"]


def poll_video_result(session, task_id):
    """Poll for video task result until succeeded/failed/expired/timeout."""
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

        consecutive_errors = 0  # Reset on success

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
        elif status == "expired":
            error("Task expired: the task did not complete within the allowed time")
            return None
        else:
            # queued or running
            elapsed = attempt * POLL_INTERVAL
            status_cn = {"queued": "排队中", "running": "生成中"}.get(status, status)
            print(f"\r  {CYAN}⏳ Generating... ({elapsed}s) [{status_cn}]{RESET}", end="", flush=True)
            time.sleep(POLL_INTERVAL)

    print()
    error(f"Timeout: task did not complete within {MAX_POLL_ATTEMPTS * POLL_INTERVAL}s")
    print(f"  You can query later with: --task-id {task_id}")
    return None


def download_video(session, video_url, output_dir, prefix="video", task_id=""):
    """Download generated video to output directory."""
    # Determine extension from URL
    ext = ".mp4"
    url_path = video_url.split("?")[0]
    for fmt in [".mp4", ".mov", ".avi", ".webm"]:
        if url_path.lower().endswith(fmt):
            ext = fmt
            break

    # Handle filename conflict: append short taskId if file exists
    filename = f"{prefix}{ext}"
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath) and task_id:
        short_id = task_id.replace("vg_", "")[:8]
        filename = f"{prefix}_{short_id}{ext}"
        filepath = os.path.join(output_dir, filename)

    step(f"Downloading video: {filename}")
    try:
        resp = session.get(video_url, stream=True, timeout=300)
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
        return filepath
    except requests.exceptions.RequestException as e:
        error(f"Download failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="AI 视频生成器 - 基于 Seedance 2.0 模型，输入关键词生成视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 基本生成
  python3 videogen.py "一只橘猫在窗台上打哈欠，阳光温暖地照在它的毛上"

  # 竖屏短视频
  python3 videogen.py "时尚都市夜景，霓虹灯闪烁" --ratio 9:16

  # 高清 10 秒
  python3 videogen.py "海浪拍打岩石的慢动作" --resolution 720p --duration 10

  # 图生视频（参考图/首帧/尾帧）
  python3 videogen.py "让图片中的猫咪动起来，眨眼摇尾巴" --image-url "https://example.com/cat.jpg"
  python3 videogen.py "转场到第二个场景" --image-url "上一步的lastFrameUrl" --image-role first_frame

  # 仅提交任务
  python3 videogen.py "复杂场景" --no-download

  # 查询已有任务
  python3 videogen.py "ignored" --task-id <taskId>
        """,
    )
    parser.add_argument("prompt", help="视频生成提示词（中英文均可）")
    parser.add_argument("--resolution", default="720p", choices=["480p", "720p"],
                        help="视频分辨率 (默认 720p)")
    parser.add_argument("--ratio", default="16:9",
                        choices=["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"],
                        help="画面比例 (默认 16:9)")
    parser.add_argument("--duration", type=int, default=5,
                        help="视频时长秒数: 4-15 (默认 5)")
    parser.add_argument("--no-audio", action="store_true",
                        help="不生成声音 (默认生成)")
    parser.add_argument("--return-last-frame", action="store_true",
                        help="返回视频尾帧图片 URL")
    parser.add_argument("--image-url",
                        help="参考图片 URL，逗号分隔可传多张")
    parser.add_argument("--image-role", default="reference_image",
                        choices=["first_frame", "last_frame", "reference_image"],
                        help="图片角色: 首帧图/尾帧图/参考图 (默认 reference_image)")
    parser.add_argument("--api-key", help="API Key (前往 https://redfox.hk/settings/api-keys?source=github 注册获取)")
    parser.add_argument("-o", "--output-dir", help="输出目录 (默认 ~/Downloads/QoderVideos)")
    parser.add_argument("--prefix", default="video", help="下载文件名前缀 (默认 video)")
    parser.add_argument("--no-download", action="store_true",
                        help="仅提交任务并返回 taskId，不等待结果")
    parser.add_argument("--task-id", help="直接查询已有任务的结果 (跳过提交)")

    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════════╗
  ║      Qoder Video Generator (API)         ║
  ║   AI 视频生成工具 · Seedance 2.0         ║
  ╚══════════════════════════════════════════╝{RESET}
"""
    print(banner)

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        error("未找到 API Key，请设置环境变量 REDFOX_API_KEY 或使用 --api-key 参数")
        print(f"  获取 Key: https://redfox.hk/settings/api-keys?source=github")
        sys.exit(1)

    # ── Session (all requests use HTTPS with SSL verification) ──
    session = requests.Session()
    session.verify = True
    session.headers.update({
        "Content-Type": "application/json",
        "REDFOX_API_KEY": api_key,
    })

    # ── Mode: Query existing task ──
    if args.task_id:
        step(f"Querying task: {args.task_id}")
        result = poll_video_result(session, args.task_id)
        if not result:
            sys.exit(1)

        print()
        video_url = result.get("videoUrl")
        last_frame_url = result.get("lastFrameUrl")
        duration = result.get("duration", "?")
        resolution = result.get("resolution", "?")
        ratio = result.get("ratio", "?")
        usage = result.get("usage", {})
        tokens = usage.get("totalTokens", "?") if usage else "?"

        info(f"Video ready: {duration}s, {resolution}, {ratio}")
        if last_frame_url:
            info(f"Last frame: {last_frame_url}")
        if usage:
            info(f"Token usage: {tokens}")

        if video_url:
            output_dir = os.path.expanduser(args.output_dir) if args.output_dir else str(Path.home() / "Downloads" / "QoderVideos")
            os.makedirs(output_dir, exist_ok=True)
            filepath = download_video(session, video_url, output_dir, args.prefix, args.task_id)
            if filepath:
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"\n{GREEN}{BOLD}✓ Done!{RESET}")
                print(f"  {filepath} ({size_mb:.1f} MB)")
            else:
                print(f"\n{RED}{BOLD}✗ Download failed{RESET}")
                sys.exit(1)
        else:
            warn("Task succeeded but no videoUrl returned")
        sys.exit(0)

    # ── Mode: Submit new task ──
    prompt = args.prompt.strip()
    if not prompt:
        error("提示词不能为空")
        sys.exit(1)

    # Validate duration
    if args.duration < 4 or args.duration > 15:
        error(f"duration 取值范围: 4-15，当前值: {args.duration}")
        sys.exit(1)

    # Build image list with role
    images = []
    if args.image_url:
        for u in [x.strip() for x in args.image_url.split(",") if x.strip()]:
            images.append({"url": u, "role": args.image_role})
        if args.image_role in ("first_frame", "last_frame") and len(images) > 1:
            error(f"{args.image_role} 最多只能传 1 张图片，当前: {len(images)} 张")
            sys.exit(1)

    step(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    step(f"Settings: {args.resolution}, {args.ratio}, {args.duration}s, audio={'off' if args.no_audio else 'on'}")

    if images:
        step(f"Reference images: {len(images)} 张 (role={args.image_role})")

    # Build parameters
    params = {
        "resolution": args.resolution,
        "ratio": args.ratio,
        "duration": args.duration,
        "generateAudio": not args.no_audio,
        "returnLastFrame": args.return_last_frame,
    }

    # Submit
    while True:
        step("Submitting video generation task...")
        task_id = submit_video_task(session, prompt, params, images)
        if task_id:
            break
        if not confirm_retry():
            sys.exit(1)

    info(f"Task submitted: {task_id}")

    if args.no_download:
        print(f"\n{GREEN}{BOLD}✓ Task submitted successfully{RESET}")
        print(f"  taskId: {task_id}")
        print(f"  查询命令: python3 videogen.py \"ignored\" --task-id {task_id}")
        sys.exit(0)

    # Poll for result
    step("Waiting for video generation (may take several minutes)...")
    result = poll_video_result(session, task_id)
    if not result:
        sys.exit(1)

    print()
    video_url = result.get("videoUrl")
    last_frame_url = result.get("lastFrameUrl")
    duration = result.get("duration", "?")
    resolution = result.get("resolution", "?")
    ratio = result.get("ratio", "?")
    usage = result.get("usage", {})
    tokens = usage.get("totalTokens", "?") if usage else "?"

    info(f"Video ready: {duration}s, {resolution}, {ratio}")
    if last_frame_url:
        info(f"Last frame: {last_frame_url}")
    if usage:
        info(f"Token usage: {tokens}")

    if video_url:
        output_dir = os.path.expanduser(args.output_dir) if args.output_dir else str(Path.home() / "Downloads" / "QoderVideos")
        os.makedirs(output_dir, exist_ok=True)
        filepath = download_video(session, video_url, output_dir, args.prefix, task_id)
        if filepath:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"\n{GREEN}{BOLD}✓ Done!{RESET}")
            print(f"  {filepath} ({size_mb:.1f} MB)")
            sys.exit(0)
        else:
            print(f"\n{RED}{BOLD}✗ Download failed{RESET}")
            sys.exit(1)
    else:
        error("Task succeeded but no videoUrl returned")
        sys.exit(1)


if __name__ == "__main__":
    main()
