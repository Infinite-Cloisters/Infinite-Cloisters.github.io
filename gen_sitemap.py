#!/usr/bin/env python3
"""生成 sitemap.xml，供 robots.txt 的 Sitemap: 指令引用。

从构建产物 docs/ 中扫描已渲染的 HTML 页面，转成 sitemaps.org 0.9 协议格式。
- 只收录正文页面；_sources/、_static/ 与 genindex/search 这类功能页不入库。
- lastmod 取该页面源文件的最后一次 git 提交日期，避免每次构建都刷新时间戳
  （频繁变动的 lastmod 会被搜索引擎判定为不可信信号）。
- 在仓库根目录运行： python gen_sitemap.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = "https://cad.qzz.io"

# 这些页面是站点功能页，不是内容，不放进 sitemap
SKIP_NAMES = {"genindex.html", "search.html", "404.html", "objects.inv"}
SKIP_PARTS = {"_sources", "_static", "_images"}

# 源文件目录（用于查 git 提交时间），conf.py 在 sphinx/ 下
SOURCE_DIR = ROOT / "sphinx"


def git_last_commit_date(path: Path) -> str | None:
    """返回文件最后一次提交的日期（YYYY-MM-DD），无记录则 None。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = out.stdout.strip()
    return value or None


def source_for(page: Path) -> Path | None:
    """把 docs/doc/x/y.html 映射回 sphinx/doc/x/y.{md,rst}。"""
    rel = page.relative_to(DOCS).with_suffix("")
    for suffix in (".md", ".rst"):
        candidate = SOURCE_DIR / rel.parent / (rel.name + suffix)
        if candidate.is_file():
            return candidate
    # 分区首页：docs/doc/x/index.html -> sphinx/doc/x/index.{rst,md}
    for suffix in (".rst", ".md"):
        candidate = SOURCE_DIR / rel.parent / ("index" + suffix)
        if candidate.is_file():
            return candidate
    return None


def page_url(page: Path) -> str:
    rel = page.relative_to(DOCS).as_posix()
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return f"{SITE}/{rel}"


def priority_for(page: Path) -> str:
    rel = page.relative_to(DOCS).as_posix()
    if rel == "index.html":
        return "1.0"
    if page.name == "index.html":
        return "0.8"
    return "0.6"


def collect_pages() -> list[Path]:
    pages = []
    for page in sorted(DOCS.rglob("*.html")):
        rel = page.relative_to(DOCS)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if page.name in SKIP_NAMES:
            continue
        pages.append(page)
    return pages


def main() -> int:
    if not DOCS.is_dir():
        print(f"error: {DOCS} not found", file=sys.stderr)
        return 1

    pages = collect_pages()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    today = date.today().isoformat()
    dated = 0
    for page in pages:
        src = source_for(page)
        lastmod = git_last_commit_date(src) if src else None
        if lastmod is None:
            lastmod = today
        else:
            dated += 1

        lines.append("  <url>")
        lines.append(f"    <loc>{escape(page_url(page))}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{priority_for(page)}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    lines.append("")

    targets = [DOCS / "sitemap.xml", SOURCE_DIR / "_extra" / "sitemap.xml"]
    body = "\n".join(lines)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        # newline='' 禁用 Windows 上的 CRLF 转换，保证产物为纯 LF
        with open(target, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        print(f"wrote {target.relative_to(ROOT)}")

    print(f"{len(pages)} pages ({dated} with git lastmod, rest defaulted to {today})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
