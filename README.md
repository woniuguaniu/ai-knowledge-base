# AI 探索知识库

> 记录与 AI 交流学习的探索之旅，持续积累对人工智能的理解。

---

## 知识库结构

```
与AI交流AI/
├── 00_核心概念/           # AI/ML 基础（Transformer、注意力机制 …）
├── 01_模型架构/           # 各模型的架构与创新（DeepSeek …）
├── 02_提示词工程/         # 独立子项目，10 个递进模块的完整教程
├── 03_应用实践/           # 实际应用案例（RAG、数据建模 …）
├── 04_探索日志/           # 按日期归档的探索记录（YYYY-MM-DD_主题.md）
├── 05_技术基础/           # AI 之外的技术基础（Shell、系统、软件工程）
├── 06_Agent工程/          # Harness Engineering、Agent 架构、Claude Code 源码分析
├── claude code skills知识/ # Claude Skills 课件与截图素材
└── _templates/            # 笔记模板
```

---

## 知识索引

### 00 核心概念

| 主题 | 文件 | 简介 |
|------|------|------|
| Transformer | [Transformer.md](00_核心概念/Transformer.md) | 大模型的核心架构 |
| 注意力机制 | [注意力机制.md](00_核心概念/注意力机制.md) | Self-Attention 与 Multi-Head Attention |
| 上下文窗口与 Token 计费 | [上下文窗口与Token计费.md](00_核心概念/上下文窗口与Token计费.md) | Context Window、Token 换算、Prompt Caching 与账单拆解 |
| 模型训练技术速查 | [模型训练技术速查.md](00_核心概念/模型训练技术速查.md) | 预训练 / SFT / RLHF / DPO / **蒸馏** / RFT / RLAIF 一次讲清，含全景流水线图与"何时用哪种"判断框架 |

### 01 模型架构

| 模型 | 文件 | 核心创新 |
|------|------|---------|
| DeepSeek | [DeepSeek.md](01_模型架构/DeepSeek.md) | 架构层 (MLA / MoE) + 训练层 (GRPO / R1 多阶段训练 / R1-Distill 蒸馏家族)；含成本对比、Aha Moment 涌现解析 |

### 02 提示词工程（子项目）

独立子项目，含 10 个递进学习模块与速查/练习题。详见子项目 README：
[02_提示词工程/README.md](02_提示词工程/README.md)

### 03 应用实践

| 主题 | 文件 | 简介 |
|------|------|------|
| RAG | [RAG/RAG学习笔记.md](03_应用实践/RAG/RAG学习笔记.md) | 检索增强生成的原理与工程实践 |
| 数据分析建模 | [数据分析建模（二手车经验）.md](03_应用实践/数据分析建模（二手车经验）.md) | 二手车价格预测的建模经验总结 |
| 虚拟形象与数字人技术全景 | [虚拟形象与数字人技术全景.md](03_应用实践/虚拟形象与数字人技术全景.md) | VTuber / 换脸 / 换声 / 数字人 / 云端 API 的技术解剖与实战指南 |

### 04 探索日志

| 日期 | 主题 | 链接 |
|------|------|------|
| 2024-12-10 | Transformer 与 DeepSeek 创新 | [查看](04_探索日志/2024-12-10_Transformer与DeepSeek.md) |
| 2026-05-04 | Agent 知识体系闭环（工作流方法论复盘）| [查看](04_探索日志/2026-05-04_Agent知识体系闭环.md) |

### 05 技术基础

