#!/usr/bin/env python3
"""知识库体检脚本

把历次人工排查固化成可重复执行的检查，避免每次都临时写一遍。

用法：
    python3 _scripts/kb_check.py            # 全部检查
    python3 _scripts/kb_check.py --quiet    # 只输出有问题的项

检查项：
    1. 断链        —— [文字](路径) 指向的本地文件是否存在
    2. 孤儿笔记    —— 没有任何其他笔记链接进来的笔记
    3. 死胡同笔记  —— 自己不链接任何其他笔记的笔记
    4. 元数据覆盖  —— 「最后更新」与「来源与局限性」章节的覆盖率
    5. 字符损坏    —— UTF-8 替换符 U+FFFD（写入过程被截断的痕迹）
    6. 索引一致性  —— 根 README 与各模块 README 是否覆盖了全部笔记
    7. 重复章节    —— 同一篇里出现多个「来源/局限」二级标题

退出码：发现「必须修」级别的问题（断链 / 字符损坏 / 索引遗漏）时返回 1，否则 0。
"""

import os
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter

# 知识库根目录 = 本脚本的上一级
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 扫描时要跳过的目录（不属于笔记正文）
SKIP_DIRS = ('.git', '.obsidian', '.playwright-mcp', '.claude', '_templates', '_scripts')

# 这些文件是入口/导航，不参与「孤儿」「死胡同」统计
ENTRY_FILES = ('README.md', 'index.md', 'CHANGELOG.md', 'ROADMAP.md', 'CLAUDE.md')

# 02 子项目与概念扫盲有自己的索引体系，不参与根索引覆盖检查
SUBPROJECT_MARKS = ('02_提示词工程', '概念扫盲')


def norm(s):
    """macOS 文件系统返回 NFD 分解式中文，git 与文本里是 NFC，比较前必须归一"""
    return unicodedata.normalize('NFC', s)


def collect_markdown():
    """收集知识库里所有参与检查的 .md 文件（相对 ROOT 的规范化路径）"""
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if any(skip in dirpath for skip in SKIP_DIRS):
            continue
        for name in filenames:
            if name.endswith('.md'):
                full = os.path.join(dirpath, name)
                found.append(os.path.relpath(full, ROOT))
    return sorted(found)


def read(rel_path):
    """读取笔记内容，读不出来时返回空串而不是抛异常"""
    try:
        with open(os.path.join(ROOT, rel_path), encoding='utf-8', errors='ignore') as fh:
            return fh.read()
    except OSError:
        return ''


def strip_code(text):
    """剥掉围栏代码块与行内代码

    必须先剥再解析链接：Python 的 `self.experts[idx](x)`、注释里写的
    `[text](path#anchor)` 都会被 Markdown 链接正则误判成断链。
    """
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'~~~.*?~~~', '', text, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', text)


def local_links(rel_path, text):
    """解析一篇笔记里的本地 Markdown 链接，返回 (原始 URL, 解析后的相对路径)"""
    results = []
    for _, url in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', strip_code(text)):
        if url.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        path = urllib.parse.unquote(url.split('#')[0])
        if not path:
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(rel_path), path))
        results.append((url, target))
    return results


def is_note(rel_path):
    """是否算「一篇笔记」（排除入口文件与模块 README）"""
    return os.path.basename(rel_path) not in ENTRY_FILES


