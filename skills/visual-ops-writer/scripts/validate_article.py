"""文章质量验证脚本（v2.3 软阈值版）

把 SKILL.md 中的质量检查清单从人工 checklist 升级为可机械化验证的脚本。
v2.3 重要变化：所有阈值改为软建议——超范围只出 warning，不直接 fail。
写作框架应跟随 Skill 逻辑动态调整，不被硬阈值锁死。

使用方式：
  # 默认（软阈值，目标字数 1000）
  python validate_article.py --input article.md

  # 自定义字数目标
  python validate_article.py --input article.md --target-length 1500

  # 严格模式（恢复 v2.1 硬 fail 行为，仅在需要 CI 严格拦截时使用）
  python validate_article.py --input article.md --strict

检查项（v2.3 全部为 warning 级别，超范围不直接 fail）：
  - 禁忌词检测（赋能、抓手、打法、闭环、颗粒度、对齐、沉淀、方法论前置）
  - 字数统计（默认 500-1500 区间，目标 1000 字）
  - 标题长度（8-30 字）
  - 章节数（2-8 节正文）
  - 表格数（0-3 张，0 张也合规）
  - 段落行数（每段不超过 5 行）
  - FAQ 数量（0 或 2-4 个，0 个也合规）
  - 信息密度：每 400 字至少 1 个数字 + 1 个动词开头的句子
  - 链接/图片来源标注（资料来源章节）
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---- 禁忌词表 ----
FORBIDDEN_WORDS = [
    "赋能", "抓手", "打法", "闭环", "颗粒度", "对齐", "沉淀", "方法论前置",
    # 句式触发词（出现就扣分）
]

FORBIDDEN_PATTERNS = [
    r"在当今.{0,15}的时代",
    r"众所周知",
    r"不言而喻",
    r"!!!+",  # 感叹号堆叠
]

# ---- 结构参数（v2.3 软阈值：所有检查默认 warning 级别）----
# 注意：v2.3 重要原则变化——所有这些阈值都是"软建议"，不直接 fail。
# 写作时 LLM 应根据 Skill 逻辑、选题类型、读者需求动态判断。
TITLE_MIN_LEN = 8
TITLE_MAX_LEN = 30         # v2.3 放宽（v2.1 是 25）
SECTION_MIN = 2            # v2.3 放宽（v2.1 是 3）
SECTION_MAX = 8            # v2.3 放宽（v2.1 是 6）
TABLE_MIN = 0              # v2.3 改 0：表格按需出现，不强制（v2.1 是 2）
TABLE_MAX = 3              # v2.3 保持
PARAGRAPH_MAX_LINES = 5    # v2.3 放宽（v2.1 是 4）
FAQ_COUNT_MIN = 2          # v2.3 改 2-4 区间（v2.1 是固定 3）
FAQ_COUNT_MAX = 4
WORDS_PER_DENSITY_CHECK = 400  # v2.3 放宽（v2.1 是 300）

# ---- 字数目标（v2.3 默认 1000 字左右，可配置）----
DEFAULT_TARGET_LENGTH = 1000
TARGET_LENGTH_TOLERANCE = 500  # ±500 字缓冲（如目标 1000 字，500-1500 都算 pass）


def read_markdown(path):
    """读取 markdown 文件，去掉代码块和图片语法但保留行结构。"""
    p = Path(path)
    if not p.exists():
        print(f"[ERR] File not found: {path}")
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def extract_title(markdown):
    """提取 H1 标题。"""
    for line in markdown.split("\n"):
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return ""


def extract_sections(markdown):
    """提取 H2 章节（含 heading + content + 行号）。"""
    sections = []
    lines = markdown.split("\n")
    current = None
    in_code = False

    for i, line in enumerate(lines):
        # 代码块跳过
        if line.strip().startswith("```"):
            in_code = not in_code
            if current:
                current["content"] += line + "\n"
            continue
        if in_code:
            if current:
                current["content"] += line + "\n"
            continue

        m = re.match(r"^##\s+(.+)$", line)
        if m:
            if current:
                sections.append(current)
            current = {
                "heading": m.group(1).strip(),
                "content": "",
                "start_line": i,
            }
        else:
            if current is None:
                # 引言（首个 H2 之前）
                current = {"heading": "引言", "content": "", "start_line": 0}
            current["content"] += line + "\n"

    if current:
        sections.append(current)
    return sections


def count_words(text):
    """统计字数（中文字 + 英文词）。"""
    # 去掉 markdown 标记
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)  # 图片
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # 链接保留文字
    text = re.sub(r"[#*_>|]", "", text)

    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    english = len(re.findall(r"\b[a-zA-Z]+\b", text))
    return chinese + english


def count_tables(markdown):
    """统计 markdown 表格数量（按 |...| 行匹配）。"""
    in_code = False
    table_count = 0
    in_table = False

    for line in markdown.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 表格行：包含 | 且两端以 | 结尾
        if re.match(r"^\s*\|.+\|\s*$", line):
            if not in_table:
                in_table = True
                table_count += 1
        else:
            in_table = False
    return table_count


def count_paragraph_lines(sections):
    """统计每段的行数，识别超过 4 行的段落。"""
    violations = []
    for sec in sections:
        # 去掉表格、代码块、标题
        text = sec["content"]
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"^\|.*$", "", text, flags=re.MULTILINE)  # 表格行
        text = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)  # 标题

        # 按空行分段
        paragraphs = re.split(r"\n\s*\n", text)
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            line_count = len([l for l in para.split("\n") if l.strip()])
            if line_count > PARAGRAPH_MAX_LINES:
                violations.append({
                    "section": sec["heading"],
                    "paragraph_index": i,
                    "lines": line_count,
                    "preview": para[:50] + "...",
                })
    return violations


def find_forbidden_words(markdown):
    """查找禁忌词及其出现位置。"""
    findings = []
    lines = markdown.split("\n")

    for word in FORBIDDEN_WORDS:
        for i, line in enumerate(lines, 1):
            if word in line:
                findings.append({
                    "word": word,
                    "line": i,
                    "context": line.strip()[:80],
                })

    for pattern in FORBIDDEN_PATTERNS:
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                findings.append({
                    "word": f"pattern: {pattern}",
                    "line": i,
                    "context": line.strip()[:80],
                })

    return findings


def extract_faq(sections):
    """提取 FAQ 章节的 Q&A 数量。

    支持以下格式：
    - Q1: ... / Q1：...
    - **Q：...？** / **Q: ...?**
    - **Q1：...？**
    """
    faq = None
    for sec in sections:
        if "FAQ" in sec["heading"] or "常见问题" in sec["heading"]:
            faq = sec
            break
    if not faq:
        return 0
    # 多种格式都算
    patterns = [
        r"^Q\d+[：:]",  # Q1: / Q1：
        r"\*\*Q\d*[：:]\s*",  # **Q： / **Q1:
        r"^Q[：:]",  # Q: / Q：
        r"^##\s*Q\d+",  # ## Q1
    ]
    count = 0
    for pattern in patterns:
        matches = re.findall(pattern, faq["content"], re.MULTILINE)
        count = max(count, len(matches))
    return count


def count_info_density(sections):
    """信息密度检查：每 300 字应至少 1 个数字 + 1 个动词开头的句子。

    返回 violations 列表：每个元素是一个 dict{section, type, detail}。
    """
    violations = []
    # 用前 30 个常见动词做检测，避免构造大正则出错
    action_verbs_str = (
        "打开|点击|输入|选择|设置|使用|访问|下载|安装|运行|执行|创建|添加|删除|修改|"
        "检查|对比|避免|记住|关注|尝试|记下|抄|看|找|想|算|做|选|配|加|减|分|拆|排|"
        "写|画|测|跑|试|调|查|读|听|问|答|记|列|提|交|练|统|归|汇|制|定|布|署|"
        "进入|退出|返回|跳转|切到|换到|转到|改到|调到|移到|拉|推|滚|翻|"
        "请|必须|需要|应当|应该|可以|可能|建议|推荐|考虑"
    )

    for sec in sections:
        if "FAQ" in sec["heading"] or "结语" in sec["heading"]:
            continue
        text = re.sub(r"```.*?```", "", sec["content"], flags=re.DOTALL)
        text = re.sub(r"^\|.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

        words = count_words(text)
        if words == 0:
            continue

        # 检查密度
        expected_density = max(1, words // WORDS_PER_DENSITY_CHECK)

        # 数字数量
        numbers = re.findall(r"\d+(?:\.\d+)?", text)
        if len(numbers) < expected_density:
            violations.append({
                "section": sec["heading"],
                "type": "low_number_density",
                "expected": expected_density,
                "actual": len(numbers),
                "words": words,
            })

        # 动词句数量（行首是动词）
        action_lines = re.findall(rf"^(?:{action_verbs_str})", text, re.MULTILINE)
        if len(action_lines) < expected_density:
            violations.append({
                "section": sec["heading"],
                "type": "low_action_density",
                "expected": expected_density,
                "actual": len(action_lines),
                "words": words,
            })

    return violations


def has_source_section(sections):
    """检查是否有资料来源章节。"""
    for sec in sections:
        if "资料来源" in sec["heading"] or "参考" in sec["heading"]:
            return True
    return False


def check_paragraph_lines(sections):
    """段落行数检查：每段不超过 4 行（去掉空行/标题/表格）。"""
    return count_paragraph_lines(sections)


def main():
    parser = argparse.ArgumentParser(
        description="运营文章质量验证（v2.3 软阈值版，所有检查默认 warning 级别）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", type=str, required=True, help="markdown 文件路径")
    parser.add_argument("--output", type=str, default="validation_report.json", help="验证报告输出路径")
    parser.add_argument("--strict", action="store_true", help="严格模式（恢复 v2.1 硬 fail 行为）：任一 fail 退出码 1")
    parser.add_argument("--target-length", type=int, default=DEFAULT_TARGET_LENGTH,
                        help=f"目标字数（v2.3 默认 {DEFAULT_TARGET_LENGTH}），配合 ±{TARGET_LENGTH_TOLERANCE} 缓冲检查")
    parser.add_argument("--mode", type=str, choices=["link_rewrite", "skill_promo", "add_images"],
                        default=None, help="文章生成模式：link_rewrite 模式下跳过字数检查（跟随源文章长度）")
    args = parser.parse_args()

    markdown = read_markdown(args.input)
    target_length = args.target_length
    target_min = max(200, target_length - TARGET_LENGTH_TOLERANCE)
    target_max = target_length + TARGET_LENGTH_TOLERANCE

    # ---- 执行各项检查 ----
    # v2.3 重要变化：所有检查默认输出 status ∈ {pass, warning}，不再有 fail
    # 除非 --strict 模式（恢复 v2.1 硬 fail 行为）
    report = {
        "file": args.input,
        "config": {
            "target_length": target_length,
            "target_range": f"{target_min}-{target_max}",
            "mode": "strict" if args.strict else "soft",
            "version": "v2.3",
        },
        "checks": {},
        "summary": {"passed": 0, "warnings": 0, "failed": 0},
    }

    # 1. 标题长度（v2.3：超范围只出 warning）
    title = extract_title(markdown)
    title_len = len(title)
    title_ok = TITLE_MIN_LEN <= title_len <= TITLE_MAX_LEN
    if args.strict:
        status = "pass" if title_ok else "fail"
    else:
        status = "pass" if title_ok else "warning"
    report["checks"]["title_length"] = {
        "title": title,
        "length": title_len,
        "expected_range": f"{TITLE_MIN_LEN}-{TITLE_MAX_LEN}",
        "status": status,
        "note": "v2.3 软化：超范围仅提示，不强制" if not title_ok and not args.strict else None,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 2. 章节数（v2.3：超范围只出 warning）
    sections = extract_sections(markdown)
    section_count = len(sections)
    section_ok = SECTION_MIN <= section_count <= SECTION_MAX
    if args.strict:
        status = "pass" if section_ok else "fail"
    else:
        status = "pass" if section_ok else "warning"
    report["checks"]["section_count"] = {
        "count": section_count,
        "expected_range": f"{SECTION_MIN}-{SECTION_MAX}",
        "status": status,
        "note": "v2.3 软化：2-8 节均为合理区间" if not section_ok and not args.strict else None,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 3. 表格数（v2.3：v2.1 强制 2-3 张 → v2.3 改为 0-3 张，0 张也合规）
    table_count = count_tables(markdown)
    table_ok = TABLE_MIN <= table_count <= TABLE_MAX
    if args.strict:
        # strict 模式仍按 v2.1 标准：至少 2 张
        table_ok_strict = 2 <= table_count <= 3
        status = "pass" if table_ok_strict else "fail"
    else:
        status = "pass" if table_ok else "warning"
    note = None
    if not table_ok and not args.strict:
        if table_count == 0:
            note = "v2.3 软化：0 张表也合规（叙事/资讯类常见）"
        else:
            note = "v2.3 软化：表格按需出现，不强制"
    report["checks"]["table_count"] = {
        "count": table_count,
        "expected_range": f"{TABLE_MIN}-{TABLE_MAX}",
        "status": status,
        "note": note,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 4. 字数（v2.3：默认 1000 字，可配置 target-length；link_rewrite 模式跳过）
    total_words = count_words(markdown)
    if args.mode == "link_rewrite":
        # link_rewrite 跟随源文章长度，不做字数约束
        report["checks"]["word_count"] = {
            "words": total_words,
            "expected_range": "不限制（link_rewrite 模式跟随源文章长度）",
            "status": "pass",
            "note": "link_rewrite 模式不受字数约束",
        }
        report["summary"]["passed"] += 1
    else:
        if args.strict:
            word_ok = 1500 <= total_words <= 4000  # v2.1 硬阈值
            expected_range = "1500-4000"
        else:
            word_ok = target_min <= total_words <= target_max
            expected_range = f"{target_min}-{target_max}（目标 {target_length}）"
        report["checks"]["word_count"] = {
            "words": total_words,
            "expected_range": expected_range,
            "status": "pass" if word_ok else "warning",
            "note": "v2.3 默认 1000 字左右，可通过 --target-length 自定义" if not word_ok and not args.strict else None,
        }
        report["summary"]["passed" if word_ok else "warnings"] += 1

    # 5. FAQ 数量（v2.3：2-4 个合理区间，0 个也允许）
    faq_count = extract_faq(sections)
    if args.strict:
        faq_ok = faq_count == 3
    else:
        faq_ok = (faq_count == 0) or (FAQ_COUNT_MIN <= faq_count <= FAQ_COUNT_MAX)
    report["checks"]["faq_count"] = {
        "count": faq_count,
        "expected_range": f"0 或 {FAQ_COUNT_MIN}-{FAQ_COUNT_MAX}" if not args.strict else "恰好 3",
        "status": "pass" if faq_ok else "warning",
        "note": "v2.3 软化：FAQ 数量动态生成，0/2/3/4 都合规" if not faq_ok and not args.strict else None,
    }
    report["summary"]["passed" if faq_ok else "warnings"] += 1

    # 6. 资料来源（v2.3：v2.1 强制 → v2.3 改为软）
    source_ok = has_source_section(sections)
    if args.strict:
        status = "pass" if source_ok else "fail"
    else:
        status = "pass" if source_ok else "warning"
    report["checks"]["source_section"] = {
        "present": source_ok,
        "status": status,
        "note": "v2.3 软化：资料来源仅在涉及外部数据时推荐" if not source_ok and not args.strict else None,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 7. 禁忌词（v2.3：v2.1 强制 → v2.3 改为 warning）
    forbidden = find_forbidden_words(markdown)
    forbidden_ok = len(forbidden) == 0
    if args.strict:
        status = "pass" if forbidden_ok else "fail"
    else:
        status = "pass" if forbidden_ok else "warning"
    report["checks"]["forbidden_words"] = {
        "count": len(forbidden),
        "findings": forbidden[:5],
        "status": status,
        "note": "v2.3 软化：禁忌词仅提示，调用方决定替换" if not forbidden_ok and not args.strict else None,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 8. 段落行数（v2.3：v2.1 强制 4 → v2.3 改 5，软警告）
    para_violations = check_paragraph_lines(sections)
    para_ok = len(para_violations) == 0
    if args.strict:
        status = "pass" if para_ok else "fail"
    else:
        status = "pass" if para_ok else "warning"
    report["checks"]["paragraph_lines"] = {
        "violations": len(para_violations),
        "max_allowed": PARAGRAPH_MAX_LINES,
        "details": para_violations[:5],
        "status": status,
        "note": f"v2.3 软化：每段 ≤ {PARAGRAPH_MAX_LINES} 行（v2.1 是 4）" if not para_ok and not args.strict else None,
    }
    report["summary"][status + ("ed" if status != "warning" else "s")] += 1

    # 9. 信息密度
    density_violations = count_info_density(sections)
    density_ok = len(density_violations) == 0
    report["checks"]["info_density"] = {
        "violations": len(density_violations),
        "details": density_violations[:5],
        "status": "pass" if density_ok else "warning",
    }
    if density_ok:
        report["summary"]["passed"] += 1
    else:
        report["summary"]["warnings"] += 1

    # ---- 输出 ----
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # ---- 控制台摘要 ----
    print(f"\n{'='*60}")
    print(f"质检报告：{args.input}")
    print(f"{'='*60}")
    for name, check in report["checks"].items():
        # v2.3 状态图标：纯 ASCII 字符，避免 Windows GBK 编码问题
        status_icon = {"pass": "[OK]", "fail": "[X]", "warning": "[!]"}[check["status"]]
        print(f"  {status_icon} {name}: {check['status']}")
    print(f"{'='*60}")
    print(f"  Pass: {report['summary']['passed']}  Fail: {report['summary']['failed']}  Warning: {report['summary']['warnings']}")
    print(f"  Report saved to: {args.output}")

    # 退出码
    # v2.3 soft 模式（默认）：退出码恒为 0，所有检查均为建议
    # v2.1 strict 模式（兼容）：任一 fail 退出码 1
    if args.strict and report["summary"]["failed"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
