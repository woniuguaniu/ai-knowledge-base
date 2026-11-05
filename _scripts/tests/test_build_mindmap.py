#!/usr/bin/env python3
"""build_mindmap.py 的单元测试

运行方法（在知识库根目录执行）：
    python3 -m unittest discover -s _scripts/tests -v

每个测试都在临时目录里搭一个「迷你知识库」，不会碰真实笔记。
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile

# 让测试能 import 上一级目录（_scripts）里的 build_mindmap.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build_mindmap as bm  # noqa: E402


def writeFile(filePath, content):
    """写一个 UTF-8 文本文件，目录不存在就先建"""
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    with open(filePath, 'w', encoding='utf-8') as fileHandle:
        fileHandle.write(content)


class MiniKnowledgeBaseCase(unittest.TestCase):
    """测试基类：搭一个迷你知识库

    00_甲模块/   README.md（不算笔记）、笔记一.md、笔记 二.md（文件名带空格）、
                子目录/笔记三.md、.claude/隐藏.md（隐藏目录，不算笔记）
    01_乙模块/   笔记四.md
    08_知识导图/ README.md（导图模块自己，不参与收录统计）
    """

    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.rootDir = self.tempDir.name
        self.mapDir = os.path.join(self.rootDir, bm.MAP_DIR_NAME)
        writeFile(os.path.join(self.rootDir, '00_甲模块', 'README.md'), '# 甲模块\n')
        writeFile(os.path.join(self.rootDir, '00_甲模块', '笔记一.md'), '# 笔记一\n正文一\n')
        writeFile(os.path.join(self.rootDir, '00_甲模块', '笔记 二.md'), '# 笔记二\n正文二\n')
        writeFile(os.path.join(self.rootDir, '00_甲模块', '子目录', '笔记三.md'), '# 笔记三\n')
        writeFile(os.path.join(self.rootDir, '00_甲模块', '.claude', '隐藏.md'), '不算笔记\n')
        writeFile(os.path.join(self.rootDir, '01_乙模块', '笔记四.md'), '# 笔记四\n')
        writeFile(os.path.join(self.mapDir, 'README.md'), '# 导图\n')

    def tearDown(self):
        self.tempDir.cleanup()

    def fingerprintOf(self, relPath):
        """迷你知识库里某篇笔记当前的内容指纹"""
        return bm.computeFingerprint(os.path.join(self.rootDir, relPath))

    def makeNoteBlock(self, title, href, points, stampHash=None):
        """生成一篇笔记在底稿里的几行：笔记节点行 + 缩进的要点行"""
        stampText = f' <!-- 提炼 2026-11-04 #{stampHash} -->' if stampHash else ''
        lines = [f'- [{title}]({href}) <!-- markmap: fold -->{stampText}']
        lines += [f'  - {point}' for point in points]
        return lines

    def buildOutline(self, noteLines):
        """把笔记行拼成一份最小底稿：front matter + 根 + 甲模块"""
        header = ['---', 'title: 测试导图', '---', '', '# 测试导图', '', '## 00 甲模块（3 篇）', '']
        return '\n'.join(header + noteLines) + '\n'

    def makeCompleteOutline(self, firstNotePoints=('要点甲', '要点乙')):
        """甲模块 3 篇全部收录、提炼记录都是最新的底稿"""
        lines = self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', list(firstNotePoints),
                                   self.fingerprintOf('00_甲模块/笔记一.md'))
        lines += self.makeNoteBlock('笔记二', '../00_甲模块/笔记%20二.md', ['要点丙', '要点丁'],
                                    self.fingerprintOf('00_甲模块/笔记 二.md'))
        lines += self.makeNoteBlock('笔记三', '../00_甲模块/子目录/笔记三.md', ['要点戊', '要点己'],
                                    self.fingerprintOf('00_甲模块/子目录/笔记三.md'))
        return self.buildOutline(lines)

    def runCheck(self, outlineText):
        """解析并检查一份底稿，返回 CheckReport"""
        root, strayLines = bm.parseOutline(outlineText)
        return bm.checkOutline(root, self.rootDir, self.mapDir, strayLines)


class TestMeasureWidth(unittest.TestCase):

    def testCjkCountsOneOthersCountHalf(self):
        # 预训练 = 3，两个空格 = 1，箭头 = 0.5，SFT = 1.5
        self.assertEqual(bm.measureWidth('预训练 → SFT'), 6.0)

    def testIgnoresBoldAndCodeMarks(self):
        # 去掉标记后只剩「加粗ab」：2 + 1
        self.assertEqual(bm.measureWidth('**加粗**`ab`'), 3.0)


class TestParseOutline(unittest.TestCase):

    def testParsesHierarchyLinkFoldAndStamp(self):
        text = '\n'.join([
            '---', 'title: 测试', 'markmap:', '  colorFreezeLevel: 2', '---', '',
            '# 根', '',
            '## 模块甲', '',
            '### 分组一', '',
            '- [笔记一](../00_甲模块/笔记一.md) <!-- markmap: fold --> <!-- 提炼 2026-11-04 #1a2b3c4d -->',
            '  - 要点 A',
            '  - 要点 B',
            '',
        ])
        root, strayLines = bm.parseOutline(text)
        self.assertEqual(strayLines, [])
        self.assertEqual(root.text, '根')
        group = root.children[0].children[0]
        self.assertEqual((root.children[0].text, group.text), ('模块甲', '分组一'))
        note = group.children[0]
        self.assertEqual(note.text, '笔记一')
        self.assertEqual(note.href, '../00_甲模块/笔记一.md')
        self.assertTrue(note.folded)
        self.assertEqual((note.stampDate, note.stampHash), ('2026-11-04', '1a2b3c4d'))
        self.assertEqual(note.lineNo, 13)
        self.assertEqual([point.text for point in note.children], ['要点 A', '要点 B'])

    def testCollectsStrayLines(self):
        root, strayLines = bm.parseOutline('# 根\n\n这是一段普通文字\n\n- 列表项\n')
        self.assertEqual(strayLines, [(3, '这是一段普通文字')])
        self.assertEqual(root.children[0].text, '列表项')

    def testRejectsSecondRoot(self):
        with self.assertRaises(ValueError):
            bm.parseOutline('# 根一\n\n# 根二\n')


class TestBuildSiteUrl(unittest.TestCase):

    def testSpacesBecomeDashesAndChineseIsEncoded(self):
        self.assertEqual(
            bm.buildSiteUrl('06_Agent工程/Claude Code 实战速查.md'),
            'https://woniuguaniu.github.io/ai-knowledge-base/'
            '06_Agent%E5%B7%A5%E7%A8%8B/Claude-Code-%E5%AE%9E%E6%88%98%E9%80%9F%E6%9F%A5')

    def testFollowsQuartzSpecialCharacterRules(self):
        self.assertEqual(bm.buildSiteUrl('x/a&b%c?d#e.md'),
                         'https://woniuguaniu.github.io/ai-knowledge-base/x/a-and-b-percentcde')


class TestCollectNotes(MiniKnowledgeBaseCase):

    def testSkipsReadmeHiddenDirsAndMapModule(self):
        notesByModule = bm.collectNotes(self.rootDir)
        self.assertEqual(sorted(notesByModule), ['00_甲模块', '01_乙模块'])
        self.assertEqual(sorted(notesByModule['00_甲模块']),
                         sorted(['00_甲模块/笔记一.md', '00_甲模块/笔记 二.md', '00_甲模块/子目录/笔记三.md']))
        self.assertEqual(notesByModule['01_乙模块'], ['01_乙模块/笔记四.md'])


class TestCheckOutline(MiniKnowledgeBaseCase):

    def testCompleteModulePassesAndUnstartedModuleOnlyWarns(self):
        report = self.runCheck(self.makeCompleteOutline())
        self.assertEqual(report.failures, [])
        self.assertEqual(report.warnings, ['[未收录模块] 01_乙模块（1 篇）'])
        self.assertEqual((report.noteCount, report.totalNotes, report.moduleCount), (3, 4, 1))

    def testMissingNoteInStartedModuleFails(self):
        lines = self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', ['要点甲', '要点乙'])
        report = self.runCheck(self.buildOutline(lines))
        self.assertIn('[漏收] 00_甲模块/笔记 二.md', report.failures)
        self.assertIn('[漏收] 00_甲模块/子目录/笔记三.md', report.failures)

    def testDuplicateNoteFails(self):
        extraLines = self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', ['要点甲', '要点乙'])
        report = self.runCheck(self.makeCompleteOutline() + '\n'.join(extraLines) + '\n')
        self.assertTrue(any(item.startswith('[重复] 00_甲模块/笔记一.md') for item in report.failures))

    def testBrokenLinkFails(self):
        brokenBlock = '- [不存在](../00_甲模块/不存在.md)\n  - 甲\n  - 乙\n'
        report = self.runCheck(self.makeCompleteOutline() + brokenBlock)
        self.assertTrue(any(item.startswith('[断链]') for item in report.failures))

    def testPointCountOutOfRangeFails(self):
        report = self.runCheck(self.makeCompleteOutline(firstNotePoints=['只有一条']))
        self.assertIn('[要点数量] 00_甲模块/笔记一.md：1 条（应为 2–6 条）', report.failures)

    def testLongPointOnlyWarns(self):
        report = self.runCheck(self.makeCompleteOutline(firstNotePoints=['这' * 26, '短']))
        self.assertEqual(report.failures, [])
        self.assertTrue(any(item.startswith('[要点超长]') for item in report.warnings))

    def testMissingOrStaleStampOnlyWarns(self):
        lines = self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', ['甲', '乙'])
        lines += self.makeNoteBlock('笔记二', '../00_甲模块/笔记%20二.md', ['甲', '乙'], '00000000')
        lines += self.makeNoteBlock('笔记三', '../00_甲模块/子目录/笔记三.md', ['甲', '乙'],
                                    self.fingerprintOf('00_甲模块/子目录/笔记三.md'))
        report = self.runCheck(self.buildOutline(lines))
        self.assertEqual(report.failures, [])
        self.assertIn('[缺提炼记录] 00_甲模块/笔记一.md', report.warnings)
        self.assertIn('[原文已改] 00_甲模块/笔记 二.md（提炼于 2026-11-04）', report.warnings)

    def testStrayLineFails(self):
        report = self.runCheck(self.makeCompleteOutline() + '一段不该出现的文字\n')
        self.assertTrue(any(item.startswith('[格式]') for item in report.failures))


class TestStampNotes(MiniKnowledgeBaseCase):

    def testAddsStampKeepsFoldAndIsIdempotent(self):
        text = self.buildOutline(self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', ['甲', '乙']))
        newText, updatedPaths = bm.stampNotes(text, None, self.mapDir, self.rootDir, '2026-11-04')
        self.assertEqual(updatedPaths, {'00_甲模块/笔记一.md'})
        expectedLine = ('- [笔记一](../00_甲模块/笔记一.md) <!-- markmap: fold --> '
                        f'<!-- 提炼 2026-11-04 #{self.fingerprintOf("00_甲模块/笔记一.md")} -->')
        self.assertIn(expectedLine, newText.split('\n'))
        againText, _ = bm.stampNotes(newText, None, self.mapDir, self.rootDir, '2026-11-04')
        self.assertEqual(againText, newText)

    def testOnlyStampsRequestedNotes(self):
        lines = self.makeNoteBlock('笔记一', '../00_甲模块/笔记一.md', ['甲', '乙'])
        lines += self.makeNoteBlock('笔记三', '../00_甲模块/子目录/笔记三.md', ['甲', '乙'])
        newText, updatedPaths = bm.stampNotes(self.buildOutline(lines), {'00_甲模块/子目录/笔记三.md'},
                                              self.mapDir, self.rootDir, '2026-11-04')
        self.assertEqual(updatedPaths, {'00_甲模块/子目录/笔记三.md'})
        self.assertEqual(newText.count('<!-- 提炼'), 1)


class TestRenderMarkmapSource(MiniKnowledgeBaseCase):

    def testConvertsLinksDropsStampsKeepsFoldAndFrontMatter(self):
        output = bm.renderMarkmapSource(self.makeCompleteOutline(), self.mapDir, self.rootDir)
        expectedUrl = bm.buildSiteUrl('00_甲模块/笔记 二.md')
        self.assertIn(f'<a href="{expectedUrl}" target="_blank" rel="noopener">笔记二</a>', output)
        self.assertNotIn('<!-- 提炼', output)
        self.assertIn('<!-- markmap: fold -->', output)
        self.assertIn('title: 测试导图', output)


class TestWriteXmind(MiniKnowledgeBaseCase):

    def testWritesFoldedLinkedTopicsMatchingOutline(self):
        root, _ = bm.parseOutline(self.makeCompleteOutline())
        outputPath = os.path.join(self.rootDir, '测试.xmind')
        bm.writeXmind(root, outputPath, self.mapDir, self.rootDir)
        self.assertEqual(bm.countXmindTopics(outputPath), bm.countNodes(root))
        with zipfile.ZipFile(outputPath) as archive:
            self.assertEqual(sorted(archive.namelist()), ['content.json', 'manifest.json', 'metadata.json'])
            sheets = json.loads(archive.read('content.json').decode('utf-8'))
        rootTopic = sheets[0]['rootTopic']
        self.assertEqual(rootTopic['title'], '测试导图')
        noteTopic = rootTopic['children']['attached'][0]['children']['attached'][0]
        self.assertEqual(noteTopic['title'], '笔记一')
        self.assertEqual(noteTopic['href'], bm.buildSiteUrl('00_甲模块/笔记一.md'))
        self.assertEqual(noteTopic['branch'], 'folded')
        self.assertEqual([topic['title'] for topic in noteTopic['children']['attached']], ['要点甲', '要点乙'])


class TestSetHtmlTitle(unittest.TestCase):

    def testReplacesMarkmapDefaultTitle(self):
        self.assertEqual(bm.setHtmlTitle('<head><title>Markmap</title></head>', 'AI <知识库>'),
                         '<head><title>AI &lt;知识库&gt;</title></head>')


if __name__ == '__main__':
    unittest.main()
