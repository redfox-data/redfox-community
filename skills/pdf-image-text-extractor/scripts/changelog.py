#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf-image-text-extractor/scripts/changelog.py

版本更新提示脚本
- 首次使用：展示完整新功能介绍
- 版本升级：展示变更日志
- 版本一致：静默退出（无输出）

版本记录文件：~/.pdf_image_extractor_version
用法：python3 scripts/changelog.py
"""

import sys
from pathlib import Path

CURRENT_VERSION = "2.1.0"
VERSION_FILE = Path.home() / ".pdf_image_extractor_version"

CHANGELOG = {
    "2.1.0": {
        "title": "PDF和图片文字提取 v2.1.0 — 零依赖轻量升级",
        "features": [
            "🔍  扫描版 PDF 识别（零额外依赖）\n"
            "     自动检测无文字页面，渲染为高清 PNG 交由 AI 视觉识别\n"
            "     无需安装 tesseract / rapidocr 等任何 OCR 引擎\n"
            "     中英文混排均可识别，准确率取决于 AI 视觉能力",

            "📊  表格结构化提取（零额外依赖）\n"
            "     用 pymupdf 内置 find_tables() 识别表格，输出 Markdown 格式\n"
            "     无需安装 pdfplumber\n"
            "     支持多页多表格，保留行列结构",

            "📁  批量处理模式\n"
            "     传入目录路径，一次性处理所有 PDF 和图片文件\n"
            "     支持格式：PDF / PNG / JPG / JPEG / WebP / BMP / TIFF\n"
            "     可输出合并 Markdown 文件或 JSON 结构化数据\n"
            "     用法：python3 scripts/batch_extractor.py <目录路径> [-o result.md]",

            "⚡  依赖大幅精简\n"
            "     全部功能仅需 pymupdf + requests 两个包\n"
            "     安装从「几百 MB + 系统级引擎」降为「一条 pip 命令秒装」",
        ],
        "deps": "pip install pymupdf requests",
    }
}


def get_stored_version() -> str:
    try:
        if VERSION_FILE.exists():
            return VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""


def save_version(version: str) -> None:
    try:
        VERSION_FILE.write_text(version, encoding="utf-8")
    except Exception:
        pass


def show_changelog() -> None:
    stored = get_stored_version()

    if stored == CURRENT_VERSION:
        # 版本一致，静默退出
        return

    entry = CHANGELOG.get(CURRENT_VERSION, {})
    title = entry.get("title", f"PDF和图片文字提取 v{CURRENT_VERSION}")
    features = entry.get("features", [])
    deps = entry.get("deps", "")

    if not stored:
        # 首次使用
        print(f"👋 欢迎使用 {title}！")
        print()
        print("本次更新新增以下功能：")
        print()
        for feat in features:
            print(f"  {feat}")
            print()
    else:
        # 版本升级
        print(f"🔄 已从 v{stored} 升级至 v{CURRENT_VERSION}")
        print()
        print("新增功能：")
        print()
        for feat in features:
            print(f"  {feat}")
            print()

    if deps:
        print("─" * 50)
        print(f"📦 必需依赖（一条命令装齐全部功能）：{deps}")

    print()
    save_version(CURRENT_VERSION)


if __name__ == "__main__":
    show_changelog()
