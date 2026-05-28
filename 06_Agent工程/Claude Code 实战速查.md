# Claude Code 实战速查

> Claude Code 日常使用的**速查手册**——指令大全、模型切换、危险但实用的 flag、5 类场景的 MCP 应用图鉴。
> 配套阅读：原理与扩展机制详解参见 [Claude Code 扩展生态.md](Claude%20Code%20扩展生态.md)。

---

> ## 📌 知识通用度提示
>
> 本文是 **Claude Code (CC) 专属操作手册**——绝大多数命令、flag、环境变量对 Codex CLI / Gemini CLI **不通用**。
>
> | 内容 | 通用度 | 说明 |
> |---|---|---|
> | **斜杠指令**（`/clear` `/compact` `/agents` `/mcp` 等）| 🔴 CC 独有 | 各家有自己的命令体系 |
> | **`claude mcp add/list/remove`** 命令 | 🔴 CC 独有 | Codex / Gemini 的 MCP 管理命令格式不同 |
> | **`ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN`** 环境变量 | 🔴 CC 独有 | 仅对 CC 生效；3 家国产模型直连方案是因为它们模仿 Anthropic API 才适用 |
> | **`--dangerously-skip-permissions`** flag | 🔴 CC 独有 | 仅 CC 支持 |
> | **`.claude/agents/` 目录** | 🔴 CC 独有 | Codex 用 `AGENTS.md`，Gemini 用 `GEMINI.md`，目录约定不同 |
> | **「秋瓷团」5 角色协作**的设计**思路** | 🟢 通用 | 思路通用（任何 Agent 都能编排多角色），但 CC 实现细节专属 |
> | **5 类场景 MCP 应用图鉴**（视频/笔记/Word/面试/论文）| 🟢 全通用 | MCP 是协议标准，三家都能用同一批 MCP 服务 |
> | **MCP 安装的通用套路**（找市场→拿 key→装）| 🟢 全通用 | 思路通用，命令格式各家不同 |
>
> **一句话**：**这篇 70% 是 CC 专属命令操作**——换工具几乎要全部重学；想找通用思想看姊妹篇 [Claude Code 扩展生态.md](Claude%20Code%20扩展生态.md)。

---

## 阅读指南

- **第一次配 CC**：直接看【三、模型切换】
- **遇到指令忘了**：看【二、指令大全】
- **想做新场景**：看【五、5 类场景的 MCP 应用图鉴】
- **常见坑**：看【六、踩坑提醒】

---

## 一、CC 启停基础

| 操作 | 命令 |
|---|---|
| **启动** | 在终端输入 `claude` |
| **退出** | 连续 2 次 `Ctrl+C`，或输入 `/exit` |
| **跳过权限询问启动**（⚠️ 高危）| `claude --dangerously-skip-permissions` |

> ⚠️ `--dangerously-skip-permissions` 等于把所有写操作的"红绿灯"全部关掉。仅在隔离环境（Docker / 虚拟机）+ 明确知道自己在干什么时使用。

---

## 二、CC 指令大全

### 2.1 基础控制类

| 指令 | 作用 |
|---|---|
| `/help` | 提供所有指令 + 背后含义 |
| `/exit` | 退出会话 |
| `/logout` | 登出（想重新设置大模型 API 时用）|
| `/clear` | **彻底清空**当前上下文（相当于重开会话）|
| `/compact` | 主动**压缩**精简上下文（保留摘要继续聊）|
| `/resume` | 在全新窗口里恢复**之前的对话** |
| `/context` | 显示上下文详细信息（占比、类别、剩余空间）|
| `/status` | 显示 CC 详细状态（版本、模型、配置）|
| `/rewind` | 进入**回滚**界面，撤销之前的操作 |

### 2.2 模型与会话类

| 指令 | 作用 |
|---|---|
| `/model` | 切换高/中/低档模型 |
| `/btw` | "By The Way" 缩写——**临时切出**正在执行的项目，进入隔离对话；完毕后按 `esc` 消除临时会话 |

### 2.3 项目与记忆类

