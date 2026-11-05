#!/usr/bin/env python3
"""知识库导图：检查底稿、写提炼记录、生成网页导图与 XMind

底稿 08_知识导图/知识库导图.md 是唯一手工维护的源文件，其余的事都由本脚本完成：

    python3 _scripts/build_mindmap.py check              # 检查底稿（不改任何文件）
    python3 _scripts/build_mindmap.py stamp 笔记路径…     # 刷新这几篇笔记的提炼记录
    python3 _scripts/build_mindmap.py stamp --all        # 刷新底稿里全部笔记的提炼记录
    python3 _scripts/build_mindmap.py build              # 检查通过后生成网页（.htm）与 XMind

检查与提炼规则见 08_知识导图/README.md。
只依赖 Python 标准库（兼容系统自带的 Python 3.9）；
生成网页时通过 npx 调用 markmap-cli，需要本机装有 Node.js。
"""

import argparse
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional

# ============================================================
# 一、常量
# ============================================================

# 知识库根目录 = 本脚本所在目录（_scripts）的上一级
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAP_DIR_NAME = '08_知识导图'      # 导图模块目录（它自己不算「被收录的模块」）
SOURCE_NAME = '知识库导图.md'     # 底稿
HTML_NAME = '知识库导图.htm'      # 网页导图。用 .htm：Quartz 发布时会去掉资源文件的 .html 扩展名
XMIND_NAME = '知识库导图.xmind'   # XMind 文件

# 线上 Quartz 站根地址，必须与 .github/workflows/deploy-pages.yml 里的 SITE_BASE_URL 一致
SITE_BASE_URL = 'https://woniuguaniu.github.io/ai-knowledge-base/'

# 固定 markmap-cli 版本，避免 npx 每次拉到新版本导致输出变化
MARKMAP_CLI = 'markmap-cli@0.18.12'

# npx 专用的 npm 缓存目录。
# 原因：本机默认缓存 ~/.npm-user-cache 里混进了 root 属主的目录，npx 会报 EACCES；
# 换一个只属于当前用户的目录就能绕开，也不影响别的项目。
NPM_CACHE_DIR = os.path.expanduser('~/.cache/kb-mindmap-npm')

NON_NOTE_NAMES = ('README.md', 'CLAUDE.md')   # 入口 / 导航文件，不算正文笔记
MODULE_DIR_PATTERN = re.compile(r'^\d\d_')    # 模块目录：两位数字 + 下划线，如 00_核心概念

MIN_POINTS = 2     # 每篇笔记的要点下限，少于它算失败
MAX_POINTS = 6     # 每篇笔记的要点上限，多于它算失败
WARN_WIDTH = 25    # 单条要点的显示宽度超过它就提醒

# 底稿里用到的几种语法
HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*)$')            # 标题行：# 根、## 模块 …
LIST_PATTERN = re.compile(r'^(\s*)[-*+]\s+(.*)$')              # 列表项：- 笔记、  - 要点
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')           # [文字](链接)
COMMENT_PATTERN = re.compile(r'<!--.*?-->')                    # 任意 HTML 注释
FOLD_PATTERN = re.compile(r'<!--\s*markmap:\s*fold\s*-->')     # markmap 的折叠标记
# 提炼记录，例如 <!-- 提炼 2026-11-04 #1a2b3c4d -->；开头的 \s* 让删除时连前面的空格一起删掉
STAMP_PATTERN = re.compile(r'\s*<!--\s*提炼\s+(\d{4}-\d{2}-\d{2})\s+#([0-9a-f]{8})\s*-->')


# ============================================================
# 二、数据结构
# ============================================================

@dataclass
class OutlineNode:
    """导图里的一个节点；根、模块、分组、笔记、要点都用它表示"""
    text: str                          # 显示文字（已去掉注释，链接只留文字部分）
    depth: int                         # 层级，根节点为 1
    lineNo: int                        # 在底稿中的行号（从 1 开始），报错时定位用
    href: Optional[str] = None         # 链接目标（底稿里的原样写法）；没有链接为 None
    folded: bool = False               # 是否带折叠标记
    stampDate: Optional[str] = None    # 提炼日期
    stampHash: Optional[str] = None    # 提炼时原文的内容指纹
    children: List['OutlineNode'] = field(default_factory=list)


