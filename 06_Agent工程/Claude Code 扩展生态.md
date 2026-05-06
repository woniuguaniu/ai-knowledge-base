# Claude Code 扩展生态

> 系统讲清 Claude Code 的 **5 大扩展机制**：Skill / MCP / CLI / SubAgent / Hook，以及把它们打包整合的 **Plugin**。
> 看完这篇你能回答：每种是什么、解决什么问题、它们是什么关系、什么时候用哪个。

---

> ## 📌 知识通用度提示
>
> 本文聚焦 **Claude Code (CC)**，但其中很多知识对 **Codex CLI / Gemini CLI** 也有效。读前先分清边界：
>
> | 内容 | 通用度 | 说明 |
> |---|---|---|
> | **5 大机制的概念**（Skill / MCP / SubAgent / Hook / Plugin 是什么、解决什么问题） | 🟢 全通用 | 这是行业范式，三家都有对应实现 |
> | **MCP 协议本身** | 🟢 全通用 | Anthropic 提出，已成事实标准，OpenAI / Google 都在跟进 |
> | **Tool Use / 渐进式披露 / SubAgent 派生** 等设计思想 | 🟢 全通用 | LLM Agent 通用模式 |
> | **`/agents` `/plugin` `/btw`** 等斜杠命令 | 🔴 CC 独有 | 各家命令体系不同 |
> | **`claude mcp add/list/remove`** 命令语法 | 🔴 CC 独有 | Codex / Gemini 的 MCP 命令格式不同 |
> | **`CLAUDE.md`** 项目记忆机制 | 🟡 思想通用 | Codex 有 `AGENTS.md`，Gemini 有 `GEMINI.md`，命名和细节有差异 |
> | **「秋瓷团」案例的目录结构**（`.claude/agents/`）| 🔴 CC 独有 | 目录路径是 CC 约定 |
>
> **一句话**：**思想全通用，命令各家不同**——换工具时概念直接迁移，命令需要重新查文档。
> 三家协同玩法详见 [多CLI联动.md](../05_技术基础/多CLI联动.md)。

---

## 阅读指南

- **完全新手**：按顺序看 一 → 二 → 八（关系总图）
- **想直接动手**：跳【二】扩展生态总图 + 【七】Plugin（最快上手）
- **要做选型**：直接看【八】对比表 + 选型建议
- **配套实战**：参见 `Claude Code 实战速查.md`（指令、模型切换、应用场景）

---

## 一、为什么 Claude Code 需要"扩展机制"

Claude Code 默认只是一个**会聊天 + 能调用基本工具**（读写文件、跑 Bash 等）的命令行 AI。
但真实工作场景千差万别——你想让它：

- 帮你**写设计稿**（需要前端审美知识）
- 帮你**操作飞书**（需要飞书 API 接口）
- 帮你**用别家 LLM**（需要桥接外部 CLI）
- 让 Agent **自动 review 代码**（需要派一个分身去做）
- **代码提交前自动跑格式化**（需要钩子触发器）

这些都不是"再聊几轮"能解决的——**需要给 CC 装上"扩展插槽"**。这就是 5 大扩展机制存在的意义。

> 💡 一句话：**5 大扩展机制 = CC 的"USB 接口"**——按需插入不同的能力。

---

## 二、5 大扩展生态总图

先看全景，再逐个展开。

```
                    Claude Code（裸机）
                    ┌─────────────────┐
                    │  LLM + 基础工具  │
                    └────────┬────────┘
                             │
      ┌──────────┬───────────┼──────────┬──────────┐
      ▼          ▼           ▼          ▼          ▼
   ┌──────┐  ┌─────┐    ┌──────────┐ ┌─────┐  ┌──────┐
   │Skill │  │ MCP │    │SubAgent  │ │Hook │  │ CLI  │
   │ 技能 │  │协议 │    │ 子代理   │ │钩子 │  │工具链│
   └──────┘  └─────┘    └──────────┘ └─────┘  └──────┘
      │          │           │          │          │
      └──────────┴─────┬─────┴──────────┘          │
                       │                           │
                       ▼                           │
                  ┌─────────┐                      │
                  │ Plugin  │ ← 整合包             │
                  └─────────┘                      │
                                                   │
                       桥接外部 ──────────────────►│
                       (Codex, Gemini, 飞书 CLI…)
```

### 核心金句（必记）

> **Plugin = Skill + SubAgent + Hook + MCP 的整合包**

这句话直接讲清了 5 + 1 个机制的层级关系：
- **Skill / SubAgent / Hook / MCP** 是**原子能力**（单点功能）
- **Plugin** 是**组合包**（把上述原子打包给别人用）
- **CLI** 略特殊——是**外部工具桥接**，不是 CC 内的扩展点