| 指令 | 作用 |
|---|---|
| `/init` | 初始化创建项目级 `CLAUDE.md`（让 CC 自动总结当前项目）|
| `/memory` | 管理 Claude 的**全局记忆 / 项目记忆 / Auto Memory** |

### 2.4 扩展生态类

| 指令 | 作用 |
|---|---|
| `/agents` | 创建、调用、管理 **subagent** |
| `/plugin` | 发现新插件、管理已下载插件 |
| `/mcp` | 查看已安装的 **MCP** |
| `/simplify` | 派生 3 个 subagent，从代码质量 / 运行效率 / 复用性 三个角度审核代码并自动优化 |
| **`/goal <条件>`** | **2026-05-12 新增（v2.1.139+）** 长任务原语：设完成条件，Claude 跨多轮自动循环到达成；独立 Haiku 评估器每轮判断目标是否满足（详见 [Claude Code goal命令.md](Claude%20Code%20goal命令.md)）|

### 2.5 速查口诀

> 💡 **3 个最常用**：`/clear`（重开）、`/compact`（瘦身）、`/agents`（管分身）
> 💡 **2 个救命**：`/rewind`（撤销）、`/resume`（恢复）
> 💡 **1 个秘密武器**：`/btw`（临时聊）

---

## 三、模型切换：3 家国产模型直连方案

CC 默认走 Anthropic 官方 API，但国内常见 3 种替代路径：

| 路径 | 优势 | 劣势 |
|---|---|---|
| **Anthropic 直连** | 模型最新最强 | 需要魔法上网 + 美元账单 |
| **网关代理**（anyrouter 等）| 一个 token 多家模型 | 中转有信任和延迟成本 |
| **国产模型直连** | 稳定 / 便宜 / 不需翻墙 | 模型能力略逊 Claude Opus |

下面给出 **3 家国产模型**用 Anthropic 兼容协议接 CC 的命令。设置后 CC 启动会自动用这些模型。

### 3.1 智谱 GLM 4.5

**Mac OS**:
```bash
export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="你的智谱 apikey"
```

**Windows (PowerShell)**:
```powershell
$Env:ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
$Env:ANTHROPIC_AUTH_TOKEN="你的智谱 apikey"
```

