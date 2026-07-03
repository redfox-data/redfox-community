"""运营文章配图生成脚本（统一版）
基于 gpt-image-2 模型，支持文生图与图生图（传入参考图）
仅依赖 Python 标准库，无需额外安装

用法：
    # 文生图（默认）
    python generate_image.py --prompt "图片描述" --api-key "ak_xxx"
    # 图生图（传入参考图）
    python generate_image.py --prompt "图片描述" --image assets/skill标题.jpg --api-key "ak_xxx"
    # 链接仿写模式（红狐风格不启用，参考图作为风格参照）
    python generate_image.py --prompt "图片描述" --reference-image "https://xxx.com/img.jpg" --style reference --api-key "ak_xxx"
    # 风格切换
    python generate_image.py --prompt "..." --style {redfox|reference|none} --api-key "ak_xxx"
    # 批量生成（prompts.json 中可指定 image 字段）
    python generate_image.py --batch prompts.json --api-key "ak_xxx"
    # 查询已有任务
    python generate_image.py --task-id "task_xxx" --api-key "ak_xxx"
    # 随机风格模式（从可用风格中随机选一种，单次调用内所有图保持一致）
    python generate_image.py --prompt "..." --style random --api-key "ak_xxx"
    # 批量随机风格
    python generate_image.py --batch prompts.json --style random --api-key "ak_xxx"

prompts.json 格式：
    [
        {"id": "img1", "prompt": "...", "chapter": "封面", "image": "assets/skill标题.jpg", "style": "redfox"},
        {"id": "img2", "prompt": "...", "chapter": "热点分析", "image": "assets/02.jpg", "style": "reference"},
        {"id": "img3", "prompt": "...", "chapter": "操作指南", "style": "popcomic"}
    ]

style 参数说明：
    - redfox（默认）：红狐讲解员 + 美式复古报刊暖米黄底
    - popcomic：现代波普漫画风 + 亮黄底 + 多角色场景 + 浮动图标
    - yellowcomic：亮黄信息图漫画风 + 斜纹底 + 分类表格中心
    - reference：原 prompt 不变，仅作图生图参考（适合链接仿写）
    - none：原 prompt 不动，不追加任何风格修饰
    - random：从 redfox / popcomic / yellowcomic 中随机选一个，同批次所有图用同一风格
"""

import argparse
import json
import os
import sys
import time
import random
import urllib.request
import urllib.error
import ssl
import tempfile
from pathlib import Path

SUBMIT_URL = "https://redfox.hk/story/api/parseWork/imageGen/submitSkill"
RESULT_URL = "https://redfox.hk/story/api/parseWork/imageGen/result"
UPLOAD_URL = "https://redfox.hk/story/api/parseWork/imageGen/uploadImage"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"

DEFAULT_PARAMS = {
    "modelName": "gpt-image-2",
    "n": 1,
    "size": "1792x1024",
    "outputFormat": "png",
}

POLL_INTERVAL = 5
MAX_POLLS = 20

# 分辨率白名单（非白名单可能导致生成过慢或失败）
FAST_SIZES = {"1024x1024", "1024x1536", "1536x1024", "1792x1024", "1024x1792"}
HD_SIZES = {"2048x2048", "2048x1152", "1152x2048"}
ALLOWED_SIZES = FAST_SIZES | HD_SIZES

MAX_PROMPT_LENGTH = 500


# 风格修饰器：三种可选视觉风格

# 风格 A — redfox：红狐讲解员 IP + 美式复古报刊暖米黄底
REDFOX_STYLE_SUFFIX = (
    "，画面中心为红色狐狸讲解员（红色毛皮、白色胸腹、大尾巴、海军蓝小马甲、圆框眼镜），"
    "美式复古报刊科普条漫风格，横向宽幅多格分镜，胶片颗粒质感，"
    "无装饰性边框，狐狸为视觉中心，参考 prompt 描述的姿态（封面=欢迎、分析=前倾拿教鞭、"
    "方法论=托腮沉思、操作=坐在电脑前打字）"
)