@dataclass
class CheckReport:
    """检查结果：failures 非空时退出码为 1；warnings 只提醒"""
    failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    noteCount: int = 0       # 底稿里收录的笔记篇数
    totalNotes: int = 0      # 全库正文笔记篇数
    moduleCount: int = 0     # 已收录（至少收了一篇）的模块数


# ============================================================
# 三、通用小工具
# ============================================================

def normalizePath(path):
    """统一路径写法：NFC 编码 + 正斜杠

    macOS 文件系统可能给出 NFD 分解式的文字，而 git 和 Markdown 文本里是 NFC；
    不统一的话，同一个文件名会被当成两个不同的字符串。
    """
    return unicodedata.normalize('NFC', path).replace(os.sep, '/')


def stripMarkdown(text):
    """去掉加粗和行内代码标记（XMind 不渲染 Markdown；算宽度时它们也不占位置）"""
    return text.replace('**', '').replace('`', '')


def measureWidth(text):
    """按显示宽度计算字数：全角字符（汉字、全角标点）算 1，其余（英文、数字、半角符号）算 0.5"""
    width = 0.0
    for char in stripMarkdown(text):
        width += 1.0 if unicodedata.east_asian_width(char) in ('W', 'F') else 0.5
    return width


def computeFingerprint(filePath):
    """原文内容指纹：文件字节的 SHA-256 取前 8 位十六进制"""
    with open(filePath, 'rb') as fileHandle:
        return hashlib.sha256(fileHandle.read()).hexdigest()[:8]


def iterNodes(node):
    """深度优先遍历整棵树（含 node 自己）"""
    yield node
    for child in node.children:
        yield from iterNodes(child)


def countNodes(root):
    """整棵树的节点总数"""
    return sum(1 for _ in iterNodes(root))


# ============================================================
# 四、解析底稿
# ============================================================

def findBodyStart(lines):
    """返回正文开始的行下标：开头有 YAML front matter（两行 --- 包起来）就跳过它"""
    if lines and lines[0].strip() == '---':
        for index in range(1, len(lines)):
            if lines[index].strip() == '---':
                return index + 1
    return 0


def createNode(body, depth, lineNo):
    """把一行的正文部分解析成节点：识别折叠标记、提炼记录和链接"""
    stampMatch = STAMP_PATTERN.search(body)
    visibleText = COMMENT_PATTERN.sub('', body).strip()
    href = None
    linkMatch = LINK_PATTERN.search(visibleText)
    if linkMatch:
        href = linkMatch.group(2).strip()
        visibleText = LINK_PATTERN.sub(lambda match: match.group(1), visibleText)   # 链接只留文字
    return OutlineNode(
        text=visibleText.strip(),
        depth=depth,
        lineNo=lineNo,
        href=href,
        folded=bool(FOLD_PATTERN.search(body)),
        stampDate=stampMatch.group(1) if stampMatch else None,
        stampHash=stampMatch.group(2) if stampMatch else None,
    )


def parseOutline(text):
    """把底稿解析成节点树，返回 (根节点, 无法识别的行列表)

    层级规则与 markmap 一致：
    - 标题行：层级 = 井号个数（底稿只能有一个一级标题，它就是根）
    - 列表项：层级 = 上一个标题的层级 + 1 + 缩进级数（每 2 个空格算一级）
    空行和只有注释的行直接忽略；其余既不是标题也不是列表项的行记入「无法识别的行」，
    因为 markmap 会把它们画成节点、XMind 却不会，两个成品会对不上。
    """
    lines = text.split('\n')
    root = None
    stack = []          # 从根到「最近一个节点」的路径，用来给新节点找父节点
    headingDepth = 0    # 最近一个标题的层级
    strayLines = []
    for index in range(findBodyStart(lines), len(lines)):
        line = lines[index].rstrip()
        lineNo = index + 1
        headingMatch = HEADING_PATTERN.match(line)
        listMatch = LIST_PATTERN.match(line)
        if headingMatch:
            depth = len(headingMatch.group(1))
            headingDepth = depth
            body = headingMatch.group(2)
        elif listMatch:
            indentLevel = len(listMatch.group(1).replace('\t', '  ')) // 2
            depth = headingDepth + 1 + indentLevel
            body = listMatch.group(2)
        else:
            if COMMENT_PATTERN.sub('', line).strip():
                strayLines.append((lineNo, line.strip()))
            continue

        node = createNode(body, depth, lineNo)
        if root is None:
            if depth != 1:
                raise ValueError(f'第 {lineNo} 行：底稿的第一个节点必须是一级标题（# 开头）')
            root = node
            stack = [node]
            continue
        # 弹出层级不比新节点浅的节点，栈顶剩下的就是父节点
        while stack and stack[-1].depth >= depth:
            stack.pop()
        if not stack:
            raise ValueError(f'第 {lineNo} 行：出现了第二个一级标题，底稿只能有一个根节点')
        stack[-1].children.append(node)
        stack.append(node)

    if root is None:
        raise ValueError('底稿里没有一级标题（# 开头的根节点）')
    return root, strayLines