| 主题 | 文件 | 简介 |
|------|------|------|
| Shell 与终端 | [Shell与终端基础知识总结.md](05_技术基础/Shell与终端基础知识总结.md) | 小白通俗版：终端/Shell/命令行三层结构、Shell 家族隶属图、Mac/Linux/Windows 对照、跨平台脚本兼容性、**`ls -l` 输出与文件权限详解（含数字权限/macOS 扩展属性 `@`）、常用命令大全（12 类含管道重定向）、新手 5 大踩坑提醒** |
| swap 内存 | [swap内存处理技术.md](05_技术基础/swap内存处理技术.md) | Linux 交换分区原理与处理 |
| 软件架构 | [软件架构设计详解.md](05_技术基础/软件架构设计详解.md) | 软件架构设计原则与实践 |
| 程序员黑话速查 | [程序员黑话速查.md](05_技术基础/程序员黑话速查.md) | **持续生长型**术语速查：API / async / Canary Token / diff / DLP / GCG Attack / hack / HITL / MCP / N-version programming / patch / Reasoning Effort / Spotlighting / stdin-stdout-stderr / unified diff patch …… |
| 多 CLI 联动 | [多CLI联动.md](05_技术基础/多CLI联动.md) | Claude / Codex / Gemini 三家协同：能力对比、3 个层级、4 种玩法（管道接力 / MCP 互调 / 三方投票 / 角色分工）+ 双模型协作案例评析（含 7 大坑与改进版配置） |
| GitHub 项目入门（实操指南） | [GitHub项目入门/小白入门-GitHub项目部署使用指南.md](05_技术基础/GitHub项目入门/小白入门-GitHub项目部署使用指南.md) | 以 gpt_image_playground 为样本，从零开始的 7 步部署流程：识别项目类型、装环境、装依赖、配置、启动、上线；含小白排错四件套、高效求助提问模板、30 秒口令速记 |
| GitHub 项目入门（概念地图） | [GitHub项目入门/程序小白概念扫盲手册.md](05_技术基础/GitHub项目入门/程序小白概念扫盲手册.md) | 配套概念手册：软件工程全景图（按使用场景）、npm/pnpm/yarn 对比、MIT/Fork、命令参数、Docker/Nginx、容器化、pnpm + Docker 共用机制、缩写表、编程语言识别图鉴、Git 常用命令实战图解 |
| GitHub 项目入门（速查卡） | [GitHub项目入门/五看一跑_小白工程运行部署学习文档.md](05_技术基础/GitHub项目入门/五看一跑_小白工程运行部署学习文档.md) | 30 秒口令版：五看一跑（README/类型/scripts/环境/部署/本地跑）+ 排错四件套 + 实战模板，临时回忆流程时翻 |

### 06 Agent 工程

| 主题 | 文件 | 简介 |
|------|------|------|
| 什么是 Agent（**入门必读**）| [什么是Agent.md](06_Agent工程/什么是Agent.md) | 完全没接触过 Agent 的入门科普：三段循环（Perception → Reasoning → Action）、4 大核心能力（Tool Use / Memory / Planning / Reflection）、Claude Code 修 bug 真实例子、7 大常见误区、Agent vs Workflow/LLM/Copilot 对比、ReAct 模式、术语速查 |
| Harness 工程与 Agent 解剖 | [Harness工程与Agent解剖.md](06_Agent工程/Harness工程与Agent解剖.md) | Agent = Model + Harness；三层工程递进、Claude Code 泄露事件、**Agent 五层架构图（编排层 / 记忆层 / 大模型 / 执行层 / 反馈层）**与补强版、Guides/Sensors 框架 |
| Agent 发展轨迹四阶段 | [Agent发展轨迹四阶段.md](06_Agent工程/Agent发展轨迹四阶段.md) | 小白视角史观文：Prompt → Reasoning/ReAct → Context → Harness 的"俄罗斯套娃"演进，附生动比喻、入门路径与「**Agent 架构师**」职业视角评析 |
| Eval 测评体系 | [Eval测评体系.md](06_Agent工程/Eval测评体系.md) | Agent 工程的命根子：四类 Eval（离线 / 在线 A/B / LLM-as-Judge / 人工）、构建数据集、关键指标、实战工具、5 大经典误区、小白第一周落地路径 |
| Agent 安全攻防 | [Agent安全攻防.md](06_Agent工程/Agent安全攻防.md) | **30 种攻击手法**（提示词注入 / 间接注入 / RAG 投毒 / MCP 投毒 / GCG 对抗后缀 / DAN 越狱…）+ **17 项防御技术**（5 层框架 + 12 项具体：Canary Token / LLM Guard / Spotlighting / DLP / HITL / 沙箱…）+ 纵深防御方法论；源自 OpenClaw 敲壳测试 |

---

## 如何使用这个知识库

### 1. 继续探索

每次与 AI 交流学习时：

- 选定要探索的主题
- 判断归属：已有模块 → 进模块目录；一次性探索 → 按 `YYYY-MM-DD_主题.md` 放入 `04_探索日志/`
- 复制 `_templates/探索记录模板.md` 作为起点
- **写完后同步更新本 README 对应的索引表**

### 2. 复习回顾

- 通过索引快速找到想复习的内容
- 查看 `04_探索日志/` 回顾学习历程

### 3. 知识关联

在笔记中使用相对链接建立知识关联：

```markdown
参见 [Transformer](../00_核心概念/Transformer.md) 的基础概念
```

---

## 待探索主题

- [ ] 位置编码（Positional Encoding）
- [ ] Layer Normalization
- [ ] RLHF（人类反馈强化学习）
- [ ] GPT 系列演进
- [ ] Claude 的架构特点
- [ ] LLaMA 开源模型
- [x] ~~Agent 智能体~~ → 已新建 `06_Agent工程/`，首篇笔记《Harness 工程与 Agent 解剖》已落盘

---

*最后更新: 2026-05-05*
