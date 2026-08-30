# 06 Agent 工程

本模块收录 Agent 的概念、架构、评测、安全、工具调用和 Claude Code 生态。它适合从“什么是 Agent”一路读到“如何工程化维护 Agent 系统”。

> 🗺️ **想先看一张总览地图**——Agent 架构师该掌握哪 8 个能力域、按哪 6 个能力边界阶段学——看 [Agent架构师能力地图与学习路线.md](Agent架构师能力地图与学习路线.md)（本模块导航总纲，每项能力都映射到下面的具体笔记）。

## 推荐阅读顺序

1. [什么是Agent.md](什么是Agent.md)：建立 Agent 的基础心智模型。
2. [Agent发展轨迹四阶段.md](Agent发展轨迹四阶段.md)：理解从 Prompt 到 Harness 的演进。
3. [Loop Engineering与四代演化.md](Loop%20Engineering与四代演化.md)：把演进史推到 Loop 这一代——四次跃迁（语言表达 → 信息筛选 → 系统设计 → 目标管理）与 Loop 之后的四个演化方向。
4. [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md)：进入架构层，理解 Model + Harness。
5. [Function Calling与MCP工程指南.md](Function%20Calling与MCP工程指南.md)：理解工具调用和 MCP。
6. [Eval测评体系.md](Eval测评体系.md) 与 [LLM典型失败模式.md](LLM典型失败模式.md)：建立质量控制和失败识别能力。
7. [Agent安全攻防.md](Agent安全攻防.md)：补安全边界和攻防意识。

## 按主题分组

| 分组 | 笔记 |
|---|---|
| 总纲 / 能力地图 | [Agent架构师能力地图与学习路线.md](Agent架构师能力地图与学习路线.md) |
| 基础与演进 | [什么是Agent.md](什么是Agent.md)、[Agent发展轨迹四阶段.md](Agent发展轨迹四阶段.md)、[Loop Engineering与四代演化.md](Loop%20Engineering与四代演化.md) |
| 运行时：架构 / 上下文 / 记忆 / 成本 | [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md)、[长程任务原语-Session-Workspace-Checkpoint-Resume.md](长程任务原语-Session-Workspace-Checkpoint-Resume.md)、[Agent记忆体系.md](Agent记忆体系.md)、[Agent可观测性与成本工程.md](Agent可观测性与成本工程.md) |
| 工具与 Coding Agent | [Function Calling与MCP工程指南.md](Function%20Calling与MCP工程指南.md)、[极简可控的Coding-Agent设计-pi.md](极简可控的Coding-Agent设计-pi.md)、[Claude Code 实战速查.md](Claude%20Code%20实战速查.md)、[Claude Code 扩展生态.md](Claude%20Code%20扩展生态.md)、[Claude Code goal命令.md](Claude%20Code%20goal命令.md) |
| 质量与治理 | [Eval测评体系.md](Eval测评体系.md)、[LLM典型失败模式.md](LLM典型失败模式.md)、[Skill工程化设计与失效防御.md](Skill工程化设计与失效防御.md)、[Vibe Coding与技术债治理.md](Vibe%20Coding与技术债治理.md)、[Agent安全攻防.md](Agent安全攻防.md) |
| Multi-Agent | [Multi-Agent工程实战与Persona设计.md](Multi-Agent工程实战与Persona设计.md) |

## 边缘笔记怎么用

- [Claude Code goal命令.md](Claude%20Code%20goal命令.md)：适合需要长任务自动推进、可衡量完成条件和独立评估器机制时看；它是 Claude Code 生态的专题补充，不是 Agent 入门第一篇。
- [Multi-Agent工程实战与Persona设计.md](Multi-Agent工程实战与Persona设计.md)：适合已经理解单 Agent 后，再看多角色协作、共享真相源和 Persona 设计。
- [极简可控的Coding-Agent设计-pi.md](极简可控的Coding-Agent设计-pi.md)：拆解开源极简 Coding Agent **pi**，看它在可观测性、可扩展、极简可控三个方向上为什么和 Claude Code / Codex 走了相反的路。适合已经在用大厂 Coding Agent、但被黑盒和功能膨胀困扰时读——它是**对照组**，不是入门篇。
- [Vibe Coding与技术债治理.md](Vibe%20Coding与技术债治理.md)：讲的不是 Agent 架构而是**人怎么用 Agent 写代码**——vibe coding 之后代码难维护，病根是人放弃了对代码的理解，AI 只是放大器。适合在实际项目里已经感到"AI 改的代码看不懂了"时读。
- [DeepSeek Engram 条件记忆](../01_模型架构/DeepSeek_Engram条件记忆.md)：不属于 Agent 工程，但对理解“记忆”和“推理”分工有启发，可作为 Memory 机制的模型层对照。

## 维护提示

- Agent 相关内容变化很快。涉及具体版本、命令、模型行为的笔记应标明资料日期或最后更新日期。
- 新增 Claude Code / Codex / MCP 生态笔记时，优先回填到本 README 和根 README，避免散落。
