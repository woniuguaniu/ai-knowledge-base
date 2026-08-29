# Harness 工程与 Agent 解剖

> 一句话：**Agent = Model + Harness**。大模型是"引擎"，Harness 是"引擎周围让它能真正干活的一整套基础设施"。随着开源模型追平闭源模型，**护城河正在从模型本身迁移到 Harness**。

---

## 目录

- [1. 什么是 Harness Engineering](#1-什么是-harness-engineering)
- [2. 三层工程的递进关系](#2-三层工程的递进关系)
- [3. 为什么这个概念一夜爆红：Claude Code 泄露事件](#3-为什么这个概念一夜爆红claude-code-泄露事件)
- [4. Agent 五层解剖图](#4-agent-五层解剖图)
- [5. 核心设计原则：Guides + Sensors](#5-核心设计原则guides--sensors)
- [6. 补强版 Harness 架构图](#6-补强版-harness-架构图)
- [7. Harness 的典型组件清单](#7-harness-的典型组件清单)
- [8. 为什么 Harness 是新的 AI 护城河](#8-为什么-harness-是新的-ai-护城河)
- [9. 未来：Harness 会被模型吞并吗](#9-未来harness-会被模型吞并吗)
- [10. 与本知识库其他章节的关联](#10-与本知识库其他章节的关联)
- [11. 延伸阅读](#11-延伸阅读)

---

## 1. 什么是 Harness Engineering

**Harness**（马具 / 挽具）：一个形象的比喻——马（大模型）再强壮，没有缰绳、鞍、马车的连接，也无法把力气变成有用的工作。

官方定义（Martin Fowler / Thoughtworks）：

> "Harness" 指 AI Agent 中**除模型本身以外**的所有东西。Harness Engineering 就是**围绕模型搭建应用与基础设施**的工程学科。

它管的事：
- 什么时候加载什么上下文
- 有哪些工具可以调用
- 哪些动作被允许、哪些被拦截
- 失败了怎么恢复
- 会话如何持久化
- 多轮交互里的状态如何管理

**一句话判断法**：如果你把这个模块里的 LLM 从 Claude 换成 GPT-5 再换成本地 Qwen，它还能工作——那这个模块就是 Harness 的一部分。

### 1.1 词源考据：这个词是怎么在 2026 年初出现的

> 本小节与 § 1.2 源自中文社区词源考据长文《什么是 Harness Engineering：聊聊最近爆火的技术词》（2026 年年中，作者自述综合 linux.do 20+ 帖子与多篇一手文献）。文中时间与事件以该文考据为准。

这个词不是某一家公司发明的，而是**两个月内四个标志性事件把它推成了公共话题**：

| 时间 | 事件 | 贡献 |
|------|------|------|
| **2026-02-05** | HashiCorp 联合创始人 **Mitchell Hashimoto** 发表博客《My AI Adoption Journey》，提出 **"Engineer the harness"** | 首次正式亮相。核心思路：每次发现 Agent 犯错，就改一次外围环境（工具、规则、脚手架），让它永远不再犯同样的错——改的不是 prompt，也不是模型权重 |
| **2026-02-11** | OpenAI 工程博客《Harness Engineering: Leveraging Codex in an Agent-First World》（Ryan Lopopolo） | 让术语**出圈的具体案例**：AGENTS.md 保持 100 行以内当目录而非百科全书、执行计划当一流工件纳入版本控制、自定义 linter 的报错里直接嵌修复指令、CI 当 Agent 输出的质量闸门 |
| **2026-03-24** | Anthropic 发表长时运行 Agent 的 harness 研究《Effective harnesses for long-running agents》 | 进阶方案：planner-generator-evaluator 三代理架构、`progress.txt` 记录跨 session 状态、执行计划与已完成计划都纳入版本控制 |
| **2026-03-31** | 安全研究员 Chaofan Shou 发现 Claude Code npm 包因构建配置失误经 source map 泄露完整源码（披露推文超 1700 万次浏览） | **催化剂**：讨论从博客与二手经验层面，进入"逐行对照一个生产级系统"层面（详见 § 3） |

Anthropic 那篇研究里有一句被广泛引用的话，值得单独记住：

> 每一个 harness 组件都编码了一个关于"模型自身做不到什么"的假设，而这些假设值得反复检验：它们可能本来就是错的，也可能随着模型进步很快过时。

**前传：swyx 的 IMPACT 框架（2025-03）**——早在上面这条时间线开始前近一年，知名开发者 swyx 就提出过几乎同构的说法，当时叫 **"agent engineering"**，配套 **IMPACT 六维框架**：**I**ntent（用户意图→指令设计）、**M**emory（跨 session 记忆→上下文治理）、**P**lanning（任务拆解→规划）、**A**uthority（自主边界→权限判定）、**C**ontrol Flow（LLM 驱动的控制流→运行时循环）、**T**ools（工具集→工具系统）。六个维度与 2026 年的核心议题几乎完全重合，但当时没有出圈——说明**问题意识早已酝酿，只差一个好比喻、一组具体案例和一个催化事件**。

**为什么爆发在 2026 年初**：主要矛盾变了。2023–2024 年瓶颈是"模型能不能用"（prompt engineering 是主话题）；2024–2025 年瓶颈是"怎么把合适的信息喂给模型"（context engineering 是主话题）；2025 年底起，单次推理质量不再是主要瓶颈，出问题的地方变成**长期运行中的系统性失败**——修 A 坏 B、半路耗光上下文、跨 session 失忆、把自己的实现判为通过。这些需要运行时纪律、制度化约束、外部验证，于是 harness engineering 成为主话题。演化史观的完整展开见 [Agent 发展轨迹四阶段](Agent发展轨迹四阶段.md)。

⚠️ **考据的局限**：该文时间线没有提到 Martin Fowler / Thoughtworks 这条线（本文 § 1 定义与 § 5 Guides/Sensors 框架的来源）。两条线不冲突——按该文自己的结论，这个词是"**一场群体性的命名过程**"：Mitchell 的个人实践、swyx 的早期框架、OpenAI 的工程报告、Anthropic 的研究、Thoughtworks 的方法论、源码泄露事件，共同构成了它的诞生环境。正因为它不是某一家的发明，才会出现下面三种解释口径并存的局面。

### 1.2 三种解释口径：马具派、工作空间派、约束执行派

社区对这个词的解读大致分三派。三派不矛盾，只是**重心和适用场合不同**：

| 口径 | 核心立场 | 适合谁用 | 风险 |
|------|---------|---------|------|
| **马具派** | 模型是赤兔马，harness 是马镫和缰绳；同一匹赤兔马，会骑的人手里是战神，不会骑的人手里是摔伤事故 | 写教程开场、向不熟 AI 的读者解释 | 隐喻自带"被动驾驭"意味，一部分开发者觉得贬低了模型 |
| **工作空间派** | harness 是给模型的**工作环境**：定义协作边界与协议，让模型在稳定、可交互、可反馈的环境里持续工作；本质是 context engineering 的延伸 | 从零搭 Agent 产品的工程师向同事解释自己在做什么 | 容易过于乐观，淡化"模型会犯错，且错误在 shell / 文件系统 / Git 里留下真实后果" |
| **约束执行派** | **模型是整个系统里最不稳定的部件**，不天然值得信任；harness 是一整套制度化控制平面——"**代理系统的关键能力是约束执行**" | 生产环境 Agent 系统的负责人，说服管理层给"看起来像补丁"的基础设施投时间 | 听起来最悲观，但最接近 Claude Code 源码在实现上呈现的态度 |

如果只能选一种当默认理解，**约束执行派最稳妥**（该考据文的立场，本笔记认同）：系统是给未来的自己写的，未来总会遇到今天没看见的故障，约束结构比漂亮比喻更管用。本文 § 5 的 Guides/Sensors、§ 6 的权限闸门，本质都是约束执行派的具体化。

---

## 2. 三层工程的递进关系

业界已经形成共识的三层划分，**每一层都包含前一层**：

| 层次 | 管什么 | 生活类比 |
|------|--------|---------|
| **Prompt Engineering**（提示词工程） | 怎么写指令、怎么问问题 | 教一个员工"怎么说话" |
| **Context Engineering**（上下文工程） | 什么内容何时进入上下文窗口 | 管理员工"每次看到的信息" |
| **Harness Engineering**（脚手架工程） | 整个应用与基础设施：工具、记忆、权限、错误恢复 | 搭建员工"工作的整个公司" |

```
Harness Engineering
└── Context Engineering
    └── Prompt Engineering
        └── 原始 API 调用
```

**这也解释了为什么提示词工程不够用**：单靠调整 prompt，解决不了"工具失败要重试"、"上下文爆掉要压缩"、"并发调用要编排"这些工程问题。

### 2.1 修正视角：三层楼板，不是三代拳王

"递进阶梯"有个副作用：容易让人以为 prompt engineering 已经过时、被 context engineering 取代，后者又被 harness engineering 取代。更准确的说法是**同一栋建筑的三层楼板**——每一层都还在，只是关注点从"一句话怎么措辞"扩展到了"整个运行环境怎么组织"：

- prompt engineering 的原则没有过时，它变成了大系统里的**子模块**——system prompt、工具描述、给 LLM 消费的错误信息，全都要写好 prompt
- harness 里每个组件都依然依赖好的上下文选择
- 阶梯论真正描述的是**瓶颈的迁移**（模型弱时措辞是瓶颈 → 中等时上下文拼装是瓶颈 → 很强时外围工程结构是瓶颈，见 § 1.1），不是技术的代际淘汰

### 2.2 别混淆：另一个"三层"——通用 / 项目 / 任务 harness

⚠️ 本节的"三层"与上面的"三层工程递进"**不是一回事**：上面按"工程学科的包含关系"分层，本节按"**harness 与具体项目的关联程度**"分层（这个划分最早在 linux.do 的讨论帖里被清晰表达）。它回答一个非常实际的问题：**我到底该操心哪一层？**

| 层 | 与项目的关系 | 包含什么 | 谁来做 |
|----|------------|---------|--------|
| **通用 harness 层** | 弱相关，属于 Agent runtime / framework 的通用能力 | 终端交互、tool loop、权限系统、记忆、线程持久化、context compaction、hook 机制、任务调度 | Claude Code / Codex / OpenCode 等工具已经做好——**选一个合适的就行，不用自己造** |
| **项目 harness 层** | 强相关，但不是业务功能本身 | AGENTS.md / CLAUDE.md、仓库知识布局、架构边界定义、lint 规则、质量标准、依赖选择原则、文档索引 | **开发者自己搭，是长期值得投入的主战场** |
| **任务 harness 层** | 只和当前这次具体工作相关 | planner-generator-evaluator 三代理、跨 session 交接文档、特定任务的 QA prompt、Playwright 检查脚本 | 临时搭、用完可拆——为一次特别复杂的工作提供额外支架 |

这个划分能防一个常见误解：**写了一个 CLAUDE.md ≠ 做了 harness engineering**。CLAUDE.md 只是项目层的入口，它替代不了通用层的运行时问题（那是工具的职责），也替代不了任务层的具体编排（那是具体活儿的职责）。三层各司其职，少了任何一层会出问题，混为一谈也会出问题。

- 通用层的极简实践案例见 [极简可控的 Coding Agent 设计（pi）](极简可控的Coding-Agent设计-pi.md)——把通用层压到 4 个工具、<1000 token 系统提示词也能站住
- 任务层"定目标 + 定时驱动"的进一步演化见 [Loop Engineering 与四代演化](Loop%20Engineering与四代演化.md)

---

## 3. 为什么这个概念一夜爆红：Claude Code 泄露事件

**2026 年 3 月 31 日**，安全研究员 **Chaofan Shou** 发现：Anthropic 在发布 Claude Code v2.1.88 npm 包时，因打包错误意外泄露了**约 51.2 万行 TypeScript 源码**（1900 个文件，完整未混淆的 source map）。披露推文获得超 **1700 万次浏览**，几小时内相关镜像仓库飙到 5 万星。

人们打开一看，震惊整个 AI 圈——**这根本不是"LLM 的薄壳调用层"**，而是一整套工程精密的系统：

| 组件 | 规模 / 做法 |
|------|-----------|
| **权限受控工具** | 约 40 个（文件操作、Bash、网络、LSP 集成） |
| **Query Engine** | 约 **46,000 行**，负责 API 调用、token 缓存、上下文管理、重试逻辑 |
| **动态上下文管理** | 上下文快爆时自动压缩消息 |
| **静默故障恢复** | 工具失败后走一套恢复策略，用户完全感觉不到 |
| **编译时特性剔除** | 防止内部实验工具流到外部用户 |

几天后，OpenAI 跟进公布：一个 3 人团队用"harness engineering"方法，产出了**百万行代码库，人均每天 3.5 个 PR，零手动敲代码**。

**关键影响——泄露不是词源，是催化剂**：泄露发生前，这个术语已经由 Mitchell Hashimoto 和 OpenAI 在 2 月带火（见 § 1.1），但讨论大多停留在博客、推文和二手经验层面。泄露之后，人们第一次可以**逐行对照一个年化收入十亿美元级的生产 Agent 系统**——控制面在哪一层、query loop 怎么运转、工具权限如何校验、上下文怎么压缩、错误如何恢复。看完源码的普遍反应是：让 Claude Code 比裸调模型强那么多的，不是模型本身，是外面那一圈脚手架。围绕 harness engineering 的讨论，到这时候才真正开始深入。

---

## 4. Agent 五层解剖图

目前入门课件里最主流的切法（中文社区常见版本）：

```
┌─────────────────────────────────────────────────┐
│                    编排层                        │
├──────────┬────────────────────────┬────────────┤
│          │                         │            │
│  记忆层   │      大模型 LLM          │   执行层    │
│          │                         │            │
├──────────┴────────────────────────┴────────────┤
│                    反馈层                        │
└─────────────────────────────────────────────────┘
                     AI Agent
```

### 4.1 每一层对应到 Harness 世界里的什么

| 图中层级 | Harness 世界里的对应 | Claude Code 里的具体体现 |
|---------|-------------------|-------------------------|
| **编排层** | Control Loop / Query Engine（调度大脑） | 泄露代码里那 46,000 行的 query engine——决定何时调用工具、何时停止、怎么重试 |
| **记忆层** | Memory + Context Engineering | 会话持久化、自动消息压缩、`MEMORY.md`、`CLAUDE.md`、Prompt Caching |
| **大模型** | **Model**（唯一不属于 Harness 的部分） | Claude / GPT / Gemini 本身 |
| **执行层** | Tools + MCP + Sandbox | ~40 个权限受控工具（Read、Write、Bash、LSP...）+ MCP servers |
| **反馈层** | **Sensors**（反馈控制） | 测试失败回灌、lint 报错 → 模型自修复、错误恢复循环 |

**一句话**：去掉中间那块"大模型"，剩下的**四层框架结构就是 Harness 的全部**。

### 4.2 这个五层图的优点

1. 干净地把模型和基础设施分开，避免初学者把"Agent 智能"全归功于模型
2. "反馈层"单独拎出来——很多简化图会漏掉，但它恰恰是 Agent 质量翻倍的关键
3. "编排层"在顶部覆盖整个系统——准确，它确实是全局调度者
4. 结构对称，适合入门讲解

### 4.3 这个五层图的局限

入门图没有展开的关键机制：

| 缺失的部分 | 为什么重要 |
|-----------|-----------|
| **Guides（前馈引导）** | 五层图只画了反馈控制，但 Harness 更关键的是**事前引导**：system prompt、Skills、工具描述都属于 Guides |
| **权限闸门** | Claude Code 的工具是 **permission-gated** 的。执行层不应该是"直通"，中间必须有权限判定。安全攻防的具体战术见 [Agent 安全攻防](Agent安全攻防.md) |
| **Skills / 渐进式披露** | 现代 Harness 的核心优化——按需加载指令，而不是塞满 system prompt |
| **子代理（Sub-agents）** | 编排层实际可以派生子 Agent 跑并行 / 便宜任务 |
| **观测 / 日志** | 反馈层只体现了"自修复"，生产级 Harness 还需要给人看的日志与回放 |

---

## 5. 核心设计原则：Guides + Sensors

Thoughtworks 的 Birgitta Böckeler 提出的 Harness 设计框架：

### 5.1 Guides（前馈控制）——事前引导

> 预判 Agent 可能做错什么，**在它行动前**就引导它走对路。

- **目标**：提高"首次做对"的概率
- **手段**：system prompt、Skills、工具描述、example few-shot、角色设定
- **类比**：员工入职手册、SOP、岗位说明书

### 5.2 Sensors（反馈控制）——事后纠正

> 在 Agent 行动**之后**观察结果，让它自我纠正。

- **目标**：即便第一次做错，也能自动收敛到正确结果
- **最强形式**：**为 LLM 消费优化的信号**——例如 linter 报错里直接包含"修复指令"（一种正向的 prompt injection）
- **类比**：测试反馈、代码评审、监控告警

### 5.3 两条反直觉的洞见

**洞见 1：Agent 并不讨厌被微观管理**
> 和人类开发者不同，**约束越多、检查越多、结构越清晰，Agent 表现越好**——而不是更差。对人类团队奏效的"lean & minimal"直觉，在 Agent 身上反而是减分项。

**洞见 2：自我验证是最强杠杆**
> Boris Cherny（Claude Code 作者）说：给模型一种**验证自己工作**的方式（跑测试、看 lint、调 API 验证返回），**质量直接提升 2–3 倍**。

### 5.4 两种控制手段的成本光谱

| 类型 | 示例 | 特点 |
|------|------|------|
| **Computational**（计算型） | 静态类型检查、单元测试、lint | 确定、快、便宜 |
| **Inferential**（推断型） | AI 驱动的语义 review、LLM-as-judge | 慢、贵，但能抓住语义层面的问题 |

**原则**：先用便宜的计算型控制尽可能多的情况，把贵的推断型控制留给真正需要语义判断的部分。

### 5.5 实操速查：常见 Harness 错误与正确做法

> 借鉴自社区「六层架构」视角（来源 B 站「code 秘密花园」+ LINUX DO `@bushishisan` 整理稿，**资料日期 2026-04-08**，作者声明含 AI 生成内容；原稿与本文五层架构约 60% 重叠，本节只吸收 3 处与本文真正互补的实操内容。）

#### 5.5.1 Guides 的具体化：上下文的三层组织

把 § 5.1 Guides 进一步切成三类信息分类隔离——Agent 出错时也容易定位是哪一层的问题：

| 层 | 职责 | 典型内容 |
|---|---|---|
| **规则层** | 不可逾越的硬边界 | 技术红线、安全约束、架构原则 |
| **状态层** | 当前任务的进度追踪 | 完成了什么、阻塞是什么、下一步 |
| **证据层** | 支撑结论的外部依据 | 文档、测试结果、日志、用户反馈 |

> **反例**：200 条对话混在一起，规则 / 状态 / 证据全纠缠 → Agent 抓不住重点，幻觉率上升。
> **正例**：分清"别动数据库（规则）/ 正在修 bug（状态）/ 错误日志（证据）"。

#### 5.5.2 记忆与状态：3 类生命周期不要混用

§ 6 补强版架构图里的「记忆层」可以再细分成三类，不同生命周期不能用同一存储：

| 分类 | 生命周期 | 示例 |
|---|---|---|
| 当前任务状态 | 任务结束即销毁 | 任务进度、当前阶段、已完成步骤 |
| 会话中间结果 | 会话结束即销毁 | 用户需求记录、已生成代码片段 |
| 长期记忆 | 跨会话持久化 | 用户偏好、项目背景、技术栈 |

**4 大踩坑**：

| 错误做法 | 后果 | 正确做法 |
|---|---|---|
| 不保存中间结果 | 相同问题要重复查 / 重复算 | 每轮对话结束前保存到会话状态 |
| 三种状态混用 | 用户偏好被任务数据覆盖 | 用独立存储区隔三类 |
| 长期记忆不更新 | 用过时偏好导致答非所问 | 每次交互后更新长期记忆 |
| 状态丢失无感知 | 任务中断后无法恢复 | 定期检查状态完整性，断点可查 |

> 📎 这里是从"**存储生命周期**"角度给记忆分类；从"**认知架构**"角度（工作 / 短期 / 长期 × 情节 / 语义 / 程序记忆、读写遗忘循环、「记忆 vs 上下文 vs RAG」辨析）的展开见 [Agent 记忆体系](Agent记忆体系.md)。

#### 5.5.3 失败类型 → 恢复策略对照表（Sensors 的工程化）

§ 5.2 Sensors（反馈控制）落到工程上，需要按失败类型选不同的恢复策略——**不是所有失败都该重试**：

| 失败类型 | 检测方法 | 恢复策略 |
|---|---|---|
| 超时失败 | 执行时间超阈值 | 指数退避重试，最多 3 次 |
| 资源不足 | 内存 / CPU 超限 | 等待资源释放后重试，或降级处理 |
| 工具调用失败 | 工具返回错误码 | 检查工具状态，可切换备用工具 |
| 逻辑错误 | 输出校验不通过 | 记录错误模式，尝试替代方案 |
| 不可恢复错误 | 权限不足、参数非法 | 直接返回错误，不重试 |

**关键洞察**：双重校验（执行前 + 执行后）成本不对称——前置校验防无效执行浪费资源，后置校验保输出质量；便宜的前置校验能省下 90% 的事后清理工作。

---

## 6. 补强版 Harness 架构图

把前面五层图扩展成一个**更贴近真实生产级 Harness** 的结构图：

```
┌─────────────────────────────────────────────────────────┐
│                  编排层 (Orchestrator)                   │
│         · 调度循环   · 子代理派生   · 并发管理             │
├───────────┬──────────────────────────────────┬──────────┤
│           │                                    │          │
│           │         Guides (前馈控制)          │          │
│           │   System Prompt · Skills · 模板   │          │
│           │                                    │          │
│  记忆层    │      ┌────────────────────┐       │  执行层   │
│ Context   │      │                    │       │  Tools   │
│ + 压缩    │      │    大模型 LLM       │◄──────┤ +权限闸门 │
│ + Cache   │      │                    │       │ + MCP    │
│           │      └────────────────────┘       │          │
│           │                                    │          │
│           │        Sensors (反馈控制)          │          │
│           │   测试 · Lint · 错误回灌 · 重试     │          │
│           │                                    │          │
├───────────┴──────────────────────────────────┴──────────┤
│              反馈层 + 观测 / 日志 / 回放                   │
└─────────────────────────────────────────────────────────┘
                         AI Agent
```

补强版架构图把五层图缺失的三个关键部分补上了：
1. **Guides / Sensors 的二分**显式化
2. **权限闸门**作为执行层的必经通道
3. **观测层**作为反馈层的生产级配套

---

## 7. Harness 的典型组件清单

### 7.1 Skills（技能 / 渐进式披露）

**要解决的问题**：把所有指令都塞 system prompt，上下文会被提前消耗完。

**做法**：
- 把知识、指令、工具打包成"技能单元"
- Agent 只在**判断需要时**才加载对应技能
- 类比：人类的专业知识不是全部记在脑子里，而是"知道什么时候查什么书"

### 7.2 Sub-agents（子代理）

**要解决的问题**：
- 成本：不是所有任务都值得调用 Opus
- 上下文污染：子任务的中间过程不应该占用主会话窗口

**做法**：
- 主会话用贵模型（Opus）做规划、编排
- 派生子代理用便宜模型（Sonnet / Haiku）做具体活儿
- 子代理返回**摘要结果**给主会话，中间过程不回流

### 7.3 MCP Servers（Model Context Protocol）

**作用**：用标准协议把外部服务接进 Agent。

**两种形态**：
- **本地 MCP**：运行在本机，操作本地文件、执行命令
- **远程 MCP**：HTTP 连接，对接 Linear、Sentry、GitHub、Notion 等 SaaS

**机制要点**：MCP 把工具描述、参数 schema 注入到 Agent 的 system prompt，Agent 自动学会何时调用。

### 7.4 Error Correction Loops（错误纠正循环）

标准模式：

```
测试失败 → 模型读取错误 → 分析根因 → 生成修复 → 重跑测试
     ↑                                                │
     └────────────────────────────────────────────────┘
                 循环直到通过 或 达到重试上限
```

**关键点**：错误信息要以 LLM 能高效消费的方式呈现（结构化、带上下文、带建议），否则循环效率很低。

### 7.5 工具层的"有主见"

**反例**：直接给模型裸 `bash` 访问。
- 噪声大、结果不可预测
- 难以并发
- 危险操作无保护

**正例**（Claude Code 的做法）：
- 提供 40 个**经过验证、语义明确**的工具
- 工具内部做**并发安全**处理
- 每个工具有**明确的权限等级**（read / write / destructive）

### 7.6 全景对照：harness 的"八大器官系统"

把几篇有代表性的文章对齐看（词源见 § 1.1），大家其实在同一套"器官系统"上打转。下表可以当作 harness 组件的**完整性自查清单**——审视自己的 Agent 系统时逐行问"这个器官有没有、归谁管"：

| # | 器官 | 管什么 | 本文对应章节 / 补充 |
|---|------|--------|-------------------|
| 1 | **System prompt 与指令分层** | 不是"你是一个有帮助的助手"式人格设定，是**分层的运行时规章**：身份 / 工具权限 / 工程约束分段书写、按优先级组装、层与层有清楚的覆盖关系 | § 5.1 Guides。把 prompt 当控制面的一部分而不是文字魔法，是与传统 prompt engineering 的明确分界 |
| 2 | **Query loop（运行时主循环）** | Agent 不是"请求-响应"问答，是带状态的循环体：messages、tool use context、compact tracking、turn count | § 4.1 编排层。没有这个循环，Agent 只是带工具的 chatbot |
| 3 | **工具系统** | 工具不是模型能力的自然延伸，是**受管执行单元**：被调度、被授权、被限制并发、被审计 | § 7.5。高风险工具（如 Bash）要施加高密度行为规约 |
| 4 | **上下文治理** | 工作记忆、长期记忆、压缩策略、跨轮会话状态。context compact 不是可选优化，是长时运行 Agent 的**生存器官** | § 5.5.1 / § 5.5.2。认知角度的展开见 [Agent 记忆体系](Agent记忆体系.md) |
| 5 | **权限与沙箱** | 决定模型犯错时**后果的范围**：宿主机还是 Docker 沙箱、自动执行还是高危弹窗、任意路径还是限定项目目录 | § 6 权限闸门。Codex 走得更远，把审批做成独立的 execpolicy 模块（Policy / Rule / Evaluation / Decision，接近一门小政策语言） |
| 6 | **错误恢复** | **失败是日常天气，不是异常**：超 token、prompt too long、工具拒绝、用户打断、hook 阻塞、API 重试——失败路径要当主路径设计 | § 7.4 纠错循环 + § 5.5.3 失败类型→恢复策略对照表 |
| 7 | **多代理编排与验证** | 实现者天然倾向相信自己的改动"差不多行了"，模型更是如此——**验证要成为独立阶段，最好由独立代理承担** | § 7.2 子代理。呼应 [LLM 典型失败模式](LLM典型失败模式.md) 的"自我汇报偏差" |
| 8 | **本地规则与 hook** | CLAUDE.md / AGENTS.md 项目级配置 + pre-commit / session-start 等生命周期钩子：把"组织习惯"写进系统，新人不用重学项目规矩 | § 2.2 项目 harness 层 |

八个器官不是独立模块，是一个循环系统：prompt 定义行为协议 → query loop 负责执行 → 工具系统决定能触碰什么 → 上下文治理决定记忆如何流动 → 权限决定错误后果的范围 → 恢复机制处理错误本身 → 多代理把不确定性分区 → 本地规则把经验沉淀下来。**少了任何一个，系统就在那个方向上漏风**。

---

## 8. 为什么 Harness 是新的 AI 护城河

```
同一个 Claude API key
    │
    ├─── 开发者 A：简单 prompt-response 循环 → 玩具级 demo
    │
    └─── 开发者 B：工具 + 自动测试 + 错误纠正 + 持久记忆 → 生产力工具
```

差距的全部来源于 Harness 的工程深度，**和模型本身无关**。

**商业逻辑**：
- 开源模型正在快速追平闭源模型（性能差距在缩小）
- 多家厂商提供智力接近的模型
- **下一个差异化的战场是"模型周围的一切"**

这就是为什么 Anthropic 对 Claude Code 源码被泄露反应那么剧烈——**那 51 万行代码是真正的护城河**，不是模型权重。

---

## 9. 未来：Harness 会被模型吞并吗

**常见疑问**：模型越来越强，Harness 里做的事（工具调用、上下文管理、自修复）会不会被模型内置掉，以至于 Harness 变得不必要？

**LangChain 的 Harrison Chase 的反向观点**：

> Claude Code 现在已经 **51 万行代码**，这是一个**随着模型变强而持续增长的 Harness，不是缩小的**。
>
> **更强的模型会扩展 Harness 需要做的事，而不是取代 Harness 的必要性。**

为什么：
- 模型越强 → 能被委托的任务更复杂 → Harness 要管理的状态/工具/约束更多
- 模型越强 → 用户对质量要求更高 → 需要更多的 Guides 和 Sensors
- 模型越强 → 和外部系统的集成需求越多 → MCP / 工具层越厚

**结论**：Harness Engineering 是一个**随 AI 能力一起增长的长期工程学科**，不是过渡方案。

---

## 10. 与本知识库其他章节的关联

| 相关章节 | 关联点 |
|---------|-------|
| [Skill工程化设计与失效防御](Skill工程化设计与失效防御.md) | 那篇的四道防线（Session Discipline / 薄壳 / SessionStart hook / PreToolUse hook）全部属于 harness 层，是本文 Guides 与 Sensors 框架的具体落地 |
| [00_核心概念/上下文窗口与Token计费](../00_核心概念/上下文窗口与Token计费.md) | Harness 的"记忆层"核心就是上下文工程；Prompt Caching 是降低 Harness 运行成本的关键 |
| [02_提示词工程/](../02_提示词工程/) | Prompt Engineering 是 Harness Engineering 的**最内层**——这篇笔记解释了为什么提示词工程是"必要但不充分"的 |
| [03_应用实践/RAG/](../03_应用实践/RAG/) | RAG 本质是"记忆层"的一种具体实现——把外部知识喂进上下文 |
| [05_技术基础/软件架构设计详解.md](../05_技术基础/软件架构设计详解.md) | Harness Engineering 本质是"软件架构"在 AI 时代的新分支——分层、关注点分离、可替换性等原则同样适用 |
| [Multi-Agent 工程实战与 Persona 设计](Multi-Agent工程实战与Persona设计.md) | 五层架构的多 Agent 落地案例:**记忆层**对应"共享真相源",**编排层**对应"R&D 流水线",**执行层**对应"任务二分法"(脚本 vs AI) |
| [Function Calling 与 MCP 工程指南](Function%20Calling与MCP工程指南.md) | **执行层**的具体实现——工具调用协议、御三家差异、MCP "USB 化"工具生态 |
| [极简可控的 Coding Agent 设计（pi）](极简可控的Coding-Agent设计-pi.md) | **极简派落地案例**:pi 是一个真实 harness,把"可观测/状态外置/上下文工程"做到极致——系统提示词 < 1000 token、只留 4 个工具,反向印证 Harness 工程"控制什么进上下文"的核心命题 |
| [Loop Engineering 与四代演化](Loop%20Engineering与四代演化.md) | **Harness 之后的下一跃迁**：Loop 把"目标定义 + 定时驱动"叠在 harness 之上；§ 2.2 的任务 harness 层正是 Loop 的作业面 |
| [Agent 发展轨迹四阶段](Agent发展轨迹四阶段.md) | § 1.1 的"瓶颈迁移"（prompt → context → harness）是那篇四阶段史观的另一种讲法，两文互为印证 |

---

## 11. 延伸阅读

### 权威一手资料
- Martin Fowler / Thoughtworks — [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html)（Böckeler 的 Guides/Sensors 框架原文）
- Mitchell Hashimoto — 《My AI Adoption Journey》（2026-02-05，"Engineer the harness" 的首次提出）
- OpenAI（Ryan Lopopolo）— 《Harness Engineering: Leveraging Codex in an Agent-First World》（2026-02-11，让术语出圈的工程报告）
- Anthropic — 《Effective harnesses for long-running agents》（2026-03-24，长时运行 harness 研究）
- swyx — agent engineering / IMPACT 框架（2025-03，harness engineering 的前传）
- Viv Trivedy（LangChain）— 《The Anatomy of an Agent Harness》（"Agent = Model + Harness" 公式的推广来源）
- Firecrawl — [What Is an Agent Harness?](https://www.firecrawl.dev/blog/what-is-an-agent-harness)
- HumanLayer — [Skill Issue: Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)

### Claude Code 泄露事件分析
- TechTalks — [Why harness engineering is becoming the new AI moat](https://bdtechtalks.com/2026/04/06/ai-harness-engineering-claude-code-leak/)
- Productboard — [Harness Engineering Explained: What the Claude Leak Means](https://www.productboard.com/blog/what-the-claude-clode-leak-means-for-product-managers/)
- GitHub — [Learn Claude Code: Harness Engineering for Real Agents](https://github.com/shareAI-lab/learn-claude-code)

### 中文深度解读
- 张涵东 — [Harness Engineering: From Claude Code Internals](https://zhanghandong.github.io/harness-engineering-from-cc-to-ai-coding/en/)
- 《什么是 Harness Engineering：聊聊最近爆火的技术词》（2026 年年中词源考据长文，本文 § 1.1 / § 1.2 / § 2.1 / § 2.2 / § 7.6 的主要来源；无公开链接，原文以 PDF 存档）

---

## 附录：关键术语速查

| 术语 | 中文 | 一句话解释 |
|------|------|---------|
| Harness | 脚手架 / 挽具 | 模型之外让 Agent 能工作的一切 |
| Agent | 智能体 | Model + Harness 的整体 |
| Orchestrator | 编排层 | 调度循环的大脑 |
| Guides | 前馈控制 | 事前引导（system prompt、Skills、工具描述） |
| Sensors | 反馈控制 | 事后纠正（测试、lint、错误回灌） |
| MCP | 模型上下文协议 | Agent 接入外部工具/服务的标准协议 |
| Skills | 技能 / 渐进式披露 | 按需加载指令，不把所有东西塞进 system prompt |
| Sub-agent | 子代理 | 派生的、运行小任务的子 Agent |
| Permission Gate | 权限闸门 | 工具执行前的权限判定点 |
| Query Loop | 运行时主循环 | 带状态的循环体（messages / 压缩追踪 / 轮次计数），Agent 与 chatbot 的分界 |
| IMPACT | swyx 六维框架 | Intent / Memory / Planning / Authority / Control Flow / Tools，2025 年的 harness 前传 |
| execpolicy | 执行策略模块 | Codex 把工具审批与执行限制做成的独立政策引擎 |

---

*最后更新: 2026-07-06（新增 § 1.1 词源考据时间线 + swyx IMPACT 前传、§ 1.2 三种解释口径、§ 2.1 三层楼板视角、§ 2.2 通用/项目/任务三层划分、§ 7.6 八大器官对照；修正 § 3 "泄露=词源"叙事为"泄露=催化剂"。来源：《什么是 Harness Engineering：聊聊最近爆火的技术词》考据文）*
*归属模块: 06_Agent工程*
