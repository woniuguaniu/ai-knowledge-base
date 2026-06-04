# 06 Agent 工程

本模块收录 Agent 的概念、架构、评测、安全、工具调用和 Claude Code 生态。它适合从“什么是 Agent”一路读到“如何工程化维护 Agent 系统”。

> 🗺️ **想先看一张总览地图**——Agent 架构师该掌握哪 8 个能力域、按哪 6 个能力边界阶段学——看 [Agent架构师能力地图与学习路线.md](Agent架构师能力地图与学习路线.md)（本模块导航总纲，每项能力都映射到下面的具体笔记）。

## 推荐阅读顺序

1. [什么是Agent.md](什么是Agent.md)：建立 Agent 的基础心智模型。
2. [Agent发展轨迹四阶段.md](Agent发展轨迹四阶段.md)：理解从 Prompt 到 Harness 的演进。
3. [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md)：进入架构层，理解 Model + Harness。
4. [Function Calling与MCP工程指南.md](Function%20Calling与MCP工程指南.md)：理解工具调用和 MCP。
5. [Eval测评体系.md](Eval测评体系.md) 与 [LLM典型失败模式.md](LLM典型失败模式.md)：建立质量控制和失败识别能力。
6. [Agent安全攻防.md](Agent安全攻防.md)：补安全边界和攻防意识。

## 按主题分组

| 分组 | 笔记 |
|---|---|
| 总纲 / 能力地图 | [Agent架构师能力地图与学习路线.md](Agent架构师能力地图与学习路线.md) |
| 长程任务 / 状态管理 | [长程任务原语-Session-Workspace-Checkpoint-Resume.md](长程任务原语-Session-Workspace-Checkpoint-Resume.md) |
| 可观测 / 成本 / 记忆 | [Agent可观测性与成本工程.md](Agent可观测性与成本工程.md)、[Agent记忆体系.md](Agent记忆体系.md) |
| 入门与演进 | [什么是Agent.md](什么是Agent.md)、[Agent发展轨迹四阶段.md](Agent发展轨迹四阶段.md) |
| 架构与工具调用 | [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md)、[Function Calling与MCP工程指南.md](Function%20Calling与MCP工程指南.md) |
| 质量与失败模式 | [Eval测评体系.md](Eval测评体系.md)、[LLM典型失败模式.md](LLM典型失败模式.md) |
| 安全 | [Agent安全攻防.md](Agent安全攻防.md) |
| Claude Code 生态 | [Claude Code 实战速查.md](Claude%20Code%20实战速查.md)、[Claude Code 扩展生态.md](Claude%20Code%20扩展生态.md)、[Claude Code goal命令.md](Claude%20Code%20goal命令.md) |
| Multi-Agent | [Multi-Agent工程实战与Persona设计.md](Multi-Agent工程实战与Persona设计.md) |

## 边缘笔记怎么用

- [Claude Code goal命令.md](Claude%20Code%20goal命令.md)：适合需要长任务自动推进、可衡量完成条件和独立评估器机制时看；它是 Claude Code 生态的专题补充，不是 Agent 入门第一篇。
- [Multi-Agent工程实战与Persona设计.md](Multi-Agent工程实战与Persona设计.md)：适合已经理解单 Agent 后，再看多角色协作、共享真相源和 Persona 设计。
- [DeepSeek Engram 条件记忆](../01_模型架构/DeepSeek_Engram条件记忆.md)：不属于 Agent 工程，但对理解“记忆”和“推理”分工有启发，可作为 Memory 机制的模型层对照。

## 维护提示

- Agent 相关内容变化很快。涉及具体版本、命令、模型行为的笔记应标明资料日期或最后更新日期。
- 新增 Claude Code / Codex / MCP 生态笔记时，优先回填到本 README 和根 README，避免散落。
