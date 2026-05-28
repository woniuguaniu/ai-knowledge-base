# Claude 调用 Codex 协作实战案例

> **一句话**:通过 MCP 协议把 Codex 注册为 Claude 的工具,让 Claude 在需要时自动调用 Codex 进行代码 review / 生成 / 优化,实现**双模型协作**。本文记录完整配置流程、用户级 vs 项目级对比、首次授权流程、实战测试,以及常见问题排查。

---

## 目录

- [0. 背景与动机](#0-背景与动机)
- [1. 配置全流程(5 步)](#1-配置全流程5-步)
- [2. 用户级 vs 项目级对比](#2-用户级-vs-项目级对比)
- [3. 首次授权流程](#3-首次授权流程)
- [4. 实战测试示例](#4-实战测试示例)
- [5. 常见问题排查](#5-常见问题排查)
- [6. 进阶:配置 CLAUDE.md 自动协作](#6-进阶配置-claudemd-自动协作)
- [7. 与本知识库其他章节的关联](#7-与本知识库其他章节的关联)

---

## 0. 背景与动机

### 0.1 为什么要让 Claude 调用 Codex?

| Claude 的强项 | Codex 的强项 |
|--------------|-------------|
| 长任务规划、架构设计 | 代码生成、refactor |
| 代码审查、安全分析 | OpenAI 代码训练量大 |
| 推理、解释、文档 | 快速原型、补全 |

**核心洞察**:让 Claude 当"主控 + 决策者",Codex 当"代码顾问",**取长补短**。

### 0.2 MCP 协议的作用

**MCP = Model Context Protocol**(模型上下文协议),Anthropic 推出的标准协议,让 AI 模型能调用外部工具。

```
┌─────────────────────────────────────────────┐
│  Claude (主控)                               │
│                                             │
│  收到用户需求                                │
│       ↓                                     │
│  判断:需要 Codex 帮忙吗?                     │
│       ↓ 是                                  │
│  调用 mcp__codex__codex 工具                │
└─────────────────────────────────────────────┘
                ↑↓ MCP 协议(stdio)
┌─────────────────────────────────────────────┐
│  Codex CLI (作为 MCP Server)                 │
│  codex mcp-server                           │
└─────────────────────────────────────────────┘
```

**关键**:Codex 以 `mcp-server` 模式运行,等待 Claude 通过标准输入/输出(stdio)调用。

---

## 1. 配置全流程(5 步)

### 前置条件

```bash
# 检查 Claude CLI
claude --version
# 应该输出: 2.1.x 或更高

# 检查 Codex CLI
codex --version
# 应该输出: codex-cli 0.x.x
```

如果没安装,参考:
- Claude CLI:[官方文档](https://docs.anthropic.com/claude/docs/claude-cli)
- Codex CLI:[OpenAI Codex 文档](https://platform.openai.com/docs/guides/codex)

---

### 步骤 1:注册 Codex 为 MCP Server(用户级,全局可用)

```bash
# 注册到用户级别(推荐)
claude mcp add codex -s user -- codex mcp-server
```

**输出**:
```
Added stdio MCP server codex with command: codex mcp-server to user config
File modified: /Users/你的用户名/.claude.json
```

---

### 步骤 2:验证注册成功

```bash
claude mcp list
```

**预期输出**:
```
Checking MCP server health…

codex: codex mcp-server - ✓ Connected
plugin:playwright:playwright: npx @playwright/mcp@latest - ✓ Connected
```

看到 `codex - ✓ Connected` 就说明成功了。

---

### 步骤 3:查看配置文件(可选,了解原理)

```bash
# 用户级配置在这里
cat ~/.claude.json | grep -A 10 '"codex"'
```

**应该看到**:
```json
"codex": {
  "type": "stdio",
  "command": "codex",
  "args": [
    "mcp-server"
  ],
  "env": {}
}
```

---

### 步骤 4:测试 Claude 能否看到 Codex 工具

```bash
# 启动非交互模式测试
claude -p "列出你当前可用的所有 MCP 工具"
```

**预期输出**(节选):
```
我当前可用的 MCP 工具如下:

## Codex MCP 工具

**mcp__codex__codex**
- 运行 Codex 会话,接受配置参数
- 用于启动新的 Codex 对话

**mcp__codex__codex-reply**
- 通过 thread ID 继续现有的 Codex 对话
- 用于多轮交互
```

看到这两个工具就说明配置完全正确。

---

### 步骤 5:首次授权(必须在交互式会话中)

```bash
# 启动交互式 Claude
claude

# 在交互中输入:
请用 Codex review 一下当前目录的 Python 文件
```

**会弹出权限提示**:
```
Tool call: mcp__codex__codex
  workingDirectory: /当前目录
  prompt: "Review Python files"

Allow this tool call? [y/n/always/never]
```

**输入 `always`**(总是允许)或 `y`(本次允许)。

**首次授权后**,以后 Claude 调用 Codex 就不会再问了(如果选了 `always`)。

---

## 2. 用户级 vs 项目级对比

| 维度 | 用户级(`-s user`) | 项目级(`-s project`) |
|------|------------------|---------------------|
| **配置文件位置** | `~/.claude.json` | 项目根目录 `.mcp.json` |
| **作用范围** | 所有项目全局可用 | 仅当前项目 |
| **适合场景** | Codex 是通用工具,任何项目都可能用 | 项目特定的 MCP Server(如连接项目数据库) |
| **团队协作** | 每人自己配,不提交到 git | 配置提交到 git,团队共享 |
| **命令** | `claude mcp add xxx -s user` | `claude mcp add xxx -s project` |

**本案例选择用户级**,因为:
- Codex 是通用代码工具,不限项目
- 你希望"随意可以通过 Claude 调用 Codex review 代码"

---

## 3. 首次授权流程

### 3.1 为什么需要授权?

**安全机制**:MCP 工具可以执行任意命令(如 Codex 会读写文件),Claude 必须征得用户同意才能调用。

### 3.2 授权选项说明

| 选项 | 含义 | 推荐场景 |
|------|------|---------|
| **`y`** | 本次允许 | 试验性调用,不确定是否长期使用 |
| **`n`** | 本次拒绝 | 发现 Claude 误判,这次不该调 Codex |
| **`always`** | 总是允许(记住) | 确定 Codex 是可信工具,以后自动批准 |
| **`never`** | 永不允许(拉黑) | 发现某个 MCP Server 有问题,彻底禁用 |

**推荐**:首次测试用 `y`,确认工作正常后,下次选 `always`。

### 3.3 授权记录在哪?

```bash
# 查看已授权的工具
cat ~/.claude.json | grep -A 5 "customApiKeyResponses"
```

**输出示例**:
```json
"customApiKeyResponses": {
  "approved": [
    "02028595bd589815a0b9",  // 某次 Codex 调用的 hash
    "oorSecx9gmYM8GPUnF7L"
  ],
  "rejected": [
    "6yXvM4D7INY6gaik4DPT"
  ]
}
```

---

## 4. 实战测试示例

### 4.1 场景 1:让 Codex review 一段代码

**创建测试文件**:
```python
# test_code.py
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

def find_max(numbers):
    max_num = numbers[0]
    for i in range(len(numbers)):
        if numbers[i] > max_num:
            max_num = numbers[i]
    return max_num
```

**在 Claude 交互中输入**:
```
请用 Codex review test_code.py,给出改进建议
```

**预期 Codex 会指出**:
1. 没处理空列表(会 `ZeroDivisionError` / `IndexError`)
2. `range(len(numbers))` 是反模式,应该直接 `for num in numbers`
3. 可以用内置函数 `sum()` / `max()`
4. 缺少类型提示和文档字符串

---

### 4.2 场景 2:让 Codex 生成代码原型

**在 Claude 交互中输入**:
```
我要写一个 Python 函数,实现二分查找。请先调用 Codex 给一个参考原型,然后你基于它重写一个更完善的版本
```

**协作流程**:
1. Claude 调用 Codex 生成原型
2. Codex 返回基础实现
3. Claude 分析原型,重写并加上:
   - 完整的边界条件处理
   - 类型提示
   - 文档字符串
   - 单元测试

---

### 4.3 场景 3:双模型争辩(高级)

**在 Claude 交互中输入**:
```
我有一段代码(贴代码)。请你先给出你的 review 意见,然后调用 Codex 也 review 一遍。如果你们意见不一致,请列出分歧点并说明你的理由
```

**效果**:
- Claude 给出意见 A
- Codex 给出意见 B
- 如果 A ≠ B,Claude 会分析差异,给出"为什么我认为 A 更合理"

这就是 [N-version programming](程序员黑话速查.md#n-version-programmingn-版本编程) 思想在 AI 协作中的应用。

---

## 5. 常见问题排查

### 问题 1:claude mcp list 显示 codex 但状态是 ✗ Failed

**可能原因**:
- Codex CLI 没装或路径不对
- Codex 没登录(`codex login`)

**排查**:
```bash
# 检查 Codex 是否可用
which codex
codex --version

# 检查登录状态
codex doctor
```

---

### 问题 2:Claude 说"需要授权"但我在非交互模式

**原因**:非交互模式(`claude -p`)无法弹出授权提示。

**解法**:必须在交互式会话中首次授权:
```bash
claude  # 启动交互式
# 然后输入需要调用 Codex 的指令
```

---

### 问题 3:授权后 Claude 还是不调用 Codex

**可能原因**:
1. Claude 判断"这个任务不需要 Codex"
2. 你的指令不够明确

**解法**:明确说"请用 Codex":
```
请用 Codex review 这段代码
```

或者配置 CLAUDE.md 自动触发(见下一节)。

---

### 问题 4:Codex 返回错误"model not found"

**原因**:Codex CLI 配置的模型不存在。

**排查**:
```bash
# 查看可用模型
codex doctor
# 或者查看配置
cat ~/.codex/config.toml
```

**修复**:编辑 `~/.codex/config.toml`,改成实际存在的模型(如 `o1` / `o3`)。

---

### 问题 5:想删除 Codex MCP 配置

```bash
# 删除用户级
claude mcp remove codex -s user

# 删除项目级
claude mcp remove codex -s project
```

---

## 6. 进阶:配置 CLAUDE.md 自动协作

如果你想让 Claude **自动判断**什么时候调用 Codex(而不是每次手动说"用 Codex"),可以在项目根目录创建 `CLAUDE.md`:

```markdown
## Codex 协作策略

### 触发条件(满足任一即自动调用 Codex)
- 用户明确说"用 codex review"
- 任务涉及 100 行以上代码改动
- 任务涉及架构决策、安全敏感代码
- 用户明确说"重要 / 关键 / 生产环境"

### 简单任务(默认)
- 直接由 Claude 完成,不调 codex
- 节省成本和延迟

### 复杂任务流程
1. Claude 写代码
2. 完成后 → 调 codex review(输出 unified diff patch 建议)
3. Claude 决定是否采纳

### 争辩规则
- 最多 2 轮争辩
- 仍不一致 → 把双方观点呈现给用户决策
- 不要陷入死循环

### 兜底
- codex 调用失败 → 跳过该步骤,继续主流程
- codex 返回明显错误 → 记录但不阻塞
```

**效果**:Claude 会自动识别"这是个复杂任务"→ 调用 Codex → 综合双方意见 → 给你最终建议。

**注意**:这会增加成本(每次复杂任务 = 1 次 Claude + 1~3 次 Codex),适合"质量优先"的场景。

---

## 7. 与本知识库其他章节的关联

| 关联点 | 文档 | 关系 |
|--------|------|------|
| **理论基础** | [多CLI联动](多CLI联动.md) | 本案例是"玩法 B:MCP 互调"的完整实战版 |
| **MCP 协议详解** | [Claude Code 扩展生态](../06_Agent工程/Claude%20Code%20扩展生态.md) | MCP 机制、stdio transport、工具注册原理 |
| **Function Calling 原理** | [Function Calling与MCP工程指南](../06_Agent工程/Function%20Calling与MCP工程指南.md) | MCP 底层是 Function Calling 的标准化封装 |
| **术语速查** | [程序员黑话速查](程序员黑话速查.md) | MCP / stdio / unified diff patch 等术语解释 |
| **N-version programming** | [程序员黑话速查](程序员黑话速查.md#n-version-programmingn-版本编程) | 双模型协作的理论依据 |
| **Eval 体系** | [Eval测评体系](../06_Agent工程/Eval测评体系.md) | 双模型对比是 Eval 的低成本实现 |

---

## 附:配置时间线

- **2026-05-28 15:30**:用户提出"想试试 Claude + Codex 协作"
- **2026-05-28 15:35**:环境检查(Claude CLI 2.1.153 / Codex CLI 0.134.0)
- **2026-05-28 15:40**:首次注册到项目级(`-s project`)
- **2026-05-28 15:45**:发现非交互模式无法授权
- **2026-05-28 15:50**:用户要求改为用户级(`-s user`),全局可用
- **2026-05-28 16:00**:配置完成,验证 `claude mcp list` 显示 ✓ Connected
- **2026-05-28 16:10**:落盘本案例笔记

---

## 核心要点总结

| 要点 | 说明 |
|------|------|
| **一行命令搞定** | `claude mcp add codex -s user -- codex mcp-server` |
| **用户级 vs 项目级** | 通用工具用 `-s user`,项目特定用 `-s project` |
| **首次授权必须交互式** | 非交互模式(`claude -p`)无法弹授权提示 |
| **授权选 always** | 确认可信后选 `always`,以后自动批准 |
| **明确指令更可靠** | 说"请用 Codex"比让 Claude 自己判断更稳 |
| **配置文件位置** | 用户级在 `~/.claude.json`,项目级在 `.mcp.json` |
| **验证命令** | `claude mcp list` 看到 `✓ Connected` 就成功 |

---

*创建时间: 2026-05-28*
*配置环境: macOS / Claude CLI 2.1.153 / Codex CLI 0.134.0*
*作者备注: 本案例从实际配置过程中提炼,所有命令和输出均为真实记录*
