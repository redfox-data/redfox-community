#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf-image-text-extractor/scripts/batch_extractor.py  v2.1.0（轻量版）

批量文件文字提取脚本，核心依赖仅 pymupdf 一个包。
支持格式：
  - PDF：文字层提取 + 表格结构化提取（find_tables）+ 扫描页渲染为图片
  - 图片（PNG/JPG/JPEG/WebP/BMP/TIFF）：直接收集路径，交由 Agent read_image 识别

⚠️ 本脚本不做本地 OCR。所有需要视觉识别的内容（扫描页 + 图片）会汇总到
   返回结果的 ocr_images 清单中，由 Agent 逐张调用 read_image 完成识别。

用法：
  python3 scripts/batch_extractor.py ./documents/
  python3 scripts/batch_extractor.py ./documents/ -o result.md
  python3 scripts/batch_extractor.py ./documents/ --json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

PDF_EXTS   = {'.pdf'}
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif', '.gif'}
ALL_EXTS   = PDF_EXTS | IMAGE_EXTS


def scan_directory(dir_path: str) -> list:
    """扫描目录，返回所有支持文件的绝对路径（按文件名排序）"""
    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        return []
    return sorted(
        [str(f.resolve()) for f in p.iterdir()
         if f.is_file() and f.suffix.lower() in ALL_EXTS],
        key=lambda x: Path(x).name.lower()
    )


def batch_extract(
    dir_path: str,
    extract_tables: bool = True,
    render_scan: bool = True,
    scan_dir: str = None,
) -> dict:
    """
    批量提取目录下所有 PDF 与图片。

    返回 dict:
        success           bool
        dir_path          str
        total_files       int
        pdf_count         int
        image_count       int
        results           list  — 每个文件的处理结果
        ocr_images        list  — 需 Agent read_image 识别的图片汇总 [{'source','image'}]
        combined_markdown str   — 合并 Markdown 报告
        error             str
    """
    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from pdf_text_extractor import extract_text_from_pdf

    dirp = Path(dir_path)
    files = scan_directory(dir_path)
    if not files:
        return {
            'success': False, 'dir_path': dir_path, 'total_files': 0,
            'pdf_count': 0, 'image_count': 0, 'results': [],
            'ocr_images': [], 'combined_markdown': '',
            'error': (
                f'目录不存在或无支持的文件：{dir_path}\n'
                f'支持格式：PDF、{", ".join(sorted(IMAGE_EXTS))}'
            )
        }

    # 批量模式下扫描页图片统一输出目录
    out_scan_dir = scan_dir or str((dirp / '_ocr_pages').resolve())
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    results = []
    ocr_images_all = []
    body_parts = []

    for file_path in files:
        fname = Path(file_path).name
        ext   = Path(file_path).suffix.lower()
        print(f'  处理中：{fname} ...', file=sys.stderr)

        # ── PDF ──────────────────────────────
        if ext in PDF_EXTS:
            pdf_res = extract_text_from_pdf(
                pdf_path=file_path,
                extract_tables=extract_tables,
                render_scan=render_scan,
                scan_dir=out_scan_dir,
            )
            entry = {
                'file': fname, 'type': 'pdf',
                'success': pdf_res['success'],
                'text': pdf_res['text'],
                'page_count': pdf_res['page_count'],
                'tables_markdown': pdf_res.get('tables_markdown', ''),
                'ocr_images': pdf_res.get('ocr_images', []),
                'warnings': pdf_res.get('warnings', []),
                'error': pdf_res['error'],
            }
            # 扫描页图片汇入总清单
            for oi in pdf_res.get('ocr_images', []):
                ocr_images_all.append({'source': fname, 'page': oi['page'], 'image': oi['image']})

            body_parts.append(f'\n---\n\n## 📄 {fname}\n')
            if pdf_res['success']:
                body_parts.append(f'*{pdf_res["page_count"]} 页*')
                if pdf_res['text']:
                    body_parts.append('\n' + pdf_res['text'] + '\n')
                if pdf_res.get('ocr_images'):
                    pages = ', '.join(str(o['page']) for o in pdf_res['ocr_images'])
                    body_parts.append(f'\n> 🔍 第 {pages} 页为扫描页，已渲染为图片，待 read_image 识别\n')
                if pdf_res.get('tables_markdown'):
                    body_parts.append('\n### 📊 提取到的表格\n\n' + pdf_res['tables_markdown'] + '\n')
            else:
                body_parts.append(f'\n❌ 提取失败：{pdf_res["error"]}\n')

        # ── 图片 ─────────────────────────────
        elif ext in IMAGE_EXTS:
            abs_img = str(Path(file_path).resolve())
            entry = {
                'file': fname, 'type': 'image',
                'success': True, 'text': '',
                'ocr_images': [{'page': None, 'image': abs_img}],
                'warnings': [], 'error': '',
            }
            ocr_images_all.append({'source': fname, 'page': None, 'image': abs_img})
            body_parts.append(
                f'\n---\n\n## 🖼️ {fname}\n\n> 待 read_image 识别：`{abs_img}`\n'
            )

        results.append(entry)

    pdf_count   = sum(1 for r in results if r['type'] == 'pdf')
    image_count = sum(1 for r in results if r['type'] == 'image')
    ok_count    = sum(1 for r in results if r['success'])
    tbl_count   = sum(1 for r in results if r.get('tables_markdown'))

    header = [
        '# 批量文字提取报告\n',
        '| 项目 | 值 |',
        '|------|-----|',
        f'| 目录 | `{dir_path}` |',
        f'| 文件总数 | {len(files)}（PDF {pdf_count} / 图片 {image_count}） |',
        f'| 成功解析 | {ok_count} |',
        f'| 含表格 | {tbl_count} |',
        f'| 待 read_image 识别 | {len(ocr_images_all)} |',
        f'| 提取时间 | {now} |',
        '',
    ]
    if ocr_images_all:
        header.append('> ⚠️ 以下图片需由 Agent 逐张调用 read_image 识别（见 JSON 的 ocr_images 字段）\n')

    combined_md = '\n'.join(header + body_parts)

    return {
        'success': True, 'dir_path': dir_path,
        'total_files': len(files), 'pdf_count': pdf_count, 'image_count': image_count,
        'results': results, 'ocr_images': ocr_images_all,
        'combined_markdown': combined_md, 'error': '',
    }