# ============================================================
# 五、收集笔记、解析链接、换算线上网址
# ============================================================

def collectNotes(rootDir):
    """收集各模块目录下的全部正文笔记，返回 {模块目录名: [相对知识库根目录的路径, …]}

    - 只看「两位数字_」开头的目录，并排除导图模块自己
    - 跳过 README.md、CLAUDE.md，以及以点开头的隐藏目录（如 .claude）
    """
    notesByModule = {}
    for entryName in sorted(os.listdir(rootDir)):
        moduleName = normalizePath(entryName)
        modulePath = os.path.join(rootDir, entryName)
        if not os.path.isdir(modulePath) or not MODULE_DIR_PATTERN.match(moduleName):
            continue
        if moduleName == MAP_DIR_NAME:
            continue
        notes = []
        for dirPath, dirNames, fileNames in os.walk(modulePath):
            dirNames[:] = sorted(name for name in dirNames if not name.startswith('.'))
            for fileName in sorted(fileNames):
                if fileName.endswith('.md') and fileName not in NON_NOTE_NAMES:
                    notes.append(normalizePath(os.path.relpath(os.path.join(dirPath, fileName), rootDir)))
        notesByModule[moduleName] = notes
    return notesByModule


def collectAllNotes(rootDir):
    """全库正文笔记的路径集合"""
    return {notePath for notes in collectNotes(rootDir).values() for notePath in notes}


def resolveLocalLink(href, mapDir, rootDir):
    """把底稿里的相对链接换算成「相对知识库根目录」的路径；外链与页内锚点返回 None

    例：底稿在 08_知识导图/ 下，链接 ../06_Agent工程/Claude%20Code%20实战速查.md
        → 06_Agent工程/Claude Code 实战速查.md
    """
    target = href.strip().strip('<>')
    if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
        return None
    target = urllib.parse.unquote(target.split('#')[0])
    absolutePath = os.path.normpath(os.path.join(mapDir, target))
    return normalizePath(os.path.relpath(absolutePath, rootDir))


def buildSiteUrl(relPath):
    """把笔记路径（相对知识库根目录）换成线上 Quartz 站对应页面的网址

    规则与 Quartz 源码 quartz/util/path.ts 的 sluggify 一致：
    去掉 .md；每段路径里空白换成 -，& 换成 -and-，% 换成 -percent，删除 ? 和 #。
    """
    slug = relPath[:-3] if relPath.endswith('.md') else relPath
    segments = []
    for segment in slug.split('/'):
        segment = re.sub(r'\s', '-', segment)
        segment = segment.replace('&', '-and-').replace('%', '-percent')
        segment = segment.replace('?', '').replace('#', '')
        segments.append(segment)
    return SITE_BASE_URL + urllib.parse.quote('/'.join(segments), safe='/')


# ============================================================
# 六、检查
# ============================================================