API key 获取：[bigmodel.cn](https://bigmodel.cn/)

### 3.2 Kimi K2

**Mac OS**:
```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.cn/anthropic"
export ANTHROPIC_AUTH_TOKEN="你的 Kimi apikey"
export ANTHROPIC_MODEL="kimi-k2-turbo-preview"
export ANTHROPIC_SMALL_FAST_MODEL="kimi-k2-turbo-preview"
```

**Windows (PowerShell)**:
```powershell
$env:ANTHROPIC_BASE_URL="https://api.moonshot.cn/anthropic"
$env:ANTHROPIC_AUTH_TOKEN="你的 Kimi apikey"
$env:ANTHROPIC_MODEL="kimi-k2-turbo-preview"
$env:ANTHROPIC_SMALL_FAST_MODEL="kimi-k2-turbo-preview"
```

API key 获取：[platform.moonshot.cn](https://platform.moonshot.cn/console/api-keys)

> 💡 Kimi 多了 `ANTHROPIC_MODEL` 和 `ANTHROPIC_SMALL_FAST_MODEL` 两个变量——分别指定主模型和**小快模型**（CC 内部对短任务用便宜模型省成本）。

### 3.3 Qwen3 Coder Plus（阿里通义千问）

**Mac OS**:
```bash
export ANTHROPIC_BASE_URL="https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy"
export ANTHROPIC_AUTH_TOKEN="你的阿里云百炼 apikey"
```

**Windows (PowerShell)**:
```powershell
$Env:ANTHROPIC_BASE_URL="https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy"
$Env:ANTHROPIC_AUTH_TOKEN="你的阿里云百炼 apikey"
```

API key 获取：[bailian.console.aliyun.com](https://bailian.console.aliyun.com/?tab=model#/api-key)

### 3.4 4 种方案对比

| 方案 | 适合 | 模型能力 | 成本 |
|---|---|---|---|
| **Anthropic 直连** | 追求最强能力 | ⭐⭐⭐⭐⭐ | 高（美元 + 魔法）|
| **网关（anyrouter）** | 一个 token 多家用 | ⭐⭐⭐⭐⭐（透传 Claude）| 中 |
| **GLM 4.5 直连** | 中文场景 | ⭐⭐⭐⭐ | 低（人民币）|
| **Kimi K2 直连** | 长上下文场景 | ⭐⭐⭐⭐ | 低 |
| **Qwen3 Coder 直连** | 代码场景 | ⭐⭐⭐⭐ | 低 |

> 📌 **建议**：主用网关（一个 token 走遍天下），把国产模型直连当**备份方案**——网关偶尔挂掉时切到本地变量。

### 3.5 永久持久化（不用每次设）

把 `export` 那几行加到你的 shell 配置文件里：
- **Zsh**（Mac 默认）：`~/.zshrc`
- **Bash**：`~/.bashrc` 或 `~/.bash_profile`

修改后 `source ~/.zshrc` 立即生效。

---

## 四、SubAgent 实战案例：「秋瓷团」5 角色一日工作流

完整的 subagent 编排范式，把 1 天工作流拆成 5 个独立 subagent：

| 时段 | 角色 | 职责 |
|---|---|---|
| 早 1 | **新闻秋** | 全网爬 AI 新闻 → 总结成文档 → 飞书推送 |
| 早 2 | **穿搭秋** | 问场合 → 查天气 → 给穿搭建议 |
| 早 3 | **教练秋** | 催报体重 → 记健康数据 → 推荐运动 + 外卖 |
| 早 4 | **日报秋** | 问大体安排 → 规划成日程早报 → 发工作群 |
| 晚 | **反思秋** | 根据当天事件 + 文档 → 引导复盘反思 |

**用了哪些扩展机制**：
- **SubAgent**：5 个角色独立运行
- **MCP**（飞书）：发消息到群、个人
- **Web 工具**：爬新闻、查天气
- **Skill**（可选）：穿搭/健身专业知识

### 关键技巧：飞书推送的角色化配置

每个 subagent 的设定里，用一行描述把"发给谁"固化：

```
Feishu Delivery: Send the completed news briefing to Qiuzhi
via Feishu using receive_id: <你的飞书个人 ID>
```

把这行加到 `.claude/agents/<角色名>.md` 里，subagent 就知道往哪发了。

> 个人 ID 获取方式：[飞书开发文档](https://open.feishu.cn/document/home/index) 里的 ID 查询接口。

---

## 五、5 类场景的 MCP 应用图鉴

按场景找现成 MCP，不用自己造轮子。

### 5.1 视频/社交平台助手（用 AI 刷视频）

```
让 AI 帮你刷抖音、B 站、小红书 → 把内容发到群里
```

| 平台 | MCP |
|---|---|
| 小红书 | [smithery: xhs-mcp](https://smithery.ai/server/@jobsonlook/xhs-mcp) |
| 抖音 | [smithery: douyin-mcp-server2](https://smithery.ai/server/@leinatorX/douyin-mcp-server2) |
| B 站 | [smithery: bilibili-video-info-mcp](https://smithery.ai/server/@lesir831/bilibili-video-info-mcp) |
| 飞书（推送）| `@larksuiteoapi/lark-mcp` |

### 5.2 笔记管理（Obsidian 分析助手）

```
定期总结你的 Obsidian 笔记
```

- [smithery: mcp-obsidian](https://smithery.ai/server/mcp-obsidian)

### 5.3 文档处理（Word 排版助手）

```
用 AI 帮你排版 Word 文档
```

- [smithery: office-word-mcp-server](https://smithery.ai/server/@jackxzxz/office-word-mcp-server)

### 5.4 求职辅助（面试助手）

```
智能简历解析 + 精准面试问题生成 + 评估报告
```

- [smithery: interview-mcp-server](https://smithery.ai/server/@HelloGGX/interview-mcp-server)

### 5.5 学术研究（论文助手）

```
用 AI 找论文 / 下载论文 / 读论文
```

| 工具 | MCP |
|---|---|
| 论文搜索 | [smithery: paper-search-mcp](https://smithery.ai/server/@openags/paper-search-mcp) |
| AI 研究助手（Semantic Scholar）| [smithery: mcpsemanticscholar](https://smithery.ai/server/@hamid-vakilzadeh/mcpsemanticscholar) |

### 5.6 找更多 MCP

- 主流商店：[smithery.ai](https://smithery.ai/)
- 官方导航：[Anthropic MCP 主页](https://modelcontextprotocol.io/)
- 类目检索：[GitHub topics: mcp](https://github.com/topics/mcp)

---

## 六、踩坑提醒

### 6.1 MCP 装完不 work？

**优先检查 4 件事**：
1. **API key 是否过期**（如即梦的 sessionid 会过期）
2. **MCP 名称是否完整**（`claude mcp remove` 时尤其要注意）
3. **`/mcp` 看连接状态**（是否真的连上了）
4. **`claude mcp list` 看有没有装上**

### 6.2 模型环境变量不生效？

**3 个常见原因**：
1. **`export` 是 Mac 的，Windows 用 `$Env:`**——别搞混
2. **shell 配置没 reload**——`source ~/.zshrc`
3. **CC 已经在跑**——重启 CC 让它读新变量

### 6.3 subagent 跑飞了

- 用 **`/agents`** 进 Library 看具体配置
- 检查 **工具权限**（步骤 5）是不是给少了——subagent 要操作什么得先勾上
- 检查 **模型选错**——重任务别选 Haiku
- **从源头：何时不该派 subagent**——目标文件/符号已知（直接 Read/grep 更快）、单文件几行修改（自己干）、需要和用户来回澄清（subagent 没法对话）、强依赖主对话上下文（prompt 写不全）

### 6.4 上下文爆了

- 不要等系统自动 autocompact——**主动 `/compact`**
- 真不重要的 → **`/clear`** 重开
- 长项目准备复用 → **`/init` 写 CLAUDE.md** 把项目信息固化（下次自动加载，不占 token）

### 6.5 别把网关 token 写进 git

如果改了 shell 配置或 settings.json，**`.gitignore` 一下**——网关 token 泄露会被滥用。

---

## 七、与本知识库其他章节的关联

| 主题 | 文档 |
|---|---|
| 扩展机制原理 | [Claude Code 扩展生态.md](Claude%20Code%20扩展生态.md) |
| Agent 是什么 | [什么是Agent.md](什么是Agent.md) |
| Harness 工程 | [Harness工程与Agent解剖.md](Harness工程与Agent解剖.md) |
| 上下文与 Token 计费 | [上下文窗口与Token计费.md](../00_核心概念/上下文窗口与Token计费.md) |
| Shell 与终端 | [Shell与终端基础知识总结.md](../05_技术基础/Shell与终端基础知识总结.md) |
| 多 CLI 联动 | [多CLI联动.md](../05_技术基础/多CLI联动.md) |
| **各家模型特点速查** | [各家LLM模型特点速查.md](../03_应用实践/各家LLM模型特点速查.md) — 6 闭源 + 10 开源家族,选哪个接入 CC 的全景图 |
| **API 选型方法论** | [LLM-API选型方法论.md](../03_应用实践/LLM-API选型方法论.md) — 5 维度 + 3 场景 + 18 家提供商对比 |
| **接口规范实战** | [LLM接口规范实战.md](../03_应用实践/LLM接口规范实战.md) — Anthropic Messages API 字段细节、多轮签名携带坑 |

---

## 附：高频命令一览

```bash
# 启动
claude
claude --dangerously-skip-permissions   # ⚠️ 跳过权限

# MCP
claude mcp add --transport http <name> "<url>"
claude mcp add <name> -- npx -y <package>
claude mcp list
claude mcp remove <name>

# CC 内（输入 / 触发命令模式）
/help    /clear   /compact  /context   /resume
/agents  /plugin  /mcp      /init      /model
/btw     /memory  /rewind   /simplify  /status
/logout  /exit
```
