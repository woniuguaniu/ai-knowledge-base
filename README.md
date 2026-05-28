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
| 大模型如何"理解"文本 | [大模型如何理解文本.md](00_核心概念/大模型如何理解文本.md) | 从"分析文章主题"任务切入，把**词嵌入语义几何 / attention 主题词聚焦 / 层级抽象 (probing 探针实验) / 预训练见过亿万"长内容+总结"对**四层机制串起来；戳穿"理解"的真相（高维统计压缩 + 模式匹配），含 **Lost in the Middle** 实证、局限边界与术语速查 |
| 计算机视觉与深度学习框架 | [计算机视觉与深度学习框架.md](00_核心概念/计算机视觉与深度学习框架.md) | 一次讲清 **CV / OpenCV / PyTorch / TensorFlow** 四件套：CV 是领域（含分类/检测/分割/OCR/3D重建等 10 大子任务）、OpenCV 是传统算法工具箱（瑞士军刀比喻）、PyTorch 是深度学习框架（积木箱比喻）；四者关系图 + **摄像头实时人脸检测**四阶段实战（Haar 极简版 → MTCNN 标准版 → 跳帧/缩分辨率/异步抓帧/GPU 性能优化 → 完整工程版）+ 7 大常见踩坑表 + 选型建议（torchvision/MMDet/YOLO/MONAI/Detectron2/ONNX）+ 16 项术语速查 |
| Dense 与 MoE 架构对比 | [Dense与MoE架构对比.md](00_核心概念/Dense与MoE架构对比.md) | **以 Qwen3-32B（Dense）vs Qwen3-30B-A3B（MoE）做对照实验**：Dense/MoE 通俗类比（诊所 vs 医院、天才 vs 团队、大胃袋巨人）+ 优缺点表 + Model Card 五大参数逐项解读（嵌入词表/隐藏维度/头数/层数/专家数）+ **GQA 三类注意力对比（MHA / MQA / GQA，Q:KV 比值的工程含义）** + **YaRN 上下文外推**（尺子/古神比喻 + 宏观微观区别压缩）+ 模型参数经验值速查表；含 11 项术语速查 |

### 01 模型架构

| 模型 | 文件 | 核心创新 |
|------|------|---------|
| DeepSeek | [DeepSeek.md](01_模型架构/DeepSeek.md) | 架构层 (MLA / MoE) + 训练层 (GRPO / R1 多阶段训练 / R1-Distill 蒸馏家族)；含成本对比、Aha Moment 涌现解析 |
| **DeepSeek Engram 条件记忆** | [DeepSeek_Engram条件记忆.md](01_模型架构/DeepSeek_Engram条件记忆.md) | **给大模型加"查字典"模块**(DeepSeek 2026 年 1 月发表):**条件记忆 vs 条件计算(MoE)** 对比 + 三大关键设计(**哈希查表 O(1) + 多头哈希防撞车 + 上下文门控防张冠李戴**) + **第 2 层注入最优** 实验结论 + **U 型最优配比**(75-80% 推理 + 20-25% 记忆) + 27B 模型实测(**长文本大海捞针 84%→97%**) + **DRAM 存记忆表不占 HBM 显存**(PCIe 异步预取)的硬件意义;已应用于 DeepSeek V4 支撑 1M token 上下文 |

### 02 提示词工程（子项目）

独立子项目，含 10 个递进学习模块与速查/练习题。详见子项目 README：
[02_提示词工程/README.md](02_提示词工程/README.md)

> **2026-05-08 加深**：01.md 新增 **Lost in the Middle 现象 / Prompt 不改模型参数 / 网页端调试 4 技巧 / 完整 API 参数表**；02.md 新增 **NO COMMENTS, NO ACKNOWLEDGEMENTS** 抑制套话技巧；03.md 角色提示加"开头收窄问题域"原理；10.md 安全节扩充 **奶奶漏洞案例 + 注入分类器/价值观刷墙/Moderation API/网易易盾对比/HITL** + 新增 **§ 10.7 架构师三问**；速查手册新增"实战经验金句"节。

### 03 应用实践