# 风格 B — popcomic：现代波普漫画风 + 亮黄底 + 多角色场景（基于 assets/02.jpg）
POPCOMIC_STYLE_SUFFIX = (
    "，现代波普漫画信息图插画风格，高饱和亮黄色底色配波普网点纹理，粗黑轮廓线+扁平高饱和色块填充，"
    "画面中心为一位干练的讲解员卡通人物（职业装/衬衫，表情自信开朗），左侧1-2位困惑的从业者卡通人物带问号和对话气泡，右侧可有1-2位角色互动，"
    "顶部圆角矩形横幅内大号加粗中文主标题，周围浮动UI装饰图标（图表/邮件/齿轮/搜索框/对话框），"
    "人物间有白色圆角对话气泡承载中文文案，动态活泼构图，2D矢量商业插画，8K高清；"
    "禁止写实摄影、3D渲染、暗沉阴影、杂乱线条、水印、模糊字体、文字乱码"
)

# 风格 C — yellowcomic：亮黄信息图漫画风 + 斜纹底 + 分类表格中心（基于 assets/03.jpg）
YELLOWCOMIC_STYLE_SUFFIX = (
    "，亮黄色斜纹底色现代信息图漫画插画风格，粗重清晰黑色轮廓线，纯色平涂高饱和马卡龙色块，"
    "画面中心为一位自信的讲解员手持分类表格或文档（职业装，表情从容），左侧困惑角色群带问号气泡，右侧角色可互动，"
    "顶部圆角矩形横幅大号加粗中文标题，周围散布齿轮/文档/聊天框/折线图等操作类图标装饰，"
    "人物对话气泡承载中文文案，流程感和分工感强，2D矢量商业插画，8K高清；"
    "禁止写实摄影、3D渲染、暗沉阴影、杂乱线条、水印、模糊字体、文字乱码"
)

# 所有可用风格（random 从中选取，排除 reference 和 none）
RANDOMIZABLE_STYLES = ["redfox", "popcomic", "yellowcomic"]
VALID_STYLES = {"redfox", "popcomic", "yellowcomic", "reference", "none", "random"}


def apply_style(prompt, style):
    """根据 style 参数对 prompt 做风格修饰。

    - redfox: 追加红狐讲解员 + 美式复古报刊条漫风格
    - popcomic: 追加现代波普漫画风（亮黄底+多角色场景）
    - yellowcomic: 追加亮黄信息图漫画风（斜纹底+分类表格中心）
    - reference: 原 prompt 不变（参考图自带风格）
    - none: 原 prompt 不变
    """
    style_suffix_map = {
        "redfox": REDFOX_STYLE_SUFFIX,
        "popcomic": POPCOMIC_STYLE_SUFFIX,
        "yellowcomic": YELLOWCOMIC_STYLE_SUFFIX,
    }
    suffix = style_suffix_map.get(style)
    if suffix:
        if len(prompt) + len(suffix) > MAX_PROMPT_LENGTH:
            available = MAX_PROMPT_LENGTH - len(suffix) - 3
            prompt = prompt[:available] + "..."
        return prompt + suffix
    # reference / none：原样返回
    return prompt


def pick_random_style():
    """从 RANDOMIZABLE_STYLES 中随机选一个风格名称。"""
    return random.choice(RANDOMIZABLE_STYLES)


def get_api_key(cli_key=None):
    """Get API key: CLI arg > env var > config file."""
    if cli_key:
        return cli_key
    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            key = data.get("api_key")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return None


def make_request(url, data, api_key, timeout=30):
    """Send a JSON POST request and return parsed response."""
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "REDFOX_API_KEY": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"code": -1, "msg": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"code": -1, "msg": str(e)}


