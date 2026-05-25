# Function Calling 与 MCP:从工具调用原理到工程实战

> **一句话**:**Function Calling(工具调用)** 让 LLM 学会"喊外援",**MCP(Model Context Protocol)** 让"外援名单"变成 USB 接口式的可插拔标准。这两件事是 2024-2026 年 Agent 工程的两块基石——理解它们,就理解了"为什么 Cursor / Claude Code / ChatGPT 都能用你的本地工具"。
>
> ⚠️ **本篇为 Claude 原创补充笔记**,非 LINUX DO @flymyd 原稿(详见末尾「作者声明」)。
> 📌 **不重复已有内容**:本文聚焦"原理 + 协议对比 + 工程实战",MCP 的"装/查/删命令 + 实战安装例子" 详见 [Claude Code 扩展生态.md § 四](../06_Agent工程/Claude%20Code%20扩展生态.md)。

---

## 目录

- [0. 为什么需要 Function Calling](#0-为什么需要-function-calling)
- [1. Function Calling 的工作流程](#1-function-calling-的工作流程)
- [2. 御三家 Function Calling 接口对比](#2-御三家-function-calling-接口对比)
- [3. MCP:工具协议的"USB 化"](#3-mcp工具协议的usb-化)
- [4. MCP vs Function Calling:不是替代,是协作](#4-mcp-vs-function-calling不是替代是协作)
- [5. 工程实战:从零到能跑的 4 个例子](#5-工程实战从零到能跑的-4-个例子)
- [6. 常见坑与最佳实践](#6-常见坑与最佳实践)
- [7. 与本知识库其他章节的关联](#7-与本知识库其他章节的关联)
- [8. 术语速查](#8-术语速查)
- [9. 作者声明、来源与局限性](#9-作者声明来源与局限性)

---

## 0. 为什么需要 Function Calling

### 0.1 LLM 的"先天残疾"

**LLM 是"纯文本预测器"**:输入文本 → 输出文本。

它**不能直接**:
- ❌ 联网查最新天气
- ❌ 读你电脑上的文件
- ❌ 操作数据库
- ❌ 发邮件
- ❌ 看实时股价
- ❌ 跑代码

```
用户:今天广州天气怎么样?
LLM(没工具):根据我的训练数据,广州一般 25 度左右...(完全乱编)
```

### 0.2 工具调用 = 给 LLM 配"外援电话本"

**Function Calling 的核心思路**:
1. 你告诉 LLM:"你能调用 `get_weather(city)`、`send_email(to, body)` 这些函数"
2. LLM 看到用户问天气,**不直接回答**,而是输出一段结构化 JSON:`{"function": "get_weather", "args": {"city": "广州"}}`
3. 你的程序拦截这个 JSON,**真的去调用 API**
4. 把 API 结果**塞回给 LLM**作为新上下文
5. LLM 基于真实数据生成回复

```
用户:今天广州天气怎么样?
LLM:[调用 get_weather(city="广州")]  ← 模型输出工具调用意图
程序:[拦截 → 真的调天气 API → 返回 "22°C 多云"]
LLM:广州今天 22 度,多云,建议带件外套。
```

这就是 **Function Calling** —— **LLM "决定调谁",程序"真的去调"**。

---

## 1. Function Calling 的工作流程

### 1.1 完整时序图

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│ User       │    │ App        │    │ LLM API    │    │ Tool/API   │
└─────┬──────┘    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
      │                 │                 │                 │
      │ "广州天气?"     │                 │                 │
      ├────────────────>│                 │                 │
      │                 │                 │                 │
      │                 │ messages +      │                 │
      │                 │ tools schema    │                 │
      │                 ├────────────────>│                 │
      │                 │                 │                 │
      │                 │                 │ "我要调          │
      │                 │                 │  get_weather"   │
      │                 │<────────────────┤                 │
      │                 │ (tool_calls)    │                 │
      │                 │                 │                 │
      │                 │                 │                 │
      │                 │ call get_weather("广州")          │
      │                 ├────────────────────────────────────>
      │                 │                                    │
      │                 │ "22°C 多云"                        │
      │                 │<────────────────────────────────────
      │                 │                 │                 │
      │                 │ messages + tool │                 │
      │                 │ result          │                 │
      │                 ├────────────────>│                 │
      │                 │                 │                 │
      │                 │                 │ "广州 22 度,    │
      │                 │                 │  多云,建议..." │
      │                 │<────────────────┤                 │
      │                 │                 │                 │
      │ "广州 22 度..."  │                 │                 │
      │<────────────────┤                 │                 │
      │                 │                 │                 │
```

### 1.2 关键认知

1. **LLM 不"直接调"工具,只"决定调谁"** —— 真正的调用是你的应用代码做的
2. **整个流程至少要调 LLM 2 次** —— 第一次让它决定调什么、第二次让它基于结果生成回复
3. **每次都要把所有历史 + 工具定义重新发给 LLM** —— 这是 stateless 模型的特点(详见 [上下文窗口与Token计费](../00_核心概念/上下文窗口与Token计费.md))
4. **错误处理是你的事** —— LLM 不知道你的 API 失败了,你要把错误信息塞回去让它重试或道歉

---

## 2. 御三家 Function Calling 接口对比

> 📌 本节内容延续 [LLM 接口规范实战.md](../03_应用实践/LLM接口规范实战.md) 的 4 接口对比,聚焦"工具调用部分"的差异。

### 2.1 OpenAI 风格(事实标准)

#### 工具定义

```json
{
  "model": "gpt-4o",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "城市名,如'广州'"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "温度单位"
            }
          },
          "required": ["city"]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

**关键字段**:

| 字段 | 含义 |
|---|---|
| `tools[].function.name` | 函数名,字母数字下划线 |
| `tools[].function.description` | **超级重要——LLM 主要靠这个判断要不要调** |
| `tools[].function.parameters` | JSON Schema 标准格式 |
| `tool_choice` | `"auto"`(LLM 决定)/ `"none"`(禁用工具)/ `{"type":"function","function":{"name":"X"}}`(强制调 X) |

#### LLM 返回的工具调用

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"city\":\"广州\",\"unit\":\"celsius\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

**关键**:
- `arguments` 是**字符串化的 JSON**,不是 JSON 对象,需要 `JSON.parse()`
- 多个 `tool_calls` 可能并行(parallel function calling)
- `finish_reason == "tool_calls"` 表示 "我要调工具"

#### 把工具结果传回去

```json
{
  "messages": [
    {"role": "user", "content": "广州天气?"},
    {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "..."}
      }]
    },
    {
      "role": "tool",
      "tool_call_id": "call_abc123",
      "content": "22°C 多云"
    }
  ]
}
```

**关键**:
- 用 **`role: "tool"`** 的消息回传结果
- 必须用 `tool_call_id` 关联到 LLM 上次的调用
- 然后再次发起 chat completion,LLM 会基于结果生成最终回复

### 2.2 Anthropic 风格

```json
{
  "model": "claude-opus-4-7",
  "max_tokens": 4096,
  "messages": [...],
  "tools": [
    {
      "name": "get_weather",
      "description": "查询天气",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        },
        "required": ["city"]
      }
    }
  ]
}
```

**差异**:
- 工具定义直接放在 `tools` 顶层,**没有 OpenAI 的 `type: "function"` 这层包装**
- 字段叫 `input_schema` 而非 `parameters`
- 没有 `tool_choice`,改用 `tool_choice: {"type": "auto"}` 之类

**返回**:

```json
{
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01",
      "name": "get_weather",
      "input": {"city": "广州"}
    }
  ],
  "stop_reason": "tool_use"
}
```

- `input` 直接是 JSON 对象(**不是字符串**)
- `stop_reason: "tool_use"` 取代了 OpenAI 的 `finish_reason: "tool_calls"`

**回传结果**:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01",
      "content": "22°C 多云"
    }
  ]
}
```

- **用 `role: "user"` 回传**,内容数组里塞 `tool_result` 块
- (OpenAI 是用 `role: "tool"` 单独的消息)

### 2.3 Google Gemini 风格

```json
{
  "contents": [...],
  "tools": [{
    "functionDeclarations": [{
      "name": "get_weather",
      "description": "查询天气",
      "parameters": {
        "type": "OBJECT",
        "properties": {
          "city": {"type": "STRING"}
        },
        "required": ["city"]
      }
    }]
  }]
}
```

**差异**:
- 工具放在 `tools[].functionDeclarations` 数组里
- 字段名首字母大写(`OBJECT` 不是 `"object"`)
- 类型是大写 `STRING / NUMBER / BOOLEAN / OBJECT / ARRAY`

**返回与回传**:用 `functionCall` 和 `functionResponse` 块,详见 [Gemini 官方文档](https://ai.google.dev/gemini-api/docs/function-calling)。

### 2.4 三家差异速查表

| 维度 | OpenAI | Anthropic | Gemini |
|---|---|---|---|
| 工具定义包装 | `type: function, function: {...}` | 直接平铺 | `functionDeclarations: [...]` |
| Schema 字段名 | `parameters` | `input_schema` | `parameters`(大写值)|
| 调用结果字段 | `tool_calls[].function.arguments`(**字符串**)| `content[].input`(**对象**)| `functionCall.args` |
| 回传 role | `role: tool` | `role: user, content: [{type: tool_result}]` | `role: user, parts: [{functionResponse}]` |
| stop 标志 | `finish_reason: tool_calls` | `stop_reason: tool_use` | `finishReason: STOP` + parts 含 `functionCall` |
| 并行调用支持 | ✅ | ✅ | ✅ |
| 流式工具调用 | ✅(参数 token 流式累积) | ✅ | ✅ |

---

## 3. MCP:工具协议的"USB 化"

### 3.1 MCP 是什么(一句话)

**MCP(Model Context Protocol)** 是 Anthropic 2024 年 11 月开源的协议,**让"LLM 应用"和"工具/数据源"之间像 USB 一样可插拔**。

> 💡 详细介绍见 [Claude Code 扩展生态.md § 四](../06_Agent工程/Claude%20Code%20扩展生态.md),本节聚焦"为什么需要 MCP"和"它和 Function Calling 什么关系"。

### 3.2 MCP 解决的问题:M × N 爆炸

```
没有 MCP:
  3 个 LLM 应用(Cursor / Claude Desktop / Cline)
  × 4 个数据源(GitHub / Slack / 飞书 / 公司数据库)
  = 12 套独立集成

  每个 LLM 应用都要为每个数据源单独写连接代码,工作量爆炸
```

```
有了 MCP:
  3 个 LLM 应用 各自实现"MCP 客户端"(一次)
  4 个数据源 各自实现"MCP 服务端"(一次)
  → 3 + 4 = 7 个组件,**所有组合都能互通**

  这就是协议的力量
```

### 3.3 MCP 三件套

| 角色 | 是什么 |
|---|---|
| **MCP Host** | LLM 应用(Claude Desktop / Cursor / Claude Code) |
| **MCP Client** | Host 内嵌的协议客户端,负责跟 Server 通信 |
| **MCP Server** | 工具 / 数据源的提供者,如 `mcp-server-github`、`mcp-server-postgres` |

```
┌──────────────────────────────┐
│ MCP Host(Claude Desktop)    │
│  ┌────────────────────────┐  │
│  │ MCP Client             │  │
│  └────┬───────────┬───────┘  │
└───────┼───────────┼──────────┘
        ↓           ↓
  ┌──────────┐  ┌──────────┐
  │ Server A │  │ Server B │
  │ GitHub   │  │ Postgres │
  └──────────┘  └──────────┘
```

### 3.4 MCP 协议提供的三类原语

MCP 不只能调函数(Tools),还有更多:

| 原语 | 含义 | 例子 |
|---|---|---|
| **Tools** | 模型可调用的函数(等价 Function Calling)| `get_weather(city)` |
| **Resources** | 模型可读的数据 | `file:///proj/README.md` 内容 |
| **Prompts** | 预设的 prompt 模板 | `/summarize-bug-report` |

> 💡 **Resources vs Tools**:
> - **Tools = 动作**(写文件、发邮件、调 API)
> - **Resources = 数据**(读文件、查数据库快照、看监控指标)

### 3.5 传输方式

| Transport | 适用 | 特点 |
|---|---|---|
| **stdio** | 本地命令行工具 | 最简单,启动子进程 |
| **HTTP + SSE** | 远程服务 | 支持跨网络 |
| **WebSocket** | 实时双向 | 较少用 |

---

## 4. MCP vs Function Calling:不是替代,是协作

这是新手最容易混淆的点:

### 4.1 关系图

```
┌─────────────────────────────────────┐
│  LLM API 层                          │
│  (OpenAI / Anthropic / Gemini)      │
│  - 提供 Function Calling 能力        │
│  - "把工具描述塞 prompt → 输出 JSON" │
└─────────────────────────────────────┘
              ↑
              │ 工具 schema
              │
┌─────────────────────────────────────┐
│  LLM 应用层(Claude Desktop / Cursor)│
│  ┌──────────────────────────────┐    │
│  │  MCP Client(协议客户端)    │    │
│  │  - 跟 MCP Server 通信        │    │
│  │  - 把 MCP Tools 转成 FC schema│    │
│  │  - 把 LLM 输出的 FC 调用      │    │
│  │    转成对 MCP Server 的请求  │    │
│  └──────────────────────────────┘    │
└─────────────────────────────────────┘
              ↑
              │ stdio / HTTP
              │
┌─────────────────────────────────────┐
│  MCP Server(工具提供者)            │
│  - mcp-server-github                │
│  - mcp-server-filesystem            │
│  - mcp-server-postgres              │
└─────────────────────────────────────┘
```

### 4.2 区分

| 维度 | Function Calling | MCP |
|---|---|---|
| **协议层** | **LLM ↔ 应用**(模型决定调什么)| **应用 ↔ 工具**(工具如何被发现、调用)|
| **谁定义** | OpenAI / Anthropic / Gemini | Anthropic(已被生态广泛接受) |
| **能力范围** | 仅函数调用 | 函数 + 数据资源 + Prompt 模板 |
| **谁实现** | LLM 服务商内置(API 调用方写 schema)| 工具开发者写 Server,应用厂商写 Client |
| **是否需要 LLM 支持** | ✅ 必须 LLM 支持 | ✅ MCP Tools 也需 LLM 支持 FC |
| **可移植性** | 各厂家格式不同(需适配)| **跨 LLM 厂家通用** |

### 4.3 简单类比

| 类比 | Function Calling | MCP |
|---|---|---|
| 操作系统术语 | **API 调用约定**(怎么传参) | **设备驱动模型**(设备如何注册到系统) |
| 硬件术语 | **CPU 指令集** | **USB 标准** |
| 商业术语 | **签合同模板** | **行业法规** |

### 4.4 一个具体例子

**用户**:"帮我看看 GitHub 上我那个仓库的 PR"

**没有 MCP 的世界**:
- Claude Desktop 开发者自己写"GitHub 集成"代码
- Cursor 开发者也得自己写
- Cline 开发者也得自己写

**有 MCP 的世界**:
- 任何人写一个 `mcp-server-github`,**所有支持 MCP 的应用都能用**
- 用户在 Claude Desktop 配置一次,**Tools 自动出现在对话中**
- LLM 看到工具 schema,触发 Function Calling 调用
- MCP Client 把调用转发给 `mcp-server-github`
- 拿到结果再给 LLM 生成回复

---

## 5. 工程实战:从零到能跑的 4 个例子

### 5.1 例 1:Python + OpenAI 风格 Function Calling

```python
from openai import OpenAI
import json

client = OpenAI()

# 1. 定义工具
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
}]

# 2. 实现工具(真实的话调 API)
def get_weather(city: str) -> str:
    fake_db = {"广州": "22°C 多云", "北京": "5°C 晴", "上海": "15°C 雨"}
    return fake_db.get(city, "未知城市")

# 3. 主循环
def chat_with_tools(user_query: str):
    messages = [{"role": "user", "content": user_query}]
    
    # 第一次调用:让 LLM 决定要不要调工具
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    msg = response.choices[0].message
    
    if msg.tool_calls:
        # 4. 把 LLM 的"调用意图"添加到消息历史
        messages.append(msg)
        
        # 5. 真实执行每个工具调用
        for tc in msg.tool_calls:
            if tc.function.name == "get_weather":
                args = json.loads(tc.function.arguments)
                result = get_weather(**args)
                
                # 6. 把结果作为 tool 消息添加
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        
        # 7. 第二次调用:基于工具结果生成最终回复
        final = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return final.choices[0].message.content
    else:
        return msg.content

# 8. 试一下
print(chat_with_tools("今天广州天气怎么样?"))
# → "广州今天 22 度,多云,建议..."

print(chat_with_tools("1 + 1 等于几?"))
# → "1 + 1 等于 2"(没调工具)
```

### 5.2 例 2:多工具 + 并行调用

```python
tools = [
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "查天气",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
    }},
    {"type": "function", "function": {
        "name": "get_time",
        "description": "查指定时区当前时间",
        "parameters": {"type": "object", "properties": {"timezone": {"type": "string"}}, "required": ["timezone"]}
    }}
]

# 用户问"现在北京几点?顺便看下天气"
# → LLM 可能 **并行** 输出 2 个 tool_calls

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "现在北京几点?顺便看下天气"}],
    tools=tools
)

for tc in response.choices[0].message.tool_calls:
    print(tc.function.name, tc.function.arguments)
# get_time {"timezone":"Asia/Shanghai"}
# get_weather {"city":"北京"}
```

**关键**:并行 tool_calls 时**全部执行完**再一次性回传所有结果,**不要 1 个 1 个回**(那是串行,慢)。

### 5.3 例 3:写一个最简 MCP Server(stdio)

```python
# my_mcp_server.py
# pip install mcp

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("my-tools")

# 注册一个工具
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="查询指定城市的当前天气",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        )
    ]

# 处理工具调用
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments["city"]
        # 这里调真 API
        result = f"{city}: 22°C 多云"
        return [TextContent(type="text", text=result)]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

**在 Claude Desktop 配置使用**:

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "my-weather": {
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"]
    }
  }
}
```

重启 Claude Desktop,**`get_weather` 自动出现在工具列表里**,可以直接用。

### 5.4 例 4:在自部署 LiteLLM 网关上启用 MCP

LiteLLM 自 1.50 起原生支持 MCP,**所有走 LiteLLM 的 LLM 自动获得 MCP 工具**:

```yaml
# config.yaml
model_list:
  - model_name: qwen-flagship
    litellm_params:
      model: openai/Qwen/Qwen3-32B-Instruct
      api_base: http://vllm:8000/v1

mcp_servers:
  github:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/data"]
```

**效果**:任何调 `litellm/v1/chat/completions` 的客户端,**自动可以让 LLM 调用 github / filesystem 工具**——客户端代码完全不用改。

> 💡 这是 MCP 真正发力的场景:**给整个公司的 LLM 接入,一键给所有应用配上工具**。

---

## 6. 常见坑与最佳实践

### 6.1 工具 description 是最重要的字段

```python
# ❌ 差的描述
{"name": "get_weather", "description": "天气"}

# ✅ 好的描述
{"name": "get_weather",
 "description": """查询指定城市的当前实时天气信息。
适用场景:用户询问当前天气、是否下雨、是否需要带伞等。
不适用场景:历史天气、未来天气预报、空气质量。
返回内容:温度、天气状况(如多云/晴/雨)。"""}
```

**LLM 完全靠 description 决定要不要调**——写得越清楚、约束越明确,误调和漏调越少。

### 6.2 参数 schema 越严越好

```python
# ❌ 差的 schema(LLM 可能传任意字符串)
"properties": {"city": {"type": "string"}}

# ✅ 好的 schema
"properties": {
    "city": {
        "type": "string",
        "description": "城市的中文名,如'广州'、'北京'。不要使用拼音或英文。",
        "minLength": 2,
        "maxLength": 20
    }
}
```

OpenAI 还支持 `strict: true` 模式,**强制 LLM 输出严格符合 schema 的 JSON**——但兼容性需查模型支持情况。

### 6.3 错误处理:LLM 不知道你的 API 挂了

```python
def safe_call_tool(name, args):
    try:
        return real_call(name, args)
    except Exception as e:
        # ✅ 把错误信息返回给 LLM,让它知道
        return {"error": str(e), "suggestion": "请告知用户工具暂时不可用"}
    # ❌ 不要直接抛异常——LLM 不会看到 Python traceback
```

### 6.4 不要工具数量爆炸

| 工具数 | LLM 表现 |
|---|---|
| 1-5 个 | ✅ 表现好 |
| 6-20 个 | ⚠️ 误选率上升 |
| 20+ 个 | ❌ 严重的"选错工具"问题 |

**应对**:
- **工具分组 + 动态加载**(只把当前任务相关的 5-10 个 tools 暴露给 LLM)
- **写"工具路由器"**(用便宜小模型先选 tool 组,再喂给大模型)

### 6.5 安全:工具调用是攻击面

**典型的危险反模式**(下面是反例,**不要这么写**):

| 反例 | 为什么危险 |
|---|---|
| 注册一个 `execute_shell` 工具直接把 LLM 输出的命令丢给 shell 执行 | LLM 被 prompt injection 后会跑任意命令 |
| 注册 `read_file(path)` 不限制路径 | LLM 可能被诱导读 `/etc/passwd`、SSH key 等敏感文件 |
| 注册数据库工具不限制 SQL | LLM 可能被诱导 `DROP TABLE` 或读全表 |

**最佳实践**:
- **白名单**:只允许特定命令 / 路径前缀 / SQL 模式
- **沙箱**:在 Docker / Firecracker 等隔离环境执行
- **审计**:所有工具调用落日志
- **HITL**:危险操作要人工确认

详见 [Agent 安全攻防.md](../06_Agent工程/Agent安全攻防.md)。

### 6.6 流式工具调用的复杂性

OpenAI / Anthropic 都支持**流式工具调用** — `tool_calls.function.arguments` 是**字符 token 一段段流出的**,而不是一次性给完整 JSON:

```
chunk 1: {"name":"get_weather","arguments":"{\""}
chunk 2: {"arguments":"city"}
chunk 3: {"arguments":"\":\"广"}
chunk 4: {"arguments":"州\"}"}
```

**应用层必须累积所有 arguments token,等 `finish_reason` 后才能 `JSON.parse`**。

---

## 7. 与本知识库其他章节的关联

- **MCP 的实战命令 / 安装例子**:[Claude Code 扩展生态.md § 四](../06_Agent工程/Claude%20Code%20扩展生态.md)——本文不重复
- **接口规范基础**:[LLM 接口规范实战.md § 1.3 finish_reason](../03_应用实践/LLM接口规范实战.md)——`finish_reason: tool_calls` 的来源
- **Agent 工程基础**:[什么是 Agent.md](../06_Agent工程/什么是Agent.md)——Function Calling 是 Agent 的"动作能力"
- **Agent 安全**:[Agent 安全攻防.md](../06_Agent工程/Agent安全攻防.md)——工具调用是主要攻击面
- **Harness 工程**:[Harness工程与Agent解剖.md](../06_Agent工程/Harness工程与Agent解剖.md)——工具是 Agent 的"执行层"
- **API 选型决策**:[LLM-API 选型方法论.md](../03_应用实践/LLM-API选型方法论.md)——选模型时要看是否支持 FC

---

## 8. 术语速查

| 术语 | 全称 / 含义 |
|---|---|
| **Function Calling / FC** | LLM 调用外部函数的能力 |
| **Tool Use** | Anthropic 用语,等价 Function Calling |
| **tool_calls** | OpenAI 响应中表示"LLM 决定调工具"的字段 |
| **tool_choice** | 控制 LLM 是否 / 调哪个工具的字段 |
| **parallel function calling** | LLM 一次输出多个工具调用,并行执行 |
| **strict mode** | OpenAI 的严格 schema 模式,保证返回符合定义 |
| **JSON Schema** | JSON 的类型描述标准,FC schema 用它 |
| **MCP** | Model Context Protocol,Anthropic 2024.11 开源的工具协议 |
| **MCP Host** | LLM 应用(Claude Desktop / Cursor 等) |
| **MCP Client** | MCP Host 内嵌的协议客户端 |
| **MCP Server** | 工具 / 数据源提供方 |
| **Tools / Resources / Prompts** | MCP 的三类原语 |
| **stdio Transport** | MCP 通过子进程标准输入输出通信 |
| **HTTP+SSE Transport** | MCP 通过 HTTP 流式通信 |
| **流式工具调用** | tool_calls 的 arguments 字段是 token 流式累积的 |
| **ReAct** | Reasoning + Acting,Agent 的经典 prompt 范式 |
| **工具路由器** | 大量工具时,用小模型先选"工具组"的优化模式 |
| **HITL** | Human-in-the-Loop,危险操作需人工确认 |

---

## 9. 作者声明、来源与局限性

### 9.1 作者声明

> ⚠️ **本篇是 Claude 基于公开技术资料整理的科普综述,不是 LINUX DO @flymyd 的实战经验帖**。
>
> 原作者在「简单易懂的 LLM 相关知识梳理」目录中标记 ep.6「Function Call 与 MCP」为待填坑,本笔记为补位之作。

### 9.2 主要来源

- OpenAI Function Calling 官方文档:https://platform.openai.com/docs/guides/function-calling
- Anthropic Tool Use 官方文档:https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- Google Gemini Function Calling:https://ai.google.dev/gemini-api/docs/function-calling
- MCP 官方:https://modelcontextprotocol.io
- MCP 规范:https://spec.modelcontextprotocol.io
- MCP Python SDK:https://github.com/modelcontextprotocol/python-sdk
- LiteLLM MCP 集成:https://docs.litellm.ai/docs/proxy/mcp

### 9.3 本笔记的局限性

| 维度 | 局限性 |
|---|---|
| **个人实战踩坑** | 笔者没在生产环境踩过"工具调用导致 LLM 死循环 100 次烧 100 美元"这种事故,**生活化细节缺** |
| **多 LLM 厂家最新动态** | OpenAI / Anthropic 的 FC 协议演进很快,**月级更新可能让本文细节过时** |
| **MCP 生态** | MCP 仍在快速演进,**Resources 与 Sampling 的高级用法本文未深入** |
| **企业级权限** | 工具调用的细粒度权限控制(谁能调哪个工具)未深入 |
| **跨模型 FC schema 自动转换** | LiteLLM 等中间件如何把 OpenAI schema 自动转 Anthropic schema 的细节未深入 |
| **Function Calling 评测** | 主流 FC benchmark(如 BFCL)及各家模型的真实排名未涵盖 |

### 9.4 给读者的建议

- **想理解 Function Calling 原理**:跑一遍本文 § 5.1 的 OpenAI 例子,**最多 30 分钟**
- **想给自己用**:写个 MCP Server,接 Claude Desktop / Cursor / Claude Code,**马上能用**
- **想给团队 / 公司用**:看 LiteLLM 的 MCP 集成 / LangChain 的 MCP 适配,**统一接入更省事**
- **想做研究 / 评测**:BFCL(Berkeley Function-Calling Leaderboard)是当前最权威的 FC benchmark