| 主题 | 文件 | 简介 |
|------|------|------|
| RAG | [RAG/RAG学习笔记.md](03_应用实践/RAG/RAG学习笔记.md) | 检索增强生成的原理与工程实践 |
| 数据分析建模 | [数据分析建模（二手车经验）.md](03_应用实践/数据分析建模（二手车经验）.md) | 二手车价格预测的建模经验总结 |
| Medprompt 方法论解析 | [Medprompt方法论解析.md](03_应用实践/Medprompt方法论解析.md) | **微软研究院论文解读**：**不微调模型,光靠提示词组合让通用大模型在医学测试超越专用微调模型**(GPT-4 + Medprompt 在 MMLU 拿 90.10%,超过 Med-PaLM 2)；三大核心技巧(**动态少样本选择 (Dynamic Few-Shot)** + **自动生成思维链 (Self-Generated CoT)** + **选项打乱多数投票 (Choice-Shuffle Ensembling)**) + **Medprompt+ 进阶**(策略路由 + 扩大集成规模) + 4 类典型应用场景 + 成本/延迟折中考量；含"组合 > 单一"的协同效应原理 |
| 虚拟形象与数字人技术全景 | [虚拟形象与数字人技术全景.md](03_应用实践/虚拟形象与数字人技术全景.md) | VTuber / 换脸 / 换声 / 数字人 / 云端 API 的技术解剖与实战指南 |
| 宠物 CT 影像 AI 辅助诊断方案 | [宠物CT影像AI辅助诊断方案.md](03_应用实践/宠物CT影像AI辅助诊断方案.md) | **真实客户方案案例**:4000 份猫狗 CT(DICOM)+ 10+ 病种 + 1 人标注 + 3 个月做云端 SaaS MVP；**两阶段混合架构**——Month 1-2 用**多模态大模型 + RAG**(BiomedCLIP/RAD-DINO 向量化历史病例 + 相似检索)快速出 MVP,Month 3+ 用 **MONAI 框架训练专用检测模型**(高频病种)；完整技术栈(pydicom + SimpleITK + Milvus/Qdrant + FastAPI + cornerstone.js) + 核心提示词模板 + 3 个月周里程碑表 + 4 类风险应对 + 月成本估算 ¥3000-6000 |
| 本地部署模型量化选型 | [本地部署模型量化选型.md](03_应用实践/本地部署模型量化选型.md) | **私有化部署模型的硬件适配地图**：5 步决策路径 + Hugging Face / ModelScope / hf-mirror 平台速览 + Model Card 字段解读 + Files 目录说明（safetensors / tokenizer / generation_config） + **config.json 字段速查表（Dense 与 MoE 双版本）** + **数据精度全景表（FP64~FP4 / INT8 / INT4，W8A8 vs W8A16 解释）** + **量化方法全景表（GGUF/GPTQ/AWQ/EXL2/HQQ/AQLM/SmoothQuant/LLM.int8/FP8/NF4/MLX 共 11 种）** + **按显卡架构对号入座（Ada/Ampere/Turing/Volta/Pascal/AMD/Apple Silicon）** + 5 大踩坑（FP8 在 Ampere、量化标号陷阱、长上下文质量、KV cache 显存、MoE 显存不省）|
| **各家 LLM 模型特点速查** | [各家LLM模型特点速查.md](03_应用实践/各家LLM模型特点速查.md) | **选 API 前先认人**：**6 大闭源家族**（GPT / Gemini / Claude / Grok / Qwen 闭源 / 豆包）+ **10 大开源家族**（DeepSeek / Qwen 开源 / GLM / MiniMax / Kimi / Hunyuan / MiMo / LongCat / gpt-oss / Gemma）的核心定位、当前主力型号、性格画像、选型场景、踩坑提醒 + **5 张模型 ID 速查表** + **8 条作者实战金句**（"改 bug 用 codex / 新工程用 5.2"、"DeepSeek V4 需暖机"、"30B-A3B ≈ 14B Dense"等）+ A÷ / Z÷ / 牢字辈等 LD 社区黑话解释 |
| **LLM-API 选型方法论** | [LLM-API选型方法论.md](03_应用实践/LLM-API选型方法论.md) | **领导给你一个 AI 项目时**：5 维度框架（能力 / 速度 / 稳定性 / 价格 / 合规）+ **3 场景案例**（toB/toG 展厅 AI / toC 情感陪伴 / 个人创业）+ **3 大方法论**（不可能三角 / 业务决定技术 / 够用就好）+ **选型三问**（用户是谁 / 在乎什么 / 预算多少）+ **18 家 API 提供商对比表**（阿里云百炼 / 硅基流动 / 火山方舟 / OpenRouter / Cerebras / Vertex 等）+ 7 类作者未覆盖的补充方向（数据出境合规 / 行业垂直场景等）|
| **LLM 接口规范实战** | [LLM接口规范实战.md](03_应用实践/LLM接口规范实战.md) | **OpenAI 兼容一把梭不再够用**：4 种主流接口（OpenAI Chat Completion / OpenAI Response API / Gemini /v1beta / Anthropic Messages API）的核心字段、流式 SSE 结构、思考模型字段、多模态格式 + **9 种 role 速查**（含 LangChain 的 human/ai、OpenAI 新出的 developer、Gemini 专属的 model）+ **4 类经典坑**（role 适配 / 御三家严格参数 / /v1 前缀 / JSON 截断）+ **4 接口横向对比速查表** + 10 类作者未覆盖的工程化补充方向 |
| **LLM 推理引擎选型** ⭐新增 | [LLM推理引擎选型.md](03_应用实践/LLM推理引擎选型.md) | **7 大推理引擎横评**(**vLLM** / **SGLang** / **llama.cpp** / **Ollama** / **LMDeploy** / **TensorRT-LLM** / **MLX**):一句话定位 + 选型决策树 + 各引擎详解(PagedAttention / RadixAttention / GGUF 等核心创新)+ **6 大性能优化技术**(Continuous Batching / Speculative Decoding / TP/PP/EP 并行)+ **横向对比速查表** + 5 大典型场景部署示例(单卡 4090 / 双卡 + LMDeploy / Mac MLX / Tesla P40 等) |
| **HomeLab 到中小企业 LLM 部署架构** ⭐新增 | [HomeLab到中小企业LLM部署架构.md](03_应用实践/HomeLab到中小企业LLM部署架构.md) | **4 层部署架构模型**(硬件 / 推理服务 / 网关 / 接入)+ **3 类典型场景**(单 GPU 1-3 用户 / 2-4 卡 10-50 用户 / 4-8 卡 50-500 用户)+ **LiteLLM 网关**配置 + Nginx / Caddy 反向代理 + **API Key 管理 + RPM/TPM/Budget 三维限流** + Prometheus/Grafana/DCGM/Langfuse 监控栈 + 容灾 + **自建 vs API 盈亏平衡分析** |
| **Embedding / Reranker / 向量数据库** ⭐新增 | [Embedding-Reranker-向量数据库.md](03_应用实践/Embedding-Reranker-向量数据库.md) | **RAG 三大基石**:**Embedding 模型选型**(BGE-M3 / GTE / Conan / OpenAI v3 / Voyage / Cohere / Jina)+ **7 大向量数据库横评**(Milvus / Qdrant / Weaviate / Chroma / pgvector / Pinecone / Faiss)+ **Reranker** 召回-精排两阶段架构(bge-reranker-v2-m3 / Cohere Rerank 3 / Jina) + **完整 RAG Pipeline 代码** + 切块 / Hybrid Search / 元数据过滤 / 评测 4 大指标 |

