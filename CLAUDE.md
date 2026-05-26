# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目性质

这是一个**纯 Markdown 中文知识库**，不是代码项目：
- 没有 build / lint / test 流程，没有 `package.json` / `pyproject.toml` 等清单文件
- 已纳入 git 版本管理（用于追踪笔记演进，不是协作开发）
- 内容是作者（个人学习者）与 AI 交流学习过程中沉淀的笔记
- 所有交流与写作使用**中文**

## 仓库的"双层"结构

本仓库是**"根级知识库 + 子知识库"**的嵌套结构，新来的 Claude 最容易踩的坑是把两层混为一谈：

1. **根目录** = 跨主题的综合知识库，按编号模块组织：
   - `00_核心概念/` —— AI/ML 基础理论
   - `01_模型架构/` —— 模型设计与创新
   - `02_提示词工程/` —— 自带 CLAUDE.md 的独立子项目（见下条）
   - `03_应用实践/` —— 应用案例（含 `RAG/` 子目录、数据建模案例等）
   - `04_探索日志/` —— 按日期归档的一次性探索，命名 `YYYY-MM-DD_主题.md`
   - `05_技术基础/` —— AI 之外的通用技术笔记（Shell、系统、软件工程等）
   - `claude code skills知识/` —— `.pptx` 与截图素材，不是 Markdown 笔记，**一般不动**
   - `_templates/` —— 笔记模板
   - 根目录**不应该**再有散落的 `.md`（除 `README.md` / `CLAUDE.md`）。如果发现有，通常意味着该归类到上面某个模块。

2. **`02_提示词工程/`** = 自成一套的完整教程子项目
   - 该子目录**自带** `CLAUDE.md`、`README.md`、`.claude/settings.local.json`
   - 在该目录下工作时，**优先遵守它自己的 `02_提示词工程/CLAUDE.md`**，不要用根级规则去覆盖它的约定（例如它有固定的 `01_` ~ `10_` 编号体系和四阶段学习路线）

## 文件命名与组织惯例

- **模块目录**：`NN_中文主题名/`（两位数字 + 下划线 + 中文），例如 `00_核心概念`、`01_模型架构`
- **模块内的笔记**：`主题名.md`（如 `Transformer.md`）；`02_提示词工程/` 子项目内额外有 `NN_主题.md` 的二级编号
- **探索日志**：`YYYY-MM-DD_主题.md`，这是 `_templates/探索记录模板.md` 规定的格式。新建探索日志时应复制该模板。
- **根目录散文件**：无编号的 `.md`，一般是一次性总结/速查，不强制归类

## 新增内容时的决策树

当用户要求"记录"或"整理"某个新主题时：

1. 内容属于已有模块（核心概念 / 模型架构 / 提示词工程 / 应用实践 / 技术基础）？→ 放进对应目录，并**更新根 README.md 的索引表**
2. 是一次性探索记录？→ 按 `YYYY-MM-DD_主题.md` 命名放进 `04_探索日志/`，复制 `_templates/探索记录模板.md`
3. 属于尚未存在的新类别？→ **先和用户确认**是否开新模块目录（下一编号 `06_主题/`），不要擅自建目录搞乱结构
4. `02_提示词工程/` 内部的新增必须遵守它的 `01_` ~ `10_` 编号体系，不要插入乱序编号

## 基于截图/图片整理笔记的规则

用户给截图（PPT、网页图、图片）让 Claude 整理成笔记时，**笔记必须脱离原图独立成立**——读者（包括用户日后回看）看不到原图，文档不能依赖它：

- ❌ 不要写 `这张图`、`这种 PPT`、`图里`、`课程图里那 4 句话`、`PPT 里没列出`、`配色用荧光黄`（脱离上下文）等指代外部图的措辞
- ✅ 把"这张图/PPT" 换成**内容主语**（如 `这套定义`、`这个框架`、`该 title`、`行业里常见的四句判断`）——主语必须是笔记里能看到的对象
- ✅ 原话里的**洞察与辨识方法论**要保留，但让它独立于具体图（例：`这种 PPT 是培训课造词` → `这种 title 大概率是培训课造词`）
- ✅ 出处可以交代但不依赖图：`出自国内某 AI 培训课` 可以，`看图就知道` 不行

