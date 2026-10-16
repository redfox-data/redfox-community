#!/usr/bin/env python3
"""
YouTube 提文案 — 输入 YouTube 链接提取视频文字稿
=========================================
接口：POST /story/api/parseWork/videoSubtitle/youtube
流程：调接口获取字幕轨列表 → 客户端按语言优先级选轨 → 下载字幕文件（json3/srt/vtt）→ 解析为文字稿

Usage:
    python3 extract.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    python3 extract.py "dQw4w9WgXcQ" --language "zh,en"
    python3 extract.py "https://youtu.be/dQw4w9WgXcQ" --timestamp   # 带时间戳
    python3 extract.py "URL" --excel                               # 同时导出 Excel
    python3 extract.py "URL" --json
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from deep_translator import GoogleTranslator
    HAS_TRANSLATOR = True
except ImportError:
    HAS_TRANSLATOR = False

# ─── 配置 ─────────────────────────────────────────────────────────────────────────
API_URL = "https://redfox.hk/story/api/parseWork/videoSubtitle/youtube"
CONFIG_FILE = Path.home() / ".qoder" / "apis" / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "YouTube提文案-GitHub"

DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "QoderYoutubeDigest"
DEFAULT_LANGUAGE = "zh,en,asr"
MAX_RETRIES = 3

# 中文语言标识前缀（languageTag 可能为 zh / zh-CN / zh-TW 等）
ZH_PREFIX = ("zh",)

# ─── 终端颜色 ──────────────────────────────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def is_chinese(language):
    """判断 languageTag 是否为中文"""
    lang_lower = (language or "").lower().replace("_", "-")
    return any(lang_lower.startswith(p) for p in ZH_PREFIX)


def translate_lines(lines, batch_size=30):
    """
    将非中文文案行批量翻译为中文。
    每 batch_size 行合并为一次翻译请求，减少 API 调用次数。
    返回翻译后的行列表（与输入一一对应）。
    """
    if not HAS_TRANSLATOR:
        warn("未安装 deep-translator，无法自动翻译，请执行：pip3 install deep-translator")
        return lines

    translator = GoogleTranslator(source="auto", target="zh-CN")
    translated = []

    for i in range(0, len(lines), batch_size):
        batch = lines[i:i + batch_size]
        # 用特殊分隔符合并，翻译后拆分
        separator = " \n⟪SEP⟫\n "
        merged = separator.join(batch)
        try:
            result = translator.translate(merged)
            parts = result.split("⟪SEP⟫")
            # 清理多余空白
            parts = [p.strip() for p in parts]
            # 如果拆分数量不匹配，回退为逐条翻译
            if len(parts) != len(batch):
                for line in batch:
                    try:
                        translated.append(translator.translate(line).strip())
                    except Exception:
                        translated.append(line)
            else:
                translated.extend(parts)
        except Exception as e:
            warn(f"批量翻译失败，回退逐条翻译：{e}")
            for line in batch:
                try:
                    translated.append(translator.translate(line).strip())
                except Exception:
                    translated.append(line)

    return translated


def info(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")

def warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")

def error(msg):
    print(f"{RED}[✗]{RESET} {msg}")

def step(msg):
    print(f"{CYAN}[→]{RESET} {msg}")


# ─── API Key 管理（CLI > 环境变量 > 配置文件）────────────────────────────────────
def get_api_key(cli_key=None):
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


def print_key_guide():
    error("未检测到 RedFox API Key，请任选一种方式配置：")
    print(f"  1. 环境变量（推荐）：export {ENV_KEY}=ak_你的密钥")
    print(f"  2. 命令行参数：--api-key ak_你的密钥")
    print(f"  3. 配置文件：echo '{{\"api_key\":\"ak_你的密钥\"}}' > ~/.qoder/apis/redfox.json")
    print(f"  注册地址：https://redfox.hk/settings/api-keys?source=github")


# ─── 工具函数 ─────────────────────────────────────────────────────────────────────
def fmt_ts(seconds):
    """秒 → MM:SS 或 HH:MM:SS"""
    try:
        seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "00:00"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def video_url_of(video_id):
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else ""


def normalize_video_url(raw):
    """规范化输入：裸视频 ID / 无协议短链 → 完整 URL（新接口仅接受完整视频链接）"""
    raw = (raw or "").strip().strip('"').strip("'")
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", raw):
        return video_url_of(raw)
    if raw.startswith(("http://", "https://")):
        return raw
    if raw.startswith(("youtube.com/", "www.youtube.com/", "youtu.be/", "m.youtube.com/")):
        return "https://" + raw
    return raw


def ts_to_sec(ts):
    """SRT/VTT 时间戳（HH:MM:SS,mmm 或 HH:MM:SS.mmm）→ 秒"""
    ts = ts.strip().replace(",", ".")
    parts = ts.split(":")
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return 0.0
    return int(h) * 3600 + int(m) * 60 + float(s)


# ─── 字幕轨选择（客户端按语言优先级选轨）──────────────────────────────────────────
def is_auto_track(track):
    """是否为自动生成字幕轨（languageName 含 auto-generated 或 URL 带 kind=asr）"""
    name = (track.get("languageName") or "").lower()
    if "auto-generated" in name or "(auto)" in name:
        return True
    for u in track.get("urls") or []:
        if "kind=asr" in (u.get("url") or ""):
            return True
    return False


def select_track(subtitles, priority):
    """
    按逗号分隔的优先级选轨，如 "zh,en,asr"：
    - 语言 token（zh/en/...）匹配 languageTag 前缀，人工字幕优先，无人工轨时接受同语言自动生成轨
    - "asr" 匹配自动生成轨，并按前面语言 token 的顺序优选同语言 asr
    """
    tokens = [t.strip().lower() for t in (priority or "").split(",") if t.strip()]
    if not tokens:
        tokens = [t.strip() for t in DEFAULT_LANGUAGE.split(",")]
    lang_tokens = [t for t in tokens if t != "asr"]

    def tag_of(track):
        return (track.get("languageTag") or "").lower().replace("_", "-")

    for token in tokens:
        if token == "asr":
            auto = [t for t in subtitles if is_auto_track(t)]
            for lt in lang_tokens:
                for t in auto:
                    if tag_of(t).startswith(lt):
                        return t
            if auto:
                return auto[0]
        else:
            for t in subtitles:
                if tag_of(t).startswith(token) and not is_auto_track(t):
                    return t
            for t in subtitles:
                if tag_of(t).startswith(token) and is_auto_track(t):
                    return t
    return None


# ─── 字幕文件下载与解析 ───────────────────────────────────────────────────────────
def pick_subtitle_url(track):
    """从字幕轨的 urls 中按 json3 → srt → vtt 优先级选一个下载地址"""
    urls = track.get("urls") or []
    for fmt in ("json3", "srt", "vtt"):
        for u in urls:
            if (u.get("format") or "").lower() == fmt and u.get("url"):
                return u["url"], fmt
    for u in urls:
        if u.get("url"):
            return u["url"], (u.get("format") or "").lower()
    return None, None


def clean_text(txt):
    txt = re.sub(r"<[^>]+>", "", txt)  # 去掉 VTT 内联标签
    return re.sub(r"\s+", " ", txt).strip()


def parse_json3(raw):
    """YouTube timedtext json3：events[].segs[].utf8"""
    obj = json.loads(raw)
    segs = []
    for ev in obj.get("events") or []:
        parts = [s.get("utf8", "") for s in (ev.get("segs") or [])]
        txt = clean_text("".join(parts))
        if not txt:
            continue
        segs.append({
            "text": txt,
            "start": (ev.get("tStartMs") or 0) / 1000,
            "duration": (ev.get("dDurationMs") or 0) / 1000,
        })
    return segs


def parse_srt_vtt(raw):
    """解析 SRT / VTT 字幕块（时间行含 -->，其余为文本）"""
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    if raw.lstrip().startswith("WEBVTT"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else ""
    segs = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        ti = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if ti is None:
            continue
        m = re.search(r"(\d{1,2}:\d{2}:\d{2}[,.]\d+)\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.]\d+)", lines[ti])
        if not m:
            continue
        start = ts_to_sec(m.group(1))
        end = ts_to_sec(m.group(2))
        txt = clean_text(" ".join(lines[ti + 1:]))
        if txt:
            segs.append({"text": txt, "start": start, "duration": max(0.0, end - start)})
    return segs


def dedupe_segments(segs):
    """去掉连续重复文本（自动生成字幕常见滚动重复）"""
    out = []
    for s in segs:
        if out and out[-1]["text"] == s["text"]:
            continue
        out.append(s)
    return out


def download_subtitle(session, track):
    """下载并解析所选字幕轨，返回 segments 列表；失败回退其他格式"""
    urls = track.get("urls") or []
    tried = set()
    ordered = []
    for fmt in ("json3", "srt", "vtt"):
        for u in urls:
            f = (u.get("format") or "").lower()
            if f == fmt and u.get("url") and u["url"] not in tried:
                ordered.append((u["url"], f))
    for u in urls:
        f = (u.get("format") or "").lower()
        if u.get("url") and u["url"] not in tried and (u["url"], f) not in ordered:
            ordered.append((u["url"], f))

    for url, fmt in ordered:
        tried.add(url)
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code != 200 or not resp.text.strip():
                warn(f"字幕下载失败（{fmt}，HTTP {resp.status_code}），尝试其他格式…")
                continue
            segs = parse_json3(resp.text) if fmt == "json3" else parse_srt_vtt(resp.text)
            segs = dedupe_segments(segs)
            if segs:
                return segs
            warn(f"字幕解析为空（{fmt}），尝试其他格式…")
        except (requests.exceptions.RequestException, ValueError) as e:
            warn(f"字幕下载/解析异常（{fmt}）：{e}")
    return []


# ─── 字幕接口（带递增延迟重试 + 限频处理）──────────────────────────────────────────
def fetch_transcript(session, api_key, video_url, language):
    """
    调用 videoSubtitle 接口获取字幕轨列表，客户端选轨后下载解析字幕。
    成功返回标准化 data 字典（video_id / title / duration / language / language_name / transcript），失败返回 None。
    重试覆盖三类失败：网络异常、状态码错误、业务数据为空；鉴权失败不重试。
    """
    payload = {"url": video_url, "source": SOURCE}
    headers = {
        "REDFOX_API_KEY": api_key,
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = session.post(API_URL, json=payload, headers=headers, timeout=30)
            result = resp.json()

            if not isinstance(result, dict):
                warn("响应格式异常（非 JSON 对象）")
                data = None
            else:
                code = result.get("code")
                if code in (200, 2000):
                    data = result.get("data")
                elif code == 3105:
                    error("API Key 已禁用（3105），请更换有效密钥")
                    return None
                elif code in (3106, 3107):
                    error("API Key 无效或已过期，请检查配置（3106/3107）")
                    return None
                elif code == 3108:
                    warn("触发接口限频，5 秒后重试…")
                    time.sleep(5)
                    continue
                elif code == 3203:
                    # 链接无效/提取失败属确定性错误，重试无意义
                    error(f"提取失败：{result.get('msg', result.get('message', ''))}")
                    return None
                else:
                    warn(f"接口返回错误：code={code} msg={result.get('msg', result.get('message', ''))}")
                    data = None

            if isinstance(data, dict):
                subtitles = data.get("subtitles") or []
                if not subtitles:
                    warn("返回数据不含字幕轨（视频可能无字幕）")
                else:
                    track = select_track(subtitles, language)
                    if not track:
                        avail = "、".join(
                            f"{t.get('languageTag', '?')}({t.get('languageName', '?')})"
                            for t in subtitles[:10]
                        )
                        warn(f"按语言优先级 [{language}] 未匹配到字幕轨，可用轨：{avail}")
                    else:
                        tag = track.get("languageTag") or ""
                        name = track.get("languageName") or tag
                        segs = download_subtitle(session, track)
                        if segs:
                            return {
                                "video_id": data.get("id", ""),
                                "title": data.get("title") or "",
                                "duration": data.get("duration") or 0,
                                "language": tag,
                                "language_name": name,
                                "auto": is_auto_track(track),
                                "transcript": segs,
                            }
                        warn("所选字幕轨下载/解析失败")

        except requests.exceptions.RequestException as e:
            warn(f"网络请求异常：{e}")
        except (json.JSONDecodeError, ValueError):
            warn("响应解析失败（非 JSON）")

        if attempt < MAX_RETRIES - 1:
            delay = 0.5 * (attempt + 1)  # 0.5s → 1.0s 递增
            time.sleep(delay)

    return None


# ─── 输出格式化 ─────────────────────────────────────────────────────────────────────
def render_lines(data, with_timestamp=True):
    """把 transcript 渲染成行列表"""
    lines = []
    transcript = data.get("transcript") or []
    for seg in transcript:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        if with_timestamp:
            lines.append(f"[{fmt_ts(seg.get('start', 0))}] {text}")
        else:
            lines.append(text)
    return lines


def total_duration_of(data):
    """优先用接口返回的视频时长，兜底取最后一条字幕的结束时间"""
    try:
        dur = float(data.get("duration") or 0)
        if dur > 0:
            return dur
    except (ValueError, TypeError):
        pass
    transcript = data.get("transcript") or []
    if not transcript:
        return 0
    last = transcript[-1]
    try:
        return float(last.get("start", 0)) + float(last.get("duration", 0))
    except (ValueError, TypeError):
        return 0


def build_markdown(data, lines, with_timestamp, video_url_input):
    video_id = data.get("video_id", "")
    language = data.get("language", "")
    language_name = data.get("language_name") or language
    title = data.get("title") or ""

    md = ["# YouTube 视频文案", ""]
    md.append("| 项目 | 内容 |")
    md.append("|------|------|")
    if title:
        md.append(f"| 标题 | {title} |")
    md.append(f"| 视频ID | {video_id} |")
    md.append(f"| 视频链接 | {video_url_of(video_id) or video_url_input} |")
    md.append(f"| 语言 | {language_name} ({language}){' 自动生成' if data.get('auto') else ''} |")
    md.append(f"| 片段数 | {len(data.get('transcript') or [])} |")
    md.append(f"| 总时长 | {fmt_ts(total_duration_of(data))} |")
    md.append(f"| 时间戳 | {'含' if with_timestamp else '不含'} |")
    md.append(f"| 提取时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    md.append("")
    md.append("---")
    md.append("")
    md.extend(lines)
    md.append("")
    return "\n".join(md)


# ─── Excel 导出 ──────────────────────────────────────────────────────────────────
def export_excel(data, lines, fpath):
    """导出 xlsx：标题 / 时长 / 视频链接 / 文案内容（与当前时间戳模式一致）"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
    except ImportError:
        return False

    video_id = data.get("video_id", "")
    title = data.get("title") or video_id

    wb = Workbook()
    ws = wb.active
    ws.title = "视频文案"
    ws.append(["标题", "时长", "视频链接", "文案内容"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.append([title, fmt_ts(total_duration_of(data)), video_url_of(video_id), "\n".join(lines)])

    for col, width in {"A": 40, "B": 10, "C": 52, "D": 100}.items():
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(fpath)
    return True


# ─── 主流程 ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="YouTube 提文案 — 输入 YouTube 链接/ID 提取视频文字稿"
    )
    parser.add_argument("video_url", help="YouTube 视频 URL（完整/短链）或直接给视频 ID")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE,
                        help=f"字幕语言优先级，逗号分隔（默认 {DEFAULT_LANGUAGE}：中文字幕轨优先，无中文回退英文，asr=自动生成字幕兜底；客户端选轨）")
    parser.add_argument("--timestamp", action="store_true",
                        help="输出带 [MM:SS] 时间戳的文案（默认不带时间戳）")
    parser.add_argument("--excel", action="store_true",
                        help="同时导出 Excel（.xlsx，需 openpyxl）")
    parser.add_argument("--json", action="store_true",
                        help="终端输出原始 JSON 响应")
    parser.add_argument("--no-save", action="store_true",
                        help="不保存 Markdown 文件")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR),
                        help=f"输出目录（默认 {DEFAULT_OUTPUT_DIR}）")
    parser.add_argument("--no-translate", dest="translate", action="store_false",
                        help="禁用自动翻译（默认非中文字幕自动翻译为中文）")
    parser.set_defaults(translate=True)
    parser.add_argument("--api-key", default=None, help="指定 RedFox API Key")
    args = parser.parse_args()

    if not HAS_REQUESTS:
        error("缺少 requests 库，请先执行：pip3 install requests")
        sys.exit(1)

    api_key = get_api_key(args.api_key)
    if not api_key:
        print_key_guide()
        sys.exit(1)

    with_timestamp = args.timestamp
    video_url = normalize_video_url(args.video_url)
    step(f"正在提取文字稿：{video_url}（语言优先级：{args.language}）")

    session = requests.Session()
    data = fetch_transcript(session, api_key, video_url, language=args.language)
    if data is None:
        error("提取失败：多次重试后仍无法获取文字稿")
        error("可能原因：视频无字幕 / 视频不存在或受限 / API 额度不足")
        sys.exit(1)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))

    # ─── 概要 ───
    video_id = data.get("video_id", "")
    language = data.get("language", "")
    language_name = data.get("language_name") or language
    transcript = data.get("transcript") or []
    title = data.get("title") or ""

    info(f"提取成功：视频 {video_id}")
    if title:
        print(f"  标题：{title}")
    print(f"  语言：{language_name} ({language}){' 自动生成' if data.get('auto') else ''} ｜ 片段数：{len(transcript)} ｜ 总时长：{fmt_ts(total_duration_of(data))}")
    print(f"  链接：{video_url_of(video_id) or video_url}")

    # ─── 自动翻译（非中文字幕 → 中文）───
    need_translate = args.translate and not is_chinese(language)
    if need_translate:
        step(f"检测到字幕语言为 {language_name}，正在自动翻译为中文…")

    # ─── 文案全文 ───
    lines = render_lines(data, with_timestamp)
    if not lines:
        warn("文字稿为空，无文案可展示")
    else:
        if need_translate:
            lines = translate_lines(lines)
            info(f"翻译完成（{len(lines)} 段）")
        print(f"\n{DIM}{'─' * 60}{RESET}")
        print(f"{BOLD}文案全文（{len(lines)} 段）：{RESET}\n")
        for line in lines:
            print(line)
        print(f"{DIM}{'─' * 60}{RESET}\n")

    # ─── 保存文件 ───
    if not args.no_save:
        out_dir = Path(args.output_dir).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{video_id or 'transcript'}_{stamp}.md"
        fpath = out_dir / fname
        fpath.write_text(build_markdown(data, lines, with_timestamp, video_url), encoding="utf-8")
        info(f"文案已保存：{fpath}")

    # ─── Excel 导出 ───
    if args.excel:
        out_dir = Path(args.output_dir).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xpath = out_dir / f"{video_id or 'transcript'}_{stamp}.xlsx"
        if export_excel(data, lines, xpath):
            info(f"Excel 已保存：{xpath}")
        else:
            warn("未安装 openpyxl，无法导出 Excel，请执行：pip3 install openpyxl")


if __name__ == "__main__":
    main()