### 04 探索日志

| 日期 | 主题 | 链接 |
|------|------|------|
| 2024-12-10 | Transformer 与 DeepSeek 创新 | [查看](04_探索日志/2024-12-10_Transformer与DeepSeek.md) |
| 2026-05-04 | Agent 知识体系闭环（工作流方法论复盘）| [查看](04_探索日志/2026-05-04_Agent知识体系闭环.md) |
| 2026-05-08 | 提示词工程经验补全（**Lost in the Middle / NO COMMENTS / 奶奶漏洞 / 架构师三问 / 内容审核 API 对比**）| [查看](04_探索日志/2026-05-08_提示词工程经验补全.md) |
| 2026-05-19 | LLM 表演性完成失败模式（**真实自我犯错复盘**：能讲 ≠ 能做、做了 ≠ 真做，含三大根因分析与机制层防御）| [查看](04_探索日志/2026-05-19_LLM表演性完成失败模式.md) |

### 05 技术基础

| 主题 | 文件 | 简介 |
|------|------|------|
| Shell 与终端 | [Shell与终端基础知识总结.md](05_技术基础/Shell与终端基础知识总结.md) | 小白通俗版：终端/Shell/命令行三层结构、Shell 家族隶属图、Mac/Linux/Windows 对照、跨平台脚本兼容性、**`ls -l` 输出与文件权限详解（含数字权限/macOS 扩展属性 `@`）、常用命令大全（12 类含管道重定向）、新手 5 大踩坑提醒** |
| swap 内存 | [swap内存处理技术.md](05_技术基础/swap内存处理技术.md) | Linux 交换分区原理与处理 |
| **NVIDIA 显卡架构与 AI 算力** | [NVIDIA显卡架构与AI算力.md](05_技术基础/NVIDIA显卡架构与AI算力.md) | **LLM 时代懂显卡**：NVIDIA 架构演进(Fermi → Kepler → Maxwell → Pascal → Volta → Turing → Ampere → Hopper → Ada → **Blackwell**) + **算力单位辨析(TFLOPS / TOPS / TIPS)** + **Tensor Core 代际演进**(各代 FP16/BF16/FP8/FP4/INT8 倍率全表 + 累加精度 + 结构化稀疏) + 显存进化(GDDR → HBM3e) + **"老黄刀法"工厂比喻**(算力 = 生产速度 / 位宽 = 车道数 / 带宽 = 运输能力) + **打游戏 vs LLM 推理 vs LLM 训练的瓶颈差异**(为什么 4060Ti 128bit 跑 LLM 拉胯) + SLI/NVLink 完整代际表(A6000 vs 3090 桥不通用警告) + 显卡选购决策树 + 8 类作者未覆盖方向(AMD/Intel/国产昇腾/Apple Silicon/TPU 等) |
| **NVIDIA 驱动 / CUDA / cuDNN / PyTorch** ⭐新增 | [NVIDIA驱动-CUDA-PyTorch工程基础.md](05_技术基础/NVIDIA驱动-CUDA-PyTorch工程基础.md) | **五层版本依赖链解剖**(Driver → CUDA Toolkit → cuDNN → PyTorch / TensorFlow)+ **Driver API vs Runtime API** 辨析(nvidia-smi 显示的 CUDA != nvcc --version)+ **驱动与 CUDA 兼容矩阵速查** + Ubuntu/Windows/WSL2 安装命令 + **PyTorch 与 CUDA 对应矩阵** + Apple Silicon MPS 后端 + **7 类典型报错速查表**(`The NVIDIA driver too old` / `no kernel image` / `Could not load libcudnn` 等)+ **一键自检 Python 脚本** + 三平台从零到能跑命令 |
| 软件架构 | [软件架构设计详解.md](05_技术基础/软件架构设计详解.md) | 软件架构设计原则与实践 |
| 程序员黑话速查 | [程序员黑话速查.md](05_技术基础/程序员黑话速查.md) | **持续生长型**术语速查：API / async / Canary Token / diff / DLP / GCG Attack / hack / HITL / MCP / N-version programming / patch / Reasoning Effort / Spotlighting / stdin-stdout-stderr / unified diff patch ……<br>**2026-05-16 新增 4 族**：☁️ 云服务（**SaaS / IaaS / PaaS / FaaS / BaaS / DBaaS / MaaS / Serverless / On-premise**）+ 📋 需求采购（**MVP / PoC / PRD / BRD / SRS / RFI / RFP / RFQ / SOW**）+ 💰 商业模式（**B2B / B2C / Freemium / PMF / MRR / ARR / GA**）+ 🧑‍💻 独立创业（**gap / OPC / Solopreneur / Indie Hacker / Digital Nomad**） |
| 云服务交付模型 | [云服务交付模型.md](05_技术基础/云服务交付模型.md) | **披萨打比方专题**：On-premise → IaaS → PaaS → SaaS 的 **9 层责任栈对比**（应用 / 数据 / 运行时 / 中间件 / OS / 虚拟化 / 服务器 / 存储 / 网络），含代表产品、真实场景、优缺点、4 大误区、选型框架、OPC / Indie Hacker 的典型技术栈；进阶讲 FaaS / BaaS / Serverless / DBaaS / MaaS / AaaS 全家福；附"上云演进 30 秒史" |
| 多 CLI 联动 | [多CLI联动.md](05_技术基础/多CLI联动.md) | Claude / Codex / Gemini 三家协同：能力对比、3 个层级、4 种玩法（管道接力 / MCP 互调 / 三方投票 / 角色分工）+ 双模型协作案例评析（含 7 大坑与改进版配置） |
| 内部工具选型方法论 | [内部工具选型方法论.md](05_技术基础/内部工具选型方法论.md) | **PM 视角实战框架**：先做"内部工具 vs 产品级 App"定性判断（7 题速测）→ 4 种实现形态横向对比（低代码 / 小程序 / H5 / 原生 App）→ 选型决策树 → **"两步走"战略**（低代码先跑半年再评估自研）→ 成本估算模型 → 需求评审 6 类风险（合规 / 平台限制 / 灰度 / 权限粒度 / 查重主键 / 附件膨胀）→ 场景速查表 + 5 大主流低代码平台对比；源自民宿运营管理系统选型实战 |
| 逆向 API 的二分定位方法 | [逆向API的二分定位方法.md](05_技术基础/逆向API的二分定位方法.md) | **黑盒接口分析通用方法论**：抓基准请求 → 单字段删减 → 改值找边界 → 复测 ≥ 2 次 → 输出最小必需集；三大陷阱（把"恰好能跑"当成协议本意 / 状态码被中间层改写 / 灰度让结论矛盾）+ 5 个可迁移场景（Prompt 调试 / bug 复现 / 依赖冲突 / CSS / 慢 SQL）+ 完整案例骨架（脱敏自 AnyRouter 逆向分析）|
| GitHub 项目入门（实操指南） | [GitHub项目入门/小白入门-GitHub项目部署使用指南.md](05_技术基础/GitHub项目入门/小白入门-GitHub项目部署使用指南.md) | 以 gpt_image_playground 为样本，从零开始的 7 步部署流程：识别项目类型、装环境、装依赖、配置、启动、上线；含小白排错四件套、高效求助提问模板、30 秒口令速记 |
| GitHub 项目入门（概念地图） | [GitHub项目入门/程序小白概念扫盲手册.md](05_技术基础/GitHub项目入门/程序小白概念扫盲手册.md) | 配套概念手册：软件工程全景图（按使用场景）、npm/pnpm/yarn 对比、MIT/Fork、命令参数、Docker/Nginx、容器化、pnpm + Docker 共用机制、缩写表、编程语言识别图鉴、Git 常用命令实战图解 |
| GitHub 项目入门（速查卡） | [GitHub项目入门/五看一跑_小白工程运行部署学习文档.md](05_技术基础/GitHub项目入门/五看一跑_小白工程运行部署学习文档.md) | 30 秒口令版：五看一跑（README/类型/scripts/环境/部署/本地跑）+ 排错四件套 + 实战模板，临时回忆流程时翻 |
| **Git 进阶速查**（rebase / stash / reflog） | [GitHub项目入门/Git进阶速查.md](05_技术基础/GitHub项目入门/Git进阶速查.md) | **概念扫盲手册第十二章的进阶补充**:`日常 90% 场景之外的 10%`——**6 大进阶命令实战**:① **`stash`** 临时藏起未提交改动(改一半切分支救命)② **`reflog`** 救命找回被 reset/删分支误删的 commit(90 天内可救)③ **`rebase`** 整理 commit 历史(`pull --rebase` + `rebase -i HEAD~N` 交互式 squash/reword)④ **`--force-with-lease`** 安全强推 vs 危险的裸 `--force` ⑤ **`cherry-pick`** 挑樱桃式合单个 commit ⑥ **`tag`** 版本号管理(发版 v1.0.0 必备);进阶速查图 + 5 条铁律 + 实战练习 |
| **静态站点生成器与 Quartz 部署实战** ⭐新增 | [静态站点生成器与Quartz部署实战.md](05_技术基础/静态站点生成器与Quartz部署实战.md) | **SSG 范式入门 + Quartz 完整部署 SOP**:**静态站点生成器(SSG)** 与动态站对比(类比"餐厅现炒 vs 便利店饭团")+ 工作流**四角色**(作者/生成器/产物/Web 服务器)+ Quartz `quartz.config.ts` 关键字段速览(`baseUrl` / `ignorePatterns` / `transformers` / `emitters`)+ **三种部署路线对比**(自有 VPS+rsync / **Cloudflare Pages** / 服务器自 build)+ **本知识库部署到 `kingrich.top/knowledge-base/quartz/` 的完整 7 步实战**(改 baseUrl / build / SSH / **rsync 上传** / **nginx `try_files` 配置** / **子路径斜杠 301 重定向** / `curl` 验证)+ **子路径部署"恰好兼容"机制**(Quartz 内部资源用相对路径,无需 nginx rewrite)+ **`deploy.sh` 一键脚本** + **7 大常见报错速查**(`rsync: 未找到命令` / 404 / 样式乱 / 中文路径 / `baseUrl` 没改导致 sitemap 全是 localhost 等)+ **9 大主流 SSG 横向对比**(Hugo / Jekyll / Astro / Eleventy / Docusaurus / MkDocs / VitePress / Next.js)+ 19 项术语速查 |

