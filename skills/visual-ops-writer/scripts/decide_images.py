"""断章生图决策脚本

输入：markdown 格式正文（字符串 或 文件路径）
输出：JSON {image_plan: [...], stats: {...}}

决策规则：
  1. 切分：按 H2 拆成多个 section
  2. 字数：每 500-800 字配 1 张图（章节内），首图建议在第 1-2 节内
  3. 锚点：检测"如下图/如上图/举个例子/来看个案例/接下来"等强提示词，
     在该句之后优先插图
  4. 边界：不在引言/结语/FAQ 内强制插图，由字数决定
  5. 标题检测：H2 标题含"案例/示例/图解/对比/数据"等关键词时，倾向插图

使用方式：
  python decide_images.py --input article.md
  python decide_images.py --input article.md --min-words 500 --max-words 800
  echo "正文" | python decide_images.py --stdin
"""

import argparse
import json
import re
import sys
from pathlib import Path


# 强锚点词：这些词出现后，必然是图位的强信号
ANCHOR_KEYWORDS_STRONG = [
    r"如下图", r"如上图", r"看下面这张图", r"看这张图",
    r"举个例子", r"来看个例子", r"来看个案例", r"举个栗子",
    r"如图所示", r"见图", r"看图", r"如图",
    r"接下来", r"来看", r"看这里",
]

# 弱锚点词：图位候选信号，需要结合字数判断
ANCHOR_KEYWORDS_WEAK = [
    r"比如", r"例如", r"想象一下", r"假设",
    r"对比", r"区别", r"差异", r"差距",
    r"流程", r"步骤", r"操作",
]

# 标题信号词：H2 标题含这些词时，倾向在该节插图
HEADING_HINT_KEYWORDS = [
    "案例", "示例", "图解", "对比", "数据", "图表",
    "流程", "步骤", "工具", "方法", "技巧",
    "before", "after", "前后",
]

# 跳过插图的章节类型
SKIP_SECTION_KEYWORDS = [
    "FAQ", "常见问题", "问答", "结语", "总结", "写在最后", "写在最后的话",
]

# 强制插图的章节类型
FORCE_SECTION_KEYWORDS = [
    "案例", "示例", "图解",
]

# 默认参数
DEFAULT_MIN_WORDS = 500
DEFAULT_MAX_WORDS = 800
DEFAULT_MAX_IMAGES = 6
MIN_WORDS_HARD_LIMIT = 300  # 低于此字数不插图


def split_sections(markdown):
    """按 H2 切分 markdown，返回 [{heading, level, content, start_line}]."""
    lines = markdown.split("\n")
    sections = []
    current = None
    in_code_block = False

    for i, line in enumerate(lines):
        # 跳过代码块
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            if current is not None:
                current["content"] += line + "\n"
            continue
        if in_code_block:
            if current is not None:
                current["content"] += line + "\n"
            continue

        # H2 切分
        h2_match = re.match(r"^##\s+(.+)$", line)
        if h2_match:
            if current is not None:
                sections.append(current)
            current = {
                "heading": h2_match.group(1).strip(),
                "level": 2,
                "content": "",
                "start_line": i,
            }
        else:
            if current is None:
                # 引言（在第一个 H2 之前）
                current = {
                    "heading": "引言",
                    "level": 1,
                    "content": "",
                    "start_line": 0,
                }
            current["content"] += line + "\n"

    if current is not None:
        sections.append(current)

    return sections


def count_words(text):
    """统计中文字数（中文按字、英文按词）。"""
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"\b[a-zA-Z]+\b", text))
    return chinese + english


def find_anchor_positions(section_content):
    """在章节内容中查找锚点词位置（行号、类型）。"""
    positions = []
    for i, line in enumerate(section_content.split("\n")):
        for pattern in ANCHOR_KEYWORDS_STRONG:
            if re.search(pattern, line):
                positions.append({"line": i, "type": "strong", "match": pattern, "context": line.strip()[:50]})
                break
        else:
            for pattern in ANCHOR_KEYWORDS_WEAK:
                if re.search(pattern, line):
                    positions.append({"line": i, "type": "weak", "match": pattern, "context": line.strip()[:50]})
                    break
    return positions


def should_skip_section(heading):
    """判断该章节是否跳过插图（FAQ、结语等）。"""
    for kw in SKIP_SECTION_KEYWORDS:
        if kw in heading:
            return True
    return False


def should_force_section(heading):
    """判断该章节是否强制插图（案例、示例等）。"""
    for kw in FORCE_SECTION_KEYWORDS:
        if kw in heading:
            return True
    return False


def heading_has_visual_hint(heading):
    """标题是否含视觉化关键词。"""
    for kw in HEADING_HINT_KEYWORDS:
        if kw.lower() in heading.lower():
            return True
    return False


