# LLM 接口规范实战:OpenAI / Response / Gemini / Anthropic 四种格式

> **一句话**:"反正都是 OpenAI 兼容接口,一把梭就行了吧?"——**这话在 2024 年还算对,2026 年已经不再适用**。御三家各有特色,转换过程中既可能缺少特有参数,又可能因为传入了"OpenAI 标准但目标厂商不支持的参数"直接调用失败。本篇从 HTTP 请求角度讲清 4 种主流接口规范的核心差异与常见坑。

---

## 目录

- [0. 为什么"OpenAI 兼容一把梭"不再够用](#0-为什么openai-兼容一把梭不再够用)
- [1. OpenAI Chat Completion(经典款)](#1-openai-chat-completion经典款)
  - [1.1 Chat Completion vs Completion 别搞混](#11-chat-completion-vs-completion-别搞混)
  - [1.2 请求体核心字段](#12-请求体核心字段)
  - [1.3 响应体解析:5 个关键字段](#13-响应体解析5-个关键字段)
  - [1.4 流式响应(SSE)的结构](#14-流式响应sse的结构)
  - [1.5 思考模型的特殊字段](#15-思考模型的特殊字段)
  - [1.6 多模态调用:content 字段的 6 种类型](#16-多模态调用content-字段的-6-种类型)
- [2. 4 类经典坑](#2-4-类经典坑)
  - [2.1 坑 1:role 不止 system/user/assistant 三种](#21-坑-1role-不止-systemuserassistant-三种)
  - [2.2 坑 2:御三家的"严格参数"问题](#22-坑-2御三家的严格参数问题)
  - [2.3 坑 3:`/v1` 前缀的坑](#23-坑-3v1-前缀的坑)
  - [2.4 坑 4:`finish_reason=length` 时 JSON 截断](#24-坑-4finish_reasonlength-时-json-截断)
- [3. OpenAI Response API(新款)](#3-openai-response-api新款)
- [4. Gemini API(/v1beta)](#4-gemini-apiv1beta)
- [5. Anthropic Messages API](#5-anthropic-messages-api)
- [6. 4 种接口对比速查表](#6-4-种接口对比速查表)
- [7. 与本知识库其他章节的关联](#7-与本知识库其他章节的关联)
- [8. 术语速查](#8-术语速查)
- [9. 来源、评分与可商榷点](#9-来源评分与可商榷点)

---

## 0. 为什么"OpenAI 兼容一把梭"不再够用

LLM 早期(2023~2024 年),所有厂商都尽量靠拢 OpenAI 的 Chat Completion 接口,**一套代码改个 BASE_URL + API_KEY 就能跑遍**。

但 2025~2026 年后,**御三家(OpenAI / Google / Anthropic)各自走出了独立路径**:

```
2023 年:OpenAI Chat Completion 一统天下
   ↓
2024 年:Anthropic 推出 Messages API + Gemini 推出 /v1beta
   ↓
2025 年:OpenAI 推出 Response API(自己都不向后兼容)
   ↓
2026 年:四套主流接口共存,**OpenAI 兼容只能跑文本基础场景**
```

**为什么不能一把梭**:

1. **多模态格式不统一**:画图、传图片、视频、向量等,**许多服务商都有自己的表示法**
2. **特有参数不通用**:Gemini 的 `safety_settings` / Anthropic 的 `thinking` / OpenAI 的 `reasoning_effort` 互不通用
3. **严格参数检查**:御三家比中转站严格,**多传一个不支持的参数直接报错**

> 💡 **本文只从 HTTP 请求角度讲**,不讲各家 SDK,因为 **SDK 本质上也是对 HTTP 请求的包装**。Function Call、MCP 调用在 Agent 工程系列里讲,本文略。

---

## 1. OpenAI Chat Completion(经典款)

**梦开始的地方**:**99.99% 的人第一次调用 LLM 都是用 OpenAI 兼容接口**。它现在是事实标准,DeepSeek、Qwen、各种中转都兼容。

**端点**:`POST {base_url}/v1/chat/completions`

参考文档:
- 官方:https://platform.openai.com/docs/quickstart
- New API 中文:https://docs.newapi.pro/zh/docs/api/ai-model/chat/openai

### 1.1 Chat Completion vs Completion 别搞混

**这是一个常被混淆的概念**:

| 接口 | 全名 | 输入 | 用法 |
|---|---|---|---|
| **Chat Completion** | 聊天补全 | `messages` 数组(每条消息含 role + content)| **当前主流**,99% 调用都用这个 |
| **Completion** | 文本补全 | `prompt` 字符串 + `max_tokens` | **老式接口**,GPT-3 时代的玩法,现已弃用 |

**别再混用了**——它们的端点路径都不一样:
- `/v1/chat/completions` ← 用这个
- `/v1/completions` ← 别用

### 1.2 请求体核心字段

最基本的请求结构:

```javascript
const payload = {
  // 必填
  model: "deepseek-chat",          // 模型 ID
  messages: [                       // 对话历史
    {role: "system", content: "你是一名资深游戏设计师"},
    {role: "user", content: "请设计一个 24 岁大学生角色"}
  ],
  
  // 常用可选
  stream: true,                    // 是否流式
  temperature: 0.7,                // 创意度 0~2
  max_tokens: 1000,                // 输出上限
  
  // 高级
  response_format: {type: "json_object"},  // 强制 JSON 输出(需 prompt 配合)
  seed: 1919810,                   // 复现性
  
  // 思考模型才有
  // reasoning_effort: "high",
  
  // 旧 API 兼容(部分服务商支持)
  // top_p: 0.9, top_k: 50, presence_penalty: 0, frequency_penalty: 0
};

const resp = await fetch(BASE_URL + "/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${API_KEY}`
  },
  body: JSON.stringify(payload)
});
```

> 💡 **重要警告**:如果想 JSON 格式化输出(`response_format: json_object`),**强烈建议在 prompt 里也强调输出 JSON**,否则模型可能输出"JSON 包裹在 markdown 代码块里"。

### 1.3 响应体解析:5 个关键字段

非流式响应示例:

```javascript
{
  "id": "chatcmpl-123",                  // 此次请求唯一标识
  "object": "chat.completion",           // 对象类型
  "created": 1677652288,                 // Unix 时间戳
  "model": "deepseek-chat",              // 实际使用的模型
  "system_fingerprint": "fp_447",        // ← 关键字段 1
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "...",                  // ← 关键字段 2
      "reasoning_content": "..."         // ← 关键字段 3(思考模型才有)
    },
    "finish_reason": "stop"              // ← 关键字段 4
  }],
  "usage": {                             // ← 关键字段 5
    "prompt_tokens": 56,
    "completion_tokens": 120,
    "total_tokens": 176,
    "completion_tokens_details": {
      "reasoning_tokens": 40             // 思考 token(不显示但计费)
    }
  }
}
```

#### 1. `finish_reason`(停止状态)

判断回复是否完整的字段。**四种值**:

| 值 | 含义 | 工程含义 |
|---|---|---|
| `stop` | 模型自然结束(遇停止符或生成完毕)| ✅ 正常 |
| `length` | **达到 max_tokens 限制,内容被截断** | ⚠️ JSON 输出场景会得到不完整 JSON |
| `content_filter` | **触发安全审核被静默拦截** | ⚠️ Gemini 429,需查 promptFeedback |
| `tool_calls` | 模型决定调用工具 | 进入 Function Call 流程 |

#### 2. `usage`(用量统计 / 计费核心)

| 字段 | 含义 |
|---|---|
| `prompt_tokens` | 输入 + 系统提示 + 历史经 Tokenizer 后的数量 |
| `completion_tokens` | AI 生成内容长度 |
| `reasoning_tokens` | **思考模型不可见但计费的思考成本**——前端不显示,账单照收 |

#### 3. `system_fingerprint`(系统指纹)

如果服务商更新了底层硬件或模型权重,**指纹会变化**。

> 💡 **Benchmark 必备**:如果你在做模型性能对比,**记录这个字段**有助于排查"为什么同样的 Prompt 在今天和昨天的输出表现不一致"——服务商悄悄换底座了。

### 1.4 流式响应(SSE)的结构

当设置 `stream: true`,API 通过 **Server-Sent Events(SSE)** 返回一系列 **ChatCompletionChunk**。每一块的结构与标准响应略有不同——**`message` 变成了 `delta`**:

```
// 第一个 chunk:角色定义或空内容
{"choices":[{"delta":{"role":"assistant"},"finish_reason":null}]}

// 中间的 chunk:增量内容
{"choices":[{"delta":{"content":"你好"},"finish_reason":null}]}
{"choices":[{"delta":{"content":",我"},"finish_reason":null}]}
{"choices":[{"delta":{"content":"是…"},"finish_reason":null}]}

// 最后一个 chunk:结束标识
{"choices":[{"delta":{},"finish_reason":"stop"}]}

// 如果开启 include_usage,最后多一个含 usage 的 chunk
{"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{...}}
```

**解析时的关键**:
- 每个 chunk 都是独立 JSON,**不是完整对话**
- 需要客户端累积 `delta.content` 才能拼出完整回答
- **完整结束标志是 `finish_reason !== null`**

### 1.5 思考模型的特殊字段

思考模型(DeepSeek-R1 / GLM-4-Thinking / Gemini Thinking / o1 系列)在 OpenAI 兼容接口下有两个特点:

#### `reasoning_content`(非标准但部分厂家支持)

```javascript
{
  "message": {
    "role": "assistant",
    "content": "{\"name\": \"李天梭\", ...}",     // 最终答案
    "reasoning_content": "用户要求 24 岁大学生..."  // ← 思考过程
  }
}
```

**部分厂家会把 `reasoning_content` 字段也返回**(DeepSeek、GLM 等),OpenAI 自己的 o1 系列**不返回**思考过程,只在 usage 里给 `reasoning_tokens` 计费。

#### 思考模型的扩展阅读

- **Gemini 系列**:https://ai.google.dev/gemini-api/docs/thinking
- **Gemini 在 OpenAI 兼容下的交错思考**:https://ai.google.dev/gemini-api/docs/thought-signatures
- **GLM 的交错思考 / 回合级思考控制**:https://docs.z.ai (Thinking Mode - Overview)

### 1.6 多模态调用:content 字段的 6 种类型

文本调用时,`content` 是字符串。**多模态时,`content` 变成数组**:

```javascript
{
  role: "user",
  content: [
    { type: "image_url", image_url: { url: "https://example.com/cat.png" } },
    { type: "text", text: "图片里有什么?" }
  ]
}
```

`content` 数组里的元素类型(以 TypeScript 风格定义):

```typescript
type ContentItem = {
  type: "text" | "image_url" | "input_audio" | "file" | "video_url",
  text?: string,
  image_url?: {
    url?: string,           // HTTP 链接 或 data:[MIME];base64,xxx
    detail?: "low" | "high" | "auto"   // 控制后台分辨率
  },
  input_audio?: {
    data?: string,          // Base64 音频
    format?: "wav" | "mp3"
  },
  file?: {
    filename?: string,
    file_data?: string,     // Base64
    file_id?: string
  },
  video_url?: {
    url?: string            // 在线视频链接,部分厂商支持 Base64
  },
  
  // 阿里百炼 Qwen3-VL 特有
  fps?: number,             // 视频理解参数
  max_pixels?: number       // 视觉理解像素阈值
}
```

#### 图片转 Base64 的代码骨架

```javascript
import { readFileSync } from 'node:fs';

const encodeImage = (imagePath) => {
  return readFileSync(imagePath).toString('base64');
};

// 使用
const base64Image = encodeImage('./cat.png');
const dataUri = `data:image/png;base64,${base64Image}`;
```

> 💡 **实时多模态、Omni 等实验性模型的调用方法略**——这些目前还没有统一格式,各家差异巨大,**用前必看官方文档**。

---

## 2. 4 类经典坑

### 2.1 坑 1:role 不止 system/user/assistant 三种

在接入各种模型时,常见报错:

```
[{'type': 'value_error', 'loc': ('body', 'messages', 0, 'role'), 
  'msg': "Value error, 'role' must be one of 'system', 'assistant', 'user'..."}]
```

**为什么会出错?难道 role 不就是这三个吗?** 实际上,role 远不止三个:

| Role | 对应概念 | 主要使用平台 | 备注 |
|---|---|---|---|
| `system` | 系统指令 | OpenAI / Mistral / Llama / Ollama | **最基础的角色,定义 AI 人设** |
| `user` | 用户输入 | 所有平台 | **核心角色** |
| `assistant` | AI 回复 | OpenAI / Anthropic / Mistral / Ollama | **核心角色** |
| **`model`** | AI 回复 | **Google Gemini / Vertex AI** | **Google 专用,等同于 assistant** |
| **`developer`** | 开发者指令 | **OpenAI o1 系列** | **新特性,权重高于 system,用于推理模型** |
| `tool` | 工具结果 | OpenAI / Mistral(新版)| 回传函数 / 工具执行结果 |
| `function` | 函数结果 | OpenAI(旧版)/ Google(部分)| **`tool` 的旧称**,仍广泛兼容 |
| `human` | 用户(框架层)| LangChain | **最终会转换为 user** |
| `ai` | AI 回复(框架层)| LangChain | **最终会转换为 assistant** |

**常见踩坑场景**:

- ❌ 直接把 LangChain 的 `human/ai` 传给 OpenAI 兼容接口
- ❌ 给 Gemini 传 `assistant`(应该是 `model`)
- ❌ 给非 o1 模型传 `developer`

### 2.2 坑 2:御三家的"严格参数"问题

大部分模型服务对请求参数比较宽松——**传了不需要的参数也会自动忽略**。

**但御三家(OpenAI 严格模型 / Anthropic / Google)卡得比较死**:

```
错误场景:
  你的代码模板写着 top_p / top_k / repetition_penalty
  发给 DeepSeek/中转 → 自动忽略 ✅
  发给 OpenAI o1 系列 → 直接报错 ❌
  发给 Anthropic Claude → 直接报错 ❌
```

**正确做法**:

> 🔑 **千万要按需注入参数,而不是直接写在请求模板里。**

代码层面建议:

```javascript
// ❌ 错误:固定模板
const payload = {
  model, messages, stream, 
  temperature, top_p, top_k,         // ← 万一目标模型不支持就炸
  presence_penalty, frequency_penalty
};

// ✅ 正确:按需构造
const payload = { model, messages, stream };
if (modelSupports.temperature) payload.temperature = 0.7;
if (modelSupports.topP) payload.top_p = 0.9;
if (modelIsThinking) payload.reasoning_effort = "high";
```

### 2.3 坑 3:`/v1` 前缀的坑

请求端点的细节:

```
DeepSeek 官方:  https://api.deepseek.com/v1/chat/completions
某中转站:       https://x-router.io/api/v1/chat/completions
阿里云百炼:     https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
                                  ^^^^^^^^^^^^^^^^^
```

- 有的 AI 应用会**自动补 `/v1` 前缀**
- 而有的服务商前缀**不一定是 `/v1`**(如阿里百炼)

> 💡 **debug 时**:**请求失败先打印最终请求的端点 URL 到底是个什么东西**。

### 2.4 坑 4:`finish_reason=length` 时 JSON 截断

```
你想要的:    {"name": "李天梭", "age": 24, "skills": [...]}
实际得到的:  {"name": "李天梭", "age": 24, "skills": ["代码", "设
                                                              ↑ 在这里被截断
```

**为什么**:`max_tokens` 设小了或 prompt 太长,**token 用完了**。

**症状**:
- `finish_reason == "length"`
- 内容是不完整 JSON,`JSON.parse()` 报错

**应对**:

```javascript
const data = await resp.json();
const finish = data.choices[0].finish_reason;

if (finish === "length") {
  console.warn("内容被截断,考虑增大 max_tokens");
  // 或者重试一次,或者拆分任务
}

if (finish === "content_filter") {
  console.warn("内容被审查拦截");
  // Gemini 还要看 promptFeedback
}
```

---

## 3. OpenAI Response API(新款)

> 💡 **作者吐槽**:"除了 gpt5 系列以外谁会用 Responses API 啊"——这是 OpenAI 自己推的新规范,**目前生态使用度还在爬坡**。

**端点**:`POST /v1/responses`

### 与 Chat Completion 的关键差异

| 维度 | Chat Completion | Response API |
|---|---|---|
| 输入字段 | `messages` 数组 | **`input`**(可字符串,或 messages 数组,或内容块数组)|
| 输出结构 | `choices` 数组 | **`response` 对象**(含 `output` 数组、聚合 `usage`)|
| 流式标志 | 只有 `data:` | **`event:` 行 + `data:` 行**(完整 SSE) |
| max tokens 字段名 | `max_tokens` | **`max_output_tokens`** |
| 多模态内容块 | `image_url` / `input_audio` | **`input_image` / `input_audio` / `input_text`** |
| 工具调用 | 一阶段 | **二阶段**(需 `/responses/{id}/tool_outputs`)|
| 结构化输出 | `response_format.type` | **`response_format.json_schema.strict=true`** |

### 6 大常见坑

1. **`max_*` 字段名**:Response 普遍用 `max_output_tokens`;部分兼容服务仍用 `max_tokens`。**以目标服务文档为准**,避免抄错
2. **流事件名**:Response 流含 `event:` 行(与 Chat Completion 只有 `data:` 不同)。**解析时务必读取 `event:`**,根据事件名路由处理(`response.output_text.delta`、`response.completed` 等)
3. **JSON 严格性**:`json_object` 只是"尽量 JSON";要强约束用 `json_schema.strict=true`。**但严格模式更可能触发拒绝/空输出**
4. **工具调用为二阶段**:记得对接 `/responses/{id}/tool_outputs`。参数流式到达(`*.delta`)需拼接再 `JSON.parse`
5. **Reasoning 与 usage**:`reasoning` 只在部分模型有效;`reasoning_tokens` 仅在支持的事件 / 模型与 usage 中出现,**不保证一定返回**
6. **超时与断线**:SSE 建议使用 `AbortController` 设置超时;同时处理中断后重试策略

### 多模态命名差异

```
Chat Completion:    image_url, input_audio, file, video_url
Response API:       input_image, input_audio, input_text, output_*
```

> ⚠️ **作者警告**:本文 Response 示例中使用 OpenAI 官方 `input_text/input_image/input_audio/output_*` 命名;与通用 Chat 兼容示例中的 `image_url` 等命名不同,**注意区分**。

### 请求骨架

```javascript
const payload = {
  model: "gpt-5.2",
  input: "请设计一个 24 岁大学生角色的 JSON",
  response_format: { type: "json_object" },
  max_output_tokens: 500,         // ← 注意是 output 而非 tokens
  // reasoning: { effort: "high" },     // 思考强度
  seed: 1919810,
  user: "user_id_9527"            // 用于反滥用追踪
};
```

---

## 4. Gemini API(/v1beta)

**端点特征**:`/v1beta` 而非 OpenAI 的 `/v1`。

> 💡 **作者梗**:"基米我不许你管它叫 beta,它很成熟了 \\(\\^∇\\^)/"——这个 `/v1beta` 命名是历史包袱,实际成熟度很高。

**完整路径格式**:

```
/v1beta/models/{model_name}:{action}

action:
  generateContent       ← 非流式
  streamGenerateContent ← 流式
```

例如:`/v1beta/models/gemini-3-pro:generateContent`

### 与 OpenAI 兼容接口的 3 大重大差异

#### 差异 1:对话角色

| OpenAI | Gemini |
|---|---|
| `user` + `assistant` | **`user` + `model`** ← 注意! |

#### 差异 2:消息结构

OpenAI 是 `role + content`(简单字符串):

```javascript
{role: "user", content: "你好"}
```

**Gemini 是 `role + parts`(数组)**:

```javascript
{
  role: "user",
  parts: [
    {text: "你好"},                          // 文本
    {inlineData: {mimeType: "image/png", data: "base64..."}}  // 图片
  ]
}
```

#### 差异 3:响应中的 finishReason

Gemini 用驼峰命名(不是下划线),且有更多审查相关字段:

```javascript
{
  candidates: [{
    content: {parts: [{text: "..."}]},
    finishReason: "STOP" | "MAX_TOKENS" | "SAFETY" | "RECITATION",
    safetyRatings: [...]      // ← 各维度安全评分
  }],
  promptFeedback: {           // ← 提示词侧的安全审查
    blockReason: "SAFETY",
    safetyRatings: [...]
  }
}
```

### Gemini 常见坑:429 与内容审查

> ⚠️ **作者警告**:"比起其他家模型来说,基米很容易遇到 429,**所以要特别注意检查响应体的 `candidates.finishReason` 和 `candidates.promptFeedback` 以确定是否被安全审查过滤掉了**。Vertex 保平安!"

**正确的错误处理**:

```javascript
const data = await resp.json();

// 1. 检查请求侧是否被审查
if (data.promptFeedback?.blockReason) {
  console.error("提示词被审查:", data.promptFeedback.blockReason);
}

// 2. 检查响应侧的 finishReason
const reason = data.candidates?.[0]?.finishReason;
if (reason === "SAFETY") {
  console.error("响应被安全审查拦截");
} else if (reason === "RECITATION") {
  console.error("响应可能涉及版权内容");
}
```

### Gemini 文档优势

> 💡 **作者评价**:"基米的文档非常清晰直观,我认为远强于 OpenAI。而且无论是 Anthropic 还是 Gemini 都没吃过 OpenAI 兼容的苦,没那么多历史包袱,**直接看文档就行**。"

**推荐文档**:
- Google AI for Developers:https://ai.google.dev
- Gemini API 文本生成:https://ai.google.dev/gemini-api/docs/text-generation

---

## 5. Anthropic Messages API

很多服务商为了兼容 Claude Code,**也提供 Anthropic 格式的 API(Messages API)**。

**端点**:`POST {base_url}/v1/messages`

**请求示例**:

```javascript
{
  model: "claude-sonnet-4-7",
  max_tokens: 4096,
  messages: [
    {role: "user", content: "你好"}
  ],
  system: "你是一名资深游戏设计师",  // system 独立于 messages
  
  // 思考模式(Claude 特色)
  thinking: {
    type: "enabled",
    budget_tokens: 1024
  }
}
```

### Anthropic 接口的 3 个独特点

1. **`system` 独立字段**:不像 OpenAI 在 messages 里塞 system 消息,Anthropic 把它单独抽出来作为顶层字段
2. **`max_tokens` 必填**:不像 OpenAI 可选,Anthropic **必须显式指定**
3. **`thinking` 块**:Claude 的思考模式有显式 budget_tokens 控制

### Anthropic 常见坑:多轮签名携带

> ⚠️ **作者警告**:"由于大部分使用 Anthropic API 的场景都是发生在接入 Claude Code 时,所以要**特别注意多轮对话场景下签名携带的问题**,否则很容易导致 Claude Code 爆炸。"

**具体场景**:Claude Code 在多轮对话中会维护 **prefix cache 签名 / cache_control 字段**,中转或自实现需要正确转发,否则 Cache 命中失败 + 上下文丢失 + 响应混乱。

**推荐文档**:
- 快速入门:Anthropic Messages API quickstart
- API 详细:https://platform.claude.com/docs/en/api/messages

---

## 6. 4 种接口对比速查表

| 维度 | OpenAI Chat Completion | OpenAI Response API | Gemini | Anthropic Messages |
|---|---|---|---|---|
| **端点** | `/v1/chat/completions` | `/v1/responses` | `/v1beta/models/{m}:{action}` | `/v1/messages` |
| **输入字段** | `messages` | `input` | `contents` | `messages` |
| **system 位置** | messages 数组内 | input 数组内 | `systemInstruction` 顶层 | **`system` 顶层** |
| **assistant role 名** | `assistant` | `assistant` | **`model`** | `assistant` |
| **消息内容** | `content`(字符串或数组)| `input`(同左)| **`parts`** 数组 | `content`(字符串或数组)|
| **max tokens 字段** | `max_tokens` | **`max_output_tokens`** | `maxOutputTokens` | `max_tokens`(**必填**)|
| **流式触发** | `stream: true` | `stream: true` | 路径 `:streamGenerateContent` | `stream: true` |
| **流式格式** | SSE `data:` | SSE `event:` + `data:` | SSE | SSE |
| **finish 字段** | `finish_reason` | `output[].status` / `response.completed` | **`finishReason`**(驼峰)| `stop_reason` |
| **思考控制** | `reasoning_effort` | `reasoning.effort` | `thinkingConfig` | **`thinking.budget_tokens`** |
| **多模态图片** | `image_url` | **`input_image`** | `inlineData` + `mimeType` | `image` 块 |
| **审查标志** | `content_filter` | 同左 | **`safetyRatings` + `promptFeedback`** | — |

---

## 7. 与本知识库其他章节的关联

### 7.1 调用之前

- 选哪个模型 → [各家 LLM 模型特点速查](各家LLM模型特点速查.md):16 个家族的核心定位
- 选哪个 API 提供商 → [LLM-API 选型方法论](LLM-API选型方法论.md):5 维度框架 + 提供商表

### 7.2 调用涉及的概念

- Token 与计费 → [上下文窗口与 Token 计费](../00_核心概念/上下文窗口与Token计费.md)
- Prompt Caching(Anthropic / DeepSeek 都支持)→ 同上
- 思考模型基础 → [模型训练技术速查](../00_核心概念/模型训练技术速查.md):o1 系列、R1 等

### 7.3 工程实践

- Claude Code 接入国产模型 → [Claude Code 实战速查](../06_Agent工程/Claude%20Code%20实战速查.md):3 家国产模型 ANTHROPIC_AUTH_TOKEN 配置实例
- 多 CLI 协同 → [多 CLI 联动](../05_技术基础/多CLI联动.md):3 家协同的 4 种玩法
- 提示词最佳实践 → [02_提示词工程/](../02_提示词工程/README.md)

### 7.4 与 Agent 的关系

- Function Calling 与 MCP(下一篇待填坑)→ 暂参考 [Claude Code 扩展生态](../06_Agent工程/Claude%20Code%20扩展生态.md)
- Agent 安全(提示词注入)→ [Agent 安全攻防](../06_Agent工程/Agent安全攻防.md)

### 7.5 真实业务场景案例

- **多模态接口的实战落地**:[宠物CT影像AI辅助诊断方案.md](宠物CT影像AI辅助诊断方案.md)——DICOM 切片 → Base64 编码 → `content` 数组 → 多模态大模型分析的完整链路,以及 Gemini/GPT/Claude 三家多模态接口的实战选择
- **Function Calling 与 MCP 完整指南**:[Function Calling与MCP工程指南.md](../06_Agent工程/Function%20Calling与MCP工程指南.md)——本文 § 1.3 提到的 `finish_reason: tool_calls` 完整时序、御三家工具调用差异、MCP 协议

---

## 8. 术语速查

| 术语 | 全称 | 含义 |
|---|---|---|
| **Chat Completion** | — | OpenAI 的聊天补全接口,主流接口 |
| **Completion** | — | OpenAI 的老式文本补全接口,**别用** |
| **Response API** | — | OpenAI 推的新接口规范(2025 年起) |
| **Messages API** | — | Anthropic 的接口规范 |
| **SSE** | Server-Sent Events | 服务器推送事件,HTTP 长连接,**流式响应的底层协议** |
| **delta** | — | 流式 chunk 中的"增量内容"字段 |
| **chunk** | — | SSE 流中的一个数据块 |
| **role** | 角色 | system / user / assistant / model / tool / function / developer 等 |
| **finish_reason** | — | OpenAI 风格:`stop` / `length` / `content_filter` / `tool_calls` |
| **finishReason** | — | Gemini 风格(驼峰):`STOP` / `MAX_TOKENS` / `SAFETY` / `RECITATION` |
| **stop_reason** | — | Anthropic 风格 |
| **system_fingerprint** | — | OpenAI 的"后端配置指纹",**模型重大更新时变化** |
| **reasoning_tokens** | — | 思考模型不可见但计费的思考 token 数 |
| **reasoning_content** | — | 非标准字段,DeepSeek/GLM 等返回的思考过程 |
| **prompt_tokens** | — | 输入 token 数 |
| **completion_tokens** | — | 输出 token 数 |
| **content** | — | OpenAI 消息内容字段 |
| **parts** | — | **Gemini 的消息内容字段**(数组,非字符串)|
| **input** | — | **Response API 的输入字段**(对应 messages) |
| **base_url** | — | API 服务地址前缀 |
| **promptFeedback** | — | Gemini 提示词侧的安全审查反馈 |
| **safetyRatings** | — | Gemini 各维度安全评分 |
| **AbortController** | — | JavaScript 用于取消 fetch 请求的 API,**SSE 超时必备** |
| **Function Calling / Tool Use** | — | LLM 调用外部工具的能力,本文未深讲 |
| **MCP** | Model Context Protocol | Anthropic 推的工具协议,详见 [Claude Code 扩展生态](../06_Agent工程/Claude%20Code%20扩展生态.md) |
| **prefix cache** | 前缀缓存 | Anthropic / DeepSeek 等支持的"重复前缀复用缓存"机制 |
| **cache_control** | — | Anthropic Messages API 的缓存控制字段 |
| **`Bearer` Token** | — | HTTP Authorization Header 标准格式 |

---

## 9. 来源、评分与可商榷点

### 9.1 来源

- **原始素材**:LINUX DO 社区 @flymyd 的「简单易懂的 LLM 相关知识梳理」系列
  - **ep.5 常见接口规范的介绍及实践中的坑**(2026 年 1 月 22 日)
- **整理日期**:2026 年 5 月 24 日

### 9.2 笔者评分

| 维度 | 评分 |
|---|---|
| 实战代码 | ★★★★★ |
| 4 接口对比清晰度 | ★★★★★ |
| 坑表实用性 | ★★★★★ |
| 时效性 | ★★★★★ |
| 可读性 | ★★★★☆(原文代码示例较长,本笔记已简化) |
| **总分** | **9 / 10** |

### 9.3 笔记吸收策略

- ✅ **完整吸收**:4 种接口的核心字段与差异
- ✅ **完整吸收**:9 种 role 速查表 + finish_reason 4 种值
- ✅ **完整吸收**:6 大 Response API 坑 + 多模态命名差异
- ✅ **新增**:4 种接口对比速查表(原文是分章节讲,我做了横向对比)
- ✂️ **代码简化**:原文有大量完整可运行的 JS 代码,本文只保留**核心字段示例**(知识库不是教程,需要时去看原文 / 官方文档)
- ⚠️ **保留作者梗**:"A÷" / "基米" / "Vertex 保平安" 等用引用块标注

### 9.4 作者没覆盖到的(可补充方向)

1. **Function Calling / Tool Use 的具体格式**:作者明说"在 ep.6 讲",目前是空缺
2. **MCP 协议**:Anthropic 推的工具协议,作者未涉及(本知识库有 [Claude Code 扩展生态](../06_Agent工程/Claude%20Code%20扩展生态.md))
3. **Embedding API 格式**:作者 ep.7 待填,目前是空缺
4. **WebSocket 实时接口**:OpenAI Realtime API、Gemini Live API 等实时多模态,作者明说"略,有兴趣自查官方文档"
5. **SDK 最佳实践**:作者只讲 HTTP,但实际工程中 Python `openai` / TypeScript `openai` / `@anthropic-ai/sdk` 用得多,这些 SDK 的:
   - 自动重试策略
   - 流式响应处理封装
   - Token 计数本地预估
   - 错误分类与重试时机
   - **这些都是工程化必备,作者没讲**
6. **rate limit / quota**:不同 API 提供商的限速策略(RPM / TPM / TPD)与处理建议
7. **多模型 fallback 实现**:**核心工程问题**(主模型挂了切备模型),但需要 API 抽象层
8. **结构化输出的实战**:json_schema vs json_object vs 普通输出 + prompt 提示,作者只提了字段没深入
9. **批量请求(Batch API)**:OpenAI / Anthropic 都有 Batch API(半价,24h 内返回),作者未提
10. **审计日志格式**:企业级合规要求 API 调用的全量审计日志,各家格式差异

### 9.5 接口规范的时效性提醒

> 📅 截至 2026 年 5 月:
>
> - **OpenAI Response API 仍在演进**——字段命名 / 工具调用 / 多模态格式可能继续变化
> - **Gemini 仍叫 `/v1beta`**,虽然实际是 GA 状态
> - **Anthropic 的 `cache_control` 持续增强**——Prompt Caching 类型从 ephemeral 扩展到更长 TTL
>
> **每月 follow 一次官方 changelog 是必要的**。

### 9.6 主观色彩的提醒

作者写作风格非常工程师社区化:

- "**OpenAI 兼容接口一把梭不就好了吗?**"——这是早期开发者的天真,作者用反讽方式开篇
- "**基米我不许你管它叫 beta,它很成熟了**"——亲切吐槽 Google 的 `/v1beta` 命名
- "**Vertex 保平安**"——Google Cloud Vertex 的企业服务审查较低
- "**除了 gpt5 系列以外谁会用 Responses API 啊**"——对 OpenAI 推新规范的吐槽

**洞察都是真实工程经验**,直接照搬即可。