**自检方法**：写完后假装读者没看过原图，从头读一遍。凡是出现 `这张图`、`这个 PPT`、`图里` 等需要外部视觉支持的句子，立刻改写。

## 索引维护

根 `README.md` 的索引表是手工维护的——任何新增/移动笔记后，都应同步更新该表的对应行，保持"索引 = 实际"一致。2026-04-18 已做过一次大整理，把原先散落在根目录的 5 个 md 归入了 `03/04/05` 三个模块，目前索引与磁盘一致。

## Quartz 前端站同步规则

本知识库**同时是一个 Quartz 4 前端站的内容源**——`~/Desktop/quartz-preview/quartz/content` 已经软链到本目录（`ln -s /Users/xxddd/Desktop/与AI交流AI`）。这意味着：

**KB 改动 → Web 站自动同步**：
- 任何 `.md` 文件的新增 / 修改 / 删除，Quartz `build --serve` 进程会在 1-2 秒内 hot-rebuild
- 验证方式：`curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/路径`
- 在浏览器中刷新页面也会立刻看到变化

**前端站访问入口**：`http://localhost:8080/`（服务由 `cd ~/Desktop/quartz-preview/quartz && npx quartz build --serve` 启动并常驻；如果未运行可手动重启）

**新增笔记后必做的验证（这是同步链路的端到端检查）**：

1. 笔记落盘到对应模块目录后
2. `curl` 一下新笔记的 URL 是否 200（注意中文路径要 `urllib.parse.quote`，文件名空格会被 Quartz 转成 `-` 短横线）
3. 如果新笔记被其他笔记引用，再 curl 一下被引用页确认 Backlinks 是否多了一条
4. 把命令输出贴给用户做证据（按表演性完成防御要求）

**index.md vs README.md 的职责分工**：
- `index.md`（Quartz 首页 hero 卡片）—— **只在 Quartz 站显示**，含 ✨ AI Knowledge Hub 标签 + 4 个统计数字 + 模块导航
- `README.md`（GitHub 浏览索引）—— GitHub / IDE 里看的完整索引表
- 两者**各司其职，不要互相 copy**。新增笔记同时更新 README 索引（必须）+ 如果数字到了下一个量级（如 70+/100+）再更新 index.md 的统计（可选）

**Quartz 已 ignore 的路径**（在 `~/Desktop/quartz-preview/quartz/quartz.config.ts` 的 `ignorePatterns` 里）：
- `.claude` / `.obsidian` / `_templates` / `claude code skills知识` / `CLAUDE.md`
- README.md 会被渲染到 `/README` 路径（作为普通笔记）

**什么时候需要重启 `npx quartz build --serve`**：
- 改了 `quartz.config.ts` / `quartz.layout.ts` —— Quartz 一般会自动 hard rebuild
- 改了 `quartz/styles/custom.scss` —— 通常 hot-reload，浏览器刷新即可
- 改了 `package.json` 或装新依赖 —— 必须重启
- 进程崩了或被 `pkill` —— 必须重启

**临时文件不要放 KB 根目录**：Quartz watch 软链监听到 KB 根的任何文件创建/删除都会触发 rebuild。如果在 KB 根目录创建后又 `mv` 走（例如截图、临时测试 .md），Quartz 在 unlink 阶段可能找不到旧资源而崩溃。所以：
- Playwright 截图等临时输出 → 放 `~/Desktop/quartz-preview/screenshots/` 或 `/tmp/`，**不要放 KB 根**
- 用 `_sync_test_*.md` 测试 hot-reload 时，**先停 watch 或在 build 完成后再 mv**

**注意：本节描述的是当前已配置好的状态**。如果未来 `quartz-preview` 目录被删 / 软链断了 / 端口冲突，恢复流程见 `~/Desktop/quartz-preview/` 内的备注；本规则不负责"如何从零安装 Quartz"。

## 本地 Claude 配置

`.claude/settings.local.json` 仅声明了三项权限白名单：`WebFetch(domain:linux.do)`、`WebSearch`、`Bash(python3 *)`。不要在未经用户同意下改动此文件。