def decide_image_plan(sections, min_words, max_words, max_images):
    """根据切分后的章节，决定生图计划。"""
    plan = []
    total_words = 0

    for idx, sec in enumerate(sections):
        sec_words = count_words(sec["content"])
        total_words += sec_words
        heading = sec["heading"]

        # 规则 1: 跳过类章节
        if should_skip_section(heading):
            continue

        # 规则 2: 字数太少，整个跳过
        if sec_words < MIN_WORDS_HARD_LIMIT:
            continue

        # 规则 3: 强制插图类
        if should_force_section(heading):
            count = max(1, sec_words // max_words)
            count = min(count, 2)  # 单节最多 2 张
            plan.append({
                "after_section": idx,
                "section_heading": heading,
                "count": count,
                "reason": "force_section",
                "prompt_hint": f"该章节是「{heading}」，需配视觉化插图",
                "anchors": find_anchor_positions(sec["content"])[:count],
            })
            continue

        # 规则 4: 标题含视觉化关键词
        if heading_has_visual_hint(heading):
            count = max(1, sec_words // max_words)
            count = min(count, 2)
            plan.append({
                "after_section": idx,
                "section_heading": heading,
                "count": count,
                "reason": "heading_visual_hint",
                "prompt_hint": f"「{heading}」含视觉化关键词，配置图强化理解",
                "anchors": find_anchor_positions(sec["content"])[:count],
            })
            continue

        # 规则 5: 字数触发（500-800 字/张）
        if sec_words >= min_words:
            # 优先找强锚点；找不到再放章节末尾
            anchors = find_anchor_positions(sec["content"])
            strong_anchors = [a for a in anchors if a["type"] == "strong"]
            count = max(1, sec_words // max_words)
            count = min(count, 2)
            plan.append({
                "after_section": idx,
                "section_heading": heading,
                "count": count,
                "reason": "word_count_trigger" if not strong_anchors else "anchor_match",
                "prompt_hint": f"「{heading}」内容较长（{sec_words}字），配图降低阅读疲劳",
                "anchors": (strong_anchors or anchors)[:count],
            })

    # 全局限制
    if len(plan) > max_images:
        # 优先级：force > heading_visual > anchor > word_count
        priority = {
            "force_section": 4,
            "heading_visual_hint": 3,
            "anchor_match": 2,
            "word_count_trigger": 1,
        }
        plan.sort(key=lambda x: priority.get(x["reason"], 0), reverse=True)
        plan = plan[:max_images]
        # 按章节顺序重排
        plan.sort(key=lambda x: x["after_section"])

    return plan, total_words


def main():
    parser = argparse.ArgumentParser(
        description="读 markdown 正文，自动决定生图点（数量+位置+锚点）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", type=str, help="markdown 文件路径")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取正文")
    parser.add_argument("--output", type=str, default="image_plan.json", help="输出 JSON 路径")
    parser.add_argument("--min-words", type=int, default=DEFAULT_MIN_WORDS, help=f"触发配图的最小字数（默认 {DEFAULT_MIN_WORDS}）")
    parser.add_argument("--max-words", type=int, default=DEFAULT_MAX_WORDS, help=f"每张图覆盖的最大字数（默认 {DEFAULT_MAX_WORDS}）")
    parser.add_argument("--max-images", type=int, default=DEFAULT_MAX_IMAGES, help=f"全篇最大生图数（默认 {DEFAULT_MAX_IMAGES}）")
    args = parser.parse_args()

    # 读取输入
    if args.stdin:
        markdown = sys.stdin.read()
    elif args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"[ERR] File not found: {args.input}")
            sys.exit(1)
        markdown = p.read_text(encoding="utf-8")
    else:
        print("[ERR] Provide --input <file> or --stdin")
        sys.exit(1)

    # 校验参数
    if args.min_words >= args.max_words:
        print(f"[ERR] --min-words ({args.min_words}) must be < --max-words ({args.max_words})")
        sys.exit(1)

    # 切分
    sections = split_sections(markdown)
    print(f"[OK] Split into {len(sections)} sections")
    for sec in sections:
        print(f"  - [{count_words(sec['content'])}字] {sec['heading']}")

    # 决策
    plan, total_words = decide_image_plan(sections, args.min_words, args.max_words, args.max_images)

    # 输出
    result = {
        "image_plan": plan,
        "stats": {
            "total_sections": len(sections),
            "total_words": total_words,
            "planned_images": sum(p["count"] for p in plan),
        },
        "params": {
            "min_words": args.min_words,
            "max_words": args.max_words,
            "max_images": args.max_images,
        },
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[Plan] {result['stats']['planned_images']} images planned")
    for p in plan:
        print(f"  - Section {p['after_section']}「{p['section_heading']}」 x {p['count']} ({p['reason']})")
    print(f"\n[Done] Saved to {args.output}")


if __name__ == "__main__":
    main()