def upload_image(image_path, api_key):
    """Upload a local image to OSS, return the image URL."""
    if not os.path.isfile(image_path):
        print(f"[ERR] Image file not found: {image_path}")
        return None

    ext = os.path.splitext(image_path)[1].lower()
    fmt_map = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp"}
    fmt = fmt_map.get(ext, "png")

    print(f"[UP] Uploading image: {image_path}")

    boundary = "----PythonFormBoundary7MA4YWxkTrZu0gW"
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="format"\r\n\r\n'
        f"{fmt}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: image/{fmt}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        UPLOAD_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-API-KEY": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[ERR] Upload failed: {e}")
        return None

    code = result.get("code")
    if not str(code).startswith("2"):
        print(f"[ERR] Upload failed (code {code}): {result.get('msg', '')}")
        return None

    image_url = result.get("data", {}).get("imageUrl")
    if not image_url:
        print("[ERR] Upload succeeded but no imageUrl returned")
        return None

    print(f"[OK] Upload complete: {image_url}")
    return image_url


def is_url(path):
    """Check if a string is an HTTP(S) URL."""
    return path.startswith("http://") or path.startswith("https://")


def download_url_to_temp(url):
    """Download a URL to a temp file, return the temp file path."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ext = os.path.splitext(url.split("?")[0])[1] or ".webp"
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    print(f"[DL] Downloading: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, context=ctx) as resp:
            tmp.write(resp.read())
        tmp.close()
        print(f"[OK] Downloaded to: {tmp.name}")
        return tmp.name
    except Exception as e:
        print(f"[ERR] Download failed: {e}")
        tmp.close()
        return None


def download_images(image_urls, output_dir, prefix="image"):
    """Download generated images to output directory."""
    downloaded = []
    total = len(image_urls)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for i, url in enumerate(image_urls, 1):
        ext = ".png"
        url_path = url.split("?")[0]
        for fmt in [".png", ".jpg", ".jpeg", ".webp"]:
            if url_path.lower().endswith(fmt):
                ext = fmt
                break

        filename = f"{prefix}_{i}{ext}" if total > 1 else f"{prefix}{ext}"
        filepath = os.path.join(output_dir, filename)

        print(f"[DL] Downloading {i}/{total}: {filename}")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, context=ctx) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  OK: {filepath} ({size_kb:.1f} KB)")
            downloaded.append(filepath)
        except Exception as e:
            print(f"  ERR: Download failed: {e}")

    return downloaded


def submit_task(prompt, api_key, image_path=None, fidelity=None, size=None, quality=None, style="redfox"):
    """Submit an image generation task. Returns taskId or None.

    style:
        - redfox: 红狐讲解员 + 美式复古报刊风格（默认）
        - popcomic: 现代波普漫画风（亮黄底+多角色场景）
        - yellowcomic: 亮黄信息图漫画风（斜纹底+分类表格中心）
        - reference: prompt 不变，靠参考图自带的风格
        - none: prompt 不变
        - random: 从 redfox/popcomic/yellowcomic 中随机选一个（调用方需自行确保同批次一致性）
    """
    operation = "generate"
    images = None

    # 风格修饰：random 需在此处解析为具体风格
    if style == "random":
        style = pick_random_style()
        print(f"[OK] Random style selected: {style}")

    if style not in VALID_STYLES:
        print(f"[WARN] Unknown style '{style}', fallback to 'redfox'")
        style = "redfox"
    final_prompt = apply_style(prompt, style)
    if final_prompt != prompt:
        print(f"[OK] Style applied: {style} (+{len(final_prompt) - len(prompt)} chars)")
    elif style in ("reference", "none"):
        print(f"[OK] Style applied: {style} (no modification)")

    if image_path:
        operation = "edit"
        if is_url(image_path):
            temp_path = download_url_to_temp(image_path)
            if not temp_path:
                return None
            image_url = upload_image(temp_path, api_key)
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            if not image_url:
                return None
            print(f"[OK] Mode: image-to-image (edit), ref URL -> OSS: {image_url}")
        else:
            image_url = upload_image(image_path, api_key)
            if not image_url:
                return None
            print(f"[OK] Mode: image-to-image (edit), ref: {image_path}")
        images = [{"url": image_url}]
    else:
        print(f"[OK] Mode: text-to-image (generate)")

    params = dict(DEFAULT_PARAMS)
    if size:
        params["size"] = size
    if quality:
        params["quality"] = quality

    data = {"prompt": final_prompt, "parameters": params, "operation": operation}
    if images:
        data["images"] = images
    if operation == "edit" and fidelity:
        data["parameters"]["inputFidelity"] = fidelity

    resp = make_request(SUBMIT_URL, data, api_key)

    if resp.get("code") == 2000 and resp.get("data", {}).get("taskId"):
        task_id = resp["data"]["taskId"]
        print(f"[OK] Task submitted: {task_id}")
        return task_id
    else:
        print(f"[ERR] Submit failed: {resp.get('msg', 'unknown error')}")
        return None


def poll_result(task_id, api_key):
    """Poll task result until success, failure, or timeout."""
    for i in range(MAX_POLLS):
        resp = make_request(RESULT_URL, {"taskId": task_id}, api_key, timeout=15)

        if resp.get("code") != 2000:
            print(f"[WARN] Poll {i+1}/{MAX_POLLS}: API error - {resp.get('msg')}")
            time.sleep(POLL_INTERVAL)
            continue

        status = resp.get("data", {}).get("status", "")

        if status == "success":
            paths = resp["data"].get("imagePaths", [])
            if isinstance(paths, str):
                paths = [paths]
            print(f"[OK] Task {task_id} succeeded: {paths}")
            return paths

        elif status == "failed":
            reason = resp["data"].get("failReason", "unknown")
            print(f"[ERR] Task {task_id} failed: {reason}")
            return None

        else:
            elapsed = (i + 1) * POLL_INTERVAL
            print(f"[...] Poll {i+1}/{MAX_POLLS}: pending ({elapsed}s elapsed)")
            time.sleep(POLL_INTERVAL)

    print(f"[TIMEOUT] Task {task_id} timed out after {MAX_POLLS * POLL_INTERVAL}s")
    return None


def generate_single(prompt, api_key, image_path=None, fidelity=None, size=None, quality=None, style="redfox"):
    """Generate a single image. Returns list of URLs or empty list."""
    task_id = submit_task(prompt, api_key, image_path=image_path, fidelity=fidelity, size=size, quality=quality, style=style)
    if not task_id:
        return []
    result = poll_result(task_id, api_key)
    return result or []


def generate_batch(prompts_file, api_key, default_style="redfox"):
    """Generate multiple images from a JSON file. Returns dict of id -> URLs.

    每个 item 可独立指定 style 字段；未指定则用 default_style。
    当 default_style 为 random 时，会先随机选一个具体风格，整批所有图都用该风格（保证同批次一致）。
    """
    base_dir = os.path.dirname(os.path.abspath(prompts_file))
    with open(prompts_file, "r", encoding="utf-8") as f:
        items = json.load(f)

    # 如果默认风格是 random，整批统一选一个
    if default_style == "random":
        resolved_default = pick_random_style()
        print(f"[OK] Batch random style selected: {resolved_default} (all items will use this style)")
    else:
        resolved_default = default_style

    results = {}
    tasks = {}
    for item in items:
        img_id = item.get("id", f"img_{len(tasks)}")
        prompt = item["prompt"]
        image_path = item.get("image")
        fidelity = item.get("fidelity")
        size = item.get("size")
        quality = item.get("quality")
        # 优先用 item 自身的 style，否则用已解析的 default
        item_style = item.get("style", resolved_default)
        if image_path and not os.path.isabs(image_path) and not is_url(image_path):
            image_path = os.path.join(base_dir, image_path)
        task_id = submit_task(prompt, api_key, image_path=image_path, fidelity=fidelity, size=size, quality=quality, style=item_style)
        if task_id:
            tasks[img_id] = task_id

    for img_id, task_id in tasks.items():
        urls = poll_result(task_id, api_key)
        results[img_id] = urls or []

    return results


def main():
    parser = argparse.ArgumentParser(
        description="运营文章配图生成（统一版，支持文生图 + 图生图 + 批量生成）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", type=str, help="单张图片 prompt")
    parser.add_argument("--batch", type=str, help="批量生成 JSON 文件路径")
    parser.add_argument("--image", type=str, default=None, help="参考图路径或 URL（启用图生图模式）")
    parser.add_argument("--reference-image", type=str, default=None, help="参考图别名（等同于 --image，但语义更清晰）")
    parser.add_argument("--fidelity", type=str, default=None, choices=["high", "low"], help="图生图保真度（high=高保真/low=低保真）")
    parser.add_argument("--size", type=str, default="1792x1024", help=f"图片尺寸（默认 1792x1024，可选: {', '.join(sorted(ALLOWED_SIZES))}）")
    parser.add_argument("--quality", type=str, default="medium", choices=["low", "medium", "high", "auto"], help="图片质量（默认 medium）")
    parser.add_argument("--style", type=str, default="redfox", choices=sorted(VALID_STYLES), help="风格模式：redfox（默认）/ popcomic / yellowcomic / reference / none / random（随机，同批次内需手动保持一致）")
    parser.add_argument("--api-key", type=str, default=None, help="REDFOX_API_KEY")
    parser.add_argument("--output", type=str, default="results.json", help="结果输出文件")
    parser.add_argument("--task-id", type=str, default=None, help="查询已有任务结果（跳过提交）")
    parser.add_argument("--download-dir", type=str, default=None, help="下载图片到本地目录（不传则仅返回 URL）")
    args = parser.parse_args()

    # 兼容 --reference-image 与 --image
    if args.reference_image and not args.image:
        args.image = args.reference_image

    # Validate size
    if args.size not in ALLOWED_SIZES:
        print(f"[ERR] Unsupported size: {args.size}")
        print(f"  Fast sizes: {', '.join(sorted(FAST_SIZES))}")
        print(f"  HD sizes (slower): {', '.join(sorted(HD_SIZES))}")
        sys.exit(1)

    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        print("[ERR] REDFOX_API_KEY is required. Set via --api-key or REDFOX_API_KEY env var.")
        print("  Get key: https://redfox.hk/settings/api-keys?source=skillhub")
        sys.exit(1)

    # Mode: Query existing task
    if args.task_id:
        print(f"[QUERY] Querying task: {args.task_id}")
        urls = poll_result(args.task_id, api_key)
        if urls:
            results = {"query": urls}
            if args.download_dir:
                os.makedirs(args.download_dir, exist_ok=True)
                downloaded = download_images(urls, args.download_dir)
                results["downloaded"] = downloaded
        else:
            results = {"query": []}
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0 if urls else 1)

    # Validate prompt length
    if args.prompt and len(args.prompt) > MAX_PROMPT_LENGTH:
        print(f"[ERR] Prompt too long ({len(args.prompt)} chars), max {MAX_PROMPT_LENGTH}")
        sys.exit(1)

    if args.batch:
        results = generate_batch(args.batch, api_key, default_style=args.style)
    elif args.prompt:
        urls = generate_single(args.prompt, api_key, image_path=args.image, fidelity=args.fidelity, size=args.size, quality=args.quality, style=args.style)
        results = {"single": urls}
        if urls and args.download_dir:
            os.makedirs(args.download_dir, exist_ok=True)
            downloaded = download_images(urls, args.download_dir)
            results["downloaded"] = downloaded
    else:
        print("[ERR] Provide --prompt or --batch")
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[Done] Results saved to {args.output}")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