def checkOutline(root, rootDir, mapDir, strayLines=()):
    """对照磁盘上的笔记检查底稿，返回 CheckReport（判定规则见 08_知识导图/README.md）"""
    report = CheckReport()
    notesByModule = collectNotes(rootDir)
    allNotes = {notePath for notes in notesByModule.values() for notePath in notes}
    report.totalNotes = len(allNotes)

    # 1. 逐个检查链接：指向不存在的文件算失败；指向正文笔记的节点按路径归档
    noteNodes = {}
    for node in iterNodes(root):
        if node.href is None:
            continue
        relPath = resolveLocalLink(node.href, mapDir, rootDir)
        if relPath is None:
            continue
        if not os.path.isfile(os.path.join(rootDir, relPath)):
            report.failures.append(f'[断链] 第 {node.lineNo} 行：{node.href}')
            continue
        if relPath in allNotes:
            noteNodes.setdefault(relPath, []).append(node)
    report.noteCount = len(noteNodes)

    # 2. 同一篇笔记出现多次
    for relPath, nodes in sorted(noteNodes.items()):
        if len(nodes) > 1:
            lineText = '、'.join(str(node.lineNo) for node in nodes)
            report.failures.append(f'[重复] {relPath} 出现了 {len(nodes)} 次（第 {lineText} 行）')

    # 3. 覆盖：整个模块都没收录只提醒（铺开阶段的正常状态）；收录了一部分，漏掉的算失败
    for moduleName, notes in notesByModule.items():
        if not any(notePath in noteNodes for notePath in notes):
            report.warnings.append(f'[未收录模块] {moduleName}（{len(notes)} 篇）')
            continue
        report.moduleCount += 1
        for notePath in notes:
            if notePath not in noteNodes:
                report.failures.append(f'[漏收] {notePath}')

    # 4. 每篇笔记的要点数量、要点长度、提炼记录
    for relPath, nodes in sorted(noteNodes.items()):
        node = nodes[0]
        pointCount = len(node.children)
        if not MIN_POINTS <= pointCount <= MAX_POINTS:
            report.failures.append(f'[要点数量] {relPath}：{pointCount} 条（应为 {MIN_POINTS}–{MAX_POINTS} 条）')
        for point in node.children:
            width = measureWidth(point.text)
            if width > WARN_WIDTH:
                report.warnings.append(f'[要点超长] 第 {point.lineNo} 行（{width:g} 字）：{point.text}')
        if node.stampHash is None:
            report.warnings.append(f'[缺提炼记录] {relPath}')
        elif node.stampHash != computeFingerprint(os.path.join(rootDir, relPath)):
            report.warnings.append(f'[原文已改] {relPath}（提炼于 {node.stampDate}）')

    # 5. 既不是标题也不是列表项的行
    for lineNo, lineText in strayLines:
        report.failures.append(f'[格式] 第 {lineNo} 行既不是标题也不是列表项：{lineText[:40]}')
    return report


def printReport(report):
    """把检查结果打印成人能读的样子"""
    print('==== 底稿检查')
    print(f'底稿收录笔记 {report.noteCount} 篇 / 全库正文笔记 {report.totalNotes} 篇 / '
          f'已收录模块 {report.moduleCount} 个')
    print(f'失败 {len(report.failures)} 项，提醒 {len(report.warnings)} 项')
    for item in report.failures:
        print(f'  失败 {item}')
    for item in report.warnings:
        print(f'  提醒 {item}')


# ============================================================
# 七、写提炼记录
# ============================================================

def stampNotes(sourceText, targetPaths, mapDir, rootDir, today):
    """给笔记节点行写入新的提炼记录（日期 + 原文指纹），返回 (新底稿文本, 实际更新的路径集合)

    targetPaths 为 None 时更新底稿里的全部笔记，否则只更新集合里的路径。
    只处理指向正文笔记的列表行；旧记录会先被删掉，所以重复执行结果不变。
    """
    allNotes = collectAllNotes(rootDir)
    lines = sourceText.split('\n')
    updatedPaths = set()
    for index, line in enumerate(lines):
        if not LIST_PATTERN.match(line):
            continue
        linkMatch = LINK_PATTERN.search(COMMENT_PATTERN.sub('', line))
        if not linkMatch:
            continue
        relPath = resolveLocalLink(linkMatch.group(2), mapDir, rootDir)
        if relPath not in allNotes:
            continue
        if targetPaths is not None and relPath not in targetPaths:
            continue
        stampText = f'<!-- 提炼 {today} #{computeFingerprint(os.path.join(rootDir, relPath))} -->'
        lines[index] = STAMP_PATTERN.sub('', line).rstrip() + ' ' + stampText
        updatedPaths.add(relPath)
    return '\n'.join(lines), updatedPaths


# ============================================================
# 八、生成网页导图（markmap）
# ============================================================

def renderMarkmapSource(sourceText, mapDir, rootDir):
    """生成交给 markmap 的 Markdown

    - 本地笔记链接换成线上 Quartz 页面的网址，并且在新标签页打开
    - 去掉提炼记录（只对检查有用，不必进网页）
    - front matter 和折叠标记原样保留
    """
    def replaceLink(match):
        title, href = match.group(1), match.group(2)
        relPath = resolveLocalLink(href, mapDir, rootDir)
        url = buildSiteUrl(relPath) if relPath else href.strip().strip('<>')
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(title)}</a>'

    outputLines = []
    for line in sourceText.split('\n'):
        line = STAMP_PATTERN.sub('', line).rstrip()
        outputLines.append(LINK_PATTERN.sub(replaceLink, line))
    return '\n'.join(outputLines)