### 06 Agent 工程

| 主题 | 文件 | 简介 |
|------|------|------|
| 什么是 Agent（**入门必读**）| [什么是Agent.md](06_Agent工程/什么是Agent.md) | 完全没接触过 Agent 的入门科普：三段循环（Perception → Reasoning → Action）、4 大核心能力（Tool Use / Memory / Planning / Reflection）、Claude Code 修 bug 真实例子、7 大常见误区、Agent vs Workflow/LLM/Copilot 对比、ReAct 模式、术语速查 |
| Harness 工程与 Agent 解剖 | [Harness工程与Agent解剖.md](06_Agent工程/Harness工程与Agent解剖.md) | Agent = Model + Harness；三层工程递进、Claude Code 泄露事件、**Agent 五层架构图（编排层 / 记忆层 / 大模型 / 执行层 / 反馈层）**与补强版、Guides/Sensors 框架；**§ 5.5 实操速查（社区六层视角对照）**：上下文三层组织（规则/状态/证据）+ 记忆 3 类生命周期 + 失败类型→恢复策略对照表 |
| Agent 发展轨迹四阶段 | [Agent发展轨迹四阶段.md](06_Agent工程/Agent发展轨迹四阶段.md) | 小白视角史观文：Prompt → Reasoning/ReAct → Context → Harness 的"俄罗斯套娃"演进，附生动比喻、入门路径与「**Agent 架构师**」职业视角评析 |
| Eval 测评体系 | [Eval测评体系.md](06_Agent工程/Eval测评体系.md) | Agent 工程的命根子：四类 Eval（离线 / 在线 A/B / LLM-as-Judge / 人工）、构建数据集、关键指标、实战工具、5 大经典误区、小白第一周落地路径 |
| Agent 安全攻防 | [Agent安全攻防.md](06_Agent工程/Agent安全攻防.md) | **30 种攻击手法**（提示词注入 / 间接注入 / RAG 投毒 / MCP 投毒 / GCG 对抗后缀 / DAN 越狱…）+ **17 项防御技术**（5 层框架 + 12 项具体：Canary Token / LLM Guard / Spotlighting / DLP / HITL / 沙箱…）+ 纵深防御方法论；源自 OpenClaw 敲壳测试 |
| Claude Code 扩展生态 | [Claude Code 扩展生态.md](06_Agent工程/Claude%20Code%20扩展生态.md) | **5 大扩展机制系统讲解**：Skill（技能/渐进式披露）+ MCP（USB 协议/装查删命令/4 个实战例子：即梦/飞书/天气/Firecrawl）+ CLI（飞书/OpenCLI/gh/Gemini）+ SubAgent（自动派生 vs `/agents` 7 步流程 + 「秋瓷团」5 角色案例）+ Hook（5 种钩子类型）+ Plugin（整合包/`/plugin`管理）；含核心金句、对比选型表、渐进学习路径 |
| **Function Calling 与 MCP 工程指南** ⭐新增 | [Function Calling与MCP工程指南.md](06_Agent工程/Function%20Calling与MCP工程指南.md) | **Agent 工程两块基石**:**Function Calling 工作流时序图** + **御三家工具调用接口对比**(OpenAI tool_calls / Anthropic tool_use / Gemini functionCall;参数差异 / 回传 role 差异 / stop 标志差异) + **MCP 协议解剖**(Host/Client/Server 三件套 / Tools/Resources/Prompts 三类原语 / stdio+HTTP+WebSocket 三种 Transport) + **MCP vs Function Calling 关系图**(协议层 vs 应用层) + **4 个工程实战例子**(Python OpenAI 风格 / 多工具并行 / 写 MCP Server / LiteLLM 集成) + 6 类常见坑(description 重要性 / schema 严格性 / 错误处理 / 工具数量爆炸 / 工具调用攻击面 / 流式工具调用) |
| Claude Code 实战速查 | [Claude Code 实战速查.md](06_Agent工程/Claude%20Code%20实战速查.md) | **日常使用速查手册**：CC 启停 + 17 个常用指令分类速查（基础/模型/项目/扩展）+ 3 家国产模型 API 直连配置（GLM 4.5 / Kimi K2 / Qwen3 Coder）+ 4 种接入方案对比 + 「秋瓷团」5 角色一日工作流案例 + 5 类场景的 MCP 应用图鉴（视频/笔记/Word/面试/论文）+ 5 大踩坑提醒 + 高频命令一览 |
| Multi-Agent 工程实战与 Persona 设计 | [Multi-Agent工程实战与Persona设计.md](06_Agent工程/Multi-Agent工程实战与Persona设计.md) | **7 人 AI 团队全自动炒股案例**(LINUX DO @Oking 2026-05-17 文章 + 2026-05-19 整合):**Persona 文件**结构化定义(YAML 模板 + 词源记忆法 `per-`+`-sona`=戴面具变身)、R&D 流水线时间表(06:00→12:00→18:00→次日09:00)、**四大工程原则**(不问只做 / 任务二分法脚本vsAI / 模型分级 / 共享真相源 Single Source of Truth)、三大踩坑(手续费 bug 让 500 笔交易作废 / 本地状态≠真实执行的 API 鬼影 / 多 Agent 数据漂移)、Multi-Agent 入门 5 条建议;素材评分 8/10,可商榷点已批注 |
| LLM 典型失败模式 | [LLM典型失败模式.md](06_Agent工程/LLM典型失败模式.md) | **「能讲 ≠ 能做、做了 ≠ 真做」**：4 层 14 种 failure mode 分类表（知识层 / 执行层 / 元认知层 / 推理层 / 安全层）+ 三大重点专题（**表演性完成 / 跳步 / 自我汇报偏差**）含定义/案例/根因/识别红旗/机制层防御 + Goodhart's Law 在 LLM 自我汇报场景的具象推论 + 实战 checklist；源自 2026-05-19 真实犯错复盘（同日探索日志） |
| **Claude Code `/goal` 命令** ⭐新增 | [Claude Code goal命令.md](06_Agent工程/Claude%20Code%20goal命令.md) | **Anthropic 2026-05-12 v2.1.139 引入的长任务原语**：设可衡量的完成条件，Claude 跨多轮自动循环到达成；**独立 Haiku 评估器**每轮判断目标是否满足——"被评估者不能自评"原则的工程化落地；含**机制图**（主 Claude 干活 ↔ Haiku 评估循环）+ 4 个实战例子（测试套件 / lint 修复 / 知识库整理 / 跨文件迁移）+ 4000 字符限制 + 成本警示（一日可烧几十美元）+ 完成条件可衡量性设计原则 + **与 OpenAI Codex /goal 对比**（4 月底先发，5 月跟进）|

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