def main():
    quiet = '--quiet' in sys.argv
    files = collect_markdown()
    texts = {f: read(f) for f in files}
    exists = {norm(f) for f in files}

    problems_must = 0   # 必须修
    problems_soft = 0   # 建议看

    def section(title):
        if not quiet:
            print(f"\n{'=' * 4} {title}")

    # ---------- 1. 断链 ----------
    section('1. 断链检查')
    broken = []
    link_total = 0
    for f in files:
        for url, target in local_links(f, texts[f]):
            link_total += 1
            # 目标可能是目录（如 02_提示词工程/），也算有效
            if not os.path.exists(os.path.join(ROOT, target)):
                broken.append((f, url))
    print(f"本地链接 {link_total} 条，断链 {len(broken)} 条")
    for f, url in broken:
        print(f"  [断链] {f} -> {url}")
    problems_must += len(broken)

    # ---------- 2/3. 孤儿与死胡同 ----------
    section('2/3. 孤儿与死胡同')
    inbound, outbound = Counter(), Counter()
    for f in files:
        for _, target in local_links(f, texts[f]):
            tn = norm(target)
            if tn in exists and tn != norm(f):
                inbound[tn] += 1
                outbound[norm(f)] += 1

    def countable(rel_path):
        return is_note(rel_path) and not any(m in rel_path for m in SUBPROJECT_MARKS)

    orphans = [f for f in files if countable(f) and inbound[norm(f)] == 0]
    deadends = [f for f in files if countable(f) and outbound[norm(f)] == 0]
    print(f"孤儿笔记（无入链）{len(orphans)} 篇 / 死胡同笔记（无出链）{len(deadends)} 篇")
    for f in orphans:
        print(f"  [孤儿] {f}")
    for f in deadends:
        print(f"  [死胡同] {f}")
    problems_soft += len(orphans) + len(deadends)

    # ---------- 4. 元数据覆盖 ----------
    section('4. 元数据覆盖率')
    notes = [f for f in files if is_note(f) and re.match(r'^0\d_', f)
             and '概念扫盲' not in f]
    no_date, no_source = [], []
    for f in notes:
        tail = ''.join(texts[f].splitlines(keepends=True)[-8:])
        if not re.search(r'最后更新|探索日期|更新日期', tail):
            no_date.append(f)
        heads = re.findall(r'^#{1,4}\s*(.+)$', texts[f], re.M)
        if not any(('来源' in h or '局限' in h) for h in heads):
            no_source.append(f)
    print(f"笔记 {len(notes)} 篇：缺「最后更新」{len(no_date)} 篇，"
          f"缺「来源与局限性」{len(no_source)} 篇")
    for f in no_date:
        print(f"  [缺日期] {f}")
    for f in no_source:
        print(f"  [缺来源] {f}")
    problems_soft += len(no_date) + len(no_source)

    # ---------- 5. 字符损坏 ----------
    section('5. UTF-8 字符损坏')
    corrupt = [(f, i + 1) for f in files
               for i, line in enumerate(texts[f].splitlines()) if '�' in line]
    print(f"含替换符 U+FFFD 的位置：{len(corrupt)} 处")
    for f, line_no in corrupt:
        print(f"  [损坏] {f}:{line_no}")
    problems_must += len(corrupt)

    # ---------- 6. 索引一致性 ----------
    section('6. 索引一致性')
    readme = texts.get('README.md', '')
    indexed = {norm(urllib.parse.unquote(u))
               for _, u in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', strip_code(readme))}
    # 02 子项目有自己的索引体系，根 README 只需指向它的 README，不逐篇列出
    missing_root = [f for f in notes
                    if norm(f) not in indexed
                    and not any(m in f for m in SUBPROJECT_MARKS)]
    print(f"未被根 README 索引覆盖的笔记：{len(missing_root)} 篇")
    for f in missing_root:
        print(f"  [未索引] {f}")
    problems_must += len(missing_root)

    # 各模块 README 是否覆盖本模块笔记
    for module in sorted(d for d in os.listdir(ROOT) if re.match(r'^0\d_', d)):
        mod_readme = os.path.join(module, 'README.md')
        if mod_readme not in texts:
            print(f"  [无模块 README] {module}/")
            problems_soft += 1
            continue
        links_in = {urllib.parse.unquote(u)
                    for _, u in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', texts[mod_readme])}
        own = [n for n in os.listdir(os.path.join(ROOT, module))
               if n.endswith('.md') and n not in ENTRY_FILES]
        miss = [n for n in own if n not in links_in]
        if miss:
            print(f"  [模块 README 遗漏] {module}: {', '.join(miss)}")
            problems_soft += len(miss)

    # ---------- 7. 重复章节 ----------
    section('7. 重复的「来源/局限」二级标题')
    dupes = []
    for f in files:
        # 只看二级标题：^## 后面不能再跟 #，否则会把 ### 也算进来
        h2 = re.findall(r'^##[^#]\s*(.+)$', texts[f], re.M)
        hit = [h for h in h2 if ('来源' in h or '局限' in h)]
        if len(hit) > 1:
            dupes.append((f, hit))
    print(f"存在重复章节的笔记：{len(dupes)} 篇")
    for f, hit in dupes:
        print(f"  [重复] {f}: {hit}")
    problems_must += len(dupes)

    # ---------- 汇总 ----------
    print(f"\n{'=' * 4} 汇总")
    print(f"必须修：{problems_must} 项（断链 / 字符损坏 / 索引遗漏 / 重复章节）")
    print(f"建议看：{problems_soft} 项（孤儿 / 死胡同 / 元数据缺口 / 模块 README 遗漏）")
    return 1 if problems_must else 0


if __name__ == '__main__':
    sys.exit(main())
