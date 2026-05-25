# LLM 推理引擎选型:vLLM / SGLang / llama.cpp / Ollama / LMDeploy / TensorRT-LLM / MLX

> **一句话**:有了模型和显卡,**怎么把模型跑起来对外提供服务?**——这就是推理引擎的事。**模型只是参数文件,推理引擎才是"让模型每秒吐 Token 的发动机"**。本文是 7 大主流推理引擎的横向对比 + 选型决策树 + 各引擎"最适合的场景"指南。
>
> ⚠️ **本篇为 Claude 原创补充笔记**,非 LINUX DO @flymyd 原稿(详见末尾「作者声明」)。
> 📌 **填坑提示**:[本地部署模型量化选型.md § 1](本地部署模型量化选型.md) 末尾标注"推理引擎不在本篇范围",本篇就是填这个坑。

---

## 目录

- [0. 推理引擎是什么 / 为什么需要它](#0-推理引擎是什么--为什么需要它)
- [1. 七大主流引擎一句话定位](#1-七大主流引擎一句话定位)
- [2. 选型决策树](#2-选型决策树)
- [3. 各引擎详解](#3-各引擎详解)
  - [3.1 vLLM:服务端王者](#31-vllm服务端王者)
  - [3.2 SGLang:结构化输出与高吞吐双王](#32-sglang结构化输出与高吞吐双王)
  - [3.3 llama.cpp:CPU/边缘/HomeLab 之王](#33-llamacppcpu边缘homelab-之王)
  - [3.4 Ollama:小白友好包装](#34-ollama小白友好包装)
  - [3.5 LMDeploy:国产推理引擎](#35-lmdeploy国产推理引擎)
  - [3.6 TensorRT-LLM:NVIDIA 官方最高性能](#36-tensorrt-llmnvidia-官方最高性能)
  - [3.7 MLX:Apple Silicon 专属](#37-mlxapple-silicon-专属)
- [4. 核心性能优化技术](#4-核心性能优化技术)
- [5. 横向对比速查表](#5-横向对比速查表)
- [6. 实战部署示例](#6-实战部署示例)
- [7. 与本知识库其他章节的关联](#7-与本知识库其他章节的关联)
- [8. 术语速查](#8-术语速查)
- [9. 作者声明、来源与局限性](#9-作者声明来源与局限性)

---

## 0. 推理引擎是什么 / 为什么需要它

### 0.1 朴素做法:用 PyTorch 直接推理(性能拉胯)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B").cuda()
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")

inputs = tokenizer("写一个排序算法", return_tensors="pt").to("cuda")
output = model.generate(**inputs, max_new_tokens=500)
```

**这能跑,但效率极低**:
- 一次只能伺候 1 个请求
- 每个新请求都从头算 KV cache,无法跨请求复用
- 显存碎片严重,跑不了大 batch
- 没有 continuous batching,GPU 利用率 30% 左右就上不去了

### 0.2 推理引擎做了什么

| 优化项 | 朴素 PyTorch | 推理引擎 |
|---|---|---|
| **并发请求** | 串行 | **连续批处理(Continuous Batching)** |
| **KV cache 管理** | 每请求独立 | **PagedAttention**(显存按页分配,几乎无碎片) |
| **量化推理** | 需手动改代码 | **原生支持** GPTQ / AWQ / FP8 / GGUF |
| **吞吐 vs 延迟** | 顾此失彼 | **可调度策略** |
| **多卡并行** | DDP 麻烦 | **Tensor Parallelism / Pipeline Parallelism 一行配置** |
| **结构化输出** | 需后处理 | **Grammar / JSON Schema 约束解码** |
| **prompt caching** | 无 | **前缀复用** |
| **OpenAI 兼容 API** | 需自己包 | **原生提供** |

> 💡 **真实差距**:在 4090 上跑 Qwen-7B,朴素 PyTorch 约 30 tokens/s,**vLLM 在多并发下能跑到 1000+ tokens/s(总吞吐)**——差 30 倍。

---

## 1. 七大主流引擎一句话定位

| 引擎 | 一句话定位 | 主要场景 | 团队/出处 |
|---|---|---|---|
| **vLLM** | 服务端推理王者,生态最全 | 企业 / 多用户 / 高并发 API | UC Berkeley + 社区 |
| **SGLang** | 编程接口最强,结构化输出王 | RAG / Agent / 复杂程序化推理 | UC Berkeley LMSys |
| **llama.cpp** | CPU / 边缘 / 量化王者 | HomeLab / Mac / 树莓派 / 手机 | ggerganov 个人项目 |
| **Ollama** | 小白友好包装,一键运行 | 个人玩家 / 快速试模型 | Ollama Inc(基于 llama.cpp)|
| **LMDeploy** | 国产推理引擎,InternLM 出品 | 国内 toB 落地 | 上海 AI Lab |
| **TensorRT-LLM** | NVIDIA 官方最高性能 | 极致延迟敏感场景 | NVIDIA |
| **MLX** | Apple Silicon 专属 | M 系列 MacBook | Apple 官方 |

> 📌 **遗珠**:Hugging Face 的 `text-generation-inference (TGI)` 也是主流之一,但在中文社区使用度不如 vLLM,本文略。其他还有 LightLLM、TurboMind(后被并入 LMDeploy)、Triton Inference Server(NVIDIA 的更底层调度器)。

---

## 2. 选型决策树

```
你要部署 LLM 推理服务?
  │
  ├─ 设备类型?
  │
  ├──→ NVIDIA GPU,服务器,要对外提供 API
  │     ├─→ 高并发企业场景? ──── vLLM(生态最全)
  │     ├─→ 结构化输出/RAG/Agent? ─ SGLang
  │     ├─→ 极致低延迟(单请求 50ms)? ─ TensorRT-LLM
  │     ├─→ 国产模型 + 国内 toB? ─── LMDeploy
  │     └─→ InternLM / Qwen 全家? ── LMDeploy / vLLM 都可
  │
  ├──→ NVIDIA GPU,个人 HomeLab
  │     ├─→ 想要"一键运行"? ────── Ollama
  │     ├─→ 想要"开 API 给家庭网用"? ─ Ollama / llama.cpp server
  │     └─→ 显卡很差(老 P40 / 1080Ti)? ─ llama.cpp(量化好,显存省)
  │
  ├──→ CPU 推理(无 GPU)
  │     └─→ llama.cpp(几乎是唯一选)
  │
  ├──→ Mac(M1/M2/M3/M4)
  │     ├─→ 想要最快推理? ──────── MLX
  │     ├─→ 兼顾通用性? ────────── llama.cpp(MPS 后端)
  │     └─→ 小白图省事? ────────── Ollama(底层就是 llama.cpp)
  │
  └──→ Windows + GPU
        └─→ Ollama(原生支持,不需要 WSL)
        └─→ LM Studio(图形界面,基于 llama.cpp)
```

---

## 3. 各引擎详解

### 3.1 vLLM:服务端王者

**项目**:https://github.com/vllm-project/vllm

#### 核心创新:PagedAttention

vLLM 由 UC Berkeley 团队 2023 年开源,**核心创新是 PagedAttention**:

```
传统 KV cache 管理:
  每个请求预分配一大块连续显存 → 显存碎片严重 + 无法动态扩容

PagedAttention:
  把 KV cache 切成固定大小的"页"(类似 OS 虚拟内存)
  按需分配 + 跨请求共享 + 几乎零碎片
```

**效果**:相比 HuggingFace Transformers 的朴素推理,**吞吐提升 2-4 倍**,显存利用率 96%+。

#### 适用场景

- ✅ 企业级 OpenAI 兼容 API 服务
- ✅ 多用户高并发(continuous batching 后吞吐线性扩展)
- ✅ 主流模型(Llama / Qwen / DeepSeek / GLM / Mistral / Phi 等)的官方支持非常及时
- ✅ 多卡 Tensor Parallelism 一行配置
- ✅ 主流量化方案(GPTQ / AWQ / FP8 / FP4)一应俱全

#### 不适用场景

- ❌ CPU 推理(不支持)
- ❌ Apple Silicon(不支持)
- ❌ 资源极少的端侧(它是为服务器设计的)

#### 简易部署

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-7B \
  --port 8000 \
  --tensor-parallel-size 1
```

启动后即可用 OpenAI SDK 调用 `http://localhost:8000/v1/`。

### 3.2 SGLang:结构化输出与高吞吐双王

**项目**:https://github.com/sgl-project/sglang

#### 核心创新

SGLang 是 LMSys 团队(也是 Vicuna / Chatbot Arena 团队)的新作,**两大特点**:

1. **RadixAttention**:基于 Radix Tree 的 prompt 前缀缓存——多个请求共享相同前缀时**自动复用 KV cache**,适合 few-shot / RAG / Agent
2. **结构化输出**:**正则约束 / JSON Schema / Grammar** 强制模型输出符合给定结构,**速度远快于"事后解析+重试"**

#### 适用场景

- ✅ **RAG 系统**(prompt 模板相同,变化的只是检索结果) → RadixAttention 大杀器
- ✅ **Agent 系统**(多轮 + 工具调用 + ReAct 循环) → SGLang 的 SGLProgram DSL 专为此设计
- ✅ **强 JSON / 结构化输出场景**(法律文书提取、医学报告生成等)
- ✅ 性能上 **2024 年起在多个 benchmark 超过 vLLM**

#### 不适用场景

- ❌ 模型支持范围比 vLLM 略窄(但主流模型都支持)
- ❌ 生态成熟度不如 vLLM(社区文档、第三方教程少)

#### 简易部署

```bash
pip install "sglang[all]"
python -m sglang.launch_server \
  --model-path Qwen/Qwen3-7B \
  --port 8000
```

#### SGLang 程序示例(独有的 DSL)

```python
import sglang as sgl

@sgl.function
def multi_turn_qa(s, question):
    s += sgl.user("你是 Linux 运维专家")
    s += sgl.user(question)
    s += sgl.assistant(sgl.gen("answer", max_tokens=256))
    s += sgl.user("用一句话总结")
    s += sgl.assistant(sgl.gen("summary", max_tokens=64))

# 一次调用拿到 answer 和 summary
state = multi_turn_qa.run(question="什么是 systemd?")
print(state["answer"], state["summary"])
```

### 3.3 llama.cpp:CPU / 边缘 / HomeLab 之王

**项目**:https://github.com/ggerganov/llama.cpp

#### 起源与定位

Georgi Gerganov(一个保加利亚开发者)2023 年 3 月 LLaMA 泄露后用 C++ 重写推理,**核心目标:让大模型能在 MacBook、树莓派甚至手机上跑**。

**核心特性**:
- **纯 C/C++ 实现**,无 Python / 框架依赖
- **GGUF 格式**:专为 llama.cpp 设计的量化文件格式,一文件含权重+元数据+tokenizer
- **超强量化**:支持 1.5-bit、2-bit、3-bit 等极致量化
- **CPU/GPU/Apple Silicon 全栈支持**(CUDA / Metal / Vulkan / SYCL 后端)
- **Server 模式**:提供 OpenAI 兼容 API

#### 适用场景

- ✅ **CPU 推理**(几乎是唯一选择)
- ✅ **Apple Silicon**(Metal 后端,推理速度不错)
- ✅ **老旧 GPU**(P40 / 1080Ti 等没 Tensor Core 的卡)
- ✅ **HomeLab**(轻量、单文件、配置简单)
- ✅ **手机 / 树莓派 / 边缘设备**

#### 不适用场景

- ❌ **企业级高并发**(吞吐不如 vLLM)
- ❌ **大 batch size 训练**(它是纯推理)
- ❌ **multi-LoRA 动态加载**(支持有限)

#### 简易部署

```bash
# 1. 编译
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON   # 或 -DGGML_METAL=ON(Apple)
cmake --build build --config Release -j

# 2. 下载 GGUF 模型
huggingface-cli download bartowski/Qwen3-7B-Instruct-GGUF Qwen3-7B-Instruct-Q4_K_M.gguf

# 3. 跑(命令行交互)
./build/bin/llama-cli -m Qwen3-7B-Instruct-Q4_K_M.gguf -p "你好"

# 4. 跑(OpenAI 兼容 API server)
./build/bin/llama-server -m Qwen3-7B-Instruct-Q4_K_M.gguf --port 8080
```

### 3.4 Ollama:小白友好包装

**项目**:https://github.com/ollama/ollama

#### 定位

Ollama 不是新推理引擎——它**底层就是 llama.cpp 的封装**。但它做了三件让小白爽到飞起的事:

1. **Docker 式模型管理**:`ollama pull qwen3:7b` / `ollama run qwen3:7b` / `ollama list`
2. **后台 daemon 模式**:开机自启,后台运行,随时调用
3. **跨平台一键安装**:Windows / macOS / Linux 都有官方安装包

#### 适用场景

- ✅ **完全没碰过 LLM 的新手**(5 分钟跑起来 Qwen 7B)
- ✅ **个人玩家快速试模型**(`ollama pull` 几十个主流模型一键切换)
- ✅ **家庭 LAN 共享 LLM**(开 API 给家人/同事用)
- ✅ **macOS 上跑大模型**(因为底层是 llama.cpp + Metal)

#### 不适用场景

- ❌ **企业高并发**(底层 llama.cpp 的吞吐天花板)
- ❌ **极致性能优化**(参数调优能力远不如 vLLM/SGLang)
- ❌ **需要细粒度控制推理过程**(被 Ollama 包了一层,改起来麻烦)

#### 使用极简(真的就这么简单)

```bash
# 1. 安装
curl -fsSL https://ollama.com/install.sh | sh        # Linux
# 或下载 Mac/Windows 安装包

# 2. 拉模型
ollama pull qwen3:7b
ollama pull deepseek-r1:14b
ollama pull llama3.1:8b

# 3. 交互
ollama run qwen3:7b

# 4. API 调用(OpenAI 兼容)
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:7b",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 3.5 LMDeploy:国产推理引擎

**项目**:https://github.com/InternLM/lmdeploy

#### 定位

上海 AI Lab(InternLM 团队)开源,**整合了原 TurboMind**(早期国产高性能推理引擎)+ PyTorch 后端,**针对 InternLM / Qwen / DeepSeek 等国产模型深度优化**。

#### 核心特性

- **TurboMind 后端**:针对 NVIDIA GPU 的高性能 C++ 实现,**与 vLLM 性能相当**
- **PyTorch 后端**:支持更广泛的模型架构,易于 debug
- **多模态支持**:针对 InternVL / Qwen-VL 等做了优化
- **AWQ / GPTQ / SmoothQuant** 量化原生支持
- **完善的中文文档**

#### 适用场景

- ✅ **国内 toB 场景**(中文文档好、国产模型适配好)
- ✅ **InternLM / Qwen / DeepSeek / Yi / Mixtral** 等模型
- ✅ **多模态模型**(VLM 系列)
- ✅ **昇腾 NPU 部分支持**(虽然不如华为 MindIE 完整)

#### 不适用场景

- ❌ **生态丰富度不如 vLLM**(社区资源相对少)
- ❌ **非国产模型的支持滞后**(Llama 最新版可能晚几周)

#### 简易部署

```bash
pip install lmdeploy
lmdeploy serve api_server Qwen/Qwen3-7B \
  --server-port 8000 \
  --backend turbomind
```

### 3.6 TensorRT-LLM:NVIDIA 官方最高性能

**项目**:https://github.com/NVIDIA/TensorRT-LLM

#### 定位

NVIDIA 官方推出,**集成 TensorRT(NVIDIA 的推理优化器)+ LLM 优化**。**理论性能上限最高**,但学习曲线最陡峭。

#### 核心特性

- **算子级别优化**:针对每张卡架构(Ampere / Hopper / Ada / Blackwell)单独优化
- **In-flight Batching**:类似 continuous batching
- **FP8 / FP4 原生支持**(在 Hopper / Blackwell 上能发挥到极致)
- **多 GPU + 多节点**:NVIDIA 官方支持
- **Triton Inference Server 集成**:可以无缝接入 NVIDIA 的部署体系

#### 适用场景

- ✅ **延迟极度敏感**(金融交易 AI / 实时语音对话)
- ✅ **NVIDIA 数据中心 GPU 集群**(H100 / B200)
- ✅ **极致性能要求**,愿意付出复杂的部署代价
- ✅ **企业有 NVIDIA AI Enterprise 授权 + 厂商支持**

#### 不适用场景

- ❌ **个人 / 小团队**(学习成本太高,编译 engine 都要折腾几小时)
- ❌ **快速迭代**(每换一个模型 / 改一个参数都要重新编译)
- ❌ **非 NVIDIA 硬件**(完全锁定 NVIDIA)

#### 使用门槛说明

TensorRT-LLM 不是 `pip install` 就完事——需要:
1. 用 TensorRT-LLM 的 Python API 把 HuggingFace 模型**转换为 TensorRT engine**
2. 编译 engine 需要几分钟到几小时
3. engine 与硬件 / 量化方案强绑定,**换张卡就得重新编译**
4. 然后用 Triton Inference Server 包装成 API

**普通用户不推荐**,除非追求极致性能且有专门工程师维护。

### 3.7 MLX:Apple Silicon 专属

**项目**:https://github.com/ml-explore/mlx

#### 定位

Apple 2023 年底开源,**专为 Apple Silicon 统一内存架构设计的深度学习框架**(同时支持训练和推理)。

#### 核心特性

- **统一内存零拷贝**:CPU / GPU 共享同一片内存,无需在 RAM / VRAM 间复制
- **Python / Swift API**
- **MLX-LM**:专门的 LLM 推理工具包
- **比 llama.cpp 在 Apple Silicon 上更快**(尤其 M3/M4 系列)

#### 适用场景

- ✅ **M 系列 MacBook 用户**(尤其 M3 Max / M4 Pro 这种 64GB+ 内存的)
- ✅ **想跑 30B+ 模型在 Mac 上**(M2 Ultra 192GB 能跑 Llama 70B Q4)
- ✅ **既要推理又要微调**(MLX 支持训练)

#### 不适用场景

- ❌ **任何非 Apple Silicon**(完全平台专属)
- ❌ **要 OpenAI 兼容 API**(需配合 `mlx-server` 等第三方包)

#### 简易部署

```bash
pip install mlx-lm

# 推理
python -m mlx_lm.generate \
  --model mlx-community/Qwen3-7B-Instruct-4bit \
  --prompt "你好"

# OpenAI 兼容 server(需额外安装)
pip install mlx-server
mlx-server --model mlx-community/Qwen3-7B-Instruct-4bit
```

---

## 4. 核心性能优化技术

理解这些技术,选型时能看懂"为什么 X 比 Y 快":

### 4.1 Continuous Batching(连续批处理)

**朴素 batch**:等所有请求都到齐了一起算 → 短请求等长请求,GPU 空转

**Continuous batching**:新请求随时插入 batch,已完成的请求随时移出 → **GPU 利用率 90%+**

> 💡 vLLM / SGLang / LMDeploy / TensorRT-LLM 都默认开启。

### 4.2 PagedAttention(vLLM 原创)

详见 [§ 3.1](#31-vllm服务端王者)。

### 4.3 RadixAttention(SGLang 原创)

基于 Radix Tree 的 prompt 前缀缓存:

```
请求 A:"你是法律顾问。问题:合同 X 怎么签?" 
请求 B:"你是法律顾问。问题:遗嘱怎么写?"

→ 前缀"你是法律顾问。问题:" 的 KV cache 自动共享,只算后半段
```

适合 RAG / Agent 场景,**前缀重复率高达 80%+ 时,推理速度提升 2-5 倍**。

### 4.4 Speculative Decoding(投机解码)

用一个小模型"草拟"几个 token,大模型"验证"——验证通过则一次接受多个 token,**推理速度 1.5-3 倍**。

vLLM / SGLang / TensorRT-LLM 都支持,但需要小模型(draft model)配套。

### 4.5 Tensor Parallelism / Pipeline Parallelism

| 并行方式 | 拆分维度 | 适用场景 |
|---|---|---|
| **Tensor Parallelism (TP)** | 把每层的矩阵切分到多卡 | 单节点多卡,NVLink 互联 |
| **Pipeline Parallelism (PP)** | 把不同层放到不同卡 | 多节点,卡间带宽弱时 |
| **Expert Parallelism (EP)** | MoE 专家分到不同卡 | 大 MoE 模型(DeepSeek V3、Mixtral 8x22B) |

> 📌 **个人用户**:**单卡能跑就单卡**,多卡 TP/PP 会引入显著通信开销,不一定更快。

### 4.6 量化与算子优化

详见 [本地部署模型量化选型.md § 6](本地部署模型量化选型.md):**Marlin / Machete / FP8 native** 等内核针对不同卡架构优化。

---

## 5. 横向对比速查表

| 维度 | vLLM | SGLang | llama.cpp | Ollama | LMDeploy | TensorRT-LLM | MLX |
|---|---|---|---|---|---|---|---|
| **OpenAI 兼容 API** | ✅ | ✅ | ✅ | ✅ | ✅ | (需 Triton) | (需 mlx-server) |
| **服务端高并发** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **CPU 推理** | ❌ | ❌ | ✅ | ✅ | 部分 | ❌ | ❌ |
| **NVIDIA GPU** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Apple Silicon** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **AMD GPU(ROCm)** | ✅(实验) | ✅(实验) | ✅ | ✅ | 部分 | ❌ | ❌ |
| **昇腾 NPU** | 实验 | ❌ | ❌ | ❌ | 部分 | ❌ | ❌ |
| **结构化输出 / Grammar** | 部分 | ⭐⭐⭐⭐⭐ | 部分 | 基础 | 部分 | 部分 | 基础 |
| **多 LoRA 动态加载** | ✅ | ✅ | 部分 | 基础 | ✅ | 部分 | 部分 |
| **MoE 模型** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **多模态(VL)** | ✅ | ✅ | 有限 | 有限 | ✅⭐ | ✅ | ✅ |
| **量化方案** | GPTQ/AWQ/FP8/FP4 | GPTQ/AWQ/FP8 | GGUF 全套 | GGUF | AWQ/GPTQ/SmoothQuant | FP8/INT4/INT8 | MLX 量化 |
| **小白友好度** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **企业级生产用** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **学习曲线** | 中 | 中 | 低 | 极低 | 中 | 高 | 低 |
| **社区活跃度(GitHub Star)** | 40k+ | 7k+ | 70k+ | 100k+ | 5k+ | 11k+ | 15k+ |

> 📌 **2026 年初的"无脑选"建议**:
> - 企业 NVIDIA GPU 服务 → **vLLM** 或 **SGLang**
> - 个人 NVIDIA HomeLab → **Ollama**(图省事)或 **vLLM**(要榨干性能)
> - Mac 个人玩家 → **Ollama** 或 **MLX**
> - 老旧硬件 / CPU / 边缘 → **llama.cpp**
> - 国内 toB 项目 → **LMDeploy** 或 **vLLM**

---

## 6. 实战部署示例

### 6.1 单卡 4090 + Qwen 7B + vLLM(高并发 API 服务)

```bash
# 1. 装 vLLM(需 CUDA 12.1+)
pip install vllm

# 2. 启动 OpenAI 兼容 server
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-7B-Instruct \
  --port 8000 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.92 \
  --enable-prefix-caching

# 3. 客户端调用(任何 OpenAI SDK 都能用)
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-7B-Instruct",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 6.2 双卡 4090 + Qwen 72B AWQ + LMDeploy(国产模型部署)

```bash
pip install lmdeploy

lmdeploy serve api_server Qwen/Qwen2.5-72B-Instruct-AWQ \
  --backend turbomind \
  --tp 2 \
  --quant-policy 0 \
  --cache-max-entry-count 0.5 \
  --server-port 8000
```

### 6.3 M4 Pro MacBook + Qwen 7B + MLX(Apple 极致性能)

```bash
pip install mlx-lm

# 推理一次
mlx_lm.generate \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --prompt "用 Python 写快速排序"

# 起 server
pip install mlx-server
mlx-server \
  --model mlx-community/Qwen2.5-7B-Instruct-4bit \
  --port 8080
```

### 6.4 M1 MacBook Air 8GB + Llama 3.2 1B + Ollama(资源极限)

```bash
# 装 Ollama(macOS 安装包一键)
brew install ollama
ollama serve &

# 拉小模型(1B 参数 + 4bit 量化 ≈ 1GB)
ollama pull llama3.2:1b

# 用
ollama run llama3.2:1b
```

### 6.5 Tesla P40 24G(老矿卡)+ llama.cpp(经典垃圾佬场景)

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build -j

# 下载 Qwen 32B 的 Q4_K_M GGUF(约 19 GB)
huggingface-cli download bartowski/Qwen3-32B-Instruct-GGUF Qwen3-32B-Instruct-Q4_K_M.gguf

# 启动 server(P40 没有 Tensor Core,但 24G 显存够大)
./build/bin/llama-server \
  -m Qwen3-32B-Instruct-Q4_K_M.gguf \
  --port 8080 \
  -ngl 99   # 所有层卸载到 GPU
```

---

## 7. 与本知识库其他章节的关联

- **前置:模型量化与精度选择**:[本地部署模型量化选型](本地部署模型量化选型.md)——选好 GGUF / AWQ / FP8 后,再用本文的引擎跑起来
- **前置:NVIDIA 工程基础**:[NVIDIA 驱动 / CUDA / PyTorch](../05_技术基础/NVIDIA驱动-CUDA-PyTorch工程基础.md)——推理引擎跑之前,要先把驱动 / CUDA 调通
- **前置:硬件知识**:[NVIDIA 显卡架构与 AI 算力](../05_技术基础/NVIDIA显卡架构与AI算力.md)——为什么 P40 上跑不了 FP8、为什么 5090 需要 nightly PyTorch
- **后续:部署架构**:[HomeLab 到中小企业 LLM 部署架构](HomeLab到中小企业LLM部署架构.md)——单引擎起来后,如何做负载均衡 / 多用户 / 监控
- **前置:模型选择**:[各家 LLM 模型特点速查](各家LLM模型特点速查.md)——选哪个模型扔到推理引擎里
- **平行:API 选型**:[LLM-API 选型方法论](LLM-API选型方法论.md)——什么场景需要自部署 vs 用 API
- **下游:接口标准**:[LLM 接口规范实战](LLM接口规范实战.md)——所有上述引擎都支持 OpenAI 兼容接口

---

## 8. 术语速查

| 术语 | 全称 / 含义 |
|---|---|
| **推理引擎** | Inference Engine,把训练好的模型变成"实际能对外服务"的运行时 |
| **Continuous Batching** | 连续批处理,新请求随时插入 batch,GPU 利用率最大化 |
| **PagedAttention** | vLLM 原创,KV cache 按页管理,几乎零碎片 |
| **RadixAttention** | SGLang 原创,基于 Radix Tree 的 prompt 前缀复用 |
| **Speculative Decoding** | 投机解码,小模型草拟 + 大模型验证 |
| **TP / PP / EP** | Tensor / Pipeline / Expert 并行,见 [§ 4.5](#45-tensor-parallelism--pipeline-parallelism) |
| **GGUF** | Georgi Gerganov Universal Format,llama.cpp 专用模型格式 |
| **AWQ** | Activation-aware Weight Quantization,4-bit 量化 |
| **GPTQ** | Post-training 4-bit 量化 |
| **FP8 / FP4** | 8-bit / 4-bit 浮点量化,Ada / Blackwell 原生支持 |
| **Marlin** | NVIDIA 在 Ampere/Ada 上的 INT4/FP8 加速算子 |
| **Triton Inference Server** | NVIDIA 的通用推理调度器,可包 TensorRT-LLM |
| **LoRA** | Low-Rank Adaptation,轻量微调技术,推理时可动态加载 |
| **MoE** | Mixture of Experts,见 [Dense与MoE架构对比](../00_核心概念/Dense与MoE架构对比.md) |
| **VLM** | Vision-Language Model,多模态视觉模型 |
| **draft model** | 投机解码中的"草稿"小模型 |
| **NCCL** | NVIDIA Collective Communications Library,多 GPU 通信 |
| **Tensor Core** | NVIDIA 自 Volta 起的矩阵乘累加专用单元 |
| **Metal** | Apple 的 GPU API,llama.cpp / MLX 在 Mac 上用 Metal 后端 |
| **ROCm** | AMD GPU 的开源计算平台,对标 CUDA |
| **昇腾 / Ascend** | 华为的 NPU 平台 |

---

## 9. 作者声明、来源与局限性

### 9.1 作者声明

> ⚠️ **本篇是 Claude 基于公开技术资料整理的科普综述,不是 LINUX DO @flymyd 的实战经验帖**。
>
> 原作者在「简单易懂的 LLM 相关知识梳理」目录中标记 ep.3-4「认识常用推理引擎」为待填坑,本笔记是补位之作。当 @flymyd 实际发文后,建议优先参考其实战细节。

### 9.2 主要来源

- vLLM 官方:https://docs.vllm.ai
- SGLang 官方:https://docs.sglang.ai
- llama.cpp:https://github.com/ggerganov/llama.cpp
- Ollama:https://ollama.com/library
- LMDeploy:https://lmdeploy.readthedocs.io
- TensorRT-LLM:https://nvidia.github.io/TensorRT-LLM/
- MLX:https://ml-explore.github.io/mlx/
- Hugging Face TGI:https://huggingface.co/docs/text-generation-inference

### 9.3 本笔记的局限性

| 维度 | 局限性 |
|---|---|
| **个人实测对比数据** | 笔者没有亲测 7 个引擎在同硬件下的吞吐 / 延迟,**所有"快几倍"的说法均出自各引擎官方 benchmark 或社区共识**——实际数字因模型 / 卡 / 量化 / 配置不同而异 |
| **国内特殊版本** | 某些国产平台(如华为 MindIE / 寒武纪推理 SDK)的对比未深入 |
| **新版本特性** | 各引擎月度更新很快,**最新功能(如某个引擎刚加的 Mamba 支持)可能在本文中未体现** |
| **生产环境调优** | 本文聚焦"能跑起来",**生产级别的吞吐调优(如 chunked prefill / prefix cache 共享集群)** 需配合各引擎官方文档 |
| **多机分布式** | 多节点训练 / 推理(NCCL 多节点 / Ray 集成)未深入 |
| **冷启动 / 模型切换** | 推理服务的冷启动时间、运行时切换模型等运维细节未覆盖 |

### 9.4 选型补充建议

- **2026 年的"如果只学一个"**:**vLLM**——生态最全,生产可用,主流模型支持及时
- **2026 年的"如果想未来 1-2 年用"**:也是 vLLM,**SGLang** 的增长速度也值得关注
- **个人玩家不要走极端**:别一上来就 TensorRT-LLM,Ollama 或 vLLM 够你玩好几年
- **国内 toB**:LMDeploy 是不错的"国货之光",但 vLLM 也完全胜任
- **教学用**:llama.cpp 的代码最容易读懂,适合"想理解推理引擎到底干了什么"的学习者
