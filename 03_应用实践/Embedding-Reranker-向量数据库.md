# Embedding / Reranker / 向量数据库:RAG 工程的三大基石

> **一句话**:RAG 系统是 LLM 应用最常见的形态,而 RAG 工程能不能落地、效果好不好,**绝大多数取决于三件事**:**Embedding 怎么选**(把文本变向量)、**向量数据库怎么用**(存检索)、**Reranker 配不配**(精排提质)。本文是这三大基石的横向对比 + 选型决策 + 工程实战。
>
> ⚠️ **本篇为 Claude 原创补充笔记**,非 LINUX DO @flymyd 原稿(详见末尾「作者声明」)。
> 📌 **关系说明**:[RAG学习笔记.md](RAG/RAG学习笔记.md) 是 RAG 的入门笔记,聚焦"搜索 API 怎么选";本文深入"自建 RAG 的三件套",**两者互补**。

---

## 目录

- [0. 三大基石各管什么](#0-三大基石各管什么)
- [1. Embedding 模型](#1-embedding-模型)
  - [1.1 Embedding 是什么 / 干什么用的](#11-embedding-是什么--干什么用的)
  - [1.2 主流 Embedding 模型选型](#12-主流-embedding-模型选型)
  - [1.3 中文场景的关键选择](#13-中文场景的关键选择)
  - [1.4 维度的工程权衡](#14-维度的工程权衡)
- [2. 向量数据库](#2-向量数据库)
  - [2.1 为什么需要向量数据库](#21-为什么需要向量数据库)
  - [2.2 ANN 索引算法速览](#22-ann-索引算法速览)
  - [2.3 主流向量库横评](#23-主流向量库横评)
  - [2.4 选型决策树](#24-选型决策树)
- [3. Reranker](#3-reranker)
  - [3.1 为什么需要 Reranker](#31-为什么需要-reranker)
  - [3.2 主流 Reranker 模型](#32-主流-reranker-模型)
  - [3.3 召回-精排两阶段架构](#33-召回-精排两阶段架构)
- [4. 完整 RAG Pipeline 示例](#4-完整-rag-pipeline-示例)
- [5. 常见坑与最佳实践](#5-常见坑与最佳实践)
- [6. 与本知识库其他章节的关联](#6-与本知识库其他章节的关联)
- [7. 术语速查](#7-术语速查)
- [8. 作者声明、来源与局限性](#8-作者声明来源与局限性)

---

## 0. 三大基石各管什么

```
完整的 RAG 工作流:

  原始文档(PDF / Markdown / 网页)
        ↓ 切块(Chunking)
  小段文本(Chunk)
        ↓ Embedding 模型
  向量(768/1024/4096 维)
        ↓ 存入
  向量数据库(支持向量检索)
        ↓ 用户提问
  Query 文本
        ↓ 同一个 Embedding 模型
  Query 向量
        ↓ 向量数据库相似检索
  Top-K 候选 chunk(粗排)
        ↓ Reranker
  Top-N 精排结果(N < K)
        ↓ 塞进 prompt
  LLM 基于检索结果回答
```

**三个基石各自的责任**:

| 基石 | 干什么 | 不干什么 |
|---|---|---|
| **Embedding 模型** | 把文本变成"能比较相似度的"向量 | 不负责存储 / 检索 |
| **向量数据库** | 存向量 + 提供"快速近似最近邻搜索" | 不理解语义 |
| **Reranker** | 把"召回的 100 条"精排成"最相关的 5 条" | 不替代召回阶段 |

**单凭任何一个都不够**——Embedding 决定**能不能召回**,向量库决定**能不能撑住量**,Reranker 决定**质量上限**。

---

## 1. Embedding 模型

### 1.1 Embedding 是什么 / 干什么用的

**Embedding(嵌入)**:**把文本(或图片、音频)变成固定长度的浮点数向量,使得"语义相近的文本→向量相近"**。

```python
# 概念示意
embed("猫")          → [0.21, -0.05, 0.87, ...]   # 768 维
embed("小猫")        → [0.19, -0.03, 0.85, ...]   # 跟"猫"很接近
embed("打篮球")      → [-0.42, 0.61, 0.13, ...]   # 跟"猫"差很远

similarity(embed("猫"), embed("小猫"))     → 0.95
similarity(embed("猫"), embed("打篮球"))   → 0.12
```

**相似度计算公式**:几乎都用**余弦相似度**(Cosine Similarity):

```
sim(A, B) = (A · B) / (|A| × |B|)

值域:[-1, 1],越接近 1 越相似
```

### 1.2 主流 Embedding 模型选型

#### 1.2.1 中文场景四大派系

| 模型家族 | 出品方 | 代表 | 特点 |
|---|---|---|---|
| **BGE** | 北京智源(BAAI) | bge-large-zh-v1.5 / bge-m3 | 中文 SOTA 之一,生态最广 |
| **M3E** | MokaAI(Moka) | m3e-base / m3e-large | 早期中文标杆,目前不如 BGE |
| **GTE** | 阿里 | gte-large-zh / gte-Qwen2 | 阿里推出,Qwen 系列友好 |
| **Conan** | 腾讯 | conan-embedding-v1 | 腾讯推出,微信场景验证 |

#### 1.2.2 国际主流

| 模型 | 出品方 | 维度 | 备注 |
|---|---|---|---|
| `text-embedding-3-large` | OpenAI | 3072(可降维)| 商业 API,合规要求高时用 |
| `text-embedding-3-small` | OpenAI | 1536 | 性价比高 |
| `voyage-3` | Voyage AI | 1024 | Anthropic 投资,质量很好 |
| `Cohere embed v3` | Cohere | 1024 | 多语言强 |
| `Jina Embeddings v3` | Jina AI | 1024(matryoshka)| 支持降维 + 多任务 |

#### 1.2.3 多模态 Embedding

| 模型 | 模态 | 备注 |
|---|---|---|
| **CLIP**(OpenAI 经典)| 文本 + 图像 | 老牌,被广泛使用 |
| **SigLIP**(Google) | 文本 + 图像 | CLIP 的改进版 |
| **BiomedCLIP / RAD-DINO** | 医学影像 | 见 [宠物CT影像AI辅助诊断方案.md](宠物CT影像AI辅助诊断方案.md) |
| **bge-vl** | 文本 + 图像 | BGE 家族多模态版 |

### 1.3 中文场景的关键选择

#### 1.3.1 BGE-M3:2024 年起的"无脑选"

`BAAI/bge-m3` 是当前中文 RAG 场景的**默认推荐**,因为它解决了多个痛点:

- **多语言**:100+ 语言通用,不用为每种语言换模型
- **多功能**:同一个模型支持 **稠密向量 + 稀疏向量 + ColBERT 风格** 三种检索
- **多粒度**:**单文档最多支持 8192 token**(过去的 bge 只支持 512)

**用法**:

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

embeddings = model.encode(
    ["猫是哺乳动物", "我喜欢吃苹果"],
    batch_size=12,
    max_length=8192
)
# embeddings['dense_vecs'].shape = (2, 1024)
```

#### 1.3.2 其他场景的选择

| 场景 | 推荐 |
|---|---|
| **通用中文 RAG** | `BAAI/bge-m3`(default) |
| **极致中文表现** | `BAAI/bge-large-zh-v1.5`(精排时配 reranker) |
| **多语言通用** | `BAAI/bge-m3` 或 `Jina-v3` |
| **必须用商业 API + 合规** | `text-embedding-3-large`(OpenAI) |
| **想跟 Qwen 配套** | `gte-Qwen2-7B-instruct`(阿里出品)|
| **完全离线 / 端侧** | `bge-small-zh`(33MB,CPU 也能跑) |
| **超低延迟** | `m3e-base`(384 维,极快) |

### 1.4 维度的工程权衡

| 维度 | 内存占用(每 100 万向量,FP32)| 检索速度 | 精度 |
|---|---|---|---|
| 384 | ~1.5 GB | 极快 | 一般 |
| 768 | ~3 GB | 快 | 不错 |
| 1024 | ~4 GB | 中 | 好 |
| 1536(OpenAI small)| ~6 GB | 中 | 很好 |
| 3072(OpenAI large)| ~12 GB | 慢 | 最好 |
| 4096(部分 LLM 派生)| ~16 GB | 慢 | 视模型 |

> 💡 **关键认知**:**维度越高 ≠ 越好**——存储成本线性增,精度提升通常是亚线性的。
>
> 一些新模型支持 **Matryoshka 维度**(可在使用时降维):
> - OpenAI v3 系列:从 3072 砍到 256 都行
> - Jina v3:同样支持
> - **3072 维存储,使用时降到 768 维做粗排**——存储不变、检索提速

---

## 2. 向量数据库

### 2.1 为什么需要向量数据库

传统数据库**精确匹配**(WHERE id = 1),但向量需要**近似匹配**(找跟我最像的 K 条)。

**问题规模**:
- 文档数 100 万 × 每个 chunk 1024 维 = **存 10 亿 float**
- 每次查询要算这个查询向量和 **所有** 100 万条的相似度
- 暴力计算每次 1024 × 100 万 = 10 亿次乘加 = **每次查 100ms-1s**(慢!)

**向量数据库的核心价值**:**用 ANN(Approximate Nearest Neighbor)算法,牺牲一点精度,换取 100-1000 倍的查询速度**。

### 2.2 ANN 索引算法速览

| 算法 | 全称 | 思路 | 典型库 |
|---|---|---|---|
| **HNSW** | Hierarchical Navigable Small World | 多层"近邻图",从粗到细查 | Faiss / Milvus / Qdrant / pgvector |
| **IVF** | Inverted File Index | 先聚类成 N 个桶,只查最近的几个桶 | Faiss / Milvus |
| **PQ** | Product Quantization | 把高维向量切段量化,大幅压缩 | Faiss(常和 IVF 组合) |
| **DiskANN** | — | 索引存盘,适合超大规模 | Milvus / 微软研究 |
| **ScaNN** | Google | Google 内部优化的 IVF + 量化 | TensorFlow Serving |

> 📌 **HNSW 是当前最主流**——召回率高、速度快、调参少。**99% 的中小项目用 HNSW 就够**。

### 2.3 主流向量库横评

#### 2.3.1 七大主流向量库

| 库 | 类型 | 部署 | 适合 |
|---|---|---|---|
| **Milvus** | 独立向量库 | Docker / K8s | **企业级**,主流首选 |
| **Qdrant** | 独立向量库 | Docker / 二进制 | 中小项目,Rust 实现性能好 |
| **Weaviate** | 独立向量库 + 多模态 | Docker / 云 | 多模态场景 |
| **Chroma** | 独立向量库 | 嵌入 / 服务端 | 原型 / 个人项目 |
| **pgvector** | PostgreSQL 扩展 | 装到现有 PG | **已有 PG 的项目** |
| **Pinecone** | 商业云服务 | SaaS | 无运维需求 + 预算够 |
| **Faiss** | 库不是服务 | Python / C++ | 学术 / 嵌入应用 |

#### 2.3.2 横向对比

| 维度 | Milvus | Qdrant | Weaviate | Chroma | pgvector | Pinecone | Faiss |
|---|---|---|---|---|---|---|---|
| **部署模式** | 独立服务 | 独立服务 | 独立服务 | 嵌入 / 独立 | 装在 PG | SaaS | 库 |
| **数据持久化** | ✅ | ✅ | ✅ | ✅ | ✅(走 PG) | ✅ | ❌ 自己写 |
| **元数据过滤** | ✅⭐ | ✅⭐ | ✅⭐ | ✅ | ✅(SQL!)| ✅ | ❌ |
| **稀疏向量(BM25)** | ✅ | ✅ | ✅ | 部分 | ✅(pg_trgm) | ✅ | 需自实现 |
| **多模态** | ✅ | ✅ | ✅⭐ | 部分 | ✅ | ✅ | 自实现 |
| **水平扩展** | ✅⭐ | ✅ | ✅ | ❌ | 难 | ✅ | 需 sharding |
| **生产 SLA** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐(依 PG)| ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **学习曲线** | 中 | 低 | 中 | 极低 | 极低(SQL)| 极低 | 高 |
| **国内可用** | ✅ | ✅ | ✅ | ✅ | ✅ | 部分 | ✅ |
| **License** | Apache 2.0 | Apache 2.0 | BSD | Apache 2.0 | PostgreSQL | 商业 | MIT |

### 2.4 选型决策树

```
你需要存的向量数量?
  │
  ├─ < 10 万(原型 / 个人) ──── Chroma 或 pgvector(够用就别折腾)
  │
  ├─ 10 万 - 1000 万(中小项目)
  │     ├─ 已有 PostgreSQL? ──── pgvector(零额外运维)
  │     ├─ 想要"简单 + 自部署"? ─ Qdrant(单二进制就跑)
  │     └─ 多模态需求? ────────── Weaviate
  │
  ├─ 1000 万 - 10 亿(企业级)
  │     ├─ 自建团队 ──────────── Milvus(集群版)
  │     └─ 想完全外包 ────────── Pinecone(贵)
  │
  └─ 嵌入到 Python 应用 ──────── Faiss(直接 import,无服务)
```

### 2.5 极简代码:Qdrant 30 行入门

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from FlagEmbedding import BGEM3FlagModel

# 1. 准备模型 + 客户端
embedder = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
client = QdrantClient(":memory:")    # 内存模式;生产用 url="http://qdrant:6333"

# 2. 建 collection
client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
)

# 3. 灌数据
docs = ["猫是哺乳动物", "我喜欢吃苹果", "Python 是编程语言"]
vectors = embedder.encode(docs)['dense_vecs']

client.upsert(
    collection_name="docs",
    points=[
        PointStruct(id=i, vector=v.tolist(), payload={"text": doc})
        for i, (doc, v) in enumerate(zip(docs, vectors))
    ]
)

# 4. 查询
query_vec = embedder.encode(["小猫"])['dense_vecs'][0]
results = client.search(
    collection_name="docs",
    query_vector=query_vec.tolist(),
    limit=3
)
for r in results:
    print(r.score, r.payload["text"])
# 0.91 猫是哺乳动物
# 0.18 我喜欢吃苹果
# 0.05 Python 是编程语言
```

---

## 3. Reranker

### 3.1 为什么需要 Reranker

**Embedding 检索的根本局限**:

| 阶段 | Embedding 检索 | Reranker |
|---|---|---|
| **算什么** | Query 向量 vs Document 向量(**各算各的**)| Query + Document **拼起来** 一起算 |
| **架构** | **Bi-Encoder**(双塔) | **Cross-Encoder**(单塔交叉编码) |
| **速度** | 极快(候选向量提前算好)| 慢(每对都要重新过模型) |
| **精度** | 中(隐藏了交互信息)| 高(能看到 Query × Document 的细节) |

```
Bi-Encoder(Embedding 检索):
  query  → [BERT] → [v_q]
                              cos_sim
  doc    → [BERT] → [v_d]   ←─────────  打分

Cross-Encoder(Reranker):
  [CLS] query [SEP] doc [SEP] → [BERT] → [score]
                                          ↑
                            能看到 query 和 doc 的所有 token 交互
```

**典型 RAG 工作流**:

```
Query → Embedding 召回 Top-100(快)
                ↓
       Reranker 精排到 Top-5(慢但准)
                ↓
            塞进 LLM Prompt
```

### 3.2 主流 Reranker 模型

| 模型 | 出品方 | 备注 |
|---|---|---|
| **bge-reranker-v2-m3** | BAAI | **中文 RAG 默认选**,与 bge-m3 配套 |
| **bge-reranker-large** | BAAI | 老一代,bge-reranker-v2-m3 不可用时降级 |
| **Cohere Rerank 3** | Cohere | 商业 API,多语言 |
| **Jina Reranker v2** | Jina AI | 多语言,支持 8192 token |
| **mxbai-rerank-large-v1** | Mixedbread | 英文场景强 |
| **ms-marco-MiniLM-L-12-v2** | Microsoft | 老牌轻量,英文 |

> 💡 **2026 年默认推荐**:中文场景用 **`BAAI/bge-reranker-v2-m3`**,英文场景用 **`Cohere Rerank 3`** 或 **`Jina Reranker v2`**。

### 3.3 召回-精排两阶段架构

#### 3.3.1 为什么不直接用 Reranker?

| 单用 Reranker | 召回 + 精排 |
|---|---|
| 100 万文档每条都过 Cross-Encoder | 100 万→Top-100(Embedding,毫秒级)→Top-5(Reranker,百毫秒) |
| **每次查 30 分钟** | **每次查 < 1 秒** |
| 显存 / GPU 占用爆炸 | 可接受 |

**两阶段是工程必然**。

#### 3.3.2 配置参数:K 怎么选

| K | 召回数 | 精排数 N | 适用 |
|---|---|---|---|
| K=10, N=3 | 10 | 3 | 极快,但漏召概率高 |
| K=20, N=5 | 20 | 5 | 平衡 |
| **K=50, N=5** | 50 | 5 | **常见默认值** |
| K=100, N=5 | 100 | 5 | 高质量,慢一些 |
| K=200, N=10 | 200 | 10 | 极致质量,Reranker 慢 |

**调优经验**:
- **召回 Recall@K 不够时**(目标答案没被召回):加大 K
- **精排后还不准**(LLM 上下文有相关但效果差):换 Reranker 或加 N
- **延迟接受范围内**,**先加 K 后加 N**

#### 3.3.3 Reranker 调用示例

```python
from FlagEmbedding import FlagReranker

# 1. 加载
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

# 2. 输入 query + 候选文档对
query = "什么是 RAG?"
docs = [
    "RAG 是 Retrieval-Augmented Generation,检索增强生成",
    "Python 是一种高级编程语言",
    "RAG 通过外挂知识库扩展 LLM 的能力",
    "今天天气真好",
]

# 3. 算分(每对 query-doc 一个分数)
scores = reranker.compute_score(
    [[query, d] for d in docs],
    normalize=True
)
# scores = [0.95, 0.02, 0.92, 0.01]

# 4. 排序取 Top-N
ranked = sorted(zip(docs, scores), key=lambda x: -x[1])
top_2 = ranked[:2]
print(top_2)
# [("RAG 是 Retrieval-Augmented Generation...", 0.95),
#  ("RAG 通过外挂知识库扩展 LLM 的能力", 0.92)]
```

---

## 4. 完整 RAG Pipeline 示例

把三者拼起来,**一个最小可工作的 RAG**:

```python
# 完整 RAG 示例(伪生产代码)
from FlagEmbedding import BGEM3FlagModel, FlagReranker
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from openai import OpenAI

# 1. 初始化
embedder = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
qdrant = QdrantClient(url="http://localhost:6333")
llm = OpenAI(base_url="http://localhost:8000/v1", api_key="...")

# 2. 灌库阶段(离线)
def index_documents(docs: list[str]):
    """切块 + 向量化 + 存库"""
    qdrant.recreate_collection(
        collection_name="kb",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
    vectors = embedder.encode(docs, batch_size=32)['dense_vecs']
    qdrant.upsert(
        collection_name="kb",
        points=[
            PointStruct(id=i, vector=v.tolist(), payload={"text": d})
            for i, (d, v) in enumerate(zip(docs, vectors))
        ]
    )

# 3. 查询阶段(在线)
def rag_query(query: str, k: int = 50, n: int = 5) -> str:
    # Step A:Embedding 检索 Top-K
    qvec = embedder.encode([query])['dense_vecs'][0]
    candidates = qdrant.search(
        collection_name="kb",
        query_vector=qvec.tolist(),
        limit=k
    )
    candidate_docs = [c.payload["text"] for c in candidates]
    
    # Step B:Reranker 精排 Top-N
    rerank_scores = reranker.compute_score(
        [[query, d] for d in candidate_docs],
        normalize=True
    )
    top_docs = [d for d, _ in sorted(
        zip(candidate_docs, rerank_scores),
        key=lambda x: -x[1]
    )[:n]]
    
    # Step C:塞进 LLM
    context = "\n\n".join(f"[{i+1}] {d}" for i, d in enumerate(top_docs))
    prompt = f"""请基于以下知识回答问题。如果知识里没有相关信息,直接说"我不知道"。

知识:
{context}

问题:{query}

回答:"""
    
    response = llm.chat.completions.create(
        model="qwen-flagship",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 4. 跑起来
index_documents([
    "RAG 全称 Retrieval-Augmented Generation,检索增强生成",
    "RAG 由三部分组成:Embedding 检索、向量数据库、LLM 生成",
    "Reranker 用于二阶段精排,提升 RAG 质量",
    "Python 是一种解释型编程语言",
])

print(rag_query("RAG 有几个部分?"))
# → RAG 由三部分组成:Embedding 检索、向量数据库、LLM 生成。
```

---

## 5. 常见坑与最佳实践

### 5.1 切块(Chunking)策略

切块质量决定召回质量,但常被忽视。

| 策略 | 适用 | 优点 | 缺点 |
|---|---|---|---|
| **固定字符数**(如 500 字)| 简单文档 | 极简单 | 可能切断语义 |
| **固定 token 数** | LLM 友好 | 准确控制成本 | 同上 |
| **按段落 / 句子** | 结构化文档 | 保语义完整 | 长度不均 |
| **递归切分**(LangChain 默认)| 复杂文档 | 兼顾结构和长度 | 实现稍复杂 |
| **语义切分**(用 LLM 判断切点)| 高质量需求 | 质量最好 | 成本高 |
| **滑动窗口 + overlap** | 上下文连贯敏感 | 不漏边界信息 | 存储翻倍 |

**经验默认值**:
- chunk_size: **500-1000 字符** 或 **200-500 token**
- overlap: **chunk_size 的 10-20%**

### 5.2 多语言混合时

| 场景 | 应对 |
|---|---|
| 全中文 | `bge-m3` 或 `bge-large-zh-v1.5` |
| 全英文 | `bge-en-icl` 或 `voyage-3` |
| 中英混合 | **`bge-m3`**(多语言原生支持) |
| 代码混合 | 加 `voyage-code-3` 或 `codesage` 等代码 embedding |

### 5.3 Hybrid Search(混合检索)

**纯向量检索的弱点**:命名实体(人名 / 产品名 / 错别字)检索效果差,因为 Embedding 模型对**精确字符**不敏感。

**解决方案**:**Hybrid Search = BM25 关键词检索 + 向量检索**

```python
# 伪代码
keyword_results = bm25_search(query, k=20)
vector_results  = vector_search(query, k=20)
merged = reciprocal_rank_fusion(keyword_results, vector_results)
final  = reranker.rerank(query, merged, top_n=5)
```

**何时必须用 Hybrid**:
- 客服 / 售后场景(产品型号、订单号等命名实体)
- 学术 / 法律(精确术语)
- 代码搜索(关键字、API 名)

**支持 Hybrid 的向量库**:Milvus / Qdrant / Weaviate / Elasticsearch + 向量。

### 5.4 元数据过滤(Metadata Filtering)

**生产环境必备**:

```python
# 只在某个用户的文档里搜
results = qdrant.search(
    collection_name="docs",
    query_vector=qvec,
    query_filter=Filter(
        must=[
            FieldCondition(key="user_id", match=MatchValue(value="user_123")),
            FieldCondition(key="date", range=Range(gte="2026-01-01")),
        ]
    ),
    limit=50
)
```

**典型过滤维度**:
- `user_id` / `tenant_id`(多租户)
- `date / created_at`(时间窗口)
- `doc_type`(只搜文档 / 邮件 / Slack)
- `permission_level`(权限隔离)
- `language`(语言过滤)

> ⚠️ **重要**:**元数据过滤要在向量库层做,不要"先取 100 个再过滤"**——这会导致过滤后剩 5 个甚至 0 个,严重影响召回。

### 5.5 评测 RAG 的 4 个核心指标

| 指标 | 含义 | 算法 |
|---|---|---|
| **Recall@K** | Top-K 召回里包含正确答案的比例 | 标注数据集 + 自动算 |
| **MRR@K** | 平均倒数排名(正确答案越靠前越好)| 同上 |
| **NDCG@K** | 考虑相关度的排名质量 | 同上 |
| **Faithfulness** | LLM 回答是否忠于检索内容 | LLM-as-Judge / 人工 |

> 💡 **冷启动经验**:**先做 Recall@10**——如果你的 RAG Recall@10 不到 80%,所有"Reranker 调优 / Prompt 优化"都白费,**先把 Embedding 和切块改对**。

### 5.6 何时 RAG 比微调更好

| 维度 | RAG | Fine-tuning |
|---|---|---|
| 知识更新频率 | **高频**(每天)✅ | 低频(月度) |
| 数据量 | **少**(几百 KB 起) | 大(GB 级) |
| 部署成本 | **低** | 高(GPU 训练) |
| 可解释性 | **强**(看 source)| 弱 |
| 工程难度 | 中 | 高 |
| 模型行为改变 | ❌ 不能 | ✅ 能(风格 / 格式) |

**最佳实践**:**先 RAG,实在搞不定再 Fine-tuning**(或两者结合)。

---

## 6. 与本知识库其他章节的关联

- **RAG 入门**:[RAG/RAG学习笔记.md](RAG/RAG学习笔记.md)——RAG 的概念入门 + 搜索 API(Tavily / Exa)选型,**本文是它的"自建 RAG 三件套"深度补全**
- **真实案例**:[宠物CT影像AI辅助诊断方案.md](宠物CT影像AI辅助诊断方案.md)——医疗 RAG 的实战方案(用 BiomedCLIP + Milvus/Qdrant)
- **Medprompt 启发**:[Medprompt方法论解析.md](Medprompt方法论解析.md)——动态 few-shot 本质就是"检索示例题"的 RAG
- **LLM 接入**:[LLM 接口规范实战.md](LLM接口规范实战.md)——RAG 的 LLM 调用部分
- **模型选择**:[各家 LLM 模型特点速查.md](各家LLM模型特点速查.md)——RAG 配什么 LLM
- **本地部署**:[LLM 推理引擎选型.md](LLM推理引擎选型.md)——自部署 Embedding / Reranker 推理引擎(可用 [Infinity](https://github.com/michaelfeil/infinity) 或 [TEI](https://github.com/huggingface/text-embeddings-inference))
- **硬件适配**:[NVIDIA 显卡架构与 AI 算力.md](../05_技术基础/NVIDIA显卡架构与AI算力.md)——Embedding 模型对显存要求

---

## 7. 术语速查

| 术语 | 全称 / 含义 |
|---|---|
| **Embedding** | 把文本 / 图像 / 音频变成定长向量的过程 / 模型 |
| **Dense Vector** | 稠密向量(浮点数数组,每位都有值) |
| **Sparse Vector** | 稀疏向量(大部分为 0,如 BM25 关键词向量) |
| **Cosine Similarity** | 余弦相似度,向量相似度的标准算法 |
| **Bi-Encoder** | 双塔结构,Query / Doc 分开编码 |
| **Cross-Encoder** | 单塔结构,Query+Doc 拼起来一起编码 |
| **ANN** | Approximate Nearest Neighbor,近似最近邻 |
| **HNSW** | Hierarchical Navigable Small World,主流 ANN 算法 |
| **IVF / PQ** | Inverted File Index / Product Quantization,经典 ANN 算法组合 |
| **Reranker** | 精排模型(Cross-Encoder) |
| **Recall@K** | Top-K 内召回率 |
| **NDCG / MRR** | 排名质量指标 |
| **Chunking** | 切块,把长文档切成检索单元 |
| **Hybrid Search** | 混合检索 = 关键词 + 向量 |
| **BM25** | 经典关键词检索算法,常和向量检索互补 |
| **RRF** | Reciprocal Rank Fusion,合并多个检索结果的算法 |
| **Matryoshka** | 套娃维度,同一个 embedding 可在不同维度使用 |
| **ColBERT** | 后期交互检索范式,bge-m3 支持 |
| **Faithfulness** | RAG 评测维度:回答是否忠于检索内容 |
| **LLM-as-Judge** | 用强 LLM 给生成结果打分的评测方法 |
| **Vector DB / 向量数据库** | 专为向量检索优化的存储 |
| **Multi-tenancy** | 多租户,生产环境必备 |
| **Embedding 服务化** | 用 Infinity / TEI 把 Embedding 模型变成 OpenAI 兼容 API |
| **TEI** | text-embeddings-inference,HuggingFace 出品的 Embedding 推理 server |

---

## 8. 作者声明、来源与局限性

### 8.1 作者声明

> ⚠️ **本篇是 Claude 基于公开技术资料整理的科普综述,不是 LINUX DO @flymyd 的实战经验帖**。
>
> 原作者在「简单易懂的 LLM 相关知识梳理」目录中标记 ep.7「Embedding、Reranker 与向量数据库」为待填坑,本笔记为补位之作。

### 8.2 主要来源

- BGE 系列:https://github.com/FlagOpen/FlagEmbedding
- bge-m3 论文:https://arxiv.org/abs/2402.03216
- Milvus 文档:https://milvus.io/docs
- Qdrant 文档:https://qdrant.tech/documentation/
- pgvector:https://github.com/pgvector/pgvector
- MTEB 排行榜:https://huggingface.co/spaces/mteb/leaderboard
- Pinecone 教育内容:https://www.pinecone.io/learn/
- LangChain RAG 教程:https://python.langchain.com/docs/tutorials/rag/

### 8.3 本笔记的局限性

| 维度 | 局限性 |
|---|---|
| **个人 benchmark** | 没有亲自跑过 7 大向量库的 100 万级压测,**性能数据来自各官方 benchmark + MTEB 榜** |
| **超大规模(10 亿+)** | 本文止步于亿级,**Twitter / Google 级别的 RAG 架构**未涉及 |
| **法律 / 医疗等垂直领域** | 不同领域的 best practice 差异大(医学要 BiomedCLIP / 法律要 lex-emb),**没逐一展开** |
| **GraphRAG / 知识图谱 RAG** | 微软 GraphRAG 等"图 + RAG" 新范式未涉及 |
| **Agentic RAG** | "Agent 决定检索什么 / 什么时候检索" 的高级 RAG 未涉及 |
| **多模态 RAG** | 文本 RAG 是主体,**图像 / 视频 / 音频 RAG** 的特殊处理未展开 |
| **评测方法** | RAGAS、TruLens 等专业评测框架未深入 |

### 8.4 给读者的建议

- **想 30 分钟跑起来 RAG**:Chroma + bge-m3,本文 § 4 的代码改改就能用
- **想给公司搭中型 RAG**:Qdrant + bge-m3 + bge-reranker-v2-m3,**这是当前最实用的组合**
- **想要企业级 RAG**:Milvus 集群 + bge-m3 + bge-reranker + Hybrid Search,配 LangChain / LlamaIndex
- **想做研究 / 评测**:RAGAS 是当前主流的 RAG 评测框架
- **关注前沿**:微软 GraphRAG、Anthropic Contextual Retrieval、CRAG(Corrective RAG)是 2025 年值得关注的新方向