def main():
    parser = argparse.ArgumentParser(
        description='批量文件文字提取工具 v2.1.0（轻量版，仅需 pymupdf）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例：\n'
            '  python3 scripts/batch_extractor.py ./documents/\n'
            '  python3 scripts/batch_extractor.py ./documents/ -o result.md\n'
            '  python3 scripts/batch_extractor.py ./documents/ --json\n'
        )
    )
    parser.add_argument('dir_path', help='要处理的目录路径')
    parser.add_argument('--no-tables', action='store_true', help='跳过 PDF 表格提取')
    parser.add_argument('--no-render', action='store_true', help='不渲染扫描页为图片')
    parser.add_argument('--scan-dir', default=None, help='扫描页图片输出目录（默认 <目录>/_ocr_pages/）')
    parser.add_argument('-o', '--output', metavar='FILE', help='将合并 Markdown 保存到指定文件')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出（含 ocr_images 清单）')

    args = parser.parse_args()
    print(f'📁 开始批量提取：{args.dir_path}', file=sys.stderr)

    result = batch_extract(
        dir_path=args.dir_path,
        extract_tables=not args.no_tables,
        render_scan=not args.no_render,
        scan_dir=args.scan_dir,
    )

    if not result['success']:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    if args.json:
        output = {k: v for k, v in result.items() if k != 'combined_markdown'}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result['combined_markdown'], encoding='utf-8')
        print(json.dumps({
            'success': True,
            'total_files': result['total_files'],
            'ocr_images': len(result['ocr_images']),
            'output_file': str(out_path.resolve()),
        }, ensure_ascii=False, indent=2))
        print(f'\n✅ Markdown 报告已保存至：{out_path.resolve()}', file=sys.stderr)
    else:
        print(result['combined_markdown'])

    print(
        f'\n✅ 完成：{result["total_files"]} 个文件（PDF {result["pdf_count"]} / 图片 {result["image_count"]}），'
        f'待识别图片 {len(result["ocr_images"])} 张',
        file=sys.stderr
    )


if __name__ == '__main__':
    main()
