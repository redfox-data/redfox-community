#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf-image-text-extractor/scripts/pdf_text_extractor.py  v2.1.0（轻量版）

核心依赖仅 pymupdf 一个包，无需 pdfplumber / tesseract / rapidocr。

功能：
  1. 文字层提取：pymupdf get_text，保留标题与段落结构
  2. 表格结构化提取：pymupdf 内置 page.find_tables()，输出 Markdown 表格
  3. 扫描页处理：文字层为空的页面自动渲染为 PNG 图片，输出图片路径清单，
     交由 Agent 的 read_image（AI 视觉）识别 —— 无需任何本地 OCR 引擎

用法：
  python3 scripts/pdf_text_extractor.py document.pdf
  python3 scripts/pdf_text_extractor.py document.pdf --no-tables
  python3 scripts/pdf_text_extractor.py scan.pdf --scan-dir ./ocr_pages
"""

import sys
import json
import argparse
import contextlib
from pathlib import Path

# pymupdf 1.24+ 推荐 import pymupdf；旧版为 import fitz
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz  # noqa: F401
    except ImportError:
        print(json.dumps({
            'success': False,
            'error': '缺少依赖：pymupdf。请安装：pip install pymupdf',
            'text': '', 'page_count': 0,
            'tables': [], 'tables_markdown': '',
            'ocr_images': [], 'warnings': []
        }, ensure_ascii=False))
        sys.exit(1)


# ─────────────────────────────────────────────
# 表格：Markdown 转换 + find_tables 提取
# ─────────────────────────────────────────────

def _table_to_markdown(rows: list) -> str:
    """将二维列表转换为 Markdown 表格字符串"""
    if not rows:
        return ''

    cleaned = [
        [str(cell).replace('\n', ' ').strip() if cell is not None else ''
         for cell in row]
        for row in rows
    ]
    cleaned = [r for r in cleaned if any(c for c in r)]  # 过滤全空行
    if not cleaned:
        return ''

    max_cols = max(len(r) for r in cleaned)
    for r in cleaned:
        while len(r) < max_cols:
            r.append('')

    header, body = cleaned[0], cleaned[1:]
    lines = [
        '| ' + ' | '.join(header) + ' |',
        '| ' + ' | '.join(['---'] * max_cols) + ' |',
    ]
    lines += ['| ' + ' | '.join(row) + ' |' for row in body]
    return '\n'.join(lines)


def _extract_tables(doc) -> tuple:
    """
    使用 pymupdf 内置 find_tables() 提取全文档表格。
    返回 (tables_list, tables_markdown)
    """
    tables_list = []
    md_parts = []

    for page_idx, page in enumerate(doc):
        try:
            finder = page.find_tables()
            tables = getattr(finder, 'tables', [])
        except Exception:
            continue

        for t_idx, table in enumerate(tables):
            try:
                data = table.extract()
            except Exception:
                continue
            if not data or not any(any(c for c in row) for row in data):
                continue

            tables_list.append({
                'page': page_idx + 1,
                'table_index': t_idx + 1,
                'data': data,
            })
            md = _table_to_markdown(data)
            if md:
                md_parts.append(
                    f"#### 第 {page_idx + 1} 页 · 表格 {t_idx + 1}\n\n{md}"
                )

    return tables_list, '\n\n'.join(md_parts)


# ─────────────────────────────────────────────
# 扫描页渲染（供 Agent read_image 识别）
# ─────────────────────────────────────────────

def _render_page_to_png(page, out_path: str, dpi: int = 200) -> bool:
    """将 PDF 页面渲染为 PNG 图片，成功返回 True"""
    try:
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat)
        pix.save(out_path)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# 核心提取函数
# ─────────────────────────────────────────────

def extract_text_from_pdf(*args, **kwargs) -> dict:
    """
    对外接口。
    包一层 stdout 重定向：pymupdf 在处理时可能往 stdout 打印非 JSON 的提示
    （如 "Consider using the pymupdf_layout package ..."），会污染调用方的
    JSON / Markdown 输出。这里将提取阶段的 stdout 全部重定向到 stderr，
    确保调用方（Agent / batch_extractor）从 stdout 拿到的是干净结果。
    """
    with contextlib.redirect_stdout(sys.stderr):
        return _extract_impl(*args, **kwargs)


def _extract_impl(
    pdf_path: str,
    extract_tables: bool = True,
    render_scan: bool = True,
    scan_dir: str = None,
    scan_threshold: int = 20,
    dpi: int = 200,
) -> dict:
    """
    从 PDF 提取文字 + 表格，并将扫描页渲染为图片供 Agent 识别。

    参数:
        pdf_path       : PDF 文件路径
        extract_tables : 是否用 find_tables() 提取表格
        render_scan    : 是否将文字层为空的扫描页渲染为 PNG
        scan_dir       : 扫描页图片输出目录（默认 <pdf名>_ocr_pages/）
        scan_threshold : 判定为扫描页的文字字符数阈值（默认 < 20）
        dpi            : 扫描页渲染分辨率（默认 200，越高越清晰）

    返回 dict:
        success          bool
        text             str   — Markdown 格式正文（文字层）
        page_count       int
        tables           list  — 表格原始数据 [{'page','table_index','data'}]
        tables_markdown  str   — 所有表格的 Markdown 汇总
        ocr_images       list  — 需 Agent read_image 识别的图片 [{'page','image'}]
        warnings         list  — 非致命警告
        error            str
    """
    warnings = []
    result = {
        'success': False, 'text': '', 'page_count': 0,
        'tables': [], 'tables_markdown': '',
        'ocr_images': [], 'warnings': warnings, 'error': ''
    }

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        result['error'] = f'文件不存在：{pdf_path}'
        return result
    if pdf_file.suffix.lower() != '.pdf':
        result['error'] = f'文件格式错误：{pdf_file.suffix}，仅支持 PDF 格式'
        return result

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        result['error'] = f'无法打开 PDF（可能已加密或损坏）：{e}'
        return result

    page_count = len(doc)
    if page_count == 0:
        result['error'] = 'PDF 文件为空，无任何页面'
        return result

    # 扫描页图片输出目录
    if scan_dir:
        out_dir = Path(scan_dir)
    else:
        out_dir = pdf_file.parent / f'{pdf_file.stem}_ocr_pages'

    md_parts = []
    ocr_images = []

    for page_num in range(page_count):
        page = doc[page_num]
        if page_num > 0:
            md_parts.append('\n---\n')

        # ── 提取文字层（保留标题结构）──
        page_text = ''
        try:
            blocks = page.get_text("dict")["blocks"]
            text_lines = []
            for block in blocks:
                if block.get("type") != 0:
                    continue
                block_lines = []
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        txt = span["text"].strip()
                        if not txt:
                            continue
                        if span["size"] > 16:
                            if line_text:
                                block_lines.append(line_text)
                            is_bold = "bold" in span["font"].lower()
                            line_text = f"### {txt}" if is_bold else f"## {txt}"
                        else:
                            line_text += txt + " "
                    if line_text.strip():
                        block_lines.append(line_text.strip())
                if block_lines:
                    text_lines.append('\n'.join(block_lines))
            page_text = '\n\n'.join(text_lines).strip()
        except Exception:
            page_text = ''

        # ── 文字层稀少 → 判定为扫描页，渲染为图片 ──
        if len(page_text) < scan_threshold:
            if render_scan:
                out_dir.mkdir(parents=True, exist_ok=True)
                img_path = str((out_dir / f'{pdf_file.stem}_p{page_num + 1}.png').resolve())
                if _render_page_to_png(page, img_path, dpi=dpi):
                    ocr_images.append({'page': page_num + 1, 'image': img_path})
                else:
                    warnings.append(f'第 {page_num + 1} 页：疑似扫描页，但渲染图片失败')
            else:
                warnings.append(f'第 {page_num + 1} 页：疑似扫描页（文字层为空），已跳过渲染')
        elif page_text:
            md_parts.append(page_text)

    doc.close()

    full_text = '\n'.join(md_parts)
    while '\n\n\n' in full_text:
        full_text = full_text.replace('\n\n\n', '\n\n')

    # ── 表格提取 ──
    tables, tables_markdown = [], ''
    if extract_tables:
        try:
            doc2 = fitz.open(pdf_path)
            tables, tables_markdown = _extract_tables(doc2)
            doc2.close()
        except Exception as e:
            warnings.append(f'表格提取时发生错误：{e}')

    if ocr_images:
        pages_str = ', '.join(str(i['page']) for i in ocr_images)
        warnings.append(
            f'第 {pages_str} 页为扫描页，已渲染为图片，需用 read_image 识别（见 ocr_images 字段）'
        )

    result.update({
        'success': True,
        'text': full_text.strip(),
        'page_count': page_count,
        'tables': tables,
        'tables_markdown': tables_markdown,
        'ocr_images': ocr_images,
    })
    return result


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='PDF 文字提取工具 v2.1.0（轻量版，仅需 pymupdf）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例：\n'
            '  python3 scripts/pdf_text_extractor.py document.pdf\n'
            '  python3 scripts/pdf_text_extractor.py report.pdf --no-tables\n'
            '  python3 scripts/pdf_text_extractor.py scan.pdf --scan-dir ./ocr_pages\n'
        )
    )
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('--no-tables', action='store_true', help='跳过表格提取')
    parser.add_argument('--no-render', action='store_true',
                        help='不渲染扫描页为图片（仅提示哪些页是扫描页）')
    parser.add_argument('--scan-dir', default=None,
                        help='扫描页图片输出目录（默认 <pdf名>_ocr_pages/）')
    parser.add_argument('--threshold', type=int, default=20,
                        help='判定扫描页的文字字符数阈值（默认 20）')
    parser.add_argument('--dpi', type=int, default=200,
                        help='扫描页渲染分辨率（默认 200）')

    args = parser.parse_args()

    result = extract_text_from_pdf(
        pdf_path=args.pdf_path,
        extract_tables=not args.no_tables,
        render_scan=not args.no_render,
        scan_dir=args.scan_dir,
        scan_threshold=args.threshold,
        dpi=args.dpi,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result['success']:
        sys.exit(1)


if __name__ == '__main__':
    main()