def setHtmlTitle(htmlText, title):
    """把 markmap 默认的网页标题（Markmap）换成导图根节点的文字"""
    return re.sub(r'<title>.*?</title>', lambda match: f'<title>{html.escape(title)}</title>',
                  htmlText, count=1, flags=re.S)


def runMarkmap(markdownText, outputPath):
    """调用 markmap-cli，把 Markdown 渲染成离线可用的单文件网页"""
    os.makedirs(NPM_CACHE_DIR, exist_ok=True)
    environment = dict(os.environ, npm_config_cache=NPM_CACHE_DIR, npm_config_prefer_offline='true')
    with tempfile.TemporaryDirectory() as tempDir:
        tempSource = os.path.join(tempDir, SOURCE_NAME)
        with open(tempSource, 'w', encoding='utf-8') as fileHandle:
            fileHandle.write(markdownText)
        command = ['npx', '--yes', MARKMAP_CLI, tempSource, '--offline', '--no-open', '-o', outputPath]
        result = subprocess.run(command, capture_output=True, text=True, env=environment, cwd=tempDir)
    if result.returncode != 0:
        raise RuntimeError('markmap-cli 运行失败：\n' + result.stdout + result.stderr)


def findExternalAssets(htmlText):
    """找出网页里引用的外部脚本 / 样式地址（离线版应该一个都没有）"""
    pattern = re.compile(r'<(?:script|link)\b[^>]*?\b(?:src|href)="(https?://[^"]+)"', re.IGNORECASE)
    return pattern.findall(htmlText)


# ============================================================
# 九、生成 XMind
# ============================================================

def buildXmindTopic(node, mapDir, rootDir, counter):
    """把一个节点（连同全部子节点）转成 XMind 的 topic 字典；counter[0] 用来给主题编号"""
    counter[0] += 1
    topic = {'id': f'topic-{counter[0]:05d}', 'class': 'topic', 'title': stripMarkdown(node.text)}
    if node.href:
        relPath = resolveLocalLink(node.href, mapDir, rootDir)
        topic['href'] = buildSiteUrl(relPath) if relPath else node.href.strip().strip('<>')
    if node.folded and node.children:
        topic['branch'] = 'folded'      # XMind 里默认收起
    if node.children:
        topic['children'] = {'attached': [buildXmindTopic(child, mapDir, rootDir, counter)
                                          for child in node.children]}
    return topic


def writeXmind(root, outputPath, mapDir, rootDir):
    """写出 .xmind 文件（Xmind 2020 及以后的格式：zip 包里放 content.json、metadata.json、manifest.json）"""
    rootTopic = buildXmindTopic(root, mapDir, rootDir, [0])
    rootTopic['structureClass'] = 'org.xmind.ui.map.unbalanced'    # 「思维导图」结构
    files = {
        'content.json': [{'id': 'sheet-00001', 'class': 'sheet', 'title': rootTopic['title'],
                          'rootTopic': rootTopic}],
        'metadata.json': {'creator': {'name': 'build_mindmap.py', 'version': '1.0'}},
        'manifest.json': {'file-entries': {'content.json': {}, 'metadata.json': {}}},
    }
    with zipfile.ZipFile(outputPath, 'w') as archive:
        for fileName, data in files.items():
            # 固定时间戳：内容没变时，重新生成的文件字节也不变，git 不会误报改动
            info = zipfile.ZipInfo(fileName, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, json.dumps(data, ensure_ascii=False, indent=1))


def countXmindTopics(xmindPath):
    """重新打开生成好的 .xmind，数一数里面的主题个数（独立核对写出的文件）"""
    with zipfile.ZipFile(xmindPath) as archive:
        sheets = json.loads(archive.read('content.json').decode('utf-8'))

    def countTopic(topic):
        return 1 + sum(countTopic(child) for child in topic.get('children', {}).get('attached', []))

    return sum(countTopic(sheet['rootTopic']) for sheet in sheets)


# ============================================================
# 十、命令行入口
# ============================================================

def loadSource(mapDir):
    """读入底稿原文"""
    with open(os.path.join(mapDir, SOURCE_NAME), encoding='utf-8') as fileHandle:
        return fileHandle.read()