*最后更新: 2026-05-28(新增 `05_技术基础/静态站点生成器与Quartz部署实战.md`:把这次部署知识库到 `kingrich.top/knowledge-base/quartz/` 的实战流程沉淀成 SSG 范式入门 + 三种部署路线对比 + 完整 7 步 SOP + 常见报错速查;3 处反向回填:`云服务交付模型.md` 加 PaaS vs IaaS 实战对照 / `程序员黑话速查.md` 加 SSG 术语关联 / `GitHub项目入门/程序小白概念扫盲手册.md` 加"想发布笔记站"的进阶指引)*
*上次更新: 2026-05-26（新增 `06_Agent工程/Claude Code goal命令.md`：Anthropic v2.1.139 长任务原语完整解析，含 Haiku 独立评估器机制 / 实战 4 例 / 与 Codex 对比；3 处反向回填：`Claude Code 实战速查.md` 加新命令行 / `Claude Code 扩展生态.md` 加交叉引用 / `LLM典型失败模式.md` 加官方机制层防御）*
*上次更新: 2026-05-25(填补作者 @flymyd 的 5 个待填坑,新增 5 篇 Claude 原创补充笔记:`03_应用实践/LLM推理引擎选型.md` + `03_应用实践/HomeLab到中小企业LLM部署架构.md` + `03_应用实践/Embedding-Reranker-向量数据库.md` + `05_技术基础/NVIDIA驱动-CUDA-PyTorch工程基础.md` + `06_Agent工程/Function Calling与MCP工程指南.md`;每篇均含「作者声明 + 局限性」节明确标注非作者原稿;含 9 处反向回填确保双向引用)*