---

## 三、Skill（技能）——给 CC 装"专业知识"

### 3.1 是什么

**Skill = 一个文件夹**，包含 `SKILL.md`（用法说明）+ 可选的脚本/资源文件。
CC 看到 SKILL.md 中描述的"触发场景"匹配你的请求，就**自动加载这个 Skill 并按它的说明执行**。

> 类比：Skill 是给 CC 的**"专家手册"**——平时不看，遇到对应场景才翻。

### 3.2 解决的问题

不需要塞一坨指令到 system prompt（占 context 还容易遗忘）——**按需加载**。这就是 **渐进式披露（Progressive Disclosure）** 思想。

例子：你问"帮我画一张算法流程图"，CC 自动加载 `algorithmic-art` Skill，按里面写好的 p5.js 套路生成代码。

### 3.3 推荐 Skill

| Skill 名 | 功能 |
|---|---|
| **Find-Skill** | 帮你查找/安装其他 Skill（Skill 的"应用商店检索器"）|
| **Frontend-Design** | 创建有设计感的前端界面 |
| **Skill-Creator** | 帮你创建/改进自己的 Skill |
| **卡帕西 Skill** | 依据 Andrej Karpathy 经验提升 CC 编码表现 |

**Skill 合集站**：[lobehub.com/zh/skills](https://lobehub.com/zh/skills)

### 3.4 怎么装

**两种作用域**：
- **项目级 Skill** → 放到当前项目的 `.claude/skills/<name>/` 下，仅本项目生效
- **全局级 Skill** → 放到 `~/.claude/skills/<name>/` 下，所有项目都能用

**最简方法**：把 GitHub 仓库链接直接发给 CC，让 CC 自己 clone 到对应目录。

---

## 四、MCP（Model Context Protocol）——给 CC 接"外部世界"

### 4.1 是什么

**MCP = AI 世界的 USB 接口标准**——由 Anthropic 提出的协议，让任何 AI（不只是 Claude）能用统一方式调用外部工具/数据源。

> 类比：USB 协议让任何 U 盘都能插进任何电脑。MCP 让任何符合标准的服务都能接进任何 AI。

### 4.2 解决的问题

不写 MCP 之前：每接一个新服务（飞书、GitHub、数据库），都要写一套定制的 Function Calling 代码。
写了 MCP 之后：一次实现，多家 AI 共用——**生态化标准化**。

### 4.3 两种 MCP

| 类型 | 跑在哪 | 例子 |
|---|---|---|
| **本地 MCP** | 你电脑上 | 文件系统 MCP、本地数据库 MCP |
| **远程 MCP** | 通过 HTTP 连云端 | 飞书 MCP、Linear MCP、GitHub MCP |

> 📌 与本知识库其他章节的关系：[Harness工程与Agent解剖.md](Harness工程与Agent解剖.md) 7.3 节讲了 MCP 在 Harness 中的位置；[程序员黑话速查.md](../05_技术基础/程序员黑话速查.md) 第 346 行有 MCP 词条。

### 4.4 装/查/删命令（实战必记）

```bash
# 通用安装格式（HTTP 类）
claude mcp add --transport http <MCP名称> "<MCP_URL>"

# 通用安装格式（命令行类，本地起服务）
claude mcp add <名称> -- npx -y <包名> <参数...>

# 查看已装 MCP
claude mcp list          # 在 CC 外执行
/mcp                     # 在 CC 内执行（命令模式）

# 删除已装 MCP
claude mcp remove <完整名称>
# ⚠️ 名称必须和 add 时一模一样
```

### 4.5 4 个实战安装例子

#### 例 1：即梦 MCP（AI 出图）

```bash
claude mcp add --transport http hans-m-yin-jimeng-mcp "<你的 Smithery 带密钥 URL>"
```
- 去 [即梦 AI](https://jimeng.jianying.com/) 拿 sessionid → 输入到 [Smithery 即梦页面](https://smithery.ai/server/@Hans-M-Yin/jimeng-mcp) → 拿到带密钥的 URL
- ⚠️ sessionid 会过期，过期后重新登录拿新的

#### 例 2：飞书 MCP

```bash
# Mac
claude mcp add lark-mcp -- npx -y @larksuiteoapi/lark-mcp mcp -a <app_id> -s <app_secret> --oauth

# Windows
claude mcp add lark-mcp -- cmd /c "npx -y @larksuiteoapi/lark-mcp mcp -a <app_id> -s <app_secret> --oauth"
```

**前置准备**（这一步最繁琐）：
1. 去 [飞书开发者后台](https://open.feishu.cn/app) **创建应用** → 拿 `app_id` 和 `app_secret`
2. **添加机器人能力**
3. **开通权限**：`im:message`（消息）、`base:app`（多维表格）、`docs:document`（云文档）、`im:chat`（群）、`contact:user.id`（用户 ID）
4. **发布应用**
5. 去 [飞书开发文档](https://open.feishu.cn/document/home/index) 拿你自己的**个人 ID**（让 Agent 知道发消息给谁）

#### 例 3：天气 MCP

```bash
claude mcp add --transport http harun-guclu-weather-mcp "<Smithery 带密钥 URL>"
```
URL 来源：[smithery.ai 天气 MCP 页面](https://smithery.ai/server/@HarunGuclu/weather_mcp)

#### 例 4：网页爬取 MCP（Firecrawl）

```bash
claude mcp add --transport http krieg-2065-firecrawl-mcp-server "<Smithery 带密钥 URL>"
```
URL 来源：去 [Firecrawl 官网](https://www.firecrawl.dev/) 拿 API key → 输入 [Smithery Firecrawl 页面](https://smithery.ai/server/@Krieg2065/firecrawl-mcp-server)

### 4.6 通用模式总结

> **9 成 MCP 安装都遵循这个套路**：
> 1. 在 [Smithery](https://smithery.ai/) 找到要装的 MCP
> 2. 选 "Claude Code"，复制安装命令
> 3. 大多数需要先去服务方拿 API key，填到 Smithery 配置里
> 4. 拿到带密钥的 URL，粘贴到 `claude mcp add` 命令里执行

---

## 五、CLI 命令行工具——让 CC 用别家的"嘴和手"

### 5.1 是什么

CLI 不是 CC **内部**的扩展点，而是**外部命令行工具**——CC 可以通过 Bash 调用它们，等于给 CC 装上"外语翻译"和"跨家协作"能力。

> 类比：CC 是经理，CLI 是它能调遣的**外协工具**。

### 5.2 解决的问题

- **跨家协同**：让 Claude 调 Codex、调 Gemini，用别家模型的特殊能力
- **垂直工具**：让 CC 操作飞书、GitHub、特定 SaaS 服务

### 5.3 推荐 CLI

| CLI 名 | 功能 |
|---|---|
| **飞书 CLI** | 飞书官方工具，覆盖消息/文档/多维表格/电子表格/幻灯片/日历/邮箱/任务/会议 9 大业务域，200+ 命令 + 24 个 AI Agent Skill |
| **OpenCLI** | "万能命令行工具箱"——把任何网站/桌面应用/本地程序变成统一的命令行操作界面 |
| **GitHub CLI（gh）** | GitHub 官方工具，把 PR、Issue 等 GitHub 概念带到终端 |
| **Gemini CLI** | Google 官方，把 Gemini 模型能力直接引入终端 |

**找更多 CLI**：[GitHub CLI 主题页](https://github.com/topics/cli)

### 5.4 怎么用

**最简方法**：把 GitHub 仓库链接发给 CC，让它自己装、自己读 README、自己引导你用。

> 📌 与本知识库其他章节的关系：[多CLI联动.md](../05_技术基础/多CLI联动.md) 详细讲了 Claude/Codex/Gemini 三家协同的 4 种玩法（管道接力 / MCP 互调 / 三方投票 / 角色分工）。

---

## 六、SubAgent（子代理）——CC 的"分身派遣"

### 6.1 是什么

**SubAgent = CC 主会话派生出的子 AI**，跑特定任务，结果回来再交给主会话。

> 类比：你是项目经理，subagent 是你派出去做具体活儿的实习生——做完汇报结果，过程不用你管。

### 6.2 解决的问题

- **并发**：多任务并行，不堵主会话
- **隔离**：subagent 用单独的 context，不污染主上下文
- **降本**：subagent 可以用便宜模型（Sonnet / Haiku）做具体活儿，主会话用贵模型（Opus）做编排

### 6.3 两种创建方式

| 方式 | 触发 | 适合 |
|---|---|---|
| **自动派生** | CC 判断任务复杂、有并行可能时**自动调用** | 大部分日常场景 |
| **手动创建** | 你输入 `/agents` 进 Library 界面创建 | 想固化某个特定角色（如"代码 reviewer"）|

### 6.4 手动创建 7 步流程

1. 输入 `/agents` 进 Library
2. 选择**项目级**（仅本项目用）或**全局级**（所有项目共用）
3. 选 **AI 辅助创建**——让 AI 根据你的描述生成 subagent 配置
4. **描述功能**：你想要这个 subagent 干什么
5. **决定工具权限**：勾选哪些工具它能用（Read / Write / Bash / WebFetch...）
6. **选模型**：一般 Sonnet 够用；如果用 CC Switch 配置了网关，选哪个都一样
7. **选颜色**：方便在终端里区分主 Agent 和子 Agent

### 6.5 实战案例：「秋瓷团」5 角色协作

一个把 subagent 用得很妙的真实工作流案例——**5 个角色在一天内依次上场**：

```
早上：
  "新闻秋"  → 全网搜刮 AI 新闻 → 总结成文档 → 飞书推送给我
   ↓
  "穿搭秋"  → 问我今天去什么场合 → 查天气 → 给穿搭建议
   ↓
  "教练秋"  → 催我报体重 → 记录健康数据 → 推荐运动+外卖
   ↓
  "日报秋"  → 问我今天大体安排 → 规划成日程早报 → 发到工作群

晚上：
  "反思秋"  → 根据今天发生的事 + 各种文档 → 引导我复盘反思
```

**为什么这个案例有价值**：
- 展示了 subagent 不是"一次性派工"，可以**编排成日常工作流**
- 每个 subagent **职责单一**（符合 SRP 单一职责原则）
- 通过 **MCP（飞书）+ SubAgent（5 角色）** 组合实现，体现了多机制协同

### 6.6 启动技巧

```bash
# 跳过所有权限询问（⚠️ 高危）
claude --dangerously-skip-permissions
```

> ⚠️ 这个 flag 等于**核武器**——所有写操作不再问你。仅在你完全信任的隔离环境用（如 Docker、虚拟机）。

---

## 七、Hook（钩子）——CC 的"自动触发器"

### 7.1 是什么

**Hook = 在 CC 生命周期的某个时刻自动执行的脚本**。
事件来了 → CC 自动跑你设的钩子 → 钩子干完活再继续。

> 类比：自动门感应器——人靠近就开门，不用你按按钮。

### 7.2 常见事件

| 事件 | 触发时机 |
|---|---|
| **PreToolUse** | 工具调用前（可拦截）|
| **PostToolUse** | 工具调用后 |
| **UserPromptSubmit** | 你提交问题前 |
| **SessionStart** | 会话开始 |
| **Stop** | CC 停止响应 |
| **PreCompact** | 上下文压缩前 |

### 7.3 解决的问题

- **自动化重复操作**：每次写完代码自动跑 prettier 格式化
- **安全拦截**：删除前自动备份，防误删
- **状态通知**：任务完成响铃提醒，不用盯着屏幕
- **强制规则**：提交前必须跑 lint，不通过不让提交

### 7.4 两个实用例子

#### 例 1：完成提示音

```
设置一个 hook，每次完成任务之后，
都自动执行一个声音脚本，发出提示音"叮"进行提醒
```
直接把这句话发给 CC，它会自动配置 settings.json。

#### 例 2：提交前格式检查

```
设置一个 hook，每次提交代码之前，
都会自动触发代码格式的检查
```

### 7.5 高阶玩法

钩子有 5 种类型：
- **command**：跑 shell 命令（最常用）
- **prompt**：让 LLM 评估条件
- **agent**：派 subagent 验证
- **http**：POST 到指定 URL
- **mcp_tool**：调 MCP server 工具

> 钩子配在哪：`~/.claude/settings.json`（全局）或 `.claude/settings.json`（项目）的 `hooks` 字段。

---

## 八、Plugin（插件）——5 大机制的"整合包"

### 8.1 是什么

**Plugin = 把 Skill / SubAgent / Hook / MCP 打包到一起，一键安装/分发**。

> 类比：Skill/Hook/MCP 是单独的乐高积木，Plugin 是组好的"机器人套装"——想用一整套能力时，装一个 Plugin 就够。

### 8.2 解决的问题

- 一个完整场景往往**需要多种机制配合**（如"代码安全审查" = Hook 拦截 + Skill 经验 + SubAgent 验证）
- 用户不用一个个去装——**整合包一次性给齐**

### 8.3 怎么管

```
/plugin
```
进入插件管理界面：
- 浏览/搜索官方 + 社区插件
- 一键安装/卸载
- 管理已装插件的开关

### 8.4 官方推荐插件

| 插件 | 功能 |
|---|---|
| **commit-commands** | 简化 Git 工作流（提交、推送、创建 PR）|
| **content-creator** | 跨平台内容创作（博客、视频脚本、社交媒体）|
| **security-guidance** | 安全提醒钩子，编辑文件时提示潜在的命令注入、XSS、不安全模式 |

### 8.5 找更多插件

- 官方：[claude.com/plugins](https://claude.com/plugins#plugins)
- 第三方导航：[Claude Code Plugins](https://claudecodeplugins.dev/zh)

---

## 九、5 大机制对比与选型

### 9.1 对比表

| 机制 | 本质 | 加载方式 | 写难度 | 典型场景 |
|---|---|---|---|---|
| **Skill** | 文件夹（说明 + 资源）| 按描述自动触发 | 低 | 给 CC 灌输专业知识 |
| **MCP** | 协议 + 服务 | 启动时连接 | 中 | 接外部 API/数据源 |
| **CLI** | 外部命令行工具 | CC 用 Bash 调 | —（用现成的）| 跨家 AI / 垂直工具 |
| **SubAgent** | 子 LLM 会话 | 自动派生 / `/agents` | 低 | 并发任务、降本、隔离 |
| **Hook** | 事件触发的脚本 | 配置后自动 | 中 | 自动化、拦截、通知 |
| **Plugin** | 上述 4 种打包 | `/plugin` 安装 | 高 | 完整场景一键部署 |

### 9.2 选型决策树

```
我的需求是？
│
├─ "想让 CC 懂某个领域"（如设计、特定算法）
│   → Skill ⭐
│
├─ "想让 CC 操作某个外部服务"（飞书、GitHub、数据库）
│   → MCP ⭐
│
├─ "想用别家 AI 模型 / 垂直工具"
│   → CLI（让 CC 调用）
│
├─ "想让 CC 派分身做并行任务"
│   → SubAgent ⭐
│
├─ "想在某个事件自动做点什么"（提交前检查、完成提示）
│   → Hook ⭐
│
└─ "上面几种都要，且别人也能用"
    → 打包成 Plugin
```

### 9.3 渐进学习路径（小白推荐顺序）

```
第 1 周：Skill          ← 装现成的最容易出效果
第 2 周：MCP            ← 接 1 个你常用的服务（飞书 / GitHub）
第 3 周：SubAgent       ← /agents 创建 1 个固定角色
第 4 周：Hook           ← 加 1 个完成提示音
第 N 周：Plugin / CLI   ← 按需深入
```

**核心建议**：**别一上来就 5 种全装**——每装一个跑稳一周再加下一个。

---

## 十、与本知识库其他章节的关联

| 主题 | 文档 | 关系 |
|---|---|---|
| Agent 是什么 | [什么是Agent.md](什么是Agent.md) | 本文是 CC 这一具体 Agent 的扩展机制；那篇讲 Agent 通用概念 |
| Harness 工程深度解剖 | [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md) | 5 大机制都属于 Harness 范畴；那篇讲架构 |
| Agent 演进史 | [Agent发展轨迹四阶段.md](Agent发展轨迹四阶段.md) | 第三阶段→第四阶段（Context → Harness）的具体落地体现 |
| 多 CLI 联动 | [多CLI联动.md](../05_技术基础/多CLI联动.md) | CLI 章节的深入扩展 |
| MCP 词条 | [程序员黑话速查.md](../05_技术基础/程序员黑话速查.md) | MCP 简短定义速查 |
| Agent 安全攻防 | [Agent安全攻防.md](Agent安全攻防.md) | MCP 投毒等攻击手法对应到本文的 MCP 章节 |

---

## 十一、一句话终极总结

> **Skill / MCP / CLI / SubAgent / Hook 是 5 把工具——Plugin 是装着这 5 把工具的工具箱。**
>
> Claude Code 之所以从"会聊天的 AI"进化成"能干活的实习员工"，靠的不是模型变强，而是这套**生态扩展机制**让你能按需武装它。

---

## 附：核心术语速查

| 术语 | 中文 | 一句话 |
|---|---|---|
| **Skill** | 技能 | 文件夹形式的"专家手册"，CC 按需自动加载 |
| **MCP** | 模型上下文协议 | AI 世界的 USB 标准，统一接外部服务 |
| **CLI** | 命令行工具 | 外部工具，CC 用 Bash 调用 |
| **SubAgent** | 子代理 | CC 派出去的"分身"，跑特定任务 |
| **Hook** | 钩子 | 事件触发的自动脚本 |
| **Plugin** | 插件 | 上面 4 种的打包整合 |
| **渐进式披露** | Progressive Disclosure | 按需加载指令，不塞满 system prompt |
| **Smithery** | — | 主流的 MCP 应用商店 |
| **`--dangerously-skip-permissions`** | — | 跳过所有权限询问（高危）|
