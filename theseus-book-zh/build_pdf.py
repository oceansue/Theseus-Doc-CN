#!/usr/bin/env python3
"""将本目录下的中文翻译 Markdown 章节合并构建为单个 PDF。

依赖：pip install markdown weasyprint
      （weasyprint 需要 libpango/libcairo 等系统库；
        中文渲染需要系统安装 CJK 字体，如 fonts-noto-cjk）

用法：python3 build_pdf.py
输出：Theseus-OS-Book-中文版.pdf（生成于本目录，已被 .gitignore 排除）
"""
import glob
import os
import re
import sys

import markdown
from weasyprint import HTML

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(HERE, 'Theseus-OS-Book-中文版.pdf')
BASE = 'https://www.theseus-os.com/Theseus/book/'

MD_EXTENSIONS = ['fenced_code', 'tables', 'sane_lists', 'attr_list']

CSS = '''
@page {
    size: A4;
    margin: 20mm 16mm 18mm 16mm;
    @bottom-center { content: counter(page) " / " counter(pages);
                     font-size: 8.5pt; color: #888;
                     font-family: "Noto Sans CJK SC", sans-serif; }
}
@page cover { @bottom-center { content: none; } }
body { font-family: "Noto Sans CJK SC", "AR PL SungtiL GB", sans-serif;
       font-size: 10.5pt; line-height: 1.75; color: #1a1a1a; }
/* ---------- 封面 ---------- */
.cover { page: cover; text-align: center; padding-top: 60mm; }
.cover h1 { font-size: 30pt; border: none; margin: 0 0 6mm; }
.cover .sub { font-size: 14pt; color: #444; margin-bottom: 16mm; }
.cover .meta { font-size: 10pt; color: #666; line-height: 1.9; }
/* ---------- 目录 ---------- */
.toc { page-break-before: always; }
.toc h2 { font-size: 18pt; border: none; }
.toc ol { list-style: none; padding-left: 0; }
.toc li { margin: 2.2pt 0; font-size: 10pt; }
.toc a { text-decoration: none; color: #1a1a1a; }
.toc a::after { content: leader('.') target-counter(attr(href), page);
                color: #888; }
.toc .lvl2 { padding-left: 18pt; font-size: 9.5pt; color: #444; }
/* ---------- 正文 ---------- */
section.chapter { page-break-before: always; }
h1 { font-size: 19pt; color: #1a3c6e; border-bottom: 2px solid #1a3c6e;
     padding-bottom: 4pt; margin: 0 0 12pt; }
h2 { font-size: 14.5pt; color: #1a3c6e; margin: 16pt 0 8pt;
     border-bottom: 1px solid #ccd; padding-bottom: 3pt; }
h3 { font-size: 12pt; color: #2a4d7f; margin: 12pt 0 6pt; }
p { margin: 6pt 0; text-align: justify; }
a { color: #1155aa; text-decoration: none; word-break: break-all; }
ul, ol { padding-left: 20pt; } li { margin: 2.5pt 0; }
blockquote { margin: 8pt 0; padding: 5pt 12pt; border-left: 3px solid #b8c4d8;
             background: #f4f6fa; color: #333; }
blockquote p { margin: 3pt 0; }
img { max-width: 100%; display: block; margin: 8pt auto; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt;
       background: #f0f2f5; padding: 0.5pt 3pt; border-radius: 2pt; }
pre { background: #f6f8fa; border: 1px solid #e2e6ea; border-radius: 3pt;
      padding: 7pt 9pt; overflow: hidden; }
pre code { background: none; padding: 0; white-space: pre-wrap;
           word-wrap: break-word; }
table { border-collapse: collapse; margin: 8pt 0; width: 100%; }
th, td { border: 1px solid #c8c8c8; padding: 3.5pt 6pt; font-size: 9.5pt;
         text-align: left; }
th { background: #eef1f5; }
hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
'''


def chapter_files():
    files = []
    for p in sorted(glob.glob(os.path.join(HERE, '[0-9][0-9]-*.md'))):
        n = int(os.path.basename(p)[:2])
        files.append((n, p))
    return sorted(files)


def strip_html_comments(text):
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def build():
    chapters = chapter_files()
    if not chapters:
        sys.exit('未找到章节文件（NN-*.md）')

    body, toc = [], []
    for n, path in chapters:
        text = strip_html_comments(open(path, encoding='utf-8').read())
        html = markdown.markdown(text, extensions=MD_EXTENSIONS)
        title = text.splitlines()[0].lstrip('# ').strip()
        anchor = f'ch{n:02d}'
        # 每章一个 section，标题挂上锚点供目录跳转
        html = html.replace('<h1>', f'<h1 id="{anchor}">', 1)
        body.append(f'<section class="chapter">{html}</section>')
        toc.append(f'<li><a href="#{anchor}">{n:02d} · {title}</a></li>')
        # 目录二级条目：章内 h2
        for h2 in re.findall(r'<h2>(.*?)</h2>', html):
            h2_txt = re.sub(r'<[^>]+>', '', h2)
            toc.append(f'<li class="lvl2">{h2_txt}</li>')

    cover = '''
    <div class="cover">
      <h1>Theseus OS Book</h1>
      <div class="sub">中文版（简体中文翻译）</div>
      <div class="meta">
        原文：<a href="https://www.theseus-os.com/Theseus/book/print.html">
        https://www.theseus-os.com/Theseus/book/print.html</a><br/>
        仓库：https://github.com/theseus-os/Theseus<br/>
        一个用 Rust 从零编写的安全语言操作系统 —— 由无数“细胞”构成<br/>
        <br/>翻译日期：2026-09-21
      </div>
    </div>'''

    toc_html = ('<div class="toc"><h2>目录</h2><ol>'
                + ''.join(toc) + '</ol></div>')

    document = (f'<!DOCTYPE html><html lang="zh-CN"><head>'
                f'<meta charset="utf-8"><style>{CSS}</style></head>'
                f'<body>{cover}{toc_html}{"".join(body)}</body></html>')

    HTML(string=document, base_url=HERE).write_pdf(OUTPUT)
    size = os.path.getsize(OUTPUT) / 1024 / 1024
    print(f'已生成 {OUTPUT}（{len(chapters)} 章，{size:.1f} MB）')


if __name__ == '__main__':
    build()