def runCheck(rootDir, mapDir):
    """check 命令：打印检查结果，返回 (退出码, 根节点, 底稿原文)"""
    sourceText = loadSource(mapDir)
    root, strayLines = parseOutline(sourceText)
    report = checkOutline(root, rootDir, mapDir, strayLines)
    printReport(report)
    return (1 if report.failures else 0), root, sourceText


def runStamp(rootDir, mapDir, paths, stampAll):
    """stamp 命令：刷新指定笔记（或全部笔记）的提炼记录，返回退出码"""
    if not stampAll and not paths:
        print('请给出笔记路径，或者用 --all 刷新全部笔记')
        return 1
    targetPaths = None
    if not stampAll:
        targetPaths = {normalizePath(os.path.relpath(os.path.abspath(path), rootDir)) for path in paths}
    today = datetime.date.today().isoformat()
    newText, updatedPaths = stampNotes(loadSource(mapDir), targetPaths, mapDir, rootDir, today)
    with open(os.path.join(mapDir, SOURCE_NAME), 'w', encoding='utf-8') as fileHandle:
        fileHandle.write(newText)
    print(f'已刷新提炼记录 {len(updatedPaths)} 篇（日期 {today}）')
    missingPaths = sorted(targetPaths - updatedPaths) if targetPaths is not None else []
    for path in missingPaths:
        print(f'  底稿里没找到：{path}')
    return 1 if missingPaths else 0


def runBuild(rootDir, mapDir):
    """build 命令：检查通过后生成网页与 XMind，再自检两项（网页无外部资源、XMind 主题数 = 底稿节点数）"""
    exitCode, root, sourceText = runCheck(rootDir, mapDir)
    if exitCode != 0:
        print('检查有失败项，已停止生成。')
        return exitCode

    htmlPath = os.path.join(mapDir, HTML_NAME)
    runMarkmap(renderMarkmapSource(sourceText, mapDir, rootDir), htmlPath)
    with open(htmlPath, encoding='utf-8') as fileHandle:
        htmlText = setHtmlTitle(fileHandle.read(), root.text)
    with open(htmlPath, 'w', encoding='utf-8') as fileHandle:
        fileHandle.write(htmlText)
    externalAssets = findExternalAssets(htmlText)

    xmindPath = os.path.join(mapDir, XMIND_NAME)
    writeXmind(root, xmindPath, mapDir, rootDir)
    topicCount = countXmindTopics(xmindPath)
    nodeCount = countNodes(root)

    print('==== 生成结果')
    print(f'{HTML_NAME}：{os.path.getsize(htmlPath) // 1024} KB，外部资源引用 {len(externalAssets)} 处')
    for url in externalAssets:
        print(f'  外部资源：{url}')
    print(f'{XMIND_NAME}：{os.path.getsize(xmindPath) // 1024} KB，'
          f'主题 {topicCount} 个，底稿节点 {nodeCount} 个')
    return 0 if not externalAssets and topicCount == nodeCount else 1


def main(argv=None):
    """命令行入口：解析子命令并分发"""
    parser = argparse.ArgumentParser(description='知识库导图：检查底稿、写提炼记录、生成网页导图与 XMind')
    subParsers = parser.add_subparsers(dest='command', required=True)
    subParsers.add_parser('check', help='只检查底稿，不改任何文件')
    stampParser = subParsers.add_parser('stamp', help='刷新笔记的提炼记录')
    stampParser.add_argument('paths', nargs='*', help='笔记路径（相对当前目录，或绝对路径）')
    stampParser.add_argument('--all', dest='stampAll', action='store_true', help='刷新底稿里的全部笔记')
    subParsers.add_parser('build', help='检查通过后生成网页（.htm）与 XMind')
    args = parser.parse_args(argv)

    mapDir = os.path.join(ROOT_DIR, MAP_DIR_NAME)
    if not os.path.isfile(os.path.join(mapDir, SOURCE_NAME)):
        print(f'底稿不存在：{MAP_DIR_NAME}/{SOURCE_NAME}')
        return 1
    if args.command == 'check':
        return runCheck(ROOT_DIR, mapDir)[0]
    if args.command == 'stamp':
        return runStamp(ROOT_DIR, mapDir, args.paths, args.stampAll)
    return runBuild(ROOT_DIR, mapDir)


if __name__ == '__main__':
    sys.exit(main())
